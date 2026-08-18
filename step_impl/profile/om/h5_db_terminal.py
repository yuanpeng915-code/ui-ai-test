"""
description: H5数据库运维终端操作
route: /webdbclient (H5数据库运维新窗口)
steps:
  1. @step("获取H5数据库运维页面")                          【必须】
  2. @step("H5数据库选择库<database>执行查询<sql>")         【必须】
  3. @step("H5数据库查看结果<index>验证查询结果<expected>") 【必须】
remark：
  1. H5 数据库运维页面由发起运维连接触发 window.open 打开在新 tab，URL 含 /webdbclient
  2. 需先调用"获取H5数据库运维页面"将 page 存入 data_store.suite["h5_db_page"]
  3. SQL 编辑器使用 CodeMirror，keyboard.type 无效，通过 CodeMirror API (setValue/getValue) 输入和读取
  4. 执行后底部生成"结果 N" tab（N 随执行次数递增），默认停留在"执行日志"，需点击"结果 N"切换查看结果
  5. 结果表格使用 ReactVirtualized 虚拟滚动 (.usm_virtual_row)
  6. 与 SSH 的 h5_terminal.py 不同：URL 是 /webdbclient 而非 /webclient，page 存 h5_db_page 而非 h5_page
"""
from getgauge.python import step, data_store
from step_impl.profile.om import _get_active_page


def _get_h5_db_page():
    """从 suite 取 h5_db_page，不存在则自动查找 webdbclient tab"""
    if "h5_db_page" in data_store.suite:
        return data_store.suite["h5_db_page"]
    page = _get_active_page()
    # 新 tab 可能还在打开中，轮询等一等
    for _ in range(10):
        pages = [p for p in page.context.pages if '/webdbclient' in p.url]
        if pages:
            data_store.suite["h5_db_page"] = pages[-1]
            return data_store.suite["h5_db_page"]
        page.wait_for_timeout(500)
    assert False, "未找到 H5 数据库运维页面，请先调用发起运维连接"


@step("获取H5数据库运维页面")
def get_h5_db_page():
    """
    name: 获取H5数据库运维页面
    description: 发起运维连接后调用，从 context 中获取 webdbclient H5 数据库运维 page 并存入 suite。后续 H5 数据库操作的前置步骤，必须。
    params: 无
    """
    _get_h5_db_page()


@step("H5数据库选择库<database>执行查询<sql>")
def h5_db_select_and_query(database, sql):
    """
    name: H5数据库选择库执行查询
    description: 在 H5 数据库运维页面选择数据库、输入 SQL 查询语句并执行。第2步，必须。
                 database 为空则跳过选择保留默认；执行后断言执行日志显示"成功"。
    params:
        - database: 非必填 | 文本 | 数据库下拉中的选项(如 t1/mysql/information_schema/performance_schema)
        - sql: 必填 | 文本 | 任意 SQL 查询语句(如 select txt from test;)
    """
    page = _get_h5_db_page()

    # 1. 选择数据库（#database 下拉）
    if database:
        sel = page.locator("#database").locator("..").locator("..")
        sel.click()
        page.wait_for_timeout(800)
        dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)")
        option = dropdown.locator(".ant-select-item-option").filter(has_text=database).first
        assert option.count() > 0, f"数据库下拉中未找到 '{database}'"
        option.click()
        page.wait_for_timeout(500)
        selected = sel.locator(".ant-select-selection-item").first.text_content().strip()
        assert database in selected, f"数据库选中失败: 期望含 '{database}', 实际 '{selected}'"

    # 2. 输入 SQL（CodeMirror API，keyboard.type 对 CodeMirror 无效）
    page.evaluate(
        "(sql) => { const cm = document.querySelector('.CodeMirror'); "
        "if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(sql); } }",
        sql,
    )
    page.wait_for_timeout(300)
    actual = page.evaluate(
        "() => { const cm = document.querySelector('.CodeMirror'); "
        "return cm && cm.CodeMirror ? cm.CodeMirror.getValue() : ''; }"
    )
    assert sql.strip() in actual.strip(), f"SQL 输入失败: 期望 '{sql}', 实际 '{actual}'"

    # 3. 点击执行按钮（type=submit，工具栏内唯一的提交按钮）
    page.locator("button[type='submit']").first.click()
    page.wait_for_timeout(2000)

    # 4. 断言执行日志显示成功（执行日志 tab 默认激活）
    log_panel = page.get_by_role("tabpanel", name="执行日志")
    log_text = log_panel.text_content() or ""
    assert "成功" in log_text, f"查询执行失败，执行日志未显示成功: {log_text[:200]}"


@step("H5数据库查看结果<index>验证查询结果<expected>")
def h5_db_view_and_verify_result(index, expected):
    """
    name: H5数据库查看结果验证查询结果
    description: 在 H5 数据库运维页面点击"结果 N" tab 查看查询结果，并验证预期值。第3步，必须。
                 index 为结果 tab 序号，与 SQL 查询 tab 一一对应（单个 SQL tab 时始终为 1，
                 多次执行更新同一"结果 N" tab 而非新增）；expected 为空则只验证结果表格非空。
    params:
        - index: 必填 | 数字 | 结果 tab 序号(如 1 对应"结果 1")，与 SQL 查询 tab 对应
        - expected: 非必填 | 文本 | 预期结果值(如 yes)，为空则只验证有结果返回
    """
    page = _get_h5_db_page()

    # 1. 点击"结果 N" tab
    tab_name = f"结果 {index}"
    tab = page.get_by_role("tab", name=tab_name, exact=True).first
    assert tab.is_visible(), f"未找到 '{tab_name}' tab"
    tab.click()
    page.wait_for_timeout(1500)

    # 2. 验证结果表格非空（取可见的虚拟行，执行日志面板隐藏后只剩结果表格行）
    all_rows = page.locator(".usm_virtual_row").all()
    visible_rows = [r for r in all_rows if r.is_visible()]
    assert len(visible_rows) > 0, "结果表格为空，无查询结果"

    # 3. 如果 expected 非空，验证值出现在结果中
    if expected and expected.strip():
        all_text = " ".join((r.text_content() or "") for r in visible_rows)
        assert expected in all_text, f"查询结果中未找到预期值 '{expected}', 实际: {all_text[:300]}"
