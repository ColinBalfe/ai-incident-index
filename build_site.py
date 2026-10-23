#!/usr/bin/env python3
"""Fill index.template.html -> index.html using data/meta.json and data/incidents.json (for OG tags), and stamp a build id.
Run from the site/ directory after updating data/. Then run make_og.py to refresh the share image."""
import json, time, datetime as dt, os, sys
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
meta = json.load(open('data/meta.json'))
inc = json.load(open('data/incidents.json'))

def sev(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    return round(0.55 * harm + 0.45 * sig)

as_of = dt.date.fromisoformat(meta['as_of'][:10])
yr = dt.timedelta(days=365)
def inwin(r, a, b): d = dt.date.fromisoformat(r['date']); return a < d <= b
last12 = [r for r in inc if inwin(r, as_of - yr, as_of)]
prior12 = [r for r in inc if inwin(r, as_of - 2 * yr, as_of - yr)]
s12 = sum(sev(r) >= 60 for r in last12); p12 = sum(sev(r) >= 60 for r in prior12)
wild_recent = [r for r in last12 if r['setting'] == 'wild']
share = round(100 * sum(r['A'] >= 3 for r in wild_recent) / max(1, len(wild_recent)))
n = len(inc)
title = meta.get('site_name', 'The AI Incident Index')
og_title = f"Severe AI incidents went from {p12} to {s12} in a year. {title}"
og_desc = f"{n} AI safety incidents since 2023, scored 0–100 and sourced. In {share}% of this year's real-world cases the AI acted on its own. Live tracking of {meta.get('live_name', 'the incident unfolding now')}, 20 dated forecasts, and what officials have said. Updated {meta['as_of_label']}."
build = time.strftime('%Y%m%d%H%M', time.gmtime())
tpl = open('index.template.html', encoding='utf-8').read()
out = (tpl.replace('{{OG_TITLE}}', og_title.replace('"', '&quot;')).replace('{{OG_DESC}}', og_desc.replace('"', '&quot;'))
          .replace('{{SITE_URL}}', meta['site_url']).replace('{{REPO_URL}}', meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')).replace('{{BUILD}}', build))
open('index.html', 'w', encoding='utf-8').write(out)
json.dump(dict(build=build, og_title=og_title, og_desc=og_desc, severe_last12=s12, severe_prior12=p12, agentic_share=share, n=n), open('assets/build.json', 'w'))
print('built', build, '|', og_title, '|', og_desc)
