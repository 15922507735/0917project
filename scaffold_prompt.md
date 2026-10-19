# 长安启源 APP UI 自动化测试脚手架搭建提示词

## 角色
你是一位资深 Android App UI 自动化测试架构师，精通 Page Object Model 分层设计、Appium 2 / UiAutomator2、pytest fixture 体系、WebView 混合上下文切换、ddddocr 图形验证码识别、Jenkins Pipeline CI 集成。请基于下述规范在当前空目录中搭建一个**可运行、可维护、可接入 CI**的 Android App UI 自动化测试脚手架。

## 目标 APP 与运行环境
- 包名：com.changan.oushangCos1（长安启源 APP）
- 启动 Activity：.DefaultAliasActivity
- 测试设备：Android 9 模拟器（DEVICE_NAME=emulator-5554）
- WebView Chrome 内核版本：91.0.4472（chromedriver 必须精确匹配）
- Appium Server：http://127.0.0.1:4723（Appium 2，不再带 /wd/hub）

## 技术栈（requirements.txt）
```
appium-python-client==6.0.6     # Appium 2 新版客户端
selenium==4.49.0                # WebDriverWait / EC / ActionChains
ddddocr==1.6.1                  # 图形验证码 OCR 识别
Pillow==12.3.0                  # 配合 ddddocr 处理验证码图片
pytest>=7.0
allure-pytest>=2.13             # 测试报告
openpyxl                        # Excel 数据读取（可选）
```

## 目录结构（PO 四层 + utils 公共层 + CI 文件）

