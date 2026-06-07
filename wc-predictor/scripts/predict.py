# -*- coding: utf-8 -*-
"""CLI for wc-predictor skill — deterministic match prediction."""
import argparse
import io
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Allow running as script from any cwd
sys.path.insert(0, str(Path(__file__).resolve().parent))

import engine as eng  # noqa: E402


def _pct(v: float) -> str:
    return f"{int(round(v * 100))}%" if v <= 1 else f"{int(round(v))}%"


def _format_lineup_block(lineup: dict, lang: str = "zh") -> str:
    if lang == "en":
        lines = ["**Starters**", "", "| Slot | Player |", "|------|--------|"]
        for s in lineup.get("starters", []):
            lines.append(f"| {s['slot']} | {s['nameEn'] or s['name']} |")
        lines.extend(["", "**Bench**", ""])
        bench = lineup.get("bench", [])
        if bench:
            lines.append("| Player |")
            lines.append("|--------|")
            for p in bench:
                lines.append(f"| {p['nameEn'] or p['name']} |")
        else:
            lines.append("(none)")
        return "\n".join(lines)

    lines = ["**首发**", "", "| 槽位 | 球员 |", "|------|------|"]
    for s in lineup.get("starters", []):
        lines.append(f"| {s['slot']} | {s['name']} ({s['nameEn']}) |")
    lines.extend(["", "**替补**", ""])
    bench = lineup.get("bench", [])
    if bench:
        lines.append("| 球员 |")
        lines.append("|------|")
        for p in bench:
            lines.append(f"| {p['name']} ({p['nameEn']}) |")
    else:
        lines.append("（无）")
    return "\n".join(lines)


def format_markdown(result: dict, lang: str = "zh") -> str:
    ta, tb = result["teamA"], result["teamB"]
    s = result["settings"]
    tops = result["topScores"]
    top_line = " | ".join(f"{x['display']} ({x['probability']}%)" for x in tops)
    la = _format_lineup_block(result.get("lineupA", {}), lang)
    lb = _format_lineup_block(result.get("lineupB", {}), lang)
    kw = " · ".join(result["keywords"]) if result["keywords"] else "—"

    if lang == "en":
        return f"""## {ta['nameEn']} vs {tb['nameEn']}

| | {ta['nameEn']} | {tb['nameEn']} |
|--|--------|--------|
| Formation | {ta['formation']} | {tb['formation']} |
| Adjusted strength | {ta['rating']} | {tb['rating']} |

**Win rate**: {ta['nameEn']} {result['winRateA']}% · {tb['nameEn']} {result['winRateB']}%  
**Most likely scores**: {top_line}  
**Keywords**: {kw}

**Settings**: openness {_pct(s['openness'] / 100 if s['openness'] > 1 else s['openness'])} · heritage weight {_pct(s['formWeight'])} · home tactical tendency {_pct(s['starWeightA'])} · away tactical tendency {_pct(s['starWeightB'])}

### {ta['nameEn']} squad

{la}

### {tb['nameEn']} squad

{lb}
"""

    return f"""## {ta['name']} vs {tb['name']}

| | {ta['name']} | {tb['name']} |
|--|--------|--------|
| 阵型 | {ta['formation']} | {tb['formation']} |
| 调整后实力 | {ta['rating']} | {tb['rating']} |

**胜率**：{ta['name']} {result['winRateA']}% · {tb['name']} {result['winRateB']}%  
**最可能比分**：{top_line}  
**关键词**：{kw}

**设定**：开放度 {_pct(s['openness'] / 100 if s['openness'] > 1 else s['openness'])} · 历史底蕴权重 {_pct(s['formWeight'])} · 主队战术倾向 {_pct(s['starWeightA'])} · 客队战术倾向 {_pct(s['starWeightB'])}

### {ta['name']} 阵容

{la}

### {tb['name']} 阵容

{lb}
"""


def format_team_detail(team: dict) -> str:
    fmt = eng.default_formation_name(team)
    player_map = {p["id"]: p for p in team.get("players", [])}
    starters = team.get("defaultStarters", [])
    bench = [
        p for pid, p in player_map.items()
        if pid not in starters and p.get("rating", 0) > 0
    ]
    bench.sort(key=lambda p: (-p.get("rating", 0), p.get("nameEn", "")))

    lines = [
        f"# {team['name']} ({team['nameEn']})",
        f"id: `{team['id']}` · rating: {team.get('rating', '-')} · 默认阵型: {fmt}",
        "",
        "## 首发（11 人，按阵型槽位顺序）",
        "",
        "| 槽位 | 球员 |",
        "|------|------|",
    ]
    formation = eng.get_formation(fmt)
    if formation:
        for i, pid in enumerate(starters):
            p = player_map.get(pid, {})
            slot = formation["slots"][i]["label"] if i < len(formation["slots"]) else "?"
            lines.append(
                f"| {slot} | {p.get('name', '?')} ({p.get('nameEn', '')}) | `{pid}` |"
            )
    lines.extend(["", "## 替补", "", "| 球员 | id |", "|------|-----|"])
    for p in bench:
        lines.append(f"| {p.get('name', '?')} ({p.get('nameEn', '')}) | `{p['id']}` |")
    lines.extend(["", "## 可选阵型（全局 12 种）", ""])
    lines.append(", ".join(eng.list_formations()))
    lines.append("")
    return "\n".join(lines)


