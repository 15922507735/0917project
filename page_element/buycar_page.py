from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE
from selenium.webdriver.common.by import By



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
# 选装按钮到下一步（WebView/uni-app 页面）
# 与 STORE_CONFIG_NEXT_BTN / STORE_CONFIG_INTERIOR_NEXT_BTN 同模式：
# bottomDes 容器下 + bdBtn 内含 span "选装"
STORE_CONFIG_EXT_NEXT_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bottomDes')]//div[contains(@class,'bdBtn')][.//span[contains(.,'选装')]]",
)
# 内饰颜色卡片（van-tab-3 为内饰 Tab 下的图片卡片）
STORE_CONFIG_INTERIOR_COLOR_BTN = (
    AppiumBy.XPATH,
    "//*[@id='van-tab-3']/div/div[1]/div[1]/img",
)
# 添加🤔按钮
STORE_CONFIG_THINK_BTN = (
    AppiumBy.XPATH,
    "//*[@id='van-tab-4']/div/div/div[2]/div[2]",
)
# "订单中心 ->" 下一步按钮（切 Tab 到订单中心）
# 与 STORE_CONFIG_NEXT_BTN / STORE_CONFIG_INTERIOR_NEXT_BTN / STORE_CONFIG_EXT_NEXT_BTN 同模式：
# bottomDes 容器下 + bdBtn 内含 span "订单中心"
STORE_CONFIG_ORDER_NEXT_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bottomDes')]//div[contains(@class,'bdBtn')][.//span[contains(.,'订单中心')]]",
)
# 完成配置按钮
STORE_CONFIG_COMPLETE_BTN = (
    AppiumBy.XPATH,
    "//div[contains(@class,'bottomDes')]//div[contains(@class,'bdBtn')][.//span[contains(.,'完成配置')]]",
)
# 订单中心勾选按钮 —— 点商家列表第一条的左侧圆形勾选 icon
# van-tab-5 下 listbox 容器内的第一个 list-l 元素下的 icon（listbox 是商家列表容器）
STORE_CONFIG_ORDER_CHECK_BTN = (
    AppiumBy.XPATH,
    "//*[@id='van-tab-5']//div[contains(@class,'listbox')][1]//i[contains(@class,'icon')]",
)
# 保存配置按钮
STORE_CONFIG_SAVE_BTN = (
    AppiumBy.XPATH,
    "//*[@id='app']/div[2]/div/div[4]/div[4]/div/div[1]",
)
# 去订购按钮
STORE_CONFIG_ORDER_BTN = (
    AppiumBy.XPATH,
    "//*[@id='app']/div[2]/div/div[4]/div[4]/div/div[2]",
)
# 车主姓名输入框（按 name 属性定位，避免 class 名变化导致失效）
STORE_CONFIG_NAME = (
    By.CSS_SELECTOR,
    'input[name="user"]',
)
# 证件号码输入框（按 name 属性定位，避免 class 名变化导致失效）
STORE_CONFIG_IDCARD = (
    By.CSS_SELECTOR,
    'input[name="idcard"]',
)
# 订购协议勾选框
STORE_CONFIG_PROTOCOL_CHECK_BTN = (
    By.XPATH,
    "//*[@id='app']/div[2]/div[1]/div[2]/div[1]/div/img",
)
# 提交订单按钮
STORE_CONFIG_SUBMIT_BTN = (
    By.XPATH,
    "//*[@id='app']/div[2]/div[1]/div[2]/div[2]/div/div",
)
# 我同意按钮
STORE_CONFIG_AGREE_BTN = (
    By.XPATH,
    "//*[@id='app']/div[2]/div/div/div[2]/div",
)
