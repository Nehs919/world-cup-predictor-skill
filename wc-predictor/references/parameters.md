# 可调参数说明

## 默认设定（快速预测）

| 项目 | 默认值 |
|------|--------|
| 主队阵型 | 该队 `defaultFormation` 对应阵型 |
| 客队阵型 | 同上 |
| 主队首发 | `defaultStarters`（11 人） |
| 客队首发 | 同上 |
| 开放程度 | 50（0=极度保守，100=疯狂对攻） |
| 主队战术倾向 | 50%（0=团队足球，100=球星决定一切） |
| 客队战术倾向 | 50% |
| 历史底蕴权重 | 50%（0=只看近期状态，100=只看历史底蕴） |

## 自定义模式 — 用户必须逐项确认

自定义模式下，以下 **每一项** 都需要用户提供（不可静默沿用默认值，除非用户明确说「某一项用默认」）：

| 用户-facing 名称 | CLI 参数 | 引擎字段 | 范围 |
|------------------|----------|----------|------|
| 主队阵型 | `--formation-a` | formationNameA | 12 种全局阵型 |
| 客队阵型 | `--formation-b` | formationNameB | 12 种全局阵型 |
| 主队首发 11 人 | `--starters-a` | starterIdsA | 11 个 player id，逗号分隔 |
| 客队首发 11 人 | `--starters-b` | starterIdsB | 同上 |
| 开放程度 | `--open` | openness | 0–100 |
| 主队战术倾向 | `--tendency-a` | starWeightA | 0–1（或 0%–100%） |
| 客队战术倾向 | `--tendency-b` | starWeightB | 0–1 |
| 历史底蕴权重 | `--heritage` | formWeight | 0–1 |

### 战术倾向说明

与主站滑块「主队/客队战术倾向」一致：数值越高，该队评分最高的球星对球队实力的影响越大；越低则越强调整体团队。

### 首发说明

- 用 `python scripts/predict.py --team <id>` 查看默认首发与球员 id
- 11 人顺序对应所选阵型的 11 个槽位
- 换阵型后应确认首发是否仍适配新阵型槽位

### 示例 CLI

```bash
python scripts/predict.py --a ger --b cuw \
  --formation-a "4-2-3-1" --formation-b "4-4-2" \
  --open 40 --heritage 0.6 --tendency-a 0.7 --tendency-b 0.3 \
  --starters-a "id1,id2,...(11 ids)" \
  --starters-b "id1,id2,...(11 ids)" \
  --format json
```
