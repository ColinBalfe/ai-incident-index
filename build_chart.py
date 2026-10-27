#!/usr/bin/env python3
"""The Chart: one original, striking chart a day, built from the index's own data.

research/charts.json lists the charts, newest last: {id, date, kind, title, dek, takeaway, ...kind params}.
Each `kind` is a renderer below that returns an SVG (16:9, title, source line and citation baked in, so the
image carries its citation wherever it goes) plus a table of the data behind it.

Writes: data/chart.json (today's chart, for the homepage), chart/<id>/index.html (permanent page with the
table), chart/index.html (every chart), and assets/charts/<id>.svg. make_charts.mjs turns each SVG into a PNG.
Run after build_site.py:  python3 build_chart.py
"""
import json, os, datetime as dt, html, math
from pagekit import write, register, SITE, footer_note, webpage, fdate

esc = html.escape
L = lambda f: json.load(open(f, encoding='utf-8'))
meta = L('data/meta.json')
AS_OF = meta['as_of'][:10]

# palette (validated for the navy surface; the gray is muted context, not a category; red is the index's alarm, always labelled)
NAVY, PAPER, INK2, GRID, MUTED, RED = '#0A111E', '#F4F3EF', '#A8B3C2', '#22304A', '#6F7F96', '#FF3B14'
W, H = 1200, 675
FONT_S = "Archivo, 'Archivo Fallback', Arial, sans-serif"
FONT_D = "Playfair, 'Playfair Fallback', Georgia, serif"

