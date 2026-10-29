#!/usr/bin/env python3
"""The level with a memory: one row per day since frozen editions began (Oct 26, 2026), read from the last frozen edition
of each day in archive/ (what readers actually saw). Writes data/level_history.json (the homepage strip and streak; today's
live level is added on the page) and the /level/ page. Only real, archived levels: no backfill from guesses."""
import glob, json, os, re, collections
from pagekit import write, footer_note, webpage, esc, fdate, SITE

TIER = {1: 'Minor', 2: 'Moderate', 3: 'Serious', 4: 'Severe', 5: 'Critical'}
last = {}
for d in sorted(glob.glob('archive/*/index.html')):
    ed = d.split('/')[1]
    m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{4})$', ed)
    if not m: continue
    t = open(d, encoding='utf-8', errors='ignore').read()
    lv = re.search(r'WS-([1-5]) (MINOR|MODERATE|SERIOUS|SEVERE|CRITICAL)', t)
    if not lv: continue
    last[m.group(1)] = dict(date=m.group(1), level=int(lv.group(1)), tier=TIER[int(lv.group(1))], edition=ed)
hist = [last[k] for k in sorted(last)]
json.dump(hist, open('data/level_history.json', 'w'), indent=0)

# the /level/ page
url = SITE + 'level/'
runs, cur = [], None
for h in hist:
    if cur and cur['level'] == h['level']: cur['to'] = h['date']; cur['n'] += 1
    else: cur = dict(level=h['level'], tier=h['tier'], frm=h['date'], to=h['date'], n=1); runs.append(cur)
rows = ''.join(f'<tr><td>{esc(fdate(h["date"]))}</td><td><b>WS-{h["level"]} {esc(h["tier"])}</b></td><td><a href="/archive/{esc(h["edition"])}/">The edition</a></td></tr>' for h in reversed(hist))
cnt = collections.Counter(h['tier'] for h in hist)
body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb">The level</nav>
<h1>The level, day by day</h1>
<p class="aka">Each day's Warning Shots level, as it stood in the last edition of that day. The level is set by the most severe incident that is live or disclosed in the last day, on the <a href="/methodology/">published scale</a> from WS-1 Minor to WS-5 Critical. The record starts on Oct 26, 2026, when editions began to be frozen; earlier days are not reconstructed.</p>
<section class="box"><b class="k">So far</b><p>{len(hist)} days recorded: {', '.join(f'{v} at {k}' for k, v in cnt.most_common())}.{(' Longest run: ' + str(max(r['n'] for r in runs)) + ' days at WS-' + str(max(runs, key=lambda r: r['n'])['level']) + '.') if runs else ''}</p></section>
<div class="tw"><table><thead><tr><th>Day</th><th>Level</th><th>As published</th></tr></thead><tbody>{rows}</tbody></table></div>
<p><a href="/archive/">Every frozen edition →</a></p>
{footer_note(False)}</article>"""
write('level/index.html', url=url, title='The Warning Shots level, day by day', desc='Each day\'s Warning Shots level since Oct 26, 2026, with a link to the edition that carried it.', body=body, draft=False,
      crumbs=[('The level', '')], graph=[webpage(url, 'The level, day by day', 'Daily AI threat level history', hist[-1]['date'] if hist else '', False, '')])
tu_p = 'data/tool_urls.json'
tu = json.load(open(tu_p)) if os.path.exists(tu_p) else []
if url not in tu: tu.append(url)
json.dump(tu, open(tu_p, 'w'))
print(f'level: {len(hist)} days, runs {[(r["level"], r["n"]) for r in runs]}')
