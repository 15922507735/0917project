"""发现-推荐首页操作层：封装「发现」Tab、「推荐」二级 Tab、列表滑动等操作。

仅依赖 page_element.first_page 中的元素常量，
不包含用例断言，方便在用例层（testcase_manage/test_first_page.py）中复用。
"""
from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.first_page import DISCOVER_BUTTON, RECOMMEND_BUTTON
from page_element.login_page import APP_PACKAGE, EXPECT_WAIT_TIMEOUT


class FirstPageOperate:
    """「发现-推荐」首页操作封装。"""

    def __init__(self, driver: WebDriver, logger: Any, expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT):
        self.driver = driver
        self.logger = logger
        self.expect_wait_timeout = expect_wait_timeout

    # ===================== 滑动工具 =====================
    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 500,
    ) -> None:
        """W3C Actions 滑动优先；失败时 fallback 到 mobile: swipe。

        Appium-Python-Client 4.x 已移除 driver.swipe(..., duration_ms)，
        因此本方法统一走 W3C Actions + mobile command 兜底。
        """
        try:
            actions = ActionChains(self.driver)
            pa = actions.w3c_actions.pointer_action
            pa.move_to_location(start_x, start_y)
            pa.pointer_down()
            pa.move_to_location(end_x, end_y)
            pa.pause(duration_ms / 1000)
            pa.pointer_up()
            actions.perform()
            self.logger.info(
                f"[swipe] W3C Actions 成功：({start_x},{start_y}) -> "
                f"({end_x},{end_y}) 耗时 {duration_ms}ms"
            )
        except Exception as e:
            self.logger.warning(
                f"[swipe] W3C Actions 失败，回退到 mobile: swipe：{e}"
            )
            self.driver.execute_script(
                "mobile: swipe",
                {
                    "startX": start_x,
                    "startY": start_y,
                    "endX": end_x,
                    "endY": end_y,
                    "duration": duration_ms,
                },
            )
            self.logger.info(
                f"[swipe] mobile: swipe 成功：({start_x},{start_y}) -> "
                f"({end_x},{end_y}) 耗时 {duration_ms}ms"
            )

    # ===================== 页面探测 =====================
    def is_on_discover_page(self) -> bool:
        """判断当前是否已处于「发现」页。

        判据：
        1) current_package == APP_PACKAGE（APP 在前台，没被弹桌面）；
        2) 「推荐」二级 Tab（tv_tab='推荐'）2s 内可见。

        noReset=True 场景下，登录成功 + 热启动 APP 后会停留在发现页，
        此时 RECOMMEND_BUTTON 一定可见，无需再走"点同意 / 左滑 / 入口 5 次"前置流程。
        """
        try:
            if self.driver.current_package != APP_PACKAGE:
                self.logger.info(
                    f"[is_on_discover] current_package={self.driver.current_package} "
                    f"≠ {APP_PACKAGE}，未在 APP 内"
                )
                return False
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located(RECOMMEND_BUTTON)
            )
            self.logger.info("[is_on_discover] 推荐 Tab 可见 → 已在发现页")
            return True
        except Exception:
            self.logger.info("[is_on_discover] 推荐 Tab 不可见 → 未在发现页")
            return False

    # ===================== Tab 切换 =====================
    def click_discover_tab(self) -> None:
        """点击底部「发现」Tab；等待元素可点击。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(DISCOVER_BUTTON)
        ).click()
        sleep(1)
        self.logger.info("已点击底部'发现'Tab")

    def wait_recommend_tab_visible(self) -> None:
        """等待「推荐」二级 Tab 可见，用于断言发现页加载完成。"""
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.presence_of_element_located(RECOMMEND_BUTTON)
        )
        self.logger.info("已检测到'推荐'按钮")

    def click_recommend_btn(self) -> None:
        """点击「发现」页内嵌的「推荐」二级 Tab。"""
        # 不复用 LoginOperate._click，避免引入耦合；这里直接 WebDriverWait + click
        WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.element_to_be_clickable(RECOMMEND_BUTTON)
        ).click()
        self.logger.info("已点击'推荐'按钮")

    # ===================== 列表滑动 =====================
    def swipe_up_recommend(self) -> None:
        """推荐页向上滑动一次（温和滚动，避免触发底部 Tab 横滑）。"""
        sleep(1)  # 等列表稳定再滑
        # 与旧项目保持一致的滑动坐标
        self.swipe(start_x=450, start_y=1253, end_x=450, end_y=500, duration_ms=800)
        self.logger.info("已向上滑动推荐页面")

