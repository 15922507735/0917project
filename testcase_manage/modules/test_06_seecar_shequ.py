"""看车 / 社区 / 话题（用例 6-10）。

- test_click_seecar_btn（用例 6）：回归，点击看车 Tab + Q05 车型入口（**登录/未登录都跑**）
- test_click_shequ_tab（用例 7）：回归，点击社区 Tab + 断言热门话题（**登录/未登录都跑**）
- test_click_topic_square（用例 8）：回归，切社区页 + 点击话题广场（**登录/未登录都跑**）
- test_click_topic_all_page_btn（用例 9）：回归，所有圈子地域标签
- test_click_topic_neirong（用例 10）：社区内容标签切换
"""
from __future__ import annotations

import pytest

from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate
from object_operation.seecar_operate import SeeCarOperate
from object_operation.shequ_operate import ShequOperate
from object_operation.webview_operate import WebViewOperate

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from utils.test_helpers import (
    build_ops as _build_ops,
    ensure_ready as _ensure_ready,
)


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
def test_click_shequ_tab(driver, logger):
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
def test_click_topic_square(driver, logger):
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
def test_click_topic_all_page_btn(driver, logger):
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
def test_click_topic_neirong(driver, logger):
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
