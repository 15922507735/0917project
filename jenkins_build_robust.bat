@echo off
REM ==========================================================
REM  Jenkins 构建脚本 - qiyuan_project (Windows)
REM  位置：仓库根目录 (即 demo_project/)
REM  调用方式：Jenkins "Execute Windows batch command" -> call jenkins_build_robust.bat
REM  假设：Python / Appium server / Android 模拟器 已在节点预装
REM ==========================================================
setlocal enabledelayedexpansion

REM 切到脚本所在目录（即仓库根目录）
cd /d "%~dp0"

echo ==========================================================
echo Jenkins 构建脚本 - qiyuan_project
echo 工作目录: %CD%
echo 时间: %DATE% %TIME%
echo ==========================================================

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
echo [4/5] 运行 pytest + 生成 allure-results...
if not exist "allure-results" mkdir "allure-results"

pytest scripts\test_login.py scripts\test_first_page.py ^
    -v ^
    --alluredir=.\allure-results ^
    --clean-alluredir
set PYTEST_RC=%ERRORLEVEL%

REM pytest 退出码说明：
REM   0  = 全部通过
REM   1  = 有用例失败
REM   2  = 测试执行被中断
REM   3  = 内部错误
REM   4  = pytest 命令错误
REM   5  = 未收集到用例（脚本还在骨架阶段，暂时接受）
echo.
echo pytest 退出码: %PYTEST_RC%
if %PYTEST_RC% neq 0 (
    if %PYTEST_RC% neq 5 (
        echo [ERROR] pytest 执行失败，退出码 %PYTEST_RC%
        exit /b %PYTEST_RC%
    ) else (
        echo [WARN] 未收集到 pytest 用例（退出码 5），脚本仍处于骨架阶段，继续生成 allure 报告。
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
