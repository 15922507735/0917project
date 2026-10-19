"""通过 ADB 直接启动启源 APP。

启动方式（在 .venv 下）：
    .\\.venv\\Scripts\\python.exe adb_open_qiyuan.py

依赖：
    - adb 已配置（platform-tools 已加入 PATH）
    - Android 设备已连接（adb devices 能看到）

说明：
    midscene-python 0.1.1 版本的 AndroidAgent 类存在 TypeError bug
    （Agent 类不支持 Generic 语法），导致 midscene.android 模块无法导入。
    本脚本绕开 midscene，直接通过 ADB 启动 APP 并等待主页加载。
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

# 加载 .env
PROJECT_ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv

    env_path = PROJECT_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)
except ImportError:
    pass

APP_PACKAGE = os.getenv("APP_PACKAGE", "com.changan.oushangCos1")
DEVICE_NAME = os.getenv("DEVICE_NAME", "emulator-5554")


def _adb(args: list[str], check: bool = True, timeout: int = 30) -> subprocess.CompletedProcess:
    """执行 adb 命令（自动加 -s device_id 前缀）。"""
    cmd = ["adb", "-s", DEVICE_NAME, *args]
    print(f"[adb] {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True, timeout=timeout)


def check_device() -> None:
    """确认设备已连接。"""
    result = subprocess.run(["adb", "devices"], check=True, capture_output=True, text=True)
    print(result.stdout.strip())
    if DEVICE_NAME not in result.stdout or "device" not in result.stdout.split(DEVICE_NAME, 1)[1].split("\n")[0]:
        print(f"[!] 设备 {DEVICE_NAME} 未连接，请检查 adb 连接")
        sys.exit(1)
    print(f"[*] 设备 {DEVICE_NAME} 已就绪")


def launch_app() -> None:
    """通过 ADB 启动 APP。"""
    # 1) 先强制停止旧实例（确保冷启动）
    _adb(["shell", "am", "force-stop", APP_PACKAGE], check=False)
    time.sleep(0.5)

    # 2) 启动 APP（monkey 方式，触发系统启动 intent）
    print(f"[*] 启动 {APP_PACKAGE} ...")
    result = _adb(
        [
            "shell",
            "monkey",
            "-p",
            APP_PACKAGE,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(f"[!] 启动失败: {result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())

    # 3) 等待 APP 进入前台
    print("[*] 等待 APP 进入前台...")
    for i in range(20):
        result = _adb(
            ["shell", "dumpsys", "window", "windows"],
            check=False,
            timeout=10,
        )
        if APP_PACKAGE in result.stdout and "mCurrentFocus" in result.stdout:
            # 简单判断：dump 中包含包名即可认为启动
            print(f"[*] APP 已进入前台（轮询 {i + 1} 次）")
            return
        time.sleep(1)
    print("[!] 等待 APP 启动超时（20s）")
    sys.exit(1)


def main() -> None:
    print(f"[*] 设备: {DEVICE_NAME}")
    print(f"[*] APP: {APP_PACKAGE}")
    check_device()
    launch_app()
    print("[*] 启源 APP 启动完成！")


if __name__ == "__main__":
    main()
