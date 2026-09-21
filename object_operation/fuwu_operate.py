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
    STORE_BACK_BTN,
    STORE_CHARGE_BTN,
    MENDIAN_BACK_BTN_ID,
    MENDIAN_BACK_BTN_XPATH,
    STORE_CHARGE_BTN_HUAWEI,
    STORE_CHARGE_TEXT,
    STORE_CHARGE_PILL_TEXT,
    STORE_CHARGE_BACK_BTN,
    STORE_FINANCE_TEXT,
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

    # 点击收起展开按钮
    def click_store_search_btn(self):
        """点击收起展开按钮。"""
        self.driver.find_element(*STORE_SEARCH_BTN).click()
        self.logger.info("收起展开按钮点击成功")

    # 点击交付中心按钮
    def click_store_deliver_btn(self):
        """点击交付中心按钮。"""
        self.driver.find_element(*STORE_DELIVER_BTN).click()
        self.logger.info("交付中心按钮点击成功")
    
    # 点击维保中心按钮
    def click_store_maint_btn(self):
        """点击维保中心按钮。"""
        self.driver.find_element(*STORE_MAINT_BTN).click()
        self.logger.info("维保中心按钮点击成功")
    
    # 点击门店详情返回按钮
    def click_store_back_btn(self):
        """点击门店详情返回按钮。
        
        联合定位策略：先按 ID 找，找不到再按 XPath 找，确保点中"返回按钮"本身。
        """
        from selenium.common.exceptions import NoSuchElementException
        try:
            self.driver.find_element(*MENDIAN_BACK_BTN_ID).click()
            self.logger.info("[联合定位] 按 ID 命中并点击门店返回按钮")
        except NoSuchElementException:
            self.driver.find_element(*MENDIAN_BACK_BTN_XPATH).click()
            self.logger.info("[联合定位] 按 XPath 命中并点击门店返回按钮")
        self.logger.info("门店详情返回按钮点击成功")
        # 等待服务页面加载完成，出现金融试算文本元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_FINANCE_TEXT)
        )
        self.logger.info("服务页面加载成功，出现“金融试算”文本")

    # 页面向上滑动
    def swipe_up(self):
        """页面向上滑动。"""
        self.driver.swipe(420, 1336, 420, 390, 1000)
        self.logger.info("页面向上滑动成功")
        # 等待页面加载完成，出现“家充桩”元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CHARGE_BTN)
        )
        self.logger.info("页面加载成功，出现“家充桩”按钮")

    # 点击家充服务按钮
    def click_store_charge_btn(self):
        """点击家充服务按钮。"""
        self.driver.find_element(*STORE_CHARGE_BTN).click()
        self.logger.info("家充服务按钮点击成功")
        # 等待页面加载完成，出现“家充桩”元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CHARGE_PILL_TEXT)
        )
        self.logger.info("页面加载成功，出现“家充桩”文本")
    
    # 点击家充装返回按钮
    def click_store_charge_back_btn(self):
        """点击家充装返回按钮。"""
        self.driver.find_element(*STORE_CHARGE_BACK_BTN).click()
        self.logger.info("家充装返回按钮点击成功")
        # 等待页面加载完成，出现“家充服务”文本元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CHARGE_TEXT)
        )
        self.logger.info("页面加载成功，出现“家充服务”文本")
        
