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

import allure

import pytest


# ===================== 用例 21 =====================
@allure.feature("我的模块")
@allure.story("我的入口")
@pytest.mark.feature_mine
@pytest.mark.story_mineentry
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate(driver, logger, my_op):
    """用例21：我的模块操作。"""
    with allure.step("步骤2：点击底部「我的」Tab（内部断言设置按钮可见 = 页面加载完成）"):
        my_op.click_my_btn()
        logger.info("[用例21] 点击我的按钮-完成")


# ===================== 用例 22 =====================
@allure.feature("我的模块")
@allure.story("皮肤卡片切换")
@pytest.mark.feature_mine
@pytest.mark.story_mineskin
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_skin(driver, logger, my_op):
    """用例22：我的模块操作-皮肤卡片切换使用。"""
    with allure.step("步骤2：点击皮肤按钮（内部断言皮肤列表加载完成）"):
        my_op.click_skin_btn()
        logger.info("[用例22] 点击皮肤按钮-完成")

    with allure.step("步骤3：点击第一个皮肤卡片（系统默认）并立即使用"):
        my_op.click_skin_card_first()
        logger.info("[用例22] 点击第一个皮肤卡片并立即使用-完成")

    with allure.step("步骤4：系统返回键返回皮肤列表页面"):
        my_op.click_skin_back_btn()
        logger.info("[用例22] 返回皮肤列表页面-完成")

    with allure.step("步骤5：点击第二个皮肤卡片（长安启源Q06）并立即使用"):
        my_op.click_skin_card_second()
        logger.info("[用例22] 点击第二个皮肤卡片并立即使用-完成")

    with allure.step("步骤6：系统返回键返回皮肤列表页面"):
        my_op.click_skin_back_btn()
        logger.info("[用例22] 返回皮肤列表页面-完成")

    with allure.step("步骤7：点击挂件入口按钮（内部断言回到我的页）"):
        my_op.click_gujian_tab_btn()
        logger.info("[用例22] 点击挂件入口按钮-完成")


# ===================== 用例 23 =====================
@allure.feature("我的模块")
@allure.story("设置 / 个人资料")
@pytest.mark.feature_mine
@pytest.mark.story_minesetting
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_setting(driver, logger, my_op):
    """用例23：我的模块操作-设置按钮。"""
    with allure.step("步骤2：点击设置按钮（内部断言个人资料可见 = 设置页加载完成）"):
        my_op.click_setting_btn()
        logger.info("[用例23] 点击设置按钮-完成")

    with allure.step("步骤3：点击个人资料（内部断言个性签名可见）"):
        my_op.click_user_info()
        logger.info("[用例23] 点击个人资料-完成")


# ===================== 用例 24 =====================
@allure.feature("我的模块")
@allure.story("修改昵称")
@pytest.mark.feature_mine
@pytest.mark.story_minenickname
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_nickname(driver, logger, my_op):
    """用例24：我的模块操作-昵称。"""
    with allure.step("步骤2：点击昵称（内部断言修改昵称标题出现）"):
        my_op.click_nickname()
        logger.info("[用例24] 点击昵称-完成")

    with allure.step("步骤3：点击昵称输入框 → 清除 → 输入新昵称 → 确定 → 保存"):
        my_op.click_nickname_input()
        logger.info("[用例24] 点击昵称输入框，清除输入框内容，输入新昵称，并保存-完成")


# ===================== 用例 25 =====================
@allure.feature("我的模块")
@allure.story("设置页返回")
@pytest.mark.feature_mine
@pytest.mark.story_minesettingback
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_setting_back(driver, logger, my_op):
    """用例25：我的模块操作-设置页面返回按钮。"""
    with allure.step("步骤2：系统返回键退出设置页（内部断言昵称文本出现 = 回到我的页）"):
        my_op.click_setting_back_btn()
        logger.info("[用例25] 点击返回按钮-完成")


