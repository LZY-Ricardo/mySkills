---
name: cn-commit
description: 根据 Git 暂存区生成中文 Conventional Commit，并在确认后执行本地提交。
---

# cn-commit（中文规范提交）

## Overview（概览）

该 skill 用于把“暂存区事实”转成可读、可追踪、可审计的中文提交信息，并在确认后完成本地提交。

## 约束（必须满足）

- `type` 用英文，并限定为常见 Conventional Commits：`feat|fix|docs|refactor|chore|test|perf|build|ci|style|revert`。
- 摘要与正文使用中文（允许夹杂技术名词/路径/代码符号）；摘要必须包含至少 1 个中文字符。
- 摘要长度：**≤30 个字符**（只统计 `type(scope): ` 之后的摘要文本）。
- `scope` 从目录推断（见下方规则），统一使用小写；无法唯一确定时用 `multi`。
- 小改动允许只写标题（无正文）；大改动建议补一段中文正文说明“做了什么/为什么”。
- **提交动作需要你明确确认**：在执行 `git commit` 前，必须展示最终 message，并等待你回复“确认/继续/是”之一。
- 只做本地提交：不执行 `git push`、不修改远端。

## Workflow（工作流）

### Step 0：预检查

- 确认处于 Git 仓库：`git rev-parse --is-inside-work-tree`
- 确认存在暂存区变更：`git diff --cached --quiet`（退出码非 0 表示有变更）
  - 若没有暂存变更：提示用户先 `git add -p` 或 `git add <files>`，然后再继续。

### Step 1：读取暂存区事实（只看 staged）

- 首选运行脚本获取结构化信息：`python "C:/Users/lenovo/.codex/skills/cn-commit/scripts/collect_staged_facts.py"`
  - 该脚本输出 JSON：包含变更文件、状态、行数统计、顶层目录分布等（用于推断 scope 与写摘要/正文）。
- 也可以直接用 Git 命令交叉验证：
  - `git diff --cached --name-status`
  - `git diff --cached --stat`
  - 必要时：`git diff --cached`（大 diff 只按文件分段查看）

### Step 2：推断 scope（按目录）

规则（确定性、可解释）：

- 取每个变更文件路径的“第一段目录”（例如 `app/layout.jsx` 的顶层目录是 `app`）。
- 统计顶层目录出现次数：
  - 若只有 1 个顶层目录：`scope = 该目录的小写形式`
  - 否则：`scope = 出现次数最多的顶层目录的小写形式`；若并列或无法判断：`scope = multi`
- 对根目录文件（如 `README.md`）可忽略其对 scope 的投票；若全部都是根目录文件：`scope = root`

### Step 3：选择 type（英文）

优先按变更性质推断，并允许你在确认前覆盖：

- `docs`：仅文档/注释/README 等
- `test`：仅测试
- `ci`：CI 配置
- `build`：构建/依赖
- `refactor`：重构（不改变外部行为）
- `fix`：修复缺陷
- `feat`：新增能力
- 不确定：默认 `chore`

### Step 4：生成提交信息（中文）

格式：

```
type(scope): 中文摘要（≤30字）

[可选正文：1-3 段中文，解释做了什么/为什么；小改动可省略]
```

写作要求：

- 摘要必须包含中文，且不超过 30 字。
- 摘要尽量表达“动作 + 对象 + 结果”，避免只写“更新/修复一些问题”。
- 若涉及多目录/多主题，摘要聚焦最主要变更；正文再补充次要点。

### Step 5：校验与确认（必须）

- 使用脚本校验 message（建议写入临时文件再校验）：  
  `python "C:/Users/lenovo/.codex/skills/cn-commit/scripts/validate_commit_msg.py" --file "<path/to/message.txt>"`
- 输出最终 message + `git diff --cached --stat` 给你审阅。
- 询问你是否继续执行本地提交；未明确确认则停止。

### Step 6：执行本地提交（确认后）

- 写入 message 文件后提交：`git commit -F "<path/to/message.txt>"`
- 提交后回显：`git show --stat --oneline -1`

## 典型效果（你会看到什么）

- 你提出“根据暂存区生成中文 commit 并提交到本地”
- 我会先展示 staged 事实（文件/统计/scope 推断/type 建议）→ 给出中文提交信息 → 让你确认 → 执行 `git commit`（不 push）→ 输出最新提交摘要
