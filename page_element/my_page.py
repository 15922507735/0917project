from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE
from selenium.webdriver.common.by import By

# 底部我的按钮
MY_TAB = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@text='我的']/..",
)
# 我的-设置按钮
MY_SETTING_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/iv_msgset",
)
# 我的-皮肤按钮
MY_SKIN_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/iv_pifu",
)
# 第一个皮肤卡片 —— 按 skin_name 文字"系统默认"找同一卡片容器的 ImageView
# 用 parent::* 定位，因为实际 DOM 是 TextView 嵌套在 ViewGroup > ImageView 内
MY_SKIN_CARD_FIRST = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/skin_name' and @text='系统默认']/parent::*/android.widget.ImageView[@resource-id='{APP_PACKAGE}:id/skin_img']",
)
# 第二个皮肤卡片 —— 按 skin_name 文字"长安启源Q06"找同一卡片容器的 ImageView
MY_SKIN_CARD_SECOND = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/skin_name' and @text='长安启源Q06']/parent::*/android.widget.ImageView[@resource-id='{APP_PACKAGE}:id/skin_img']",
)
# 皮肤详情页-立即使用按钮
MY_SKIN_USE_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@resource-id='{APP_PACKAGE}:id/bt' and @text='立即使用']",
)
# 挂件按钮
MY_SKIN_TAB_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='挂件']",
)
# 第二个挂件卡片
MY_GUAJIAN_CARD_SECOND = (
    AppiumBy.ANDROID_UIAUTOMATOR,
    f'new UiSelector().resourceId("{APP_PACKAGE}:id/tag_bg").instance(1)',
)
# 无挂件卡片
MY_SKIN_CARD_NO = (
    AppiumBy.ANDROID_UIAUTOMATOR,
    f'new UiSelector().resourceId("{APP_PACKAGE}:id/tag_bg").instance(0)',
)
# 立即佩戴按钮
MY_GUAJIAN_USE_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/btn_use",
)
# 个性装扮返回按钮
MY_GUAJIAN_BACK_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/bar_img_back",
)
# 正在使用
MY_GUAJIAN_USEING_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@resource-id='{APP_PACKAGE}:id/bt' and @text='正在使用']",
)
# 皮肤详情页返回按钮（采用系统返回键 driver.back()，此处保留常量占位但不再使用）
# 挂件入口按钮
MY_GUAJIAN_TAB_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='挂件']",
)
# 无挂件卡片
MY_GUAJIAN_CARD_NO = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tag_name' and @text='无挂件']",
)


