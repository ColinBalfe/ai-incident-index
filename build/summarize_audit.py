#!/usr/bin/env python3
"""Turn lychee's JSON report into research/link_audit.json: dead links (404/410/DNS) and unreachable ones (5xx, timeouts), with where each is used.
Usage: python3 build/summarize_audit.py <lychee.json> <usage.json> <out.json>"""
import json, sys, datetime as dt
rep = json.load(open(sys.argv[1])); usage = json.load(open(sys.argv[2]))
dead, unreachable = [], []
for inp, items in (rep.get('fail_map') or {}).items():
    for it in items:
        url = it.get('url'); st = it.get('status') or {}
        code = st.get('code'); text = st.get('text') or st.get('details') or json.dumps(st)[:120]; blob = (str(st.get('text', '')) + ' ' + str(st.get('details', ''))).lower()
        row = dict(url=url, status=code if code is not None else text, used_in=usage.get(url, []))
        if code in (404, 410) or (code is None and any(k in blob for k in ('dns', 'resolve', 'certificate', 'not found'))): dead.append(row)
        else: unreachable.append(row)
out = dict(checked_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), total=rep.get('total'), successful=rep.get('successful'), excluded=rep.get('excludes'),
           dead=sorted(dead, key=lambda r: r['url']), unreachable=sorted(unreachable, key=lambda r: r['url']),
           note='dead: 404/410/DNS failures, replace the source or link an archived copy; unreachable: timeouts and 5xx, re-check by hand before changing anything. 401/403/429 count as alive (the site answered).')
json.dump(out, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('checked', rep.get('total'), 'dead', len(dead), 'unreachable', len(unreachable))
