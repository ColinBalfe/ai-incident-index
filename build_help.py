#!/usr/bin/env python3
"""'What to do' help pages: help/<slug>/ and the hub help/, built from research/help.json.

Each page answers one urgent search ("a loved one called in a panic asking for money", "is this text a scam") the way a
panicked person needs it: the answer first, then numbered steps, warning signs, real dated cases from the index, the
numbers with sources, where to report, an FAQ, and every source listed.

Drafts: a page whose "approved" is false is built with robots noindex, kept out of the sitemap and llms.txt, and carries
a visible draft banner. Colin approves a page by setting "approved": true and "reviewed": "<YYYY-MM-DD>" after checking
every fact; only then does it get the reviewer byline, the sitemap entry and an IndexNow ping.

Run after build_press.py, before build_pages.py (which reads data/tool_urls.json for the sitemap)."""
import json, os, html, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pageshell import shell
esc = html.escape
meta = json.load(open('data/meta.json', encoding='utf-8')); site = meta['site_url']
inc = {r['id']: r for r in json.load(open('data/incidents.json', encoding='utf-8'))}
PAGES = json.load(open('research/help.json', encoding='utf-8'))
BY = {p['slug']: p for p in PAGES}
REVIEWER = 'Colin Balfe'

def a(u, t, ext=True):
    return f'<a href="{esc(u)}"' + (' target="_blank" rel="noopener noreferrer"' if ext and u.startswith('http') else '') + f'>{esc(t)}</a>'
def fdate(s):
    try: return dt.date.fromisoformat(s).strftime('%b %-d, %Y')
    except Exception: return s

STYLE = """<style>
.hp{max-width:760px}
.hp .kick{font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--alarm);margin:18px 0 8px}
.hp h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3rem);line-height:1.05;margin:0 0 10px}
.hp .meta{font-size:13px;color:var(--ink-3);margin-bottom:16px}
.hp .now{border:2px solid var(--ink);border-left:8px solid var(--alarm);background:var(--panel);padding:16px 18px;margin:0 0 8px}
.hp .now b.k{display:block;font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--alarm);margin-bottom:8px}
.hp .now p{margin:0;font-size:clamp(1.08rem,2vw,1.3rem);line-height:1.45;font-family:var(--serif)}
.hp .share{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}
.hp .share button{font:700 14px/1 var(--sans);padding:10px 14px;border:1px solid var(--ink);background:var(--ink);color:var(--paper);cursor:pointer}
.hp .share button.alt{background:transparent;color:var(--ink)}
.hp h2{font-family:var(--serif);font-size:1.55rem;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}
.hp p,.hp li{line-height:1.55}
.hp ol.steps{counter-reset:s;list-style:none;padding:0;margin:0}
.hp ol.steps li{counter-increment:s;position:relative;padding:10px 0 10px 46px;border-bottom:1px solid var(--line)}
.hp ol.steps li::before{content:counter(s);position:absolute;left:0;top:10px;width:32px;height:32px;border-radius:50%;background:var(--alarm);color:#fff;font:800 16px/32px Arial,sans-serif;text-align:center}
.hp ol.steps b{display:block;font-size:17px}
.hp dl.sig{margin:0;display:block!important;grid-template-columns:none!important} .hp dl.sig dt,.hp dl.sig dd{width:auto!important;float:none!important} .hp dl.sig div{padding:9px 0;border-bottom:1px solid var(--line)} .hp dl.sig dt{font-weight:700} .hp dl.sig dd{margin:2px 0 0;color:var(--ink-2)}
.hp .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:10px}
.hp .stats div{border:1px solid var(--line-2);border-top:3px solid var(--alarm);background:var(--panel);padding:12px}
.hp .stats b{display:block;font-size:1.6rem;line-height:1.1} .hp .stats span{display:block;font-size:14px;margin-top:4px} .hp .stats small{display:block;font-size:12px;margin-top:6px;color:var(--ink-3)} .hp .stats small a{color:var(--ink-3)}
.hp .cases li{margin:0 0 12px} .hp .cases time{font-weight:700} .hp .cases small{color:var(--ink-3)}
.hp details{border-bottom:1px solid var(--line);padding:10px 0} .hp summary{font-weight:700;cursor:pointer;font-size:16.5px} .hp details p{margin:8px 0 0}
.hp .src{font-size:14px} .hp .src li{margin:4px 0}
.hp .disc{font-size:13px;color:var(--ink-3);margin-top:26px;border-top:1px solid var(--line);padding-top:12px}
.hp .draft{background:#FFF4D6;color:#5A4300;border:1px solid #E5C76B;padding:10px 12px;font-size:14px;margin:12px 0}
.hp .rel a{font-weight:700}
.hp .aka{font-size:15px;color:var(--ink-2);margin:-2px 0 8px}
.hp blockquote.script{margin:10px 0;padding:14px 16px;background:var(--panel);border:1px dashed var(--ink-3);font-family:var(--serif);font-size:1.1rem;line-height:1.5}
.hp .ex{display:grid;gap:12px;align-items:start} @media(min-width:640px){.hp .ex{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.hp .bubble{background:#E9E9EB;color:#111;border-radius:18px;padding:12px 14px;font:15px/1.4 -apple-system,Segoe UI,Arial,sans-serif;max-width:340px}
.hp .ex ul{margin:0;padding-left:18px} .hp .ex li{color:var(--alarm);font-weight:600}
.hp table.paid{width:100%;border-collapse:collapse;font-size:15px} .hp table.paid th,.hp table.paid td{text-align:left;vertical-align:top;padding:8px 6px;border-bottom:1px solid var(--line)} .hp table.paid td:first-child{font-weight:700;width:38%}
@media print{.mast,footer,.share,.draft,.skip{display:none!important}.hp .now{border-width:1px}}
</style>"""

