"""
我的页面操作
"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from object_operation.webview_operate import WebViewOperate
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from page_element.login_page import APP_PACKAGE, EXPECT_WAIT_TIMEOUT

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.my_page import (
MY_TAB,
MY_SETTING_BTN,
MY_SKIN_BTN,
MY_SKIN_CARD_FIRST,
MY_SKIN_CARD_SECOND,
MY_SKIN_USE_BTN,
MY_SKIN_TAB_BTN,
MY_GUAJIAN_CARD_SECOND,
MY_SKIN_CARD_NO,
MY_GUAJIAN_USE_BTN,
MY_GUAJIAN_BACK_BTN,
MY_GUAJIAN_USEING_BTN,
MY_GUAJIAN_TAB_BTN,
MY_GUAJIAN_CARD_NO,
MY_NICKNAME,
MY_NICKNAME_TITLE,
MY_USER_INFO,
MY_SIGN,
MY_NICKNAME_INPUT,
MY_NICKNAME_COMMIT_BTN,
MY_SAVE_BTN,
MY_SETTING_BACK_BTN,
MY_NICKNAME_TEXT,
MY_SIGN_BTN,
MY_SIGN_SUCCESS_TEXT,
MY_SIGN_SUCCESS_BTN,
MY_CONYB_BTN,
MY_CONYB_RECORD,
MY_CONYB_LEVEL_BTN,
MY_CONYB_LEVEL_RECORD,
MY_ORDER_BTN,
MY_ORDER_RECORD,
MY_ORDER_RECORD_MALL,
MY_ORDER_FIRST_ITEM,
MY_ORDER_DETAIL,
MY_ORDER_DETAIL_BACK_BTN,
MY_SHOP_BTN,
MY_QRCODE,
MY_SHOP_BACK_BTN,
MY_CROSS_CITY_ACTIVITY,
MY_CROSS_CITY_TITLE,
MY_CROSS_CITY_NAV_BRAND,
MY_CROSS_CITY_MONDAY,
MY_CROSS_CITY_BACK_BTN,

)
import pytest
import time


class MyOperate:
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

    def click_my_btn(self):
        """点击我的按钮。"""
        self.driver.find_element(*MY_TAB).click()
        self.logger.info("成功点击我的按钮")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("我的页面加载完成-设置按钮出现")

    # 点击皮肤按钮
    def click_skin_btn(self):
        """点击皮肤按钮。"""
        self.driver.find_element(*MY_SKIN_BTN).click()
        self.logger.info("成功点击皮肤按钮")
        # 页面加载完成，皮肤卡片出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SKIN_CARD_FIRST)
        )
        self.logger.info("皮肤列表页面加载完成")
    
    # 点击皮肤卡片并使用（通用实现）
    def _click_skin_card_and_use(self, card_locator, card_label: str):
        """点击指定的皮肤卡片并立即使用。

        :param card_locator: 皮肤卡片的定位元组 (AppiumBy, value)
        :param card_label: 用于日志的人类可读名称，例如"第二个""系统默认"
        """
        self.driver.find_element(*card_locator).click()
        self.logger.info(f"成功点击{card_label}皮肤卡片")
        # 页面加载完成，出现立即使用按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SKIN_USE_BTN)
        )
        self.logger.info("跳转到皮肤详情页面-立即使用按钮出现")
        # 点击立即使用按钮
        self.driver.find_element(*MY_SKIN_USE_BTN).click()
        self.logger.info("成功点击立即使用按钮")
        # 皮肤使用成功，显示正在使用
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_GUAJIAN_USEING_BTN)
        )
        self.logger.info("皮肤使用成功，显示正在使用")

    # 点击第二个皮肤卡片并使用
    def click_skin_card_second(self):
        """点击第二个皮肤卡片并使用。"""
        self._click_skin_card_and_use(MY_SKIN_CARD_SECOND, "第二个")

    # 点击第一个皮肤卡片并使用
    def click_skin_card_first(self):
        """点击第一个（系统默认）皮肤卡片并使用。"""
        self._click_skin_card_and_use(MY_SKIN_CARD_FIRST, "第一个")

    # 点击皮肤详情页返回按钮
    def click_skin_back_btn(self):
        """点击皮肤详情页返回按钮。
        使用系统返回键（driver.back()）规避 bar_img_back ImageView 本身 clickable=false 导致的点击无效问题。
        """
        self.driver.back()
        self.logger.info("使用系统返回键返回上一级")
        # 页面加载完成，出现皮肤列表（用第二个皮肤卡片作锚点，避免系统默认卡片滚动出可视区）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SKIN_CARD_SECOND)
        )
        self.logger.info("跳转到皮肤列表页面-皮肤列表出现")

    # 点击挂件入口按钮
    def click_gujian_tab_btn(self):
        """点击挂件入口按钮。"""
        self.driver.find_element(*MY_GUAJIAN_TAB_BTN).click()
        self.logger.info("成功点击挂件入口按钮")
        # 页面加载完成，出现无挂件卡片
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_GUAJIAN_CARD_NO)
        )
        self.logger.info("跳转到挂件列表页面-无挂件卡片出现")
        # 从挂件列表页面返回我的页面
        self.driver.back()
        self.logger.info("返回到我的页面")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("我的页面加载完成-设置按钮出现")

    # 点击我的设置按钮
    def click_setting_btn(self):
        """点击我的设置按钮。"""
        self.driver.find_element(*MY_SETTING_BTN).click()
        self.logger.info("成功点击我的设置按钮")
        # 页面加载完成，出现个人资料
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_USER_INFO)
        )
        self.logger.info("跳转到设置页面-个人资料出现")
    
    # 点击个人资料
    def click_user_info(self):
        """点击个人资料。"""
        self.driver.find_element(*MY_USER_INFO).click()
        self.logger.info("成功点击个人资料")
        # 页面加载完成，出现个性签名
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SIGN)
        )
        self.logger.info("跳转到设置页面-个性签名出现")
    # 点击昵称
    def click_nickname(self):
        """点击昵称。"""
        self.driver.find_element(*MY_NICKNAME).click()
        self.logger.info("成功点击昵称")
        # 页面加载完成，出现修改昵称标题
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_NICKNAME_TITLE)
        )
        self.logger.info("跳转到设置页面-修改昵称标题出现")

    # 点击昵称输入框，清除输入框内容
    def click_nickname_input(self):
        """点击昵称输入框，清除输入框内容，输入新昵称，并保存。"""
        nickname = self.driver.find_element(*MY_NICKNAME_INPUT)
        nickname.clear()
        nickname.send_keys("大圣")
        self.logger.info("成功输入新昵称")
        # 点击确定按钮
        self.driver.find_element(*MY_NICKNAME_COMMIT_BTN).click()
        self.logger.info("成功点击确定昵称按钮")
        # 点击保存按钮
        self.driver.find_element(*MY_SAVE_BTN).click()
        self.logger.info("保存成功")
        # 跳转到设置页面，出现个人资料
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_USER_INFO)
        )
        self.logger.info("跳转到设置页面-个人资料出现")

    # 点击设置页面返回按钮
    def click_setting_back_btn(self):
        """点击设置页面返回按钮。
        使用系统返回键（driver.back()）规避 bar_img_back 在 App 调试横条上重复出现导致错点的问题。
        """
        self.driver.back()
        self.logger.info("使用系统返回键退出设置页面")
        # 页面加载完成，出现昵称文本
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_NICKNAME_TEXT)
        )
        self.logger.info("跳转到我的页面-昵称出现")

    # 点击签到按钮
    def click_sign_btn(self):
        """点击签到按钮。"""
        self.driver.find_element(*MY_SIGN_BTN).click()
        self.logger.info("成功点击签到按钮")
        # 弹出签到成功弹窗，出现签到成功文本
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SIGN_SUCCESS_TEXT)
        )
        self.logger.info("签到成功弹窗出现-签到成功文本出现")
        # 点击好的按钮
        self.driver.find_element(*MY_SIGN_SUCCESS_BTN).click()
        self.logger.info("成功点击好的按钮")

    # 点击查看源宝
    def click_conyb_btn(self):
        """点击查看源宝，并返回我的页面。"""
        self.driver.find_element(*MY_CONYB_BTN).click()
        self.logger.info("成功点击查看源宝")
        # 页面加载完成，出现源宝记录
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_CONYB_RECORD)
        )
        self.logger.info("跳转到源宝记录页面-源宝记录出现")
        # 使用系统返回键退出源宝记录页面（bar_img_back 受调试横幅干扰，clickable 不可靠）
        self.driver.back()
        self.logger.info("使用系统返回键退出源宝记录页面")
        # 页面加载完成，出现昵称文本
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_NICKNAME_TEXT)
        )
        self.logger.info("跳转到我的页面-昵称出现")
        
    # 点击查看定级积分
    def click_conyb_level_btn(self):
        """点击查看定级积分，并返回我的页面。"""
        self.driver.find_element(*MY_CONYB_LEVEL_BTN).click()
        self.logger.info("成功点击查看定级积分")
        # 页面加载完成，出现定级积分记录
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_CONYB_LEVEL_RECORD)
        )
        self.logger.info("跳转到定级积分记录页面-定级积分记录出现")
        # 使用系统返回键退出定级积分记录页面（bar_img_back 受调试横幅干扰，clickable 不可靠）
        self.driver.back()
        self.logger.info("使用系统返回键退出定级积分记录页面")
        # 页面加载完成，出现昵称文本
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_NICKNAME_TEXT)
        )
        self.logger.info("跳转到我的页面-昵称出现")
        
    # 点击我的订单
    def click_order_btn(self):
        """点击我的订单。"""
        self.driver.find_element(*MY_ORDER_BTN).click()
        self.logger.info("成功点击我的订单")
        # 页面加载完成，出现订车订单
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_RECORD)
        )
        self.logger.info("我的订单列表-订车订单出现")
        # 点击订车订单
        self.driver.find_element(*MY_ORDER_RECORD).click()
        self.logger.info("成功点击订车订单")
        # 切换到webview（复用 WebViewOperate 的 context 切换与 chromedriver 匹配逻辑）
        self.webview_operate.switch_to_webview()
        self.logger.info("成功切换到webview")
        # 打印url+title
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")
        # 等待订单列表加载完成后点击第一个订单
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_FIRST_ITEM)
        )
        self.driver.find_element(*MY_ORDER_FIRST_ITEM).click()
        self.logger.info("成功点击第一个订单")
        # 页面加载完成，出现订单详情
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_DETAIL)
        )
        self.logger.info("订单详情-订单详情出现")
        # 点击页面顶部返回按钮2次：第一次返回订单列表，第二次返回我的页面
        self.driver.find_element(*MY_ORDER_DETAIL_BACK_BTN).click()
        self.logger.info("成功点击返回按钮第1次")
        # 等待返回到订单列表页
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_FIRST_ITEM)
        )
        self.driver.find_element(*MY_ORDER_DETAIL_BACK_BTN).click()
        self.logger.info("成功点击返回按钮第2次")
        # 切换回native context
        self.webview_operate.switch_to_native()
        self.logger.info("成功切换回native context")
        # 页面加载完成，出现订车订单
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_RECORD)
        )
        self.logger.info("跳转到我的页面-订车订单出现")
        # 系统返回到我的页面
        self.driver.back()
        self.logger.info("使用系统返回键退出我的订单页面")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现")

    # 点击车主店铺
    def click_shop_btn(self):
        """点击进入车主店铺，并返回到我的页面。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(MY_SHOP_BTN)
        ).click()
        self.logger.info("成功点击车主店铺")
        # 切换到webview（复用 WebViewOperate 的 context 切换与 chromedriver 匹配逻辑）
        self.webview_operate.switch_to_webview()
        self.logger.info("成功切换到webview")
        # 打印url+title
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")

        # 页面加载完成，出现个人二维码
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_QRCODE)
        )
        self.logger.info("个人二维码-个人二维码出现")
        # 点击车主店铺返回按钮
        self.driver.find_element(*MY_SHOP_BACK_BTN).click()
        self.logger.info("成功点击车主店铺返回按钮")
        # 切换回native context
        self.webview_operate.switch_to_native()
        self.logger.info("成功切换回native context")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现")

    # 点击同城活动
    def click_cross_city_activity(self):
        """点击进入同城活动，并返回到我的页面。"""
        # 等待原生页面上的同城活动入口出现（NATIVE_APP context）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(MY_CROSS_CITY_ACTIVITY)
        )
        self.logger.info("同城活动入口出现")
        # 点击同城活动
        self.driver.find_element(*MY_CROSS_CITY_ACTIVITY).click()
        self.logger.info("成功点击同城活动")
        # 切换到webview（复用 WebViewOperate 的 context 切换与 chromedriver 匹配逻辑）
        self.webview_operate.switch_to_webview()
        self.logger.info("成功切换到webview")
        # 打印url+title
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")
        # 等待 WebView 页面 title 出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_CROSS_CITY_TITLE)
        )
        self.logger.info("出现同城活动页面title")
        # 点击精彩日程
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(MY_CROSS_CITY_NAV_BRAND)
        ).click()
        self.logger.info("成功点击精彩日程")
        # 页面加载完成，出现星期一元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_CROSS_CITY_MONDAY)
        )
        self.logger.info("出现星期一元素")
        # 点击同城活动返回按钮
        self.driver.find_element(*MY_CROSS_CITY_BACK_BTN).click()
        self.logger.info("成功点击同城活动返回按钮")
        # 切换回native context
        self.webview_operate.switch_to_native()
        self.logger.info("成功切换回native context")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现")

        
        
