"""登录页 / 应用级元素层。

仅存放定位表达式元组，不包含任何业务逻辑。
- 应用级常量（包名、Activity、设备名、Appium 地址）集中放在本文件；
- 登录页相关元素（同意按钮、账号 / 密码 / 验证码输入框、登录按钮等）放本文件；
- 「发现 / 推荐 / 资讯 / 聚合页 / WebView」元素已迁出到 first_page / consult_page / order_page。
"""
from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

# ===================== 应用级常量 =====================
# 待测 APP 包名
APP_PACKAGE = "com.changan.oushangCos1"
# 启动 Activity
APP_ACTIVITY = ".DefaultAliasActivity"
# 允许停留的 Activity 列表（多 Activity 串行等待，逗号分隔）
APP_WAIT_ACTIVITY = (
    f"{APP_PACKAGE}/.DefaultAliasActivity,"
    "com.changan.qiyuan.SplashActivity,"
    "com.changan.qiyuan.activity.QYMainActivity,"
    "com.changan.qiyuan.activity.QYLeadingActivity,"
    "com.changan.qiyuan.my.activity.QYLoginActivty"
)
# 设备名（默认模拟器）
DEVICE_NAME = "emulator-5554"
# Appium 2 服务地址（注意：Appium 2 已不带 /wd/hub）
APPIUM_SERVER = "http://127.0.0.1:4723"
# 全局隐式等待 / 显式等待超时（秒）
EXPECT_WAIT_TIMEOUT = 10

# ===================== 启动阶段元素 =====================
# 启动时的隐私协议"同意"按钮
AGREEMENT_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/submit")
# 系统级 ANR / 崩溃弹窗的关闭按钮
CLOSE_BTN = (AppiumBy.ID, "android:id/aerr_close")
# 引导页点击入口
CLICK_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/img")

# ===================== 底部 Tab =====================
# 底部 Tab "我的"（XPath 按文本匹配，与旧框架 scripts/test_login.py 一致）
MY_BTN = (By.XPATH, "//*[@text='我的']")

# ===================== 登录入口 =====================
# "未登录"入口
LOGINOUT_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvloginout")
# 切换"密码登录"
GO_PASSLOGIN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tv_gopasslogin")

# ===================== 登录表单元素 =====================
# 手机号输入框
IMSPHONE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpasswordphone")
# 密码输入框（与图形验证码同 id，复用不同位置）
IMGCODE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpassword")
# 图形验证码输入框
PHONECODE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpassimgcode")
# 图形验证码图片
CAPTCHA_IMG = (AppiumBy.ID, f"{APP_PACKAGE}:id/ivpassimgcode")
# 登录页底部"同意协议"复选框
AGREEMENT = (AppiumBy.ID, f"{APP_PACKAGE}:id/cb_agreement")
# 登录按钮
LOGIN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tv_login")
# 登录成功后的昵称元素（用于断言）
LOGINING_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvlogining")
# 签到按钮（登录后页面常见）
SIGN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvsign")

# 显式声明对外暴露的常量，方便 from page_element.login_page import * 使用
__all__ = [
    # 应用级常量
    "APP_PACKAGE", "APP_ACTIVITY", "APP_WAIT_ACTIVITY",
    "DEVICE_NAME", "APPIUM_SERVER", "EXPECT_WAIT_TIMEOUT",
    # 启动阶段
    "AGREEMENT_BTN", "CLOSE_BTN", "CLICK_BTN",
    # 底部 Tab
    "MY_BTN",
    # 登录入口
    "LOGINOUT_BTN", "GO_PASSLOGIN_BTN",
    # 登录表单
    "IMSPHONE", "IMGCODE", "PHONECODE", "CAPTCHA_IMG",
    "AGREEMENT", "LOGIN_BTN", "LOGINING_BTN", "SIGN_BTN",
]
