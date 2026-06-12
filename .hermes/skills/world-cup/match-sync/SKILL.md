---
name: match-sync
description: Automatically fetch latest World Cup 2026 match information and results, then update the 世界杯预测.html file. Covers match schedule sync, result fetching, AI_ROUNDS updates, prize calculation, and leaderboard refresh.
version: 1.0.0
author: QoobeeHermes
platforms: [linux, win32]
metadata:
  hermes:
    tags: [world-cup, match, results, html-update, sync]
    related_skills: [lottery-updater, bet-sync, repo-sync]
---

# Match Sync

自动拉取最新比赛信息并更新 HTML 展示页面。整合赔率获取、赛果拉取、奖金计算、排行榜刷新为一条龙流程。

## When to Use

| 场景 | 触发方式 | 动作 |
|------|----------|------|
| 用户说 "更新比赛" / "拉取赛果" | 主动 | 抓取最新赛果 → 更新 HTML |
| 用户说 "刷新排行榜" / "更新排行" | 主动 | 重算奖金 → 更新排行榜 |
| 用户说 "同步第N轮" | 主动 | 完整同步指定轮次 |
| 用户说 "比赛信息更新" | 主动 | 拉取赛程/赔率/赛果 |
| cron 定时触发 | 被动 | 自动检查已结束比赛 |

**Don't use for:** 修改投注策略（由各模型 agent 完成）、创建 round 目录（由人工触发）。

## 数据源

### 赛果来源（按优先级）
1. **ESPN API** (`site.api.espn.com`) — 快速、结构化 JSON
2. **FIFA 官方** (`fifa.com`) — 最权威，但解析复杂
3. **球探网** (`win007.com`) — 中文快速源

### 赔率来源
1. **中国竞彩网** (`sporttery.cn`) — 官方赔率
2. **500彩票网** (`500.com`) — 备用源

## 完整执行流程

### Step 1: 拉取最新代码

```bash
cd ~/world-cup && git pull origin main
```

### Step 2: 抓取最新赛果

```bash
python3 ~/world-cup/.hermes/skills/world-cup/match-sync/scripts/fetch_match_info.py --round N
```

脚本会：
1. 调用 ESPN API 获取世界杯已完成比赛
2. 与 HTML 中 `AI_ROUNDS` 的 matchId 匹配
3. 输出 JSON 格式的赛果

### Step 3: 更新 HTML AI_ROUNDS

```bash
python3 ~/world-cup/.hermes/skills/world-cup/match-sync/scripts/update_match_data.py --round N --input results.json
```

更新逻辑：
1. 读取 `世界杯预测.html`，定位 `AI_ROUNDS` 数组
2. 对每个已出结果的 match：
   - 设置 `actualScore` 为实际比分
   - 判定 `result`：胜平负比对 pick；过关票需所有腿都赢
   - 计算 `prize`：
     - **过关票**：`赔率1 × 赔率2 × ... × 2元 × (amount/2)`（首腿 amount 为整票金额）
     - **单关**：`赔率 × 2元 × (amount/2)`
   - 设置 `result` = `'win'` 或 `'loss'`
3. 若该轮所有 bet 都有结果 → `status = 'completed'`
4. 写回 HTML

### Step 4: 验证更新

```bash
python3 ~/world-cup/.hermes/skills/world-cup/match-sync/scripts/verify_html.py
```

验证项：
- AI_ROUNDS JSON 语法正确
- 所有 model 的 bets 数量与原始一致
- prize 计算可验证
- status 与 results 一致

### Step 5: 提交并部署

```bash
cd ~/world-cup
git add 世界杯预测.html
git commit -m "sync(round-N): 更新第N轮赛果"
git push origin main
cp 世界杯预测.html index.html
```

Caddy 部署：
```bash
docker cp index.html colosseum-caddy-1:/srv/world-cup/index.html
docker exec colosseum-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

## 奖金计算规则

### 过关票（2×1, 3×1 等）
```
奖金 = 腿1赔率 × 腿2赔率 × ... × 腿N赔率 × 2元 × 倍数
倍数 = amount / 2
```
所有腿都赢才算赢，任一腿输则整票输。

### 单关
```
奖金 = 赔率 × 2元 × 倍数
倍数 = amount / 2
```

### 结果判定
- **胜平负**：主队得分 > 客队 → 主胜；= → 平；< → 客胜
- **让球胜平负**：主队得分 + 让球数 与 客队得分比较
- 比对 bet 的 `pick` 字段判断输赢

## HTML 数据结构参考

```javascript
const AI_ROUNDS = [
  {
    round: 1,
    title: '小组赛第1轮',
    dateRange: '6月12日 — 6月18日',
    status: 'active',  // 'active' | 'completed'
    predictions: {
      deepseek: {
        analysis: '...',
        strategy: '...',
        bets: [
          {
            match: '德国 vs 库拉索',
            matchId: 'M9',
            playType: '胜平负',
            pick: '主胜',
            amount: 60,
            odds: 1.12,
            过关: '2×1',
            actualScore: '',     // 赛后填入 '4:0'
            result: 'pending',   // 'win' | 'loss' | 'pending'
            prize: 0,            // 赛后计算
          },
        ],
      },
    },
  },
];
```

## 赛程匹配规则

HTML 中比赛表格的 matchId（M1-M72）与 ESPN 数据的匹配：
1. 优先通过队伍名称精确匹配
2. 无法精确匹配时，按日期+组别辅助匹配
3. 匹配映射表在脚本中维护

## 注意事项

1. **购彩时间**：体彩店 11:00-22:00（工作日）/ 11:00-23:00（周末）
2. **赔率变动**：竞彩赔率随投注量浮动，以出票时为准
3. **北京时间**：所有时间 UTC+8
4. **M1/M2 已截止**：第1轮这两场早于购彩时间
5. **HTML 更新前备份**：建议先 `cp 世界杯预测.html 世界杯预测.html.bak`
6. **ESPN API 可能不稳定**：失败时使用备用源或手动输入
