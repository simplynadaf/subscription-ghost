"""bake_static.py: freeze a realistic demo into static-data.json for GitHub Pages.

Builds a believable "one person's subscriptions" list (including the Airtel-bundled
Amazon Prime used only for shopping, and an abandoned New Year gym), runs the REAL
TabPFN ranking and a REAL Gemma verdict for each, and writes web/assets/static-data.json.
The static UI reads this when there is no live backend, so the hosted demo shows real
model output and needs zero setup.

Run: python scripts/bake_static.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ghost import __version__, catalog
from ghost.predict import evaluate, load_rows, rank
from ghost.remember import write_verdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web", "assets", "static-data.json")

# A realistic Indian subscriber's list. Each dict is what the UI collects per service.
# uses_per_month and months_active are the honest usage signal the person would set.
DEMO = [
    # the hero story: Airtel Black bundled full Prime, used for shopping only
    {"name": "Amazon Prime", "tier": "Full Prime (annual)", "monthly_cost": 124.9,
     "annual_cost": 1499, "uses_per_month": 2, "months_active": 14, "price_creep_pct": 0,
     "is_annual_prepaid": 1, "trial_converted": 1, "n_tiers": 4, "category": "shopping"},
    # abandoned New Year gym
    {"name": "Gym / Fitness", "tier": "Annual (New Year pack)", "monthly_cost": 833,
     "annual_cost": 10000, "uses_per_month": 1, "months_active": 2, "price_creep_pct": 0,
     "is_annual_prepaid": 1, "trial_converted": 0, "n_tiers": 3, "category": "fitness"},
    # dead: Netflix Premium barely watched
    {"name": "Netflix", "tier": "Premium", "monthly_cost": 649, "annual_cost": 7788,
     "uses_per_month": 1, "months_active": 11, "price_creep_pct": 0, "is_annual_prepaid": 0,
     "trial_converted": 0, "n_tiers": 4, "category": "streaming"},
    # over-tier: Spotify Platinum but student
    {"name": "Spotify", "tier": "Platinum", "monthly_cost": 299, "annual_cost": 3588,
     "uses_per_month": 20, "months_active": 9, "price_creep_pct": 0, "is_annual_prepaid": 0,
     "trial_converted": 0, "n_tiers": 3, "category": "music"},
    # crept: ChatGPT Plus price rose, barely used
    {"name": "ChatGPT Plus", "tier": "Plus", "monthly_cost": 1900, "annual_cost": 22800,
     "uses_per_month": 2, "months_active": 6, "price_creep_pct": 35, "is_annual_prepaid": 0,
     "trial_converted": 1, "n_tiers": 1, "category": "productivity"},
    # dead: Swiggy One, rarely orders
    {"name": "Swiggy One", "tier": "One (3 months)", "monthly_cost": 83, "annual_cost": 996,
     "uses_per_month": 1, "months_active": 3, "price_creep_pct": 0, "is_annual_prepaid": 1,
     "trial_converted": 0, "n_tiers": 1, "category": "food"},
    # over-tier: iCloud 2TB, tiny usage
    {"name": "iCloud+", "tier": "2 TB", "monthly_cost": 749, "annual_cost": 8988,
     "uses_per_month": 3, "months_active": 18, "price_creep_pct": 0, "is_annual_prepaid": 0,
     "trial_converted": 0, "n_tiers": 3, "category": "cloud"},
    # worth it: JioHotstar Mobile, watched often
    {"name": "JioHotstar", "tier": "Mobile", "monthly_cost": 79, "annual_cost": 948,
     "uses_per_month": 18, "months_active": 10, "price_creep_pct": 0, "is_annual_prepaid": 0,
     "trial_converted": 0, "n_tiers": 3, "category": "streaming"},
    # worth it: YouTube Premium, daily
    {"name": "YouTube Premium", "tier": "Individual", "monthly_cost": 149, "annual_cost": 1788,
     "uses_per_month": 25, "months_active": 20, "price_creep_pct": 0, "is_annual_prepaid": 0,
     "trial_converted": 0, "n_tiers": 1, "category": "streaming"},
]


def main():
    for d in DEMO:
        d["stopped_using"] = 1 if d["uses_per_month"] == 0 else 0

    ranked, engine = rank(DEMO)
    print(f"Writing real Gemma verdicts for {len(ranked)} demo subscriptions...")
    for g in ranked:
        v = write_verdict(g)
        g["verdict"] = v
        tag = "GHOST" if g["ghost_type"] != "worth-it" else "keep "
        print(f"  [{tag}] {g['predicted_waste']:>6}/yr {g['ghost_label']:<10} {g['name']} "
              f"[{v['writer']}, removed {v['removed']}]")

    total = sum(g["predicted_waste"] for g in ranked)
    ghost_total = sum(g["predicted_waste"] for g in ranked if g["ghost_type"] != "worth-it")
    scorecard = evaluate(load_rows())

    payload = {
        "version": __version__,
        "engine": engine,
        "currency": "INR",
        "total_spend_year": sum(g["annual_cost"] for g in ranked),
        "total_waste_year": ghost_total,
        "scorecard": scorecard,
        "ghosts": ranked,
        "catalog": {"categories": catalog.CATEGORIES, "services": catalog.CATALOG},
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    text = json.dumps(payload)
    assert "\u2014" not in text and "\u2013" not in text, "dash in baked data"
    print(f"\nTotal ghost cost found: {ghost_total} rupees/yr across {len(ranked)} subs.")
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes). Engine: {engine}.")


if __name__ == "__main__":
    main()
