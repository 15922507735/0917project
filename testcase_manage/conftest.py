"""测试用例层 conftest：定义核心 fixture。

层级关系（按作用域从大到小）：
- logger (session)            ← 不依赖任何 fixture
- driver (session)            ← 依赖 logger
- login_op (session)          ← 依赖 driver / logger（无状态操作对象，全局复用）
- first_page_op (session)     ← 依赖 driver / logger（无状态操作对象，全局复用）
- webview_op (session)        ← 依赖 driver / logger（无状态操作对象，全局复用）
- is_logged_in_session (session) ← 依赖 driver / logger（启动时探测一次登录态）
- fatie_op (function)         ← 依赖 driver / logger / webview_op（带 yield 清理）
- case_level_guard (function, autouse) ← 每个用例前后做轻量状态清理

设计原则：
- fixture 只做"准备 + 清理"，业务逻辑放操作层；
- 无状态操作对象（LoginOperate / FirstPageOperate / WebViewOperate）提为 session 级，
  避免每个用例重复构造；
- 有副作用的 fixture（is_logged_in_session / fatie_op）用 try/finally 或 yield
  保证状态恢复；
- session 级 driver 在整个测试会话只启动一次，结束统一 quit()。
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from time import sleep

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 加载项目根目录下的 .env（如果存在）—— 由 python-dotenv 提供支持
# 加载后所有 os.getenv(...) 都能读到 .env 中的变量；找不到 .env 时跳过
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
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
    options.no_reset = os.getenv("APP_NO_RESET", "false").lower() not in ("false", "0", "no")
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
    """尝试点启动时授权同意按钮；找不到就返回 False（不抛异常）。"""
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

    - 自动创建 logs/ 目录；
    - 日志文件名按时间戳命名；
    - 控制台 + 文件双输出；
    - 避免重复 handler。
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    log_obj = logging.getLogger("auto_test")
    log_obj.setLevel(logging.INFO)
    if not log_obj.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
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

    - 使用 UiAutomator2Options 新版 API 构建启动参数；
    - Appium 2 服务地址 http://127.0.0.1:4723（v6 客户端不再追加 /wd/hub）；
    - 启动后先探测是否已在发现页，是则跳过协议弹窗探测；
    - 整个 session 结束统一 quit()（try/finally 兜底）。
    """
    logger.info("[driver] 启动 Appium session ...")
    options = _build_appium_options()
    d = webdriver.Remote(APPIUM_SERVER, options=options)
    d.implicitly_wait(EXPECT_WAIT_TIMEOUT)
    sleep(3)

    logger.info(f"[driver] 当前 Activity: {d.current_activity}")
    logger.info(f"[driver] 当前包名: {d.current_package}")

    _close_anr_if_exists(d, logger)

    if _is_on_discover_page(d, logger):
        logger.info(
            "[driver] APP 已在发现页（热启动 / noReset 残留登录态），"
            "跳过协议探测与冷启动"
        )
    else:
        try:
            if d.current_package != APP_PACKAGE:
                logger.warning(
                    f"[driver] 启动后当前包名={d.current_package} 不等于 APP，强制冷启动"
                )
                _relaunch_app(d, logger)
        except Exception as e:
            logger.warning(f"[driver] 检查包名失败（可忽略）: {e}")

        clicked = _click_agreement_with_retry(d, logger, max_retry=1)
        if not clicked:
            logger.warning(
                "[driver] 未找到授权同意按钮，可能 APP 已停在主页"
                "（残留会话），继续执行（由用例 2 自行处理）"
            )

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


# ===================== 3. 无状态操作对象 fixture（session，全局复用） =====================
@pytest.fixture(scope="session")
def login_op(driver, logger):
    """session 级 LoginOperate 实例（无状态，全局复用）。

    LoginOperate 只持有 driver / logger 引用，不缓存页面状态，
    因此可以安全地在 session 内复用，避免每个用例重复构造。
    """
    from object_operation.login_operate import LoginOperate
    return LoginOperate(driver, logger)


@pytest.fixture(scope="session")
def first_page_op(driver, logger):
    """session 级 FirstPageOperate 实例（无状态，全局复用）。"""
    from object_operation.first_page_operate import FirstPageOperate
    return FirstPageOperate(driver, logger)


