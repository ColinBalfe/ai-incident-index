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
_lead = (meta.get('serial') or {}).get('lead') or {}
if _lead.get('tag') and (meta.get('serial') or {}).get('state') != 'closed':   # the running story has taken the lead slot: the share title follows it
    _sir = {'tag': _lead['tag'], 'summary': _lead.get('standfirst', '')}
og_title = (_sir['tag'] + ' | ' + title) if _sir else f"AI has started breaking in on its own — {title}: see what’s coming, know what it means"
og_desc = ((_sir.get("summary", "") + " ") if _sir else "") + f"Severe AI incidents went from {p12} to {s12} in a year. In {share}% of this year's real-world cases the AI itself did the acting. {n} incidents since 2023, scored 0–100 and sourced. Live tracking of {meta.get('live_name', 'the incident unfolding now')}, 20 dated forecasts, and what officials have said. Updated {et}."
build = time.strftime('%Y%m%d%H%M', time.gmtime())
site_url = meta['site_url']
jsonld = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "NewsMediaOrganization", "@id": site_url + "#org", "name": title, "url": site_url, "slogan": "See what’s coming. Know what it means.",
     "logo": {"@type": "ImageObject", "url": site_url + "assets/icon-512.png", "width": 512, "height": 512}},
    {"@type": "WebSite", "@id": site_url + "#site", "url": site_url, "name": title, "description": og_desc, "inLanguage": "en", "publisher": {"@id": site_url + "#org"}, "dateModified": meta['as_of']},
    {"@type": "Dataset", "name": "The AI Incident Index", "url": site_url + "index/#all", "description": f"{n} AI incidents since 2023, each scored 0–100 on harm, reach, irreversibility, autonomy and novelty, with sources. Open data from {title}.",
     "creator": {"@id": site_url + "#org"}, "dateModified": meta['as_of'], "isAccessibleForFree": True, "temporalCoverage": "2023-01-01/..", "keywords": ["AI incidents", "AI safety", "AI security", "AI risk", "incident database", "agentic AI", "deepfakes", "cybersecurity"], "variableMeasured": ["harm", "reach", "autonomy", "novelty", "irreversibility", "severity 0-100"], "measurementTechnique": "Each incident rated on five factors by a published rubric; severity = 0.55 x harm score + 0.45 x signal score.",
     "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": site_url + "data/incidents.json"}, {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": site_url + "data/incidents.csv"}]},
]}, ensure_ascii=False).replace('</', '<\\/')
tpl = open('index.template.html', encoding='utf-8').read()
# Readable versions of the charts, so search engines, screen readers and touch users get the numbers without hovering
import html as _h
_AUT = ['A person misused it', 'People relied on it', 'It took a bounded action', 'It ran multi-step operations', 'It worked against its operator']
_top = sorted(inc, key=lambda r: -sev(r))[:10]
TOP_TABLE = '<table><tr><th>Score</th><th>Incident</th><th>Date</th></tr>' + ''.join(f'<tr><td>{sev(r)}</td><td><a href="/i/{_h.escape(r["id"])}/">{_h.escape(r["title"])}</a></td><td>{_h.escape(r["date"])}</td></tr>' for r in _top) + '</table>'
_q = {}
for r in inc:
    y, m = int(r['date'][:4]), int(r['date'][5:7]) if len(r['date']) >= 7 else 1
    k = f'{y} Q{(m - 1) // 3 + 1}'; _q.setdefault(k, [0] * 5); _q[k][min(4, int(r['A']))] += 1
