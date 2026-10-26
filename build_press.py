#!/usr/bin/env python3
"""The embeddable level badge and the press page.

Writes:
  assets/badge.svg        320x64 "Today's AI threat level" badge, rebuilt every refresh (other sites hotlink it)
  assets/badge-small.svg  180x28 compact version
  badge/index.html        how to embed it (HTML and Markdown snippets, each linking back)
  press/index.html        for journalists: what the site is, how to cite it, key figures, screenshots, logos, contact
and adds /badge/ and /press/ to data/tool_urls.json so build_pages.py puts them in the sitemap.
Run after build_tools.py and build_tracker.py, before build_pages.py.

The level is computed exactly as assets/app.js drawLevel() does: the highest severity among incidents disclosed in the
24 hours before as_of, plus the live incident. Contact details come from press.json ({"contact_email": ""}); while that is
empty the page points to GitHub issues instead of inventing an address."""
import json, os, html, datetime as dt
from zoneinfo import ZoneInfo
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pageshell import shell
esc = html.escape
L = lambda f: json.load(open(f'data/{f}.json', encoding='utf-8'))
meta = L('meta'); inc = L('incidents'); build = json.load(open('assets/build.json'))
site = meta['site_url']; AS_OF = meta['as_of']; repo = meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')
ET = ZoneInfo('America/New_York')
asof = dt.datetime.fromisoformat(AS_OF)
date_label = asof.astimezone(ET).strftime('%b %-d, %Y')

# ---------- the level (mirror of app.js sevScore + drawLevel)
TIERS = ['Minor', 'Moderate', 'Serious', 'Severe', 'Critical']
def sev(r):
    H, R, A, N, I = (float(r[k]) for k in 'HRANI')
    harm = 100 * (0.5 * H / 5 + 0.25 * R / 5 + 0.25 * I / 5); signal = 100 * (0.6 * A / 4 + 0.4 * N / 5)
    s = round(0.55 * harm + 0.45 * signal)
    return s, (4 if s >= 80 else 3 if s >= 60 else 2 if s >= 40 else 1 if s >= 20 else 0)
def when(r):
    d = r.get('disclosed') or r['date']
    try:
        x = dt.datetime.fromisoformat(d if len(d) > 10 else d + 'T12:00:00')
        return x if x.tzinfo else x.replace(tzinfo=ET)
    except ValueError:
        return None
pool = [r for r in inc if (w := when(r)) and dt.timedelta(0) <= asof - w <= dt.timedelta(days=1)]
live = next((r for r in inc if r['id'] == meta.get('live_incident')), None)
if live: pool.append(live)
if pool:
    top = max(pool, key=lambda r: sev(r)[0]); score, ti = sev(top)
else:
    top, score, ti = None, 0, 0
n = ti + 1; tier = TIERS[ti]
COL = {1: '#6B7A6E', 2: '#6B7A6E', 3: '#B5751A', 4: '#C0391B', 5: '#FF3300'}[n]

