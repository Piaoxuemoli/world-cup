---
name: bet-sync
description: Sync betting data from agents/*/round-N/bets.md into the HTML AI_ROUNDS array. Parses each model's bets.md, extracts bet entries, and updates the HTML file.
version: 1.0.0
author: QoobeeHermes
platforms: [linux]
metadata:
  hermes:
    tags: [world-cup, sync, bets, html]
    related_skills: [lottery-updater]
---

# Bet Sync

从各模型 agent 的 `bets.md` 文件同步投注方案到 HTML。

## When to Use

| 场景 | 触发方式 | 动作 |
|------|----------|------|
| 新一轮投注方案就绪 | 主动/被动 | 解析 bets.md → 同步到 HTML |
| 用户说 "同步投注" | 主动 | 执行同步流程 |
| 用户说 "某模型的方案改了" | 主动 | 重新同步该模型 |

## 执行流程

### Step 1: 拉取最新代码

```bash
cd ~/world-cup && git pull origin main
```

### Step 2: 运行同步脚本

```bash
python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/sync_bets.py --round N
```

### Step 3: 手动核对并更新 HTML

脚本会解析各模型的 bets.md，输出 JSON。将 JSON 数据手动转写为 HTML 中 `AI_ROUNDS` 的 JavaScript 对象格式。

关键转换规则：
- bets.md 中的组合对应过关票：第一条 bet 的 `amount > 0`，后续 legs 的 `amount = 0`
- 单关的 `过关: '单关'`
- `actualScore` / `result` / `prize` 留空/`'pending'`/`0`，等赛后填

### Step 4: 部署

```bash
cd ~/world-cup
cp 世界杯预测.html index.html
nginx -s reload
```

## 注意事项

1. 各模型 bets.md 格式不完全统一，需人工核对转换结果
2. Deepseek 的 v4 方案已排除 M1/M2（已过截止时间）
3. 同步后必须 `cp 世界杯预测.html index.html` 使 nginx 生效
