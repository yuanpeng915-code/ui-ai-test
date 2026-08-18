"""
description: 在 个人工作台-运维 页选择左侧树节点
route: /index/#/index/profile/om
steps:
  1. @step("进入运维界面")                         【必须】
  2. @step("选择运维界面左侧树节点<node_path>")     【必须】
remark：
  1. node_path 为空时默认点击"根目录"节点
  2. 支持多级逗号分隔，如"按服务分类,SSH"表示先展开"按服务分类"再点击"SSH"
  3. 节点支持所有左侧树：工单、按服务分类、继承管理员视图、自定义分组等
"""
from getgauge.python import step
from step_impl.profile.om import _get_active_page, _get_active_page_helper


@step("进入运维界面")
def enter_om_page():
    """
    description: 导航到个人工作台运维页面。左侧树操作第1步，必须。
    """
    ph = _get_active_page_helper()
    ph.goto_route("个人工作台-运维")


@step("选择运维界面左侧树节点<node_path>")
def select_om_tree_node(node_path):
    """
    description: 在运维界面左侧面板选择树节点。第2步，必须。
                 空字符串默认选"根目录"，逗号分隔支持多级路径，逐级展开后选中末级。
    params:
        - node_path: 必填 | 文本 | 空选根目录；逗号分隔多级如"按服务分类,SSH"
    """
    page = _get_active_page()

    # 解析路径：空 → 默认"根目录"
    if not node_path or not node_path.strip():
        node_names = ["根目录"]
    else:
        node_names = [n.strip() for n in node_path.split(",") if n.strip()]

    for i, name in enumerate(node_names):
        is_last = (i == len(node_names) - 1)

        treenode = _find_tree_node(page, name)
        assert treenode is not None, f"未在左侧树中找到节点: {name}"

        treenode.scroll_into_view_if_needed()
        page.wait_for_timeout(300)

        if is_last:
            # 末级节点：点击选中
            treenode.locator(".ant-tree-node-content-wrapper").first.click()
            page.wait_for_timeout(800)
        else:
            # 非末级节点：折叠则展开
            class_attr = treenode.get_attribute("class") or ""
            if "ant-tree-treenode-switcher-close" in class_attr:
                treenode.locator(".ant-tree-switcher").first.click()
                page.wait_for_timeout(600)


def _find_tree_node(page, name):
    """在所有 ant-tree 中按 title 匹配查找 treenode，找不到则展开所有折叠节点后重试。"""
    # 第一轮：直接在已渲染的节点中查
    treenodes = page.locator(".ant-tree-treenode").all()
    for node in treenodes:
        title_el = node.locator(".ant-tree-title .name")
        if title_el.count() > 0:
            title = title_el.first.get_attribute("title")
            if title == name:
                return node

    # 第二轮：展开所有折叠节点后重查
    collapsed = page.locator(".ant-tree-treenode-switcher-close").all()
    for cn in collapsed:
        sw = cn.locator(".ant-tree-switcher").first
        if sw.count() > 0:
            try:
                sw.click()
                page.wait_for_timeout(300)
            except Exception:
                pass

    treenodes = page.locator(".ant-tree-treenode").all()
    for node in treenodes:
        title_el = node.locator(".ant-tree-title .name")
        if title_el.count() > 0:
            title = title_el.first.get_attribute("title")
            if title == name:
                return node

    return None
