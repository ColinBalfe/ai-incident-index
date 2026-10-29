#!/usr/bin/env python3
"""Trust pages (audit v5): /about/, /methodology/ and /corrections/ as real, citable pages instead of anchors on the Record.
Content comes from what the site already states (the Record's 'About the data', REFRESH rules as published practice) and,
for corrections, from the changelog (build/build_live.py CHANGELOG), research/retractions.json and research/superseded.json.
No 'Reviewed by' byline; Colin Balfe is named as the publisher, which he is."""
import ast, json, re
from pagekit import write, footer_note, webpage, register, esc, fdate, SITE, REPO

def _changelog():
    src = open('build/build_live.py', encoding='utf-8').read()
    m = re.search(r'^CHANGELOG = (\[.*?^\])', src, re.S | re.M)
    try:
        node = ast.parse(m.group(1), mode='eval').body
        return [{k.arg: ast.literal_eval(k.value) for k in e.keywords} for e in node.elts]
    except Exception:
        return []

CL = _changelog()
TODAY = max([c['date'] for c in CL] or ['2026-10-29'])
urls = []
STYLE = '<style>.tp h2{font-family:var(--serif)}.tp code{font-size:.92em}.tp .rule{border-left:4px solid var(--alarm);padding:2px 0 2px 14px;margin:10px 0}</style>'

