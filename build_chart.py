#!/usr/bin/env python3
"""The Charts: one original, shareable chart a day, built from the index's own data.

research/charts.json lists the charts: {id, date, kind, title?, dek?, takeaway?, pin?}. Each `kind` is a renderer below
that returns the finding (title, dek, takeaway), a legend, the data table and a plot function. Every chart is drawn twice:
wide (16:9, 1200x675: web, X, LinkedIn, TV) and tall (4:5, 1080x1350: phones, Instagram, stories). Title, source line and
the citation are baked into both images, so a chart carries its citation wherever it goes.

Writes: assets/charts/<id>.svg and <id>-tall.svg (make_charts.mjs turns them into PNGs), chart/<id>/index.html (the
chart, why it matters, share buttons, embed code, the data), chart/index.html (the gallery), data/chart.json (today's,
for the homepage).  Run before build_site.py:  python3 build_chart.py
"""
import json, os, datetime as dt, html, collections, urllib.parse
from pagekit import write, register, SITE, footer_note, webpage, fdate

esc = html.escape
L = lambda f: json.load(open(f, encoding='utf-8'))
meta = L('data/meta.json')
AS_OF = meta['as_of'][:10]

# Palette, validated on the navy surface (dataviz skill): muted slates are context, never a category; the alarm red marks
# the one thing that matters and is always labelled. Ordinal context steps differ in lightness and carry direct labels.
NAVY, PAPER, INK2, GRID, MUTED, DIM, RED = '#0A111E', '#F4F3EF', '#A8B3C2', '#22304A', '#6F7F96', '#3E4B62', '#FF3B14'
FS = "Archivo, 'Archivo Fallback', Arial, sans-serif"
FD = "Playfair, 'Playfair Fallback', Georgia, serif"
FORMATS = {'wide': (1200, 675), 'tall': (1080, 1350)}

def score(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    return round(0.55 * harm + 0.45 * sig)

def wrap(text, n):
    lines, cur = [], ''
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    return lines + ([cur] if cur else [])

def T(x, y, s, size, fill=PAPER, font=FS, weight=400, anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(str(s))}</text>'

def card(fmt, c):
    """Header (title, dek, legend), the plot in the remaining box, and the footer with source and citation."""
    W, H = FORMATS[fmt]; tall = fmt == 'tall'
    m = 56 if tall else 48
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c["aria"])}" class="ws-chart">', f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']
    tsize, tlh, tchars = (58, 64, 26) if tall else (38, 44, 54)
    y = m + tsize * 0.9
    for line in wrap(c['title'], tchars):
        out.append(T(m, y, line, tsize, PAPER, FD, 900)); y += tlh
    dsize, dchars = (25, 66) if tall else (18, 110)
    y += 2
    for line in wrap(c['dek'], dchars):
        out.append(T(m, y, line, dsize, INK2)); y += dsize * 1.4
    lx, ly = m, y + (18 if tall else 12)
    for color, r, label in c['legend']:
        cx, cy = lx + 6, ly - 5
        if color == 'half':
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 1}" fill="none" stroke="{PAPER}" stroke-width="2"/><path d="M{cx} {cy - r + 1} A{r - 1} {r - 1} 0 0 0 {cx} {cy + r - 1} Z" fill="{PAPER}"/>')
        elif color == 'ring':
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 1}" fill="none" stroke="{DIM}" stroke-width="2"/>')
        else:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
        out.append(T(lx + 6 + r + 8, ly, label, 22 if tall else 14))
        lx += 6 + r + 8 + len(label) * (11 if tall else 7.2) + 30
    top = ly + (40 if tall else 30)
    foot = 96 if tall else 58
    box = (m + (34 if tall else 24), top, W - m, H - foot)
    out.append(c['plot'](box, tall))
    if tall:
        out.append(T(m, H - 58, c['source'], 18, INK2))
        out.append(f'<text x="{m}" y="{H - 24}" fill="{PAPER}" font-family="{FD}" font-weight="700" font-size="22" letter-spacing="3.3">W<tspan fill="{RED}">:</tspan> WARNING SHOTS · warningshots.ai</text>')
    else:
        out.append(T(m, H - 22, c['source'], 13, INK2))
        out.append(f'<text x="{W - m}" y="{H - 22}" text-anchor="end" fill="{PAPER}" font-family="{FD}" font-weight="700" font-size="15" letter-spacing="2.4">W<tspan fill="{RED}">:</tspan> WARNING SHOTS · warningshots.ai</text>')
    out.append('</svg>')
    return ''.join(out)

def scored():
    rows = []
    for r in L('data/incidents.json'):
        rows.append(dict(r, sev=score(r)))
    rows.sort(key=lambda r: (r['date'], r['id']))
    for i, r in enumerate(rows):
        r['ws'] = 'WS-%04d' % (i + 1)
    return rows

SRC_INDEX = f'Source: Warning Shots AI Incident Index, scored 0–100 by a published formula. Data as of {fdate(AS_OF)}.'

