"""活动（用例 11）。

- test_click_huodong_status（用例 11）：活动状态筛选
"""
from __future__ import annotations

import allure

import pytest

from object_operation.first_page_operate import FirstPageOperate
from object_operation.huodong_operate import HuodongOperate
from object_operation.login_operate import LoginOperate

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from utils.test_helpers import (
    build_ops as _build_ops,
    ensure_ready as _ensure_ready,
)


# ===================== 用例 11 =====================
@allure.feature("活动模块")
@allure.story("活动状态筛选")
@pytest.mark.feature_huodong
@pytest.mark.story_huodongstatus
@pytest.mark.regression
def test_click_huodong_status(driver, logger):
    """用例 11：点击活动状态按钮。"""
    with allure.step("步骤1：ensure_ready 重置 APP 状态到发现页"):
        login_op, first_page_op = _build_ops(driver, logger)
        _ensure_ready(login_op, first_page_op, logger)

    with allure.step("步骤2：构造 HuodongOperate"):
        huodong_op = HuodongOperate(driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)

    with allure.step("步骤3：点击底部「活动」Tab"):
        huodong_op.click_huodong_tab()
        logger.info("[用例11] 点击活动 Tab 按钮-完成")

    with allure.step("步骤4：点击活动状态筛选按钮"):
        huodong_op.select_huodong_status()
        logger.info("[用例11] 点击活动状态按钮-完成")

    with allure.step("步骤5：点击筛选弹窗「确定」按钮"):
        huodong_op.click_huodong_confirm_btn()
        logger.info("[用例11] 点击确定按钮-完成")
