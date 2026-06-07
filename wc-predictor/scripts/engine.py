# Kengine © 2026
"""
wc-predictor 预测引擎 — fork from worldcup-predictor/server/engine.py

扩展：支持全局 12 种阵型名称（formationNameA/B），不限球队 formations 数组。
"""
import json
import math
import re
from pathlib import Path

# ── 配置 (config.js) ──────────────────────────────────
OPENNESS_SCALE = 0.4
STAR_COUNT = 3
STAR_WEIGHT = 1.3
STAR_TIER1_MIN = 91; STAR_TIER1_BOOST = 1.15
STAR_TIER2_MIN = 86; STAR_TIER2_BOOST = 1.09
STAR_TIER3_MIN = 76; STAR_TIER3_BOOST = 1.05
STAR_TIER4_BOOST = 1.00
TEAM_BOOST_RANGE = 0.04
GOAL_BASE_MIN = 1.5
GOAL_RANGE = 5.5
GAP_GOAL_SCALE = 0.015
SIGMOID_STEEPNESS = 12
GOAL_SHARE_BIAS = 1.0
POS_PENALTY_SAME_AREA = 0.95
POS_PENALTY_ADJACENT = 0.90
POS_PENALTY_FAR = 0.70
KEYWORD_OPEN_LOW = 30
KEYWORD_OPEN_HIGH = 70
KEYWORD_DIFF_BIG = 15
KEYWORD_DIFF_CLOSE = 3
FORMATION_BONUS_TOTAL = 0.2

POSITION_LINE = {
    "GK": 6,
    "CB": 5, "RB": 5, "LB": 5, "RCB": 5, "LCB": 5,
    "LWB": 4, "CDM": 4, "RWB": 4,
    "CM": 3, "RM": 3, "LM": 3,
    "CAM": 2, "AMR": 2, "AML": 2,
    "RW": 1, "LW": 1, "ST": 1,
}

FORMATION_RAW = {
    "4-3-3": {"bonuses": [0.00, 0.05, 0.00, 0.00, 0.05, 0.03, 0.05, 0.03, 0.08, 0.05, 0.08],
              "labels": ["GK", "RB", "CB", "CB", "LB", "CM", "CM", "CM", "RW", "ST", "LW"]},
    "4-2-3-1": {"bonuses": [0.00, 0.03, 0.05, 0.05, 0.03, 0.05, 0.05, 0.06, 0.08, 0.06, 0.05],
                "labels": ["GK", "RB", "CB", "CB", "LB", "CDM", "CDM", "AMR", "CAM", "AML", "ST"]},
    "4-4-2": {"bonuses": [0.00, 0.05, 0.00, 0.00, 0.05, 0.06, 0.05, 0.03, 0.06, 0.05, 0.05],
              "labels": ["GK", "RB", "CB", "CB", "LB", "RM", "CM", "CM", "LM", "ST", "ST"]},
    "4-1-4-1": {"bonuses": [0.00, 0.05, 0.00, 0.00, 0.05, 0.00, 0.06, 0.05, 0.03, 0.06, 0.08],
                "labels": ["GK", "RB", "CB", "CB", "LB", "CDM", "RM", "CM", "CM", "LM", "ST"]},
    "4-5-1": {"bonuses": [0.00, 0.03, 0.00, 0.00, 0.03, 0.05, 0.05, 0.08, 0.05, 0.05, 0.08],
              "labels": ["GK", "RB", "CB", "CB", "LB", "CDM", "CM", "CAM", "RM", "LM", "ST"]},
    "3-4-3": {"bonuses": [0.00, 0.05, 0.00, 0.05, 0.08, 0.05, 0.03, 0.05, 0.08, 0.05, 0.08],
              "labels": ["GK", "CB", "CB", "CB", "RM", "CM", "CM", "LM", "RW", "ST", "LW"]},
    "3-5-2": {"bonuses": [0.00, 0.05, 0.00, 0.05, 0.08, 0.03, 0.00, 0.03, 0.08, 0.05, 0.05],
              "labels": ["GK", "RCB", "CB", "LCB", "RM", "CM", "CM", "CM", "LM", "ST", "ST"]},
    "3-2-4-1": {"bonuses": [0.00, 0.05, 0.00, 0.05, 0.00, 0.00, 0.08, 0.08, 0.06, 0.08, 0.05],
                "labels": ["GK", "RCB", "CB", "LCB", "CDM", "CDM", "AMR", "CAM", "CAM", "AML", "ST"]},
    "3-4-2-1": {"bonuses": [0.00, 0.05, 0.00, 0.05, 0.05, 0.05, 0.03, 0.03, 0.06, 0.06, 0.08],
                "labels": ["GK", "CB", "CB", "CB", "LWB", "CM", "CM", "RWB", "AMR", "AML", "ST"]},
    "3-4-1-2": {"bonuses": [0.00, 0.05, 0.00, 0.05, 0.05, 0.05, 0.03, 0.05, 0.06, 0.06, 0.06],
                "labels": ["GK", "CB", "CB", "CB", "RWB", "CM", "CM", "LWB", "CAM", "ST", "ST"]},
    "5-3-2": {"bonuses": [0.00, 0.05, 0.00, 0.00, 0.00, 0.05, 0.06, 0.05, 0.03, 0.05, 0.05],
              "labels": ["GK", "RWB", "CB", "CB", "CB", "LWB", "CM", "CM", "CM", "ST", "ST"]},
    "5-4-1": {"bonuses": [0.00, 0.05, 0.00, 0.00, 0.00, 0.05, 0.06, 0.05, 0.05, 0.03, 0.08],
              "labels": ["GK", "RWB", "CB", "CB", "CB", "LWB", "RM", "CM", "CM", "LM", "ST"]},
}

