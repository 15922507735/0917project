"""调试 / 排障工具函数（无状态，跨模块复用）。

提供页面元素 dump、WebView 源码 dump、ANR 弹窗关闭等通用排障能力。
所有函数均为独立函数，接收 (driver, logger, ...) 参数，不依赖任何类实例。
"""
from __future__ import annotations

from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import CLOSE_BTN


def dump_visible(
    driver: WebDriver,
    logger: Any,
    label: str,
    limit: int | None = None,
) -> None:
    """打印当前页面所有可见元素的 text / resource-id / class，便于排查定位问题。

    参数：
        driver: Appium / Selenium driver 实例。
        logger: 日志对象。
        label: 日志标签（如用例名 / 操作名），用于区分不同 dump 来源。
        limit: 最多打印前 N 条元素；None 表示全部打印。
    """
    try:
        elements = driver.find_elements(
            By.XPATH, "//*[@text!='' or @resource-id!='']"
        )
        if limit is not None:
            elements = elements[:limit]
            logger.info(f"[{label}] 当前页面可见元素（前 {limit} 条）：")
        else:
            logger.info(f"[{label}] 当前页面可见元素：")
        for i, el in enumerate(elements, 1):
            logger.info(
                f"  [{i}] text='{el.text}', "
                f"id='{el.get_attribute('resource-id')}', "
                f"class='{el.get_attribute('class')}'"
            )
    except Exception as e:
        logger.warning(f"[{label}] dump 可见元素失败: {e}")


def dump_webview_html(
    driver: WebDriver,
    logger: Any,
    save_name: str = "debug_webview.html",
) -> None:
    """dump 当前 WebView 页面源码到本地文件，便于排查 H5 元素定位失败。"""
    try:
        html = driver.page_source
        with open(save_name, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(
            f"已保存 WebView 页面源码: {save_name} (length={len(html)})"
        )
    except Exception as e:
        logger.warning(f"保存 WebView 源码失败: {e}")


def close_anr_if_exists(
    driver: WebDriver,
    logger: Any,
    timeout: int = 2,
) -> bool:
    """检测并关闭系统级 ANR / 崩溃弹窗，返回 True 表示关闭了一次。

    参数：
        driver: Appium driver 实例。
        logger: 日志对象。
        timeout: 等待弹窗出现的超时秒数，默认 2s。
    """
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(CLOSE_BTN)
        )
        if btn.is_displayed():
            btn.click()
            logger.info("[ANR] 已关闭 ANR / 崩溃弹窗")
            return True
    except Exception:
        return False
    return False
