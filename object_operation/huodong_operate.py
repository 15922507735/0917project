"""活动页操作层。"""
from __future__ import annotations
from time import sleep
from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from page_element.login_page import EXPECT_WAIT_TIMEOUT

from page_element.huodong_page import(
    HUODONG_TAB,
    HUODONG_LIST,
    HUODONG_STATUS,
    SELECT_HUODONG_STATUS_BTN,
    HUODONG_CONFIRM_BTN,
)

class HuodongOperate:
    """活动页 操作封装。"""

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

    # ===================== 活动页 =====================
    def click_huodong_tab(self):
        """点击活动 Tab 按钮。"""
        # 点击活动按钮
        self.driver.find_element(*HUODONG_TAB).click()
        # 等待活动列表页面加载完成，活动列表元素可见
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.visibility_of_element_located(HUODONG_LIST)
        )

    # 进行活动状态选择
    def select_huodong_status(self):
        """选择活动状态。"""
        # 点击活动状态按钮
        self.driver.find_element(*HUODONG_STATUS).click()
        # 等待状态选择弹窗加载完成，选择状态元素可见
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.visibility_of_element_located(SELECT_HUODONG_STATUS_BTN)
        )
        # 点击确定按钮
    def click_huodong_confirm_btn(self):
        """点击确定按钮。"""
        self.driver.find_element(*HUODONG_CONFIRM_BTN).click()
        """等待状态选择弹窗关闭。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.invisibility_of_element_located(SELECT_HUODONG_STATUS_BTN)
        )

       


        
