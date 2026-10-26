# Deep-dive narrative text (this index's own words, drawn from the cited research files).
DEEPDIVES = [
 dict(incident_id='php2shell', order=1, status='active', tab_label='PHP2Shell (live)',
      name='PHP2Shell: the AI-found flaw under 70% of the web',
      status_label='Active · attacks ongoing',
      dates_label='Found Aug 2026 · first attack Oct 17 · leaked Oct 20 · patched Oct 21',
      signal_tag='PHP2Shell',
      now_text='AI-found flaws in PHP leaked before the patch. Millions of attack attempts, a botnet already trying to ride on it, and governments in a dozen-plus countries pulled services offline. Still no confirmed breach — every named organization tracked here.',
      hook="Japan's prime minister told every website operator in the country to patch or switch off, on X, at night, before the fix was out. Then AI-written exploits appeared within hours and no one was hacked anyway.",
      one_liner="Researchers at Wiz, Calif and OpenAI used frontier AI to find and weaponize flaws in PHP's core that let anyone take over a server running almost any PHP version of the last decade — and PHP runs about 70% of websites. Details leaked before the coordinated patch, a probe hit Amazon's sensors four days early, and governments from the Netherlands to Japan switched off public services rather than wait.",
      how="Two memory-safety flaws in PHP itself (CVE-2026-109618 and CVE-2026-109619) let an attacker take over a server with crafted web requests — no login needed — and leave almost no trace beyond a memory error in a log. They sit beneath WordPress, Drupal and every other PHP app, so a secure app doesn't help. The bug IDs, a proof-of-concept video and other details leaked a day early; one vendor shipped fixed images hours before the agreed time.",
      ai_role="AI found it and made it exploitable. Calif first spotted the flaw with OpenAI's GPT-5.6 Sol; Wiz independently used Gemini 4 Argon and GPT-5.6 Sol to find the bugs and chain them into working attacks — work it says once would have taken a team months. After the leak, defenders built working exploits in under a day. There is no evidence yet that attackers used AI.",
      damage="No organization has confirmed a breach, one vendor retracted its claim of one, and researchers who watched the first two days say reliable exploitation is harder than the leak implied. The damage so far is disruption: national login systems, banks, airlines, a payroll platform and government sites in more than a dozen countries went offline as a precaution; the UK alone confirms 32 digital services unavailable. The first malware is already riding on it: a Mirai botnet variant is trying to enlist exploited servers. Censys still counts 34.4 million vulnerable PHP services, and versions before 8.2 will never get an official fix.",
      why="It is the first time an AI-discovered bug pushed governments to switch off public services pre-emptively. The gap between a patch and a working exploit has shrunk to hours, and secrecy-based disclosure looks fragile when several labs' AIs can find the same bug. The counterintuitive lesson so far: the biggest AI-security event of the year has hurt nobody by hacking. It hurt by making everyone turn things off.",
      scale_value='2.6M', scale_label='internet-facing PHP hosts, nearly all vulnerable before patching (VulnCheck)'),
]

# index in php2shell.json timeline -> replacement text ('' keeps the original)
PHP_TIMELINE_KEEP = {
 0: "A PHP out-of-memory flaw is found but left unpatched because exploitation wasn't proven.",
 1: "The same memory issue resurfaces in an external PHP audit; the PHP Foundation later calls the delay a structural failure.",
 3: "Calif finds the first issue using OpenAI's GPT-5.6 Sol under OpenAI's 'Patch the Planet' program.",
 4: "Calif and OpenAI report the out-of-memory-to-takeover issue.",
 5: "Wiz independently discovers the first bug with AI assistance.",
 8: "Wiz reports its findings to the PHP security team.",
 9: "PHP acknowledges the reports and starts a coordinated fix.",
 11: "The White House says it learned of the flaw on this day.",
 12: "First known attack: a single probe hits Amazon's honeypots from anonymized infrastructure, four days before disclosure.",
 13: "watchTowr publicly confirms the rumored flaws are real, without publishing details.",
 15: "A pseudonymous Hacker News post leaks details ahead of the planned disclosure.",
 16: "The two CVE IDs start circulating online, with a wrong release time and an inflated severity score.",
 17: "PHP moves the release up a day, to Oct 21.",
 18: "Calif mistakenly publishes a proof-of-concept video; copies spread on social media.",
 19: "First proof-of-concept attacks appear, from several anonymized sources.",
 22: "Cloudflare switches on firewall protections for all plans, about nine hours before disclosure.",
 24: "Chainguard publishes fixed images six hours early; the PHP Foundation says this broke the embargo (Chainguard disputes it).",
 26: "Japan's Prime Minister Takaichi posts on X urging site operators to patch.",
 29: "PHP ships fixed releases and the flaws are publicly disclosed.",
 30: "UK NCSC urges immediate updates.",
 31: "CISA says the flaws require immediate patching; it has not yet seen exploitation.",
 33: "Governments and companies in Europe, Canada, Japan, Australia and the UK take sites offline as a precaution.",
 34: "Slovenia raises its national cyber threat level to high.",
 35: "OpenAI publishes its 'Patch the Planet' post and a free PHP checker.",
 36: "Hundreds of proof-of-concept repositories appear on GitHub, most fake — some carrying malware.",
 37: "Major Linux distributions, control panels and Docker images ship fixes.",
 40: "Pantheon reports blocking more than 60,000 suspicious requests.",
 41: "South Korea raises its private-sector cyber alert to 'caution' and warns about 28,000 organizations.",
 42: "VulnCheck confirms a working exploit against default production settings of a widely used PHP 8.4 build.",
 44: "Sophos retracts its claim of one successful compromise; officials in Germany, the Netherlands, Japan and Australia report no confirmed breaches.",
 45: "Cloudflare's CEO says exploit attempts have reached the millions.",
}

