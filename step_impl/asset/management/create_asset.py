"""
description: 在 资产-资产管理 页新建资产
route: /index/#/index/manage/project/1/asset/asset
steps:
  1. @step("打开新建资产页面")                【必须】
  2. @step("选择资产模板<template>")          【必须】
  3. @step("填写资产信息 <table>")            【必须】
  4. @step("新建或修改资产账号 <table>")      【可选】
  5. @step("保存新建资产")                    【必须】
  6. @step("验证新建资产成功<asset_name>")    【必须】
remark：
  1. 步骤2模板决定步骤3操作系统可选项与默认值(如Linux模板默认Other Linux)
  2. 步骤4可选，默认已有root(SSH)账号，不需额外建账号时可跳过
  3. 步骤4 action=新建时account_name为新账号名；action=修改时为已有账号名(如root)，用于定位行点编辑
  4. 所属网络/所在目录/标签为动态加载下拉，留空保留默认(default/根目录/空)
  5. 步骤2模板=B/S时，步骤3资产信息含三个折叠面板(基本信息/服务信息/更多信息)，需额外填「服务信息」面板：
     传 table 的 url 参数即触发服务信息填写(URL必填)，其余服务信息字段均非必填留默认；
     B/S 模板步骤4无默认账号(暂无数据)，不需建账号时直接跳过步骤4
"""
from getgauge.python import step, data_store
from utils.parser import table_to_dict


@step("打开新建资产页面")
def open_create_asset_page():
    """
    description: 导航到资产管理页并点击新建按钮打开抽屉。新建资产第1步，必须。
    """
    page = data_store.suite["page"]
    ph = data_store.suite["page_helper"]
    ph.goto_route("资产管理")
    page.get_by_role("button", name="新建", exact=True).click()
    page.wait_for_timeout(1000)
    drawer = page.locator(".ant-drawer-content").last
    assert "新建资产" in drawer.text_content(), "新建资产抽屉未打开"


