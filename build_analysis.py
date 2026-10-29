#!/usr/bin/env python3
"""Analysis: Warning Shots' own investigations (research/analysis.json), one permanent page each at /analysis/<slug>/,
plus the /analysis/ hub. Original work only: the Wire links out; these pages are ours, so they get their own URLs, the
share card, Article JSON-LD and a place in the sitemap and the news sitemap while fresh. No 'Reviewed by' byline: the
author is Warning Shots unless Colin has read the piece."""
import json
from pagekit import write, frame, footer_note, article, webpage, register, esc, fdate, a, SITE

D = json.load(open('research/analysis.json', encoding='utf-8'))
pieces = sorted(D['pieces'], key=lambda p: p['date'], reverse=True)
urls = []

for p in pieces:
    url = f'{SITE}analysis/{p["slug"]}/'; urls.append(url)
    img = SITE + p['img'].lstrip('/') if p.get('img') else None
    top, by = frame(draft=False, rev='', updated=p['updated'], crumbs=[('Analysis', '/analysis/'), (p['short'], '')], family_label='Analysis')
    rows = []
    for r in p['rows']:
        h, outlet, hu = r['headline']
        src = ' · '.join(a(u, t) for t, u in r['sources'])
        rows.append(f'<section class="an-row"><h3>{esc(r["name"])} <small>{esc(r["size"])}</small></h3>'
                    f'<p class="an-hl"><span class="k">What the headline said</span> “{esc(h)}” <small>{a(hu, outlet)}</small></p>'
                    f'<p><span class="verdict">{esc(r["verdict"])}</span></p><p>{esc(r["said"])}</p><p class="src">Sources: {src}</p></section>')
    table = ('<div class="tw"><table><thead><tr><th>Employer</th><th>Cut</th><th>Our verdict</th></tr></thead><tbody>'
             + ''.join(f'<tr><td><b>{esc(r["name"])}</b></td><td>{esc(r["size"])}</td><td><span class="st{" yes" if r["verdict"] in ("Yes", "Partly") else ""}">{esc(r["verdict"])}</span></td></tr>' for r in p['rows'])
             + '</tbody></table></div>')
    corr = ''.join(f'<li><time>{fdate(c["date"])}</time> {esc(c["text"])}</li>' for c in p.get('corrections') or [])
    links = ''.join(f'<li><a href="{esc(u)}">{esc(t)} →</a></li>' for u, t in p.get('links') or [])
    share = (f'<div class="share"><button type="button" data-copy="{esc(url)}">Copy link</button>'
             f'<a class="alt" href="https://twitter.com/intent/tweet?text={esc(p["short"])}&amp;url={esc(url)}&amp;via=WarningShotsAI" target="_blank" rel="noopener noreferrer">Post on X</a>'
             + (f'<a class="alt" href="{esc(p["img"])}" download>Card image</a>' if p.get('img') else '') + '</div>')
    body = (f'<article class="pk an">{top}<p class="kick">{esc(p["kicker"])}</p><h1>{esc(p["title"])}</h1>'
            f'<p class="meta">By Warning Shots · Published {fdate(p["date"])} · {by}</p>'
            f'<p class="aka">{esc(p["dek"])}</p>'
            f'<div class="box"><b class="k">What we found</b><p>{esc(p["finding"])}</p></div>{table}{share}'
            f'<h2>Employer by employer</h2>{"".join(rows)}'
            f'<h2>How we checked</h2><p>{esc(p["method"])}</p>'
            + (f'<h2>Corrections</h2><ul class="rec">{corr}</ul>' if corr else '')
            + (f'<h2>Related</h2><ul class="rec">{links}</ul>' if links else '')
            + footer_note(False) + '</article>'
            + '<style>.an .an-row{border-top:1px solid var(--line);padding:6px 0 4px}.an .an-row h3{font-family:var(--serif);font-size:1.35rem;margin:14px 0 6px}.an .an-row h3 small{font:400 14px var(--sans);color:var(--ink-3);margin-left:6px}.an .an-hl{font-family:var(--serif);font-style:italic;color:var(--ink-2)}.an .an-hl .k{display:block;font:800 11px/1.4 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;font-style:normal;color:var(--ink-3)}.an .share a{font:700 14px/1 var(--sans);padding:10px 14px;border:1px solid var(--ink);color:var(--ink);text-decoration:none}</style>')
    cites = [r['headline'][2] for r in p['rows']] + [u for r in p['rows'] for _, u in r['sources']]
    write(f'analysis/{p["slug"]}/index.html', url=url, title=p['title'], desc=p['dek'][:300], body=body,
          graph=[article(url, p['title'], p['dek'][:300], p['updated'], False, '', 'Analysis', cites, img)], draft=False, img=img,
          crumbs=[('Analysis', '/analysis/'), (p['short'], '')])

hub = f'{SITE}analysis/'; urls.append(hub)
top, by = frame(draft=False, rev='', updated=pieces[0]['updated'] if pieces else '', crumbs=[('Analysis', '')], family_label='Analysis')
items = ''.join(f'<li><a href="/analysis/{esc(p["slug"])}/">{esc(p["title"])}</a><span class="meta">{fdate(p["date"])} · {esc(p["kicker"])}</span></li>' for p in pieces)
desc = "Warning Shots' own investigations: original, checkable analysis of what AI is really doing, with every source linked."
write('analysis/index.html', url=hub, title='Analysis: Warning Shots investigations', desc=desc,
      body=f'<div class="pk">{top}<h1>Analysis</h1><p class="aka">{esc(desc)} One a week.</p><ul class="list">{items}</ul>{footer_note(False)}</div>',
      graph=[webpage(hub, 'Analysis: Warning Shots investigations', desc, pieces[0]['updated'] if pieces else '', False, '')], draft=False, crumbs=[('Analysis', '')])
register('analysis/', urls)
json.dump([{'slug': p['slug'], 'title': p['title'], 'short': p['short'], 'date': p['date']} for p in pieces], open('data/analysis.json', 'w'))
print(f'analysis: {len(pieces)} piece(s)')