FORMATION_LIBRARY = {}
for _name, _raw in FORMATION_RAW.items():
    _total = sum(_raw["bonuses"])
    _scale = FORMATION_BONUS_TOTAL / _total
    FORMATION_LIBRARY[_name] = {
        "name": _name,
        "slots": [
            {"label": _raw["labels"][i], "bonus": round(_raw["bonuses"][i] * _scale, 4)}
            for i in range(11)
        ],
    }

FORMATION_NAMES = sorted(FORMATION_LIBRARY.keys())

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "teams.json"
_TEAMS_CACHE: list | None = None
_TEAMS_BY_ID: dict | None = None


def list_formations() -> list[str]:
    return list(FORMATION_NAMES)


def validate_formation(name: str) -> str | None:
    if name in FORMATION_LIBRARY:
        return None
    return f"未知阵型「{name}」。可选阵型：{', '.join(FORMATION_NAMES)}"


def load_teams() -> list[dict]:
    global _TEAMS_CACHE, _TEAMS_BY_ID
    if _TEAMS_CACHE is None:
        with open(DATA_PATH, encoding="utf-8") as f:
            _TEAMS_CACHE = json.load(f)
        _TEAMS_BY_ID = {t["id"]: t for t in _TEAMS_CACHE}
    return _TEAMS_CACHE


def teams_by_id() -> dict[str, dict]:
    load_teams()
    return _TEAMS_BY_ID  # type: ignore[return-value]


def default_formation_name(team: dict) -> str:
    idx = team.get("defaultFormation", 0)
    formations = team.get("formations", ["4-3-3"])
    if idx < 0 or idx >= len(formations):
        idx = 0
    return formations[idx]


def resolve_team(query: str) -> dict | None:
    q = query.strip().lower()
    if not q:
        return None
    by_id = teams_by_id()
    if q in by_id:
        return by_id[q]
    for t in load_teams():
        if q == t["name"].lower() or q == t["nameEn"].lower():
            return t
    q_norm = re.sub(r"\s+", "", q)
    for t in load_teams():
        for field in ("name", "nameEn", "id"):
            val = str(t.get(field, "")).lower().replace(" ", "")
            if q_norm == val or q_norm in val or val in q_norm:
                return t
    return None


def suggest_teams(query: str, limit: int = 5) -> list[dict]:
    q = query.strip().lower()
    scored = []
    for t in load_teams():
        hay = f"{t['id']} {t['name']} {t['nameEn']}".lower()
        if q in hay:
            scored.append(t)
    return scored[:limit]