def case_li(c):
    when, where, text, url, outlet, iid = c
    link = ''
    if iid and iid in inc:
        link = f' <a href="/i/{esc(iid)}/">The case file →</a>'
        if not url:
            url = inc[iid].get('source_url') or ''; outlet = inc[iid].get('source_label') or 'source'
    src = f' <small>({a(url, outlet)})</small>' if url else ''
    return f'<li><time>{esc(when)}</time> · <b>{esc(where)}</b>. {esc(text)}{src}{link}</li>'

# What to do if you already paid, by payment method (FTC, 'What To Do if You Were Scammed')
PAID = [
 ['Credit card', 'Call the card issuer right away and ask to reverse the charge.'],
 ['Debit card', 'Call your bank or credit union right away and ask for a refund.'],
 ['Bank transfer, including Zelle', 'Call your bank or credit union right away and ask them to reverse the transfer.'],
 ['Payment app (Venmo, Cash App, PayPal)', 'Report it in the app right away and ask them to reverse the payment.'],
 ['Wire transfer (Western Union, MoneyGram)', 'Call the wire company right away, tell them a scammer tricked you, and ask for a refund.'],
 ['Gift card', 'Call the company that issued the card, say a scammer has the number and PIN, and ask for a refund. Keep the card and receipt.'],
 ['Cryptocurrency', 'Contact the exchange or crypto-ATM operator right away, say the payment was fraud, and ask them to reverse it.'],
 ['Cash sent by mail', 'Call the US Postal Inspection Service at 1-877-876-2455; they may be able to stop the package. For FedEx or UPS, call them.'],
 ['A password', 'Change it, and anywhere else you used it, and turn on two-step login.'],
 ['Your Social Security number', 'Go to IdentityTheft.gov for a recovery plan.'],
]
REPO = meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')

