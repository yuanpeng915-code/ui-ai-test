# 个人工作台 - 运维 (profile/om)

## Ping 策略验证

验证资产运维连接是否正常建立，通过 Ping 服务时间戳来确认运维通道已打通。

### 验证三步流程

| 步骤 | 对应 Step | 说明 |
|------|----------|------|
| 1. 清除时间戳 | `清除Ping服务时间戳` | 运维前清空上次 `/ping` 记录的时间戳，确保验证结果准确 |
| 2. 触发 Ping | — | 运维连接建立后，在运维终端/浏览器内访问 `http://10.113.56.129:5000/sshCheck/ping`，更新服务端内置时间戳 |
| 3. 验证调用 | `验证Ping服务已被调用` | 请求 `/sshCheck/pong`，断言 `code="ok"`，即步骤2的 ping 已成功到达 |

**服务地址**: `http://10.113.56.129:5000`，三个接口：
- `/sshCheck/clear` — 清除时间戳
- `/sshCheck/ping` — 更新时间戳
- `/sshCheck/pong` — 查询时间戳状态

### 不同资产类型的 Ping 触发方式

| 资产类型 | 运维方式 | H5 Step | 操作方法 |
|---------|---------|---------|---------|
| SSH | H5运维 | `H5终端输入<text>回车提交<submit>` | 终端内输入 `curl http://10.113.56.129:5000/sshCheck/ping`，submit=True 回车执行 |
| RDP | H5运维 | `H5终端粘贴<text>回车提交<submit>` | RDP 是浏览器窗口，需先点击地址栏再粘贴：x=800, y=100（地址栏坐标），text=`http://10.113.56.129:5000/sshCheck/ping`，submit=True 回车访问 |
| HTTP/B/S | H5运维 | `H5运维页面访问URL<url>` | H5 webclient 页面无原生地址栏，直接用 page.goto() 导航到 ping URL：url=`http://10.113.56.129:5000/sshCheck/ping` |

### 完整 Spec 步骤序列参考

```
# 管理端做好资产+授权前置后，用户端验证：

# -- 清除时间戳 --
* 清除Ping服务时间戳

# -- 进入运维页 --
* 进入运维界面
* 选择运维界面左侧树节点"根目录"
* 填写运维界面资产搜索条件
|asset_name|
|{资产名}  |
* 点击运维界面资产查询

# -- 发起运维连接 --
* 打开运维连接弹窗"{资产名}"
* 选择运维账号"{账号/服务}"
* 选择H5运维方式
* 发起运维连接
* 获取H5运维页面

# -- 触发 Ping --
# SSH 资产: * H5终端输入"curl http://10.113.56.129:5000/sshCheck/ping"回车提交"True"
# RDP 资产: * H5终端粘贴"http://10.113.56.129:5000/sshCheck/ping"回车提交"True"坐标X"800"坐标Y"100"

# -- 验证 --
* 验证Ping服务已被调用
```

### 注意事项

- RDP H5 运维打开的是浏览器窗口，不能用 `H5终端输入`（xterm.js 终端），必须用 `H5终端粘贴` 配合坐标点击地址栏
- HTTP/B/S H5 运维打开的是 webclient 内嵌页面，**没有 Chrome 原生地址栏**，`H5终端粘贴` 坐标方式无效，必须用 `H5运维页面访问URL<url>` step 直接 page.goto() 导航
- Ping URL 是 `http://10.113.56.129:5000/sshCheck/ping`，注意路径是 `/sshCheck/ping` 不是 `/ping`
- 三个 ping step 都在 `step_impl/common.py` 中，非 profile 专属，所有用例可复用
- 运维配置默认时，`选择运维账号` 步骤可省略（popover 默认已选中账号）
