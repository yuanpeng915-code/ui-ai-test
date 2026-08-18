"""
description: H5运维终端操作
route: /webclient/index/ (H5运维新窗口)
steps:
  1. @step("获取H5运维页面")                        【必须】
  2. @step("断言H5 tab名称<name>")                 【可选】
  3. @step("H5终端输入<text>回车提交<submit>")      【必须】
  4. @step("H5终端粘贴<text>回车提交<submit>")      【必须】
  5. @step("H5运维页面访问URL<url>")               【可选】
  6. @step("关闭H5 tab会话<mode>")                 【可选】
remark：
  1. H5 运维页面由发起运维连接触发 window.open 打开在新 tab
  2. 需先调用"获取H5运维页面"将 page 存入 data_store.suite["h5_page"]
  3. close_h5_tabs('all') 会关闭当前 H5 页面本身
  4. 终端使用 xterm.js，步骤3走 keyboard.type 模拟真实键入
  5. 步骤4走 keyboard.insert_text 一次性粘贴，规避RDP运维时输入法(IME)导致输入异常
"""
from getgauge.python import step, data_store
import time
from step_impl.profile.om import _get_active_page


def _get_h5_page():
    """从 suite 取 h5_page，不存在则自动查找 webclient tab"""
    if "h5_page" in data_store.suite:
        return data_store.suite["h5_page"]
    page = _get_active_page()
    # 新 tab 可能还在打开中，轮询等一等
    for _ in range(10):
        pages = [p for p in page.context.pages if '/webclient/' in p.url]
        if pages:
            data_store.suite["h5_page"] = pages[-1]
            return data_store.suite["h5_page"]
        page.wait_for_timeout(500)
    assert False, "未找到 H5 运维页面，请先调用发起运维连接"


@step("获取H5运维页面")
def get_h5_page():
    """
    name: 获取H5运维页面
    description: 发起运维连接后调用，从 context 中获取 webclient H5 运维 page 并存入 suite。后续 H5 操作的前置步骤，必须。
    params: 无
    """
    _get_h5_page()


@step("断言H5 tab名称<name>")
def assert_h5_tab_name(name):
    """
    name: 断言H5 tab名称
    description: 断言 H5 运维页面左上角当前选中 tab 的名称包含预期值。第2步，可选。仅在需要验证 tab 名称时调用。
    params:
        - name: 必填 | 文本 | 预期 tab 名称(如 usm@10.113.76.175/SSH)
    """
    h5_page = _get_h5_page()
    tab = h5_page.get_by_role('tab', selected=True)
    assert tab.is_visible(), "未找到选中的 tab"
    actual = tab.text_content().strip()
    assert name in actual, f"Tab 名称不匹配: 期望包含 '{name}', 实际 '{actual}'"


@step("H5终端输入<text>回车提交<submit>")
def type_h5_terminal(text, submit):
    """
    name: H5终端输入
    description: 聚焦 H5 运维终端并模拟真实键入文本，可选是否回车提交。第3步，必须。可多次调用输入多条命令。
    params:
        - text: 必填 | 文本 | 要输入的文本(如 uname -a、ls -la)
        - submit: 必填 | 勾选框 | True(回车提交)/False(只输入不回车)
    """
    h5_page = _get_h5_page()
    term = h5_page.get_by_role('textbox', name='Terminal input')
    term.click()
    h5_page.wait_for_timeout(200)
    h5_page.keyboard.type(text, delay=80)
    if submit in ('True', 'true', '是'):
        h5_page.keyboard.press('Enter')
    h5_page.wait_for_timeout(500)


@step("H5终端点击X<x>Y<y>粘贴<text>回车提交<submit>")
def paste_h5_terminal(x,y,text, submit):
    """
    name: H5终端粘贴
    description: 使用粘贴方式输入文本到 H5 运维终端，可选是否回车提交。第4步，与步骤3二选一。
                 chrome运维浏览器网址输入框坐标800, 100。
    params:
        - text: 必填 | 文本 | 要粘贴的文本(如 uname -a、ls -la)
        - submit: 必填 | 勾选框 | True(回车提交)/False(只粘贴不回车)
        - x: 非必填 | 数字 | 终端区域点击x坐标(像素)，不传则不点击直接粘贴
        - y: 非必填 | 数字 | 终端区域点击y坐标(像素)，不传则不点击直接粘贴
    """
    page = _get_h5_page()
    if x != "" and y != "":
        page.mouse.click(int(x), int(y))
        page.wait_for_timeout(200)
    time.sleep(2)  # 粘贴前稍等，避免粘贴过快导致终端未聚焦
    page.keyboard.insert_text(text)
    if submit in ('True', 'true', '是'):
        page.keyboard.press('Enter')
    page.wait_for_timeout(500)


@step("H5运维页面访问URL<url>")
def navigate_h5_page(url):
    """
    name: H5运维页面访问URL
    description: 在 H5 运维页面中直接导航到指定 URL。适用于 HTTP/B/S 类型资产，
                 通过浏览器地址栏导航来触发 ping 验证等操作。
    params:
        - url: 必填 | 文本 | 目标 URL(如 http://10.113.56.129:5000/sshCheck/ping)
    """
    h5_page = _get_h5_page()
    h5_page.goto(url, wait_until="domcontentloaded")
    h5_page.wait_for_timeout(3000)


@step("关闭H5 tab会话<mode>")
def close_h5_tabs(mode):
    """
    name: 关闭H5 tab会话
    description: 点击右上角"..."按钮，在菜单中关闭其他或所有 tab 会话。最后一步，可选。
    params:
        - mode: 必填 | 下拉框选择 | other(关闭其他)/all(关闭所有)
    """
    h5_page = _get_h5_page()
    # 点 "..." 打开菜单
    h5_page.get_by_role('button', name='图标: ellipsis').click()
    h5_page.wait_for_timeout(500)

    btn_label = '关闭其他会话' if mode == 'other' else '关闭所有'
    btn = h5_page.get_by_role('button', name=btn_label)
    assert btn.is_visible(), f"未找到按钮: {btn_label}"
    btn.click()
    h5_page.wait_for_timeout(500)
