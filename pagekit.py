"""Shared pieces for the data-driven page families (checks/, jobs/, can-ai/, exposed/, midterms-2026/).

Every family follows the help/learn rules: a page is built as a hidden draft (noindex, out of the sitemap) until its family
is approved in research/approvals.json; approved pages carry the reviewer byline and go into data/tool_urls.json for the
sitemap. Individual pages can also be held back by a quality gate (thin pages stay noindex even when the family is approved),
which is what keeps programmatic pages on the right side of Google's scaled-content rules."""
import json, os, html, datetime as dt, re
from pageshell import shell
esc = html.escape
here = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(here, 'data/meta.json'), encoding='utf-8'))
SITE = meta['site_url']
REPO = meta.get('repo_url', 'https://github.com/ColinBalfe/ai-incident-index')
INC = {r['id']: r for r in json.load(open(os.path.join(here, 'data/incidents.json'), encoding='utf-8'))}
REVIEWER = 'Colin Balfe'
ROBOTS_ON = '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'
ROBOTS_OFF = '<meta name="robots" content="noindex, nofollow">'
try:
    APPROVALS = json.load(open(os.path.join(here, 'research/approvals.json'), encoding='utf-8'))
except (OSError, ValueError):
    APPROVALS = {}

def approved(family):
    v = APPROVALS.get(family) or {}
    return bool(v.get('approved')), v.get('reviewed') or ''

def slugify(s):
    s = re.sub(r'\([^)]*\)', '', s or '').lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:70].strip('-') or 'org'

def a(u, t):
    if not u: return esc(t)
    return f'<a href="{esc(u)}"' + (' target="_blank" rel="noopener noreferrer"' if u.startswith('http') else '') + f'>{esc(t)}</a>'

def fdate(s):
    try: return dt.date.fromisoformat(s[:10]).strftime('%b %-d, %Y')
    except Exception: return s or ''

def case_ref(ref, label=''):
    """A link to an index case file plus its primary source, or a plain source link."""
    if ref in INC:
        r = INC[ref]
        tail = f' <small>({a(r.get("source_url") or "", r.get("source_label") or "source")}{" · lab or test finding" if r.get("setting") != "wild" else ""})</small>' if r.get('source_url') else ''
        return f' <a href="/i/{esc(ref)}/">The case file →</a>{tail}'
    if ref and ref.startswith('http'):
        return f' <small>({a(ref, label or "source")})</small>'
    return ''

