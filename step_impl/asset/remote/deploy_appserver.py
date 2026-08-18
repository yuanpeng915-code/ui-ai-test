"""
description: 在 资产-远程客户端-应用服务器 页部署usmdriver
route: /index/#/index/manage/project/1/asset/remote_server
steps:
  1. @step("打开应用服务器页面")                            【必须】
  2. @step("打开应用服务器部署弹窗<server_ip>")              【必须】
  3. @step("生成应用服务器部署命令")                         【必须】
  4. @step("调用接口部署Linux的usmdriver<architecture>")      【可选】
  5. @step("调用接口部署Windows的usmdriver")                 【可选】
  6. @step("测试应用服务器部署")                             【必须】
  7. @step("确认应用服务器部署")                             【必须】
  8. @step("验证应用服务器服务状态<server_ip>")               【必须】
remark:
  1. step4/step5 二选一，按服务器操作系统选择(Linux 走 step4，Windows 走 step5)
  2. step4 的 architecture 决定取 2.2 安装usmdriver 中哪条命令(arm_64->arm, x86_64->x86)
  3. step4/5 从页面生成的命令中自动提取 server_ip/ak/sk，调用 http://10.113.56.129:5000/appServer/deploy
  4. Windows 命令无架构区分，接口 architecture 默认传 x86_64
"""
import re
import requests
from getgauge.python import step, data_store

DEPLOY_API = "http://10.113.56.129:5000/appServer/deploy"
_ARCH_SUFFIX = {"arm_64": "arm", "x86_64": "x86"}


