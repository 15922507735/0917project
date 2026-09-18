"""活动页元素层。"""
from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE
from selenium.webdriver.common.by import By

# 活动 Tab 按钮
HUODONG_TAB = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='活动']",
)
# 活动列表元素
HUODONG_LIST = (
    AppiumBy.XPATH,
    "//android.widget.TextView[@text='活动列表']",
)
# 活动状态
HUODONG_STATUS = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_state' and @text='活动状态']",
)
# 选择状态按钮
SELECT_HUODONG_STATUS_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tvTitle",
)
# 确定按钮
HUODONG_CONFIRM_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/btnSubmit",
)

