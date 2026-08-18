---
name: usm-v9-case-gen
description: 公司专用(明御运维安全管理系统 / USM V9 堡垒机) Gauge Spec 用例生成 skill。从已有 step_impl 步骤白名单中自动组合生成 .spec 用例文件。当用户要生成XX用例、写XX的spec、组合XX测试场景时使用。
context：fork
---

# USM V9 Gauge Spec 用例生成

> 本 skill 服务于 **明御运维安全管理系统 / USM V9 堡垒机** 前端自动化测试。
> 核心职责：从 `step_impl/` 已有步骤白名单中，按用户意图自动组合生成 `.spec` 用例文件。
> **绝不凭空捏造 step**，所有 step 文案必须与 `step_impl/` 中 `@step("...")` 装饰器内的文案完全一致。
> 笔记内容参考`note/README.md`

## 工作流程

总流程：**解析用户意图 → 构造测试步骤 → 参数校验与端侧组装 → 生成验证脚本并逐阶段验收**。

### 阶段 1: 解析用户意图

根据用户输入信息提取用例涉及的模块，并按照调用顺序进行初步整理

| 序号 | 模块 | 操作 | 参数约束 |
|------|------|--------|------|
| 1    |模块1 | 创建xxx |无 |
| 2    |模块2 | 授权xxx |授权指定xxx |
| 3    |模块1 | 删除 |删除指定xxx |

例如
```
用户输入：创建user1并为他创建window资产

| 序号 | 步骤模块 | 操作 | 参数约束 |
|------|------|------|--------|
| 1 | user| 创建用户user1 | |
| 2 |asset|创建资产window|指定user1|
| 3 | user| 删除user1 | |
```

根据拆解的步骤表，检索已有用例细化操作：
- 扫描对应`specs/<L2>/` 下所有 `.spec` 文件，查看每个spec用例的内容
- 匹配与当前意图（模块 + 操作类型）相关的已有用例，标注为参考来源
- 同时读取 `notes/<模块名>.md` 沉淀笔记，获取标准流程模板和已知坑位
- 端测判断：更具模块判断操作步骤是用户端还是管理端

完成后，输出**模块规划表** 例如
| 步骤模块 | 操作 |端侧| 其它约束 |
|------|------|----|----|
| user| 创建user1用户|管理端|无|
| asset|创建window资产|管理端|指定user1，资产为window |
| usercheck|登录用户验证|用户端|登录user1 |
| user| 删除user1用户|管理端|无|


### 阶段 2: 构造步骤（白名单匹配 + 测试数据）

按`模块规划表`，为每个**步骤模块** **同步启动 `steps-matcher` Agent**，各自独立完成 step 用例步骤生成与测试数据构造：

### 阶段 3: 参数校验与端侧组装

汇总阶段 2 的所有 agent 输出，按照`模块规划表`顺序进行汇总,依次执行以下检查：

1. **参数引用检查**：汇总后先检查步骤间的参数引用链，确保下游步骤的参数值与上游步骤的输出一致：
   - 识别跨步骤引用关系：如"授权资产"步骤的 `user` 参数应引用上文"新建用户"步骤的 `username`，`asset` 参数应引用"新建资产"步骤的 `asset_name`
   - 统一参数值：发现不一致时，以上游步骤的值为准，覆盖下游
   - 典型引用链示例：`新建用户(username=autotest_0714) → 新建资产(asset_name=autotest_asset_0714) → 授权(user=autotest_0714, asset=autotest_asset_0714) → 删除(user=autotest_0714, asset=autotest_asset_0714)`
2. **步骤引用检测**：每个步骤必须存在，若出现不存在的步骤则告知用户结束用例生成

### 阶段 4: 生成验证脚本并逐阶段验收


根据汇总的整个步骤列表，生成测试验收脚本到`temp`目录下：

