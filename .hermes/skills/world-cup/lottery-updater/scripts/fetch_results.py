#!/usr/bin/env python3
"""Fetch match results from ESPN/FIFA and output as JSON."""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime


def fetch_espn_results(date_str=None):
    """Fetch results from ESPN World Cup 2026 API."""
    base_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
    try:
        with urllib.request.urlopen(base_url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching ESPN: {e}", file=sys.stderr)
        return []

    results = []
    events = data.get("events", [])
    for event in events:
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        status = comp.get("status", {}).get("type", {}).get("name", "")
        if status != "STATUS_FINAL":
            continue
        scores = comp.get("scores", [])
        if len(scores) < 2:
            continue
        home = scores[0].get("team", {}).get("displayName", "")
        away = scores[1].get("team", {}).get("displayName", "")
        home_score = scores[0].get("score", "?")
        away_score = scores[1].get("score", "?")
        results.append({
            "home": home,
            "away": away,
            "score": f"{home_score}:{away_score}",
            "status": "finished",
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch World Cup 2026 match results")
    parser.add_argument("--round", type=int, help="Round number")
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--auto-update", action="store_true", help="Auto-update HTML if results found")
    args = parser.parse_args()

    results = fetch_espn_results()

    output = {"round": args.round, "results": results, "fetched_at": datetime.now().isoformat()}

    out_str = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)

    if args.auto_update and results:
        print(f"Found {len(results)} finished matches, running auto-update...", file=sys.stderr)


if __name__ == "__main__":
    main()
