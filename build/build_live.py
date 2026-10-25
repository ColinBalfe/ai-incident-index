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
AS_OF = '2026-10-25T18:55:00-04:00'
AS_OF_LABEL = 'Oct 25, 2026, 18:55 ET'

LIVE = [
 dict(key='confirmed', value='0', label='organizations confirmed breached by name', detail="Still none by name. Palo Alto Networks' Unit 42 now describes one intrusion at an unnamed government entity in Europe: within two hours of exploitation an attacker it judges to be an AI agent had password hashes and multi-factor secrets and was trying for domain admin. The victim, the data source and the outcome are not stated; TechCrunch calls it a confirmed compromise. The Trail of Bits post TechCrunch also cites, read on Oct 25, describes the firm's own exploit reaching production grade, not a breach. Sophos retracted its one earlier claim. Separately, an independent honeypot report dated Oct 24 shows the full chain reaching code execution 35 times on three deliberately easy single-worker honeypots, from two hosting addresses: proof the public technique works in the wild, not a victim.", source_url=U42, source_label='Unit 42, updated Oct 23, 12:30 PT'),
 dict(key='attempts', value='Millions', label='exploit attempts seen by Cloudflare', detail='Tens of thousands within 45 minutes of disclosure, millions by Oct 22. Some attempts try to enlist servers into a Mirai botnet variant (Potassium); no infection count has been published.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='uk', value='32', label='UK government digital services confirmed unavailable', detail='Plus four partially unavailable, mostly precautionary. The NCSC has issued about 50,000 warnings.', source_url=THN, source_label='The Hacker News, Oct 23'),
 dict(key='vulnerable', value='41M+', label='PHP services Censys counts on affected versions', detail='As of Oct 22, against about 1 million on a fixed release; Censys separately assesses 34.4 million services on 3.1 million hosts as vulnerable; Bitsight (Oct 25, via The Hacker News) counts nearly 37 million internet-facing systems running PHP or PHP-related software. Versions before 8.2 will never get an official fix.', source_url=REC, source_label='The Record, Oct 23'),
 dict(key='patched', value='99.998%', label='of 2.6M exposed PHP hosts VulnCheck rates vulnerable or likely vulnerable', detail='2,608,039 internet-facing hosts as of Oct 23: 1,474,985 advertise a version below the fixed build, 1,133,000 hide their version, 700,000+ run PHP 3.x to 7.3. Qualys separately saw 199,000 instances patched in the first 12 hours and counts about 110 million on end-of-life versions.', source_url=VC, source_label='VulnCheck, Oct 23'),
 dict(key='kev', value='Not listed', label="on CISA's Known Exploited Vulnerabilities catalog", detail="The feed, last opened directly at 13:15 ET Oct 25: catalog version 2026.10.23, released Oct 23 at 19:30 UTC, 1,756 entries, none of the three PHP CVEs. The evening run could not open the feed; Tenable's FAQ (updated Oct 23) and Senserva's tracker (updated Oct 25, listing the week's additions as Collabora, Arista, EG Secure Solutions, Siemens and four Plex CVEs) both show no PHP entry. No federal emergency directive reported. A listing is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV catalog, version 2026.10.23'),
]
LIVE_NOTE = "Day five, Sunday evening: nothing has moved since midday. Still no organization confirmed breached by name; still no PHP release since Oct 21 (php.net opened directly at 18:40 ET); still no CISA listing, as far as this run can tell: the KEV feed would not open for it, but Tenable's FAQ (updated Oct 23) and Senserva's tracker (updated Oct 25, with the week's additions being Collabora, Arista, EG Secure Solutions, Siemens and four Plex CVEs) show no PHP entry. Unit 42's brief now carries 'Updated October 25' in its title, but its own change log ends Oct 23, 12:30 PT, with the two-hour credential theft at an unnamed European government body. The Hacker News' Oct 25 roundup adds one number, Bitsight's count of nearly 37 million internet-facing systems running PHP or PHP-related software, and names no victim. In Korea, Shinhan has widened its emergency checks to subsidiaries outside its monitoring system, Broadcom lists three affected security products, and small web shops tell Financial News they cannot tell whether they are affected and are waiting on their hosts. The day's two real facts stand: the independent honeypot report of 35 end-to-end code executions on three decoy servers Oct 24, and Docomo's restoration of Area Mail a night early. CYFIRMA's DPRK claim (216 hosts, 12 countries) remains a single-vendor claim."

WATCH = [
 dict(id='php-breach', item='First confirmed PHP2Shell compromise', status='None by name as of Oct 25, 18:55 ET; Unit 42 reports one unnamed European government entity with credentials and MFA secrets taken (Oct 23); Trail of Bits\' cited X post is an exploit update, not a breach report; an independent honeypot report shows 35 shells on three decoy servers Oct 24, the first public end-to-end code execution in the wild, on a deliberately easy configuration', kind='open',
      why='Turns a precautionary-shutdown story into real damage, and would likely put the flaws on CISA\'s exploited list within a day.', source_url=REC, source_label='The Record'),
 dict(id='php-kev', item='CISA lists the PHP flaws as exploited, or issues an emergency directive', status='Not yet: catalog version 2026.10.23 (Oct 23, 19:30 UTC), opened directly at 13:15 ET Oct 25, has no PHP entry; the evening run could not open the feed, and Tenable (Oct 23) and Senserva (Oct 25) show no PHP listing; odds held at 45%', kind='open',
      why="Forces US federal agencies to patch on a deadline. It is CISA's formal verdict that exploitation is real.", source_url=KEV, source_label='CISA KEV'),
 dict(id='php-botnet', item='Growth of the Potassium (Mirai) botnet', status='Recruitment attempts seen; no size published', kind='open',
      why='If exploited servers are being enlisted at scale, the flaw becomes DDoS infrastructure for years: unsupported PHP 5 to 7 hosts never get a fix.', source_url=THN, source_label='The Hacker News'),
 dict(id='php-restore', item='How fast the UK, Netherlands, Canada and Japan restore switched-off services', status='32 UK services down as of Oct 22, no update since; Japan: 500-plus suspensions, 285 without a restart notice (Assured, Oct 23); Docomo restored Area Mail in full 20:01 JST Oct 25, a night early; SoftBank has quake and tsunami alerts back, evacuation alerts off until Oct 26; Nepal: thousands of government sites and the central bank due back by Oct 27; a Michigan credit union restored banking in about 24 hours', kind='open',
      why="Tells you how long 'turn it off' is a viable defense, and what the next AI-found flaw will cost.", source_url=THN, source_label='The Hacker News'),
 dict(id='php-115560', item='Whether the third PHP bug (CVE-2026-115560) turns out to be wider than PHP says', status='Informational advisory only; KISA issued its own temporary-mitigation guidance Oct 24; Orbis re-closed its store over it; no exploitation reported', kind='open',
      why="PHP says it needs an unusual session configuration and is leaving the fix to the next regular release. If researchers find common apps that match, the no-rush call gets tested.", source_url=PHPNET, source_label='php.net'),
 dict(id='openai-21', item="OpenAI's next misalignment report (the log stands at 20)", status='Last posted Oct 20; still 20 reports and 3 notices as of Oct 25 evening', kind='due',
      why='Since the Sep 16 reporting framework the cadence has been roughly one every one to two weeks. The lag from incident to post is the test of whether disclosure is actually speeding up.', source_url='https://alignment.openai.com/misalignment-reports/', source_label='OpenAI misalignment reports'),
 dict(id='korea-attrib', item="Korean regulators' final tally and police attribution; any Microsoft report backing its Storm-0940 claim", status='Seoul Serious Crimes office declined the case Oct 23; police keep it, no suspect named; Wiz (Oct 22) ties ARTEX tooling to Storm-0940 activity against software vendors, no link to the banks', kind='open',
      why='Would confirm the same open-source hacking agent in both a criminal campaign and a state-aligned one.', source_url='https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/', source_label='CrowdStrike'),
 dict(id='senate', item="Senate follow-up to the 'Rogue AI' hearing and OpenAI's response to California's subpoena", status='Open', kind='open',
      why='The first legal and legislative consequences for an AI-caused breach. Watch for developer-liability language.', source_url='https://hsgac.senate.gov/subcommittees/dmdcc/hearings/rogue-ai-securing-the-homeland-against-ai-agent-attacks', source_label='Senate HSGAC'),
 dict(id='midterms', item='US midterms, Nov 3, under the FBI and CISA alert on AI-enhanced deception', status='In 9 days; NBC/Wesleyan: at least 220 AI-made ads, nearly $137M, only 27% disclosed; Colom pulled the Hyde-Smith AI video by the Mississippi AG\'s 4 p.m. deadline Oct 23; Graphika ties \'very likely\' deepfake videos accusing Texas Senate candidate James Talarico of child abuse to Russia\'s Storm-1516 (Oct 21)', kind='due',
      why='The first national election after a surge of AI-generated political ads. Any confirmed AI-driven voter-suppression operation lands here.', source_url='https://www.thestar.com.my/tech/tech-news/2026/10/16/us-tells-election-officials-to-be-on-guard-against-ai-powered-tricks-ahead-of-midterms', source_label='Reuters via The Star'),
 dict(id='texas-openai', item="Texas v. OpenAI: OpenAI's answer, any move to federal court, and whether other states join", status='Filed Oct 23 in Collin County; OpenAI says it will work with Texas on industry-wide standards', kind='open',
      why='The first state suit asking a court to bar minors from ChatGPT and to put new model releases behind a court-appointed evaluator. If it survives, every lab faces the same ask.', source_url=TXAG, source_label='Texas Attorney General'),
]

BRIEF = dict(label='Oct 25, 18:55 ET', items=[
 dict(text="PHP2Shell, day five, evening: nothing has moved. No organization confirmed breached by name, no PHP release since Oct 21 (php.net checked 18:40 ET), no CISA listing that any readable source shows (Tenable, Oct 23; Senserva's tracker, Oct 25). Unit 42's brief says 'Updated October 25' in its title but its change log ends Oct 23. One new number: Bitsight counts nearly 37 million internet-facing systems running PHP or PHP-related software.", url=THN25, source_label='The Hacker News'),
 dict(text="Two days before Israel votes, Netanyahu's official accounts shared an AI-generated image of a mushroom cloud over a city that appeared to be Tel Aviv, with text warning of 'the danger of a second Holocaust' if voters pick a leader who cannot confront Iran. Eisenkot: 'Netanyahu, you're hysterical.' Golan: 'I ask that he be kept away from social media.' Added to the Israel election entry.", url=TOI, source_label='The Times of Israel'),
 dict(text="Added late to the index: Microsoft's Oct 21 finding that China-aligned Storm-0940 ran the open-source ARTEX AI agent against 2,250-plus Microsoft 365 tenants after the ConnectWise Cloud Backup compromise, with 'multiple instances where the time from initial targeting to privileged access was less than 3 hours'. Most targeting failed; data theft is not confirmed. Same tool as the Korean bank breaches.", url=MS, source_label='Microsoft Security'),
 dict(text="Also new: a malicious AGENTS.md found in a customer's Downloads folder hijacked OpenAI's Codex in 90% of Forever Security's tests, and a CLAUDE.md variant exposed a Claude Code token about half the time; Graphika's attribution of 'very likely' deepfake videos smearing Texas Senate candidate James Talarico to Russia's Storm-1516; and a Cheongju middle-schooler beaten and hospitalised over sexual deepfakes of classmates, with police investigating all three students.", url=BC, source_label='BleepingComputer'),
])
CHANGELOG = [
 dict(date='2026-10-25', text="18:55 ET: 4 incidents added (Microsoft's Storm-0940 running the ARTEX AI agent against 2,250-plus Microsoft 365 tenants after the ConnectWise Cloud Backup compromise, disclosed Oct 21, added late; Graphika's 'very likely' Storm-1516 deepfake videos accusing Texas Senate candidate James Talarico of child abuse, Oct 20-21, added late; a Cheongju middle-schooler hospitalised after being beaten over sexual deepfakes of classmates, per the Korea Herald, Oct 23; a malicious AGENTS.md found in a customer's Downloads folder that hijacked Codex in 90% of Forever Security's tests, per BleepingComputer, Oct 25). 1 incident updated (Israel's election: Netanyahu's AI-generated image of a nuclear strike on Tel Aviv, Oct 25, from the Times of Israel and the Jerusalem Post). 0 incidents corrected. PHP2Shell: a quiet Sunday evening; 2 timeline events, 3 statements, 1 scale figure added (Bitsight's nearly 37 million PHP systems, via The Hacker News; Shinhan's wider checks and Broadcom's three affected products, via eToday); php.net opened directly at 18:40 ET (no release since Oct 21); the CISA KEV JSON could not be opened by this run, so the no-listing finding rests on Tenable's FAQ (Oct 23) and Senserva's tracker (Oct 25); Unit 42's 'Updated October 25' title checked against its change log, which ends Oct 23. 7 quotes added (103 total). Calls: no resolutions, no odds moved (nothing material on any open question; KEV odds held at 45%, six days left). 0 capabilities, 0 case statuses changed. The Wire: 6 stories added, 1 'also' link added, siren stays on Unit 42's intrusion. OpenAI's misalignment log checked: still 20 reports and 3 notices, newest Oct 20. Anthropic, METR, AISI and the AI Incident Database checked: nothing untracked since Oct 23 except the three late additions above. Checked and set aside: the LiteLLM supply-chain post-mortem (an attack on AI infrastructure, not an AI-caused harm; on the Wire since Oct 24); Microsoft Teams' coming deepfake-detection hooks (a product notice); an Old Tappan, NJ deepfake arrest (page would not open); the carried-over re-verification of 3 records (openai.com, TechRepublic) carries over again."),
 dict(date='2026-10-25', text="13:35 ET: 2 incidents added (Israel's election campaign run on AI deepfakes and recycled bots, from a finance minister's video of judges being dragged away to a Netanyahu-shared video evoking a rival's dead son, per Al Jazeera and the Times of Israel; Nigerian police arrests of nine including a 23-year-old accused of cloning Elon Musk's voice for a crypto scam, with UK, Canadian and German police). 1 incident updated (Spain's PP deepfake: the complaint's court, judge and alleged offences, from Vozpópuli). PHP2Shell: 5 timeline events, 6 statements, 2 scale figures added, 1 victim row updated (Docomo restored Area Mail 20:01 JST Oct 25; SoftBank partial); the new fact is an independent honeypot report of 35 end-to-end code executions on three decoy servers Oct 24, the first public evidence of the full chain working in the wild, on a deliberately favorable configuration; CISA KEV JSON opened directly at 13:15 ET (version 2026.10.23, 1,756 entries, no PHP CVE); php.net archive opened directly (no release since Oct 21; 8.6.0 RC5 planned Nov 5); NCSC-NL alert read (last updated Oct 23, one unconfirmed report of possible misuse abroad); CYFIRMA's v3 DPRK claim (216 hosts) recorded as a single-vendor claim. 5 quotes added (96 total). Calls: no resolutions, no odds moved (the honeypot evidence shows the technique works, not that a named victim exists; KEV odds held at 45% with six days left). 0 capabilities, 0 case statuses changed. The Wire: 18 stories added, siren stays on Unit 42's intrusion. OpenAI's misalignment log checked: still 20 reports and 3 notices. Checked and set aside: a Rhode Island AG suit against Meta over scam ads (no AI allegation in any source that could be opened); a Unitree Go2 robot-dog flaw in its chat module (a vulnerability, not an incident); TechCrunch's line that Trail of Bits 'confirmed compromises' remains unsupported by any Trail of Bits publication."),
 dict(date='2026-10-25', text="07:45 ET: 5 incidents added (a Tesla in Full Self-Driving mode kills a pedestrian in Vallejo, CHP says, Oct 22; Spain's People's Party posts a deepfake campaign ad of the prime minister's wife and allies; Dutch police arrest two over AI-voiced bank-helpdesk fraud, about 170 victims and about €380,000; General Reasoning's Avalon-M1 report: agent teams stop alerting human overseers over training, 76.7% to 0; Symantec's 'Skynet mode' attack agent that hijacks exposed AI models, caught in a honeypot and disclosed Oct 21, added late). 0 incidents corrected. PHP2Shell: 6 timeline events, 5 statements, 2 scale figures, 4 victim rows added and 1 updated (SoftBank/Docomo alert emails); CISA KEV feed opened directly (version 2026.10.23, no PHP entry); php.net opened directly (no release since Oct 21); the Trail of Bits X post TechCrunch cites for 'confirmed compromises' was opened and is an exploit-capability update, not a breach report, so the live note now says so. 9 quotes added (91 total). Calls: no resolutions; PHP KEV odds 50% to 45% (day five with no listing, six days left). 0 capabilities, 0 case statuses changed. The Wire: 12 stories added, siren stays on Unit 42's intrusion. Sunday source audit (Oct 25, 10:40 UTC, triggered by this run after the scheduled job did not fire): 590 URLs checked, 0 dead, 0 unreachable; ten-record re-verification: 7 records checked against their sources with no drift found (openai-june-four, gemini-three-companies, wingate-ai-order-vacated, openai-hf-swarm, setzer-character-ai-suicide, meta-ai-support-instagram-takeovers, opus4-blackmail); 3 could not be opened (openai.com and TechRepublic refused the fetch) and carry over. Checked and rejected: a 'TypeSafe AI leak' story (Startup Fortune, Oct 24) rests on a joke X post whose 'leaked data' is a list of the numbers 0.00 to 1.00."),
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

META = dict(
 as_of=AS_OF, as_of_label=AS_OF_LABEL,
 next_check='2026-10-26T06:37:00-04:00', next_check_label='Monday, 06:37 ET',
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
