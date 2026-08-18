## 已知坑位

- **资产搜索"展开"无实际隐藏字段**：搜索区域点击"展开"前后字段一致（12个搜索条件均可见），无需特殊处理，但保留展开逻辑作为防御。
- **操作系统下拉无固定 ID**：`rc_select_7` 为 Ant Design 自动生成，不稳定，改用 `.ant-form-item` 通过 label "操作系统" 定位。
- **IP/域名和资产名称 placeholder 相同**：都是"多关键词以空格隔开"，需用 `get_by_role("textbox", name="资产名称")` 区分资产名称；IP/域名取 `.first`。
- **文本输入后需等待**：填写 textbox 后加 `page.wait_for_timeout(300)`，否则后续下拉框操作可能被页面渲染干扰。
- **表格使用 ReactVirtualized 虚拟滚动**：不是标准 Ant Design 表格。行定位用 `.usm_virtual_row`，单元格 `.usm_virtual_cell`，内容 `.usm_virtual_cell_content`。IP/域名在第5列(索引4)，值为 `A.link.inline`。
- **空结果检测三重机制**：①分页 `共0条` ② `.ant-empty` 占位 ③ `.usm_virtual_body` 显示 `暂无数据`。三者任一命中即视为空结果。
- **Ant Design Modal 关闭后 DOM 残留**：批量删除确认框关闭后 `.ant-modal-wrap`/`.ant-modal-content` 仍留在 DOM（`display:none`），`count()` 不归零。判定弹窗关闭必须用 `wait_for(state="hidden")` 或可见性，**不可用 `.count() == 0`**。多个 modal 并存时用 `.filter(has_text="批量删除")` 区分。
- **批量删除按钮0选中可点**：工具栏"删除"按钮始终可点（非 disabled），0 选中时点会弹"未选择条目"提示而非确认框，故勾选步骤需校验 `.checked_count` 选中数非 0。
- **资产名称搜索为大小写敏感包含匹配**："MySQL" 匹配 "MySQL_175" 但不匹配 "MYSQL_129"。多选测试数据用统一大小写前缀+时间戳构造。

## 业务逻辑

### 资产管理页搜索区域（共12个字段 + 4个操作按钮）

| 字段 | 控件类型 | 控件 ID | 可选值 | 默认值 |
|------|----------|---------|--------|--------|
| IP/域名 匹配模式 | 下拉框 | assetAddrMatchMode | 模糊匹配 / 精准匹配 | 模糊匹配 |
| IP/域名 | 输入框 | — | 文本 | 空 |
| 资产名称 | 输入框 | — | 文本 | 空 |
| 资产源 | 下拉框 | sourceIds | 123 | 请选择(空) |
| 标签 | 下拉框 | tagIds | 未绑定标签 / biaobiaobaio | 请选择(空) |
| 所属网络 | 下拉框 | networkId | default | 请选择(空) |
| 状态 | 下拉框 | status | 正常 / 禁用 | 请选择(空) |
| 上次运维时间 | 下拉框 | lastOmTime | 全部/30天以内/30天以前/90天以前/180天以前/1年前/从未运维 | 全部 |
| 连通性 | 下拉框 | connStatus | 全部/正常/异常/未知 | 全部 |
| 操作系统 | 下拉框 | rc_select_7(动态) | Cisco IOS Device / Huawei Quidway Device / H3C IOS Device / Tp-Link Device / Other Network / CentOS / Ubuntu / Debian | 请选择(空) |
| 系统编码 | 下拉框 | encoding | UTF-8 / GBK / GB2312 / GB18030 | 请选择(空) |
| 备注 | 输入框 | — | 文本 | 空 |

操作按钮：查询 / 重置 / 展开(收起) / 保存

### 搜索结果表格列
资产名称 / 资产源 / IP/域名 / IP/域名连通性 / 状态 / 备注 / 操作（编辑、更多）

