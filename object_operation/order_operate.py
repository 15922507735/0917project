"""订单 / 聚合页操作层：封装「点击聚合页 → 处理位置授权 → 点击立即订购 → WebView 跳转」。

依赖：
- page_element.order_page：聚合页 / 立即订购元素
- object_operation.first_page_operate：用于切回「发现」首页
- object_operation.webview_operate：用于切 WebView + H5 操作
"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.order_page import (
    AGGREGATE_BUTTON,
    AGGREGATE_ORDER_BTN,
    PERMISSION_ALLOW_BTN,
)


class OrderOperate:
    """聚合页 / 订单 / 立即订购 操作封装。"""

    def __init__(
        self,
        driver: WebDriver,
        logger: Any,
        webview_operate,
        expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT,
    ):
        self.driver = driver
        self.logger = logger
        # 注入 WebViewOperate，用于切 context + H5 操作
        self.webview_operate = webview_operate
        self.expect_wait_timeout = expect_wait_timeout

    # ===================== 聚合页 =====================
    def click_aggregate_btn(self) -> None:
        """点击聚合页按钮，处理位置授权弹窗。

        session 场景下用例3 跑完后 APP 可能停在「我的」Tab 或「推荐」二级 Tab，
        而 AGGREGATE_BUTTON（iv_cover）只在「发现」首页可见；
        由调用方负责先切回「发现」首页（本方法不强制再做一次 Tab 切换）。
        """
        self.driver.find_element(*AGGREGATE_BUTTON).click()
        sleep(1)
        # 处理位置授权弹窗（如出现）
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(PERMISSION_ALLOW_BTN)
            ).click()
            self.logger.info("已点击位置授权允许按钮")
        except Exception:
            self.logger.info("未出现位置授权弹窗，跳过")

        # 等待聚合页加载完成（出现「立即订购」按钮）
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.visibility_of_element_located(AGGREGATE_ORDER_BTN)
            )
        except Exception as e:
            self.logger.error(
                f"聚合页加载完成 {self.expect_wait_timeout}s 内未出现立即订购按钮，"
                f"当前 Activity: {self.driver.current_activity}, 错误: {e}"
            )
            raise
        self.logger.info("聚合页立即订购按钮已出现")

    # ===================== 立即订购 =====================
    def click_aggregate_order_btn(self) -> None:
        """点击「立即订购」按钮，跳转后会打开 WebView（订购 H5）。

        步骤：
        1) 等「立即订购」按钮可点击再点击；
        2) 切到对应 WEBVIEW_<package> context；
        3) 打印 current_url / title 便于确认；
        4) 演示点击第一个配置项 + 断言配置选择页面已加载。
        """
        # 1) 点击「立即订购」按钮
        try:
            order_btn = WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(AGGREGATE_ORDER_BTN),
                f"立即订购按钮 {self.expect_wait_timeout}s 内不可点击",
            )
            order_btn.click()
            self.logger.info("已点击立即订购按钮")
        except Exception as e:
            self.logger.error(
                f"点击立即订购按钮失败: {e}, "
                f"当前 Activity: {self.driver.current_activity}"
            )
            raise

        # 2) 切到 WebView context
        self.webview_operate.switch_to_webview()

        # 3) 打印 url + title
        try:
            self.logger.info(
                f"WebView 已激活, url={self.driver.current_url}, "
                f"title={self.driver.title}"
            )
        except Exception as e:
            self.logger.warning(f"读取 WebView url/title 失败（不影响切 context）: {e}")

        # 4) 演示 WebView 内元素定位（用 webview_operate.webview_click 等工具）
        #    真实页面元素按 dump 的 page_source 调整 by/locator。
        try:
            self.webview_operate.webview_click(
                "css", ".mvList", name="首个配置项",
            )
            self.webview_operate.webview_assert_text(
                "css", "body", "配置", name="配置页文本断言",
            )
        except Exception as e:
            self.logger.error(f"WebView 演示操作失败: {e}")
            # 不抛异常，让用例至少完成 WebView 切换验证

        # 5) 断言配置选择页面加载完成
        self.webview_operate.wait_aggregate_config_page()