built, approved_urls = [], []
for p in PAGES:
    url = f"{site}help/{p['slug']}/"
    draft = not p.get('approved')
    rev = p.get('reviewed') or ''
    steps = ''.join(f'<li><b>{esc(t)}</b>{esc(d)}</li>' for t, d in p['steps'])
    signs = ''.join(f'<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>' for t, d in p['signs'])
    types = ''.join(f'<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>' for t, d in p.get('types', []))
    prevent = ''.join(f'<li><b>{esc(x[0])}</b> {esc(x[1])}' + (f' <a href="{esc(x[2])}">{esc(x[3])} →</a>' if len(x) > 3 else '') + '</li>' for x in p.get('prevent', []))
    stats = ''.join(f'<div><b>{esc(n)}</b><span>{esc(t)}</span><small>{a(u, s)}</small></div>' for n, t, u, s in p['stats'])
    cases = ''.join(case_li(c) for c in p['cases'])
    report = ''.join(f'<li><b>{esc(w)}:</b> ' + (a(u, t) if u else esc(t)) + '</li>' for w, u, t in p['report'])
    faq = ''.join(f'<details{" open" if i < 2 else ""}><summary>{esc(q)}</summary><p>{esc(t)}</p></details>' for i, (q, t) in enumerate(p['faq']))
    srcs = ''.join(f'<li>{a(u, t)}</li>' for t, u in p['sources'])
    rel = ''.join(f'<li><a href="/help/{esc(s)}/">{esc(BY[s]["title"])}</a></li>' for s in p.get('related', []) if s in BY)
    byline = (f'Reviewed by {REVIEWER} on {fdate(rev)} · ' if (not draft and rev) else '') + f'Updated {fdate(p["updated"])}'
    share_text = p['h1'] + ' ' + url
    body = f"""{STYLE}<article class="hp">
{'<div class="draft"><b>Draft, not yet reviewed.</b> Hidden from search engines until every fact is checked and approved.</div>' if draft else ''}
<nav class="kick" aria-label="Breadcrumb"><a href="/help/" style="color:inherit">What to do</a> · {esc(p['kicker'])}</nav>
<h1>{esc(p['h1'])}</h1>
{f'<p class="aka">{esc(p["aka"])}</p>' if p.get('aka') else ''}
<div class="meta">{esc(byline)} · Every fact links to its source</div>
<section class="now" aria-label="What to do right now"><b class="k">If it's happening right now</b><p>{esc(p['now'])}</p></section>
<div class="share"><button type="button" data-copy="{esc(share_text)}">Copy link to send to family</button><button type="button" class="alt" onclick="window.print()">Print this page</button></div>
{f'<p>{esc(p["intro"])}</p>' if p.get('intro') else ''}
<h2>What to do, step by step</h2>
<ol class="steps">{steps}</ol>
<h2>Warning signs</h2>
<dl class="sig">{signs}</dl>
{(f'<h2>{esc(p["example"]["label"])}</h2><div class="ex"><div class="bubble">{esc(p["example"]["text"])}</div><ul>' + ''.join(f'<li>{esc(x)}</li>' for x in p['example']['flags']) + '</ul></div>') if p.get('example') else ''}
{f'<h2>The five most common scam texts</h2><dl class="sig">{types}</dl><p class="meta">From the FTC’s analysis of 2024 reports.</p>' if types else ''}
{f'<h2>Protect your family before it happens</h2><ul>{prevent}</ul>' if prevent else ''}
{(f'<h2>Send this to your family</h2><p>Copy it, fill in the blanks, and send it by text or read it to them on the phone.</p><blockquote class="script">{esc(p["script"])}</blockquote><div class="share"><button type="button" data-copy="{esc(p["script"])}">Copy the message</button></div>') if p.get('script') else ''}
<h2>If you already paid or shared something</h2>
<p>Speed matters most. What to do depends on how you paid, per the FTC:</p>
<table class="paid"><thead><tr><th>You paid or gave…</th><th>Do this now</th></tr></thead><tbody>{''.join(f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>' for k, v in PAID)}</tbody></table>
<p>Then report it (below). Recovery isn't guaranteed; reporting quickly gives you the best chance.</p>
<h2>How big this is</h2>
<div class="stats">{stats}</div>
<h2>Real cases</h2>
<p>From the Warning Shots index of AI incidents, each dated and sourced.</p>
<ul class="cases">{cases}</ul>
<h2>Where to report it</h2>
<ul>{report}</ul>
<h2>Questions people ask</h2>
{faq}
{f'<h2>Related</h2><ul class="rel">{rel}<li><a href="/">Today’s AI threats and what they mean for you →</a></li></ul>' if rel else ''}
<h2>Sources</h2>
<ul class="src">{srcs}</ul>
<p class="disc">Spot an error or out-of-date advice? <a href="{esc(REPO)}/issues">Tell us</a>; corrections are made and logged. Written with AI assistance from public sources; {'every fact checked and approved by ' + REVIEWER if not draft else 'awaiting fact-check and approval by ' + REVIEWER}. This page is general guidance, not legal or financial advice. In an emergency, call 911.</p>
</article>"""
    howto = {"@type": "HowTo", "name": p['h1'], "description": p['now'],
             "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d} for i, (t, d) in enumerate(p['steps'])]}
    art = {"@type": "Article", "headline": p['title'][:110], "description": p['desc'], "url": url, "mainEntityOfPage": url,
           "image": [site + 'assets/og.png'], "datePublished": p['updated'], "dateModified": p['updated'], "isAccessibleForFree": True, "inLanguage": "en",
           "about": p['kicker'], "citation": [u for _, u in p['sources']],
           "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site, "logo": {"@type": "ImageObject", "url": site + "assets/icon-512.png"}}}
    if not draft and rev:
        art["author"] = {"@type": "Person", "name": REVIEWER}
    else:
        art["author"] = {"@type": "Organization", "name": "Warning Shots", "url": site}
    wp = {"@type": "WebPage", "@id": url, "url": url, "name": p['title'], "description": p['desc'], "inLanguage": "en", "dateModified": p['updated'], "primaryImageOfPage": site + f"assets/help/{p['slug']}.png"}
    if not draft and rev:
        wp["reviewedBy"] = {"@type": "Person", "name": REVIEWER}; wp["lastReviewed"] = rev
    ld = json.dumps({"@context": "https://schema.org", "@graph": [wp, art, howto,
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in p['faq']]},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Warning Shots", "item": site},
            {"@type": "ListItem", "position": 2, "name": "What to do", "item": site + 'help/'}, {"@type": "ListItem", "position": 3, "name": p['kicker'], "item": url}]}]},
        ensure_ascii=False).replace('</', '<\\/')
    img = site + f"assets/help/{p['slug']}.png" if os.path.exists(f"assets/help/{p['slug']}.png") else site + 'assets/og.png'
    out = shell(title=p['title'], desc=p['desc'], url=url, img=img, body=body, jsonld=ld.replace(site + 'assets/og.png', img), kind='help')
    if draft:
        out = out.replace('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">', '<meta name="robots" content="noindex, nofollow">', 1)
        assert 'noindex' in out, 'draft page must be noindex'
    os.makedirs(f"help/{p['slug']}", exist_ok=True)
    open(f"help/{p['slug']}/index.html", 'w', encoding='utf-8').write(out)
    built.append((p, draft))
    if not draft: approved_urls.append(url)

