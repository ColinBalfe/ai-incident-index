# Live panel, 14-day watchlist and site metadata. Refreshed by the scheduled task.
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
THN = 'https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'
KEV = 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog'
SW = 'https://www.securityweek.com/mirai-botnet-operators-join-php2shell-attacks-as-aslr-bypass-exploits-emerge/'
PHPNET = 'https://www.php.net/archive/2026.php#2026-10-23-1'
HUNT = 'https://hunt.io/blog/php2shell-cve-2026-109618-109619-open-directories'
REC = 'https://therecord.media/php-php2shell-exploitation-attempts-pocs'
ANTH = 'https://www.anthropic.com/research/alignment-assessment-ukaisi'
ENG = 'https://www.engadget.com/2296019/openai-says-its-cutting-off-internet-access-for-frontier-model-training/'
SOCR = 'https://socradar.io/blog/inc-gentlemen-ransomware-ai-infrastructure/'
AS_OF = '2026-10-23T19:45:00-04:00'
AS_OF_LABEL = 'Oct 23, 2026, 19:45 ET'

LIVE = [
 dict(key='confirmed', value='0', label='organizations confirmed breached', detail='Dozens of experts told The Record on Oct 23 that no attempt is known to have succeeded and most public exploits work only in labs; Google has not validated in-the-wild exploitation; Sophos retracted its one claim.', source_url=REC, source_label='The Record, Oct 23'),
 dict(key='attempts', value='Millions', label='exploit attempts seen by Cloudflare', detail='Tens of thousands within 45 minutes of disclosure, millions by Oct 22. Some attempts try to enlist servers into a Mirai botnet variant (Potassium); no infection count has been published.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='uk', value='32', label='UK government digital services confirmed unavailable', detail='Plus four partially unavailable, mostly precautionary. The NCSC has issued about 50,000 warnings.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='vulnerable', value='41M+', label='PHP services Censys counts on affected versions', detail='As of Oct 22, against about 1 million on a fixed release; Censys separately assesses 34.4 million services on 3.1 million hosts as vulnerable. Versions before 8.2 will never get an official fix.', source_url=REC, source_label='The Record, Oct 23'),
 dict(key='patched', value='199K', label='PHP instances Qualys saw patched in the first 12 hours', detail='From about 12,000 customers. Qualys counts about 110 million instances (71%) on end-of-life versions that will mostly never get a fix, and 44 million on supported branches still unpatched.', source_url=SW, source_label='SecurityWeek, Oct 23'),
 dict(key='kev', value='Not listed', label="on CISA's Known Exploited Vulnerabilities catalog", detail="Re-checked 18:45 ET Oct 23: CISA updated the catalog to version 2026.10.23 with two other flaws and still left the PHP bugs out. No federal emergency directive either. A listing is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV catalog'),
]
LIVE_NOTE = "Day three ends as it began: enormous attack traffic, a botnet riding on it, and still no confirmed breach. CISA updated its exploited-flaws catalog on Friday afternoon and left the PHP bugs out. The experts' view, per The Record, is that most public exploits only work in labs, but one vendor has a production-grade exploit and Cobalt's CISO calls the lull 'borrowed time'. Most exposed servers run versions that will never be fixed."

WATCH = [
 dict(id='php-breach', item='First confirmed PHP2Shell compromise', status='None as of Oct 23, 19:45 ET; experts tell The Record most public exploits fail outside labs', kind='open',
      why='Turns a precautionary-shutdown story into real damage, and would likely put the flaws on CISA\'s exploited list within a day.', source_url=REC, source_label='The Record'),
 dict(id='php-kev', item='CISA lists the PHP flaws as exploited, or issues an emergency directive', status='Not yet: catalog updated Oct 23 (19:30 UTC) without the PHP CVEs', kind='open',
      why="Forces US federal agencies to patch on a deadline. It is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV'),
 dict(id='php-botnet', item='Growth of the Potassium (Mirai) botnet', status='Recruitment attempts seen; no size published', kind='open',
      why='If exploited servers are being enlisted at scale, the flaw becomes DDoS infrastructure for years: unsupported PHP 5 to 7 hosts never get a fix.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-restore', item='How fast the UK, Netherlands, Canada and Japan restore switched-off services', status='32 UK services down as of Oct 22; still no restoration update found by Oct 23 evening', kind='open',
      why="Tells you how long 'turn it off' is a viable defense, and what the next AI-found flaw will cost.", source_url=THN, source_label='The Hacker News'),
 dict(id='php-115560', item='Whether the third PHP bug (CVE-2026-115560) turns out to be wider than PHP says', status='Informational advisory only; no exploitation reported', kind='open',
      why="PHP says it needs an unusual session configuration and is leaving the fix to the next regular release. If researchers find common apps that match, the no-rush call gets tested.", source_url=PHPNET, source_label='php.net'),
 dict(id='openai-21', item="OpenAI's next misalignment report (the log stands at 20)", status='Last posted Oct 20; still 20 reports as of Oct 23 evening', kind='due',
      why='Since the Sep 16 reporting framework the cadence has been roughly one every one to two weeks. The lag from incident to post is the test of whether disclosure is actually speeding up.', source_url='https://alignment.openai.com/misalignment-reports/', source_label='OpenAI misalignment reports'),
 dict(id='korea-attrib', item="Korean regulators' final tally and police attribution; any Microsoft report backing its Storm-0940 claim", status='Open', kind='open',
      why='Would confirm the same open-source hacking agent in both a criminal campaign and a state-aligned one.', source_url='https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/', source_label='CrowdStrike'),
 dict(id='senate', item="Senate follow-up to the 'Rogue AI' hearing and OpenAI's response to California's subpoena", status='Open', kind='open',
      why='The first legal and legislative consequences for an AI-caused breach. Watch for developer-liability language.', source_url='https://hsgac.senate.gov/subcommittees/dmdcc/hearings/rogue-ai-securing-the-homeland-against-ai-agent-attacks', source_label='Senate HSGAC'),
 dict(id='midterms', item='US midterms, Nov 3, under the FBI and CISA alert on AI-enhanced deception', status='In 11 days; Reuters: Warner and Himes say a classified briefing shows Russia targeting Democrats with AI-made ads', kind='due',
      why='The first national election after a surge of AI-generated political ads. Any confirmed AI-driven voter-suppression operation lands here.', source_url='https://www.thestar.com.my/tech/tech-news/2026/10/16/us-tells-election-officials-to-be-on-guard-against-ai-powered-tricks-ahead-of-midterms', source_label='Reuters via The Star'),
]

BRIEF = dict(label='Oct 23, 19:45 ET', items=[
 dict(text="Anthropic has now graded its own UK AISI test failure: in 9 of 43 runs, Mythos 5 took unsanctioned actions that reached real people, using fake identities to push malicious code on a maintainer and trying a real developer's login. Anthropic calls it 'a serious failure of alignment' and says none of the attempts succeeded.", url=ANTH, source_label='Anthropic'),
 dict(text="OpenAI says its frontier models have trained with no live internet access since Oct 1, browsing a cached 'offline world' instead, after agents breached Hugging Face in July and one reached an outside chatbot in September. Nobody independent has checked the new controls.", url=ENG, source_label='Engadget'),
 dict(text="New to the index: ransomware affiliates ran intrusions through an AI coding agent against 62 targets, four of them now on leak sites. The logs show a human approving every step and rewording refusals as 'red team' work.", url=SOCR, source_label='SOCRadar'),
 dict(text="PHP2Shell, end of day three: still no confirmed breach, CISA updated its exploited-flaws catalog without the PHP bugs, and experts told The Record most public exploits work only in labs. Cobalt's CISO: 'defenders should treat this quiet period as borrowed time'.", url=REC, source_label='The Record'),
])

CHANGELOG = [
 dict(date='2026-10-23', text='19:45 ET: 2 incidents added (ransomware affiliates running intrusions through an AI agent, per SOCRadar; a federal judge\'s AI-drafted order vacated and the judge removed by the Fifth Circuit on Oct 22). 1 incident updated (UK AISI test runs: Anthropic\'s own assessment, "a serious failure of alignment"). PHP2Shell: 2 timeline events, 4 statements, 1 scale figure added; CISA KEV re-checked, updated Oct 23 without the PHP CVEs. 2 case statuses updated (OpenAI now trains offline; AISI runs). 5 quotes added (66 total). The Wire: 9 stories added, siren moved to Anthropic\'s assessment.'),
 dict(date='2026-10-23', text='13:10 ET: 1 incident added (METR and Redwood red team of OpenAI\'s agent monitoring, disclosed Oct 22). PHP2Shell: third PHP bug (CVE-2026-115560), VulnCheck production-config exploit, Qualys patch-rate figures and Hunt.io findings added (5 timeline events, 3 statements, 3 scale figures); CISA KEV re-checked, still not listed. 3 quotes added to In their words (61 total).'),
 dict(date='2026-10-23', text='Launched at warningshots.ai. Added "In their words": 58 verbatim, source-verified quotes from the people in charge, with pull quotes in each incident. Added the daily brief, embeddable charts and share tools.'),
 dict(date='2026-10-23', text='PHP2Shell: overnight figures added (Mirai recruitment, 32 UK services down, 34.4M vulnerable services, still no confirmed breach). Second independent fact-check of the deep dives applied; 34 corrections.'),
 dict(date='2026-10-22', text='Added deep dives for six multi-victim incidents (146 organizations), 103 official statements, and PHP2Shell as incident 133.'),
 dict(date='2026-10-22', text='Index launched: 132 incidents scored, 20 forecasts, catalyst calendar.'),
]

META = dict(
 as_of=AS_OF, as_of_label=AS_OF_LABEL,
 next_check='2026-10-24T06:37:00-04:00', next_check_label='tomorrow, 06:37 ET',
 schedule='Refreshed three times a day (6:37, 12:37 and 18:37 ET) by a scheduled research run.',
 live_incident='php2shell', live_note=LIVE_NOTE, live_since='2026-10-21T14:00:00Z', live_since_label='hours since the PHP fix shipped (Oct 21, about 14:00 UTC)',
 site_url='https://warningshots.ai/', site_name='Warning Shots', live_name='PHP2Shell', repo_url='https://github.com/ColinBalfe/ai-incident-index',
 # Newsletter signup in the masthead. Hidden until `action` is set to the list provider's form endpoint
 # (Buttondown: https://buttondown.com/api/emails/embed-subscribe/<username> with fields {'embed': '1'};
 #  Kit: https://app.kit.com/forms/<form id>/subscriptions with the field name email_address, see `email_field`).
 newsletter=dict(action='', fields={}, email_field='email', note=''),
 # Field-note intake: a form URL (Tally, Formspree, Google Form). Hidden until set.
 fieldnote_url='',
 changelog=CHANGELOG,
)

# ---- the Wire: research/news.json -> data/news.json (links to other outlets' reporting; see REFRESH.md)
NEWS_MAX_AGE_H = 84
def build_news():
    import datetime as dt
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research', 'news.json')
    if not os.path.exists(src):
        return []
    rows = json.load(open(src, encoding='utf-8'))
    as_of = dt.datetime.fromisoformat(AS_OF)
    out, seen = [], set()
    for r in rows:
        if not (r.get('title') and r.get('url') and r.get('published')):
            continue
        key = r['url'].split('#')[0].rstrip('/')
        if key in seen:
            continue
        seen.add(key)
        try:
            pub = dt.datetime.fromisoformat(r['published'].replace('Z', '+00:00'))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            continue
        if pub > dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1):
            continue  # a future timestamp is a typo
        if (as_of - pub).total_seconds() > NEWS_MAX_AGE_H * 3600:
            continue
        r = dict(r)
        r['title'] = r['title'].strip()[:120]
        r['summary'] = (r.get('summary') or '').strip()
        r['kind'] = r.get('kind') if r.get('kind') in ('breaking', 'incident', 'official', 'analysis') else 'incident'
        r['topic'] = r.get('topic') or 'other'
        r['siren'] = bool(r.get('siren'))
        r['also'] = [a for a in (r.get('also') or []) if a.get('url') and a.get('outlet')][:4]
        out.append(r)
    out.sort(key=lambda r: r['published'], reverse=True)
    sirens = [r for r in out if r['siren']]
    if len(sirens) != 1:
        for r in out:
            r['siren'] = False
        pick = next((r for r in out if r['kind'] == 'breaking'), out[0] if out else None)
        if pick:
            pick['siren'] = True
    return out

def load_research(name):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research', name)
    if not os.path.exists(src):
        return []
    try:
        rows = json.load(open(src, encoding='utf-8'))
    except ValueError as e:
        print('WARNING: could not parse', name, e); return []
    return rows if isinstance(rows, list) else []

def build_capabilities():
    rows = load_research('capabilities.json'); out = []
    for r in rows:
        if not (r.get('id') and r.get('title') and r.get('date')) or r['date'] > AS_OF[:10]:
            continue
        r = dict(r); r['stages'] = r.get('stages') or {}
        for k in ('demonstrated', 'reproduced', 'accessible', 'reliable', 'consequences'):
            st = dict(r['stages'].get(k) or {}); st['status'] = st.get('status') if st.get('status') in ('yes', 'partial', 'no', 'unknown') else 'unknown'; r['stages'][k] = st
        r['related_incident_ids'] = [i for i in (r.get('related_incident_ids') or []) if i]
        out.append(r)
    out.sort(key=lambda r: r['date'], reverse=True)
    return out

def build_fixes():
    rows = load_research('case_status.json'); out = []
    for r in rows:
        if not (r.get('incident_id') and r.get('chain')):
            continue
        cur = next((c for c in r['chain'] if c.get('stage') == 'current'), None)
        if not cur or cur.get('status') not in ('fixed', 'unverified', 'disputed', 'reopened', 'unresolved', 'ongoing'):
            print('WARNING: fixes: bad current status for', r['incident_id']); continue
        out.append(r)
    return out

# ---- Then. Now. Still. — one everyday task, three columns, drawn from published evidence on this index (not our own tests)
TNS = dict(
 note="Coding agents, the capability behind more incidents on this index than any other. Drawn from published evaluations and documented incidents, not from Warning Shots' own tests; each column links to its evidence.",
 then=dict(date='February 2025', title='An agent fixes about seven in ten real GitHub issues, with a human watching each run', text='Claude 3.7 Sonnet with Claude Code scored 70.3% on SWE-bench Verified, the standard test of fixing real software issues, and shipped with a documented habit of gaming the tests meant to check its work.', capabilities=['claude-code-agentic-coding-swe-bench-70'], incidents=['sonnet37-test-gaming']),
 now=dict(date='February 2026', title='The best agents work most of a day unsupervised, at a 50% success rate', text='METR measured a 12-hour time horizon for Claude Opus 4.6; a year earlier it was about an hour. Opus 4 had already coded for seven hours unattended on a production codebase.', capabilities=['claude-opus-4-6-12-hour-time-horizon', 'claude-opus-4-seven-hour-autonomous-coding'], incidents=[]),
 still=dict(date='July 2025 to April 2026', title='Still deletes production databases when it hits a wall, and still misreports what it did', text='Three production database wipes by coding agents in nine months, one followed by a false account of what happened. The limiting factor is no longer what the agent can do but whether anyone checks it.', capabilities=[], incidents=['replit-agent-deletes-saastr-db', 'claude-code-terraform-destroy-datatalksclub', 'pocketos-db-wipe']),
 could_change="Software written and operated by agents is arriving inside the products and services you use, faster than the checking around it. Expect more of what you rely on to have been built or changed by an agent nobody fully reviewed.",
 do_now="If you let an agent act for you, give it the least access that does the job, keep backups it cannot reach, and compare its summary with what it actually did; this index records agents misreporting their own actions.",
)

if __name__ == '__main__':
    json.dump(TNS, open(f'{OUT}/tns.json', 'w'), ensure_ascii=False, indent=1)
    caps = build_capabilities(); fixes = build_fixes()
    json.dump(caps, open(f'{OUT}/capabilities.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(fixes, open(f'{OUT}/fixes.json', 'w'), ensure_ascii=False, indent=0)
    print('capabilities', len(caps), 'fixes', len(fixes))
    json.dump(LIVE, open(f'{OUT}/live.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(WATCH, open(f'{OUT}/watch.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(META, open(f'{OUT}/meta.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(BRIEF, open(f'{OUT}/brief.json', 'w'), ensure_ascii=False, indent=1)
    news = build_news()
    json.dump(news, open(f'{OUT}/news.json', 'w'), ensure_ascii=False, indent=0)
    print('live', len(LIVE), 'watch', len(WATCH), 'news', len(news), 'siren', next((r['title'] for r in news if r['siren']), None))
