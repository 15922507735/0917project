"""WebView（H5）操作层：封装 context 切换、H5 元素操作、源码 dump 等工具。

切到 WebView 后不能再用 AppiumBy.ID（resource-id 是 Android 原生属性），
需要用浏览器侧选择器：By.CSS_SELECTOR / By.XPATH（DOM）/ By.ID（HTML id 属性）等。
"""
from __future__ import annotations
from typing import Any
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from page_element.login_page import APP_PACKAGE, EXPECT_WAIT_TIMEOUT
from page_element.order_page import SELECT_CONFIG_BTN

class WebViewOperate:
    """WebView / H5 操作封装。"""

    def __init__(self, driver: WebDriver, logger: Any, expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT):
        self.driver = driver
        self.logger = logger
        self.expect_wait_timeout = expect_wait_timeout

    # ===================== context 切换 =====================
    def switch_to_webview(self, package: str = APP_PACKAGE) -> None:
        """等待 WebView 注册到 Appium，再切换到对应的 WEBVIEW_<package> context。

        参数：
            package: 原生应用包名，默认 APP_PACKAGE；用于精确匹配
                     'WEBVIEW_<package>'（避免命中第三方 WebView）。
        """
        # 等出现至少 2 个 context（含 NATIVE_APP）
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                lambda d: len(d.contexts) >= 2,
                f"{self.expect_wait_timeout}s 内 WebView 未注册",
            )
        except Exception as e:
            self.logger.error(
                f"等待 WebView 注册失败: {e}, 当前 contexts={self.driver.contexts}, "
                f"Activity={self.driver.current_activity}"
            )
            raise

        contexts = self.driver.contexts
        self.logger.info(f"当前 contexts: {contexts}")
        # 优先精确匹配 WEBVIEW_<package>，否则兜底取第一个非 NATIVE_APP
        target = None
        for c in contexts:
            if c == "NATIVE_APP":
                continue
            if package and package in c:
                target = c
                break
        if target is None:
            target = next((c for c in contexts if c != "NATIVE_APP"), None)
        if not target:
            raise RuntimeError(f"找不到 WebView context, 当前 contexts={contexts}")

        self.driver.switch_to.context(target)
        self.logger.info(f"已切换到 WebView context: {target}")

    def switch_to_native(self) -> None:
        """从 WebView 切回 NATIVE_APP context。"""
        if self.driver.contexts and self.driver.current_context != "NATIVE_APP":
            self.driver.switch_to.context("NATIVE_APP")
            self.logger.info("已切回 NATIVE_APP context")
        else:
            self.logger.info("当前已在 NATIVE_APP context，跳过切换")

    # ===================== H5 元素操作 =====================
    def webview_click(self, by: str, locator: str, name: str = "") -> None:
        """WebView 中等待元素可点击后点击；失败时 dump 当前 WebView HTML。"""
        try:
            loc = self._to_selenium_locator(by, locator)
            el = WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(loc),
                f"WebView 元素 {name or locator} {self.expect_wait_timeout}s 内不可点击",
            )
            el.click()
            self.logger.info(f"WebView 已点击{name or locator}")
        except Exception as e:
            self.logger.error(
                f"WebView 点击 {name or locator} 失败: {e}, "
                f"current_url={self.driver.current_url}"
            )
            self._dump_webview_html()
            raise

    def webview_input(self, by: str, locator: str, text: str, name: str = "") -> None:
        """WebView 中清空输入框并输入文本。"""
        try:
            loc = self._to_selenium_locator(by, locator)
            el = WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.visibility_of_element_located(loc),
                f"WebView 元素 {name or locator} {self.expect_wait_timeout}s 内不可见",
            )
            el.clear()
            el.send_keys(text)
            self.logger.info(f"WebView 已输入 {name or locator}: {text}")
        except Exception as e:
            self.logger.error(
                f"WebView 输入 {name or locator} 失败: {e}, "
                f"current_url={self.driver.current_url}"
            )
            self._dump_webview_html()
            raise

    def webview_assert_text(
        self, by: str, locator: str, expected: str, name: str = ""
    ) -> None:
        """WebView 中断言某元素文本包含 expected。"""
        loc = self._to_selenium_locator(by, locator)
        el = WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.visibility_of_element_located(loc),
            f"WebView 元素 {name or locator} {self.expect_wait_timeout}s 内不可见",
        )
        actual = el.text
        assert expected in actual, (
            f"WebView 文本断言失败: 期望包含 '{expected}', 实际 '{actual}'"
        )
        self.logger.info(f"WebView 文本断言通过: '{actual}' 包含 '{expected}'")

    @staticmethod
    def _to_selenium_locator(by: str, locator: str):
        """把字符串 by 映射到 Selenium By 常量。"""
        mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,             # H5 的 HTML id 属性（不是 Android resource-id）
            "name": By.NAME,         # H5 的 name 属性
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
        }
        if by not in mapping:
            raise ValueError(
                f"不支持的 WebView 定位方式: {by}, "
                f"可选: {list(mapping.keys())}"
            )
        return (mapping[by], locator)

    # ===================== 源码 dump =====================
    def _dump_webview_html(self, save_name: str = "debug_webview.html") -> None:
        """dump 当前 WebView 的页面源码到本地，便于排查 H5 元素定位失败。"""
        from utils.debug_helpers import dump_webview_html
        dump_webview_html(self.driver, self.logger, save_name)

    # ===================== 业务专属：聚合页配置选择 =====================
    def wait_aggregate_config_page(self, timeout: int | None = None) -> None:
        """断言配置选择页面已加载：SELECT_CONFIG_BTN 可见。

        点击「立即订购」并切换到 WebView 后，页面会跳转到配置选择 H5；
        当 SELECT_CONFIG_BTN（"请选择配置"按钮）可见时即认为页面加载完成。
        超时则 dump WebView 页面源码到 debug_webview.html，便于排查。
        """
        wait_timeout = timeout if timeout is not None else self.expect_wait_timeout
        try:
            WebDriverWait(self.driver, wait_timeout).until(
                EC.visibility_of_element_located(SELECT_CONFIG_BTN),
                f"配置选择页面 {wait_timeout}s 内未加载, SELECT_CONFIG_BTN 不可见",
            )
            self.logger.info(
                f"配置选择页面已加载, current_url={self.driver.current_url}"
            )
        except Exception as e:
            self.logger.error(
                f"等待配置选择页面超时: {e}, "
                f"current_url={self.driver.current_url}"
            )
            self._dump_webview_html("debug_aggregate_config.html")
            raise

    def wait_aggregate_reserve_page(self, timeout: int | None = None) -> None:
        """断言配置选择 H5 的返回已成功：原生侧「预约试驾」按钮 (AGGREGATE_RESERVE_BTN) 可见。

        流程：配置选择 H5 点返回 → 切回 NATIVE_APP → 回到聚合页 → 预约试驾按钮可见。
        必须在 switch_to_native() 之后调用。

        注意：切回 NATIVE_APP 后**不要**读 current_url —— NATIVE context 下读取会触发
        chromedriver proxy 转发，Appium 2 UiAutomator2 server 在该路径上
        返回 "NotYetImplementedError: Method has not yet been implemented"。
        只读 current_activity（server 端原生支持）。
        """
        from page_element.order_page import AGGREGATE_RESERVE_BTN  # 延迟导入
        wait_timeout = timeout if timeout is not None else self.expect_wait_timeout
        try:
            WebDriverWait(self.driver, wait_timeout).until(
                EC.visibility_of_element_located(AGGREGATE_RESERVE_BTN),
                f"聚合页 {wait_timeout}s 内未出现预约试驾按钮",
            )
            self.logger.info(
                f"聚合页已返回, Activity={self.driver.current_activity}"
            )
        except Exception as e:
            self.logger.error(
                f"等待聚合页返回超时: {e}, "
                f"Activity={self.driver.current_activity}"
            )
            raise
