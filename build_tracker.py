#!/usr/bin/env python3
"""The live-incident tracker page: php2shell/ (or whatever meta.live_incident names, if it has a deep dive).
A plain, crawlable page written for what people search during a live incident: the name, the CVE numbers, 'am I affected',
'fixed version', 'is it being exploited', 'CISA KEV'. Built from the same data the refresh updates, so it is current on every
run. FAQPage + Article JSON-LD. Run after build_site.py, before build_pages.py (which adds it to the sitemap)."""
import json, os, html, datetime as dt
from zoneinfo import ZoneInfo
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pageshell import shell
esc = html.escape
L = lambda f: json.load(open(f'data/{f}.json', encoding='utf-8'))
meta = L('meta'); site = meta['site_url']; AS_OF = meta['as_of']
ET = ZoneInfo('America/New_York')
as_of_label = dt.datetime.fromisoformat(AS_OF).astimezone(ET).strftime('%b %-d, %Y, %-I:%M %p ET')
inc_id = 'php2shell'
P = json.load(open('research/php2shell.json', encoding='utf-8'))['incident']
dd = next(d for d in L('deepdives') if d['incident_id'] == inc_id)
live = L('live'); tl = [t for t in L('timeline') if t.get('incident_id') == inc_id]
vic = L('victims_php'); sig = L('signals_php'); news = [n for n in L('news') if n.get('topic') == 'php2shell']
cves = P['cves']; fixed = P.get('fixed_versions', [])
liv = {x['key']: x for x in live}

def a(u, t): return f'<a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{esc(t)}</a>'
def fd(iso):
    try: return dt.date.fromisoformat(iso[:10]).strftime('%b %-d')
    except Exception: return esc(iso or '')

conf = liv.get('confirmed', {}); kev = liv.get('kev', {}); att = liv.get('attempts', {}); uk = liv.get('uk', {})
faq = [
    ('What is PHP2Shell?', f"PHP2Shell is the name for {len(cves)} critical flaws in PHP's core engine ({', '.join(cves)}, CVSS up to {P.get('cvss_max')}), found with the help of AI by Wiz Research with Calif and OpenAI. They let an attacker run code on, or read memory from, a server running PHP without logging in. Fixes shipped on Oct 21, 2026."),
    ('Which PHP versions fix PHP2Shell?', f"The fixed releases are PHP {', '.join(fixed)}. {P.get('affected_versions', '')} Versions before 8.2 get no official fix."),
    ('Am I affected?', "If a website you run uses PHP (WordPress, Drupal, Magento and most shared hosting do), it was exposed until upgraded to a fixed release. Ask your host or developer which PHP version the site runs; if it is older than the fixed releases above, upgrade or take it offline until you can."),
    ('Is PHP2Shell being exploited?', f"{att.get('detail', '')} Code execution has been confirmed on researchers' decoy servers (honeypots)."),
    ('Has any organization been hacked through PHP2Shell?', conf.get('detail') or 'No organization has been confirmed breached by name.'),
    ('Is PHP2Shell on CISA’s Known Exploited Vulnerabilities list?', kev.get('detail') or P.get('cisa_kev', '')),
    ('What is CVE-2026-115560?', "A third PHP bug disclosed on Oct 23 that the Oct 21 fixes do not cover. PHP issued an informational advisory and is leaving the fix to the next regular release; Korea's KISA published a temporary workaround. No exploitation has been reported."),
    ('Did AI find PHP2Shell?', f"Yes. Wiz Research, Calif and OpenAI used frontier AI models ({', '.join(P.get('ai_models_used', []))}) to find and weaponize the flaws in August 2026; they were reported to PHP on Aug 24 and disclosed Oct 21. It is the first AI-found bug to push governments to switch off public services as a precaution."),
]
title = f"PHP2Shell live tracker: {', '.join(cves)} exploitation, victims, CISA KEV status"
desc = f"Updated {as_of_label}. Is PHP2Shell being exploited, who has been hit, which PHP versions are fixed ({', '.join(fixed)}), and whether CISA has listed it. Every fact sourced."
url = site + 'php2shell/'

