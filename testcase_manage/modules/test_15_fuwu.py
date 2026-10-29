"""服务（用例 15-20，强状态链）。

- test_click_fuwu_tab（用例 15）：服务 Tab
- test_click_store_btn（用例 16）：门店跳转
- test_click_store_address_btn（用例 17）：门店详情位置按钮
- test_click_store_address_btn_submit（用例 18）：位置弹窗确定
- test_click_store_deliver_maint_back（用例 19）：门店详情 → 交付 → 维保 → 返回
- test_click_store_charge（用例 20）：服务首页 → 家充服务 → 返回

模块内强状态链：用例 N 直接复用上一用例的最终状态（用 fuwu_op_keep fixture 跳过 ensure_ready）。
"""
from __future__ import annotations

import allure

import pytest


# ===================== 用例 15：点击服务 Tab =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("服务 Tab")
@pytest.mark.feature_fuwu
@pytest.mark.story_fuwutab
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_fuwu_tab(driver, logger, fuwu_op):
    """用例15：点击底部"服务"Tab，断言服务页面加载完成（出现"门店"文本）。

    fuwu_op fixture 已内置 ensure_ready，把 APP 拉到发现页。
    """
    with allure.step("步骤1：点击底部「服务」Tab（内部断言「门店」文本可见 = 页面加载完成）"):
        fuwu_op.click_fuwu_tab()
        logger.info("[用例15] 点击服务 Tab-完成")


# ===================== 用例 16：点击门店 =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("门店跳转")
@pytest.mark.feature_fuwu
@pytest.mark.story_storeentry
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_store_btn(driver, logger, fuwu_op_keep):
    """用例16：在服务首页点击门店跳转按钮，断言门店详情页加载（出现位置按钮）。

    注意：本用例不做 ensure_ready。上一用例（用例15）跑完停在服务 Tab，
    此时 ensure_ready 会因为"推荐 Tab 不可见"误判为未在发现页，触发冷启动失败。
    使用 fuwu_op_keep fixture 跳过 ensure_ready 直接复用当前页面状态。
    如果单独跑本用例，APP 不在服务 Tab，click_fuwu_tab 内部的断言会兜底。
    """
    fuwu_op = fuwu_op_keep

    with allure.step("步骤1：点击底部「服务」Tab"):
        fuwu_op.click_fuwu_tab()

    with allure.step("步骤2：点击门店入口跳转（内部断言门店详情页加载完成）"):
        fuwu_op.click_store_btn()
        logger.info("[用例16] 点击门店跳转按钮-完成")


# ===================== 用例 17：点击门店详情位置按钮 =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("门店位置按钮")
@pytest.mark.feature_fuwu
@pytest.mark.story_storeaddress
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_store_address_btn(driver, logger, fuwu_op_keep):
    """用例17：点击门店详情位置按钮，断言弹窗加载（出现"确定"按钮）。

    用例 16 跑完停在门店详情页，本用例直接复用该状态继续往下点位置按钮。
    不要在这里再调 click_store_btn() —— APP 已经离开服务首页，再点找不到。
    """
    fuwu_op = fuwu_op_keep

    with allure.step("步骤1：点击门店详情位置按钮（内部断言弹窗加载，出现「确定」按钮）"):
        fuwu_op.click_store_address_btn()
        logger.info("[用例17] 点击门店详情位置按钮-完成")


# ===================== 用例 18：点击位置弹窗确定按钮 =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("位置弹窗确定")
@pytest.mark.feature_fuwu
@pytest.mark.story_storeaddresssubmit
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_store_address_btn_submit(driver, logger, fuwu_op_keep):
    """用例18：点击位置弹窗的确定按钮，断言弹窗关闭。

    用例 17 跑完位置弹窗已开，本用例直接点弹窗"确定"按钮关闭弹窗。
    """
    fuwu_op = fuwu_op_keep

    with allure.step("步骤1：点击位置弹窗「确定」按钮（内部断言弹窗关闭）"):
        fuwu_op.click_store_address_btn_submit()
        logger.info("[用例18] 点击位置弹窗确定按钮-完成")


# ===================== 用例 19：门店详情→交付→维保→返回服务首页 =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("门店 → 交付 → 维保 → 返回")
@pytest.mark.feature_fuwu
@pytest.mark.story_storedelivermaint
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_store_deliver_maint_back(driver, logger, fuwu_op_keep):
    """用例19：门店详情页 → 收起 → 交付中心 → 维保中心 → 返回到服务首页。

    用例 18 跑完位置弹窗已关，仍在门店详情页，本用例直接复用该状态继续。
    最后一步 click_store_back_btn 会反复 driver.back() 直到看到购车文本，回到服务首页。
    """
    fuwu_op = fuwu_op_keep

    with allure.step("步骤1：点击门店收起展开按钮"):
        fuwu_op.click_store_search_btn()
        logger.info("[用例19] 点击门店收起展开按钮-完成")

    with allure.step("步骤2：点击「交付中心」按钮"):
        fuwu_op.click_store_deliver_btn()
        logger.info("[用例19] 点击交付中心按钮-完成")

    with allure.step("步骤3：点击「维护中心」按钮"):
        fuwu_op.click_store_maint_btn()
        logger.info("[用例19] 点击维护中心按钮-完成")

    with allure.step("步骤4：返回服务首页（内部断言购车文本可见）"):
        fuwu_op.click_store_back_btn()
        logger.info("[用例19] 门店详情返回服务首页-完成")


# ===================== 用例 20：服务首页→滑动→家充服务→返回 =====================
@allure.feature("服务模块（门店、家充）")
@allure.story("家充服务")
@pytest.mark.feature_fuwu
@pytest.mark.story_storecharge
@pytest.mark.requires_login
@pytest.mark.regression
def test_click_store_charge(driver, logger, fuwu_op_keep):
    """用例20：服务首页 → 上滑 → 点家充服务 → 返回。

    用例 19 的 click_store_back_btn 已保证 APP 回到服务首页（含购车文本可见），
    本用例直接接着上滑 → 点家充 → 返回，不再调 click_fuwu_tab。
    """
    fuwu_op = fuwu_op_keep

    with allure.step("步骤1：服务首页上滑，露出家充服务入口"):
        fuwu_op.swipe_up()
        logger.info("[用例20] 滑动成功-完成")

    with allure.step("步骤2：点击「家充服务」按钮"):
        fuwu_op.click_store_charge_btn()
        logger.info("[用例20] 点击家充服务按钮-完成")

    with allure.step("步骤3：点击家充桩智享返回按钮"):
        fuwu_op.click_store_charge_back_btn()
        logger.info("[用例20] 点击家充桩智享返回按钮-完成")
