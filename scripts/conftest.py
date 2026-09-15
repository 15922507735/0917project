"""pytest 公共 fixture：启动 Appium session 并接受隐私协议。

提供给同一目录下的 test_*.py 使用。模块名以 conftest.py 命名，
pytest 会自动加载，无需在用例文件里显式 import。
"""
from __future__ import annotations

import logging
from time import sleep

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from test_login import (
    AGREEMENT_BTN,
    APP_ACTIVITY,
    APP_PACKAGE,
    APP_WAIT_ACTIVITY,
    APPIUM_SERVER,
    DEVICE_NAME,
    EXPECT_WAIT_TIMEOUT,
    Login_Process,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("summitbuy")


def _build_appium_options() -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name = "android"
    options.platform_version = "9"
    options.device_name = DEVICE_NAME
    options.udid = DEVICE_NAME
    options.automation_name = "UiAutomator2"
    options.unicode_keyboard = True
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.app_wait_activity = APP_WAIT_ACTIVITY
    return options


@pytest.fixture(scope="session")
def appium_driver():
    """session 级 fixture：启动 Appium、点击启动时"授权弹窗"同意按钮，结束用例 quit。

    yield 一个 appium.webdriver 实例，登录流程类可以基于它继续操作。
    """
    log.info("[fixture] 启动 Appium session ...")
    d = webdriver.Remote(APPIUM_SERVER, options=_build_appium_options())
    d.implicitly_wait(EXPECT_WAIT_TIMEOUT)
    sleep(5)

    log.info(f"[fixture] 当前 Activity: {d.current_activity}")
    log.info(f"[fixture] 当前包名: {d.current_package}")

    # 启动时弹出的隐私协议授权弹窗
    try:
        WebDriverWait(d, 10).until(
            EC.element_to_be_clickable(AGREEMENT_BTN)
        ).click()
        log.info("[fixture] 已点击启动时授权弹窗的同意按钮")
    except Exception as e:
        log.error(f"[fixture] 启动时未找到授权同意按钮: {e}")
        try:
            d.save_screenshot("debug_no_agreement.png")
        except Exception:
            pass
        d.quit()
        raise

    try:
        yield d
    finally:
        log.info("[fixture] 关闭 Appium session")
        try:
            d.quit()
        except Exception:
            pass


@pytest.fixture
def login_process(appium_driver):
    """用例级 fixture：注入 Login_Process 实例。"""
    return Login_Process(appium_driver, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)