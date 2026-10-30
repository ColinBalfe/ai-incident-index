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
         'families': 'Families and kids', 'everyday': 'Everyday life', 'power': 'Power and data centers', 'markets': 'Money and markets', 'regulation': 'Government and politics', 'deepfakes': 'Deepfakes', 'chatbot-harm': 'Chatbot harms', 'other': 'Other'}
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
            + (f'<br>{esc(n["summary"])}' if n.get('summary') else '') + (f'<br><small class="tch">Who this touches: {esc(n["touches"])}</small>' if n.get('touches') else '') + '</li>' for n in ns) + '</ul>'
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

# ======================================================== beats: AI near you, AI at school, AI decided
import re as _re
BEATS = [
 ('near-you', 'AI near you', 'Data centres, power bills, water and the local fights over them.', r'data[- ]?cent(er|re).{0,60}(power|electric|water|bill|within|oppose|neighbo|resident|local|town|county)|(power|electric|water).{0,40}data[- ]?cent(er|re)|power bill|electricity (bill|price|rate)'),
 ('school', 'AI at school', 'Classrooms, tutors, cheating, school rules and the teachers caught in the middle.', r'\b(schools?|students?|teachers?|classrooms?|pupils?|homework|tutors?)\b(?!.{0,3}shoot)'),
 ('decided', 'AI decided', 'When AI makes a decision about you: credit, insurance, hiring, benefits, policing and facial recognition.', r'credit score|loan (decision|denial)|insurance claim|claims? (were |was )?denied|denied coverage|hiring (tool|algorithm|screen)|job applicants?|r[eé]sum[eé] screen|benefits (claim|decision|denied)|facial recognition|wrongful(ly)? arrest|algorithm(ic)? (decision|denial)'),
]
beat_urls = []
try: BG = json.load(open('research/beat_background.json', encoding='utf-8'))
except (OSError, ValueError): BG = {}
def bg_html(slug):
    rows = BG.get(slug) or []
    if not rows: return ''
    li = ''.join(f'<li><time>{esc(b["date"])}</time> <a href="{esc(b["url"])}" target="_blank" rel="noopener noreferrer"><b>{esc(b["title"])}</b></a> <small>{esc(b["outlet"])}</small><br>{esc(b["status"])}'
                 + (f'<br><small class="tch">Who this touches: {esc(b["touches"])}</small>' if b.get('touches') else '')
                 + (f'<br><small class="nxt">Next: {esc(b["next_what"])}, {esc(fdate(b["next"]))}</small>' if b.get('next') else '') + '</li>' for b in rows)
    return f'<h2>Cases still open</h2><p class="meta">The slow stories behind the headlines: where each one stands and what decides it next.</p><ul class="rec">{li}</ul>'
for slug, name, blurb, rx in BEATS:
    hits = [n for n in rows if n.get('beat') == slug or (n.get('topic') != 'php2shell' and _re.search(rx, n.get('title', '') + ' ' + (n.get('tag') or ''), _re.I))]
    hits.sort(key=lambda n: n.get('published') or '', reverse=True)
    items = ''.join(f'<li><time>{esc(n["published"][:10])}</time> ' + (f'<span class="st">{esc(LBL[n["label"]])}</span> ' if n.get('label') in LBL else '') +
                    f'<a href="{esc(n["url"])}" target="_blank" rel="noopener noreferrer"><b>{esc(n.get("tag") or n["title"])}</b></a> <small>{esc(n.get("outlet") or "")}</small>'
                    + (f'<br>{esc(n["summary"])}' if n.get('summary') else '') + (f'<br><small class="tch">Who this touches: {esc(n["touches"])}</small>' if n.get('touches') else '') + '</li>' for n in hits)
    url = SITE + f'wire/{slug}/'
    body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/wire/">The Wire</a> · A beat</nav><h1>{esc(name)}</h1>
