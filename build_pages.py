#!/usr/bin/env python3
"""Dispatch pages: a real page for every incident (i/<id>/), case (c/<id>/) and milestone (m/<id>/), built from data/*.json in the
site's design, plus i/, c/, m/ index pages, sitemap.xml and robots.txt. Each page carries its own title, description, share card
and Article JSON-LD, and links back to the interactive view on the front page. Run after build_site.py and make_cards.mjs."""
import json, os, re, html, datetime as dt, shutil
from zoneinfo import ZoneInfo

here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
L = lambda f: json.load(open(f'data/{f}.json', encoding='utf-8'))
meta = L('meta'); site = meta['site_url']
build = json.load(open('assets/build.json'))['build']
inc, fixes, caps, quotes, signals, dds, timeline, impl, victims = (L(f) for f in ('incidents', 'fixes', 'capabilities', 'quotes', 'signals', 'deepdives', 'timeline', 'implications', 'victims'))
esc = html.escape
AS_OF = meta['as_of']; AS_OF_DATE = AS_OF[:10]
ET = ZoneInfo('America/New_York')
as_of_label = dt.datetime.fromisoformat(AS_OF).astimezone(ET).strftime('%b %-d, %Y, %-I:%M %p ET')

# ---------- scoring: the same formula as assets/app.js compute()
TIERS = ['Minor', 'Moderate', 'Serious', 'Severe', 'Critical']
AUTONOMY = [('Tool', 'a person misused it'), ('Relied on', 'people trusted bad output'), ('Acted', 'the AI took a bounded action'), ('Autonomous', 'the AI ran multi-step operations'), ('Against intent', 'the AI worked against its operator')]
FACT = [('H', 'Harm', 5, 'damage actually done'), ('R', 'Reach', 5, 'who was affected'), ('A', 'Autonomy', 4, 'how much the AI did on its own'), ('N', 'Novelty', 5, 'how new the behavior was'), ('I', 'Permanence', 5, 'how hard it is to undo')]
def score(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    s = round(0.55 * harm + 0.45 * sig)
    t = 4 if s >= 80 else 3 if s >= 60 else 2 if s >= 40 else 1 if s >= 20 else 0
    return dict(harm_score=round(harm), signal_score=round(sig), severity=s, tier=TIERS[t], level='WS-%d' % (t + 1))
scored = [dict(r, **score(r)) for r in inc]
for i, r in enumerate(sorted(scored, key=lambda r: (r['date'], r['id']))): r['ws'] = 'WS-%04d' % (i + 1)
by_id = {r['id']: r for r in scored}
by_date = sorted(scored, key=lambda r: (r['date'], r['id']))
TIER_DOT = {'Minor': 'var(--line-2)', 'Moderate': 'color-mix(in oklab, var(--amber) 45%, var(--line-2))', 'Serious': 'var(--amber)', 'Severe': 'var(--alarm)', 'Critical': 'color-mix(in oklab, var(--alarm) 70%, var(--ink))'}
TIER_TEXT = {'Minor': 'var(--ink-2)', 'Moderate': 'var(--amber-text)', 'Serious': 'var(--amber-text)', 'Severe': 'var(--alarm-text)', 'Critical': 'color-mix(in oklab, var(--alarm) 70%, var(--ink))'}

def fdate(iso, precision='day'):
    if not iso: return ''
    d = dt.date.fromisoformat(iso[:10])
    return d.strftime('%b %Y') if precision == 'month' else d.strftime('%b %-d, %Y')
def first_sentence(t):
    t = (t or '').strip(); m = re.match(r'(.+?[.!?])(\s|$)', t); return (m.group(1) if m else t).strip()
def clip(t, n):
    t = (t or '').strip(); return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'
def link(u, label, cls=''):
    return f'<a href="{esc(u)}" target="_blank" rel="noopener noreferrer"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{esc(label)}</a>'
def initials(org):
    w = [x for x in re.split(r'[\s/,]+', org or '') if x and x[0].isalnum()]
    return ''.join(x[0] for x in w[:3]).upper() or '—'
def av_color(org_type):
    t = (org_type or '').lower()
    return 'var(--av-agency)' if 'agency' in t or 'security' in t else 'var(--av-gov)' if 'gov' in t or 'regulator' in t or 'legislat' in t or 'court' in t else 'var(--av-lab)'

# ---------- the shell (shared with build_tools.py)
from pageshell import shell, MARK, NAV, FOOT, SCRIPT

def article_ld(title, desc, url, img, published, section):
    d = {"@context": "https://schema.org", "@type": "Article", "headline": title[:110], "description": desc, "url": url, "mainEntityOfPage": url, "image": [img],
         "datePublished": published, "dateModified": AS_OF, "articleSection": section, "isAccessibleForFree": True,
         "author": {"@type": "Organization", "name": "Warning Shots", "url": site}, "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site, "logo": {"@type": "ImageObject", "url": site + "assets/icon-512.png"}}}
    return json.dumps(d, ensure_ascii=False).replace('</', '<\\/')

def share_html(url, text, card, deep, deep_label):
    x = 'https://twitter.com/intent/tweet?text=' + html.escape(__import__('urllib.parse').parse.quote(text)) + '&url=' + __import__('urllib.parse').parse.quote(url)
    parts = [f'<button type="button" data-copy="{esc(url)}">Copy link</button>', f'<a href="{x}" target="_blank" rel="noopener noreferrer">Post on X</a>']
    if card: parts.append(f'<a href="{esc(card)}" download>Card image</a>')
    parts.append(f'<a class="cta" href="{esc(deep)}">{esc(deep_label)}</a>')
    return '<div class="share">' + ''.join(parts) + '</div>'

def prevnext(prev, nxt, kind, label_of, sub_of):
    if not prev and not nxt: return ''
    out = ['<nav class="prevnext" aria-label="Previous and next">']
    out.append(f'<a href="/{kind}/{esc(prev["id"])}/"><span class="k">← Earlier</span>{esc(clip(label_of(prev), 90))}<br><span class="k">{esc(sub_of(prev))}</span></a>' if prev else '<span></span>')
    out.append(f'<a class="next" href="/{kind}/{esc(nxt["id"])}/"><span class="k">Later →</span>{esc(clip(label_of(nxt), 90))}<br><span class="k">{esc(sub_of(nxt))}</span></a>' if nxt else '<span></span>')
    out.append('</nav>'); return ''.join(out)

def card_for(kind, slug):
    return f'{site}cards/{kind}-{slug}.jpg' if os.path.exists(f'cards/{kind}-{slug}.jpg') else f'{site}assets/og.png?v={build}'

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)

# ---------- indexes for the related sections
fix_by_inc = {f['incident_id']: f for f in fixes}
dd_by_inc = {d['incident_id']: d for d in dds}
quotes_by_inc = {}
for q in quotes: quotes_by_inc.setdefault(q.get('incident_id') or '', []).append(q)
signals_by_tag = {}
for s in signals: signals_by_tag.setdefault(s.get('related_incident') or '', []).append(s)
tl_by_inc = {}
for t in timeline: tl_by_inc.setdefault(t['incident_id'], []).append(t)
impl_by_inc = {}
for x in impl: impl_by_inc.setdefault(x['incident_id'], []).append(x)
vic_by_inc = {}
for v in victims: vic_by_inc.setdefault(v['incident_id'], []).append(v)
caps_by_inc = {}
for c in caps:
    for rid in (c.get('related_incident_ids') or []): caps_by_inc.setdefault(rid, []).append(c)
STAGES = [('demonstrated', 'Demonstrated', 'shown once, by its developer or a researcher'), ('reproduced', 'Reproduced', 'shown again by someone else'), ('accessible', 'Accessible', 'available to the public or to customers'), ('reliable', 'Reliable', 'works most of the time on a defined task'), ('consequences', 'Real consequences', 'has changed something in the world, for good or ill')]
CHAIN = {'reported': 'Reported', 'response': 'Response', 'claimed_fix': 'Claimed fix', 'retest': 'Independent check', 'current': 'Where it stands'}
def cur_of(f): return next((c for c in f['chain'] if c['stage'] == 'current'), {})
def cur_status(f): return (cur_of(f).get('status') or 'unresolved')
VGROUP = [('confirmed', 'confirmed compromised'), ('reported', 'reported hit'), ('attacked', 'attacked or abused'), ('disrupted', 'took services offline'), ('other', 'other'), ('unnamed', 'unnamed')]

def chain_html(f, compact=False):
    out = ['<ol class="chain">']
    for c in f['chain']:
        stage, status = c['stage'], (c.get('status') or '')
        cls = 'cur' if stage == 'current' else ('missing' if status in ('none', 'missing', 'no') else 'done')
        chip = f'<span class="stt {esc(status)}">{esc(status.replace("_", " "))}</span>' if stage == 'current' else (f'<span class="stt">{esc(status.replace("_", " "))}</span>' if status and status != 'done' else '')
        note = c.get('note') or ''
        if compact: note = clip(note, 240)
        src = (' ' + link(c['source_url'], 'source', 'k')) if c.get('source_url') else ''
        out.append(f'<li class="{cls}"><div class="st"><b>{esc(CHAIN.get(stage, stage))}</b>{(" " + esc(fdate(c["date"]))) if c.get("date") else ""} {chip}</div><p>{esc(note)}{src}</p></li>')
    out.append('</ol>'); return ''.join(out)

# ---------- incident pages
urls = []
def incident_page(r, prev, nxt):
    url = f'{site}i/{r["id"]}/'; img = card_for('i', r['id'])
    tier_dot = TIER_DOT[r['tier']]
    disclosed = ''
    if r.get('disclosed') and r['disclosed'][:10] != r['date'][:10]:
        lag = (dt.date.fromisoformat(r['disclosed'][:10]) - dt.date.fromisoformat(r['date'][:10])).days
        disclosed = f'<span class="dot">·</span><span>disclosed {esc(fdate(r["disclosed"]))}{(" (" + str(lag) + " days later)") if lag > 0 else ""}</span>'
    kick = f'<div class="kicker"><span>Incident</span><span class="dot">·</span><b>{r["ws"]}</b><span class="dot">·</span><span>{esc(fdate(r["date"], r.get("date_precision")))}</span>{disclosed}<span class="dot">·</span><span>{"in the wild" if r["setting"] == "wild" else "in the lab"}</span><span class="dot">·</span><span>{esc(r.get("category_label") or "")}</span></div>'
    aut = AUTONOMY[int(r['A'])]
    factors = ''.join(f'<div class="factor">{lab} <span class="fv">{r[k]}</span>/{mx}<div class="ft"><i style="width:{int(r[k]) / mx * 100:.0f}%"></i></div><div class="fd">{d}</div></div>' for k, lab, mx, d in FACT)
    scorebox = f'<div class="score"><div class="big">{r["severity"]}<small>/100</small></div><span class="pill"><i style="background:{tier_dot}"></i>{r["level"]} {r["tier"]}</span><div class="sub">Harm score <b>{r["harm_score"]}</b>, signal score <b>{r["signal_score"]}</b>. Autonomy: <b>{aut[0].lower()}</b> ({aut[1]}). <a href="/index/#about">How the scores work</a>.</div><div class="factors" style="flex-basis:100%">{factors}</div></div>'
    body = [kick, f'<h1>{esc(r["title"])}</h1>']
    if r.get('actors'): body.append(f'<p class="meta">{esc(r["actors"])}</p>')
    body.append(scorebox)
    body.append(f'<p class="lede">{esc(r["summary"])}</p>')
    body.append(f'<section><h2>Damage</h2><p>{esc(r["harm"])}</p></section>')
    dd = dd_by_inc.get(r['id'])
    if dd:
        paras = [(dd.get('how'), 'How it happened'), (dd.get('ai_role'), 'The AI’s role'), (dd.get('damage'), 'Damage so far'), (dd.get('why'), 'Why it matters')]
        body.append('<section><h2>Inside the incident</h2>' + ''.join(f'<h3 style="margin-top:14px">{esc(h)}</h3><p>{esc(t)}</p>' for t, h in paras if t) + f'<p class="k" style="margin-top:12px"><a href="/index/#d={esc(r["id"])}">Every organization named, the map and the full timeline on the index →</a></p></section>')
        vs = vic_by_inc.get(r['id'], [])
        if vs:
            def n(v): c = v.get('count'); return 1 if c in ('', None) or not str(c).replace('.', '').isdigit() else int(float(c))
            counts = [(lab, sum(n(v) for v in vs if v['status_group'] == g)) for g, lab in VGROUP]
            counts = [(lab, c) for lab, c in counts if c]
            order = {g: i for i, (g, _) in enumerate(VGROUP)}
            top = sorted([v for v in vs if v['status_group'] != 'unnamed'], key=lambda v: (order.get(v['status_group'], 9), v.get('date') or ''))[:8]
            rows = ''.join(f'<li><span class="t">{esc(v["organization"])}<small>{esc(", ".join(x for x in [v.get("sector"), v.get("country"), v.get("status")] if x))}{(" · " + clip(v.get("extent"), 140)) if v.get("extent") else ""}</small></span></li>' for v in top)
            body.append(f'<section><h2>Organizations affected</h2><p class="meta">{esc("; ".join(f"{c} {lab}" for lab, c in counts))}. “Reported” means an outlet or researcher says so and the organization has not confirmed.</p><ul class="rows">{rows}</ul><p class="k" style="margin-top:10px"><a href="/index/#d={esc(r["id"])}">All {len(vs)} entries, filterable, on the index →</a></p></section>')
        tl = sorted(tl_by_inc.get(r['id'], []), key=lambda t: t['date'], reverse=True)[:10]
        if tl:
            body.append('<section><h2>Timeline</h2><ol class="tl">' + ''.join(f'<li><span class="d">{esc(t.get("date_label") or fdate(t["date"]))}</span><span>{esc(t["event"])}{(link(t["source_url"], "source", "s")) if t.get("source_url") else ""}</span></li>' for t in tl) + '</ol>' + (f'<p class="k" style="margin-top:10px">Latest {len(tl)} of {len(tl_by_inc[r["id"]])} events; <a href="/index/#d={esc(r["id"])}">the full timeline is on the index</a>.</p>' if len(tl_by_inc[r['id']]) > len(tl) else '') + '</section>')
        sigs = sorted(signals_by_tag.get(dd.get('signal_tag') or '', []), key=lambda s: s['date'], reverse=True)[:6]
        if sigs:
            body.append('<section><h2>What officials said</h2>' + ''.join(f'<div class="sig"><div class="av" style="background:{av_color(s.get("org_type"))}">{esc(initials(s["org"]))}</div><div><b>{esc(s["org"])}</b>{(" " + esc(s["speaker"])) if s.get("speaker") else ""}<div>{esc(s["gist"])}</div><div class="sm">{esc(fdate(s["date"]))}{(" · <b>" + esc(s["channel"]) + "</b>") if s.get("channel") else ""}{(" · " + link(s["url"], "Source")) if s.get("url") else ""}</div></div></div>' for s in sigs) + '</section>')
        ims = impl_by_inc.get(r['id'], [])
        if ims:
            body.append('<section class="imp"><h2>What it means next</h2>' + ''.join(f'<p>{esc(x["text"])}<small>{link(x["source_url"], x.get("source_label") or "source") if x.get("source_url") else esc(x.get("source_label") or "")}</small></p>' for x in ims) + '</section>')
    qs = sorted(quotes_by_inc.get(r['id'], []), key=lambda q: (-(float(q.get('weight') or 0)), q.get('date') or ''))[:3]
    if qs:
        body.append('<section><h2>In their words</h2>' + ''.join(f'<div class="q"><blockquote>“{esc(q["quote"])}”</blockquote><div class="who"><b>{esc(q["speaker"])}</b>{(", " + esc(q["title"])) if q.get("title") else ""} · {esc(fdate(q["date"]))}{(" · " + link(q["url"], "source")) if q.get("url") else ""}</div></div>' for q in qs) + '</section>')
    f = fix_by_inc.get(r['id'])
    if f:
        st = cur_status(f)
        body.append(f'<section><h2>Did they fix it?</h2><p class="meta"><span class="stt {esc(st)}">{esc(st.replace("_", " "))}</span> {esc(f.get("one_liner") or "")}</p>{chain_html(f, compact=True)}<p class="k"><a href="/c/{esc(f["incident_id"])}/">The full case, with what would change the verdict →</a></p></section>')
    cs = sorted(caps_by_inc.get(r['id'], []), key=lambda c: c['date'], reverse=True)
    if cs:
        body.append('<section><h2>The capability behind it</h2><ul class="rows">' + ''.join(f'<li><span class="t"><a href="/m/{esc(c["id"])}/">{esc(c["title"])}</a><small>{esc(fdate(c["date"], c.get("date_precision")))} · {esc(c.get("org") or "")} · reliable for a defined task: {esc(((c.get("stages") or {}).get("reliable") or {}).get("status") or "unknown")}</small></span></li>' for c in cs) + '</ul></section>')
    srcs = [(r.get('source_url'), r.get('source_label') or 'primary source'), (r.get('source2_url'), 'second source'), (r.get('source3_url'), 'third source')]
    src = ', '.join(link(u, l) for u, l in srcs if u)
    conf = f' Evidence confidence: {esc(r["confidence"])}.' if r.get('confidence') and r['confidence'] != 'high' else ''
    notes = (' ' + esc(r['notes'])) if r.get('notes') else ''
    body.append(f'<section class="src"><h2>Sources</h2><p>{src}.{conf}{notes}</p><p class="k">Factor ratings and the score are this index’s judgments by a published formula; facts, dates and figures come from the linked sources. Where a lawsuit is pending, the summary reports allegations, not findings.</p></section>')
    share_text = f'{r["title"]} ({r["severity"]}/100, {r["tier"].lower()}). {first_sentence(r["summary"])} Warning Shots:'
    body.append(share_html(url, share_text, f'/cards/i-{r["id"]}.jpg' if os.path.exists(f'cards/i-{r["id"]}.jpg') else '', f'/#i={r["id"]}', 'Open on the index'))
    body.append(prevnext(prev, nxt, 'i', lambda x: x['title'], lambda x: f'{x["ws"]} · {fdate(x["date"], x.get("date_precision"))} · {x["severity"]}/100 {x["tier"]}'))
    desc = f'{first_sentence(r["summary"])} {r["tier"]}, {r["severity"]}/100. {"Real-world incident" if r["setting"] == "wild" else "Lab or test finding"}, {fdate(r["date"], r.get("date_precision"))}. Scored and sourced by Warning Shots.'
    write(f'i/{r["id"]}/index.html', shell(title=r['title'], desc=desc[:300], url=url, img=img, body='\n'.join(body), jsonld=article_ld(r['title'], desc[:300], url, img, (r.get('disclosed') or r['date'])[:10], 'Incidents'), kind='incident'))
    return url

for i, r in enumerate(by_date):
    urls.append(incident_page(r, by_date[i - 1] if i > 0 else None, by_date[i + 1] if i + 1 < len(by_date) else None))

# ---------- case pages
def case_page(f, prev, nxt):
    url = f'{site}c/{f["incident_id"]}/'; img = card_for('c', f['incident_id']); r = by_id.get(f['incident_id'])
    st = cur_status(f); cur = cur_of(f)
    kick = f'<div class="kicker"><span>Did they fix it?</span><span class="dot">·</span><b>{esc(st.replace("_", " "))}</b>{("<span class=dot>·</span><span>checked " + esc(fdate(cur["date"])) + "</span>") if cur.get("date") else ""}<span class="dot">·</span><span>re-checked every refresh</span></div>'
    body = [kick, f'<h1>{esc(f["name"])}</h1>', f'<p class="lede">{esc(f.get("one_liner") or cur.get("note") or "")}</p>']
    if r:
        body.append(f'<div class="score"><div class="big">{r["severity"]}<small>/100</small></div><span class="pill"><i style="background:{TIER_DOT[r["tier"]]}"></i>{r["level"]} {r["tier"]}</span><div class="sub">Incident <b>{r["ws"]}</b>, {esc(fdate(r["date"], r.get("date_precision")))}: <a href="/i/{esc(r["id"])}/">{esc(r["title"])}</a></div></div>')
    body.append('<section><h2>The chain</h2><p class="meta">The report, the responsible party’s response, the fix they claimed, whether anyone independent checked, and where it stands. A company saying it fixed something and evidence that the fix worked are different rows.</p>' + chain_html(f) + '</section>')
    if f.get('what_would_change_it'): body.append(f'<section><h2>What would change the verdict</h2><p>{esc(f["what_would_change_it"])}</p></section>')
    body.append(f'<section class="src"><h2>Method</h2><p>Statuses move only on evidence: <b>fixed</b> needs an independent party confirming the fix under stated conditions; <b>unverified</b> is a claimed fix nobody independent has checked; <b>disputed</b>, <b>reopened</b> (recurred after a claimed fix), <b>unresolved</b> (no fix claimed), <b>ongoing</b> (still unfolding). “No public response found” is a valid entry; nothing here is invented.{(" Evidence confidence: " + esc(f["confidence"]) + ".") if f.get("confidence") and f["confidence"] != "high" else ""}</p></section>')
    share_text = f'Did they fix it? {f["name"]}: {f.get("one_liner") or cur.get("note") or ""} Warning Shots:'
    body.append(share_html(url, share_text, f'/cards/c-{f["incident_id"]}.jpg' if os.path.exists(f'cards/c-{f["incident_id"]}.jpg') else '', f'/index/#c={f["incident_id"]}', 'Open on the index'))
    body.append(prevnext(prev, nxt, 'c', lambda x: x['name'], lambda x: 'Status: ' + cur_status(x).replace('_', ' ')) if (prev or nxt) else '')
    desc = ('Did they fix it? ' + (f.get('one_liner') or cur.get('note') or ''))[:300]
    rid = r['date'] if r else AS_OF_DATE
    write(f'c/{f["incident_id"]}/index.html', shell(title=f['name'], desc=desc, url=url, img=img, body='\n'.join(body), jsonld=article_ld(f['name'], desc, url, img, rid[:10], 'Did they fix it?'), kind='case'))
    return url

cases = [dict(f, id=f['incident_id']) for f in fixes]
for i, f in enumerate(cases):
    urls.append(case_page(f, cases[i - 1] if i > 0 else None, cases[i + 1] if i + 1 < len(cases) else None))

# ---------- milestone pages
def milestone_page(c, prev, nxt):
    url = f'{site}m/{c["id"]}/'; img = card_for('m', c['id'])
    kick = f'<div class="kicker"><span>What AI can now do</span><span class="dot">·</span><span>{esc(fdate(c["date"], c.get("date_precision")))}</span><span class="dot">·</span><b>{esc((c.get("domain") or "").capitalize())}</b></div>'
    body = [kick, f'<h1>{esc(c["title"])}</h1>']
    if c.get('org'): body.append(f'<p class="meta">{esc(c["org"])}</p>')
    if c.get('metric_value'): body.append(f'<div class="metric"><b>{esc(c["metric_value"])}</b><span>{esc(c.get("metric_label") or "")}</span></div>')
    body.append(f'<p class="lede">{esc(c.get("what") or "")}</p>')
    st = c.get('stages') or {}
    rows = []
    for k, lab, d in STAGES:
        s = st.get(k) or {}; status = s.get('status') or 'unknown'
        rows.append(f'<div class="stage"><div class="sn">{lab}<small>{d}</small></div><div class="sd"><span class="{esc(status)}">{esc(status)}</span>{(" · " + esc(fdate(s["date"]))) if s.get("date") else ""}{(" · " + esc(s["note"])) if s.get("note") else ""}{(" " + link(s["source_url"], "source", "k")) if s.get("source_url") else ""}</div></div>')
    body.append('<section><h2>How far it has travelled</h2><p class="meta">From a demonstration to real life, in five steps. Empty steps are the point: a demonstration is not a deployment.</p><div class="stages">' + ''.join(rows) + '</div></section>')
    if c.get('everyday'): body.append(f'<section><h2>What this could change for you</h2><p>{esc(c["everyday"])}</p></section>')
    rel = [by_id[i] for i in (c.get('related_incident_ids') or []) if i in by_id]
    if rel:
        body.append('<section><h2>Incidents it made possible</h2><ul class="rows">' + ''.join(f'<li><span class="n" style="color:{TIER_TEXT[x["tier"]]}">{x["severity"]}</span><span class="t"><a href="/i/{esc(x["id"])}/">{esc(x["title"])}</a><small>{x["ws"]} · {esc(fdate(x["date"], x.get("date_precision")))} · {x["level"]} {x["tier"]}</small></span></li>' for x in sorted(rel, key=lambda x: -x['severity'])) + '</ul></section>')
    src = ', '.join(link(u, l) for u, l in [(c.get('source_url'), 'primary source'), (c.get('source2_url'), 'second source')] if u)
    body.append(f'<section class="src"><h2>Sources</h2><p>{src}.{(" Evidence confidence: " + esc(c["confidence"]) + ".") if c.get("confidence") and c["confidence"] != "high" else ""}</p><p class="k">A milestone is a dated, sourced result that moved what AI can do; a stage is upgraded only when a source shows it (a reproduction, a public release, production evidence, a documented consequence). “Unknown” is the honest default.</p></section>')
    share_text = f'What AI can now do: {c["title"]}. {first_sentence(c.get("what"))} Warning Shots:'
    body.append(share_html(url, share_text, f'/cards/m-{c["id"]}.jpg' if os.path.exists(f'cards/m-{c["id"]}.jpg') else '', f'/index/#m={c["id"]}', 'Open on the index'))
    body.append(prevnext(prev, nxt, 'm', lambda x: x['title'], lambda x: fdate(x['date'], x.get('date_precision')) + ' · ' + (x.get('org') or '')))
    desc = ((c.get('what') or '') + ' Graded from demonstration to real consequences by Warning Shots.')[:300]
    write(f'm/{c["id"]}/index.html', shell(title=c['title'], desc=desc, url=url, img=img, body='\n'.join(body), jsonld=article_ld(c['title'], desc, url, img, c['date'][:10], 'What AI can now do'), kind='milestone'))
    return url

cap_sorted = sorted(caps, key=lambda c: (c['date'], c['id']))
for i, c in enumerate(cap_sorted):
    urls.append(milestone_page(c, cap_sorted[i - 1] if i > 0 else None, cap_sorted[i + 1] if i + 1 < len(cap_sorted) else None))

# ---------- index pages
def index_page(kind, title, lede, rows_html, desc):
    url = f'{site}{kind}/'
    body = f'<div class="index-head"><h1>{esc(title)}</h1><span class="k">{len(rows_html)} entries · last refresh {esc(as_of_label)}</span></div><p class="lede quiet">{lede}</p><ul class="rows">{"".join(rows_html)}</ul>'
    write(f'{kind}/index.html', shell(title=title, desc=desc, url=url, img=f'{site}assets/og.png?v={build}', body=body, jsonld=json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": url, "description": desc, "dateModified": AS_OF, "isPartOf": {"@id": site + "#site"}}, ensure_ascii=False), kind='index'))
    return url

inc_rows = [f'<li><span class="n" style="color:{TIER_TEXT[x["tier"]]}">{x["severity"]}</span><span class="t"><a href="/i/{esc(x["id"])}/">{esc(x["title"])}</a><small>{x["ws"]} · {esc(fdate(x["date"], x.get("date_precision")))} · {x["level"]} {x["tier"]} · {"real-world" if x["setting"] == "wild" else "lab or test"}</small></span></li>' for x in sorted(scored, key=lambda x: (x['date'], x['id']), reverse=True)]
urls.append(index_page('i', 'All incidents', f'Every incident on the index, newest first: {len(scored)} since 2023, each scored 0–100 by a <a href="/index/#about">published formula</a> and linked to its sources. <a href="/index/#all">Sort, filter and search them on the front page</a>.', inc_rows, f'{len(scored)} AI incidents since 2023, scored 0–100 and sourced, newest first. Warning Shots.'))
case_rows = [f'<li><span class="t"><a href="/c/{esc(f["incident_id"])}/">{esc(f["name"])}</a><small><span class="stt {esc(cur_status(f))}">{esc(cur_status(f).replace("_", " "))}</span> {esc(clip(f.get("one_liner") or "", 160))}</small></span></li>' for f in fixes]
urls.append(index_page('c', 'Did they fix it?', 'What happened after the headline, for each major incident: the report, the response, the claimed fix, whether anyone independent checked, and where it stands. Re-checked every refresh.', case_rows, 'For each major AI incident: the report, the response, the claimed fix, whether anyone independent checked, and where it stands today. Warning Shots.'))
cap_rows = [f'<li><span class="t"><a href="/m/{esc(c["id"])}/">{esc(c["title"])}</a><small>{esc(fdate(c["date"], c.get("date_precision")))} · {esc(c.get("org") or "")} · {esc((c.get("domain") or "").capitalize())} · reliable: {esc(((c.get("stages") or {}).get("reliable") or {}).get("status") or "unknown")}</small></span></li>' for c in sorted(caps, key=lambda c: c['date'], reverse=True)]
urls.append(index_page('m', 'What AI can now do', 'Dated, sourced results that moved what AI can do, each graded from demonstration to real consequences. The breakthroughs and the incidents come from the same capabilities.', cap_rows, f'{len(caps)} AI capability milestones since 2023, graded from demonstration to real consequences. Warning Shots.'))

# ---------- the tools (built by build_tools.py) go in the sitemap too
try:
    urls += [u for u in json.load(open('data/tool_urls.json')) if u not in urls]
except (OSError, ValueError):
    pass

# ---------- the live-incident tracker (build_tracker.py)
if os.path.exists('php2shell/index.html') and site + 'php2shell/' not in urls:
    urls.insert(0, site + 'php2shell/')
if os.path.exists('index/index.html') and site + 'index/' not in urls:
    urls.insert(0, site + 'index/')
if os.path.exists('wire/index.html') and site + 'wire/' not in urls:
    urls.insert(0, site + 'wire/')

# ---------- prune pages for records that no longer exist
keep = {u.replace(site, '') for u in urls}
for kind in ('i', 'c', 'm'):
    if os.path.isdir(kind):
        for slug in os.listdir(kind):
            if os.path.isdir(os.path.join(kind, slug)) and f'{kind}/{slug}/' not in keep:
                shutil.rmtree(os.path.join(kind, slug), ignore_errors=True)

# ---------- sitemap + robots
lastmod = AS_OF_DATE
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', f'<url><loc>{esc(site)}</loc><lastmod>{lastmod}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority></url>']
for u in urls:
    sm.append(f'<url><loc>{esc(u)}</loc><lastmod>{lastmod}</lastmod></url>')
sm.append('</urlset>')
open('sitemap.xml', 'w', encoding='utf-8').write('\n'.join(sm))
# ---------- Google News sitemap: pages for incidents disclosed in the last 48 hours, plus the live tracker
_now = dt.datetime.fromisoformat(AS_OF)
_news = []
if os.path.exists('php2shell/index.html'):
    _news.append((site + 'php2shell/', 'PHP2Shell live tracker: exploitation, victims, CISA KEV status'))
for r in scored:
    d = r.get('disclosed') or r['date']
    try:
        if len(d) >= 10 and (_now.date() - dt.date.fromisoformat(d[:10])).days <= 2:
            _news.append((f'{site}i/{r["id"]}/', r['title']))
    except ValueError:
        pass
ns = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">']
for u, t in _news:
    ns.append(f'<url><loc>{esc(u)}</loc><news:news><news:publication><news:name>Warning Shots</news:name><news:language>en</news:language></news:publication><news:publication_date>{AS_OF}</news:publication_date><news:title>{esc(t[:110])}</news:title></news:news></url>')
ns.append('</urlset>')
open('news-sitemap.xml', 'w', encoding='utf-8').write('\n'.join(ns))
json.dump([u for u, _ in _news], open('data/fresh_urls.json', 'w'))
open('robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {site}sitemap.xml\nSitemap: {site}news-sitemap.xml\n')
print('pages', len(urls), '(incidents', len(scored), 'cases', len(fixes), 'milestones', len(caps), '+ 3 indexes), sitemap written')
