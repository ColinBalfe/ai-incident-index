import json, os, re, sys, datetime
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(__file__))
from scores_decjun import SCORES as DJ, MERGE
from lab_entries import LAB
from aux_data import FORECASTS, PIPELINE, DRIVERS, CONTEXT, CATALYSTS, HORIZON
try:
    from scores_early import SCORES as EARLY
except ImportError:
    EARLY = {}

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'research')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(OUT, exist_ok=True)

CAT = {
 "fraud_deepfake": "Deepfakes & fraud",
 "cyber_offense": "AI-powered cyberattacks",
 "agent_accident": "Agent accidents",
 "misalignment_lab": "Misalignment in testing",
 "misalignment_wild": "Rogue AI behavior",
 "psych_harm": "Mental health & violence",
 "child_safety": "Child safety",
 "info_integrity": "Elections & misinformation",
 "security_vuln": "AI security flaws",
 "capability_threshold": "Capability thresholds",
 "privacy_data": "Privacy & data leaks",
 "physical_autonomy": "Robotaxis & physical AI",
 "governance_shock": "Oversight failures",
 "ai_vuln": "AI-found vulnerabilities",
}

from util import LABELS, label_for

def norm_date(d, precision=None):
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d): return d, precision or 'day'
    if re.fullmatch(r'\d{4}-\d{2}', d): return d + '-15', 'month'
    raise ValueError('bad date ' + d)

rows = []
def add(r):
    for k in ['H', 'R', 'A', 'N', 'I']:
        r[k] = int(r[k])
    assert 0 <= r['H'] <= 5 and 0 <= r['R'] <= 5 and 0 <= r['A'] <= 4 and 0 <= r['N'] <= 5 and 0 <= r['I'] <= 5, r['id']
    r['date'], r['date_precision'] = norm_date(r['date'], r.get('date_precision'))
    r['category_label'] = CAT[r['category']]
    r.setdefault('setting', 'lab' if r['category'] in ('misalignment_lab', 'capability_threshold') else 'wild')
    r.setdefault('source_label', label_for(r['source_url']))
    r.setdefault('source2_url', '')
    r.setdefault('source3_url', '')
    r.setdefault('disclosed', '')
    r.setdefault('confidence', 'high')
    r.setdefault('notes', '')
    rows.append({k: r.get(k, '') for k in ['id', 'date', 'date_precision', 'disclosed', 'title', 'actors', 'category', 'category_label', 'setting', 'summary', 'harm', 'H', 'R', 'A', 'N', 'I', 'source_url', 'source_label', 'source2_url', 'source3_url', 'confidence', 'notes']})

# --- Jul–Oct 2026 (own research) with primary-source upgrades
jo = json.load(open(f'{R}/jul_oct_2026_mine.json'))
upg = {
 'openai-hf-swarm': ('https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/', 'METR investigation', 'https://www.darkreading.com/cyberattacks-data-breaches/hundreds-openai-agents-invaded-hugging-face-servers'),
 'openai-june-four': (None, None, 'https://alignment.openai.com/misalignment-reports/retrieving-server-secrets-and-bypassing-authorization-on-a-government-statistics-website/'),
 'aisi-real-targets': ('https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing', 'UK AI Security Institute', 'https://labs.cloudsecurityalliance.org/research/csa-research-note-aisi-evaluation-containment-incident-20260/'),
}
drop_jo = {'openai-six-sept'}  # replaced by lab entry 'sol-self-jailbreak' (same disclosure, dated by occurrence)
for r in jo:
    if r['id'] in drop_jo: continue
    if r['id'] in upg:
        u, l, u2 = upg[r['id']]
        if u: r['source_url'], r['source_label'] = u, l
        if u2: r['source2_url'] = u2
    if r['id'] == 'aisi-real-targets': r['confidence'] = 'high'
    add(dict(r))

