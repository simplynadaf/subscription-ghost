---
title: "I let an open model hunt the ghost costs in my subscriptions. It found Rs 29,056 a year."
published: false
tags: devchallenge, hf26challenge
cover_image: https://raw.githubusercontent.com/simplynadaf/subscription-ghost/main/docs/cover.png
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

In college I could never figure out why some things were so cheap. A printer for almost nothing. A console sold at a loss. A coffee machine priced like a gift. It took me years to understand the trick: the cheap thing was never the product. The ink, the games, the pods, the membership, that was the product. The company was not selling you a machine. It was signing you up for a bill that arrives forever, and the machine was just the hook.

Once I saw it, I could not unsee it. The modern version is the subscription. The app is free to download, the first month is free, the hardware is subsidised, because the real business is the small charge that repeats every month after you have forgotten you agreed to it. The whole model is built so you stop noticing. That is not a bug in the pricing. That is the pricing.

And it got me too. When I upgraded to Airtel Black, it bundled Amazon Prime free for a year. I was happy. A year later the free window closed and I was quietly billed Rs 1,499 for a full Prime membership.

Except I have never watched a single video on Prime Video. I use Prime for one reason, shipping. And Amazon sells a Prime Shopping Edition for Rs 399 a year that gives me exactly that and drops the video I never touch. So I was about to pay Rs 1,499 for a plan where I use one third of it, when Rs 399 covers my real life. That is Rs 1,100 a year leaking out of my account for a feature I do not use. The free year was the cheap printer. The Rs 1,499 renewal was the ink.

That is not a forgotten subscription. It is sneakier: a plan too big for how I actually live. And once I saw it, I started seeing the pattern everywhere. The gym membership I paid a year up front for and stopped going to by February, like 80% of people do. The storage tier I pay for and barely fill. The music I pay for twice without noticing.

The theme is Ghost in the Machine, and I read it literally: the ghosts are the charges that haunt your statement every month, small enough that your brain never flags them, quietly taking money while you are not looking. The business model depends on you not looking. So I built something whose only job is to look.

**Subscription Ghost** is an open-weight model that reads a small list of your subscriptions and predicts which ones are ghosts, then tells you the single thing to do about each, with the exact rupees you get back. It runs entirely on your own machine, for free, and it never asks for your bank login.

It names four kinds of ghost:

- **Over-tier** you use one slice of a bundle, and a cheaper tier covers your real use (my Prime, Rs 1,100 a year)
- **Abandoned** you paid a year up front and stopped showing up (the New Year gym)
- **Dead** you are paying and barely opening it
- **Price crept** the price quietly rose and you never noticed

On a sample person's nine subscriptions it found **Rs 29,056 a year** quietly leaking, and for every one of them it named the exact cheaper plan.

The biggest single ghost on that list was not the one you would guess. It was **iCloud+ at Rs 8,988 a year** on the 2 TB tier, for someone whose photos fit in 40 GB. The 50 GB tier at Rs 900 a year covers them with room to spare. That is Rs 8,088 going out the door every year for storage nobody fills. The gym was second at Rs 8,333. My Prime, the one that started all this, was way down the list at Rs 1,100. The small charges hide the big ones, which is exactly why a ranked prediction beats scrolling your own statement.

Then there is the ghost you cannot see by looking at any single line: **paying for the same thing twice.** This person pays for Amazon Prime, YouTube Premium, and Spotify. All three play music. Each one on its own looks fine, so no per-line check ever flags it. Subscription Ghost looks across the whole list, sees three music subscriptions where one would do, and says keep the one bundled into something you already pay for and drop the other two. That overlap alone is **Rs 5,376 a year.** I made that call deliberately conservative: it only flags an overlap when a capability is genuinely duplicated, so it will not tell you to cancel the music you actually sit and listen to.

That last point matters. A dumb version of this would scream "cancel everything." This one leaves three subscriptions marked **worth it** and says so, because the goal is to find the waste, not to nag you out of the things you use. A tool you cannot trust to leave the good stuff alone is a tool you close.

---

## Demo

Try it now, no setup, nothing uploaded: **https://simplynadaf.github.io/subscription-ghost/**

Open it on your phone too. It opens on a real sample person's subscriptions so you see the value with zero effort, then you can tap services from a catalog to add your own (the price fills in automatically). Tap any ghost to see the verdict and the fix, then hit "Stop this leak" and watch the total drop.

Try this in ten seconds: tap the gym row. It tells you that paying a year up front and stopping in February is Rs 8,333 gone, and that a monthly plan would have let you stop paying the month you stopped going. Then tap "Stop this leak" on it and watch Rs 8,333 jump out of the leaking total into the reclaimed counter. That is the whole loop: see the leak, understand it in one line, close it.

