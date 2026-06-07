**中文** | [English](README.en.md)

> [!TIP]
> **网页版 · 免安装 · 免注册 · 直接开玩**  
> **[kengine.xx.kg](https://kengine.xx.kg)**  
> 国内域名 [www.kengine.fun](https://www.kengine.fun) 备案中

# world-cup-predictor-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](#前置要求)
[![Cursor Agent Skill](https://img.shields.io/badge/Cursor-Agent%20Skill-000000)](https://cursor.com)
[![Teams](https://img.shields.io/badge/Teams-48-2ea44f)](#1-安装-skill)
[![Web App](https://img.shields.io/badge/Web-kengine.xx.kg-orange)](https://kengine.xx.kg)

**world-cup-predictor-skill** 将 **Kengine** 足球仿真引擎封装为符合 [Agent Skills 标准](https://agentskills.io/specification) 的可移植技能包，可在 Cursor、Hermes Agent、Claude Code、Codex 等环境中即装即用。在 Agent 对话中指定任意两支 2026 世界杯参赛队，即可获得 **胜率分布、最可能比分与双方完整阵容**（含首发与替补）。

引擎内置 **48 支球队的全量球员能力评分**，以及由历史竞技表现沉淀而来的 **球队底蕴、近期状态与比赛风格** 等结构化数据。你在对话中定义 **阵型、首发名单、比赛开放度、主客战术倾向与历史底蕴权重** 等仿真参数——或使用默认一键预测——引擎据此完成 **确定性数值推演**：同一组输入，永远得到同一组输出，而非 LLM 的即兴估算。

Agent 负责理解意图、补齐参数并调用 bundled Python CLI；**所有胜率与比分均来自引擎计算，不得心算或编造。**

## 预览

<table>
  <tr>
    <td width="50%" align="center"><strong>网页版 · kengine.xx.kg</strong></td>
    <td width="50%" align="center"><strong>Agent · wc-predictor</strong></td>
  </tr>
  <tr>
    <td><img src="docs/images/web-demo.png" alt="Kengine 网页版预测界面" width="100%"></td>
    <td><img src="docs/images/cursor-skill-demo.png" alt="Cursor 中使用 wc-predictor skill 的对话示例" width="100%"></td>
  </tr>
</table>

---

## 前置要求

- **Python 3.10+**（仅标准库，无第三方依赖）— **所有 Agent 通用**
- 任一支持 [Agent Skills 标准](https://agentskills.io/specification) 的 Agent（如 Cursor、Hermes、Claude Code）
- Windows 用户若 CLI 输出中文乱码，可设置 `PYTHONUTF8=1` 后再运行

---

## 1. 安装 Skill

安装包是仓库内的 **`wc-predictor/`** 目录（含 `SKILL.md`、脚本与数据），不是整个 `world-cup-predictor-skill` 根目录。仓库其余部分（`docs/`、`tools/`）为文档与维护脚本，**终端用户只需复制 `wc-predictor/`**。

### Cursor

**Windows**

```powershell
# 若目录不存在则创建
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\skills\wc-predictor"

# 从本仓库复制（请按实际路径修改源路径）
robocopy "C:\path\to\world-cup-predictor-skill\wc-predictor" "$env:USERPROFILE\.cursor\skills\wc-predictor" /E
```

**macOS / Linux**

```bash
mkdir -p ~/.cursor/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.cursor/skills/wc-predictor/
```

### 验证安装

```bash
python ~/.cursor/skills/wc-predictor/scripts/predict.py --list-teams
python ~/.cursor/skills/wc-predictor/scripts/predict.py --a ger --b cuw
```

能列出 48 支球队并输出预测结果，即表示安装成功。

### 加载 Skill

安装后请 **新开一个 Agent 对话**（必要时重启 Cursor），Agent 才会加载 `SKILL.md`。

---

## 2. 其它 Agent 安装

同一份 `wc-predictor/` 可安装到 Hermes、Claude Code、Codex、Gemini CLI 等，**无需改 skill 格式**。

| Agent | 用户级安装路径 |
|-------|----------------|
| **Cursor** | `~/.cursor/skills/wc-predictor/` |
| **Hermes Agent** | `~/.hermes/skills/wc-predictor/` |
| **Claude Code** | `~/.claude/skills/wc-predictor/` |
| **Codex / 多 Agent 通用** | `~/.agents/skills/wc-predictor/` |
| **Gemini CLI** | `~/.gemini/skills/wc-predictor/` |

**Hermes 快速安装：**

```bash
cp -r /path/to/world-cup-predictor-skill/wc-predictor ~/.hermes/skills/wc-predictor
hermes skills list   # 确认 wc-predictor 已识别
```

**验证（任意 Agent，将路径换成你的 skill 根目录）：**

```bash
python ~/.hermes/skills/wc-predictor/scripts/predict.py --list-teams
```

完整对照、GitHub 远程安装与各平台细节见 **[docs/AGENTS.md](docs/AGENTS.md)**。

安装后 **新开 Agent 会话** 以加载 skill。触发方式：`/wc-predictor` 或自然语言（如「预测德国 vs 库拉索」）。

---

## 3. 使用 Skill

### 在 Agent 对话中使用

**中文示例**

```
/wc-predictor 预测德国和库拉索的比赛结果
```

**英文示例**

```
/wc-predictor predict Germany vs Curaçao, use default settings
```

**自定义参数示例**

```
/wc-predictor 自定义预测巴西对阿根廷：巴西 4-2-3-1、阿根廷 4-3-3，开放度 70，历史底蕴 60%，主队战术倾向 80%、客队 50%，首发都用各队默认
```

**让 Agent 定参数（趣玩）**

除了你自己逐项指定，也可以把自定义模式下的 8 类参数**全部交给 Agent 决定**——让它根据对阵、球员和战术理解自行选阵型、首发、开放度等，再调用引擎计算。参数一旦确定，结果就是确定性的；你可以和朋友比比 **谁的 Agent 最懂球**。

```
/wc-predictor 自定义预测巴西对阿根廷，所有参数你来定，定完解释理由再预测
```

```
/wc-predictor custom Brazil vs Argentina — you pick formation, lineups, and all sliders, then run the engine
```

### Agent 定参数 · 全场模拟（示例）

下面是我们让 **Composer 2.5**、**GPT-5.5**、**Opus 4.8** 三个 Agent **自行定义每场参数**，用 Kengine 跑完 2026 世界杯**小组赛 + 淘汰赛**全程模拟的结果（各 2 张，共 6 张）：

| Agent | 小组赛 | 淘汰赛 | 模拟冠军 |
|-------|--------|--------|----------|
| Composer 2.5 | ![Composer 小组赛](docs/images/agent-sims/group-stage-composer.png) | ![Composer 淘汰赛](docs/images/agent-sims/knockout-composer.png) | 英格兰 |
| GPT-5.5 | ![GPT 小组赛](docs/images/agent-sims/group-stage-gpt.png) | ![GPT 淘汰赛](docs/images/agent-sims/knockout-gpt.png) | 阿根廷 |
| Opus 4.8 | ![Opus 小组赛](docs/images/agent-sims/group-stage-opus.png) | ![Opus 淘汰赛](docs/images/agent-sims/knockout-opus.png) | 巴西 |

> 看上去，**我们自己选参数会预测得更好**……要不你也试试，看能不能 beat 这些 Agent？😏

### 交互流程

1. **模式分流（必做）**  
   Agent 会先问：使用 **默认设定** 还是 **自定义参数**？  
   除非你已在同一句里明确说了「默认」或「自定义」。

2. **默认设定**  
   各队默认阵型 + 默认首发 11 人 + 开放度 50 + 主客战术倾向各 50% + 历史底蕴权重 50%。

3. **自定义设定**  
   需逐项确认全部 8 类参数：主客阵型、主客首发、开放程度、主客战术倾向、历史底蕴权重；也可明确说「参数你来定」，由 Agent 代为选择后再跑 CLI。详见 [`wc-predictor/references/parameters.md`](wc-predictor/references/parameters.md)。

4. **输出**  
   Agent 运行 `predict.py` 后，按模板呈现结果：
   - 阵型、**球队**调整后实力、胜率、Top 3 概率比分、关键词
   - 双方首发（带槽位）与替补名单
   - **不展示球员能力值**（rating 仅用于引擎内部计算）
   - 不使用国旗 emoji
   - 中文问 → 中文答；英文问 → 英文答；其它语言 → 英文答

### 本地 CLI（不经过 Agent）

Skill 根目录下的脚本可独立运行，便于调试或脚本化：

```bash
cd wc-predictor/scripts

# 列出 48 支球队
python predict.py --list-teams

# 列出 12 种全局阵型
python predict.py --list-formations

# 查看某队 roster 与默认首发
python predict.py --team ger

# 默认设定预测（Markdown）
python predict.py --a ger --b cuw

# JSON 输出（Agent 内部应使用此格式取数）
python predict.py --a ger --b cuw --format json

# 英文 Markdown
python predict.py --a ger --b cuw --format md --lang en

# 自定义参数
python predict.py --a bra --b arg \
  --formation-a "4-2-3-1" --formation-b "4-3-3" \
  --open 70 --heritage 0.6 --tendency-a 0.8 --tendency-b 0.5 \
  --format json
```

队名支持 id（`ger`）、中文名（`德国`）或英文名（`Germany`）。非法阵型会被拒绝并列出全部 12 种可选阵型。

---

## 4. 计算逻辑说明

引擎实现见 [`wc-predictor/scripts/engine.py`](wc-predictor/scripts/engine.py)，fork 自主项目 `worldcup-predictor` 的 Kengine，流程如下。

### 4.1 输入

| 来源 | 内容 |
|------|------|
| `data/teams.json` | 48 支世界杯参赛队：球员 rating、位置、年龄、默认首发、历史底蕴 `heritage`、比赛风格 `playStyle` 等 |
| 用户参数 | 阵型（12 种全局）、首发 11 人、开放度、战术倾向、历史底蕴权重 |

### 4.2 单队实力计算（主客队各算一次）

```
① 阵型槽位加成
   每名首发球员 rating × (1 + 该槽位阵型加成)

② 位置适配惩罚
   球员擅长位置与槽位匹配度 → 系数 1.0 / 0.95 / 0.90 / 0.70

③ 战术倾向（球星权重）
   按 rating 排序，前 3 名球星获得额外 tier 加成（91+/86+/76+ 分档）
   战术倾向越高 → 球星影响越大；越低 → 更偏团队整体

④ 历史底蕴混合
   最终 = 近期实力 × (1 - 底蕴权重) + 球队 heritage × 底蕴权重

⑤ 开放程度修正
   根据球队 playStyle 与开放度滑块（0–100）微调实力
   开放度越高，进攻型球队受益越多；越低则防守型球队相对受益
```

得到主客队 **调整后实力** `aFinal`、`bFinal`，差值 `diff = aFinal - bFinal`。

### 4.3 胜率

使用 Sigmoid 函数将实力差映射为胜率：

```
winRateA = sigmoid(diff, steepness=12)
winRateB = 1 - winRateA
```

实力差越大，胜率越接近 0% 或 100%，但不会完全为 0/100。

### 4.4 比分概率（Top 3）

1. 根据 **开放度** 估算比赛总进球期望（约 1.5–7 球区间）
2. 根据 **实力差** 放大进球差距（强队领先时大比分概率上升）
3. 将总进球按胜率分配给主客队的 Poisson 参数 λA、λB
4. 枚举 0:0 至 9:9 的所有比分，计算联合概率，取 Top 3

因此「最可能比分」是概率最大的三个比分及其百分比，**不是**单一 deterministic 预测比分。

### 4.5 关键词

根据开放度与实力差自动生成，例如：「势均力敌」「碾压之势」「以下克上」「酣畅对攻」「沉闷保守」。

### 4.6 重要说明

- 所有数值由同一套公式**确定性**产生；相同输入永远得到相同输出
- Agent **禁止**绕过 CLI 心算或编造球员/比分
- 输出中的球员名单来自 JSON 的 `lineupA` / `lineupB`，不得手工编造

---

## 5. 其它说明

### 项目结构

```
world-cup-predictor-skill/
├── wc-predictor/              ← 安装到 ~/.cursor/skills/wc-predictor/
│   ├── SKILL.md               Agent 工作流与输出规范
│   ├── scripts/
│   │   ├── predict.py         CLI 入口
│   │   ├── engine.py          Kengine 预测引擎
│   │   └── sync_data.py       从主项目同步球队数据
│   ├── data/teams.json        48 队球员数据
│   └── references/            队名、阵型、参数参考文档
├── tools/
│   └── fix_player_name_en.py  修补缺失/错误的球员英文名
└── docs/                      AGENTS / README 插图
```

### 更新球队数据

从主项目 `worldcup-predictor` 同步最新 `data.json`：

```bash
python wc-predictor/scripts/sync_data.py --source "C:/path/to/worldcup-predictor"
```

同步后若发现球员英文名缺失，可运行：

```bash
python tools/fix_player_name_en.py
```

同步会覆盖 `teams.json`；`fix_player_name_en.py` 会重新写入已知的英文名补丁。

### 修改 Skill 后重新部署

开发仓库内改完 `wc-predictor/` 后，需再次复制到 `~/.cursor/skills/wc-predictor/`，并新开 Agent 对话生效。

### 边界（Skill 不包含）

- Web UI、分享卡、部署脚本
- 预测完成后的口头二次微调（无 Layer 2）
- 远程 API；一切计算在本地 Python 完成

### 相关文档

- [docs/AGENTS.md](docs/AGENTS.md) — Cursor / Hermes / Claude Code / Codex 等安装指南
- [wc-predictor/references/parameters.md](wc-predictor/references/parameters.md) — 可调参数详解
- [wc-predictor/references/formations.md](wc-predictor/references/formations.md) — 12 种阵型
- [wc-predictor/references/teams.md](wc-predictor/references/teams.md) — 48 队 id 对照表

### License

MIT
