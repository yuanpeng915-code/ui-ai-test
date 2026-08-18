"""
标题: 等待/Ping 验证服务 / 公用截屏 / WinApp 桌面程序操作
功能: 工具服务调用；提供用例级别的截图 step；向 Windows 桌面程序发送键盘输入
"""
import os
import requests
from getgauge.python import step, data_store
from utils.page_helper import save_screenshots_merged
from utils.win_app import *

# 支持的桌面程序白名单: {名称: 窗口标题关键词}
_WIN_APPS = {
    "Xshell": XShell,
    "MobaXterm": MobaXterm,
    # 后续补充: "DBeaver": "DBeaver", "PuTTY": "PuTTY", ...
}


SERVER_URL = "http://10.113.56.129:5000"

@step("等待<t>秒")
def time_sleep(t):
    """
    name: 等待
    description: 等待指定秒数，单位秒。用于等待异步操作完成或人为延时。
    params:
        - t: 必填 | 数字 | 等待时间(秒)
    """
    time.sleep(float(t))


@step("验证Ping服务已被调用")
def verify_ping_called():
    """
    name:验证Ping服务已被调用
    description:请求 /pong，断言 code="ok"（即 /ping 已被调用过）
    params: 无
    """
    resp = requests.get(f"{SERVER_URL}/sshCheck/pong", timeout=5)
    data = resp.json()
    assert data["code"] == "ok", f"Ping 服务未被调用: last_time={data.get('last_time')}"


@step("清除Ping服务时间戳")
def clear_ping_timestamp():
    """
    name:清除Ping服务时间戳
    description:请求 /clear，清空上次 /ping 记录的时间戳
    params: 无
    """
    requests.get(f"{SERVER_URL}/sshCheck/clear", timeout=5)


@step("截图保存<label>")
def take_step_screenshot(label):
    """
    name:截图保存
    description:截取所有浏览器窗口（管理端/用户端/H5运维）并横向拼接保存到 gauge 报告目录，用于关键步骤人工二次校验
    params:
        - label:文本输入|无|截图标签(如 登录后、提交前)，用于文件名辨识
    """
    screenshots_dir = os.getenv("gauge_screenshots_dir")
    assert screenshots_dir, "gauge_screenshots_dir 环境变量未设置"

    pages = [
        ("admin", data_store.suite.get("page")),
        ("user", data_store.suite.get("user_page")),
        ("h5", data_store.suite.get("h5_page")),
    ]
    save_screenshots_merged(pages, label, screenshots_dir)


@step("向桌面程序<app>发送内容<content>末尾回车<enter>")
def send_to_win_app(app, content, enter):
    """
    name:向桌面程序发送内容
    description:根据程序名聚焦窗口，发送键盘输入，可指定是否末尾加回车。用于向 Xshell/MobaXterm 等终端发送命令
    params:
        - app:文本输入|无|程序名(当前支持 Xshell/MobaXterm)
        - content:文本输入|无|要发送的内容(如 uname、ls /)，为空则仅回车
        - enter:勾选框|是|是否末尾加回车(是/否)
    """
    app = _WIN_APPS.get(app)
    assert app, f"不支持的桌面程序 '{app}'，当前支持: {list(_WIN_APPS.keys())}"

    enter = enter in ("是", "true", "True", "1", "yes")

    windows = app()
    assert windows, f"未找到 {app} 窗口，请先打开 {app}"

    if content:
        windows.send_keys(content)
    if enter:
        windows.press_enter()
        


@step("关闭桌面程序<app>")
def close_win_app(app):
    """
    name:关闭桌面程序
    description:按程序名查找窗口并关闭，用于后置环境清理。当前支持 Xshell/MobaXterm
    params:
        - app:文本输入|无|程序名(当前支持 Xshell/MobaXterm)
    """
    app = _WIN_APPS.get(app)
    assert app, f"不支持的桌面程序 '{app}'，当前支持: {list(_WIN_APPS.keys())}"

    app().close_window()