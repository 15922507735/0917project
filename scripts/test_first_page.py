"""发现-推荐首页用例集合（占位骨架）。"""
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pytest


def test_collectible_smoke():
    """纯冒烟用例：不依赖 Appium driver，验证 pytest 能收集到此文件。"""
    assert True