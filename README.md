# qiyuan_project

长安起源 APP 自动化测试工程：Appium-Python-client 6.x + Pytest + PO 分层架构。

## 目录结构

```
d:\git_project\demo_qiyuan_bac\
├── cli.py                            # 测试执行入口（pytest 编程调用）
├── pytest.ini                        # testpaths=markers/addopts
├── conftest.py                       # 根：预留全局钩子
├── Jenkinsfile                       # Jenkins Pipeline 定义
├── jenkins_build_robust.bat          # Windows CI 脚本（默认调 python cli.py smoke）
├── requirements.txt
├── logs/                             # 自动生成日志目录
├── utils/                            # 公共工具层
│   ├── debug_helpers.py
│   └── test_helpers.py               # _build_ops / _ensure_ready / *_op_keep 等
├── page_element/                     # PO 元素层（locator 元组）
│   ├── login_page.py                 # 应用常量 + 启动阶段 + 登录表单
│   ├── first_page.py                 # 「发现」/「推荐」Tab
│   ├── order_page.py                 # 聚合页 / 立即订购 / WebView 配置选择
│   ├── seecar_page.py                # 看车 Tab + Q05 车型入口
│   ├── shequ_page.py                 # 社区 Tab + 话题广场
│   ├── huodong_page.py               # 活动 Tab + 活动状态
│   ├── fatie_page.py                 # 发帖入口 + 发文章 WebView
│   ├── fuwu_page.py                  # 服务 Tab + 门店/家充
│   ├── buycar_page.py                # 购车 Tab + 配置选择/订购
│   └── my_page.py                    # 我的 Tab + 皮肤/挂件
├── object_operation/                 # PO 操作层
│   ├── login_operate.py              # 引导页 + 登录
│   ├── first_page_operate.py         # Tab 切换 + 滑动
│   ├── order_operate.py              # 聚合页 + 立即订购（依赖 webview_operate）
│   ├── seecar_operate.py             # 看车 Tab + Q05
│   ├── shequ_operate.py              # 社区 + 话题广场
│   ├── huodong_operate.py             # 活动 Tab + 活动状态
│   ├── fatie_operate.py              # 发帖 + 富文本 + 上传封面/图片
│   ├── fuwu_operate.py               # 服务 + 门店 + 家充
│   ├── buycar_operate.py             # 购车 + 配置 + 订购
│   ├── my_operate.py                 # 我的 + 皮肤/挂件切换
│   └── webview_operate.py            # WebView context + H5 元素操作
└── testcase_manage/
    ├── conftest.py                   # logger / driver / is_logged_in_session fixture
    ├── data/
    │   └── fatie_data.py             # 用例14 数据驱动（标题/内容/期望关键字）
    └── test_business_flow.py         # 全部业务用例（用例 1~24）
```

## 运行方式

```bash
# 全部用例
python cli.py

# 仅冒烟（用例 1 + 3）
python cli.py smoke

# 仅回归（用例 2 + 3 + 5 + 6 + 7 + 8）
python cli.py regression

# 完整 pytest 调用（不走 cli.py）
python -m pytest testcase_manage -v --tb=short
```

## MCP Servers（IDE 工具集）

`mcp_servers/` 目录存放独立运行的 MCP Server，通过 stdio 与 IDE 对接：

- `mcp_mysql.py`：MySQL 操作（connect / list_databases / execute_query / execute_update 等 8 个工具）
- `mcp_file_ops.py`：文件读写 + 目录列表 + 文件搜索
- `mcp_weather.py`：示例天气查询

接入方式：见 `mcp_servers/README.md` 与项目根 `.mcp.json`。

## CI（Jenkins）

- 自由风格任务：Jenkins "Execute Windows batch command" → `call jenkins_build_robust.bat`
- Pipeline 任务：使用本仓库 `Jenkinsfile`

构建脚本默认执行 `python cli.py smoke`（冒烟），并通过环境变量 `PYTEST_ADDOPTS=--alluredir=.\allure-results --clean-alluredir` 注入 Allure 报告目录。

## PO 分层约定

- `page_element/`：**只放 locator 元组**，不写业务逻辑
- `object_operation/`：**只封装操作**（点击 / 输入 / 滑动 / 切换 context），构造方法接 `driver, logger`，不写断言
- `testcase_manage/`：**只做流程串联 + 断言**，每个用例文件只调用 operate，不直接使用定位表达式