STYLE = """<style>
.pk{max-width:780px}
.pk .kick{font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--alarm);margin:18px 0 8px} .pk .kick a{color:inherit}
.pk h1{font-family:var(--serif);font-size:clamp(2rem,5vw,3rem);line-height:1.05;margin:0 0 10px}
.pk .meta{font-size:13px;color:var(--ink-3);margin-bottom:16px}
.pk .aka{font-size:15px;color:var(--ink-2);margin:-2px 0 8px}
.pk .box{border:2px solid var(--ink);border-left:8px solid var(--alarm);background:var(--panel);padding:16px 18px;margin:0 0 8px}
.pk .box b.k{display:block;font:800 12px/1 Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--alarm);margin-bottom:8px}
.pk .box p{margin:0;font-size:clamp(1.08rem,2vw,1.28rem);line-height:1.45;font-family:var(--serif)}
.pk .verdict{display:inline-block;font:800 13px/1 Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;padding:6px 9px;border:2px solid var(--alarm);color:var(--alarm);margin-bottom:8px}
.pk h2{font-family:var(--serif);font-size:1.5rem;margin:32px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}
.pk h3{font-size:1.05rem;margin:16px 0 6px}
.pk p,.pk li{line-height:1.6}
.pk dl{margin:0;display:block!important} .pk dl div{padding:9px 0;border-bottom:1px solid var(--line)} .pk dt{font-weight:700} .pk dd{margin:2px 0 0;color:var(--ink-2)}
.pk ol.steps{counter-reset:s;list-style:none;padding:0;margin:0}
.pk ol.steps li{counter-increment:s;position:relative;padding:10px 0 10px 46px;border-bottom:1px solid var(--line)}
.pk ol.steps li::before{content:counter(s);position:absolute;left:0;top:10px;width:32px;height:32px;border-radius:50%;background:var(--alarm);color:#fff;font:800 16px/32px Arial,sans-serif;text-align:center}
.pk ol.steps b{display:block}
.pk ul.checks{list-style:none;padding:0} .pk ul.checks li{padding:10px 0 10px 34px;border-bottom:1px solid var(--line);position:relative} .pk ul.checks li::before{content:'?';position:absolute;left:0;top:10px;width:24px;height:24px;border:2px solid var(--ink);border-radius:4px;font:800 14px/22px Arial,sans-serif;text-align:center}
.pk ul.checks b{display:block}
.pk .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:10px}
.pk .stats div{border:1px solid var(--line-2);border-top:3px solid var(--alarm);background:var(--panel);padding:12px} .pk .stats b{display:block;font-size:1.5rem;line-height:1.1} .pk .stats span{display:block;font-size:14px;margin-top:4px} .pk .stats small{display:block;font-size:12px;margin-top:6px;color:var(--ink-3)} .pk .stats small a{color:var(--ink-3)}
.pk ul.rec{list-style:none;padding:0} .pk ul.rec li{padding:9px 0;border-bottom:1px solid var(--line)} .pk ul.rec time{font-weight:700;margin-right:6px} .pk ul.rec small{color:var(--ink-3)} .pk ul.rec small a{color:var(--ink-3)}
.pk table{width:100%;border-collapse:collapse;font-size:14.5px;margin:8px 0} .pk th,.pk td{text-align:left;vertical-align:top;padding:8px 6px;border-bottom:1px solid var(--line)} .pk .tw{overflow-x:auto}
.pk .st{display:inline-block;font:800 11px/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:4px 6px;border:1px solid var(--ink-3);color:var(--ink-2);white-space:nowrap}
.pk .st.yes,.pk .st.deployed,.pk .st.confirmed{border-color:var(--alarm);color:var(--alarm)} .pk .st.partly,.pk .st.demonstrated,.pk .st.attacked{border-color:#B5751A;color:#B5751A}
.pk details{border-bottom:1px solid var(--line);padding:10px 0} .pk summary{font-weight:700;cursor:pointer;font-size:16.5px} .pk details p{margin:8px 0 0}
.pk .src{font-size:14px} .pk .src li{margin:4px 0}
.pk .share{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.pk .share button{font:700 14px/1 var(--sans);padding:10px 14px;border:1px solid var(--ink);background:var(--ink);color:var(--paper);cursor:pointer} .pk .share button.alt{background:transparent;color:var(--ink)}
.pk .disc{font-size:13px;color:var(--ink-3);margin-top:26px;border-top:1px solid var(--line);padding-top:12px}
.pk .draft{background:#FFF4D6;color:#5A4300;border:1px solid #E5C76B;padding:10px 12px;font-size:14px;margin:12px 0}
.pk .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr));gap:10px;padding:0;list-style:none} .pk .grid li{border:1px solid var(--line-2);background:var(--panel);padding:12px} .pk .grid a{font-weight:700}
.pk .cap{border:2px solid var(--ink);padding:14px 16px;margin:24px 0;background:var(--panel)} .pk .cap form{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px} .pk .cap input{flex:1 1 14rem;padding:10px;font:inherit;border:1px solid var(--ink-3)} .pk .cap button{padding:10px 14px;font:700 14px/1 var(--sans);background:var(--ink);color:var(--paper);border:0;cursor:pointer}
.pk .search{width:100%;padding:12px;font:inherit;font-size:17px;border:2px solid var(--ink);margin:8px 0}
@media print{.mast,footer,.share,.draft,.skip,.cap{display:none!important}}
</style>"""

