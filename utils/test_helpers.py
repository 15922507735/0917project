"""测试辅助函数（跨用例复用）。

目前仅保留 ``ensure_ready`` —— 用例开始前保证 APP 处于「发现」首页。
其余 ``build_*_op`` 构造函数已由 conftest.py 中的 session / function 级 fixture 替代，
避免每个用例重复构造无状态操作对象。
"""
from __future__ import annotations

from typing import Any


def ensure_ready(login_op, first_page_op, logger) -> None:
    """用例开始前调用：保证 APP 处于「发现」首页。

    状态机（v5）：
        1. 在发现页 → 跳过；
        2. 在登录页（"密码登录"可见）→ 跳过（用例 3 业务前提就是登录页）；
        3. 在协议页 / 引导页（QYLeadingActivity，没有底部 Tab 栏）→
           跑 run_pre_login_flow（点同意→左滑 3→入口 5）把 APP 带到发现页；
        4. 其他场景（上一条用例停在"我的"/"社区"/"活动"/"服务"/"购车" Tab）→
           主动 click_discover_tab() 切回发现页。

    设计要点：
        - 协议页必须跑前置流程（否则"发现" Tab 根本不存在）；
        - 其他非发现页只点"发现" Tab 切回（避免破坏用例 1/2/3 留下的稳态）；
        - 启动期 conftest 不再主动跑 run_pre_login_flow（避免 2~3 分钟的 swipe 兼容问题浪费），
          由 ensure_ready 在每个用例开始时按需跑。
    """
    # 1. 探测是否已在发现页
    on_discover = False
    try:
        on_discover = first_page_op.is_on_discover_page()
    except Exception as e:
        logger.warning(f"[ensure_ready] 探测发现页失败: {e}")

    if on_discover:
        logger.info("[ensure_ready] 已在发现页 → 跳过")
        return

    # 1.5 兜底：检测到系统级弹窗（包名 com.android.packageinstaller），
    #     说明上一条用例结束时残留了权限授予 / 通知授权弹窗。
    try:
        current_pkg = first_page_op.driver.current_package or ""
    except Exception:
        current_pkg = ""

    if current_pkg == "com.android.packageinstaller":
        logger.warning(
            "[ensure_ready] 检测到系统级弹窗（com.android.packageinstaller），"
            "尝试点「允许」关闭弹窗"
        )
        from selenium.webdriver.support.ui import WebDriverWait as _W
        from selenium.webdriver.support import expected_conditions as _EC
        try:
            from page_element.fatie_page import PERMISSION_ALLOW_BUTTON
            for _attempt in range(2):
                try:
                    _W(first_page_op.driver, 3).until(
                        _EC.presence_of_element_located(PERMISSION_ALLOW_BUTTON)
                    ).click()
                    logger.info(
                        f"[ensure_ready] 已点掉系统弹窗「允许」按钮（第 {_attempt + 1} 次）"
                    )
                    break
                except Exception as e:
                    logger.info(
                        f"[ensure_ready] 第 {_attempt + 1} 次未找到「允许」按钮: "
                        f"{e.__class__.__name__}"
                    )
        except Exception as e:
            logger.warning(f"[ensure_ready] 尝试点「允许」失败: {e}")

        # 兜底：若 2 次都没点到「允许」，按返回键（最多 3 次）
        for _ in range(3):
            try:
                current_pkg = first_page_op.driver.current_package or ""
            except Exception:
                current_pkg = ""
            if current_pkg != "com.android.packageinstaller":
                break
            try:
                first_page_op.driver.back()
            except Exception:
                pass
            import time as _t
            _t.sleep(1)

        # 拉回 APP
        try:
            from page_element.login_page import APP_PACKAGE as _APP_PKG
            first_page_op.driver.activate_app(_APP_PKG)
        except Exception as e:
            logger.warning(f"[ensure_ready] 拉回 APP 失败: {e}")
        import time as _t
        _t.sleep(2)
        # 重新探测发现页
        try:
            on_discover = first_page_op.is_on_discover_page()
        except Exception:
            on_discover = False
        if on_discover:
            logger.info("[ensure_ready] 处理完系统弹窗后已在发现页 → 跳过")
            return

    # 2. 不在发现页 → 探测是否已在登录页（"密码登录"按钮可见）
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from page_element.login_page import GO_PASSLOGIN_BTN
        WebDriverWait(first_page_op.driver, 2).until(
            EC.visibility_of_element_located(GO_PASSLOGIN_BTN)
        )
        logger.info(
            "[ensure_ready] 已在登录页（\"密码登录\"按钮可见）→ 跳过，"
            "由用例自身处理登录逻辑"
        )
        return
    except Exception:
        pass

    # 3. 不在发现页/登录页 → 探测是否在协议页 / 引导页
    try:
        activity = first_page_op.driver.current_activity or ""
    except Exception:
        activity = ""

    if "QYLeadingActivity" in activity:
        logger.info(
            "[ensure_ready] 检测到协议页/引导页（"
            f"{activity}）→ 跑前置流程（点同意→滑动→入口 5）"
        )
        try:
            login_op.run_pre_login_flow()
        except Exception as e:
            logger.warning(
                f"[ensure_ready] 协议页前置流程部分失败（不影响）: {e}"
            )
        try:
            first_page_op.click_discover_tab()
        except Exception as e:
            logger.warning(f"[ensure_ready] 协议页前置后切发现 Tab 失败: {e}")
        return

    # 4. 其他场景 → 主动点"发现" Tab
    logger.info(
        "[ensure_ready] 不在发现页（Activity="
        f"{activity}），可能停在'我的'/'社区'/'活动'等 Tab → 主动点「发现」Tab 切回"
    )
    try:
        first_page_op.click_discover_tab()
    except Exception as e:
        logger.warning(
            f"[ensure_ready] 切发现 Tab 失败（可能已在发现页 / APP 未启动完成）: {e}"
        )
