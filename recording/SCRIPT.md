# Subscription Ghost: Video Recording Script + Plan

Target: a tight, punchy 75 to 95 second demo for YouTube + the Dev.to post.
Voice: Amazon Polly neural, Matthew (calm, authoritative) or Joanna. AI voice disclosed.
Style (from the recording playbook): open on the result, cut fast, chrome/kinetic feel,
real program output, no dead air. Ducked ambient bed under the voice.

Flow: HOOK -> the real Airtel use case -> GitHub repo preview -> live website demo
(add a real subscription) -> the honest scorecard -> CLOSING (socials + like/comment/share).

===============================================================================
TIMED SEGMENTS (segId | start seconds | on-screen | voiceover line)
===============================================================================

seg1_hook | 0.0 | HERO of the live site, the big red leaking number counting up
VO: "There is money leaving your account every month, and you probably have not noticed."

seg2_pain | 6.0 | zoom on the Amazon Prime ghost row (Over-tier, Rs 1,100)
VO: "I upgraded to Airtel Black, got Amazon Prime free for a year, and then got billed
fifteen hundred rupees for video I have never watched. I only use it for shipping."

seg3_fix | 16.0 | the verdict card for Prime: pay 1499 -> best Rs 399 -> save 1100
VO: "Subscription Ghost caught it. The four hundred rupee shopping plan covers what I
actually use. That is eleven hundred rupees a year, back in my pocket."

seg4_what | 25.5 | the ranked ghost list scrolling, badges visible
VO: "It is an open model that reads your subscriptions and predicts which ones are
ghosts: the plan too big for you, the price that crept up, the gym you quit in February."

seg5_repo | 35.0 | GitHub repo page, the cover banner + README scrolling
VO: "The whole thing is open source. TabPFN does the prediction, Gemma writes the
verdict, and every rupee is computed from a real price list, never invented."

seg6_demo | 45.0 | live site: open Add, tap a service tile, pick usage, confirm
VO: "Add your own in two taps. Pick a service, say how often you really use it, and it
ranks it instantly. No bank login. Nothing is uploaded. It runs on your laptop for free."

seg7_kill | 57.0 | tap Stop this leak, the big total drops, reclaimed ticks up
VO: "Hit stop the leak, and watch the money come back. On this sample, twenty nine
thousand rupees a year was quietly bleeding out."

seg8_honest | 66.0 | the scorecard: rank 0.971, missed 3
VO: "And it is honest about being wrong. It tells you the three real ghosts it still
missed, because a money tool that hides its mistakes is not worth trusting."

seg9_close | 75.5 | closing card: logo + socials + like/comment/share + repo URL
VO: "Try it, the link is in the description. If this found a ghost in your subscriptions,
like, comment, and share, and follow for more open source AI builds."

END ~ 88s

===============================================================================
CLOSING CARD TEXT (on screen for seg9)
===============================================================================
Title:  Subscription Ghost
Line:   Find the money quietly leaving your account.
Live:   simplynadaf.github.io/subscription-ghost
Repo:   github.com/simplynadaf/subscription-ghost
CTA:    LIKE  .  COMMENT  .  SHARE
Socials: sarvarnadaf.com  .  @sarvar_04 (Dev.to)  .  @sarvar-nadaf (YouTube)
         linkedin.com/in/sarvar04  .  x.com/SarvarN_04

===============================================================================
INTRO CARD TEXT (optional 2s pre-roll)
===============================================================================
Ghost in the Machine . Hacktoberfest 2026
Subscription Ghost
built by Sarvar Nadaf

===============================================================================
TEST EXAMPLES TO RECORD (real use cases, verify each on-screen before final take)
===============================================================================
Primary (the hero): Amazon Prime, Full Prime annual Rs 1,499, used ~2x/mo, shopping only
   -> Over-tier -> Prime Shopping Edition Rs 399 -> save Rs 1,100. THIS IS THE STORY.
Secondary demos to show in the list (already in the baked demo):
   - Gym / Fitness, New Year annual Rs 10,000, ~1x/mo -> Abandoned -> monthly plan -> ~Rs 8,333
   - Netflix Premium Rs 7,788, ~1x/mo -> Over-tier -> Mobile Rs 1,788 -> save Rs 6,000
   - ChatGPT Plus Rs 22,800, price crept -> Price crept
   - Spotify / YouTube / JioHotstar -> Worth it (shows it does not over-flag)
Add-live demo (record this interaction): tap "Netflix" tile -> pick "rarely" -> Add and
   find its ghost -> it appears ranked with its cheaper-plan line.
Overlap demo: the "paying for music twice" card (Prime + YouTube + Spotify) -> save Rs 5,376.

===============================================================================
RECORDING STEPS
===============================================================================
1. Record the SILENT screen capture of the live site + the GitHub repo, following the
   segment on-screen cues above (use the recorders in ~/.kiro/skills; browser scenes via
   testreel for polish, or a plain Playwright screencast). Trim freeze/dead frames.
2. Synth each VO line with Polly neural (see build_voiceover.sh), place at its start time.
3. Add a quiet original ambient bed, mux onto the silent video, loudness-normalize to -16 LUFS.
4. Build intro + outro brand cards (GSAP), concat intro + demo + outro.
5. QA: narration lands in each window, no overrun, no dead air, dims/codec correct.
6. Upload to YouTube with the youtube-thumbnail.png, get VIDEO_ID, embed in the Dev.to post.

Disclosure: the footage is a real screen recording; only the voice is AI (Polly). Disclose
on YouTube's synthetic-content question.
