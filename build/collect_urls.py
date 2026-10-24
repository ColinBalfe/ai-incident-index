#!/usr/bin/env python3
"""Collect every source URL in data/*.json (recursively) -> a URL list for the link audit, plus a map of where each is used.
Usage: python3 build/collect_urls.py <urls.txt> <usage.json>"""
import json, os, sys, glob, re
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
urls = {}
def walk(x, where):
    if isinstance(x, dict):
        wid = x.get('id') or x.get('incident_id') or ''
        for k, v in x.items(): walk(v, f'{where}#{wid}' if wid and not where.endswith('#' + str(wid)) else where)
    elif isinstance(x, list):
        for v in x: walk(v, where)
    elif isinstance(x, str) and re.match(r'https?://', x.strip()):
        u = x.strip(); urls.setdefault(u, set()).add(where)
for f in sorted(glob.glob(os.path.join(root, 'data', '*.json'))):
    name = os.path.basename(f)
    if name in ('bundle.json', 'posts.json'): continue
    try: walk(json.load(open(f, encoding='utf-8')), name[:-5])
    except ValueError: pass
out_urls, out_map = sys.argv[1], sys.argv[2]
open(out_urls, 'w').write('\n'.join(sorted(urls)) + '\n')
json.dump({u: sorted(w) for u, w in sorted(urls.items())}, open(out_map, 'w'), indent=0)
print(len(urls), 'urls from', len(set(w.split('#')[0] for ws in urls.values() for w in ws)), 'files')
