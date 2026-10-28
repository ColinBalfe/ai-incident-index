"""One set of rules for the AI layoffs ledger, used by the ledger page (build_archive.py) and the job-cuts chart (build_chart.py),
so the page and the chart can never disagree: one entry per employer per month (two stories on the same cut count once; the
company's own word wins over reporters'), and industry tallies are not cuts."""
import re

TALLY = re.compile(r'layoffs reach|tall(y|ies)|in 2026; |across the industry|layoffs tracker', re.I)


def employer(what):
    w = re.sub(r'^(The )', '', what or '')
    m = re.match(r"([A-Z][\w&.'’-]*(?: [A-Z][\w&.'’-]*){0,3})", w)
    e = m.group(1) if m else w[:30]
    e = re.sub(r' (To|Offers|Confirms|Cutting|Plans|Will|Says|Cuts)$', '', e)
    return {'Dutch': 'Dutch government', 'Dutch cabinet': 'Dutch government'}.get(e, e)


def clean(rows, who_key='who', is_company=lambda w: w == 'co'):
    out, seen = [], {}
    for x in sorted(rows, key=lambda x: x['date']):
        if TALLY.search(x.get('what') or ''):
            continue
        x['emp'] = employer(x['what']); k = (x['date'][:7], x['emp'].lower())
        if k in seen:
            prev = seen[k]
            if is_company(x[who_key]) and not is_company(prev[who_key]):
                prev[who_key] = x[who_key]
            continue
        seen[k] = x; out.append(x)
    return out
