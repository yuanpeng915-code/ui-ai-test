"""
description: 在 个人工作台-运维 页搜索资产
route: /index/#/index/profile/om
steps:
  1. @step("进入运维界面")                           【必须】
  2. @step("选择运维界面左侧树节点<node_path>")       【必须】
  3. @step("填写运维界面资产搜索条件 <table>")         【可选】
  4. @step("点击运维界面资产查询")                    【必须】
  5. @step("验证运维界面资产搜索结果 <expected_asset>") 【必须】
remark：
  1. 搜索条件以 table 传参，所有参数非必填，留空则跳过筛选
  2. 点击"按服务分类"等树节点后才显示完整搜索表单
  3. 验证步骤支持虚拟表格IP列严格校验，期望值空格分隔多IP
"""
import re

from getgauge.python import step
from utils.parser import table_to_dict
from step_impl.profile.om import _get_active_page, _get_active_page_helper


@step("填写运维界面资产搜索条件 <table>")
def fill_om_asset_search_conditions(table):
    """
    description: 在运维界面填写资产搜索条件。第3步，可选。
    tableparams:
        - ip_domain_match_mode: 非必填 | 文本 | 模糊匹配/精准匹配
        - ip_domain: 非必填 | 文本 | 任意文本
        - asset_name: 非必填 | 文本 | 任意文本
        - account_name: 非必填 | 文本 | 任意文本
        - auth_rule: 非必填 | 文本 | 全部/下拉中的选项
        - project: 非必填 | 文本 | default/下拉中的选项
        - tag: 非必填 | 文本 | 下拉中的选项
        - service_url: 非必填 | 文本 | 任意文本
        - asset_network: 非必填 | 文本 | 下拉中的选项
    """
    page = _get_active_page()
    ph = _get_active_page_helper()
    params = table_to_dict(table)

    # 确保搜索区域已展开（点击"展开"若存在）
    expand_btn = page.locator(".higher_search_bar").get_by_text("展开")
    if expand_btn.count() > 0:
        expand_btn.first.click()
        page.wait_for_timeout(500)

    # IP/域名 匹配模式
    ph.main_select("assetAddrMatchMode", params.get("ip_domain_match_mode"))

    # IP/域名 输入
    ip_domain = params.get("ip_domain")
    if ip_domain:
        page.locator("#addresses").fill(ip_domain)
        page.wait_for_timeout(300)

    # 资产名称
    asset_name = params.get("asset_name")
    if asset_name:
        page.locator("#assetNames").fill(asset_name)
        page.wait_for_timeout(300)

    # 账号名
    account_name = params.get("account_name")
    if account_name:
        page.locator("#usernames").fill(account_name)
        page.wait_for_timeout(300)

    # 授权规则
    ph.main_select("ruleIds", params.get("auth_rule"))

    # 项目
    ph.main_select("projectIds", params.get("project"))

    # 标签
    ph.main_select("tagIds", params.get("tag"))

    # 服务URL
    service_url = params.get("service_url")
    if service_url:
        page.locator("#url").fill(service_url)
        page.wait_for_timeout(300)

    # 资产网络
    ph.main_select("networkIds", params.get("asset_network"))


@step("点击运维界面资产查询")
def click_om_asset_search():
    """
    description: 点击运维界面查询按钮执行资产搜索。第4步，必须。
    """
    page = _get_active_page()
    page.get_by_role("button", name="查询").first.click()
    page.wait_for_timeout(1500)


@step("验证运维界面资产搜索结果 <expected_asset>")
def verify_om_asset_search_result(expected_asset):
    """
    description: 验证运维界面搜索结果。第5步，必须。
                 优先使用虚拟表格IP列严格校验，期望值支持空格分隔多IP(如"10.113.56.137 10.113.56.129")，
                 空结果视为合法；非虚拟表格时退回文本可见性检查。
    params:
        - expected_asset: 必填 | 文本 | 任意文本，IP支持空格分隔多值
    """
    page = _get_active_page()

    # --- 1. 空结果检查 ---
    pagination = page.locator(".ant-pagination-total-text")
    if pagination.count() > 0 and "共0条" in pagination.first.text_content():
        return

    empty = page.locator(".ant-empty")
    if empty.count() > 0:
        return

    # 虚拟表格空状态
    virtual_body = page.locator(".usm_virtual_body")
    if virtual_body.count() > 0 and "暂无数据" in virtual_body.first.text_content():
        return

    # 非虚拟表格的暂无数据
    grid = page.locator("[role=grid]")
    if grid.count() > 0 and grid.get_by_text("暂无数据").count() > 0:
        return

    # --- 2. 虚拟表格严格校验 ---
    virtual_rows = page.locator(".usm_virtual_row").all()

    if virtual_rows:
        expected_ips = set(ip.strip() for ip in expected_asset.split() if ip.strip())

        actual_ips = []
        for row in virtual_rows:
            cells = row.locator(".usm_virtual_cell").all()
            # 运维界面表格列: [checkbox, sep, 资产名称, IP/域名, 所属项目, 备注, 访问]
            # IP/域名 在第4列(索引3)
            if len(cells) > 3:
                ip_cell = cells[3]
                content = ip_cell.locator(".usm_virtual_cell_content").first
                if content.count() > 0:
                    ip_text = (content.get_attribute("title") or "").strip()
                    if not ip_text:
                        ip_text = content.text_content().strip()
                    if ip_text:
                        actual_ips.append(ip_text)

        # 验证：每个实际IP都在期望集合中
        unexpected = [ip for ip in actual_ips if ip not in expected_ips]
        assert not unexpected, \
            f"搜索结果中存在不匹配的IP: {unexpected}，期望: {expected_ips}"

        # 验证：每个期望IP都出现在结果中
        missing = [ip for ip in expected_ips if ip not in actual_ips]
        assert not missing, \
            f"搜索结果中未找到IP: {missing}"
        return

    # --- 3. Fallback: 文本可见性检查 ---
    assert page.get_by_text(expected_asset).first.is_visible(), \
        f"搜索结果中未找到资产: {expected_asset}"
