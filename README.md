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
├── page_element/                     # PO 元素层（locator 元组）
│   ├── __init__.py
│   ├── login_page.py                 # 应用常量 + 启动阶段 + 登录表单
│   ├── first_page.py                 # 「发现」/「推荐」Tab
│   └── order_page.py                 # 聚合页 / 立即订购 / WebView 配置选择
├── object_operation/                 # PO 操作层
│   ├── __init__.py
│   ├── login_operate.py              # 引导页 + 登录
│   ├── first_page_operate.py         # Tab 切换 + 滑动
│   ├── order_operate.py              # 聚合页 + 立即订购（依赖 webview_operate）
│   └── webview_operate.py            # WebView context + H5 元素操作
└── testcase_manage/
    ├── conftest.py                   # logger / driver 两个 fixture
    └── test_login.py                 # 4 个用例（用例 1 / 2 / 3 / 5）
```

## 运行方式

```bash
# 全部用例
python cli.py

# 仅冒烟（用例 1 + 3）
python cli.py smoke

# 仅回归（用例 2 + 3 + 5）
python cli.py regression

# 完整 pytest 调用（不走 cli.py）
python -m pytest testcase_manage -v --tb=short
```

## CI（Jenkins）

- 自由风格任务：Jenkins "Execute Windows batch command" → `call jenkins_build_robust.bat`
- Pipeline 任务：使用本仓库 `Jenkinsfile`

构建脚本默认执行 `python cli.py smoke`（冒烟），并通过环境变量 `PYTEST_ADDOPTS=--alluredir=.\allure-results --clean-alluredir` 注入 Allure 报告目录。

## PO 分层约定

- `page_element/`：**只放 locator 元组**，不写业务逻辑
- `object_operation/`：**只封装操作**（点击 / 输入 / 滑动 / 切换 context），构造方法接 `driver, logger`，不写断言
- `testcase_manage/`：**只做流程串联 + 断言**，每个用例文件只调用 operate，不直接使用定位表达式