def run_predict(args) -> int:
    team_a = eng.resolve_team(args.a)
    team_b = eng.resolve_team(args.b)
    if not team_a:
        print(f"未找到球队：{args.a}", file=sys.stderr)
        for t in eng.suggest_teams(args.a):
            print(f"  - {t['id']}: {t['name']} / {t['nameEn']}", file=sys.stderr)
        return 1
    if not team_b:
        print(f"未找到球队：{args.b}", file=sys.stderr)
        for t in eng.suggest_teams(args.b):
            print(f"  - {t['id']}: {t['name']} / {t['nameEn']}", file=sys.stderr)
        return 1

    fa = args.formation_a or eng.default_formation_name(team_a)
    fb = args.formation_b or eng.default_formation_name(team_b)
    for label, name in (("主队", fa), ("客队", fb)):
        err = eng.validate_formation(name)
        if err:
            print(f"{label}阵型错误：{err}", file=sys.stderr)
            return 2

    starters_a = None
    starters_b = None
    if args.starters_a:
        starters_a = [x.strip() for x in args.starters_a.split(",") if x.strip()]
        err = eng.validate_starters(team_a, starters_a)
        if err:
            print(err, file=sys.stderr)
            return 3
    if args.starters_b:
        starters_b = [x.strip() for x in args.starters_b.split(",") if x.strip()]
        err = eng.validate_starters(team_b, starters_b)
        if err:
            print(err, file=sys.stderr)
            return 3

    params = {
        "formationNameA": fa,
        "formationNameB": fb,
        "starterIdsA": starters_a,
        "starterIdsB": starters_b,
        "starWeightA": args.tendency_a,
        "starWeightB": args.tendency_b,
        "formWeight": args.heritage,
        "openness": args.open,
    }
    result = eng.predict(team_a, team_b, params)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(result, args.lang))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Kengine wc-predictor CLI")
    p.add_argument("--list-teams", action="store_true", help="List 48 teams")
    p.add_argument("--list-formations", action="store_true", help="List 12 formations")
    p.add_argument("--team", metavar="ID", help="Show team roster and default lineup")
    p.add_argument("--a", help="Team A id or name")
    p.add_argument("--b", help="Team B id or name")
    p.add_argument("--formation-a", help="Team A formation name")
    p.add_argument("--formation-b", help="Team B formation name")
    p.add_argument("--starters-a", help="Team A starter ids, comma-separated (11)")
    p.add_argument("--starters-b", help="Team B starter ids, comma-separated (11)")
    p.add_argument("--open", type=float, default=50.0, help="Openness 0-100 (default 50)")
    p.add_argument("--heritage", type=float, default=0.5, help="Heritage weight 0-1 (default 0.5)")
    p.add_argument("--tendency-a", type=float, default=0.5, help="Team A tactical tendency 0-1 (default 0.5)")
    p.add_argument("--tendency-b", type=float, default=0.5, help="Team B tactical tendency 0-1 (default 0.5)")
    p.add_argument("--lang", choices=("zh", "en"), default="zh", help="Markdown output language")
    p.add_argument("--format", choices=("md", "json"), default="md")
    args = p.parse_args()

    if args.list_teams:
        for t in sorted(eng.load_teams(), key=lambda x: x["id"]):
            print(f"{t['id']:4}  {t['name']:8}  {t['nameEn']}")
        return 0

    if args.list_formations:
        for name in eng.list_formations():
            f = eng.get_formation(name)
            slots = "/".join(s["label"] for s in f["slots"]) if f else ""
            print(f"{name:10}  {slots}")
        return 0

    if args.team:
        team = eng.resolve_team(args.team)
        if not team:
            print(f"未找到球队：{args.team}", file=sys.stderr)
            return 1
        print(format_team_detail(team))
        return 0

    if not args.a or not args.b:
        p.error("预测需要 --a 和 --b（或使用 --list-teams / --team）")

    return run_predict(args)


if __name__ == "__main__":
    raise SystemExit(main())
