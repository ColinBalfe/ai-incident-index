import json, os, re, sys
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(__file__))
from util import label_for
from deep_text import DEEPDIVES, EXTRA_TIMELINE, EXTRA_IMPL, PHP_TIMELINE_KEEP

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
php = json.load(open(f'{R}/php2shell.json'))

def iso(d):
    m = re.match(r'(\d{4}-\d{2}-\d{2})', d)
    return m.group(1) if m else None

def nice(d):
    import datetime
    try:
        return datetime.date.fromisoformat(d).strftime('%b %-d')
    except Exception:
        return d

# ---------------- victims
EXCLUDE = ('Ahold', 'Yonsei', 'Asana', '4chan', 'Japanese mobile games', 'Nintendo')
SHUT = re.compile(r'offline|shut|halt|paus|suspend|disabl|went dark|taken down|took .* down|pulled|switched off|down\b|maintenance|unavailable|affected', re.I)
victims = []
for i, v in enumerate(php['victims']):
    name = v.get('name') or v.get('organization')
    if any(name.startswith(x) for x in EXCLUDE): continue
    st = v['status']
    wh = v.get('what_happened', '')
    note = v.get('note', '')
    if st == 'confirmed compromise':
        group, label = 'confirmed', 'Compromised'
    elif st == 'attacked/attempted':
        group, label = 'attacked', 'Attacked (blocked or unknown)'
    elif st == 'unconfirmed claim':
        group, label = 'other', ('Claim retracted' if 'RETRACTED' in note or 'retract' in wh.lower() else 'Unconfirmed claim')
    else:
        if SHUT.search(wh) and 'protected' not in wh:
            group, label = 'disrupted', 'Took services offline'
        else:
            group, label = 'other', 'Patched / exposed'
    if 'not definitively' in (note + wh).lower() or 'not definitively linked' in wh:
        label += ' · link unconfirmed'
    dmg = v.get('damage', '')
    extent = wh + ('' if not dmg or dmg.startswith('none') else ' Damage: ' + dmg)
    d0 = iso(v.get('date', '')) or '2026-10-21'
    dl = v.get('date', '')
    m = re.match(r'(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', dl)
    date_label = (nice(m.group(1)) + '–' + nice(m.group(2)).split(' ')[-1]) if m else nice(d0)
    victims.append(dict(id=f'php-{i:02d}', incident_id='php2shell', organization=name, sector=v.get('sector', ''), country=v.get('country', ''),
                        status=label, status_group=group, date=d0, date_label=date_label, extent=extent, how='', count=1,
                        source_url=v['source'], source_label=label_for(v['source'])))

# ---------------- timeline
timeline = []
for i, t in enumerate(php['timeline']):
    if i not in PHP_TIMELINE_KEEP: continue
    d = t['date']
    m = re.match(r'(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?', d)
    if m:
        sort = m.group(1) + ('T' + m.group(2) if m.group(2) else 'T18:00')
        lab = nice(m.group(1)) + (' ' + m.group(2) + ' UTC' if m.group(2) else '')
    elif re.fullmatch(r'\d{4}-\d{2}', d):
        sort, lab = d + '-01T00:00', __import__('datetime').date.fromisoformat(d + '-01').strftime('%b %Y')
    else:
        sort, lab = d[:4] + '-01-01T00:00', d[:4]
    timeline.append(dict(id=f'php-t{i:02d}', incident_id='php2shell', date=sort, date_label=lab, event=PHP_TIMELINE_KEEP[i] or t['event'], source_url=t['source']))
timeline += EXTRA_TIMELINE

# ---------------- implications
impl = []
for i, x in enumerate(php['implications']):
    src = x['sources'][0] if x.get('sources') else ''
    impl.append(dict(id=f'php-i{i}', incident_id='php2shell', text=x['implication'], source_label=label_for(src) if src else '', source_url=src))
impl += EXTRA_IMPL