1. **生成两个脚本**：
   - `test_<名称>_verify.py` — 分阶段验证脚本，每个阶段一个独立函数，步骤导入放到方法内
   - `test_<名称>_cleanup.py` — 数据清理脚本，删除本次用例创建的所有测试数据

2. **verify脚本结构规范**：
   - 直接导入step_impl模块下对应的step组装函数转化
   - 每个模块写一个方法命名为 `stage{步骤编号}_{模块名称}` 例如:`def stage1_create_user()`
   - table 参数使用MockTable类进行模拟
   ```python
   class MockTable:
   """桥接 Gauge Table 对象，使 step_impl 函数在 standalone 脚本中可用"""
   def __init__(self, data: dict):
      self.headers = list(data.keys())
      self.rows = [[data[k] for k in self.headers]]
   ```
   - 按业务阶段拆分为独立函数，如 `stage1_create_user()` / `stage2_create_asset()` / `stage3_authorize()` / `stage4_verify_user()`

   例如：
   ```python
   from getgauge.python import data_store
   from step_impl.hooks import init_test_env, quit_driver

   class MockTable:
   """桥接 Gauge Table 对象，使 step_impl 函数在 standalone 脚本中可用"""
      def __init__(self, data: dict):
         self.headers = list(data.keys())
         self.rows = [[data[k] for k in self.headers]]

   def stage1_create_user():
       from step_impl.user.management.create_user import *
       cureat_user(user=user1,passwd="123456")  #对应@setp("创建指定用<user>密码<pass>")
       fill_user_info(MockTable({"age":"18", "phone":"15811111111"})) #对应step("填写用户信息<table>")
       ....

   def stage2_create_asset():
       from step_impl.asset.management.create_asset import *
       ....
   ```

4. **逐阶段验收流程**（主 agent 执行）：
   先全量运行，如果中途报错，则注释之前通过stage，**先清理当前阶段的数据**（调用 cleanup 脚本中对应函数），修复脚本后**从当前阶段重新执行**
   - 所有阶段通过后 → **运行 cleanup 脚本清理全部数据** → **取消所有注释，完整从头跑一遍**作为最终验收

5. **cleanup 脚本**：独立的 `<名称>_cleanup.py`，按逆序清理（授权 → 资产 → 用户），每个资源独立 try/except 保证部分清理成功不影响其他。

### 阶段 5: 输出 .spec 文件

**文件路径**：`specs/<L2>/P<优先级>_<名称>.spec`

**文件内容格式**：
执行步骤 + Tear-down清理

```markdown
# <用例标题（中文，≤20字）>

## P<0|1|2>-<名称>
* <step 1 的 Gauge 文案>
* <step 2 的 Gauge 文案> <参数>
* <step 3 的 Gauge 文案>
|<表头1>|<表头2>|
|<值1>  |<值2>  |
___
* 清理1
* 清理2
```

**命名规则**：
- 用例名称由用户指定 → 直接用
- 用户未指定 → AI 根据意图概括，≤10 字
- 示例：`新建资产.spec`、`查询用户.spec`、`批量编辑资产.spec`

### 混合端侧示例（管理端 + 客户端）

**用户**：「创建资产并为user1授权，用户端验证该资产可见」

**AI 处理**：

1. 阶段1-解析意图：

| 序号 | 步骤模块 | 操作 | 参数约束 |
|------|------|------|--------|
| 1 | asset | 创建window资产 | |
| 2 | authority | 为user1授权 | 授权指定user1和资产 |
| 3 | profilecheck | 用户端验证资产可见 | 用户端 |

检索 `specs/asset/`、`specs/authority/`、`specs/profile/` 和对应 notes → 输出模块规划表：

| 步骤模块 | 操作 | 端侧 | 其它约束 |
|------|------|----|----|
| asset | 创建window资产 | 管理端 | 资产名/IP自动生成 |
| authority | 为user1授权该资产 | 管理端 | 指定user1，指定资产名(关联上游) |
| profilecheck | 登录user1验证资产 | 用户端 | 需启动用户浏览器，指定资产名(关联上游) |

