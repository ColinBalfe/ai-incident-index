#!/usr/bin/env python3
"""Know What It Means: the explainer section (learn/<slug>/ and the hub learn/), built from research/learn.json.

Three paths, from everyday to big-picture: Living with AI, How it works, Where it's going. Each piece leads with a short
answer, explains in plain words, puts theory next to the dated record from the index, and ends with what to do, an FAQ,
sources and the next piece in the path.

Drafts ("approved": false) are noindex, out of the sitemap and llms.txt, with a visible banner, exactly like build_help.py.
Run after build_help.py, before build_pages.py."""
import json, os, html, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pageshell import shell
esc = html.escape
meta = json.load(open('data/meta.json', encoding='utf-8')); site = meta['site_url']
REPO = meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')
inc = {r['id']: r for r in json.load(open('data/incidents.json', encoding='utf-8'))}
P = json.load(open('research/learn.json', encoding='utf-8'))
BY = {p['slug']: p for p in P}
REVIEWER = 'Colin Balfe'
PATHS = [('living', 'Living with AI', 'Practical help for the AI already in your life and your family’s.'),
         ('how', 'How it works', 'What’s actually going on inside the tools, in plain words.'),
         ('where', 'Where it’s going', 'The big ideas about powerful AI, set next to what has actually happened.')]
PNAME = {k: n for k, n, _ in PATHS}
ROBOTS_ON = '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'
ROBOTS_OFF = '<meta name="robots" content="noindex, nofollow">'

def a(u, t):
    return f'<a href="{esc(u)}"' + (' target="_blank" rel="noopener noreferrer"' if u.startswith('http') else '') + f'>{esc(t)}</a>'
def fdate(s):
    try: return dt.date.fromisoformat(s).strftime('%b %-d, %Y')
    except Exception: return s
def rec_li(when, ref, text, label=''):
    if ref in inc:
        r = inc[ref]
        return f'<li><time>{esc(when)}</time> {esc(text)} <a href="/i/{esc(ref)}/">The case file →</a> <small>({a(r.get("source_url") or "", r.get("source_label") or "source") if r.get("source_url") else ""}{" · lab or test finding" if r.get("setting") != "wild" else ""})</small></li>'
    return f'<li><time>{esc(when)}</time> {esc(text)} <small>({a(ref, label or "source")})</small></li>'

STYLE = """<style>
.lp{max-width:760px}
.lp .kick{font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--alarm);margin:18px 0 8px}
.lp .kick a{color:inherit}
.lp h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3rem);line-height:1.05;margin:0 0 10px}
.lp .meta{font-size:13px;color:var(--ink-3);margin-bottom:16px}
.lp .ans{border:2px solid var(--ink);border-left:8px solid var(--ink);background:var(--panel);padding:16px 18px;margin:0 0 8px}
.lp .ans b.k{display:block;font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);margin-bottom:8px}
.lp .ans p{margin:0;font-size:clamp(1.08rem,2vw,1.28rem);line-height:1.45;font-family:var(--serif)}
.lp h2{font-family:var(--serif);font-size:1.55rem;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}
.lp h3{font-size:1.05rem;margin:18px 0 6px}
.lp p,.lp li{line-height:1.6}
.lp dl{margin:0;display:block!important} .lp dl div{padding:9px 0;border-bottom:1px solid var(--line)} .lp dt{font-weight:700} .lp dd{margin:2px 0 0;color:var(--ink-2)}
.lp ol.steps{counter-reset:s;list-style:none;padding:0;margin:0}
.lp ol.steps li{counter-increment:s;position:relative;padding:10px 0 10px 46px;border-bottom:1px solid var(--line)}
.lp ol.steps li::before{content:counter(s);position:absolute;left:0;top:10px;width:32px;height:32px;border-radius:50%;background:var(--ink);color:var(--paper);font:800 16px/32px Arial,sans-serif;text-align:center}
.lp ol.steps b{display:block}
.lp table{width:100%;border-collapse:collapse;font-size:15px;margin:8px 0} .lp th,.lp td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line)}
.lp .rec{list-style:none;padding:0} .lp .rec li{padding:9px 0;border-bottom:1px solid var(--line)} .lp .rec time{font-weight:700;margin-right:6px} .lp .rec small{color:var(--ink-3)} .lp .rec small a{color:var(--ink-3)}
.lp .rung{border-left:4px solid var(--alarm);padding:2px 0 2px 14px;margin:14px 0}
.lp .card{white-space:pre-line;border:2px dashed var(--ink-3);background:var(--panel);padding:16px 18px;font:600 16px/1.6 Arial,sans-serif}
.lp .share{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.lp .share button{font:700 14px/1 var(--sans);padding:10px 14px;border:1px solid var(--ink);background:var(--ink);color:var(--paper);cursor:pointer}
.lp .share button.alt{background:transparent;color:var(--ink)}
.lp details{border-bottom:1px solid var(--line);padding:10px 0} .lp summary{font-weight:700;cursor:pointer;font-size:16.5px} .lp details p{margin:8px 0 0}
.lp .src{font-size:14px} .lp .src li{margin:4px 0}
.lp .next{display:block;margin:28px 0 0;padding:16px 18px;border:2px solid var(--ink);text-decoration:none;color:var(--ink)} .lp .next small{display:block;font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin-bottom:6px} .lp .next b{font-family:var(--serif);font-size:1.3rem}
.lp .disc{font-size:13px;color:var(--ink-3);margin-top:26px;border-top:1px solid var(--line);padding-top:12px}
.lp .draft{background:#FFF4D6;color:#5A4300;border:1px solid #E5C76B;padding:10px 12px;font-size:14px;margin:12px 0}
.lp .paths{display:grid;gap:14px} .lp .paths section{border-top:4px solid var(--ink);padding-top:8px} .lp .paths ul{padding-left:18px}
@media print{.mast,footer,.share,.draft,.skip{display:none!important}}
</style>"""