![Subscription Ghost ranking subscriptions worst first, each with a ghost badge, the rupees it wastes, and the exact cheaper plan](https://raw.githubusercontent.com/simplynadaf/subscription-ghost/main/docs/ui-hero.png)

---

## Code

{% embed https://github.com/simplynadaf/subscription-ghost %}

```bash
# runs on a plain CPU, no GPU, no key
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull gemma3:1b          # optional; falls back cleanly without it
python scripts/build_dataset.py
python scripts/validate.py     # asserts the whole pipeline end to end
python run.py                  # http://127.0.0.1:8080
```

---

## How I Built It

Two open models, one job each, both on CPU.

![How it works: your subscriptions go into TabPFN which predicts the waste and ranks them, then Gemma writes the verdict and the exact cheaper plan, with a deterministic fallback](https://raw.githubusercontent.com/simplynadaf/subscription-ghost/main/docs/architecture.png)

**TabPFN-v2 decides.** Prior Labs' open-weight tabular foundation model reads a small table of subscriptions (what you pay, how often you use it, how long you have had it, whether the price crept, whether you prepaid a year) and predicts the rupees each one wastes per year, in a single forward pass, no training loop of my own. It then ranks them worst first. This is exactly what TabPFN is built for: small tables, instant predictions. I use the open v2 weights so the whole stack is genuinely open, and it runs on CPU in a couple of seconds.

I went with a ranked prediction on purpose, not a rulebook of "if you use it fewer than N times, cancel." Thresholds break the moment real life does not match them: someone who opens an app twice a month might be getting full value, and someone who opens it daily out of habit might be wasting money on a tier they outgrew. The model learns the shape of waste from the whole table instead of from one brittle cutoff, and the number that matters for a triage tool is the order, which is why I score the ranking, not just the raw rupees.

**Gemma 3 writes.** A local Gemma 3 model, served through Ollama, turns the decision into two plain lines: the verdict and the one action. It is handed the real numbers and is forbidden from inventing any price or figure that is not supplied. Every rupee it writes is checked against the numbers I gave it, and a line that smuggles in a figure I never provided is stripped.

**The catalog keeps it honest.** Prices and cheaper tiers come from a real 2026 price catalog (Amazon Prime, Netflix, JioHotstar, Spotify, gym memberships, and more), not from the model. That is how it can say "move to Prime Shopping Edition at Rs 399" and have that be a real plan, not a hallucination.

**A deterministic fallback** covers both halves, so if the model weights or Ollama are not available the app still works and the response says which path ran. It never hard-fails.

The front end is a single file, Tailwind and GSAP, with a premium dark finance look that works on phone, tablet, and desktop.

And because it is a prediction, I score it honestly. I fit TabPFN on 75% of the subscriptions and test it on the 25% it has never seen:

```
scorecard (held-out, synthetic subscriptions)
  engine:              tabpfn
  mae_rupees:          523     # waste prediction lands within ~500 rupees
  rank_correlation:    0.971   # the worst-first ORDER is strong
  precision_at_k:      0.85    # of the 20 it flags most wasteful, 17 are truly top tier
  rupees_captured_pct: 96      # its top flags capture 96% of the real rupee waste
  missed:              3       # and it still MISSES 3 real ghosts
```

That `missed: 3` is the number that matters. Subscription Ghost is a triage aid that gets the ordering mostly right and sometimes wrong, not an oracle. The training data is synthetic and labeled as such, because no public dataset of "which of your subscriptions you secretly do not use" exists. The prices it reasons over, though, are real.

---

## Why Does Open Innovation Matter?

**Because a tool that finds money leaks should not be one.** The popular subscription apps ask to link your bank account and then watch every transaction you make, forever, and many charge a monthly fee to do it. There is a real irony in paying a subscription to cancel your subscriptions, and in handing your entire financial history to a third party to find out which charges you forgot.

Subscription Ghost runs TabPFN and Gemma on your own machine, on open weights, for Rs 0. It reads only what you tell it and uploads nothing. No bank login, no account, no bill. A closed API could not make that promise, because the whole business model of the closed tools is the data and the subscription.

Open also means two things a closed box cannot give you. The held-out scorecard above is right there, misses included, so you can see exactly how much to trust it. And because I could read the model's output next to the real numbers, I could build the rule that strips any figure it invents, and write tests for it. You cannot audit a closed model like that.

---

## The Spirit of It

The one that got me was my own Prime bill. I genuinely did not know I was about to pay Rs 1,499 for video I have never watched, when Rs 399 covers what I use. Building this made me go check, and I will be switching to the shopping tier.

That is the whole point, and it closes the loop on the cheap printer from college. The entire subscription economy is built around you not noticing. The free trial, the auto-renew, the tier you outgrew, the thing you pay for twice, all of it leans on the same bet: that a small charge repeated forever is a charge you stop seeing. Subscription Ghost is the opposite bet. It is a small open model whose only job is to notice, running on your own laptop, owned by nobody, charging you nothing. The ghost in the machine was the quiet charge. This is the machine that catches it.

---

## Prize Categories

- **Best Use of TabPFN** the prediction is the product: TabPFN ranks every subscription by predicted annual waste and is scored on held-out data
- **Best Use of Gemma** a local Gemma 3 writes the verdict and the exact action, with a no-invented-numbers rule enforced in code

---

*Lineage, disclosed: this reuses an engine pattern I have shipped before in this challenge series (an open-weight predictor paired with a local Gemma writer and a deterministic fallback). New project, new repo, new idea, built fresh in the Week 4 window.*
