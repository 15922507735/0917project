"""订单 / 聚合页元素层。

包含原生侧聚合页入口、位置授权、立即订购按钮、预约试驾按钮，
以及 WebView 内的「配置选择」加载标志 + 配置选择页返回按钮。
"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .login_page import APP_PACKAGE

# 聚合页 tab 按钮
AGGREGATE_BUTTON = (AppiumBy.ID, f"{APP_PACKAGE}:id/iv_tab")
# 位置授权允许按钮
PERMISSION_ALLOW_BTN = (
    AppiumBy.ID,
    "com.android.packageinstaller:id/permission_allow_button",
)
# 聚合页「立即订购」按钮（按 id 精确定位）
AGGREGATE_ORDER_BTN = (AppiumBy.ID, "com.changan.oushangCos1:id/btn2")
# 聚合页「预约试驾」按钮（与"立即订购"并排的另一个按钮）
AGGREGATE_RESERVE_BTN = (AppiumBy.ID, "com.changan.oushangCos1:id/btn1")
# 配置选择页面加载标志（WebView 中"配置选择"标题）
SELECT_CONFIG_BTN = (
    By.XPATH,
    "//div[@class='title' and normalize-space(text())='配置选择']",
)
# 配置选择页面返回按钮（H5 顶部 headerBox 内的返回图标）
SELECT_CONFIG_BACK_BTN = (
    By.XPATH,
    "//*[@id='headerBox']/div[4]/div[1]/i",
)


__all__ = [
    "AGGREGATE_BUTTON", "PERMISSION_ALLOW_BTN",
    "AGGREGATE_ORDER_BTN", "AGGREGATE_RESERVE_BTN",
    "SELECT_CONFIG_BTN", "SELECT_CONFIG_BACK_BTN",
]
