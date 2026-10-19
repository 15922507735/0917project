"""发现-推荐首页元素层。

仅存放「发现」首页 / 「推荐」二级 Tab 的定位表达式。

历史背景：
- 旧框架 (qiyuantest) 用 ``(//rlt)[1]`` 选第一个 rlt 容器作为「发现」入口。
- 实际底部 Tab 栏结构是
    [78] text='发现', id='com.changan.oushangCos1:id/title'
    [82] text='服务', id='com.changan.oushangCos1:id/title'
    [86] text='购车', id='com.changan.oushangCos1:id/title'
    [91] text='商城', id='com.changan.oushangCos1:id/title'
    [95] text='我的', id='com.changan.oushangCos1:id/title'
  ``rlt`` 在登录后跳到的"我的"页里没有，强行用 rlt 找不到元素。
- 改用底部 Tab 栏的 TextView text='发现' 精确定位「发现」Tab。
"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .login_page import APP_PACKAGE

# 底部 Tab 栏的「发现」Tab（TextView id=title 且 text=发现）
DISCOVER_BUTTON = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/title' and @text='发现']",
)
# 「发现」页内嵌的「推荐」二级 Tab（TextView id=tv_tab 且 text='推荐'）
RECOMMEND_BUTTON = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='推荐']",
)


__all__ = ["DISCOVER_BUTTON", "RECOMMEND_BUTTON"]
