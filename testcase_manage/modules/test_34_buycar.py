"""购车（用例 34-35，置于最后执行）。

- test_click_store_buy（用例 34）：购车完整配置 + 订购流程
- test_click_ruten_btn（用例 35）：支付定金返回

模块说明：上一用例（用例 33）跑完停在「我的」页面，用 _build_buycar_op_keep 主动重置，
避免用例 33 跑完后的状态干扰。
"""
from __future__ import annotations

import pytest

from object_operation.first_page_operate import FirstPageOperate
from object_operation.login_operate import LoginOperate

from utils.test_helpers import (
    build_ops as _build_ops,
    build_buycar_op_keep as _build_buycar_op_keep,
)


# ===================== 用例 34：购车模块操作 =====================
@pytest.mark.regression
def test_click_store_buy(driver, logger):
    """用例34：购车模块操作。

    注意：本用例不复用 _ensure_ready。上一用例（用例33）跑完停在「我的」页面，
    此时 _ensure_ready 会因为"推荐 Tab 不可见"误判为未在发现页，触发冷启动失败。
    使用 _build_buycar_op_keep 跳过 ensure_ready 直接复用当前页面状态，
    由本用例开头手动切回「发现」首页。
    """
    # 1) 切回「发现」Tab（用例 33 跑完停在「我的」页面）
    login_op, first_page_op = _build_ops(driver, logger)
    first_page_op.click_discover_tab()

    # 2) 构造购车操作实例（不带 ensure_ready）
    buycar_op = _build_buycar_op_keep(driver, logger)
    buycar_op.click_store_buy_btn()
    logger.info("[用例34] 点击购车tab按钮-完成")
    buycar_op.click_store_order_btn()
    logger.info("[用例34] 点击立即订购按钮-完成")
    buycar_op.click_store_config_version_btn()
    logger.info("[用例34] 点击去选择车型版本-完成")
    buycar_op.click_store_config_next_btn()
    logger.info("[用例34] 点击外观 -> 下一步-完成")
    buycar_op.click_store_config_ext_color_btn()
    logger.info("[用例34] 点击外观颜色卡片-完成")
    buycar_op.click_store_config_interior_next_btn()
    logger.info("[用例34] 点击内饰按钮到下一步-完成")
    buycar_op.click_store_config_interior_color_btn()
    logger.info("[用例34] 点击内饰颜色卡片-完成")
    buycar_op.click_store_config_ext_next_btn()
    logger.info("[用例34] 点击选装按钮到下一步-完成")
    buycar_op.click_store_config_think_btn()
    logger.info("[用例34] 点击添加选装按钮-完成")
    buycar_op.click_store_config_order_next_btn()
    logger.info("[用例34] 点击订单中心下一步按钮-完成")
    buycar_op.click_store_config_order_check_btn()
    logger.info("[用例34] 点击订单中心勾选按钮-完成")
    buycar_op.click_store_config_complete_btn()
    logger.info("[用例34] 点击完成配置按钮-完成")
    buycar_op.click_store_config_order_btn()
    logger.info("[用例34] 点击去订购按钮-完成")
    buycar_op.click_store_config_name()
    logger.info("[用例34] 点击车主姓名输入框-完成")
    buycar_op.click_store_config_idcard()
    logger.info("[用例34] 点击证件号码输入框-完成")
    buycar_op.click_store_config_protocol_check_btn()
    logger.info("[用例34] 点击订购协议勾选框-完成")
    buycar_op.click_store_config_submit_btn()
    logger.info("[用例34] 点击提交订单按钮-完成")


# ===================== 用例 35：支付定金返回 =====================
@pytest.mark.regression
def test_click_ruten_btn(driver, logger):
    """用例35：点击支付定金返回按钮。"""
    buycar_op = _build_buycar_op_keep(driver, logger)
    buycar_op.click_store_config_pay_btn()
    logger.info("[用例35] 点击支付定金返回按钮-完成")
