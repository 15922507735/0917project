"""Midscene 视觉驱动：执行 qymidscene.txt 用例（我的页面：粉丝/关注/发布/草稿/评论/喜欢）。"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    _env_path = PROJECT_ROOT / ".env"
    if _env_path.is_file():
        load_dotenv(_env_path, override=False)
except ImportError:
    pass


def _setup_midscene_env() -> None:
    # 切换到 MiniMax（Doubao 额度已用完）
    if os.getenv("API_KEY") and os.getenv("MODEL_NAME") and os.getenv("BASE_URL"):
        os.environ["MIDSCENE_AI_API_KEY"] = os.environ["API_KEY"]
        os.environ["MIDSCENE_AI_MODEL"] = os.environ["MODEL_NAME"]
        os.environ["MIDSCENE_AI_BASE_URL"] = os.environ["BASE_URL"]
        os.environ["MIDSCENE_AI_PROVIDER"] = "openai"
        print(f"[*] 使用 MiniMax 模型: {os.environ['MODEL_NAME']}")
        return

    # 回退到 MIDSCENE_MODEL_* 配置
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

    provider = os.getenv("MIDSCENE_AI_PROVIDER", "")
    if provider in ("doubao-seed", "doubao", "ark"):
        os.environ["MIDSCENE_AI_PROVIDER"] = "openai"


_setup_midscene_env()

APP_PACKAGE = os.getenv("APP_PACKAGE", "com.changan.oushangCos1")
DEVICE_NAME = os.getenv("DEVICE_NAME", "emulator-5554")


async def _run() -> None:
    from midscene.android import AndroidAgent

    print(f"[*] 设备: {DEVICE_NAME}")
    print(f"[*] Provider: {os.getenv('MIDSCENE_AI_PROVIDER', 'openai')}")
    print(f"[*] Model: {os.getenv('MIDSCENE_AI_MODEL', '<unset>')}")

    if not os.getenv("MIDSCENE_AI_API_KEY"):
        print("[!] MIDSCENE_AI_API_KEY 未设置")
        sys.exit(1)

    print("[*] 初始化 AndroidAgent ...")
    agent = await AndroidAgent.create(device_id=DEVICE_NAME)
    print("[*] AndroidAgent 就绪\n")

    # ======== 步骤 1：启动 APP ========
    print("[1] 启动 APP ...")
    await agent.launch_app(package_name=APP_PACKAGE)
    await asyncio.sleep(5)

    # 关闭崩溃弹窗
    print("[1] 检测并关闭崩溃弹窗 ...")
    try:
        await agent.ai_action("如果页面上有崩溃或 Application Error 弹窗，点击其'关闭'或'确定'按钮；如果没有弹窗则不做任何操作")
        await asyncio.sleep(2)
    except Exception as e:
        print(f"[1] 崩溃弹窗处理跳过: {e}")

    # ======== 步骤 2：点击底部"我的" ========
    print("[2] 点击底部'我的'按钮 ...")
    await agent.ai_action("点击页面底部导航栏的'我的'按钮")
    await asyncio.sleep(2)

    # ======== 步骤 3：点击"粉丝" ========
    print("[3] 点击'粉丝' ...")
    await agent.ai_action("点击页面上显示'粉丝'的文字入口")
    await asyncio.sleep(2)

    # 3a: 点击第一个粉丝的"回关"或"互相关注"按钮
    print("[3a] 点击第一个粉丝的'回关'或'互相关注'按钮 ...")
    try:
        await agent.ai_action("在粉丝列表中，点击第一个条目右侧的'回关'按钮；如果没有'回关'按钮则点击'互相关注'按钮")
    except Exception as e:
        print(f"[3a] 未找到回关/互相关注按钮: {e}")
    await asyncio.sleep(1)

    # 3b: 点击左上角返回按钮
    print("[3b] 点击左上角返回按钮 ...")
    await agent.back()
    await asyncio.sleep(2)

    # ======== 步骤 4：点击"关注" ========
    print("[4] 点击'关注' ...")
    await agent.ai_action("点击页面上显示'关注'的文字入口")
    await asyncio.sleep(2)

    # 4a: 点击左上角返回按钮，等2s
    print("[4a] 点击左上角返回按钮 ...")
    await agent.back()
    await asyncio.sleep(2)

    # ======== 步骤 5：点击"发布" ========
    print("[5] 点击'发布' ...")
    await agent.ai_action("点击页面上显示'发布'的文字入口")
    await asyncio.sleep(2)

    # 5a: 检查出现"编辑"按钮
    print("[5a] 检查'编辑'按钮是否出现 ...")
    try:
        await agent.ai_assert("页面上能看到'编辑'按钮", message="编辑按钮应出现")
        print("[5a] '编辑'按钮可见 ✓")
    except Exception as e:
        print(f"[5a] '编辑'按钮断言失败: {e}")

    # 5b: 点击第一个帖子标题"此刻我想吟诗一首"
    print("[5b] 点击帖子标题'此刻我想吟诗一首' ...")
    try:
        await agent.ai_action("点击帖子标题文字'此刻我想吟诗一首'")
    except Exception:
        await agent.ai_action("点击帖子列表中的第一个帖子")
    await asyncio.sleep(2)

    # 5c: 检查出现"帖子详情"，等2s
    print("[5c] 检查帖子详情页面 ...")
    try:
        await agent.ai_assert("页面显示帖子详情内容", message="应进入帖子详情页")
        print("[5c] 帖子详情页可见 ✓")
    except Exception as e:
        print(f"[5c] 帖子详情页断言失败: {e}")
    await asyncio.sleep(2)

    # 5d: 点击帖子详情页返回按钮
    print("[5d] 点击帖子详情页返回按钮 ...")
    await agent.back()
    await asyncio.sleep(2)

    # ======== 步骤 6：点击"我的草稿" ========
    print("[6] 点击'我的草稿'，等2s ...")
    await agent.ai_action("点击页面上显示'我的草稿'的文字入口")
    await asyncio.sleep(2)

    # ======== 步骤 7：点击"我的评论" ========
    print("[7] 点击'我的评论' ...")
    await agent.ai_action("点击页面上显示'我的评论'的文字入口")
    await asyncio.sleep(2)

    # 7a: 点击左上角返回按钮
    print("[7a] 点击左上角返回按钮 ...")
    await agent.back()
    await asyncio.sleep(2)

    # ======== 步骤 8：点击"喜欢" ========
    print("[8] 点击'喜欢' ...")
    await agent.ai_action("点击页面上显示'喜欢'的文字入口")
    await asyncio.sleep(2)

    # 8a: 检查出现"我的收藏"
    print("[8a] 检查'我的收藏'是否出现 ...")
    try:
        await agent.ai_assert("页面上能看到'我的收藏'文字", message="应出现我的收藏")
        print("[8a] '我的收藏'可见 ✓")
    except Exception as e:
        print(f"[8a] '我的收藏'断言失败: {e}")

    # 8b: 点击"资讯"
    print("[8b] 点击'资讯' ...")
    await agent.ai_action("点击页面上的'资讯'Tab或文字")
    await asyncio.sleep(2)

    # 8c: 检查出现"关注"或"已关注"按钮
    print("[8c] 检查'关注'或'已关注'按钮 ...")
    try:
        await agent.ai_assert("页面上能看到'关注'按钮或'已关注'按钮", message="应出现关注/已关注按钮")
        print("[8c] '关注/已关注'按钮可见 ✓")
    except Exception as e:
        print(f"[8c] 关注按钮断言失败: {e}")

    # 8d: 点击页面左上角返回按钮
    print("[8d] 点击左上角返回按钮 ...")
    await agent.back()
    await asyncio.sleep(2)

    print("\n[√] 所有步骤执行完毕！")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
