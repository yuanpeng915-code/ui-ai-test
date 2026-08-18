# 资产搜索用例生成笔记

## 已有 step（search_asset.py）

| Step | 参数 | 必填 |
|------|------|------|
| 打开资产管理页面 | 无 | 是 |
| 填写资产搜索条件 \<table\> | ip_domain_match_mode, ip_domain, asset_name, ... | 否(按需填) |
| 点击查询资产 | 无 | 是 |
| 验证资产搜索结果 \<expected_asset\> | expected_asset(文本) | 是 |

## 生成经验

- IP精确搜索只需填 `ip_domain_match_mode`("精准匹配") 和 `ip_domain`
- 多值搜索用空格分隔 IP，如 `10.113.56.137 10.113.56.129`
- 验证步骤可多次调用，每次验证一个 IP
- 纯查询用例无需清理步骤

## B/S 资产创建（APP 模板）

### 业务约束
- B/S 模板步骤2「资产信息」比 Linux/Windows 多一个「服务信息」面板，URL 必填（HTTP/HTTPS 服务地址）。`fill_asset_info` 通过 table 传 `url` 参数触发该面板填写，非 B/S 模板不传 `url`。
- B/S 模板步骤3「资产账号」**无默认账号**（暂无数据），不像 Linux 有默认 root。不需建账号时跳过步骤4 `新建或修改资产账号`，直接 `保存新建资产`。
- IP/域名仍必填（提示：HTTP/HTTPS 用 URL 配置连接，非 IP/域名）。

### 参数说明
- `url`：B/S 必填，HTTP/HTTPS 服务地址，如 `https://10.113.76.175`
- `same_origin`：非必填，是/否（同源限制，默认否）
- `url_filter_mode`：非必填，黑名单/白名单（默认黑名单）
- `url_filter`：非必填，URL 过滤内容（支持通配符，如 `https://10.113.76.181/admin`）
- `special_url_whitelist`：非必填，但**校验过严暂不可填**（见 step-gen 笔记），用例中留空
- `fill_script` / `change_pwd_script`：非必填，代填/改密脚本文本

### 清理
B/S 资产删除与普通资产一致：搜索 -> 勾选首行 -> 删除 -> 确认 -> 验证已删。