def score(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    return round(0.55 * harm + 0.45 * sig)

def frame(title, dek, source, body, aria):
    """The shared card: title, dek, the plot, and the source + citation line."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(aria)}" class="ws-chart">'
            f'<rect width="{W}" height="{H}" fill="{NAVY}"/>'
            f'<text x="48" y="64" fill="{PAPER}" font-family="{FONT_D}" font-weight="900" font-size="38">{esc(title)}</text>'
            f'<text x="48" y="100" fill="{INK2}" font-family="{FONT_S}" font-size="18">{esc(dek)}</text>'
            + body +
            f'<text x="48" y="{H - 22}" fill="{INK2}" font-family="{FONT_S}" font-size="13">{esc(source)}</text>'
            f'<text x="{W - 48}" y="{H - 22}" text-anchor="end" fill="{PAPER}" font-family="{FONT_D}" font-weight="700" font-size="15" letter-spacing="2.4">W<tspan fill="{RED}">:</tspan> WARNING SHOTS · warningshots.ai</text>'
            '</svg>')

# ---------------------------------------------------------------- kind: every incident as a dot, by date and severity
def incident_field(spec):
    inc = L('data/incidents.json')
    rows = []
    for r in inc:
        s = score(r)
        rows.append(dict(id=r['id'], date=r['date'], title=r['title'], sev=s, setting=r.get('setting', '')))
    rows.sort(key=lambda r: (r['date'], r['id']))
    for i, r in enumerate(rows):
        r['ws'] = 'WS-%04d' % (i + 1)
    d0, d1 = dt.date(2023, 1, 1), dt.date.fromisoformat(AS_OF)
    left, right, top, bot = 70, W - 48, 172, H - 74
    X = lambda d: left + (right - left) * (d - d0).days / max(1, (d1 - d0).days)
    Y = lambda s: bot - (bot - top) * s / 100
    asof = dt.date.fromisoformat(AS_OF)
    yr = dt.timedelta(days=365.25)
    last = [r for r in rows if asof - yr < dt.date.fromisoformat(r['date']) <= asof]
    prev = [r for r in rows if asof - 2 * yr < dt.date.fromisoformat(r['date']) <= asof - yr]
    sev_last, sev_prev = sum(r['sev'] >= 60 for r in last), sum(r['sev'] >= 60 for r in prev)
    out = []
    # the two comparison years, as quiet bands
    xa, xb, xc = X(asof - 2 * yr), X(asof - yr), X(asof)
    out.append(f'<rect x="{xb:.1f}" y="{top - 26}" width="{xc - xb:.1f}" height="{bot - top + 26}" fill="{RED}" fill-opacity="0.07"/>')
    out.append(f'<text x="{(xa + xb) / 2:.1f}" y="{top - 8}" text-anchor="middle" fill="{INK2}" font-family="{FONT_S}" font-size="15">12 months before: <tspan font-weight="700" fill="{PAPER}">{sev_prev} severe</tspan></text>')
    out.append(f'<text x="{(xb + xc) / 2:.1f}" y="{top - 8}" text-anchor="middle" fill="{INK2}" font-family="{FONT_S}" font-size="15">Last 12 months: <tspan font-weight="700" fill="{RED}">{sev_last} severe</tspan></text>')
    # grid: severity every 20, years on the axis
    for s in (0, 20, 40, 60, 80, 100):
        y = Y(s)
        out.append(f'<line x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID if s != 60 else RED}" stroke-width="{1 if s != 60 else 1.2}" stroke-dasharray="{"" if s != 60 else "5 5"}" stroke-opacity="{1 if s != 60 else .75}"/>')
        out.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" fill="{INK2}" font-family="{FONT_S}" font-size="13">{s}</text>')
    out.append(f'<text x="{left + 8}" y="{Y(60) - 8:.1f}" fill="{RED}" font-family="{FONT_S}" font-size="13" font-weight="700" letter-spacing="1">SEVERE: 60 AND ABOVE</text>')
    out.append(f'<text transform="translate(22 {(top + bot) / 2:.0f}) rotate(-90)" text-anchor="middle" fill="{INK2}" font-family="{FONT_S}" font-size="13">Severity, 0–100</text>')
    for yv in range(d0.year, d1.year + 1):
        x = X(dt.date(yv, 1, 1))
        out.append(f'<text x="{x:.1f}" y="{bot + 26}" fill="{INK2}" font-family="{FONT_S}" font-size="14">{yv}</text>')
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{bot}" y2="{bot + 8}" stroke="{INK2}"/>')
    # dots: nudge sideways to avoid stacking (the score never moves)
    placed = []
    for r in sorted(rows, key=lambda r: r['sev']):
        sev = r['sev'] >= 60
        rad = 6.5 if sev else 4.5
        x, y = X(dt.date.fromisoformat(r['date'])), Y(r['sev'])
        for k in range(14):
            dx = (k + 1) // 2 * (1 if k % 2 else -1) * 3.2
            if left + rad <= x + dx <= right - rad and all((x + dx - px) ** 2 + (y - py) ** 2 >= (rad + pr + 1) ** 2 for px, py, pr in placed):
                x += dx
                break
        placed.append((x, y, rad))
        tip = f"{r['ws']} · {fdate(r['date'])} · {r['sev']}/100 · {r['title']}"
        out.append(f'<a href="/i/{esc(r["id"])}/"><circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{RED if sev else MUTED}" stroke="{NAVY}" stroke-width="2"><title>{esc(tip)}</title></circle></a>')
    # label the single most severe incident on the record
    topr = max(rows, key=lambda r: (r['sev'], r['date']))
    tx, ty = X(dt.date.fromisoformat(topr['date'])), Y(topr['sev'])
    lab = topr['title'] if len(topr['title']) <= 48 else topr['title'][:46].rsplit(' ', 1)[0] + '…'
    anchor = 'end' if tx > W * 0.6 else 'start'
    lx = tx - 4 if anchor == 'end' else tx + 4
    ly = max(top + 34, ty - 52)
    out.append(f'<line x1="{tx:.1f}" y1="{ty - 8:.1f}" x2="{tx:.1f}" y2="{ly + 8:.1f}" stroke="{INK2}" stroke-width="1"/>')
    out.append(f'<text x="{lx:.1f}" y="{ly - 14:.1f}" text-anchor="{anchor}" fill="{PAPER}" font-family="{FONT_S}" font-size="14" font-weight="700">Most severe: {topr["sev"]}/100</text>')
    out.append(f'<text x="{lx:.1f}" y="{ly + 3:.1f}" text-anchor="{anchor}" fill="{INK2}" font-family="{FONT_S}" font-size="13">{esc(lab)}</text>')
    # legend (two marks, labelled; never colour alone)
    lgx = left + 6
    out.append(f'<circle cx="{lgx}" cy="129" r="6.5" fill="{RED}"/><text x="{lgx + 12}" y="134" fill="{PAPER}" font-family="{FONT_S}" font-size="14">Severe or critical</text>')
    out.append(f'<circle cx="{lgx + 158}" cy="129" r="4.5" fill="{MUTED}"/><text x="{lgx + 170}" y="134" fill="{PAPER}" font-family="{FONT_S}" font-size="14">Below severe</text>')
    title = spec.get('title') or f'Severe AI incidents went from {sev_prev} to {sev_last} in a year'
    dek = spec.get('dek') or f'Every AI incident on the record since January 2023 ({len(rows)}), one dot each, placed by date and severity.'
    source = f'Source: Warning Shots AI Incident Index, scored 0–100 by a published formula. Data as of {fdate(AS_OF)}.'
    aria = f'{title}. {len(rows)} incidents plotted by date and severity; {sev_last} scored severe in the last 12 months against {sev_prev} in the 12 before.'
    svg = frame(title, dek, source, ''.join(out), aria)
    table = [dict(case=r['ws'], date=r['date'], severity=r['sev'], incident=r['title'], url=f'/i/{r["id"]}/') for r in sorted(rows, key=lambda r: r['date'], reverse=True)]
    takeaway = spec.get('takeaway') or f'The red dots are the ones that matter: {sev_last} severe incidents in the last 12 months, against {sev_prev} in the 12 before.'
    return dict(title=title, dek=dek, svg=svg, table=table, takeaway=takeaway, source=source)

KINDS = {'incident_field': incident_field}

# ---------------------------------------------------------------- build
try:
    SPECS = L('research/charts.json')
except (OSError, ValueError):
    SPECS = []
os.makedirs('assets/charts', exist_ok=True)
built, urls = [], []
for spec in SPECS:
    fn = KINDS.get(spec['kind'])
    if not fn:
        print('  unknown chart kind', spec['kind']); continue
    c = fn(spec); c.update(id=spec['id'], date=spec['date'])
    open(f"assets/charts/{spec['id']}.svg", 'w', encoding='utf-8').write(c['svg'])
    url = SITE + f"chart/{spec['id']}/"
    rows = ''.join(f'<tr><td>{esc(t["date"])}</td><td>{t["severity"]}</td><td><a href="{esc(t["url"])}">{esc(t["incident"])}</a></td></tr>' for t in c['table'])
    body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/chart/">The Chart</a> · {esc(fdate(spec['date']))}</nav>
<h1>{esc(c['title'])}</h1><p>{esc(c['takeaway'])}</p>
<figure style="margin:16px 0">{c['svg']}</figure>
<div class="share"><a class="button" href="/assets/charts/{esc(spec['id'])}.png" download>Download the image</a> <button type="button" data-copy="{esc(c['title'] + ' ' + url)}">Copy link</button></div>
<p class="meta">{esc(c['source'])} Hover or tap a dot for the incident; every dot opens its case page. Free to use with the citation: Source: Warning Shots, warningshots.ai.</p>
<details><summary>The data behind this chart ({len(c['table'])} rows)</summary><div class="tw"><table><thead><tr><th>Date</th><th>Severity</th><th>Incident</th></tr></thead><tbody>{rows}</tbody></table></div></details>
<p><a href="/chart/">Every chart →</a></p>{footer_note(False)}</article>"""
    write(f"chart/{spec['id']}/index.html", url=url, title=c['title'], desc=c['takeaway'][:200], body=body, draft=False,
          img=SITE + f"assets/charts/{spec['id']}.png",   # make_charts.mjs writes it later in the same refresh
          crumbs=[('The Chart', '/chart/'), (fdate(spec['date']), '')], graph=[webpage(url, c['title'], c['takeaway'], spec['date'], False, '')])
    built.append(c); urls.append(url)
if built:
    today = max(built, key=lambda c: (c['date'], c['id']))
    json.dump(dict(id=today['id'], date=today['date'], title=today['title'], takeaway=today['takeaway'], svg=today['svg'], url=f"/chart/{today['id']}/"),
              open('data/chart.json', 'w', encoding='utf-8'), ensure_ascii=False)
    items = ''.join(f'<li><a href="/chart/{esc(c["id"])}/">{esc(c["title"])}</a><span class="meta">{esc(fdate(c["date"]))}</span></li>' for c in sorted(built, key=lambda c: c['date'], reverse=True))
    write('chart/index.html', url=SITE + 'chart/', title='The Chart: one original AI chart a day', desc='One original chart a day from the Warning Shots data: AI incidents, forecasts, jobs and breakthroughs, free to share with the citation.',
          body=f'<article class="pk"><div class="kick">Warning Shots</div><h1>The Chart</h1><p>One original chart a day, built from the index\'s own data. Free to share and embed with the citation.</p><ul class="list">{items}</ul></article>',
          draft=False, crumbs=[('The Chart', '')], graph=[webpage(SITE + 'chart/', 'The Chart', 'One original AI chart a day', AS_OF, False, '')])
    register('chart/', [SITE + 'chart/'] + urls)
print(f'chart: {len(built)} built' + (f", today: {today['title']}" if built else ''))
