"""Builds data/raw/knowledge_base.csv from a compact tag list.

Each candidate lists only the attributes that are TRUE; everything else is 0.
Edit CANDIDATES below, run `python data/build_knowledge_base.py`, and the CSV is
regenerated (and checked for candidates that no question can tell apart).

IMPORTANT: this is a starter dataset written from general knowledge.
Verify every row against Wikipedia/Wikidata before submitting, and extend it
to your target size (about 150-200 candidates).
"""
import csv
import sys
from pathlib import Path

ATTRS = {
    "P": "is_person", "PL": "is_place", "AL": "is_alive", "M": "is_male", "F": "is_female",
    "B50": "born_before_1950", "C21": "active_in_21st_century",
    "POL": "is_politician", "PM": "was_prime_minister", "PRES": "was_president",
    "MIL": "is_military_figure", "CRK": "is_cricketer", "FB": "is_fast_bowler", "CAPT": "captained_national_team",
    "SPT": "is_other_sportsperson", "ACT": "is_actor_or_filmmaker",
    "MUS": "is_singer_or_musician", "WRI": "is_writer_or_poet",
    "SCI": "is_scientist_or_academic", "ACV": "is_activist_or_humanitarian",
    "BIZ": "is_businessperson", "TV": "is_tv_personality",
    "AWD": "won_international_award", "INTL": "is_known_internationally",
    "PAK": "linked_to_pakistan_movement",
    "PUN": "region_punjab", "SIN": "region_sindh", "KPK": "region_kpk",
    "BAL": "region_balochistan", "ISB": "region_islamabad_gb_ajk",
    "CITY": "is_city", "CAP": "is_capital_city", "MON": "is_historical_monument",
    "REL": "is_religious_site", "MOSQ": "is_mosque", "SHR": "is_shrine_or_tomb",
    "FORT": "is_fort_or_palace", "NAT": "is_natural_landmark", "PEAK": "is_peak",
    "LAKE": "is_lake", "VAL": "is_valley_or_meadow", "UNE": "is_unesco_world_heritage",
    "COA": "is_coastal", "MTN": "is_in_mountains", "TOUR": "is_tourist_destination",
    "FOOD": "is_known_for_food", "MUG": "is_mughal_era",
}

