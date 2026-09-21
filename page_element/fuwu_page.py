"""服务模块页面元素。"""

from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE
from selenium.webdriver.common.by import By
import pytest

# 底部服务按钮：按 text 找到"服务"TextView，再取其父 ViewGroup（rlt），整块点击更稳
FUWU_TAB = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@text='服务']/..",
)
# 门店文本元素
STORE_TEXT = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tvtitle' and @text='门店']",
)
# 门店跳转按钮
STORE_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/imgrt",
)
# 门店详情位置按钮
STORE_ADDRESS_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_address'][1]",
)
# 位置弹窗确定按钮
STORE_ADDRESS_BTN_SUBMIT = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/btnSubmit",
)
# 门店详情搜索输入框
STORE_SEARCH_INPUT = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/et_search",
)
# 收起展开按钮
STORE_SEARCH_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/iv_menu",
)
# 交付中心按钮
STORE_DELIVER_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='交付中心']",
)
# 维保中心按钮
STORE_MAINT_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='维保中心']",
)
# 门店详情返回按钮
STORE_BACK_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/bar_img_back",
)
# 预约试驾按钮
STORE_RESERVE_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tv_reservation",
)
# 心仪车系按钮
STORE_FAVORITE_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@text='心仪车型 心仪车型']",
)
# 心仪车系确认按钮
STORE_FAVORITE_BTN_SUBMIT = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@text='确定']",
)
# 试驾页面订单中心按钮
STORE_ORDER_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@text='订单中心 订单中心']",
)
# 好评优先按钮
STORE_GOOD_BTN = (
    AppiumBy.XPATH,
    f"//android.view.View[@text='好评优先']",
)
# 距离最近按钮
STORE_DISTANCE_BTN = (
    AppiumBy.XPATH,
    f"//android.view.View[@text='距离最近']",
)
# 经销商页面返回按钮
STORE_BACK_BTN = (
    AppiumBy.XPATH,
    f"//android.view.View[@resource-id='{APP_PACKAGE}:id/headerBox']/android.view.View[1]/android.view.View[1]",
)
# 姓名输入框
STORE_NAME_INPUT = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/van-field-3-input",
)
# 同意协议按钮
STORE_AGREE_BTN = (
    AppiumBy.XPATH,
    f"//android.view.View[@resource-id='{APP_PACKAGE}:id/headerBox']/android.view.View[5]",
)
# 家充桩入口按钮
STORE_CHARGE_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/l1img2",
)
# 华为超充入口
STORE_CHARGE_BTN_HUAWEI = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/l1img3",
)
# 家充服务文本元素
STORE_CHARGE_TEXT = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@text='家充服务']",
)
# 家充桩文本元素
STORE_CHARGE_PILL_TEXT = (
    AppiumBy.XPATH,
    f"//android.view.View[@text='家充桩'][2]",
)
# 家充装返回按钮
STORE_CHARGE_BACK_BTN = (
    AppiumBy.XPATH,
    f"//android.view.View[@resource-id='app']/android.view.View[2]/android.view.View/android.view.View[1]/android.view.View[1]",
)
