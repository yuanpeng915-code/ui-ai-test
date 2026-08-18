# Gauge 用例编写参考指南

> 基于 Gauge 官方文档整理，供 AI 编写 Gauge 测试用例时参考。

---

## 1. 概述

Gauge 是一个轻量级的跨平台测试自动化框架。测试用例以 **Markdown** 格式编写，存放在 `.spec` 或 `.md` 文件中。

**核心概念：**
- **Spec（规范）**：一个业务测试用例，描述需要测试的特定功能。
- **Scenario（场景）**：每个 Spec 可包含一个或多个 Scenario。
- **Step（步骤）**：每个 Scenario 由多个 Step 组成，Step 是测试执行的最小单元。

---

## 2. Spec 文件基本结构

```markdown
# Spec 标题（H1）

这是注释，纯文本不会被 Gauge 执行，用于增强可读性。

Tags: tag1, tag2, tag3

* 这是 Context Step（上下文步骤），在每个 Scenario 之前执行
* 另一个 Context Step

## Scenario 标题（H2）

Tags: scenario-tag

这是场景内的注释。

* Step 描述
* 另一个 Step 描述

---

## 另一个 Scenario 标题

* Step 描述

____
* 这是 Tear-down Step（拆卸步骤），在每个 Scenario 之后执行
* 另一个 Tear-down Step
```

**关键规则：**
- Spec 标题使用 `#`（H1 Markdown 语法）
- Scenario 标题使用 `##`（H2 Markdown 语法）
- Step 以 `*` 开头
- 不符合语法的纯文本被视为注释，不执行
- 标签以 `Tags:` 开头，用逗号分隔

---

## 3. 参数

### 3.1 简单参数

用双引号 `"` 括起来的值作为参数传递。

```markdown
* Search for product "Cup Cakes"
* Create a "gauge-java" project
* Write "100" line specification
```

保留字符（不能在步骤文本中使用）：`"`、`<`、`>`

### 3.2 动态参数

用尖括号 `<param>` 作为占位符，引用数据表的列值。

**在 Spec 级别定义数据表：**

```markdown
# Create projects

    | name      |
    |-----------|
    | Alice     |
    | Bob       |
    | Eve       |

## First scenario
* Say "hello" to <name>.

## Second scenario
* Say "namaste" to <name>.
```

以上场景会执行三次，每次对应数据表中的一行。

**在 Scenario 级别定义数据表：**

```markdown
# Search specification

## Vowel counts in multiple word

    |word   |vowel count|
    |-------|-----------|
    |Gauge  |3          |
    |Mingle |2          |
    |Snap   |1          |
    |GoCD   |1          |
    |Rhythm |0          |

* The word <word> has <vowel count> vowels.
```

> 规范和场景级别的表可以同时使用，实现嵌套执行循环。

### 3.3 表格参数

步骤中可以嵌入内联表格作为参数：

```markdown
* Create the following projects

    |project name | username  |
    |-------------|-----------|
    | Gauge java  | Daredevil |
    | Gauge ruby  | Iron Fist |
```

**内联表格中使用动态参数：**

```markdown
# Create projects

    |id | name |
    |---|------|
    |1  | john |
    |2  | mike |

## First scenario
* Create the following projects

    |project name | username |
    |-------------|----------|
    | Gauge java  | <name>   |
    | Gauge ruby  | <name>   |
```

### 3.4 特殊参数：File

读取文件内容并作为字符串参数传递给步骤。

语法：`<file:[value]>`

```markdown
* Verify email text is <file:email.txt>
* Check if <file:/work/content.txt> is visible
```

`[value]` 是相对于项目根目录的绝对或相对路径。

### 3.5 特殊参数：CSV

通过外部 CSV 文件传递表格值。

语法：`<table:[value]>`

```markdown
* Step that takes a table <table:data.csv>
* Check if the following users exist <table:/Users/john/work/users.csv>
```

CSV 文件格式：第一行为表头，后续行为行值。

```csv
Id,Name
1,The Way to Go On
2,Ivo Jay Balbaert
```

---

## 4. 标签（Tags）

标签用于筛选或搜索 Spec 和 Scenario。

```markdown
# Search specification
Tags: search, admin

## Successful search
Tags: successful
```

**多行标签**（需缩进）：

```markdown
# Login specification
Tags: login,
      admin, user-abc

## Successful login scenario
Tags: admin,
      login-success
```

