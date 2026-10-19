"""业务流程用例模块集合。

文件命名规则：``test_<用例起始号>_<业务名>.py``，
确保 pytest 按用例编号顺序收集（跨平台稳定）。

用例编号 → 文件映射（与业务策略 / 强状态链完全一致）：

    编号        文件                              模块
    ----------------------------------------------------------
    1, 2, 3     test_01_login.py                  登录 / 我的前置
    5           test_05_order.py                  订单 / WebView
    6, 7, 8, 9, 10
                test_06_seecar_shequ.py           看车 / 社区 / 话题
    11          test_11_huodong.py                活动
    12, 13, 14  test_12_fatie.py                  发帖
    15 ~ 20     test_15_fuwu.py                   服务（强状态链）
    21 ~ 33     test_21_mine.py                   我的（强状态链）
    34, 35      test_34_buycar.py                 购车（最后执行）

``__all__`` 显式声明用于：
- IDE/静态分析时清晰看到用例顺序；
- 外部脚本 ``from testcase_manage.modules import *`` 时按编号顺序导入。
"""
from __future__ import annotations

# 严格按用例编号顺序导入
from testcase_manage.modules import (  # noqa: F401
    test_01_login,        # 用例 1, 2, 3
    test_05_order,        # 用例 5
    test_06_seecar_shequ, # 用例 6, 7, 8, 9, 10
    test_11_huodong,      # 用例 11
    test_12_fatie,        # 用例 12, 13, 14
    test_15_fuwu,         # 用例 15 ~ 20
    test_21_mine,         # 用例 21 ~ 33
    test_34_buycar,       # 用例 34, 35
)

__all__ = [
    "test_01_login",
    "test_05_order",
    "test_06_seecar_shequ",
    "test_11_huodong",
    "test_12_fatie",
    "test_15_fuwu",
    "test_21_mine",
    "test_34_buycar",
]
