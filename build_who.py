#!/usr/bin/env python3
"""who/<slug>/: one page per company, agency or person the index follows, gathering everything on the site about them:
Up & Down rows, forecasts, incidents on the record, Wire stories, posts on X and breakthroughs, newest first. Plus who/, the hub.
Also writes data/links.json (how stories, incidents and names connect), which the homepage and incident pages read.
Names and matching live in entities.py; a name gets a page only with at least entities.MIN_ITEMS items.
Run after build_archive.py (so the Wire archive is current), before build_pages.py (which lists these in the sitemap)."""
import json, os, collections
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pagekit import *
import entities as E

IDX, PAGES, NEWS2INC, A = E.index()
TODAY = meta['as_of'][:10]
TIERS = [(80, 'Critical'), (60, 'Severe'), (40, 'Serious'), (20, 'Moderate'), (0, 'Minor')]
def sev(r):
    H, R, Av, N, I = (int(r[k]) for k in 'HRANI')
    s = round(0.55 * 100 * (0.5 * H / 5 + 0.25 * R / 5 + 0.25 * I / 5) + 0.45 * 100 * (0.6 * Av / 4 + 0.4 * N / 5))
    return s, next(t for v, t in TIERS if s >= v)
KIND_ORDER = ['ud', 'call', 'inc', 'news', 'xp', 'bt']
try:
    NOTES = {k: v for k, v in json.load(open('research/who_notes.json', encoding='utf-8')).items() if not k.startswith('_')}
except (OSError, ValueError):
    NOTES = {}
import datetime as _dt
def spark(incs):
    """Every incident for this name as a spike: height = severity, red where the AI acted on its own in the real world."""
    if not incs: return ''
    W, H, b = 720, 90, 74
    t0 = _dt.date(2023, 1, 1).toordinal(); t1 = _dt.date.fromisoformat(TODAY).toordinal() + 20
    x = lambda d: 4 + (W - 40) * (_dt.date.fromisoformat(d[:10]).toordinal() - t0) / (t1 - t0)
    lines = ''.join(f'<line x1="{x(r["date"]):.1f}" x2="{x(r["date"]):.1f}" y1="{b}" y2="{b - (b - 6) * sev(r)[0] / 100:.1f}" stroke="{"#FF3300" if r.get("setting") == "wild" and int(r["A"]) >= 3 else "#7E8C9F"}" stroke-width="2.4" stroke-linecap="round"><title>{esc(r["title"])} ({sev(r)[0]}/100)</title></line>' for r in incs)
    yrs = ''.join(f'<text x="{x(f"{y}-01-01") + 2:.1f}" y="{H - 2}" font-size="11" fill="#7E8C9F">{y}</text>' for y in range(2023, int(TODAY[:4]) + 1))
    return (f'<figure class="wspark" style="margin:18px 0 8px;background:#0A111E;padding:10px 12px 6px;border-top:3px solid #FF3300"><svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{len(incs)} incidents over time; red where the AI acted on its own">'
            f'<line x1="4" x2="{W - 36}" y1="{b}" y2="{b}" stroke="#3A4D6B"/>{lines}{yrs}<text x="{W - 32}" y="12" font-size="10" font-weight="700" fill="#F4F3EF">NOW</text></svg>'
            '<figcaption style="color:#A8B3C2;font-size:12px;margin-top:4px">Every incident on the record, by date. Taller is worse; <b style="color:#FF3300">red</b>: the AI acted on its own in the real world.</figcaption></figure>')
NEWJS = """<script>(function(){try{var k='ws-who-'+document.body.dataset.who,p=+localStorage.getItem(k)||0;if(p){var n=0;document.querySelectorAll('[data-d]').forEach(function(e){if(Date.parse(e.dataset.d+'T23:59:00Z')>p){n++;var b=document.createElement('span');b.className='st';b.style.cssText='background:#FF3300;color:#fff;border-color:#FF3300;margin-right:6px';b.textContent='New';e.insertBefore(b,e.firstChild);}});var m=document.getElementById('who-new');if(m)m.textContent=n?n+' new since you last looked':'Nothing new since you last looked';}localStorage.setItem(k,String(Date.now()));}catch(e){}})();</script>"""