```
demo_qiyuan_bac/
├── cli.py                          # 命令行入口：python cli.py [smoke|regression|business]
├── pytest.ini                      # testpaths=testcase_manage; markers; addopts=-v --tb=short
├── conftest.py                     # 根 conftest：仅预留全局钩子（pytest_configure / pytest_addoption），不放业务 fixture
├── requirements.txt
├── README.md                       # 工程说明 + 运行方式 + CI 说明
├── .gitignore                      # 排除 .venv/ chromedriver.exe logs/ allure-results/ debug_*
│
├── Jenkinsfile                     # Jenkins Declarative Pipeline：Checkout → Build & Test → Allure Report → 邮件通知
├── jenkins_build_robust.bat        # Windows CI 脚本：UTF-8 代码页 + 前置环境检查 + venv + 依赖 + cli.py
│
├── page_element/                   # 【第一层】定位器层
│   ├── __init__.py                 # __all__ 暴露各 page 模块
│   ├── login_page.py               # ★ APP 级常量（APP_PACKAGE/APP_ACTIVITY/APP_WAIT_ACTIVITY/
│   │                               #   DEVICE_NAME/APPIUM_SERVER/EXPECT_WAIT_TIMEOUT=10）
│   │                               # + 启动阶段元素 + 底部 Tab + 登录入口 + 登录表单
│   ├── first_page.py               # 「发现」入口 + 「推荐」二级 Tab
│   ├── order_page.py               # 聚合页 / 立即订购 / WebView 配置选择
│   ├── seecar_page.py              # 看车 Tab + Q05 车型入口
│   ├── shequ_page.py               # 社区 Tab + 热门话题
│   ├── fuwu_page.py                # 服务 Tab + 家充服务入口
│   ├── buycat_page.py              # 购车入口
│   ├── fatie_page.py               # 发帖页 + 发布按钮
│   └── huodong_page.py             # 活动页
│
├── object_operation/               # 【第二层】操作层（动词短语方法，不做断言）
│   ├── __init__.py
│   ├── login_operate.py           # LoginOperate：构造时初始化 ddddocr.DdddOcr(beta=True, show_ad=False)
│   │                               #   _click 内部模板：close_popup_if_exists → find → click → 失败 dump + raise
│   │                               #   方法：click_my_btn / click_loginout_btn / click_go_passlogin_btn /
│   │                               #   input_phone / input_password / input_captcha（OCR）/ click_agreement /
│   │                               #   click_login_btn / run_pre_login_flow（协议+左滑3+入口5+兜底再同意）
│   ├── first_page_operate.py       # FirstPageOperate：swipe（W3C Actions 优先，mobile: swipe 兜底）/
│   │                               #   is_on_discover_page / click_discover_tab / click_recommend_btn / swipe_up_recommend
│   ├── order_operate.py            # OrderOperate（依赖 WebViewOperate）
│   ├── seecar_operate.py           # SeeCarOperate
│   ├── shequ_operate.py            # ShequOperate
│   ├── fuwu_operate.py             # FuwuOperate（依赖 WebViewOperate）
│   ├── buycar_operate.py           # BuycarOperate
│   ├── fatie_operate.py            # FatieOperate
│   ├── huodong_operate.py          # HuodongOperate
│   └── webview_operate.py          # WebViewOperate：switch_to_webview（精确匹配 WEBVIEW_<package>，否则兜底取首个非 NATIVE_APP）
│                                   #   / switch_to_native（用完必须切回，否则后续 native 操作报 invalid locator）
│                                   #   H5 元素用 By.CSS_SELECTOR / By.XPATH / By.ID（HTML id）
│
├── utils/                          # 【公共层】跨用例 / 跨操作复用工具（无业务状态）
│   ├── __init__.py                 # __all__ = ["debug_helpers", "test_helpers"]
│   ├── debug_helpers.py            # 无状态排障函数，签名固定 (driver, logger, ...)
│   │                               #   dump_visible(driver, logger, label, limit=None) → 打印可见元素 text/id/class
│   │                               #   dump_webview_html(driver, logger, save_name="debug_webview.html") → dump H5 源码
│   │                               #   close_anr_if_exists(driver, logger, timeout=2) -> bool → 关 ANR/崩溃弹窗
│   └── test_helpers.py             # 测试用例侧公共构造函数
│                                   #   build_ops(driver, logger) -> (LoginOperate, FirstPageOperate)
│                                   #   ensure_ready(login_op, first_page_op, logger) -> None
│                                   #       探测发现页：is_on_discover_page() 为真 → 跳过前置；
│                                   #       否则走 run_pre_login_flow + click_discover_tab
│                                   #   build_fuwu_op(driver, logger)         # 带 ensure_ready
│                                   #   build_fuwu_op_keep(driver, logger)    # 不做 ensure_ready（热续跑场景：用例 16~20 跟在用例 15 之后）
│                                   #   build_buycar_op(driver, logger)       # 带 ensure_ready
│
├── testcase_manage/                # 【第三层】用例层
│   ├── conftest.py                 # session 级 fixture（依赖链 logger ← driver ← is_logged_in_session）
│   │                               # + 启动辅助函数：_build_appium_options / _close_anr_if_exists /
│   │                               #   _relaunch_app / _is_on_discover_page / _click_agreement_with_retry
│   ├── test_business_flow.py       # test_<flow> 函数，@pytest.mark.smoke|regression|business
│   │                               # 用例通过 utils.test_helpers 构造 operate（别名导入保持调用点不变）
│   └── data/
│       ├── __init__.py
│       └── fatie_data.py           # FATIE_DRAFT_DATA：parametrize 数据 (用例ID, 标题, 内容, 断言关键字)
│
├── logs/                           # 运行时生成 run_YYYYMMDD_HHMMSS.log（gitignore）
├── allure-results/                 # allure 报告数据（gitignore，cli.py 硬编码 --alluredir）
└── testcase_manage/chromedriver.exe # 与 WebView Chrome 91 对应的 chromedriver（gitignore，手动安装）
```

## 分层规范

### page_element 层
- 只定义定位器元组：`BTN = (AppiumBy.ID, f"{APP_PACKAGE}:id/btn2")` 或 `(By.XPATH, "//android.widget...")`
- **APP 级常量**（APP_PACKAGE / APP_ACTIVITY / APP_WAIT_ACTIVITY / DEVICE_NAME / APPIUM_SERVER / EXPECT_WAIT_TIMEOUT=10）统一放 `login_page.py`
  - APP_WAIT_ACTIVITY 用逗号分隔多 Activity 列表（SplashActivity / QYMainActivity / QYLeadingActivity / QYLoginActivty）
- 优先使用 text-based XPath，避免依赖 `[index]`（index 在不同分辨率下不稳定）
- resource-id 歧义时改用 text XPath
- 每个模块用 `__all__` 显式导出常量
- 启动阶段元素（AGREEMENT_BTN / CLOSE_BTN / CLICK_BTN）单独分组

