"""测试用例层 conftest：定义核心 fixture（logger / driver）。

层级关系：
- logger (session)  ← 不依赖任何 fixture
- driver (session)  ← 依赖 logger，用于在启动/失败时写日志

设计原则：
- fixture 只做"准备 + 清理"，业务逻辑放操作层；
- Appium 2 端口默认 4723，URL 不带 /wd/hub（v6 客户端已自动处理）；
- session 级 driver 在整个测试会话只启动一次；
- 启动后尽力点击启动时隐私协议"同意"按钮，找不到就 warning 继续（不强制 quit）；
- 整个 session 结束统一 quit()。

注：本框架"引导页左滑 3 次 + 主页入口 5 次 + 切到发现页"前置流程
在 test_login.py 的用例 2 内部按需触发。
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from time import sleep

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 允许从项目根目录导入 page_element / object_operation 包
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 加载项目根目录下的 .env（如果存在）—— 由 python-dotenv 提供支持
# 加载后所有 os.getenv(...) 都能读到 .env 中的变量；找不到 .env 时跳过
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.isfile(_env_path):
        load_dotenv(_env_path, override=False)
except ImportError:
    pass

from page_element.login_page import (  # noqa: E402
    AGREEMENT_BTN,
    APP_ACTIVITY,
    APP_PACKAGE,
    APP_WAIT_ACTIVITY,
    APPIUM_SERVER,
    CLOSE_BTN,
    DEVICE_NAME,
    EXPECT_WAIT_TIMEOUT,
)


# ===================== 工具：构建 Appium 启动选项 =====================
# chromedriver 路径：手动安装的 91.0.4472 版（与模拟器内 WebView Chrome 91 对应）。
# Appium 2 默认不会自动下载 chromedriver，必须显式指定才能在切 WebView 时正常启动。
CHROMEDRIVER_EXECUTABLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe"
)


def _build_appium_options() -> UiAutomator2Options:
    """构造 Appium 启动选项（UiAutomator2Options 新版 API）。

    Appium 2 注意点：
    - capabilities 全部走 options.xxx，不再使用 desired_capabilities 字典；
    - chromedriver 路径通过 appium:chromedriverExecutable 扩展 capability 注入。
    """
    options = UiAutomator2Options()
    options.platform_name = "android"
    options.platform_version = "9"
    options.device_name = DEVICE_NAME
    options.udid = DEVICE_NAME
    options.automation_name = "UiAutomator2"
    options.unicode_keyboard = True
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.app_wait_activity = APP_WAIT_ACTIVITY
    # noReset：通过环境变量 APP_NO_RESET 切换。
    #   APP_NO_RESET=false → 冷启动：APP 状态被清空，必然停在协议页 / 引导页，
    #                        用例 1/2/3 的"未登录"前置流程可被实际跑到。**默认行为**。
    #   APP_NO_RESET=true  → 热启动：复用 noReset 残留登录态（用例 1/2/3 会被 SKIPPED）。
    # 默认改为 false：用户希望"从冷启动开始跑"，业务场景是 APP 重新进入业务流。
    options.no_reset = os.getenv("APP_NO_RESET", "false").lower() not in ("false", "0", "no")
    # 指定 chromedriver 路径，避免切 WebView 时 Appium 报
    # "No Chromedriver found that can automate Chrome '91.0.4472'"
    options.set_capability("appium:chromedriverExecutable", CHROMEDRIVER_EXECUTABLE)
    return options


def _close_anr_if_exists(d, logger_obj, timeout: int = 2) -> bool:
    """检测并关闭系统级 ANR / 崩溃弹窗，返回 True 表示关闭了一次。"""
    from utils.debug_helpers import close_anr_if_exists
    result = close_anr_if_exists(d, logger_obj, timeout)
    if result:
        sleep(2)
    return result


def _relaunch_app(d, logger_obj):
    """强制重新拉起 APP（activate_app 优先，失败时 fallback 到 mobile: startActivity）。"""
    last_err = None
    try:
        d.activate_app(APP_PACKAGE)
        logger_obj.info(f"[driver] 已重新拉起 APP (activate_app): {APP_PACKAGE}")
        sleep(3)
        return
    except Exception as e:
        last_err = e
        logger_obj.warning(f"[driver] activate_app 失败: {e}")
    try:
        d.execute_script("mobile: startActivity", {
            "appId": APP_PACKAGE,
            "intent": {
                "action": "android.intent.action.MAIN",
                "category": "android.intent.category.LAUNCHER",
            },
        })
        logger_obj.info(f"[driver] 已重新拉起 APP (mobile: startActivity): {APP_PACKAGE}")
        sleep(3)
        return
    except Exception as e:
        last_err = e
    logger_obj.warning(f"[driver] 重新拉起 APP 失败: {last_err}")
    raise last_err


def _is_on_discover_page(d, logger_obj) -> bool:
    """探测当前是否已在「发现」首页。

    判据：current_package == APP_PACKAGE + 「推荐」二级 Tab 2s 内可见。
    用于 driver fixture 启动时快速判断"是否已登录 / 已在发现页"——
    若已发现，就不需要再等协议弹窗（协议弹窗本就不存在）。
    """
    from page_element.first_page import RECOMMEND_BUTTON  # 延迟导入避免循环
    try:
        if d.current_package != APP_PACKAGE:
            return False
        WebDriverWait(d, 2).until(
            EC.visibility_of_element_located(RECOMMEND_BUTTON)
        )
        logger_obj.info("[driver] 已检测到「推荐」Tab → 已在发现页")
        return True
    except Exception:
        return False


def _click_agreement_with_retry(d, logger_obj, max_retry: int = 1) -> bool:
    """尝试点启动时授权同意按钮；找不到就返回 False（不抛异常）。

    设计变更（v2）：
    - max_retry 砍到 1 —— 启动时协议弹窗有就是有，没有就真的没有；
    - 等待时间 2s —— 协议弹窗若存在，2s 必然出现；不存在时立刻放行。
    - 历史教训：3 次 × 10s 重试会在"已停在主页 / 已登录"的 noReset 状态下
      白白浪费 30s。driver fixture 不应该重试，重试的职责交给用例侧
      `ensure_ready` → `run_pre_login_flow`。
    """
    for attempt in range(1, max_retry + 1):
        _close_anr_if_exists(d, logger_obj)
        try:
            WebDriverWait(d, 2).until(
                EC.element_to_be_clickable(AGREEMENT_BTN)
            ).click()
            logger_obj.info(
                f"[driver] 已点击启动时授权弹窗的同意按钮（第 {attempt} 次）"
            )
            return True
        except Exception as e:
            logger_obj.info(
                f"[driver] 第 {attempt} 次未找到同意按钮（已停止重试，"
                f"由用例侧 run_pre_login_flow 兜底）: {e.__class__.__name__}"
            )
            return False
    return False


# ===================== 1. logger fixture（session） =====================
@pytest.fixture(scope="session")
def logger():
    """session 级日志 fixture。

    功能：
    - 自动创建 logs/ 目录（不存在则创建）；
    - 日志文件名按时间戳命名，避免互相覆盖；
    - 控制台 + 文件双输出；
    - 避免重复 handler（同一 logger 多次 setup 时复用现有 handler）。
    """
    # 项目根目录下的 logs/ 文件夹
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名：logs/run_YYYYMMDD_HHMMSS.log
    log_file = os.path.join(
        log_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # 使用独立 logger（不污染 root logger），便于 fixture 隔离
    log_obj = logging.getLogger("auto_test")
    log_obj.setLevel(logging.INFO)
    # 避免重复 handler：仅当 logger 还没有 handler 时才追加
    if not log_obj.handlers:
        # 文件 handler：UTF-8，避免中文乱码
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        # 控制台 handler：实时回显到终端
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        log_obj.addHandler(file_handler)
        log_obj.addHandler(console_handler)

    log_obj.info(f"[logger] 日志系统初始化完成，日志文件：{log_file}")
    return log_obj


# ===================== 2. driver fixture（session，依赖 logger） =====================
@pytest.fixture(scope="session")
def driver(logger):
    """session 级 Appium driver fixture。

    参数：
        logger: 注入的 session 级日志器，便于启动/失败时记录日志。

    行为：
    - 使用 UiAutomator2Options 新版 API 构建启动参数；
    - Appium 2 服务地址 http://127.0.0.1:4723（注意：v6 客户端不再追加 /wd/hub）；
    - noReset=True 保留 APP 状态，implicitly_wait=10s；
    - 启动后**先探测是否已在发现页**：
      * 是 → 跳过协议弹窗探测 / 冷启动 / ANR 处理，直接 yield；
      * 否 → 再走"协议弹窗 + 必要时冷启动"流程；
    - 整个 session 结束统一 quit()。

    历史教训：noReset=True 场景下，APP 经常直接停在主页 / 发现页，
    再去 10s×3 重试找协议弹窗会白白浪费 30s。
    """
    logger.info("[driver] 启动 Appium session ...")
    options = _build_appium_options()
    # Appium 2 地址：http://127.0.0.1:4723（不再带 /wd/hub）
    d = webdriver.Remote(APPIUM_SERVER, options=options)
    # 隐式等待 10s
    d.implicitly_wait(EXPECT_WAIT_TIMEOUT)
    # 等 3s 让 APP 启动动画结束（与旧框架 sleep 5 等协议不同——
    # 我们先看"是否已在发现页"，有就不管协议）
    sleep(3)

    logger.info(f"[driver] 当前 Activity: {d.current_activity}")
    logger.info(f"[driver] 当前包名: {d.current_package}")

    # 启动时可能立即 ANR，先尝试关一次
    _close_anr_if_exists(d, logger)

    # ★ 关键优化：先探测"是否已在发现页"。
    # 若是 → 整个启动流程结束（不点协议 / 不重启 / 不冷启动），
    #        让用例侧 ensure_ready 走"已发现 → 跳过前置"路径。
    if _is_on_discover_page(d, logger):
        logger.info(
            "[driver] APP 已在发现页（热启动 / noReset 残留登录态），"
            "跳过协议探测与冷启动"
        )
    else:
        # 不在发现页 → 才走"协议弹窗 + 必要时冷启动"流程
        # 若 APP 不在包内（被弹桌面 / 闪退 / 上一次残留），强制重启一次
        try:
            if d.current_package != APP_PACKAGE:
                logger.warning(
                    f"[driver] 启动后当前包名={d.current_package} 不等于 APP，强制冷启动"
                )
                _relaunch_app(d, logger)
        except Exception as e:
            logger.warning(f"[driver] 检查包名失败（可忽略）: {e}")

        # 处理启动时隐私协议授权弹窗（1 次尝试，2s 等待）；
        # 找不到不强制 quit —— APP 可能已停在主页，后续用例 2 会自行处理。
        clicked = _click_agreement_with_retry(d, logger, max_retry=1)
        if not clicked:
            logger.warning(
                "[driver] 未找到授权同意按钮，可能 APP 已停在主页"
                "（残留会话），继续执行（由用例 2 自行处理）"
            )

        # 兜底：点完协议按钮后，APP 偶尔会闪退到桌面（系统弹 ANR 后被 close_anr 误关）。
        # 此时若 current_package != APP_PACKAGE，主动冷启动一次把 APP 拉回前台。
        try:
            sleep(2)
            if d.current_package != APP_PACKAGE:
                logger.warning(
                    f"[driver] 点完协议后当前包名={d.current_package} ≠ {APP_PACKAGE}，"
                    f"主动冷启动拉回 APP 前台"
                )
                _relaunch_app(d, logger)
        except Exception as e:
            logger.warning(f"[driver] 协议后兜底冷启动失败（可忽略）: {e}")

        # ★ 关键：点完协议 + 处理 ANR 之后，只做"软探测"——不主动跑前置流程。
        # 原因：run_pre_login_flow（点同意→左滑 3→入口 5）会浪费 2~3 分钟，
        #       且 swipe 在 Appium 2 上常失败。
        # 这里只打印"未在发现页"的 warning，由后续用例的 ensure_ready（v4）兜底。
        logger.warning(
            "[driver] 启动后 APP 不在发现页（可能停在 QYLeadingActivity / 协议页 / 主页），"
            "由用例侧 ensure_ready 兜底切回发现 Tab"
        )

    try:
        yield d
    finally:
        logger.info("[driver] 关闭 Appium session")
        try:
            d.quit()
        except Exception:
            pass


# ===================== 3. 登录态探测 fixture（session） =====================
@pytest.fixture(scope="session")
def is_logged_in_session(driver, logger) -> bool:
    """session 级登录态探测 fixture。

    业务背景：用户要求"不要强制清除登录，如果是已登录就走用例 5"。
    本 fixture 在 driver 启动后立即探测一次当前登录态，
    用例 1 / 2 / 3 在已登录时 pytest.skip，只让用例 5 跑主体。

    判据：点"我的" Tab 后看登录态昵称元素（LOGINING_BTN）是否可见。
        可见 → 已登录；不可见 → 未登录。
    （"在发现页"判据不准确：未登录用户也能看到发现页 / 推荐 Tab。）

    返回：
        bool: True 表示已登录（已在发现页），False 表示未登录。
    """
    # 延迟导入避免 conftest 启动时拉入 first_page_operate（依赖 ddddocr 等）
    from object_operation.first_page_operate import FirstPageOperate
    from object_operation.login_operate import LoginOperate
    from page_element.login_page import LOGINING_BTN, MY_BTN
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    fp_op = FirstPageOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    login_op = LoginOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)

    # 0. 兜底：检测当前是否在系统级崩溃弹窗（"长安启源屡次停止运行"）。
    #    冷启动时常因 ANR / 闪退触发系统弹窗，导致后续 find_element 失败。
    #    这里主动点 "关闭应用" + activate_app 拉回 APP。
    try:
        _close_anr_if_exists(driver, logger)
    except Exception:
        pass
    try:
        from page_element.login_page import APP_PACKAGE as _APP_PKG
        current_pkg = driver.current_package or ""
        if current_pkg and current_pkg != _APP_PKG:
            logger.warning(
                f"[is_logged_in_session] 当前包名={current_pkg} ≠ {_APP_PKG}，"
                f"主动 activate_app 拉回 APP"
            )
            driver.activate_app(_APP_PKG)
            import time as _t
            _t.sleep(2)
    except Exception as e:
        logger.warning(f"[is_logged_in_session] 拉回 APP 失败（忽略）: {e}")

    # 1. 先确保 APP 在"我的" Tab（这样才能看到登录态昵称元素 LOGINING_BTN）
    try:
        login_op.click_my_btn()
        import time as _t
        _t.sleep(1)
    except Exception as e:
        logger.warning(f"[is_logged_in_session] 点我的 Tab 失败: {e}")

    # 2. 探测 LOGINING_BTN（已登录后"我的"页面会显示昵称）是否可见
    try:
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(LOGINING_BTN)
        )
        logger.info("[is_logged_in_session] LOGINING_BTN 可见 → 已登录")
        # 3. 探测完点回发现 Tab（不影响后续用例的稳态）
        try:
            fp_op.click_discover_tab()
        except Exception:
            pass
        return True
    except (TimeoutException, NoSuchElementException):
        logger.info("[is_logged_in_session] LOGINING_BTN 不可见 → 未登录")
        # 探测完点回发现 Tab（让后续用例从发现页起跑）
        try:
            fp_op.click_discover_tab()
        except Exception:
            pass
        return False


# ===================== 4. 用例级自动前后置 fixture（autouse） =====================
@pytest.fixture(autouse=True)
def case_level_guard(driver, logger):
    """function 级自动 fixture：每个用例前/后做轻量状态清理与恢复。

    设计目标（不侵入业务逻辑，只做兜底）：
    - setup：关闭 ANR / 崩溃弹窗（避免中途弹窗导致用例假失败）；
    - teardown：
      * 若 driver 残留在 WebView context，强制切回 NATIVE_APP
        （防止下个用例 find_element 报 invalid locator）；
      * 若当前包名不在 APP 内（闪退 / 被弹桌面），调用 activate_app 热重启；
      * 出错不抛异常，只记 warning，避免 teardown 失败掩盖真实用例失败。
    """
    # ---------- setup ----------
    try:
        _close_anr_if_exists(driver, logger)
    except Exception as e:
        logger.warning(f"[case_guard] setup 关闭 ANR 失败（忽略）: {e}")

    yield

    # ---------- teardown ----------
    # 1. 强制切回 NATIVE_APP（若当前在 WebView）
    try:
        current_ctx = getattr(driver, "current_context", None)
        if current_ctx and current_ctx != "NATIVE_APP":
            logger.warning(
                f"[case_guard] teardown 检测到 WebView 残留: {current_ctx}，强制切回 NATIVE_APP"
            )
            try:
                driver.switch_to.context("NATIVE_APP")
            except Exception as e:
                logger.warning(f"[case_guard] 切回 NATIVE_APP 失败（忽略）: {e}")
    except Exception as e:
        logger.warning(f"[case_guard] 探测 current_context 失败（忽略）: {e}")

    # 2. 若不在 APP 包内，热重启 APP
    try:
        current_pkg = driver.current_package
        if current_pkg != APP_PACKAGE:
            logger.warning(
                f"[case_guard] teardown 检测到包名漂移: {current_pkg}，尝试热重启 APP"
            )
            try:
                driver.activate_app(APP_PACKAGE)
            except Exception as e:
                logger.warning(f"[case_guard] 热重启 APP 失败（忽略）: {e}")
    except Exception as e:
        logger.warning(f"[case_guard] 探测 current_package 失败（忽略）: {e}")

    