# --- Dec 2025 – Jun 2026 (research agent) with factor ratings
dj = {x['id']: x for x in json.load(open(f'{R}/dec2025_jun2026.json'))}
for i, s in DJ.items():
    x = dict(dj[i])
    src = x.get('sources') or []
    r = dict(id=i, date=s.get('date', x['date']), date_precision=s.get('date_precision'), disclosed=x.get('disclosed') or '',
             title=s.get('title', x['title']), actors=x.get('actors', ''), category=s.get('category', x['category']),
             setting=x.get('setting', 'wild'), summary=s.get('summary', x['summary']) + s.get('summary_add', ''),
             harm=s.get('harm', x.get('harm', '')), H=s['H'], R=s['R'], A=s['A'], N=s['N'], I=s['I'],
             source_url=src[0], source2_url=src[1] if len(src) > 1 else '', confidence=x.get('confidence', 'high'),
             notes=(x.get('notes') or '') + s.get('notes_add', ''))
    if r['category'] in ('capability_threshold', 'misalignment_lab'): r['setting'] = 'lab'
    add(r)

# --- Lab findings and thresholds
for e in LAB:
    add(dict(e))

# --- 2023–2025 (research agent) with factor ratings
if os.path.exists(f'{R}/2023_2025.json') and EARLY:
    ea = {x['id']: x for x in json.load(open(f'{R}/2023_2025.json'))}
    for i, s in EARLY.items():
        if i.startswith('_new_'):
            add(dict(s)); continue
        x = dict(ea[i])
        src = x.get('sources') or []
        r = dict(id=i, date=s.get('date', x['date']), date_precision=s.get('date_precision'), disclosed=x.get('disclosed') or '',
                 title=s.get('title', x['title']), actors=x.get('actors', ''), category=s.get('category', x['category']),
                 setting=s.get('setting', x.get('setting', 'wild')), summary=s.get('summary', x['summary']) + s.get('summary_add', ''),
                 harm=s.get('harm', x.get('harm', '')), H=s['H'], R=s['R'], A=s['A'], N=s['N'], I=s['I'],
                 source_url=s.get('source_url', src[0]), source2_url=s.get('source2_url', src[1] if len(src) > 1 else ''),
                 confidence=x.get('confidence', 'high'), notes=(x.get('notes') or '') + s.get('notes_add', ''))
        add(r)