### object_operation 层
- 构造签名统一：`__init__(self, driver, logger, expect_wait_timeout=EXPECT_WAIT_TIMEOUT)`
- 方法名为动词短语：`click_xxx` / `input_xxx` / `swipe_xxx` / `is_on_xxx`
- **操作方法不做业务断言**，只在内部 `logger.info` 记录；让用例层决定成败
- **_click 内部模板**：`close_popup_if_exists()` → `find_element(*locator).click()` → 失败时 `_dump_visible` + `raise`
- 跨操作依赖通过构造参数注入（如 `OrderOperate(..., webview_operate=webview_op)`）
- dump 类排障方法改为调用 `utils.debug_helpers.dump_visible`（避免每个 operate 各自实现）
- 方法名、docstring、实际行为三者必须一致
- 验证码识别：`LoginOperate.__init__` 初始化 `ddddocr.DdddOcr(beta=True, show_ad=False)`，`input_captcha` 用 `screenshot_as_png` + `ocr.classification` 自动填入
- 滑动兼容：`swipe` 方法 W3C Actions 优先（`ActionChains.w3c_actions.pointer_action`），失败 fallback 到 `mobile: swipeGesture` 命令

### utils 层
- **debug_helpers.py**：无状态独立函数，签名固定 `(driver, logger, ...)`，不依赖任何 operate 类
- **test_helpers.py**：跨用例的 operate 构造 + APP 状态重置函数；可 import operate 类，但不能反向依赖用例层
- **消除循环依赖**：operate 文件内**延迟导入** utils（`from utils.debug_helpers import dump_visible` 放在方法体内），避免 operate↔utils 互相 import
- 用例层导入使用别名以保持调用点不变：`from utils.test_helpers import build_ops as _build_ops, ensure_ready as _ensure_ready`

### testcase_manage 层
- 用例函数命名 `test_<business_function>_flow`
- 标记：`@pytest.mark.smoke` / `@pytest.mark.regression` / `@pytest.mark.business`
- 用例只调用 operate / utils 函数；不直接 find_element（除非断言点）
- **业务策略**：根据登录态决定 skip 或继续
  * 未登录前提的用例 → `if is_logged_in_session: pytest.skip("已登录态：让用例 5 跑主体")`
  * 已登录前提的用例 → `if not is_logged_in_session: pytest.skip("未登录态：用例 5 业务前提是'已登录'")`
  * 不依赖登录态的用例（看车/社区/服务 Tab）→ 不判断 is_logged_in_session
- 用例开始前调用 `_ensure_ready(login_op, first_page_op, logger)` 重置 APP 状态
- 用例之间不依赖彼此的 APP 状态，任一失败不影响下一个
- 数据驱动：`@pytest.mark.parametrize("case_id,title,content,assert_key", FATIE_DRAFT_DATA, ids=[x[0] for x in FATIE_DRAFT_DATA])`

## conftest.py 关键设计

### 根 conftest.py
- 仅预留全局钩子（`pytest_configure` / `pytest_addoption`），**不放任何业务 fixture**
- 业务 fixture（logger / driver / is_logged_in_session）统一在 `testcase_manage/conftest.py`
- 让 pytest 识别工程为"带 conftest 的工程"，方便 IDE / CI 加载

### testcase_manage/conftest.py — fixture 依赖链

#### logger（session 级，无依赖）
- 自动创建 `logs/` 目录
- 日志文件名按时间戳：`run_YYYYMMDD_HHMMSS.log`，UTF-8 编码
- 控制台 + 文件双输出
- 独立 logger 名 `"auto_test"`，不污染 root logger
- 避免重复 handler：`if not log_obj.handlers:` 才追加
- Formatter：`%(asctime)s [%(levelname)s] %(message)s`

#### driver（session 级，依赖 logger）
- 使用 `UiAutomator2Options` 新版 API（capabilities 全部走 `options.xxx`，不用 desired_capabilities 字典）
- `noReset=True`：保留 APP 登录态 / 缓存，避免每个用例重新登录
- `appium:chromedriverExecutable` 显式指定 chromedriver 路径（Appium 2 不自动下载）
  - 路径：`os.path.join(os.path.dirname(__file__), "chromedriver.exe")`
- Appium 2 地址 `http://127.0.0.1:4723`（v6 客户端不再追加 /wd/hub）
- `implicitly_wait(EXPECT_WAIT_TIMEOUT)` + `sleep(3)` 等 APP 启动动画结束
- 启动后**先探测是否已在发现页**（`_is_on_discover_page`：包名匹配 + 「推荐」Tab 2s 可见）：
  * 是 → 跳过协议弹窗 / 冷启动 / ANR 处理，直接 yield
  * 否 → 走 `_click_agreement_with_retry`（max_retry=1，等待 2s）→ 必要时 `_relaunch_app`