@pytest.fixture(scope="session")
def webview_op(driver, logger):
    """session 级 WebViewOperate 实例（无状态，全局复用）。"""
    from object_operation.webview_operate import WebViewOperate
    return WebViewOperate(driver, logger)


@pytest.fixture(scope="session")
def my_op(driver, logger):
    """session 级 MyOperate 实例（无状态，全局复用）。"""
    from object_operation.my_operate import MyOperate
    return MyOperate(driver, logger)


@pytest.fixture(scope="session")
def order_op(driver, logger, webview_op):
    """session 级 OrderOperate 实例（无状态，全局复用）。"""
    from object_operation.order_operate import OrderOperate
    return OrderOperate(driver, logger, webview_operate=webview_op)


@pytest.fixture(scope="session")
def seecar_op(driver, logger):
    """session 级 SeeCarOperate 实例（无状态，全局复用）。"""
    from object_operation.seecar_operate import SeeCarOperate
    return SeeCarOperate(driver, logger)


@pytest.fixture(scope="session")
def shequ_op(driver, logger):
    """session 级 ShequOperate 实例（无状态，全局复用）。"""
    from object_operation.shequ_operate import ShequOperate
    return ShequOperate(driver, logger)


@pytest.fixture(scope="session")
def shequ_op_webview(driver, logger, webview_op):
    """session 级 ShequOperate 实例（带 webview，用于话题广场等切 WebView 场景）。"""
    from object_operation.shequ_operate import ShequOperate
    return ShequOperate(driver, logger, webview_operate=webview_op)


@pytest.fixture(scope="session")
def huodong_op(driver, logger):
    """session 级 HuodongOperate 实例（无状态，全局复用）。"""
    from object_operation.huodong_operate import HuodongOperate
    return HuodongOperate(driver, logger)


# ===================== 4. 登录态探测 fixture（session） =====================
@pytest.fixture(scope="session")
def is_logged_in_session(driver, logger, login_op, first_page_op) -> bool:
    """session 级登录态探测 fixture。

    业务背景：用户要求"不要强制清除登录，如果是已登录就走用例 5"。
    本 fixture 在 driver 启动后立即探测一次当前登录态，
    用例 1 / 2 / 3 在已登录时 pytest.skip。

    判据：点"我的" Tab 后看登录态昵称元素（LOGINING_BTN）是否可见。
        可见 → 已登录；不可见 → 未登录。

    注意（作用域语义）：
        本 fixture 是 session 级，**只在首次调用时探测一次**。
        如果用例 3 执行了登录，本 fixture 的返回值不会刷新。
        因此用例 5+ 不应依赖本 fixture 判断登录态，而应自带断言。

    用 try/finally 保证：无论探测是否成功，最终都切回发现 Tab，
    避免污染后续用例的起始状态。
    """
    from page_element.login_page import LOGINING_BTN
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    logged_in = False
    try:
        # 兜底：检测系统级崩溃弹窗
        try:
            _close_anr_if_exists(driver, logger)
        except Exception:
            pass
        try:
            current_pkg = driver.current_package or ""
            if current_pkg and current_pkg != APP_PACKAGE:
                logger.warning(
                    f"[is_logged_in_session] 当前包名={current_pkg} ≠ {APP_PACKAGE}，"
                    f"主动 activate_app 拉回 APP"
                )
                driver.activate_app(APP_PACKAGE)
                sleep(2)
        except Exception as e:
            logger.warning(f"[is_logged_in_session] 拉回 APP 失败（忽略）: {e}")

        # 点"我的" Tab（这样才能看到登录态昵称元素）
        try:
            login_op.click_my_btn()
            sleep(1)
        except Exception as e:
            logger.warning(f"[is_logged_in_session] 点我的 Tab 失败: {e}")

        # 探测 LOGINING_BTN 是否可见
        try:
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located(LOGINING_BTN)
            )
            logger.info("[is_logged_in_session] LOGINING_BTN 可见 → 已登录")
            logged_in = True
        except (TimeoutException, NoSuchElementException):
            logger.info("[is_logged_in_session] LOGINING_BTN 不可见 → 未登录")
    finally:
        # 无论成功失败，都切回发现 Tab，保证后续用例从发现页起跑
        try:
            first_page_op.click_discover_tab()
        except Exception:
            pass

    return logged_in