# ---------- the hub
live = [p for p, d in built if not d]
items = ''.join(f'<li><a href="/help/{esc(p["slug"])}/"><b>{esc(p["h1"])}</b></a><br><span class="meta">{esc(p["desc"])}</span></li>' for p, d in built)
hub_body = f"""{STYLE}<article class="hp"><div class="kick">What to do</div><h1>When AI happens to you</h1>
<p>Plain, sourced steps for the moments that need them: a panicked call in a loved one's voice, a text that seems off, a video you're not sure is real. Each page puts what to do right now first.</p>
<ul class="cases">{items}</ul>
<p class="disc">Written with AI assistance from public sources and checked by a person before publishing. In an emergency, call 911.</p></article>"""
hub_url = site + 'help/'
ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "What to do when AI happens to you", "url": hub_url,
                 "publisher": {"@type": "Organization", "name": "Warning Shots", "url": site}}, ensure_ascii=False).replace('</', '<\\/')
hub = shell(title='What to do when AI happens to you', desc='Plain, sourced steps for AI voice-clone calls, AI scam texts and deepfakes: what to do right now, how to check, where to report it.', url=hub_url, img=site + 'assets/og.png', body=hub_body, jsonld=ld, kind='help')
if not live:
    hub = hub.replace('<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">', '<meta name="robots" content="noindex, nofollow">', 1)
os.makedirs('help', exist_ok=True)
open('help/index.html', 'w', encoding='utf-8').write(hub)

# ---------- sitemap: approved pages only
try: tu = json.load(open('data/tool_urls.json'))
except (OSError, ValueError): tu = []
tu = [u for u in tu if '/help/' not in u] + ([hub_url] if live else []) + approved_urls
json.dump(tu, open('data/tool_urls.json', 'w'))
json.dump(approved_urls, open('data/help_urls.json', 'w'))
print(f'help/: {len(built)} pages ({len(live)} approved, {len(built) - len(live)} drafts kept noindex)')
