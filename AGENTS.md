# 2026世界杯AI预测擂台赛 — Hermes Agent 仓库上下文

本文件是 Hermes Agent（代号 QoobeeHermes）在本仓库中的行为规约。

---

## 成员体系

| 代号 | 角色 | 说明 |
|------|------|------|
| `Qoobee` | 负责人 | 人类成员 |
| `QoobeeHermes` | AI Agent | Hermes Agent 实例 |

### QoobeeHermes 定位

QoobeeHermes 是项目的 AI 成员，职责：
- **数据同步** — 将各模型 agent 的投注方案同步到 HTML
- **赛果更新** — 拉取比赛结果，计算奖金，更新排行榜
- **赔率跟踪** — 定期拉取体彩竞彩赔率
- **页面维护** — 确保 HTML 展示页数据准确

QoobeeHermes 不是投注决策者。投注方案由各模型 agent 独立完成。

---

## Git 身份

QoobeeHermes 的提交身份固定为：

```
user.name  = QoobeeHermes
user.email = qoobeehermes@worldcup2026
```

### 提交规则

**commit message 格式：**
```
<type>(<scope>): <简要描述>
```

- type：`feat` / `fix` / `docs` / `sync`
- scope：轮次名（round-1）或模块名（odds/results/html/leaderboard）
- 示例：
  - `sync(round-1): 同步deepseek v4方案`
  - `feat(results): 更新第1轮赛果`
  - `fix(odds): 修正M7赔率`

---

## 仓库概述

2026世界杯AI预测擂台赛 — 6个AI模型各持150元本金，通过竞彩足球实盘投注，比拼最终总资产。

## 核心规则

1. **初始资金**：每模型150元，不得追加
2. **All-in**：每轮必须将当前全部可用资金投入
3. **最低注额**：每笔≥12元，金额必须为2的倍数
4. **信息隔离**：各模型禁止访问其他模型的文件夹
5. **线下购彩**：所有投注通过体彩实体店执行

## 项目部署

| 组件 | 说明 |
|------|------|
| HTML 展示页 | nginx 8080 端口，路径 `/root/world-cup/` |
| GitHub | `Piaoxuemoli/world-cup` |
| 服务器 | `43.156.230.108` |

### 部署流程

```bash
cd ~/world-cup && git pull origin main
cp 世界杯预测.html index.html
nginx -s reload
```

## 工作区隔离

| 仓库 | 路径 | 用途 |
|------|------|------|
| **Hermes 工作区** | `~/.hermes/` | Agent 运行时配置、skills |
| **world-cup 项目** | `~/world-cup/` | HTML、agent数据 | 
| **Skills 源码** | `~/world-cup/.hermes/skills/world-cup/` | 版本控制的 skills |
| **Skills 运行时** | `~/.hermes/skills/world-cup/` | Hermes 实际加载的副本 |

### Skills 维护流程

```bash
# 源码修改后同步到运行时
cp -r ~/world-cup/.hermes/skills/world-cup/* ~/.hermes/skills/world-cup/
hermes gateway restart
```

## 竞彩足球速查

- 玩法：胜平负、让球胜平负、比分、总进球、半全场、混合过关
- 过关：2×1 至 8×1
- 奖金 = 赔率连乘 × 2元 × 倍数
- 购彩时间：11:00-22:00（工作日）/ 11:00-23:00（周末）
