@echo off
REM 切换 CMD 到 UTF-8 代码页，避免中文乱码（脚本与 Python 输出都需要 UTF-8）
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
REM ==========================================================
REM  Jenkins 构建脚本 - qiyuan_project (Windows)
REM  位置：仓库根目录 (即 d:\git_project\demo_qiyuan_bac\)
REM  调用方式：Jenkins "Execute Windows batch command" -> call jenkins_build_robust.bat
REM  假设：Python / Appium server / Android 模拟器 已在节点预装
REM  框架：Appium-Python-client 6.x + Pytest + PO 分层（page_element / object_operation / testcase_manage）
REM ==========================================================
setlocal enabledelayedexpansion

REM 切到脚本所在目录（即仓库根目录）
cd /d "%~dp0"

echo ==========================================================
echo Jenkins 构建脚本 - qiyuan_project
echo 工作目录: %CD%
REM %DATE%/%TIME% 在中文 Windows 下会带"星期X"，容易在 Jenkins 控制台乱码。
REM 改用 PowerShell 拿 ISO 风格的纯数字时间，避免中文。
for /f "delims=" %%t in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"') do set BUILD_TIME=%%t
echo 时间: %BUILD_TIME%
echo ==========================================================

REM ---- 0. 前置环境检查（chromedriver / adb / Appium server / 模拟器） ----
echo.
echo [0/5] 前置环境检查（chromedriver / adb / Appium server / 模拟器）...
set PRECHECK_FAIL=0

REM 0.1 chromedriver.exe 必须在 testcase_manage/ 下（gitignore 排除，需手动安装）
if not exist "testcase_manage\chromedriver.exe" (
    echo   [FAIL] chromedriver.exe 不存在：testcase_manage\chromedriver.exe
    echo          原因：chromedriver.exe 被 .gitignore 排除（手动安装，未随仓库分发）。
    echo          Jenkins 节点需要预装 chromedriver 91.0.4472（与模拟器 WebView Chrome 91 匹配）。
    echo          下载：https://chromedriver.chromium.org/downloads （选 ChromeDriver 91.0.4472.114）
    set PRECHECK_FAIL=1
) else (
    echo   [OK]   chromedriver.exe 已就位
)

REM 0.2 adb 可用，且至少有一个 device
where adb >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] adb 不在 PATH 中。请安装 Android Platform Tools。
    set PRECHECK_FAIL=1
) else (
    for /f "tokens=1" %%d in ('adb devices ^| findstr /R "device$"') do set ADB_DEV=%%d
    if "!ADB_DEV!"=="" (
        echo   [FAIL] adb devices 未返回任何可用设备。请启动 Android 模拟器或连接真机。
        set PRECHECK_FAIL=1
    ) else (
        echo   [OK]   adb 可用，已检测设备：!ADB_DEV!
    )
)

REM 0.3 Appium server 是否在 4723 端口监听
powershell -NoProfile -Command "$c=New-Object System.Net.Sockets.TcpClient; try{$c.Connect('127.0.0.1',4723);$c.Close();exit 0}catch{exit 1}" >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] Appium server 未在 127.0.0.1:4723 监听。
    echo          请先在节点上启动 Appium：appium --base-path /
    set PRECHECK_FAIL=1
) else (
    echo   [OK]   Appium server 在 127.0.0.1:4723 监听
)

REM 0.4 目标 APP 包是否已安装（可选提醒，不阻断）
if not "!ADB_DEV!"=="" (
    adb -s !ADB_DEV! shell pm path com.changan.oushangCos1 >nul 2>nul
    if errorlevel 1 (
        echo   [WARN] 目标 APP 未在 !ADB_DEV! 安装（com.changan.oushangCos1）。
        echo          noReset 模式下跳过冷启动；本警告仅作记录，不阻断构建。
    ) else (
        echo   [OK]   目标 APP 已安装
    )
)

if !PRECHECK_FAIL!==1 (
    echo.
    echo [ERROR] 前置环境检查未通过，请按上述 FAIL 项修复后重新构建。
    exit /b 1
)

REM ---- 1. 检查 Python ----
echo.
echo [1/5] 检查 Python 环境...
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    exit /b 1
)
python --version

REM ---- 2. 创建/激活虚拟环境 ----
echo.
echo [2/5] 配置虚拟环境...
if not exist ".venv\Scripts\python.exe" (
    echo 未检测到虚拟环境，正在创建 .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] 虚拟环境创建失败
        exit /b 1
    )
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] 虚拟环境激活失败
    exit /b 1
)
python -m pip install --upgrade pip --quiet

REM ---- 3. 安装依赖 ----
echo.
echo [3/5] 安装 Python 依赖...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] 依赖安装失败
    exit /b 1
)

REM ---- 4. 运行测试 ----
echo.
echo [4/5] 运行测试（python cli.py 走 pytest 编程调用入口）...
if not exist "allure-results" mkdir "allure-results"

REM 通过 cli.py 执行：默认 regression 标签（已登录态下业务全跑通）。
REM cli.py 已硬编码 --alluredir=./allure-results --clean-alluredir，无需 PYTEST_ADDOPTS。
python cli.py regression
set PYTEST_RC=%ERRORLEVEL%

REM pytest 退出码说明：
REM   0  = 全部通过
REM   1  = 有用例失败
REM   2  = 测试执行被中断
REM   3  = 内部错误
REM   4  = pytest 命令错误
REM   5  = 未收集到用例
echo.
echo pytest 退出码: %PYTEST_RC%
REM 注意：CMD 的多行 if 必须用 () 把整段括起来，否则换行会被当成新命令，
REM 导致 Jenkins 控制台出现 "0 不是内部或外部命令 / 执行被中断?" 之类的乱码。
if not %PYTEST_RC%==0 (
    if not %PYTEST_RC%==5 (
        echo [ERROR] pytest 执行失败，退出码 %PYTEST_RC%
        exit /b %PYTEST_RC%
    ) else (
        echo [WARN] 未收集到 pytest 用例（退出码 5）
    )
)

REM ---- 5. 汇总 ----
echo.
echo [5/5] 汇总...
echo Allure 结果目录: %CD%\allure-results
if exist "allure-results" (
    dir /b "allure-results"
) else (
    echo [WARN] allure-results 目录不存在
)
echo ==========================================================
echo 构建脚本执行完成
echo ==========================================================
exit /b 0