def capture(prompt, tag):
    """An alert sign-up box, shown only once an email provider is configured (meta.newsletter.action); otherwise nothing."""
    nl = meta.get('newsletter') or {}
    if not nl.get('action'):
        return ''
    fields = ''.join(f'<input type="hidden" name="{esc(k)}" value="{esc(v)}">' for k, v in (nl.get('fields') or {}).items())
    return (f'<section class="cap"><b>{esc(prompt)}</b><form action="{esc(nl["action"])}" method="post" target="_blank">{fields}'
            f'<input type="hidden" name="tag" value="{esc(tag)}"><input type="email" name="{esc(nl.get("email_field") or "email")}" placeholder="you@example.com" required aria-label="Email address">'
            f'<button type="submit">Alert me</button></form></section>')

def faq_html(faq):
    return ''.join(f'<details{" open" if i < 2 else ""}><summary>{esc(q)}</summary><p>{esc(t)}</p></details>' for i, (q, t) in enumerate(faq))

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}

def frame(*, draft, rev, updated, crumbs, family_label):
    """Top of page: draft banner, breadcrumb, byline line."""
    bc = ' · '.join(f'<a href="{esc(u)}">{esc(t)}</a>' if u else esc(t) for t, u in crumbs)
    by = (f'Reviewed by {REVIEWER} on {fdate(rev)} · ' if (not draft and rev) else '') + f'Updated {fdate(updated)}'
    return (('<div class="draft"><b>Draft, not yet reviewed.</b> Hidden from search engines until every fact is checked and approved.</div>' if draft else '')
            + f'<nav class="kick" aria-label="Breadcrumb">{bc}</nav>', by)

def footer_note(draft):
    return (f'<p class="disc">Spot an error or something out of date? <a href="{esc(REPO)}/issues">Tell us</a>; corrections are made and logged. '
            f'Written with AI assistance from public sources; {"every fact checked and approved by " + REVIEWER if not draft else "awaiting fact-check and approval by " + REVIEWER}. '
            'General information, not legal, medical or financial advice.</p>')

def write(path, *, url, title, desc, body, graph, draft, img=None, crumbs=()):
    img = img or SITE + 'assets/og.png'
    bl = {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t, "item": (SITE + u.lstrip('/')) if u else url} for i, (t, u) in enumerate([('Warning Shots', '/')] + list(crumbs))]}
    ld = json.dumps({"@context": "https://schema.org", "@graph": list(graph) + [bl]}, ensure_ascii=False).replace('</', '<\\/')
    out = shell(title=title, desc=desc, url=url, img=img, body=STYLE + body, jsonld=ld, kind='family')
    if draft:
        out = out.replace(ROBOTS_ON, ROBOTS_OFF, 1)
        assert ROBOTS_OFF in out
    os.makedirs(os.path.join(here, os.path.dirname(path)), exist_ok=True)
    open(os.path.join(here, path), 'w', encoding='utf-8').write(out)

def webpage(url, title, desc, updated, draft, rev, img=None):
    wp = {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en", "dateModified": updated}
    if img: wp["primaryImageOfPage"] = img
    if not draft and rev:
        wp["reviewedBy"] = {"@type": "Person", "name": REVIEWER}; wp["lastReviewed"] = rev
    return wp

def article(url, title, desc, updated, draft, rev, section, citations, img=None):
    return {"@type": "Article", "headline": title[:110], "description": desc, "url": url, "mainEntityOfPage": url, "image": [img or SITE + 'assets/og.png'],
            "datePublished": updated, "dateModified": updated, "inLanguage": "en", "isAccessibleForFree": True, "articleSection": section,
            "citation": [u for u in citations if u][:30],
            "author": {"@type": "Person", "name": REVIEWER} if (not draft and rev) else {"@type": "Organization", "name": "Warning Shots", "url": SITE},
            "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": SITE, "logo": {"@type": "ImageObject", "url": SITE + "assets/icon-512.png"}}}

def register(prefix, urls):
    """Replace this family's entries in data/tool_urls.json (read by build_pages.py for the sitemap)."""
    p = os.path.join(here, 'data/tool_urls.json')
    try: tu = json.load(open(p))
    except (OSError, ValueError): tu = []
    tu = [u for u in tu if not u.startswith(SITE + prefix)] + list(urls)
    json.dump(tu, open(p, 'w'))
    json.dump(list(urls), open(os.path.join(here, f'data/{prefix.strip("/").replace("-", "_")}_urls.json'), 'w'))
