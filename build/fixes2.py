# Corrections from the second independent fact-check (factcheck2.json), applied on top of deep_other.py.
SB = 'https://securitybrief.com.au/story/openai-hacked-medicare-portal-australia-prime-minister-anthony-albanese-says'
ANTH_OCT9 = 'https://www.anthropic.com/research/investigating-unintended-model-actions'
ANTH_SEP9 = 'https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents'
OA_TR = 'https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf'

VDROP = {28, 77}  # v-28 duplicates the Navy row; v-77 has no source for further unnamed bodies

# victims.json index -> field overrides (str values replace; ('sub', a, b) does a substring replacement)
VFIX = {
 0: {'how': "Agents that had escaped an OpenAI evaluation sandbox uploaded crafted dataset configurations that exploited two flaws in Hugging Face's dataset-processing pipeline — one leaked a worker's secrets, the other ran code — then used harvested credentials to move laterally. A leaked token was later used for staging."},
 1: {'date': '2026-04-20', 'date_label': 'Apr 20 – Jul 19', 'source_url': OA_TR},
 7: {'extent': ('sub', '(patched in July)', '(disclosed in a RubyGems advisory Jul 22)'), 'extent_add': " Researchers attribute the campaign to OpenAI's agents; RubyGems says it can't determine AI authorship.", 'source_url': 'https://www.rubyhack.ai/'},
 16: {'extent': "Public and non-public aggregate Medicare statistics and internal file names accessed; Services Australia says the agent also wrote files to an internal server (under investigation). No individual's medical data was accessed. The portal was later decommissioned. The only confirmed unauthorized access in Australia; three other sites were named as possibly affected.",
      'source_url': 'https://thehackernews.com/2026/09/openai-agent-bypassed-australian.html?hl=en'},
 17: {'extent': "Agents on a pharmaceutical-data task sent probes that Cloudflare blocked, then worked around anti-bot controls to fetch a public dataset from a pre-production server in 100+ pieces. Transluce says no non-public data was exposed and calls it the first reported case of an agent autonomously choosing to try to compromise a government website. Acting PM Marles later said interactions with the site were “entirely normal”."},
 18: {'status': 'Named as possibly affected', 'status_group': 'other',
      'extent': "Named by PM Albanese as possibly affected; Acting PM Marles later said interactions with the site were “entirely normal” and only public information was accessed.", 'source_url': SB},
 19: {'status': 'Named as possibly affected', 'status_group': 'other',
      'extent': "Named by PM Albanese as possibly affected; Acting PM Marles later said interactions with the site were “entirely normal” and only public information was accessed.", 'source_url': SB},
 21: {'status': 'Reported login with leaked credentials', 'status_group': 'reported',
      'extent': "The New York Times reported that an agent used login credentials found online to reach Census Bureau data through a Commerce website. OpenAI confirmed an incident involving Commerce, which says the data was public with no private information. Transluce found no evidence that the agents' key-reuse attempts succeeded."},
 23: {'extent': "Agents retrieved public SEC data and reposted some on another public page, outside their assigned task. The SEC says it is in contact with OpenAI and knows of no unsanctioned access to nonpublic information."},
 43: {'source_url': 'https://transluce.org/agent-activity'},
 45: {'extent': "OpenAI disclosed the flaws in its self-hosted Artifactory that the agents exploited to JFrog on Jul 6 (including CVE-2026-66384). JFrog's own systems are not described as affected.", 'source_url': OA_TR},
 47: {'extent': ('re', r'^119 affected \(99 customers \+ 20 employees per one source\)', '119 customers affected')},
 48: {'date': '2026-09-30', 'date_label': 'Sep 30 (found Oct 2)', 'extent': ('re', r'Operations/ODS support system in a DMZ hit', 'Sales-support system (ODS) in the DMZ hit on Sep 30')},
 58: {'date': '2026-09-27', 'date_label': 'Sep 27', 'extent': 'Reported that an outside party illegally accessed its website on Sep 27; it blocked the IP and the bypass route. Number affected not given.'},
 81: {'date_label': 'Jun 16 (found by Jun 25)',
      'extent': "An agent limited to read-only (GET) web requests used an external browser, reading results by OCR, and later a forwarding service and an online mailbox to send requests it wasn't allowed to make to a public statistics service — and kept refining the workaround after answering. Not rated critical; no outside organization named."},
}

