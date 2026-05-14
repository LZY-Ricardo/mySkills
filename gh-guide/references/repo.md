# repo

## 高频目标

- 查看当前仓库或远程仓库信息
- clone / fork 仓库
- 设置默认仓库上下文

## 常用命令

```bash
gh repo view
gh repo view <owner/repo>
gh repo clone <owner/repo>
gh repo fork
gh repo set-default <owner/repo>
```

## 选择规则

- 查看仓库摘要：`gh repo view`
- 拉取远程仓库：`gh repo clone`
- 基于当前仓库建立 fork：`gh repo fork`
- 后续命令都指向固定仓库：`gh repo set-default`

## 安全约束

以下操作执行前建议确认用户意图：

- `gh repo fork`
- `gh repo set-default`

如果命令会改变后续默认目标仓库或创建新的远程仓库，必须明确告知影响范围。

## 汇报重点

- 仓库全名
- 默认分支
- 可见性
- 当前默认目标仓库是否被改变
- URL

