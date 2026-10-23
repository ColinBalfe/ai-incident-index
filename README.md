# Warning Shots

See what’s coming. Know what it means for you.

A public, live-updated index of every major AI safety incident since January 2023: scored 0–100 by a fixed rubric, linked to its primary source, and projected forward with dated forecasts. It also tracks, for the biggest multi-victim incidents, every organization publicly named as hit, and what security agencies, governments and AI companies have said. The Wire, at the top of the page, is a rolling board of links to the latest reporting worldwide on AI's dangers and breakthroughs and what they mean for real lives, jobs and families. "What AI can now do" is a capability index graded from demonstration to real consequences, drawn against the incident line. "Did they fix it?" tracks each major incident from report to response to claimed fix to independent check.

Live site: `index.html` (served by GitHub Pages). Data: `data/*.json` (open; cite as "The AI Incident Index" with a link).

## How it is built

```
research/            raw research files: incidents by period, PHP2Shell, victims, official statements, quotes, the Wire (news.json), capability milestones (capabilities.json), case statuses (case_status.json), rubric
build/               Python that turns research into the site's data files (run in order: build_data.py, build_deep.py, build_live.py)
build/data/          output of the build (copied to data/)
data/                what the page loads
index.template.html  page template; build_site.py fills the OG tags, JSON-LD and build id -> index.html, and writes data/bundle.json (all data in one request)
prerender.mjs        bakes the first screen (ribbon, ticker, siren, brief, Wire board, live rail) into index.html so it is in the first paint; the script redraws it on load
404.html             branded not-found page; sends old /i/, /c/, /m/ links back to the matching deep link
manifest.webmanifest, assets/icon-*.png  home-screen icon and name
assets/app.js        all page logic (d3 v7, vendored as assets/vendor/d3-lite.min.js, only the modules the page uses; regenerate from assets/vendor/d3-lite.entry.js with esbuild)
make_og.mjs          renders assets/og.png (the share card) from the live page with Playwright
make_cards.mjs       renders a 1200x630 share card per dispatch into cards/ (incremental, manifest-based)
build_pages.py       writes i/<id>/, c/<id>/ and m/<id>/ pages (own title, description and card; redirect to the deep link) plus sitemap.xml and robots.txt
build/build_posts.py drafts the post queue for X from each refresh into posts/ (nothing posts itself)
shot.mjs, sections.mjs  QA screenshots at desktop and phone widths; print console errors
REFRESH.md           the refresh runbook used by the scheduled task
```

Rebuild everything:

```
cd build && python3 build_data.py && python3 build_deep.py && python3 build_live.py && cp data/*.json ../data/
cd .. && python3 build_site.py
python3 -m http.server 8765 --bind 127.0.0.1 &   # then:
node prerender.mjs http://127.0.0.1:8765/index.html   # expect "prerendered 21 blocks"
node make_og.mjs http://127.0.0.1:8765/index.html
node shot.mjs    http://127.0.0.1:8765/index.html   # expect "errors none" three times
```

`prerender.mjs`, `make_og.mjs`, `make_cards.mjs` and `shot.mjs` need `npm i playwright` and a Chromium; set the `executablePath` at the top of each file to yours.

## Scoring

Five factor ratings per incident (Harm, Reach, Autonomy, Novelty, Irreversibility), then

```
Harm score   = 100 × (0.5·H/5 + 0.25·R/5 + 0.25·I/5)
Signal score = 100 × (0.6·A/4 + 0.4·N/5)
Severity     = 0.55 × Harm + 0.45 × Signal
```

Minor under 20, Moderate 20–39, Serious 40–59, Severe 60–79, Critical 80 and up. The full rubric is in `research/rubric.md` and on the page under "How the scores work".

## Corrections

Open an issue with the incident id (from `data/incidents.json`), what is wrong, and a source. Every factual claim on the page is meant to be traceable to a linked source; the ratings and forecasts are the index's own judgments.
