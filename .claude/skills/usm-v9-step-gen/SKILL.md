---
name: usm-v9-step-gen
description: 公司专用(明御运维安全管理系统 / USM V9 堡垒机)前端功能沉淀 skill。人机协作把功能沉淀为参数化、可重放的 Python 方法。当用户要写/调堡垒机功能脚本、沉淀方法、修改step、检查step报错时使用。
context：fork
---

# USM V9 功能生成（公司专用）

> 本 skill 只服务公司内部的 **明御运维安全管理系统 / USM V9 堡垒机**，不是通用 Playwright skill。沉淀出的方法库住在**项目**里（见下「项目架构」）。

## 依赖与前置

- 浏览器操作依赖 `playwright-cli` skill，配置已在 `.playwright/cli.config.json` 配好，直接启动即可。只有脚本验收时才调 driver。
- 公共元素定位与探测逻辑参考`referce/元素定位规则.md`，优先按照其中规则进行尝试。
- 已有的按模块拆分的笔记沉淀在 `notes/` 目录下，先读 `notes/README.md` 了解索引，遇到难题可参考对应模块笔记及 `notes/common.md` 公共笔记。


## 项目架构

本项目是标准 **Gauge** 布局，沉淀出的step不随skill 携带，而是长在项目里：
| `step_impl/`           | **gauge 沉淀 step**。按路由 L2/L3 英文目录组织，是所有 workspace 中方法测试通过后沉淀的标准 gauge step。|
| `utils/page_helper.py` | **公共设施**（`PageHelper` 类：`goto_route`、`drawer`、`antd_select`、`antd_radio`、`antd_checkbox` 等）。**全量读**。Gauge 模式通过 `data_store.suite["page_helper"]`，如有补充请遵守格式规范。

**skill 目录**只携带：
- `notes/` — 按模块拆分的踩坑/站点事实/沉淀规范备忘（**开工前先读 `notes/README.md` + 对应模块笔记**，做完把新经验追加到对应模块文件）
- `reference/` — 验收脚本规则、step_impl 生成规则
- `templates/gauge_step.py` — 新方法模板（复制改）

## 工作流（状态机）

总流程：**探索页面 & 拆解步骤 → step逐步生成（参数沉淀） → 引变量后验证（重试 & 求助）→ 最终脚本用户验收**。

---

### 阶段 1：探索页面 & 拆解步骤（必须步骤）

根据用户描述找到相关页面，**先探索当前功能所在页面**，再结合用户要求总结出有序的原子步骤（如：打开页面 → 输入账号 → 输入密码 → 点登录 → 断言进入首页），**把 step 步骤列表总结给用户过一眼**。这一步不可省略，不要一口气写整段代码。

**先查已沉淀方法，再决定探索深度。** 探索前先做两件事：

1. **粗筛**：扫一遍 `step_impl` **对应功能目录下**的 py 文件的**顶部 docstring**（标题/路由/功能），查看是否存在相关步骤。
2. **精读**：如果存在步骤且用户要求优化，则对相关文件进行精读；`utils/page_helper.py` 全量读。

然后对照 `notes/<对应模块>.md` 和 `notes/common.md`：

- 要做的功能或其中某几步已经沉淀过 → **直接复用/参考现成方法和定位**。
- 相似功能（如"新建 X"和已有"新建用户"）→ 照搬其抽屉/表单定位套路（`drawer()`/`antd_select`/`antd_radio` 等），只补差异部分。
- **启动浏览器探索**根据已有经验或步骤快速验证并执行。缺失或差异部分仔细探索。

---

### 阶段 2：step逐步生成（参数沉淀）


**铁律：step按拆解步骤一一对应。** 不拆解步骤，也不合并步骤

**变量提取准则（提取 params 参数范围）：**

- **原则上**页面中需要用户填写、选择、勾选等操作都应该要做成参数形式。
- **固定选项的下拉框或按钮选项**应该获取其中值，写到方法中params中。
- **非固定动态加载下拉框**（例如目录树选项等），如果有默认值则只用提取默认值。

**参数化：将步骤页面上的参数转化到gauge step中**：将步骤页面涉及的参数全部转化到step，当参数大于3个时，收敛成`step`的`table`传参，小于3个正常带入step

