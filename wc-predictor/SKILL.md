---
name: wc-predictor
description: >
  Predict 2026 World Cup match outcomes (win probability, top scorelines, adjusted
  team strength) using the bundled Kengine engine and 48-team player database.
  Use whenever the user mentions /wc-predictor, World Cup match prediction,
  predicting two national teams, win rate, expected goals, or "X vs Y" World Cup
  scorelines — even if they do not name this skill explicitly.
license: MIT
compatibility: Requires Python 3.10+ on PATH. Run scripts/predict.py relative to this skill root (or use absolute paths). No network required for prediction. On Windows set PYTHONUTF8=1 if CLI output is garbled.
metadata:
  hermes:
    category: sports
    tags: [world-cup, football, prediction, kengine]
---

# wc-predictor — 世界杯比分预测

用 bundled Python 引擎做**确定性**预测。你必须运行 `scripts/predict.py`，**禁止**自行估算胜率或比分。

**Skill 根目录** = 本文件（`SKILL.md`）所在目录。数据与脚本路径：

```
<skill-root>/scripts/predict.py
<skill-root>/data/teams.json
```

运行 CLI 时，请使用 **skill 根目录下的绝对路径**，或先 `cd` 到 `<skill-root>/scripts/` 再执行。各 Agent 的工作目录不固定，不要依赖当前 cwd 推断 `teams.json` 位置。

## 触发

- `/wc-predictor ...`
- 「预测德国 vs 库拉索」「世界杯胜率」「两队比分推演」

## 第一步：模式分流（必做）

用户给出对阵后，**先问**（除非同句已明确「默认」或「自定义」）：

> 要用 **默认设定** 直接预测，还是 **自定义参数**？
>
> **默认**：各队默认阵型 + 默认首发 + 开放度 50 · 战术倾向各 50% · 历史底蕴 50%  
> **自定义**：你逐项指定阵型、首发、开放程度、主客队战术倾向、历史底蕴权重（见 [parameters.md](references/parameters.md)）

不要跳过此步直接预测。

---

## 回复语言

根据用户**本条消息**所用语言选择回复语言（仅影响你写的说明文字，不影响 CLI 计算）：

| 用户语言 | 回复语言 |
|----------|----------|
| 中文 | 中文（球员可写「中文名 (English)」） |
| 英文 | 英文 |
| 其它任何语言（日文、葡萄牙语、西语等） | **英文** |

胜率、比分等数字必须来自 CLI JSON；`lineupA` / `lineupB` 中的球员名单也必须来自 JSON，不得编造。

---

## 路径 A — 默认设定

1. 解析队名 → 查 [teams.md](references/teams.md) 或 `python scripts/predict.py --list-teams`
2. 运行（工作目录不限，用绝对路径或 `cd` 到 `scripts/`）：

```bash
python scripts/predict.py --a <id或队名> --b <id或队名> --format json
```

3. 用下方「输出模板」呈现；数值必须来自 CLI JSON，不得编造。

---

## 路径 B — 自定义设定

进入自定义后，先向用户说明可配置项（可读 [parameters.md](references/parameters.md)）：

1. **主队阵型**、**客队阵型**（12 种全局阵型，见 [formations.md](references/formations.md)）
2. **主队首发 11 人**、**客队首发 11 人**（player id；用 `--team <id>` 查看 roster）
3. **开放程度**（0–100）
4. **主队战术倾向**、**客队战术倾向**（0–100% 或 0–1）
5. **历史底蕴权重**（0–100% 或 0–1）

**每一项都需要用户确认**才能跑预测。收集顺序可灵活，但不可遗漏。若用户对某项说「用默认」，则该项取默认设定表中的值。

展示首发前，先跑：

```bash
python scripts/predict.py --team <主队id>
python scripts/predict.py --team <客队id>
```

收集齐全部参数后运行：

```bash
python scripts/predict.py --a <A> --b <B> \
  --formation-a "<阵型>" --formation-b "<阵型>" \
  --open <0-100> --heritage <0-1> \
  --tendency-a <0-1> --tendency-b <0-1> \
  --starters-a "id1,id2,...,id11" \
  --starters-b "id1,id2,...,id11" \
  --format json
```

百分数请转为 0–1 再传入 `--heritage` / `--tendency-*`。

---

## 阵型校验

合法阵型仅 12 种（见 [formations.md](references/formations.md)）。

用户指定非法阵型 → **不要猜测** → 列出全部 12 种并重问。

CLI 报错时 stderr 也会列出可选阵型，原样转述给用户。

---

## 队名 / 球员错误

- 队名无法解析：运行 `--list-teams` 或查 teams.md，给出相近选项
- 球员 id 无效：重新展示 `--team` 输出中的 id 列表

---

## 输出模板

**不要**在标题或表格中使用国旗 emoji。必须包含**双方首发 11 人（带槽位）和替补名单**（来自 JSON 的 `lineupA` / `lineupB`）。

**不要**在回复中展示**球员能力值**（JSON 中 `lineupA/B` 的 `rating` 字段仅供引擎计算，不得写入表格或正文）。球队级「调整后实力」可以保留。

中文用户示例：

```markdown
## {主队} vs {客队}

| | {主队} | {客队} |
|--|--------|--------|
| 阵型 | … | … |
| 调整后实力 | … | … |

**胜率**：…  
**最可能比分**：…  
**关键词**：…

**设定**：…

### {主队} 阵容

**首发**

| 槽位 | 球员 |
| … |

**替补**

| 球员 |
| … |

### {客队} 阵容

（同上结构）
```

英文用户：相同结构，表头与标签改为英文（Starters / Bench / Win rate 等）；**同样不得展示球员 rating**。

---

## 禁止事项

- 禁止不用 CLI 心算胜率、比分
- 禁止编造不在 roster 中的球员
- 禁止在回复中展示球员能力值（lineup 中的 rating）
- 禁止 WebUI、分享卡、部署、远程 API
- 禁止在回复中提及错误的数据来源标签（历史文档中的 FM 字样已作废）

---

## 参考文件何时读取

| 文件 | 何时 |
|------|------|
| [teams.md](references/teams.md) | 解析队名 |
| [formations.md](references/formations.md) | 自定义阵型、非法阵型报错 |
| [parameters.md](references/parameters.md) | 自定义模式说明与默认值 |

---

## 快速命令参考

```bash
python scripts/predict.py --list-teams
python scripts/predict.py --list-formations
python scripts/predict.py --team ger
python scripts/predict.py --a ger --b cuw --format json
```
