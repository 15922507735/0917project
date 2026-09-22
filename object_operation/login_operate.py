"""登录操作层：封装登录流程中所有页面操作。

设计原则（PO 分层）：
- 只引用 page_element 中的元素常量，不直接写定位表达式；
- 构造方法接收 driver 与 logger，便于在用例中注入和复用；
- 不包含用例断言，仅封装"操作 + 失败 dump + 抛异常"；
- 业务方法命名统一为动词短语（如 click_xxx / input_xxx）。
"""
from __future__ import annotations

import re
from io import BytesIO
from time import sleep
from typing import Any

import ddddocr
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_element.login_page import (
    AGREEMENT,
    AGREEMENT_BTN,
    APP_PACKAGE,
    CAPTCHA_IMG,
    CLICK_BTN,
    CLOSE_BTN,
    EXPECT_WAIT_TIMEOUT,
    GO_PASSLOGIN_BTN,
    IMGCODE,
    IMSPHONE,
    LOGINING_BTN,
    LOGIN_BTN,
    LOGINOUT_BTN,
    MY_BTN,
    PHONECODE,
)

# ===================== 可调参数（phone / password） =====================
# 顶部集中维护默认账号；用例/测试可通过参数覆盖
DEFAULT_PHONE: str = "18908323900"
DEFAULT_PASSWORD: str = "Aa123456"