EXTRA_TIMELINE = [
 dict(id='php-t-uk32', incident_id='php2shell', date='2026-10-22T20:00', date_label='Oct 22', event='The UK government confirms 32 digital services unavailable and four partially unavailable, mostly as a precaution; the NCSC has sent about 50,000 warnings.', source_url='https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'),
 dict(id='php-t-mirai', incident_id='php2shell', date='2026-10-23T09:00', date_label='Oct 23', event='Attackers try to use the flaws to recruit servers into a Mirai botnet variant (Potassium). Previdian, SOCRadar, Wordfence and Hunt.io still report no successful exploitation; VulnCheck shows a working chain against a default production build.', source_url='https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'),
 dict(id='php-t-censys', incident_id='php2shell', date='2026-10-23T10:00', date_label='Oct 23', event='Censys counts 34.4 million PHP services still assessed as vulnerable across about 3.1 million hosts.', source_url='https://thehackernews.com/2026/10/php2shell-exploit-attempts-hit-millions.html'),
 dict(id='php-t-kev', incident_id='php2shell', date='2026-10-23T10:30', date_label='Oct 23', event="Neither flaw is yet on CISA's Known Exploited Vulnerabilities list, and no federal emergency directive has been issued.", source_url='https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'),
 dict(id='php-t-qualys', incident_id='php2shell', date='2026-10-23T11:00', date_label='Oct 23', event='Qualys, from about 12,000 customers, counts only about 199,000 PHP instances patched within 12 hours of disclosure; about 110 million (71%) run end-of-life versions that will mostly never get a fix.', source_url='https://www.securityweek.com/mirai-botnet-operators-join-php2shell-attacks-as-aslr-bypass-exploits-emerge/'),
 dict(id='php-t-vulncheck-prod', incident_id='php2shell', date='2026-10-23T11:30', date_label='Oct 23', event='VulnCheck says it has an exploit that works against the recommended production configuration on x86-64, kept to its paying customers, and knows of no other public or commercial exploit that does so across PHP versions. Hunt.io, Wordfence and SOCRadar still report no confirmed compromise.', source_url='https://www.securityweek.com/mirai-botnet-operators-join-php2shell-attacks-as-aslr-bypass-exploits-emerge/'),
 dict(id='php-t-cve115560', incident_id='php2shell', date='2026-10-23T12:00', date_label='Oct 23', event="PHP flags a third, narrower code-execution risk (CVE-2026-115560) that needs an unusual session configuration. It recommends disabling session upload progress and will fix it in the next regular release; no exploitation reported.", source_url='https://www.php.net/archive/2026.php#2026-10-23-1'),
]

EXTRA_TIMELINE += [
 dict(id='php-t-msufcu', incident_id='php2shell', date='2026-10-23T12:18', date_label='Oct 23', event="A Michigan credit union, MSUFCU, becomes the first US financial institution to describe its own precautionary outage: digital banking offline about 24 hours to patch in-house PHP systems, no impact to member data. New York's financial regulator tells firms to patch at once and not rely on web firewalls.", source_url='https://www.americanbanker.com/news/banks-dodge-early-damage-from-php2shell-flaws'),
 dict(id='php-t-unit42', incident_id='php2shell', date='2026-10-23T15:30', date_label='Oct 23', event="Palo Alto Networks' Unit 42 gives the first vendor account of a successful intrusion: at an unnamed European government entity, an attacker it judges to be an AI agent had password hashes and multi-factor secrets within two hours of exploitation and tried for domain admin. The victim, the data source and the outcome are not stated. Retracted by Unit 42 on Oct 25 (2:15 p.m. PT): it could not confirm the initial access involved the PHP2Shell flaws.", source_url='https://unit42.paloaltonetworks.com/cve-2026-109618-cve-2026-109619/'),
 dict(id='php-t-barron', incident_id='php2shell', date='2026-10-23T18:00', date_label='Oct 23', event="The PHP Foundation tells Reuters it has one full-time employee and 14 mostly part-time contractors, and no evidence the flaws were exploited before disclosure or against patched servers.", source_url='https://whtc.com/2026/10/23/php-foundation-under-funded-with-one-full-time-staff-member-director-says/'),
 dict(id='php-t-kev-oct24', incident_id='php2shell', date='2026-10-24T12:40', date_label='Oct 24', event="CISA's catalog, opened directly: version 2026.10.23, no PHP entry, no emergency directive. No PHP release since Oct 21. Korean press relays a CYFIRMA report, at moderate confidence, of Korean-speaking actors preparing attacks on banks and government in four countries.", source_url='https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'),
]

EXTRA_IMPL = []
