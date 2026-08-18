"""
description:
route :
steps:
remark:
"""
from getgauge.python import step, data_store
from utils.parser import table_to_dict

@step("<Gauge step 文案,参数用 <param> 包住>")
def action_name(param1, param2):
    """
    description:这个方法做什么 + 何时调用它(+ 第几步/必选性)
    params:
        - param1:是否必填|传入格式|选项参数
        - param2:是否必填|传入格式|选项参数
    """
    # 参数类型词表(可扩充):按钮点击 / 文本输入 / 下拉框选择 / 勾选框 / 单选 / 文件上传
    page = data_store.suite["page"]  # page从driver.page 替换为data_store.suite["page"]获取
    ph = data_store.suite["page_helper"] # PageHelper 从`data_store.suite["page_helper"]`获取


# 参数 >3 时:@step 用一个 <table>,签名只留 tables(dict),取值用 tables.get(...)
@step("<Gauge step 文案> <table>")
def action_with_table(tables):
    """
    description:这个方法做什么 + 何时调用它(+ 第几步/必选性)
    tableparams:
        - param1:是否必填|传入格式|选项参数
        - param2:是否必填|传入格式|选项参数
    """
    page = data_store.suite["page"]
    # 每个参数用 tables.get("参数名", 默认值) 取,没传的键兜默认
    # page.get_by_label("xxx").fill(tables.get("param1", ""))
    # antd_select("下拉标签", tables.get("param2", None))


# ================= 以下为非 step 方法(调试入口) =================
# create 类功能最后加一个最终校验 step(非必须):
@step("最终校验: 确认新建XXX成功<identifier>")
def verify_create_xxx(identifier=""):
    """
    description:回到列表页搜索 identifier,确认创建成功或发现重复。create 类功能最后一步,非必须
    params:
        - identifier:文本输入|无|创建时用的唯一标识(名称/用户名等)
    """
    page = data_store.suite["page"]
    # 1. 导航回列表页
    # goto_route("XXX-XXX管理")
    # 2. 搜索新创建的数据
    # page.get_by_placeholder("请输入名称").fill(identifier)
    # page.get_by_role("button", name="查询").click()
    # page.wait_for_timeout(1000)
    # 3. 判断结果
    # if page.get_by_text("已存在").first.is_visible():       # 重复
    #     return False
    # if page.get_by_text(identifier).first.is_visible():      # 成功
    #     return True
    # return None                                              # 不确定