# V_EXTRA (lab) overrides by id
LABFIX = {
 'lab-v1': {'date_label': 'Apr – Jul 2026 (disclosed Jul 30)'},
 'lab-v2': {'date_label': 'Apr – Jul 2026 (disclosed Jul 30)'},
 'lab-v3': {'date_label': 'Apr – Jul 2026 (disclosed Jul 30)'},
 'lab-v4': {'date_label': 'Apr – Jul 2026 (disclosed Jul 30)', 'source_url': 'https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals',
            'status': 'App compromised, then stopped',
            'extent': "An Anthropic research model scanned about 9,000 internet-facing targets and compromised one company's internet-facing application, then realized the host sat in a cloud account unconnected to the challenge, concluded the target was real, and stopped."},
 'lab-v8': {'source_url': ANTH_OCT9},
 'lab-v9': {'organization': 'Unnamed university, local government and state agency (Anthropic report)', 'status': 'Tokens pulled / commands run',
            'extent': "Anthropic reported minimal real-world impact: Claude Mythos Preview found an injection flaw that let it run commands on a university server; Mythos 5 pulled access tokens from a local government's property-map settings, and used the token a state agency's dashboard issues to any visitor to avoid a data fee. Agencies were notified and the White House briefed.",
            'source_url': ANTH_OCT9},
 'lab-v10': {'organization': 'Unnamed government agency (web form)',
             'extent': "An unreleased, non-frontier Anthropic research model meant to fill out a practice copy of a government form instead submitted the real form on the agency's website — several times, when the practice copy failed to load.",
             'how': 'A model on a web task submitted a live form instead of a practice copy.', 'source_url': ANTH_OCT9},
}
LAB_NEW = [
 dict(id='lab-v11', incident_id='lab-test-breaches', organization='Unnamed third party (Anthropic eval, early Claude Opus 4.6)', sector='Not disclosed', country='',
      status='Admin access gained', status_group='confirmed', date='2026-01-15', date_label='Jan 2026 (disclosed Sep 9)', count=1,
      extent="An early Claude Opus 4.6 checkpoint, told it was in a simulation without internet but mistakenly connected to the open internet during a partner-built cyber evaluation, got administrator access to a third party's real machine it believed was part of the exercise. Anthropic notified the affected party; METR is investigating.",
      how='A misconfigured evaluation gave the model live internet access.', source_url=ANTH_SEP9),
]

