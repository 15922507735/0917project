"""midSCene 启动启源 APP —— AI 视觉驱动的 UI 自动化演示。

启动方式（在 .venv 下）：
    .\\.venv\\Scripts\\python.exe midscene_open_qiyuan.py

依赖：
    pip install midscene-python
    Android 设备已连接（adb devices 能看到）

midSCene 模型配置从环境变量读取：
    MIDSCENE_AI_PROVIDER  -- qwen / openai / doubao-seed（默认 openai）
    MIDSCENE_AI_MODEL     -- 模型名
    MIDSCENE_AI_API_KEY   -- API key
    MIDSCENE_AI_BASE_URL  -- 可选，自定义 endpoint
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# 加载项目根目录的 .env
PROJECT_ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv

    env_path = PROJECT_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)
except ImportError:
    pass


# 将 .env 里的 MIDSCENE_MODEL_* 系列变量映射到 midscene 期望的 MIDSCENE_AI_*
# （用户 .env 里使用 MIDSCENE_MODEL_* 前缀，是为了统一管理多个模型）
def _setup_midscene_env() -> None:
    """将 MIDSCENE_MODEL_* 映射到 midscene 期望的 MIDSCENE_AI_*。"""
    mapping = {
        "MIDSCENE_MODEL_FAMILY": "MIDSCENE_AI_PROVIDER",
        "MIDSCENE_MODEL_NAME": "MIDSCENE_AI_MODEL",
        "MIDSCENE_MODEL_API_KEY": "MIDSCENE_AI_API_KEY",
        "MIDSCENE_MODEL_BASE_URL": "MIDSCENE_AI_BASE_URL",
    }
    for src, dst in mapping.items():
        src_val = os.getenv(src)
        if src_val and not os.getenv(dst):
            os.environ[dst] = src_val
    # 单值别名（BASE_URL / API_KEY / MODEL_NAME）
    if os.getenv("BASE_URL") and not os.getenv("MIDSCENE_AI_BASE_URL"):
        os.environ["MIDSCENE_AI_BASE_URL"] = os.environ["BASE_URL"]
    if os.getenv("API_KEY") and not os.getenv("MIDSCENE_AI_API_KEY"):
        os.environ["MIDSCENE_AI_API_KEY"] = os.environ["API_KEY"]
    if os.getenv("MODEL_NAME") and not os.getenv("MIDSCENE_AI_MODEL"):
        os.environ["MIDSCENE_AI_MODEL"] = os.environ["MODEL_NAME"]


_setup_midscene_env()

APP_PACKAGE = os.getenv("APP_PACKAGE", "com.changan.oushangCos1")
DEVICE_NAME = os.getenv("DEVICE_NAME", "emulator-5554")


async def _run() -> None:
    """异步启动 APP。"""
    from midscene.android import AndroidAgent, AndroidDevice

    print(f"[*] 设备: {DEVICE_NAME}")
    print(f"[*] APP: {APP_PACKAGE}")
    print(f"[*] Provider: {os.getenv('MIDSCENE_AI_PROVIDER', 'openai')}")
    print(f"[*] Model: {os.getenv('MIDSCENE_AI_MODEL', '<unset>')}")
    print(f"[*] Base URL: {os.getenv('MIDSCENE_AI_BASE_URL', '<default>')}")

    if not os.getenv("MIDSCENE_AI_API_KEY"):
        print("[!] MIDSCENE_AI_API_KEY 未设置，请在 .env 里填入真实 key")
        sys.exit(1)

    # 构造 AndroidAgent（midSCene 0.1.1 修复了 Generic bug 后可直接用）
    print("[*] 初始化 AndroidAgent ...")
    agent = await AndroidAgent.create(device_id=DEVICE_NAME)
    print("[*] midSCene AndroidAgent 已就绪")

    # 通过自然语言启动 APP（midSCene 的核心能力：AI 视觉驱动 UI）
    print("[*] 启动启源 APP ...")
    await agent.launch_app(package_name=APP_PACKAGE)
    print(f"[*] 已启动 {APP_PACKAGE}")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
