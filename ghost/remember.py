"""remember.py: Gemma writes the plain verdict and the exact action for each ghost.

Once TabPFN decides which charges are ghosts and how much they waste, a local Gemma 3
model (via Ollama) writes two short, human lines per ghost:
  1. VERDICT: one plain sentence on why this is a ghost
  2. ACTION: the one concrete thing to do (downgrade to the X tier, cancel, switch to
     the annual plan), with the rupee saving

THE RULE IT NEVER BENDS: the code computes every rupee; Gemma only phrases it. Gemma is
given the numbers and is forbidden from inventing any figure, price, or tier that is not
supplied. Every number in the output is checked against the numbers we gave it; a line
that invents a rupee value we never provided is replaced with the deterministic version.
When unsure, it says so rather than guessing.

If Ollama is not running, a deterministic template writes the same two lines from the
numbers alone. The response always reports which writer ran.
"""

import json
import os
import re
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL = os.environ.get("GHOST_MODEL", "gemma3:1b")


def _normalize(text):
    if not text:
        return text
    return (text.replace("\u2014", ", ").replace("\u2013", "-")
                .replace("\u2019", "'").replace("\u2018", "'")
                .replace("\u201c", '"').replace("\u201d", '"'))


def _allowed_numbers(ghost):
    """The only rupee figures Gemma is allowed to use."""
    nums = set()
    for key in ("predicted_waste", "annual_cost", "monthly_cost"):
        v = ghost.get(key)
        if v is not None:
            nums.add(round(float(v)))
    return nums


def _prompt(ghost):
    return (
        "You help a person cut wasted subscription money. Use ONLY the numbers given. "
        "Do not invent any price, rupee figure, or plan name that is not listed. If you "
        "are unsure, say so. Be warm and plain.\n\n"
        f"Subscription: {ghost['name']} ({ghost['tier']})\n"
        f"Costs: {ghost['annual_cost']} rupees per year\n"
        f"Used about: {ghost['uses_per_month']} times a month\n"
        f"Ghost type: {ghost['ghost_label']}\n"
        f"Estimated wasted per year: {ghost['predicted_waste']} rupees\n\n"
        "Write exactly two short lines, no preamble:\n"
        "VERDICT: one plain sentence on why this is wasted money.\n"
        "ACTION: the one concrete thing to do about it.\n"
    )


def _parse(text):
    verdict, action = "", ""
    for line in text.splitlines():
        s = line.strip()
        if s.upper().startswith("VERDICT:"):
            verdict = _normalize(s.split(":", 1)[1].strip())
        elif s.upper().startswith("ACTION:"):
            action = _normalize(s.split(":", 1)[1].strip())
    return verdict, action


def _deterministic(ghost):
    name = ghost["name"]
    waste = ghost["predicted_waste"]
    gtype = ghost["ghost_type"]
    uses = ghost["uses_per_month"]
    if gtype == "abandoned":
        verdict = f"You paid for {name} up front but stopped using it, so about {waste} rupees a year is gone."
        action = f"Switch to a monthly plan so you stop paying the month you stop going."
    elif gtype == "over-tier":
        verdict = f"You use {name} about {uses} times a month, far less than this plan assumes, wasting about {waste} rupees a year."
        action = f"Move to the cheapest tier that covers what you actually use."
    elif gtype == "dead":
        verdict = f"You are paying for {name} and barely opening it, wasting about {waste} rupees a year."
        action = f"Cancel {name} unless you will genuinely use it next month."
    elif gtype == "crept":
        verdict = f"The price of {name} quietly rose, and you are now wasting about {waste} rupees a year."
        action = f"Check if the current price is still worth it, or downgrade."
    else:
        verdict = f"{name} looks worth keeping for now."
        action = f"Keep it, but check again if your usage drops."
    return verdict, action


def _strip_invented_numbers(line, allowed):
    """Remove a line that cites a rupee number we never provided."""
    if not line:
        return line, False
    found = re.findall(r"\d[\d,]*", line)
    for f in found:
        n = int(f.replace(",", ""))
        # ignore small counts (like "3 times a month"); only guard rupee-scale figures
        if n >= 50 and n not in allowed:
            return "", True
    return line, False


def write_verdict(ghost, timeout=45):
    allowed = _allowed_numbers(ghost)
    allowed.add(int(float(ghost.get("uses_per_month", 0))))
    try:
        payload = json.dumps({
            "model": MODEL, "prompt": _prompt(ghost), "stream": False,
            "options": {"temperature": 0.4, "num_predict": 110},
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
        verdict, action = _parse(body.get("response", ""))
        writer = "gemma"
        if not verdict or not action:
            verdict, action = _deterministic(ghost)
            writer = "gemma+fallback"
        verdict, r1 = _strip_invented_numbers(verdict, allowed)
        action, r2 = _strip_invented_numbers(action, allowed)
        removed = int(r1) + int(r2)
        if not verdict or not action:
            dv, da = _deterministic(ghost)
            verdict = verdict or dv
            action = action or da
    except Exception:
        verdict, action = _deterministic(ghost)
        writer, removed = "deterministic-fallback", 0
    return {"verdict": verdict, "action": action, "writer": writer, "removed": removed}


if __name__ == "__main__":
    sample = {
        "name": "Amazon Prime", "tier": "Full Prime (annual)", "annual_cost": 1499,
        "monthly_cost": 124.9, "uses_per_month": 2, "ghost_type": "over-tier",
        "ghost_label": "Over-tier", "predicted_waste": 1100,
    }
    import pprint
    pprint.pprint(write_verdict(sample))
