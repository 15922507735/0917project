"""购车模块操作。"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from object_operation.webview_operate import WebViewOperate
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from page_element.login_page import EXPECT_WAIT_TIMEOUT

from page_element.buycar_page import (
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
    STORE_CONFIG_THINK_BTN,
    STORE_CONFIG_ORDER_NEXT_BTN,
    STORE_CONFIG_COMPLETE_BTN,
    STORE_CONFIG_ORDER_CHECK_BTN,
    STORE_CONFIG_SAVE_BTN,
    STORE_CONFIG_ORDER_BTN,
    STORE_CONFIG_NAME,
    STORE_CONFIG_IDCARD,
    STORE_CONFIG_PROTOCOL_CHECK_BTN,
    STORE_CONFIG_SUBMIT_BTN,
    STORE_CONFIG_AGREE_BTN,
    STORE_CONFIG_PAY_BTN,
    STORE_CONFIG_PAY_TIMER,
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
        # 等待版本标题出现（mvlTit，小写 L）—— 按位置取第一个版本，不依赖具体版本名
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_VERSION_FIRST_TITLE_CSS)
        )
        self.logger.info("版本列表已加载")
        # 点击第一个版本标题
        self.driver.find_element(*STORE_CONFIG_VERSION_FIRST_TITLE_CSS).click()
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
    def click_store_config_ext_color_btn(self):
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

    # 点击选择内饰颜色卡片
    def click_store_config_interior_color_btn(self):
        """点击选择内饰颜色卡片。"""
        self.driver.find_element(*STORE_CONFIG_INTERIOR_COLOR_BTN).click()
        self.logger.info("点击选择内饰颜色卡片成功")
        
    # 点击选装按钮到下一步
    def click_store_config_ext_next_btn(self):
        """点击选装按钮到下一步。

        失败时 dump 当前 WebView HTML + dump_visible（通过延迟导入避免循环依赖），
        便于排查 "选装按钮是否真的存在" / "XPath 是否匹配"。
        """
        try:
            self.driver.find_element(*STORE_CONFIG_EXT_NEXT_BTN).click()
        except Exception as e:
            from utils.debug_helpers import dump_visible, dump_webview_html
            dump_webview_html(self.driver, self.logger, "debug_buycar_ext_next.html")
            dump_visible(self.driver, self.logger, "click_store_config_ext_next_btn 失败", limit=80)
            self.logger.error(f"点击选装按钮失败: {e}")
            raise
        self.logger.info("点击选装按钮到下一步成功")

    # 点击添加选装按钮
    def click_store_config_think_btn(self):
        """点击添加选装按钮。"""
        self.driver.find_element(*STORE_CONFIG_THINK_BTN).click()
        self.logger.info("点击添加选装按钮成功")

    # 点击订单中心下一步按钮
    def click_store_config_order_next_btn(self):
        """点击订单中心下一步按钮。"""
        self.driver.find_element(*STORE_CONFIG_ORDER_NEXT_BTN).click()
        self.logger.info("点击订单中心下一步按钮成功")
        # 订单订单中心列表加载完成，出现完成配置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_COMPLETE_BTN)
        )
        self.logger.info("订单中心下一步加载成功，出现完成配置按钮")

    # 选择订单中心
    def click_store_config_order_check_btn(self):
        """点击订单中心勾选按钮。

        失败时 dump 当前 WebView HTML + dump_visible，便于排查
        "订单中心 Tab 是否真的切到了" / "XPath 是否匹配"。
        """
        try:
            check_btn = WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(STORE_CONFIG_ORDER_CHECK_BTN)
            )
            check_btn.click()
            self.logger.info("点击订单中心勾选按钮成功")
        except Exception as e:
            from utils.debug_helpers import dump_visible, dump_webview_html
            dump_webview_html(self.driver, self.logger, "debug_buycar_order_check.html")
            dump_visible(
                self.driver, self.logger,
                "click_store_config_order_check_btn 失败",
                limit=120,
            )
            self.logger.error(f"点击订单中心勾选按钮失败: {e}")
            raise

    # 点击完成配置按钮
    def click_store_config_complete_btn(self):
        """点击完成配置按钮。"""
        self.driver.find_element(*STORE_CONFIG_COMPLETE_BTN).click()
        self.logger.info("点击完成配置按钮成功")
        # 等待保存配置按钮出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_SAVE_BTN)
        )
        self.logger.info("点击完成配置按钮成功，出现保存配置按钮")

    # 点击去订购按钮
    def click_store_config_order_btn(self):
        """点击去订购按钮。"""
        self.driver.find_element(*STORE_CONFIG_ORDER_BTN).click()
        self.logger.info("点击去订购按钮成功")
        # 等待车主姓名输入框出现
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.presence_of_element_located(STORE_CONFIG_NAME)
            )
            self.logger.info("点击去订购按钮成功，出现车主姓名输入框")
        except Exception as e:
            from utils.debug_helpers import dump_visible, dump_webview_html
            dump_webview_html(self.driver, self.logger, "debug_buycar_order_btn.html")
            dump_visible(
                self.driver, self.logger,
                "click_store_config_order_btn 失败",
                limit=120,
            )
            self.logger.error(f"点击去订购按钮后未出现车主姓名输入框: {e}")
            raise

    # 点击车主姓名输入框，输入车主姓名
    def click_store_config_name(self):
        """点击车主姓名输入框。"""
        self.driver.find_element(*STORE_CONFIG_NAME).send_keys("小王")
        self.logger.info("输入车主姓名成功")
    
    # 点击证件号码输入框，输入证件号码
    def click_store_config_idcard(self):
        """点击证件号码输入框。"""
        self.driver.find_element(*STORE_CONFIG_IDCARD).send_keys("44030419900101001X")
        self.logger.info("输入证件号码成功")
    
    # 点击订购协议勾选框
    def click_store_config_protocol_check_btn(self):
        """点击订购协议勾选框。"""
        self.driver.find_element(*STORE_CONFIG_PROTOCOL_CHECK_BTN).click()
        self.logger.info("点击订购协议勾选框成功")
        # 等待同意按钮出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_AGREE_BTN)
        )
        sleep(4)
        self.driver.find_element(*STORE_CONFIG_AGREE_BTN).click()
        self.logger.info("点击同意按钮成功")

    # 点击提交订单按钮
    def click_store_config_submit_btn(self):
        """点击提交订单按钮。"""
        self.driver.find_element(*STORE_CONFIG_SUBMIT_BTN).click()
        self.logger.info("点击提交订单按钮成功")
        # 跳转到支付页面，断言订单提交成功倒计时提示文字出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CONFIG_PAY_TIMER)
        )
        self.logger.info("成功跳转到支付页面，出现倒计时提示文字")

    # 点击支付定金页面的返回按钮
    def click_store_config_pay_btn(self):
        """点击支付定金页面的返回按钮。"""
        self.driver.find_element(*STORE_CONFIG_PAY_BTN).click()
        self.logger.info("点击支付定金页面的返回按钮成功")


        