def get_position_penalty(player_pos_array: list[str], slot_label: str) -> float:
    if slot_label == "GK":
        return 1.0 if "GK" in player_pos_array else 0.0
    if len(player_pos_array) == 1 and player_pos_array[0] == "GK":
        return 0.0
    if slot_label in player_pos_array:
        return 1.0
    slot_line = POSITION_LINE.get(slot_label, 3)
    player_lines = list(set(POSITION_LINE.get(p, 3) for p in player_pos_array))
    min_line_diff = min(abs(pl - slot_line) for pl in player_lines)
    if min_line_diff == 0:
        return POS_PENALTY_SAME_AREA
    if min_line_diff == 1:
        return POS_PENALTY_ADJACENT
    return POS_PENALTY_FAR


def get_formation(name: str) -> dict | None:
    return FORMATION_LIBRARY.get(name)


def get_active_formation(
    team: dict,
    formation_index: int | None = None,
    formation_name: str | None = None,
) -> dict | None:
    if formation_name:
        return get_formation(formation_name)
    idx = formation_index if formation_index is not None else team.get("defaultFormation", 0)
    formations = team.get("formations", ["4-3-3"])
    if idx < 0 or idx >= len(formations):
        idx = 0
    return get_formation(formations[idx])


def get_starters_with_bonus(
    team: dict,
    formation_index: int | None = None,
    formation_name: str | None = None,
    starter_ids: list[str] | None = None,
) -> list[dict]:
    formation = get_active_formation(team, formation_index, formation_name)
    if not formation:
        return []
    ids = starter_ids if starter_ids else team.get("defaultStarters", [])
    player_map = {p["id"]: p for p in team.get("players", [])}
    result = []
    for i, pid in enumerate(ids):
        player = player_map.get(pid)
        slot = formation["slots"][i] if i < len(formation["slots"]) else formation["slots"][-1]
        rating = player["rating"] if player and player.get("rating", 0) > 0 else 0
        result.append({
            "player": player,
            "slot": slot,
            "bonusMultiplier": 1 + slot["bonus"],
            "adjustedRating": rating * (1 + slot["bonus"]),
        })
    return result


def calculate_adjusted_ratings(
    team: dict,
    formation_index: int | None = None,
    formation_name: str | None = None,
    starter_ids: list[str] | None = None,
) -> dict:
    starters = get_starters_with_bonus(team, formation_index, formation_name, starter_ids)
    ratings = []
    for s in starters:
        if not s["player"] or s["player"].get("rating", 0) <= 0:
            continue
        pos_penalty = get_position_penalty(s["player"]["pos"], s["slot"]["label"])
        ratings.append(round(s["adjustedRating"] * pos_penalty))
    avg = sum(ratings) / len(ratings) if ratings else 0
    return {"ratings": ratings, "avg": avg, "starters": starters}


def sort_by_rating_then_age(starters: list[dict]) -> list[dict]:
    valid = [s for s in starters if s.get("player") and s["player"].get("rating", 0) > 0]
    return sorted(valid, key=lambda s: (-s["player"]["rating"], s["player"].get("age", 99)))


def get_star_tier_boost(rating: float) -> float:
    if rating >= STAR_TIER1_MIN:
        return STAR_TIER1_BOOST
    if rating >= STAR_TIER2_MIN:
        return STAR_TIER2_BOOST
    if rating >= STAR_TIER3_MIN:
        return STAR_TIER3_BOOST
    return STAR_TIER4_BOOST


def apply_star_weight(starters: list[dict], count: int, star_mult: float, star_factor: float = 0.5) -> float:
    valid = [s for s in starters if s.get("player") and s["player"].get("rating", 0) > 0]
    if not valid:
        return 0.0
    sorted_players = sort_by_rating_then_age(valid)
    star_count = min(count, len(sorted_players))
    team_boost = 1.0 + max(0, 0.5 - star_factor) * TEAM_BOOST_RANGE
    total = 0.0
    for i, s in enumerate(sorted_players):
        r = s["player"]["rating"]
        if i < star_count:
            tier_boost = get_star_tier_boost(r)
            total += r * star_mult * tier_boost
        else:
            total += r * team_boost
    return total / len(sorted_players)


