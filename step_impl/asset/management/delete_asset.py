"""
description: 在 资产-资产管理 页删除资产（先搜索后批量删除）
route: /index/#/index/manage/project/1/asset/asset
steps:
  1. @step("勾选资产行<select_mode>")         【必须】
  2. @step("点击删除选中资产")                【必须】
  3. @step("确认删除资产")                    【必须】
  4. @step("验证资产删除成功<asset_name>")    【必须】
remark：
  1. 删除前必须先执行搜索步骤(search_asset.py 的 打开资产管理页面/填写资产搜索条件/点击查询资产)
     筛选出目标资产，否则全选会选中整页全部资产
  2. select_mode=全选 点击表头全选框；select_mode=1,3 点击第1、3行checkbox(1起始，逗号分隔)
  3. 勾选步骤通过 .checked_count 文本校验选中数量，0选中时阻断(点删除只会提示"未选择条目")
  4. 验证步骤按资产名称搜索，确认列表中已无该资产(命中空结果即视为删除成功)
"""
from getgauge.python import step, data_store


@step("勾选资产行<select_mode>")
def select_asset_rows(select_mode):
    """
    description: 在资产管理页表格中勾选目标行。删除第1步，必须。先搜索筛选后再勾选。
                 select_mode=全选 点表头全选框；select_mode=1,3 点第1、3行checkbox(1起始)。
                 已勾选的行不会重复点击(避免反选)，通过 .checked_count 校验选中数量。
    params:
        - select_mode: 必填|文本|全选/1,3,5(行号1起始逗号分隔)
    """
    page = data_store.suite["page"]
    assert select_mode, "select_mode 必填，可选: 全选 或 行号如 1,3"

    def _is_checked(locator):
        """读 .ant-checkbox-wrapper 是否带选中态 class。"""
        cls = locator.get_attribute("class") or ""
        return "ant-checkbox-wrapper-checked" in cls

    if select_mode == "全选":
        # 表头全选 checkbox：th.ant-table-selection-column 内的 .ant-checkbox-wrapper
        header_cb = page.locator("th.ant-table-selection-column .ant-checkbox-wrapper").first
        header_cb.wait_for(state="visible", timeout=5000)
        # 仅在未全选时点击(全选态点击会反选清空)
        if not _is_checked(header_cb):
            header_cb.click()
            page.wait_for_timeout(500)
        expected = page.locator(".usm_virtual_row").count()
    else:
        # 解析行号(1起始)，去重排序
        indices = sorted({int(x.strip()) for x in select_mode.split(",") if x.strip()})
        assert indices, f"select_mode 解析无有效行号: {select_mode}"
        rows = page.locator(".usm_virtual_row")
        total = rows.count()
        for idx in indices:
            assert 1 <= idx <= total, f"行号 {idx} 越界，当前共 {total} 行(可选 1~{total})"
            row_cb = rows.nth(idx - 1).locator(".ant-checkbox-wrapper").first
            row_cb.scroll_into_view_if_needed()
            if not _is_checked(row_cb):
                row_cb.click()
                page.wait_for_timeout(300)
        expected = len(indices)

    # 校验选中数量
    page.wait_for_timeout(500)
    count_text = page.locator(".checked_count").first.text_content()
    assert f"选中{expected}项" in count_text, \
        f"勾选后选中数量不符，期望 选中{expected}项，实际 {count_text}"


@step("点击删除选中资产")
def click_delete_asset():
    """
    description: 点击工具栏删除按钮弹出批量删除确认框。删除第2步，必须。
                 依赖前一步已勾选资产(0选中点删除只会提示"未选择条目")。
    """
    page = data_store.suite["page"]
    # 工具栏删除按钮(与 启用/禁用/更多 同级，exact 避免误匹配)
    page.get_by_role("button", name="删除", exact=True).click()
    page.wait_for_timeout(800)
    # 用"批量删除"文本过滤定位弹窗(Ant Design 可能残留其它隐藏 modal)
    modal = page.locator(".ant-modal-content").filter(has_text="批量删除").last
    modal.wait_for(state="visible", timeout=5000)
    assert "批量删除" in modal.text_content(), "弹窗标题非'批量删除'"


@step("确认删除资产")
def confirm_delete_asset():
    """
    description: 在批量删除确认框点确定执行删除。删除第3步，必须。断言弹窗已关闭(visibility)。
    """
    page = data_store.suite["page"]
    modal = page.locator(".ant-modal-content").filter(has_text="批量删除").last
    modal.wait_for(state="visible", timeout=5000)
    modal.get_by_role("button", name="确 定").click()
    # Ant Design 关闭后 modal-wrap 残留(display:none), count 不归零, 改用 visibility 判定
    modal.wait_for(state="hidden", timeout=8000)


@step("验证资产删除成功<asset_name>")
def verify_asset_deleted(asset_name):
    """
    description: 按资产名称搜索确认已从列表删除。删除第4步，必须。
                 搜索无结果(共0条/暂无数据/空表格)即视为删除成功。
    params:
        - asset_name: 必填|文本|任意文本，删除前使用的资产名称
    """
    page = data_store.suite["page"]
    # 用资产名称搜索框精确定位
    page.get_by_role("textbox", name="资产名称").fill(asset_name)
    page.get_by_role("button", name="查询").click()
    page.wait_for_timeout(1500)

    # 空结果检测：分页0条 / .ant-empty / 虚拟表格"暂无数据" 任一命中即删除成功
    pagination = page.locator(".ant-pagination-total-text")
    if pagination.count() > 0 and "共0条" in pagination.first.text_content():
        return

    if page.locator(".ant-empty").count() > 0:
        return

    virtual_body = page.locator(".usm_virtual_body")
    if virtual_body.count() > 0 and "暂无数据" in virtual_body.first.text_content():
        return

    # 仍有数据行 -> 检查是否还能找到该资产名称
    row = page.locator(".usm_virtual_row").filter(has_text=asset_name).first
    assert not row.is_visible(), \
        f"资产 {asset_name} 删除失败：列表中仍能找到该资产"
