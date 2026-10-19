# -*- coding: utf-8 -*-
"""
用例1: 打开长安启源APP -> 等 2S -> 处理崩溃弹窗 -> 点击底部"我的" -> 点击"粉丝"

对应源文件: AI_agent_DOM/testcase.txt
驱动方式: appium-mcp(调用 appium Session/Driver 而非 selenium-style 关键字)
"""
import time

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


# ---------- 全局配置 ----------
APP_PACKAGE = "com.changan.oushangCos1"
APP_ACTIVITY = ".DefaultAliasActivity"
WAIT_AFTER_LAUNCH = 2  # 用例要求: 等 2S
IMPLICIT_WAIT = 10


# ---------- Fixture ----------
@pytest.fixture(scope="function")
def driver():
    """启动长安启源 APP 并返回 driver;用例结束后关闭会话。"""
    options = UiAutomator2Options()
    options.no_reset = True
    options.set_capability("appium:appPackage", APP_PACKAGE)
    options.set_capability("appium:appActivity", APP_ACTIVITY)
    options.set_capability("appium:noReset", True)
    options.set_capability("appium:autoLaunch", True)

    drv = webdriver.Remote("http://127.0.0.1:4723", options=options)
    drv.implicitly_wait(IMPLICIT_WAIT)
    yield drv
    drv.quit()


# ---------- 工具方法 ----------
def _close_crash_alert_if_present(driver):
    """如出现崩溃弹窗,点击"关闭应用"。"""
    time.sleep(WAIT_AFTER_LAUNCH)
    try:
        # 标题: "长安启源屡次停止运行"
        title = driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().textContains("屡次停止运行")',
        )
        if title.is_displayed():
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("关闭应用")',
            ).click()
            # 关闭弹窗后稍作停顿,再由后续步骤重新激活
            time.sleep(1)
            return True
    except Exception:
        pass
    return False


# ---------- 用例 ----------
@pytest.mark.regression
def test_open_app_click_my_fans(driver):
    """用例1: 打开长安启源APP -> 等 2S(崩溃弹窗处理) -> 我的 -> 粉丝。"""
    # Step 1: 拉起 APP(已在 fixture 中完成)并等 2S
    closed = _close_crash_alert_if_present(driver)
    if closed:
        # 关闭弹窗后,重新激活一次确保 APP 进入正常态
        driver.activate_app(APP_PACKAGE)
        time.sleep(WAIT_AFTER_LAUNCH)

    # Step 2: 点击底部"我的"
    my_tab = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("我的")',
    )
    my_tab.click()

    # Step 3: 点击"粉丝"
    fans_entry = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("粉丝")',
    )
    fans_entry.click()

    # 断言已进入"我的粉丝"页
    time.sleep(1)
    title = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("我的粉丝")',
    )
    assert title.is_displayed(), "未进入'我的粉丝'页面"