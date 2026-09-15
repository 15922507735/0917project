import logging
import re
import subprocess
import time
from io import BytesIO
from time import sleep
import pytest
import ddddocr
from PIL import Image
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("summitbuy")

APP_PACKAGE = "com.changan.oushangCos1"
APP_ACTIVITY = ".DefaultAliasActivity"
APP_WAIT_ACTIVITY = (
    f"{APP_PACKAGE}/.DefaultAliasActivity,"
    "com.changan.qiyuan.SplashActivity,"
    "com.changan.qiyuan.activity.QYMainActivity,"
    "com.changan.qiyuan.activity.QYLeadingActivity,"
    "com.changan.qiyuan.my.activity.QYLoginActivty"
)
DEVICE_NAME = "emulator-5554"
APPIUM_SERVER = "http://127.0.0.1:4723"

# ============= 元素定位 ==============
# 点击同意按钮（隐私协议弹窗）
AGREEMENT_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/submit")          # 授权弹窗同意按钮（"同意"文字）
CLOSE_BTN = (AppiumBy.ID, "android:id/aerr_close")            # 关闭应用弹窗按钮
CLICK_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/img")         # 点击页面
MY_BTN = (By.XPATH, "//*[@text='我的']")                       # 我的按钮
LOGINOUT_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvloginout")      # 未登录按钮
GO_PASSLOGIN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tv_gopasslogin")  # 切换密码登录
IMSPHONE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpasswordphone")          # 手机号输入框
IMGCODE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpassword")         # 密码输入框
PHONECODE = (AppiumBy.ID, f"{APP_PACKAGE}:id/etpassimgcode")        # 验证码输入框
CAPTCHA_IMG = (AppiumBy.ID, f"{APP_PACKAGE}:id/ivpassimgcode")     # 验证码图片（点击可刷新）
AGREEMENT = (AppiumBy.ID, f"{APP_PACKAGE}:id/cb_agreement")             # 同意协议
LOGIN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tv_login")
SIGN_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvsign")     # 签到按钮
LOGINING_BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/tvlogining")           # 昵称


# 等待时间
EXPECT_WAIT_TIMEOUT = 10

# 进入到指定设备
options = UiAutomator2Options()
options.platform_name = "android"
options.platform_version = "9"
options.device_name = DEVICE_NAME
options.udid = DEVICE_NAME
options.automation_name = "UiAutomator2"
options.unicode_keyboard = True  # 支持中文输入
# 显式指定 app 包与启动 activity，让 Appium 自动拉起 App
options.app_package = APP_PACKAGE
options.app_activity = APP_ACTIVITY
# 显式指定 app 启动过程中可能出现的多个 Activity，避免 Appium 等待错误的 SplashActivity
options.app_wait_activity = APP_WAIT_ACTIVITY

driver = None  # 占位，__main__ 里再创建 Appium session

# 工具函数：dump 可见文本（在 driver 不可用时也能调用，不报错）
def _dump_visible_texts_safe(driver, tag: str):
    try:
        visible_texts = driver.find_elements(By.XPATH, "//*[@text!='' or @resource-id!='']")
        log.info(f"[{tag}] 当前页面可见元素：")
        for el in visible_texts:
            log.info(f"  - text='{el.text}', id='{el.get_attribute('resource-id')}', class='{el.get_attribute('class')}'")
    except Exception as e:
        log.warning(f"[{tag}] dump 可见元素失败: {e}")


def _init_appium_driver_and_accept_agreement():
    """启动 Appium session，等待应用启动后点击"授权弹窗"同意按钮。
    放在函数里，避免 pytest 收集阶段 import 模块时执行顶层 UI 逻辑。
    """
    global driver
    log.info("等待应用启动...")
    d = webdriver.Remote(APPIUM_SERVER, options=options)
    d.implicitly_wait(EXPECT_WAIT_TIMEOUT)
    sleep(5)
    log.info(f"当前 Activity: {d.current_activity}")
    log.info(f"当前包名: {d.current_package}")
    try:
        WebDriverWait(d, 10).until(
            EC.element_to_be_clickable(AGREEMENT_BTN)
        ).click()
        log.info("已点击同意按钮")
    except Exception as e:
        log.error(f"未找到同意按钮: {e}")
        _dump_visible_texts_safe(d, "授权同意")
        try:
            d.save_screenshot("debug_no_agreement.png")
            log.info("已保存截图: debug_no_agreement.png")
        except Exception:
            pass
        raise
    driver = d

