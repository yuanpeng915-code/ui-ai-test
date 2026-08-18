# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 技术栈

- 环境 python3.12 + uv(环境管理) + Gauge BDD
- 核心库
    - getgauge
    - playwright
- 代码规范
    - 严格使用typing模块

## 项目结构

| 目录/文件                  | 用途|
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| `configs/router.json`  | **存放路由信息**。name命名规则为`管理控制台-L2-L3`或`个人工作台-L2-L3`，概览页面无L3 | 
| `step_impl/`           | **gauge 沉淀 step**。按路由 L2/L3 英文目录组织，是所有 workspace 中方法测试通过后沉淀的标准 gauge step。|         
| `data/`                | **存放测试数据目录**。`assets.json`存放一些测试资产数据|
| `utils/`               | **核心公共方法库**。存放一些核心的公共方法|
| `temp/`                | **临时调试脚本文件**。调试代码文件方次目录。**所有思考过程中生成的脚本和验收脚本一律放 `temp/`，禁止放到其它目录。** |
## 常用命令

```bash
# Install dependencies (creates .venv + syncs lock file)
uv sync

# Install Playwright Chromium (use proxy on intranet)
$env:PLAYWRIGHT_DOWNLOAD_HOST="http://10.113.56.129:8080"
uv run playwright install chromium

# Run all specs
gauge run specs/

# Run a module
gauge run specs/asset/

# Run a single spec
gauge run specs/asset/P0_新建资产.spec
```

## AI Skills

| Skill | 职责 |
|-------|------|
| `usm-v9-fun-gen` | 浏览器探索 → 沉淀功能为参数化 Python 方法 → 转化为 `step_impl/` 的 `@step` |
| `usm-v9-case-gen` | 从 `step_impl/` 白名单组合 step → 生成 `.spec` 用例（绝不编造 step） |
| `playwright-cli` | 浏览器自动化（打开、点击、填充、截图、trace） |

依赖链：`usm-v9-fun-gen` 产出 step → `usm-v9-case-gen` 消费 step 生成 spec。

## 铁律

1. **Step 白名单唯一来源**：`.spec` 中 step 文案必须与 `step_impl/` 中 `@step("...")` 逐字一致
2. **不编造 step**：找不到匹配时停止生成，告知缺失
3. **不编造数据**：测试数据来自用户输入 / `data/assets.json` / `env/test.json` / 时间戳自动生成
4. **Login**: `before_suite` 自动完成，spec 中不写登录 step
5. **Test data uniqueness**: 测试数据名带时间戳（如 `autotest_ssh_20260710`）确保可重复执行
