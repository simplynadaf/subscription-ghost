"""catalog.py: a catalog of real subscription services and their real 2026 tiers.

Every price here was read from a cited public source in October 2026 (see
SUBSCRIPTION-GHOST-DESIGN-BRIEF.md). We do not invent prices. When a service has a
cheaper tier that still covers a common use, that is recorded so the app can spot an
"over-tier" ghost (paying for a bundle when a cheaper tier covers your real use).

All amounts are rupees per MONTH (monthly_cost). Annual-only plans store the annual
figure in `annual_cost` and the monthly view is annual / 12 for comparison.

This powers three things:
  1. the lazy logo-tile input (tap a service, price autofills)
  2. the over-tier ghost check (is there a cheaper tier for your real use?)
  3. the monthly-vs-annual trap check
"""

# category keys: streaming, music, shopping, food, fitness, cloud, productivity, other
CATALOG = [
    {
        "id": "amazon_prime", "name": "Amazon Prime", "category": "shopping",
        "emoji": "📦", "currency": "INR",
        "tiers": [
            {"tier": "Full Prime (annual)", "monthly_cost": 124.9, "annual_cost": 1499,
             "covers": ["shopping", "video", "music"]},
            {"tier": "Full Prime (monthly)", "monthly_cost": 299, "annual_cost": 3588,
             "covers": ["shopping", "video", "music"]},
            {"tier": "Prime Lite", "monthly_cost": 66.6, "annual_cost": 799,
             "covers": ["shopping", "video-1device"]},
            {"tier": "Prime Shopping Edition", "monthly_cost": 33.3, "annual_cost": 399,
             "covers": ["shopping"]},
        ],
        "note": "Shopping Edition at 399 a year drops video entirely. If you only use "
                "Prime for delivery, the full 1499 plan is mostly video you do not watch.",
    },
    {
        "id": "netflix", "name": "Netflix", "category": "streaming",
        "emoji": "🎬", "currency": "INR",
        "tiers": [
            {"tier": "Mobile", "monthly_cost": 149, "covers": ["video-1device-sd"]},
            {"tier": "Basic", "monthly_cost": 199, "covers": ["video-1device-hd"]},
            {"tier": "Standard", "monthly_cost": 499, "covers": ["video-2screen-fhd"]},
            {"tier": "Premium", "monthly_cost": 649, "covers": ["video-4screen-4k"]},
        ],
        "note": "If you watch on your phone, Mobile at 149 is the same catalogue as "
                "Premium at 649, just fewer screens and lower resolution.",
    },
    {
        "id": "jiohotstar", "name": "JioHotstar", "category": "streaming",
        "emoji": "📺", "currency": "INR",
        "tiers": [
            {"tier": "Mobile", "monthly_cost": 79, "covers": ["video-1device"]},
            {"tier": "Super", "monthly_cost": 149, "covers": ["video-2device-tv"]},
            {"tier": "Premium", "monthly_cost": 299, "annual_cost": 2199,
             "covers": ["video-4device-4k"]},
        ],
        "note": "Premium is for 4 screens in 4K. One viewer rarely needs it.",
    },
    {
        "id": "spotify", "name": "Spotify", "category": "music",
        "emoji": "🎧", "currency": "INR",
        "tiers": [
            {"tier": "Student", "monthly_cost": 69, "covers": ["music", "student"]},
            {"tier": "Standard", "monthly_cost": 139, "covers": ["music"]},
            {"tier": "Platinum", "monthly_cost": 299, "covers": ["music", "extras"]},
        ],
        "note": "If you are a student, the 69 plan is the same music as the 139 plan.",
    },
    {
        "id": "youtube_premium", "name": "YouTube Premium", "category": "streaming",
        "emoji": "▶️", "currency": "INR",
        "tiers": [
            {"tier": "Individual", "monthly_cost": 149, "covers": ["video", "music"]},
        ],
        "note": "Includes YouTube Music. If you also pay for Spotify, one of them is a ghost.",
    },
    {
        "id": "swiggy_one", "name": "Swiggy One", "category": "food",
        "emoji": "🍔", "currency": "INR",
        "tiers": [
            {"tier": "One (3 months)", "monthly_cost": 83, "annual_cost": 996,
             "covers": ["free-delivery"]},
        ],
        "note": "Only pays off if you order often. A few orders a month and it is a ghost.",
    },
    {
        "id": "zomato_gold", "name": "Zomato Gold", "category": "food",
        "emoji": "🍽️", "currency": "INR",
        "tiers": [
            {"tier": "Gold (annual)", "monthly_cost": 83, "annual_cost": 999,
             "covers": ["free-delivery", "discounts"]},
        ],
        "note": "Overlaps heavily with Swiggy One. Few people need both.",
    },
    {
        "id": "gym", "name": "Gym / Fitness", "category": "fitness",
        "emoji": "🏋️", "currency": "INR",
        "tiers": [
            {"tier": "Annual (New Year pack)", "monthly_cost": 833, "annual_cost": 10000,
             "covers": ["gym"]},
            {"tier": "Monthly", "monthly_cost": 1200, "covers": ["gym"]},
            {"tier": "Quarterly", "monthly_cost": 1000, "annual_cost": 12000,
             "covers": ["gym"]},
        ],
        "note": "80 percent of people who join in January stop going by March. If you "
                "paid a year upfront and stopped, the rest is a ghost. A monthly plan "
                "would have let you stop paying when you stopped going.",
    },
    {
        "id": "cultfit", "name": "cult.fit", "category": "fitness",
        "emoji": "🧘", "currency": "INR",
        "tiers": [
            {"tier": "Elite (annual)", "monthly_cost": 1000, "annual_cost": 12000,
             "covers": ["gym", "classes"]},
            {"tier": "Pro (monthly)", "monthly_cost": 1500, "covers": ["gym", "classes"]},
        ],
        "note": "Same abandonment risk as any gym. Match the plan to how often you really go.",
    },
    {
        "id": "icloud", "name": "iCloud+", "category": "cloud",
        "emoji": "☁️", "currency": "INR",
        "tiers": [
            {"tier": "50 GB", "monthly_cost": 75, "covers": ["storage-50"]},
            {"tier": "200 GB", "monthly_cost": 219, "covers": ["storage-200"]},
            {"tier": "2 TB", "monthly_cost": 749, "covers": ["storage-2tb"]},
        ],
        "note": "Many people pay for 2 TB and use under 50 GB.",
    },
    {
        "id": "google_one", "name": "Google One", "category": "cloud",
        "emoji": "🗄️", "currency": "INR",
        "tiers": [
            {"tier": "100 GB", "monthly_cost": 130, "covers": ["storage-100"]},
            {"tier": "2 TB", "monthly_cost": 650, "covers": ["storage-2tb"]},
        ],
        "note": "Check your actual storage used before paying for the 2 TB tier.",
    },
    {
        "id": "chatgpt_plus", "name": "ChatGPT Plus", "category": "productivity",
        "emoji": "🤖", "currency": "INR",
        "tiers": [
            {"tier": "Plus", "monthly_cost": 1900, "covers": ["ai"]},
        ],
        "note": "Useful if you use it weekly. If you opened it twice last month, it is a ghost.",
    },
    {
        "id": "linkedin_premium", "name": "LinkedIn Premium", "category": "productivity",
        "emoji": "💼", "currency": "INR",
        "tiers": [
            {"tier": "Career", "monthly_cost": 1400, "covers": ["jobs"]},
        ],
        "note": "People often subscribe during a job hunt and forget to cancel after.",
    },
]