json.dump(victims, open(f'{OUT}/victims_php.json', 'w'), ensure_ascii=False, indent=0)
json.dump(timeline, open(f'{OUT}/timeline.json', 'w'), ensure_ascii=False, indent=0)
json.dump(impl, open(f'{OUT}/implications.json', 'w'), ensure_ascii=False, indent=0)
json.dump(DEEPDIVES, open(f'{OUT}/deepdives.json', 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print('php victims', len(victims), Counter(v['status_group'] for v in victims))
print('timeline', len(timeline), 'impl', len(impl), 'deepdives', len(DEEPDIVES))

# ---------------- PHP2Shell statements -> signals rows
AGENCY = ('NSA', 'CISA', 'NCSC', 'Canadian Centre', 'CERT', 'BSI', 'ANSSI', 'Australian Cyber Security Centre', 'KISA', 'JPCERT', 'Japan IPA',
          'Singapore', 'HKCERT', 'ThaiCERT', 'Switzerland', 'INCIBE', 'URSIV', 'Japan National Cybersecurity Office', 'FBI', 'ENISA', 'Belgium Centre', 'NHS', 'Tokyo Metropolitan Police', 'China MIIT')
LAB = ('OpenAI', 'Google DeepMind')
SECFIRM = ('Wiz', 'CrowdStrike', 'Sophos', 'watchTowr', 'Sansec', 'Patchstack', 'NCC Group', 'Huntress', 'Mondoo', 'Trail of Bits', 'SentinelOne', 'TLP:Black', 'Center for Internet Security', 'Calif')
GOV = ('Government', 'White House', 'Netherlands government', 'Germany Federal', 'Australian Government', 'Australian Home Affairs', 'South Korea', 'UK Government', 'Kenya', 'UK Office for Budget')
def otype(org):
    if org.startswith('Rep.'): return 'legislature'
    if any(org.startswith(x) or x in org for x in AGENCY): return 'security agency'
    if any(org.startswith(x) for x in LAB): return 'AI lab'
    if any(org.startswith(x) for x in SECFIRM): return 'security firm'
    if any(org.startswith(x) for x in GOV): return 'government'
    return 'tech company'
KEEP = [
 ('NSA', 'Press release'), ('NSA Cybersecurity Directorate', 'X post'), ('CISA', 'Alert'), ('UK NCSC', 'News alert'), ('Government of Canada', 'X post'),
 ('Government of Japan', 'X post'), ('White House', 'Press statement'), ('FBI Cyber Division', 'X post'), ('PHP Foundation', 'Blog post'), ('Amazon / AWS', 'Blog'),
 ('Wiz', 'Blog'), ('OpenAI', 'Blog'), ('OpenAI', 'X post'), ('Cloudflare', 'X post'), ('Chainguard', 'Public statement'), ('Sophos', 'Blog'),
 ('ENISA, European Commission', 'Joint statement'), ('Germany BSI', 'Interview'), ('Government of Japan', 'Press conference'), ('South Korea Ministry of Science and ICT', 'X post'),
 ('URSIV', 'Government press release'), ('Rep. Lori Trahan', 'X post'), ('Australian Government', 'Press'), ('UK Government', 'Press statement'), ('Trail of Bits', 'Interview'),
 ('CrowdStrike', 'Blog'), ('NCC Group', 'Press comment'), ('ThaiCERT', 'X post'),
]
HIGH = {'NSA', 'NSA Cybersecurity Directorate', 'CISA', 'Government of Canada', 'White House', 'FBI Cyber Division', 'PHP Foundation', 'Amazon / AWS', 'Wiz', 'OpenAI', 'Cloudflare', 'Sophos', 'South Korea Ministry of Science and ICT', 'UK Government'}
php_signals = []
used = set()
for k, (org, ch) in enumerate(KEEP):
    for j, st in enumerate(php['statements']):
        if j in used: continue
        if st['organization'].startswith(org) and st['channel'].startswith(ch):
            used.add(j)
            xp = str(st.get('x_post', 'no'))
            is_x = xp.startswith('http') or st['channel'].startswith('X post')
            url = xp if xp.startswith('http') else st['url']
            q = st.get('short_quote') or ''
            if q and len(q.split()) > 12: q = ''
            org_name = {'NSA Cybersecurity Directorate': 'NSA Cybersecurity', 'Amazon / AWS': 'Amazon (AWS)', 'ENISA, European Commission (DG CNECT), CERT-EU, Europol EC3, EU CSIRTs Network': 'EU (ENISA, CERT-EU, Europol, Commission)',
                        'URSIV / SI-CERT (Slovenia)': 'Slovenia (URSIV)', 'South Korea Ministry of Science and ICT': 'South Korea Science Ministry', 'Government of Japan': 'Government of Japan',
                        'Germany BSI': 'Germany BSI', 'FBI Cyber Division': 'FBI Cyber Division'}.get(st['organization'], st['organization'])
            gist = st['paraphrase']
            if is_x and not xp.startswith('http'):
                gist += ' (Post confirmed by press reports; direct link not located.)'
            php_signals.append(dict(id=f'php-s{k:02d}', date=st['date'], org=org_name, org_type=otype(st['organization']), speaker=st.get('speaker') or '',
                                    channel='X post' if is_x else st['channel'].split(' (')[0].split(' / ')[0], gist=gist, quote=q,
                                    related_incident='PHP2Shell', significance='high' if st['organization'] in HIGH else 'medium', url=url))
            break
    else:
        print('NOT FOUND', org, ch)
json.dump(php_signals, open(f'{OUT}/signals_php.json', 'w'), ensure_ascii=False, indent=0)
print('php signals', len(php_signals))
for s_ in php_signals: print(' ', s_['date'], s_['org_type'], '|', s_['org'], '|', s_['channel'], '|', s_['url'][:70])

# ================= other incidents (victims.json) + merged signals =================
from deep_other import (DEEPDIVES_OTHER, VMAP, V_EXTRA, TIMELINE_OTHER, IMPL_KEEP, STATEMENT_ADD, SIG_DROP, PHP_DROP,
                        SIG_RETAG, SIG_RETAG_ID, TRANSLUCE_NOTE, KOREA_HOW, MEX_HOW)
import datetime as _dt
from fixes2 import VDROP, VFIX, LABFIX, LAB_NEW, TDROP, TFIX, TADD, SIGFIX2, SIG_SUB, IMPLFIX
def _apply(row, fx):
    for k, v in fx.items():
        if k == 'extent_add': continue
        if isinstance(v, tuple):
            kind, a, b = v
            if kind == 'sub': assert a in row[k], (row['id'], a); row[k] = row[k].replace(a, b)
            else: n0 = row[k]; row[k] = re.sub(a, b, row[k]); assert row[k] != n0, (row['id'], a)
        else: row[k] = v
    if 'extent_add' in fx: row['extent'] = row['extent'].rstrip() + fx['extent_add']
vr = json.load(open(f'{R}/victims.json'))
LABMAP = {'lab-test-breaches': 'lab-test-breaches'}

def _d(s):
    m = re.fullmatch(r'(\d{4})-(\d{2})(?:-(\d{2}))?', s)
    if not m: return None
    return _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 15)), bool(m.group(3))