### 虚拟表格 DOM 结构
```
.ant-table-container
└── .ant-table-header（表头，th 的 title 属性获取列名）
└── .usm_virtual_body（内容区）
    └── .ReactVirtualized__Grid.ReactVirtualized__List
        └── .usm_virtual_row（数据行）
            └── .usm_virtual_cell（单元格，IP在第5列索引4）
                └── .usm_virtual_cell_content
                    └── A.link.inline（IP链接文本）
```
空结果时: `.usm_virtual_row` 数量为 0，`.usm_virtual_body` 文本为 `暂无数据`。

### 左侧面板视图切换

资产管理页左上角有一个视图切换面板，通过 `.tree_header .ant-dropdown-trigger.dropdown_button` 下拉按钮切换四种视图：

| 视图 | URL参数 | 树节点示例 |
|------|---------|-----------|
| 目录 | `menu=node_id` | 根目录、网络平台二部、运维系统部、运行三部… |
| 标签 | `menu=tag_id` | 未绑定标签、biaobiaobaio… |
| 所属网络 | `menu=vpc_id` | default… |
| 操作系统 | `menu=os_id` | 分层：Network(Cisco/Huawei/H3C/Tp-Link/Other)、Windows、Unix、Linux、Other |

**DOM 结构：**
```
.tree
├── .tree_header
│   ├── .ant-dropdown-trigger.dropdown_button  (下拉按钮，文本="目录"/"标签"/"所属网络"/"操作系统")
│   └── .usm_search input.input  (搜索框，placeholder="请输入搜索内容(不区分大小写)")
└── .tree_content
    └── .ant-tree  (树形列表)
        └── .ant-tree-treenode
            ├── .ant-tree-switcher  (展开/折叠，仅目录和操作系统有层级)
            └── .ant-tree-node-content-wrapper
                └── .ant-tree-title .name  (节点名称，title属性为节点文本)
```

**选择节点方法：**
- 遍历 `.ant-tree-treenode` 的 `.name` 的 `title` 属性匹配
- 未直接找到时，先展开所有 `.ant-tree-treenode-switcher-close` 后再查找
- 选中节点后 URL 自动变化，右侧表格刷新

### 个人工作台-运维页左侧面板

运维页（`/index/#/index/profile/om`）左侧面板在 main 内的 `.om_sider` 区域，结构与管理控制台资产管理不同。

**区域划分：**
- 搜索框：`.usm_search input.input` placeholder="工单名/分组名"
- `系统默认` section（`.group_type`）：
  - 最近运维 / 收藏夹（`.header_wrap`，非树节点，点击切换视图）
  - 工单 tree（`.om_tree_box > .ant-tree`，单叶子节点）
  - 按服务分类 tree（可展开，子节点为各服务类型）
- `用户配置` section（`.group_type`）：
  - 继承管理员视图 tree（禁用父节点 → 子节点由管理员资产树决定，如"根目录"）
  - 自定义分组 tree（禁用父节点 → 子节点如"未分组"）

**树节点 DOM 结构（与资产管理页相同）：**
```
.ant-tree-treenode
├── .ant-tree-switcher
└── .ant-tree-node-content-wrapper
    └── .ant-tree-title
        └── .item
            └── .name[title="节点名称"]
```

**视图切换 URL 参数映射：**
| 点击项 | URL type 参数 | selectedId 参数 |
|--------|-------------|----------------|
| 最近运维 | LAST7DAYS | (空) |
| 按服务分类 | SERVICE | (空)/ssh/rdp... |
| 工单 | TICKET | (空) |
| 继承管理员视图子节点 | NODE | 对应节点ID |

**搜索表单（仅"按服务分类"等视图显示）：**
搜索区容器：`.higher_search_bar`，包含 9 个字段

| 字段 | 输入 ID | 类型 |
|------|---------|------|
| IP/域名 匹配模式 | assetAddrMatchMode | select |
| IP/域名 | addresses | input |
| 资产名称 | assetNames | input |
| 账号名 | usernames | input |
| 授权规则 | ruleIds | select |
| 项目 | projectIds | select |
| 标签 | tagIds | select |
| 服务URL | url | input |
| 资产网络 | networkIds | select |

