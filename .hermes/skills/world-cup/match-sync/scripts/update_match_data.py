#!/usr/bin/env python3
"""Update AI_ROUNDS in 世界杯预测.html with match results and prize calculations."""

import argparse
import json
import os
import re
import sys
import copy

HTML_FILE_KEY = "世界杯预测.html"


def find_html_file():
    """Find the HTML file path."""
    candidates = [
        os.path.expanduser("~/world-cup/世界杯预测.html"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "世界杯预测.html"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


def extract_ai_rounds(content):
    """Extract AI_ROUNDS JavaScript array from HTML content as text."""
    pattern = r'const AI_ROUNDS\s*=\s*(\[[\s\S]*?\]);'
    m = re.search(pattern, content)
    if not m:
        return None, None
    return m.group(1), m.group(0)


def determine_result(play_type, pick, home_score, away_score, handicap=0):
    """Determine if a bet wins based on actual score."""
    if play_type == "胜平负":
        if home_score > away_score:
            actual = "主胜"
        elif home_score == away_score:
            actual = "平"
        else:
            actual = "客胜"
        return actual == pick
    elif "让球" in play_type:
        adjusted_home = home_score + handicap
        if adjusted_home > away_score:
            actual = "让胜"
        elif adjusted_home == away_score:
            actual = "让平"
        else:
            actual = "让负"
        pick_map = {"让胜": "让胜", "让平": "让平", "让负": "让负"}
        for key in pick_map:
            if key in pick:
                return actual == key
    return False


def parse_handicap(pick_str):
    """Parse handicap value from pick string like '让胜(-1)' or '让平(-2)'."""
    m = re.search(r'\((-?\d+)\)', pick_str)
    if m:
        return int(m.group(1))
    return 0


def calculate_prize(bet, is_win):
    """Calculate prize for a winning bet."""
    if not is_win:
        return 0
    odds = bet.get("odds", 0)
    amount = bet.get("amount", 0)
    if amount <= 0 or odds <= 0:
        return 0
    guoguan = bet.get("过关", "单关")
    multiplier = amount / 2
    if guoguan == "单关":
        return round(odds * 2 * multiplier, 2)
    else:
        return round(odds * 2 * multiplier, 2)


def calculate_parlay_prize(bets_group, results_map):
    """Calculate prize for a parlay (过关) bet group.

    bets_group: list of bets belonging to the same parlay ticket.
    results_map: {matchId: {homeScore, awayScore, ...}}
    Returns (all_win: bool, prize: float)
    """
    all_win = True
    combined_odds = 1.0
    amount = 0
    for bet in bets_group:
        bet_amount = bet.get("amount", 0)
        if bet_amount > 0:
            amount = bet_amount
        odds = bet.get("odds", 1.0)
        combined_odds *= odds
        match_id = bet.get("matchId", "")
        result_info = results_map.get(match_id)
        if not result_info or result_info.get("homeScore") is None:
            all_win = False
            break
        home_score = result_info["homeScore"]
        away_score = result_info["awayScore"]
        handicap = parse_handicap(bet.get("pick", ""))
        if not determine_result(bet.get("playType", ""), bet.get("pick", ""), home_score, away_score, handicap):
            all_win = False
            break

    if all_win and amount > 0:
        multiplier = amount / 2
        prize = round(combined_odds * 2 * multiplier, 2)
        return True, prize
    return False, 0


def update_html_with_results(html_path, results_data, round_num=None, dry_run=False):
    """Update AI_ROUNDS in HTML file with match results."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    rounds_text, full_match = extract_ai_rounds(content)
    if not rounds_text:
        print("Could not find AI_ROUNDS in HTML", file=sys.stderr)
        return False

    results_map = {}
    for r in results_data.get("results", []):
        key = r.get("matchId", "")
        if not key:
            for field in ["home", "away"]:
                if field in r:
                    key = f"{r.get('home', '')}_vs_{r.get('away', '')}"
                    break
        if key:
            results_map[key] = r

    if not results_map:
        print("No results to apply", file=sys.stderr)
        return False

    lines = content.split("\n")
    updated_lines = []
    changes = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if "actualScore:" in line and "result:" in line:
            match_id_m = re.search(r"matchId:\s*'([^']+)'", line)
            if match_id_m:
                match_id = match_id_m.group(1)
                result_info = results_map.get(match_id)
                if result_info and result_info.get("homeScore") is not None:
                    home_score = result_info["homeScore"]
                    away_score = result_info["awayScore"]
                    score_str = f"{home_score}:{away_score}"

                    if "actualScore: ''" in line or "actualScore: ''" in line:
                        line = re.sub(r"actualScore:\s*''", f"actualScore: '{score_str}'", line)
                        changes += 1

        if "result: 'pending'" in line:
            match_id_m = re.search(r"matchId:\s*'([^']+)'", line)
            if match_id_m:
                match_id = match_id_m.group(1)
                result_info = results_map.get(match_id)
                if result_info and result_info.get("homeScore") is not None:
                    home_score = result_info["homeScore"]
                    away_score = result_info["awayScore"]
                    play_type_m = re.search(r"playType:\s*'([^']+)'", line)
                    pick_m = re.search(r"pick:\s*'([^']+)'", line)
                    if play_type_m and pick_m:
                        play_type = play_type_m.group(1)
                        pick = pick_m.group(1)
                        handicap = parse_handicap(pick)
                        is_win = determine_result(play_type, pick, home_score, away_score, handicap)
                        result_val = "win" if is_win else "loss"
                        line = re.sub(r"result:\s*'pending'", f"result: '{result_val}'", line)
                        changes += 1

        updated_lines.append(line)
        i += 1

    print(f"Applied {changes} changes to HTML", file=sys.stderr)

    if dry_run:
        print("Dry run - no changes written", file=sys.stderr)
        return True

    new_content = "\n".join(updated_lines)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"HTML updated: {html_path}", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(description="Update HTML with match results")
    parser.add_argument("--round", type=int, help="Round number")
    parser.add_argument("--input", required=True, help="JSON file with results (from fetch_match_info.py)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    html_path = find_html_file()
    if not html_path:
        print("Could not find 世界杯预测.html", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        results_data = json.load(f)

    success = update_html_with_results(html_path, results_data, args.round, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
