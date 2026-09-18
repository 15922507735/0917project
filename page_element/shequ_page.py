"""社区页元素层。"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy

from .login_page import APP_PACKAGE

# 社区 Tab 按钮（底部导航栏的"社区"）
SHEQU_TAB = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='社区']",
)
# 热门话题元素（社区页加载完成的标志）
HOT_TOPIC = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tvht",
)
# 话题广场按钮（社区页内的二级入口）
TOPIC_SQUARE_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tvht",
)

__all__ = ["SHEQU_TAB", "HOT_TOPIC", "TOPIC_SQUARE_BTN"]
