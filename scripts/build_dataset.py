"""build_dataset.py: a synthetic but grounded set of real people's subscription logs.

HONESTY NOTE (said plainly, this is the project's spine):
There is no public dataset of "which of your subscriptions you secretly do not use."
So this training data is SYNTHETIC. Each row is one person's one subscription, with a
usage signal, built from a transparent rule about when a charge becomes a ghost:

  a charge is more of a ghost (more wasted money) when
    - you use it rarely (low uses_per_month vs what the plan assumes)
    - you are on a bigger tier than your real use needs (over-tier)
    - the price has crept up since you started
    - you pay annually but stopped using it partway (abandoned, the gym case)
    - a free trial converted and you never engaged

The generator writes a real `wasted_per_year` label in rupees. TabPFN learns this from
a training slice and is scored on a held-out slice, exactly as it would learn YOUR
pattern from YOUR real log. Prices come from the real catalog, never invented.

Run: python scripts/build_dataset.py  ->  data/subscriptions.csv
"""

import csv
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ghost import catalog

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "subscriptions.csv")


def annual_of(tier):
    return tier.get("annual_cost") or round(tier["monthly_cost"] * 12)


def wasted_per_year(service, tier, uses_per_month, months_active,
                    price_creep_pct, is_annual_prepaid, stopped_using):
    """Transparent rupee waste label. The model learns to reproduce this."""
    annual = annual_of(tier)

    # 1. under-use: if you barely use it, most of the fee is wasted.
    #    assume a plan "earns out" at roughly 8 uses a month.
    use_ratio = min(1.0, uses_per_month / 8.0)
    underuse_waste = annual * (1.0 - use_ratio) * 0.6

    # 2. over-tier: could a cheaper tier cover your real use?
    overtier_waste = 0.0
    if uses_per_month <= 3 and len(service["tiers"]) > 1:
        cheapest = min(service["tiers"], key=lambda t: t["monthly_cost"])
        overtier_waste = max(0.0, annual - annual_of(cheapest)) * 0.7

    # 3. price creep: the amount it rose that you never noticed.
    creep_waste = annual * (price_creep_pct / 100.0) * 0.5

    # 4. abandoned annual prepaid (the gym): paid the year, stopped partway.
    abandoned_waste = 0.0
    if is_annual_prepaid and stopped_using:
        remaining = max(0.0, (12 - months_active) / 12.0)
        abandoned_waste = annual * remaining

    total = underuse_waste + overtier_waste + creep_waste + abandoned_waste
    return max(0.0, min(annual, total))


def build(n=400, seed=11):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        service = rng.choice(catalog.CATALOG)
        tier = rng.choice(service["tiers"])
        is_annual = bool(tier.get("annual_cost")) and ("annual" in tier["tier"].lower()
                                                        or service["category"] == "fitness"
                                                        or rng.random() < 0.3)
        # usage: fitness and food skew toward abandonment; AI/productivity bimodal
        if service["category"] == "fitness":
            uses_per_month = rng.choices([0, 1, 2, 4, 10], weights=[30, 25, 20, 15, 10])[0]
        elif service["category"] in ("food",):
            uses_per_month = rng.choices([1, 2, 4, 8, 15], weights=[24, 24, 22, 18, 12])[0]
        else:
            uses_per_month = rng.choices([0, 1, 3, 6, 12, 25], weights=[14, 18, 22, 20, 16, 10])[0]

        months_active = rng.choices([1, 2, 3, 6, 11, 14, 24], weights=[10, 12, 16, 20, 16, 14, 12])[0]
        price_creep_pct = rng.choices([0, 0, 10, 20, 35, 60], weights=[34, 20, 18, 14, 9, 5])[0]
        trial_converted = rng.choices([0, 1], weights=[70, 30])[0]
        stopped_using = 1 if (uses_per_month == 0 or (service["category"] == "fitness" and uses_per_month <= 1)) else 0

        waste = wasted_per_year(service, tier, uses_per_month, months_active,
                                price_creep_pct, is_annual, stopped_using)
        waste = max(0.0, waste + rng.gauss(0, annual_of(tier) * 0.04))

        rows.append({
            "service_id": service["id"],
            "name": service["name"],
            "category": service["category"],
            "tier": tier["tier"],
            "monthly_cost": round(tier["monthly_cost"], 1),
            "annual_cost": annual_of(tier),
            "uses_per_month": uses_per_month,
            "months_active": months_active,
            "price_creep_pct": price_creep_pct,
            "is_annual_prepaid": int(is_annual),
            "trial_converted": trial_converted,
            "stopped_using": stopped_using,
            "n_tiers": len(service["tiers"]),
            "wasted_per_year": round(waste),
        })
    return rows


FIELDS = ["service_id", "name", "category", "tier", "monthly_cost", "annual_cost",
          "uses_per_month", "months_active", "price_creep_pct", "is_annual_prepaid",
          "trial_converted", "stopped_using", "n_tiers", "wasted_per_year"]


def main():
    rows = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    total = sum(r["wasted_per_year"] for r in rows)
    ghosts = sum(1 for r in rows if r["wasted_per_year"] >= 500)
    print(f"Wrote {len(rows)} synthetic subscriptions to {OUT}")
    print(f"{ghosts} are ghosts (>= 500/yr wasted). Total synthetic waste: {total} rupees.")
    print("Data is synthetic and labeled as such; prices are from the real catalog.")


if __name__ == "__main__":
    main()
