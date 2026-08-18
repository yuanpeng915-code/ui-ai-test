## 已知坑位

- **H5数据库运维 URL 与 SSH 终端不同**：MySQL 等数据库资产的 H5 运维页面 URL 含 `/webdbclient`（SSH 终端是 `/webclient`）。`h5_terminal.py` 的 `_get_h5_page()` 只匹配 `/webclient/`，**无法复用**于数据库运维，需用 `h5_db_terminal.py` 的 `_get_h5_db_page()`（匹配 `/webdbclient`，存 `h5_db_page`）。
- **SQL 编辑器是 CodeMirror**：`keyboard.type` / `fill` 对 CodeMirror 无效（输入不进）。必须通过 CodeMirror API 输入和读取：
  - 输入：`page.evaluate("(sql) => { const cm = document.querySelector('.CodeMirror'); if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(sql); } }", sql)`
  - 读取：`page.evaluate("() => { const cm = document.querySelector('.CodeMirror'); return cm && cm.CodeMirror ? cm.CodeMirror.getValue() : ''; }")`
- **"结果 N" tab 不随执行次数递增**：结果 tab 序号与 SQL 查询 tab 一一对应，**多次执行更新同一"结果 N" tab** 而非新增。单个 SQL tab（默认"Untitled"）时结果始终是"结果 1"，需点切换才看到结果表格。默认执行后停留在"执行日志" tab。
- **headless 模式不可用**：环境未安装 `chrome-headless-shell`，`headless=True` 会报 `BrowserType.launch: spawn UNKNOWN`。自检/验收脚本统一用 `headless=False`（走 `init_test_env()` 默认配置）。

## 业务逻辑

### H5 数据库运维客户端页面结构（/webdbclient）

**顶部 tab**：连接 tab（如 `root@10.113.56.129/MYSQL`），每个资产连接一个。

**左侧面板**：数据库树（`.ant-tree`），列出所有可访问数据库（如 information_schema / mysql / performance_schema / t1），可展开看表。有搜索框 `placeholder="请输入搜索内容(不区分大小写)"`。

**右侧面板**（SQL 工作区）：
- SQL tab 栏（默认"Untitled" tab + plus 按钮新增）
- 工具栏：
  - 数据库选择下拉：`#database`（id 固定），placeholder="选择数据库"，选项动态加载
  - 执行按钮：`button[type='submit']`（工具栏内唯一提交按钮，play 图标）
  - 保存等按钮：`type='button'`（非提交）
- SQL 编辑器：CodeMirror（`.CodeMirror` 类）
- 底部结果面板（`.ant-tabs`）：
  - "执行日志" tab（默认激活）：表格含列 时间/SQL语句/返回信息/结果/耗时，执行成功显示"成功"
  - "结果 N" tab：查询结果表格，ReactVirtualized 虚拟滚动（`.usm_virtual_row` / `.usm_virtual_cell`），列头为查询字段名，带分页"共N条"

### 关键定位速查

| 元素 | 定位 |
|------|------|
| 数据库下拉 | `#database` -> `..` -> `..`（`.ant-select-selector`），同 `PageHelper.main_select` 套路 |
| SQL 编辑器 | `.CodeMirror`（通过 CodeMirror API 操作） |
| 执行按钮 | `button[type='submit']` |
| 执行日志面板 | `get_by_role("tabpanel", name="执行日志")` |
| 结果 tab | `get_by_role("tab", name="结果 N", exact=True)` |
| 结果数据行 | `.usm_virtual_row`（可见的） |

### 运维连接流程（与 SSH H5 一致）

`打开运维连接弹窗<asset>` -> `选择H5运维方式` -> （可选）`选择运维账号<account>` -> `发起运维连接` -> `获取H5数据库运维页面`

MySQL 资产连接弹窗默认账号已选（如 root/MySQL），可不调 `选择运维账号`。
