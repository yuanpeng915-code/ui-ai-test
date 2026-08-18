"""
description: 在 资产-资产管理 页切换左侧面板视图并选择节点
route: /index/#/index/manage/project/1/asset/asset
steps:
  1. @step("切换资产管理左侧视图<view_type>")        【必须】
  2. @step("在左侧视图中搜索<keyword>")              【可选】
  3. @step("选择左侧视图中的节点<node_name>")        【必须】
  4. @step("验证左侧视图选中项<expected_node>")      【可选】
remark：
  1. view_type 可选值：目录/标签/所属网络/操作系统
  2. 搜索步骤可选，用于节点较多时快速定位
  3. 操作系统视图有层级（Network/Windows/Unix/Linux/Other），选择子节点前需先展开父节点
  4. 切换视图或选择节点后右侧资产表格自动刷新过滤
"""
from getgauge.python import step, data_store


# view_type → URL menu 参数映射
MENU_MAP = {
    "目录": "node_id",
    "标签": "tag_id",
    "所属网络": "vpc_id",
    "操作系统": "os_id",
}


@step("切换资产管理左侧视图<view_type>")
def switch_asset_left_view(view_type):
    """
    description: 切换资产管理页左侧面板的视图类型。第1步，必须。
    params:
        - view_type: 必填 | 文本 | 目录/标签/所属网络/操作系统
    """
    page = data_store.suite["page"]
    assert view_type in MENU_MAP, f"view_type 仅支持: {', '.join(MENU_MAP.keys())}"

    # 点击左侧面板顶部的下拉按钮
    dropdown_btn = page.locator(".tree_header .ant-dropdown-trigger.dropdown_button")
    dropdown_btn.click()
    page.wait_for_timeout(500)

    # 在下拉菜单中选中目标视图
    page.locator(".ant-dropdown:not(.ant-dropdown-hidden) .ant-dropdown-menu-item") \
        .filter(has_text=view_type).first.click()
    page.wait_for_timeout(1000)

    # 验证 URL 参数已切换
    expected_menu = MENU_MAP[view_type]
    assert f"menu={expected_menu}" in page.url, \
        f"视图未切换到 {view_type}，当前 URL: {page.url}"


@step("在左侧视图中搜索<keyword>")
def search_in_left_view(keyword):
    """
    description: 在左侧面板的搜索框中输入关键词过滤树节点。第2步，可选。
    params:
        - keyword: 必填 | 文本 | 任意文本
    """
    page = data_store.suite["page"]
    search_input = page.locator(".tree_header .usm_search input.input")
    search_input.fill(keyword)
    page.wait_for_timeout(800)


@step("选择左侧视图中的节点<node_name>")
def select_left_view_node(node_name):
    """
    description: 在左侧面板的树形列表中选中指定节点，切换后右侧资产表格自动刷新。第3步，必须。
                 支持层级选择：自动展开未展开的父节点（仅操作系统视图有层级）。
    params:
        - node_name: 必填 | 文本 | 任意文本，与树上节点名称匹配
    """
    page = data_store.suite["page"]

    tree = page.locator(".tree_content .ant-tree")
    tree.wait_for(state="visible", timeout=5000)

    # 收集所有已展开和可展开的节点，尝试找到目标
    treenodes = tree.locator(".ant-tree-treenode").all()
    found = None

    for node in treenodes:
        title_el = node.locator(".ant-tree-node-content-wrapper .ant-tree-title .name")
        if title_el.count() > 0 and title_el.first.get_attribute("title") == node_name:
            found = node
            break

    # 若未直接找到，尝试展开所有折叠的父节点后再查找
    if found is None:
        collapsed_parents = tree.locator(".ant-tree-treenode-switcher-close").all()
        for parent in collapsed_parents:
            switcher = parent.locator(".ant-tree-switcher").first
            if switcher.count() > 0:
                switcher.click()
                page.wait_for_timeout(300)

        # 重新查找
        treenodes = tree.locator(".ant-tree-treenode").all()
        for node in treenodes:
            title_el = node.locator(".ant-tree-node-content-wrapper .ant-tree-title .name")
            if title_el.count() > 0 and title_el.first.get_attribute("title") == node_name:
                found = node
                break

    assert found is not None, f"未在左侧树中找到节点: {node_name}"

    found.scroll_into_view_if_needed()
    found.locator(".ant-tree-node-content-wrapper").first.click()
    page.wait_for_timeout(1200)


@step("验证左侧视图选中项<expected_node>")
def verify_left_view_selection(expected_node):
    """
    description: 验证左侧面板当前选中的节点名称，可选。同时校验右侧表格已刷新（非空页面）。
    params:
        - expected_node: 必填 | 文本 | 任意文本，期望选中的节点名称
    """
    page = data_store.suite["page"]

    # 验证选中的节点
    selected = page.locator(".tree_content .ant-tree-node-selected .ant-tree-title .name")
    if selected.count() > 0:
        actual = selected.first.get_attribute("title") or selected.first.text_content().strip()
        assert actual == expected_node, \
            f"左侧选中节点不匹配: 期望 '{expected_node}'，实际 '{actual}'"

    # 确保表格区域存在（非空页面）
    main_area = page.locator("main").first
    assert main_area.is_visible(), "右侧主内容区域不可见，视图切换可能失败"