def date_parts(raw):
    toks = re.findall(r'\d{4}-\d{2}(?:-\d{2})?', raw)
    note = re.sub(r'[\d\-/+]|and|to', ' ', raw).strip(' ()').strip()
    note = re.sub(r'\s+', ' ', note).strip(' ()')
    if not toks:
        y = re.search(r'\d{4}', raw)
        return (y.group(0) + '-06-30' if y else ''), (y.group(0) if y else '') + (' (dates not disclosed)' if 'not' in raw else '')
    a, afull = _d(toks[0])
    def fmt(d, full): return d.strftime('%b %-d') if full else d.strftime('%b %Y')
    if '/' in raw and len(toks) >= 2:
        b, bfull = _d(toks[1])
        if afull and bfull:
            lab = ((a.strftime('%b %-d') + '–' + str(b.day)) if a.month == b.month else (a.strftime('%b %-d') + ' – ' + b.strftime('%b %-d'))) if a.year == b.year else (fmt(a, 1) + ', ' + str(a.year) + ' – ' + fmt(b, 1))
            if a.year != 2026 and a.year == b.year: lab += ', ' + str(a.year)
        elif not afull and not bfull and a.year == b.year:
            lab = a.strftime('%b') + ' – ' + b.strftime('%b %Y')
        else:
            lab = fmt(a, afull) + ' – ' + fmt(b, bfull)
    elif ' and ' in raw and len(toks) >= 2:
        b, bfull = _d(toks[1]); lab = fmt(a, afull) + ' and ' + fmt(b, bfull)
    else:
        lab = fmt(a, afull) + (' onward' if raw.endswith('+') else '')
        if afull and a.year != 2026: lab += ', ' + str(a.year)
    if 'before' in raw: lab = 'Before ' + lab
    for kw in ('discovered', 'found', 'disclosed', 'referenced'):
        if kw in raw and not raw.startswith('disclosed'): lab += f' ({kw})'
    if raw.startswith('disclosed'): lab = 'Disclosed ' + lab
    m2 = re.search(r'\((disclosed|reported|discovered) (\d{4}-\d{2}-\d{2})\)', raw)
    if m2: lab = fmt(a, afull) + f' ({m2.group(1)} ' + _dt.date.fromisoformat(m2.group(2)).strftime('%b %-d') + ')'
    return a.isoformat(), lab

