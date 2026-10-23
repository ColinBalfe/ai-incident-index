# The post queue: drafts for X, generated from each refresh. Nothing posts itself; the editor approves.
# Writes posts/<date>-<time>.md (human review) and data/posts.json (latest queue). Run after build_live.py.
import json, os, re, sys, datetime as dt
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
D = lambda f: json.load(open(os.path.join(HERE, 'data', f + '.json'), encoding='utf-8'))
meta = D('meta'); site = meta['site_url']
AS_OF = dt.datetime.fromisoformat(meta['as_of']); ET = ZoneInfo('America/New_York')
LINK = 23  # X counts every link as 23 characters
LIMIT = 280

def sev(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    s = round(0.55 * harm + 0.45 * sig)
    tiers = ['Minor', 'Moderate', 'Serious', 'Severe', 'Critical']
    t = 4 if s >= 80 else 3 if s >= 60 else 2 if s >= 40 else 1 if s >= 20 else 0
    return s, tiers[t], 'WS-%d' % (t + 1)

def within(iso, hours):
    if not iso:
        return False
    try:
        d = dt.datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
    except ValueError:
        return False
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return 0 <= (AS_OF - d).total_seconds() <= hours * 3600 or (d - AS_OF).total_seconds() <= 3 * 3600 and d > AS_OF

def first_sentence(t):
    t = (t or '').strip(); m = re.match(r'(.+?[.!?])(\s|$)', t); return (m.group(1) if m else t).strip()

def fit(text, link=None):
    """Trim text so text + link fits X's limit."""
    budget = LIMIT - (LINK + 1 if link else 0)
    if len(text) <= budget:
        return text
    head = text[:budget]
    # prefer a sentence boundary when it keeps most of the text
    m = max(head.rfind('. '), head.rfind('.\n'), head.rfind('; '))
    if m >= budget * 0.6:
        return head[:m + 1].rstrip()
    cut = text[:budget - 1]
    cut = cut[:cut.rfind(' ')] if ' ' in cut else cut
    return cut.rstrip(' ,;:') + '…'

posts = []
def add(kind, text, link=None, image=None, note=''):
    text = fit(text, link)
    posts.append(dict(kind=kind, text=text, link=link, image=image, chars=len(text) + (LINK + 1 if link else 0), note=note))

inc = {r['id']: r for r in D('incidents')}
news = D('news'); fixes = D('fixes'); caps = D('capabilities'); brief = D('brief'); watch = D('watch'); cats = D('catalysts')
card = lambda kind, slug: f'cards/{kind}-{slug}.jpg' if os.path.exists(os.path.join(ROOT, 'cards', f'{kind}-{slug}.jpg')) else None

# 1. the siren
siren = next((n for n in news if n.get('siren')), news[0] if news else None)
if siren:
    add('siren', f"{siren['title']}. {siren.get('summary', '')} (via {siren['outlet']})", link=siren['url'], image=card('n', siren['id']), note='The outlet gets the link; the card carries our framing.')

# 2. the brief, line by line
for it in brief.get('items', []):
    img = None
    for key, slug in (('PHP2Shell', 'php2shell'), ('PHP', 'php2shell'), ('METR', 'metr-openai-monitoring'), ('Hugging Face', 'openai-hf-swarm')):
        if key in it['text'] and slug in inc:
            img = card('i', slug); break
    add('brief', it['text'], link=it.get('url'), image=img, note='From "Since the last refresh"; written to be posted as-is.')

# 3. new incidents (24h)
for r in inc.values():
    if within(r.get('disclosed') or r.get('date'), 24):
        s, tier, lvl = sev(r)
        add('incident', f"New on the index: {r['title']} ({lvl} {tier}, {s}/100). {first_sentence(r.get('summary'))}", link=f"{site}i/{r['id']}/", image=card('i', r['id']))

# 4. cases that moved (24h)
for f in fixes:
    moved = [c for c in f['chain'] if within(c.get('date'), 24)]
    if moved:
        cur = next((c for c in f['chain'] if c['stage'] == 'current'), {})
        add('case', f"Did they fix it? {f['name']}: {f.get('one_liner') or cur.get('note', '')}", link=f"{site}c/{f['incident_id']}/", image=card('c', f['incident_id']), note='Status: ' + cur.get('status', ''))

# 5. new milestones (7d)
for c in caps:
    if within(c.get('date'), 24 * 7):
        add('milestone', f"What AI can now do: {c['title']}. {first_sentence(c.get('what'))} Reliable for a defined task: {(c.get('stages', {}).get('reliable') or {}).get('status', 'unknown')}.", link=f"{site}m/{c['id']}/", image=card('m', c['id']))

# 6. the week ahead (Sundays, or on request)
if AS_OF.astimezone(ET).weekday() == 6 or '--week-ahead' in sys.argv:
    lines = ['The next 14 days on Warning Shots:']
    for w in watch[:4]:
        lines.append('• ' + w['item'] + ' (' + w['status'].split(';')[0].split('(')[0].strip() + ')')
    for c in sorted(cats, key=lambda c: c['date'])[:2]:
        if c['date'] >= AS_OF.date().isoformat():
            lines.append('• ' + c['date_label'] + ': ' + c['event'])
    add('week-ahead', '\n'.join(lines), link=site + '#next', note='Trim to the four that matter most; this is the raw list.')

stamp_et = AS_OF.astimezone(ET)
out_md = [f"# Post queue — {stamp_et.strftime('%a %b %-d, %Y, %-I:%M %p ET')}", '', 'Drafts generated from this refresh. Nothing posts itself: edit, pick, post. Each line fits X (links count as 23 characters). Images are the pre-rendered cards in /cards.', '']
for i, p in enumerate(posts, 1):
    out_md.append(f"## {i}. {p['kind']}  ({p['chars']} chars)")
    out_md.append('')
    out_md.append(p['text'])
    if p['link']:
        out_md.append(p['link'])
    if p['image']:
        out_md.append(f"Image: {p['image']}")
    if p['note']:
        out_md.append(f"_Note: {p['note']}_")
    out_md.append('')
os.makedirs(os.path.join(ROOT, 'posts'), exist_ok=True)
fn = os.path.join(ROOT, 'posts', stamp_et.strftime('%Y-%m-%d-%H%M') + '.md')
open(fn, 'w', encoding='utf-8').write('\n'.join(out_md))
json.dump(dict(as_of=meta['as_of'], posts=posts), open(os.path.join(HERE, 'data', 'posts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('posts', len(posts), '->', os.path.relpath(fn, ROOT))