CANDIDATES = [
    # ---------------- People: politics & state ----------------
    ("Muhammad Ali Jinnah", "P M B50 POL PAK SIN INTL"),
    ("Fatima Jinnah", "P F B50 POL ACV PAK SIN"),
    ("Liaquat Ali Khan", "P M B50 POL PM PAK"),
    ("Zulfikar Ali Bhutto", "P M B50 POL PM PRES SIN INTL"),
    ("Benazir Bhutto", "P F POL PM SIN INTL C21"),
    ("Nawaz Sharif", "P M AL POL PM BIZ PUN C21 INTL"),
    ("Shehbaz Sharif", "P M AL POL PM BIZ PUN C21"),
    ("Imran Khan", "P M AL POL PM CRK FB CAPT ACV PUN C21 INTL"),
    ("Asif Ali Zardari", "P M AL POL PRES BIZ SIN C21"),
    ("Pervez Musharraf", "P M B50 POL PRES MIL C21 INTL"),
    ("Zia-ul-Haq", "P M B50 POL PRES MIL"),
    ("Ayub Khan", "P M B50 POL PRES MIL KPK"),
    ("Bilawal Bhutto Zardari", "P M AL POL SIN C21"),
    ("Maryam Nawaz", "P F AL POL PUN C21"),
    ("Abdul Ghaffar Khan", "P M B50 POL ACV KPK"),
    # ---------------- People: science, activism, writing ----------------
    ("Malala Yousafzai", "P F AL ACV AWD KPK C21 INTL"),
    ("Abdus Salam", "P M B50 SCI AWD PUN INTL"),
    ("Abdul Qadeer Khan", "P M B50 SCI C21 INTL"),
    ("Abdul Sattar Edhi", "P M B50 ACV SIN C21 INTL"),
    ("Sharmeen Obaid-Chinoy", "P F AL ACT ACV AWD SIN C21 INTL"),
    ("Allama Muhammad Iqbal", "P M B50 WRI PAK PUN INTL"),
    ("Faiz Ahmed Faiz", "P M B50 WRI PUN INTL"),
    ("Saadat Hasan Manto", "P M B50 WRI"),
    ("Bano Qudsia", "P F B50 WRI"),
    ("Mustansar Hussain Tarar", "P M AL B50 WRI TV PUN C21"),
    # ---------------- People: music, film, TV ----------------
    ("Nusrat Fateh Ali Khan", "P M B50 MUS PUN INTL"),
    ("Rahat Fateh Ali Khan", "P M AL MUS PUN C21 INTL"),
    ("Atif Aslam", "P M AL MUS ACT PUN C21 INTL"),
    ("Abida Parveen", "P F AL MUS SIN C21 INTL"),
    ("Noor Jehan", "P F B50 MUS ACT PUN"),
    ("Mehdi Hassan", "P M B50 MUS"),
        ("Mahira Khan", "P F AL ACT SIN C21 INTL"),
    ("Fawad Khan", "P M AL ACT SIN C21 INTL"),
    ("Humayun Saeed", "P M AL ACT SIN C21"),
    ("Moin Akhtar", "P M ACT TV SIN C21"),
    # ---------------- People: sport ----------------
    ("Wasim Akram", "P M AL CRK FB CAPT TV PUN C21 INTL"),
    ("Waqar Younis", "P M AL CRK FB CAPT PUN C21 INTL"),
    ("Javed Miandad", "P M AL CRK CAPT SIN"),
    ("Inzamam-ul-Haq", "P M AL CRK CAPT PUN C21"),
    ("Younis Khan", "P M AL CRK CAPT KPK C21"),
    ("Shahid Afridi", "P M AL CRK CAPT KPK C21 INTL"),
    ("Shoaib Akhtar", "P M AL CRK FB TV PUN C21 INTL"),
    ("Babar Azam", "P M AL CRK CAPT PUN C21 INTL"),
    ("Hanif Mohammad", "P M B50 CRK CAPT"),
    ("Jahangir Khan", "P M AL SPT INTL"),
    ("Jansher Khan", "P M AL SPT KPK INTL"),
    ("Arshad Nadeem", "P M AL SPT AWD PUN C21 INTL"),
    # ---------------- Places: Punjab & Islamabad ----------------
    ("Minar-e-Pakistan", "PL MON PAK PUN TOUR"),
    ("Badshahi Mosque", "PL MON REL MOSQ PUN TOUR MUG INTL"),
    ("Lahore Fort", "PL MON FORT UNE PUN TOUR MUG"),
    ("Shalimar Gardens", "PL MON UNE PUN TOUR MUG"),
    ("Rohtas Fort", "PL MON FORT UNE PUN TOUR"),
    ("Derawar Fort", "PL MON FORT PUN"),
    ("Taxila", "PL MON UNE PUN TOUR"),
    ("Data Darbar", "PL REL SHR PUN"),
    ("Wagah Border", "PL PUN TOUR INTL"),
    ("Khewra Salt Mine", "PL NAT PUN TOUR"),
    ("Murree", "PL CITY PUN MTN TOUR"),
    ("Lahore", "PL CITY CAP PUN FOOD TOUR MUG INTL"),
    ("Multan", "PL CITY PUN REL"),
    ("Rawalpindi", "PL CITY PUN"),
    ("Islamabad", "PL CITY CAP ISB TOUR"),
    ("Faisal Mosque", "PL REL MOSQ ISB TOUR INTL"),
    ("Pakistan Monument", "PL MON ISB PAK TOUR"),
    # ---------------- Places: Sindh ----------------
    ("Mazar-e-Quaid", "PL MON SHR PAK SIN TOUR"),
    ("Mohenjo-daro", "PL MON UNE SIN TOUR INTL"),
    ("Makli Necropolis", "PL MON SHR UNE SIN"),
    ("Mohatta Palace", "PL MON FORT SIN TOUR"),
    ("Lal Shahbaz Qalandar Shrine", "PL REL SHR SIN"),
    ("Clifton Beach", "PL NAT SIN COA TOUR"),
    ("Karachi", "PL CITY CAP SIN COA FOOD INTL"),
    ("Hyderabad", "PL CITY SIN FOOD"),
    # ---------------- Places: Khyber Pakhtunkhwa ----------------
    ("Swat Valley", "PL NAT VAL KPK MTN TOUR INTL"),
    ("Lake Saiful Muluk", "PL NAT LAKE KPK MTN TOUR"),
    ("Naran", "PL NAT VAL KPK MTN TOUR"),
    ("Khyber Pass", "PL NAT KPK INTL"),
    ("Peshawar", "PL CITY CAP KPK FOOD"),
    ("Chitral", "PL CITY KPK MTN TOUR"),
    # ---------------- Places: Balochistan ----------------
    ("Quetta", "PL CITY CAP BAL MTN"),
    ("Gwadar", "PL CITY BAL COA TOUR"),
    ("Hingol National Park", "PL NAT BAL COA TOUR"),
    ("Ziarat Juniper Forest", "PL NAT BAL MTN TOUR"),
    ("Hanna Lake", "PL NAT LAKE BAL TOUR"),
    # ---------------- Places: Gilgit-Baltistan ----------------
    ("K2", "PL NAT PEAK ISB MTN INTL"),
    ("Nanga Parbat", "PL NAT PEAK ISB MTN"),
    ("Hunza Valley", "PL NAT VAL ISB MTN TOUR INTL"),
    ("Baltit Fort", "PL MON FORT ISB MTN TOUR"),
    ("Fairy Meadows", "PL NAT VAL ISB MTN TOUR"),
    ("Attabad Lake", "PL NAT LAKE ISB MTN TOUR"),
    ("Deosai National Park", "PL NAT ISB MTN TOUR"),
    ("Skardu", "PL CITY ISB MTN TOUR"),
    ("Gilgit", "PL CITY CAP ISB MTN TOUR"),
]


def build(out_path: Path) -> list[list[str]]:
    columns = list(ATTRS.values())
    rows, seen = [], {}
    for name, tags in CANDIDATES:
        tagset = tags.split()
        unknown = [t for t in tagset if t not in ATTRS]
        if unknown:
            raise SystemExit(f"{name}: unknown tag(s) {unknown}")
        vec = tuple(1 if ATTRS[t] in tagset_names(tagset) else 0 for t in ATTRS)
        seen.setdefault(vec, []).append(name)
        rows.append([name, *vec])
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", *columns])
        w.writerows(rows)
    dups = [g for g in seen.values() if len(g) > 1]
    print(f"Wrote {len(rows)} candidates x {len(columns)} attributes to {out_path}")
    if dups:
        print("WARNING - indistinguishable candidates:", dups)
    return rows


def tagset_names(tagset):
    return {ATTRS[t] for t in tagset}


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    build(here / "raw" / "knowledge_base.csv")
    sys.exit(0)
