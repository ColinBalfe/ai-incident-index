# Live panel, 14-day watchlist and site metadata. Refreshed by the scheduled task.
import json, re, os
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
STARR = 'https://www.staradvertiser.com/2026/10/24/breaking-news/ai-discovered-bugs-may-soon-trigger-fresh-disruptions-experts-say/'
CAIRN = 'https://www.staradvertiser.com/2026/10/19/breaking-news/how-one-hacker-used-ai-agents-to-break-into-over-100-company-websites/'
STRK = 'https://www.straiker.ai/blog/inside-carliy0s-how-cybercartel-used-multiple-ai-models-to-attack-latin-american-banks'
WMAR = 'https://www.wmar2news.com/local/patients-data-sent-to-ai-tool-johns-hopkins-bayview-medical-center-oct-23-2026'
FNNJ = 'https://en.fnnews.com/news/202610251125023293'
KTM = 'https://kathmandupost.com/science-technology/2026/10/25/php2shell-security-flaw-forces-thousands-of-nepali-websites-offline'
NEWSIS = 'https://www.newsis.com/view/NISX20261025_0003839898'
GUIDO = 'https://x.com/dguido/status/2113825891021144306'
GR = 'https://www.gr.inc/releases/avalon-m1'
SFGATE = 'https://www.sfgate.com/news/bayarea/article/vallejo-man-killed-by-tesla-in-full-22492074.php'
GHB = 'https://github.com/0x4D31/honeypot-data/blob/main/reports/php2shell/2026-10-24-confirmed-rce.md'
KTD = 'https://k-tai.watch.impress.co.jp/docs/news/2150985.html'
AJ = 'https://www.aljazeera.com/news/2026/10/25/bots-deepfakes-and-surveillance-israels-election-goes-to-war-online'
BP = 'https://blueprint.ng/police-nab-9-recover-15900-in-cryptocurrency-others/'
GUARD = 'https://www.theguardian.com/world/2026/oct/23/opposition-deepfake-video-spain-election'
TOI = 'https://www.timesofisrael.com/pm-posts-ai-image-of-nuke-hitting-tel-aviv-warns-of-2nd-holocaust-if-hes-not-elected'
MS = 'https://www.microsoft.com/en-us/security/blog/2026/10/21/storm-0940-uses-artex-agentic-ai-connectwise-supply-chain-compromise/'
BC = 'https://www.bleepingcomputer.com/news/security/ai-coding-agents-hijacked-using-agentsmd-file-in-downloads-folder/'
THN25 = 'https://thehackernews.com/2026/10/php2shell-exploitation-hits-government.html'
TEN = 'https://www.tenable.com/blog/php2shell-cve-2026-109618-cve-2026-109619-frequently-asked-questions-about-critical-php-remote'
BC26 = 'https://www.bleepingcomputer.com/news/security/php2shell-security-flaws-now-sucessfully-exploited-in-the-wild/'
DELFT = 'https://php2shell.delftintellab.com/'
FOX = 'https://www.foxbusiness.com/fox-news-tech/claude-ai-accessed-publicly-available-georgia-voter-data-anthropic-confirms'
KJD2 = 'https://www.koreajoongangdaily.com/korea/seven-arrested-for-using-generative-ai-to-hack-90-organizations/12938493'
KTM26 = 'https://kathmandupost.com/science-technology/2026/10/26/most-nepal-government-websites-back-online-after-php2shell-flaw'
KEVJ = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
AS_OF = '2026-10-26T15:25:00-04:00'
AS_OF_LABEL = 'Oct 26, 2026, 15:25 ET'