# ===================== 5. 发帖操作 fixture（function，带 yield 清理） =====================
@pytest.fixture
def fatie_op(driver, logger, webview_op):
    """function 级 FatieOperate 实例，带 yield 后置清理。

    清理逻辑（yield 之后）：
    1. 强制切回 NATIVE_APP context（避免 WebView 残留污染下一个用例）；
    2. 若 APP 不在主 Activity，按返回键回到 QYMainActivity。

    用例无需自己写 try/finally，fixture 自动兜底。
    """
    from object_operation.fatie_operate import FatieOperate

    op = FatieOperate(driver, logger, webview_operate=webview_op)

    yield op

    # ---------- teardown ----------
    # 1. 强制切回 NATIVE_APP
    try:
        if "NATIVE_APP" in driver.contexts:
            driver.switch_to.context("NATIVE_APP")
            logger.info("[fatie_op] teardown 已切回 NATIVE_APP context")
    except Exception as e:
        logger.warning(
            f"[fatie_op] teardown 切回 NATIVE 失败: {e.__class__.__name__}: {e}"
        )
        return

    # 2. 如果 APP 还在发文章 WebView 页，按返回键退出到主 Activity
    max_back = 5
    for i in range(max_back):
        try:
            activity = driver.current_activity or ""
        except Exception:
            break
        if "QYMainActivity" in activity:
            logger.info(f"[fatie_op] teardown 已回到 QYMainActivity（用 {i} 次返回）")
            break
        try:
            driver.back()
        except Exception:
            break
        sleep(0.5)
    else:
        logger.warning(
            f"[fatie_op] teardown 连续按了 {max_back} 次返回，仍未回到 QYMainActivity"
        )


# ===================== 6. 业务操作 fixture（function） =====================
@pytest.fixture
def fuwu_op(driver, logger, login_op, first_page_op, webview_op):
    """function 级 FuwuOperate，前置 ensure_ready 把 APP 拉到发现页。"""
    from utils.test_helpers import ensure_ready
    ensure_ready(login_op, first_page_op, logger)
    from object_operation.fuwu_operate import FuwuOperate
    return FuwuOperate(driver, logger, webview_operate=webview_op)


@pytest.fixture
def fuwu_op_keep(driver, logger, webview_op):
    """function 级 FuwuOperate，不做 ensure_ready，直接复用当前页面。

    用于强状态链用例（16~20）：上一用例跑完停在服务 Tab，强行 ensure_ready
    会因为"推荐 Tab 不可见"被判定为未在发现页，触发冷启动前置流程失败。
    """
    from object_operation.fuwu_operate import FuwuOperate
    return FuwuOperate(driver, logger, webview_operate=webview_op)


@pytest.fixture
def buycar_op(driver, logger, login_op, first_page_op):
    """function 级 BuycarOperate，前置 ensure_ready 把 APP 拉到发现页。"""
    from utils.test_helpers import ensure_ready
    ensure_ready(login_op, first_page_op, logger)
    from object_operation.buycar_operate import BuycarOperate
    return BuycarOperate(driver, logger)


@pytest.fixture
def buycar_op_keep(driver, logger):
    """function 级 BuycarOperate，不做 ensure_ready，直接复用当前页面。

    用于强状态链末尾（用例 34~35）：上一用例跑完停在「我的」页面，
    由用例自行切回「发现」Tab 后再操作。
    """
    from object_operation.buycar_operate import BuycarOperate
    return BuycarOperate(driver, logger)


# ===================== 7. 用例级自动前后置 fixture（autouse） =====================
@pytest.fixture(autouse=True)
def case_level_guard(driver, logger):
    """function 级自动 fixture：每个用例前/后做轻量状态清理与恢复。

    - setup：关闭 ANR / 崩溃弹窗；
    - teardown：
      * 若 driver 残留在 WebView context，强制切回 NATIVE_APP；
      * 若当前包名不在 APP 内，调用 activate_app 热重启；
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
