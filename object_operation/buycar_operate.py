"""购车模块操作。"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from object_operation.webview_operate import WebViewOperate
from appium.webdriver.common.appiumby import AppiumBy

from page_element.login_page import EXPECT_WAIT_TIMEOUT

from page_element.buycat_page import (
    STORE_BUY_BTN,
    STORE_ORDER_BTN,
    STORE_CONFIG_CHOOSE_TIP,
    STORE_CONFIG_NEXT_BTN,
    STORE_CONFIG_VERSION_BY_NAME,
    STORE_CONFIG_INTERIOR_BTN,
    STORE_CONFIG_INTERIOR_NEXT_BTN,
    STORE_CONFIG_VERSION_FIRST,
    STORE_CONFIG_VERSION_FIRST_CSS,
    STORE_CONFIG_VERSION_TITLE_CSS,
    STORE_CONFIG_VERSION_TITLE,
    STORE_CONFIG_VERSION_FIRST_TITLE_CSS,
    STORE_CONFIG_VERSION_BTN,
    STORE_CONFIG_PRICE,
    STORE_CONFIG_EXT_COLOR_BTN,
    STORE_CONFIG_EXT_NEXT_BTN,
    STORE_CONFIG_INTERIOR_COLOR_BTN,
)

class BuycarOperate:
    """购车模块操作。"""

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
        self.webview_operate = WebViewOperate(
            driver,
            logger,
            expect_wait_timeout,
        )
    def click_store_buy_btn(self):
        """点击购车tab按钮。"""
        self.driver.find_element(*STORE_BUY_BTN).click()
        # 等待购车页面加载完成，出现立即订购按钮元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_ORDER_BTN)
        )
        self.logger.info("购车页面加载成功，出现立即订购按钮")
        sleep(1)

    def click_store_order_btn(self):
        """点击立即订购按钮。"""
        self.driver.find_element(*STORE_ORDER_BTN).click()
        self.logger.info("点击立即订购按钮成功")
        sleep(1)
        # 切换到webview
        self.webview_operate.switch_to_webview()
        self.logger.info("切换到webview成功")

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
        # 等待配置选择页加载完成，出现"请选择配置"提示文本
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_CHOOSE_TIP)
        )
        self.logger.info("配置选择页加载成功，出现\"请选择配置\"提示文本")
    
    # 点击去选择车型版本，选择第一个版本卡片
    def click_store_config_version_btn(self):
        """点击去选择车型版本，选择第一个版本卡片。"""
        # 等待版本标题出现（mvlTit，小写 L）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_VERSION_TITLE)
        )
        self.logger.info("版本列表已加载")
        # 精准点击第一个版本标题（XPATH 文字限定，最稳）
        self.driver.find_element(*STORE_CONFIG_VERSION_TITLE).click()
        self.logger.info("点击去选择车型版本成功")
        # 等待价格出现（确认版本已选中）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_PRICE)
        )
        self.logger.info("车型版本已选中，价格已显示")
        
    # 点击外观 -> 下一步
    def click_store_config_next_btn(self):
        """点击外观 -> 下一步。"""
        self.driver.find_element(*STORE_CONFIG_NEXT_BTN).click()
        self.logger.info("点击外观 -> 下一步成功")
        # 等待内饰 Tab 按钮出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_INTERIOR_BTN)
        )
        self.logger.info("点击外观 -> 下一步成功，出现内饰 Tab 按钮")

    # 点击选择外观颜色卡片
    def click_store_config_interior_color_btn(self):
        """点击选择外观颜色卡片。"""
        self.driver.find_element(*STORE_CONFIG_EXT_COLOR_BTN).click()
        self.logger.info("点击选择外观颜色卡片成功")

    # 点击内饰按钮到下一步
    def click_store_config_interior_next_btn(self):
        """点击内饰按钮到下一步。"""
        self.driver.find_element(*STORE_CONFIG_INTERIOR_NEXT_BTN).click()
        self.logger.info("点击内饰按钮到下一步成功")
        # 等待选装按钮出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_EXT_NEXT_BTN)
        )
        self.logger.info("点击内饰按钮到下一步成功，出现选装按钮")
        
    # 点击选装按钮到下一步
    def click_store_config_ext_next_btn(self):
        """点击选装按钮到下一步。"""
        self.driver.find_element(*STORE_CONFIG_EXT_NEXT_BTN).click()
        self.logger.info("点击选装按钮到下一步成功")