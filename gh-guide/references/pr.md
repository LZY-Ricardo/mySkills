# pr

## 高频目标

- 查看 PR 列表
- 查看某个 PR 详情
- 基于当前分支创建 PR
- checkout 远程 PR
- 评论、review、合并或关闭 PR

## 常用命令

```bash
gh pr list
gh pr view <number>
gh pr checks <number>
gh pr diff <number>
gh pr create
gh pr checkout <number>
gh pr comment <number> --body "..."
gh pr review <number> --approve
gh pr review <number> --comment --body "..."
gh pr merge <number>
gh pr close <number>
```

## 选择规则

- 只想看状态：`gh pr list` / `gh pr view`
- 想看 CI：`gh pr checks`
- 想看变更：`gh pr diff`
- 想把远程 PR 拉到本地：`gh pr checkout`
- 想发起远程变更：`create` / `comment` / `review` / `merge` / `close`

## 安全约束

以下操作执行前必须得到用户明确确认：

- `gh pr create`
- `gh pr comment`
- `gh pr review`
- `gh pr merge`
- `gh pr close`

创建 PR 前至少确认：

- base 分支
- head 分支
- 标题与正文来源
- 目标仓库是否正确

合并 PR 前至少确认：

- PR 编号
- 合并方式（merge / squash / rebase）
- 是否需要删除分支

## 汇报重点

- PR 编号与标题
- base/head 分支
- open/closed/merged 状态
- review / checks 状态
- URL

