"""
description: 运维资产连接 - 本地运维方式
route: /index/#/index/profile/om
steps:
  1. @step("打开运维连接弹窗<asset_name>")          【必须】 (connect_om)
  2. @step("选择运维账号<account_service>")         【必须】 (connect_om)
  3. @step("选择本地运维方式")                      【必须】 (本文件)
  4. @step("选择运维远程客户端<remote_client>")     【可选】 (connect_om)
  5. @step("发起运维连接")                          【必须】 (connect_om)
remark：
  1. 需配合 connect_om.py 使用，spec 中同时导入两个文件
  2. 运维方式固定为"本地运维"，用户无需传参
  3. 远程客户端默认"不使用"，可不传
  4. 点击登录后触发 window.open("sso://...") 唤起本地运维客户端，Chrome弹出协议确认对话框
"""
from getgauge.python import step, data_store
from step_impl.profile.om import _get_active_page
import ctypes

# Windows 虚拟键码 — OS 级按键，操作 Chrome 协议弹窗用
_VK_LEFT = 0x25
_VK_RETURN = 0x0D
_KEYEVENTF_KEYUP = 0x0002


def _system_key(vk: int):
    """系统级按键: key down + key up"""
    u = ctypes.windll.user32
    u.keybd_event(vk, 0, 0, 0)
    u.keybd_event(vk, 0, _KEYEVENTF_KEYUP, 0)


@step("选择本地运维方式")
def select_om_method_local():
    """
    name: 选择本地运维方式
    description: 在已打开的运维连接弹窗中，固定选择"本地运维"方式。第3步，必须。
                 用户无需传参，内部自动选中本地运维。
    params: 无
    """
    page = _get_active_page()
    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未打开"

    popover.locator(
        "//label[@title='运维方式']/../..//div[contains(@class,'ant-select-selector')]"
    ).click()
    page.wait_for_timeout(800)

    dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
    option = dropdown.locator(".ant-select-item-option").filter(has_text="本地运维").first
    assert option.count() > 0, "运维方式下拉中未找到 '本地运维' 选项"
    option.click()
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    selected = popover.locator(
        "//label[@title='运维方式']/../..//span[contains(@class,'ant-select-selection-item')]"
    ).text_content().strip()
    assert "本地运维" in selected, f"运维方式选中失败: 期望含 '本地运维', 实际 '{selected}'"


@step("发起本地运维连接")
def do_om_login_local():
    """
    name: 发起本地运维连接
    description: 在已配置好的运维连接弹窗中点击"登 录"，触发本地运维连接。最后一步，必须。
                 本地运维时 Chrome 弹出协议确认对话框，模拟 ← + Enter 选择"打开usmsso"。
    params: 无
    """
    page = _get_active_page()
    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未打开"

    popover.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)

    # 本地运维: Chrome 弹出协议确认对话框，默认焦点在"取消"
    # 系统级按键: ← 切到"打开usmsso" → Enter 确认
    _system_key(_VK_LEFT)
    page.wait_for_timeout(500)
    _system_key(_VK_RETURN)
    page.wait_for_timeout(2000)
