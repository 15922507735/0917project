# -*- coding: utf-8 -*-
"""pytest 全局配置。

在命令行加入 ``--appium-server=http://127.0.0.1:4723`` 可自定义 Appium 服务地址。
"""
import logging


def pytest_addoption(parser):
    parser.addoption(
        "--appium-server",
        action="store",
        default="http://127.0.0.1:4723",
        help="Appium server URL,默认 http://127.0.0.1:4723",
    )


def pytest_configure(config):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )