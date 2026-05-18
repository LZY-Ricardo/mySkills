# AI Skills Guide

本文件是仓库级总入口，用于说明当前仓库中的所有 AI skill、各自目录内容、适用场景，以及未来新增 skill 时建议遵循的统一模板。

## 1. 仓库定位

这个仓库不是业务代码仓库，而是一个个人 AI skill 仓库。

每个顶层目录通常代表一个独立 skill。一个 skill 可以包含：

- `SKILL.md`：skill 的核心说明文件，必需
- `agents/`：给特定代理平台使用的入口配置
- `scripts/`：配套脚本或命令行工具
- `references/`：参考资料、子主题说明
- `examples/`：示例输入、输出或使用方式
- `assets/`：图片、模板等资源文件

当前仓库中的 skill 既包含“具体动作型能力”，也包含“流程控制型能力”。

## 2. 当前 Skill 总览

| Skill | 类型 | 主要用途 | 目录特征 |
| --- | --- | --- | --- |
| `chrome-cdp` | 工具型 | 连接本地 Chrome 会话并执行调试/截图/交互 | `SKILL.md` + `scripts/` |
| `cn-commit` | 工具型 | 基于 Git 暂存区生成中文规范提交信息 | `SKILL.md` + `agents/` + `scripts/` |
| `code-reviewer` | 流程型 | 在完成前做独立代码审查并给出结论 | `SKILL.md` + `agents/` |
| `context-compression` | 流程型 | 压缩长上下文，便于继续执行或交接 | `SKILL.md` + `agents/` + `examples.md` |
| `full-auto-executor` | 流程型 | 高自治地把任务一路执行到完成或受阻 | `SKILL.md` + `agents/` |
| `gh-guide` | 工具型 | 安全使用 GitHub CLI 完成远程操作 | `SKILL.md` + `agents/` + `references/` |
| `safe-auto-executor` | 流程型 | 在安全边界内持续推进任务 | `SKILL.md` + `agents/` |

## 3. Skill 目录详解

### 3.1 `chrome-cdp`

**目录内容**

```text
chrome-cdp/
  SKILL.md
  scripts/
    cdp.mjs
    daemon-ipc.mjs
    daemon-ipc.selftest.mjs
```

**核心定位**

这是一个面向本地 Chrome/Chromium 会话的调试与自动化 skill。它通过 Chrome DevTools Protocol 直接连接浏览器标签页，不依赖 Puppeteer，更偏向“轻量、直接、快速”的浏览器控制方式。

**适用场景**

- 需要查看当前打开的浏览器页面
- 需要截图、抓取 HTML、查看无障碍树
- 需要在页面中执行 JavaScript
- 需要点击、输入、导航、查看资源加载情况

**目录说明**

- `SKILL.md`：说明如何启用远程调试、支持哪些命令、如何处理坐标和 DPR
- `scripts/cdp.mjs`：主命令入口
- `scripts/daemon-ipc.mjs`：后台守护进程通信逻辑
- `scripts/daemon-ipc.selftest.mjs`：自测脚本

**特点**

- 偏执行型 skill
- 强依赖本地浏览器环境
- 适合页面调试、人工辅助操作、浏览器内验证

### 3.2 `cn-commit`

**目录内容**

```text
cn-commit/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    collect_staged_facts.py
    example.py
    restage_split_group.py
    selftest.py
    validate_commit_msg.py
```

**核心定位**

这是一个中文规范提交 skill，目标是把 Git 暂存区中的事实信息转成一条可读、可追踪、可审计的中文 Conventional Commit，并在用户确认后执行本地提交。

**适用场景**

- 已经完成 `git add`，想自动生成中文提交信息
- 想根据 staged diff 推断 `type`、`scope`、摘要和正文
- 想判断当前暂存区是否适合拆分提交

**目录说明**

- `SKILL.md`：定义提交信息约束、scope 推断规则、拆分提交流程、确认机制
- `agents/openai.yaml`：给代理平台的入口配置，例如展示名和默认 prompt
- `scripts/collect_staged_facts.py`：提取 staged 事实并输出结构化信息
- `scripts/validate_commit_msg.py`：校验提交信息格式
- `scripts/restage_split_group.py`：辅助拆分提交时重新暂存分组
- `scripts/selftest.py`：技能相关自检
- `scripts/example.py`：示例脚本

**特点**

- 是当前仓库里工程化程度较高的 skill
- 同时包含文档、脚本和 agent 入口
- 既有规则，也有落地执行工具

### 3.3 `code-reviewer`

**目录内容**

```text
code-reviewer/
  SKILL.md
  agents/
    openai.yaml
```

**核心定位**

这是一个独立审查角色 skill。它不负责改代码，而是专注于检查变更风险，输出结构化 findings，并给出 `PASS`、`FLAG` 或 `BLOCK` 结论。

**适用场景**

- 用户明确要求 code review
- 重要提交前想做一次风险审查
- 改动涉及共享模块、接口、权限、数据写入等高风险区域

**目录说明**

- `SKILL.md`：定义何时触发、关注什么、输出格式、结论规则
- `agents/openai.yaml`：让该 skill 可以作为独立 reviewer 入口被调用

**特点**

- 偏治理和质量控制
- 适合与实现类 skill 配合使用
- 目标不是“改”，而是“审”

### 3.4 `context-compression`

**目录内容**

```text
context-compression/
  SKILL.md
  agents/
    openai.yaml
  examples.md
```

**核心定位**

这是一个上下文压缩 skill，用于在长对话、长日志、多文件任务中提取最耐用的信息，形成可继续工作的短摘要。

**适用场景**

- 会话很长，已经积累了很多上下文
- 需要切换子任务或准备交接
- 需要给后续 agent 或后续轮次一个简洁 continuation brief

**目录说明**

- `SKILL.md`：定义压缩目标、触发时机、保留信息优先级、输出模板
- `agents/openai.yaml`：允许作为单独能力入口被调用
- `examples.md`：提供压缩结果示例或格式参考

**特点**

- 偏记忆管理和任务续航
- 很适合作为复杂任务中的辅助型基础设施 skill

### 3.5 `full-auto-executor`

**目录内容**

```text
full-auto-executor/
  SKILL.md
  agents/
    openai.yaml
```

**核心定位**

这是一个高自治执行模式 skill。它强调代理自己规划、实现、验证、重试，尽量不中途打断用户，直到任务完成或遇到客观阻塞。

**适用场景**

- 用户明确要求“你自己一路做完”
- 任务需要自主循环执行而不是频繁确认
- 适合清晰目标、较强执行链路的编码或仓库任务

**目录说明**

- `SKILL.md`：定义自动执行循环、停止条件、决策边界和完成标准
- `agents/openai.yaml`：为代理提供默认入口说明

**特点**

- 偏执行编排
- 自主性强
- 适合明确目标、低歧义任务

### 3.6 `gh-guide`

**目录内容**

```text
gh-guide/
  SKILL.md
  agents/
    openai.yaml
  references/
    auth.md
    issue.md
    pr.md
    repo.md
    workflow.md
```

**核心定位**

这是一个 GitHub CLI 使用规范 skill，用于在涉及 GitHub 远程实体时，帮助代理区分该用 `git` 还是 `gh`，并在执行前做最小预检查和风险控制。

**适用场景**

- 查看、创建、编辑 PR
- 查看或处理 issue
- 查看仓库远端信息
- 查看、跟踪或重跑 GitHub Actions workflow
- 检查 `gh` 登录、主机、权限、token 状态

**目录说明**

- `SKILL.md`：总规则、触发时机、预检查方式、写操作确认原则
- `agents/openai.yaml`：将此 skill 暴露为可调用入口
- `references/auth.md`：认证相关参考
- `references/issue.md`：issue 相关参考
- `references/pr.md`：PR 相关参考
- `references/repo.md`：仓库相关参考
- `references/workflow.md`：workflow 相关参考

**特点**

- 面向 GitHub 远端操作
- 强调安全边界和显式确认
- 适合作为 `gh` 命令的操作守则

### 3.7 `safe-auto-executor`

**目录内容**

```text
safe-auto-executor/
  SKILL.md
  agents/
    openai.yaml
```

**核心定位**

这是一个“保守版自动执行” skill。它与 `full-auto-executor` 类似，但更强调在安全边界内持续推进，遇到高风险动作才停下来询问用户。

**适用场景**

- 用户希望尽量少打断，但又不想放开全部高风险动作
- 任务需要连续推进，但仍需保留关键确认点
- 适合大多数常规仓库工作流

**目录说明**

- `SKILL.md`：定义默认工作流、什么时候继续、什么时候必须停下询问
- `agents/openai.yaml`：提供独立执行模式入口

**特点**

- 是“自动执行”和“安全控制”的折中方案
- 比 `full-auto-executor` 更适合日常任务

## 4. `agents/`、`scripts/`、`references/` 的通用含义

为了后续扩展统一，建议按下面的理解使用目录：

- `agents/`
  - 放代理平台适配配置
  - 常见内容包括展示名、简短说明、默认 prompt、是否允许隐式触发

- `scripts/`
  - 放 skill 配套脚本
  - 适用于解析、校验、自测、CLI 执行入口等

- `references/`
  - 放不适合写进主 `SKILL.md` 的补充文档
  - 适用于子主题说明、命令手册、策略拆分

- `examples/`
  - 放输入输出示例、调用示例、演示数据

- `assets/`
  - 放图示、模板、图片或其他资源文件

## 5. 未来新增 Skill 的推荐模板

以后新增 skill 时，建议至少保持下面的目录结构：

```text
my-skill/
  SKILL.md
```

如果 skill 稍复杂，推荐结构：

```text
my-skill/
  SKILL.md
  agents/
    openai.yaml
  scripts/
  references/
  examples/
```

### 5.1 `SKILL.md` 推荐结构

```md
---
name: my-skill
description: 用一句话说明这个 skill 的用途
---

# My Skill

## Overview

说明这个 skill 解决什么问题。

## When to Use

- 触发场景 1
- 触发场景 2

## Core Rules

- 规则 1
- 规则 2

## Workflow

1. 第一步
2. 第二步
3. 第三步

## Output

说明输出格式、结论结构或执行结果要求。
```

### 5.2 `agents/openai.yaml` 推荐结构

```yaml
interface:
  display_name: "My Skill"
  short_description: "一句话短描述"
  default_prompt: "Use $my-skill to ..."

policy:
  allow_implicit_invocation: true
```

### 5.3 新增 Skill 时建议补充到本文件的信息

当新增一个 skill 时，建议同步更新本文件中的以下内容：

1. 在“当前 Skill 总览”表格中新增一行
2. 在“Skill 目录详解”中新增一个独立小节
3. 写清楚该 skill 的：
   - 核心定位
   - 适用场景
   - 目录内容
   - 关键文件作用
   - 与其他 skill 的关系

## 6. 建议的维护规则

- 每新增一个 skill，优先先写好 `SKILL.md`
- 只在确实需要平台入口时新增 `agents/`
- 只在确实需要执行逻辑时新增 `scripts/`
- 如果一个 skill 规则很多，优先把主流程留在 `SKILL.md`，把专题细节拆到 `references/`
- 本文件应保持“能快速理解全仓库”的目标，不适合写过细实现细节

## 7. 新增 Skill 检查清单

以后每新增一个 skill，建议至少逐项检查下面这些内容：

- [ ] skill 目录名是否使用小写 kebab-case
- [ ] 是否包含必需文件 `SKILL.md`
- [ ] `SKILL.md` 是否写清楚用途、触发场景、核心规则、工作流、输出要求
- [ ] 是否需要 `agents/openai.yaml` 作为平台入口
- [ ] 如果有脚本，是否放入 `scripts/` 并命名清晰
- [ ] 如果有补充说明，是否拆入 `references/` 或 `examples/`
- [ ] 是否把新 skill 补充进本文件的“当前 Skill 总览”
- [ ] 是否为该 skill 增加“Skill 目录详解”小节
- [ ] 是否验证过文档内容与真实目录结构一致
- [ ] 如果 skill 行为可执行，是否至少有一个可本地验证的示例或自检方式

## 8. 当前仓库的整体判断

从现状看，这个仓库已经形成了两类 skill：

- **执行/工具类**：`chrome-cdp`、`cn-commit`、`gh-guide`
- **流程/治理类**：`code-reviewer`、`context-compression`、`full-auto-executor`、`safe-auto-executor`

这说明仓库方向已经比较清晰：不是单纯堆命令，而是在搭建一套 AI 代理的个人工作系统。
