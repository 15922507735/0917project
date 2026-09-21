"""业务流程测试用例（business_flow）。

按 PO 分层设计，所有用例集中在本文件：
- 用例只调用 LoginOperate / FirstPageOperate / OrderOperate / WebViewOperate /
  SeeCarOperate / ShequOperate 的方法；
- **业务策略**：不强制清除登录。
  * 用例 1 / 2 / 3 业务前提是'未登录'，已登录态 pytest.skip；
  * 用例 5 业务前提是'已登录'（聚合页/立即订购），未登录态 pytest.skip；
  * 用例 6（看车 Tab + Q05）、用例 7（社区 Tab）、用例 8（话题广场）
    **不依赖登录态**——两种状态都跑；
- 用例开始前自动调用 `ensure_ready()` 重置 APP 状态：
  * 探测当前是否已在「发现」首页（first_page_op.is_on_discover_page()），
    判据 = 包名在 APP 内 + 「推荐」二级 Tab 可见；
  * 已在发现页 → 跳过所有前置流程（点协议 / 左滑 / 入口 5 次 / 切发现），
    这正是"已登录 + 热启动后"的稳态；
  * 不在发现页 → 走完整前置流程：点同意 → 左滑 3 → 入口 5 → 兜底再点同意 → 切发现；
- 用例之间不依赖彼此的 APP 状态（任何一个失败不影响下一个）；
- 所有用例共享 session 级 driver fixture。

包含 7 个用例（业务用例 1 / 2 / 3 / 5 / 6 / 7 / 8）：
- test_start_app_and_accept_agreement：冒烟，断言 APP 包名（已登录态 skip）
- test_go_mine_and_logout：回归，进入「我的 → 未登录」（已登录态 skip）
- test_login_with_password：冒烟 + 回归，密码登录完整流程（已登录态 skip）
- test_click_aggregate_btn：回归，点击聚合页 + 立即订购 + 配置选择页 + 返回聚合页（**未登录态 skip**）
- test_click_seecar_btn：回归，点击看车 Tab + Q05 车型入口（**登录/未登录都跑**）
- test_click_shequ_tab：回归，点击社区 Tab + 断言热门话题（**登录/未登录都跑**）
- test_click_topic_square：回归，切社区页 + 点击话题广场（**登录/未登录都跑**）
- test_click_topic_all_page_btn：回归，切社区页 + 点击最新标签（**登录/未登录都跑**）



运行方式：
    python cli.py            # 全部用例
    python cli.py smoke      # 仅冒烟（用例 1 + 3）
    python cli.py regression # 仅回归（用例 2 / 3 + 5 + 6 + 7 + 8）
    python cli.py business   # 仅业务用例
"""
from __future__ import annotations
import os
import time

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate
from object_operation.order_operate import OrderOperate
from object_operation.seecar_operate import SeeCarOperate
from object_operation.webview_operate import WebViewOperate
from object_operation.shequ_operate import ShequOperate
from object_operation.huodong_operate import HuodongOperate
from object_operation.fatie_operate import FatieOperate
from object_operation.fuwu_operate import FuwuOperate