def page_html(slug):
    s, name, kind, rx, desc = next(e for e in E.RX if e[0] == slug)
    d = IDX[slug]
    incs = sorted(d['inc'], key=lambda r: r.get('disclosed') or r['date'], reverse=True)
    news = sorted(d['news'], key=lambda n: n.get('published') or '', reverse=True)
    worst = max(incs, key=lambda r: sev(r)[0]) if incs else None
    parts = []
    stats = [(len(incs), 'incidents on the record'), (len(news), 'stories on the Wire'), (len(d['call']), 'forecasts')]
    parts.append('<div class="stats">' + ''.join(f'<div><b>{n}</b><span>{esc(l)}</span></div>' for n, l in stats if n) +
                 (f'<div><b>{sev(worst)[0]}/100</b><span>worst incident on the record</span><small>{a("/i/" + worst["id"] + "/", worst["title"])}</small></div>' if worst else '') + '</div>')
    nts = sorted(NOTES.get(slug, []), key=lambda x: x['date'], reverse=True)
    if nts:
        def srcs(ids): return ' '.join(f'<a href="{esc(A["news"][i]["url"])}" target="_blank" rel="noopener noreferrer">{esc(A["news"][i].get("outlet") or "source")}</a>' for i in ids if i in A['news'])
        parts.insert(0, f'<section class="box" style="border-left-color:var(--alarm)"><b class="k">This week · {esc(fdate(nts[0]["date"]))}</b><p style="font-size:1.08rem">{esc(nts[0]["text"])}</p><p class="meta" style="font-size:13px">Sources: {srcs(nts[0].get("sources", []))}</p></section>')
        if len(nts) > 1:
            parts.append('<h2>Earlier weeks</h2><ul class="rec">' + ''.join(f'<li><time>{esc(x["date"])}</time> {esc(x["text"])} <small>{srcs(x.get("sources", []))}</small></li>' for x in nts[1:]) + '</ul>')
    parts.append(spark(incs))
    parts.append('<p class="meta" id="who-new"></p>')
    if d['ud']:
        parts.append('<h2>Up &amp; Down</h2><ul class="rec">' + ''.join(
            f'<li data-d="{esc(u["date"])}"><time>{esc(u["date"])}</time> <span class="st{" yes" if u["dir"] == "up" else ""}">{"▲ Up" if u["dir"] == "up" else "▼ Down"}</span> {esc(u["line"])}<br><small><b>Why it matters:</b> {esc(u["why"])}</small></li>'
            for u in sorted(d['ud'], key=lambda u: u['date'], reverse=True)) + '</ul><p class="meta"><a href="/up-and-down/">The full Up &amp; Down board</a></p>')
    if d['call']:
        def odds(c):
            r = c.get('resolution')
            if r: return f'graded {esc(fdate(r["date"]))}: {esc(r["outcome"])}'
            p = float(c['odds']); w = 'very likely' if p >= .85 else 'likely' if p >= .6 else 'could go either way' if p > .4 else 'unlikely' if p > .15 else 'very unlikely'
            return f'resolves {esc(fdate(c["resolve_by"]))} · our odds: {w}'
        parts.append('<h2>Forecasts</h2><ul class="rec">' + ''.join(f'<li><a href="/forecast/{esc(c["id"])}/"><b>{esc(c.get("plain") or c["question"])}</b></a><br><small>{odds(c)}</small></li>' for c in d['call']) + '</ul>')
    if incs:
        parts.append('<h2>Incidents on the record</h2><ul class="rec">' + ''.join(
            f'<li data-d="{esc((r.get("disclosed") or r.get("date") or "")[:10])}"><time>{esc((r.get("date") or "")[:10])}</time> <span class="st">{sev(r)[0]}/100 {sev(r)[1]}</span> <a href="/i/{esc(r["id"])}/"><b>{esc(r["title"])}</b></a><br><small>{esc(r.get("category_label") or "")} · {"in the real world" if r.get("setting") == "wild" else "in a lab or test"}</small></li>'
            for r in incs[:40]) + '</ul>')
    if news:
        parts.append('<h2>On the Wire</h2><ul class="rec">' + ''.join(
            f'<li data-d="{esc((n.get("published") or "")[:10])}"><time>{esc((n.get("published") or "")[:10])}</time> <a href="{esc(n["url"])}" target="_blank" rel="noopener noreferrer"><b>{esc(n.get("tag") or n["title"])}</b></a> <small>{esc(n.get("outlet") or "")}</small>'
            + (f' · <a href="/i/{esc(NEWS2INC[n["id"]])}/">on the record</a>' if n['id'] in NEWS2INC else '') + (f'<br>{esc(n["summary"])}' if n.get('summary') else '') + '</li>'
            for n in news[:30]) + '</ul>')
    if d['xp']:
        parts.append('<h2>On X</h2><ul class="rec">' + ''.join(f'<li data-d="{esc(x["posted"][:10])}"><time>{esc(x["posted"][:10])}</time> <a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer"><b>{esc(x["author"])}</b></a>: {esc(x["what"])}</li>' for x in sorted(d['xp'], key=lambda x: x['posted'], reverse=True)) + '</ul>')
    if d['bt']:
        parts.append('<h2>Breakthroughs</h2><ul class="rec">' + ''.join(f'<li><time>{esc(b["date"])}</time> <b>{esc(b["payoff"])}</b><br><small>{esc(b["means"])}</small></li>' for b in d['bt']) + '</ul>')
    co = collections.Counter(o for k in ('news', 'inc') for x in d[k] for o in E.who(E.text_of(k, x)) if o != slug and PAGES.get(o))
    if co:
        parts.append('<p class="share">Often in the same stories: ' + ' · '.join(f'<a href="/who/{o}/">{esc(E.NAME[o])}</a>' for o, _ in co.most_common(6)) + '</p>')
    body = f"""<article class="pk" id="who-page" data-who="{slug}"><nav class="kick" aria-label="Breadcrumb"><a href="/who/">Who's who</a> · {esc(kind)}</nav>
<h1>{esc(name)}</h1><p class="aka">{esc(desc)}</p>
<div class="meta">Everything Warning Shots has on {esc(name)}, newest first: incidents scored on the record, forecasts, the week's power moves and every Wire story, each linked to its source. Updated on every refresh.</div>
{''.join(parts)}
{capture(f'Follow {name}: one email when something moves', 'who-' + slug)}
{footer_note(False)}</article>{NEWJS.replace('document.body.dataset.who', "document.getElementById('who-page').dataset.who")}"""
    n_all = sum(len(v) for v in d.values())
    dsc = f'{name} and AI: {len(incs)} incidents on the record' + (f', worst {sev(worst)[0]}/100' if worst else '') + f', {len(news)} news stories, {len(d["call"])} forecasts. Sourced and updated three times a day by Warning Shots.'
    return body, dsc, n_all

