"""测试执行入口：python cli.py [smoke|regression|...]。

支持三种调用方式：
- python cli.py                  # 执行所有用例（pytest 默认行为）
- python cli.py smoke            # 仅执行带 @pytest.mark.smoke 标记的用例
- python cli.py regression       # 仅执行带 @pytest.mark.regression 标记的用例

返回值约定：
- 0  -> 全部用例通过
- 非 0 -> 有用例失败（5=无用例收集，1=有失败，2=用户中断，3=内部错误）

环境变量：
- PYTEST_ADDOPTS：可由 CI / 外部脚本注入额外参数（如 --alluredir=./allure-results），
  会被 shlex 拆分后追加到 pytest.main() 参数列表。
"""
from __future__ import annotations

import os
import sys
import time

import pytest


# pytest exit code 语义参考：
#   0 = 所有用例通过
#   1 = 部分用例失败
#   2 = 用户中断（Ctrl+C）
#   3 = pytest 内部错误
#   4 = pytest 命令行参数错误
#   5 = 没有用例被收集
EXIT_CODE_MAP = {
    0: ("成功", "所有用例执行通过"),
    1: ("失败", "存在用例执行失败，请查看上方日志"),
    2: ("中断", "用户中断（Ctrl+C）"),
    3: ("内部错误", "pytest 内部错误"),
    4: ("参数错误", "命令行参数错误"),
    5: ("无用例", "未收集到任何用例，请检查标记或用例路径"),
}


def _build_pytest_args(marker: str | None) -> list[str]:
    """根据用户传入的标记构造 pytest.main() 参数列表。

    参数：
        marker: 标签名（smoke / regression / business），传 None 表示不筛选。

    返回：
        完整的 pytest.main() 参数列表。

    额外逻辑：
        - 读取环境变量 PYTEST_ADDOPTS（如 CI 注入的 --alluredir=./allure-results），
          shlex 拆分后追加到参数列表，等价于命令行透传。
    """
    # addopts 与 pytest.ini 中的配置保持一致；显式传入是为了让
    # 直接调用 pytest.main() 时也能拿到相同的输出格式。
    args = ["-v", "--tb=short"]
    if marker:
        # -m 后跟标记名即可筛选；不存在时 pytest 会报"未收集到用例"
        args.extend(["-m", marker])

    # 透传 PYTEST_ADDOPTS（CI / 外部脚本追加 --alluredir / -k 等场景）
    extra = os.environ.get("PYTEST_ADDOPTS", "").strip()
    if extra:
        try:
            import shlex
            args.extend(shlex.split(extra))
        except Exception:
            args.extend(extra.split())
    return args


def run(marker: str | None = None) -> int:
    """执行测试入口。

    参数：
        marker: 用例标记名，可选；为 None 时执行全部用例。

    返回：
        pytest 的退出码（0 表示全部通过）。
    """
    title = f"pytest 自动化测试 - {marker if marker else '全部用例'}"
    print("=" * 70)
    print(f"▶ {title}")
    print("=" * 70)

    args = _build_pytest_args(marker)
    print(f"[cli] 即将执行命令: pytest {' '.join(args)}")
    start_ts = time.time()
    # pytest.main() 返回值即为退出码
    exit_code = pytest.main(args)
    elapsed = time.time() - start_ts

    # 解析退出码并输出中文提示
    status, message = EXIT_CODE_MAP.get(
        exit_code, ("未知", f"未识别的退出码 {exit_code}")
    )
    print("=" * 70)
    print(f"◀ 执行完成，用时 {elapsed:.2f}s")
    print(f"  退出码: {exit_code}")
    print(f"  状态:   {status}")
    print(f"  说明:   {message}")
    print("=" * 70)

    # 成功/失败时分别输出醒目提示
    if exit_code == 0:
        print("[OK] 所有用例执行通过！")
    else:
        print(f"[FAIL] 执行结束，状态：{status}。请查看上方详细日志。")
    return exit_code


def main() -> int:
    """命令行入口：解析 argv[1]，决定执行哪个标记。"""
    if len(sys.argv) > 1:
        marker = sys.argv[1].strip()
        # 仅作为 marker 透传给 pytest -m；不强制做白名单校验，
        # 这样未来新增标记无需改 cli.py 即可直接通过命令行调用。
        print(f"[cli] 收到参数: {marker!r}，将作为 pytest -m 参数使用")
    else:
        marker = None
        print("[cli] 未传参数，将执行全部用例")
    return run(marker)


if __name__ == "__main__":
    # sys.exit 把退出码返回给操作系统 / CI
    sys.exit(main())
