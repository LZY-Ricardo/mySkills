# issue

## 高频目标

- 查看 issue 列表
- 查看某个 issue
- 创建、评论、关闭、重开 issue

## 常用命令

```bash
gh issue list
gh issue view <number>
gh issue create
gh issue comment <number> --body "..."
gh issue close <number>
gh issue reopen <number>
```

## 选择规则

- 需要快速浏览：`gh issue list`
- 需要完整上下文：`gh issue view`
- 需要远程变更：`create` / `comment` / `close` / `reopen`

## 安全约束

以下操作执行前必须得到用户明确确认：

- `gh issue create`
- `gh issue comment`
- `gh issue close`
- `gh issue reopen`

创建 issue 前至少确认：

- 标题
- 描述
- 目标仓库

关闭或重开前至少确认：

- issue 编号
- 目标状态
- 是否需要说明原因

## 汇报重点

- issue 编号与标题
- open / closed 状态
- 作者
- 标签、assignee、milestone（如 relevant）
- URL

