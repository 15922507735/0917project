"""活动（用例 11）。

- test_click_huodong_status（用例 11）：活动状态筛选
"""
from __future__ import annotations

import allure

import pytest

from utils.test_helpers import ensure_ready as _ensure_ready


# ===================== 用例 11 =====================
@allure.feature("活动模块")
@allure.story("活动状态筛选")
@pytest.mark.feature_huodong
@pytest.mark.story_huodongstatus
@pytest.mark.regression
def test_click_huodong_status(driver, logger, login_op, first_page_op, huodong_op):
    """用例 11：点击活动状态按钮。"""
    with allure.step("步骤1：ensure_ready 重置 APP 状态到发现页"):
        _ensure_ready(login_op, first_page_op, logger)

    with allure.step("步骤2：点击底部「活动」Tab"):
        huodong_op.click_huodong_tab()
        logger.info("[用例11] 点击活动 Tab 按钮-完成")

    with allure.step("步骤3：点击活动状态筛选按钮"):
        huodong_op.select_huodong_status()
        logger.info("[用例11] 点击活动状态按钮-完成")

    with allure.step("步骤4：点击筛选弹窗「确定」按钮"):
        huodong_op.click_huodong_confirm_btn()
        logger.info("[用例11] 点击确定按钮-完成")