## 用例流程索引

所有用例位于 `testcase_manage/test_business_flow.py`，共享 session 级 driver fixture。  
通用前置：每个用例开始前调用 `ensure_ready()` 重置 APP 状态 —— 若已在「发现」首页则跳过全部前置流程（点协议 / 左滑 / 入口 5 次 / 切发现），否则走完整前置。

### 登录 / 我的

#### 用例 1 — `test_start_app_and_accept_agreement`：冒烟

1. 断言 `driver.current_package == APP_PACKAGE`（包名正确即视为冒烟通过）
2. 业务前提 = 未登录；已登录态 `pytest.skip`

#### 用例 2 — `test_go_mine_and_logout`：未登录入口

1. ensure_ready 重置 APP 状态
2. 点击底部「我的」Tab
3. 点击「未登录」入口 → 进入登录方式选择页（断言「密码登录」切换按钮出现）
4. 业务前提 = 未登录；已登录态 `pytest.skip`

#### 用例 3 — `test_login_with_password`：密码登录完整流程

1. ensure_ready 重置 APP 状态
2. 点击「密码登录」切换按钮
3. 依次输入：手机号 / 密码 / 图形验证码
4. 勾选协议 → 提交登录
5. 登录成功后切到「发现 → 推荐」二级 Tab，并上滑一次让列表稳定
6. 业务前提 = 未登录；已登录态 `pytest.skip`

### 订单 / WebView

#### 用例 5 — `test_click_aggregate_btn`：聚合页 + 立即订购

1. ensure_ready 重置 APP 状态
2. 兜底再点一次发现 Tab
3. 点击聚合页入口（内部处理位置授权 + 等待「立即订购」按钮）
4. 点击「立即订购」→ 自动切 WebView + 等待「配置选择」页加载
5. 点击「配置选择」H5 返回按钮 → 切回 NATIVE_APP + 断言聚合页「预约试驾」可见
6. 业务前提 = 已登录；未登录态 `pytest.skip`

#### 用例 22 — `test_click_ruten_btn`：支付定金返回

1. 承接用例 21 的状态（在支付确认页）
3. 点击支付定金返回按钮

### 看车 / 社区 / 话题

以下用例不依赖登录态（登录/未登录都跑）。

#### 用例 6 — `test_click_seecar_btn`：看车 + Q05

1. ensure_ready 重置 APP 状态
2. 点击顶部「看车」Tab
3. 点击 Q05 车型图标

#### 用例 7 — `test_click_shequ_tab`：社区 Tab

1. ensure_ready 重置 APP 状态
2. 点击底部「社区」Tab + 断言「热门话题」元素可见

#### 用例 8 — `test_click_topic_square`：话题广场

1. ensure_ready 重置 APP 状态
2. 切社区 Tab
3. 点击话题广场按钮（WebView）
4. 点击话题列表返回按钮
5. 点击查看更多按钮

#### 用例 9 — `test_click_topic_all_page_btn`：所有圈子地域标签

1. 紧接用例 8 之后运行（已在「所有圈子」WebView 页）
2. 点击地域标签按钮
3. 点击所有圈子返回按钮

#### 用例 10 — `test_click_topic_neirong`：社区内容标签切换

1. ensure_ready 重置 APP 状态
2. 切社区 Tab
3. 依次点击：最新 / 视频 / 关注 / 聊天 四个原生标签
4. 点击聊天列表返回按钮

### 活动

#### 用例 11 — `test_click_huodong_status`：活动状态筛选

1. ensure_ready 重置 APP 状态
2. 点击活动 Tab
3. 选择活动状态按钮
4. 点击确定按钮

### 发帖

#### 用例 12 — `test_click_post_button`：发帖入口 + 发文章

1. ensure_ready 重置 APP 状态 + 强制切回 NATIVE_APP
2. 点击发帖入口按钮
3. 点击「发文章」按钮
4. 切换到发文章 WebView，断言发布按钮元素存在
5. finally 块切回 NATIVE_APP + 按返回键回到主 Activity（收口）

#### 用例 13 — `test_click_fatie`：发帖完整流程（含上传封面/内容图，默认 skip）

