#!/usr/bin/env python3
"""The data-driven page families: checks/ (Is This a Scam?), jobs/ (Can AI Do Your Job?), can-ai/ (What AI Can Now Do),
exposed/ (Am I Exposed?) and midterms-2026/ (the election deepfake tracker).

Sources: research/checks.json, research/jobs.json, research/can_ai.json, research/midterm_fakes.json,
research/midterm_context.json, data/victims.json + data/incidents.json. Approval per family in research/approvals.json.

Quality gate for exposed/: an organisation gets an indexable page only when the record says something specific about it
(a confirmed compromise, an attack on it, or appearances in two or more incidents). Every other organisation is listed and
searchable on the hub, and its page stays noindex, so we never publish hundreds of near-identical thin pages.
Run after build_learn.py, before build_pages.py."""
import urllib.parse
import json, os, collections
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
from pagekit import *

TODAY = json.load(open('data/meta.json'))['as_of'][:10]
L = lambda f: json.load(open(f, encoding='utf-8'))

def stats_html(stats):
    return '<div class="stats">' + ''.join(f'<div><b>{esc(n)}</b><span>{esc(t)}</span><small>{a(u, s)}</small></div>' for n, t, u, s in stats) + '</div>' if stats else ''
def src_html(sources):
    return '<h2>Sources</h2><ul class="src">' + ''.join(f'<li>{a(u, t)}</li>' for t, u in sources) + '</ul>'
def steps_html(steps):
    return '<ol class="steps">' + ''.join(f'<li><b>{esc(t)}</b>{esc(d)}</li>' for t, d in steps) + '</ol>'
def rel_html(paths):
    names = {'voice-clone-scam-call': '/help/voice-clone-scam-call/', 'ai-scam-texts': '/help/ai-scam-texts/', 'fake-nude-image': '/help/ai-fake-nude-image-what-to-do/', 'ai-fake-nude-image-what-to-do': '/help/ai-fake-nude-image-what-to-do/'}
    out = []
    for p in paths:
        u = names.get(p) or (p if p.startswith('/') else f'/checks/{p}/')
        out.append(f'<li><a href="{esc(u)}">{esc(TITLES.get(u, u))} →</a></li>')
    return '<h2>Related</h2><ul>' + ''.join(out) + '</ul>' if out else ''

# titles for related links
TITLES = {}
for f, pre in (('research/help.json', '/help/'), ('research/learn.json', '/learn/')):
    for x in L(f): TITLES[pre + x['slug'] + '/'] = x['title']