> Spec 级别的标签会自动应用到其所有 Scenario。

---

## 5. Context Steps（上下文步骤）

在每个 Scenario 之前执行的步骤，用于设置前置条件。

```markdown
# Delete project

* User is logged in as "mike"
* Navigate to the project page

## Delete single project
* Delete the "example" project
* Ensure "example" project has been deleted

## Delete multiple projects
* Delete all the projects in the list
* Ensure project list is empty
```

执行顺序：Context Steps → Scenario → Context Steps → Next Scenario → ...

---

## 6. Tear-down Steps（拆卸步骤）

在每个 Scenario 之后执行的步骤，用于清理操作。以三个以上连续下划线 `___` 开头。

```markdown
# Delete project

* Sign up for user "mike"
* Log in as "mike"

## Delete single project
* Delete the "example" project
* Ensure "example" project has been deleted

____________________
* Logout user "mike"
* Delete user "mike"
```

执行流程：Context → Scenario → Tear-down → Context → Next Scenario → Tear-down → ...

---

## 7. Concepts（概念）

将可复用的逻辑步骤组组合成一个单元，文件扩展名为 `.cpt`。

**概念文件定义** (`login.cpt`)：

```markdown
# Login as user <username> and create project <project_name>

* Login as user <username> and "password"
* Navigate to project page
* Create a project <project_name>
```

**在 Spec 中调用概念**：

```markdown
# Login specification

## Successful login scenario
* Login as user "john" and create project "Gauge java"
```

> 概念文件默认存放在 `<project_root>/specs` 目录下。可在 `default.properties` 中用 `gauge_concepts_dir` 修改路径。

---

## 8. 步骤实现（Step Implementations）

### 8.1 简单步骤

**Spec 中的步骤：**

```markdown
* Say "hello" to "gauge"
```

**Python 实现：**

```python
from getgauge.python import step

@step("Say <greeting> to <product name>")
def hello_world(greeting, name):
    assert False, "Add implementation code"
```

### 8.2 带表格的步骤

**Spec 中的步骤：**

```markdown
* Create following "hobbit" characters
    |id  |name    |
    |----|--------|
    |123 |frodo   |
    |456 |bilbo   |
    |789 |samwise |
```

或引用外部 CSV：

```markdown
* Create following "hobbit" characters <table:hobbits.csv>
```

**Python 实现：**

```python
@step("Create following <race> characters <table>")
def create_characters(race, table):
    assert False, "Add implementation code"
```

### 8.3 步骤别名

同一功能可以用多种步骤文本表达，遵循 DRY 原则。

```markdown
# User Creation

## Multiple Users
* Create a user "user 1"
* Verify "user 1" has access to dashboard
* Create another user "user 2"
* Verify "user 2" has access to dashboard
```

**Python 实现：**

```python
from getgauge.python import step

@step(["Create a user <user name>", "Create another user <user name>"])
def create_user(user_name):
    print("create {}.".format(user_name))
```

### 8.4 枚举参数

目前仅 Java 支持枚举作为步骤参数。

---

## 9. 执行钩子（Execution Hooks）

在测试套件执行的不同级别运行代码。

**Python 实现：**

```python
from getgauge.python import (
    before_step, after_step,
    before_scenario, after_scenario,
    before_spec, after_spec,
    before_suite, after_suite
)

@before_step
def before_step_hook():
    print("before step hook")

@after_step
def after_step_hook():
    print("after step hook")

@before_scenario
def before_scenario_hook():
    print("before scenario hook")

@after_scenario
def after_scenario_hook():
    print("after scenario hook")

@before_spec
def before_spec_hook():
    print("before spec hook")

@after_spec
def after_spec_hook():
    print("after spec hook")

@before_suite
def before_suite_hook():
    print("before suite hook")

@after_suite
def after_suite_hook():
    print("after suite hook")
```

**执行顺序（从外到内）：**
`BeforeSuite` → `BeforeSpec` → `BeforeScenario` → `BeforeStep` → Step → `AfterStep` → `AfterScenario` → `AfterSpec` → `AfterSuite`

### 9.1 获取执行上下文

```python
from getgauge.python import before_step, after_spec

@before_step
def before_step_hook(context):
    print(context)

@after_spec
def after_spec_hook(context):
    print(context)
```

### 9.2 基于标签过滤钩子