- 启动时先 `_close_anr_if_exists` 关一次 ANR 弹窗
- 整个 session 结束统一 `quit()`（try/finally 包裹）
- **协议弹窗重试职责交给用例侧** `ensure_ready` → `run_pre_login_flow`，driver fixture 不重试（避免 noReset 场景下白白浪费 30s）

#### is_logged_in_session（session 级，依赖 driver + logger）
- 基于是否探测到「推荐」Tab，返回 bool（True = 已登录）
- 供用例判断 skip 策略
- 延迟导入 `FirstPageOperate`（避免 conftest 启动时拉入 ddddocr 等）

#### 启动辅助函数（conftest 内私有，带前导下划线）
- `_build_appium_options()` — 构造 UiAutomator2Options
- `_close_anr_if_exists(d, logger, timeout=2)` — 委托 utils.debug_helpers.close_anr_if_exists
- `_relaunch_app(d, logger)` — activate_app 优先，失败 fallback 到 `mobile: startActivity`
- `_is_on_discover_page(d, logger)` — 包名匹配 + RECOMMEND_BUTTON 2s 可见
- `_click_agreement_with_retry(d, logger, max_retry=1)` — 1 次 × 2s，找不到不强制 quit

## WebView 处理规范
- `WebViewOperate.switch_to_webview()`：`WebDriverWait` 等 `len(contexts) >= 2`，精确匹配 `WEBVIEW_<package>`，找不到则兜底取首个非 NATIVE_APP
- H5 元素用 `By.CSS_SELECTOR` / `By.XPATH` / `By.ID`（HTML id 属性），不能用 AppiumBy
- **WebView 用完必须显式切回 `NATIVE_APP`**（`switch_to_native()`），否则后续 native 操作报 "invalid locator"
- chromedriver 版本必须与模拟器内 WebView Chrome 内核版本精确匹配（91.0.4472）

## CLI 入口（cli.py）
```
python cli.py            # 全部用例
python cli.py smoke      # 仅冒烟（@pytest.mark.smoke）
python cli.py regression # 仅回归
python cli.py business   # 仅业务
```
- `EXIT_CODE_MAP`：0=成功 / 1=失败 / 2=中断 / 3=内部错误 / 4=参数错误 / 5=无用例，输出中文提示
- `_build_pytest_args(marker)`：硬编码 `--alluredir=./allure-results --clean-alluredir`
- 支持 `PYTEST_ADDOPTS` 环境变量透传（CI 注入额外 `-k` 等），自动跳过已硬编码的 `--alluredir` / `--clean-alluredir`，去重
- `sys.exit(main())` 把退出码返回给操作系统 / CI

## CI 集成（Jenkins）

### Jenkinsfile（Declarative Pipeline）
- `agent any`
- options：`timestamps()` + 60 分钟 timeout + 保留最近 5 次构建
- environment：`ALLURE_RESULTS_DIR = 'allure-results'`
- stages：
  1. Checkout（`checkout scm`）
  2. Build & Test（`bat 'call jenkins_build_robust.bat'`）
  3. Generate Allure Report（`allure` 步骤指向 `allure-results`）
- post：
  - always：归档 `allure-report/**,allure-results/**`
  - success / failure / unstable：邮件通知（Email-ext Plugin，SMTP 在 Jenkins 系统配置）

### jenkins_build_robust.bat（Windows CI 脚本）
- `chcp 65001` + `PYTHONIOENCODING=utf-8` 解决中文乱码
- 时间用 PowerShell `Get-Date -Format` 拿 ISO 风格时间，避免中文"星期X"乱码
- **0. 前置环境检查**（不通过则 `exit /b 1`）：
  1. `testcase_manage\chromedriver.exe` 存在（gitignore 排除，需手动安装 91.0.4472）
  2. `adb` 在 PATH，且 `adb devices` 至少返回一个设备
  3. Appium server 在 127.0.0.1:4723 监听（TcpClient 探测）
  4. 目标 APP 已安装（pm path，仅 WARN 不阻断）
