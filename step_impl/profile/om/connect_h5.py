"""
description: 运维资产连接 - H5运维方式
route: /index/#/index/profile/om
steps:
  1. @step("打开运维连接弹窗<asset_name>")          【必须】 (connect_om)
  2. @step("选择运维账号<account_service>")         【必须】 (connect_om)
  3. @step("选择H5运维方式")                        【必须】 (本文件)
  4. @step("选择运维远程客户端<remote_client>")     【可选】 (connect_om)
  5. @step("发起运维连接")                          【必须】 (connect_om)
remark：
  1. 需配合 connect_om.py 使用，spec 中同时导入两个文件
  2. 运维方式固定为"H5运维"，用户无需传参
  3. 远程客户端默认"不使用"，可不传
"""
from getgauge.python import step, data_store
from step_impl.profile.om import _get_active_page


@step("选择H5运维方式")
def select_om_method_h5():
    """
    name: 选择H5运维方式
    description: 在已打开的运维连接弹窗中，固定选择"H5运维"方式。第3步，必须。
                 用户无需传参，内部自动选中H5运维。
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
    option = dropdown.locator(".ant-select-item-option").filter(has_text="H5运维").first
    assert option.count() > 0, "运维方式下拉中未找到 'H5运维' 选项"
    option.click()
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(300)

    selected = popover.locator(
        "//label[@title='运维方式']/../..//span[contains(@class,'ant-select-selection-item')]"
    ).text_content().strip()
    assert "H5运维" in selected, f"运维方式选中失败: 期望含 'H5运维', 实际 '{selected}'"
