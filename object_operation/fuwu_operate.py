"""服务模块操作。"""

from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from object_operation.webview_operate import WebViewOperate

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.fuwu_page import (
    FUWU_TAB, 
    STORE_TEXT,
    STORE_BTN,
    STORE_ADDRESS_BTN,
    STORE_ADDRESS_BTN_SUBMIT,
    STORE_SEARCH_INPUT,
    STORE_SEARCH_BTN,
    STORE_DELIVER_BTN,
    STORE_MAINT_BTN,
    STORE_RESERVE_BTN,
    STORE_FAVORITE_BTN,
    )



class FuwuOperate:
    """服务模块操作。"""

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

    def click_fuwu_tab(self):
        """点击服务模块tab。"""
        # 调试：失败时截图，便于排查
        self.driver.save_screenshot("debug_click_fuwu_tab.png")
        self.driver.find_element(*FUWU_TAB).click()
        # 等待服务页面加载完成，出现“门店”文本元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_TEXT)
        )
        self.logger.info("服务页面加载成功，出现“门店”文本")
    
    # 点击门店跳转按钮
    def click_store_btn(self):
        """点击门店跳转按钮。"""
        self.driver.find_element(*STORE_BTN).click()
        # 等待门店详情页面加载完成，出现“门店详情位置”按钮元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_ADDRESS_BTN)
        )
        self.logger.info("门店详情页面加载成功，出现“门店详情位置”按钮")

    # 点击门店详情位置按钮
    def click_store_address_btn(self):
        """点击门店详情位置按钮。"""
        self.driver.find_element(*STORE_ADDRESS_BTN).click()
        # 等待位置弹窗加载完成，出现“确定”按钮元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_ADDRESS_BTN_SUBMIT)
        )
        self.logger.info("门店弹窗加载成功，出现“确定”按钮")

    # 点击位置弹窗确定按钮
    def click_store_address_btn_submit(self):
        """点击位置弹窗确定按钮。"""
        self.driver.find_element(*STORE_ADDRESS_BTN_SUBMIT).click()
        self.logger.info("位置弹窗确定按钮点击成功")
        # 位置弹窗关闭
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.invisibility_of_element_located(STORE_ADDRESS_BTN_SUBMIT)
        )
        self.logger.info("位置弹窗关闭成功")

    