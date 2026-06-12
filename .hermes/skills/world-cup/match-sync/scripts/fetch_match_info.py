#!/usr/bin/env python3
"""Fetch latest World Cup 2026 match info and results from ESPN API."""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime


TEAM_NAME_MAP = {
    "Mexico": "墨西哥", "South Africa": "南非", "South Korea": "韩国",
    "Czech Republic": "捷克", "Canada": "加拿大", "Bosnia and Herzegovina": "波黑",
    "Qatar": "卡塔尔", "Switzerland": "瑞士", "United States": "美国",
    "Paraguay": "巴拉圭", "Australia": "澳大利亚", "Turkey": "土耳其",
    "Brazil": "巴西", "Morocco": "摩洛哥", "Haiti": "海地", "Scotland": "苏格兰",
    "Germany": "德国", "Curacao": "库拉索", "Ivory Coast": "科特迪瓦",
    "Cote d'Ivoire": "科特迪瓦", "Ecuador": "厄瓜多尔",
    "Netherlands": "荷兰", "Japan": "日本", "Sweden": "瑞典", "Tunisia": "突尼斯",
    "Spain": "西班牙", "Cape Verde": "佛得角", "Saudi Arabia": "沙特",
    "Uruguay": "乌拉圭", "Belgium": "比利时", "Egypt": "埃及",
    "Iran": "伊朗", "New Zealand": "新西兰", "France": "法国",
    "Senegal": "塞内加尔", "Iraq": "伊拉克", "Norway": "挪威",
    "Argentina": "阿根廷", "Algeria": "阿尔及利亚", "Austria": "奥地利",
    "Jordan": "约旦", "Portugal": "葡萄牙",
    "DR Congo": "民主刚果", "Uzbekistan": "乌兹别克", "Colombia": "哥伦比亚",
    "England": "英格兰", "Croatia": "克罗地亚", "Ghana": "加纳", "Panama": "巴拿马",
}


def fetch_espn_worldcup():
    """Fetch World Cup 2026 data from ESPN API."""
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching ESPN: {e}", file=sys.stderr)
        return None


def extract_results(data):
    """Extract finished match results from ESPN data."""
    results = []
    for event in data.get("events", []):
        comps = event.get("competitions", [])
        if not comps:
            continue
        comp = comps[0]
        status_type = comp.get("status", {}).get("type", {}).get("name", "")
        if status_type not in ("STATUS_FINAL", "STATUS_PLAY"):
            continue
        is_finished = status_type == "STATUS_FINAL"
        scores = comp.get("scores", [])
        if len(scores) < 2:
            continue
        home_team = scores[0].get("team", {}).get("displayName", "")
        away_team = scores[1].get("team", {}).get("displayName", "")
        home_score = scores[0].get("score")
        away_score = scores[1].get("score")
        date_str = comp.get("date", "")
        home_cn = TEAM_NAME_MAP.get(home_team, home_team)
        away_cn = TEAM_NAME_MAP.get(away_team, away_team)
        results.append({
            "home": home_cn,
            "homeEn": home_team,
            "away": away_cn,
            "awayEn": away_team,
            "score": f"{home_score}:{away_score}" if home_score is not None else "",
            "homeScore": int(home_score) if home_score is not None else None,
            "awayScore": int(away_score) if away_score is not None else None,
            "status": "finished" if is_finished else "live",
            "date": date_str,
        })
    return results


def match_with_html(match_entry, result):
    """Try to match an ESPN result with an HTML match entry by team names."""
    home_cn = result.get("home", "")
    away_cn = result.get("away", "")
    match_text = match_entry.get("match", "")
    if home_cn in match_text and away_cn in match_text:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Fetch World Cup 2026 match results")
    parser.add_argument("--round", type=int, help="Round number to focus on")
    parser.add_argument("--output", default="-", help="Output file (- for stdout)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    data = fetch_espn_worldcup()
    if not data:
        print("Failed to fetch data from ESPN", file=sys.stderr)
        sys.exit(1)

    results = extract_results(data)

    if args.verbose:
        print(f"Fetched {len(results)} match results from ESPN", file=sys.stderr)
        for r in results:
            status_mark = "✓" if r["status"] == "finished" else "⏳"
            print(f"  {status_mark} {r['home']} vs {r['away']} {r['score']}", file=sys.stderr)

    output = {
        "round": args.round,
        "results": results,
        "fetched_at": datetime.now().isoformat(),
        "source": "ESPN",
    }

    out_str = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(out_str)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_str)
        if args.verbose:
            print(f"Results saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
