"""object_operation 包：PO 分层中的"操作层"。

封装对页面元素的具体操作（点击、输入、滑动等），不包含用例断言逻辑。
每个页面单独一个模块（如 login_operate / first_page_operate /
order_operate / webview_operate），构造方法接受 driver 与 logger。
"""
from __future__ import annotations

# 包级 __all__：对外暴露所有操作模块
__all__ = [
    "login_operate",
    "first_page_operate",
    "order_operate",
    "webview_operate",
]
