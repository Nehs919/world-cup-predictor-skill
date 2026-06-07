# -*- coding: utf-8 -*-
"""Copy team data from worldcup-predictor into wc-predictor skill bundle."""
import argparse
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
DATA_OUT = SKILL_ROOT / "data" / "teams.json"
REFERENCES = SKILL_ROOT / "references"


def sync(source: Path) -> None:
    src = source / "data.json"
    if not src.is_file():
        raise SystemExit(f"Source not found: {src}")

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, DATA_OUT)

    teams = json.loads(DATA_OUT.read_text(encoding="utf-8"))
    if len(teams) != 48:
        raise SystemExit(f"Expected 48 teams, got {len(teams)}")

    _write_teams_reference(teams)
    print(f"Synced {len(teams)} teams -> {DATA_OUT}")
    print(f"Updated {REFERENCES / 'teams.md'}")


def _write_teams_reference(teams: list) -> None:
    REFERENCES.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 48 支世界杯参赛队",
        "",
        "| id | 中文名 | English | rating |",
        "|----|--------|---------|--------|",
    ]
    for t in sorted(teams, key=lambda x: x["id"]):
        lines.append(
            f"| {t['id']} | {t['name']} | {t['nameEn']} | {t.get('rating', '-')} |"
        )
    lines.extend(["", "队名解析失败时，用 `--list-teams` 或本表查找 id。", ""])
    (REFERENCES / "teams.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Sync teams.json from worldcup-predictor")
    p.add_argument(
        "--source",
        type=Path,
        default=Path(r"C:\Users\Administrator\Desktop\worldcup-predictor"),
        help="Path to worldcup-predictor project root",
    )
    sync(p.parse_args().source)


if __name__ == "__main__":
    main()
