"""看车页 / Q05 车型页元素层。"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .login_page import APP_PACKAGE

# "看车" 二级 Tab（与发现页底栏 tv_tab 复用，text 不同）
SEECAR_TAB = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='看车']",
)
# Q05 车型入口（看车页顶部车系轮播栏第 2 项）
# 用户手动操作时点红色方框区域能切换车系。
# 红色方框是 ImageView#iv_cover 车标本身（[2] = 全新Q05），
# 但 find_element().click() 在 ImageView 上无效（无 click 监听）。
# 改点外层 clickable=true 的 ViewGroup 容器，元素结构：
#   ViewGroup (clickable=true, 第 [2] 个) > FrameLayout > LinearLayout > ImageView#iv_cover
Q05_ICON = (
    By.XPATH,
    "(//*[@clickable='true' and .//android.widget.ImageView[@resource-id='"
    "com.changan.oushangCos1:id/iv_cover']])[2]",
)

__all__ = ["SEECAR_TAB", "Q05_ICON"]