ARTEX = {46, 47, 48, 49, 50, 51, 52, 53, 56, 57, 58, 59}
other_victims = []
for i, v in enumerate(vr['victims']):
    if i not in VMAP or i in VDROP: continue
    grp, lab, cnt, ov = VMAP[i]
    d0, dl = date_parts(v['date'])
    how = v['how']
    if i in ARTEX: how = KOREA_HOW
    if v['incident_id'] == 'mexico-government-breach-claude': how = MEX_HOW
    if ('transluce.org' in v['source_url'] or i in (35, 43)) and i != 20: how = how.rstrip('.') + '. ' + TRANSLUCE_NOTE
    row = dict(id=f'v-{i:02d}', incident_id=v['incident_id'], organization=v['organization'], sector=v['sector'],
               country='' if v['country'] in ('not disclosed', 'multiple') else v['country'],
               status=lab, status_group=grp, date=d0, date_label=dl, extent=v['extent'], how=how, count=cnt,
               source_url=v['source_url'], source_label=label_for(v['source_url']))
    row.update(ov)
    _apply(row, VFIX.get(i, {}))
    if 'source_url' in VFIX.get(i, {}): row['source_label'] = label_for(row['source_url'])
    other_victims.append(row)
for x in V_EXTRA + LAB_NEW:
    x = dict(x); _apply(x, LABFIX.get(x['id'], {}))
    x['country'] = '' if x['country'] == 'not disclosed' else x['country']; x['source_label'] = label_for(x['source_url'])
    other_victims.append(x)
all_victims = victims + other_victims
json.dump(all_victims, open(f'{OUT}/victims.json', 'w'), ensure_ascii=False, indent=0)

timeline_all = timeline + [dict(t, **TFIX.get(t['id'], {})) for t in TIMELINE_OTHER if t['id'] not in TDROP] + TADD
assert not (set(TFIX) - {t['id'] for t in TIMELINE_OTHER}), set(TFIX) - {t['id'] for t in TIMELINE_OTHER}
json.dump(timeline_all, open(f'{OUT}/timeline.json', 'w'), ensure_ascii=False, indent=0)

impl_all = list(impl)
for i in IMPL_KEEP:
    x = vr['implications'][i]
    t_, w_, u_ = IMPLFIX.get(i, (x['implication'], x['who'], None))
    impl_all.append(dict(id=f'oi-{i:02d}', incident_id=x['incident_id'], text=t_, source_label=w_, source_url=u_ or x['source_url']))
json.dump(impl_all, open(f'{OUT}/implications.json', 'w'), ensure_ascii=False, indent=0)

dd_all = [dict(d, related_ids='php2shell') for d in DEEPDIVES] + DEEPDIVES_OTHER
json.dump(dd_all, open(f'{OUT}/deepdives.json', 'w'), ensure_ascii=False, indent=0)