@step("选择资产模板<template>")
def select_asset_template(template):
    """
    description: 在新建资产抽屉选择模板并点下一步进入资产信息步骤。新建资产第2步，必须。
    params:
        - template: 必填|文本|Windows/Windows域控/Linux/Unix/Oracle/MySQL/SQL Server/DB2/PostgreSQL/Kingbase/DM/Gbase8a/Gbase8s/GaussDB/Redis/HighGo/Sybase/Cisco IOS/Huawei Quidway/H3C Comware/B/S
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    # 模板选项是 .c_box 内的 .b_icon，用 exact 避免误匹配(如 Windows vs Windows域控)
    drawer.locator(".c_box").get_by_text(template, exact=True).first.click()
    page.wait_for_timeout(500)
    active = drawer.locator(".b_icon.active").first
    assert active.count() > 0 and template in active.text_content(), \
        f"模板 {template} 未选中"
    drawer.get_by_role("button", name="下一步").click()
    page.wait_for_timeout(1000)
    assert drawer.locator("#name").is_visible(), "未进入资产信息步骤"


@step("填写资产信息 <table>")
def fill_asset_info(table):
    """
    description: 填写资产基本信息、服务信息(B/S模板)和更多信息后点下一步进入资产账号步骤。新建资产第3步，必须。
    tableparams:
        - asset_type: 非必填|文本|普通资产/认证中心节点/认证客户端节点
        - asset_name: 必填|文本|任意文本
        - ip_domain: 必填|文本|任意文本
        - os: 非必填|文本|CentOS/Ubuntu/Debian/Red Hat/Suse Linux/Open Suse/Aliyun Linux/Other Linux/SCO Unix(随模板变)
        - network: 非必填|文本|default(动态加载，默认default)
        - directory: 非必填|文本|根目录(动态加载目录树，默认根目录)
        - tag: 非必填|文本|biaobiaobaio(动态加载)
        - url: 非必填|文本|任意文本(HTTP/HTTPS服务URL，B/S模板必填，非B/S模板无此面板留空)
        - same_origin: 非必填|是/否|是/否(B/S同源限制开关，默认否)
        - url_filter_mode: 非必填|文本|黑名单/白名单(B/S URL过滤模式，默认黑名单)
        - url_filter: 非必填|文本|任意文本(B/S URL过滤内容)
        - special_url_whitelist: 非必填|文本|任意文本(B/S特殊URL白名单，多个换行分隔)
        - fill_script: 非必填|文本|任意文本(B/S代填脚本)
        - change_pwd_script: 非必填|文本|任意文本(B/S改密脚本)
        - remark: 非必填|文本|任意文本，最长500
    """
    page = data_store.suite["page"]
    ph = data_store.suite["page_helper"]
    params = table_to_dict(table)
    drawer = ph.drawer()

    # ---- 基本信息 ----
    # 资产类型 radio（默认普通资产，留空跳过）
    ph.antd_radio("资产类型", params.get("asset_type"))

    # 资产名称 (必填)
    asset_name = params.get("asset_name")
    assert asset_name, "asset_name 必填"
    drawer.locator("#name").fill(asset_name)
    page.wait_for_timeout(300)

    # IP/域名 (必填)
    ip_domain = params.get("ip_domain")
    assert ip_domain, "ip_domain 必填"
    drawer.locator("#address").fill(ip_domain)
    page.wait_for_timeout(300)

    # 操作系统 (下拉，默认随模板)
    ph.antd_select("操作系统", params.get("os"))

    # 所属网络 (下拉，默认 default)
    ph.antd_select("所属网络", params.get("network"))

    # 所在目录 (树形下拉，默认 根目录；非默认值时展开树选节点)
    directory = params.get("directory")
    if directory and directory != "根目录":
        drawer.locator(".ant-form-item").filter(has_text="所在目录").first \
            .locator(".ant-select").first.click()
        page.wait_for_timeout(500)
        dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").last
        dropdown.locator(".ant-select-tree-node-content-wrapper") \
            .filter(has_text=directory).first.click()
        page.wait_for_timeout(300)

    # 标签 (下拉)
    ph.antd_select("标签", params.get("tag"))

    # ---- 服务信息 (仅 B/S 模板，传入 url 即触发) ----
    url = params.get("url")
    if url:
        _fill_bs_service_info(page, drawer, params, url)

    # ---- 更多信息 ----
    # 备注 (textarea，在"更多信息"折叠面板内)
    remark = params.get("remark")
    if remark:
        if not drawer.locator("#remark").is_visible():
            drawer.locator(".ant-collapse-header").filter(has_text="更多信息").first.click()
            page.wait_for_timeout(300)
        drawer.locator("#remark").fill(remark)
        page.wait_for_timeout(300)

    # 点下一步进入资产账号步骤
    drawer.get_by_role("button", name="下一步").click()
    page.wait_for_timeout(1000)
    # 步骤指示器中"资产账号"始终可见，不能用作判据；改用步骤3独有的"确 定"按钮
    if not drawer.get_by_role("button", name="确 定").is_visible():
        errors = drawer.locator(".ant-form-item-explain-error").all_text_contents()
        assert False, f"未进入资产账号步骤，表单验证错误: {errors}"


def _fill_bs_service_info(page, drawer, params, url):
    """填写 B/S 模板独有的「服务信息」折叠面板。非 B/S 模板无此面板，仅由 fill_asset_info 在传入 url 时调用。"""
    # 确保服务信息面板已展开(URL 输入框不可见则点折叠头展开)
    url_input = drawer.locator("#serviceConfig_url")
    if not url_input.is_visible():
        drawer.locator(".ant-collapse-header").filter(has_text="服务信息").first.click()
        page.wait_for_timeout(300)

    # URL (必填)
    url_input.fill(url)
    page.wait_for_timeout(300)

    # 代填脚本 (textarea)
    fill_script = params.get("fill_script")
    if fill_script:
        drawer.locator("#serviceConfig_fillScript").fill(fill_script)
        page.wait_for_timeout(300)

    # 改密脚本 (textarea)
    change_pwd_script = params.get("change_pwd_script")
    if change_pwd_script:
        drawer.locator("#serviceConfig_changePassScript").fill(change_pwd_script)
        page.wait_for_timeout(300)

    # 同源限制 (switch，默认关闭)
    same_origin = params.get("same_origin")
    if same_origin:
        switch_el = drawer.get_by_role("switch", name="同源限制")
        is_on = "ant-switch-checked" in (switch_el.get_attribute("class") or "")
        if is_on != (same_origin == "是"):
            switch_el.click()
            page.wait_for_timeout(300)

    # 黑白名单 (radio，默认"(黑名单)不允许以下URL")
    url_filter_mode = params.get("url_filter_mode")
    if url_filter_mode:
        keyword = "黑名单" if "黑" in url_filter_mode else "白名单"
        drawer.locator(".ant-radio-wrapper").filter(has_text=keyword).first.click()
        page.wait_for_timeout(300)

    # URL 过滤内容 (无固定 ID，按 placeholder 子串定位)
    url_filter = params.get("url_filter")
    if url_filter:
        drawer.locator("[placeholder*='支持通配符匹配']").first.fill(url_filter)
        page.wait_for_timeout(300)

    # 特殊 URL 白名单 (textarea，多个换行分隔)
    special_url_whitelist = params.get("special_url_whitelist")
    if special_url_whitelist:
        drawer.locator("#serviceConfig_httpSpecialUrlWhitelist").fill(special_url_whitelist)
        page.wait_for_timeout(300)


@step("新建或修改资产账号 <table>")
def create_or_edit_asset_account(table):
    """
    description: 在资产账号步骤新建账号或修改已有账号(root)。新建资产第4步，可选。
                 action=新建点新建按钮开空表单；action=修改按account_name定位行点编辑。
                 默认已有root(SSH)账号，不需要额外操作时可跳过本步。
    tableparams:
        - action: 必填|文本|新建/修改
        - account_name: 必填|文本|新建=新账号名；修改=已有账号名(如root)
        - privileged: 非必填|是/否|是/否(特权账号勾选)
        - password: 非必填|文本|任意文本(密码)
        - tag: 非必填|文本|biaobiaobaio(动态加载)
        - service: 非必填|文本|SYSDEF/SSH/SFTP/RDP/TELNET/RLOGIN/VNC/FTP/HTTP/HTTPS/ORACLE(默认SSH)
        - ssh_key: 非必填|文本|动态加载(SSH密钥，留默认)
        - switch_from: 非必填|文本|动态加载(切换自，留默认)
        - change_pwd: 非必填|是/否|是/否(是否可改密，默认是)
        - use_priv_change_pwd: 非必填|是/否|是/否(使用特权账号改密勾选)
        - change_pwd_script: 非必填|文本|动态加载(改密脚本，留默认)
    """
    page = data_store.suite["page"]
    ph = data_store.suite["page_helper"]
    params = table_to_dict(table)
    drawer = page.locator(".ant-drawer-content").last  # 主资产抽屉

    action = params.get("action")
    account_name = params.get("account_name")
    assert action in ("新建", "修改"), f"action 仅支持 新建/修改，实际: {action}"
    assert account_name, "account_name 必填"

    if action == "新建":
        # 账号区的"新建"按钮(exact 避免误匹配外层"资产账号 新建"折叠头)
        drawer.get_by_role("button", name="新建", exact=True).click()
        page.wait_for_timeout(1000)
    else:
        # 按账号名在虚拟表格定位行，点编辑
        row = drawer.locator(".usm_virtual_row").filter(has_text=account_name).first
        assert row.is_visible(), f"未找到账号 {account_name} 的行"
        row.get_by_text("编辑", exact=True).first.click()
        page.wait_for_timeout(1000)

    # 账号表单抽屉已打开(此时最后一个 drawer 即账号表单)
    acc_drawer = ph.drawer()
    assert "资产账号" in acc_drawer.text_content(), "资产账号表单未打开"

    # 账号名
    acc_drawer.locator("#username").fill(account_name)
    page.wait_for_timeout(300)

    # 特权账号勾选(留空保留当前态)
    privileged = params.get("privileged")
    if privileged:
        ph.antd_checkbox("特权账号", privileged == "是")

    # 密码
    password = params.get("password")
    if password:
        acc_drawer.locator("#password").fill(password)
        page.wait_for_timeout(300)

    # 标签
    ph.antd_select("标签", params.get("tag"))

    # 应用于服务 (多选，默认 SSH；diff 模式按传入值增删)
    ph.antd_multi_select("应用于服务", "services", params.get("service"))

    # SSH密钥
    ph.antd_select("SSH密钥", params.get("ssh_key"))

    # 切换自
    ph.antd_select("切换自", params.get("switch_from"))

    # 是否可改密
    ph.antd_radio("是否可改密", params.get("change_pwd"))

    # 使用特权账号改密(留空保留当前态)
    use_priv = params.get("use_priv_change_pwd")
    if use_priv:
        ph.antd_checkbox("使用特权账号改密", use_priv == "是")

    # 改密脚本
    ph.antd_select("改密脚本", params.get("change_pwd_script"))

    # 确定保存账号
    acc_drawer.get_by_role("button", name="确 定").click()
    page.wait_for_timeout(1000)
    if page.locator(".ant-drawer-content").count() > 1:
        # 账号表单仍打开, 提取验证错误信息辅助排查
        errors = acc_drawer.locator(".ant-form-item-explain-error").all_text_contents()
        assert False, f"资产账号表单未关闭, 验证错误: {errors}"
    assert page.locator(".ant-drawer-content").count() == 1, "资产账号表单未关闭"


@step("保存新建资产")
def save_new_asset():
    """
    description: 点击确定保存新建资产。新建资产第5步，必须。
    """
    page = data_store.suite["page"]
    drawer = page.locator(".ant-drawer-content").last
    drawer.get_by_role("button", name="确 定").click()
    page.wait_for_timeout(2000)
    assert page.locator(".ant-drawer-content").count() == 0, \
        "新建资产抽屉未关闭，保存可能失败"


@step("验证新建资产成功<asset_name>")
def verify_create_asset_success(asset_name):
    """
    description: 回列表按资产名称搜索验证创建成功。新建资产第6步，必须。
    params:
        - asset_name: 必填|文本|任意文本，创建时用的资产名称
    """
    page = data_store.suite["page"]
    page.get_by_role("textbox", name="资产名称").fill(asset_name)
    page.get_by_role("button", name="查询").click()
    page.wait_for_timeout(1500)
    row = page.locator(".usm_virtual_row").filter(has_text=asset_name).first
    assert row.is_visible(), f"资产 {asset_name} 创建失败：列表中未找到"
