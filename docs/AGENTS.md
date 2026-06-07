# 其它 Agent 安装指南

本 skill 遵循 [Agent Skills 开放标准](https://agentskills.io/specification)（`SKILL.md` + `scripts/` + `references/` + `data/`）。**同一份 `wc-predictor/` 目录**可安装到不同 Agent，无需改格式。

完整安装包 = 仓库内的 **`wc-predictor/`** 子目录（不是整个 `world-cup-predictor-skill` 根目录）。

---

## 通用前提（所有 Agent）

| 要求 | 说明 |
|------|------|
| Python | **3.10+**，仅标准库 |
| 安装内容 | 复制整个 `wc-predictor/` 到对应 skills 目录 |
| 验证 | `python <skill-root>/scripts/predict.py --list-teams` 应列出 48 支球队 |
| Windows | 若中文乱码，设置 `PYTHONUTF8=1` |
| 网络 | 预测本身**不需要**联网；数据已 bundled 在 `data/teams.json` |

安装后请 **新开一次 Agent 会话**（或重启 Agent 应用），以便加载 `SKILL.md`。

---

## 安装路径对照

| Agent | 用户级路径 | 项目级路径（可选） |
|-------|-----------|-------------------|
| **Cursor** | `~/.cursor/skills/wc-predictor/` | — |
| **Hermes Agent** | `~/.hermes/skills/wc-predictor/` | `~/.hermes/skills/sports/wc-predictor/` |
| **Claude Code** | `~/.claude/skills/wc-predictor/` | `.claude/skills/wc-predictor/` |
| **OpenAI Codex 等** | `~/.agents/skills/wc-predictor/` | `.agents/skills/wc-predictor/` |
| **Gemini CLI** | `~/.gemini/skills/wc-predictor/` | 或 fallback 到 `.agents/skills/` |

目录名建议与 `SKILL.md` frontmatter 中的 `name: wc-predictor` 一致。

### 手动复制示例

```bash
# macOS / Linux — 以 Cursor 为例，其它 Agent 只改目标路径
mkdir -p ~/.cursor/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.cursor/skills/wc-predictor/
```

```powershell
# Windows — Cursor
robocopy "C:\path\to\world-cup-predictor-skill\wc-predictor" "$env:USERPROFILE\.cursor\skills\wc-predictor" /E
```

---

## Hermes Agent

文档：[Working with Skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)

### 方式 A：手动复制（推荐）

```bash
mkdir -p ~/.hermes/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.hermes/skills/wc-predictor/
hermes skills list    # 确认 wc-predictor 已出现
```

### 方式 B：从 GitHub 安装

仓库：[github.com/Nehs919/world-cup-predictor-skill](https://github.com/Nehs919/world-cup-predictor-skill)

```bash
# 克隆后复制
git clone https://github.com/Nehs919/world-cup-predictor-skill.git
cp -r world-cup-predictor-skill/wc-predictor ~/.hermes/skills/wc-predictor

# 或安装远程 SKILL.md（单文件入口；仍需自行保证 scripts/ 与 data/ 在同目录）
hermes skills install https://raw.githubusercontent.com/Nehs919/world-cup-predictor-skill/master/wc-predictor/SKILL.md --name wc-predictor
```

若使用方式 B 的单文件安装，请确认 `scripts/`、`data/`、`references/` 与 `SKILL.md` 在同一 skill 目录下。

### 使用

- 斜杠命令：`/wc-predictor ...`
- 或自然语言（由 `description` 触发）
- 流程与 Cursor 相同：先问默认/自定义 → 跑 `predict.py` → 按 SKILL.md 模板输出

---

## Claude Code

```bash
mkdir -p ~/.claude/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.claude/skills/wc-predictor/
```

项目级：复制到 `<project>/.claude/skills/wc-predictor/` 仅对当前仓库生效。

---

## OpenAI Codex / 多 Agent 通用路径

Codex 及多个工具默认识别 **vendor-neutral** 路径：

```bash
mkdir -p ~/.agents/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.agents/skills/wc-predictor/
```

项目级：`.agents/skills/wc-predictor/` 或 `.github/skills/wc-predictor/`（视工具版本而定）。

---

## Gemini CLI

```bash
mkdir -p ~/.gemini/skills/wc-predictor
cp -r /path/to/world-cup-predictor-skill/wc-predictor/* ~/.gemini/skills/wc-predictor/
```

若未识别，可改用 `~/.agents/skills/wc-predictor/`。

---

## 触发与输出（各 Agent 通用）

| 步骤 | 行为 |
|------|------|
| 触发 | `/wc-predictor` 或「预测德国 vs 库拉索」等自然语言 |
| 分流 | 先问 **默认设定** 或 **自定义参数** |
| 计算 | 必须运行 `python <skill-root>/scripts/predict.py ... --format json` |
| 语言 | 中文问 → 中文答；英文问 → 英文答；其它 → 英文 |
| 禁止 | 心算胜率、编造球员、展示球员 rating |

---

## 更新 skill

1. 在开发仓库更新 `wc-predictor/`
2. 再次复制到对应 Agent 的 skills 目录（覆盖）
3. 新开 Agent 会话

从主项目同步数据：

```bash
python wc-predictor/scripts/sync_data.py --source "/path/to/worldcup-predictor"
python tools/fix_player_name_en.py
```

---

## English summary

- **Install unit:** copy the `wc-predictor/` folder only (not the whole repo).
- **Requires:** Python 3.10+, `PYTHONUTF8=1` on Windows if needed.
- **Paths:** Cursor `~/.cursor/skills/`, Hermes `~/.hermes/skills/`, Claude `~/.claude/skills/`, Codex/multi-agent `~/.agents/skills/`, Gemini `~/.gemini/skills/`.
- **Verify:** `python <skill-root>/scripts/predict.py --list-teams`
- **Hermes:** `hermes skills list` after copy; or `git clone https://github.com/Nehs919/world-cup-predictor-skill.git`; see [Hermes skills docs](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills).
- **Usage:** same workflow as Cursor — mode gate → CLI → formatted output per `SKILL.md`.
