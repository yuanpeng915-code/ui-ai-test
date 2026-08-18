# USM UI Test

明御运维安全管理系统（USM V9 堡垒机）前端自动化测试框架，基于 **Gauge + Playwright + Python**，通过 `uv` 管理依赖，支持 **AI 辅助生成** 测试用例。

## 技术栈

| 层级 | 技术 | 职责 |
|------|------|------|
| 底层驱动 | Playwright | 跨浏览器自动化操作 |
| 测试框架 | Gauge | BDD 规范即代码，自然语言 Step |
| 编程语言 | Python 3.11+ | Gauge-Python 实现 |
| 包管理 | uv | Python 依赖管理与虚拟环境 |
| AI 能力 | 大模型（LLM） | Step 语义理解 → Spec 用例组合生成 |

## 核心理念

| 原则        | 说明                                |
|-----------|-----------------------------------|
| **AI 封装** | SKILL封装业务级 Step（Gauge 规范）         |
| **AI 生成** | 大模型理解 Step 语义，自动组合生成 Gauge Spec 用例 |
| **约束优先**  | AI 仅在既定 Step 白名单内组合，杜绝代码幻觉        |
| **数据分离**  | 测试数据独立维护，AI 按需检索匹配                |

## 项目结构

```
usm-ui-test/
├── .agents/                # Codex AI Skill 定义目录
│   └── skills/
│       ├── playwright-cli/      #   Playwright CLI 浏览器自动化
│       ├── usm-v9-case-gen/     #   Spec 用例组合生成
│       └── usm-v9-fun-gen/      #   前端功能沉淀
├── specs/                  # Gauge .spec 用例文件（AI 生成的目标目录）
│   ├── account/            #   账户管理用例
│   ├── asset/              #   资产管理用例
│   ├── user/               #   用户管理用例
│   ├── audit/              #   审计模块用例
│   ├── authority/          #   授权模块用例
│   ├── config/             #   配置模块用例
│   ├── report/             #   报表模块用例
│   ├── strategy/           #   策略模块用例
│   ├── system/             #   系统管理用例
│   └── auth/               #   认证模块用例
├── step_impl/              # 步骤实现（人工封装的 Gauge Step）
│   ├── hooks.py            #   before_suite / after_suite 钩子
│   ├── login.py            #   登录步骤
│   ├── common.py           #   公共步骤
│   ├── account/management/ #   账户管理步骤实现
│   ├── asset/management/   #   资产管理步骤实现
│   └── user/management/    #   用户管理步骤实现
├── acceptance/             # 可独立运行的业务脚本（非 Gauge 模式）
│   ├── login.py            #   登录功能脚本
│   ├── account/management/ #   账户功能脚本
│   ├── asset/management/   #   资产功能脚本
│   └── user/management/    #   用户功能脚本
├── utils/                  # 工具库
│   ├── dirver.py           #   Playwright ChromeDriver 封装
│   ├── page_helper.py      #   页面操作助手（路由跳转、Ant Design 表单操作）
│   ├── data_loader.py      #   配置/数据加载器
│   └── parser.py           #   解析工具
├── configs/                # 配置文件
│   ├── driver.json         #   浏览器驱动配置（窗口、超时、headless 等）
│   └── router.json         #   堡垒机全部页面路由映射
├── data/                   # 测试数据
│   └── assets.json         #   测试资产数据（OS/IP/协议/账号密码）
├── env/                    # 环境配置
│   ├── test.json           #   测试环境账号
│   └── default/            #   Gauge 默认配置
├── scripts/                # 探索/辅助脚本
├── packages/               # 离线安装包（Gauge、Gauge-Python）
├── reports/                # 测试报告输出
├── logs/                   # 运行日志
└── reference/              # 参考文档
```

## 快速开始

### 环境要求

- Python >= 3.11
- Node.js（Playwright 依赖）
- uv（Python 包管理器）
- Gauge 1.6+（离线安装包位于 `packages/`）

### 安装