<p class="aka">{esc(blurb)}</p><div class="meta">{(str(len(hits)) + ' stories so far, newest first · ') if hits else ''}added to on every refresh · each headline links to the original reporting</div>
{('<ul class="rec">' + items + '</ul>') if hits else '<p>No fresh story on this beat yet that meets our bar: AI as the actor, a real consequence, a source we could open. It fills as the stories come.</p>'}
{bg_html(slug)}
<p class="share"><a href="/wire/archive/">Every day on the Wire</a> · <a href="/exposed/">What it means for you</a></p></article>"""
    write(f'wire/{slug}/index.html', url=url, title=f'{name}: AI news, tracked', desc=f'{blurb} Every story Warning Shots has reported on it, newest first, with sources.', body=body, draft=not (hits or BG.get(slug)),
          crumbs=[('The Wire', '/wire/'), (name, '')], graph=[{"@type": "CollectionPage", "name": name, "url": url, "about": blurb}])
    if hits or BG.get(slug): beat_urls.append(url)

# ======================================================== the AI layoffs ledger (jobs/layoffs/)
J = json.load(open('research/jobs.json', encoding='utf-8'))
occ = {j['slug']: j['occupation'] for j in J['jobs']}
led, seen_u = [], set()
for j in J['jobs']:
    for d, what, u, lab in j.get('jobs_evidence', []):
        low = what.lower()
        who = 'Company says AI' if 'company says ai' in low else 'Reported as AI' if 'reported as ai' in low else 'Study' if '(study' in low or low.endswith('study') or 'study)' in low else ''
        if who == 'Study' or not u or u in seen_u: continue
        seen_u.add(u)
        led.append(dict(date=d, what=_re.sub(r'\s*\((company says AI[^)]*|reported as AI[^)]*)\)\s*', ' ', what).strip(), who=who or 'See source', url=u, label=lab, occ=j['slug']))
for n in rows:
    if n.get('topic') == 'jobs' and n['url'] not in seen_u and _re.search(r'cut|layoff|lay off|buyout|job loss|redundanc|shed|eliminat', n.get('title', '') + ' ' + (n.get('summary') or ''), _re.I):
        seen_u.add(n['url'])
        led.append(dict(date=n['published'][:10], what=n.get('tag') or n['title'], who={'confirmed': 'See source', 'reported': 'Reported as AI'}.get(n.get('label'), 'See source'), url=n['url'], label=n.get('outlet', ''), occ=''))
import ledger_rules as _LR
led = _LR.clean(led, is_company=lambda w: w.startswith('Company'))   # same rules as the job-cuts chart
led.sort(key=lambda x: x['date'], reverse=True)
trs = ''.join(f'<tr><td>{esc(x["date"])}</td><td>{esc(x["what"])}' + (f' <small>(<a href="/jobs/{esc(x["occ"])}/">{esc(occ[x["occ"]])}</a>)</small>' if x['occ'] in occ else '') + f'</td><td><span class="st{" confirmed" if x["who"].startswith("Company") else ""}">{esc(x["who"])}</span></td><td>{a(x["url"], x["label"] or "source")}</td></tr>' for x in led)
n_co = sum(1 for x in led if x['who'].startswith('Company'))
body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/jobs/">Can AI do your job?</a> · The ledger</nav>
<h1>Layoffs tied to AI: the ledger</h1>
<p class="aka">Every job cut on our record where AI is part of the story, newest first, labelled by who says AI was the reason.</p>
<p><b>Our investigation:</b> <a href="/analysis/ai-layoffs-october-2026/">October's “AI layoffs”, checked: in none of the five is AI clearly doing the work →</a></p>
<section class="box"><b class="k">How to read it</b><p><b>Company says AI</b>: the employer itself tied the cuts to AI. <b>Reported as AI</b>: reporters or analysts made the link; the company didn't. A cut that names no AI link isn't evidence that AI took the jobs, and we label it that way.</p></section>
<div class="stats"><div><b>{len(led)}</b><span>entries on the ledger</span></div><div><b>{n_co}</b><span>where the company itself tied the cuts to AI</span></div></div>
<div class="tw"><table><thead><tr><th>Date</th><th>What happened</th><th>Who says AI</th><th>Source</th></tr></thead><tbody>{trs}</tbody></table></div>
<p>Find your own job: <a href="/jobs/">Can AI do your job?</a> grades what AI has actually done, task by task.</p>
{capture('One update a month on AI and jobs. Only when something actually changes.', 'jobs-ledger')}
{footer_note(False)}</article>"""
write('jobs/layoffs/index.html', url=SITE + 'jobs/layoffs/', title='AI layoffs ledger: job cuts tied to AI, labelled', desc=f'Every job cut on the Warning Shots record where AI is part of the story: {len(led)} entries, each labelled by whether the company or only reporters tied it to AI, with sources.', body=body, draft=False,
      crumbs=[('Can AI do your job?', '/jobs/'), ('Layoffs ledger', '')], graph=[{"@type": "Dataset", "name": "AI layoffs ledger", "url": SITE + 'jobs/layoffs/', "description": "Job cuts tied to AI, labelled by attribution", "creator": {"@type": "Organization", "name": "Warning Shots"}}])
p = os.path.join(here, 'data/tool_urls.json'); tu = json.load(open(p))
tu = [u for u in tu if not any(u == SITE + f'wire/{b[0]}/' for b in BEATS) and u != SITE + 'jobs/layoffs/'] + beat_urls + [SITE + 'jobs/layoffs/']
json.dump(tu, open(p, 'w'))
json.dump({'layoffs': len(led), 'company_stated': n_co}, open('data/ledger_count.json', 'w'))
print(f'beats: ' + ', '.join(f'{b[0]}' for b in BEATS) + f' ({len(beat_urls)} with stories); layoffs ledger: {len(led)} entries ({n_co} company-stated)')
