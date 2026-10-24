# The daily brief: one script per refresh, in a fixed rundown, assembled from the index's own data. Nothing is written here
# that is not already on the site; the editor reads it, cuts it, records it or mails it. Also keeps the forecast ledger
# (research/forecast_log.jsonl: every refresh's odds) so "what moved" can be reported honestly.
# Writes briefs/<YYYY-MM-DD-HHMM>.md. Run after build_live.py and build_posts.py.
import json, os, re, sys, datetime as dt
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
D = lambda f: json.load(open(os.path.join(HERE, 'data', f + '.json'), encoding='utf-8'))
meta = D('meta'); site = meta['site_url']
ET = ZoneInfo('America/New_York')
AS_OF = dt.datetime.fromisoformat(meta['as_of']); AS_ET = AS_OF.astimezone(ET)
TIERS = ['Minor', 'Moderate', 'Serious', 'Severe', 'Critical']

def sev(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    s = round(0.55 * harm + 0.45 * sig)
    t = 4 if s >= 80 else 3 if s >= 60 else 2 if s >= 40 else 1 if s >= 20 else 0
    return s, t
def when(iso):
    if not iso: return None
    try: d = dt.datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
    except ValueError: return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
def hours_ago(iso):
    d = when(iso); return None if d is None else (AS_OF - d).total_seconds() / 3600
def fdate(iso):
    if not iso: return ''
    d = dt.date.fromisoformat(iso[:10]); return d.strftime('%b %-d') if d.year == AS_ET.year else d.strftime('%b %-d, %Y')
def first_sentence(t):
    t = (t or '').strip(); m = re.match(r'(.+?[.!?])(\s|$)', t); return (m.group(1) if m else t).strip()
def days_since(iso):
    d = when(iso); return None if d is None else int((AS_OF - d).total_seconds() // 86400)

inc = D('incidents'); news = D('news'); fixes = D('fixes'); caps = D('capabilities'); fc = D('forecasts'); watch = D('watch'); cats = D('catalysts'); brief = D('brief'); live = D('live'); dds = D('deepdives'); tns = D('tns')
scored = sorted(inc, key=lambda r: (r['date'], r['id']))
for i, r in enumerate(scored): r['ws'] = 'WS-%04d' % (i + 1); r['severity'], r['t'] = sev(r)

# ---- forecast ledger: append this refresh's odds, then compare with the last snapshot at least 20 hours older
log_path = os.path.join(ROOT, 'research', 'forecast_log.jsonl')
rows = []
if os.path.exists(log_path):
    for line in open(log_path, encoding='utf-8'):
        line = line.strip()
        if line:
            try: rows.append(json.loads(line))
            except ValueError: pass
if not any(r.get('as_of') == meta['as_of'] for r in rows):
    with open(log_path, 'a', encoding='utf-8') as fh:
        for f in fc: fh.write(json.dumps(dict(as_of=meta['as_of'], id=f['id'], p=float(f['probability']), resolve_by=f.get('resolve_by'), resolved=f.get('resolved')), ensure_ascii=False) + '\n')
snapshots = sorted({r['as_of'] for r in rows if r.get('as_of') != meta['as_of']})
prev_as_of = next((s for s in reversed(snapshots) if (AS_OF - when(s)).total_seconds() >= 20 * 3600), None)
prev = {r['id']: r['p'] for r in rows if r.get('as_of') == prev_as_of} if prev_as_of else {}
moved = sorted([(f, prev[f['id']]) for f in fc if f['id'] in prev and abs(float(f['probability']) - prev[f['id']]) >= 0.05], key=lambda x: -abs(float(x[0]['probability']) - x[1]))
resolved = [f for f in fc if f.get('resolved') in ('yes', 'no')]

# ---- the level: highest tier among incidents with an event or disclosure in the last 7 days, read as WS-1..5
recent = [r for r in scored if (hours_ago(r.get('disclosed') or r['date']) or 1e9) <= 7 * 24 and (hours_ago(r.get('disclosed') or r['date']) or 0) >= -24]
top = max(recent, key=lambda r: r['severity']) if recent else None
level = ('WS-%d %s' % (top['t'] + 1, TIERS[top['t']])) if top else 'WS-1 quiet week'
live_dd = next((d for d in dds if d['incident_id'] == meta.get('live_incident')), dds[0] if dds else None)
live_day = days_since(meta.get('live_since')) if meta.get('live_since') else None

# ---- the siren and the board
items = [n for n in news if n.get('title') and n.get('url')]
items.sort(key=lambda n: str(n.get('published') or ''), reverse=True)
siren = next((n for n in items if n.get('siren')), items[0] if items else None)
rest = [n for n in items if n is not siren and (hours_ago(n.get('published')) or 1e9) <= 36]
board, seen_topics = [], set()
for pref in (('breaking', 'official'), ('breakthrough',), ('incident', 'analysis')):
    for n in rest:
        if n in board: continue
        if (n.get('kind') in pref or n.get('topic') in pref) and n.get('topic') not in seen_topics:
            board.append(n); seen_topics.add(n.get('topic'))
        if len(board) >= 4: break
    if len(board) >= 4: break
for n in rest:
    if len(board) >= 4: break
    if n not in board: board.append(n)

# ---- fix watch: the case that moved most recently, with a day count on its claimed fix or its report
def cur(f): return next((c for c in f['chain'] if c['stage'] == 'current'), {})
def latest_move(f): return max((c.get('date') or '' for c in f['chain']), default='')
moved_case = max(fixes, key=latest_move) if fixes else None
verified = sum(1 for f in fixes if cur(f).get('status') == 'fixed')
reopened = sum(1 for f in fixes if cur(f).get('status') == 'reopened')
def fix_clock(f):
    claim = next((c for c in f['chain'] if c['stage'] == 'claimed_fix' and c.get('date')), None)
    rep = next((c for c in f['chain'] if c['stage'] == 'reported' and c.get('date')), None)
    if claim: return 'Day %d since the claimed fix' % (days_since(claim['date']) or 0)
    if rep: return 'Day %d since it was reported' % (days_since(rep['date']) or 0)
    return ''

# ---- the shot: the next dated tests and anything due on the watch list
today = AS_ET.date().isoformat()
upcoming = [c for c in sorted(cats, key=lambda c: c['date']) if c['date'] >= today][:3]
due = [w for w in watch if w.get('kind') == 'due'][:2]

# ---- for you: the newest milestone's everyday line, else the Then/Now/Still action
newest_cap = max(caps, key=lambda c: c['date']) if caps else None
for_you = (newest_cap.get('everyday') if newest_cap else '') or (tns.get('do_now') if isinstance(tns, dict) else '') or ''

# ---- new on the index since the previous brief window (24h)
new_inc = [r for r in scored if 0 <= (hours_ago(r.get('disclosed') or r['date']) or 1e9) <= 24]
new_caps = [c for c in caps if 0 <= (hours_ago(c['date']) or 1e9) <= 24 * 7]

stamp = AS_ET.strftime('%A, %B %-d, %Y, %-I:%M %p ET')
L = []
L.append(f'# Warning Shots daily brief — {stamp}')
L.append('')
L.append('Script and email draft, assembled from this refresh. Fixed rundown; read in order; cut what is thin. Target 6–8 minutes spoken. Every line is on the site with its source; nothing here is new reporting.')
L.append('')
L.append('## 1. The level (15s)')
L.append(f'Today’s level: **{level}**' + (f', set by {top["title"]} ({top["ws"]}, {top["severity"]}/100).' if top else '. No incident on the index was reported or disclosed in the last seven days.'))
if live_dd: L.append(f'{live_dd["name"]}' + (f', day {live_day}.' if live_day is not None else '.') + ' ' + ' '.join(f'{x["value"]} {x["label"]};' for x in live[:3]).rstrip(';') + '.')
L.append('_Formula: the highest WS level among incidents reported or disclosed in the last seven days. Not a prediction._')
L.append('')
L.append('## 2. The siren (90s)')
if siren:
    L.append(f'**{siren["title"]}** ({siren["outlet"]}' + (', also ' + ', '.join(a['outlet'] for a in siren.get('also') or []) if siren.get('also') else '') + ').')
    if siren.get('summary'): L.append(siren['summary'])
    L.append(f'What it is and what it isn’t: say which figures are confirmed and by whom; name what has not happened. Link: {siren["url"]}')
L.append('')
L.append('## 3. The board (90s, one line each)')
for n in board:
    L.append(f'- **{n["title"]}** — {n.get("summary") or ""} ({n["outlet"]}, {fdate(n.get("published"))}) {n["url"]}')
if new_inc:
    for r in new_inc: L.append(f'- New on the index: **{r["title"]}** ({r["ws"]}, {r["severity"]}/100 {TIERS[r["t"]]}). {first_sentence(r.get("summary"))} {site}i/{r["id"]}/')
if new_caps:
    c = max(new_caps, key=lambda c: c['date']); L.append(f'- Both edges: **{c["title"]}** — {first_sentence(c.get("what"))} Reliable for a defined task: {((c.get("stages") or {}).get("reliable") or {}).get("status", "unknown")}. {site}m/{c["id"]}/')
L.append('')
L.append('## 4. Fix watch (45s)')
if moved_case:
    c = cur(moved_case)
    L.append(f'**{moved_case["name"]}** — {fix_clock(moved_case)}. Status: **{c.get("status", "")}**. {moved_case.get("one_liner") or c.get("note") or ""} {site}c/{moved_case["incident_id"]}/')
L.append(f'The tally: {verified} of {len(fixes)} cases on the index have an independently verified fix; {reopened} have recurred after a claimed fix.')
L.append('')
L.append('## 5. The ledger (45s)')
if moved:
    L.append(f'Odds that moved since {fdate(prev_as_of)}:')
    for f, p0 in moved: L.append(f'- {f["event"]}: {int(round(p0 * 100))}% → **{f["probability_label"]}** (by {fdate(f["resolve_by"])}). Say why, from the basis: {first_sentence(f.get("basis"))}')
else:
    L.append('No forecast moved by five points or more since the last brief. Standing odds to repeat:')
    for f in sorted(fc, key=lambda f: -float(f['probability']))[:3]: L.append(f'- **{f["probability_label"]}** that {f["event"][0].lower() + f["event"][1:]} (by {fdate(f["resolve_by"])}).')
if resolved:
    for f in resolved: L.append(f'- Graded: {f["event"]} — resolved **{f["resolved"]}** ({f.get("resolution_note") or ""}).')
nearest = min(fc, key=lambda f: f['resolve_by']) if fc else None
if nearest: L.append(f'Next to resolve: {nearest["event"]} ({nearest["probability_label"]}), by {fdate(nearest["resolve_by"])}.')
L.append('')
L.append('## 6. The shot (30s)')
for c in upcoming: L.append(f'- {c["date_label"]}: {c["event"]} — {first_sentence(c.get("why"))}')
for w in due: L.append(f'- Due: {w["item"]} — {w["status"]}')
L.append('')
L.append('## 7. For you (20s)')
L.append(for_you)
L.append('')
L.append('## 8. Sign-off')
L.append('That’s the warning shot. See what’s coming. Know what it means for you. Everything in this brief, with its sources, is at warningshots.ai.')
L.append('')
L.append('---')
L.append(f'Refresh notes: {meta["changelog"][0]["text"] if meta.get("changelog") else ""}')
os.makedirs(os.path.join(ROOT, 'briefs'), exist_ok=True)
fn = os.path.join(ROOT, 'briefs', AS_ET.strftime('%Y-%m-%d-%H%M') + '.md')
open(fn, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('brief ->', os.path.relpath(fn, ROOT), '| level', level, '| board', len(board), '| moved', len(moved), '| ledger snapshots', len(snapshots) + 1)