```python
@before_spec("<tag1> and <tag2>")
def before_spec_hook():
    print("before spec hook with tag")

@after_step("<tag1> and <tag2>")
def after_step_hook():
    print("after step hook with tag")
```

> `BeforeSuite` 和 `AfterSuite` 不能指定标签。

---

## 10. 数据存储（Data Store）

在步骤之间共享数据。

### 10.1 ScenarioStore

数据在 Scenario 执行期间有效，每个 Scenario 结束后清除。

```python
from getgauge.python import data_store

# 存值
data_store.scenario["key"] = value
# 或
data_store.scenario.key = value

# 取值
data_store.scenario["key"]
# 或
data_store.scenario.key
```

### 10.2 SpecStore

数据在 Spec 执行期间有效，每个 Spec 结束后清除。

```python
from getgauge.python import data_store

# 存值
data_store.spec["key"] = value

# 取值
data_store.spec["key"]
```

### 10.3 SuiteStore

数据在整个测试套件执行期间有效，全部执行完毕后清除。

```python
from getgauge.python import data_store

# 存值
data_store.suite["key"] = value

# 取值
data_store.suite["key"]
```

> 并行执行时不建议使用 SuiteStore。

---

## 11. 自定义截图

```python
from uuid import uuid1
from getgauge.python import custom_screenshot_writer

@custom_screenshot_writer
def take_screenshot():
    image = driver.get_screenshot_as_png()
    file_name = os.path.join(
        os.getenv("gauge_screenshots_dir"),
        "screenshot-{0}.png".format(uuid1().int)
    )
    file = open(file_name, "wb")
    file.write(image)
    return os.path.basename(file_name)
```

**在执行中手动截图：**

```python
from getgauge.python import Screenshots

Screenshots.capture_screenshot()
```

---

## 12. 报告中的自定义消息

```python
from getgauge.python import Messages

Messages.write_message("Custom message for report")
```

---

## 13. Continue on Failure（失败时继续执行）

默认情况下步骤失败后不再执行后续步骤。标记 `ContinueOnFailure` 可使失败后继续。

**Python 实现：**

```python
@continue_on_failure([RuntimeError])
@step("Say <greeting> to <product>")
def step2(greeting, product):
    pass
```

> - `ContinueOnFailure` 不适用于钩子函数
> - 需要显式标记每个需要继续的步骤
> - 如果步骤实现在参数匹配阶段就失败了，则不会继续执行
> - 步骤别名共享同一实现，标记后所有别名都具备该特性

---

## 14. Gauge 项目结构

```
<project_root>/
├── env/
│   └── default/
│       ├── default.properties    # 默认环境变量
│       └── python.properties     # 语言插件配置
├── logs/
├── manifest.json                 # 语言和插件信息
├── specs/
│   └── example.spec              # 规范文件
└── step_impl/
    └── step_impl.py              # 步骤实现
```

### manifest.json

```json
{
    "Language": "python",
    "Plugins": [
        "html-report"
    ]
}
```

---

## 15. 完整示例

```markdown
# 用户搜索功能测试

Tags: search, regression

用户需要能够在搜索页面搜索已存在的产品。

* 以管理员身份登录 "admin"
* 打开产品搜索页面

## 成功搜索已有产品

Tags: successful, smoke

* 搜索产品 "Cup Cakes"
* "Cup Cakes" 应该出现在搜索结果中

## 搜索不存在的产品

Tags: negative

* 搜索产品 "NonExistentProduct"
* 搜索结果应该为空

## 多关键词搜索

    | keyword   | expected_count |
    |-----------|----------------|
    | cake      | 3              |
    | bread     | 2              |
    | cookie    | 1              |

* 搜索 "<keyword>"
* 搜索结果数量应为 <expected_count>

____
* 注销当前用户
* 清理测试数据
```

---

## 16. 常用命令参考

| 命令 | 说明 |
|------|------|
| `gauge init <lang>` | 初始化项目 |
| `gauge run specs/` | 运行所有 spec |
| `gauge run specs/xxx.spec` | 运行指定 spec |
| `gauge run --tags "tag1" specs/` | 按标签过滤运行 |
| `gauge run --env <env_name> specs/` | 指定环境运行 |
| `gauge run --parallel specs/` | 并行运行 |
| `gauge validate specs/` | 验证 spec 语法 |

---

*文档基于 Gauge 官方 Writing Specifications 文档整理。*
