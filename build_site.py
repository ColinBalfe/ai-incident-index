#!/usr/bin/env python3
"""Fill index.template.html -> index.html using data/meta.json and data/incidents.json (for OG tags), and stamp a build id.
Run from the site/ directory after updating data/. Then run make_og.py to refresh the share image."""
import json, time, datetime as dt, os, sys
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
meta = json.load(open('data/meta.json'))
inc = json.load(open('data/incidents.json'))

def sev(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    return round(0.55 * harm + 0.45 * sig)

as_of = dt.date.fromisoformat(meta['as_of'][:10])
from zoneinfo import ZoneInfo
_t = dt.datetime.fromisoformat(meta['as_of']).astimezone(ZoneInfo('America/New_York'))
et = _t.strftime('%b %-d, %-I:%M %p ET')
yr = dt.timedelta(days=365)
def inwin(r, a, b): d = dt.date.fromisoformat(r['date']); return a < d <= b
last12 = [r for r in inc if inwin(r, as_of - yr, as_of)]
prior12 = [r for r in inc if inwin(r, as_of - 2 * yr, as_of - yr)]
s12 = sum(sev(r) >= 60 for r in last12); p12 = sum(sev(r) >= 60 for r in prior12)
wild_recent = [r for r in last12 if r['setting'] == 'wild']
share = round(100 * sum(r['A'] >= 3 for r in wild_recent) / max(1, len(wild_recent)))
n = len(inc)
title = meta.get('site_name', 'Warning Shots')
try:
    _sir = next((x for x in json.load(open('data/news.json', encoding='utf-8')) if x.get('wall') == 'siren' and x.get('tag')), None)
except (OSError, ValueError):
    _sir = None
og_title = (_sir['tag'] + ' | ' + title) if _sir else f"AI has started breaking in on its own — {title}: see what’s coming and know what it means"
og_desc = ((_sir.get("summary", "") + " ") if _sir else "") + f"Severe AI incidents went from {p12} to {s12} in a year. In {share}% of this year's real-world cases the AI itself did the acting. {n} incidents since 2023, scored 0–100 and sourced. Live tracking of {meta.get('live_name', 'the incident unfolding now')}, 20 dated forecasts, and what officials have said. Updated {et}."
build = time.strftime('%Y%m%d%H%M', time.gmtime())
site_url = meta['site_url']
jsonld = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "NewsMediaOrganization", "@id": site_url + "#org", "name": title, "url": site_url, "slogan": "See what’s coming and know what it means.",
     "logo": {"@type": "ImageObject", "url": site_url + "assets/icon-512.png", "width": 512, "height": 512}},
    {"@type": "WebSite", "@id": site_url + "#site", "url": site_url, "name": title, "description": og_desc, "inLanguage": "en", "publisher": {"@id": site_url + "#org"}, "dateModified": meta['as_of']},
    {"@type": "Dataset", "name": "The AI Incident Index", "url": site_url + "index/#all", "description": f"{n} AI incidents since 2023, each scored 0–100 on harm, reach, irreversibility, autonomy and novelty, with sources. Open data from {title}.",
     "creator": {"@id": site_url + "#org"}, "dateModified": meta['as_of'], "isAccessibleForFree": True,
     "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": site_url + "data/incidents.json"}, {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": site_url + "data/incidents.csv"}]},
]}, ensure_ascii=False).replace('</', '<\\/')
tpl = open('index.template.html', encoding='utf-8').read()
out = (tpl.replace('{{OG_TITLE}}', og_title.replace('"', '&quot;')).replace('{{OG_DESC}}', og_desc.replace('"', '&quot;'))
          .replace('{{JSONLD}}', jsonld).replace('{{SITE_URL}}', meta['site_url']).replace('{{REPO_URL}}', meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')).replace('{{BUILD}}', build))
from analytics import tag as _analytics_tag   # visitor counter (Cloudflare Web Analytics); empty until analytics.json has a token
_an = _analytics_tag()
if _an:
    out = out.replace('</body>', _an + '\n</body>', 1)
open('index.html', 'w', encoding='utf-8').write(out.replace('{{PAGE}}', 'front'))
# ---- the Record (/index/): the same template with the headline page hidden and the full index shown
rec = out.replace('{{PAGE}}', 'record')
rec = rec.replace('<title>Warning Shots: live AI incidents, threats and breakthroughs</title>', f'<title>The Record: every AI incident since 2023, scored and sourced | {title}</title>', 1)
rec = rec.replace(f'<link rel="canonical" href="{site_url}">', f'<link rel="canonical" href="{site_url}index/">', 1)
rec = rec.replace(f'<meta property="og:url" content="{site_url}">', f'<meta property="og:url" content="{site_url}index/">', 1)
rec = rec.replace(og_title.replace('"', '&quot;'), (f"AI has started breaking in on its own — the Record, {title}").replace('"', '&quot;'))
rec = rec.replace('<a class="skip" href="#wire">Skip to the Wire</a>', '<a class="skip" href="#record">Skip to the Record</a>', 1)
os.makedirs('index', exist_ok=True)
open('index/index.html', 'w', encoding='utf-8').write(rec)
# ---- data/incidents.csv: the same rows as data/incidents.json, for spreadsheets
import csv as _csv
_rows = json.load(open('data/incidents.json', encoding='utf-8'))
_cols = ['id', 'date', 'date_precision', 'disclosed', 'title', 'actors', 'category', 'setting', 'H', 'R', 'A', 'N', 'I', 'harm', 'summary', 'source_url', 'source2_url', 'confidence']
with open('data/incidents.csv', 'w', newline='', encoding='utf-8') as _f:
    _w = _csv.DictWriter(_f, fieldnames=_cols, extrasaction='ignore'); _w.writeheader(); [_w.writerow(r) for r in _rows]

# ---- data/bundle.json: every data file in one request (the page preloads it; the individual files stay for scripts and the update check)
FILES = ['incidents', 'forecasts', 'pipeline', 'drivers', 'context', 'catalysts', 'horizon', 'deepdives', 'victims', 'timeline', 'implications', 'signals', 'live', 'watch', 'meta',
         'quotes', 'brief', 'news', 'capabilities', 'fixes', 'tns', 'calls']
bundle = {}
for f in FILES:
    try:
        bundle[f] = json.load(open(f'data/{f}.json', encoding='utf-8'))
    except (OSError, ValueError):
        pass
json.dump(bundle, open('data/bundle.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ---- RSS: the Wire and the daily brief
import html as _html, email.utils as _eu
def _rfc(iso):
    try:
        d = dt.datetime.fromisoformat(iso.replace('Z', '+00:00'))
        return _eu.format_datetime(d)
    except ValueError:
        return _eu.format_datetime(dt.datetime.now(dt.timezone.utc))
site = meta['site_url']
items = []
try:
    brief = json.load(open('data/brief.json'))
    for i, it in enumerate(brief.get('items', [])):
        items.append(dict(title='Since the last refresh: ' + it['text'][:90].rstrip() + ('…' if len(it['text']) > 90 else ''), link=site + '#brief', guid=site + '#brief-' + meta['as_of'] + '-' + str(i), date=_rfc(meta['as_of']), desc=it['text'] + (' Source: ' + it['url'] if it.get('url') else '')))
except (OSError, ValueError):
    pass
try:
    for n in json.load(open('data/news.json'))[:40]:
        items.append(dict(title=n['title'], link=n['url'], guid=n['url'], date=_rfc(n['published']), desc=(n.get('summary') or '') + ' (' + n.get('outlet', '') + ')'))
except (OSError, ValueError):
    pass
rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', f'<title>{_html.escape(title)}: the Wire and the daily brief</title>', f'<link>{site}</link>',
       '<description>See what’s coming and know what it means. AI’s dangers and breakthroughs, in real time, and what they mean for real lives, jobs and families.</description>', f'<lastBuildDate>{_rfc(meta["as_of"])}</lastBuildDate>']
for it in items:
    rss.append(f'<item><title>{_html.escape(it["title"])}</title><link>{_html.escape(it["link"])}</link><guid isPermaLink="false">{_html.escape(it["guid"])}</guid><pubDate>{it["date"]}</pubDate><description>{_html.escape(it["desc"])}</description></item>')
rss.append('</channel></rss>')
open('feed.xml', 'w', encoding='utf-8').write('\n'.join(rss))

# ---- RSS: dispatches (new incidents, cases that moved, milestones), each linking to its own page
disp = []
def _sev_tier(r):
    s = sev(r); return s, ('Critical' if s >= 80 else 'Severe' if s >= 60 else 'Serious' if s >= 40 else 'Moderate' if s >= 20 else 'Minor')
for r in sorted(inc, key=lambda r: (r.get('disclosed') or r['date']), reverse=True)[:40]:
    s_, t_ = _sev_tier(r)
    disp.append(dict(title=f"{r['title']} ({s_}/100 {t_})", link=f"{site}i/{r['id']}/", guid=f"{site}i/{r['id']}/", date=_rfc((r.get('disclosed') or r['date']) + 'T12:00:00+00:00'), desc=r.get('summary') or ''))
try:
    for f in json.load(open('data/fixes.json')):
        cur = next((c for c in f['chain'] if c['stage'] == 'current'), {})
        disp.append(dict(title=f"Did they fix it? {f['name']}: {cur.get('status', '')}", link=f"{site}c/{f['incident_id']}/", guid=f"{site}c/{f['incident_id']}/#{cur.get('date', '')}", date=_rfc((cur.get('date') or meta['as_of'][:10]) + 'T12:00:00+00:00'), desc=f.get('one_liner') or cur.get('note') or ''))
except (OSError, ValueError):
    pass
try:
    for c in sorted(json.load(open('data/capabilities.json')), key=lambda c: c['date'], reverse=True)[:20]:
        disp.append(dict(title=f"What AI can now do: {c['title']}", link=f"{site}m/{c['id']}/", guid=f"{site}m/{c['id']}/", date=_rfc(c['date'] + 'T12:00:00+00:00'), desc=c.get('what') or ''))
except (OSError, ValueError):
    pass
disp.sort(key=lambda it: _eu.parsedate_to_datetime(it['date']), reverse=True)
rss2 = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', f'<title>{_html.escape(title)}: dispatches</title>', f'<link>{site}</link>',
        '<description>Every incident, case and capability milestone on the index as it lands, each on its own page with sources.</description>', f'<lastBuildDate>{_rfc(meta["as_of"])}</lastBuildDate>']
for it in disp[:80]:
    rss2.append(f'<item><title>{_html.escape(it["title"])}</title><link>{_html.escape(it["link"])}</link><guid isPermaLink="false">{_html.escape(it["guid"])}</guid><pubDate>{it["date"]}</pubDate><description>{_html.escape(it["desc"])}</description></item>')
rss2.append('</channel></rss>')
open('feed-dispatches.xml', 'w', encoding='utf-8').write('\n'.join(rss2))
json.dump(dict(build=build, og_title=og_title, og_desc=og_desc, severe_last12=s12, severe_prior12=p12, agentic_share=share, n=n), open('assets/build.json', 'w'))
print('built', build, '|', og_title, '|', og_desc)
