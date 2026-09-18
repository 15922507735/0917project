"""业务流程测试用例（business_flow）。

按 PO 分层设计，所有用例集中在本文件：
- 用例只调用 LoginOperate / FirstPageOperate / OrderOperate / WebViewOperate 的方法；
- **业务策略**：不强制清除登录。如果当前 APP 已登录（已在发现页），
  用例 1 / 2 / 3 全部 pytest.skip，只让用例 5（点击聚合页 + 立即订购）跑主体；
- 用例开始前自动调用 `ensure_ready()` 重置 APP 状态：
  * 探测当前是否已在「发现」首页（first_page_op.is_on_discover_page()），
    判据 = 包名在 APP 内 + 「推荐」二级 Tab 可见；
  * 已在发现页 → 跳过所有前置流程（点协议 / 左滑 / 入口 5 次 / 切发现），
    这正是"已登录 + 热启动后"的稳态；
  * 不在发现页 → 走完整前置流程：点同意 → 左滑 3 → 入口 5 → 兜底再点同意 → 切发现；
- 用例之间不依赖彼此的 APP 状态（任何一个失败不影响下一个）；
- 所有用例共享 session 级 driver fixture。

包含 4 个用例（业务用例 1 / 2 / 3 / 5）：
- test_start_app_and_accept_agreement：冒烟，断言 APP 包名（已登录态 skip）
- test_go_mine_and_logout：回归，进入「我的 → 未登录」（已登录态 skip）
- test_login_with_password：冒烟 + 回归，密码登录完整流程（已登录态 skip）
- test_click_aggregate_btn：回归，点击聚合页 + 立即订购 + WebView（**已登录态才跑**）

运行方式：
    python cli.py            # 全部用例
    python cli.py smoke      # 仅冒烟（用例 1 + 3）
    python cli.py regression # 仅回归（用例 2 / 3 + 5）
    python cli.py business   # 仅业务用例
"""
from __future__ import annotations

import pytest

from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate
from object_operation.order_operate import OrderOperate
from object_operation.webview_operate import WebViewOperate
from page_element.login_page import (
    APP_PACKAGE,
    EXPECT_WAIT_TIMEOUT,
)


# ===================== 共享：构造 operate 实例 =====================
def _build_ops(driver, logger):
    """根据 session 级 driver 构造 LoginOperate / FirstPageOperate。"""
    login_op = LoginOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    first_page_op = FirstPageOperate(
        driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT
    )
    return login_op, first_page_op


def _ensure_ready(login_op, first_page_op, logger) -> None:
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


# ===================== 用例 1 =====================
@pytest.mark.smoke
def test_start_app_and_accept_agreement(driver, logger, is_logged_in_session):
    """用例 1：验证 Appium session 已就绪 + 包名 / Activity 断言（冒烟）。

    业务背景：
        conftest.py 的 driver fixture 已启动 Appium session。
        本用例断言 current_package 等于 APP_PACKAGE，作为冒烟用例。

    业务策略：
        已登录（已在发现页）→ skip，只让用例 5 跑主体。

    断言点：
        - driver.current_package == "com.changan.oushangCos1"
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 1 仅做未登录态下的包名断言，让用例 5 跑主体")

    logger.info(f"[用例1] 当前 Activity: {driver.current_activity}")
    logger.info(f"[用例1] 当前包名: {driver.current_package}")
    assert driver.current_package == APP_PACKAGE, (
        f"期望当前包名 {APP_PACKAGE}, 实际 {driver.current_package}"
    )


# ===================== 用例 2 =====================
@pytest.mark.regression
def test_go_mine_and_logout(driver, logger, is_logged_in_session):
    """用例 2：进入「我的」Tab 并打开「未登录」入口。

    操作步骤：
        1. ensure_ready 重置 APP 状态；
        2. 点击底部 Tab「我的」 → 进入「我的」页面；
        3. 点击「未登录」入口按钮 → 进入登录方式选择页。

    业务策略：
        已登录（已在发现页）→ skip（"未登录"入口不存在）。

    断言点：
        - 点完「未登录」后，密码登录切换按钮 (GO_PASSLOGIN_BTN) 出现
          （由 click_loginout_btn 内部断言）。
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 2 业务前提是'未登录'，让用例 5 跑主体")

    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    logger.info("[用例2] 进入我的-未登录")
    login_op.click_my_btn()
    login_op.click_loginout_btn()


# ===================== 用例 3 =====================
@pytest.mark.smoke
@pytest.mark.regression
def test_login_with_password(driver, logger, is_logged_in_session):
    """用例 3：使用「手机号 + 密码 + 图形验证码」登录已注册账号。

    操作步骤：
        1. ensure_ready 重置 APP 状态；
        2. 点击「密码登录」切换按钮；
        3. 输入手机号 / 密码 / 验证码 / 勾选协议 / 提交登录；
        4. 登录成功后切到「发现 → 推荐」二级 Tab 并上滑一次。

    业务策略：
        已登录（已在发现页）→ skip（"密码登录"入口不存在）。

    断言点：
        - 登录成功后 driver.find_element(LOGINING_BTN) 找到昵称元素。
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 3 业务前提是'未登录'，让用例 5 跑主体")

    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    logger.info("[用例3] 密码登录完整流程")
    login_op.click_go_passlogin_btn()
    login_op.input_phone()
    login_op.input_password()
    login_op.input_captcha()
    login_op.click_agreement()  # 勾选同意协议
    login_op.click_login_btn()

    # 登录成功后切到「发现 → 推荐」二级 Tab
    first_page_op.click_discover_tab()
    first_page_op.click_recommend_btn()  # 切换到「推荐」Tab
    first_page_op.swipe_up_recommend()  # 上滑推荐页面，等待列表稳定


# ===================== 用例 5 =====================
@pytest.mark.regression
def test_click_aggregate_btn(driver, logger, is_logged_in_session):
    """用例 5：点击聚合页按钮，处理位置授权弹窗，点击立即订购按钮。

    操作步骤：
        1. ensure_ready 重置 APP 状态：
           - 若 APP 已在「发现」首页（已登录 + 热启动后的稳态）→ 跳过全部前置流程；
           - 若不在发现页 → 走完整前置流程（点同意 / 左滑 / 入口 5 / 兜底再点同意）；
        2. OrderOperate 内部完成：点击聚合页 + 处理位置授权 + 等待「立即订购」按钮；
        3. 点击「立即订购」按钮，自动切到 WebView 并等待「配置选择」页加载完成。

    业务策略（与用例 1/2/3 互斥）：
        **已登录态才跑**——用例 5 业务前提是"已登录后才能看到聚合页 / 立即订购"。

    断言点：
        - click_aggregate_btn 内部断言「立即订购」按钮 (AGGREGATE_ORDER_BTN) 可见；
        - click_aggregate_order_btn 内部断言 WebView 切 context 成功 + 配置选择页加载完成。
    """
    if not is_logged_in_session:
        pytest.skip("未登录态：用例 5 业务前提是'已登录'，请先登录再跑")

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
    # 不切回 NATIVE_APP，保持 WebView context —— 调用方可以继续操作 H5 元素