def blend_form_heritage(form_rating: float, heritage_rating: float, form_weight: float) -> float:
    return form_rating * (1 - form_weight) + heritage_rating * form_weight


def apply_openness(base_rating: float, play_style: float, openness_value: float, scale: float) -> float:
    factor = (openness_value - 50) / 50
    bonus = (play_style - 50) * factor * scale
    return base_rating + bonus


def sigmoid(x: float, steepness: float) -> float:
    return 1 / (1 + math.exp(-x / steepness))


def poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    log_p = -lam + k * math.log(lam)
    for i in range(2, k + 1):
        log_p -= math.log(i)
    return math.exp(log_p)


def predict_top_scores(diff: float, openness_value: float, top_n: int = 3) -> list[dict]:
    base_goals = GOAL_BASE_MIN + (openness_value / 100) * GOAL_RANGE
    gap_amplifier = 1 + abs(diff) * GAP_GOAL_SCALE * (openness_value / 100)
    total_goals = base_goals * gap_amplifier
    win_rate = sigmoid(diff, SIGMOID_STEEPNESS)
    a_share = 0.5 + (win_rate - 0.5) * GOAL_SHARE_BIAS
    lambda_a = total_goals * a_share
    lambda_b = total_goals * (1 - a_share)
    all_scores = []
    for a in range(10):
        for b in range(10):
            prob = poisson_pmf(a, lambda_a) * poisson_pmf(b, lambda_b)
            all_scores.append({"a": a, "b": b, "prob": prob})
    all_scores.sort(key=lambda x: x["prob"], reverse=True)
    return [
        {
            "home": s["a"], "away": s["b"],
            "display": f"{s['a']}:{s['b']}",
            "probability": f"{s['prob'] * 100:.1f}",
            "probRaw": s["prob"],
        }
        for s in all_scores[:top_n]
    ]


def validate_starters(team: dict, starter_ids: list[str]) -> str | None:
    if len(starter_ids) != 11:
        return f"{team['name']} 首发必须为 11 人，当前 {len(starter_ids)} 人"
    player_map = {p["id"]: p for p in team.get("players", [])}
    for pid in starter_ids:
        if pid not in player_map:
            return f"{team['name']} 无效球员 id：{pid}"
    return None


def build_lineup_summary(team: dict, formation_name: str, starter_ids: list[str] | None) -> dict:
    """Return starters (with slot) and bench (remaining squad players)."""
    formation = get_formation(formation_name)
    ids = starter_ids if starter_ids else team.get("defaultStarters", [])
    player_map = {p["id"]: p for p in team.get("players", [])}
    starters = []
    if formation:
        for i, pid in enumerate(ids):
            p = player_map.get(pid, {})
            slot = formation["slots"][i]["label"] if i < len(formation["slots"]) else "?"
            starters.append({
                "slot": slot,
                "id": pid,
                "name": p.get("name", ""),
                "nameEn": p.get("nameEn", ""),
                "rating": p.get("rating", 0),
            })
    bench = []
    for pid, p in player_map.items():
        if pid in ids or p.get("rating", 0) <= 0:
            continue
        bench.append({
            "id": pid,
            "name": p.get("name", ""),
            "nameEn": p.get("nameEn", ""),
            "rating": p.get("rating", 0),
        })
    bench.sort(key=lambda x: (-x["rating"], x.get("nameEn", "")))
    return {"starters": starters, "bench": bench}


