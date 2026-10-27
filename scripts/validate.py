"""validate.py: assert-based end-to-end check. No server needed.

Run: python scripts/validate.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ghost import catalog
from ghost.predict import evaluate, ghost_type, load_rows, rank
from ghost.remember import write_verdict


def main():
    # catalog sanity: the Airtel Prime over-tier story must hold with real numbers
    prime = catalog.by_id("amazon_prime")
    full = catalog.default_tier(prime)
    shop = catalog.cheapest_tier_covering(prime, ["shopping"])
    saving = full["annual_cost"] - shop["annual_cost"]
    assert saving == 1100, f"expected Prime over-tier ghost of 1100, got {saving}"
    print(f"catalog ok: Prime over-tier ghost = {saving}/yr (1499 vs 399)")

    rows = load_rows()
    assert len(rows) >= 300, f"expected >=300 rows, got {len(rows)}"

    card = evaluate(rows)
    assert card["engine"] in ("tabpfn", "deterministic-fallback")
    assert 0.0 <= card["mae_rupees"]
    assert -1.0 <= card["rank_correlation"] <= 1.0
    assert 0.0 <= card["precision_at_k"] <= 1.0
    print("scorecard:", card)

    ranked, engine = rank(rows)
    assert len(ranked) == len(rows)
    waste = [r["predicted_waste"] for r in ranked]
    assert waste == sorted(waste, reverse=True), "not sorted by waste"
    assert all(r["ghost_type"] in ("abandoned", "over-tier", "dead", "crept", "worth-it")
               for r in ranked), "bad ghost type"
    types = {r["ghost_type"] for r in ranked}
    print(f"ranking ok, engine={engine}, ghost types present: {sorted(types)}")

    # verdict writer shape + honesty + no dashes
    out = write_verdict(ranked[0])
    assert out["verdict"] and out["action"], "empty verdict"
    assert out["writer"] in ("gemma", "gemma+fallback", "deterministic-fallback")
    assert isinstance(out["removed"], int) and out["removed"] >= 0
    for field in (out["verdict"], out["action"]):
        assert "\u2014" not in field and "\u2013" not in field, "dash in output"
    print(f"verdict ok, writer={out['writer']}, removed={out['removed']}")

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