stats = ''.join(f'<div class="tk-st"><b>{esc(x["value"])}</b><span>{esc(x["label"])}</span><small>{a(x["source_url"], x["source_label"])}</small></div>' for x in live)
rows = sorted(tl, key=lambda t: t['date'], reverse=True)[:25]
tl_html = ''.join(f'<li><time>{fd(t["date"])}</time><span>{esc(t["event"])} {a(t["source_url"], "source") if t.get("source_url") else ""}</span></li>' for t in rows)
order = {'confirmed': 0, 'attacked': 1, 'disrupted': 2}
vs = sorted(vic, key=lambda v: (order.get(v.get('status_group'), 3), v.get('date') or ''))
v_html = ''.join(f'<tr><td><b>{esc(v["organization"])}</b><small>{esc(v.get("sector") or "")}</small></td><td>{esc(v.get("country") or "")}</td><td>{esc(v.get("status") or "")}</td><td>{esc(v.get("extent") or "")} {a(v["source_url"], v.get("source_label") or "source") if v.get("source_url") else ""}</td></tr>' for v in vs)
s_html = ''.join(f'<li><time>{fd(s["date"])}</time><span><b>{esc(s.get("org") or "")}</b>: {esc(s.get("gist") or "")} {a(s["url"], "source") if s.get("url") else ""}</span></li>' for s in sorted(sig, key=lambda s: s['date'], reverse=True)[:12])
n_html = ''.join(f'<li><a href="{esc(n["url"])}" target="_blank" rel="noopener noreferrer">{esc(n["title"])}</a> <small>{esc(n.get("outlet") or "")}, {fd(n["published"])}</small></li>' for n in sorted(news, key=lambda n: n['published'], reverse=True)[:15])
faq_html = ''.join(f'<details{" open" if i < 3 else ""}><summary>{esc(q)}</summary><p>{esc(t)}</p></details>' for i, (q, t) in enumerate(faq))

