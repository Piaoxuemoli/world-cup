---
name: branch-mgr
description: Create, manage, and clean up temporary Git branches for making isolated modifications. Supports creating feature/fix branches from main, committing changes, merging back or discarding, with automatic cleanup.
version: 1.0.0
author: QoobeeHermes
platforms: [linux, win32]
metadata:
  hermes:
    tags: [world-cup, git, branch, workflow]
    related_skills: [repo-sync]
---

# Branch Manager

在 `world-cup` 仓库中创建和管理临时 Git 分支，用于隔离修改、避免直接污染 `main` 分支。

## When to Use

| 场景 | 触发方式 | 动作 |
|------|----------|------|
| 用户说 "新建分支" / "创建临时分支" | 主动 | 从 main 创建新分支并切换 |
| 用户说 "在分支上改" / "临时修改" | 主动 | 确认在临时分支上操作 |
| 用户说 "合并到main" / "合回去" | 主动 | 合并分支到 main |
| 用户说 "放弃修改" / "丢弃分支" | 主动 | 删除分支不合并 |
| 用户说 "当前分支" / "分支状态" | 主动 | 显示分支信息 |

**Don't use for:** 直接在 main 上提交（用 repo-sync）、修改其他仓库。

## 分支命名规范

```
tmp/<描述>        # 临时修改（如 tmp/fix-odds-r1）
feat/<描述>       # 功能开发（如 feat/add-leaderboard）
fix/<描述>        # 修复（如 fix/html-encoding）
sync/<描述>       # 数据同步（如 sync/round-2-results）
```

## 执行流程

### Step 1: 创建临时分支

```bash
cd ~/world-cup
git checkout main
git pull origin main
git checkout -b tmp/<描述>
```

在 Windows 本地开发环境：
```powershell
cd C:\Users\qoobeewang\Desktop\world-cup
git checkout main
git pull origin main
git checkout -b tmp/<描述>
```

### Step 2: 在分支上修改

正常进行文件修改、编辑 HTML、更新数据等操作。

### Step 3: 提交修改

```bash
git add -A
git commit -m "<type>(<scope>): <描述>"
```

commit message 格式遵循 AGENTS.md 规范：
- type: `feat` / `fix` / `docs` / `sync`
- scope: 轮次名或模块名
- 示例：`sync(round-1): 同步deepseek v4方案`

### Step 4: 合并回 main

```bash
git checkout main
git pull origin main
git merge tmp/<描述>
git push origin main
```

### Step 5: 清理分支

```bash
git branch -d tmp/<描述>    # 已合并 → 安全删除
git branch -D tmp/<描述>    # 未合并 → 强制删除（放弃修改）
```

### Step 6: 部署（如需）

```bash
cd ~/world-cup
cp 世界杯预测.html index.html
# Caddy 环境：
docker cp index.html colosseum-caddy-1:/srv/world-cup/index.html
docker exec colosseum-caddy-1 caddy reload --config /etc/caddy/Caddyfile
# 或 nginx 环境：
nginx -s reload
```

## 注意事项

1. **始终从最新 main 创建分支**，避免合并冲突
2. **临时分支生命周期要短**，改完即合即删
3. **合并前先 pull**，确保 main 是最新的
4. **冲突处理**：若合并有冲突，先 `git diff` 查看冲突，手动解决后再提交
5. **不要推送临时分支到远端**，除非需要跨机器协作
6. **Git 身份**：QoobeeHermes 的提交身份为 `QoobeeHermes <qoobeehermes@worldcup2026>`

## 快速参考

| 操作 | 命令 |
|------|------|
| 列出分支 | `git branch -a` |
| 当前分支 | `git branch --show-current` |
| 切换分支 | `git checkout <branch>` |
| 创建+切换 | `git checkout -b <branch>` |
| 删除已合并分支 | `git branch -d <branch>` |
| 强制删除分支 | `git branch -D <branch>` |
| 查看未合并改动 | `git diff main...HEAD` |
| 撤销未提交改动 | `git checkout -- .` |
