"""page_element 包：PO 分层中的"元素层"。

仅存放页面元素定位表达式（locator 元组），不包含任何业务逻辑。
每个页面单独一个模块（如 login_page.py / first_page.py / order_page.py），
并在 __all__ 中按页面导出元素常量。
"""
from __future__ import annotations

# 包级 __all__：对外暴露所有页面模块，方便外部统一 from page_element import *
__all__ = [
    "login_page",
    "first_page",
    "order_page",
]