# ---------- the badge SVGs (system fonts only: an <img> cannot load web fonts)
MARK = open('assets/mark.svg', encoding='utf-8').read()
mark_inner = MARK[MARK.index('>') + 1:MARK.rindex('</svg>')]
FONT = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
title = f"Today's AI threat level: WS-{n} {tier}, per Warning Shots ({date_label})"
big = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="64" viewBox="0 0 320 64" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<rect width="320" height="64" fill="#0F1B2D"/>
<svg x="8" y="8" width="48" height="48" viewBox="0 0 100 100">{mark_inner}</svg>
<rect x="64" y="0" width="6" height="64" fill="{COL}"/>
<text x="80" y="20" font-family="{FONT}" font-size="10" font-weight="700" letter-spacing="1.2" fill="#9FB0C4">TODAY’S AI THREAT LEVEL</text>
<text x="80" y="43" font-family="{FONT}" font-size="22" font-weight="800" fill="#FFFFFF">WS-{n} <tspan fill="{COL if n >= 3 else '#C9D3DE'}">{tier.upper()}</tspan></text>
<text x="80" y="57" font-family="{FONT}" font-size="9.5" fill="#9FB0C4">warningshots.ai · {esc(date_label)}</text>
</svg>
'''
small = f'''<svg xmlns="http://www.w3.org/2000/svg" width="190" height="28" viewBox="0 0 190 28" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<rect width="190" height="28" fill="#0F1B2D"/>
<svg x="3" y="3" width="22" height="22" viewBox="0 0 100 100">{mark_inner}</svg>
<text x="31" y="18" font-family="{FONT}" font-size="11" font-weight="700" fill="#C9D3DE">AI THREAT LEVEL</text>
<rect x="128" y="0" width="62" height="28" fill="{COL}"/>
<text x="159" y="18" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="800" fill="#FFFFFF">WS-{n}</text>
</svg>
'''
open('assets/badge.svg', 'w', encoding='utf-8').write(big)
open('assets/badge-small.svg', 'w', encoding='utf-8').write(small)

def copybox(code, label):
    return f'<div class="pr-code"><pre><code>{esc(code)}</code></pre><button type="button" class="pr-copy" data-copy="{esc(code)}">Copy {esc(label)}</button></div>'
STYLE = """<style>
.pr h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3.2rem);line-height:1.04;margin:18px 0 8px}
.pr .lede{font-size:18px;line-height:1.5;max-width:68ch;margin:0 0 8px}
.pr h2{font-family:var(--serif);font-size:1.5rem;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}
.pr p,.pr li{line-height:1.55;max-width:72ch}
.pr-code{position:relative;margin:10px 0 18px;background:var(--panel);border:1px solid var(--line-2)}
.pr-code pre{margin:0;padding:12px 14px;overflow-x:auto;font-size:12.5px;line-height:1.5;white-space:pre-wrap;word-break:break-all}
.pr-copy{display:block;margin:0;border:0;border-top:1px solid var(--line-2);width:100%;padding:9px;font:inherit;font-weight:700;font-size:14px;background:var(--ink);color:var(--paper);cursor:pointer}
.pr-demo{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:14px 0}
.pr-figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,12rem),1fr));gap:10px;margin:14px 0}
.pr-figs div{border:1px solid var(--line-2);border-top:3px solid var(--alarm);padding:12px;background:var(--panel)} .pr-figs b{display:block;font-size:1.7rem;line-height:1.1} .pr-figs span{font-size:13.5px;color:var(--ink-2)}
.pr-shots{display:grid;align-items:start;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));gap:14px;margin:14px 0}
.pr-shots figure{margin:0} .pr-shots img{width:100%;height:auto;border:1px solid var(--line-2);display:block} .pr-shots figcaption{font-size:13px;color:var(--ink-2);margin-top:6px}
.pr-dl{display:flex;flex-wrap:wrap;gap:8px 18px;font-weight:600}
</style>"""

# ---------- /badge/
link = site + '?utm_source=badge&utm_medium=embed'
html_big = f'<a href="{link}" title="Today\'s AI threat level, checked three times a day"><img src="{site}assets/badge.svg" width="320" height="64" alt="Today\'s AI threat level, from Warning Shots"></a>'
html_small = f'<a href="{link}" title="Today\'s AI threat level, checked three times a day"><img src="{site}assets/badge-small.svg" width="190" height="28" alt="AI threat level, from Warning Shots"></a>'
md_small = f'[![AI threat level, from Warning Shots]({site}assets/badge-small.svg)]({site}?utm_source=badge&utm_medium=readme)'
bbody = f"""{STYLE}<article class="pr">
<h1>Put today’s AI threat level on your site</h1>
<p class="lede">A free badge that shows the current Warning Shots level. It updates on its own three times a day, so your page always shows today’s reading. No script, no tracking, no cookies: it is a plain image and a link.</p>
<div class="pr-demo"><a href="/"><img src="/assets/badge.svg?v={esc(build['build'])}" width="320" height="64" alt="Today's AI threat level, from Warning Shots"></a><a href="/"><img src="/assets/badge-small.svg?v={esc(build['build'])}" width="190" height="28" alt="AI threat level, from Warning Shots"></a></div>
<p>Today it reads <b>WS-{n} {esc(tier)}</b>{f' ({score}/100), set by: <a href="/i/{esc(top["id"])}/">{esc(top["title"])}</a>' if top else ''}.</p>
<h2>Standard badge (320 × 64)</h2>
<p>For a sidebar, footer or article. Paste this into your page’s HTML:</p>
{copybox(html_big, 'badge code')}
<h2>Compact badge (190 × 28)</h2>
<p>For a newsletter, a status page or a tight sidebar:</p>
{copybox(html_small, 'compact code')}
<h2>For a GitHub README or anything in Markdown</h2>
{copybox(md_small, 'Markdown')}
<h2>What the level means</h2>
<p>The level is the highest score among AI incidents disclosed in the last 24 hours and the incident being tracked live, by the index’s <a href="/index/#about">published formula</a>: WS-1 Minor, WS-2 Moderate, WS-3 Serious, WS-4 Severe, WS-5 Critical. Every incident behind it links to its sources.</p>
<p>Use it freely. Please keep the link so readers can see why the level is what it is. Writing about AI incidents? See the <a href="/press/">press page</a>.</p>
</article>"""
bdesc = f"A free badge showing today's AI threat level (now WS-{n} {tier}). Updates three times a day; no script, no tracking. Copy the HTML or Markdown to embed it."
ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "Embed today's AI threat level", "url": site + 'badge/', "description": bdesc,
                 "publisher": {"@type": "Organization", "name": "Warning Shots", "url": site}}, ensure_ascii=False).replace('</', '<\\/')
os.makedirs('badge', exist_ok=True)
open('badge/index.html', 'w', encoding='utf-8').write(shell(title="Embed today's AI threat level on your site", desc=bdesc, url=site + 'badge/', img=site + 'assets/og.png', body=bbody, jsonld=ld, kind='tool'))

# ---------- /press/
try:
    press = json.load(open('press.json', encoding='utf-8'))
except (OSError, ValueError):
    press = {}
email = (press.get('contact_email') or '').strip()
contact = (f'<p>Email <a href="mailto:{esc(email)}">{esc(email)}</a>. Corrections are answered first.</p>' if email else
           f'<p>Open an issue on <a href="{esc(repo)}/issues" rel="noopener">GitHub</a>; corrections are answered first and logged in the public changelog.</p>')
year = asof.year
cite_short = f'Source: Warning Shots (warningshots.ai)'
cite_full = f'Warning Shots. "The AI Incident Index." warningshots.ai, accessed {asof.astimezone(ET).strftime("%B %-d, %Y")}. {site}index/'
cite_data = f'Warning Shots ({year}). AI Incident Index dataset [Data set]. {site}data/incidents.csv'
shots = [(f, c) for f, c in [('front-desktop.jpg', 'The front page: the day’s level, the running story and the headlines'),
                             ('front-phone.jpg', 'The front page on a phone'),
                             ('record-desktop.jpg', 'The Record: every incident since 2023, scored and sourced'),
                             ('tracker-desktop.jpg', 'A live-incident tracker')] if os.path.exists(f'assets/press/{f}')]
shots_html = ''.join(f'<figure><a href="/assets/press/{f}"><img src="/assets/press/{f}" alt="{esc(c)}" loading="lazy"></a><figcaption>{esc(c)}</figcaption></figure>' for f, c in shots)
pbody = f"""{STYLE}<article class="pr">
<h1>Press</h1>
<p class="lede">Warning Shots tracks AI’s dangers and breakthroughs as they land on real lives, checked three times a day. Every significant AI incident since 2023 is scored 0–100 by a published formula and linked to its sources. Free to cite, quote and embed.</p>
<h2>Key figures</h2>
<div class="pr-figs"><div><b>{build['n']}</b><span>AI incidents since 2023, each scored and sourced</span></div><div><b>{build['severe_prior12']} → {build['severe_last12']}</b><span>severe incidents, previous 12 months vs. last 12</span></div><div><b>{build['agentic_share']}%</b><span>of this year’s real-world cases where the AI itself did the acting</span></div><div><b>WS-{n}</b><span>today’s level: {esc(tier)}</span></div></div>
<p>Figures as of {esc(date_label)}; they change as the index is refreshed. Check the <a href="/index/">Record</a> for the current numbers before publishing.</p>
<h2>How to cite</h2>
<p>Short credit, for a chart or a caption:</p>
{copybox(cite_short, 'credit')}
<p>Full citation:</p>
{copybox(cite_full, 'citation')}
<p>The dataset:</p>
{copybox(cite_data, 'dataset citation')}
<p>Linking to a single incident? Every incident has its own page, for example <a href="/i/">the full list</a>. Link to that page so readers land on the sources.</p>
<h2>How it works</h2>
<p>Each incident is rated on five factors (harm, reach, autonomy, novelty and irreversibility) and combined into a 0–100 score by a <a href="/index/#about">formula published on the site</a>. Claims about live events are graded by proof: <b>Tried</b> (attempts logged), <b>Proven</b> (a test system broken into, no real victim yet), <b>Hit</b> (a real victim confirmed). The three are never blurred. Forecasts are dated and never edited after they resolve, and every change is logged.</p>
<h2>Screenshots</h2>
{f'<div class="pr-shots">{shots_html}</div>' if shots else '<p>Screenshots coming soon.</p>'}
<h2>Logo and badge</h2>
<div class="pr-dl"><a href="/assets/warning-shots-mark-800.png" download>Logo mark, PNG 800 px</a><a href="/assets/mark.svg" download>Logo mark, SVG</a><a href="/assets/og.png" download>Today’s share card, PNG</a><a href="/badge/">Live level badge for your site</a></div>
<h2>Data</h2>
<p>The full index is downloadable: <a href="/data/incidents.csv">CSV</a> · <a href="/data/incidents.json">JSON</a>. New reports arrive by <a href="/feed.xml">RSS</a>.</p>
<h2>Contact</h2>
{contact}
</article>"""
pdesc = f"Press resources for Warning Shots: key figures ({build['n']} AI incidents since 2023, scored and sourced), ready-to-paste citations, screenshots, logos and the open dataset."
ld = json.dumps({"@context": "https://schema.org", "@type": "AboutPage", "name": "Warning Shots press", "url": site + 'press/', "description": pdesc,
                 "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site, "logo": {"@type": "ImageObject", "url": site + "assets/icon-512.png"}}}, ensure_ascii=False).replace('</', '<\\/')
os.makedirs('press', exist_ok=True)
open('press/index.html', 'w', encoding='utf-8').write(shell(title='Press: cite, quote and embed Warning Shots', desc=pdesc, url=site + 'press/', img=site + 'assets/og.png', body=pbody, jsonld=ld, kind='tool'))

# ---------- sitemap entries
try:
    tu = json.load(open('data/tool_urls.json'))
except (OSError, ValueError):
    tu = []
for u in (site + 'press/', site + 'badge/'):
    if u not in tu: tu.append(u)
json.dump(tu, open('data/tool_urls.json', 'w'))
print(f'press/ and badge/: level WS-{n} {tier} ({score}), {len(shots)} screenshots')
