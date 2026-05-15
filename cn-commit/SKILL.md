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

- 首选运行脚本获取结构化信息：`python cn-commit/scripts/collect_staged_facts.py`
  - 该脚本输出 JSON：包含变更文件、状态、行数统计、顶层目录分布、文件类别、是否建议拆分提交、是否允许自动拆分、部分暂存文件、建议分组等（用于推断 scope 与写摘要/正文）。
  - 若 skill 被安装在其他目录，脚本路径应相对当前 `cn-commit/` 目录解析，而不是写死机器上的绝对路径。
- 也可以直接用 Git 命令交叉验证：
  - `git diff --cached --name-status`
  - `git diff --cached --stat`
  - 必要时：`git diff --cached`（大 diff 只按文件分段查看）

### Step 2：判断是否适合拆分提交

- 根据 `collect_staged_facts.py` 的 `analysis` 字段判断当前 staged 是否“范围较广且混合”。
- 若 `split_recommended = false`：沿用单次提交流程。
- 若 `split_recommended = true`：先展示触发原因，再询问用户三选一：
  - `一次提交`
  - `拆分提交（推荐）`
  - `暂不提交，手动整理`
- **必须由用户选择**；不能擅自进入拆分提交流程。
- 若 `can_auto_split = false`：
  - 展示 `split_blockers` 与 `partially_staged_files`
  - 说明当前存在部分暂存文件，自动拆分会误带未暂存内容
  - 只能让用户选择 `一次提交` 或 `暂不提交，手动整理`

### Step 3：推断 scope（按目录）

规则（确定性、可解释）：

- 取每个变更文件路径的“第一段目录”（例如 `app/layout.jsx` 的顶层目录是 `app`）。
- 统计顶层目录出现次数：
  - 若只有 1 个顶层目录：`scope = 该目录的小写形式`
  - 否则：`scope = 出现次数最多的顶层目录的小写形式`；若并列或无法判断：`scope = multi`
- 对根目录文件（如 `README.md`）可忽略其对 scope 的投票；若全部都是根目录文件：`scope = root`

### Step 4：选择 type（英文）

优先按变更性质推断，并允许你在确认前覆盖：

- `docs`：仅文档/注释/README 等
- `test`：仅测试
- `ci`：CI 配置
- `build`：构建/依赖
- `refactor`：重构（不改变外部行为）
- `fix`：修复缺陷
- `feat`：新增能力
- 不确定：默认 `chore`

### Step 5：生成提交信息（中文）

格式：

```
type(scope): 中文摘要（≤30字）

[可选正文：1-3 段中文，解释做了什么/为什么；小改动可省略]
```

写作要求：

- 摘要必须包含中文，且不超过 30 字。
- 摘要尽量表达“动作 + 对象 + 结果”，避免只写“更新/修复一些问题”。
- 若涉及多目录/多主题，摘要聚焦最主要变更；正文再补充次要点。

### Step 6：拆分提交流程（用户选择后）

- 若用户选择 `拆分提交（推荐）`：
  - 展示 `suggested_groups`，每组至少包含文件列表、建议 `type`、建议 `scope`、建议中文摘要。
  - 在修改暂存区之前，必须再次向用户确认是否按建议分组执行。
  - 允许用户要求跳过某组、合并某组，或改回一次提交。
  - 若用户确认按分组执行，使用脚本按组重建 index：  
    `python cn-commit/scripts/restage_split_group.py --plan-file "<path/to/facts.json>" --group-key "<group_key>"`
  - 每一组都必须单独生成 message、单独校验、单独确认、单独执行 `git commit`。
  - 每组提交后，再对下一组重复执行 `restage_split_group.py`，直到所有确认过的分组提交完成。
- 若用户选择 `暂不提交，手动整理`：
  - 直接停止，不执行任何提交动作。
- 若用户选择 `一次提交`：
  - 忽略拆分建议，继续走单次提交流程。

### Step 7：校验与确认（必须）

- 使用脚本校验 message（建议写入临时文件再校验）：  
  `python cn-commit/scripts/validate_commit_msg.py --file "<path/to/message.txt>"`
- 输出最终 message + `git diff --cached --stat` 给你审阅。
- 询问你是否继续执行本地提交；未明确确认则停止。

### Step 8：执行本地提交（确认后）

- 写入 message 文件后提交：`git commit -F "<path/to/message.txt>"`
- 提交后回显：`git show --stat --oneline -1`

## 典型效果（你会看到什么）

- 你提出“根据暂存区生成中文 commit 并提交到本地”
- 我会先展示 staged 事实（文件/统计/scope 推断/type 建议）→ 给出中文提交信息 → 让你确认 → 执行 `git commit`（不 push）→ 输出最新提交摘要
- 若 staged 变更明显混合：我会先解释为什么建议拆分，再让你选择 `一次提交 / 拆分提交（推荐） / 暂不提交，手动整理`
- 若 staged 中包含部分暂存文件：我会明确说明当前不能安全自动拆分，并列出阻塞文件

## 最小验证

- 运行 `python cn-commit/scripts/selftest.py`
- 预期结果：
  - `SKILL.md` 不包含环境绑定的绝对路径
  - `SKILL.md` 明确描述一次提交、拆分提交、手动整理三种选择
  - `validate_commit_msg.py` 能区分合法/非法提交信息
  - `collect_staged_facts.py` 能在临时 Git 仓库中读取 staged 信息、正确推断 `scope`，并对混合改动给出拆分建议
  - `restage_split_group.py` 能按建议分组重建 index
