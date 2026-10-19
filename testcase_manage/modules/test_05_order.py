"""订单 / WebView（用例 5）。

- test_click_aggregate_btn（用例 5）：回归，点击聚合页 + 立即订购 + 配置选择页 + 返回聚合页（**未登录态 skip**）
"""
from __future__ import annotations

import pytest

from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate
from object_operation.order_operate import OrderOperate
from object_operation.webview_operate import WebViewOperate

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from utils.test_helpers import (
    build_ops as _build_ops,
    ensure_ready as _ensure_ready,
)


# ===================== 用例 5 =====================
@pytest.mark.regression
def test_click_aggregate_btn(driver, logger):
    """用例 5：点击聚合页 + 立即订购 + 配置选择页 + 返回聚合页（不点预约试驾）。

    操作步骤：
        1. ensure_ready 重置 APP 状态：
           - 若 APP 已在「发现」首页（已登录 + 热启动后的稳态）→ 跳过全部前置流程；
           - 若不在发现页 → 走完整前置流程（点同意 / 左滑 / 入口 5 / 兜底再点同意）；
        2. OrderOperate 内部完成：点击聚合页 + 处理位置授权 + 等待「立即订购」按钮；
        3. 点击「立即订购」按钮，自动切到 WebView 并等待「配置选择」页加载完成；
        4. 点击「配置选择」页 H5 顶部的返回按钮 → 切回 NATIVE_APP context
           → 断言聚合页的「预约试驾」按钮已可见 = 回到聚合页（用例到此结束）。

    业务策略：
        用例 3 紧接跑本用例时，APP 已是登录后 → 正常跑主体。
        如果用例 5 单独跑（前面没登录）→ 由用例内部断言"找不到立即订购"自然 FAILED。
        （注：原版依赖 session 级 is_logged_in_session，但 session fixture 在 driver 启动时就
         探测一次，之后用例 3 的登录状态不会被刷新，导致误判"未登录"skip。）

    断言点：
        - click_aggregate_btn 内部断言「立即订购」按钮 (AGGREGATE_ORDER_BTN) 可见；
        - click_aggregate_order_btn 内部断言 WebView 切 context 成功 + 配置选择页加载完成；
        - click_select_config_back_btn 内部断言切回 NATIVE_APP + 聚合页「预约试驾」按钮可见。
    """
    login_op, first_page_op = _build_ops(driver, logger)
    # 已在发现页时 _ensure_ready 会直接 return（不点协议 / 不左滑 / 不点入口 5 次），
    # 避免重复冷启动导致死循环。
    _ensure_ready(login_op, first_page_op, logger)

    # 构造 OrderOperate（依赖 WebViewOperate）
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    order_op = OrderOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )

    logger.info("[用例5] 点击聚合页")
    # 兜底再点一次发现 Tab（_ensure_ready 末尾已切过一次）
    try:
        first_page_op.click_discover_tab()
    except Exception as e:
        logger.warning(f"[用例5] 切发现 Tab 失败（可能已在发现页）: {e}")
    order_op.click_aggregate_btn()
    # 点击立即订购按钮（自动切到 WebView 并等待「配置选择」页加载完成）
    order_op.click_aggregate_order_btn()
    # 点配置选择页面返回按钮 → 切回 NATIVE_APP → 断言已回到聚合页
    order_op.click_select_config_back_btn()
    logger.info("[用例5] 点击聚合页-完成")
