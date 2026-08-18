## 已知坑位

- **应用服务器 tab 二次点击失效**：远程客户端页有两个 tab（远程客户端/应用服务器），应用服务器 URL 为 `/asset/remote_server`。从 `remote` 页点 tab 切到 `remote_server` 首次正常，但二次进入（先到 remote_server 再回 remote 再点 tab）时 tab 点击不改变 URL（SPA hash 路由问题）。**解决**：直接 `page.goto(base + "/index/#/index/manage/project/1/asset/remote_server")` 导航，不点 tab。
- **生成命令区是 `<p>` 标签**：部署抽屉点"生成命令"后，命令以 `<p>` 元素呈现。Linux 区分 2.1 安装XRDP Server（4条：UOS/Kylin × x86_64/arm_64）和 2.2 安装usmdriver（2条：x86_64/arm_64），命令段落含 `usmdriver-linux-{arm|x86}`；Windows 只有一条 PowerShell 命令，段落含 `usmdriver-win`。按架构取命令用 `drawer.locator("p").filter(has_text=f"usmdriver-linux-{suffix}").first`。
- **ak/sk 内嵌在命令中且按平台不同**：Linux 命令尾部 `-ak=XXX -sk=YYY`（ak/sk 两空格分隔），Windows 在 `Start-Process -ArgumentList "-ak=XXX -sk=YYY ..."` 中。Windows 的 ak/sk 与 Linux 不同，需从各自命令提取，不能混用。
- **架构后缀映射**：页面架构标签 `arm_64`/`x86_64`，URL 后缀 `arm`/`x86`（不是 arm64/x64）。

## 业务逻辑

### 应用服务器部署流程

部署入口：远程客户端页 -> 应用服务器 tab -> 列表行"部署"按钮。

部署抽屉结构：
- 标题：`部署 [ {服务器名} ]`
- 说明步骤（1.登录服务器 2.生成命令 3.执行）
- "生成命令"按钮 -> 展开命令区
- "部署任务"区 + "测试"按钮 -> 测试后显示运维服务/改密服务状态（`<p>` 内含"正常"）
- 底部"确定"/"取消"按钮

实际部署通过调用 `http://10.113.56.129:5000/appServer/deploy`（POST）完成，接口内部跑 ansible 远程执行命令。从页面命令提取 server_ip/ak/sk 后传给接口，无需手填。

### 列表结构

列：名称/IP/所属网络/操作系统/参与调度/远程客户端数/运维服务状态/改密服务状态/操作（编辑/部署/同步账号/删除）。虚拟表格 `.usm_virtual_row`，按 IP 过滤行后点"部署"。

### 关键定位速查

| 元素 | 定位 |
|------|------|
| 数据行 | `.usm_virtual_row`（`filter(has_text=ip)` 按 IP 定位） |
| 部署按钮 | 行内 `get_by_text("部署", exact=True)` |
| 部署抽屉 | `.ant-drawer-content`（last） |
| 生成命令按钮 | `drawer.get_by_role("button", name="生成命令")` |
| Linux 命令段落 | `drawer.locator("p").filter(has_text="usmdriver-linux-{suffix}")` |
| Windows 命令段落 | `drawer.locator("p").filter(has_text="usmdriver-win")` |
| 测试按钮 | `drawer.get_by_role("button", name="测试")` |
| 测试结果 | `drawer.locator("p").filter(has_text="运维服务")` / `"改密服务"` |
| 确定按钮 | `get_by_role("button", name="确 定")` |