# 关闭应用弹窗（通用函数，在任何页面都可调用）
def close_popup_if_exists(timeout: int = 3) -> bool:
    """
    检查当前页面是否出现 CLOSE_BTN（应用错误/弹窗），若出现则关闭。
    :return: True=关闭了弹窗，False=未出现弹窗
    """
    try:
        close_btn = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(CLOSE_BTN)
        )
        if close_btn.is_displayed():
            close_btn.click()
            sleep(1)
            return True
        return False
    except Exception:
        return False

class Login_Process:
    """登录流程封装类。

    负责：
    1. 首次启动时弹出"隐私协议" → 点击同意；
    2. 引导页左滑三次 → 进入主页；
    3. "我的" → "未登录" → "密码登录"，输入手机号 + 密码。
    """

    def __init__(self, driver, expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT):
        # === 依赖注入：构造时不立即查询元素，只持有 driver 和超时时间 ===
        self.driver = driver
        self.expect_wait_timeout = expect_wait_timeout
        # OCR 引擎：用于识别图形验证码
        # beta=True 启用更强的字符识别模型；show_ad=False 不弹窗
        self.ocr = ddddocr.DdddOcr(beta=True, show_ad=False)

    # ---------------- 通用工具 ----------------
    def close_popup_if_exists(self, timeout: int = 3) -> bool:
        """检查当前页面是否出现 CLOSE_BTN（应用错误/弹窗），若出现则关闭。
        :return: True=关闭了弹窗，False=未出现弹窗
        """
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

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 500):
        """通过 W3C Actions 实现屏幕滑动；失败时 fallback 到 Appium 内置 swipe。"""
        try:
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
            actions.w3c_actions.pointer_action.pause(duration_ms / 1000)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
        except Exception as e:
            # W3C Actions 在某些 emulator 连续滑动时可能 InvalidElementState，兜底走 Appium swipe
            log.warning(f"W3C Actions 滑动失败，改用 driver.swipe 兜底: {e}")
            self.driver.swipe(start_x, start_y, end_x, end_y, duration_ms)

    def _close_anr_dialog_if_exists(self, timeout: int = 2) -> bool:
        """检测并关闭 App 崩溃/ANR 弹窗（"xxx 已停止运行"）。"""
        try:
            close_btn = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(CLOSE_BTN)  # 复用 aerr_close
            )
            if close_btn.is_displayed():
                close_btn.click()
                log.info("已关闭 ANR/崩溃弹窗")
                return True
        except Exception:
            return False
        return False

    def _dump_visible_texts(self, label: str):
        """打印当前页面所有可见元素（text + id + class），便于排查 id 不存在的问题。"""
        log.info(f"[{label}] 当前页面可见元素：")
        for el in self.driver.find_elements(By.XPATH, "//*[@text!='' or @resource-id!='']"):
            log.info(
                f"  - text='{el.text}', "
                f"id='{el.get_attribute('resource-id')}', "
                f"class='{el.get_attribute('class')}'"
            )

    # ---------------- 业务步骤 ----------------
    def click_agreement_btn(self):
        """授权弹窗中的"同意"按钮。"""
        # 兜底：先关掉可能遮住协议弹窗的 ANR 弹窗
        self._close_anr_dialog_if_exists()
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.element_to_be_clickable(AGREEMENT_BTN)
            ).click()
            log.info("已点击同意按钮")
        except Exception as e:
            log.error(f"未找到同意按钮: {e}")
            self._dump_visible_texts("授权同意")
            self.driver.save_screenshot("debug_no_agreement.png")
            log.info("已保存截图: debug_no_agreement.png")

    def swipe_left_three_times(self):
        """引导页左滑三次，进入主页。"""
        # App 刚启动完成后立即滑动容易触发闪退，先等待几秒让首页稳定
        sleep(3)
        for idx in range(1, 4):
            self._close_anr_dialog_if_exists()
            self.close_popup_if_exists()
            self.swipe(788, 1024, 49, 1024, duration_ms=500)
            log.info(f"已滑动页面{['一', '二', '三'][idx-1]}次")

    def click_page(self, times: int = 5):
        """连续点击 CLICK_BTN N 次（默认 5 次）。
        每次循环都重新查找元素，避免页面跳转后旧元素失效。
        若中途元素消失/不可点击，dump 可见元素 + 保存截图便于排查。
        """
        for i in range(times):
            self.close_popup_if_exists()
            try:
                btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(CLICK_BTN)
                )
                btn.click()
                log.info(f"已点击页面 {i + 1}/{times} 次")
            except Exception as e:
                log.error(
                    f"第 {i + 1}/{times} 次点击 CLICK_BTN 失败: {e}，"
                    f"当前 Activity: {self.driver.current_activity}"
                )
                self._dump_visible_texts(f"click_page 第{i+1}次失败")
                try:
                    self.driver.save_screenshot(f"debug_click_page_{i+1}.png")
                    log.info(f"已保存截图: debug_click_page_{i+1}.png")
                except Exception:
                    pass
                raise

    def click_my_btn(self):
        """点击底部 Tab 的"我的"按钮。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*MY_BTN).click()
            log.info("已点击我的按钮")
        except Exception as e:
            log.error(f"未找到'我的'按钮: {e}")
            self._dump_visible_texts("我的按钮")
            raise

    def click_loginout_btn(self):
        """点击"未登录"入口按钮，并断言已切到密码登录页（出现 GO_PASSLOGIN_BTN）。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*LOGINOUT_BTN).click()
            log.info("已点击未登录按钮")
        except Exception as e:
            log.error(f"未找到'未登录'按钮: {e}")
            self._dump_visible_texts("未登录按钮")
            raise

        # 判断密码登录按钮元素是否出现，作为页面是否成功跳转的断言
        try:
            WebDriverWait(self.driver, self.expect_wait_timeout).until(
                EC.presence_of_element_located(GO_PASSLOGIN_BTN)
            )
            log.info("点击未登录按钮后，密码登录按钮已出现")
        except Exception:
            log.error("点击未登录按钮后，密码登录按钮未出现")
            self._dump_visible_texts("密码登录按钮")

    def click_go_passlogin_btn(self):
        """点击"密码登录"切换按钮。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*GO_PASSLOGIN_BTN).click()
            log.info("已点击切换密码登录")
        except Exception as e:
            log.error(f"未找到'切换密码登录'按钮: {e}")
            self._dump_visible_texts("切换密码登录")
            raise

    def click_input_phone_btn(self, phone: str = "18908323900"):
        """在手机号输入框输入手机号。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*IMSPHONE).send_keys(phone)
            log.info("已点击输入手机号")
        except Exception as e:
            log.error(f"未找到'手机号'输入框: {e}")
            self._dump_visible_texts("手机号输入框")
            raise

    def click_input_password_btn(self, password: str = "Aa123456"):
        """在密码输入框输入密码。"""
        self.close_popup_if_exists()
        try:
            self.driver.find_element(*IMGCODE).send_keys(password)
            log.info("已点击输入密码")
        except Exception as e:
            log.error(f"未找到'密码'输入框: {e}")
            self._dump_visible_texts("密码输入框")
            raise

    # ---------------- 图形验证码自动识别 ----------------
    def _crop_captcha_from_screenshot(self) -> Image.Image:
        """截全屏并按验证码元素的 bounds 裁剪出小图，返回 PIL Image。"""
        # 1. 等验证码图片元素可显示
        captcha_el = WebDriverWait(self.driver, self.expect_wait_timeout).until(
            EC.visibility_of_element_located(CAPTCHA_IMG)
        )
        # 2. 读 bounds，格式："[x1,y1][x2,y2]"
        bounds_str = captcha_el.get_attribute("bounds")
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds_str)
        if not m:
            raise ValueError(f"无法解析验证码元素 bounds: {bounds_str!r}")
        x1, y1, x2, y2 = map(int, m.groups())

        # 3. 截全屏（PNG 字节流），用 PIL 打开
        png_bytes = self.driver.get_screenshot_as_png()
        full_img = Image.open(BytesIO(png_bytes))
        # 4. 裁剪出验证码区域
        captcha_img = full_img.crop((x1, y1, x2, y2))
        return captcha_img

    def _ocr_captcha(self, max_retry: int = 3, expected_len: int = 4) -> str:
        """截图 + OCR 识别验证码；识别失败则点图片刷新重试。

        :param max_retry: 最大重试次数
        :param expected_len: 期望验证码长度（你的 App 是 4 位数字）
        :return: 识别到的验证码字符串
        """
        for attempt in range(1, max_retry + 1):
            try:
                captcha_img = self._crop_captcha_from_screenshot()
            except Exception as e:
                log.error(f"[验证码] 截图失败: {e}")
                # 截图失败时，点一下验证码图片触发刷新，再重试
                self._refresh_captcha()
                sleep(1)
                continue

            # 把 PIL Image 转成 ddddocr 需要的 bytes
            buf = BytesIO()
            captcha_img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            # OCR 识别
            text = self.ocr.classification(img_bytes).strip()
            # 只保留数字（你的验证码是纯数字）
            digits = re.sub(r"\D", "", text)
            log.info(f"[验证码] 第 {attempt} 次识别结果: raw='{text}', digits='{digits}'")

            if len(digits) == expected_len:
                return digits

            # 长度不对，点图刷新后重试
            log.warning(f"[验证码] 长度不等于 {expected_len}，刷新重试")
            self._refresh_captcha()
            sleep(1)

        raise RuntimeError(f"验证码识别失败，已重试 {max_retry} 次")

    def _refresh_captcha(self):
        """点击验证码图片，触发后端重新生成一张。"""
        try:
            self.driver.find_element(*CAPTCHA_IMG).click()
            log.info("[验证码] 已点击刷新")
        except Exception as e:
            log.warning(f"[验证码] 刷新失败: {e}")

    def click_input_captcha_btn(self, expected_len: int = 4, max_retry: int = 3):
        """自动识别图形验证码并填入验证码输入框。

        :param expected_len: 期望验证码字符数（默认 4）
        :param max_retry: OCR 识别失败时的最大重试次数
        """
        self.close_popup_if_exists()
        code = self._ocr_captcha(max_retry=max_retry, expected_len=expected_len)
        try:
            # 清空再输入，避免上次识别残留
            input_box = self.driver.find_element(*PHONECODE)
            input_box.clear()
            input_box.send_keys(code)
            log.info(f"已自动输入图形验证码: {code}")
        except Exception as e:
            log.error(f"未找到'图形验证码'输入框: {e}")
            self._dump_visible_texts("图形验证码输入框")
            raise

    # 勾选同意协议按钮
    def click_agreement(self):
        """点击隐私协议弹窗中的"同意"按钮。"""
        self.driver.find_element(*AGREEMENT).click()
        log.info("已点击同意协议")

    # 点击登录按钮
    def click_login_btn(self):
        """点击登录按钮。"""
        self.driver.find_element(*LOGIN_BTN).click()
        log.info("已点击登录按钮")
        # 登录成功，昵称元素LOGINING_BTN可见
        self.driver.find_element(*LOGINING_BTN)
        log.info("登录成功，昵称已可见")

    # 发现-推荐页面
    def click_recommend_btn(self):
        """点击"发现"按钮。"""
        self.driver.find_element(By.XPATH, "(.//android.view.ViewGroup[@resource-id='com.changan.oushangCos1:id/rlt'])[1]").click()
        log.info("已点击发现-按钮")




if __name__ == "__main__":
    # 1. 启动 Appium session 并点击启动时的"授权弹窗"同意按钮
    _init_appium_driver_and_accept_agreement()

    # 2. 创建登录流程实例（仅持有 driver，不做任何 UI 操作）
    login = Login_Process(driver)

    # 3. 授权弹窗（启动脚本顶部已点击过启动时的"授权弹窗"同意按钮）
    #    此处不再重复点击，避免 NoSuchElementException。

    # 4. 引导页：左滑三次
    login.swipe_left_three_times()

    # 5. 进入"我的" → "未登录"
    login.click_page(times=5)
    login.click_my_btn()
    login.click_loginout_btn()

    # 6. 切换到密码登录并输入账号
    login.click_go_passlogin_btn()
    login.click_input_phone_btn()
    login.click_input_password_btn()
    # 7. 自动识别 + 输入图形验证码
    login.click_input_captcha_btn()
    # 8. 勾选同意协议（登录页的复选框）
    login.click_agreement()
    # 9. 点击登录按钮
    login.click_login_btn()
    driver.quit()
    # 11. 以 pytest 风格运行本文件（收集测试用例）
    # pytest.main([__file__, "-v", "-s"])



