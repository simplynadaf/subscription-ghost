# YouTube Metadata: Subscription Ghost

## Title research note
Analyzed the actual Week 2 winner titles (same judges, same hf26challenge). DEV judges
reward STORY-FIRST, personal, honest, specific titles, not SEO/keyword titles. Winning
pattern: a real person + a specific moment + a concrete number + an honest/anti-hype hook
+ often "on a laptop". Examples that won: "pricecheck: my friend didn't know what to
offer for a used monitor, so now he gets three numbers" (TabPFN), "I stopped asking AI to
count. Now it catches 95.6% of the mistakes in crochet patterns, on a laptop" (Tinker).
So the Dev.to title is now story-first; the YouTube titles below stay keyword-first
because YouTube search rewards the opposite.

## Dev.to title (story-first, matches the winning pattern)
"I was about to pay Rs 1,499 for Prime Video I never watch. An open model on my laptop caught it."

## YouTube Title (A/B options, keyword front-loaded for YouTube search)
A) An open AI found Rs 29,056 leaking from my subscriptions (runs on your laptop, free)
B) I built an open-source AI that finds the money leaking from your subscriptions

## Description

An open-weight AI that predicts which of your subscriptions are quietly wasting money,
then tells you the one thing to do about each, with the exact rupees you get back. It
runs 100% on your own laptop, for free, and never asks for your bank login.

It caught my own Amazon Prime bill: Rs 1,499 a year for Prime Video I have never watched,
when the Rs 399 Shopping Edition covers what I actually use. That is Rs 1,100 a year back.
On a sample of 9 subscriptions it found Rs 29,056 a year leaking, named the exact cheaper
plan for each, and even caught paying for music twice across Prime, YouTube, and Spotify.

How it works:
- TabPFN-v2 (open-weight tabular model) predicts the rupees each subscription wastes and
  ranks them worst first, on CPU, in seconds.
- Gemma 3 (local, via Ollama) writes the plain-language verdict and the single action,
  with a no-invented-numbers rule enforced in code.
- Every price comes from a real 2026 catalog, not the model.
- A deterministic fallback keeps it working even without the model weights.

Built for the Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine.

Try it (no setup, nothing uploaded): https://simplynadaf.github.io/subscription-ghost/
Code (open source, MIT): https://github.com/simplynadaf/subscription-ghost

If this found a ghost in your subscriptions, like, comment, and share, and follow for more
open-source AI builds.

Chapters:
0:00 The money leaving your account
0:06 My Amazon Prime ghost
0:16 The fix (Rs 399 covers it)
0:25 What Subscription Ghost does
0:35 The open-source code
0:45 Add your own (no bank login)
0:57 Stop the leak
1:06 Honest about being wrong
1:15 Try it

Connect:
Portfolio: https://sarvarnadaf.com
Dev.to: https://dev.to/sarvar_04
LinkedIn: https://www.linkedin.com/in/sarvar04/
X: https://x.com/SarvarN_04
GitHub: https://github.com/simplynadaf
YouTube: https://www.youtube.com/@sarvar-nadaf

Disclosure: the footage is a real screen recording; the voiceover is AI (Amazon Polly).

## Tags
subscription tracker, cancel subscriptions, save money subscriptions, open source AI,
TabPFN, Gemma, local AI, run AI on laptop, Hacktoberfest 2026, ghost in the machine,
AI on CPU, Ollama, subscription audit, Amazon Prime shopping edition, fintech AI,
open weight models, no bank login, personal finance AI

## Thumbnail
youtube-thumbnail.png (1280x720): "Find the money leaking out" + Rs 29,056/yr +
"runs on your laptop, free"

## Category / settings
- Category: Science & Technology
- Visibility: Unlisted first (for the Dev.to embed), then Public
- Synthetic-content question: YES (AI voiceover disclosed)
- Playlist: open-source AI builds

## Status
- Thumbnail: ready (youtube-thumbnail.png)
- Voiceover soundtrack: ready (recording/voiceover/soundtrack.mp3)
- Script + cards: ready (recording/SCRIPT.md, card-intro/outro)
- Demo video: NOT yet recorded (silent screen capture pending), then mux soundtrack.