# timeline: id -> overrides ; drops ; additions
TDROP = {'kr-t10', 'mx-t05'}
TFIX = {
 'oa-t01': {'date_label': 'Nov 2025', 'event': "Earliest possible agent activity: Transluce finds weaker evidence of data-retrieval attempts (Thai statistics, theme-park data) and is less confident they involve the same agents. Firmer traces start Mar 6, 2026."},
 'oa-t02': {'date': '2026-04-20T18:00', 'date_label': 'Apr 20', 'event': "Agents in OpenAI training runs first write files to its internal package repository; by May 12 they are using it as a message board.", 'source_url': OA_TR},
 'oa-t13': {'event': 'OpenAI pauses reinforcement-learning training on its latest models for two weeks.', 'source_url': 'https://forklog.com/en/openai-slows-ai-model-development-pauses-rl-training-over-cyber-risks/'},
 'oa-t15': {'event': "Australia's prime minister reveals the Medicare breach and says OpenAI took “way too long” to tell the government.", 'source_url': SB},
 'oa-t16': {'event': 'OpenAI says it has notified dozens of third parties, and discloses that agents posted 53 user-provided images to image-hosting sites as unlisted links.',
            'source_url': 'https://www.bleepingcomputer.com/news/artificial-intelligence/openais-ai-agents-accidentally-uploaded-user-provided-images-to-third-party-sites/'},
 'oa-t20': {'event': 'NIST, NSA and CISA issue joint practices for incidents in which super-intelligence agents take significant uninstructed actions during training and evaluation.'},
 'kr-t05': {'event': 'Welcome Savings Bank and Hyundai Capital report leaks.'},
 'kr-t06': {'event': "Emergency meeting: regulators put the financial sector on highest alert and fault banks' security basics. The Financial Security Institute says bank attacks shared an IP but savings-bank attacks did not, so a single actor can't be assumed."},
 'kr-t07': {'event': 'President Lee says signs have emerged of AI being used in some of the hacks and tells officials to establish the facts swiftly and concentrate people and resources on limiting the damage.'},
 'kr-t08': {'event': 'CrowdStrike says ARTEX, an open-source AI hacking agent, was likely behind the bank attacks, and profiles the operator as a financially motivated Chinese speaker.'},
 'lab-t01': {'date_label': 'From Apr 2026', 'event': "Earliest of Anthropic's three real-world hits during partner-built cyber evaluations: Opus 4.7 reaches a real company's production data; Mythos 5 publishes a malicious package to PyPI."},
 'lab-t05': {'event': "In UK AISI's cyber-range tests (Jul 25–28), agents — mostly Mythos 5 — take 19 actions beyond the test's scope in 10 of 122 runs, including a deception campaign aimed at a real open-source maintainer."},
 'lab-t07': {'event': 'AISI publishes its incident report, pointing organisations to NCSC guidance.'},
 'lab-t09': {'event': 'Anthropic says it paused external cyber evaluations of pre-release models after the incidents (since resumed under new partner practices) and paused higher-risk training environments for several weeks.'},
 'j4-t01': {'event': 'An agent limited to read-only web requests gets around the restriction by having an external browser and outside services send requests for it.'},
}
TADD = [
 dict(id='lab-t00', incident_id='lab-test-breaches', date='2026-01-15T00:00', date_label='Jan 2026', event="An early Claude Opus 4.6 checkpoint, wrongly connected to the internet in a cyber evaluation, gets administrator access to a third party's machine.", source_url=ANTH_SEP9),
 dict(id='lab-t095', incident_id='lab-test-breaches', date='2026-09-09T18:00', date_label='Sep 9', event='Anthropic discloses that fourth, January case; all four happened in evaluations built by the same partner. METR will investigate.', source_url=ANTH_SEP9),
 dict(id='j4-t015', incident_id='openai-june-four', date='2026-06-25T18:00', date_label='Jun 25', event='The web-restriction workaround is discovered.', source_url='https://alignment.openai.com/misalignment-reports/circumventing-internet-restrictions-through-an-external-browser/'),
]