QUARTERS_TABLE = '<table><tr><th>Quarter</th><th>Incidents</th>' + ''.join(f'<th>{a}</th>' for a in _AUT) + '</tr>' + ''.join(f'<tr><td>{k}</td><td>{sum(v)}</td>' + ''.join(f'<td>{x}</td>' for x in v) + '</tr>' for k, v in sorted(_q.items())) + '</table>'
tpl = tpl.replace('{{TOP_TABLE}}', TOP_TABLE).replace('{{QUARTERS_TABLE}}', QUARTERS_TABLE)
out = (tpl.replace('{{OG_TITLE}}', og_title.replace('"', '&quot;')).replace('{{OG_DESC}}', og_desc.replace('"', '&quot;'))
          .replace('{{JSONLD}}', jsonld).replace('{{SITE_URL}}', meta['site_url']).replace('{{REPO_URL}}', meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')).replace('{{BUILD}}', build).replace('{{SEV_PRIOR}}', str(p12)).replace('{{SEV_LAST}}', str(s12)).replace('{{AGENTIC}}', str(share)))
from analytics import tag as _analytics_tag   # visitor counter (Cloudflare Web Analytics); empty until analytics.json has a token
_an = _analytics_tag()
if _an:
    out = out.replace('</body>', _an + '\n</body>', 1)
try:   # search-engine ownership tags (Google Search Console, Bing Webmaster Tools); site_verify.json {"google": "...", "bing": "..."}
    _sv = json.load(open('site_verify.json', encoding='utf-8'))
except (OSError, ValueError):
    _sv = {}
_svm = ''.join(f'<meta name="{k}" content="{"".join(c for c in str(_sv.get(v, "")) if c.isalnum() or c in "-_")}">' for v, k in (('google', 'google-site-verification'), ('bing', 'msvalidate.01')) if _sv.get(v))
if _svm:
    out = out.replace('</head>', _svm + '\n</head>', 1)
from pageshell import LIVE_NAV as _LIVE_NAV, MID_NAV as _MID_NAV, DESKS as _DESKS
out = out.replace('{{LIVE_NAV}}', _LIVE_NAV).replace('{{MID_NAV}}', _MID_NAV)
out = out.replace('{{DESKS}}', '<nav class="mh-desks" aria-label="Desks">' + ''.join(f'<a href="{u}">{_h.escape(t)}</a>' for u, t in _DESKS) + '</nav>')
open('index.html', 'w', encoding='utf-8').write(out.replace('{{PAGE}}', 'front'))
# ---- the Record (/index/): the same template with the headline page hidden and the full index shown
rec = out.replace('{{PAGE}}', 'record')
rec = rec.replace('<title>Warning Shots: live AI incidents, threats and breakthroughs</title>', f'<title>The Record: every AI incident since 2023, scored and sourced | {title}</title>', 1)
rec = rec.replace(f'<link rel="canonical" href="{site_url}">', f'<link rel="canonical" href="{site_url}index/">', 1)
rec = rec.replace(f'<meta property="og:url" content="{site_url}">', f'<meta property="og:url" content="{site_url}index/">', 1)
rec = rec.replace(og_title.replace('"', '&quot;'), (f"AI has started breaking in on its own — the Record, {title}").replace('"', '&quot;'))
rec = rec.replace('<a class="skip" href="#wall">Skip to the headlines</a>', '<a class="skip" href="#record">Skip to the Record</a>', 1)
rec_desc = f"The Record: all {n} AI incidents since 2023, each scored 0–100 by a published formula and sourced. Severe incidents went from {p12} to {s12} in a year; in {share}% of this year's real-world cases the AI did the acting. Charts, forecasts and whether the fixes held."
rec = rec.replace(og_desc.replace('"', '&quot;'), rec_desc.replace('"', '&quot;'))
os.makedirs('index', exist_ok=True)
open('index/index.html', 'w', encoding='utf-8').write(rec)
# ---- the Wire (/wire/): every report from the last three days, the refresh box and the live panel
wre = out.replace('{{PAGE}}', 'wire')
wre = wre.replace('<title>Warning Shots: live AI incidents, threats and breakthroughs</title>', f'<title>The Wire: every AI threat and breakthrough reported in the last three days | {title}</title>', 1)
wre = wre.replace(f'<link rel="canonical" href="{site_url}">', f'<link rel="canonical" href="{site_url}wire/">', 1)
wre = wre.replace(f'<meta property="og:url" content="{site_url}">', f'<meta property="og:url" content="{site_url}wire/">', 1)
wre = wre.replace('<a class="skip" href="#wall">Skip to the headlines</a>', '<a class="skip" href="#wire">Skip to the Wire</a>', 1)
wire_desc = f"The Wire: every report on AI's dangers and breakthroughs from the last three days, newest first, each linking to the outlet. Plus what changed since the last refresh and the live incident. Updated {et}."
wre = wre.replace(og_desc.replace('"', '&quot;'), wire_desc.replace('"', '&quot;'))
os.makedirs('wire', exist_ok=True)
open('wire/index.html', 'w', encoding='utf-8').write(wre)
# ---- data/incidents.csv: the same rows as data/incidents.json, for spreadsheets
import csv as _csv
_rows = json.load(open('data/incidents.json', encoding='utf-8'))
_cols = ['id', 'date', 'date_precision', 'disclosed', 'title', 'actors', 'category', 'setting', 'H', 'R', 'A', 'N', 'I', 'harm', 'summary', 'source_url', 'source2_url', 'confidence']
with open('data/incidents.csv', 'w', newline='', encoding='utf-8') as _f:
    _w = _csv.DictWriter(_f, fieldnames=_cols, extrasaction='ignore'); _w.writeheader(); [_w.writerow(r) for r in _rows]

# ---- posts from X (research/x_posts.json, last 14 days; the page shows three, one per kind; exact text from research/x_cache.json via build/fetch_x.py): the last 72 hours go to the page; labels per REFRESH.md (breaking/official/claim/opinion)
try:
    _xp = json.load(open('research/x_posts.json', encoding='utf-8'))
except (OSError, ValueError):
    _xp = []
import datetime as _dtx
_cut = _dtx.datetime.fromisoformat(meta['as_of']) - _dtx.timedelta(days=14)
_xp = [x for x in _xp if _dtx.datetime.fromisoformat(x['posted'].replace('Z', '+00:00')) >= _cut]
try:
    _xc = json.load(open('research/x_cache.json', encoding='utf-8'))
except (OSError, ValueError):
    _xc = {}
_xp = [dict(x, tweet=_xc[x['id']]) if x['id'] in _xc else x for x in _xp]
# ---- the desks: counts for the standing links at the foot of each homepage column
def _jl(f, d=None):
    try:
        return json.load(open(f, encoding='utf-8'))
    except (OSError, ValueError):
        return d
_fx = _jl('data/fixes.json', []); _cur = lambda f: next((c for c in f['chain'] if c['stage'] == 'current'), f['chain'][-1])
_calls = [c for c in (_jl('data/calls.json', []) or []) if not c.get('resolution') and c.get('kind') == 'call']
_calls.sort(key=lambda c: c['resolve_by'])
def _ow(o):
    o = float(o); return 'a toss-up' if abs(o - .5) < 1e-9 else 'very likely' if o >= .85 else 'likely' if o >= .6 else 'very unlikely' if o <= .15 else 'unlikely' if o <= .4 else 'leaning yes' if o > .5 else 'leaning no'
_jobs = _jl('research/jobs.json', {}) or {}
_desks = {'fix_open': sum(1 for f in _fx if _cur(f)['status'] != 'fixed'), 'fix_total': len(_fx),
          'checks': len(_jl('research/checks.json', []) or []), 'can_ai': len(_jl('research/can_ai.json', []) or []),
          'jobs': len(_jobs.get('jobs', [])) if isinstance(_jobs, dict) else len(_jobs),
          'midterms': len(_jl('research/midterm_fakes.json', []) or []), 'layoffs': (_jl('data/ledger_count.json', {}) or {}).get('layoffs')}
if _calls:
    _c = _calls[0]; _d = dt.date.fromisoformat(_c['resolve_by'])
    _desks['next_call'] = {'id': _c['id'], 'q': (_c.get('plain') or _c['question']).rstrip('?') + '?', 'odds_word': _ow(_c['odds']), 'when': _d.strftime('%b ') + str(_d.day)}
# ---- breakthroughs (research/breakthroughs.json): written as human payoffs, joined to their Wire source for the link and outlet
_news = {n['id']: n for n in (_jl('research/news_archive.json', []) or []) + (_jl('research/news.json', []) or [])}
_bt = []
for _b in sorted(_jl('research/breakthroughs.json', []) or [], key=lambda b: b.get('date', ''), reverse=True):
    _n = _news.get(_b.get('news_id'), {})
    _bt.append(dict(_b, url=_b.get('url') or _n.get('url', ''), outlet=_b.get('outlet') or _n.get('outlet', '')))
json.dump(_bt, open('data/breakthroughs.json', 'w', encoding='utf-8'), ensure_ascii=False)
_desks['breakthroughs'] = len(_bt)
json.dump(_desks, open('data/desks.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(sorted(_xp, key=lambda x: x['posted'], reverse=True), open('data/xposts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

# ---- data/bundle.json: every data file in one request (the page preloads it; the individual files stay for scripts and the update check)
FILES = ['incidents', 'forecasts', 'pipeline', 'drivers', 'context', 'catalysts', 'horizon', 'deepdives', 'victims', 'timeline', 'implications', 'signals', 'live', 'watch', 'meta',
         'quotes', 'brief', 'news', 'capabilities', 'fixes', 'tns', 'calls', 'xposts', 'desks', 'breakthroughs']
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
        items.append(dict(title='Since the last refresh: ' + it['text'][:90].rstrip() + ('…' if len(it['text']) > 90 else ''), link=site + 'wire/#brief', guid=site + 'wire/#brief-' + __import__('hashlib').sha1(it['text'].encode()).hexdigest()[:12], date=_rfc(meta['as_of']), desc=it['text'] + (' Source: ' + it['url'] if it.get('url') else '')))
except (OSError, ValueError):
    pass
try:
    for n in json.load(open('data/news.json'))[:40]:
        items.append(dict(title=n['title'], link=n['url'], guid=n['url'], date=_rfc(n['published']), desc=(n.get('summary') or '') + ' (' + n.get('outlet', '') + ')'))
except (OSError, ValueError):
    pass
rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', f'<title>{_html.escape(title)}: the Wire and the daily brief</title>', f'<link>{site}</link>',
       '<description>See what’s coming. Know what it means. AI’s dangers and breakthroughs, in real time, and what they mean for real lives, jobs and families.</description>', f'<lastBuildDate>{_rfc(meta["as_of"])}</lastBuildDate>']
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
json.dump(dict(build=build, og_title=og_title, og_desc=og_desc, severe_last12=s12, severe_prior12=p12, agentic_share=share, n=len(inc)), open('assets/build.json', 'w'))
print('built', build, '|', og_title, '|', og_desc)