- 1. 检查 Python 在 PATH
- 2. 创建 / 激活 `.venv`（`python -m venv .venv` + `.venv\Scripts\activate.bat`）
- 3. `pip install -r requirements.txt`
- 4. 运行测试：`python cli.py regression`（默认已登录态跑业务全流程）
  - pytest 退出码 5（无用例）只 WARN 不阻断；其他非 0 退出码 `exit /b`
- 5. 汇总 allure-results 目录

## .gitignore 关键条目
- `.venv/` / `venv/` / `__pycache__/` / `*.py[cod]`
- `debug_*.png` / `debug_*.html` / `*.log`（调试产物）
- `testcase_manage/chromedriver.exe`（手动安装，体积大）
- `.pytest_cache/` / `AllureReports/` / `allure-results/` / `allure-report/`
- `.env` / `.env.local`（敏感环境变量）
- IDE：`.vscode/` / `.idea/`

## 硬约束（Lessons Learned，必须遵守）
1. **热启动场景下不得强制冷重启**：noReset=True + `_is_on_discover_page` 探测，避免死循环（旧版本 3×10s 重试协议弹窗白白浪费 30s）
2. **WebView context 切换必须显式配置 chromedriver 路径**：`appium:chromedriverExecutable`，否则报 "No Chromedriver found that can automate Chrome '91.0.4472'"
3. **元素定位器必须来自实际 UI dump**（Appium Inspector / `dump_visible`），不能用设计稿推测
4. **用例必须同时处理已登录 / 未登录两种状态**：通过 `is_logged_in_session` fixture + skip 策略，不强制 logout
5. **WebView 用完必须切回 NATIVE_APP**：否则后续 native 操作报 "invalid locator"
6. **resource-id 歧义时优先 text XPath，避免 `[index]` 定位**（index 在不同分辨率下不稳定）
7. **方法名 / docstring / 实际代码三者必须一致**（曾因方法名与实现不符导致 AttributeError）
8. **用例步骤必须遵循业务逻辑顺序**（如先选颜色再点下一步，否则假阳性）
9. **utils 层函数无状态**，签名固定 `(driver, logger, ...)`，不依赖 operate 类实例；operate 文件内延迟导入 utils 避免循环依赖
10. **用例之间不依赖彼此的 APP 状态**：任一失败不影响下一个；用例 16~20 跟在用例 15 之后跑时用 `build_fuwu_op_keep`（不做 ensure_ready），避免推荐 Tab 不可见被误判为"未在发现页"触发冷启动
11. **fixture 只做"准备 + 清理"，业务逻辑放操作层**：driver fixture 不重试协议弹窗，重试交给用例侧 `ensure_ready`
12. **chromedriver.exe 不随仓库分发**：gitignore 排除，CI 节点需预装 91.0.4472；前置环境检查脚本必须验证

## 验证要求
1. `python -m pytest --collect-only` 必须能成功收集用例（无 ImportError / 循环依赖）
2. `python cli.py smoke` 在模拟器 + Appium 就绪时能跑通冒烟
3. `call jenkins_build_robust.bat` 在 CI 节点能完成 venv + 依赖 + 测试 + allure-results 产出
4. `utils` 包可独立 import：`from utils.debug_helpers import dump_visible` 不触发循环导入
5. WebView 用例结束后 `driver.context == 'NATIVE_APP'`（不影响后续用例）

## 交付要求
1. 按上述目录结构生成全部文件（含 `__init__.py`）
2. `page_element/login_page.py` 填入 APP 级常量 + EXPECT_WAIT_TIMEOUT=10 + 启动阶段元素
3. `testcase_manage/conftest.py` 填入完整 fixture 实现（logger / driver / is_logged_in_session + 5 个启动辅助函数）
4. `utils/__init__.py` 声明 `__all__ = ["debug_helpers", "test_helpers"]`
5. `utils/debug_helpers.py` 实现 dump_visible / dump_webview_html / close_anr_if_exists 三个无状态函数
6. `utils/test_helpers.py` 实现 build_ops / ensure_ready / build_fuwu_op / build_fuwu_op_keep / build_buycar_op
7. `cli.py` 实现 EXIT_CODE_MAP + _build_pytest_args + PYTEST_ADDOPTS 透传
8. `pytest.ini` + `requirements.txt` + `.gitignore` + `README.md` 齐全
9. `Jenkinsfile` + `jenkins_build_robust.bat` CI 链路完整（含前置环境检查）
