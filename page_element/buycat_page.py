from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE

"""
购车页面元素
"""
# 购车tab按钮（底部 Tab 上的"购车"文字，resource-id 与其他 Tab 共用 title，用 text 精确匹配）
STORE_BUY_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/title' and @text='购车']",
)
# 立即订购按钮
STORE_ORDER_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/btn2",
)
# 购车配置选择页 - "请选择配置" 提示文本（WebView/uni-app 页面）
STORE_CONFIG_CHOOSE_TIP = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bdp1') and normalize-space()='请选择配置']",
)
# 点击车型版本
STORE_CONFIG_VERSION_BTN = (
    AppiumBy.XPATH,
    "//*[@resource-id='app']/div[2]/div/div[3]/div[2]/div[1]",
)
# 车型版本卡片 - 通过版本名精确定位（如 "700 智尊型天枢领航Ultra版"）
STORE_CONFIG_VERSION_BY_NAME = (
    AppiumBy.XPATH,
    "//div[contains(@class,'mvList') and .//div[contains(@class,'mvLTit') and contains(., '700 智尊型天枢领航Ultra版')]]",
)
# 车型版本卡片 - 取第一个版本（点击区域）
STORE_CONFIG_VERSION_FIRST = (
    AppiumBy.XPATH,
    "(//div[contains(@class,'mvList')])[1]",
)
# 车型版本卡片 - CSS_SELECTOR 写法（点整个 mvList）
STORE_CONFIG_VERSION_FIRST_CSS = (
    AppiumBy.CSS_SELECTOR,
    "div.mvList",
)
# 车型版本标题 - CSS_SELECTOR 写法（点 mvlTit 文字部分，注意是小写 L 不是大写 T）
STORE_CONFIG_VERSION_TITLE_CSS = (
    AppiumBy.CSS_SELECTOR,
    "div.mvlTit",
)
# 车型版本标题 - XPATH 写法（按版本名锁定，单版本唯一）
STORE_CONFIG_VERSION_TITLE = (
    AppiumBy.XPATH,
    "//div[contains(@class,'mvlTit') and contains(., '700 智尊型天枢领航Ultra版')]",
)
# 车型版本标题 - CSS_SELECTOR 取第一个版本的标题（限定在 mvList 容器下）
STORE_CONFIG_VERSION_FIRST_TITLE_CSS = (
    AppiumBy.CSS_SELECTOR,
    "div.mvList:nth-of-type(1) > div.mvlTit",
)
# 购车配置选择页 - "外观 ->" 下一步按钮（WebView/uni-app 页面）
# 精确定位：bottomDes 容器下 + bdBtn 内含 span "外观"，排除底部 Tab
STORE_CONFIG_NEXT_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bottomDes')]//div[contains(@class,'bdBtn')][.//span[contains(.,'外观')]]",
)
# 购车配置选择页 - "内饰" Tab 按钮（WebView/uni-app 页面）
STORE_CONFIG_INTERIOR_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bdBtn')]//span[text()='内饰']",
)
# 购车配置选择页 - 右下角深色"内饰 ->" 下一步按钮（WebView/uni-app 页面）
STORE_CONFIG_INTERIOR_NEXT_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bottomDes')]/div[contains(@class,'bdBtn')]//span[text()='内饰']",
)
# 金额文本（WebView/uni-app 页面）
STORE_CONFIG_PRICE = (
    AppiumBy.XPATH,
    "//div[contains(@class,'mvTxt')]//div[contains(text(),'¥')]",
)
# 点击外观颜色卡片
STORE_CONFIG_EXT_COLOR_BTN = (
    AppiumBy.XPATH,
    "//*[@id='van-tab-2']/div/div[1]/div[1]/img",
)
# 选装按钮到下一步
STORE_CONFIG_EXT_NEXT_BTN = (
    AppiumBy.XPATH,
    "//*[@//*[@id='app']/div[2]/div/div[4]/div[2]/div",
)
# 内饰颜色卡片
STORE_CONFIG_INTERIOR_COLOR_BTN = (
    AppiumBy.XPATH,
    "//*[@//*[@id='van-tab-3']/div/div[1]/div[1]/img",
)
