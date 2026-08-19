# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目说明
本项目是一套基于AI驱动的前端测试框架,使用fun-gen skill将页面功能沉淀为gauge step,通过case-gen生成前端自动化用例

## 技术栈

- 环境 python3.12 + uv(环境管理) + Gauge BDD
- 核心库
    - getgauge
    - playwright
- 代码规范
    - 严格使用typing模块

## 项目结构

| 目录                    | 用途                                                                  |
|-----------------------|---------------------------------------------------------------------| 
| `configs/`            | **配置目录**`router.json`为路由文件,命名规则为 管理控制台-L2-L3`或`个人工作台-L2-L3`，概览页面无L3 | 
| `step_impl/`          | **gauge 沉淀 step** 按L2-目录进行沉淀                                        |         
| `import_file_library` | 用于系统导入的一些数据文件                                                       |
| `test_assets/`        | **存放测试资产目录**常用的测试资产存放在此处。                                           |
| `specs/`              | **用例存放目录** index.md为用例生成的索引文件                                       |
| `utils/`              | **核心公共方法库**存放一些核心的公共方法                                              |
| `scripts/`            | 脚本存放目录                                                              |
| `rules/`              | **规则目录**存放某些步骤需要遵循的规则                                               |
| `docx`                | **文档存放目录**业务或知识参考文件存放于此                                             |
| `workspace/`          | **智能体工作目录**启动claude时,会在该目录下同步创建会话目录，所有生成临时代码文件都放在对应目录下              |
## 常用命令

```bash
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
| `fun-gen` | 浏览器探索 → 沉淀功能为参数化 Python 方法 → 转化为 `step_impl/` 的 `@step` |
| `case-gen` | 从 `step_impl/` 白名单组合 step → 生成 `.spec` 用例（绝不编造 step） |
| `playwright-cli` | 浏览器自动化（打开、点击、填充、截图、trace） |

依赖链：`fun-gen` 产出 step → `usm-v9-case-gen` 消费 step 生成 spec。

## 铁律

1. 所有**中途生成**的工作临时文件、探索脚本都必须严格放置在workspace对应的目录中