# ---------------------------------------------------------------- kind: every incident as a dot, by date and severity
def incident_field(spec):
    rows = scored()
    d0, d1 = dt.date(2023, 1, 1), dt.date.fromisoformat(AS_OF)
    yr = dt.timedelta(days=365.25)
    last = [r for r in rows if d1 - yr < dt.date.fromisoformat(r['date']) <= d1]
    prev = [r for r in rows if d1 - 2 * yr < dt.date.fromisoformat(r['date']) <= d1 - yr]
    a, b = sum(r['sev'] >= 60 for r in prev), sum(r['sev'] >= 60 for r in last)
    topr = max(rows, key=lambda r: (r['sev'], r['date']))
    def plot(box, tall):
        left, top, right, bot = box
        fs = 20 if tall else 13
        X = lambda d: left + (right - left) * (d - d0).days / max(1, (d1 - d0).days)
        Y = lambda s: bot - 34 - (bot - 34 - top - 30) * s / 100
        out = []
        xa, xb, xc = X(d1 - 2 * yr), X(d1 - yr), X(d1)
        out.append(f'<rect x="{xb:.1f}" y="{top}" width="{xc - xb:.1f}" height="{bot - 34 - top:.1f}" fill="{RED}" fill-opacity="0.07"/>')
        out.append(T((xa + xb) / 2, top + 20, f'Year before: {a} severe', fs + 1, INK2, anchor='middle'))
        out.append(T((xb + xc) / 2, top + 20, f'Last 12 months: {b} severe', fs + 1, RED, weight=700, anchor='middle'))
        for s in (0, 20, 40, 60, 80, 100):
            y = Y(s); sev = s == 60
            out.append(f'<line x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{RED if sev else GRID}" stroke-width="{1.2 if sev else 1}" {"stroke-dasharray=\"5 5\" stroke-opacity=\".75\"" if sev else ""}/>')
            out.append(T(left - 10, y + fs * .35, s, fs, INK2, anchor='end'))
        out.append(T(left + 8, Y(60) - 8, 'SEVERE: 60 AND ABOVE', fs, RED, weight=700, extra='letter-spacing="1"'))
        for yv in range(d0.year, d1.year + 1):
            x = X(dt.date(yv, 1, 1))
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{bot - 34}" y2="{bot - 26}" stroke="{INK2}"/>'); out.append(T(x, bot - 6, yv, fs + 1, INK2))
        placed = []
        for r in sorted(rows, key=lambda r: r['sev']):
            sev = r['sev'] >= 60; rad = (9 if tall else 6.5) if sev else (6 if tall else 4.5)
            x, y = X(dt.date.fromisoformat(r['date'])), Y(r['sev'])
            for k in range(16):
                dx = (k + 1) // 2 * (1 if k % 2 else -1) * (rad * .7)
                if left + rad <= x + dx <= right - rad and all((x + dx - px) ** 2 + (y - py) ** 2 >= (rad + pr + 1) ** 2 for px, py, pr in placed):
                    x += dx; break
            placed.append((x, y, rad))
            out.append(f'<a href="/i/{esc(r["id"])}/"><circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{RED if sev else MUTED}" stroke="{NAVY}" stroke-width="2"><title>{esc(r["ws"] + " · " + fdate(r["date"]) + " · " + str(r["sev"]) + "/100 · " + r["title"])}</title></circle></a>')
        tx, ty = X(dt.date.fromisoformat(topr['date'])), Y(topr['sev'])
        lab = topr['title'] if len(topr['title']) <= 44 else topr['title'][:42].rsplit(' ', 1)[0] + '…'
        anc = 'end' if tx > (left + right) * .6 else 'start'; lx = tx - 4 if anc == 'end' else tx + 4
        ly = ty - (70 if tall else 52)
        out.append(f'<line x1="{tx:.1f}" y1="{ty - 10:.1f}" x2="{tx:.1f}" y2="{ly + 8:.1f}" stroke="{INK2}"/>')
        out.append(T(lx, ly - fs - 4, f'Most severe: {topr["sev"]}/100', fs + 1, PAPER, weight=700, anchor=anc))
        out.append(T(lx, ly + 2, lab, fs, INK2, anchor=anc))
        return ''.join(out)
    return dict(title=f'Severe AI incidents went from {a} to {b} in a year',
                dek=f'Every AI incident on the record since January 2023 ({len(rows)}), one dot each, placed by date and severity.',
                takeaway=f'The red dots are the ones that matter: {b} severe incidents in the last 12 months, against {a} in the 12 before.',
                why='Most AI coverage counts incidents. This counts how bad they were, with one published formula for every case since 2023. The pile-up of red at the right is the escalation in one picture.',
                legend=[(RED, 6.5, 'Severe or critical'), (MUTED, 4.5, 'Below severe')], source=SRC_INDEX, plot=plot,
                aria=f'{len(rows)} AI incidents by date and severity; {b} severe in the last 12 months against {a} the year before.',
                table=(['Date', 'Severity', 'Incident'], [(r['date'], r['sev'], r['title'], f'/i/{r["id"]}/') for r in sorted(rows, key=lambda r: r['date'], reverse=True)]))

