# -*- coding: utf-8 -*-
"""Patch missing or CJK-only player nameEn fields in teams.json."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEAMS_JSON = ROOT / "wc-predictor" / "data" / "teams.json"

# id -> canonical English name
PATCHES = {
    "cod_CDM_mukau": "Ngal'ayel Mukau",
    "cuw_LWB_martha": "Ar'jany Martha",
    "civ_CB_ndicka": "Evan Ndicka",
    "cro_cb_duje_caleta_car": "Duje Ćaleta-Car",
    "bel_matias_fernandez_pardo": "Matías Fernández-Pardo",
    "ger_pascal_gross": "Pascal Groß",
    "fra_warren_zaire_emery": "Warren Zaire-Emery",
    "kor_kim_min_jae": "Kim Min Jae",
    "kor_park_jin_seob": "Park Jin Seob",
    "kor_lee_tae_suk": "Lee Tae Suk",
    "kor_cho_yu_min": "Cho Yu Min",
    "kor_kim_jin_gyu": "Kim Jin Gyu",
    "kor_bae_jun_ho": "Bae Jun Ho",
    "kor_paik_seung_ho": "Paik Seung Ho",
    "kor_eom_ji_sung": "Eom Ji Sung",
    "kor_kang_in_lee": "Lee Kang In",
    "kor_lee_jae_sung": "Lee Jae Sung",
    "kor_hwang_in_beom": "Hwang In Beom",
    "kor_hwang_hee_chan": "Hwang Hee Chan",
    "kor_heung_min_son": "Son Heung Min",
    "kor_cho_gue_sung": "Cho Gue Sung",
}

LATIN = re.compile(r"[A-Za-z]")


def audit(teams: list) -> tuple[list, list]:
    missing_en = []
    no_latin_en = []
    missing_zh = []
    for t in teams:
        for p in t.get("players", []):
            name = (p.get("name") or "").strip()
            name_en = p.get("nameEn")
            if not name:
                missing_zh.append((t["id"], p.get("id")))
            if name_en is None or not str(name_en).strip():
                missing_en.append((t["id"], p.get("id"), name))
            elif not LATIN.search(str(name_en)):
                no_latin_en.append((t["id"], p.get("id"), name, name_en))
    return missing_zh, missing_en, no_latin_en


def main() -> int:
    teams = json.loads(TEAMS_JSON.read_text(encoding="utf-8"))
    patched = 0
    for t in teams:
        for p in t.get("players", []):
            pid = p.get("id")
            if pid in PATCHES:
                p["nameEn"] = PATCHES[pid]
                patched += 1

    TEAMS_JSON.write_text(
        json.dumps(teams, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    missing_zh, missing_en, no_latin_en = audit(teams)
    print(f"Patched {patched} players in {TEAMS_JSON}")
    print(f"Missing Chinese name: {len(missing_zh)}")
    print(f"Missing nameEn: {len(missing_en)}")
    print(f"nameEn without Latin letters: {len(no_latin_en)}")
    if missing_zh or missing_en or no_latin_en:
        for row in missing_zh + missing_en + no_latin_en:
            print(" ", row)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
