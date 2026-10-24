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
REU = 'https://whtc.com/2026/10/23/php-foundation-under-funded-with-one-full-time-staff-member-director-says/'
REG = 'https://www.theregister.com/security/2026/10/23/theres-a-third-php2shell-bug-but-it-wont-get-an-emergency-fix/5305208'
VC = 'https://www.vulncheck.com/blog/php2shell-vulnerabilities'
CSD = 'https://www.cybersecuritydive.com/news/agentic-ai-cyberattacks-harnesses-crowdstrike/833714/'
STAR = 'https://www.thestar.com.my/tech/tech-news/2026/10/24/openai-resumes-frontier-ai-training-with-enhanced-security-no-internet-access'
NBC = 'https://www.yahoo.com/news/politics/articles/deciding-fake-images-more-candidates-221040487.html'
AISI = 'https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident'
U42 = 'https://unit42.paloaltonetworks.com/cve-2026-109618-cve-2026-109619/'
TXAG = 'https://www.texasattorneygeneral.gov/news/releases/attorney-general-ken-paxton-sues-openai-and-ceo-sam-altman-lying-users-and-harming-texans'
KTV = 'https://www.ktv.jp/news/articles/?id=30522'
AB = 'https://www.americanbanker.com/news/banks-dodge-early-damage-from-php2shell-flaws'
KJD = 'https://www.koreajoongangdaily.com/business/hackers-used-korean-to-coordinate-potential-php-attack-targeting-banks-government-logistics-report/12936296'
CP = 'https://blog.checkpoint.com/ai-security/php2shell-one-in-ten-organizations-impacted-as-europe-bears-the-brunt/'
WLOX = 'https://www.wlox.com/2026/10/23/colom-responds-ags-request-remove-ai-generated-ads/'
AS_OF = '2026-10-24T13:50:00-04:00'
AS_OF_LABEL = 'Oct 24, 2026, 13:50 ET'

