"""
description: 运维资产连接公共步骤（打开弹窗、选账号、选客户端、登录）
route: /index/#/index/profile/om
steps:
  1. @step("打开运维连接弹窗<asset_name>")          【必须】
  2. @step("选择运维账号<account_service>")         【必须】
  3. @step("选择运维远程客户端<remote_client>")     【可选】
  4. @step("发起运维连接")                          【必须】
remark：
  1. 本文件为 H5/APP 运维连接的公共步骤，不单独使用
  2. 需配合 connect_h5.py 或 connect_app.py 中的"选择XX运维方式"步骤完成完整流程
  3. 账号/服务使用模糊匹配，多个匹配时取第一个
  4. 远程客户端默认"不使用"
  5. 需先在 ASSET_NODE/GROUP 视图（选分组后），最近运维视图下无向下箭头
"""
from getgauge.python import step, data_store
from step_impl.profile.om import _get_active_page


def _find_asset_row(asset_name: str):
    """在虚拟列表中按资产名称定位行，返回 locator 或 None"""
    page = _get_active_page()
    rows = page.locator(".usm_virtual_row")
    for i in range(rows.count()):
        name_cell = rows.nth(i).locator(".usm_virtual_cell").nth(2)
        if asset_name in (name_cell.text_content() or ""):
            return rows.nth(i)
    return None


@step("打开运维连接弹窗<asset_name>")
def open_om_connect(asset_name: str):
    """
    name: 打开运维连接弹窗
    description: 在运维页按资产名称定位行，点击访问栏向下箭头弹出连接配置弹窗。第1步，必须。
                 必须先进入运维页并选中分组。
    params:
        - asset_name: 必填 | 文本 | 资产名称(如 mysql-82)
    """
    page = _get_active_page()
    assert "profile/om" in page.url, "请先进入运维页面"

    row = _find_asset_row(asset_name)
    assert row is not None, f"未找到资产 '{asset_name}'"

    arrow = row.locator(".usm_icon.click_hover.dropdown")
    assert arrow.is_visible(), f"资产 '{asset_name}' 的向下箭头不可见"
    arrow.click()
    page.wait_for_timeout(1500)

    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未出现"


@step("选择运维账号<account_service>")
def select_om_account(account_service: str):
    """
    name: 选择运维账号
    description: 在已打开的运维连接弹窗中，从账号/服务下拉模糊匹配选择指定账号。第2步，必须。
                 多个匹配时取第一个。不传则保留默认。
    params:
        - account_service: 必填 | 文本 | 账号/服务(如 MySQL, SSH)，支持模糊匹配
    """
    page = _get_active_page()
    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未打开"

    if not account_service:
        return

    popover.locator(
        "//label[@title='账号/服务']/../..//div[contains(@class,'ant-select-selector')]"
    ).click()
    page.wait_for_timeout(800)

    dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
    # 模糊匹配：多个匹配时取第一个
    option = dropdown.locator(".ant-select-item-option").filter(has_text=account_service).first
    assert option.count() > 0, f"账号/服务下拉中未找到匹配 '{account_service}' 的选项"
    option.click()
    page.wait_for_timeout(300)

    selected = popover.locator(".ant-select-selection-item").first.text_content().strip()
    assert account_service in selected, f"账号选中失败: 期望含 '{account_service}', 实际 '{selected}'"


@step("选择运维远程客户端<remote_client>")
def select_om_client(remote_client: str = ""):
    """
    name: 选择运维远程客户端
    description: 在已打开的运维连接弹窗中，从远程客户端下拉选择客户端。第4步，可选。
                 不传默认选"不使用"。目前仅支持"不使用"，其它方式环境有问题。
    params:
        - remote_client: 非必填 | 文本 | 不使用/PuTTY，默认"不使用"
    """
    page = _get_active_page()
    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未打开"

    # 默认"不使用"
    if not remote_client:
        remote_client = "不使用"

    # 检查是否已是目标值，避免重复操作
    try:
        current = popover.locator(
            "//label[@title='远程客户端']/../..//span[contains(@class,'ant-select-selection-item')]"
        ).first.text_content().strip()
        if remote_client in current:
            return
    except Exception:
        pass

    popover.locator(
        "//label[@title='远程客户端']/../..//div[contains(@class,'ant-select-selector')]"
    ).click()
    page.wait_for_timeout(800)

    dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
    option = dropdown.locator(".ant-select-item-option").filter(has_text=remote_client).first
    assert option.count() > 0, f"远程客户端下拉中未找到匹配 '{remote_client}' 的选项"
    option.click()
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    selected = popover.locator(
        "//label[@title='远程客户端']/../..//span[contains(@class,'ant-select-selection-item')]"
    ).first.text_content().strip()
    assert remote_client in selected, f"远程客户端选中失败: 期望含 '{remote_client}', 实际 '{selected}'"


@step("发起运维连接")
def do_om_login():
    """
    name: 发起运维连接
    description: 在已配置好的运维连接弹窗中点击"登 录"，触发运维连接。最后一步，必须。
                 H5/APP 运维无协议确认弹窗，直接触发连接。
    params: 无
    """
    page = _get_active_page()
    popover = page.locator(".ant-popover:not(.ant-popover-hidden)")
    assert popover.count() == 1, "运维连接弹窗未打开"

    popover.locator("button[type='submit']").click()
    page.wait_for_timeout(3000)