1. ensure_ready 重置 APP 状态 + 切回 NATIVE_APP + 兜底按返回键回到主 Activity
2. 点击发帖入口 → 发文章 → 切 WebView
3. 点击上传封面 → 切 NATIVE → 选择图片 → 授权允许 → 勾选图片 → 完成 → 封面图片确认
4. 点击标题输入框 → 输入标题
5. 点击内容输入框 → 输入内容
6. 点击内容图片上传 → 选择图片（弹窗） → 相册勾选 → 已完成 → 确定（弹窗）
7. 点击发布按钮
8. 默认跳过（污染测试数据）；设 `RUN_PUBLISH=1` 启用

#### 用例 14 — `test_fatie_input_draft`：数据驱动：标题 + 富文本内容

1. ensure_ready → 切 NATIVE_APP → 发帖入口 → 发文章 → 切 WebView
2. 参数化输入：标题 + 内容（断言期望关键字）
3. finally 切回 NATIVE_APP + 按返回键回到发现页

### 服务（Fuwu）

用例 15-20 在服务模块内形成强状态链：第 N 个用例直接复用上一用例的最终状态（用 `_build_fuwu_op_keep` 跳过 ensure_ready）。

#### 用例 15 — `test_click_fuwu_tab`：服务 Tab

1. `_build_fuwu_op`（带 ensure_ready）
2. 点击底部「服务」Tab + 断言出现「门店」文本

#### 用例 16 — `test_click_store_btn`：门店跳转

1. `_build_fuwu_op_keep`（跳过 ensure_ready）
2. 点击服务 Tab（兜底） + 点击门店跳转按钮
3. 断言门店详情页加载（出现位置按钮）

#### 用例 17 — `test_click_store_address_btn`：门店详情位置按钮

1. 承接用例 16（仍在门店详情页）
2. 点击门店详情位置按钮
3. 断言弹窗加载（出现「确定」按钮）

#### 用例 18 — `test_click_store_address_btn_submit`：位置弹窗确定

1. 承接用例 17（位置弹窗已开）
2. 点击位置弹窗的「确定」按钮
3. 断言弹窗关闭

#### 用例 19 — `test_click_store_deliver_maint_back`：门店详情 → 交付 → 维保 → 返回服务首页

1. 承接用例 18（位置弹窗已关）
2. 点击门店收起/展开按钮
3. 点击交付中心按钮
4. 点击维护中心按钮
5. 反复 `driver.back()` 直到看到购车文本，回到服务首页

#### 用例 20 — `test_click_store_charge`：服务首页 → 家充服务 → 返回

1. 承接用例 19（已在服务首页）
2. 上滑一次
3. 点击家充服务按钮
4. 点击家充桩智享返回按钮

### 购车（Buycar）

#### 用例 21 — `test_click_store_buy`：购车完整配置 + 订购流程

1. 承接用例 20（在服务 Tab），先切回「发现」Tab
2. 点击购车 Tab → 立即订购 → 去选择车型版本
3. 依次：外观下一步 / 外观颜色卡片 / 内饰下一步 / 内饰颜色卡片 / 选装下一步 / 添加选装
4. 订单中心：下一步 / 勾选 / 完成配置 / 去订购
5. 填写：车主姓名 / 证件号码 / 勾选协议 / 提交订单

#### 用例 22 — `test_click_ruten_btn`：支付定金返回

1. 承接用例 21（在支付确认页）
2. 点击支付定金返回按钮

### 我的（My）

#### 用例 23 — `test_mypage_operate`：我的模块

1. 进入「我的」Tab
2. 等待设置按钮出现，确认页面加载完成

#### 用例 24 — `test_mypage_operate_skin`：皮肤卡片切换使用

1. 点击皮肤按钮，进入皮肤列表页
2. 点击**第一个**皮肤卡片（系统默认）→ 跳转到皮肤详情页
3. 点击「立即使用」→ 显示「正在使用」
4. 系统返回键（`driver.back()`）回到皮肤列表页
5. 点击**第二个**皮肤卡片（长安启源Q06）→ 跳转到皮肤详情页
6. 点击「立即使用」→ 显示「正在使用」（完成皮肤切换）
7. 系统返回键回到皮肤列表页
8. 点击挂件入口按钮，进入挂件 Tab

> 注：一次只能有一个皮肤处于「正在使用」状态，因此切换流程必须包含「使用 → 返回 → 切换下一个」的结构。返回使用 `driver.back()` 系统返回键，避开详情页返回图标（`bar_img_back`）自身 `clickable=false` 导致的点击无效问题。