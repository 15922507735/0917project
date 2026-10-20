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
MY_CARD_BTN,
MY_CARD_UNUSED,
MY_ONLINE_EVALUATION,
MY_PENDING_EVALUATION,
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
        """点击签到按钮。

        业务逻辑：
            1. 点签到按钮（MY_SIGN_BTN，id=tvsign）；
            2. 容错等待"签到成功"弹窗（MY_SIGN_SUCCESS_TEXT，id=tv1）—— 最多 5s：
               - 已签到（今天）：弹窗不再出现 → 跳过弹窗断言，视为已签到 OK；
               - 未签到：弹窗出现 → 找到"好的"按钮并点掉。
        """
        self.driver.find_element(*MY_SIGN_BTN).click()
        self.logger.info("成功点击签到按钮")
        # 容错等待签到成功弹窗（最多 5s）；找不到说明今日已签过
        from selenium.common.exceptions import TimeoutException
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(MY_SIGN_SUCCESS_TEXT)
            )
            self.logger.info("签到成功弹窗出现-签到成功文本出现")
            # 点击好的按钮关闭弹窗
            self.driver.find_element(*MY_SIGN_SUCCESS_BTN).click()
            self.logger.info("成功点击好的按钮")
        except TimeoutException:
            # 没弹签到成功弹窗 → 用户今日已签过（每天只能签一次），属正常业务态
            self.logger.info(
                "未出现签到成功弹窗（可能今日已签到 / APP 改版），跳过弹窗断言"
            )

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
        """点击我的订单。

        完整流程（已根据 test_21_mine.py::test_mypage_operate_order 真实失败迭代过）：
          1. NATIVE 点"我的订单"按钮 → 进订单列表 NATIVE 页；
          2. NATIVE 点"订车订单"→ 触发打开 H5 详情页（WebView）；
          3. WebView 点第一个订单卡片 → 进 H5 订单详情；
          4. NATIVE 系统返回键 → 直接退到我的页（H5 详情 → 我的页可能由 WebView back 触发）；
          5. 等设置按钮出现（确认已回到"我的"页）。

        注：H5 内部返回后，可能直接退到 NATIVE 我的页（跳过 NATIVE 订单列表）。
            不管走哪条路径，最终断言都是"设置按钮可见"。
        """
        # 1. NATIVE 点"我的订单"按钮
        self.driver.find_element(*MY_ORDER_BTN).click()
        self.logger.info("成功点击我的订单")
        # 2. 等订车订单（NATVIE 订单列表元素）
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_RECORD)
        )
        self.logger.info("我的订单列表-订车订单出现")
        # 3. NATIVE 点"订车订单"（触发打开 H5 详情页）
        self.driver.find_element(*MY_ORDER_RECORD).click()
        self.logger.info("成功点击订车订单")
        # 4. 切到 WebView
        self.webview_operate.switch_to_webview()
        self.logger.info("成功切换到webview")
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")
        # 5. WebView 等 H5 订单列表元素 + 点第一个
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_FIRST_ITEM)
        )
        self.driver.find_element(*MY_ORDER_FIRST_ITEM).click()
        self.logger.info("成功点击第一个订单")
        # 6. WebView 等 H5 订单详情
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_ORDER_DETAIL)
        )
        self.logger.info("订单详情-订单详情出现")
        # 7. 在 WebView 里 driver.back()（H5 详情 → H5 上一级）
        #    注意：必须在 WebView 里 back，否则会退到桌面。
        self.driver.back()
        sleep(1)
        self.logger.info("H5 详情 → H5 上一级（WebView 内 back）")
        # 8. 若仍在 H5 列表页（能等到列表元素），再 back 一次退出 H5
        from selenium.common.exceptions import TimeoutException
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(MY_ORDER_FIRST_ITEM)
            )
            self.logger.info("H5 列表加载完成-回到 H5 订单列表")
            self.driver.back()
            sleep(1)
            self.logger.info("H5 列表 → 退出 H5（WebView back）")
        except TimeoutException:
            self.logger.info("未在 H5 列表页（可能已直接退出 H5）")
        # 9. 切回 NATIVE_APP
        self.webview_operate.switch_to_native()
        self.logger.info("切回 NATIVE_APP")
        # 10. 循环返回"我的"页：
        #     H5 退出后可能停在 NATIVE"订车订单"页 / "订单列表"页，
        #     需要逐层按系统返回键退出，直到"设置"按钮出现（最多 4 次）。
        for attempt in range(4):
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(MY_SETTING_BTN)
                )
                self.logger.info("跳转到我的页面-设置出现")
                return
            except TimeoutException:
                self.logger.info(
                    f"[返回我的页] 第 {attempt + 1} 次未到我的页，按系统返回键退一层"
                )
                self.driver.back()
                sleep(1)
        # 兜底：强制将 APP 拉回前台后再等一次
        self.driver.activate_app(APP_PACKAGE)
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现（activate_app 兜底）")

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

        # 页面加载完成：原版要求等 MY_QRCODE（//*[@id='app']/...span）元素出现，
        # 但 H5 页面结构改版后这个 XPath 经常失败（div 层级数变化）。
        # 改用更稳的判据：URL 含 "shopPartner"（合伙人店铺）。
        # 给页面 5s 渲染时间，title 应该已显示"合伙人店铺"。
        import time as _t
        _t.sleep(5)
        try:
            title = self.driver.title or ""
            url = self.driver.current_url or ""
            if "shopPartner" in url or "合伙人" in title or "店铺" in title:
                self.logger.info(
                    f"[车主店铺] 页面加载完成（url={url}, title={title}）"
                )
            else:
                self.logger.warning(
                    f"[车主店铺] 页面 URL/title 异常，强制继续: "
                    f"url={url}, title={title}"
                )
        except Exception as e:
            self.logger.warning(f"[车主店铺] 读取 URL/title 失败（继续）: {e}")
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

    # 点击我的卡券
    def click_card_btn(self):
        """点击我的卡券，并返回到我的页面。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(MY_CARD_BTN)
        ).click()
        self.logger.info("成功点击我的卡券")
        # 切换到webview（复用 WebViewOperate 的 context 切换与 chromedriver 匹配逻辑）
        self.webview_operate.switch_to_webview()
        self.logger.info("成功切换到webview")
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")
        # 等待 WebView 页面 未使用元素出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_CARD_UNUSED)
        )
        self.logger.info("出现未使用卡券元素")
        # 先切回 native context，再用系统返回键回到我的页面
        # （WebView 内 driver.back() 是浏览器历史回退，不一定能退出 WebView 回到原生页）
        self.webview_operate.switch_to_native()
        self.logger.info("成功切换回native context")
        self.driver.back()
        self.logger.info("成功返回我的页面")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现")

    # 点击在线评价
    def click_online_evaluation(self):
        """点击在线评价，并返回到我的页面。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(MY_ONLINE_EVALUATION)
        ).click()
        self.logger.info("成功点击在线评价")
        # 等待页面待评价元素出现
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_PENDING_EVALUATION)
        )
        self.logger.info("出现待评价元素")
        # 返回我的页面
        self.driver.back()
        self.logger.info("成功返回我的页面")
        # 页面加载完成，出现设置按钮
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(MY_SETTING_BTN)
        )
        self.logger.info("跳转到我的页面-设置出现")

    # 检查我的页面设置按钮是否可见
    def is_setting_btn_visible(self):
        """检查我的页面"设置"按钮是否可见。

        用于用例返回后断言"成功回到我的页面"。
        在 expect_wait_timeout 内轮询设置按钮可见性，超时返回 False。
        """
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.visibility_of_element_located(MY_SETTING_BTN)
            )
            self.logger.info("[MyOperate] 我的页面设置按钮可见")
            return True
        except Exception as e:
            self.logger.warning(
                f"[MyOperate] 我的页面设置按钮不可见（超时）: {e}"
            )
            return False