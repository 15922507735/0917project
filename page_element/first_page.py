"""发现-推荐首页元素层。

仅存放「发现」首页 / 「推荐」二级 Tab 的定位表达式。

历史背景：本文件早期版本用
    "//*[@text='发现' or .//*[@text='发现']]"
等"按文字找容器"的方式定位，发现页结构改版后全部失效；
更新框架前最后一次能跑通的版本（qiyuantest 提交，scripts/test_login.py）用的是
    "(.//android.view.ViewGroup[@resource-id='com.changan.oushangCos1:id/rlt'])[1]"
直接选第一个 rlt 容器作为「发现」入口。本文件恢复该写法。
"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .login_page import APP_PACKAGE

# 旧框架（qiyuantest）写法：直接取第 1 个 rlt 容器作为「发现」入口。
# 不再用 rlt+"发现"双条件 XPath，避免发现页改版后 0 命中。
DISCOVER_BUTTON = (
    By.XPATH,
    f"(//android.view.ViewGroup[@resource-id='{APP_PACKAGE}:id/rlt'])[1]",
)
# 「发现」页内嵌的「推荐」二级 Tab（TextView id=tv_tab 且 text='推荐'）
RECOMMEND_BUTTON = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='推荐']",
)


__all__ = ["DISCOVER_BUTTON", "RECOMMEND_BUTTON"]
