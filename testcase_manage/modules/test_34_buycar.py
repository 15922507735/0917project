"""购车（用例 34-35，置于最后执行）。

- test_click_store_buy（用例 34）：购车模块操作（校验底部 CTA 为"支付订金"或
  "立即订购"后走对应流程；订金=订金往返，订购=完整配置 + 订购）
- test_click_ruten_btn（用例 35）：支付定金返回

模块说明：上一用例（用例 33）跑完停在「我的」页面，用 buycar_op_keep fixture 主动重置，
避免用例 33 跑完后的状态干扰。
"""
from __future__ import annotations

import allure

import pytest


# ===================== 用例 34：购车模块操作 =====================
@allure.feature("购车模块")
@allure.story("购车完整配置 / 订购")
@pytest.mark.feature_buycar
@pytest.mark.story_buyconfig
@pytest.mark.critical_path
@pytest.mark.regression
def test_click_store_buy(driver, logger, first_page_op, buycar_op_keep):
    """用例34：购车模块操作。

    注意：本用例不复用 _ensure_ready。上一用例（用例33）跑完停在「我的」页面，
    此时 _ensure_ready 会因为"推荐 Tab 不可见"误判为未在发现页，触发冷启动失败。
    使用 buycar_op_keep fixture 跳过 ensure_ready 直接复用当前页面状态，
    由本用例开头手动切回「发现」首页。
    """
    with allure.step("步骤1：切回「发现」Tab（用例33跑完停在「我的」页面）"):
        first_page_op.click_discover_tab()

    with allure.step("步骤2：构造购车操作实例（不带 ensure_ready）"):
        buycar_op = buycar_op_keep

    with allure.step("步骤3：点击购车 Tab 并校验底部 CTA（支付订金 / 立即订购）"):
        cta_type = buycar_op.click_store_buy_btn()
        logger.info(f"[用例34] 点击购车tab按钮-完成，CTA={cta_type}")

    if cta_type == "pay_deposit":
        with allure.step("步骤4：点击「支付订金」按钮 → 进支付订金页 → 系统返回"):
            buycar_op.click_store_pay_deposit_btn()
            logger.info("[用例34] 支付订金往返流程-完成")
        return

    with allure.step("步骤4：点击「立即订购」按钮"):
        buycar_op.click_store_order_btn()
        logger.info("[用例34] 点击立即订购按钮-完成")

    with allure.step("步骤5：点击「去选择车型版本」"):
        buycar_op.click_store_config_version_btn()
        logger.info("[用例34] 点击去选择车型版本-完成")

    with allure.step("步骤6：外观 → 下一步 → 选外观颜色 → 下一步"):
        buycar_op.click_store_config_next_btn()
        logger.info("[用例34] 点击外观 -> 下一步-完成")
        buycar_op.click_store_config_ext_color_btn()
        logger.info("[用例34] 点击外观颜色卡片-完成")
        buycar_op.click_store_config_interior_next_btn()
        logger.info("[用例34] 点击内饰按钮到下一步-完成")

    with allure.step("步骤7：点击内饰颜色卡片 → 选装 → 下一步"):
        buycar_op.click_store_config_interior_color_btn()
        logger.info("[用例34] 点击内饰颜色卡片-完成")
        buycar_op.click_store_config_ext_next_btn()
        logger.info("[用例34] 点击选装按钮到下一步-完成")
        buycar_op.click_store_config_think_btn()
        logger.info("[用例34] 点击添加选装按钮-完成")

    with allure.step("步骤8：订单中心 → 下一步 → 勾选 → 完成配置"):
        buycar_op.click_store_config_order_next_btn()
        logger.info("[用例34] 点击订单中心下一步按钮-完成")
        buycar_op.click_store_config_order_check_btn()
        logger.info("[用例34] 点击订单中心勾选按钮-完成")
        buycar_op.click_store_config_complete_btn()
        logger.info("[用例34] 点击完成配置按钮-完成")

    with allure.step("步骤9：点击「去订购」按钮"):
        buycar_op.click_store_config_order_btn()
        logger.info("[用例34] 点击去订购按钮-完成")

    with allure.step("步骤10：填写车主姓名 → 证件号码 → 勾选订购协议"):
        buycar_op.click_store_config_name()
        logger.info("[用例34] 点击车主姓名输入框-完成")
        buycar_op.click_store_config_idcard()
        logger.info("[用例34] 点击证件号码输入框-完成")
        buycar_op.click_store_config_protocol_check_btn()
        logger.info("[用例34] 点击订购协议勾选框-完成")

    with allure.step("步骤11：点击「提交订单」按钮"):
        buycar_op.click_store_config_submit_btn()
        logger.info("[用例34] 点击提交订单按钮-完成")


# ===================== 用例 35：支付定金返回 =====================
@allure.feature("购车模块")
@allure.story("支付定金返回")
@pytest.mark.feature_buycar
@pytest.mark.story_buypay
@pytest.mark.regression
def test_click_ruten_btn(driver, logger, buycar_op_keep):
    """用例35：点击支付定金返回按钮。"""
    with allure.step("步骤1：构造购车操作实例（复用用例34停留的支付页）"):
        buycar_op = buycar_op_keep

    with allure.step("步骤2：点击支付定金页面返回按钮"):
        buycar_op.click_store_config_pay_btn()
        logger.info("[用例35] 点击支付定金返回按钮-完成")
