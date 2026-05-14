# workflow

## 高频目标

- 查看 workflow run 列表
- 查看某次 run 详情
- 跟踪执行状态
- 重跑失败 run

## 常用命令

```bash
gh run list
gh run view <run-id>
gh run watch <run-id>
gh run rerun <run-id>
gh workflow list
gh workflow view <workflow>
gh workflow run <workflow>
```

## 选择规则

- 查最近执行：`gh run list`
- 看某次执行详情：`gh run view`
- 等待某次执行完成：`gh run watch`
- 触发重新执行：`gh run rerun`
- 查看 workflow 定义：`gh workflow list` / `gh workflow view`
- 手动触发 workflow：`gh workflow run`

## 安全约束

以下操作执行前必须得到用户明确确认：

- `gh run rerun`
- `gh workflow run`

执行前至少确认：

- run id 或 workflow 名称
- 目标仓库
- 是否可能消耗 CI 配额或触发部署

## 汇报重点

- workflow / run 名称
- 分支或提交
- 结论状态（queued / in_progress / success / failure / cancelled）
- 失败步骤或失败结论
- URL