# ---- signals
agent = json.load(open(f'{R}/signals.json'))['signals']
sig = []
KEYS = ['id', 'date', 'org', 'org_type', 'speaker', 'channel', 'gist', 'quote', 'related_incident', 'significance', 'url']
for x in agent:
    if x['id'] in SIG_DROP: continue
    y = {k: (x.get(k) or '') for k in KEYS}
    y['related_incident'] = SIG_RETAG_ID.get(y['id'], SIG_RETAG.get(y['related_incident'], y['related_incident']))
    if y['quote'] and len(y['quote'].split()) > 14: y['quote'] = ''
    sig.append(y)
for x in php_signals:
    if x['id'] in PHP_DROP: continue
    sig.append({k: x.get(k, '') for k in KEYS})
for i, (org, ot, spk, ch, tag, signif, dov) in STATEMENT_ADD.items():
    s_ = vr['statements'][i]
    sig.append(dict(id=f'vs-{i:02d}', date=dov or s_['date'][:10], org=org, org_type=ot, speaker=spk, channel=ch, gist=s_['paraphrase'], quote='',
                    related_incident=tag, significance=signif, url=s_.get('url') or s_.get('source_url', '')))
for s_ in sig:
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', s_['date']), s_
    assert s_['url'].startswith('http'), s_
CH = {'blog post': 'blog', 'press statement': 'statement', 'public statement': 'statement', 'press comment': 'statement', 'joint statement': 'statement',
      'press/interview': 'interview', 'government press release': 'press release', 'alert': 'advisory', 'news alert': 'advisory', 'blog/advisory': 'advisory'}
TAG = {'midterms': 'Midterm elections', 'chatbot harms to minors': 'Chatbots and minors', 'Astra': 'GPT-6 Astra', 'Mythos': 'Mythos Preview'}
for s_ in sig:
    c = s_['channel']; c = c if c == 'X post' else c.lower(); s_['channel'] = CH.get(c, c)
    s_['related_incident'] = TAG.get(s_['related_incident'], s_['related_incident'])
SIG_FIX = {
 'trump-hoax-pacing': {'channel': 'Truth Social post'},
 'vdl-sotu-slow-down': {'channel': 'speech'},
 'unsc-france-ai-briefing': {'channel': 'briefing'},
 'takaichi-php-xpost': {'quote': ''},
 'vs-46': {'gist': "Added four June incidents to its public misalignment log, two rated critical: a government statistics site, an organization's internal systems reached during dashboard research, an unauthorized test-wallet payment, and a sandbox internet bypass."},
}
sig.append(dict(id='uk-gov-32-services', date='2026-10-22', org='UK Government', org_type='government', speaker='', channel='statement',
    gist='Confirmed that 32 government digital services were unavailable and four partially unavailable because of PHP2Shell, mostly precautionary shutdowns; the NCSC has issued about 50,000 warnings to organisations.', quote='',
    related_incident='PHP2Shell', significance='medium', url='https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'))
for s_ in sig: s_.update(SIG_FIX.get(s_['id'], {})); s_.update(SIGFIX2.get(s_['id'], {}))
for s_ in sig:
    if s_['id'] in SIG_SUB:
        a, b = SIG_SUB[s_['id']]; assert a in s_['gist'], s_['id']; s_['gist'] = s_['gist'].replace(a, b)
assert not (set(SIGFIX2) - {s_['id'] for s_ in sig}), set(SIGFIX2) - {s_['id'] for s_ in sig}
ids = [s_['id'] for s_ in sig]; assert len(ids) == len(set(ids))
json.dump(sig, open(f'{OUT}/signals.json', 'w'), ensure_ascii=False, indent=0)

from collections import Counter as C2
print('ALL victims', len(all_victims), C2((v['incident_id'], v['status_group']) for v in all_victims))
print('timeline', len(timeline_all), C2(t['incident_id'] for t in timeline_all))
print('impl', len(impl_all), C2(t['incident_id'] for t in impl_all))
print('deepdives', [d['incident_id'] for d in dd_all])
print('signals', len(sig), C2(s_['related_incident'] for s_ in sig))
print(C2(s_['org_type'] for s_ in sig), C2(s_['channel'] for s_ in sig))
