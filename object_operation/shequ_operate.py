"""社区页 操作封装。"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.shequ_page import (
    HOT_TOPIC,
    SHEQU_TAB,
    TOPIC_SQUARE_BTN,
    TOPIC_BACK_BTN,
    TOPIC_TITLE,
    TOPIC_MORE_BTN,
    TOPIC_ALL_BACK_BTN,
    TOPIC_ALL_REGION_BTN,
    TOPIC_ALL_REGION_CONTENT,
)


class ShequOperate:
    """社区页 操作封装。"""

    def __init__(
        self,
        driver: WebDriver,
        logger: Any,
        webview_operate: Any = None,
        expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT,
    ):
        self.driver = driver
        self.logger = logger
        self.webview_operate = webview_operate
        self.expect_wait_timeout = expect_wait_timeout

    def click_shequ_tab(self) -> None:
        """点击社区 Tab 按钮并断言社区页加载完成（出现热门话题元素）。"""
        # 1. 点社区 Tab
        self.driver.find_element(*SHEQU_TAB).click()
        self.logger.info("点击社区 Tab 按钮")

        # 2. 断言社区页加载完成
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(HOT_TOPIC)
        )
        self.logger.info("社区页加载完成,出现热门话题元素")

    def click_topic_square(self) -> None:
        """点击「话题广场」按钮（社区页内的二级入口）。
        """
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(TOPIC_SQUARE_BTN)
            ).click()
            self.logger.info("已点击话题广场按钮")
        except Exception as e:
            self.logger.error(
                f"点击话题广场按钮失败: {e}, "
                f"Activity={self.driver.current_activity}"
            )
            raise
        # 等话题广场页异步加载
        sleep(1)
        self.logger.info("已等待 1s 让话题广场页加载完成")

        # 切到 WebView context
        self.webview_operate.switch_to_webview()
        self.logger.info("已切换到 WebView context")
        # 打印 url + title
        try:
            self.logger.info(
                f"当前 WebView url: {self.driver.current_url}, "
                f"title: {self.driver.title}"
            )
        except Exception as e:
            self.logger.error(
                f"获取当前 WebView url + title 失败: {e}, "
                f"Activity={self.driver.current_activity}"
            )
            raise
        # 断言话题广场页加载完成（出现话题列表页面标题）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(TOPIC_TITLE)
        )
        self.logger.info("话题广场页加载完成,出现话题列表页面标题")

    def click_topic_back_btn(self) -> None:
        # 点击话题列表返回按钮
        self.logger.info("点击话题列表返回按钮")
        self.driver.find_element(*TOPIC_BACK_BTN).click()
        self.logger.info("已点击话题列表返回按钮")

        # 切回native app 页面
        self.webview_operate.switch_to_native()
        self.logger.info("已切换回native app 页面")

    def click_topic_more_btn(self) -> None:
        # 点击查看更多按钮
        self.logger.info("点击查看更多按钮")
        self.driver.find_element(*TOPIC_MORE_BTN).click()
        self.logger.info("已点击查看更多按钮")
    # 所有圈子页面操作流程
    def click_topic_all_page_btn(self) -> None:
        """在"所有圈子"页点击「地域」标签并断言省份圈子列表出现。

        前置：用例 8 最后一步点"查看更多"已打开 circle-more WebView，
        但 driver context 仍为 NATIVE_APP，故这里先切到 WebView。
        """
        # 切到 WebView context（已在 WebView 时切换是幂等的）
        self.webview_operate.switch_to_webview()

        # 点击地域标签
        self.logger.info("点击所有圈子列表页面地域标签按钮")
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(TOPIC_ALL_REGION_BTN)
        ).click()
        self.logger.info("已点击所有圈子列表页面地域标签按钮")

        # 断言地域 tab 选中（class=active）且出现省份圈子（广东省/重庆）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(TOPIC_ALL_REGION_CONTENT)
        )
        self.logger.info("已断言地域标签选中，页面出现广东省/重庆等省份圈子")

    def click_topic_all_back_btn(self) -> None:
        """点击"所有圈子"页顶部返回按钮 → 切回 NATIVE_APP → 断言回到社区页。"""
        # WebView 内点返回
        self.logger.info("点击所有圈子列表页面返回按钮")
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(TOPIC_ALL_BACK_BTN)
        ).click()
        self.logger.info("已点击所有圈子列表页面返回按钮")

        # 切回 native app 页面
        self.webview_operate.switch_to_native()
        self.logger.info("已切换回native app 页面")

        # 返回社区页：出现热门话题元素则表示成功
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(HOT_TOPIC)
        )
        self.logger.info("已断言点击返回，出现热门话题元素，则表示成功")
        


 
