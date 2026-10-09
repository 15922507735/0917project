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