from page_element.login_page import (
    APP_PACKAGE,
    EXPECT_WAIT_TIMEOUT,
)
from page_element.fatie_page import PUBLISH_BUTTON, PUBLISH_SUCCESS_TEXT
from testcase_manage.data.fatie_data import FATIE_DRAFT_DATA


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
    """用例 5：点击聚合页 + 立即订购 + 配置选择页 + 返回聚合页（不点预约试驾）。

    操作步骤：
        1. ensure_ready 重置 APP 状态：
           - 若 APP 已在「发现」首页（已登录 + 热启动后的稳态）→ 跳过全部前置流程；
           - 若不在发现页 → 走完整前置流程（点同意 / 左滑 / 入口 5 / 兜底再点同意）；
        2. OrderOperate 内部完成：点击聚合页 + 处理位置授权 + 等待「立即订购」按钮；
        3. 点击「立即订购」按钮，自动切到 WebView 并等待「配置选择」页加载完成；
        4. 点击「配置选择」页 H5 顶部的返回按钮 → 切回 NATIVE_APP context
           → 断言聚合页的「预约试驾」按钮已可见 = 回到聚合页（用例到此结束）。

    业务策略（与用例 1/2/3 互斥）：
        **已登录态才跑**——用例 5 业务前提是"已登录后才能看到聚合页 / 立即订购"。

    断言点：
        - click_aggregate_btn 内部断言「立即订购」按钮 (AGGREGATE_ORDER_BTN) 可见；
        - click_aggregate_order_btn 内部断言 WebView 切 context 成功 + 配置选择页加载完成；
        - click_select_config_back_btn 内部断言切回 NATIVE_APP + 聚合页「预约试驾」按钮可见。
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
    # 点配置选择页面返回按钮 → 切回 NATIVE_APP → 断言已回到聚合页
    order_op.click_select_config_back_btn()
    logger.info("[用例5] 点击聚合页-完成")


# ===================== 用例 6 =====================
@pytest.mark.regression
def test_click_seecar_btn(driver, logger):
    """用例 6：点击「看车」Tab → 点击 Q05 车型入口。

    操作步骤：
        1. ensure_ready 重置 APP 状态（无论登录态都会跑）；
        2. SeeCarOperate.click_entry_btn() → 点击顶部「看车」Tab；
        3. SeeCarOperate.click_q05_icon() → 点击 Q05 车型图标。

    业务策略（与用例 1/2/3 互斥）：
        **未登录也能看到看车 Tab 与车型入口**——本用例不依赖登录态，
        所以**不去判断 is_logged_in_session**（未登录也跑，已登录也跑）。

    断言点：
        - click_entry_btn 内部断言「看车」Tab 可点击；
        - click_q05_icon 内部断言 Q05 图标可点击。
    """
    # 注意：本用例不判断登录态——看车 Tab 与 Q05 车型入口在未登录态也可见。
    # 所以也不需要 `if not is_logged_in_session: pytest.skip(...)`。

    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    seecar_op = SeeCarOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    logger.info("[用例6] 点击看车按钮")
    seecar_op.click_entry_btn()
    logger.info("[用例6] 点击看车按钮-完成")
    seecar_op.click_q05_icon()
    logger.info("[用例6] 点击 Q05 图标-完成")

# ===================== 用例 7 =====================
@pytest.mark.regression
def test_click_shequ_tab(driver, logger, is_logged_in_session):
    """用例 7：点击进入社区 Tab 并断言社区页加载完成。

    操作步骤：
        1. _ensure_ready 重置 APP 状态；
        2. ShequOperate.click_shequ_tab() → 点击底部「社区」Tab + 断言出现热门话题元素。

    业务策略（与用例 1/2/3 互斥）：
        **未登录也能看到社区 Tab**——本用例不依赖登录态，
        所以**不去判断 is_logged_in_session**（未登录也跑，已登录也跑）。

    断言点：
        - click_shequ_tab 内部断言「社区」Tab 可点击；
        - click_shequ_tab 内部断言「热门话题」元素 (HOT_TOPIC) 可见 = 社区页加载完成。
    """
    # 注意：本用例不判断登录态——社区 Tab 与热门话题在未登录态也可见。
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    shequ_op = ShequOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    logger.info("[用例7] 点击社区 Tab 按钮")
    shequ_op.click_shequ_tab()
    logger.info("[用例7] 点击社区 Tab 按钮-完成")


# ===================== 用例 8 =====================
@pytest.mark.regression
def test_click_topic_square(driver, logger, is_logged_in_session):
    """用例 8：点击话题广场按钮。

    操作步骤：
        1. _ensure_ready 重置 APP 状态；
        2. ShequOperate.click_shequ_tab() → 切到「社区」页；
        3. ShequOperate.click_topic_square() → 点击话题广场按钮。

    业务策略：
        **未登录也能看到话题广场按钮**——本用例不依赖登录态，
        所以不去判断 is_logged_in_session（未登录也跑，已登录也跑）。

    断言点：
        - click_shequ_tab 内部断言社区页加载完成（热门话题元素可见）；
        - click_topic_square 内部断言话题广场按钮可点击。
    """
    # 本用例不判断登录态——话题广场按钮在未登录态也可见。
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    # click_topic_square 内部会切 WebView，需传入 WebViewOperate
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    shequ_op = ShequOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )
    logger.info("[用例8] 点击话题广场按钮")
    shequ_op.click_shequ_tab()
    shequ_op.click_topic_square()
    logger.info("[用例8] 点击话题广场按钮-完成")
    shequ_op.click_topic_back_btn()
    logger.info("[用例8] 点击话题列表返回按钮-完成")
    shequ_op.click_topic_more_btn()
    logger.info("[用例8] 点击查看更多按钮-完成")
# ===================== 用例 9 =====================
@pytest.mark.regression
def test_click_topic_all_page_btn(driver, logger, is_logged_in_session):
    # 方案A：不调 _ensure_ready —— 用例 8 最后一步已停在"所有圈子" WebView 页，
    # 本用例直接在该页面操作，无需（也不能）回发现页，否则会误走前置流程。
    # 注意：必须紧接用例 8 之后运行。
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    shequ_op = ShequOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )
    logger.info("[用例9] 点击所有圈子列表页面地域标签按钮")
    """用例 9：点击所有圈子列表页面地域标签按钮。"""
    # 点击所有圈子列表页面地域标签按钮
    shequ_op.click_topic_all_page_btn()
    logger.info("[用例9] 点击所有圈子列表页面地域标签按钮-完成")
    # 点击返回按钮
    shequ_op.click_topic_all_back_btn()
    logger.info("[用例9] 点击所有圈子列表页面返回按钮-完成")
    # 点击返回，出现热门话题元素，则表示成功
# ===================== 用例 10 =====================
@pytest.mark.regression
def test_click_topic_neirong(driver, logger, is_logged_in_session):
    """用例 10：点击社区内容标签-最新、视频、关注、聊天。

    本用例不依赖用例 9 状态，自带导航：
      _ensure_ready → 切社区 Tab → 点最新/视频/关注/聊天 → 返回。
    4 个 Tab 元素都是原生（id/tv_tab + 文本），不需要 WebView。
    """
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    shequ_op = ShequOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)

    logger.info("[用例10] 点击社区内容标签-最新、视频、关注、聊天")
    # 先切到社区页（社区 Tab 在发现页底部）
    shequ_op.click_shequ_tab()
    # 点击社区内容标签-最新
    shequ_op.click_shequ_neirong_new()
    logger.info("[用例10] 点击社区内容标签-最新-完成")
    # 点击视频标签
    shequ_op.click_topic_all_video_btn()
    logger.info("[用例10] 点击视频标签-完成")
    # 点击关注标签
    shequ_op.click_topic_all_follow_btn()
    logger.info("[用例10] 点击关注标签-完成")
    # 点击聊天标签
    shequ_op.click_topic_all_chat_btn()
    logger.info("[用例10] 点击聊天标签-完成")
    # 点击返回按钮
    shequ_op.click_topic_all_chat_back_btn()
    logger.info("[用例10] 点击聊天列表返回按钮-完成")
# ===================== 用例 11 =====================
@pytest.mark.regression
def test_click_huodong_status(driver, logger, is_logged_in_session):
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    huodong_op = HuodongOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    """用例 11：点击活动状态按钮。"""
    # 点击活动 Tab 按钮
    huodong_op.click_huodong_tab()
    logger.info("[用例11] 点击活动 Tab 按钮-完成")
    # 点击活动状态按钮
    huodong_op.select_huodong_status()
    logger.info("[用例11] 点击活动状态按钮-完成")
    # 点击确定按钮
    huodong_op.click_huodong_confirm_btn()
    logger.info("[用例11] 点击确定按钮-完成")
# ===================== 用例 12 =====================
@pytest.mark.regression
def test_click_post_button(driver, logger, is_logged_in_session):
    """用例 12：点击发帖入口按钮。"""
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)

    # 切回 NATIVE_APP（避免上一个用例残留 WebView context）
    try:
        driver.switch_to.context("NATIVE_APP")
    except Exception:
        pass

    # 构造 FatieOperate（依赖 WebViewOperate 才能切 context）
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    fatie_op = FatieOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )
    try:
        # 点击发帖入口按钮
        fatie_op.click_post_button()
        logger.info("[用例12] 点击发帖入口按钮-完成")
        # 点击发文章按钮
        fatie_op.click_post_article_button()
        # 切换到发文章编辑页面的webview
        fatie_op.switch_to_post_article_webview()
        logger.info("[用例12] 点击发文章按钮-完成")
        # 断言页面加载完成，发布按钮元素可见
        WebDriverWait(driver, EXPECT_WAIT_TIMEOUT).until(
            EC.presence_of_element_located(PUBLISH_BUTTON)
        )
        logger.info("[用例12] 断言页面加载完成，发布按钮元素存在-完成")
    finally:
        # 收口：无论用例是否成功，都切回 NATIVE_APP context
        # 避免下一个用例在错的 context 下启动
        _fatie_native_reset(driver, logger)


def _fatie_native_reset(driver, logger) -> None:
    """收口工具：把 driver 切回 NATIVE_APP，必要时按返回键回到发现页。

    给"发帖流程"相关用例的 finally 块使用，避免：
    1. WebView context 残留污染下一个用例
    2. APP 停在发文章 WebView 页，丢失原生入口
    """
    # 1. 强制切回 NATIVE
    try:
        if "NATIVE_APP" in driver.contexts:
            driver.switch_to.context("NATIVE_APP")
            logger.info("[fatie_reset] 已切回 NATIVE_APP context")
    except Exception as e:
        logger.warning(f"[fatie_reset] 切回 NATIVE 失败: {e.__class__.__name__}: {e}")
        return

    # 2. 如果 APP 还在发文章 WebView 页（不在 QYMainActivity），按返回键退出
    max_back = 5
    for i in range(max_back):
        try:
            activity = driver.current_activity or ""
        except Exception:
            break
        if "QYMainActivity" in activity:
            logger.info(f"[fatie_reset] 已回到 QYMainActivity（用 {i} 次返回）")
            break
        driver.back()
        time.sleep(0.5)
    else:
        logger.warning(f"[fatie_reset] 连续按了 {max_back} 次返回，仍未回到 QYMainActivity")
# ===================== 用例 13 =====================
# 默认跳过（真实发布会污染测试数据）；设 RUN_PUBLISH=1 启用：RUN_PUBLISH=1 pytest -k test_click_fatie
@pytest.mark.skipif(
    os.getenv("RUN_PUBLISH") != "1",
    reason="用例13会真实发布文章，污染测试数据；用例14已替代数据驱动验证场景。"
           "设环境变量 RUN_PUBLISH=1 启用。",
)
@pytest.mark.regression
def test_click_fatie(driver, logger, is_logged_in_session):
    """用例 13：发帖完整流程（含上传封面）。

    自带导航（不依赖用例 12 状态）：
      1. _ensure_ready → 切社区 Tab → 点发帖入口 → 点发文章 → 切 WebView
      2. 点上传封面按钮 → 切回原生 → 点选择图片 → 授权 → 勾选图片
    """
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)

    login_op, first_page_op = _build_ops(driver, logger)
    # 用例 13 兜底：先把 driver 切回 NATIVE + APP 拉回主 Activity
    # （避免上个用例残留 WebView context / 相册选择器等导致 is_on_discover 误判）
    try:
        if "NATIVE_APP" in driver.contexts:
            driver.switch_to.context("NATIVE_APP")
    except Exception as e:
        logger.warning(f"[用例13] 切回 NATIVE 失败: {e.__class__.__name__}")

    # 如果 APP 还在错的 Activity（如 PictureSelectorActivity），按返回键回到主 Activity
    for _ in range(5):
        try:
            activity = driver.current_activity or ""
        except Exception:
            break
        if "QYMainActivity" in activity:
            break
        driver.back()
        time.sleep(0.5)

    _ensure_ready(login_op, first_page_op, logger)
    # 切回 NATIVE_APP（避免上一个用例残留 WebView context）
    try:
        driver.switch_to.context("NATIVE_APP")
    except Exception:
        pass

    fatie_op = FatieOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )

    logger.info("[用例13] 完整发帖流程开始")
    # 1. 走到发文章页面
    fatie_op.click_post_button()
    fatie_op.click_post_article_button()
    fatie_op.switch_to_post_article_webview()
    logger.info("[用例13] 已进入发文章 WebView 页面")

    # 2. 点击上传封面按钮
    fatie_op.click_upload_cover_button()
    logger.info("[用例13] 点击上传封面按钮-完成")
    # 3. 切换到native_app页面（系统相册选择器）
    webview_op.switch_to_native()
    logger.info("[用例13] 切换到native_app页面-完成")
    # 4. 点击选择图片按钮
    fatie_op.click_select_image_button()
    logger.info("[用例13] 点击选择图片按钮-完成")
    # 5. 点击授权允许按钮（如果出现）
    fatie_op.click_permission_allow_button()
    logger.info("[用例13] 点击授权允许按钮-完成")
    # 6. 点击勾选图片按钮（image_index: 1=第一张, 2=第二张, ...）
    fatie_op.click_gouxuan_image_button()
    logger.info("[用例13] 点击勾选图片按钮-完成")
    # 7. 点击已完成按钮
    fatie_op.click_confirm_gouxuan_image_button()
    logger.info("[用例13] 点击已完成按钮-完成")
    # 8. 点击封面图片确认按钮
    fatie_op.click_confirm_cover_image_button()
    logger.info("[用例13] 点击封面图片确认按钮-完成")
    # 9. 点击标题输入框
    fatie_op.click_title_input()
    logger.info("[用例13] 点击标题输入框，并输入标题-完成")
    # 点击内容输入框
    fatie_op.click_content_input()
    logger.info("[用例13] 点击内容输入框，并输入内容-完成")
    # 点击内容图片上传按钮
    fatie_op.click_content_image_button()
    logger.info("[用例13] 点击内容图片上传按钮-完成")
    # 10. 点击内容图片选择按钮-弹窗
    fatie_op.click_select_content_image_button()
    logger.info("[用例13] 点击内容图片选择按钮-弹窗-完成")
    # 10.5 相册里勾选图片（与封面流程一致）
    fatie_op.click_gouxuan_image_button()
    logger.info("[用例13] 相册里勾选图片-完成")
    # 10.6 点"已完成"按钮回到 H5
    fatie_op.click_confirm_gouxuan_image_button()
    logger.info("[用例13] 点击已完成按钮-完成")
    # 11. 点击确定选择按钮-弹窗
    fatie_op.click_confirm_queding_image_button()
    logger.info("[用例13] 点击确定选择按钮-弹窗-完成")
    # 12. 点击发布按钮
    fatie_op.click_publish_button()
    logger.info("[用例13] 点击发布按钮-完成")

# ===================== 用例 14 =====================
@pytest.fixture
def fatie_op(driver, logger):
    """用例14构造发帖操作实例（共享 webview 切换能力）。"""
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    return FatieOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )


def _navigate_to_fatie_editor(driver, logger, fatie_op):
    """用例14：把 APP 导航到发帖编辑页（WebView）。"""
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)
    try:
        driver.switch_to.context("NATIVE_APP")
    except Exception:
        pass
    fatie_op.click_post_button()
    fatie_op.click_post_article_button()
    fatie_op.switch_to_post_article_webview()


@pytest.mark.parametrize(
    "case_id, title, content_text, expected_keyword",
    FATIE_DRAFT_DATA,
    ids=[d[0] for d in FATIE_DRAFT_DATA],
)
@pytest.mark.regression
def test_fatie_input_draft(
    driver, logger, is_logged_in_session, fatie_op,
    case_id, title, content_text, expected_keyword,
):
    """用例14：数据驱动：发帖标题 + 富文本内容输入。"""
    _navigate_to_fatie_editor(driver, logger, fatie_op)
    try:
        fatie_op.click_title_input(title)
        logger.info(f"[{case_id}] 输入标题完成: {title}")
        fatie_op.click_content_input(content_text, expected_keyword)
        logger.info(f"[{case_id}] 输入内容 + 断言关键字 '{expected_keyword}' 通过")
    finally:
        _fatie_native_reset(driver, logger)
        # 切到发现 Tab，避免用例 15 找不到"服务"Tab
        fatie_op.back_to_discover_page()
    
    
    
# ===================== 用例 15-20：服务模块拆分用例 =====================


def _build_fuwu_op(driver, logger):
    """构造服务操作实例，前置 _ensure_ready 把 APP 拉到发现页。"""
    login_op, first_page_op = _build_ops(driver, logger)
    _ensure_ready(login_op, first_page_op, logger)
    webview_op = WebViewOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)
    return FuwuOperate(
        driver, logger, webview_operate=webview_op,
        expect_wait_timeout=EXPECT_WAIT_TIMEOUT,
    )


# ===================== 用例 15：点击服务 Tab =====================
@pytest.mark.regression
def test_click_fuwu_tab(driver, logger, is_logged_in_session):
    """用例15：点击底部"服务"Tab，断言服务页面加载完成（出现"门店"文本）。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    logger.info("[用例15] 点击服务 Tab-完成")