body = f"""
<style>
.tk h1{{font-family:var(--serif);font-size:clamp(2rem,5vw,3.4rem);line-height:1.02;margin:18px 0 6px}}
.tk .cv{{font-size:14px;color:var(--ink-2)}} .tk .up{{display:inline-block;margin-top:8px;font-size:13px;font-weight:600;color:var(--alarm)}}
.tk-sum{{font-size:18px;line-height:1.5;max-width:70ch;margin:16px 0 6px}} .tk-more summary{{font-size:14px;color:var(--alarm)}}
.tk-note{{font-size:15px;line-height:1.55;max-width:72ch;margin:16px 0}}
.tk-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:10px;margin:18px 0}}
.tk-st{{border:1px solid var(--line-2);border-top:3px solid var(--alarm);padding:12px;background:var(--panel)}} .tk-st b{{display:block;font-size:1.6rem;line-height:1.1}} .tk-st span{{display:block;font-size:13px;color:var(--ink-2);margin-top:4px}} .tk-st small{{display:block;font-size:11.5px;margin-top:6px}} .tk-st small a{{color:var(--ink-3)}}
.tk h2{{font-family:var(--serif);font-size:1.6rem;margin:34px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}}
.tk-fix{{background:var(--panel);border:1px solid var(--line-2);padding:14px 16px}} .tk-fix code{{font-weight:700;font-size:15px}}
.tk details{{border-bottom:1px solid var(--line);padding:10px 0}} .tk summary{{font-weight:700;cursor:pointer;font-size:16px}} .tk details p{{margin:8px 0 0;line-height:1.55}}
.tk ul.tl{{list-style:none;padding:0;margin:0}} .tk ul.tl li{{display:grid;grid-template-columns:4.2rem 1fr;gap:10px;padding:8px 0;border-bottom:1px solid var(--line);font-size:14.5px;line-height:1.45}} .tk ul.tl time{{font-weight:700;color:var(--ink-2)}} .tk ul.tl a{{color:var(--ink-3);font-size:12px}}
.tk table{{width:100%;border-collapse:collapse;font-size:13.5px}} .tk th,.tk td{{text-align:left;vertical-align:top;padding:8px 6px;border-bottom:1px solid var(--line)}} .tk td small{{display:block;color:var(--ink-3)}} .tk td a{{color:var(--ink-3);font-size:12px}}
.tk .tw{{overflow-x:auto}} .tk ul.nw{{padding-left:18px}} .tk ul.nw li{{margin:6px 0}} .tk ul.nw small{{color:var(--ink-3)}}
</style>
<article class="tk">
<h1>PHP2Shell live tracker</h1>
<div class="cv">{esc(' · '.join(cves))} · CVSS up to {esc(str(P.get('cvss_max')))} · fixed Oct 21, 2026</div>
<span class="up">Updated {esc(as_of_label)} · checked three times a day</span>
<p class="tk-sum"><b>Status:</b> {esc(conf.get('value',''))} {esc(conf.get('label',''))}. {esc(kev.get('label','').capitalize() if False else '')}CISA Known Exploited Vulnerabilities: <b>{esc(kev.get('value',''))}</b>. Exploit attempts: <b>{esc(att.get('value',''))}</b> ({esc(att.get('label',''))}). Fixed in PHP {esc(', '.join(fixed))}.</p>
<details class="tk-more"><summary>The full latest note</summary><p class="tk-note">{esc(meta.get('live_note') or dd.get('now_text') or '')}</p></details>
<div class="tk-grid">{stats}</div>
<h2>Am I affected? What to do</h2>
<div class="tk-fix"><p>Fixed PHP releases: {' '.join(f'<code>{esc(v)}</code>' for v in fixed)}. {esc(P.get('affected_versions', ''))}</p><p>If you run a website on PHP (WordPress, Drupal, Magento and most shared hosting), ask your host or developer which version it runs. Older than the releases above: upgrade, or take it offline until you can. Versions before 8.2 will not get an official fix. A third bug, CVE-2026-115560, is not covered by these releases; follow your host's or PHP's guidance on it.</p><p><a href="/index/#d=php2shell">The full interactive breakdown: map, every organization, what officials said →</a></p></div>
<h2>Questions people are asking</h2>
{faq_html}
<h2>Latest, newest first</h2>
<ul class="tl">{tl_html}</ul>
<h2>Who has been hit, attacked or taken offline ({len(vic)})</h2>
<p class="cv">Confirmed compromises first. "Attacked" includes honeypots and blocked attempts; most entries are precautionary shutdowns, not breaches.</p>
<div class="tw"><table><thead><tr><th>Organization</th><th>Country</th><th>Status</th><th>What happened</th></tr></thead><tbody>{v_html}</tbody></table></div>
<h2>What officials have said</h2>
<ul class="tl">{s_html}</ul>
<h2>The latest reporting</h2>
<ul class="nw">{n_html}</ul>
</article>
"""
ld = json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Article", "headline": title[:110], "description": desc, "url": url, "mainEntityOfPage": url, "image": [site + 'assets/og.png'],
     "datePublished": "2026-10-21T14:00:00Z", "dateModified": AS_OF, "isAccessibleForFree": True,
     "author": {"@type": "Organization", "name": "Warning Shots", "url": site},
     "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site, "logo": {"@type": "ImageObject", "url": site + "assets/icon-512.png"}}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}]},
    ensure_ascii=False).replace('</', '<\\/')
os.makedirs('php2shell', exist_ok=True)
open('php2shell/index.html', 'w', encoding='utf-8').write(shell(title=title, desc=desc, url=url, img=site + 'assets/og.png', body=body, jsonld=ld, kind='tracker'))
print('tracker php2shell/:', len(rows), 'timeline,', len(vic), 'organizations,', len(faq), 'FAQs')