def section_html(s):
    out = f'<h2>{esc(s["h"])}</h2>'
    for para in s.get('p', []):
        out += f'<p>{esc(para)}</p>'
    if s.get('table'):
        t = s['table']; out_t = '<table><thead><tr>' + ''.join(f'<th>{esc(c)}</th>' for c in t[0]) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in row) + '</tr>' for row in t[1:]) + '</tbody></table>'
        out = out.replace(f'<h2>{esc(s["h"])}</h2>', f'<h2>{esc(s["h"])}</h2>' + out_t, 1)
    if s.get('list'):
        out += '<dl>' + ''.join(f'<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>' for t, d in s['list']) + '</dl>'
    if s.get('steps'):
        out += '<ol class="steps">' + ''.join(f'<li><b>{esc(t)}</b>{esc(d)}</li>' for t, d in s['steps']) + '</ol>'
    return out

built, approved = [], []
for p in P:
    url = f"{site}learn/{p['slug']}/"
    draft = not p.get('approved'); rev = p.get('reviewed') or ''
    secs = p['sections']
    body_secs = ''
    for s in secs:
        body_secs += section_html(s)
        if s['h'] == 'What the record shows so far' and p.get('ladder'):
            body_secs += ''.join(f'<div class="rung"><h3>{esc(name)}</h3><ul class="rec">' + ''.join(rec_li(w, ref, t) for w, ref, t in items) + '</ul></div>' for name, items in p['ladder'])
    card = ''
    if p.get('card'):
        card = f'<h2>{esc(p["card"]["h"])}</h2><p>Print it or copy it, fill in the blanks, and keep it by the phone or tablet.</p><div class="card">{esc(p["card"]["text"])}</div><div class="share"><button type="button" data-copy="{esc(p["card"]["text"])}">Copy the card</button><button type="button" class="alt" onclick="window.print()">Print this page</button></div>'
    record = ''
    if p.get('record'):
        record = '<h2>From the record</h2><p>Dated cases from the Warning Shots index and the reporting behind them.</p><ul class="rec">' + ''.join(rec_li(*x) for x in p['record']) + '</ul>'
    faq = ''.join(f'<details{" open" if i < 2 else ""}><summary>{esc(q)}</summary><p>{esc(t)}</p></details>' for i, (q, t) in enumerate(p['faq']))
    srcs = ''.join(f'<li>{a(u, t)}</li>' for t, u in p['sources'])
    deeper = ''.join(f'<li><b>{esc(t)}</b>. {esc(d)}</li>' for t, d in p.get('deeper', []))
    links = ''.join(f'<li><a href="{esc(u)}">{esc(t)} →</a></li>' for u, t in p.get('links', []))
    nx = BY.get(p.get('next'))
    nxt = f'<a class="next" href="/learn/{esc(nx["slug"])}/"><small>Next · {esc(PNAME[nx["path"]])}</small><b>{esc(nx["h1"])} →</b></a>' if nx else ''
    byline = (f'Reviewed by {REVIEWER} on {fdate(rev)} · ' if (not draft and rev) else '') + f'Updated {fdate(p["updated"])}'
    body = f"""{STYLE}<article class="lp">
{'<div class="draft"><b>Draft, not yet reviewed.</b> Hidden from search engines until every fact is checked and approved.</div>' if draft else ''}
<nav class="kick" aria-label="Breadcrumb"><a href="/learn/">Know What It Means</a> · {esc(PNAME[p['path']])}</nav>
<h1>{esc(p['h1'])}</h1>
<div class="meta">{esc(byline)} · Every fact links to its source</div>
<section class="ans" aria-label="The short answer"><b class="k">The short answer</b><p>{esc(p['answer'])}</p></section>
<div class="share"><button type="button" data-copy="{esc(p['h1'] + ' ' + url)}">Copy link to share</button></div>
{body_secs}
{card}
{record}
<h2>Questions people ask</h2>
{faq}
{f'<h2>Go deeper</h2><ul>{deeper}</ul>' if deeper else ''}
{f'<h2>Related</h2><ul>{links}</ul>' if links else ''}
<h2>Sources</h2>
<ul class="src">{srcs}</ul>
{nxt}
<p class="disc">Spot an error? <a href="{esc(REPO)}/issues">Tell us</a>; corrections are made and logged. Written with AI assistance from public sources; {('every fact checked and approved by ' + REVIEWER) if (not draft and rev) else ('checked against those sources before publishing' if not draft else 'awaiting fact-check')}. General information, not medical, legal or financial advice.</p>
</article>"""
    img = site + (f"assets/learn/{p['slug']}.png" if os.path.exists(f"assets/learn/{p['slug']}.png") else 'assets/og.png')
    art = {"@type": "Article", "headline": p['title'][:110], "description": p['desc'], "url": url, "mainEntityOfPage": url, "image": [img],
           "datePublished": p['updated'], "dateModified": p['updated'], "inLanguage": "en", "isAccessibleForFree": True,
           "articleSection": PNAME[p['path']], "citation": [u for _, u in p['sources']],
           "author": {"@type": "Person", "name": REVIEWER} if (not draft and rev) else {"@type": "Organization", "name": "Warning Shots", "url": site},
           "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site, "logo": {"@type": "ImageObject", "url": site + "assets/icon-512.png"}}}
    if p['slug'] == 'treacherous-turn':
        art["about"] = [{"@type": "Thing", "name": "Treacherous turn"}, {"@type": "Person", "name": "Nick Bostrom"}, {"@type": "Book", "name": "Superintelligence: Paths, Dangers, Strategies", "author": {"@type": "Person", "name": "Nick Bostrom"}, "datePublished": "2014"}]
    wp = {"@type": "WebPage", "@id": url, "url": url, "name": p['title'], "description": p['desc'], "inLanguage": "en", "dateModified": p['updated'], "primaryImageOfPage": img}
    if not draft and rev:
        wp["reviewedBy"] = {"@type": "Person", "name": REVIEWER}; wp["lastReviewed"] = rev
    graph = [wp, art, {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in p['faq']]},
             {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Warning Shots", "item": site}, {"@type": "ListItem", "position": 2, "name": "Know What It Means", "item": site + 'learn/'}, {"@type": "ListItem", "position": 3, "name": p['title'], "item": url}]}]
    steps = next((s['steps'] for s in secs if s.get('steps')), None)
    if steps and p['path'] == 'living':
        graph.append({"@type": "HowTo", "name": p['h1'], "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d} for i, (t, d) in enumerate(steps)]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace('</', '<\\/')
    out = shell(title=p['title'], desc=p['desc'], url=url, img=img, body=body, jsonld=ld, kind='learn')
    if draft:
        out = out.replace(ROBOTS_ON, ROBOTS_OFF, 1); assert ROBOTS_OFF in out
    os.makedirs(f"learn/{p['slug']}", exist_ok=True)
    open(f"learn/{p['slug']}/index.html", 'w', encoding='utf-8').write(out)
    built.append((p, draft))
    if not draft: approved.append(url)

# ---------- the hub
live = [p for p, d in built if not d]
cols = ''.join(f'<section><h2>{esc(n)}</h2><p>{esc(d)}</p><ul>' + ''.join(f'<li><a href="/learn/{esc(p["slug"])}/"><b>{esc(p["h1"])}</b></a></li>' for p, _ in built if p['path'] == k) + '</ul></section>' for k, n, d in PATHS)
hub_body = f"""{STYLE}<article class="lp"><div class="kick">Warning Shots</div><h1>Know What It Means</h1>
<p>The front page shows what AI did today. This is where it starts to make sense: practical help for the AI already in your life, how the tools actually work, and the big ideas about where it's going, each set next to what has actually happened.</p>
<div class="paths">{cols}</div>
<p class="disc">Written with AI assistance from public sources and checked by a person before publishing.</p></article>"""
hub_url = site + 'learn/'
ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "Know What It Means: understanding AI and your life", "url": hub_url,
                 "publisher": {"@type": "Organization", "name": "Warning Shots", "url": site}}, ensure_ascii=False).replace('</', '<\\/')
hub = shell(title='Know What It Means: understanding AI and your life', desc='Plain, sourced guides to the AI in your life: setting up a chatbot for a parent, why chatbots make things up, and big ideas like the treacherous turn, set next to the record.', url=hub_url, img=site + 'assets/og.png', body=hub_body, jsonld=ld, kind='learn')
if not live:
    hub = hub.replace(ROBOTS_ON, ROBOTS_OFF, 1)
os.makedirs('learn', exist_ok=True)
open('learn/index.html', 'w', encoding='utf-8').write(hub)

try: tu = json.load(open('data/tool_urls.json'))
except (OSError, ValueError): tu = []
tu = [u for u in tu if '/learn/' not in u] + ([hub_url] if live else []) + approved
json.dump(tu, open('data/tool_urls.json', 'w'))
json.dump(approved, open('data/learn_urls.json', 'w'))
print(f'learn/: {len(built)} pieces ({len(live)} approved, {len(built) - len(live)} drafts kept noindex)')