def predict(team_a: dict, team_b: dict, params: dict) -> dict:
    fa_name = params.get("formationNameA")
    fb_name = params.get("formationNameB")
    fa_idx = None if fa_name else params.get("formationA")
    fb_idx = None if fb_name else params.get("formationB")

    a_adj = calculate_adjusted_ratings(team_a, fa_idx, fa_name, params.get("starterIdsA"))
    b_adj = calculate_adjusted_ratings(team_b, fb_idx, fb_name, params.get("starterIdsB"))

    sf_a = params.get("starWeightA")
    if sf_a is None:
        sf_a = params.get("starWeight", 0.5)
    sf_b = params.get("starWeightB")
    if sf_b is None:
        sf_b = params.get("starWeight", 0.5)

    a_star = apply_star_weight(a_adj["starters"], STAR_COUNT, 1 + (STAR_WEIGHT - 1) * sf_a, sf_a)
    b_star = apply_star_weight(b_adj["starters"], STAR_COUNT, 1 + (STAR_WEIGHT - 1) * sf_b, sf_b)

    fw = params.get("formWeight", 0.5)
    a_blend = blend_form_heritage(a_star, team_a.get("heritage", 50), fw)
    b_blend = blend_form_heritage(b_star, team_b.get("heritage", 50), fw)

    ov = params.get("openness", 50.0)
    a_final = apply_openness(a_blend, team_a.get("playStyle", 50), ov, OPENNESS_SCALE)
    b_final = apply_openness(b_blend, team_b.get("playStyle", 50), ov, OPENNESS_SCALE)

    diff = a_final - b_final
    win_rate_a = sigmoid(diff, SIGMOID_STEEPNESS)
    top_scores = predict_top_scores(diff, ov, 3)
    best_score = top_scores[0]

    all_starters = []
    for s in a_adj["starters"] + b_adj["starters"]:
        if not s["player"] or s["player"].get("rating", 0) <= 0:
            continue
        pos_penalty = get_position_penalty(s["player"]["pos"], s["slot"]["label"])
        all_starters.append({"player": s["player"], "finalScore": round(s["adjustedRating"] * pos_penalty)})
    all_starters.sort(key=lambda x: x["finalScore"], reverse=True)
    top_players = [
        {"name": s["player"]["name"], "nameEn": s["player"]["nameEn"], "rating": s["finalScore"]}
        for s in all_starters[:3]
    ]

    keywords = []
    if ov <= KEYWORD_OPEN_LOW:
        keywords.append("沉闷保守")
    elif ov >= KEYWORD_OPEN_HIGH:
        keywords.append("酣畅对攻")
    if abs(diff) < KEYWORD_DIFF_CLOSE:
        keywords.append("势均力敌")
    elif diff > KEYWORD_DIFF_BIG:
        keywords.append("碾压之势")
    elif diff < -KEYWORD_DIFF_BIG:
        keywords.append("以下克上")

    fmt_name = fa_name or default_formation_name(team_a)
    fmt_name_b = fb_name or default_formation_name(team_b)
    ids_a = params.get("starterIdsA") or team_a.get("defaultStarters", [])
    ids_b = params.get("starterIdsB") or team_b.get("defaultStarters", [])

    return {
        "teamA": {"id": team_a["id"], "name": team_a["name"], "nameEn": team_a["nameEn"],
                  "flag": team_a["flag"], "rating": f"{a_final:.1f}", "formation": fmt_name},
        "teamB": {"id": team_b["id"], "name": team_b["name"], "nameEn": team_b["nameEn"],
                  "flag": team_b["flag"], "rating": f"{b_final:.1f}", "formation": fmt_name_b},
        "winRateA": f"{win_rate_a * 100:.1f}",
        "winRateB": f"{(1 - win_rate_a) * 100:.1f}",
        "score": {"a": best_score["home"], "b": best_score["away"]},
        "topScores": top_scores,
        "diff": f"{diff:.1f}",
        "topPlayers": top_players,
        "keywords": keywords,
        "settings": {
            "openness": ov,
            "formWeight": fw,
            "starWeightA": sf_a,
            "starWeightB": sf_b,
        },
        "lineupA": build_lineup_summary(team_a, fmt_name, ids_a),
        "lineupB": build_lineup_summary(team_b, fmt_name_b, ids_b),
        "debug": {
            "aRaw": f"{a_adj['avg']:.1f}", "bRaw": f"{b_adj['avg']:.1f}",
            "aStar": f"{a_star:.1f}", "bStar": f"{b_star:.1f}",
            "aBlend": f"{a_blend:.1f}", "bBlend": f"{b_blend:.1f}",
            "aFinal": f"{a_final:.1f}", "bFinal": f"{b_final:.1f}",
        },
    }
