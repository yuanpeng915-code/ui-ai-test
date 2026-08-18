# 应用服务器部署用例生成笔记

## 已有 step（deploy_appserver.py）

| Step | 参数 | 必填 |
|------|------|------|
| 打开应用服务器页面 | 无 | 是 |
| 打开应用服务器部署弹窗 \<server_ip\> | server_ip(文本) | 是 |
| 生成应用服务器部署命令 | 无 | 是 |
| 调用接口部署Linux的usmdriver \<architecture\> | architecture(arm_64/x86_64) | Linux 二选一 |
| 调用接口部署Windows的usmdriver | 无 | Windows 二选一 |
| 测试应用服务器部署 | 无 | 是 |
| 确认应用服务器部署 | 无 | 是 |
| 验证应用服务器服务状态 \<server_ip\> | server_ip(文本) | 是 |

## 测试数据来源

应用服务器 IP 与架构来自 `ansible/inventory.ini`，组名格式 `{platform}_{ARCH}`：
- `linux_ARM_64`: 10.113.57.78 (ARM_78)
- `windows_64`: 10.113.56.137

用户输入 `ARM_78` 时，映射到 `linux_ARM_64` 组的 10.113.57.78，architecture=arm_64。

## 生成经验

- **纯管理端用例**：部署全程在管理端操作，无需用户浏览器，无需 Tear-down 清理段
- **架构选择**：Linux 服务器走 step4（按 architecture 取 arm_64/x86_64 命令），Windows 走 step5，二选一
- **参数引号格式**：`<server_ip>`/`<architecture>` 前无空格，spec 中直接跟引号（如 `打开应用服务器部署弹窗"10.113.57.78"`）
- **无持久化数据**：部署用例不创建资产/账号等数据，应用服务器预存在，部署为安装驱动且幂等可重复执行，与查询用例一样无需清理步骤
- **server_ip 一致性**：步骤"打开部署弹窗"和"验证服务状态"的 server_ip 必须相同