```python
# 小于3个参数正常写入step
@step("登录堡垒机账号<username>密码<password>")
def login_bastion(username, password):
    pass

# 大于3个参数，收敛为gauge table
@step("填写用户基本信息 <table>")
def fill_user_basic(tables):
    pass
```

**内嵌断言：步骤用关键元素验证，不靠截图。** 判断一步是否成功，断言/检查**关键元素**，中间步骤非必须。但一个文件至少要有至少1处断言。

---
具体规则参考 `reference/step_impl生成规则.md`。

### 阶段 3：引变量后优化 & 再测试（带重试）

参数化后**用真实/多组变量重新跑**，验证方法通用可靠：

```
带变量运行方法 → 取事实
   ├─ 通过 → 进入输出
   └─ 失败 → 自动重试优化（修等待/定位/参数处理）
```

生成的临时验证脚本放在`temp`下，脚本生成准则：
- 初始化环境调取`step_impl.hooks.py` 中的`init_test_env()`,关闭浏览器调用`quit_driver()`
- 导入`from getgauge.python import data_store`确保引用到初始化环境中的page对象等
- 验证需要全面覆本次生成的所有step方法，通过`from step_impl.xx.xx import *`来导入所有方法
- 数据尽量全面覆盖到step中的传参数据，3条左右最佳（避免排列组合参数爆炸增长）
- tables参数使用一下方式进行桥接：
```python
class MockTable:
    """桥接 Gauge Table 对象，使 step_impl 函数在 standalone 脚本中可用"""
    def __init__(self, data: dict):
        self.headers = list(data.keys())
        self.rows = [[data[k] for k in self.headers]]
```

### 阶段 4：最终脚本用户验收

step调试好后，`temp`目录下生成一份验收文件，命名为{gauge文件名}_verify.py，规则如下
- 文件导入本次生成的所有step进行验证
- 根据生成的step文件顶部描述的steps来组合式生成case
- 每个case为一个方法，包含要验证到的step方法和测试数据
- case有可选步骤的使用和省略，参数的组合覆盖

例如
```python
from getgauge.python import data_store
from step_impl.hooks import init_test_env, quit_driver
from step_impl.user.management.create_user import *

class MockTable:
   """桥接 Gauge Table 对象，使 step_impl 函数在 standalone 脚本中可用"""
   def __init__(self, data: dict):
      self.headers = list(data.keys())
      self.rows = [[data[k] for k in self.headers]]


def case1():
   # 包含所有步骤
   fill_user_basic(MockTable({
      "username": "aaaa",
      "role": "aaa",
      "auth_source": "aaaa",
      "must_change_pwd": "aaaa",
      "template": "aaaa"
   }))
   # 其它步骤省略

def case2():
   # 不包含非必填步骤
   fill_user_basic(MockTable({
      "username": "bbbb",
      "role": "bbbb",
      "auth_source": "bbbb",
      "must_change_pwd": "bbbb",
      "template": "bbbb"
      })) # 不同参数进行调试 
....

if __name__ == '__main__':
   # 进行case测试
   ...

```


## 五个铁律

1. **使用 playwright-cli** 完成页面探索和脚本生成，不要自己写脚本重复启动浏览器。
2. **每步验证事实**：验证**关键元素**（URL/命中元素/关键文本/有无报错），不许只说"成功"。
3. **排查问题时**：带入 space 中相关用例的参数到 acceptance 脚本当中去复现。
4. **用户审核机制**：生成的步骤要经过用户审核。
5. **推理脚本唯一落点**：所有思考过程中生成的脚本一律放入 `temp` 目录，严禁放入其他任何目录。
6. 中途生成的自检验收脚本使用 `headless=True`，最终生成的验收脚本使用 `headless=False`。一句话给自己看的无需展示，给用户看的需要展示浏览器。

## 参考文件

- **step_impl 生成规则**：[reference/step_impl生成规则.md](reference/step_impl生成规则.md)
- **gauge step 模板**：[templates/gauge_step.py](templates/gauge_step.py)
- **验收脚本模板**：[templates/acceptance_script.py](templates/acceptance_script.py)
- **模块笔记索引**：[notes/README.md](notes/README.md)
- **公共笔记**：[notes/common.md](notes/common.md)

## 一句话本质

浏览器操作、元素获取都是 playwright-cli 的能力。本 skill 只负责把它们编排成一条**带重试与人工求助节点的状态机**，最终把"人机协作跑通的流程"沉淀为**参数化、可重放的 Python 方法**。