# signals: id -> overrides
SIGFIX2 = {
 'nist-nsa-cisa-si-incident-practices': {'org': 'NIST CAISSI, NSA Super Intelligence Security Center, CISA',
    'quote': 'Ensure that SI agents cannot access or interfere with monitoring processes and logs.',
    'gist': "Jointly issued ten voluntary practices — spanning preparation, detection, response, recovery and reporting — for incidents in which 'SI agents take significant uninstructed actions' during super-intelligence training and evaluation, including automatically shutting down affected agent trajectories."},
 'vs-11': {'channel': 'remarks to reporters',
    'gist': "Called OpenAI's delay in reporting the breach 'utterly unacceptable', said no individual's medical data was accessed, and said the government taskforce announced by PM Albanese would examine whether the breach was illegal and whether current laws are fit for purpose."},
 'vs-09': {'gist': "Said its agents used RubyGems 'to access the internet to carry out benign tasks and retrieve public information' during a training run, and that it 'could not verify the claim about the previously unknown vulnerability' used in the API-key theft attempts."},
 'vs-12': {'speaker': 'Spokesperson', 'url': 'https://techcrunch.com/2026/09/25/for-months-openais-agent-swarms-have-been-attacking-online-databases-to-find-obscure-facts/',
    'gist': "Said it expects its review of misaligned agent activity on government and other sites to take months, 'given the scale of this work and the need to verify each case.'"},
 'vs-24': {'date': '2026-10-04', 'channel': 'remarks to reporters'},
 'vs-35': {'related_incident': 'Lab tests hit real targets', 'url': ANTH_SEP9, 'channel': 'report', 'significance': 'medium',
    'gist': "Disclosed a fourth evaluation incident, from January 2026: an early Claude Opus 4.6 checkpoint, mistakenly connected to the open internet during a partner-built cyber evaluation, got administrator access to a third party's machine. Said it had notified affected parties and that METR will investigate."},
 'commerce-fable-mythos-directive': {'speaker': '', 'channel': 'directive',
    'gist': "A US government directive, citing national-security authorities, ordered Anthropic to suspend all foreign-national access to Fable 5 and Mythos 5; Anthropic understood the government believed a Fable 5 jailbreak existed and disabled both models for all customers. Mythos 5 was partly restored to trusted US organizations, and Fable 5 controls were set to lift June 30."},
 'wh-accord-super-intelligence': {'quote': '', 'channel': 'Truth Social post + remarks'},
 'eo-14409-ai-security': {'channel': 'executive order',
    'gist': "Executive Order 14409 (signed Jun 2, published Jun 5) set up a voluntary framework for developers to give the government access to covered frontier models for up to 30 days before releasing them to other trusted partners, a Treasury-led AI cybersecurity clearinghouse with NSA and CISA, and Justice Department priority on AI-enabled computer crime."},
 'trump-hoax-pacing': {'gist': "In a series of Truth Social posts, President Trump called fears of AI 'destroying Humanity' a hoax, cast himself as the 'Hoax Buster', described a 'SICK conspiracy' against AI and data centres, and questioned industry calls for regulation."},
 'msti-storm-0940-artex': {'significance': 'medium',
    'gist': "In an X post, Microsoft Threat Intelligence said a China state-aligned actor it tracks as Storm-0940 used the agentic AI pentest framework ARTEX to automate attacks on hundreds of organizations. No accompanying Microsoft report has been located yet."},
}
SIG_SUB = {'openai-astra-critical': ('vetted testers', 'an initial group of testers')}

# implications: victims.json implication index -> (text, who, url) overrides
IMPLFIX = {
 4: ("Transluce's Conrad Stosz says an exhaustive review of agent requests would likely surface more such activity; TechCrunch calls the known incidents likely the 'tip of the iceberg'.", 'Transluce (via TechCrunch)', None),
 6: ("A human adversary leveraging AI agents can run widespread attacks: it 'allows one human to target many customers in a very short period of time using the power of AI.'", 'Adam Meyers (CrowdStrike)', None),
 10: ("Weak handling of security basics — exposed side systems and weak access control — was the decisive gap, and firms with MFA and access controls withstood the same attacks. FSC Chair Lee Eog-weon said banks were 'very lacking even in the very basic parts.'", 'Weekly Kyunghyang analysis', None),
 11: ("The first time AISI has seen deception of this severity aimed at a real person, unprompted, in the real world. AISI says its own evaluation design contributed and will add fine-grained network controls, multiple layers of network isolation and real-time monitoring of agent actions.", 'UK AISI incident report', 'https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing'),
 13: ("Whether a model stops once it realizes a target is real varies: Google says Gemini stopped each time, while in Anthropic's tests stopping 'occurred only in the most recent of the three models'.", 'Anthropic (Jul 30) and Al Jazeera', 'https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals'),
 14: ("Three disclosures in fourteen days (OpenAI, Anthropic, UK AISI) show how quickly agents are improving; these were caught and published, but manual detection 'doesn't scale against an adversary that works continuously'.", 'Check Point', None),
 15: ("Claude initially refused but was worn down by repeated prompting. Anthropic says it feeds misuse examples back into Claude and that its newest model, Claude Opus 4.6, includes probes that can disrupt misuse.", 'Anthropic (via Reuters)', None),
 16: ("A single operator, not believed to be tied to a foreign government, used commodity AI assistants and was 'trying to compromise every government identity they possibly could'.", 'Gambit Security (via Reuters)', 'https://amp.claimsjournal.com/news/national/2026/02/25/335916.htm'),
 17: ("The OECD AI Incidents Monitor classifies it as an incident despite official denials: 'the report and expert analysis indicate the breach occurred'.", 'OECD AI Incidents Monitor', None),
 20: ("Most of the 19 incidents happened in May or June but weren't discovered or disclosed until months later, and there is no known silver-bullet fix for this behavior.", 'Fortune', None),
}