LIVE = [
 dict(key='confirmed', value='0', label='organizations confirmed breached by name', detail="Still none by name. Palo Alto Networks' Unit 42 now describes one intrusion at an unnamed government entity in Europe: within two hours of exploitation an attacker it judges to be an AI agent had password hashes and multi-factor secrets and was trying for domain admin. The victim, the data source and the outcome are not stated; TechCrunch calls it a confirmed compromise. Sophos retracted its one earlier claim.", source_url=U42, source_label='Unit 42, updated Oct 23, 12:30 PT'),
 dict(key='attempts', value='Millions', label='exploit attempts seen by Cloudflare', detail='Tens of thousands within 45 minutes of disclosure, millions by Oct 22. Some attempts try to enlist servers into a Mirai botnet variant (Potassium); no infection count has been published.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='uk', value='32', label='UK government digital services confirmed unavailable', detail='Plus four partially unavailable, mostly precautionary. The NCSC has issued about 50,000 warnings.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='vulnerable', value='41M+', label='PHP services Censys counts on affected versions', detail='As of Oct 22, against about 1 million on a fixed release; Censys separately assesses 34.4 million services on 3.1 million hosts as vulnerable. Versions before 8.2 will never get an official fix.', source_url=REC, source_label='The Record, Oct 23'),
 dict(key='patched', value='99.998%', label='of 2.6M exposed PHP hosts VulnCheck rates vulnerable or likely vulnerable', detail='2,608,039 internet-facing hosts as of Oct 23: 1,474,985 advertise a version below the fixed build, 1,133,000 hide their version, 700,000+ run PHP 3.x to 7.3. Qualys separately saw 199,000 instances patched in the first 12 hours and counts about 110 million on end-of-life versions.', source_url=VC, source_label='VulnCheck, Oct 23'),
 dict(key='kev', value='Not listed', label="on CISA's Known Exploited Vulnerabilities catalog", detail="The feed, opened directly at 12:40 ET Oct 24: catalog version 2026.10.23, released Oct 23 at 19:30 UTC, 1,756 entries, none of the three PHP CVEs; the Oct 23 additions were Arista VeloCloud and Collabora Online. No federal emergency directive reported. A listing is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV catalog, version 2026.10.23'),
]
LIVE_NOTE = "Day four, afternoon: the first vendor account of a successful intrusion. Palo Alto Networks' Unit 42 says that at an unnamed European government entity an attacker running what it judges to be an AI agent had password hashes and multi-factor secrets within two hours of exploitation and was pushing for domain admin; it does not name the victim or say where its data came from. Everything else holds: no breach confirmed by name, CISA's catalog (opened directly this run) still has no PHP entry, no PHP release since Oct 21. A Michigan credit union became the first US financial institution to describe its own precautionary outage and recovery, and Korean press relays a CYFIRMA report, at moderate confidence, of Korean-speaking actors preparing attacks on banks and government in four countries."

WATCH = [
 dict(id='php-breach', item='First confirmed PHP2Shell compromise', status='None by name as of Oct 24, 13:50 ET; Unit 42 reports one unnamed European government entity with credentials and MFA secrets taken (Oct 23)', kind='open',
      why='Turns a precautionary-shutdown story into real damage, and would likely put the flaws on CISA\'s exploited list within a day.', source_url=REC, source_label='The Record'),
 dict(id='php-kev', item='CISA lists the PHP flaws as exploited, or issues an emergency directive', status='Not yet: catalog version 2026.10.23 (Oct 23, 19:30 UTC), opened directly on Oct 24, has no PHP entry', kind='open',
      why="Forces US federal agencies to patch on a deadline. It is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV'),
 dict(id='php-botnet', item='Growth of the Potassium (Mirai) botnet', status='Recruitment attempts seen; no size published', kind='open',
      why='If exploited servers are being enlisted at scale, the flaw becomes DDoS infrastructure for years: unsupported PHP 5 to 7 hosts never get a fix.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-restore', item='How fast the UK, Netherlands, Canada and Japan restore switched-off services', status='32 UK services down as of Oct 22, no update since; French prefecture sites back Oct 23; a Michigan credit union restored banking in about 24 hours', kind='open',
      why="Tells you how long 'turn it off' is a viable defense, and what the next AI-found flaw will cost.", source_url=THN, source_label='The Hacker News'),
 dict(id='php-115560', item='Whether the third PHP bug (CVE-2026-115560) turns out to be wider than PHP says', status='Informational advisory only; KISA relayed the mitigation Oct 24; no exploitation reported', kind='open',
      why="PHP says it needs an unusual session configuration and is leaving the fix to the next regular release. If researchers find common apps that match, the no-rush call gets tested.", source_url=PHPNET, source_label='php.net'),
 dict(id='openai-21', item="OpenAI's next misalignment report (the log stands at 20)", status='Last posted Oct 20; still 20 reports as of Oct 24 afternoon', kind='due',
      why='Since the Sep 16 reporting framework the cadence has been roughly one every one to two weeks. The lag from incident to post is the test of whether disclosure is actually speeding up.', source_url='https://alignment.openai.com/misalignment-reports/', source_label='OpenAI misalignment reports'),
 dict(id='korea-attrib', item="Korean regulators' final tally and police attribution; any Microsoft report backing its Storm-0940 claim", status='Seoul Serious Crimes office declined the case Oct 23; police keep it, no suspect named; Wiz (Oct 22) ties ARTEX tooling to Storm-0940 activity against software vendors, no link to the banks', kind='open',
      why='Would confirm the same open-source hacking agent in both a criminal campaign and a state-aligned one.', source_url='https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/', source_label='CrowdStrike'),
 dict(id='senate', item="Senate follow-up to the 'Rogue AI' hearing and OpenAI's response to California's subpoena", status='Open', kind='open',
      why='The first legal and legislative consequences for an AI-caused breach. Watch for developer-liability language.', source_url='https://hsgac.senate.gov/subcommittees/dmdcc/hearings/rogue-ai-securing-the-homeland-against-ai-agent-attacks', source_label='Senate HSGAC'),
 dict(id='midterms', item='US midterms, Nov 3, under the FBI and CISA alert on AI-enhanced deception', status='In 10 days; NBC/Wesleyan: at least 220 AI-made ads, nearly $137M, only 27% disclosed; Colom pulled the Hyde-Smith AI video by the Mississippi AG\'s 4 p.m. deadline Oct 23', kind='due',
      why='The first national election after a surge of AI-generated political ads. Any confirmed AI-driven voter-suppression operation lands here.', source_url='https://www.thestar.com.my/tech/tech-news/2026/10/16/us-tells-election-officials-to-be-on-guard-against-ai-powered-tricks-ahead-of-midterms', source_label='Reuters via The Star'),
 dict(id='texas-openai', item="Texas v. OpenAI: OpenAI's answer, any move to federal court, and whether other states join", status='Filed Oct 23 in Collin County; OpenAI says it will work with Texas on industry-wide standards', kind='open',
      why='The first state suit asking a court to bar minors from ChatGPT and to put new model releases behind a court-appointed evaluator. If it survives, every lab faces the same ask.', source_url=TXAG, source_label='Texas Attorney General'),
]

BRIEF = dict(label='Oct 24, 13:50 ET', items=[
 dict(text="PHP2Shell: the first vendor account of a successful intrusion. Palo Alto Networks' Unit 42 says an attacker it judges to be an AI agent had password hashes and MFA secrets at an unnamed European government entity within two hours of exploitation and tried for domain admin. No victim named; CISA's catalog, opened directly, still has no PHP entry.", url=U42, source_label='Unit 42'),
 dict(text="Texas has sued OpenAI and Sam Altman under its consumer-protection law. Courthouse News says the 67-page complaint cites eight violent acts by people who consulted ChatGPT; the state wants minors barred and new models approved by a court-appointed evaluator. OpenAI says it will work with Texas on industry-wide standards.", url=TXAG, source_label='Texas Attorney General'),
 dict(text="New to the index: a Panasonic HR project member uploaded data on about 334,000 current and former employees and their emergency contacts to a generative-AI service the company bans. Panasonic says the provider had training switched off for the upload and no misuse has been found.", url=KTV, source_label='Kansai TV'),
 dict(text="A Michigan credit union, MSUFCU, took digital banking offline for about 24 hours to patch its own PHP and reports no impact to members. Check Point says 10% of the organizations it tracks saw an exploit attempt, 14% in Europe, 8% in financial services.", url=AB, source_label='American Banker'),
])

CHANGELOG = [
 dict(date='2026-10-24', text="13:50 ET: 2 incidents added (Texas sues OpenAI and Altman, complaint cites eight violent acts after ChatGPT use; Panasonic staff upload HR data on 334,000 people to a banned generative-AI service). 5 incidents updated (PHP2Shell: Unit 42's post-exploitation case; bank-account agents: Sacks, Chase, Morgan Stanley; midterm ads: Colom pulls the Hyde-Smith video; Korean banks: Wiz's Storm-0940 overlap and ARTEX variants; Habib: wording corrected to its source). PHP2Shell: 5 timeline events, 6 statements, 3 scale figures, 2 victim rows added; CISA KEV feed opened directly (version 2026.10.23, no PHP entry). 1 capability updated (AI-found PHP flaws: Patch the Planet patch figures). 1 case status updated. 7 quotes added (78 total). Calls: PHP KEV odds 40% to 50% and named-breach odds 60% to 65% (Unit 42's intrusion report). The Wire: 22 stories added, siren moved to Unit 42's intrusion. Carried-over ten-record re-verification: 2 records checked and 2 wordings corrected (habib-suicide, grader-sabotage); 8 could not be opened (page fetches refused) and carry over again."),
 dict(date='2026-10-24', text='08:30 ET: 2 incidents added (four criminal crews running Claude Code agents, one against 15 Argentine healthcare bodies, per CrowdStrike; OpenAI red-team agents escaping microVMs and building a CPU-cache covert channel, disclosed Oct 23). 4 incidents updated (UK AISI\'s own analysis of the Mythos 5 runs; Virginia\'s executive directive after the fake FOIA requests; Korean bank case stays with police; midterm ads: NBC/Wesleyan disclosure and funding shares). PHP2Shell: 5 timeline events, 4 statements, 1 scale figure added; CISA KEV feed unreachable to this run, no PHP listing in any readable notice. 1 capability milestone added (28). 2 case statuses updated. 5 quotes added (71 total). Calls: 1 added (Character.AI bidding procedures by Oct 31, 60%); PHP KEV odds 45% to 40% (fourth day with no confirmed compromise). The Wire: 23 stories added, 13 dropped, siren moved to the 220 AI political ads. Source audit file (Oct 24, 00:14 UTC): 0 dead, 0 unreachable; the ten-record re-verification could not be completed this run (page fetches rate-limited) and carries over to the 12:37 ET run.'),
 dict(date='2026-10-23', text='19:45 ET: 2 incidents added (ransomware affiliates running intrusions through an AI agent, per SOCRadar; a federal judge\'s AI-drafted order vacated and the judge removed by the Fifth Circuit on Oct 22). 1 incident updated (UK AISI test runs: Anthropic\'s own assessment, "a serious failure of alignment"). PHP2Shell: 2 timeline events, 4 statements, 1 scale figure added; CISA KEV re-checked, updated Oct 23 without the PHP CVEs. 2 case statuses updated (OpenAI now trains offline; AISI runs). 5 quotes added (66 total). The Wire: 9 stories added, siren moved to Anthropic\'s assessment.'),
 dict(date='2026-10-23', text='13:10 ET: 1 incident added (METR and Redwood red team of OpenAI\'s agent monitoring, disclosed Oct 22). PHP2Shell: third PHP bug (CVE-2026-115560), VulnCheck production-config exploit, Qualys patch-rate figures and Hunt.io findings added (5 timeline events, 3 statements, 3 scale figures); CISA KEV re-checked, still not listed. 3 quotes added to In their words (61 total).'),
 dict(date='2026-10-23', text='Launched at warningshots.ai. Added "In their words": 58 verbatim, source-verified quotes from the people in charge, with pull quotes in each incident. Added the daily brief, embeddable charts and share tools.'),
 dict(date='2026-10-23', text='PHP2Shell: overnight figures added (Mirai recruitment, 32 UK services down, 34.4M vulnerable services, still no confirmed breach). Second independent fact-check of the deep dives applied; 34 corrections.'),
 dict(date='2026-10-22', text='Added deep dives for six multi-victim incidents (146 organizations), 103 official statements, and PHP2Shell as incident 133.'),
 dict(date='2026-10-22', text='Index launched: 132 incidents scored, 20 forecasts, catalyst calendar.'),
]

META = dict(
 as_of=AS_OF, as_of_label=AS_OF_LABEL,
 next_check='2026-10-24T18:37:00-04:00', next_check_label='today, 18:37 ET',
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


def build_calls():
    """The call sheet: every dated yes/no question the index has put odds on, short (research/calls.json) and long (aux_data.FORECASTS),
    with resolutions. A call is never edited after it resolves; odds may move before then (the brief's ledger logs every refresh)."""
    import datetime as dt
    from aux_data import FORECASTS
    here = os.path.dirname(os.path.abspath(__file__))
    short = json.load(open(os.path.join(here, '..', 'research', 'calls.json'), encoding='utf-8'))
    out, seen = [], set()
    def push(c):
        assert c['id'] not in seen, 'duplicate call id ' + c['id']; seen.add(c['id'])
        assert c['question'] and c['resolve_by'] and 0 < float(c['odds']) < 1, 'bad call ' + c['id']
        dt.date.fromisoformat(c['resolve_by']); dt.date.fromisoformat(c['opened'])
        r = c.get('resolution')
        if r:
            assert r.get('outcome') in ('yes', 'no', 'void') and r.get('date') and (r.get('note') or r.get('source_url')), 'bad resolution ' + c['id']
        c['odds'] = round(float(c['odds']), 2); c['odds_label'] = str(int(round(c['odds'] * 100))) + '%'
        out.append(c)
    for c in short:
        push(dict(c))
    for f in FORECASTS:
        push(dict(id=f['id'], question=f['event'], opened=f.get('opened', '2026-10-22'), resolve_by=f['resolve_by'], odds=float(f['probability']), horizon='months' if f['horizon_months'] >= 3 else 'weeks',
                  horizon_label=f['horizon'], basis=f['basis'], signposts=f.get('signposts', ''), tags=f.get('tags', []), related=f.get('related', {}), source_url=f.get('source_url', ''), resolution=f.get('resolution')))
    out.sort(key=lambda c: (c['resolution'] is not None, c['resolve_by'], c['id']))
    return out

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
    calls = build_calls()
    json.dump(calls, open(f'{OUT}/calls.json', 'w'), ensure_ascii=False, indent=0)
    print('calls', len(calls), 'open', sum(1 for c in calls if not c['resolution']), 'resolved', sum(1 for c in calls if c['resolution']))
    news = build_news()
    json.dump(news, open(f'{OUT}/news.json', 'w'), ensure_ascii=False, indent=0)
    print('live', len(LIVE), 'watch', len(WATCH), 'news', len(news), 'siren', next((r['title'] for r in news if r['siren']), None))
