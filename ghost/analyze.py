"""analyze.py: the smart per-subscription verdict.

This is the upgrade over the old additive rule. For one subscription it:
  1. works out what the user actually NEEDS from it (from usage + optional flags)
  2. finds the BEST-FIT cheaper plan in the catalog that still covers those needs
  3. picks the ONE dominant ghost reason (no double-counting), and
  4. returns the exact numbers: you pay X, the right plan is Y at Z, you save (X - Z)

It is deterministic and transparent (every rupee is arithmetic over real catalog
prices). TabPFN still ranks the ghosts, but it now learns a cleaner, non-overlapping
signal, and the UI can show the specific better offer, not just a waste number.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ghost import catalog


def needs_from_usage(sub):
    """Infer what the user really needs. Optional flags refine it; usage is the base.

    Flags (all optional, default off so the input stays lazy):
      shopping_only  -> they use Prime etc only for delivery, not video
      student        -> eligible for a student tier
      screens        -> how many screens they truly need (1 by default)
      video          -> do they actually watch the video part
    """
    needs = set()
    cat = sub.get("category", "other")
    screens = int(sub.get("screens", 1))
    if sub.get("shopping_only"):
        needs.add("shopping")
    if sub.get("student"):
        needs.add("student")
    # map category + screens to the catalog `covers` vocabulary where it helps
    return {"tags": needs, "screens": screens, "category": cat}


def _num(sub, key, default=0):
    try:
        return float(sub.get(key, default))
    except (TypeError, ValueError):
        return float(default)


def best_fit_plan(sub):
    """Find the cheapest real tier that still covers the user's real need.

    Returns (plan_tier_dict, annual_cost) or None if no cheaper fit exists.
    """
    sid = sub.get("service_id") or catalog.service_id_for_name(sub.get("name", ""))
    service = catalog.by_id(sid) if sid else None
    if not service or len(service["tiers"]) < 2:
        return None

    need = needs_from_usage(sub)
    current_annual = _num(sub, "annual_cost") or round(_num(sub, "monthly_cost") * 12)
    tiers = service["tiers"]

    if need["tags"]:
        fit = catalog.cheapest_tier_covering(service, need["tags"])
        if fit and catalog.annual_of(fit) < current_annual:
            return fit, catalog.annual_of(fit)

    uses = _num(sub, "uses_per_month")
    if uses <= 3:
        cheapest = min(tiers, key=lambda t: t["monthly_cost"])
        if catalog.annual_of(cheapest) < current_annual:
            return cheapest, catalog.annual_of(cheapest)

    name_now = (sub.get("tier") or "").lower()
    if "month" in name_now:
        annual_same = [t for t in tiers if "annual" in t["tier"].lower()
                       and set(t.get("covers", [])) == set(_current_covers(service, sub))]
        if annual_same:
            cheap = min(annual_same, key=lambda t: catalog.annual_of(t))
            if catalog.annual_of(cheap) < current_annual:
                return cheap, catalog.annual_of(cheap)
    return None


def _current_covers(service, sub):
    for t in service["tiers"]:
        if t["tier"] == sub.get("tier"):
            return t.get("covers", [])
    return []


def dominant_ghost(sub):
    """Pick the ONE biggest reason this is a ghost, with the exact saving.

    Returns a dict:
      type, label, wasted (rupees/yr), current_annual, better_plan, better_annual, save
    No double counting: whichever reason saves the most money wins.
    """
    current_annual = _num(sub, "annual_cost") or round(_num(sub, "monthly_cost") * 12)
    uses = _num(sub, "uses_per_month")
    creep = _num(sub, "price_creep_pct")
    annual_prepaid = int(_num(sub, "is_annual_prepaid"))
    months = _num(sub, "months_active", 12)

    candidates = []  # (type, label, wasted, better_plan_name, better_annual)

    # abandoned: paid a year up front, barely went, stopped early
    if annual_prepaid and uses <= 1 and months < 10:
        remaining = max(0.0, (12 - months) / 12.0)
        candidates.append(("abandoned", "Abandoned",
                           round(current_annual * remaining),
                           "a monthly plan (stop paying when you stop going)", None))

    # over-tier / best-fit: a cheaper real plan covers your use
    fit = best_fit_plan(sub)
    if fit:
        plan, plan_annual = fit
        save = current_annual - plan_annual
        if save > 0:
            candidates.append(("over-tier", "Over-tier", round(save),
                               plan["tier"], plan_annual))

    # dead: paying, hardly using, and no cheaper plan helps (cancel).
    # not for annual-prepaid charges: those are "abandoned", a more accurate story.
    if uses <= 1 and not fit and not annual_prepaid:
        use_ratio = min(1.0, uses / 8.0)
        candidates.append(("dead", "Dead",
                           round(current_annual * (1.0 - use_ratio)),
                           "cancel it", 0))

    # price crept: rose and you did not notice
    if creep >= 20:
        candidates.append(("crept", "Price crept",
                           round(current_annual * (creep / 100.0) * 0.6),
                           "re-check if it is worth the new price", None))

    if not candidates:
        return {"type": "worth-it", "label": "Worth it", "wasted": 0,
                "current_annual": current_annual, "better_plan": None,
                "better_annual": None, "save": 0}

    # dominant = the one that saves the most
    best = max(candidates, key=lambda c: c[2])
    gtype, label, wasted, plan_name, plan_annual = best
    return {
        "type": gtype, "label": label, "wasted": wasted,
        "current_annual": current_annual,
        "better_plan": plan_name,
        "better_annual": plan_annual,
        "save": wasted,
    }


if __name__ == "__main__":
    # the Airtel Prime story, shopping only
    prime = {"name": "Amazon Prime", "service_id": "amazon_prime",
             "tier": "Full Prime (annual)", "annual_cost": 1499, "monthly_cost": 124.9,
             "uses_per_month": 2, "shopping_only": True, "is_annual_prepaid": 1,
             "months_active": 14}
    print("Prime (shopping only):", dominant_ghost(prime))
    gym = {"name": "Gym / Fitness", "service_id": "gym", "tier": "Annual (New Year pack)",
           "annual_cost": 10000, "monthly_cost": 833, "uses_per_month": 1,
           "is_annual_prepaid": 1, "months_active": 2}
    print("Gym (abandoned):", dominant_ghost(gym))
    nf = {"name": "Netflix", "service_id": "netflix", "tier": "Premium",
          "annual_cost": 7788, "monthly_cost": 649, "uses_per_month": 1,
          "is_annual_prepaid": 0, "months_active": 11}
    print("Netflix (heavy under-use):", dominant_ghost(nf))
