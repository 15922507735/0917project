"""业务流程测试用例（business_flow）的**聚合入口**。

历史：
- 早期所有用例都集中在本文件（约 944 行 / 35 个用例），
  维护成本随模块增多而显著上升；
- 现已按业务模块拆分为 8 个文件，位于 ``testcase_manage/modules/`` 目录。

  文件命名规则：``test_<用例起始号>_<业务名>.py``，确保 pytest 按用例编号顺序
  收集（跨平台稳定），具体映射：

    模块                     文件                              用例编号
    ------------------------------------------------------------
    登录 / 我的前置          modules/test_01_login.py         1, 2, 3
    订单 / WebView           modules/test_05_order.py         5
    看车 / 社区 / 话题        modules/test_06_seecar_shequ.py  6, 7, 8, 9, 10
    活动                    modules/test_11_huodong.py       11
    发帖                    modules/test_12_fatie.py         12, 13, 14
    服务（强状态链）         modules/test_15_fuwu.py          15, 16, 17, 18, 19, 20
    我的（强状态链）         modules/test_21_mine.py          21 ~ 33
    购车（最后执行）         modules/test_34_buycar.py        34, 35

- 本文件仅作为 **pytest 默认收集入口** —— 通过 ``import`` 各模块让
  ``pytest --collect-only`` 仍能看到 35 个用例，外部调用方式（cli.py
  / ``python cli.py smoke|regression|business`` / Jenkinsfile）保持不变。

业务策略概要（与原版完全一致）：

- 用例 1/2/3 业务前提是「未登录」，已登录态 pytest.skip；
- 用例 5 业务前提是「已登录」，未登录态 pytest.skip；
- 用例 6/7/8/10 **不依赖登录态**（未登录也跑，已登录也跑）；
- 全部用例在开始前自动调用 ``ensure_ready()`` 重置 APP 状态；
- 用例 15-20（服务）/21-33（我的）形成强状态链：第 N 个用例直接复用
  上一用例的最终状态（用 ``fuwu_op_keep`` / ``my_op`` fixture 跳过 ensure_ready）；
- 用例 34-35（购车）置于文件末尾：上一用例跑完停在「我的」页面，
  用 ``buycar_op_keep`` fixture 主动重置，避免用例 33 跑完后的状态干扰。

运行方式（与原版完全一致）：

    python cli.py            # 全部用例
    python cli.py smoke      # 仅冒烟（用例 1 + 3）
    python cli.py regression # 仅回归（用例 2 / 3 + 5 + 6 + 7 + 8）
    python cli.py business   # 仅业务用例
"""
from __future__ import annotations

# 仅做模块 re-export，让 pytest 收集到 35 个用例。
# 任何业务逻辑/共享 helper 请放到对应的 modules/test_*.py 中。
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