# ===================== 用例 26 =====================
@allure.feature("我的模块")
@allure.story("签到")
@pytest.mark.feature_mine
@pytest.mark.story_minesign
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_sign(driver, logger, my_op):
    """用例26：我的模块操作-签到操作。"""
    with allure.step("步骤2：点击签到按钮（内部容错：今日已签到则跳过弹窗断言）"):
        my_op.click_sign_btn()
        logger.info("[用例26] 点击签到操作-完成")


# ===================== 用例 27 =====================
@allure.feature("我的模块")
@allure.story("源宝")
@pytest.mark.feature_mine
@pytest.mark.story_mineconyb
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_conyb(driver, logger, my_op):
    """用例27：我的模块操作-点击查看源宝，并返回我的页面。"""
    with allure.step("步骤2：点击源宝按钮（内部断言源宝记录出现）"):
        my_op.click_conyb_btn()
        logger.info("[用例27] 点击点击查看源宝-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 28 =====================
@allure.feature("我的模块")
@allure.story("定级积分")
@pytest.mark.feature_mine
@pytest.mark.story_mineconyblevel
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_conyb_level(driver, logger, my_op):
    """用例28：我的模块操作-点击查看定级积分，并返回我的页面。"""
    with allure.step("步骤2：点击定级积分按钮（内部断言定级积分记录出现）"):
        my_op.click_conyb_level_btn()
        logger.info("[用例28] 点击点击查看定级积分-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 29 =====================
@allure.feature("我的模块")
@allure.story("我的订单")
@pytest.mark.feature_mine
@pytest.mark.story_mineorder
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_order(driver, logger, my_op):
    """用例29：我的模块操作-点击查看我的订单，并返回我的页面。"""
    with allure.step("步骤2：点击我的订单按钮（我的订单 → 订车订单 → H5 订单详情 → 逐层返回我的页）"):
        my_op.click_order_btn()
        logger.info("[用例29] 点击点击查看我的订单-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 30 =====================
@allure.feature("我的模块")
@allure.story("车主店铺")
@pytest.mark.feature_mine
@pytest.mark.story_mineshop
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_shop(driver, logger, my_op):
    """用例30：我的模块操作-点击查看车主店铺，并返回我的页面。"""
    with allure.step("步骤2：点击车主店铺按钮（内部切 WebView 并等待页面加载）"):
        my_op.click_shop_btn()
        logger.info("[用例30] 点击点击查看车主店铺-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 31 =====================
@allure.feature("我的模块")
@allure.story("同城活动")
@pytest.mark.feature_mine
@pytest.mark.story_minecrosscity
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_cross_city(driver, logger, my_op):
    """用例31：我的模块操作-点击查看同城活动，并返回我的页面。"""
    with allure.step("步骤2：点击同城活动按钮（内部切 WebView 并等待页面加载）"):
        my_op.click_cross_city_activity()
        logger.info("[用例31] 点击点击查看同城活动-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 32 =====================
@allure.feature("我的模块")
@allure.story("我的卡券")
@pytest.mark.feature_mine
@pytest.mark.story_minecard
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_card(driver, logger, my_op):
    """用例32：我的模块操作-点击查看我的卡券，并返回我的页面。"""
    with allure.step("步骤2：点击我的卡券按钮（内部切 WebView 并等待页面加载）"):
        my_op.click_card_btn()
        logger.info("[用例32] 点击点击查看我的卡券-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True


# ===================== 用例 33 =====================
@allure.feature("我的模块")
@allure.story("在线评价")
@pytest.mark.feature_mine
@pytest.mark.story_mineevaluation
@pytest.mark.requires_login
@pytest.mark.regression
def test_mypage_operate_online_evaluation(driver, logger, my_op):
    """用例33：我的模块操作-点击查看在线评价，并返回我的页面。"""
    with allure.step("步骤2：点击在线评价按钮（内部切 WebView 并等待待评价元素出现）"):
        my_op.click_online_evaluation()
        logger.info("[用例33] 点击点击查看在线评价-完成")

    with allure.step("步骤3：断言已返回我的页面（设置按钮可见）"):
        assert my_op.is_setting_btn_visible() is True
