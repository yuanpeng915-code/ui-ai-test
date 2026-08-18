"""
profile/om 公共辅助函数
- _get_active_page(): 返回当前活跃 page（优先用户端）
- _get_active_page_helper(): 返回当前活跃 page_helper（优先用户端）
"""
from getgauge.python import data_store


def _get_active_page():
    """返回当前活跃的 page：优先用户端 user_page，否则管理端 page"""
    return data_store.suite.get("user_page") or data_store.suite["page"]


def _get_active_page_helper():
    """返回当前活跃的 page_helper：优先用户端 user_page_helper，否则管理端 page_helper"""
    return data_store.suite.get("user_page_helper") or data_store.suite["page_helper"]