```bash
# 安装 uv（如未安装）
pip install uv

# 安装依赖（自动创建 .venv 并同步 lock 文件）
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium
```

> Playwright 浏览器安装默认从境外 CDN 下载，内网环境会超时。如果已在 `10.113.56.129` 搭建了代理镜像，替换为：

```bash
# 通过内网代理下载浏览器
$env:PLAYWRIGHT_DOWNLOAD_HOST="http://10.113.56.129/"
uv run playwright install chromium
```

### 配置

1. **测试环境**：编辑 `env/test.json`，填入堡垒机的 URL、用户名和密码
2. **浏览器配置**：编辑 `configs/driver.json`，可调整视口、headless 模式、超时等
3. **测试数据**：编辑 `data/assets.json`，配置可用的测试资产（OS/IP/协议等）

### 运行测试

```bash
# 运行全部用例
gauge run specs/

# 运行指定模块
gauge run specs/account/

# 运行单个 spec 文件
gauge run specs/account/P0_新建查询删除账户.spec
```

## AI Skill 体系

本项目在 `.agents/skills/` 下定义了三个专用 Skill：

| Skill | 职责 |
|-------|------|
| **$playwright-cli** | 浏览器自动化 CLI，负责页面打开、点击、填充、截图、trace 等底层操作 |
| **$usm-v9-fun-gen** | 前端功能沉淀：将页面上的功能转化为参数化的 Python 方法，最终输出为 Gauge step_impl |
| **$usm-v9-case-gen** | Spec 用例生成：从已有的 step_impl 白名单中自动组合生成 `.spec` 用例文件 |

### 使用方式

**第 1 步：沉淀页面功能** 使用 $usm-v9-fun-gen 将页面功能转化为代码方法。

用户只需要告诉 AI 要操作哪个页面的什么功能，AI 会自动打开浏览器探索页面，识别页面上的下拉框、文本框、勾选框、单选框等控件，将它们包装成方法参数。一个功能会被 AI 自动拆解为多个有序步骤，用户只需审核步骤拆分是否合理、告知需要修改的地方，AI 会根据反馈逐步完成所有步骤的方法沉淀。

举例：用户说「帮我沉淀新建用户的功能」，AI 会：
1. 打开新建用户页面，分析表单中的所有控件
2. 拆解步骤：打开页面 - 填写基本信息(username/name/password) - 填写安全配置(role) - 提交
3. 逐步生成每步代码，每步用关键元素验证通过后再进入下一步
4. 将所有写死的值提取为参数，例如: def create_user(page, username, name, password, role): ...
5. 输出到 acceptance/user/management/create_user.py 供用户验收
6. 验收通过后，转化为 step_impl/user/management/create_user.py 的 Gauge Step，供用例生成使用

**第 2 步：生成测试用例** 使用 $usm-v9-case-gen 从已有 step_impl 中组合生成 .spec 用例文件。告诉 AI 要哪个模块的什么操作，AI 会自动匹配步骤、填充测试数据、按优先级输出 spec。spec 文件命名规则为 P<优先级>_<AI 总结标题 10 字以内>.spec。

举例：用户说「完成资产管理的增删改查，用例为 P0 级别」，AI 会：
1. 在 step_impl/asset/management/ 中匹配到 create_asset.py、search_asset.py、delete_asset.py 等步骤文件
2. 从 data/assets.json 中匹配可用的资产模板(如 Windows 资产的 IP、协议、凭据)
3. 按 P<优先级>_<AI 总结标题 10 字以内>.spec 规则，生成 specs/asset/P0_资产增删改查.spec，自动串联新建 - 查询 - 删除的完整闭环，测试数据自动带时间戳保证唯一性
4. 用户审核 spec 无误后即可通过 gauge run 直接执行

**提示**：无论是方法沉淀还是用例生成，都可以直接告诉 AI「记住：xxx」，AI 会记录你的生成技巧和偏好，避免下次重复踩坑。


## 许可

内部项目
