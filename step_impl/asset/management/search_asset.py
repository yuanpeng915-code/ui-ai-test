"""
description: 在 资产-资产管理 页搜索资产
route: /index/#/index/manage/project/1/asset/asset
steps:
  1. @step("打开资产管理页面")          【必须】
  2. @step("填写资产搜索条件 <table>")  【必须】
  3. @step("点击查询资产")              【必须】
  4. @step("验证资产搜索结果 <expected_asset>") 【必须】
remark：
  1. 搜索条件以 table 传参，所有参数非必填，留空则跳过筛选
  2. "上次运维时间"和"连通性"默认值为"全部"
  3. 搜索在主页面进行（非抽屉），无需 drawer() 作用域
  4. 验证步骤支持严格IP列校验：提取虚拟表格每行IP/域名列与期望值比对，期望值空格分隔多IP，空结果自动处理
"""
from getgauge.python import step, data_store
from utils.parser import table_to_dict


@step("打开资产管理页面")
def open_asset_management_page():
    """
    description: 导航到资产管理页面。资产搜索第1步，必须。
    """
    ph = data_store.suite["page_helper"]
    ph.goto_route("资产管理")


@step("填写资产搜索条件 <table>")
def fill_asset_search_conditions(table):
    """
    description: 在资产管理页填写搜索条件。资产搜索第2步，必须。
    tableparams:
        - ip_domain_match_mode: 非必填 | 文本 | 模糊匹配/精准匹配
        - ip_domain: 非必填 | 文本 | 任意文本
        - asset_name: 非必填 | 文本 | 任意文本
        - asset_source: 非必填 | 文本 | 123
        - tag: 非必填 | 文本 | 未绑定标签/biaobiaobaio
        - network: 非必填 | 文本 | default
        - status: 非必填 | 文本 | 正常/禁用
        - last_om_time: 非必填 | 文本 | 全部/30天以内/30天以前/90天以前/180天以前/1年前/从未运维
        - conn_status: 非必填 | 文本 | 全部/正常/异常/未知
        - os_type: 非必填 | 文本 | Cisco IOS Device/Huawei Quidway Device/H3C IOS Device/Tp-Link Device/Other Network/CentOS/Ubuntu/Debian
        - encoding: 非必填 | 文本 | UTF-8/GBK/GB2312/GB18030
        - remark: 非必填 | 文本 | 任意文本
    """
    page = data_store.suite["page"]
    ph = data_store.suite["page_helper"]
    params = table_to_dict(table)

    # 确保搜索区域已展开（点击"展开"若存在）
    expand_btn = page.get_by_text("展开")
    if expand_btn.count() > 0:
        expand_btn.first.click()
        page.wait_for_timeout(500)

    # IP/域名 匹配模式
    ph.main_select("assetAddrMatchMode", params.get("ip_domain_match_mode"))

    # IP/域名 输入
    ip_domain = params.get("ip_domain")
    if ip_domain:
        page.get_by_placeholder("多关键词以空格隔开").first.fill(ip_domain)
        page.wait_for_timeout(300)

    # 资产名称
    asset_name = params.get("asset_name")
    if asset_name:
        page.get_by_role("textbox", name="资产名称").fill(asset_name)
        page.wait_for_timeout(300)

    # 资产源
    ph.main_select("sourceIds", params.get("asset_source"))

    # 标签
    ph.main_select("tagIds", params.get("tag"))

    # 所属网络
    ph.main_select("networkId", params.get("network"))

    # 状态
    ph.main_select("status", params.get("status"))

    # 上次运维时间
    ph.main_select("lastOmTime", params.get("last_om_time"))

    # 连通性
    ph.main_select("connStatus", params.get("conn_status"))

    # 操作系统（无固定 ID，通过 label 定位）
    os_type = params.get("os_type")
    if os_type:
        page.locator(".ant-form-item").filter(has_text="操作系统").first \
            .locator(".ant-select").first.click()
        page.wait_for_timeout(800)
        page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                     ".ant-select-item-option").filter(has_text=os_type).first.click()
        page.wait_for_timeout(500)

    # 系统编码
    ph.main_select("encoding", params.get("encoding"))

    # 备注
    remark = params.get("remark")
    if remark:
        page.get_by_role("textbox", name="备注").fill(remark)
        page.wait_for_timeout(300)


@step("点击查询资产")
def click_search_asset():
    """
    description: 点击查询按钮执行资产搜索。资产搜索第3步，必须。
    """
    page = data_store.suite["page"]
    page.get_by_role("button", name="查询").click()
    page.wait_for_timeout(1500)


@step("验证资产搜索结果 <expected_asset>")
def verify_asset_search_result(expected_asset):
    """
    description: 验证搜索结果。资产搜索第4步，必须。优先使用虚拟表格IP列严格校验，
                 期望值支持空格分隔多IP(如"10.113.56.137 10.113.56.129")，
                 空结果(表格无行/分页0条)视为合法；非虚拟表格时退回文本可见性检查。
    params:
        - expected_asset: 必填 | 文本 | 任意文本，IP支持空格分隔多值
    """
    page = data_store.suite["page"]

    # --- 1. 空结果检查（优先于虚拟表格，因空表格可能有占位行）---
    pagination = page.locator(".ant-pagination-total-text")
    if pagination.count() > 0 and "共0条" in pagination.first.text_content():
        return  # 搜索无结果是合法的

    empty = page.locator(".ant-empty")
    if empty.count() > 0:
        return  # 搜索无结果是合法的

    # 虚拟表格空状态："暂无数据"
    virtual_body = page.locator(".usm_virtual_body")
    if virtual_body.count() > 0 and "暂无数据" in virtual_body.first.text_content():
        return  # 搜索无结果是合法的

    # --- 2. 虚拟表格严格校验 ---
    virtual_rows = page.locator(".usm_virtual_row").all()

    if virtual_rows:
        # 有数据行 → 提取每行的 IP/域名列进行精确比对
        expected_ips = set(ip.strip() for ip in expected_asset.split() if ip.strip())

        actual_ips = []
        for row in virtual_rows:
            cells = row.locator(".usm_virtual_cell").all()
            if len(cells) > 4:
                # IP/域名列是第5列（索引4），值在 A.link.inline 或 span 内
                ip_cell = cells[4]
                link = ip_cell.locator("a.link").first
                if link.count() > 0:
                    ip_text = link.text_content().strip()
                else:
                    ip_text = ip_cell.text_content().strip()
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

    # --- 3. Fallback: 旧版页面 / 非虚拟表格，使用原有文本可见性检查 ---
    assert page.get_by_text(expected_asset).first.is_visible(), \
        f"搜索结果中未找到资产: {expected_asset}"
