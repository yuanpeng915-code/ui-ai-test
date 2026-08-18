# step_impl生成规则

> 所有step_impl 的step文件遵守本规则

## **文件组织(重要):**
- **一个功能一个 py**,按功能命名(如 `create_user.py`、`login.py`),不要把多个功能塞进一个大文件。
- **文件按路由 L2/L3 建英文目录**:从 `configs/router.json` 取目标页的 `一级-二级-三级` 名称,把 L2/L3 翻译为英文。文件放 `step_impl/<L2>/<L3>/<功能>.py`;无 L3 则 `step_impl/<L2>/<功能>.py`。示例:`管理控制台-用户-用户管理`→L2=user, L3=management → `step_impl/user/management/create_user.py`;登录页无路由条目 → `step_impl/auth/login.py`。每层目录放 `__init__.py`(Gauge 用 `python -m` 跑时需要是包)。

## **文件description规则**

存放在**文件顶部**,包含以下4个元素组成
- description：整个文件步骤实现什么样的功能（20字以内）
- route：页面路由,如 `/index/#/index/manage/user/user`
- steps：包含的所有step，以及调用顺序和必选性例如：
         1. step("aaa")   【必须】
         2. step("bbb")   【可选】
         3. step("ccc")   【可选】
         4. step("ddd")   【必须】
- remark：步骤调用备注信息（部分步骤依赖前面步骤调用）例如：`步骤2`参数传入`xxxx模板`需要执行`步骤3`

例如
```python
"""
description:在 用户-用户管理 页新建一个用户
route: /index/#/index/manage/user/user
steps:
  1. @step("打开新建用户页面")          【必须】
  2. @step("填写用户基本信息 <table>")  【必须】
  3. @step("填写用户安全配置 <table>")  【可选】
  4. @step("填写用户更多信息 <table>")  【可选】
  5. @step("保存新建用户<save>")        【必须】
remark：
  1.安全配置如果`status=启用`则需要填写更多信息
"""
from getgauge.python import step, data_store
from utils.parser import table_to_dict
```


## **方法内部description规则

存放在**step方法内部**
- description：这个方法做什么 + 何时调用它(第几步)
- params和tableparams(gauge table参数): 参数按照`是否必填|传入格式|选项参数`格式进行生成，其中`传入格式`和`选项参数`按下表规则
|对应页面元素|传入格式|选项参数|
|-----------|--------|-------|
|勾选框|是/否|是/否|
|文本参数|文本|任意文本|
|下拉框单选|文本|页面中下拉框中的所有选项文本|
|下拉框多选|文本1,文本2|页面中下拉框中的所有选项文本|
|文件参数|文本|文本|
|选择按钮|文本|页面上`可点击`的所有选项|
(备注：其它未提到的默认为文本参数)
  
例如
```python
@step("登录堡垒机账号<username>密码<password>")
def login_bastion(username, password):
    """
    description:在登录页输入账号密码并登录,进入运维系统需先调用。用户未给凭据时,可参考 assets.json 的 bastion_admin
    params:
        - username:必填|文本|任意文本
        - password:必填|文本|任意文本
    """
    pass


@step("填写用户基本信息 <table>") # 参数过多聚合成gauge table
def fill_user_basic(table):
    """
    description:在新建用户抽屉填基本信息段。新建用户第2步,必须。角色/部门/认证源留空则用页面默认(普通用户/root/本地认证)
    tableparams:
        - username:必填|文本|任意文本
        - role:必填|文本|超级管理员/系统管理员/安全管理员/安全审计员/....     # 页面实际为单选下拉框,列出所有选择
        - auth_source:非必填|文本1,文本2|本地认证/LDAP/网络认证...          # 页面为多选下拉框，列出所有选择
        - must_change_pwd:非必填|是/否|是/否
        - template：必填|文本|选项1/选项2/选项3/                            # 页面为选择按钮，列出所有选项 
    """
    pass
```