**表格结构（虚拟表格）：**
与资产管理页相同的 ReactVirtualized 虚拟表格，但列顺序不同：
- 索引0: checkbox (36px)
- 索引1: 分隔符 (1px)
- 索引2: 资产名称 (200px)
- 索引3: IP/域名 (255px) ← IP验证时取此列
- 索引4: 所属项目 (255px)
- 索引5: 备注 (255px)
- 索引6: 访问 (438px)

### 新建资产流程（3步向导）

新建资产抽屉分 3 步：资产模板 → 资产信息 → 资产账号，底部按钮随步骤变化（下一步/上一步/取消 → 确定/上一步/取消）。

**步骤1 资产模板：**
- 模板选项 DOM：`.c_box` 内的 `span.b_icon`，选中态追加 `active` 类（`.b_icon.active`）
- 分类标签是 `<p>`（不可点），选项是 `span.b_icon`（可点），二者文本可能重复（如"Linux"既是分类标签又是选项）
- 定位选项用 `drawer.locator(".c_box").get_by_text(template, exact=True)`，exact 避免"Windows"误匹配"Windows域控"
- 模板分类：OS(Windows/Windows域控/Linux/Unix)、DB(Oracle/MySQL/...)、NETWORK(Cisco IOS/Huawei Quidway/H3C Comware)、APP(B/S)

**步骤2 资产信息（`#basic` 作用域）：**
| 字段 | 控件 | ID | 必填 | 默认值 |
|------|------|----|------|--------|
| 资产类型 | radio | - | 否 | 普通资产 |
| 资产名称 | 文本 | `#name` | 是 | - |
| IP/域名 | 文本 | `#address` | 是 | - |
| 操作系统 | 下拉 | `rc_select_*`(动态) | 是 | 随模板(Linux→Other Linux) |
| 所属网络 | 下拉 | `#networkId` | 是 | default |
| 所在目录 | 树下拉 | `#nodeId` | 是 | 根目录 |
| 标签 | 下拉 | `#tagIds` | 否 | 空 |
| 备注 | textarea | `#remark` | 否 | 空(最长500) |

- 基本信息/更多信息是两个 `.ant-collapse-item` 折叠面板，默认展开
- 所在目录是树形下拉(`.ant-select-tree`)，选项是 `.ant-select-tree-node-content-wrapper`，非普通 `.ant-select-item-option`，`antd_select` 不适用
- 操作系统下拉 ID 是动态的 `rc_select_*`，用 label 定位(`antd_select("操作系统", ...)`)

**步骤3 资产账号：**
- 默认已有 root(SSH) 账号，账号表格用虚拟滚动 `.usm_virtual_row`，"编辑"是 `span.link`
- 新建账号点账号区"新建"按钮（注意与外层"资产账号 新建"折叠头区分，用 `get_by_role("button", name="新建", exact=True)`）
- 账号表单字段 ID：`#username`(账号名)、`#password`(密码)、`#tagIds`(标签)、`#services`(应用于服务)、`#sshKeyId`(SSH密钥)、`#serviceAttr_changeFromUsername`(切换自)、`#chpassScriptId`(改密脚本)
- 账号类型在新建时是 radio(仅"本地账号"一个选项)，编辑时只读文本
- 应用于服务(`#services`)是**多选**(`ant-select-multiple`)，默认随模板选 SSH

**已知坑位（新建资产）：**
- **`antd_multi_select` 与 `#services` 嵌套深度不兼容**：`#services` 的父级链是 `.ant-select-selection-search → .ant-select-selection-overflow-item → .ant-select-selection-overflow → .ant-select-selector → .ant-select`，原来用 `.locator("..").locator("..")` 只上溯2层落在 `.ant-select-selection-overflow-item` 上，读不到兄弟节点的 `.ant-select-selection-item`，导致误判"未选"→点 SSH 选项反而**取消选中**→提交报"请选择服务"。已修复为 `item.locator(".ant-select").first` 定位 select 容器。
- **Escape 会关抽屉**：探索时按 Escape 会关闭整个抽屉，调试下拉时用选值或点空白区关闭，不用 Escape（但 `antd_multi_select` 内部的 Escape 是对 select 的，不影响抽屉）。
- **`#name`/`#address` page 级 fill 可能失效**：用 `ph.drawer().locator("#name")` 限定抽屉作用域更稳。
- **步骤进入断言不能用步骤指示器文本**：`drawer.get_by_text("资产账号")` 会命中顶部步骤指示器（始终可见），改用步骤3独有的 `get_by_role("button", name="确 定")` 判定是否真正进入资产账号步骤，未进入时抓 `.ant-form-item-explain-error` 辅助排查。

