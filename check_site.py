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
pages = [p for p in glob.glob('**/*.html', recursive=True) if not p.startswith(('node_modules', 'archive', 'shots')) and p != 'index.template.html']
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

for w in warns: print('warn:', w)
for f in fails: print('FAIL:', f)
print(f'check_site: {len(fails)} failures, {len(warns)} warnings, {len(pages)} pages checked')
sys.exit(1 if fails else 0)