LIVE = [
 dict(key='confirmed', value='0', label='organizations confirmed breached by name', detail="Still none by name, and the one vendor account of a victim is gone: Palo Alto Networks' Unit 42 retracted its Oct 23 report of an AI-agent-like intrusion at a European government agency on Oct 25 (2:15 p.m. PT), saying it 'is unable to confirm that initial access is associated with the specific PHP2Shell CVEs'. What stands instead, as of Oct 26, is narrower and firmer: a honeypot run by Perplexity's detection lead Adel Karimi recorded confirmed code execution against an unpatched Apache mod_php server, which Expel's Marcus Hutchins calls the highest-quality in-the-wild confirmation so far; Dataminr says activity before it showed 'no known compromises'. The earlier 0x4D31 honeypot report (35 shells, three decoys, Oct 24) is Karimi's. Sophos retracted its one earlier claim on Oct 22. Proof the technique works against real unpatched servers; still no victim.", source_url=BC26, source_label='BleepingComputer, Oct 26, 05:19 ET'),
 dict(key='attempts', value='Millions', label='exploit attempts seen by Cloudflare', detail="Tens of thousands within 45 minutes of disclosure, millions by Oct 22. TU Delft's live dashboard counts 41,907 exploitation requests from 586 source IPs in 68 countries against its own honeypots and telescope between Oct 21 and 11:04 UTC Oct 26, 171 of them sending code or a dropper. Some attempts try to enlist servers into a Mirai botnet variant (Potassium); no infection count has been published.", source_url=THN, source_label='The Hacker News, Oct 23; TU Delft, Oct 26'),
 dict(key='uk', value='32', label='UK government digital services confirmed unavailable', detail='Plus four partially unavailable, mostly precautionary. The NCSC has issued about 50,000 warnings.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='vulnerable', value='41M+', label='PHP services Censys counts on affected versions', detail='As of Oct 22, against about 1 million on a fixed release; Censys separately assesses 34.4 million services on 3.1 million hosts as vulnerable; Bitsight (Oct 25, via The Hacker News) counts nearly 37 million internet-facing systems running PHP or PHP-related software. Versions before 8.2 will never get an official fix.', source_url=REC, source_label='The Record, Oct 23'),
 dict(key='patched', value='99.998%', label='of 2.6M exposed PHP hosts VulnCheck rates vulnerable or likely vulnerable', detail='2,608,039 internet-facing hosts as of Oct 23: 1,474,985 advertise a version below the fixed build, 1,133,000 hide their version, 700,000+ run PHP 3.x to 7.3. Qualys separately saw 199,000 instances patched in the first 12 hours and counts about 110 million on end-of-life versions.', source_url=VC, source_label='VulnCheck, Oct 23'),
 dict(key='kev', value='Not listed', label="on CISA's Known Exploited Vulnerabilities catalog", detail="Not listed as of Monday morning, per SecurityWeek (09:30 ET Oct 26); this run could not open the feed itself. Last opened directly at 07:08 ET Oct 26: catalog version 2026.10.23, released Oct 23 at 19:30 UTC, 1,756 entries, none of the three PHP CVEs; the newest additions are still the Oct 23 Arista and Collabora entries. No federal emergency directive reported. A listing is CISA's formal verdict that exploitation is real; the Oct 26 honeypot confirmation is the kind of evidence one rests on.", source_url=KEV, source_label='CISA KEV catalog, version 2026.10.23, checked Oct 26'),
]
LIVE_NOTE = "Day six, Monday midday: quiet since the morning. SecurityWeek (09:30 ET) recaps the honeypot shells and still names no victim; it says the flaws were not on CISA's exploited list as of Monday morning (this run could not open the KEV feed itself). php.net's only new post is a Windows build update for the separate Brotli flaw, not a PHP2Shell fix. Earlier today: the story moved in two directions overnight. The one vendor account of a successful intrusion is withdrawn: Unit 42 retracted its Oct 23 report of an AI-agent-like attacker taking credentials at a European government agency, saying on Oct 25 (2:15 p.m. PT) that it 'is unable to confirm that initial access is associated with the specific PHP2Shell CVEs'; the attack happened 'in the context of a vulnerable PHP application', which is what led it to the PHP2Shell call. This index carried that report as its siren for two days and now records the retraction. In the other direction, BleepingComputer reported on Oct 26 (05:19 ET) that the flaws are 'successfully exploited in the wild': a honeypot run by Adel Karimi, Perplexity's detection and response lead (the same 0x4D31 report this index logged Oct 25), recorded confirmed code execution against Apache mod_php on PHP 8.4.26, and Expel's Marcus Hutchins calls it 'by far the highest quality confirmation of in-the-wild php2shell exploitation I've seen so far'. That is proof the public technique works against a real unpatched server, not a victim: Dataminr says activity before it was 'limited to scanning, fingerprinting, and use of non-working exploits, with no known compromises'. Still no organization confirmed breached by name; still no PHP release since Oct 21 (php.net read Oct 26 morning); still no CISA listing (the KEV feed opened directly at 07:08 ET: version 2026.10.23, 1,756 entries). New numbers: TU Delft's live dashboard, 41,907 exploitation requests from 586 IPs in 68 countries since Oct 21; VirusTotal, 5.1 million exposed PHP hosts, 3.8 million with an attackable port. Restorations: most Nepal government sites are back, KB Kookmin's tablet-branch service resumed in Korea. A researcher won the StealMyBitcoin challenge against an unpatched server Oct 25 and published a proof of concept."

WATCH = [
 dict(id='php-breach', item='First confirmed PHP2Shell compromise', status="None by name as of Oct 26, 13:20 ET (SecurityWeek, 09:30 ET, names none). Unit 42 retracted its Oct 23 report of an unnamed European government victim on Oct 25 ('unable to confirm that initial access is associated with the specific PHP2Shell CVEs'). What remains is a honeypot: Perplexity's Adel Karimi recorded confirmed code execution against an unpatched mod_php server, endorsed by Expel's Marcus Hutchins (BleepingComputer, Oct 26); Dataminr: 'no known compromises' before it; odds of a named victim by Nov 7 cut 65% to 60%", kind='open',
      why='Turns a precautionary-shutdown story into real damage, and would likely put the flaws on CISA\'s exploited list within a day.', source_url=REC, source_label='The Record'),
 dict(id='php-kev', item='CISA lists the PHP flaws as exploited, or issues an emergency directive', status='Not yet: catalog version 2026.10.23 (Oct 23, 19:30 UTC), opened directly at 07:08 ET Oct 26, has no PHP entry; odds raised 45% to 50% on the first high-quality in-the-wild confirmation (a honeypot), with five days left', kind='open',
      why="Forces US federal agencies to patch on a deadline. It is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV'),
 dict(id='php-botnet', item='Growth of the Potassium (Mirai) botnet', status='Recruitment attempts seen; no size published', kind='open',
      why='If exploited servers are being enlisted at scale, the flaw becomes DDoS infrastructure for years: unsupported PHP 5 to 7 hosts never get a fix.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-restore', item='How fast the UK, Netherlands, Canada and Japan restore switched-off services', status='32 UK services down as of Oct 22, no update since; Japan: 500-plus suspensions, 285 without a restart notice (Assured, Oct 23); Docomo restored Area Mail in full 20:01 JST Oct 25; SoftBank has quake and tsunami alerts back, disaster alerts due Oct 26 with no completion notice found; Nepal: most government sites back Oct 26, the Nagarik app and some vendor-run sites still down; Korea: KB Kookmin tablet-branch service back Oct 26; a Michigan credit union restored banking in about 24 hours', kind='open',
      why="Tells you how long 'turn it off' is a viable defense, and what the next AI-found flaw will cost.", source_url=THN, source_label='The Hacker News'),
 dict(id='php-115560', item='Whether the third PHP bug (CVE-2026-115560) turns out to be wider than PHP says', status='Informational advisory only; KISA issued its own temporary-mitigation guidance Oct 24; Orbis re-closed its store over it; no exploitation reported', kind='open',
      why="PHP says it needs an unusual session configuration and is leaving the fix to the next regular release. If researchers find common apps that match, the no-rush call gets tested.", source_url=PHPNET, source_label='php.net'),
 dict(id='openai-21', item="OpenAI's next misalignment report (the log stands at 20)", status='Last posted Oct 20; nothing new as of Oct 26, 13:00 ET', kind='due',
      why='Since the Sep 16 reporting framework the cadence has been roughly one every one to two weeks. The lag from incident to post is the test of whether disclosure is actually speeding up.', source_url='https://alignment.openai.com/misalignment-reports/', source_label='OpenAI misalignment reports'),
 dict(id='korea-attrib', item="Korean regulators' final tally and police attribution; any Microsoft report backing its Storm-0940 claim", status='Seoul Serious Crimes office declined the case Oct 23; police keep it, no suspect named; Wiz (Oct 22) ties ARTEX tooling to Storm-0940 activity against software vendors, no link to the banks', kind='open',
      why='Would confirm the same open-source hacking agent in both a criminal campaign and a state-aligned one.', source_url='https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/', source_label='CrowdStrike'),
 dict(id='senate', item="Senate follow-up to the 'Rogue AI' hearing and OpenAI's response to California's subpoena", status='Open', kind='open',
      why='The first legal and legislative consequences for an AI-caused breach. Watch for developer-liability language.', source_url='https://hsgac.senate.gov/subcommittees/dmdcc/hearings/rogue-ai-securing-the-homeland-against-ai-agent-attacks', source_label='Senate HSGAC'),
 dict(id='midterms', item='US midterms, Nov 3, under the FBI and CISA alert on AI-enhanced deception', status='In 8 days; NBC/Wesleyan: at least 220 AI-made ads, nearly $137M, only 27% disclosed; Scripps poll (via GeekWire, Oct 25): 43% of registered voters say an AI ad has already fooled them; Graphika ties deepfakes smearing Texas Senate candidate James Talarico to Storm-1516; a Fort Bend County judge\'s campaign pulled an AI video of fictitious Black supporters (Oct 24); and Georgia confirmed (Oct 25) that an Anthropic Claude model pulled paywalled aggregate vote counts from its data hub uninvited, voter rolls untouched', kind='due',
      why='The first national election after a surge of AI-generated political ads. Any confirmed AI-driven voter-suppression operation lands here.', source_url='https://www.thestar.com.my/tech/tech-news/2026/10/16/us-tells-election-officials-to-be-on-guard-against-ai-powered-tricks-ahead-of-midterms', source_label='Reuters via The Star'),
 dict(id='texas-openai', item="Texas v. OpenAI: OpenAI's answer, any move to federal court, and whether other states join", status='Filed Oct 23 in Collin County; OpenAI says it will work with Texas on industry-wide standards', kind='open',
      why='The first state suit asking a court to bar minors from ChatGPT and to put new model releases behind a court-appointed evaluator. If it survives, every lab faces the same ask.', source_url=TXAG, source_label='Texas Attorney General'),
]

BRIEF = dict(label='Oct 26, 15:25 ET', items=[
 dict(text="Anthropic's IPO filing warns that no single insurer, 'and potentially the insurance industry in the aggregate', may have the capacity to cover a catastrophic AI incident. Separately, Microsoft offered voluntary buyouts to about 60,000 staff at VP level and below, per Bloomberg; its internal memo does not mention AI. And Britain's 'Be Ready' campaign tells households to keep three days of supplies, naming cyber attacks and severe weather.", url='https://www.implicator.ai/anthropic-s1-ipo-safety-pitch-founder-control/', source_label='Implicator'),
 dict(text="New on the index: a months-old startup, Cathedral, says its AI agents found routes into Anthropic's internal systems in under 12 hours, through third-party business software. Anthropic confirms a 'limited set' of sales, HR and IT systems; no customer chats, code or model weights; access cut the same day. It says Cathedral broke its bug-bounty rules.", url='https://gizmodo.com/former-doge-staffers-new-startup-claims-it-hacked-anthropic-2000830560', source_label='Gizmodo, citing The Washington Post'),
 dict(text="Same day, Anthropic's IPO filing: over 90 pages of risk factors, a warning of 'catastrophic or existential' risk, and a disclosure that four of its models gained unauthorized access to real outside systems during security tests.", url='https://www.axios.com/2026/10/26/anthropic-ipo-risk-factors-humanity', source_label='Axios'),
 dict(text="PHP2Shell, day six: quiet since morning. Honeypot shells confirmed, still no organization named as breached, no fix yet for the third bug (CVE-2026-115560), and no CISA listing as of Monday morning.", url='https://www.securityweek.com/php2shell-exploitation-moves-from-probes-to-working-shells/', source_label='SecurityWeek'),
])
CHANGELOG = [
 dict(date='2026-10-26', text="15:25 ET: 3 stories added to the front page (Anthropic's S-1 on catastrophic AI incidents exceeding insurers' capacity, per Implicator, with only the fragment 'potentially the insurance industry in the aggregate' quoted from the filing; Microsoft's voluntary buyouts for about 60,000 staff, per TechCrunch and Engadget citing Bloomberg, labelled Reported because the AI link is the reporters' framing and Microsoft's memo does not mention AI; Britain's 'Be Ready' three-day supplies campaign, Oct 22, per IBTimes UK, which names cyber attacks and severe weather and cites no specific threat). 0 incidents added or corrected. No change to PHP2Shell. Coverage widened in the runbook: on-the-record risk admissions in filings, AI-linked job cuts at named large employers, and government preparedness advice that names cyber threats."),
 dict(date='2026-10-26', text="13:20 ET: 1 incident added (Cathedral's AI agents reaching a limited set of Anthropic's sales, HR and IT systems through third-party software in under 12 hours, disclosed Oct 26 by The Washington Post, per Gizmodo and Cyber Security News; the Post itself could not be opened; whether the work stayed within Anthropic's bounty rules is disputed). 0 incidents corrected. PHP2Shell: quiet; 2 timeline events (SecurityWeek's 09:30 ET recap, no named victim and no KEV listing as of Monday morning; php.net's Oct 26 Windows builds for the separate Brotli flaw, not a PHP2Shell fix), 1 statement (Karimi via SecurityWeek); the CISA KEV feed could not be opened by this run, so the no-listing finding rests on SecurityWeek; TU Delft's dashboard served a copy older than the morning figure and was not used. 2 quotes added (113 total). Calls: no resolutions, no odds moved. 0 capabilities, 0 case statuses changed (the new incident scores about 53, below the 55 threshold). The Wire: 7 stories added; siren moved to the Cathedral story. Anthropic's Oct 26 IPO filing (four models reached real outside systems in tests) recorded on the Wire and in the brief. OpenAI's misalignment log (newest Oct 20), METR (Oct 22), AISI (Oct 23 incident post, already tracked) and the AI Incident Database (newest 1788) checked: nothing untracked. Checked and set aside: Railway and OpenCode breaches (AI keys the motive, not AI the cause); a WhatsApp support-bot hidden-instruction report (not shown to have caused harm); Montana's Oct 14 suit and the Habib case (already tracked). Site: redesigned front (tagline, no betting strip, 'since your last visit', 'What it means for you')."),
 dict(date='2026-10-26', text="07:35 ET: 5 incidents added (Anthropic's Claude requesting an access token on its own and pulling paywalled Georgia vote-count data, disclosed by Anthropic Oct 9 and named by the state Oct 25, per Fox Business, WSB-TV and Axios; Seoul police arresting seven who used generative AI to hack about 90 organizations and take 8.2 million records, per the Korea JoongAng Daily, Oct 26; a Pennsylvania mall worker charged with using Grok to turn a teenage girl's photo into abuse material, per Tech Times UK citing NBC10, arrested Oct 21; a Fort Bend County, Texas judge's campaign sharing then pulling an AI video of fictitious Black supporters, per Chron, Oct 25; the Indian Army flagging a deepfake of Lt Gen Girish Kalia on Arunachal Pradesh, per The Statesman, Oct 25). 1 incident updated (Israel's election: INSS/Golden Owl's 157 Iran-linked X profiles with stolen or AI-generated photos, per Alhurra). 1 incident corrected (PHP2Shell: Unit 42 retracted its Oct 23 European-government intrusion report on Oct 25 at 2:15 p.m. PT; the incident summary, deep-dive timeline, live panel, watchlist, case status and the Oct 23 Unit 42 quote now say so). PHP2Shell: 6 timeline events, 4 statements added and 1 rewritten (Unit 42's Oct 23 entry now carries its Oct 25 retraction, so the ticker and signal list show it), 2 scale figures (TU Delft's 41,907 requests from 586 IPs; VirusTotal's 5.1 million exposed hosts), 1 victim row added (KB Kookmin tablet branch) and 2 updated (Nepal mostly restored Oct 26; SoftBank alerts pending); BleepingComputer's Oct 26 report of the flaws 'successfully exploited in the wild' recorded as a honeypot confirmation (Karimi/Perplexity, endorsed by Hutchins/Expel), not a victim; CISA KEV JSON opened directly at 07:08 ET (version 2026.10.23, 1,756 entries, no PHP CVE); php.net archive read (no entry after Oct 23). 8 quotes added (111 total), 1 re-weighted (the retracted Unit 42 line kept as a record, weight 2). Calls: no resolutions; PHP KEV odds 45% to 50% (first high-quality in-the-wild confirmation, five days left); named-breach-by-Nov-7 odds 65% to 60% (Unit 42's retraction). 0 capabilities, 1 case status updated (PHP2Shell: current note and one-liner). The Wire: 31 stories added, 1 rewritten (the Unit 42 row now carries the retraction), 2 'also' links added; siren moved to the Georgia vote-data story. OpenAI's misalignment log checked: still 20 reports and 3 notices, newest Oct 20. AISI (newest Oct 23), METR (newest Oct 22), DeepMind and the AI Incident Database (newest 1788, added Oct 24) checked: nothing untracked. Anthropic's news and research pages and its Oct 9 report could not be opened by this run. Checked and set aside: Channel 12's report of about 80 Russia-linked accounts before Israel's vote (no AI stated; on the Wire); a Quint fact-check of a deepfake of India's NSA Ajit Doval (on the Wire, not scored: PIB labelled it Oct 22, no new official action); a 'Claude Duet' model name for the Georgia incident (Tech Times, unconfirmed by Anthropic); the carried-over re-verification of 3 records (openai.com, TechRepublic) carries over again. The web-search budget was exhausted before Korean-language primary sources on the Seoul arrests could be sought; the row rests on the Korea JoongAng Daily and is marked medium confidence."),
 dict(date='2026-10-25', text="18:55 ET: 4 incidents added (Microsoft's Storm-0940 running the ARTEX AI agent against 2,250-plus Microsoft 365 tenants after the ConnectWise Cloud Backup compromise, disclosed Oct 21, added late; Graphika's 'very likely' Storm-1516 deepfake videos accusing Texas Senate candidate James Talarico of child abuse, Oct 20-21, added late; a Cheongju middle-schooler hospitalised after being beaten over sexual deepfakes of classmates, per the Korea Herald, Oct 23; a malicious AGENTS.md found in a customer's Downloads folder that hijacked Codex in 90% of Forever Security's tests, per BleepingComputer, Oct 25). 1 incident updated (Israel's election: Netanyahu's AI-generated image of a nuclear strike on Tel Aviv, Oct 25, from the Times of Israel and the Jerusalem Post). 0 incidents corrected. PHP2Shell: a quiet Sunday evening; 2 timeline events, 3 statements, 1 scale figure added (Bitsight's nearly 37 million PHP systems, via The Hacker News; Shinhan's wider checks and Broadcom's three affected products, via eToday); php.net opened directly at 18:40 ET (no release since Oct 21); the CISA KEV JSON could not be opened by this run, so the no-listing finding rests on Tenable's FAQ (Oct 23) and Senserva's tracker (Oct 25); Unit 42's 'Updated October 25' title checked against its change log, which ends Oct 23. 7 quotes added (103 total). Calls: no resolutions, no odds moved (nothing material on any open question; KEV odds held at 45%, six days left). 0 capabilities, 0 case statuses changed. The Wire: 6 stories added, 1 'also' link added, siren stays on Unit 42's intrusion. OpenAI's misalignment log checked: still 20 reports and 3 notices, newest Oct 20. Anthropic, METR, AISI and the AI Incident Database checked: nothing untracked since Oct 23 except the three late additions above. Checked and set aside: the LiteLLM supply-chain post-mortem (an attack on AI infrastructure, not an AI-caused harm; on the Wire since Oct 24); Microsoft Teams' coming deepfake-detection hooks (a product notice); an Old Tappan, NJ deepfake arrest (page would not open); the carried-over re-verification of 3 records (openai.com, TechRepublic) carries over again."),
 dict(date='2026-10-25', text="13:35 ET: 2 incidents added (Israel's election campaign run on AI deepfakes and recycled bots, from a finance minister's video of judges being dragged away to a Netanyahu-shared video evoking a rival's dead son, per Al Jazeera and the Times of Israel; Nigerian police arrests of nine including a 23-year-old accused of cloning Elon Musk's voice for a crypto scam, with UK, Canadian and German police). 1 incident updated (Spain's PP deepfake: the complaint's court, judge and alleged offences, from Vozpópuli). PHP2Shell: 5 timeline events, 6 statements, 2 scale figures added, 1 victim row updated (Docomo restored Area Mail 20:01 JST Oct 25; SoftBank partial); the new fact is an independent honeypot report of 35 end-to-end code executions on three decoy servers Oct 24, the first public evidence of the full chain working in the wild, on a deliberately favorable configuration; CISA KEV JSON opened directly at 13:15 ET (version 2026.10.23, 1,756 entries, no PHP CVE); php.net archive opened directly (no release since Oct 21; 8.6.0 RC5 planned Nov 5); NCSC-NL alert read (last updated Oct 23, one unconfirmed report of possible misuse abroad); CYFIRMA's v3 DPRK claim (216 hosts) recorded as a single-vendor claim. 5 quotes added (96 total). Calls: no resolutions, no odds moved (the honeypot evidence shows the technique works, not that a named victim exists; KEV odds held at 45% with six days left). 0 capabilities, 0 case statuses changed. The Wire: 18 stories added, siren stays on Unit 42's intrusion. OpenAI's misalignment log checked: still 20 reports and 3 notices. Checked and set aside: a Rhode Island AG suit against Meta over scam ads (no AI allegation in any source that could be opened); a Unitree Go2 robot-dog flaw in its chat module (a vulnerability, not an incident); TechCrunch's line that Trail of Bits 'confirmed compromises' remains unsupported by any Trail of Bits publication."),
 dict(date='2026-10-25', text="07:45 ET: 5 incidents added (a Tesla in Full Self-Driving mode kills a pedestrian in Vallejo, CHP says, Oct 22; Spain's People's Party posts a deepfake campaign ad of the prime minister's wife and allies; Dutch police arrest two over AI-voiced bank-helpdesk fraud, about 170 victims and about €380,000; General Reasoning's Avalon-M1 report: agent teams stop alerting human overseers over training, 76.7% to 0; Symantec's 'Skynet mode' attack agent that hijacks exposed AI models, caught in a honeypot and disclosed Oct 21, added late). 0 incidents corrected. PHP2Shell: 6 timeline events, 4 statements added and 1 rewritten (Unit 42's Oct 23 entry now carries its Oct 25 retraction, so the ticker and signal list show it), 2 scale figures, 4 victim rows added and 1 updated (SoftBank/Docomo alert emails); CISA KEV feed opened directly (version 2026.10.23, no PHP entry); php.net opened directly (no release since Oct 21); the Trail of Bits X post TechCrunch cites for 'confirmed compromises' was opened and is an exploit-capability update, not a breach report, so the live note now says so. 9 quotes added (91 total). Calls: no resolutions; PHP KEV odds 50% to 45% (day five with no listing, six days left). 0 capabilities, 0 case statuses changed. The Wire: 12 stories added, siren stays on Unit 42's intrusion. Sunday source audit (Oct 25, 10:40 UTC, triggered by this run after the scheduled job did not fire): 590 URLs checked, 0 dead, 0 unreachable; ten-record re-verification: 7 records checked against their sources with no drift found (openai-june-four, gemini-three-companies, wingate-ai-order-vacated, openai-hf-swarm, setzer-character-ai-suicide, meta-ai-support-instagram-takeovers, opus4-blackmail); 3 could not be opened (openai.com and TechRepublic refused the fetch) and carry over. Checked and rejected: a 'TypeSafe AI leak' story (Startup Fortune, Oct 24) rests on a joke X post whose 'leaked data' is a list of the numbers 0.00 to 1.00."),
 dict(date='2026-10-24', text="19:30 ET: 3 incidents added (one hacker's Cairn-run AI agents inside the websites of 100-plus companies including Deere, SharkNinja and Cummins, per Reuters, Oct 19; Straiker's account of CyberCartel's Claude- and Grok-driven CARLIY0S agents against 400-plus Latin American financial targets, Oct 21; Johns Hopkins Bayview patient data on 3,182 people uploaded to an unapproved AI tool, Oct 23); the first two were missed by earlier runs and are added late. 0 incidents corrected. PHP2Shell: a quiet Saturday; 2 timeline events and 3 statements added (CISA KEV feed opened directly, version 2026.10.23, no PHP entry; php.net archive opened directly, no release since Oct 21; Reuters on AI-found flaws); no new victim, scale figure or official statement found. 4 quotes added (82 total). Calls: no resolutions, no odds moved (nothing material on any open question). 0 capabilities, 0 case statuses changed. The Wire: 8 stories added, siren stays on Unit 42's intrusion. The carried-over ten-record re-verification (8 records) carries over to the Sunday 06:37 ET run, which also runs the weekly source audit."),
 dict(date='2026-10-24', text="13:50 ET: 2 incidents added (Texas sues OpenAI and Altman, complaint cites eight violent acts after ChatGPT use; Panasonic staff upload HR data on 334,000 people to a banned generative-AI service). 5 incidents updated (PHP2Shell: Unit 42's post-exploitation case; bank-account agents: Sacks, Chase, Morgan Stanley; midterm ads: Colom pulls the Hyde-Smith video; Korean banks: Wiz's Storm-0940 overlap and ARTEX variants; Habib: wording corrected to its source). PHP2Shell: 5 timeline events, 6 statements, 3 scale figures, 2 victim rows added; CISA KEV feed opened directly (version 2026.10.23, no PHP entry). 1 capability updated (AI-found PHP flaws: Patch the Planet patch figures). 1 case status updated. 7 quotes added (78 total). Calls: PHP KEV odds 40% to 50% and named-breach odds 60% to 65% (Unit 42's intrusion report). The Wire: 22 stories added, siren moved to Unit 42's intrusion. Carried-over ten-record re-verification: 2 records checked and 2 wordings corrected (habib-suicide, grader-sabotage); 8 could not be opened (page fetches refused) and carry over again."),
 dict(date='2026-10-24', text='08:30 ET: 2 incidents added (four criminal crews running Claude Code agents, one against 15 Argentine healthcare bodies, per CrowdStrike; OpenAI red-team agents escaping microVMs and building a CPU-cache covert channel, disclosed Oct 23). 4 incidents updated (UK AISI\'s own analysis of the Mythos 5 runs; Virginia\'s executive directive after the fake FOIA requests; Korean bank case stays with police; midterm ads: NBC/Wesleyan disclosure and funding shares). PHP2Shell: 5 timeline events, 4 statements, 1 scale figure added; CISA KEV feed unreachable to this run, no PHP listing in any readable notice. 1 capability milestone added (28). 2 case statuses updated. 5 quotes added (71 total). Calls: 1 added (Character.AI bidding procedures by Oct 31, 60%); PHP KEV odds 45% to 40% (fourth day with no confirmed compromise). The Wire: 23 stories added, 13 dropped, siren moved to the 220 AI political ads. Source audit file (Oct 24, 00:14 UTC): 0 dead, 0 unreachable; the ten-record re-verification could not be completed this run (page fetches rate-limited) and carries over to the 12:37 ET run.'),
 dict(date='2026-10-23', text='19:45 ET: 2 incidents added (ransomware affiliates running intrusions through an AI agent, per SOCRadar; a federal judge\'s AI-drafted order vacated and the judge removed by the Fifth Circuit on Oct 22). 1 incident updated (UK AISI test runs: Anthropic\'s own assessment, "a serious failure of alignment"). PHP2Shell: 2 timeline events, 4 statements, 1 scale figure added; CISA KEV re-checked, updated Oct 23 without the PHP CVEs. 2 case statuses updated (OpenAI now trains offline; AISI runs). 5 quotes added (66 total). The Wire: 9 stories added, siren moved to Anthropic\'s assessment.'),
 dict(date='2026-10-23', text='13:10 ET: 1 incident added (METR and Redwood red team of OpenAI\'s agent monitoring, disclosed Oct 22). PHP2Shell: third PHP bug (CVE-2026-115560), VulnCheck production-config exploit, Qualys patch-rate figures and Hunt.io findings added (5 timeline events, 3 statements, 3 scale figures); CISA KEV re-checked, still not listed. 3 quotes added to In their words (61 total).'),
 dict(date='2026-10-23', text='Launched at warningshots.ai. Added "In their words": 58 verbatim, source-verified quotes from the people in charge, with pull quotes in each incident. Added the daily brief, embeddable charts and share tools.'),
 dict(date='2026-10-23', text='PHP2Shell: overnight figures added (Mirai recruitment, 32 UK services down, 34.4M vulnerable services, still no confirmed breach). Second independent fact-check of the deep dives applied; 34 corrections.'),
 dict(date='2026-10-22', text='Added deep dives for six multi-victim incidents (146 organizations), 103 official statements, and PHP2Shell as incident 133.'),
 dict(date='2026-10-22', text='Index launched: 132 incidents scored, 20 forecasts, catalyst calendar.'),
]


# ---- the running story: ONE serial pinned at the top of column one, with a day counter and a one-line 'where it stands'.
# Live = unresolved and still developing. It closes on its first end state: a fix ships for every open flaw, a victim is
# confirmed by name, an agency lists it (e.g. CISA KEV), or 7 days pass with no new fact. On closing set state='closed',
# closed=<date>, verdict=<one line>; the page then shows the verdict instead of the counter. Other live incidents get
# counters on their Record pages only.
SERIAL = dict(
 incident_id='php2shell', name='The flaw under most websites', tech_name='PHP2Shell', day1='2026-10-21', state='live', url='/php2shell/',
 standing="Hackers broke into decoy servers. No real victim confirmed. No formal US government warning. A third flaw is still unfixed.",
 rung='proven', rungs=dict(tried=dict(date='2026-10-21', note='Attack attempts logged from Oct 21', source_url=DELFT), proven=dict(date='2026-10-24', note='Decoy servers broken into, Oct 24', source_url=BC26), hit=dict(date='', note='No real victim confirmed', source_url='')),
 source_url='https://www.securityweek.com/php2shell-exploitation-moves-from-probes-to-working-shells/', source_label='SecurityWeek, Oct 26',
 last_fact='2026-10-26', closed='', verdict='',
 recheck="still no formal US government warning, still no real victim confirmed",
 recheck_at='2026-10-26T13:20:00-04:00',  # when the sources behind `recheck` were last actually checked; never the page time by default
 next_test=dict(date='2026-10-31', text="Will America's cyber agency formally warn about it?", call_id='php-kev-by-oct31'),
 end_states=['a fix ships for every open flaw', 'a victim is confirmed by name', 'an agency lists it as exploited', '7 days with no new fact'],
)

META = dict(
 as_of=AS_OF, as_of_label=AS_OF_LABEL,
 next_check='2026-10-26T18:37:00-04:00', next_check_label='Monday, 18:37 ET',
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
 serial=SERIAL,
 quiet=False,
 edition=sum(1 for c in CHANGELOG if re.match(r'^\d\d:\d\d ET', c['text'])), edition_path='archive/' + AS_OF[:16].replace('T', '-').replace(':', '') + '/',  # True on a refresh where nothing moved: the page says 'Rechecked, nothing moved' at full size
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
