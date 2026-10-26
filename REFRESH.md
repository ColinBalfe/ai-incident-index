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
5. **The Wire** (`research/news.json`): the latest reporting, worldwide, on AI's dangers and breakthroughs as they land on real lives, jobs and families: AI incidents, AI-driven cyberattacks and the live incident; what governments, agencies and labs are saying or doing; genuine capability breakthroughs (a result that moves what AI can do, with a number attached, not a product launch); and the everyday consequences, such as jobs and hiring, schools and kids, scams and fraud, health, and money. Aim for 30 to 45 stories from the last 72 hours, with at least a few breakthroughs and a few everyday-impact stories when they exist; never pad with opinion or launch coverage to hit the count. Sources: security press (The Hacker News, BleepingComputer, SecurityWeek, The Record, Krebs, CyberScoop, Dark Reading), wires and papers (Reuters, AP, Bloomberg, FT, WSJ, NYT, Guardian, BBC, Nikkei, Japan Times, Yonhap, Korea Herald, Le Monde, Handelsblatt, ABC Australia), tech press (The Verge, Ars Technica, Wired, TechCrunch, 404 Media, Platformer), official pages (CISA, NCSC, ACSC, FBI, EU Commission, state AGs, PHP Foundation, OpenAI, Anthropic, Google DeepMind, METR, UK AISI).

Keep descriptions of hacking techniques high-level. Never invent a figure; if a number cannot be sourced, leave it out.

## 2. Edit the research files

- New scored incidents: append to `research/jul_oct_2026_mine.json` (same schema as the existing rows: id, date, date_precision, disclosed, title, actors, category, setting, summary, harm, H, R, A, N, I, source_url, source2_url, confidence, notes). Rate the five factors by `research/rubric.md`. Prefer a primary source as `source_url`.
- New victims, timeline events, official statements, implications for an existing deep dive: `research/php2shell.json` (PHP2Shell) or `research/victims.json` (the other five). Follow the existing schemas exactly.
- "Since the last refresh" box: `BRIEF` in `build/build_live.py`: two to four plain, tweet-length lines on what changed, each with a source. Write them so they can be posted as-is.
- Quotes ("In their words" and the pull quotes in each deep dive): `research/quotes.json`. Add a quote only when you have fetched the page and copied the exact words (max ~45 words; mark cuts with …); fields: id, incident_id (from data/deepdives.json or ''), quote, speaker, title, org_type, date, channel, url, via, context, verified, verify_note, weight (0–10; the lead quote is the highest). `build/build_deep.py` copies it to `data/quotes.json`.
- Live panel and 14-day watchlist: `build/build_live.py` (`LIVE`, `LIVE_NOTE`, `WATCH`, `META`). Update `AS_OF`, `AS_OF_LABEL`, `next_check` and add a dated `CHANGELOG` entry that says what changed and how many rows were added or corrected.
- If the live incident has gone quiet (no new facts for 3 days), set `META.live_incident` to the most important active incident, or keep it and say so in `LIVE_NOTE`.
- Corrections to existing rows: use the `FIX` dict in `build/build_data.py` or `build/fixes2.py`, never by editing generated files in `data/`.
- The Wire: rewrite `research/news.json` each refresh (it is a rolling 72-hour board, not an archive). One object per story:

  ```
  {"id": "cybernews-php-third-flaw", "title": "PHP's nightmare is far from over: new unpatched flaw found",
   "url": "https://...", "outlet": "Cybernews", "published": "2026-10-23T14:15:00Z", "time_known": true,
   "kind": "breaking", "region": "Global", "topic": "php2shell",
   "summary": "PHP Foundation tells developers to switch off session upload progress until the next release.",
   "siren": true, "also": [{"outlet": "SecurityWeek", "url": "https://..."}]}
  ```

  Rules: the headline is written by this index (max 110 characters, factual, no clickbait, no copying the outlet's headline verbatim) and links straight to the outlet; `kind` is one of `breaking`, `incident`, `official`, `analysis`; `topic` is one of `php2shell`, `ai-attack`, `ai-incident`, `breakthrough`, `jobs`, `families`, `everyday`, `regulation`, `deepfakes`, `chatbot-harm`, `other`; `summary` is at most 22 words; `published` is the outlet's own timestamp in UTC (set `time_known: false` when only the date is known); exactly one story has `siren: true`, the one the index judges most consequential right now; `also` lists other outlets carrying the same story. Fetch every page before adding it; drop anything you cannot open. Keep paywalled sources only when a free source (`also`) exists. Do not add opinion columns. `build/build_live.py` dedupes, drops stories older than 84 hours and writes `data/news.json`; the page shows a "no stories" line rather than breaking if the file is empty.

- The headline wall (top of the page): in `research/news.json`, give the stories that lead the page `tag` (the index's own line, Drudge-style: short, blunt, alarming where the facts are), `wall` (`lead` for the four-line cluster at the very top of the page, `siren` for exactly one, or `1`/`2`/`3` for the columns: 1 attacks, flaws and emergencies; 2 deepfakes, elections and families; 3 labs, money and advances), `red` (true for the most urgent) and `wall_rank` (order). Rewrite the lines every refresh. The one rule: provocative but true. A line may sharpen, compress and pick the scariest true fact; it may never claim something the linked story doesn't support (no 'hacked' for a test, no 'victims' for honeypots, no figures rounded up). Re-read each line against its story before publishing. The page follows Drudge's order: the lead cluster (a picture, then its four lines), then the siren's centred picture and headline, then the masthead, then the columns. Give the first `lead` story and the `siren` story a picture: only free images (Unsplash or Pexels under their free licences, not Unsplash+; Wikimedia Commons public domain or CC0, or CC BY / CC BY-SA with the credit shown), never an outlet's own photo or a news-agency image. Download it into `assets/img/` (about 1200x675 JPEG) and record it in `assets/img/CREDITS.json` (file, source page, author, licence, date); set `img` (the local path), `img_alt` (what the picture shows), `img_credit` ('Photo: <author> / <site>') and `img_credit_url` (the photo's page). Pictures are illustrative, so pick one that fits the story without implying it shows the real people or place. Reuse an image already in `assets/img/` when it fits. If no story has `wall: siren`, the wall hides and the Wire's own siren shows.
- "What AI can now do" (the capability index): `research/capabilities.json`, one object per milestone with the five maturity stages (`demonstrated`, `reproduced`, `accessible`, `reliable`, `consequences`, each `{status: yes|partial|no|unknown, date, note, source_url}`), `everyday` (one sentence on what it means for real lives, jobs or families), `related_incident_ids` (ids from `data/incidents.json`), `metric_label`/`metric_value`, `source_url`, `source2_url`, `confidence`. Add a milestone only for a dated, sourced result that moved what AI can do (a benchmark, a time horizon, a scale, a success rate), never a product launch. Each refresh: add new milestones since `as_of`, and upgrade a stage only when a source shows it (a reproduction, a public release, production evidence, a documented consequence). `unknown` is the honest default. `build/build_live.py` validates and writes `data/capabilities.json`.
- "Did they fix it?" (case statuses): `research/case_status.json`, one object per case with the chain `reported → response → claimed_fix → retest → current`. Each refresh: re-check every case for a new response, claimed fix, independent check or recurrence, and move `current.status` only on evidence: `fixed` needs an independent party confirming the fix under stated conditions; `unverified` is a claimed fix nobody independent has checked; `disputed`, `reopened` (recurred after a claimed fix), `unresolved` (no fix claimed), `ongoing` (still unfolding). Add a case when a new incident scores 55 or more in the wild. "No public response found" is a valid, important entry; never invent a response. Written to `data/fixes.json` by the build.

- "Then. Now. Still." (`TNS` in `build/build_live.py`): one everyday task in three columns, each pointing at capability ids and incident ids already on the index. Change it only when a stronger documented comparison exists; never describe it as a Warning Shots test.
- The signal ribbon, the WS dispatch numbers (date order) and the WS-1 to WS-5 levels (the tiers) are computed from the data at page load; nothing to edit. `feed.xml` (the Wire and the brief) is written by `build_site.py`.

## 2b. The call sheet (every refresh)

`research/calls.json` holds the index's short and medium calls: dated yes/no questions with the index's odds. `build/aux_data.py` holds the long forecasts; `build/build_live.py` merges both into `data/calls.json`. Rules:

1. **Grade first.** For every open call whose `resolve_by` has passed, or whose question has been settled by events, set `resolution: {outcome: yes|no|void, date, note, source_url}` with a source that shows it. `void` is only for a question that turned out to be unanswerable as written (say why). Never change a question, its odds or its date after it resolves, and never delete a resolved call: misses stay on the board.
2. **Move odds on evidence, not mood.** Before a call resolves, its `odds` may change when something material happens; say what in the changelog ("CISA KEV odds 45% → 70%: Sophos confirmed a compromise"). The forecast ledger (`research/forecast_log.jsonl`, written by `build_brief.py`) records every refresh's odds, so moves are public.
3. **Keep the board stocked.** At least five open short calls (`horizon: days`, resolving within about two weeks) at all times, drawn from the watch list and the live incident. A good call is specific, checkable at a named source, and has odds you would defend; avoid questions whose answer is already public.
4. Field names: `id` (stable, kebab-case, ends with the resolve date, e.g. `php-kev-by-oct31`), `question`, `opened`, `resolve_by`, `odds` (0–1), `horizon` (`days|weeks|months`), `basis`, `signposts`, `tags`, `related` (`incident_id`, `watch_id`, `capability_id`), `source_url` (where it will be checked), `resolution`.
5. Presentation: the page shows these as the index's own expectations in plain words (very likely, likely, could go either way, unlikely, very unlikely), never as a betting board. Readers do not place picks and there is no reader record; keep it that way. Odds live in the data and the changelog so moves stay accountable.
6. The report pastes the graded calls (hit or miss) and any odds that moved, with the reason.

## 2a. Sundays: the source audit

A GitHub Action (`.github/workflows/link-audit.yml`) fetches every URL in `data/*.json` early on Sunday mornings and writes `research/link_audit.json` (dead: 404/410/DNS; unreachable: timeouts and 5xx; 401/403/429 count as alive). On the Sunday 06:37 run, and on any run where that file is newer than `as_of`:

1. For each `dead` URL, find the claim it supports (`used_in` names the file and record id) and repair it: a different outlet or document stating the same fact, or an archived copy (`https://web.archive.org/web/2026/<url>`). Update the research file; never leave a figure without a live or archived source. If nothing supports the claim any more, say so in the record's `notes` and soften the claim.
2. For each `unreachable` URL, open it once by hand. Leave it if it loads; treat it as dead if it does not.
3. Re-verify the figures in ten records picked at random (dates, numbers, who said what) against their sources, and fix what drifted.
4. Note the count repaired in the changelog entry ("source audit: 3 dead links replaced, 10 records re-verified").

## 3. Build and check

```
cd build && python3 build_data.py && python3 build_deep.py && python3 build_live.py && cp data/*.json ../data/ && cd ..
python3 build_site.py                                   # index.html, data/bundle.json (one request for all data), feed.xml, JSON-LD
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &
node prerender.mjs  http://127.0.0.1:8765/index.html   # bakes the first screen (ribbon, ticker, siren, brief, Wire, live rail) into index.html so the headline is in the first paint
node make_og.mjs    http://127.0.0.1:8765/index.html
node make_cards.mjs http://127.0.0.1:8765/index.html   # share cards for every dispatch; re-renders only changed records
python3 build_tools.py                                  # the two free tools (shield/, scraped/); refreshes the AI-crawler list from GitHub when reachable
python3 build_tracker.py                                # the live-incident tracker page (php2shell/): status, am-I-affected, FAQ, timeline, victims
python3 build_pages.py                                  # full pages for every incident, case and milestone (i/, c/, m/) with their own cards, plus sitemap.xml
cd build && python3 build_posts.py && cp data/posts.json ../data/ && cd ..   # the post queue (posts/<date>.md)
cd build && python3 build_brief.py && cd ..                                  # the daily brief script (briefs/<date>.md) and the forecast ledger (research/forecast_log.jsonl)
node shot.mjs       http://127.0.0.1:8765/index.html
```

`prerender.mjs` must print `prerendered 21 blocks` (it exits non-zero if the page threw or a block was missing; never publish without it, or the first paint is empty). `shot.mjs` must print `errors none` three times. The build prints the Wire's story count and the siren headline; check both. Look at `shots/site-desktop-top.png` and `shots/site-phone-top.png` before publishing. If anything fails, fix it; do not publish a broken page.

## 4. Fact-check what you added

Re-verify every new row against its source: names, dates, numbers, who said what. Mark uncertain attributions as uncertain in the text ("consistent with", "reported", "denies"). Fix before publishing.

## 5. Publish

```
git add -A && git commit -m "Refresh: <date> — <one line on what changed>"
git pull --rebase origin main    # the editor may have pushed site changes while this run was working; never force-push
git push
```

After the push has deployed (about two minutes), run `python3 indexnow.py` so Bing, Yandex, Naver and Seznam recrawl the front page, the tracker and new incident pages at once (Bing also feeds DuckDuckGo and ChatGPT search). The share card (`assets/og.png`) is now the siren: its picture and headline, so every share of the front page shows the current lead.

If the rebase reports a conflict, keep both sides' intent (your data rows and changelog entry, the site's code), run the build steps again from `python3 build_site.py` onward, `git add -A && git rebase --continue`, then push. GitHub Pages redeploys automatically within a couple of minutes. Confirm the live site shows the new `as_of` in the top bar.

## 6. Report

Finish with a short summary: what was added (counts), what changed on the live incident, anything that could not be verified, and the next scheduled check. Then paste the post queue from `posts/<date>.md` in full (the editor approves and posts by hand; nothing posts itself), and the daily brief from `briefs/<date>.md` in full (the editor reads, cuts, records or mails it). On Sundays run `python3 build_posts.py --week-ahead` so the queue includes the next-14-days post.

Forecast resolutions: when a forecast's event has happened, or its `resolve_by` date has passed, add `resolved: yes|no`, `resolved_date` and a one-line `resolution_note` with a source to that forecast (in `build/aux_data.py`, where the forecasts live) rather than deleting it. The ledger in the brief grades these in public; a forecast is never silently edited after its window closes, only resolved or replaced with a new, dated one.
