"""发帖（用例 12-14）。

- test_click_post_button（用例 12）：发帖入口 + 发文章
- test_click_fatie（用例 13）：发帖完整流程（含上传封面/内容图，默认 skip；设 `RUN_PUBLISH=1` 启用）
- test_fatie_input_draft（用例 14）：数据驱动：标题 + 富文本内容

注：模块内共享 `fatie_op` fixture 与 `_fatie_native_reset` 收口函数，
    强状态链：13→14 复用 driver 状态；14 的 finally 主动回到发现页，避免污染用例 15。
"""
from __future__ import annotations

import allure

import os
import time

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from object_operation.fatie_operate import FatieOperate
from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate
from object_operation.webview_operate import WebViewOperate

from page_element.fatie_page import PUBLISH_BUTTON
from page_element.login_page import EXPECT_WAIT_TIMEOUT
from testcase_manage.data.fatie_data import FATIE_DRAFT_DATA
from utils.test_helpers import (
    build_ops as _build_ops,
    ensure_ready as _ensure_ready,
)


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


# ===================== 用例 12 =====================
@allure.feature("发帖模块")
@allure.story("发帖入口 / 发文章")
@pytest.mark.feature_fatie
@pytest.mark.story_postentry
@pytest.mark.regression
def test_click_post_button(driver, logger):
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


# ===================== 用例 13 =====================
# 默认跳过（真实发布会污染测试数据）；设 RUN_PUBLISH=1 启用：RUN_PUBLISH=1 pytest -k test_click_fatie
@pytest.mark.skipif(
    os.getenv("RUN_PUBLISH") != "1",
    reason="用例13会真实发布文章，污染测试数据；用例14已替代数据驱动验证场景。"
           "设环境变量 RUN_PUBLISH=1 启用。",
)
@allure.feature("发帖模块")
@allure.story("完整发帖（含上传封面/内容图）")
@pytest.mark.feature_fatie
@pytest.mark.story_fatiefull
@pytest.mark.regression
def test_click_fatie(driver, logger):
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
@allure.feature("发帖模块")
@allure.story("数据驱动 - 标题 / 富文本内容")
@pytest.mark.feature_fatie
@pytest.mark.story_fatieinput
@pytest.mark.regression
def test_fatie_input_draft(
    driver, logger, fatie_op,
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
