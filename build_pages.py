#!/usr/bin/env python3
"""Per-dispatch pages: i/<id>/, c/<id>/ and m/<id>/ each carry their own title, description and share card,
then send the browser to the main page's deep link. Also writes sitemap.xml. Run after build_site.py and make_cards.mjs."""
import json, os, html, datetime as dt, shutil
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
meta = json.load(open('data/meta.json')); site = meta['site_url']
build = json.load(open('assets/build.json'))['build']

def sev(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    s = round(0.55 * harm + 0.45 * sig)
    tier = 'Critical' if s >= 80 else 'Severe' if s >= 60 else 'Serious' if s >= 40 else 'Moderate' if s >= 20 else 'Minor'
    return s, tier

TPL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Warning Shots</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Warning Shots"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{img}">
<link rel="icon" href="{site}assets/favicon.svg" type="image/svg+xml">
<style>body{{margin:0;background:#0A111E;color:#F4F3EF;font-family:system-ui,sans-serif;padding:40px 20px;max-width:760px;margin-inline:auto;line-height:1.5}}a{{color:#F4F3EF}}h1{{font-size:1.6rem;line-height:1.2}}p{{color:#A8B3C2}}.k{{font-size:13px;color:#7E8C9F;letter-spacing:.06em;text-transform:uppercase}}img{{max-width:100%;height:auto;border:1px solid #2A364B;margin-top:16px}}</style>
<script>location.replace({target!r});</script>
</head><body><div class="k">{kicker}</div><h1>{title}</h1><p>{desc}</p><p><a href="{target}">Open on Warning Shots</a> · <a href="{site}">warningshots.ai</a></p><img src="{img}" alt="" width="1200" height="630"></body></html>
"""

def page(kind, slug, title, desc, kicker, hash_route):
    d = os.path.join(kind, slug); os.makedirs(d, exist_ok=True)
    url = f'{site}{kind}/{slug}/'
    img = f'{site}cards/{kind}-{slug}.jpg' if os.path.exists(f'cards/{kind}-{slug}.jpg') else f'{site}assets/og.png?v={build}'
    target = f'{site}#{hash_route}'
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(TPL.format(title=html.escape(title), desc=html.escape(desc), url=url, img=img, site=site, target=target, kicker=html.escape(kicker)))
    return url

urls = [site]
inc = json.load(open('data/incidents.json'))
for r in inc:
    s, tier = sev(r)
    desc = (r.get('summary') or '').split('. ')[0].rstrip('.') + f'. {tier} ({s}/100). ' + ('Real-world incident' if r.get('setting') == 'wild' else 'Lab or test finding') + ', ' + r['date'] + '. Scored and sourced by Warning Shots.'
    urls.append(page('i', r['id'], r['title'], desc[:300], f'Incident · {r["date"]}', 'i=' + r['id']))
for f in json.load(open('data/fixes.json')):
    cur = next((c for c in f['chain'] if c['stage'] == 'current'), {})
    urls.append(page('c', f['incident_id'], f['name'], ('Did they fix it? ' + (f.get('one_liner') or cur.get('note') or ''))[:300], 'Did they fix it?', 'c=' + f['incident_id']))
for c in json.load(open('data/capabilities.json')):
    urls.append(page('m', c['id'], c['title'], ((c.get('what') or '') + ' Graded from demonstration to real consequences by Warning Shots.')[:300], f'What AI can now do · {c["date"]}', 'm=' + c['id']))

# prune pages for records that no longer exist
keep = {u.replace(site, '') for u in urls}
for kind in ('i', 'c', 'm'):
    if os.path.isdir(kind):
        for slug in os.listdir(kind):
            if f'{kind}/{slug}/' not in keep:
                shutil.rmtree(os.path.join(kind, slug), ignore_errors=True)

now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    sm.append(f'<url><loc>{html.escape(u)}</loc><lastmod>{now}</lastmod></url>')
sm.append('</urlset>')
open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(sm))
open('robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {site}sitemap.xml\n')
print('pages', len(urls) - 1, 'sitemap written')