# ======================================================== checks/
CH = L('research/checks.json'); ok, rev = approved('checks')
for c in CH: TITLES[f"/checks/{c['slug']}/"] = c['title']
urls = []
for c in CH:
    url = SITE + f"checks/{c['slug']}/"
    top, by = frame(draft=not ok, rev=c.get('reviewed', ''), updated=c.get('updated', TODAY), crumbs=[('Is this a scam?', '/checks/'), (c['pattern'], '')], family_label='checks')
    checks = '<ul class="checks">' + ''.join(f'<li><b>{esc(q)}</b>{esc(w)}</li>' for q, w in c['check']) + '</ul>'
    cases = '<ul class="rec">' + ''.join(f'<li><time>{esc(w)}</time> <b>{esc(where)}</b>. {esc(t)}' + (f' <small>({a(u, o)})</small>' if u else '') + (case_ref(i) if i else '') + '</li>' for w, where, t, u, o, i in c['cases']) + '</ul>'
    report = '<ul>' + ''.join(f'<li><b>{esc(w)}:</b> {a(u, t) if u else esc(t)}</li>' for w, u, t in c['report']) + '</ul>'
    card = 'IS THIS A SCAM? ' + c['pattern'].upper() + '\n' + '\n'.join(f'□ {q}' for q, _ in c['check']) + f'\nIf any answer worries you: stop, and check with someone you trust.\nwarningshots.ai/checks/{c["slug"]}/'
    body = f"""<article class="pk">{top}
<h1>{esc(c['h1'])}</h1><div class="meta">{esc(by)} · Every fact links to its source</div>
<section class="box"><b class="k">The short answer</b><p>{esc(c['verdict'])}</p></section>
<div class="share"><button type="button" data-copy="{esc(c['h1'] + ' ' + url)}">Copy link to send to family</button><button type="button" class="alt" data-copy="{esc(card)}">Copy the checklist</button><button type="button" class="alt" onclick="window.print()">Print</button></div>
<h2>The check</h2><p>Answer these honestly. A single "yes" to a warning sign is enough to stop.</p>{checks}
<h2>If it's happening right now</h2><p>{esc(c['now'])}</p>
<h2>How this scam works</h2>{''.join(f'<p>{esc(x)}</p>' for x in c['how_it_works'])}
<h2>What AI changes</h2><p>{esc(c['ai_role'])}</p>
<h2>What to do, step by step</h2>{steps_html(c['steps'])}
{'<h2>How big this is</h2>' + stats_html(c['stats']) if c.get('stats') else ''}
<h2>Real cases</h2>{cases}
<h2>Where to report it</h2>{report}
<h2>Questions people ask</h2>{faq_html(c['faq'])}
{rel_html(c.get('related', []))}
{src_html(c['sources'])}
{capture('Get the next scam pattern before it reaches you', 'checks')}
{footer_note(not ok)}</article>"""
    howto = {"@type": "HowTo", "name": c['h1'], "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d} for i, (t, d) in enumerate(c['steps'])]}
    write(f"checks/{c['slug']}/index.html", url=url, title=c['title'], desc=c['desc'], body=body, draft=not ok, crumbs=[('Is this a scam?', '/checks/'), (c['pattern'], '')],
          graph=[webpage(url, c['title'], c['desc'], c.get('updated', TODAY), not ok, c.get('reviewed', '')), article(url, c['title'], c['desc'], c.get('updated', TODAY), not ok, c.get('reviewed', ''), 'Is this a scam?', [u for _, u in c['sources']]), howto, faq_ld(c['faq'])])
    if ok: urls.append(url)
items = ''.join(f'<li><a href="/checks/{esc(c["slug"])}/">{esc(c["h1"])}</a><br><small>{esc(c["verdict"])}</small></li>' for c in CH)
items += f'<li><a href="/help/voice-clone-scam-call/">{esc(TITLES.get("/help/voice-clone-scam-call/", "A loved one calls in a panic"))}</a></li><li><a href="/help/ai-scam-texts/">{esc(TITLES.get("/help/ai-scam-texts/", "AI scam texts"))}</a></li>'
hub = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Is this a scam?</h1><p>One page for each scam that AI is making more convincing. Each one starts with the check: a few yes-or-no questions you can answer in a minute, at midnight, before you send anything.</p><ul class="grid">{items}</ul>{capture('Get the next scam pattern before it reaches you', 'checks')}{footer_note(not ok)}</article>"""
write('checks/index.html', url=SITE + 'checks/', title='Is this a scam? Checks for AI-powered scams', desc='Quick yes-or-no checks for the scams AI makes more convincing: deepfake celebrity investments, boss gift-card requests, romance crypto, QR codes, fake jobs and more.', body=hub, draft=not ok, crumbs=[('Is this a scam?', '')],
      graph=[{"@type": "CollectionPage", "name": "Is this a scam?", "url": SITE + 'checks/'}])
register('checks/', ([SITE + 'checks/'] if ok else []) + urls)
print(f'checks/: {len(CH)} pages ({"approved" if ok else "drafts, noindex"})')

# ======================================================== jobs/
J = L('research/jobs.json'); ok, rev = approved('jobs'); urls = []
STL = {'deployed': 'In real use', 'demonstrated': 'Shown in tests or pilots', 'not yet': 'Not yet'}
for j in J['jobs']:
    url = SITE + f"jobs/{j['slug']}/"
    top, by = frame(draft=not ok, rev=j.get('reviewed', ''), updated=j.get('updated', TODAY), crumbs=[('Can AI do your job?', '/jobs/'), (j['occupation'], '')], family_label='jobs')
    rows = ''.join(f'<tr><td>{esc(t["task"])}</td><td><span class="st {esc(t["status"].replace(" ", "-"))}">{esc(STL.get(t["status"], t["status"]))}</span></td><td>{esc(t["evidence"])} <small>({a(t["url"], t["label"])})</small></td></tr>' for t in j['tasks'])
    ev = '<ul class="rec">' + ''.join(f'<li><time>{esc(d)}</time> {esc(w)} <small>({a(u, l)})</small></li>' for d, w, u, l in j['jobs_evidence']) + '</ul>'
    b = j['bls']
    body = f"""<article class="pk">{top}
<h1>{esc(j['title'])}</h1><div class="meta">{esc(by)} · Graded, dated evidence, not predictions</div>
<section class="box"><b class="k">The short answer</b><p>{esc(j['verdict'])}</p></section>
<div class="share"><button type="button" data-copy="{esc(j['title'] + ' ' + url)}">Copy link</button></div>
<h2>The job today</h2><div class="stats"><div><b>{esc(b['employment'])}</b><span>people employed in the US</span><small>{a(b['url'], b['label'])}</small></div><div><b>Outlook</b><span>{esc(b['outlook'])}</span><small>{a(b['url'], b['label'])}</small></div></div>
<h2>Task by task: what AI can actually do</h2><p><b>In real use</b> means deployed at scale; <b>shown in tests or pilots</b> means demonstrated but not yet routine; <b>not yet</b> means we found no credible evidence it does this reliably.</p>
<div class="tw"><table><thead><tr><th>Task</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Jobs evidence so far</h2><p>Labelled by who says AI was the reason: the company itself, reporters, or a study.</p>{ev}
<h2>What to do</h2>{steps_html(j['what_to_do'])}
<h2>Questions people ask</h2>{faq_html(j['faq'])}
<h2>How we grade</h2><p>{esc(J['overview']['method'])}</p>
{src_html(j['sources'])}
{capture('One update a month on your job. Only when something actually changes.', 'jobs-' + j['slug'])}
{footer_note(not ok)}</article>"""
    write(f"jobs/{j['slug']}/index.html", url=url, title=j['title'], desc=j['desc'], body=body, draft=not ok, crumbs=[('Can AI do your job?', '/jobs/'), (j['occupation'], '')],
          graph=[webpage(url, j['title'], j['desc'], j.get('updated', TODAY), not ok, j.get('reviewed', '')), article(url, j['title'], j['desc'], j.get('updated', TODAY), not ok, j.get('reviewed', ''), 'Can AI do your job?', [t['url'] for t in j['tasks']] + [u for _, u in j['sources']]),
                 {"@type": "Occupation", "name": j['occupation'], "occupationLocation": {"@type": "Country", "name": "United States"}}, faq_ld(j['faq'])])
    if ok: urls.append(url)
facts = stats_html([[f[0], f[1], f[2], f[3]] for f in J['overview']['facts']])
items = ''.join(f'<li><a href="/jobs/{esc(j["slug"])}/">{esc(j["occupation"])}</a><br><small>{esc(j["verdict"].split(". ")[0])}.</small></li>' for j in J['jobs'])
hub = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Can AI do your job?</h1><p>Not predictions: graded, dated evidence of what AI has actually done in each job, task by task, and what has happened to the jobs themselves. {esc(J['overview']['method'])}</p>{facts}<h2>Pick your job</h2><ul class="grid">{items}</ul>{capture('One update a month on your job. Only when something actually changes.', 'jobs')}{footer_note(not ok)}</article>"""
write('jobs/index.html', url=SITE + 'jobs/', title='Can AI do your job? Graded evidence by occupation', desc='Will AI replace your job? Task-by-task, dated evidence for paralegals, accountants, customer service, developers, translators, writers, designers, radiologists, truck drivers and analysts.', body=hub, draft=not ok, crumbs=[('Can AI do your job?', '')],
      graph=[{"@type": "CollectionPage", "name": "Can AI do your job?", "url": SITE + 'jobs/'}])
register('jobs/', ([SITE + 'jobs/'] if ok else []) + urls)
print(f'jobs/: {len(J["jobs"])} pages ({"approved" if ok else "drafts, noindex"})')

# ======================================================== can-ai/
C = L('research/can_ai.json'); ok, rev = approved('can-ai'); urls = []
STAGES = [('demonstrated', 'Demonstrated', 'shown at least once'), ('reproduced', 'Reproduced', 'independently repeated'), ('accessible', 'Accessible', 'available to ordinary people, or criminals'), ('reliable', 'Reliable', 'works most of the time for a defined task'), ('consequences', 'Consequences', 'real-world use or harm documented')]
for c in C:
    url = SITE + f"can-ai/{c['slug']}/"
    top, by = frame(draft=not ok, rev=c.get('reviewed', ''), updated=c.get('updated', TODAY), crumbs=[('What AI can now do', '/can-ai/'), (c['question'], '')], family_label='can-ai')
    lad = ''.join(f'<tr><td><b>{esc(n)}</b><br><small>{esc(d)}</small></td><td><span class="st {esc(c["ladder"][k]["status"])}">{esc(c["ladder"][k]["status"])}</span></td><td>{esc(fdate(c["ladder"][k].get("date") or "") or "")}</td><td>{esc(c["ladder"][k]["note"])} <small>({a(c["ladder"][k].get("source_url") or "", c["ladder"][k].get("source_label") or "source")})</small></td></tr>' for k, n, d in STAGES if k in c['ladder'])
    fp = c['first_proven']
    rec = '<ul class="rec">' + ''.join(f'<li><time>{esc(w)}</time> {esc(t)}' + (case_ref(r, l) if r else '') + '</li>' for w, r, t, l in c['record']) + '</ul>'
    rel = ''.join(f'<li><a href="{esc(p)}">{esc(TITLES.get(p, p))} →</a></li>' for p in c.get('related', []))
    body = f"""<article class="pk">{top}
<h1>{esc(c['question'])}</h1><div class="meta">{esc(by)} · Graded on a five-step evidence ladder</div>
<span class="verdict">{esc(c['verdict_short'])}</span>
<section class="box"><b class="k">The answer</b><p>{esc(c['verdict'])}</p></section>
<p><b>First shown:</b> {esc(fdate(fp['date']) if len(fp['date']) > 4 else fp['date'])}. {esc(fp['what'])} <small>({a(fp['url'], fp['label'])})</small></p>
<div class="share"><button type="button" data-copy="{esc(c['question'] + ' ' + c['verdict_short'] + '. ' + url)}">Copy link</button></div>
<h2>What it means</h2>{''.join(f'<p>{esc(x)}</p>' for x in c['explain'])}
<h2>The evidence ladder</h2><p>Every capability on this site is graded on the same five steps, from a single demonstration to real-world consequences.</p>
<div class="tw"><table><thead><tr><th>Step</th><th>Status</th><th>When</th><th>Evidence</th></tr></thead><tbody>{lad}</tbody></table></div>
<h2>From the record</h2>{rec}
<h2>What it means for you</h2><p>{esc(c['what_it_means'])}</p>
<h2>What to do</h2>{steps_html(c['what_to_do'])}
<h2>Questions people ask</h2>{faq_html(c['faq'])}
{'<h2>Related</h2><ul>' + rel + '</ul>' if rel else ''}
{src_html(c['sources'])}
{capture('Get an alert when AI crosses a new line', 'can-ai')}
{footer_note(not ok)}</article>"""
    write(f"can-ai/{c['slug']}/index.html", url=url, title=c['title'], desc=c['desc'], body=body, draft=not ok, crumbs=[('What AI can now do', '/can-ai/'), (c['question'], '')],
          graph=[webpage(url, c['title'], c['desc'], c.get('updated', TODAY), not ok, c.get('reviewed', '')), article(url, c['title'], c['desc'], c.get('updated', TODAY), not ok, c.get('reviewed', ''), 'What AI can now do', [u for _, u in c['sources']]),
                 {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": c['question'], "acceptedAnswer": {"@type": "Answer", "text": c['verdict']}}] + [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in c['faq']]}])
    if ok: urls.append(url)
items = ''.join(f'<li><span class="st {esc(c["verdict_short"].lower().replace(" ", "-"))}">{esc(c["verdict_short"])}</span> <a href="/can-ai/{esc(c["slug"])}/">{esc(c["question"])}</a></li>' for c in C)
hub = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>What AI can now do</h1><p>Plain answers to the questions people ask about AI's abilities, each graded on the same five-step ladder (demonstrated, reproduced, accessible, reliable, real consequences) and dated to when it was first shown.</p><ul class="grid">{items}</ul><p>The full record of capability milestones is on <a href="/m/">What AI can now do: every milestone</a>.</p>{capture('Get an alert when AI crosses a new line', 'can-ai')}{footer_note(not ok)}</article>"""
write('can-ai/index.html', url=SITE + 'can-ai/', title='What can AI do now? Graded answers', desc='Can AI clone a voice, fake a video call, get hired under a fake identity, fool a bank, drive a car, deceive its testers? Graded, dated answers.', body=hub, draft=not ok, crumbs=[('What AI can now do', '')],
      graph=[{"@type": "CollectionPage", "name": "What AI can now do", "url": SITE + 'can-ai/'}])
register('can-ai/', ([SITE + 'can-ai/'] if ok else []) + urls)
print(f'can-ai/: {len(C)} pages ({"approved" if ok else "drafts, noindex"})')

# ======================================================== exposed/
V = L('data/victims.json'); ok, rev = approved('exposed'); urls = []
GROUP = {'confirmed': ('Confirmed compromised', 'confirmed'), 'attacked': ('Attacked', 'attacked'), 'disrupted': ('Took services offline as a precaution', 'disrupted'), 'reported': ('Reported, not confirmed', 'reported'), 'other': ('Named in the record', 'other'), 'unnamed': ('Unnamed', 'other')}
ADVICE = {
 'confirmed': [('Watch for official notices.', 'The organisation should tell affected customers or staff what was taken. Read notices on its own website, not links in emails or texts.'), ('Change your password for this service', 'and anywhere you reused it, and turn on two-step login.'), ('Expect scams that mention it.', 'Criminals use breach news as cover: "your account was affected, click here". Go to the organisation directly instead.'), ('If financial or ID details may be involved,', 'consider a credit freeze; IdentityTheft.gov has a step-by-step plan.')],
 'attacked': [('Attacked is not the same as breached.', 'The record shows attempts or attacks against this organisation, not a confirmed loss of data. Watch for an official statement.'), ('Be wary of messages that mention the attack.', 'Scammers use security news as a lure. Contact the organisation through its own website or app.'), ('Use a unique password and two-step login', 'for this service; that limits the damage if a breach is confirmed later.')],
 'disrupted': [('This was a precaution.', 'The organisation switched services off or restricted them while it fixed a flaw. No loss of data is recorded.'), ('Use official channels for service updates.', 'Check the organisation\'s own website or social accounts to see when services return.'), ('Ignore "restore your access" messages.', 'Outages attract scams offering to help. Don\'t click links in unexpected messages.')],
}
ADVICE['reported'] = ADVICE['attacked']; ADVICE['other'] = ADVICE['attacked']; ADVICE['unnamed'] = ADVICE['attacked']
by_org = collections.OrderedDict()
for v in sorted(V, key=lambda v: v.get('date') or ''):
    name = v['organization'].strip()
    if v.get('status_group') == 'unnamed' or 'unnamed' in name.lower(): continue
    by_org.setdefault(name, []).append(v)
slugs, rows_js = {}, []
order = ['confirmed', 'attacked', 'reported', 'disrupted', 'other', 'unnamed']
for name, rows in by_org.items():
    s = slugify(name); base = s; k = 2
    while s in slugs.values(): s = f'{base}-{k}'; k += 1
    slugs[name] = s
    worst = min((r.get('status_group') or 'other' for r in rows), key=lambda g: order.index(g) if g in order else 9)
    incs = sorted({r['incident_id'] for r in rows})
    gate = worst in ('confirmed', 'attacked') or len(incs) >= 2
    url = SITE + f'exposed/{s}/'
    top, by = frame(draft=not (ok and gate), rev='', updated=TODAY, crumbs=[('Am I exposed?', '/exposed/'), (name, '')], family_label='exposed')
    entries = ''
    for r in rows:
        inc = INC.get(r['incident_id']) or {}
        entries += (f'<li><time>{esc(r.get("date_label") or fdate(r.get("date") or ""))}</time> <span class="st {esc(r.get("status_group") or "")}">{esc(r.get("status") or "")}</span> '
                    f'<b>{esc(inc.get("title") or r["incident_id"])}</b>. {esc(r.get("extent") or "")} <small>({a(r.get("source_url") or "", r.get("source_label") or "source")})</small>'
                    + (f' <a href="/i/{esc(r["incident_id"])}/">The incident →</a>' if inc else '') + '</li>')
    sector = rows[0].get('sector') or ''; country = rows[0].get('country') or ''
    glabel = GROUP.get(worst, GROUP['other'])[0]
    title = f'Was {name} hacked by AI? What the record shows'[:90]
    desc = f'{name}{" (" + sector + ", " + country + ")" if sector else ""}: {glabel.lower()} in {len(incs)} AI incident{"s" if len(incs) > 1 else ""} on the Warning Shots record, with dates, sources and what to do if you are a customer or employee.'
    body = f"""<article class="pk">{top}
<h1>{esc(name)}: AI incidents on the record</h1><div class="meta">{esc(by)} · {esc(sector)}{' · ' + esc(country) if country else ''}</div>
<section class="box"><b class="k">The short answer</b><p>{esc(name)} appears in {len(incs)} AI incident{'s' if len(incs) > 1 else ''} on our record. The most serious status recorded: <b>{esc(glabel.lower())}</b>. {'That means a compromise has been confirmed.' if worst == 'confirmed' else 'No confirmed breach is recorded.'}</p></section>
<h2>Every entry, with its source</h2><ul class="rec">{entries}</ul>
<h2>If you're a customer or employee</h2>{steps_html(ADVICE.get(worst, ADVICE['other']))}
<p>Related: <a href="/help/ai-scam-texts/">AI scam texts: what to do</a> · <a href="/checks/fake-bank-fraud-call/">The fake bank call</a></p>
<h2>How to read this</h2><p>"Confirmed" means the organisation or an investigator confirmed a compromise. "Attacked" means attacks or attempts were recorded, including blocked ones. "Took services offline" means a precaution, not a breach. We only list what public sources say; if something here is wrong or out of date, <a href="{esc(REPO)}/issues">tell us</a> and we will correct it.</p>
{capture('Alert me if ' + name + ' appears in a new AI incident', 'exposed-' + s)}
{footer_note(not (ok and gate))}</article>"""
    write(f'exposed/{s}/index.html', url=url, title=title, desc=desc[:300], body=body, draft=not (ok and gate), crumbs=[('Am I exposed?', '/exposed/'), (name, '')],
          graph=[webpage(url, title, desc[:300], TODAY, not (ok and gate), ''), {"@type": "Organization", "name": name}])
    if ok and gate: urls.append(url)
    rows_js.append({'n': name, 's': s, 'g': worst, 'l': glabel, 'k': len(incs), 'sec': sector, 'c': country})
gated = sum(1 for r in rows_js if r['g'] in ('confirmed', 'attacked') or r['k'] >= 2)
lst = ''.join(f'<li data-n="{esc((r["n"] + " " + r["sec"] + " " + r["c"]).lower())}"><a href="/exposed/{esc(r["s"])}/">{esc(r["n"])}</a> <span class="st {esc(r["g"])}">{esc(r["l"])}</span><br><small>{esc(r["sec"])}{" · " + esc(r["c"]) if r["c"] else ""}</small></li>' for r in sorted(rows_js, key=lambda r: (order.index(r['g']) if r['g'] in order else 9, r['n'].lower())))
hub = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Am I exposed?</h1><p class="aka">What AI means for you, your family, your money, your job and your vote, and what to do about it.</p>
<p>Start with your situation. Each one has the first thing to do, then the pages that help.</p>
<ul class="grid sit">
<li><b>Something is happening right now</b><br><span class="act">Hang up and call back on a number you already have. Don't pay anyone while you're still on the call.</span><br><a href="/help/voice-clone-scam-call/">A loved one calls in a panic</a> · <a href="/help/ai-scam-texts/">A text that seems off</a> · <a href="/help/is-this-video-real/">Is this video real?</a> · <a href="/checks/">Is this a scam?</a></li>
<li><b>Your kids</b><br><span class="act">Ask which AI they talk to. Not as a test; just ask.</span><br><a href="/learn/ai-companions-parents-guide/">AI companions: a parent's guide</a> · <a href="/help/ai-fake-nude-image-what-to-do/">A fake nude of your child</a> · <a href="/checks/ai-sextortion-scam/">Sextortion</a></li>
<li><b>Your money</b><br><span class="act">Agree a family safe word. It takes two minutes.</span><br><a href="/shield/">Make your safe-word card</a> · <a href="/checks/fake-bank-fraud-call/">The fake bank call</a> · <a href="/checks/deepfake-celebrity-investment-scam/">Celebrity investment videos</a> · <a href="/checks/ai-trading-bot-scam/">AI trading bots</a></li>
<li><b>Your parents</b><br><span class="act">Set up their AI helper with them, and put the three rules by the phone.</span><br><a href="/learn/ai-helper-for-older-parent/">An AI helper for Mom, safely</a> · <a href="/checks/government-impersonator-scam/">Government impersonators</a></li>
<li><b>Your job</b><br><span class="act">Find your job and see what AI has actually done in it, task by task.</span><br><a href="/jobs/">Can AI do your job?</a> · <a href="/jobs/layoffs/">Layoffs tied to AI</a> · <a href="/checks/task-job-scam/">Fake job offers</a></li>
<li><b>Your website or business</b><br><span class="act">Ask your host which PHP version your site runs; anything before Oct 21 needs updating.</span><br><a href="/php2shell/">The live tracker</a> · <a href="/checks/boss-gift-card-wire-transfer-scam/">The boss asking for gift cards</a> · <a href="/scraped/">Keep AI crawlers out</a></li>
<li><b>Your vote</b><br><span class="act">Get where and when to vote only from your election office or vote.gov.</span><br><a href="/midterms-2026/">AI fakes in the midterms</a> · <a href="/help/is-this-video-real/">Check a clip before you share</a></li>
</ul>
<h2>Is your organisation on the record?</h2>
<p>Type your company, school, bank or employer. If it appears in an AI incident on our record, you will see what happened, how sure we are, the source, and what to do.</p>
<input class="search" id="ex-q" type="search" placeholder="Search {len(rows_js)} organisations, sectors or countries" aria-label="Search organisations">
<p id="ex-none" hidden><b>Not on our record.</b> That's good news, not a guarantee: we only list organisations named in public reporting about AI incidents.</p>
<ul class="grid" id="ex-list">{lst}</ul>
<script>(function(){{var q=document.getElementById('ex-q'),li=[].slice.call(document.querySelectorAll('#ex-list li')),no=document.getElementById('ex-none');q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase(),n=0;li.forEach(function(x){{var m=!v||x.dataset.n.indexOf(v)>-1;x.hidden=!m;if(m)n++;}});no.hidden=n>0;}});}})();</script>
{capture('Alert me if my organisation appears in an AI incident', 'exposed')}
{footer_note(not ok)}</article>"""
write('exposed/index.html', url=SITE + 'exposed/', title='Am I exposed? What AI means for you, and what to do', desc=f'Start from your situation (a scam call now, your kids, your money, your parents, your job, your website, your vote) or search {len(rows_js)} organisations named in AI incidents, each sourced, with what to do.', body=hub, draft=not ok, crumbs=[('Am I exposed?', '')],
      graph=[{"@type": "CollectionPage", "name": "Am I exposed?", "url": SITE + 'exposed/'}])
register('exposed/', ([SITE + 'exposed/'] if ok else []) + urls)
print(f'exposed/: {len(rows_js)} organisations, {gated} pass the quality gate ({"approved" if ok else "drafts, noindex"})')

# ======================================================== midterms-2026/
MF = L('research/midterm_fakes.json'); MC = L('research/midterm_context.json'); ok, rev = approved('midterms'); url = SITE + 'midterms-2026/'
top, by = frame(draft=not ok, rev='', updated=TODAY, crumbs=[('2026 midterms: AI fakes', '')], family_label='midterms')
SCL = {'confirmed fake': 'confirmed', 'removed': 'confirmed', 'labelled AI by poster': 'partly', 'alleged fake': 'other'}
fk = ''.join(f'<li><time>{esc(fdate(m["date"]))}</time> <span class="st {SCL.get(m["status"], "other")}">{esc(m["status"])}</span> <b>{esc(m["race"])}</b>. {esc(m["what"])}'
             + (f' <i>Made or posted by:</i> {esc(m["who_made_it"])}.' if m.get('who_made_it') else '') + (f' <i>How it was caught:</i> {esc(m["how_caught"])}.' if m.get('how_caught') else '')
             + f' <small>({a(m["source_url"], m["source_label"])})</small>' + (f' <a href="/i/{esc(m["index_id"])}/">The case file →</a>' if m.get('index_id') in INC else '') + '</li>'
             for m in sorted(MF, key=lambda m: m['date'], reverse=True))
facts = stats_html(MC['facts'][:6])
laws = '<dl>' + ''.join(f'<div><dt>{esc(w)}</dt><dd>{esc(e)} <small>({a(u, l)})</small></dd></div>' for w, e, u, l in MC['laws']) + '</dl>'
steps = '<ol class="steps">' + ''.join(f'<li><b>{esc(t)}</b>{esc(d)}' + (f' <small>({a(u, "source")})</small>' if u else '') + '</li>' for t, d, u in MC['check_steps']) + '</ol>'
vote = '<ul>' + ''.join(f'<li><b>{esc(w)}</b> {esc(e)} <small>({a(u, l)})</small></li>' for w, e, u, l in MC['voting_facts']) + '</ul>'
n_conf = sum(1 for m in MF if m['status'] in ('confirmed fake', 'removed'))
body = f"""<article class="pk">{top}
<h1>AI fakes in the 2026 midterms: the tracker</h1><div class="meta">{esc(by)} · Election Day is Tuesday, Nov 3 · Every entry sourced</div>
<section class="box"><b class="k">The short answer</b><p>{len(MF)} AI-made election fakes and AI ads are on our record this cycle, {n_conf} of them confirmed fake or taken down. Before you share a shocking clip of a candidate this week, run the checks below. For where and when to vote, use your state election office or vote.gov, not a video, text or call.</p></section>
<div class="share"><button type="button" data-copy="{esc('AI fakes in the 2026 midterms, tracked and sourced: ' + url)}">Copy link</button></div>
<section class="box" style="border-left-color:var(--ink)"><b class="k">Our promise</b><p>On Nov 4: which fakes mattered, and what this index got wrong. <a href="/midterms-2026/after/">The post-mortem will be here →</a></p></section>
<h2>Before you share: how to check a clip</h2>{steps}
<h2>The fakes so far</h2><p>Newest first. <b>Confirmed fake</b>: a fact-checker, platform, official or the poster confirmed AI. <b>Labelled AI by poster</b>: an ad that says it used AI. <b>Alleged</b>: claimed, not confirmed.</p><ul class="rec">{fk}</ul>
<h2>The numbers</h2>{facts}
<h2>The rules</h2>{laws}
<h2>Voting: the only sources to trust</h2>{vote}
<h2>Questions people ask</h2>{faq_html([
 ['How can I tell if a political video is a deepfake?', 'Don’t rely on spotting glitches. Check where it first appeared, whether a major outlet or the campaign has confirmed it, and whether fact-checkers have rated it. A brand-new or anonymous account posting an explosive clip is a warning sign.'],
 ['Are AI political ads legal?', 'In most states, yes, with conditions. Many states now require AI-generated political ads to carry a disclosure, and a few ban certain deceptive deepfakes close to an election. There is no federal law covering AI in campaign ads; AI-voiced robocalls are covered by federal robocall rules.'],
 ['What do I do if I see an election deepfake?', 'Don’t share it. Report it on the platform where you saw it, and if it gives false voting information, report it to your state or local election office.'],
 ['Where can I check where and when to vote?', 'Your state or local election office, or vote.gov. Treat any call, text or video that changes your polling place or date with suspicion and check it with your election office.']])}
<p>Related: <a href="/help/is-this-video-real/">Is this video real? How to check before you share</a></p>
{src_html([[m['source_label'], m['source_url']] for m in MF] + [[f[3], f[2]] for f in MC['facts']])}
{capture('Get an alert when a new election fake is confirmed', 'midterms')}
{footer_note(not ok)}</article>"""
title = 'AI deepfakes in the 2026 midterms: tracker'
desc = f'Every AI-made fake and AI ad in the 2026 US midterms on our record: {len(MF)} entries, sourced and labelled confirmed, labelled or alleged, plus how to check a clip before you share.'
write('midterms-2026/index.html', url=url, title=title, desc=desc, body=body, draft=not ok, crumbs=[('2026 midterms: AI fakes', '')],
      graph=[webpage(url, title, desc, TODAY, not ok, ''), article(url, title, desc, TODAY, not ok, '', 'Elections', [m['source_url'] for m in MF])])
register('midterms-2026/', [url] if ok else [])
print(f'midterms-2026/: {len(MF)} fakes ({"approved" if ok else "draft, noindex"})')

# ---------- the promised post-mortem: a permanent URL now, written on Nov 4 (research/midterms_after.json), hidden until then
try:
    AFTER = json.load(open('research/midterms_after.json', encoding='utf-8'))
except (OSError, ValueError):
    AFTER = {}
au = SITE + 'midterms-2026/after/'
if AFTER.get('body_html'):
    abody = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/midterms-2026/">2026 midterms: AI fakes</a> · After the vote</nav><h1>{esc(AFTER.get('h1', 'After the midterms: which AI fakes mattered, and what we got wrong'))}</h1><div class="meta">Published {esc(fdate(AFTER.get('published', TODAY)))}</div>{AFTER['body_html']}{footer_note(False)}</article>"""
    adraft = False
else:
    abody = """<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/midterms-2026/">2026 midterms: AI fakes</a> · After the vote</nav><h1>After the midterms: which AI fakes mattered, and what we got wrong</h1>
<section class="box"><b class="k">Coming Nov 4</b><p>The day after the election, this page will grade the cycle: which AI fakes reached people, which were caught and by whom, which claims fell apart, and every place this index was wrong. Until then, <a href="/midterms-2026/">the tracker</a> is updated on every refresh.</p></section></article>"""
    adraft = True
write('midterms-2026/after/index.html', url=au, title='After the 2026 midterms: which AI fakes mattered', desc='The post-election grading of AI fakes in the 2026 US midterms: what reached people, what was caught, and what Warning Shots got wrong. Published Nov 4.', body=abody, draft=adraft,
      crumbs=[('2026 midterms: AI fakes', '/midterms-2026/'), ('After the vote', '')], graph=[{"@type": "WebPage", "name": "After the 2026 midterms", "url": au}])
if not adraft: register('midterms-2026/after/', [au])

# ======================================================== breakthroughs/: what AI just made possible, as human payoffs (research/breakthroughs.json)
try:
    BTS = sorted(L('research/breakthroughs.json'), key=lambda b: b.get('date', ''), reverse=True)
except (OSError, ValueError):
    BTS = []
_NW = {n['id']: n for n in (L('research/news_archive.json') if os.path.exists('research/news_archive.json') else []) + L('research/news.json')}
BTL = {'in-use': 'In use now', 'published': 'Peer-reviewed', 'reproduced': 'Reproduced', 'claimed': 'Claimed, not yet checked'}
bu = SITE + 'breakthroughs/'
def _bt(b):
    n = _NW.get(b.get('news_id'), {}); url = b.get('url') or n.get('url', ''); outlet = b.get('outlet') or n.get('outlet', '')
    tr = f'<p><a href="{esc(b["try"][1])}"><b>Try it:</b> {esc(b["try"][0])} →</a></p>' if b.get('try') else ''
    return (f'<li>{(f"<span class=\"st yes\">{esc(BTL.get(b['proof'], b['proof']))}</span> ") if b["proof"] != "claimed" else ""}<span class="meta">{esc(b.get("area", ""))} · {esc(fdate(b["date"]))}</span>'
            f'<h2 style="border:0;margin:6px 0 4px;padding:0;font-size:1.3rem"><a href="{esc(url)}" title="{esc(outlet)}">{esc(b["payoff"])}</a></h2><p>{esc(b["means"])}</p>{tr}</li>')
btbody = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Breakthroughs: what AI just made possible</h1>
<p>The other half of the story. Real advances in medicine, science, weather, the planet and the software we all depend on, written as what they mean for you, with a way to try them when you can. Each carries the same proof label as our warnings: in use now, peer-reviewed, reproduced, or claimed and not yet checked.</p>
<ul class="list">{''.join(_bt(b) for b in BTS)}</ul>
{capture('Send me the next breakthrough', 'breakthroughs')}
{footer_note(False)}</article>"""
write('breakthroughs/index.html', url=bu, title='AI breakthroughs: what AI just made possible, in plain words', desc=f'{len(BTS)} recent AI advances in medicine, science, weather and software, written as what they mean for you, each labelled in use, peer-reviewed or claimed.', body=btbody, draft=False,
      crumbs=[('Breakthroughs', '')], graph=[webpage(bu, 'AI breakthroughs', 'Recent AI advances in plain words', TODAY, False, '')])
register('breakthroughs/', [bu] if BTS else [])
print(f'breakthroughs/: {len(BTS)}')

# ======================================================== up-and-down/: who gained or lost power in AI (research/updown.json)
try:
    UDR = sorted(L('research/updown.json'), key=lambda b: b.get('date', ''), reverse=True)
except (OSError, ValueError):
    UDR = []
uu = SITE + 'up-and-down/'
def _ud(b):
    n = _NW.get(b.get('news_id'), {}); up = b['dir'] == 'up'
    return (f'<li><span class="st{" yes" if up else ""}" style="{"" if up else "background:var(--alarm);color:#fff;border-color:var(--alarm)"}">{"▲ Up" if up else "▼ Down"}</span> <span class="meta">{esc(fdate(b["date"]))}</span>'
            f'<p style="margin:6px 0 4px;font-size:1.1rem"><b style="text-transform:uppercase;font-stretch:82%;font-weight:900">{a(n.get("url", ""), b["name"])}</b> {esc(b["line"])} <small>{esc(n.get("outlet", ""))}</small></p>'
            f'<p style="border-left:3px solid var(--ink);padding:6px 10px;background:var(--panel)"><b>Why it matters:</b> {esc(b["why"])}</p></li>')
ubody = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Up &amp; Down: who gained power in AI, who lost it</h1>
<p>The people, companies and countries whose fortunes moved, newest first. Each name links to the reporting; the arrow and <b>Why it matters</b> are our read.</p>
<ul class="list">{''.join(_ud(b) for b in UDR)}</ul>
{capture('Send me the Up &amp; Down board each week', 'up-and-down')}
{footer_note(False)}</article>"""
write('up-and-down/index.html', url=uu, title='Up & Down: who gained power in AI, who lost it, and why it matters', desc=f'{len(UDR)} moves in AI power: the companies, people and countries whose fortunes rose or fell, each sourced, each with why it matters.', body=ubody, draft=not UDR,
      crumbs=[('Up & Down', '')], graph=[webpage(uu, 'Up & Down', 'Who gained or lost power in AI', TODAY, False, '')])
register('up-and-down/', [uu] if UDR else [])
os.makedirs('ai-inc', exist_ok=True)
open('ai-inc/index.html', 'w').write('<!doctype html><meta charset="utf-8"><title>Up &amp; Down</title><meta name="description" content="AI Inc. is now Up &amp; Down: who gained power in AI, who lost it, and why it matters."><meta property="og:image" content="' + SITE + 'assets/og.png"><meta name="robots" content="noindex"><link rel="canonical" href="' + uu + '"><meta http-equiv="refresh" content="0; url=/up-and-down/"><p><a href="/up-and-down/">Up &amp; Down</a></p>')
print(f'up-and-down/: {len(UDR)}')

import entities as _E
_EIDX, _EPAGES, _N2I, _EA = _E.index()
def _fc_links(c):
    ws = [w for w in _E.who(_E.text_of('call', c)) if _EPAGES.get(w)]
    ri = (c.get('related') or {}).get('incident_id') if isinstance(c.get('related'), dict) else None
    bits = []
    if ri and ri in INC: bits.append(f'<b>The incident:</b> <a href="/i/{esc(ri)}/">{esc(INC[ri]["title"])}</a>')
    if ws: bits.append('<b>Who is involved:</b> ' + ' · '.join(f'<a href="/who/{w}/">{esc(_E.NAME[w])}</a>' for w in ws))
    return ('<p class="meta">' + ' · '.join(bits) + '</p>') if bits else ''
# ======================================================== forecast/<id>/: one permanent page per call and question
CALLS = L('data/calls.json'); fu = []
def likely(o):
    o = float(o)
    return 'a toss-up' if abs(o - 0.5) < 1e-9 else 'very likely' if o >= .85 else 'likely' if o >= .6 else 'unlikely' if o <= .4 and o > .15 else 'very unlikely' if o <= .15 else 'leaning yes' if o > .5 else 'leaning no'
for c in CALLS:
    url = SITE + f"forecast/{c['id']}/"
    q = c.get('plain') or c['question']; kind = 'Call' if c.get('kind') == 'call' else 'Question'
    r = c.get('resolution')
    if r:
        toss = abs(float(c['odds']) - .5) < 1e-9
        hit = (r['outcome'] == 'yes') == (float(c['odds']) > .5)
        grade = 'Called it a toss-up: not counted' if toss else ('Called it' if hit else 'Missed')
        res = f"<section class=\"box\"><b class=\"k\">Graded {esc(fdate(r['date']))}</b><p>Answer: <b>{esc(r['outcome'])}</b>. The index said {esc(likely(c['odds']))} ({esc(c['odds_label'])}). <b>{esc(grade)}.</b></p><p class=\"meta\">{esc(r.get('note', ''))} " + (a(r.get('url') or r.get('source_url') or '', 'Source') if (r.get('url') or r.get('source_url')) else '') + "</p></section>"
    else:
        res = f"<section class=\"box\" style=\"border-left-color:var(--ink)\"><b class=\"k\">Open · resolves {esc(fdate(c['resolve_by']))}</b><p>The index says: <b>{esc(likely(c['odds']))}</b> ({esc(c['odds_label'])}). Graded on that date, right or wrong, in public.</p></section>"
    body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb"><a href="/forecast/">Forecasts</a> · {kind}</nav>
<h1>{esc(q)}</h1><div class="meta">{kind} opened {esc(fdate(c['opened']))} · {'days to weeks' if kind == 'Call' else 'months to years'} · the question's wording never changes after it is published</div>
{res}
<div class="share"><a class="button" href="https://x.com/intent/post?{esc(urllib.parse.urlencode({'text': (q + ' Graded: ' + r['outcome'] + '. Warning Shots had said ' + likely(c['odds']).lower() + '.') if r else ('Warning Shots says ' + likely(c['odds']).lower() + ': ' + q + ' Graded ' + fdate(c['resolve_by']) + ', right or wrong.'), 'url': url}))}" target="_blank" rel="noopener">Post on X</a><button type="button" class="alt" data-copy="{esc(q + ' ' + url)}">Copy link</button>{(f'<a class="button alt" href="/assets/forecast/{esc(c["id"])}.png" download>Download the card</a>') if os.path.exists(f"assets/forecast/{c['id']}.png") else ''}</div>
{_fc_links(c)}<h2>Why the index thinks so</h2><p>{esc(c.get('basis') or '')}</p>
{('<h2>What would move it</h2><p>' + esc(c['signposts']) + '</p>') if c.get('signposts') else ''}
<p class="meta">The exact question: {esc(c['question'])}</p>
<p><a href="/forecast/">Every forecast and the track record →</a></p>
{capture('Email me when this is graded', 'forecast-' + c['id'])}
</article>"""
    img = SITE + f"assets/forecast/{c['id']}.png" if os.path.exists(f"assets/forecast/{c['id']}.png") else None
    write(f"forecast/{c['id']}/index.html", url=url, title=q[:90], desc=(f"Graded: {r['outcome']}. " if r else f"Open until {fdate(c['resolve_by'])}. ") + f"Warning Shots said {likely(c['odds'])} ({c['odds_label']}). " + (c.get('basis') or '')[:150], body=body, draft=False, img=img,
          crumbs=[('Forecasts', '/forecast/'), (kind, '')], graph=[{"@type": "Question", "name": q, "dateCreated": c['opened'], "url": url}])
    fu.append(url)
json.dump([{'slug': c['id'], 'kicker': ('Graded ' + c['resolution']['date'] + ' · answer: ' + c['resolution']['outcome']) if c.get('resolution') else ('Forecast · resolves ' + c['resolve_by']), 'h1': c.get('plain') or c['question']} for c in CALLS], open('data/forecast_cards.json', 'w'))
print(f'forecast/: {len(fu)} pages')

# ---------- forecast/: the hub (scoreboard, what resolves next, every open call and question, every graded one)
def _grade(c):
    r = c['resolution']; toss = abs(float(c['odds']) - .5) < 1e-9
    return 'toss' if toss else ('hit' if (r['outcome'] == 'yes') == (float(c['odds']) > .5) else 'miss')
graded = [c for c in CALLS if c.get('resolution') and c['resolution'].get('outcome') in ('yes', 'no')]
G = collections.Counter(_grade(c) for c in graded)
openc = sorted([c for c in CALLS if not c.get('resolution')], key=lambda c: c['resolve_by'])
def _row(c):
    q = c.get('plain') or c['question']
    if c.get('resolution'):
        g = _grade(c) if c in graded else 'void'
        tag = {'hit': 'Called it', 'miss': 'Missed', 'toss': 'Toss-up: not counted', 'void': 'Void'}[g]
        side = f"Graded {fdate(c['resolution']['date'])} · answer: {c['resolution']['outcome']} · <b>{tag}</b>"
    else:
        side = f"Resolves {fdate(c['resolve_by'])} · the index says <b>{likely(c['odds'])}</b> ({esc(c['odds_label'])})"
    return f'<li><a href="/forecast/{c["id"]}/">{esc(q)}</a><span class="meta">{side}</span></li>'
calls_open = [c for c in openc if c.get('kind') == 'call']; qs_open = [c for c in openc if c.get('kind') != 'call']
hu = SITE + 'forecast/'
fbody = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>The forecasts: what happens next, and whether we were right</h1>
<p>Every call is a dated yes-or-no question with the index's odds, published before the answer is known and graded in public on the day it resolves. Misses stay on the board. The wording never changes after a question goes up.</p>
<section class="box"><b class="k">Track record</b><p><b>{G['hit']} right, {G['miss']} wrong</b>{f", {G['toss']} called a toss-up (not counted)" if G['toss'] else ''}. {len(openc)} still open; the next resolves {fdate(openc[0]['resolve_by']) if openc else 'soon'}.</p></section>
<h2>Calls: resolving in days and weeks</h2><ul class="list">{''.join(_row(c) for c in calls_open)}</ul>
<h2>Questions: months to years</h2><ul class="list">{''.join(_row(c) for c in qs_open)}</ul>
<h2>Graded</h2><ul class="list">{''.join(_row(c) for c in sorted([c for c in CALLS if c.get('resolution')], key=lambda c: c['resolution']['date'], reverse=True)) or '<li>None yet.</li>'}</ul>
<p class="meta">How the odds move and why: <a href="/index/#changelog">the changelog</a>. The full method: <a href="/index/#about">how the index works</a>.</p>
{capture('Email me when a forecast is graded', 'forecast')}
</article>"""
write('forecast/index.html', url=hu, title='AI forecasts: what happens next, graded in public', desc=f"Warning Shots' dated AI forecasts: {len(openc)} open, {G['hit']} right, {G['miss']} wrong. Every call is graded in public on the day it resolves.", body=fbody, draft=False,
      crumbs=[('Forecasts', '')], graph=[webpage(hu, 'AI forecasts', 'Dated AI forecasts, graded in public', TODAY, False, '')])
register('forecast/', [hu] + fu)

# ---------- fixes/: did they fix it? one line per major case, with where the fix stands
FX = L('data/fixes.json')
FXST = {'ongoing': 'Still unfolding', 'reopened': 'Happened again after a fix', 'disputed': 'Disputed', 'unverified': 'Fix claimed, not verified', 'unresolved': 'No fix claimed', 'fixed': 'Fixed and verified'}
def _cur(f): return next((c for c in f['chain'] if c['stage'] == 'current'), f['chain'][-1])
fopen = [f for f in FX if _cur(f)['status'] != 'fixed']
order = {'reopened': 0, 'unresolved': 1, 'disputed': 2, 'unverified': 3, 'ongoing': 4, 'fixed': 9}
xu = SITE + 'fixes/'
items = ''.join(f'<li><a href="/c/{f["incident_id"]}/">{esc(f["name"])}</a><span class="meta"><b>{esc(FXST.get(_cur(f)["status"], _cur(f)["status"]))}.</b> {esc(f.get("one_liner") or "")}</span></li>' for f in sorted(FX, key=lambda f: order.get(_cur(f)['status'], 5)))
xbody = f"""<article class="pk"><div class="kick">Warning Shots</div><h1>Did they fix it?</h1>
<p>When an AI company, a government or a victim says a problem is fixed, we follow it: who reported it, how they responded, what fix was claimed, and whether anyone independent has checked it since. Most fixes are claimed. Few are verified.</p>
<section class="box"><b class="k">Right now</b><p><b>{len(fopen)} of {len(FX)}</b> major cases have no independently verified fix. {sum(1 for f in FX if _cur(f)['status'] == 'reopened')} happened again after a fix was announced.</p></section>
<ul class="list">{items}</ul>
<p class="meta">Each case page shows the full chain with sources. The same tracker, with every stage, is on <a href="/index/#fixes">the Record</a>.</p>
{capture('Alert me when a fix is broken or verified', 'fixes')}
</article>"""
write('fixes/index.html', url=xu, title=f'Did they fix it? {len(fopen)} of {len(FX)} AI cases still open', desc=f'The fix tracker for major AI incidents: {len(fopen)} of {len(FX)} have no independently verified fix. Who claimed what, and what happened next.', body=xbody, draft=False,
      crumbs=[('Did they fix it?', '')], graph=[webpage(xu, 'Did they fix it?', 'Fix tracker for major AI incidents', TODAY, False, '')])
register('fixes/', [xu])
print(f'forecast/ hub: {len(openc)} open, {G["hit"]}-{G["miss"]}; fixes/: {len(fopen)} of {len(FX)} open')
