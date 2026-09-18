"""社区页 操作封装。"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.shequ_page import HOT_TOPIC, SHEQU_TAB, TOPIC_SQUARE_BTN


class ShequOperate:
    """社区页 操作封装。"""

    def __init__(
        self,
        driver: WebDriver,
        logger: Any,
        expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT,
    ):
        self.driver = driver
        self.logger = logger
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

        前置：APP 处于社区页（由 click_shequ_tab 保证）。
        元素定位 TOPIC_SQUARE_BTN 当前为占位（id=tvht，与 HOT_TOPIC 相同），
        实际跑出后用 Inspector 拿到真实 id 再调整。
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
