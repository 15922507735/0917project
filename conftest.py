"""根目录 conftest.py：仅预留全局 pytest 钩子，不放任何业务 fixture。

业务相关 fixture（logger / driver / login）统一在 testcase_manage/conftest.py 定义。
本文件存在的意义：
- 未来需要加全局钩子（如 pytest_configure / pytest_addoption）时有一个落点；
- 让 pytest 识别本工程为"带 conftest 的工程"，方便 IDE / CI 工具加载。
"""
from __future__ import annotations

# 当前未启用任何全局钩子；
# 如需扩展，例如：
# def pytest_configure(config):
#     """pytest 启动时执行一次的全局配置钩子。"""
#     ...
#
# def pytest_addoption(parser):
#     """注册自定义命令行参数。"""
#     parser.addoption("--env", action="store", default="test", help="运行环境")