class LoginOperate:
    """登录页 / 前置引导页操作封装。

    使用方式：
        op = LoginOperate(driver, logger)
        op.click_agreement_btn()
        op.login(phone, password)
    """

    def __init__(self, driver: WebDriver, logger: Any, expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT):
        # 注入 driver 与 logger，避免在类内部硬编码
        self.driver = driver
        self.logger = logger
        self.expect_wait_timeout = expect_wait_timeout
        # ddddocr 初始化：beta=True 启用更强的字符识别模型；show_ad=False 不弹广告
        self.ocr = ddddocr.DdddOcr(beta=True, show_ad=False)

    # ===================== 内部工具方法 =====================
    def _dump_visible(self, label: str) -> None:
        """打印当前页面所有可见元素，便于排查 id 不存在的问题。"""
        try:
            elements = self.driver.find_elements(
                By.XPATH, "//*[@text!='' or @resource-id!='']"
            )
            self.logger.info(f"[{label}] 当前页面可见元素：")
            for el in elements:
                self.logger.info(
                    f"  - text='{el.text}', "
                    f"id='{el.get_attribute('resource-id')}', "
                    f"class='{el.get_attribute('class')}'"
                )
        except Exception as e:
            self.logger.warning(f"[{label}] dump 可见元素失败: {e}")

    def _click(self, locator, name: str) -> None:
        """点击元素；失败时 dump 可见元素 + 抛异常。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*locator).click()
            self.logger.info(f"已点击{name}")
        except Exception as e:
            self.logger.error(f"未找到'{name}': {e}")
            self._dump_visible(name)
            raise

    def _input(self, locator, text: str, name: str) -> None:
        """输入框清空 + 输入；失败时 dump + 抛异常。"""
        self.close_popup_if_exists()
        try:
            el = self.driver.find_element(*locator)
            el.clear()
            el.send_keys(text)
            self.logger.info(f"已输入{name}: {text}")
        except Exception as e:
            self.logger.error(f"未找到'{name}'输入框: {e}")
            self._dump_visible(f"{name}输入框")
            raise

    def _click_retry_n(self, locator, name: str, times: int = 5) -> None:
        """连续点击同一元素 N 次，每次重新查找。失败 dump + 抛异常。"""
        for i in range(times):
            self.close_popup_if_exists()
            try:
                btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                btn.click()
                self.logger.info(f"已点击{name} {i + 1}/{times} 次")
            except Exception as e:
                self.logger.error(
                    f"第 {i + 1}/{times} 次点击{name}失败: {e}，"
                    f"当前 Activity: {self.driver.current_activity}"
                )
                self._dump_visible(f"{name} 第{i + 1}次失败")
                try:
                    self.driver.save_screenshot(f"debug_{name}_{i + 1}.png")
                    self.logger.info(f"已保存截图: debug_{name}_{i + 1}.png")
                except Exception:
                    pass
                raise

    def close_popup_if_exists(self, timeout: int = 3) -> bool:
        """检测并关闭系统级 ANR / 崩溃弹窗。"""
        try:
            close_btn = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(CLOSE_BTN)
            )
            if close_btn.is_displayed():
                close_btn.click()
                sleep(1)
                return True
            return False
        except Exception:
            return False

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 500,
    ) -> None:
        """W3C Actions 滑动优先；失败时 fallback 到 mobile: swipe。"""
        try:
            actions = ActionChains(self.driver)
            pa = actions.w3c_actions.pointer_action
            pa.move_to_location(start_x, start_y)
            pa.pointer_down()
            pa.move_to_location(end_x, end_y)
            pa.pause(duration_ms / 1000)
            pa.pointer_up()
            actions.perform()
        except Exception as e:
            self.logger.warning(f"W3C Actions 滑动失败，改用 mobile: swipe 兜底: {e}")
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

    # ===================== 启动 / 引导 =====================
    def click_agreement_btn(self, dump_on_miss: bool = True) -> bool:
        """启动时隐私协议弹窗的"同意"按钮。

        行为参考旧框架 scripts/test_login.py::click_agreement_btn：
        - 先关 ANR 弹窗；
        - 10s 等元素可点击；
        - 找不到时 dump 可见元素 + 保存截图（仅 dump_on_miss=True 时执行），
          但**不抛异常**（协议弹窗可能不存在）；
        - 返回 True 表示点了一次，False 表示没有协议弹窗。

        参数：
            dump_on_miss: 找不到时是否 dump + 截图。run_pre_login_flow 兜底再点一次
                          时传 False，避免每轮前置流程都写一份 debug_no_agreement.png。
        """
        self._close_anr_dialog_if_exists()
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(AGREEMENT_BTN)
            ).click()
            self.logger.info("已点击同意按钮")
            return True
        except Exception as e:
            self.logger.error(f"未找到同意按钮: {e}")
            if dump_on_miss:
                self._dump_visible("授权同意")
                try:
                    self.driver.save_screenshot("debug_no_agreement.png")
                    self.logger.info("已保存截图: debug_no_agreement.png")
                except Exception:
                    pass
            return False

    def swipe_left_three_times(self) -> None:
        """引导页左滑三次进入主页。

        行为参考旧框架 scripts/test_login.py::swipe_left_three_times：
        启动后先 sleep 3（避免闪退），连续左滑 3 次。
        """
        # App 刚启动完成后立即滑动容易触发闪退，先等待几秒让首页稳定
        sleep(3)
        for idx in range(1, 4):
            self._close_anr_dialog_if_exists()
            self.close_popup_if_exists()
            self.swipe(788, 1024, 49, 1024, duration_ms=500)
            ordinal = ("一", "二", "三")[idx - 1]
            self.logger.info(f"已滑动页面{ordinal}次")

    def click_page(self, times: int = 5) -> None:
        """连续点击 CLICK_BTN N 次（默认 5 次）。

        行为参考旧框架 scripts/test_login.py::click_page：
        - 每次循环都重新查找元素，避免页面跳转后旧元素失效；
        - 若中途元素消失/不可点击，dump 可见元素 + 保存截图便于排查；
        - 任一次失败立即 raise（确保后续用例能感知到）。
        """
        for i in range(times):
            self.close_popup_if_exists()
            try:
                btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(CLICK_BTN)
                )
                btn.click()
                self.logger.info(f"已点击页面 {i + 1}/{times} 次")
            except Exception as e:
                self.logger.error(
                    f"第 {i + 1}/{times} 次点击 CLICK_BTN 失败: {e}, "
                    f"当前 Activity: {self.driver.current_activity}"
                )
                self._dump_visible(f"click_page 第{i+1}次失败")
                try:
                    self.driver.save_screenshot(f"debug_click_page_{i+1}.png")
                    self.logger.info(f"已保存截图: debug_click_page_{i+1}.png")
                except Exception:
                    pass
                raise

    def _close_anr_dialog_if_exists(self, timeout: int = 2) -> bool:
        """检测并关闭 APP 崩溃 / ANR 弹窗（"xxx 已停止运行"）。"""
        try:
            close_btn = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(CLOSE_BTN)
            )
            if close_btn.is_displayed():
                close_btn.click()
                self.logger.info("已关闭 ANR/崩溃弹窗")
                return True
        except Exception:
            return False
        return False

    # ===================== 用例间状态恢复 =====================
    def relaunch_app(self) -> None:
        """强制冷启动 APP（terminate_app + activate_app），用于用例间状态重置。

        与 driver fixture 的 _relaunch_app 区别：
        - 本方法是 LoginOperate 实例方法，可被用例 / fixture 直接调用；
        - 实现相同：先 terminate_app 清进程，再 activate_app 重新拉起。
        """
        try:
            self.driver.terminate_app(APP_PACKAGE)
            self.logger.info(f"[relaunch] 已 terminate_app: {APP_PACKAGE}")
        except Exception as e:
            self.logger.warning(f"[relaunch] terminate_app 失败（可忽略）: {e}")
        try:
            self.driver.activate_app(APP_PACKAGE)
            self.logger.info(f"[relaunch] 已 activate_app: {APP_PACKAGE}")
            sleep(3)
        except Exception as e:
            self.logger.warning(f"[relaunch] activate_app 失败: {e}")

    def is_app_alive(self) -> bool:
        """判断 APP 是否仍在前台运行（包名匹配）。"""
        try:
            return self.driver.current_package == APP_PACKAGE
        except Exception:
            return False

    def run_pre_login_flow(self) -> None:
        """一站式前置流程：点同意 → 左滑 3 次 → 主页入口 5 次 → 兜底再点同意。

        行为参考旧框架 scripts/test_login.py::__main__ 段：
        - 协议弹窗在启动时已点过（由 driver fixture 兜底），本方法再点一次幂等覆盖；
        - 左滑 3 次 + 入口 5 次是"进入主页面 → 进入我的"的标准动作链；
        - 任何步骤失败会沿用 click_page 的 raise，让上游用例知道用例间状态恢复失败。
        """
        self.logger.info("[前置流程] 开始：点同意 → 左滑 3 → 入口 5 → 兜底点同意")
        self.click_agreement_btn(dump_on_miss=True)
        self.swipe_left_three_times()
        self.click_page(times=5)
        # 兜底再点一次同意（部分机型上协议弹窗会重复弹出）；不 dump 避免重复截图
        self.click_agreement_btn(dump_on_miss=False)

    # ===================== 我的 / 未登录 =====================
    def click_my_btn(self) -> None:
        """点击底部 Tab「我的」。"""
        self._click(MY_BTN, "我的按钮")

    def click_loginout_btn(self) -> None:
        """点击「未登录」入口并断言密码登录按钮已出现。"""
        self._click(LOGINOUT_BTN, "未登录按钮")
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.presence_of_element_located(GO_PASSLOGIN_BTN)
            )
            self.logger.info("点击未登录按钮后，密码登录按钮已出现")
        except Exception:
            self.logger.error("点击未登录按钮后，密码登录按钮未出现")
            self._dump_visible("密码登录按钮")

    # ===================== 密码登录 =====================
    def click_go_passlogin_btn(self) -> None:
        """切换到「密码登录」页签。"""
        self._click(GO_PASSLOGIN_BTN, "切换密码登录")

    def input_phone(self, phone: str = DEFAULT_PHONE) -> None:
        """输入手机号。"""
        self._input(IMSPHONE, phone, "手机号")

    def input_password(self, password: str = DEFAULT_PASSWORD) -> None:
        """输入密码。"""
        self._input(IMGCODE, password, "密码")

    # ===================== 图形验证码 =====================
    def _crop_captcha(self) -> Image.Image:
        """按验证码图片元素位置裁剪，返回验证码子图。"""
        el = WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.visibility_of_element_located(CAPTCHA_IMG)
        )
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", el.get_attribute("bounds"))
        if not m:
            raise ValueError(
                f"无法解析验证码元素 bounds: {el.get_attribute('bounds')!r}"
            )
        x1, y1, x2, y2 = map(int, m.groups())
        png_bytes = self.driver.get_screenshot_as_png()
        return Image.open(BytesIO(png_bytes)).crop((x1, y1, x2, y2))

    def _refresh_captcha(self) -> None:
        """点击验证码图片，触发后端重新生成。"""
        try:
            self.driver.find_element(*CAPTCHA_IMG).click()
            self.logger.info("[验证码] 已点击刷新")
        except Exception as e:
            self.logger.warning(f"[验证码] 刷新失败: {e}")

    def _ocr_captcha(self, max_retry: int = 3, expected_len: int = 4) -> str:
        """截图 + OCR 识别验证码；长度不对则刷新重试。"""
        for attempt in range(1, max_retry + 1):
            try:
                captcha_img = self._crop_captcha()
            except Exception as e:
                self.logger.error(f"[验证码] 截图失败: {e}")
                self._refresh_captcha()
                sleep(1)
                continue

            buf = BytesIO()
            captcha_img.save(buf, format="PNG")
            text = self.ocr.classification(buf.getvalue()).strip()
            digits = re.sub(r"\D", "", text)
            self.logger.info(
                f"[验证码] 第 {attempt} 次识别结果: raw='{text}', digits='{digits}'"
            )

            if len(digits) == expected_len:
                return digits

            self.logger.warning(f"[验证码] 长度不等于 {expected_len}，刷新重试")
            self._refresh_captcha()
            sleep(1)

        raise RuntimeError(f"验证码识别失败，已重试 {max_retry} 次")

    def input_captcha(self, expected_len: int = 4, max_retry: int = 3) -> str:
        """自动识别图形验证码并填入输入框，返回识别结果字符串。"""
        self.close_popup_if_exists()
        code = self._ocr_captcha(max_retry=max_retry, expected_len=expected_len)
        self._input(PHONECODE, code, "图形验证码")
        self.logger.info(f"已自动输入图形验证码: {code}")
        return code

    # ===================== 登录提交 =====================
    def click_agreement(self) -> None:
        """登录页底部「同意协议」复选框。"""
        self._click(AGREEMENT, "同意协议")

    def click_login_btn(self) -> None:
        """点击登录按钮；登录成功标志：昵称元素 (LOGINING_BTN) 可见。"""
        self._click(LOGIN_BTN, "登录按钮")
        # 登录成功标志：昵称元素可见
        self.driver.find_element(*LOGINING_BTN)
        self.logger.info("登录成功，昵称已可见")

    # ===================== 一站式登录入口 =====================
    def login(
        self,
        phone: str = DEFAULT_PHONE,
        password: str = DEFAULT_PASSWORD,
    ) -> None:
        """一站式登录：进入「我的」→「未登录」→ 切密码登录 → 填表 → 勾协议 → 提交。

        适用于独立运行的登录用例；与前置引导页流程解耦。
        注意：登录成功后切到「发现 → 推荐」二级 Tab 的步骤，
        已迁移至 first_page_operate.FirstPageOperate，
        本方法只负责登录提交，调用方按需组合。
        """
        self.click_my_btn()
        self.click_loginout_btn()
        self.click_go_passlogin_btn()
        self.input_phone(phone)
        self.input_password(password)
        self.input_captcha()
        self.click_agreement()
        self.click_login_btn()

    def logout(self) -> None:
        """退出登录（如有"我的 → 设置 → 退出登录"入口，可在此扩展）。

        本方法保留为扩展点：当前版本不强制实现，仅在需要时填充。
        """
        self.logger.info("[logout] 当前未实现具体退出操作，保留扩展点")
