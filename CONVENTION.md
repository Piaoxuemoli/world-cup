# AI Model Arena · 2026世界杯预测擂台赛 — 工作规约

---

## 1. 比赛规则

6 个大语言模型各持 **150 元**本金，通过中国体育彩票竞彩足球进行预测投注，最终比拼总资产。

### 核心规则

1. **初始资金**: 每模型 150 元，不得追加
2. **All-in**: 每轮必须将当前全部可用资金投入，不得保留余额
3. **最低注额**: 每笔投注 ≥ 12 元，金额必须为 **2 的倍数**（竞彩规则：2元/注）
4. **轮次排名奖励**: 每轮按净收益（奖金 − 投入）排名

| 🥇 1st | 🥈 2nd | 🥉 3rd | 4th | 5th | 6th |
|--------|--------|--------|-----|-----|-----|
| 30元 | 20元 | 10元 | 5元 | 2元 | 0元 |

5. **资金归零**: 仍可分析预测，但无法下注
6. **信息隔离**: 各模型仅可读取 `世界杯预测.html` 和本规约作为公开信息源，在自己的工作区内独立完成分析和策略制定。**禁止访问其他模型的文件夹**。每轮结算后，所有模型的 bets.md 和结果公开，下轮起可参考对手历史操作
7. **线下购彩**: 所有投注通过体彩实体店执行

### 竞彩速查

- 玩法：胜平负、让球胜平负、比分、总进球、半全场、混合过关
- 过关：2×1 至 8×1（比分/半全仅限 2×1、3×1）
- 奖金 = 赔率连乘 × 2元 × 倍数

---

## 2. 文件结构

```
世界杯工作区/
├── 世界杯预测.html        # 主展示页面
├── CONVENTION.md           # 本文件
└── agents/
    ├── gpt55/              # GPT-5.5 [1M] High Thinking
    ├── glm51/              # GLM-5.1 [200K] Thinking
    ├── qwen37/             # Qwen-3.7-Max [1M] Thinking
    ├── deepseek/           # Deepseek-V4-Pro [1M] Thinking
    ├── mimo/               # Mimo-V2.5-Pro [1M] Thinking
    └── kimi/               # Kimi-K2.6 [200K] Thinking
```

每个模型文件夹内：

| 文件 | 用途 |
|------|------|
| `PROFILE.md` | 模型介绍 & 总体策略（赛前写入） |
| `THINKING.md` | **持续更新的思考日志**（见下方说明） |
| `round-N/analysis.md` | 本轮分析推理（赛前写入） |
| `round-N/bets.md` | 本轮投注方案（赛前写入） |

### THINKING.md 说明

每个模型必须维护一份 `THINKING.md`，记录**每一轮的决策思路和复盘**，持续追加更新：

- 本轮为什么选这些比赛、为什么放弃其他比赛
- 资金分配的逻辑（为什么某场下多、某场下少）
- 对赔率的判断和预期
- 赛后的复盘反思（哪些判断正确、哪些失误、下轮如何调整）

> 这是模型"思维过程"的完整记录，不允许事后补写或修改历史内容，只能追加新内容。

---

## 3. 工作流程

```
① 发布赛程（人工建 round 文件夹，提供赛程/赔率）
       ↓
② 模型分析（写入 analysis.md + bets.md + 追加 THINKING.md）
       ↓
③ 购彩执行（人工按 bets.md 线下购买）
       ↓
④ 赛后结算（更新 bets.md 结果 → 同步 HTML → 追加复盘到 THINKING.md）
```

---

## 4. 同步机制

赛后将各模型 `bets.md` 同步到 `世界杯预测.html` 的 `AI_ROUNDS` 数组：

```javascript
{
  round: N,
  title: '小组赛第X轮',
  dateRange: 'X月X日 — X月X日',
  status: 'completed',
  predictions: {
    gpt55: {
      analysis: '...',
      strategy: '...',
      bets: [
        { match, matchId, playType, pick, amount, odds, 过关, actualScore, result, prize }
      ],
    },
    // glm51, qwen37, deepseek, mimo, kimi 同结构
  },
}
```

`result`: `'win'` | `'loss'` | `'pending'`

---

## 5. 命名规范

- 模型文件夹：`agents/{modelId}/`（小写无空格）
- 轮次文件夹：`round-{N}/`（N 从 1 开始）
- 固定文件名：`PROFILE.md`、`analysis.md`、`bets.md`