CATEGORIES = {
    "streaming": {"label": "Streaming", "emoji": "🎬"},
    "music": {"label": "Music", "emoji": "🎧"},
    "shopping": {"label": "Shopping", "emoji": "📦"},
    "food": {"label": "Food delivery", "emoji": "🍔"},
    "fitness": {"label": "Fitness", "emoji": "🏋️"},
    "cloud": {"label": "Cloud storage", "emoji": "☁️"},
    "productivity": {"label": "Productivity", "emoji": "🤖"},
    "other": {"label": "Other", "emoji": "🔁"},
}


def by_id(service_id):
    for s in CATALOG:
        if s["id"] == service_id:
            return s
    return None


def default_tier(service):
    """The tier people usually land on (the first, most-complete one)."""
    return service["tiers"][0]


def cheapest_tier_covering(service, needed):
    """The cheapest tier whose `covers` includes everything in `needed`.

    Used for the over-tier ghost: if the user only really uses `shopping`, this
    finds that Prime Shopping Edition covers it for far less than full Prime.
    """
    needed = set(needed)
    candidates = [
        t for t in service["tiers"]
        if needed.issubset(set(t.get("covers", [])))
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda t: t["monthly_cost"])


if __name__ == "__main__":
    print(f"{len(CATALOG)} services across {len(CATEGORIES)} categories")
    prime = by_id("amazon_prime")
    shop_only = cheapest_tier_covering(prime, ["shopping"])
    full = default_tier(prime)
    saving = (full["annual_cost"] - shop_only["annual_cost"])
    print(f"Prime over-tier ghost: full {full['annual_cost']} vs shopping-only "
          f"{shop_only['annual_cost']} = {saving}/yr overpaid if you only shop")
