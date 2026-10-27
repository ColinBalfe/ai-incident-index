#!/usr/bin/env python3
"""The permanent Wire archive: every story that has ever been on the Wire, by day.

The live Wire (research/news.json) is a rolling 72-hour board. Before stories roll off, this script folds them into
research/news_archive.json (never pruned) and builds:
  wire/<YYYY-MM-DD>/   one page per day: every story that day, newest first, with our headline, outlet, link and
                       summary, plus links to that day's frozen front-page editions in archive/
  wire/archive/        the list of days
Run after build_live.py (so the newest stories are in), before build_pages.py (which adds the pages to the sitemap)."""
import json, os, glob, collections, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pagekit import *

A = 'research/news_archive.json'
try:
    arch = {n['id']: n for n in json.load(open(A, encoding='utf-8'))}
except (OSError, ValueError):
    arch = {}
for n in json.load(open('research/news.json', encoding='utf-8')):
    m = {k: v for k, v in n.items() if k not in ('wall', 'wall_rank', 'siren', 'moved')}
    arch[n['id']] = {**arch.get(n['id'], {}), **m}
rows = sorted(arch.values(), key=lambda n: n.get('published') or '')
json.dump(rows, open(A, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

TOPIC = {'php2shell': 'The flaw under most websites', 'ai-attack': 'AI attacks', 'ai-incident': 'AI incidents', 'breakthrough': 'Breakthroughs', 'jobs': 'Jobs',
         'families': 'Families and kids', 'everyday': 'Everyday life', 'regulation': 'Rules and regulators', 'deepfakes': 'Deepfakes', 'chatbot-harm': 'Chatbot harms', 'other': 'Other'}
LBL = {'retracted': 'Retracted', 'reported': 'Reported', 'lab': 'Lab only', 'denied': 'Denied', 'tried': 'Tried', 'proven': 'Proven', 'hit': 'Hit'}
by_day = collections.defaultdict(list)
for n in rows:
    if n.get('published'): by_day[n['published'][:10]].append(n)
days = sorted(by_day, reverse=True)
snaps = collections.defaultdict(list)
for p in sorted(glob.glob('archive/20*/index.html')):
    d = p.split('/')[1]; snaps[d[:10]].append(d)
urls = []
asof = meta['as_of'][:10]
for i, d in enumerate(days):
    items = sorted(by_day[d], key=lambda n: n['published'], reverse=True)
    label = dt.date.fromisoformat(d).strftime('%A, %B %-d, %Y')
    groups = collections.OrderedDict()
    for n in items: groups.setdefault(TOPIC.get(n.get('topic'), 'Other'), []).append(n)
    body_items = ''
    for g, ns in groups.items():
        body_items += f'<h2>{esc(g)} ({len(ns)})</h2><ul class="rec">' + ''.join(
            f'<li>' + (f'<span class="st">{esc(LBL[n["label"]])}</span> ' if n.get('label') in LBL else '') +
            f'<a href="{esc(n["url"])}" target="_blank" rel="noopener noreferrer"><b>{esc(n.get("tag") or n["title"])}</b></a>'
            f'<br><small>{esc(n.get("outlet") or "")}' + (f' · {esc(n["published"][11:16])} UTC' if n.get('time_known', True) else '') + f'</small>'
            + (f'<br>{esc(n["summary"])}' if n.get('summary') else '') + '</li>' for n in ns) + '</ul>'
    ed = ''.join(f'<li><a href="/archive/{esc(s)}/">Front page as published, {esc(s[11:13])}:{esc(s[13:15])} ET</a></li>' for s in snaps.get(d, []))
    prev_d = days[i + 1] if i + 1 < len(days) else None; next_d = days[i - 1] if i > 0 else None
    nav = ('<p class="share">' + (f'<a href="/wire/{prev_d}/">← {esc(dt.date.fromisoformat(prev_d).strftime("%b %-d"))}</a>' if prev_d else '') +
           (f' &nbsp; <a href="/wire/{next_d}/">{esc(dt.date.fromisoformat(next_d).strftime("%b %-d"))} →</a>' if next_d else '') + ' &nbsp; <a href="/wire/archive/">Every day</a></p>')
    title = f'AI news, {dt.date.fromisoformat(d).strftime("%B %-d, %Y")}: what AI did that day'
    desc = f'Every report on AI\'s dangers and breakthroughs from {label}: {len(items)} stories, each with its source, from attacks and scams to jobs, kids and new capabilities.'
    url = SITE + f'wire/{d}/'
    body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/wire/">The Wire</a> · <a href="/wire/archive/">Every day</a></nav>
<h1>{esc(label)}</h1><div class="meta">{len(items)} stories{' · still on the live Wire' if d >= (dt.date.fromisoformat(asof) - dt.timedelta(days=3)).isoformat() else ''} · each headline is ours and links to the original reporting</div>
{nav}
{('<h2>The front page that day</h2><ul>' + ed + '</ul>') if ed else ''}
{body_items}
{nav}
<p class="disc">Headlines are written by Warning Shots and link straight to the outlet. Later corrections and retractions are recorded on the incident pages and in the <a href="/index/#changelog">changelog</a>.</p></article>"""
    write(f'wire/{d}/index.html', url=url, title=title, desc=desc, body=body, draft=False, crumbs=[('The Wire', '/wire/'), (label, '')],
          graph=[{"@type": "CollectionPage", "name": title, "url": url, "datePublished": d, "about": "AI incidents, threats and breakthroughs"}])
    urls.append(url)
lst = ''.join(f'<li><a href="/wire/{d}/">{esc(dt.date.fromisoformat(d).strftime("%A, %B %-d, %Y"))}</a> <small>{len(by_day[d])} stories</small></li>' for d in days)
hub = f"""<article class="pk"><div class="kick"><a href="/wire/">The Wire</a></div><h1>Every day on the Wire</h1>
<p>The live Wire shows the last three days. Nothing is thrown away: every story that has appeared is kept here by day, with the front page exactly as it was published.</p>
<ul class="rec">{lst}</ul><p><a href="/archive/">Every front-page edition, frozen as published →</a></p></article>"""
write('wire/archive/index.html', url=SITE + 'wire/archive/', title='The Wire archive: AI news by day', desc=f'Every AI story Warning Shots has reported, by day: {len(rows)} stories across {len(days)} days, each linked to its source.', body=hub, draft=False,
      crumbs=[('The Wire', '/wire/'), ('Every day', '')], graph=[{"@type": "CollectionPage", "name": "The Wire archive", "url": SITE + 'wire/archive/'}])
register('wire/archive/', [SITE + 'wire/archive/'])
p = os.path.join(here, 'data/tool_urls.json'); tu = json.load(open(p))
tu = [u for u in tu if not (u.startswith(SITE + 'wire/20'))] + urls
json.dump(tu, open(p, 'w'))
print(f'wire archive: {len(rows)} stories, {len(days)} day pages')
