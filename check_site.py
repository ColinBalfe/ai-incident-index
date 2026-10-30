#!/usr/bin/env python3
"""Pre-publish checks. Run after the build; exits non-zero (and the refresh must not publish) if any check fails.

1. Counts: every headline number printed in static HTML matches the data it comes from (assets/build.json, data/*.json).
2. Corrections: no built page states a retracted claim without its retraction. Retracted claims are listed in
   research/retractions.json: a claim pattern and the words that must appear in the same paragraph whenever it does.
3. Tags: every page has a title, a meta description, a canonical URL and a share image; descriptions are unique.
4. News sitemap: no publication date is the refresh time; every date is within the last two days.
"""
import json, os, re, sys, glob, html, datetime as dt
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
fails, warns = [], []
build = json.load(open('assets/build.json')); meta = json.load(open('data/meta.json'))

# 1. counts
for page in ['index.html', 'index/index.html']:
    t = open(page, encoding='utf-8').read()
    for m in re.finditer(r'went from (\d+) to (\d+) in a year', t):
        if (int(m.group(1)), int(m.group(2))) != (build['severe_prior12'], build['severe_last12']):
            fails.append(f'{page}: "{m.group(0)}" but the data says {build["severe_prior12"]} to {build["severe_last12"]}')
    for m in re.finditer(r'In (\d+)% of this year', t):
        if int(m.group(1)) != build['agentic_share']:
            fails.append(f'{page}: "{m.group(0)}" but the data says {build["agentic_share"]}%')
    for m in re.finditer(r'(\d+) incidents since 2023', t):
        if int(m.group(1)) != build['n']:
            fails.append(f'{page}: "{m.group(0)}" but the data has {build["n"]} incidents')
    if re.search(r'In half of this year', t):
        fails.append(f'{page}: hard-coded "half" instead of the computed share')

# 2. corrections
try:
    retractions = json.load(open('research/retractions.json', encoding='utf-8'))
except (OSError, ValueError):
    retractions = []
pages = [p for p in glob.glob('**/*.html', recursive=True) if not p.startswith(('node_modules', 'archive', 'shots', 'build/xcard_out')) and p != 'index.template.html']
for page in pages:
    raw = open(page, encoding='utf-8').read()
    paras = re.split(r'</(?:p|li|div|td|section|tr)>', raw)
    for para in paras:
        text = html.unescape(re.sub(r'<[^>]+>', ' ', para))
        for r in retractions:
            if re.search(r['claim'], text, re.I) and not re.search(r['must_say'], text, re.I):
                fails.append(f'{page}: states the retracted claim "{r["id"]}" without its retraction: ...{re.sub(r"\\s+", " ", text.strip())[:160]}...')
                break

# 3. tags
descs = {}
for page in pages:
    if page.startswith(('archive/', '404')):
        continue
    t = open(page, encoding='utf-8').read()
    for name, rx in [('title', r'<title>[^<]{5,}</title>'), ('description', r'<meta name="description" content="[^"]{30,}"'), ('canonical', r'<link rel="canonical" href="https://'), ('share image', r'<meta property="og:image" content="https://')]:
        if not re.search(rx, t):
            (warns if page.startswith(('shield', 'scraped')) else fails).append(f'{page}: missing {name}')
    m = re.search(r'<meta name="description" content="([^"]+)"', t)
    if m:
        descs.setdefault(m.group(1), []).append(page)
for d, ps in descs.items():
    if len(ps) > 1:
        fails.append(f'duplicate description on {", ".join(ps[:4])}')

# 4. news sitemap
ns = open('news-sitemap.xml', encoding='utf-8').read()
now = dt.datetime.fromisoformat(meta['as_of'])
for d in re.findall(r'<news:publication_date>([^<]+)</news:publication_date>', ns):
    if d == meta['as_of']:
        fails.append(f'news sitemap: publication date {d} is the refresh time, not the page date')
    try:
        if (now.date() - dt.date.fromisoformat(d[:10])).days > 2:
            fails.append(f'news sitemap: {d} is older than two days')
    except ValueError:
        fails.append(f'news sitemap: bad date {d}')