### B/S 模板新建资产差异（APP 分类下唯一模板）

B/S 模板步骤2「资产信息」有**三个折叠面板**（基本信息/服务信息/更多信息），Linux/Windows 等只有两个（基本信息/更多信息）。`fill_asset_info` 传 table 的 `url` 参数即触发「服务信息」面板填写，非 B/S 模板留空跳过，向后兼容。

**服务信息面板字段（B/S 独有）：**
| 字段 | 控件 | ID | 必填 | 默认值 |
|------|------|----|------|--------|
| URL | textbox | `#serviceConfig_url` | 是 | - |
| 代填脚本 | textarea | `#serviceConfig_fillScript` | 否 | 空 |
| 改密脚本 | textarea | `#serviceConfig_changePassScript` | 否 | 空 |
| 同源限制 | switch | `#serviceConfig_httpSameOriginEnabled` | 否 | 关闭 |
| 黑白名单 | radio | (无ID, `.ant-radio-wrapper` 按文本"黑名单"/"白名单"定位) | 否 | (黑名单)不允许以下URL |
| URL过滤内容 | textarea | (无ID, `[placeholder*='支持通配符匹配']` 定位) | 否 | 空 |
| 特殊URL白名单 | textarea | `#serviceConfig_httpSpecialUrlWhitelist` | 否 | 空 |

- IP/域名仍必填，旁有提示"HTTP/HTTPS服务将会使用服务中的URL配置，而非IP/域名配置进行连接"
- 操作系统仍存在，默认 Other Linux
- **B/S 模板步骤3无默认账号**（"暂无数据"，不像 Linux 有默认 root），不需建账号时直接跳过步骤4
- **特殊URL白名单校验过严（疑似产品 bug）**：常规 URL（`https://IP`、`https://IP/path`、`https://IP/*`、`https://域名`、`IP`、`IP:port`、带 hash/query）均报"输入内容不合法"，仅空值通过。用例中该字段留空，待产品侧确认合法格式。

### 批量删除流程

删除流程前置：必须先搜索（`search_asset.py` 的 打开资产管理页面/填写资产搜索条件/点击查询资产）筛选出目标资产，否则全选会选中整页全部资产。

**工具栏按钮（表格上方）：** 新建 / 启用 / 禁用 / 删除 / 更多 / 导出 / 布局模式 / 自定义列。"删除"按钮始终可点，0选中时弹"未选择条目"提示。

**表格勾选机制（虚拟表格）：**
| 元素 | 定位 | 选中态 |
|------|------|--------|
| 表头全选 checkbox | `th.ant-table-selection-column .ant-checkbox-wrapper` | `ant-checkbox-wrapper-checked` |
| 行 checkbox | `.usm_virtual_row` 首个 `.usm_virtual_cell` 内 `.ant-checkbox-wrapper` | `ant-checkbox-wrapper-checked` |
| 选中计数 | `.checked_count`（文本"选中X项"） | - |

- 全选 checkbox 遵循 Ant Design 规则：未全选时点击=全选，已全选时点击=清空。已在选中态的行不重复点击（避免反选），先读 `ant-checkbox-wrapper-checked` class 再决定是否点。
- 行号 1 起始，`select_mode="1,3"` 解析为点击第1、3行 checkbox。

**删除确认弹窗：**
- 结构：`.ant-modal-content`，标题"批量删除"，提示"确认从本系统里删除吗？"，按钮"取 消"/"确 定"（注意中间空格）
- 点"确 定"后弹窗立即关闭，列表刷新。**关闭判定用 `wait_for(state="hidden")`，不可用 `.count() == 0`**（见已知坑位）

**验证删除：** 按资产名称搜索，命中空结果（共0条/暂无数据/.ant-empty）即视为删除成功。
