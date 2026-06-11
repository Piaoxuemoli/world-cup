---
name: lottery-updater
description: Automatically fetch China Sports Lottery (竞彩足球) odds, match results, and betting data, then update the 世界杯预测.html file. Covers odds scraping, result verification, HTML AI_ROUNDS sync, and nginx reload.
version: 1.0.0
author: QoobeeHermes
platforms: [linux]
metadata:
  hermes:
    tags: [world-cup, lottery, odds, results, html-update]
    related_skills: [bet-sync]
---

# Lottery Updater

自动拉取体彩竞彩足球赔率与赛果，更新 HTML 展示页面。

## When to Use

| 场景 | 触发方式 | 动作 |
|------|----------|------|
| 用户说 "更新赔率" / "拉取最新赔率" | 主动 | 抓取竞彩赔率 → 更新 HTML |
| 用户说 "更新赛果" / "比赛结果出来了" | 主动 | 抓取赛果 → 更新 AI_ROUNDS result/prize |
| 用户说 "同步投注" / "同步bets" | 主动 | 从 agents/*/round-N/bets.md 同步到 HTML |
| cron 定时触发 | 被动 | 自动检查是否有已结束比赛需更新 |
| 用户说 "刷新页面" | 主动 | git pull + nginx reload |

**Don't use for:** 修改投注策略（由各模型 agent 完成）、创建新的 round 目录（由人工触发）。

## 数据源

### 赔率来源
1. **中国竞彩网** (sporttery.cn) — 官方赔率，最权威
2. **500彩票网** (500.com) — 竞彩赔率备用源
3. **oddspedia.com** — 国际赔率对比参考

### 赛果来源
1. **FIFA 官方** (fifa.com) — 最权威
2. **ESPN** (espn.com) — 快速更新
3. **懂球帝 / 虎扑** — 中文快速源

## 执行流程

### Step 1: 拉取最新代码

```bash
cd ~/world-cup && git pull origin main
```

### Step 2: 抓取赔率（赛前）

```bash
python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/fetch_odds.py --round N
```

输出格式：
```json
{
  "round": 1,
  "matches": [
    {"matchId": "M3", "home": "加拿大", "away": "波黑", "odds": {"win": 2.20, "draw": 3.10, "lose": 2.90}}
  ]
}
```

赔率更新到 HTML 中对应 bet 的 odds 字段。

### Step 3: 抓取赛果（赛后）

```bash
python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/fetch_results.py --round N
```

输出格式：
```json
{
  "round": 1,
  "results": [
    {"matchId": "M3", "score": "2:1", "home": "加拿大", "away": "波黑"}
  ]
}
```

### Step 4: 更新 HTML

```bash
python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/update_html.py --round N --results results.json
```

更新逻辑：
1. 读取 `世界杯预测.html` 中 `AI_ROUNDS` 数组
2. 对每个已出结果的 match：
   - 设置 `actualScore` 为实际比分
   - 计算 `result`：过关票需检查所有腿是否都赢；单关只看单场
   - 计算 `prize`：过关票 `赔率连乘 × 2 × 倍数`；单关 `赔率 × 2 × 倍数`
3. 更新 `status`：若该轮所有 bet 都有结果 → `'completed'`
4. 写回 HTML

### Step 5: 同步 agents 投注方案

```bash
python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/sync_bets.py --round N
```

从 `agents/*/round-N/bets.md` 解析各模型投注方案，同步到 HTML `AI_ROUNDS` 对应的 predictions。

### Step 6: 提交并部署

```bash
cd ~/world-cup
git add 世界杯预测.html
git commit -m "feat: 更新第N轮赛果/赔率"
git push origin main
cp 世界杯预测.html index.html
```

### Step 7: 重新加载 nginx

```bash
nginx -s reload
```

## 赔率计算公式

### 过关票奖金
```
奖金 = 腿1赔率 × 腿2赔率 × ... × 腿N赔率 × 2元 × 倍数
```
赔率连乘先精确到分（保留两位小数），再乘倍数。

### 单关奖金
```
奖金 = 赔率 × 2元 × 倍数
```

### 结果判定
- **胜平负**：主胜/平/客胜 → 比对 pick 字段
- **让球胜平负**：根据让球数调整比分后判定
- **过关票**：所有腿都 win → 整张票 win；任一腿 loss → 整张票 loss
- **单关**：只看单场结果

## HTML 数据结构参考

```javascript
const AI_ROUNDS = [
  {
    round: 1,
    title: '小组赛第1轮',
    dateRange: '6月12日 — 6月18日',
    status: 'active',
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
            actualScore: '4:0',
            result: 'win',
            prize: 104.40,
          },
        ],
      },
    },
  },
];
```

## 注意事项

1. **购彩时间**：体彩店销售时间 11:00-22:00（工作日）/ 11:00-23:00（周末），早于开赛5-30分钟停售
2. **赔率变动**：竞彩赔率随投注量浮动，以出票时为准
3. **北京时间**：所有时间使用北京时间（UTC+8）
4. **M1/M2 已截止**：第1轮 M1(6/12 03:00) 和 M2(6/12 06:00) 早于购彩时间17:00，不可购买
5. **nginx 部署**：HTML 通过 nginx 8080 端口对外提供访问

## Cron 配置

可配置定时任务自动检查赛果：

```bash
# 每2小时检查一次是否有新赛果（比赛日）
0 */2 * * * python3 ~/world-cup/.hermes/skills/world-cup/lottery-updater/scripts/fetch_results.py --auto-update
```
