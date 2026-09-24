"""测试辅助函数（跨用例复用）。

提供构造 operate 实例 + APP 状态重置等公共辅助函数，
从 testcase_manage/test_business_flow.py 中提取，供多个用例文件复用。
"""
from __future__ import annotations

from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from object_operation.login_operate import LoginOperate
from object_operation.first_page_operate import FirstPageOperate
from object_operation.webview_operate import WebViewOperate
from object_operation.fuwu_operate import FuwuOperate
from object_operation.buycar_operate import BuycarOperate


def build_ops(driver: WebDriver, logger: Any):
    """根据 session 级 driver 构造 LoginOperate / FirstPageOperate。"""
    login_op = LoginOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    first_page_op = FirstPageOperate(
        driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT
    )
    return login_op, first_page_op


def ensure_ready(login_op, first_page_op, logger) -> None:
    """用例开始前调用：保证 APP 处于「发现」首页。

    状态机（基于"登录成功 + 热启动 APP 后停在发现页"）：
    1. 探测当前是否已在发现页（first_page_op.is_on_discover_page()）：
       - 已在发现页 → 跳过所有前置流程（点协议 / 左滑 / 入口 5 次 / 切发现），
         直接结束 —— 这就是"已登录 / 热启动后"的稳态；
       - 不在发现页 → 走完整前置流程（点同意 → 左滑 3 → 入口 5 → 兜底再点同意），
         然后切到「发现」首页。

    失败时仅打 warning，不抛异常 —— 让用例自己决定如何处理。
    """
    # 1. 探测是否已在发现页
    on_discover = False
    try:
        on_discover = first_page_op.is_on_discover_page()
    except Exception as e:
        logger.warning(f"[ensure_ready] 探测发现页失败: {e}")

    if on_discover:
        logger.info("[ensure_ready] 已在发现页 → 跳过全部前置流程")
        return

    # 2. 不在发现页 → 走完整前置流程
    logger.info("[ensure_ready] 不在发现页 → 走完整前置流程")
    try:
        login_op.run_pre_login_flow()
    except Exception as e:
        logger.warning(f"[ensure_ready] 前置流程部分失败（不影响）: {e}")

    # 3. 切到「发现」首页
    try:
        first_page_op.click_discover_tab()
    except Exception as e:
        logger.warning(f"[ensure_ready] 切发现 Tab 失败（可能已在发现页）: {e}")


def build_fuwu_op(driver: WebDriver, logger: Any) -> FuwuOperate:
    """构造服务操作实例，前置 ensure_ready 把 APP 拉到发现页。"""
    login_op, first_page_op = build_ops(driver, logger)
    ensure_ready(login_op, first_page_op, logger)
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    return FuwuOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )


def build_fuwu_op_keep(driver: WebDriver, logger: Any) -> FuwuOperate:
    """构造服务操作实例，不做 ensure_ready 直接复用当前页面。

    用例 16~20 跟在用例 15 之后跑时，APP 已在服务 Tab，强行 ensure_ready
    会因为"推荐 Tab 不可见"被判定为未在发现页，触发冷启动前置流程失败。
    本函数只构造实例，不动页面状态，把"是否在服务页"交给 click_fuwu_tab 内部断言。
    """
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    return FuwuOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )


def build_buycar_op(driver: WebDriver, logger: Any) -> BuycarOperate:
    """构造购车操作实例，前置 ensure_ready 把 APP 拉到发现页。"""
    login_op, first_page_op = build_ops(driver, logger)
    ensure_ready(login_op, first_page_op, logger)
    return BuycarOperate(
        driver, logger,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )
