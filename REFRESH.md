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

**The intake rule: widen the intake, never the lens.** A story qualifies if AI is the actor and the consequence lands on ordinary life: someone's job, kids, money, vote, safety or health. It does not qualify just for being about AI. Product launches, funding rounds, benchmark races, research papers and lab politics with no real-world consequence stay out; a breakthrough qualifies only when it changes what AI can do to or for people, with a number attached. When the reporting, not the company, ties a story to AI (a layoff whose memo never mentions AI), it runs labelled Reported. The index, the scoring and the forecasts keep their strict gates; only the front door is wide.

**Beats.** Give a Wire story `"beat": "near-you"` (data centres, power bills, water, local fights), `"school"` (classrooms, tutors, school rules, teachers) or `"decided"` (AI deciding credit, insurance, hiring, benefits, policing, facial recognition) when it belongs there; the beat pages at wire/<beat>/ collect them permanently. Search for these three every refresh. Job cuts go in `jobs_evidence` of the matching occupation in `research/jobs.json`, tagged `company says AI` or `reported as AI`; they feed the layoffs ledger at jobs/layoffs/.

**Where the mass-audience stories live:** beyond the security press, check local news (TV station sites, city papers), court filings and dockets (lawsuits, charges, AI-faked evidence), school boards and education press (Chalkbeat, local districts), consumer-protection and scam reports (FTC, state attorneys general, Action Fraud, Scamwatch, police appeals), hospitals and health regulators, and election officials. One sourced local story about a named person often beats a national trend piece.

Coverage the front page wants every refresh (not only incidents): **on-the-record admissions** (risk factors in IPO filings and annual reports, insurance and liability warnings, lab statements and system cards); **AI and jobs at scale** (layoffs, buyouts and hiring freezes at named large employers; say whether the company itself cites AI or the reporters do, and label it Reported if only the reporters do); **governments preparing the public** (household preparedness advice, outage drills, alerts that name cyber attacks or AI threats; say when no specific threat is cited, and treat older campaigns as context, not news). Trace a viral post back to its original source before using it, and quote only what the source actually quotes.

Keep descriptions of hacking techniques high-level. Never invent a figure; if a number cannot be sourced, leave it out.

## 2. Edit the research files

- New scored incidents: append to `research/jul_oct_2026_mine.json` (same schema as the existing rows: id, date, date_precision, disclosed, title, actors, category, setting, summary, harm, H, R, A, N, I, source_url, source2_url, confidence, notes). Rate the five factors by `research/rubric.md`. Prefer a primary source as `source_url`.
- **When a fact changes** (an agency lists a flaw, a fix ships, a victim is named), update every current-state field that states it (case `current` notes and one-liners in `research/case_status.json`, `WATCH` statuses and `LIVE` in `build/build_live.py`) and add the old claim's pattern to `research/superseded.json`; `check_site.py` fails the build if any current-state field still says it. Dated history (timelines, changelog, the Wire archive) is left as it was.
- New victims for incidents other than PHP2Shell: append to `research/victims.json` with `status_group` (confirmed|attacked|disrupted|reported|other) and a plain `status` label; such rows flow into data/victims.json and Am I Exposed? automatically.
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

- The headline wall (top of the page): in `research/news.json`, give the stories that lead the page `tag` (the index's own line, Drudge-style: short, blunt, alarming where the facts are), `wall` (`lead` for the four-line cluster at the very top of the page, `siren` for exactly one, or `1`/`2`/`3` for the columns: 1 attacks, flaws and emergencies; 2 deepfakes, elections and families; 3 labs, money and advances), `red` (true for the most urgent) and `wall_rank` (order). Rewrite the lines every refresh. The one rule: provocative but true. A line may sharpen, compress and pick the scariest true fact; it may never claim something the linked story doesn't support (no 'hacked' for a test, no 'victims' for honeypots, no figures rounded up). Re-read each line against its story before publishing. The page follows Drudge's order: the lead cluster (a picture, then its four lines), then the siren's centred picture and headline, then the masthead, then the columns. Give the first `lead` story and the `siren` story a picture: only free images (Unsplash or Pexels under their free licences, not Unsplash+; Wikimedia Commons public domain or CC0, or CC BY / CC BY-SA with the credit shown), never an outlet's own photo or a news-agency image. Download it into `assets/img/` (about 1200x675 JPEG) and record it in `assets/img/CREDITS.json` (file, source page, author, licence, date); set `img` (the absolute path, `/assets/img/<file>`), `img_alt` (what the picture shows), `img_credit` ('Photo: <author> / <site>') and `img_credit_url` (the photo's page). Pictures are illustrative, so pick one that fits the story without implying it shows the real people or place. Reuse an image already in `assets/img/` when it fits. If no story has `wall: siren`, the wall hides and the Wire's own siren shows.
A live stat marked `hide_while_zero` (today: organizations confirmed breached by name) stays off the page while its value is 0 and reappears on its own when the refresh sets a real number (Colin, Oct 27). A first confirmed breach is a rung move: push-notify.

### Headline rules for the wall (front page spec v1.0, §4, §6, §8)

- Readers should land on a page they can read. For a non-English source, first look for an English report of the same fact and link that; if the fact exists only in the original (a figure first published in Japanese, say), link the original through Google Translate (`https://<host with dots as hyphens>.translate.goog/<path>?_x_tr_sl=<lang>&_x_tr_tl=en&_x_tr_hl=en`) and add ", translated from <language>" to the outlet name.
- The tag-along lines under the lead (`wall: "lead"`) must fit on one line: 40 characters at most, a fact the lead headline doesn't already say ("$2,000 bait server fell in 19 hours", "Federal deadline to fix it: Oct 29").
- A bare number can be the whole headline when the number is the news (Colin, Oct 27): "57,097 break-in attempts", with who counted it and the dates in the ⓘ receipt, not the headline. When the count updates, change only the number.

Columns: `1` **Broke out & broke in** (something got somewhere it wasn't supposed to be, in the real world: break-ins, escapes with real exposure, AI-enabled intrusions, AI data leaks, physical incidents; plus all-clears and restorations for a running story). `2` **Got smarter, took over** (a capability jump, unsupervised work, AI taking workflows at named companies, on-the-record admissions or filings by labs or governments; no launches, no unreplicated benchmarks, no opinion). `3` **Fakes, scams & you** (reaches people who never chose AI: clones, fraud, impersonation, election, school and workplace fakes, consumer warnings, money). One column per story, by its consequence. Never pad a column.

**Human fact first (Colin's standing rule): no technical term, acronym or codename carries a headline.** The headline sells the human fact: who is attacking what, how fast, how widely, what is still missing. The technical name rides second, in the standfirst, the tracker and the dispatch, for professionals and search. Translations: PHP → "the software behind most websites"; vulnerability → "a flaw", "a way in"; unpatched → "still unfixed"; CISA → "America's cyber agency"; a CISA KEV listing → "a formal US government warning"; "exploited in the wild" → "hackers are already using it in real attacks"; "PoC public" → "the break-in instructions are public"; a model codename (Mythos 5, Codex) → whose AI it is ("Anthropic's top AI", "OpenAI's coding AI"); sandbox → "locked test box". The enticement engine is **clock + count + gap**: how long, how many, what's still missing.

**The three rungs of proof, never blurred:** TRIED (attempts logged) ≠ PROVEN (a test or decoy system actually broken into) ≠ HIT (a real victim confirmed). A headline states the rung it has reached and no higher: decoy servers broken into is PROVEN, not "in real attacks". The running story's box shows its current rung; reaching HIT is an end state.

**Short and powerful above all (Colin's standing rule): get to the point in the most powerful true way, and cut every word that doesn't hit.** Example: not "Startup's AI agents got into Anthropic's systems in under 12 hours" but "AI AGENTS BROKE INTO ANTHROPIC'S SYSTEMS IN 12 HOURS". Context and caveats go in the standfirst, not the headline.

The formula: **named actor + strong past-tense verb + named object + consequence or number.** If three of the four can't be filled truthfully, it isn't a front-page line yet.

1. Plain English: no jargon (agentic → its AI / AI acting on its own; CVE → flaw, name the software; PoC → working exploit code is public; exfiltrated → stole; sandbox escape → broke out of its test box).
2. The actor in the first three words. Never 'Report warns' or 'Study finds'.
3. Strong past-tense verb. 'Says/warns' only when the statement is the event (an order, a filing, a retraction).
4. Specific, never withholding: the key fact is in the line. No 'you won't believe'.
5. Numbers copied from the source, never rounded up.
6. 5 to 11 words in the columns, up to 13 for the siren.
7. Columns in sentence case; only the siren in capitals. Red only for a WS-4/5 story or a live WS-4 consumer threat, at most one per column.
8. Set `label` on every line: `confirmed` (state it flat), `reported` (single source; the line names the claimer or says 'claims'), `denied`, `retracted`, `lab` (a test result; never leads column 1). The page shows the label chip.
9. Retractions and denials run in the same column at the same size as the claim, with 'takes it back', 'withdraws' or 'denies' in the line.
10. Alarm matches the level: WS-1/2 flat; WS-3 consequence-forward; only WS-4/5 may be red. No exclamation marks below WS-4. Banned: terrifying, shocking, nightmare, chilling, bombshell, jaw-dropping, insane, slams, blasts, destroys, and could/might/may as the main verb.
11. One story per line; no roundups.
12. Write each line from the opened source page in the same step. Never from memory.

The running story (`SERIAL` in `build/build_live.py`, shown pinned at the top of column one with a day counter): one serial only. It is live while the incident is unresolved and still developing. Its `name` is the human fact ("The flaw under most websites"), the codename goes in `tech_name` and rides on the tracker link. Keep `rung` (tried, proven, hit) and `rungs` (date, note, source for each) current; each refresh, update `standing` (one line, every clause sourced; set `source_url`) and `last_fact`. Close it on the first end state: a fix ships for every open flaw, a victim is confirmed by name, an agency lists it as exploited, or 7 days pass with no new fact. To close: `state='closed'`, `closed=<date>`, `verdict=<one line saying how it ended>`; the page then shows the verdict instead of the counter. A new serial starts only when a new incident qualifies; other live incidents get counters on their Record pages.

The action line (`action: {text, url}` on the siren): only when the source or an official statement gives a real, specific action for readers ('Run PHP? Check your version'), linked to that source or the tracker. Most days there is none; never pad it with generic advice.

The siren: one story, the most consequential as of this refresh; qualifies by confirmed WS-4/5 harm, a confirmed break-in or escape with named organizations, an on-the-record lab or government admission that changes the picture, or large-scale named consumer harm. A lab-only finding can't be the siren unless a named real system was exposed. Give it `standfirst`: two or three plain sentences on what is confirmed and what isn't. The outgoing siren drops to the top of its column. A quiet day is said plainly.

Before publishing, check every line: actor in the first three words; past-tense verb, no banned words; key fact stated; every number and name copied from the opened source; verb strength matches the label, temperature matches the level.

### The marks (small, earned, each explains itself in one honest line; if a mark can't, it doesn't ship)

- **Rung tags** (`label`: tried, proven, hit, plus reported, lab, retracted, denied): the word always rides with the mark, and the tap line states the negative half ("Proven: a test system was actually broken into. No real victim confirmed yet.").
- **Moved** (`moved: {dir: up|down, at, note}` on a Wire item): set it when a story climbs or falls a rung, or a claim is withdrawn. It runs both ways; ▼ for withdrawals is as important as ▲.
- **Running story**: keep `recheck` (what was just rechecked and is still true) and `recheck_at` (when you actually checked those sources; never set it without checking), `next_test` (the next dated call that tests it, in plain words) and the rungs current. Set `quiet=True` in META on a refresh where nothing moved; the page then says "Rechecked: nothing moved" at full size.
- **Edition**: the edition number comes from the timed changelog entries; `snapshot.py` freezes each one. Never skip it.
- **Receipts** (`receipt` on a Wire item, a one-line string): required for any number in a front-page line. Name who counted it, over what window, and what it doesn't mean ("Their sensors only: Cloudflare reported millions"). A number that can't be sourced that precisely comes off the line. Lines are complete sentences, never ending in an ellipsis. The test-vs-real distinction is never dropped from a line: a server left open on purpose is a test server.
- **Not yet built, fill these fields as you go so they can ship:** `independent: {n, who, carried_by}` on Wire items, counting independent reporting, not outlets (14 sites running one Reuters story is one source); for "called it" marks, the call's `resolution` plus the running record; for the race bar on a running story, sourced dates for disclosed, exploit public, fix out, fix verified. First/most tags only for comparisons the index itself can prove, with sensor and window named.
- **Never**: reader streaks, visit badges, view counts. The pull comes from the world changing, not from mechanics that punish readers for being away.

- "What AI can now do" (the capability index): `research/capabilities.json`, one object per milestone with the five maturity stages (`demonstrated`, `reproduced`, `accessible`, `reliable`, `consequences`, each `{status: yes|partial|no|unknown, date, note, source_url}`), `everyday` (one sentence on what it means for real lives, jobs or families), `related_incident_ids` (ids from `data/incidents.json`), `metric_label`/`metric_value`, `source_url`, `source2_url`, `confidence`. Add a milestone only for a dated, sourced result that moved what AI can do (a benchmark, a time horizon, a scale, a success rate), never a product launch. Each refresh: add new milestones since `as_of`, and upgrade a stage only when a source shows it (a reproduction, a public release, production evidence, a documented consequence). `unknown` is the honest default. `build/build_live.py` validates and writes `data/capabilities.json`.
- "Did they fix it?" (case statuses): `research/case_status.json`, one object per case with the chain `reported → response → claimed_fix → retest → current`. Each refresh: re-check every case for a new response, claimed fix, independent check or recurrence, and move `current.status` only on evidence: `fixed` needs an independent party confirming the fix under stated conditions; `unverified` is a claimed fix nobody independent has checked; `disputed`, `reopened` (recurred after a claimed fix), `unresolved` (no fix claimed), `ongoing` (still unfolding). Add a case when a new incident scores 55 or more in the wild. "No public response found" is a valid, important entry; never invent a response. Written to `data/fixes.json` by the build.

- "Then. Now. Still." (`TNS` in `build/build_live.py`): one everyday task in three columns, each pointing at capability ids and incident ids already on the index. Change it only when a stronger documented comparison exists; never describe it as a Warning Shots test.
- The signal ribbon, the WS dispatch numbers (date order) and the WS-1 to WS-5 levels (the tiers) are computed from the data at page load; nothing to edit. `feed.xml` (the Wire and the brief) is written by `build_site.py`.

## 2b. The call sheet (every refresh)

`research/calls.json` holds the index's short and medium calls: dated yes/no questions with the index's odds. `build/aux_data.py` holds the long forecasts; `build/build_live.py` merges both into `data/calls.json`. Rules:

1. **Grade first.** For every open call whose `resolve_by` has passed, or whose question has been settled by events, set `resolution: {outcome: yes|no|void, date, note, source_url}` with a source that shows it. `void` is only for a question that turned out to be unanswerable as written (say why). Never change a question, its odds or its date after it resolves, and never delete a resolved call: misses stay on the board. A call at exactly 50% counts as neither right nor wrong in the track record (it is still in the Brier score); this rule was set on Oct 26, before any call resolved.
2. **Move odds on evidence, not mood.** Before a call resolves, its `odds` may change when something material happens; say what in the changelog ("CISA KEV odds 45% → 70%: Sophos confirmed a compromise"). The forecast ledger (`research/forecast_log.jsonl`, written by `build_brief.py`) records every refresh's odds, so moves are public.
3. **Keep the board stocked.** At least five open short calls (`horizon: days`, resolving within about two weeks) at all times, drawn from the watch list and the live incident. A good call is specific, checkable at a named source, and has odds you would defend; avoid questions whose answer is already public.
4. Field names: `id` (stable, kebab-case, ends with the resolve date, e.g. `php-kev-by-oct31`), `question`, `opened`, `resolve_by`, `odds` (0–1), `horizon` (`days|weeks|months`), `basis`, `signposts`, `tags`, `related` (`incident_id`, `watch_id`, `capability_id`), `source_url` (where it will be checked), `resolution`.
5. Plain wording: give each call a `plain` field, the question in plain words with no acronyms ("Will America's cyber agency formally warn about the flaw under most websites by Oct 31?"). On the day a call is graded, the homepage leads its Coming up strip with the verdict, a miss shown as prominently as a hit, plus the running record, for 36 hours.
6. Presentation: the page shows these as the index's own expectations in plain words (very likely, likely, could go either way, unlikely, very unlikely), never as a betting board. Readers do not place picks and there is no reader record; keep it that way. Odds live in the data and the changelog so moves stay accountable.
6. The report pastes the graded calls (hit or miss) and any odds that moved, with the reason.

## 2c. Posts on X (every refresh)

`research/x_posts.json` holds posts worth surfacing. The homepage shows the three that matter most right now, **each on a different story** (`story` field: a short slug shared by posts on the same story). It ranks by `power` (a post older than 72 hours counts one point less), breaks ties by showing a kind not yet shown (the news, the claim, the take) and then the newest, and reaches back up to 14 days. **The bar is urgency.** The model is the kind of post that stops a scroll: "JUST IN: Anthropic's Mythos continued launching cyberattacks in 98% of tests even after being warned..."; a big name's hot take on "Microsoft's offer of a buyout to 60,000 people"; an official agency saying a model kept attacking a real person. Fear and outrage are fine when the facts carry them; academic, incremental or polite posts are not what this box is for, however correct. Aim for three different stories, ideally a mix of hard news, an official or first-hand warning, and a sharp take (including angry reactions with real reach).

`power` 1–5: **5** = changes what a reader fears, believes or does today (an AI caught attacking real people, mass job cuts tied to AI, an agency warning, a working attack on everyone's software); **4** = a big story's sharpest take or fastest report; **3** = solid but niche or academic; **1–2** = filler (never add it). Every refresh: search X for the day's three biggest AI stories (the lead, the running case, the biggest jobs/money story, the biggest lab or agency story), add the strongest post found for each, and lower the `power` of anything that has gone stale. Stay in scope: posts about AI only (a viral warning about something else, such as general disaster preparedness, does not go in unless it is tied to AI). One exception: a major attack on election or critical systems in the run-up to a vote may go in while the cause is unknown, with `bar: false` (it never takes the red bar) and a `what` line that says plainly whether any AI link has been reported.

Each post is drawn to look like the post on X (name, photo, handle, the exact text, time) with our label above it and our plain-words line under it. A long post shows its opening and "Show more on X". Every post gets exactly one label, and the label is about the post, not the topic:

- `breaking`: a new, material fact a reader can check, posted either by a first-hand source (the researcher, the victim organisation, the reporter who broke it) or by a fast news account ("JUST IN: ...") whose fact you have confirmed against the original report or announcement before listing it (say which in `seen_via`). A `breaking` post shows as Breaking for 12 hours, then as First-hand. Only `breaking` and `official` posts under 12 hours old can take the red bar above the lead; after that they stay in the list with their label.
- `official`: an agency, company or lab account stating something on the record.
- `claim`: a new result or allegation nobody independent has checked yet (shown as "Unverified claim"). A claim never becomes `breaking` until a second, independent source confirms it; then add that source to the related Wire item.
- `opinion`: commentary, analysis, explainer threads, reactions. Shown as "Opinion" in the list, never in the red bar, however big the account.

Finding posts: search X through web search (`site:x.com <topic>`, the names of the people at the centre of the story, and the fast news accounts that post "JUST IN" items on AI, such as Polymarket, Watcher.Guru, Leading Report and Walter Bloomberg). If Colin pastes X links into `research/x_inbox.txt` (one per line), read every one first: open it, add it if it meets the bar, then clear the file. X only; no other social network.

Rules: only X posts (`https://x.com/<handle>/status/<id>`). After adding entries, run `python3 build/fetch_x.py`: it pulls each post's exact text, name, photo and time from X's public embed data into `research/x_cache.json`, which the page uses. Read the fetched text before keeping an entry; if the fetch fails, the post was deleted or is private, so drop it (never show a post whose text you have not seen in full). Never retype or edit the post text; the card shows it exactly. `what` is our plain-words line under the card (human fact first, no acronyms, says plainly when something is unconfirmed); `quote` is the shortest exact line that carries it. `who` says why this person matters, including any tie to the company involved. Fields: `id`, `url`, `platform` ("X"), `author`, `handle`, `who`, `posted` (UTC ISO, from the fetch), `kind`, `power`, `story`, `what`, `quote`, `seen_via`, `related` (Wire or incident id). Do not delete old entries; the page stops using them after 14 days. Never post, reply, like or repost on X from the refresh.

## 2d. Breakthroughs (every refresh)

The site covers AI's breakthroughs as seriously as its dangers. `research/breakthroughs.json` feeds the Breakthroughs band at the top of the Wire on the homepage (newest six) and `/breakthroughs/` (all of them, never pruned). Every refresh, look for real advances from the last few days in medicine, science, math, weather and climate, the planet, safer software, new models and new abilities people can use, and add the strongest. Aim for at least one new entry a day and keep the band at six.

- **Write the payoff to a person, not the lab's announcement.** `payoff` is the headline: what changed for people, short, no acronyms or model names carrying it ("An AI solved 8 in 10 of medicine's hardest diagnosis puzzles. Doctors solved fewer than 4", not "MAI-DxO achieves 83% on NEJM CPC benchmark"). `means` is two or three plain sentences: what happened, who it helps, and the honest catch (not available yet, weaker at X, only the company's word so far).
- **`try`** (optional): `[what to do, url]` only when an ordinary person can use it today; say if it costs money or needs a sign-in. Never invent one.
- **`proof`**, the same discipline as the warnings: `in-use` (people are using it now), `published` (peer-reviewed paper), `reproduced` (an independent group got the same result), `claimed` (the company's or lab's own word, not yet checked). A lab claim is never written as settled fact.
- Fields: `id`, `news_id` (the Wire item it comes from; add the Wire item first, with its source), `date`, `area` (Medicine, Science, Math and physics, Weather, Planet, Safer software, New models, Everyday), `proof`, `payoff`, `means`, `try`.
- Hype check: no "revolutionary", no "game-changer", no claims the source doesn't make. The wonder should come from the facts.

## 2e. People, not just systems (every refresh)

Every story is about what happened to people, good and bad. Three standing rules:

- **Who it hit / who it helped.** The lead item (or `serial.lead` on a takeover) carries `people: {kind: "hit" | "helped", text}`: one plain sentence about the real people affected, from the reporting ("A Michigan grandmother wired $9,000 to a voice that sounded like her grandson"; "Families in Japan couldn't book trains or check bank balances for days"). Each breakthrough carries `people`: who it helps, concretely ("People with rare illnesses who wait years for a diagnosis"). Counted groups are fine when no person is named. Don't repeat the people line in a tag-along line or column headline. Never invent a person, never add details the reporting doesn't give, never name a minor or a private person the reporting didn't name, and keep it to text (no photos of real victims; the free-images rule stands).
- **One human story a day,** alternating harm and help: a Wire item whose `tag` leads with the person ("Laid-off support agent trains the AI that replaced her" style), flagged `human: true`.
- **Count the people.** When an incident record has a sourced count of people harmed or helped, put it in the record's `people_count` with its source, so the index can one day say how many people AI incidents touched.

## 2f. Entity tags (every refresh, from now on)

Every new Wire item, incident record and breakthrough gets an `entities` object naming who and what is involved, so readers can later follow an organization, a product or a sector and be told when it appears:

`"entities": {"orgs": [], "vendors": [], "products": [], "models": [], "sectors": [], "states": []}`

- `orgs`: organizations affected or acting (victims, agencies, companies in the story). `vendors`: companies whose product is the route in or the subject. `products`: named software or services (e.g. "PHP", "Langflow", "ChatGPT"). `models`: named AI models. `sectors`: from a fixed list (government, health, finance, education, retail, media, tech, energy, transport, legal, defense, consumer). `states`: two-letter US state codes when a place is named.
- Use the name as the source gives it, consistently spelled (check existing tags first). Leave a list empty rather than guess. Never tag a private person.
- Never rewrite history: when a fact changes, add a dated note, don't overwrite the old record.

## 2g. The Chart (every morning refresh)

One original chart a day, built from the index's own data, at the top of the homepage Wire and on its own page (`/chart/<id>/`) with the data table and a downloadable image. The bar is high: a chart someone would screenshot and send. It has to make one thing obvious in five seconds.

- **The Charts gallery** (`/chart/`) keeps every chart for reference: `pin: true` puts a chart under "Start here" (the two or three most important, evergreen ones; refresh their data, never their meaning); `home: true` picks which of the day's charts leads the homepage. Every chart is built twice, wide (16:9) and tall (4:5, for phones and Instagram), with share buttons, downloads and embed code on its page; write `why` (why it matters, two sentences) for each new one.
- **Add an entry to `research/charts.json`**: `{id: "YYYY-MM-DD-slug", date, kind, title?, dek?, takeaway?, why?, pin?, home?}` (title, dek and takeaway are optional overrides; renderers compute honest defaults). `kind` names a renderer in `build_chart.py`.
- **Vary it.** Don't run the same kind two days in a row, and add a new kind (a new renderer) at least once a week. Ideas that fit our data: the live case as a timeline of rungs and counts; the forecast board as dots on a probability line, graded ones marked hit or miss; "Did they fix it?" as a chain per case; layoffs tied to AI by month and company; incidents by who did the acting (person vs. AI) over time; the map of organizations named in the live case; breakthroughs vs. incidents by month; the Panel's numbers once live.
- **Design rules** (follow the dataviz skill): one point per chart; the title says the finding in plain words, human fact first; one axis only; muted gray for context and the alarm red only for the thing that matters, always labelled (never colour alone); a legend for two or more series; every mark hoverable with its source, and linked to its case page where one exists; a data table on the page; source line and the citation baked into the image. Navy card, the site's fonts, 16:9.
- **Truth rules:** only data already on the record; counts recomputed from the data at build time, never typed in; no projection or trend line that the data doesn't support; small numbers shown as counts, not percentages.
- Look at the PNG before publishing. Labels must not collide with marks or each other.

## 2a. Sundays: the source audit

A GitHub Action (`.github/workflows/link-audit.yml`) fetches every URL in `data/*.json` early on Sunday mornings and writes `research/link_audit.json` (dead: 404/410/DNS; unreachable: timeouts and 5xx; 401/403/429 count as alive). On the Sunday 06:37 run, and on any run where that file is newer than `as_of`:

1. For each `dead` URL, find the claim it supports (`used_in` names the file and record id) and repair it: a different outlet or document stating the same fact, or an archived copy (`https://web.archive.org/web/2026/<url>`). Update the research file; never leave a figure without a live or archived source. If nothing supports the claim any more, say so in the record's `notes` and soften the claim.
2. For each `unreachable` URL, open it once by hand. Leave it if it loads; treat it as dead if it does not.
3. Re-verify the figures in ten records picked at random (dates, numbers, who said what) against their sources, and fix what drifted.
4. Note the count repaired in the changelog entry ("source audit: 3 dead links replaced, 10 records re-verified").

### No repeats

The front page (`/`) carries each story once: the lead (the siren: the day's strongest story, one photo, one big headline, one plain sentence), then up to four tag-along lines right under the lead headline (the `wall: "lead"` items: Drudge's follow-on angles on the same story, each linking straight out), then the running-story strip (one line: day, name, rung chip and `serial.strip`, a plain status of ten words or fewer; it opens to the proof ladder), then the three columns. Each column ends with its standing desk (our own pages, labelled, never styled as headlines): Follow the damage, What AI can now do, Protect yourself. The counts in them come from the data; the section links (nav) and the desk shelf under the masthead are set in `pageshell.py` (`MID_NAV`, `DESKS`). When a new standing page family goes live, add it to the right desk. The running story takes the lead slot only on escalation: set `serial.lead` (tag, standfirst, img and credits) when it reaches Hit or a formal government warning, and clear it when the story cools; the siren then heads the first column. Keep `serial.strip` true at every refresh.

The lead shows its headline only: the standfirst is not displayed on the homepage for now (Colin, Oct 27), but keep writing it, because share cards and search descriptions use it. The lead carries **What it means for you** (`you` on the siren item in research/news.json): `touch`, one or two plain sentences on whether and how the story reaches an ordinary reader, honest when the answer is no ("Nothing here reached families") and never implying a risk the reporting doesn't support; `today`, one small real action [text, optional url, optional link label]; and `lens`, the same two fields rewritten for any of `family`, `money`, `work`, `site`, `vote` that fit (omit a lens rather than force it). No fear without a next step. Every refresh that changes the siren writes a new `you`.

**The morning script.** The 05:17 morning refresh also writes `posts/podcast/<YYYY-MM-DD>.md`, the day's script of about 13 minutes, following `posts/podcast/SHOW.md` exactly (cold open with the date and the siren tag, the verbatim ident, the menu, the Warning in five beats ending with What it means for you, Day N of the running story with its rung and next test, the Breakthrough, Your Life (job, money, kids), the Watch List, the Last Shot, the verbatim sign-off), about 1,900 words (shorter on a quiet day, never padded), plus the 60-second cut, with a source-check list at the end. It is a draft for Colin to record; nothing publishes it. The full Wire board, the 'since the last refresh' box and the live panel live on `/wire/`; the charts, scores and trackers on `/index/`. Never put the running story's story in a column as well, and keep the four lead lines different from the running story's `recheck` text.

## 3. Build and check

```
cd build && python3 build_data.py && python3 build_deep.py && python3 build_live.py && cp data/*.json ../data/ && cd ..
python3 build/fetch_x.py                                # exact text of the X posts in research/x_posts.json -> research/x_cache.json
python3 build_chart.py                                  # The Chart: today's chart from research/charts.json -> data/chart.json, chart/<id>/, assets/charts/<id>.svg
python3 build/make_img.py                               # WebP copies of new photos in assets/img/ at three sizes (the page picks the one that fits the screen)
python3 build_site.py                                   # index.html, data/bundle.json (one request for all data), feed.xml, JSON-LD
python3 -m http.server 8765 --bind 127.0.0.1 >/dev/null 2>&1 &
node prerender.mjs  http://127.0.0.1:8765/index.html   # bakes the first screen (ribbon, ticker, siren, brief, Wire, live rail) into index.html so the headline is in the first paint
node make_charts.mjs http://127.0.0.1:8765               # PNG of each new chart (share and press image)
node make_og.mjs    http://127.0.0.1:8765/index.html
node make_cards.mjs http://127.0.0.1:8765/index.html   # share cards for every dispatch; re-renders only changed records
python3 build_tools.py                                  # the two free tools (shield/, scraped/); refreshes the AI-crawler list from GitHub when reachable
python3 build_tracker.py                                # the live-incident tracker page (php2shell/): status, am-I-affected, FAQ, timeline, victims
python3 build_press.py                                  # the embeddable level badge (assets/badge.svg, /badge/) and the press page (/press/); after the tools and tracker, before build_pages
node make_help_cards.mjs                                # share images for the help and learn pages (text-only template cards)
python3 build_help.py                                   # 'What to do' pages (help/<slug>/) from research/help.json; drafts stay noindex and out of the sitemap until Colin sets approved: true and reviewed: <date>
python3 build_learn.py                                  # Know What It Means (learn/<slug>/) from research/learn.json; same draft/approval rule as the help pages
python3 build_families.py                               # checks/, jobs/, can-ai/, exposed/ (from data/victims.json, quality-gated), midterms-2026/; each family stays noindex until approved in research/approvals.json. New victims rows and incidents flow into exposed/ automatically
python3 build_archive.py                                # the Wire archive (wire/<date>/, wire/archive/, never pruned), the beats (wire/near-you/, school/, decided/) and the layoffs ledger (jobs/layoffs/)
python3 build_pages.py                                  # full pages for every incident, case and milestone (i/, c/, m/) with their own cards, plus sitemap.xml
cd build && python3 build_posts.py && cp data/posts.json ../data/ && cd ..   # the post queue (posts/<date>.md)
cd build && python3 build_brief.py && cd ..                                  # the daily brief script (briefs/<date>.md) and the forecast ledger (research/forecast_log.jsonl)
python3 check_site.py                                   # MUST pass: counts match the data, no retracted claim stated without its retraction, tags present, news-sitemap dates real; add each new retraction to research/retractions.json
python3 snapshot.py                                     # freezes this edition into archive/<date-time>/ (scripts stripped) for the Edition No. link
node shot.mjs       http://127.0.0.1:8765/index.html
```

`prerender.mjs` must print `prerendered 5 blocks` (it exits non-zero if the page threw or a block was missing; never publish without it, or the first paint is empty). `shot.mjs` must print `errors none` three times. The build prints the Wire's story count and the siren headline; check both. Look at `shots/site-desktop-top.png` and `shots/site-phone-top.png` before publishing. If anything fails, fix it; do not publish a broken page.

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

## Growing the page families (every refresh)

The families compound from the same research the refresh already does. Each refresh:

- **Am I Exposed?** grows by itself: every new row in `research/victims.json` (named organisation, status, extent, source) becomes an entry and, if it passes the gate (confirmed, attacked, or in two or more incidents), an indexable page. Never name an organisation without a source; use the status labels exactly.
- **Midterms tracker** (`research/midterm_fakes.json`): add every newly confirmed, labelled or alleged AI election fake, same fields, until results are certified; then freeze the page with a closing note. **On Nov 4** (the first refresh that day) write the promised post-mortem into `research/midterms_after.json` (`h1`, `published`, `body_html`): which fakes reached people, which were caught and by whom, which claims collapsed, and every place this index was wrong (alleged fakes that turned out real, missed fakes, mislabelled statuses). It publishes at midterms-2026/after/ automatically.
- **Can AI Do Your Job?** (`research/jobs.json`): when a refresh finds a company tying cuts to AI, a deployment, or a study for an occupation we cover, add a `jobs_evidence` row or upgrade a task's status (with its dated source). Add a new occupation once a week when the evidence for it is real.
- **Is This a Scam?** (`research/checks.json`) and **What AI Can Now Do** (`research/can_ai.json`): add a new case to the matching page whenever the index gets one; add a new pattern or question once a week when it has an authoritative source (FTC, FBI, CFPB, a regulator, a peer-reviewed or lab study).
- **Publishing is automatic; Colin does not approve individual pages.** New pages in any existing section (help/, learn/, checks/, jobs/, can-ai/, exposed/, the trackers) publish on the build when they pass `check_site.py` and the sourcing rules: every fact from a page opened this run, primary sources first, Tried/Proven/Hit never blurred, nothing graphic, minors never identifiable. New help/learn entries go in with `"approved": true` and `"reviewed": ""`; never set `reviewed` or a "Reviewed by Colin Balfe" byline on anything he hasn't read himself. Only an entirely new *section* (a new URL family or a new kind of page) starts as a draft, and the run's notification says so.
- **Pages about minors, suicide or sexual images** publish like any other page, but take extra care: link support lines (988, NCMEC, CCRI), state allegations as allegations, and never describe images or methods.
- Bump `updated` on any page you change, and run `python3 build_families.py` before `build_pages.py`.
