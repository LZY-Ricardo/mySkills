# auth

## 目标

确认 `gh` 是否可用、当前登录到哪个主机/账号、是否具备执行当前任务所需权限。

## 常用命令

```bash
gh --version
gh auth status
gh auth token
gh auth login
gh auth logout
gh auth refresh
gh auth switch
```

## 使用规则

- 默认先用 `gh auth status`，不要直接假设已登录
- `gh auth token` 只在明确需要 token 转交给别的命令时使用，不要在回复中泄露 token
- 发现 host 不符时，明确写出当前 host，例如 `github.com` 或企业 GitHub 域名
- 如果权限不足，先报告缺的范围，不要盲目重试写操作

## 常见场景

### 检查登录状态

```bash
gh auth status
```

适合开始任何需要远程 GitHub 能力的任务前执行。

### 重新登录或切换账号

```bash
gh auth login
gh auth switch
```

适合当前账号不对、host 不对、token 过期。

### 刷新权限

```bash
gh auth refresh
```

适合已有登录但 scope 不满足当前操作。

## 汇报重点

- 是否已登录
- 登录到哪个 host
- 当前活跃账号是谁
- 是否满足当前任务权限

