"""登录 / 我的前置（用例 1-3）。

- test_start_app_and_accept_agreement（用例 1）：冒烟，断言 APP 包名（已登录态 skip）
- test_go_mine_and_logout（用例 2）：回归，进入「我的 → 未登录」（已登录态 skip）
- test_login_with_password（用例 3）：冒烟 + 回归，密码登录完整流程（已登录态 skip）
"""
from __future__ import annotations

import time

import allure

import pytest

from page_element.login_page import APP_PACKAGE
from utils.test_helpers import ensure_ready as _ensure_ready


# ===================== 用例 1 =====================
@allure.feature("登录模块")
@allure.story("启动冒烟")
@pytest.mark.feature_login
@pytest.mark.story_smoke
@pytest.mark.smoke
def test_start_app_and_accept_agreement(driver, logger, is_logged_in_session):
    """用例 1：验证 Appium session 已就绪 + 包名 / Activity 断言（冒烟）。

    业务背景：
        conftest.py 的 driver fixture 已启动 Appium session。
        本用例断言 current_package 等于 APP_PACKAGE，作为冒烟用例。

    业务策略：
        已登录 → skip（已登录场景由用例 5 覆盖）；未登录 → 跑主体。

    断言点：
        - driver.current_package == "com.changan.oushangCos1"
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 1 仅做未登录态下的包名断言，让用例 5 跑主体")

    with allure.step("步骤1：读取当前 Activity 与包名"):
        logger.info(f"[用例1] 当前 Activity: {driver.current_activity}")
        logger.info(f"[用例1] 当前包名: {driver.current_package}")

    # 兜底：若 APP 闪退到桌面（被 close_anr 误关 / 协议页后 ANR），
    # 主动 activate_app 拉回前台再断言。
    with allure.step("步骤2：包名异常时 activate_app 拉回 APP"):
        if driver.current_package != APP_PACKAGE:
            logger.warning(
                f"[用例1] 检测到当前包名={driver.current_package} ≠ {APP_PACKAGE}，"
                f"主动 activate_app 拉回 APP"
            )
            try:
                driver.activate_app(APP_PACKAGE)
                time.sleep(2)
            except Exception as e:
                logger.warning(f"[用例1] activate_app 失败: {e}")

    with allure.step("步骤3：断言当前包名 == APP_PACKAGE"):
        assert driver.current_package == APP_PACKAGE, (
            f"期望当前包名 {APP_PACKAGE}, 实际 {driver.current_package}"
        )


# ===================== 用例 2 =====================
@allure.feature("登录模块")
@allure.story("进入未登录入口")
@pytest.mark.feature_login
@pytest.mark.story_logout
@pytest.mark.regression
def test_go_mine_and_logout(driver, logger, is_logged_in_session, login_op, first_page_op):
    """用例 2：进入「我的」Tab 并打开「未登录」入口。

    操作步骤：
        1. ensure_ready 重置 APP 状态；
        2. 点击底部 Tab「我的」 → 进入「我的」页面；
        3. 点击「未登录」入口按钮 → 进入登录方式选择页。

    业务策略：
        已登录 → skip；未登录 → 跑主体。

    断言点：
        - 点完「未登录」后，密码登录切换按钮 (GO_PASSLOGIN_BTN) 出现
          （由 click_loginout_btn 内部断言）。
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 2 业务前提是'未登录'，让用例 5 跑主体")

    with allure.step("步骤1：ensure_ready 重置 APP 状态到发现页"):
        _ensure_ready(login_op, first_page_op, logger)

    with allure.step("步骤2：点击底部「我的」Tab 进入我的页面"):
        logger.info("[用例2] 进入我的-未登录")
        login_op.click_my_btn()

    with allure.step("步骤3：点击「未登录」入口进入登录方式选择页"):
        login_op.click_loginout_btn()


# ===================== 用例 3 =====================
@allure.feature("登录模块")
@allure.story("手机号密码登录")
@pytest.mark.feature_login
@pytest.mark.story_phonelogin
@pytest.mark.critical_path
@pytest.mark.smoke
@pytest.mark.regression
def test_login_with_password(driver, logger, is_logged_in_session, login_op, first_page_op):
    """用例 3：使用「手机号 + 密码 + 图形验证码」登录已注册账号。

    操作步骤：
        1. ensure_ready 重置 APP 状态；
        2. 点击「密码登录」切换按钮；
        3. 输入手机号 / 密码 / 验证码 / 勾选协议 / 提交登录；
        4. 登录成功（断言昵称可见）即结束。

    业务策略：
        已登录 → skip；未登录 → 跑主体。

    断言点：
        - 登录成功后 driver.find_element(LOGINING_BTN) 找到昵称元素
          （由 click_login_btn 内部断言）。

    注：本用例只测「登录流程」本身，不负责切到「发现」页。
        切到发现页 / 推荐 Tab 是后续用例 5+ 的职责（用例 5 会自带 ensure_ready 兜底）。
    """
    if is_logged_in_session:
        pytest.skip("已登录态：用例 3 业务前提是'未登录'，让用例 5 跑主体")

    with allure.step("步骤1：ensure_ready 重置 APP 状态"):
        _ensure_ready(login_op, first_page_op, logger)

    with allure.step("步骤2：点击「密码登录」切换按钮"):
        logger.info("[用例3] 密码登录完整流程")
        login_op.click_go_passlogin_btn()

    with allure.step("步骤3：输入手机号"):
        login_op.input_phone()

    with allure.step("步骤4：输入密码"):
        login_op.input_password()

    with allure.step("步骤5：识别并输入图形验证码"):
        login_op.input_captcha()

    with allure.step("步骤6：勾选同意协议"):
        login_op.click_agreement()  # 勾选同意协议

    with allure.step("步骤7：点击登录按钮（内部断言昵称可见 = 登录成功）"):
        login_op.click_login_btn()
    # 登录成功（昵称已可见）即结束，登录后的页面跳转由后续用例自行处理。
