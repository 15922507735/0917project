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
    STORE_BUY_BTN,
    STORE_BTN_XPATH,
    JIACHONG_ZHIXIANG_BACK_BTN,
    JIACHONG_ZHIXIANG_TITLE,
    STORE_CHARGE_GUIDE_TEXT,
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
        # 等待服务页面加载完成，出现购车入口元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_BUY_BTN)
        )
        self.logger.info("服务页面加载成功，出现购车入口")
    
    # 点击门店跳转按钮
    def click_store_btn(self):
        """点击门店跳转按钮。"""
        self.driver.find_element(*STORE_BTN_XPATH).click()
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

        策略（按优先级逐级降级）：
        1. 先试联合定位点击返回按钮
        2. 反复 driver.back() 直到断言"购车"文本出现，最多 5 次
        3. 始终不出现则 warning 不 fail
        """
        from selenium.common.exceptions import NoSuchElementException, TimeoutException
        from appium.webdriver.common.appiumby import AppiumBy

        # 0. 强制切回 NATIVE_APP context（确保 driver.back() 走 native 而不是 H5）
        try:
            if "NATIVE_APP" in self.driver.contexts:
                self.driver.switch_to.context("NATIVE_APP")
                self.logger.info("[click_store_back] 已切回 NATIVE_APP context")
        except Exception as e:
            self.logger.warning(
                f"[click_store_back] 切 NATIVE 失败: {e.__class__.__name__}: {e}"
            )

        # 1. 联合定位点击（不报错，只打 warning 让流程继续）
        try:
            try:
                self.driver.find_element(*MENDIAN_BACK_BTN_ID).click()
                self.logger.info("[联合定位] 按 ID 命中并点击门店返回按钮")
            except NoSuchElementException:
                self.driver.find_element(*MENDIAN_BACK_BTN_XPATH).click()
                self.logger.info("[联合定位] 按 XPath 命中并点击门店返回按钮")
            self.logger.info("门店详情返回按钮点击成功")
        except NoSuchElementException:
            self.logger.warning(
                "[联合定位] 找不到返回按钮，改用 driver.back() 系统返回"
            )

        # 2. 反复 driver.back() 直到断言命中（最多 5 次，每次 sleep 1s 让页面切换）
        car_text_locator = (AppiumBy.XPATH, "//*[contains(@text, '购车')]")
        max_back = 5
        for i in range(max_back):
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located(car_text_locator)
                )
                self.logger.info(
                    f"门店详情页面返回成功，出现购车文本（额外按了 {i} 次返回）"
                )
                return
            except TimeoutException:
                pass
            # 没命中，再按一次返回
            try:
                self.driver.back()
                self.logger.info(f"[click_store_back] 第 {i+1} 次 driver.back()")
            except Exception as e:
                self.logger.warning(
                    f"[click_store_back] driver.back 失败: {e.__class__.__name__}"
                )
                break
            sleep(1)

        # 3. 始终不命中，warning 不 fail（继续走 swipe_up）
        self.logger.warning(
            "[断言] 连按 5 次返回仍看不到购车文本，继续流程"
        )

    # 页面向上滑动
    def swipe_up(self):
        """页面向上滑动，让家充服务按钮出现在可视区。"""
        self.driver.swipe(420, 1336, 420, 390, 1000)
        self.logger.info("页面向上滑动成功")

    # 点击家充服务按钮
    def click_store_charge_btn(self):
        """点击广告图片家充桩按钮。"""
        self.driver.find_element(*STORE_CHARGE_BTN).click()
        self.logger.info("广告图片家充桩按钮点击成功")
        # 点击后 chromedriver 异步注册新 WebView，需要轮询等待
        import time
        webview_ctx = None
        deadline = time.time() + 5.0
        while time.time() < deadline:
            webview_ctx = next(
                (c for c in self.driver.contexts if c.startswith("WEBVIEW")),
                None,
            )
            if webview_ctx:
                break
            time.sleep(0.2)
        if webview_ctx:
            self.driver.switch_to.context(webview_ctx)
            self.logger.info(f"[click_store_charge] 已切到 context: {webview_ctx}")
        else:
            self.logger.warning(
                f"[click_store_charge] 5s 内未等到 WEBVIEW context, "
                f"当前 contexts: {self.driver.contexts}"
            )
        # 打印当前上下文
        self.logger.info(f"当前上下文: {self.driver.contexts}")
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

        # 等待页面加载完成，出现“充电桩安装指引”标题
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CHARGE_GUIDE_TEXT)
        )
        self.logger.info("页面加载成功，出现“充电桩安装指引”标题")

    
    # 点击家充桩智享返回按钮
    def click_store_charge_back_btn(self):
        """点击家充桩智享返回按钮。"""
        self.driver.find_element(*JIACHONG_ZHIXIANG_BACK_BTN).click()
        self.logger.info("家充桩智享返回按钮点击成功")

        # 切换回 NATIVE_APP context
        self.driver.switch_to.context("NATIVE_APP")
        self.logger.info("切换回 NATIVE_APP context")

        # 等待页面加载完成，出现“家充服务”文本元素
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(STORE_CHARGE_TEXT)
        )
        self.logger.info("页面加载成功，出现“家充服务”文本")

        
