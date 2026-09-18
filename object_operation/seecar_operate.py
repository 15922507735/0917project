"""看车 / Q05 车型页操作层。"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.seecar_page import SEECAR_TAB


class SeeCarOperate:
    """看车 / Q05 车型页操作封装。"""

    def __init__(
        self,
        driver: WebDriver,
        logger: Any,
        expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT,
    ):
        self.driver = driver
        self.logger = logger
        self.expect_wait_timeout = expect_wait_timeout

    # ===================== 工具方法 =====================
    def _dump_visible_texts(self, label: str, limit: int = 30) -> None:
        """打印当前页面所有可见元素的 text+id（仅前 N 条），用于排查元素定位问题。"""
        try:
            els = self.driver.find_elements(
                By.XPATH, "//*[@text!='' or @resource-id!='']"
            )
            self.logger.info(f"[{label}] 当前页面可见元素（前 {limit} 条）：")
            for i, el in enumerate(els[:limit], 1):
                self.logger.info(
                    f"  [{i}] text='{el.text}', "
                    f"id='{el.get_attribute('resource-id')}', "
                    f"class='{el.get_attribute('class')}'"
                )
        except Exception as e:
            self.logger.warning(f"[{label}] dump 可见元素失败: {e}")

    # ===================== 看车 Tab =====================
    def click_entry_btn(self) -> None:
        """点击顶部「看车」Tab。"""
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(SEECAR_TAB)
            ).click()
            self.logger.info("已点击看车 Tab")
        except Exception as e:
            self.logger.error(
                f"点击看车 Tab 失败: {e}, Activity={self.driver.current_activity}"
            )
            raise

    # ===================== Q05 车型入口 =====================
    def click_q05_icon(self) -> None:
        """用固定坐标点击「全新Q05」车标（看车页顶部车系轮播栏第 2 项）。

        真实坐标由用户提供：(245, 314) —— 看车页第 2 个"全新Q05"车标中心。
        经过多种定位方式尝试（ImageView/外层 ViewGroup/文字标签/swipe），都无效；
        改用坐标点击 —— 最稳。

        屏幕分辨率依赖：如果换了设备/分辨率，这个坐标可能需要按比例调整。
        调整公式：x = 245/720 * screen_w, y = 314/1280 * screen_h
        """
        # 1. 真实坐标（用户提供，720x1280 屏）
        REAL_X = 245
        REAL_Y = 314
        REF_SCREEN_W = 720
        REF_SCREEN_H = 1280

        # 2. 按当前屏幕分辨率做比例缩放
        try:
            size = self.driver.get_window_size()
            screen_w = size["width"]
            screen_h = size["height"]
            self.logger.info(
                f"屏幕尺寸: {screen_w}x{screen_h} (参考: {REF_SCREEN_W}x{REF_SCREEN_H})"
            )
            x = int(REAL_X * screen_w / REF_SCREEN_W)
            y = int(REAL_Y * screen_h / REF_SCREEN_H)
        except Exception as e:
            self.logger.warning(f"获取屏幕尺寸失败，用真实坐标: {e}")
            x, y = REAL_X, REAL_Y

        self.logger.info(f"用坐标点击全新Q05 车标: ({x}, {y})")
        try:
            # 优先用 TouchAction（Appium 2 推荐）
            from appium.webdriver.common.touch_action import TouchAction
            TouchAction(self.driver).tap(x=x, y=y).perform()
        except Exception:
            # 退化方案：driver.tap
            self.driver.tap([(x, y)])

        self.logger.info(f"已用坐标点击全新Q05 车标 ({x}, {y})")

        # 等车系详情异步加载
        sleep(2)
        self.logger.info("已等待 2s 让 Q05 详情加载完成")