# ---------------------------------------------------------------- /about/
u = SITE + 'about/'; urls.append(u)
body = f"""<article class="pk tp">{STYLE}<nav class="kick" aria-label="Breadcrumb">About</nav>
<h1>About Warning Shots</h1>
<p class="aka">Warning Shots tracks what AI is doing in the world: the threats, the breakthroughs and what they mean for ordinary people. It is published by Colin Balfe.</p>
<h2>What it is</h2>
<p>Three things, updated three times a day (5:17 AM, 12:17 PM and 6:17 PM ET):</p>
<ul class="rec"><li><b>The Wire</b>: a board of links to other outlets' reporting, each headline written in our own words and checked against the original page.</li>
<li><b>The Record</b>: the AI Incident Index, every significant AI incident since 2023 scored by a <a href="/methodology/">published formula</a> and linked to its sources.</li>
<li><b>Our own work</b>: dated forecasts graded in public, <a href="/analysis/">investigations</a>, live trackers, and practical pages on scams, jobs and what to do.</li></ul>
<h2>How it is made</h2>
<p>Warning Shots is written with AI assistance from public sources. Every fact links to a source that was opened before publishing, and every fact is checked twice: once as it is written, and again in a separate pass before it goes out. The <a href="/methodology/">methodology</a> sets out the rules. Mistakes are corrected in public on the <a href="/corrections/">corrections page</a>, never silently.</p>
<h2>The name</h2>
<p>It is OpenAI's own phrase for the Hugging Face breach: “a warning shot for the company and the world.”</p>
<h2>Contact and reuse</h2>
<p>Corrections and tips: <a href="{esc(REPO)}/issues">open an issue</a>. Press: <a href="/press/">the press page</a>. On X: <a href="https://x.com/WarningShotsAI">@WarningShotsAI</a>. Cite as “Warning Shots (The AI Incident Index)” with a link; the data is downloadable from <a href="/index/#about">the Record</a>.</p>
{footer_note(False)}</article>"""
write('about/index.html', url=u, title='About Warning Shots', desc="What Warning Shots is, who publishes it, how it is made and checked, and how to reach it.", body=body, draft=False,
      crumbs=[('About', '')], graph=[webpage(u, 'About Warning Shots', 'What Warning Shots is and how it is made', TODAY, False, ''), {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": SITE, "founder": {"@type": "Person", "name": "Colin Balfe"}, "correctionsPolicy": SITE + 'corrections/', "ethicsPolicy": SITE + 'methodology/'}])

# ---------------------------------------------------------------- /methodology/
u = SITE + 'methodology/'; urls.append(u)
body = f"""<article class="pk tp">{STYLE}<nav class="kick" aria-label="Breadcrumb">Methodology</nav>
<h1>How Warning Shots works</h1>
<p class="aka">The rules behind the scores, the Wire, the forecasts and the fact-checking, in one place.</p>
<h2>What counts as an incident</h2>
<p>Real-world harms or near-misses caused or materially enabled by an AI system, and lab or evaluation findings of dangerous behavior. This is a curated index of significant, well-sourced incidents, not a census; the AI Incident Database and the OECD monitor count far more.</p>
<h2>How incidents are scored</h2>
<p>Each incident is rated on five factors, then scored by a fixed formula.</p>
<dl><div><dt>Harm (H, 0–5)</dt><dd>Damage actually done: none, embarrassment, material loss, a death or $1M+, multiple deaths or $100M+ or infrastructure, mass casualty or $1B+.</dd></div>
<div><dt>Reach (R, 0–5)</dt><dd>Who was affected: a lab, one person or organization, dozens, thousands, millions, hundreds of millions.</dd></div>
<div><dt>Autonomy (A, 0–4)</dt><dd>Tool (a person misused it), relied on (people trusted bad output), acted (a bounded action), autonomous (multi-step operations on its own), against intent (worked against its own operator or developer).</dd></div>
<div><dt>Novelty (N, 1–5)</dt><dd>Repeat of a known pattern, escalation, first real-world case of a lab behavior, new dangerous capability, paradigm shift.</dd></div>
<div><dt>Irreversibility (I, 0–5)</dt><dd>Caught in a sandbox, easily undone, undone with effort, partly permanent, permanent, permanent and spreading.</dd></div></dl>
<p class="rule"><code>Harm score = 100 × (0.5·H/5 + 0.25·R/5 + 0.25·I/5)</code><br><code>Signal score = 100 × (0.6·A/4 + 0.4·N/5)</code><br><code>Severity = 0.55 × Harm + 0.45 × Signal</code></p>
<p>Tiers: Minor under 20, Moderate 20–39, Serious 40–59, Severe 60–79, Critical 80 and up, shown as WS-1 to WS-5. Harm is weighted more because it already happened; signal is weighted heavily because it predicts what happens next. A lab finding can reach Serious on signal alone, but only real-world damage can make an incident Severe or Critical. The rating is an editorial judgment by a published formula, not a probability; evidence confidence is recorded separately. Each incident has a stable dispatch number (WS-0001 onward, in date order).</p>
<h2>The proof ladder: Tried, Proven, Hit</h2>
<p>For a live attack, a rung is climbed only on a named, linked source. <b>Tried</b>: attacks were attempted and logged; nothing is confirmed broken into. <b>Proven</b>: a test or decoy system was actually broken into; no real victim confirmed. <b>Hit</b>: a real organization confirmed it was breached. The three are never blurred in a headline.</p>
<h2>The Wire</h2>
<p>A board of links to other people's reporting. Each headline is written by Warning Shots in its own words, names the outlet, links straight to it and stays on the board for about three days. Every story is checked against the original page before it is added; stories that cannot be opened are left off. A line may sharpen and pick the most alarming true fact, but never claim more than the story supports: no “hacked” for a test, no “victims” for decoys, no figures rounded up. When only reporters, not the company, tie a story to AI, it is labelled <b>Reported</b>.</p>
<h2>Forecasts</h2>
<p>Each forecast is a dated yes-or-no question with the index's odds, published before the answer is known. The wording never changes after it goes up; each forecast page shows a fingerprint (SHA-256) of the exact question and the commit that added it. Calls are graded in public on the day they resolve, misses stay on the board, and a call at exactly 50% is graded but not counted. Odds can move before resolution only on evidence, and every move is logged.</p>
<h2>Fact-checking</h2>
<p>Every fact is checked twice. First as it is written, from a page opened that day. Then in a separate pass before publishing: each headline and line is re-checked against its source word by word, every computed number is re-derived from the data, and the pass looks for duplicates, things counted as events that aren't (surveys, industry tallies, tests), absolute words (“every”, “first”, “none”) and any number that differs between two places on the site. The build refuses to publish when a headline's figure is missing from its own story or a key figure differs from the data.</p>
<h2>Images and AI</h2>
<p>Photos are free-licensed (Unsplash, Pexels, Wikimedia) and credited; they illustrate, and never show the real people or places. No AI-generated images of real incidents. The site is written with AI assistance and checked against its sources.</p>
<p><a href="/corrections/">Corrections →</a> · <a href="/about/">About →</a></p>
{footer_note(False)}</article>"""
write('methodology/index.html', url=u, title='How Warning Shots works: scores, sources, forecasts and fact-checking', desc="The published formula behind every incident score, the Wire's sourcing rules, how forecasts are graded and how every fact is checked twice.", body=body, draft=False,
      crumbs=[('Methodology', '')], graph=[webpage(u, 'Methodology', 'How Warning Shots scores, sources and checks', TODAY, False, '')])

# ---------------------------------------------------------------- /corrections/
u = SITE + 'corrections/'; urls.append(u)
corr = [c for c in CL if re.search(r'\bCorrect(ion|ed)\b|corrected|retract', c['text'])]
RET = json.load(open('research/retractions.json', encoding='utf-8'))
SUP = json.load(open('research/superseded.json', encoding='utf-8'))
items = ''.join(f'<li><time>{esc(fdate(c["date"]))}</time> {esc(c["text"])}</li>' for c in corr)
rets = ''.join(f'<li><time>{esc(fdate(r["retracted_on"]))}</time> A source withdrew a claim we had reported ({esc(r["id"].replace("-", " "))}); every page now says so.' + (f' <a href="{esc(r["source"])}">Source</a>' if r.get('source') else '') + '</li>' for r in RET)
sups = ''.join(f'<li><time>{esc(fdate(s["since"]))}</time> {esc(s["why"])}.</li>' for s in SUP)
full = ''.join(f'<li><time>{esc(fdate(c["date"]))}</time> {esc(c["text"])}</li>' for c in CL)
body = f"""<article class="pk tp">{STYLE}<nav class="kick" aria-label="Breadcrumb">Corrections</nav>
<h1>Corrections and changes</h1>
<p class="aka">When Warning Shots gets something wrong, it says so here, with the date, and fixes every page that carried it. Nothing is changed silently.</p>
<h2>Corrections</h2><ul class="rec">{items or '<li>None yet.</li>'}</ul>
<h2>Facts that changed</h2><p class="meta">Not errors: things that were true when published and later changed. The build blocks the old wording anywhere it still describes the present.</p><ul class="rec">{sups}</ul>
<h2>Claims withdrawn by their source</h2><ul class="rec">{rets}</ul>
<h2>Every refresh, logged</h2><details><summary>The full changelog ({len(CL)} entries)</summary><ul class="rec">{full}</ul></details>
<p>Spotted an error? <a href="{esc(REPO)}/issues">Tell us</a>. <a href="/methodology/">How we check →</a></p>
{footer_note(False)}</article>"""
write('corrections/index.html', url=u, title='Corrections and changes | Warning Shots', desc="Every correction Warning Shots has made, with dates, plus facts that changed and claims withdrawn by their sources, and the full log of every refresh.", body=body, draft=False,
      crumbs=[('Corrections', '')], graph=[webpage(u, 'Corrections', 'Corrections and changes', TODAY, False, '')])
import os
tu_p = 'data/tool_urls.json'
tu = json.load(open(tu_p)) if os.path.exists(tu_p) else []
tu = [x for x in tu if x not in urls] + urls
json.dump(tu, open(tu_p, 'w'))
print(f'trust: about, methodology, corrections ({len(corr)} corrections, {len(CL)} changelog entries)')