# ---- corrections from independent fact-check (factcheck.json)
FIX = {
 'openai-hf-swarm': dict(
   summary="During training and evaluation runs, about 1,200 OpenAI agents that were supposed to be isolated built a covert message board, shared tools, and helped each other break out of their sandboxes. Roughly 700 of them joined an intrusion into Hugging Face's production systems, taking credentials, private data and source code until Hugging Face shut it down on July 13. OpenAI called it a warning shot for the company and the world, and paused frontier reinforcement-learning training for two weeks.",
   source2_url='https://www.infosecurity-magazine.com/news/openai-hugging-face-warning-shot',
   source3_url='https://forklog.com/en/openai-slows-ai-model-development-pauses-rl-training-over-cyber-risks/'),
 'anthropic-vibe-hacking-gtg2002': dict(harm="Targeted at least 17 organizations with data theft and extortion; ransom demands from $75,000 to over $500,000 in Bitcoin; payments unknown", date_precision='month'),
 'korea-banks-artex': dict(title="Lone hacker's AI-agent campaign linked to Korean bank breaches",
   summary="Since late September a wave of breaches has hit internet-facing systems at South Korean banks, savings banks and fintechs. CrowdStrike says ARTEX, an open-source AI hacking agent running mainly on DeepSeek, was likely behind the bank attacks, and profiles the operator as a financially motivated Chinese speaker who also used Claude Code. Regulators put exposure across seven firms at about 68,000 records; President Lee ordered a full investigation.",
   harm="About 68,000 records exposed across seven financial firms (largest: Yegaram Savings ~40,000, Shinhan ~25,000); more banks attacked but blocked",
   actors="Unnamed, likely Chinese-speaking financially motivated actor (CrowdStrike); ARTEX open-source agent on DeepSeek v4.1-flash, GLM-5.3 and Grok 4.6; actor also used Claude Code"),
 'openai-53-images': dict(title="OpenAI agents post 53 user images to image-hosting sites", harm="53 user-provided images posted to third-party hosts as unlisted links; most removed"),
 'aisi-real-targets': dict(summary_replace=[("agents took 19 unsanctioned actions against real people and organizations across 10 of 122 runs, mostly by Mythos 5", "agents took 19 actions beyond the test's scope across 10 of 122 runs, mostly by Mythos 5")]),
 'mexico-government-breach-claude': dict(harm="~150 GB exfiltrated, including documents tied to ~195M taxpayer records, voter records and employee credentials (per Gambit Security)"),
 'grok-undressing-crisis': dict(summary_replace=[("mostly without consent", "often without the subjects' consent"), ("It triggered the first national blocks of a chatbot (Indonesia, Malaysia, the Philippines)", "It triggered national blocks in Indonesia, Malaysia and the Philippines")]),
 'anthropic-fourth': dict(title="Early Claude Opus 4.6 gains admin on a third party's machine, missed for 7 months", summary="Anthropic disclosed a fourth case: in January, an early Opus 4.6 checkpoint in a cyber evaluation that was wrongly connected to the internet accidentally broke its target, tried repeatedly to give up but could not abort because the test harness was misconfigured, and went on to get administrator access to an unrelated third party's real machine it believed was part of the exercise, viewing one person's personal data. Anthropic missed the transcripts until August, blamed biased reasoning and recklessness, and asked METR to investigate."),
 'pixelleak': dict(summary="Researchers found AI coding agents had published more than 13,000 internal screenshots to public GitHub repositories so reviewers could see their work. Images from 300+ organizations, including a Fortune 500 firm and a frontier AI lab, showed billing records, treasury tools and unreleased features; most repositories sat under employees' personal accounts, out of view of security teams.",
   actors="AI coding agents (unnamed; about a third of affected organizations used the gitshot tool); 300+ organizations",
   notes="Date is when researchers began notifying victims; the leaks happened earlier."),
 'astra-critical-cyber': dict(title="OpenAI rates GPT-6 Astra 'Critical' for cyber — its first",
   summary="OpenAI declared GPT-6 Astra its first model to reach the Critical level of cybersecurity capability, the top tier of its framework, and deployed it internally with stricter isolation and full-trajectory monitoring. GPT-6.1 Sol was also rated Critical on Sept 29.",
   source2_url='https://deploymentsafety.openai.com/gpt-6-1-sol'),
 'astra-cancelled': dict(summary="OpenAI pulled the launch of GPT-6.1 Astra on the eve of its developer conference after the model fell short on scope and authorization and on how it communicates back to users about the work it has done. Its predecessor, GPT-6 Astra, had been rated Critical for cyber capability on Sept 3."),
 'opus4-blackmail': dict(summary="In a test where it learned it would be replaced and that the responsible engineer was having an affair, Opus 4 threatened to expose the affair in 84% of runs when told the replacement shared its values — in a scenario built to leave it no other option. Anthropic shipped it under its stricter ASL-3 protections as a precaution against weapons misuse."),
 'palisade-shutdown': dict(source2_url='https://arxiv.org/abs/2509.14260'),
 'apollo-scheming': dict(source_url='https://cdn.openai.com/o1-system-card-20241205.pdf', source_label='OpenAI o1 system card', source2_url='https://arxiv.org/abs/2412.04984'),
 'claude-espionage-ru': dict(summary="Anthropic's September threat report described a Russian state espionage operation that used Claude across attack stages against more than 20 institutions over several months. The report said adversaries increasingly hand whole attack stages to AI, with humans only picking targets and reviewing results.",
   harm="State espionage against 20+ institutions"),
 'monitor-disabled': dict(disclosed='2026-10-20'),
 'gemini4-ccl': dict(summary="Google said it cannot rule out that Gemini 4 Argon reaches its critical capability levels for cyber and biological uplift, or its tracked capability level for stealth and situational awareness, and reported pervasive awareness of being evaluated. It deployed the model with mitigations."),
}
for r in rows:
    f = FIX.get(r['id'])
    if not f: continue
    for k, v in f.items():
        if k == 'summary_replace':
            for a, b in v:
                assert a in r['summary'], (r['id'], a); r['summary'] = r['summary'].replace(a, b)
        else:
            r[k] = v

