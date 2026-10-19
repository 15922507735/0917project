"""我的（用例 21-33，强状态链）。

- test_mypage_operate（用例 21）：我的模块入口
- test_mypage_operate_skin（用例 22）：皮肤卡片切换使用
- test_mypage_operate_setting（用例 23）：设置按钮 + 个人资料
- test_mypage_operate_nickname（用例 24）：修改昵称
- test_mypage_operate_setting_back（用例 25）：设置页返回
- test_mypage_operate_sign（用例 26）：签到
- test_mypage_operate_conyb（用例 27）：源宝
- test_mypage_operate_conyb_level（用例 28）：定级积分
- test_mypage_operate_order（用例 29）：我的订单
- test_mypage_operate_shop（用例 30）：车主店铺
- test_mypage_operate_cross_city（用例 31）：同城活动
- test_mypage_operate_card（用例 32）：我的卡券
- test_mypage_operate_online_evaluation（用例 33）：在线评价

模块内强状态链：第 N 个用例直接复用上一用例的最终状态。
"""
from __future__ import annotations

import pytest

from object_operation.my_operate import MyOperate


# ===================== 用例 21 =====================
@pytest.mark.regression
def test_mypage_operate(driver, logger):
    """用例21：我的模块操作。"""
    my_op = MyOperate(driver, logger)
    my_op.click_my_btn()
    logger.info("[用例21] 点击我的按钮-完成")


# ===================== 用例 22 =====================
@pytest.mark.regression
def test_mypage_operate_skin(driver, logger):
    """用例22：我的模块操作-皮肤卡片切换使用。"""
    my_op = MyOperate(driver, logger)
    # 点击皮肤按钮
    my_op.click_skin_btn()
    logger.info("[用例22] 点击皮肤按钮-完成")
    # 点击第一个皮肤卡片（系统默认）并立即使用
    my_op.click_skin_card_first()
    logger.info("[用例22] 点击第一个皮肤卡片并立即使用-完成")
    # 返回皮肤列表页面（系统返回键）
    my_op.click_skin_back_btn()
    logger.info("[用例22] 返回皮肤列表页面-完成")
    # 点击第二个皮肤卡片（长安启源Q06）并立即使用
    my_op.click_skin_card_second()
    logger.info("[用例22] 点击第二个皮肤卡片并立即使用-完成")
    # 返回皮肤列表页面（系统返回键）
    my_op.click_skin_back_btn()
    logger.info("[用例22] 返回皮肤列表页面-完成")
    # 点击挂件入口按钮
    my_op.click_gujian_tab_btn()
    logger.info("[用例22] 点击挂件入口按钮-完成")


# ===================== 用例 23 =====================
@pytest.mark.regression
def test_mypage_operate_setting(driver, logger):
    """用例23：我的模块操作-设置按钮。"""
    my_op = MyOperate(driver, logger)
    # 点击设置按钮
    my_op.click_setting_btn()
    logger.info("[用例23] 点击设置按钮-完成")
    # 点击个人资料
    my_op.click_user_info()
    logger.info("[用例23] 点击个人资料-完成")


# ===================== 用例 24 =====================
@pytest.mark.regression
def test_mypage_operate_nickname(driver, logger):
    """用例24：我的模块操作-昵称。"""
    my_op = MyOperate(driver, logger)
    # 点击昵称
    my_op.click_nickname()
    logger.info("[用例24] 点击昵称-完成")
    # 点击昵称输入框，清除输入框内容，输入新昵称，并保存
    my_op.click_nickname_input()
    logger.info("[用例24] 点击昵称输入框，清除输入框内容，输入新昵称，并保存-完成")


# ===================== 用例 25 =====================
@pytest.mark.regression
def test_mypage_operate_setting_back(driver, logger):
    """用例25：我的模块操作-设置页面返回按钮。"""
    my_op = MyOperate(driver, logger)
    # 点击返回按钮
    my_op.click_setting_back_btn()
    logger.info("[用例25] 点击返回按钮-完成")


# ===================== 用例 26 =====================
@pytest.mark.regression
def test_mypage_operate_sign(driver, logger):
    """用例26：我的模块操作-签到操作。"""
    my_op = MyOperate(driver, logger)
    # 点击签到按钮
    my_op.click_sign_btn()
    logger.info("[用例26] 点击签到操作-完成")


# ===================== 用例 27 =====================
@pytest.mark.regression
def test_mypage_operate_conyb(driver, logger):
    """用例27：我的模块操作-点击查看源宝，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击源宝按钮
    my_op.click_conyb_btn()
    logger.info("[用例27] 点击点击查看源宝-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 28 =====================
@pytest.mark.regression
def test_mypage_operate_conyb_level(driver, logger):
    """用例28：我的模块操作-点击查看定级积分，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击定级积分按钮
    my_op.click_conyb_level_btn()
    logger.info("[用例28] 点击点击查看定级积分-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 29 =====================
@pytest.mark.regression
def test_mypage_operate_order(driver, logger):
    """用例29：我的模块操作-点击查看我的订单，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击我的订单按钮
    my_op.click_order_btn()
    logger.info("[用例29] 点击点击查看我的订单-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 30 =====================
@pytest.mark.regression
def test_mypage_operate_shop(driver, logger):
    """用例30：我的模块操作-点击查看车主店铺，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击车主店铺按钮
    my_op.click_shop_btn()
    logger.info("[用例30] 点击点击查看车主店铺-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 31 =====================
@pytest.mark.regression
def test_mypage_operate_cross_city(driver, logger):
    """用例31：我的模块操作-点击查看同城活动，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击同城活动按钮
    my_op.click_cross_city_activity()
    logger.info("[用例31] 点击点击查看同城活动-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 32 =====================
@pytest.mark.regression
def test_mypage_operate_card(driver, logger):
    """用例32：我的模块操作-点击查看我的卡券，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击我的卡券按钮
    my_op.click_card_btn()
    logger.info("[用例32] 点击点击查看我的卡券-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True


# ===================== 用例 33 =====================
@pytest.mark.regression
def test_mypage_operate_online_evaluation(driver, logger):
    """用例33：我的模块操作-点击查看在线评价，并返回我的页面。"""
    my_op = MyOperate(driver, logger)
    # 点击在线评价按钮
    my_op.click_online_evaluation()
    logger.info("[用例33] 点击点击查看在线评价-完成")
    # 成功返回到我的页面，设置按钮可见
    assert my_op.is_setting_btn_visible() is True
