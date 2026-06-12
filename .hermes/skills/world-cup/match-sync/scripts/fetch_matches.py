#!/usr/bin/env python3
"""Fetch latest World Cup 2026 match schedule and results from FIFA/ESPN APIs.

Outputs structured JSON that can be consumed by update_match_html.py
to update the 世界杯预测.html group-stage table and AI_ROUNDS data.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta


CST = timezone(timedelta(hours=8))

MATCH_ID_RE = re.compile(r"M(\d+)")

GROUP_STAGE_MATCHES = 72


def fetch_espn_schedule():
    """Fetch World Cup schedule from ESPN API."""
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching ESPN schedule: {e}", file=sys.stderr)
        return []

    matches = []
    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        status_type = comp.get("status", {}).get("type", {}).get("name", "")
        scores = comp.get("scores", [])

        home_team = ""
        away_team = ""
        home_score = ""
        away_score = ""
        if len(scores) >= 2:
            home_team = scores[0].get("team", {}).get("displayName", "")
            away_team = scores[1].get("team", {}).get("displayName", "")
            home_score = scores[0].get("score", "")
            away_score = scores[1].get("score", "")

        date_str = comp.get("date", "")
        venue = comp.get("venue", {}).get("fullName", "")

        is_finished = status_type == "STATUS_FINAL"
        is_live = status_type == "STATUS_IN_PROGRESS"
        is_scheduled = status_type == "STATUS_SCHEDULED"

        match_data = {
            "home": home_team,
            "away": away_team,
            "date": date_str,
            "venue": venue,
            "status": "finished" if is_finished else "live" if is_live else "scheduled",
            "score": f"{home_score}:{away_score}" if is_finished or is_live else "",
        }
        matches.append(match_data)

    return matches


def fetch_fifa_schedule():
    """Fetch schedule from FIFA.com API (backup source)."""
    url = "https://api.fifa.com/api/v3/calendar/matches?idCompetition=17&idSeason=255711&count=100"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching FIFA schedule: {e}", file=sys.stderr)
        return []

    matches = []
    for item in data.get("Results", []):
        home = item.get("Home", {})
        away = item.get("Away", {})
        stage = item.get("StageName", [{}])[0].get("Description", "")
        group = item.get("GroupName", [{}])[0].get("Description", "")
        venue = item.get("Stadium", {}).get("Name", [{}])[0].get("Description", "")
        date_str = item.get("Date", "")

        home_score = home.get("Score", "")
        away_score = away.get("Score", "")
        home_team = home.get("ShortClubName", "")
        away_team = away.get("ShortClubName", "")

        match_status = item.get("MatchStatus", 0)
        if match_status == 10:
            status = "finished"
        elif match_status in (3, 4, 5, 6, 7):
            status = "live"
        else:
            status = "scheduled"

        match_data = {
            "home": home_team,
            "away": away_team,
            "group": group,
            "date": date_str,
            "venue": venue,
            "status": status,
            "score": f"{home_score}:{away_score}" if status in ("finished", "live") else "",
            "stage": stage,
        }
        matches.append(match_data)

    return matches


def main():
    parser = argparse.ArgumentParser(description="Fetch World Cup 2026 match info")
    parser.add_argument("--source", choices=["espn", "fifa", "both"], default="espn",
                        help="Data source (default: espn)")
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--finished-only", action="store_true",
                        help="Only output finished matches")
    args = parser.parse_args()

    all_matches = []

    if args.source in ("espn", "both"):
        espn_matches = fetch_espn_schedule()
        print(f"ESPN: fetched {len(espn_matches)} matches", file=sys.stderr)
        all_matches.extend(espn_matches)

    if args.source in ("fifa", "both"):
        fifa_matches = fetch_fifa_schedule()
        print(f"FIFA: fetched {len(fifa_matches)} matches", file=sys.stderr)
        all_matches.extend(fifa_matches)

    if args.finished_only:
        all_matches = [m for m in all_matches if m["status"] == "finished"]

    output = {
        "fetched_at": datetime.now(CST).isoformat(),
        "source": args.source,
        "match_count": len(all_matches),
        "matches": all_matches,
    }

    out_str = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        print(f"Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