urls, hub = [], []
for s, name, kind, rx, desc in E.RX:
    if not PAGES.get(s): continue
    body, dsc, n_all = page_html(s)
    url = SITE + f'who/{s}/'
    write(f'who/{s}/index.html', url=url, title=f'{name} and AI: incidents, forecasts and news, tracked', desc=dsc, body=body, draft=False,
          crumbs=[("Who's who", '/who/'), (name, '')], graph=[{"@type": "ProfilePage", "url": url, "name": name, "mainEntity": {"@type": "Person" if kind == 'Person' else "Organization", "name": name, "description": desc}}])
    urls.append(url); hub.append((n_all, s, name, kind, desc))
hub.sort(reverse=True)
hb = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Who's who in AI's dangers and breakthroughs</h1>
<p>Every company, agency and person we follow, with everything the site has on them: incidents on the record, forecasts, the week's power moves, and every story on the Wire.</p>
<ul class="rec">{''.join(f'<li><a href="/who/{s}/"><b>{esc(n)}</b></a> <span class="st">{esc(k)}</span> <small>{c} items</small><br><small>{esc(d)}</small></li>' for c, s, n, k, d in hub)}</ul>
{footer_note(False)}</article>"""
write('who/index.html', url=SITE + 'who/', title="Who's who in AI: every company and person Warning Shots follows", desc=f'{len(hub)} AI labs, companies, agencies and people, each with their incidents, forecasts and news on one page.', body=hb, draft=not hub,
      crumbs=[("Who's who", '')], graph=[webpage(SITE + 'who/', "Who's who", 'Companies and people in AI, tracked', TODAY, False, '')])
register('who/', [SITE + 'who/'] + urls)
# links for the homepage and incident pages
links = {'news2inc': NEWS2INC, 'who': {s: E.NAME[s] for s in PAGES if PAGES[s]}}
json.dump(links, open('data/links.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(f'who/: {len(urls)} pages')