2. 阶段2-构造步骤：并行 agent 匹配 step_impl 生成步骤表：

| 序号 | 步骤模块 | 端侧 | 步骤 | 参数 |
|------|------|------|----|----|
| 1 | asset | 管理端 | step("打开新建资产页面") | 无 |
| 2 | asset | 管理端 | step("选择资产模板<template>") | template: "Windows" |
| 3 | asset | 管理端 | step("填写资产信息<table>") | 见下方表1 |
| 4 | asset | 管理端 | step("维护资产账号<table>") | 见下方表2 |
| 5 | asset | 管理端 | step("资产向导导航<action>") | action: "confirm" |
| 6 | authority | 管理端 | step("打开授权规则创建页面") | 无 |
| 7 | authority | 管理端 | step("填写授权基本信息<table>") | name: autotest_auth_0714, user: user1 |
| 8 | authority | 管理端 | step("授权选择资产<asset_name>") | asset_name: autotest_win_0714 |
| 9 | authority | 管理端 | step("点击授权规则创建") | 无 |
| 10 | profilecheck | 用户端 | step("启动用户浏览器<user>密码<pwd>") | user: user1, pwd: 1qaz2wsx#EDC |
| 11 | profilecheck | 用户端 | step("用户端进入运维页面") | 无 |
| 12 | profilecheck | 用户端 | step("用户端选择运维分组<group>") | group: "根目录" |
| 13 | profilecheck | 用户端 | step("用户端验证资产可见<ip>") | ip: 10.113.76.175 |

3. 阶段3-校验组装：检查参数引用链（asset_name: autotest_win_0714 在 authority 和 profilecheck 间一致），按端侧排列：`管理端 step → 启动用户浏览器 → 用户端 step → ____ → 关闭用户浏览器 + 管理端清理`

4. 阶段4-生成验证脚本：`temp/test_混合授权验证_verify.py` + `temp/test_混合授权验证_cleanup.py`，逐阶段运行通过

5. 阶段5-输出 `specs/authority/P1_用户端验证授权资产.spec`：

```markdown
# 授权后用户端验证资产可见

## P1-创建授权并验证
* 打开新建资产页面
* 选择资产模板"Windows"
* 填写资产信息
|asset_name           |asset_ip     |os     |network |node   |
|autotest_win_0714    |10.113.76.175|Windows|default |yptest |
* 维护资产账号
|username     |password     |privileged|services|
|autotest_ac  |Autotest@2026|True      |RDP     |
* 资产向导导航"confirm"
* 打开授权规则创建页面
* 填写授权基本信息
|name             |user |
|autotest_auth_0714|user1|
* 授权选择资产"autotest_win_0714"
* 点击授权规则创建
* 启动用户浏览器"user1"密码"1qaz2wsx#EDC"
* 用户端进入运维页面
* 用户端选择运维分组"根目录"
* 用户端验证资产可见"10.113.76.175"
____
* 关闭用户浏览器
* 删除资产"autotest_win_0714"
* 删除用户"user1"
```
## 注意事项
- **一个spec文件 = 一条用例**：一个spec文件中只存放一个scenario,不要把多个scenario写在同一个spec文件中
- **用例的原子性**：一条用例不能与其他用例耦合，不能依赖其他用例的执行结果。每条用例都应该是独立的、可重复执行的。
- **环境清理**：每条用例执行完后，必须清理掉测试数据，保证环境干净。将删除步骤添加到Tear-down中


## 与其他 skill 的关系

- `usm-v9-fun-gen`：负责**沉淀新 step**（浏览器探索 → acceptance 脚本 → step_impl）
- `usm-v9-case-gen`（本 skill）：负责**组合已有 step** 生成 `.spec` 用例文件
- 依赖链：`usm-v9-fun-gen` 产出 step → 本 skill 消费 step 生成 spec