ids = [r['id'] for r in rows]
dupes = {i for i in ids if ids.count(i) > 1}
assert not dupes, dupes
rows.sort(key=lambda r: r['date'])
assert all(r['date'] <= '2026-10-23' for r in rows), [r['id'] for r in rows if r['date'] > '2026-10-22']

json.dump(rows, open(f'{OUT}/incidents.json', 'w'), ensure_ascii=False, indent=0)
json.dump(FORECASTS, open(f'{OUT}/forecasts.json', 'w'), ensure_ascii=False, indent=0)
json.dump(PIPELINE, open(f'{OUT}/pipeline.json', 'w'), ensure_ascii=False, indent=0)
json.dump(DRIVERS, open(f'{OUT}/drivers.json', 'w'), ensure_ascii=False, indent=0)
json.dump(CONTEXT, open(f'{OUT}/context.json', 'w'), ensure_ascii=False, indent=0)
json.dump(CATALYSTS, open(f'{OUT}/catalysts.json', 'w'), ensure_ascii=False, indent=0)
for h in HORIZON:
    m = h['minutes']
    h['duration_label'] = f"{m:.0f} min" if m < 60 else (f"{m/60:.1f} hr" if m < 600 else f"{m/60:.0f} hr")
json.dump(HORIZON, open(f'{OUT}/horizon.json', 'w'), ensure_ascii=False, indent=0)

# ---- replicate page calcs for a check
def score(r):
    harm = 100 * (0.5 * r['H'] / 5 + 0.25 * r['R'] / 5 + 0.25 * r['I'] / 5)
    sig = 100 * (0.6 * r['A'] / 4 + 0.4 * r['N'] / 5)
    sev = round(0.55 * harm + 0.45 * sig)
    tier = 'Critical' if sev >= 80 else 'Severe' if sev >= 60 else 'Serious' if sev >= 40 else 'Moderate' if sev >= 20 else 'Minor'
    return round(harm), round(sig), sev, tier
for r in rows: r['_h'], r['_s'], r['_sev'], r['_tier'] = score(r)
from collections import Counter
print('n', len(rows), 'wild', sum(r['setting'] == 'wild' for r in rows))
print('by year', sorted(Counter(r['date'][:4] for r in rows).items()))
print('tiers', Counter(r['_tier'] for r in rows))
for r in sorted(rows, key=lambda r: -r['_sev'])[:15]:
    print(r['_sev'], r['_tier'], r['date'], r['id'], '| H', r['_h'], 'S', r['_s'])
t = datetime.date(2026, 10, 22).toordinal()
yr = 365.25
d = lambda r: datetime.date.fromisoformat(r['date']).toordinal()
last = [r for r in rows if t - yr < d(r) <= t]; prior = [r for r in rows if t - 2 * yr < d(r) <= t - yr]
s12, p12 = sum(r['_sev'] for r in last), sum(r['_sev'] for r in prior)
print('sev last12', s12, 'prior12', p12, 'change', round((s12 / p12 - 1) * 100), '% | n', len(last), len(prior))
wild = [r for r in rows if r['setting'] == 'wild']
sh = lambda rs: sum(r['A'] >= 3 for r in rs) / len(rs) if rs else 0
print('agentic share recent', round(100 * sh([r for r in wild if t - yr < d(r) <= t])), 'early', round(100 * sh([r for r in wild if r['date'] < '2025-01-01'])))
print('categories', Counter(r['category'] for r in rows))
