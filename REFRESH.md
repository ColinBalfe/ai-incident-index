# Refresh runbook

Used by the scheduled refresh task and by anyone updating the index by hand. A refresh adds what happened since the last one, re-checks the live incident, and republishes. It never rewrites history silently: every change goes in the changelog.

## 0. Setup

```
git clone https://github.com/ColinBalfe/ai-incident-index && cd ai-incident-index
```

Read `data/meta.json` (`as_of`, `live_incident`, `changelog`) so you know the last refresh time and what is being tracked live.

## 1. Research (web search, primary sources first)

1. **The live incident** (`meta.live_incident`, currently PHP2Shell): confirmed compromises (named organizations, with a source each), exploit-attempt figures, botnet activity, CISA KEV listing or emergency directive, services restored or newly taken offline, new official statements (agencies, governments, the PHP Foundation, Cloudflare, OpenAI, Wiz). Check the CISA KEV JSON for CVE-2026-109618 and CVE-2026-109619.
2. **New AI safety incidents** since `as_of`: real-world harms or near-misses materially caused or enabled by AI, and lab or evaluation disclosures of dangerous behavior. Look at: OpenAI's misalignment reports page, Anthropic's news and research pages, Google DeepMind, Meta, the UK AI Security Institute blog, METR, Transluce, the AI Incident Database, major security press (The Hacker News, BleepingComputer, SecurityWeek, Reuters, Bloomberg, WSJ, FT, Al Jazeera).
3. **Official statements** on AI incidents from security agencies (NSA, CISA, FBI, NCSC, ACSC, CCCS, CERT-EU, ENISA, KISA), governments and regulators (White House, Commerce, EU Commission, state AGs, Korean FSC/FSS, Japan NCO, Australia), and AI labs. Record X posts with the direct post URL when it can be found.
4. **Updates to tracked incidents**: new victims named, new figures, denials, corrections, retractions.

Keep descriptions of hacking techniques high-level. Never invent a figure; if a number cannot be sourced, leave it out.

## 2. Edit the research files

- New scored incidents: append to `research/jul_oct_2026_mine.json` (same schema as the existing rows: id, date, date_precision, disclosed, title, actors, category, setting, summary, harm, H, R, A, N, I, source_url, source2_url, confidence, notes). Rate the five factors by `research/rubric.md`. Prefer a primary source as `source_url`.
- New victims, timeline events, official statements, implications for an existing deep dive: `research/php2shell.json` (PHP2Shell) or `research/victims.json` (the other five). Follow the existing schemas exactly.
- Live panel and 14-day watchlist: `build/build_live.py` (`LIVE`, `LIVE_NOTE`, `WATCH`, `META`). Update `AS_OF`, `AS_OF_LABEL`, `next_check` and add a dated `CHANGELOG` entry that says what changed and how many rows were added or corrected.
- If the live incident has gone quiet (no new facts for 3 days), set `META.live_incident` to the most important active incident, or keep it and say so in `LIVE_NOTE`.
- Corrections to existing rows: use the `FIX` dict in `build/build_data.py` or `build/fixes2.py`, never by editing generated files in `data/`.

## 3. Build and check

```
cd build && python3 build_data.py && python3 build_deep.py && python3 build_live.py && cp data/*.json ../data/ && cd ..
python3 build_site.py
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &
node make_og.mjs http://127.0.0.1:8765/index.html
node shot.mjs    http://127.0.0.1:8765/index.html
```

`shot.mjs` must print `errors none` three times. Look at `shots/site-desktop-top.png` and `shots/site-phone-top.png` before publishing. If anything fails, fix it; do not publish a broken page.

## 4. Fact-check what you added

Re-verify every new row against its source: names, dates, numbers, who said what. Mark uncertain attributions as uncertain in the text ("consistent with", "reported", "denies"). Fix before publishing.

## 5. Publish

```
git add -A && git commit -m "Refresh: <date> — <one line on what changed>" && git push
```

GitHub Pages redeploys automatically within a couple of minutes. Confirm the live site shows the new `as_of` in the top bar.

## 6. Report

Finish with a short summary: what was added (counts), what changed on the live incident, anything that could not be verified, and the next scheduled check.
