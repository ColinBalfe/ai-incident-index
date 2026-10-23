# Live panel, 14-day watchlist and site metadata. Refreshed by the scheduled task.
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
THN = 'https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'
KEV = 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog'
AS_OF = '2026-10-23T10:30:00-04:00'
AS_OF_LABEL = 'Oct 23, 2026, 10:30 ET'

LIVE = [
 dict(key='confirmed', value='0', label='organizations confirmed breached', detail='Previdian, SOCRadar, Wordfence and Hunt.io all report no successful remote-code execution; Sophos retracted its one claim.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='attempts', value='Millions', label='exploit attempts seen by Cloudflare', detail='Tens of thousands within 45 minutes of disclosure, millions by Oct 22.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='botnet', value='Mirai', label='first malware riding on it', detail='Attackers are trying to enlist exploited servers into a Mirai variant called Potassium for DDoS floods. No infection count has been published.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='uk', value='32', label='UK government digital services confirmed unavailable', detail='Plus four partially unavailable, mostly precautionary. The NCSC has issued about 50,000 warnings.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='vulnerable', value='34.4M', label='PHP services Censys still assesses as vulnerable', detail='Across about 3.1 million hosts, as of Oct 23. Versions before 8.2 will never get an official fix.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='kev', value='Not listed', label="on CISA's Known Exploited Vulnerabilities catalog", detail="No federal emergency directive either. A listing is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV catalog'),
]
LIVE_NOTE = "Attack traffic is enormous and the first botnet is riding on it, but no breach has been confirmed, and researchers now say reliable exploitation is harder than the leak implied. The damage so far is self-inflicted: switched-off services."

WATCH = [
 dict(id='php-breach', item='First confirmed PHP2Shell compromise', status='None as of Oct 23', kind='open',
      why='Turns a precautionary-shutdown story into real damage, and would likely put the flaws on CISA\'s exploited list within a day.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-kev', item='CISA lists the PHP flaws as exploited, or issues an emergency directive', status='Not yet', kind='open',
      why="Forces US federal agencies to patch on a deadline. It is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV'),
 dict(id='php-botnet', item='Growth of the Potassium (Mirai) botnet', status='Recruitment attempts seen; no size published', kind='open',
      why='If exploited servers are being enlisted at scale, the flaw becomes DDoS infrastructure for years: unsupported PHP 5 to 7 hosts never get a fix.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-restore', item='How fast the UK, Netherlands, Canada and Japan restore switched-off services', status='32 UK services still down', kind='open',
      why="Tells you how long 'turn it off' is a viable defense, and what the next AI-found flaw will cost.", source_url=THN, source_label='The Hacker News'),
 dict(id='openai-21', item="OpenAI's next misalignment report (the log stands at 20)", status='Last posted Oct 20', kind='due',
      why='Since the Sep 16 reporting framework the cadence has been roughly one every one to two weeks. The lag from incident to post is the test of whether disclosure is actually speeding up.', source_url='https://alignment.openai.com/misalignment-reports/', source_label='OpenAI misalignment reports'),
 dict(id='korea-attrib', item="Korean regulators' final tally and police attribution; any Microsoft report backing its Storm-0940 claim", status='Open', kind='open',
      why='Would confirm the same open-source hacking agent in both a criminal campaign and a state-aligned one.', source_url='https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/', source_label='CrowdStrike'),
 dict(id='senate', item="Senate follow-up to the 'Rogue AI' hearing and OpenAI's response to California's subpoena", status='Open', kind='open',
      why='The first legal and legislative consequences for an AI-caused breach. Watch for developer-liability language.', source_url='https://hsgac.senate.gov/subcommittees/dmdcc/hearings/rogue-ai-securing-the-homeland-against-ai-agent-attacks', source_label='Senate HSGAC'),
 dict(id='midterms', item='US midterms, Nov 3, under the FBI and CISA alert on AI-enhanced deception', status='In 11 days', kind='due',
      why='The first national election after a surge of AI-generated political ads. Any confirmed AI-driven voter-suppression operation lands here.', source_url='https://www.thestar.com.my/tech/tech-news/2026/10/16/us-tells-election-officials-to-be-on-guard-against-ai-powered-tricks-ahead-of-midterms', source_label='Reuters via The Star'),
]

BRIEF = dict(label='Oct 23, 10:30 ET', items=[
 dict(text="PHP2Shell, day two: millions of exploit attempts, a Mirai botnet variant trying to ride on it, and still zero confirmed breaches. The UK alone has 32 government digital services switched off.", url=THN, source_label='The Hacker News'),
 dict(text="Researchers who watched the first 48 hours say reliable exploitation is harder than the leak implied, while Censys still counts 34.4 million vulnerable PHP services.", url=THN, source_label='The Hacker News'),
 dict(text="CISA has not added the two PHP flaws to its exploited-vulnerabilities list and has issued no emergency directive; a listing would be its verdict that exploitation is real.", url=KEV, source_label='CISA KEV'),
])

CHANGELOG = [
 dict(date='2026-10-23', text='Launched at warningshots.ai. Added "In their words": 58 verbatim, source-verified quotes from the people in charge, with pull quotes in each incident. Added the daily brief, embeddable charts and share tools.'),
 dict(date='2026-10-23', text='PHP2Shell: overnight figures added (Mirai recruitment, 32 UK services down, 34.4M vulnerable services, still no confirmed breach). Second independent fact-check of the deep dives applied; 34 corrections.'),
 dict(date='2026-10-22', text='Added deep dives for six multi-victim incidents (146 organizations), 103 official statements, and PHP2Shell as incident 133.'),
 dict(date='2026-10-22', text='Index launched: 132 incidents scored, 20 forecasts, catalyst calendar.'),
]

META = dict(
 as_of=AS_OF, as_of_label=AS_OF_LABEL,
 next_check='2026-10-23T12:37:00-04:00', next_check_label='today, 12:37 ET',
 schedule='Refreshed three times a day (6:37, 12:37 and 18:37 ET) by a scheduled research run.',
 live_incident='php2shell', live_note=LIVE_NOTE,
 site_url='https://warningshots.ai/',
 changelog=CHANGELOG,
)

if __name__ == '__main__':
    json.dump(LIVE, open(f'{OUT}/live.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(WATCH, open(f'{OUT}/watch.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(META, open(f'{OUT}/meta.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(BRIEF, open(f'{OUT}/brief.json', 'w'), ensure_ascii=False, indent=1)
    print('live', len(LIVE), 'watch', len(WATCH))