# ---------------------------------------------------------------- kind: who did the acting, person or AI, by half-year
def autonomy_shift(spec):
    rows = [r for r in scored() if r.get('setting') == 'wild']
    def half(d): return f'{d[:4]} H{1 if int(d[5:7]) <= 6 else 2}'
    groups = [('person', DIM, 'A person misused it, or trusted bad output', (0, 1)), ('acted', MUTED, 'The AI took a single action', (2,)), ('own', RED, 'The AI acted on its own', (3, 4))]
    halves = []
    y0, y1 = 2023, int(AS_OF[:4])
    for y in range(y0, y1 + 1):
        for h in (1, 2):
            k = f'{y} H{h}'
            if y == y1 and h == 2 and int(AS_OF[5:7]) <= 6: continue
            halves.append(k)
    cnt = {k: collections.Counter() for k in halves}
    for r in rows:
        k = half(r['date'])
        if k in cnt:
            g = next(g for g, _, _, a in groups if r['A'] in a); cnt[k][g] += 1
    own_this = sum(cnt[k]['own'] for k in halves if k.startswith(AS_OF[:4]))
    own_early = sum(cnt[k]['own'] for k in halves if k[:4] in ('2023', '2024'))
    tot_this = sum(sum(cnt[k].values()) for k in halves if k.startswith(AS_OF[:4]))
    def label(k):
        y, h = k.split(' H'); return ('Jan–Jun ' if h == '1' else 'Jul–Dec ') + ("’" + y[2:]) + (' so far' if k == halves[-1] else '')
    def plot(box, tall):
        left, top, right, bot = box
        fs = 19 if tall else 13
        base = bot - (64 if tall else 40)
        mx = max(1, max(sum(c.values()) for c in cnt.values()))
        step = 10 if mx <= 50 else 20
        ymax = ((mx // step) + 1) * step
        Y = lambda v: base - (base - top - 10) * v / ymax
        out = []
        for v in range(0, ymax + 1, step):
            out.append(f'<line x1="{left}" x2="{right}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}"/>'); out.append(T(left - 10, Y(v) + fs * .35, v, fs, INK2, anchor='end'))
        n = len(halves); bw = (right - left) / n
        for i, k in enumerate(halves):
            x = left + i * bw + bw * .18; w = bw * .64; yb = base
            for g, color, name, _ in groups:
                v = cnt[k][g]
                if not v: continue
                h = (base - Y(v)) - 2
                out.append(f'<rect x="{x:.1f}" y="{yb - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{color}"><title>{esc(label(k) + ": " + str(v) + " · " + name)}</title></rect>')
                if g == 'own' and h > fs + 6:
                    out.append(T(x + w / 2, yb - h / 2 + fs * .35, v, fs + 1, NAVY, weight=700, anchor='middle'))
                yb -= h + 2
            tot = sum(cnt[k].values())
            out.append(T(x + w / 2, yb - 8, tot, fs, INK2, anchor='middle'))
            parts = label(k).split(' ', 1)
            out.append(T(x + w / 2, base + fs + 6, parts[0], fs, INK2, anchor='middle'))
            out.append(T(x + w / 2, base + 2 * fs + 10, parts[1], fs, INK2, anchor='middle'))
        return ''.join(out)
    return dict(title=f'AI went from tool to actor: {own_this} incidents this year where AI acted on its own',
                dek='Real-world AI incidents every six months, by who did the acting.' + (' In 2023 and 2024, the AI never acted on its own.' if not own_early else f' In 2023 and 2024: {own_early}.'),
                takeaway=(f'In 2023 and 2024, no real-world AI incident on the record had the AI acting on its own. ' if not own_early else f'In 2023 and 2024: {own_early}. ') + f'This year it happened in {own_this} of {tot_this}.',
                why=f'The question people ask is whether AI is just a tool. The record says it was, until about a year ago. Part of the rise is that more incidents get reported now, so look at the share: in 2023 and 2024 the AI never acted on its own; this year it did in {round(100 * own_this / max(1, tot_this))}% of cases.',
                legend=[(RED, 6.5, 'AI acted on its own'), (MUTED, 6.5, 'AI took a single action'), (DIM, 6.5, 'A person misused or trusted it')],
                source=f'Source: Warning Shots AI Incident Index, real-world incidents, autonomy as scored. As of {fdate(AS_OF)}.', plot=plot,
                aria=f'Real-world AI incidents per half-year by who did the acting; {own_this} this year where the AI acted on its own, {own_early} in 2023 and 2024.',
                table=(['Period', 'AI acted on its own', 'AI took a single action', 'A person misused or trusted it', 'Total'], [(label(k), cnt[k]['own'], cnt[k]['acted'], cnt[k]['person'], sum(cnt[k].values()), '') for k in reversed(halves)]))

# ---------------------------------------------------------------- kind: did they fix it? each case from report to retest
def fix_chain(spec):
    FX = L('data/fixes.json')
    stages = [('reported', 'Reported'), ('response', 'Responded'), ('claimed_fix', 'Fix claimed'), ('retest', 'Checked by outsiders')]
    ST = {'ongoing': 'Still unfolding', 'reopened': 'Came back', 'disputed': 'Disputed', 'unverified': 'Not verified', 'unresolved': 'No fix', 'fixed': 'Fixed, verified'}
    cur = lambda f: next((c for c in f['chain'] if c['stage'] == 'current'), f['chain'][-1])
    order = {'reopened': 0, 'unresolved': 1, 'disputed': 2, 'unverified': 3, 'ongoing': 4, 'fixed': 5}
    FX = sorted(FX, key=lambda f: (order.get(cur(f)['status'], 9), f['name']))
    back = sum(cur(f)['status'] == 'reopened' for f in FX); fixed = sum(cur(f)['status'] == 'fixed' for f in FX)
    short = lambda f: f['name'].split(':')[0].strip()
    def plot(box, tall):
        left, top, right, bot = box
        fs = 19 if tall else 13
        namew = (right - left) * (.36 if tall else .32)
        cols = len(stages) + 1
        cw = (right - left - namew) / cols
        rh = (bot - top - 40) / len(FX)
        out = []
        for j, (_, lab) in enumerate(stages + [('', 'Now')]):
            cx = left + namew + cw * (j + .5)
            for i, line in enumerate(wrap(lab, 12)):
                out.append(T(cx, top + 14 + i * (fs + 2), line, fs, INK2, anchor='middle', weight=700))
        for i, f in enumerate(FX):
            y = top + 48 + i * rh + rh / 2
            out.append(f'<line x1="{left}" x2="{right}" y1="{y + rh / 2:.1f}" y2="{y + rh / 2:.1f}" stroke="{GRID}"/>')
            nm = short(f); nm = nm if len(nm) <= (30 if tall else 34) else nm[:28].rsplit(' ', 1)[0] + '…'
            out.append(f'<a href="/c/{esc(f["incident_id"])}/">' + T(left, y + fs * .35, nm, fs, PAPER) + '</a>')
            st = {c['stage']: c['status'] for c in f['chain']}
            for j, (k, lab) in enumerate(stages):
                cx = left + namew + cw * (j + .5); s = st.get(k, 'none'); r = 9 if tall else 7
                if j: out.append(f'<line x1="{cx - cw + r:.1f}" x2="{cx - r:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-width="2"/>')
                if s == 'done':
                    out.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="{r}" fill="{PAPER}"><title>{esc(lab + ": done")}</title></circle>')
                elif s == 'partial':
                    out.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="{r - 1}" fill="none" stroke="{PAPER}" stroke-width="2"/><path d="M{cx:.1f} {y - r + 1:.1f} A{r - 1} {r - 1} 0 0 0 {cx:.1f} {y + r - 1:.1f} Z" fill="{PAPER}"><title>{esc(lab + ": partly")}</title></path>')
                else:
                    out.append(f'<circle cx="{cx:.1f}" cy="{y:.1f}" r="{r - 1}" fill="none" stroke="{DIM}" stroke-width="2"><title>{esc(lab + ": not done")}</title></circle>')
            s = cur(f)['status']; cx = left + namew + cw * (len(stages) + .5)
            out.append(T(cx, y + fs * .35, ST.get(s, s), fs, RED if s == 'reopened' else INK2, weight=700 if s == 'reopened' else 400, anchor='middle'))
        return ''.join(out)
    return dict(title=f'{back} of {len(FX)} major AI cases came back after a fix',
                dek='Every major case we track, from report to response to claimed fix to an outside check. ' + (f'{fixed} verified fixed.' if fixed else 'None has an outside-verified fix yet.'),
                takeaway=f'When an AI company says a problem is fixed, it often isn\'t: {back} of the {len(FX)} biggest cases we follow happened again after a fix was announced.',
                why='Companies announce fixes; almost nobody checks them. This follows each case to the end, and shows how many came back.',
                legend=[(PAPER, 6.5, 'Done'), ('half', 6.5, 'Partly'), ('ring', 6.5, 'Not done')], source=f'Source: Warning Shots, Did they fix it? tracker, each stage sourced. As of {fdate(AS_OF)}.', plot=plot,
                aria=f'{len(FX)} major AI cases tracked from report to retest; {back} came back after a fix.',
                table=(['Case', 'Now', 'Fix claimed', 'Checked by outsiders'], [(short(f), ST.get(cur(f)['status'], ''), {c['stage']: c['status'] for c in f['chain']}.get('claimed_fix', ''), {c['stage']: c['status'] for c in f['chain']}.get('retest', ''), f'/c/{f["incident_id"]}/') for f in FX]))

# ---------------------------------------------------------------- kind: job cuts tied to AI, by month and by who made the link
def layoff_months(spec):
    import re as _re
    J = L('research/jobs.json')
    led, seen = [], set()
    for j in J['jobs']:
        for d, what, u, lab in j.get('jobs_evidence', []):
            low = what.lower()
            who = 'co' if 'company says ai' in low else 'rep' if 'reported as ai' in low else 'study' if ('(study' in low or low.endswith('study') or 'study)' in low) else 'other'
            if who in ('study', 'other') or not u or u in seen: continue
            seen.add(u); led.append(dict(date=d, what=_re.sub(r'\s*\((company says AI[^)]*|reported as AI[^)]*)\)\s*', ' ', what).strip(), who=who, url=u))
    try:
        arch = {}
        try:
            arch = {n['id']: n for n in L('research/news_archive.json')}
        except (OSError, ValueError):
            pass
        for n in L('research/news.json'): arch[n['id']] = {**arch.get(n['id'], {}), **n}
        for n in sorted(arch.values(), key=lambda n: n.get('published') or ''):
            if n.get('topic') == 'jobs' and n['url'] not in seen and _re.search(r'cut|layoff|lay off|buyout|job loss|redundanc|shed|eliminat', n.get('title', '') + ' ' + (n.get('summary') or ''), _re.I):
                low = (n.get('title', '') + ' ' + (n.get('summary') or '')).lower()
                seen.add(n['url']); led.append(dict(date=n['published'][:10], what=n.get('tag') or n['title'], who='rep' if n.get('label') == 'reported' else 'co' if ('says ai' in low or 'citing ai' in low or 'cites ai' in low) else 'unk', url=n['url']))
    except (OSError, ValueError):
        pass
    import ledger_rules as _LR
    led = _LR.clean(led)   # one entry per employer per month, no industry tallies (ledger_rules.py, shared with the ledger page)
    end = dt.date.fromisoformat(AS_OF)
    months = []
    y, m = end.year, end.month
    for _ in range(12):
        months.append(f'{y:04d}-{m:02d}'); m -= 1
        if not m: y, m = y - 1, 12
    months.reverse()
    cnt = {k: collections.Counter() for k in months}
    for x in led:
        if x['date'][:7] in cnt: cnt[x['date'][:7]][x['who']] += 1
    inwin = [x for x in led if x['date'][:7] in cnt]
    co = sum(1 for x in inwin if x['who'] == 'co'); tot = len(inwin)
    last3 = sum(sum(cnt[k].values()) for k in months[-3:]); prior9 = sum(sum(cnt[k].values()) for k in months[:-3])
    MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    lab = lambda k: MN[int(k[5:]) - 1] + (" '" + k[2:4] if k[5:] == '01' or k == months[0] else '')
    groups = [('co', RED, 'The company itself tied the cuts to AI'), ('rep', MUTED, 'Only reporters or analysts made the link'), ('unk', DIM, 'Link to AI unclear: see the source')]
    def plot(box, tall):
        left, top, right, bot = box
        fs = 19 if tall else 13
        base = bot - (40 if tall else 28)
        mx = max(1, max(sum(c.values()) for c in cnt.values()))
        step = 1 if mx <= 6 else 2 if mx <= 12 else 5
        ymax = ((mx // step) + 1) * step
        Y = lambda v: base - (base - top - 10) * v / ymax
        out = []
        for v in range(0, ymax + 1, step):
            out.append(f'<line x1="{left}" x2="{right}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}"/>'); out.append(T(left - 10, Y(v) + fs * .35, v, fs, INK2, anchor='end'))
        bw = (right - left) / len(months)
        for i, k in enumerate(months):
            x = left + i * bw + bw * .2; w = bw * .6; yb = base
            for g, color, name in groups:
                v = cnt[k][g]
                if not v: continue
                h = (base - Y(v)) - 2
                out.append(f'<rect x="{x:.1f}" y="{yb - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{color}"><title>{esc(lab(k) + ": " + str(v) + " · " + name)}</title></rect>')
                if h > fs + 6: out.append(T(x + w / 2, yb - h / 2 + fs * .35, v, fs, NAVY if g == 'co' else PAPER, weight=700, anchor='middle'))
                yb -= h + 2
            t = sum(cnt[k].values())
            if t: out.append(T(x + w / 2, yb - 8, t, fs, INK2, anchor='middle'))
            out.append(T(x + w / 2, base + fs + 6, lab(k), fs, INK2, anchor='middle'))
        # name the employers in the latest month, beside its bar
        last = sorted([x for x in led if x['date'][:7] == months[-1]], key=lambda x: (x['who'] != 'co', x['date']))
        if last:
            xr = left + (len(months) - 1) * bw + bw * .1; ly = top + 8
            out.append(T(xr, ly + fs, MN[int(months[-1][5:]) - 1] + ':', fs, PAPER, weight=700, anchor='end'))
            for i, xx in enumerate(last[:8]):
                out.append(T(xr, ly + fs * (2.35 + i * 1.35), xx['emp'], fs, RED if xx['who'] == 'co' else INK2, weight=600 if xx['who'] == 'co' else 400, anchor='end'))
        return ''.join(out)
    cur = sum(cnt[months[-1]].values()); best_prev = max(sum(cnt[k].values()) for k in months[:-1])
    MF = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][int(months[-1][5:]) - 1]
    ttl = (f'{MF} already has {cur} AI-linked job cuts on our ledger, more than any other month this past year' if cur > best_prev
           else f'Job cuts tied to AI: {last3} in the last three months, {prior9} in the nine before')
    return dict(title=ttl,
                dek=f'Each bar counts employers announcing cuts tied to AI, by month (each employer once a month). Red: the employer itself named AI ({co} of {tot}). Counts of announcements, not of jobs.',
                takeaway=f'Our ledger holds {last3} AI-linked job-cut announcements from the last three months against {prior9} in the nine months before; in {co} of {tot} the company itself named AI.',
                why='Layoff headlines blur who is actually blaming AI. This separates cuts the employer tied to AI from cuts only reporters linked to it, so the trend can be read honestly. Part of the recent rise is that we started collecting in earnest this autumn, so read the red share as much as the height.',
                legend=[(RED, 6.5, 'Employer named AI'), (MUTED, 6.5, 'Only reporters made the link')],
                source=f'Source: Warning Shots layoffs ledger (jobs/layoffs/), each entry sourced. As of {fdate(AS_OF)}.', plot=plot,
                aria=f'AI-linked job-cut announcements per month over 12 months; {last3} in the last three months, {prior9} in the nine before; {co} of {tot} company-stated.',
                table=(['Date', 'Who says AI', 'What happened'], [(x['date'], {'co': 'Company says AI', 'rep': 'Reported as AI'}.get(x['who'], 'See source'), x['emp'] + ': ' + x['what'], x['url']) for x in sorted(inwin, key=lambda x: x['date'], reverse=True)]))

# ---------------------------------------------------------------- kind: the call sheet, as dots on a probability line
def forecast_board(spec):
    C = L('data/calls.json')
    end = dt.date.fromisoformat(AS_OF); horizon = end + dt.timedelta(days=int(spec.get('days', 35)))
    op = [c for c in C if not c.get('resolution') and not c.get('resolved') and c.get('resolve_by') and end <= dt.date.fromisoformat(c['resolve_by']) <= horizon]
    op.sort(key=lambda c: (c['resolve_by'], -c['odds']))
    prev = {}
    try:
        snaps = [json.loads(l) for l in open('research/forecast_log.jsonl', encoding='utf-8') if l.strip()]
        ats = sorted({s['as_of'] for s in snaps})
        if len(ats) >= 2:
            prev = {s['id']: s['p'] for s in snaps if s['as_of'] == ats[-2]}
    except (OSError, ValueError):
        pass
    moved = {c['id'] for c in op if c['id'] in prev and abs(prev[c['id']] - c['odds']) > 1e-9}
    yes = sum(c['odds'] > .5 for c in op); MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    md = lambda d: MN[int(d[5:7]) - 1] + ' ' + str(int(d[8:10]))
    last = max(c['resolve_by'] for c in op) if op else AS_OF
    words = lambda p: 'very likely' if p >= .85 else 'likely' if p > .55 else 'either way' if p >= .45 else 'unlikely' if p > .15 else 'very unlikely'
    def lab(c, n):
        q = (c.get('plain') or c['question']).strip()
        return q if len(q) <= n else q[:n - 1].rsplit(' ', 1)[0] + '…'
    def plot(box, tall):
        left, top, right, bot = box
        fs = 17 if tall else 12.5
        labw = (right - left) * (.0 if tall else .52)
        x0 = left + labw + (0 if tall else 20); x1 = right - 10
        X = lambda p: x0 + (x1 - x0) * p
        rh = (bot - top - 34) / max(1, len(op))
        out = []
        for p, t in ((0, 'No'), (.5, 'Coin flip'), (1, 'Yes')):
            out.append(f'<line x1="{X(p):.1f}" x2="{X(p):.1f}" y1="{top + 22}" y2="{bot}" stroke="{GRID}" stroke-dasharray="{"0" if p != .5 else "4 4"}"/>')
            out.append(T(X(p), top + 12, t, fs, INK2, anchor='middle' if 0 < p < 1 else ('start' if p == 0 else 'end'), weight=700))
        for i, c in enumerate(op):
            yc = top + 34 + i * rh + rh / 2
            if tall:
                out.append(T(x0, yc - fs * .55, md(c['resolve_by']) + ' · ' + lab(c, 62), fs - 1, PAPER))
                yd = yc + fs * .55
            else:
                out.append(T(left, yc + fs * .35, md(c['resolve_by']) + '  ' + lab(c, 70), fs, PAPER))
                yd = yc
            out.append(f'<line x1="{x0:.1f}" x2="{x1:.1f}" y1="{yd:.1f}" y2="{yd:.1f}" stroke="{GRID}"/>')
            mv = c['id'] in moved; col = RED if mv else (PAPER if c['odds'] > .5 else MUTED)
            if mv and c['id'] in prev:
                out.append(f'<line x1="{X(prev[c["id"]]):.1f}" x2="{X(c["odds"]):.1f}" y1="{yd:.1f}" y2="{yd:.1f}" stroke="{RED}" stroke-width="2"/>')
                out.append(f'<circle cx="{X(prev[c["id"]]):.1f}" cy="{yd:.1f}" r="4" fill="none" stroke="{RED}" stroke-width="1.5"/>')
            r = 8 if tall else 6.5
            out.append(f'<a href="/forecast/{esc(c["id"])}/"><circle cx="{X(c["odds"]):.1f}" cy="{yd:.1f}" r="{r}" fill="{col}"><title>{esc(lab(c, 200) + ": " + words(c["odds"]) + (" (moved this refresh)" if mv else ""))}</title></circle></a>')
            out.append(T(X(c['odds']) + (r + 6 if c['odds'] < .8 else -(r + 6)), yd + fs * .35, words(c['odds']) + (' · moved' if mv else ''), fs - 1, RED if mv else INK2, anchor='start' if c['odds'] < .8 else 'end', weight=700 if mv else 400))
        return ''.join(out)
    legend = [(PAPER, 6.5, 'We expect yes'), (MUTED, 6.5, 'We expect no or a coin flip')] + ([(RED, 6.5, 'Moved this refresh')] if moved else [])
    return dict(title=f'We expect yes on {yes} of the {len(op)} calls due by {md(last)}',
                dek='Every open call due in the next five weeks, placed by how likely we think it is. A coin flip sits in the middle. Each one gets graded on its date, hits and misses alike.',
                takeaway=f'{yes} of our {len(op)} calls due by {md(last)} lean yes. ' + (f'{len(moved)} moved this refresh on new evidence.' if moved else 'None moved this refresh.'),
                why='Forecasts are only worth something if they are written down before the answer is known and graded after. This is the board as it stands, so readers can hold us to it.',
                legend=legend, source=f'Source: Warning Shots call sheet (forecast/), odds set before each date; misses stay on the record. As of {fdate(AS_OF)}.', plot=plot,
                aria=f'{len(op)} open calls due by {md(last)} placed on a no-to-yes line; {yes} lean yes.',
                table=(['Due', 'Question', 'Our odds', 'Moved this refresh'], [(c['resolve_by'], lab(c, 300), f"{round(c['odds'] * 100)}%", (f"{round(prev[c['id']] * 100)}% to {round(c['odds'] * 100)}%" if c['id'] in moved else ''), f'/forecast/{c["id"]}/') for c in op]))

KINDS = {'incident_field': incident_field, 'autonomy_shift': autonomy_shift, 'fix_chain': fix_chain, 'layoff_months': layoff_months, 'forecast_board': forecast_board}

# ---------------------------------------------------------------- build
try:
    SPECS = L('research/charts.json')
except (OSError, ValueError):
    SPECS = []
os.makedirs('assets/charts', exist_ok=True)
built = []
for spec in SPECS:
    fn = KINDS.get(spec['kind'])
    if not fn:
        print('  unknown chart kind', spec['kind']); continue
    c = fn(spec)
    for k in ('title', 'dek', 'takeaway', 'why'):
        if spec.get(k): c[k] = spec[k]
    c.update(id=spec['id'], date=spec['date'], pin=spec.get('pin', False), home=spec.get('home', False))
    c['svg'] = card('wide', c); c['svg_tall'] = card('tall', c)
    open(f"assets/charts/{c['id']}.svg", 'w', encoding='utf-8').write(c['svg'])
    open(f"assets/charts/{c['id']}-tall.svg", 'w', encoding='utf-8').write(c['svg_tall'])
    built.append(c)

def share_links(c):
    url = SITE + f"chart/{c['id']}/"
    x = 'https://x.com/intent/post?' + urllib.parse.urlencode({'text': c['title'], 'url': url})
    li = 'https://www.linkedin.com/sharing/share-offsite/?' + urllib.parse.urlencode({'url': url})
    rd = 'https://www.reddit.com/submit?' + urllib.parse.urlencode({'url': url, 'title': c['title']})
    return url, x, li, rd

for c in built:
    url, x, li, rd = share_links(c)
    hd, rows = c['table']
    trs = ''.join('<tr>' + ''.join(f'<td>{(f"<a href=\"{esc(r[-1])}\">{esc(str(v))}</a>" if (i == len(r) - 2 and r[-1]) else esc(str(v)))}</td>' for i, v in enumerate(r[:-1])) + '</tr>' for r in rows)
    embed = f'<a href="{url}"><img src="{SITE}assets/charts/{c["id"]}.png" alt="{esc(c["title"])}" width="1200" height="675"></a><br>Source: <a href="{url}">Warning Shots</a>'
    body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/chart/">The Charts</a> · {esc(fdate(c['date']))}</nav>
<h1>{esc(c['title'])}</h1><p class="aka">{esc(c['takeaway'])}</p>
<style>.ch-fig .tallv{{display:none}}@media (max-width:700px){{.ch-fig .widev{{display:none}}.ch-fig .tallv{{display:block}}}}.ch-fig svg{{width:100%;height:auto;display:block}}</style><figure class="ch-fig" style="margin:16px 0"><div class="widev">{c['svg']}</div><div class="tallv">{c['svg_tall']}</div></figure>
<div class="share ch-share"><a class="button" href="{esc(x)}" target="_blank" rel="noopener">Post on X</a><a class="button alt" href="{esc(li)}" target="_blank" rel="noopener">LinkedIn</a><a class="button alt" href="{esc(rd)}" target="_blank" rel="noopener">Reddit</a><button type="button" class="alt" data-copy="{esc(c['title'] + ' ' + url)}">Copy link</button></div>
<p class="meta">Download: <a href="/assets/charts/{esc(c['id'])}.png" download>Wide image (16:9)</a> · <a href="/assets/charts/{esc(c['id'])}-tall.png" download>Phone and Instagram (4:5)</a> · <a href="/assets/charts/{esc(c['id'])}.svg" download>Vector (SVG)</a></p>
<h2>Why it matters</h2><p>{esc(c['why'])}</p>
<h2>Use it</h2><p>Free to share, embed and broadcast with the citation, which is already in the image: <b>Source: Warning Shots, warningshots.ai</b>. Paste this to embed it:</p>
<textarea readonly rows="3" style="width:100%;font:13px/1.4 monospace;padding:8px" onclick="this.select()">{esc(embed)}</textarea>
<details><summary>The data behind this chart ({len(rows)} rows)</summary><div class="tw"><table><thead><tr>{''.join(f'<th>{esc(h)}</th>' for h in hd)}</tr></thead><tbody>{trs}</tbody></table></div></details>
<p class="meta">{esc(c['source'])} Every mark is computed from the data at build time, never typed in.</p>
<p><a href="/chart/">Every chart →</a></p>{footer_note(False)}</article>"""
    write(f"chart/{c['id']}/index.html", url=url, title=c['title'], desc=c['takeaway'][:200], body=body, draft=False, img=SITE + f"assets/charts/{c['id']}.png",
          crumbs=[('The Charts', '/chart/'), (fdate(c['date']), '')], graph=[webpage(url, c['title'], c['takeaway'], c['date'], False, '')])

if built:
    today = max(built, key=lambda c: (c['date'], c['home'], c['id']))
    json.dump(dict(id=today['id'], date=today['date'], title=today['title'], takeaway=today['takeaway'], svg=today['svg'], svg_tall=today['svg_tall'], url=f"/chart/{today['id']}/"),
              open('data/chart.json', 'w', encoding='utf-8'), ensure_ascii=False)
    def tile(c, big=False):
        url, x, li, rd = share_links(c)
        return (f'<li class="ch-tile{" big" if big else ""}"><a class="ch-img" href="/chart/{esc(c["id"])}/"><img src="/assets/charts/{esc(c["id"])}.png" alt="{esc(c["title"])}" loading="lazy" width="1200" height="675"></a>'
                f'<a class="ch-t" href="/chart/{esc(c["id"])}/">{esc(c["title"])}</a><span class="meta">{esc(c["takeaway"])}</span>'
                f'<span class="ch-act"><a href="{esc(x)}" target="_blank" rel="noopener">Post</a> · <a href="/assets/charts/{esc(c["id"])}.png" download>Download</a> · <a href="/assets/charts/{esc(c["id"])}-tall.png" download>Phone size</a></span></li>')
    pins = [c for c in built if c.get('pin')]
    rest = sorted([c for c in built if not c.get('pin')], key=lambda c: c['date'], reverse=True)
    css = ('<style>.ch-grid{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:22px}'
           '.ch-tile{display:flex;flex-direction:column;gap:6px}.ch-tile.big{grid-column:1/-1}.ch-img img{width:100%;height:auto;display:block;border-radius:2px}'
           '.ch-t{font-family:var(--serif);font-weight:800;font-size:1.15rem;line-height:1.25;color:var(--ink)}.ch-tile.big .ch-t{font-size:1.6rem}.ch-act{font-size:13.5px;font-weight:700}</style>')
    body = (f'{css}<article class="pk" style="max-width:1100px"><div class="kick">Warning Shots</div><h1>The Charts</h1>'
            '<p>Original charts from the Warning Shots data: what AI is actually doing, counted case by case. A new one every morning. Every chart is free to share, embed and broadcast; the citation is already in the image. Each comes wide for the web and TV, and tall for phones.</p>'
            + (f'<h2>Start here</h2><ul class="ch-grid">{"".join(tile(c, True) for c in pins)}</ul>' if pins else '')
            + f'<h2>{"Latest" if pins else "Every chart"}</h2><ul class="ch-grid">{"".join(tile(c) for c in rest)}</ul>'
            + f'<p class="meta">Data: <a href="/index/">the Record</a> (download it there). Questions or corrections: <a href="{esc(meta.get("repo_url", ""))}">the public repository</a>.</p></article>')
    write('chart/index.html', url=SITE + 'chart/', title='The Charts: what AI is actually doing, in charts', desc='Original charts from the Warning Shots data on AI incidents, jobs, fixes and breakthroughs. A new one every morning, free to share with the citation.',
          body=body, draft=False, img=SITE + f"assets/charts/{(pins or rest)[0]['id']}.png",
          crumbs=[('The Charts', '')], graph=[webpage(SITE + 'chart/', 'The Charts', 'Original AI charts', AS_OF, False, '')])
    register('chart/', [SITE + 'chart/'] + [SITE + f"chart/{c['id']}/" for c in built])
print(f'charts: {len(built)} built' + (f", today: {today['title']}" if built else ''))
