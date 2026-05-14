---
name: gh-guide
description: Use GitHub CLI safely for PRs, issues, repos, workflows, and auth checks.
---

# gh-guide

## Overview

在任务需要使用 GitHub CLI（`gh`）时使用本 skill。它负责三件事：

1. 先确认上下文与认证状态
2. 为当前目标选择合适的 `gh` 子命令
3. 在执行后以开发者可读的方式汇总结果

本 skill 面向代理执行，不是面向终端新手的完整教程。

## When to Use

当任务涉及以下任一情况时触发：

- 需要查看、创建、编辑或合并 PR
- 需要查看、创建、评论、关闭或重开 issue
- 需要查看仓库信息、fork、clone、默认仓库设置
- 需要查看、重跑、跟踪 GitHub Actions workflow
- 需要确认 `gh` 登录状态、账号、主机或 token 情况
- 需要决定“这里该用 `git` 还是 `gh`”

以下情况不要优先使用本 skill：

- 只涉及本地工作区、分支、提交、暂存区、diff：优先 `git`
- 只需要浏览本地文件：直接用文件系统工具
- 远程操作可以通过现有 MCP 直接完成且更稳：优先 MCP

## Core Rules

### 1. 先分清 `git` 与 `gh`

- `git` 负责本地仓库状态与提交历史
- `gh` 负责 GitHub 远程实体与账号上下文
- 不要用 `gh` 代替本地 `git status`、`git diff`、`git log`

### 2. 永远先做最小预检查

在首次使用 `gh` 前，按需执行：

```bash
gh --version
gh auth status
```

在任务依赖当前仓库上下文时，再补充：

```bash
git remote -v
gh repo view
```

如果 `gh auth status` 显示未登录、主机不匹配、权限不足或 token 作用域不足，先向用户说明，再决定是否继续。

### 3. 默认优先只读

优先选择不会改变远程状态的命令，例如：

- `gh pr list`
- `gh pr view`
- `gh issue list`
- `gh issue view`
- `gh repo view`
- `gh run list`
- `gh run view`

只有在用户目标明确且操作范围清楚时，才进入写操作。

### 4. 写操作必须显式确认

对 GitHub 远程状态产生持久影响的操作，执行前必须得到用户明确确认。典型场景：

- `gh pr create`
- `gh pr merge`
- `gh pr close`
- `gh issue create`
- `gh issue close`
- `gh issue reopen`
- `gh issue comment`
- `gh pr comment`
- `gh run rerun`
- 修改仓库设置、创建 release、删除远程资源

确认时要说明：

- 操作类型
- 影响范围
- 潜在风险
- 需要用户明确回复“是”“确认”或“继续”

### 5. 输出必须是结论，不是命令回放

用户通常不需要完整命令输出。应提炼关键信息、状态、链接、失败原因和下一步建议。

## Command Selection

按目标选择主题参考文件：

- 认证与账号：读 [references/auth.md](references/auth.md)
- PR：读 [references/pr.md](references/pr.md)
- Issue：读 [references/issue.md](references/issue.md)
- Workflow / Actions：读 [references/workflow.md](references/workflow.md)
- 仓库与远程：读 [references/repo.md](references/repo.md)

如果以上子命令都不合适，但任务仍明确属于 GitHub CLI，可以考虑：

```bash
gh help
gh <subcommand> --help
gh api
```

只有在标准子命令不足以覆盖需求时再使用 `gh api`，并优先选择只读调用。

## Response Templates

### 查询类结果

```text
结论：<一句话说明当前状态>
关键信息：<编号/标题/分支/作者/状态/时间>
链接：<GitHub URL>
下一步：<可选，只有在确实需要动作时提供>
```

### 变更类结果

```text
已执行：<具体动作>
影响对象：<PR/issue/workflow/repo>
结果：<成功/失败 + 关键结果>
链接：<GitHub URL，如有>
备注：<失败原因或后续建议，如需要>
```

### 失败类结果

```text
结果：未完成。
原因：<真实失败原因>
影响范围：<未产生变更 / 可能已部分生效>
建议：<最小下一步>
```

## Practical Heuristics

- 先查询，再修改；先单项查看，再批量操作
- 处理 PR / issue 前，优先带编号，避免歧义
- 当仓库上下文不明确时，优先显式指定 `-R owner/repo`
- 当结果要写进回复时，优先抽取标题、编号、状态、作者、URL、时间
- 不要把大段 CLI 原始输出直接贴给用户，除非用户明确要求