@step("打开应用服务器页面")
def open_appserver_page():
    """
    description:导航到远程客户端页并切换到应用服务器tab。部署第1步，必须。
    params: 无
    """
    page = data_store.suite["page"]
    # 应用服务器是远程客户端页的子tab，直接导航到 remote_server 比点tab更稳(SPA hash路由二次点击会失效)
    base = page.url.split("/index/")[0]
    page.goto(base + "/index/#/index/manage/project/1/asset/remote_server", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    assert "remote_server" in page.url, "未切换到应用服务器页面"


@step("打开应用服务器部署弹窗<server_ip>")
def open_appserver_deploy_drawer(server_ip):
    """
    description:在应用服务器列表按IP找到目标行，点击部署打开部署抽屉。部署第2步，必须。
    params:
        - server_ip:必填|文本|任意文本，应用服务器IP(如 10.113.57.78)
    """
    page = data_store.suite["page"]
    row = page.locator(".usm_virtual_row").filter(has_text=server_ip).first
    assert row.is_visible(), f"未找到 IP 为 {server_ip} 的应用服务器"
    row.get_by_text("部署", exact=True).first.click()
    page.wait_for_timeout(1000)
    drawer = page.locator(".ant-drawer-content").last
    assert "部署" in drawer.text_content(), "部署弹窗未打开"


@step("生成应用服务器部署命令")
def generate_appserver_deploy_command():
    """
    description:在部署抽屉点击生成命令按钮，等待命令区出现。部署第3步，必须。
    params: 无
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    drawer.get_by_role("button", name="生成命令").click()
    page.wait_for_timeout(1500)
    assert "usmdriver" in drawer.text_content(), "生成命令后未显示 usmdriver 命令"


@step("调用接口部署Linux的usmdriver<architecture>")
def deploy_linux_usmdriver_via_api(architecture):
    """
    description:从命令区按架构取Linux usmdriver命令，提取server_ip/ak/sk后调部署接口。部署第4步，Linux服务器选此。
    params:
        - architecture:必填|文本|arm_64/x86_64，CPU架构决定取哪条命令
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    arch_suffix = _ARCH_SUFFIX.get(architecture, architecture)
    cmd_para = drawer.locator("p").filter(has_text=f"usmdriver-linux-{arch_suffix}").first
    cmd_text = cmd_para.text_content()
    assert cmd_text, f"未找到架构 {architecture}(后缀{arch_suffix}) 的 Linux usmdriver 命令"

    match = re.search(
        rf"https://([^/]+)/pamapi/appserver/tools/usmdriver-linux-{arch_suffix}.*?-ak=(\w+)\s+-sk=(\w+)",
        cmd_text,
    )
    assert match, f"无法从命令中提取参数: {cmd_text}"
    server_ip, ak, sk = match.group(1), match.group(2), match.group(3)

    resp = requests.post(DEPLOY_API, json={
        "platform": "linux",
        "architecture": architecture,
        "server_ip": server_ip,
        "ak": ak,
        "sk": sk,
    }, timeout=600)
    data = resp.json()
    assert data.get("code") == "ok", f"Linux 部署接口调用失败: {data}"


@step("调用接口部署Windows的usmdriver")
def deploy_windows_usmdriver_via_api():
    """
    description:从命令区取Windows usmdriver命令(PowerShell)，提取server_ip/ak/sk后调部署接口。部署第5步，Windows服务器选此。
    params: 无
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    cmd_para = drawer.locator("p").filter(has_text="usmdriver-win").first
    cmd_text = cmd_para.text_content()
    assert cmd_text, "未找到 Windows usmdriver 命令"

    match = re.search(
        r'https://([^/]+)/pamapi/appserver/tools.*?-ak=(\w+)\s+-sk=(\w+)',
        cmd_text, re.DOTALL,
    )
    assert match, f"无法从 Windows 命令中提取参数: {cmd_text}"
    server_ip, ak, sk = match.group(1), match.group(2), match.group(3)

    resp = requests.post(DEPLOY_API, json={
        "platform": "windows",
        "architecture": "64",
        "server_ip": server_ip,
        "ak": ak,
        "sk": sk,
    }, timeout=600)
    data = resp.json()
    assert data.get("code") == "ok", f"Windows 部署接口调用失败: {data}"


@step("测试应用服务器部署")
def test_appserver_deploy():
    """
    description:点击测试按钮，等待测试结果，断言运维服务/改密服务均为正常。部署第6步，必须。
    params: 无
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    drawer.get_by_role("button", name="测试").click()
    # 等待测试结果出现(运维服务段落)
    drawer.locator("p").filter(has_text="运维服务").wait_for(state="visible", timeout=20000)
    page.wait_for_timeout(500)

    om_text = drawer.locator("p").filter(has_text="运维服务").first.text_content()
    pwd_text = drawer.locator("p").filter(has_text="改密服务").first.text_content()
    assert "正常" in om_text, f"运维服务状态异常: {om_text}"
    assert "正常" in pwd_text, f"改密服务状态异常: {pwd_text}"


@step("确认应用服务器部署")
def confirm_appserver_deploy():
    """
    description:点击确定按钮关闭部署抽屉。部署第7步，必须。
    params: 无
    """
    page = data_store.suite["page"]
    page.get_by_role("button", name="确 定").click()
    page.wait_for_timeout(2000)
    btn = page.get_by_role("button", name="确 定")
    assert btn.count() == 0 or not btn.first.is_visible(), "部署弹窗未关闭"


@step("验证应用服务器服务状态<server_ip>")
def verify_appserver_service_status(server_ip):
    """
    description:在列表中按IP找到应用服务器行，断言运维服务状态/改密服务状态均为正常。部署第8步，必须。
    params:
        - server_ip:必填|文本|任意文本，应用服务器IP(如 10.113.57.78)
    """
    page = data_store.suite["page"]
    page.wait_for_timeout(1500)
    row = page.locator(".usm_virtual_row").filter(has_text=server_ip).first
    assert row.is_visible(), f"未找到 IP 为 {server_ip} 的应用服务器"

    normal_count = row.get_by_text("正常", exact=True).count()
    assert normal_count >= 2, f"服务状态异常: 期望运维/改密服务均为正常，'正常'数量={normal_count}"