# 5. superseded claims: a fact that has changed must not survive in any current-state field (watch statuses, live panel,
#    the current stage of every fix chain, case one-liners). Dated history (timelines, changelog, Wire archive) is exempt.
try:
    superseded = json.load(open('research/superseded.json', encoding='utf-8'))
except (OSError, ValueError):
    superseded = []
if superseded:
    cur = []
    for w in json.load(open('data/watch.json', encoding='utf-8')): cur.append(('watch:' + w['id'], w.get('status', '')))
    for x in json.load(open('data/live.json', encoding='utf-8')): cur.append(('live:' + x['key'], x.get('detail', '') + ' ' + str(x.get('value', ''))))
    cur.append(('live_note', meta.get('live_note') or ''))
    for f in json.load(open('data/fixes.json', encoding='utf-8')):
        cur.append(('case:' + f['incident_id'] + ':one_liner', f.get('one_liner', '')))
        cur.append(('case:' + f['incident_id'] + ':what_would_change_it', f.get('what_would_change_it', '')))
        for st in f.get('chain', []):
            if st.get('stage') == 'current': cur.append(('case:' + f['incident_id'] + ':current', st.get('note', '')))
    for s in superseded:
        for where, text in cur:
            if re.search(s['pattern'], text or '', re.I):
                fails.append(f'superseded claim "{s["id"]}" ({s["why"]}) still stated in {where}')

# Wire headlines are written to 110 characters (REFRESH.md); the page no longer cuts them, so a long one shows in full: flag it for a rewrite
try:
    _long = [n['id'] for n in json.load(open('data/news.json', encoding='utf-8')) if len(n.get('title') or '') > 120]
    if _long: warns.append(f'{len(_long)} Wire headlines run past 120 characters (the rule is 110); shorten them when you next touch them: {", ".join(_long[:6])}')
except (OSError, ValueError):
    pass
for w in warns: print('warn:', w)
# ---- The numbers agree with themselves (Oct 29). A headline line's figures must appear in its own story (title, summary,
# receipt or people line): this catches a tag updated to a new figure while the story text still says the old one, or the reverse.
_num = lambda t: {re.sub(r'[,\s]', '', m) for m in re.findall(r'(?<![\w.])\d[\d,]*(?:\.\d+)?(?![\w])', t or '') if len(re.sub(r'\D', '', m)) >= 2}
try:
    for n in json.load(open('data/news.json', encoding='utf-8')):
        if not n.get('tag'): continue
        body = ' '.join([n.get('title') or '', n.get('summary') or '', n.get('receipt') or '', ((n.get('people') or {}).get('text') or '')])
        miss = _num(n['tag']) - _num(body)
        if miss: fails.append(f'news "{n["id"]}": headline line has {", ".join(sorted(miss))} but its story text does not (stale or mistyped figure): {n["tag"]}')
        # the lead's summary and its "What happens next" line follow the same rule (Oct 30 front page)
        body2 = body + ' ' + (n.get('standfirst') or '')
        nx = n.get('next'); nx = (nx.get('text') if isinstance(nx, dict) else nx) or ''
        for fld, val in (('lead_summary', n.get('lead_summary') or ''), ('next', nx)):
            miss = _num(val) - _num(body2)
            if miss: fails.append(f'news "{n["id"]}": {fld} has {", ".join(sorted(miss))} but its story text does not: {val[:120]}')
except (OSError, ValueError):
    pass
# The share where the AI did the acting is a last-12-months figure; it must be the same everywhere and never called "this year's".
for page in pages:
    t = open(page, encoding='utf-8', errors='ignore').read()
    if re.search(r"this year[’']s real-world", t): fails.append(f"{page}: says \"this year's real-world\"; the figure covers the last 12 months")
    for m in re.finditer(r'(\d{1,3})%\s*(?:</b>)?\s*of (?:the last 12 months[’\'] |real-world)[^<]{0,80}?(?:did the acting|acted)', t):
        if int(m.group(1)) != build['agentic_share']: fails.append(f'{page}: "{m.group(0)[:80]}" but the data says {build["agentic_share"]}%')
for f in fails: print('FAIL:', f)
print(f'check_site: {len(fails)} failures, {len(warns)} warnings, {len(pages)} pages checked')
sys.exit(1 if fails else 0)
