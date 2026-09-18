"""社区页元素层。"""
from __future__ import annotations
from appium.webdriver.common.appiumby import AppiumBy
from .login_page import APP_PACKAGE
from selenium.webdriver.common.by import By
import pytest



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
# 话题广场按钮（社区页内的二级入口）—— 按文本定位（社区页上"话题广场"唯一且可点击）
TOPIC_SQUARE_BTN = (
    AppiumBy.XPATH,
    "//android.widget.TextView[@text='话题广场']",
)

# 话题列表页面标题
TOPIC_TITLE = (
    By.XPATH,
    "//*[@id='app']/div[1]/div[1]/div[2]/span",
)
# 话题列表返回按钮
TOPIC_BACK_BTN = (
    By.XPATH,
    "//*[@id='app']/div[1]/div[1]/div[1]/div",
)

# 查看更多按钮（社区页"热门圈子"右侧，真实 id=tvmorequanzi）
TOPIC_MORE_BTN = (
    AppiumBy.ID,
    "com.changan.oushangCos1:id/tvmorequanzi",
)
# 所有圈子页（circle-more WebView）元素 —— 定位来自真实 DOM dump
# 顶部返回按钮：<div class="header-back">
TOPIC_ALL_BACK_BTN = (
    By.CSS_SELECTOR,
    ".header-back",
)
# 地域标签：<div class="">地域</div>（选中后 class 变为 active）
TOPIC_ALL_REGION_BTN = (
    By.XPATH,
    "//div[text()='地域']",
)
# 兴趣标签
TOPIC_ALL_INTEREST_BTN = (
    By.XPATH,
    "//div[text()='兴趣']",
)
# 点地域后出现的省份圈子内容（广东/重庆任一出现即成功）
TOPIC_ALL_REGION_CONTENT = (
    By.XPATH,
    "//*[contains(text(),'广东省') or contains(text(),'重庆')]",
)
# 社区内容标签-最新
TOPIC_ALL_PAGE_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='最新']",
)
# 社区内容标签-精选（用于断言"回到社区页"）
TOPIC_NEIRONG_JINGXIN_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='精选']",
)
# 社区内容标签-视频
TOPIC_ALL_VIDEO_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='视频']",
)
# 社区内容标签-关注
TOPIC_ALL_FOLLOW_BTN = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_tab' and @text='关注']",
)
# 社区内容标签-聊天
TOPIC_ALL_CHAT_BTN = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tv_imChatList",
)  
# 聊天列表
TOPIC_ALL_CHAT_LIST = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/tv01",
)
# 聊天页面返回按钮
TOPIC_ALL_CHAT_BACK_BTN = (
    AppiumBy.ID,
    f"com.changan.oushangCos1:id/tv_head_callBack2",
)


__all__ = [
    "SHEQU_TAB", 
    "HOT_TOPIC", 
    "TOPIC_SQUARE_BTN", 
    "TOPIC_TITLE", 
    "TOPIC_BACK_BTN", 
    "TOPIC_ALL_PAGE_BTN", 
    "TOPIC_ALL_VIDEO_BTN", 
    "TOPIC_ALL_FOLLOW_BTN", 
    "TOPIC_ALL_CHAT_BTN",
    "TOPIC_ALL_CHAT_LIST",
    "TOPIC_ALL_CHAT_BACK_BTN",
    ]