# ===================== 用例 16：点击门店 =====================
@pytest.mark.regression
def test_click_store_btn(driver, logger, is_logged_in_session):
    """用例16：在服务首页点击门店按钮，断言门店详情页加载（出现位置按钮）。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    fuwu_op.click_store_btn()
    logger.info("[用例16] 点击门店按钮-完成")


# ===================== 用例 17：点击门店详情位置按钮 =====================
@pytest.mark.regression
def test_click_store_address_btn(driver, logger, is_logged_in_session):
    """用例17：点击门店详情位置按钮，断言弹窗加载（出现"确定"按钮）。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    fuwu_op.click_store_btn()
    fuwu_op.click_store_address_btn()
    logger.info("[用例17] 点击门店详情位置按钮-完成")


# ===================== 用例 18：点击位置弹窗确定按钮 =====================
@pytest.mark.regression
def test_click_store_address_btn_submit(driver, logger, is_logged_in_session):
    """用例18：点击位置弹窗的确定按钮，断言弹窗关闭。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    fuwu_op.click_store_btn()
    fuwu_op.click_store_address_btn()
    fuwu_op.click_store_address_btn_submit()
    logger.info("[用例18] 点击位置弹窗确定按钮-完成")


# ===================== 用例 19：门店详情→交付→维保→返回 =====================
@pytest.mark.regression
def test_click_store_deliver_maint_back(driver, logger, is_logged_in_session):
    """用例19：门店详情页 → 收起 → 交付中心 → 维保中心 → 返回到门店列表。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    fuwu_op.click_store_btn()
    fuwu_op.click_store_search_btn()
    logger.info("[用例19] 点击门店收起展开按钮-完成")
    fuwu_op.click_store_deliver_btn()
    logger.info("[用例19] 点击交付中心按钮-完成")
    fuwu_op.click_store_maint_btn()
    logger.info("[用例19] 点击维护中心按钮-完成")
    fuwu_op.click_store_back_btn()
    logger.info("[用例19] 点击门店详情返回按钮-完成")


# ===================== 用例 20：服务首页→滑动→家充服务→返回 =====================
@pytest.mark.regression
def test_click_store_charge(driver, logger, is_logged_in_session):
    """用例20：服务首页 → 上滑 → 点家充服务 → 返回。"""
    fuwu_op = _build_fuwu_op(driver, logger)
    fuwu_op.click_fuwu_tab()
    fuwu_op.swipe_up()
    logger.info("[用例20] 滑动成功-完成")
    fuwu_op.click_store_charge_btn()
    logger.info("[用例20] 点击家充服务按钮-完成")
    fuwu_op.click_store_charge_back_btn()
    logger.info("[用例20] 点击家充装返回按钮-完成")



    