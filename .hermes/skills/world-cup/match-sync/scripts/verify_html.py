#!/usr/bin/env python3
"""Verify AI_ROUNDS data integrity in 世界杯预测.html."""

import json
import os
import re
import sys


def find_html_file():
    candidates = [
        os.path.expanduser("~/world-cup/世界杯预测.html"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "世界杯预测.html"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


def verify(html_path):
    errors = []
    warnings = []

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'const AI_ROUNDS\s*=\s*(\[[\s\S]*?\]);'
    m = re.search(pattern, content)
    if not m:
        errors.append("AI_ROUNDS not found in HTML")
        return errors, warnings

    rounds_text = m.group(1)

    try:
        rounds = json.loads(rounds_text)
    except json.JSONDecodeError as e:
        errors.append(f"AI_ROUNDS JSON parse error: {e}")
        return errors, warnings

    model_ids = {"gpt55", "glm51", "qwen37", "deepseek", "mimo", "kimi"}
    bet_fields = {"match", "matchId", "playType", "pick", "amount", "odds", "actualScore", "result", "prize"}

    for r in rounds:
        round_num = r.get("round", "?")
        status = r.get("status", "")
        if status not in ("active", "completed"):
            warnings.append(f"Round {round_num}: unexpected status '{status}'")

        predictions = r.get("predictions", {})
        for model_id, pred in predictions.items():
            if model_id not in model_ids:
                warnings.append(f"Round {round_num}: unknown model '{model_id}'")

            bets = pred.get("bets", [])
            for i, bet in enumerate(bets):
                missing = bet_fields - set(bet.keys())
                if missing:
                    errors.append(f"Round {round_num}/{model_id}/bet[{i}]: missing fields {missing}")

                result = bet.get("result", "")
                if result not in ("win", "loss", "pending", ""):
                    errors.append(f"Round {round_num}/{model_id}/bet[{i}]: invalid result '{result}'")

                if result in ("win", "loss") and not bet.get("actualScore"):
                    warnings.append(f"Round {round_num}/{model_id}/bet[{i}]: has result but no actualScore")

                if result == "win" and (bet.get("prize", 0) <= 0):
                    errors.append(f"Round {round_num}/{model_id}/bet[{i}]: win but prize={bet.get('prize', 0)}")

                if result == "loss" and bet.get("prize", 0) > 0:
                    errors.append(f"Round {round_num}/{model_id}/bet[{i}]: loss but prize={bet.get('prize', 0)}")

    return errors, warnings


def main():
    html_path = find_html_file()
    if not html_path:
        print("Could not find HTML file", file=sys.stderr)
        sys.exit(1)

    errors, warnings = verify(html_path)

    if warnings:
        print(f"[WARN] {len(warnings)} warning(s):", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)

    if errors:
        print(f"[FAIL] {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[PASS] AI_ROUNDS verification passed ({len(warnings)} warning(s))", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
