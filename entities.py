"""Who's who: the companies, agencies and people the index follows, and the links between every part of the site.

One place decides which names get a page (/who/<slug>/) and how stories, incidents, forecasts, Up & Down rows, X posts and
breakthroughs connect. Used by build_site.py (to tag the homepage data), build_who.py (the pages) and build_pages.py (incident pages).
Matching is by name in the text, case-sensitive, so 'Meta' the company is not 'metadata'. A name gets a page only when it appears
in at least MIN_ITEMS items, so we never publish thin pages."""
import json, os, re

MIN_ITEMS = 4
# slug, display name, kind, pattern (case-sensitive), one-line description
ENTITIES = [
 ('anthropic', 'Anthropic', 'AI lab', r'\bAnthropic\b|\bClaude\b', 'Maker of Claude; filed to go public in October 2026.'),
 ('openai', 'OpenAI', 'AI lab', r'\bOpenAI\b|\bChatGPT\b|\bCodex\b|\bGPT-\d', 'Maker of ChatGPT and the GPT models.'),
 ('google', 'Google and DeepMind', 'AI lab', r'\bGoogle\b|\bDeepMind\b|\bGemini\b|\bAlphabet\b', 'Google, its DeepMind lab and the Gemini models.'),
 ('microsoft', 'Microsoft', 'Company', r'\bMicrosoft\b|\bCopilot\b', 'Maker of Copilot and OpenAI\'s biggest backer.'),
 ('meta', 'Meta', 'Company', r'\bMeta\b(?!-)|\bFacebook\b|\bInstagram\b|\bWhatsApp\b|\bLlama\b', 'Facebook, Instagram and WhatsApp, and the Llama models.'),
 ('xai', 'xAI and Grok', 'AI lab', r'\bxAI\b|\bGrok\b', 'Elon Musk\'s AI company and its Grok chatbot.'),
 ('nvidia', 'Nvidia', 'Company', r'\bNvidia\b|\bNVIDIA\b', 'The chipmaker behind most AI computing.'),
 ('deepseek', 'DeepSeek', 'AI lab', r'\bDeepSeek\b', 'Chinese AI lab with open-weight models.'),
 ('alibaba', 'Alibaba and Qwen', 'AI lab', r'\bAlibaba\b|\bQwen\b', 'Chinese tech group and its Qwen models.'),
 ('moonshot', 'Moonshot AI', 'AI lab', r'\bMoonshot\b|\bKimi\b', 'Chinese lab behind the Kimi models.'),
 ('character-ai', 'Character.AI', 'Company', r'\bCharacter\.AI\b', 'Companion-chatbot company, in bankruptcy in 2026.'),
 ('tesla', 'Tesla', 'Company', r'\bTesla\b', 'Carmaker selling Full Self-Driving.'),
 ('amazon', 'Amazon', 'Company', r'\bAmazon\b|\bAWS\b', 'Amazon and Amazon Web Services.'),
 ('apple', 'Apple', 'Company', r'\bApple\b', 'Maker of the iPhone and Apple Intelligence.'),
 ('hugging-face', 'Hugging Face', 'Company', r'\bHugging Face\b', 'The largest public library of AI models and data.'),
 ('crowdstrike', 'CrowdStrike', 'Company', r'\bCrowdStrike\b', 'Security firm that tracks AI-driven intrusions.'),
 ('cloudflare', 'Cloudflare', 'Company', r'\bCloudflare\b', 'Network company that sits in front of millions of sites.'),
 ('samsung', 'Samsung', 'Company', r'\bSamsung\b', 'Korean electronics and memory-chip giant.'),
 ('workday', 'Workday', 'Company', r'\bWorkday\b', 'HR software maker facing an AI hiring-bias case.'),
 ('unitedhealth', 'UnitedHealth', 'Company', r'\bUnitedHealth\b', 'US health insurer sued over an algorithm that denied care.'),
 ('cisa', 'CISA (America\'s cyber agency)', 'Government', r'\bCISA\b|America\'s cyber agency|Cybersecurity and Infrastructure Security Agency', 'The US agency that warns about exploited flaws.'),
 ('ftc', 'The FTC', 'Government', r'\bFTC\b|Federal Trade Commission', 'The US consumer-protection regulator.'),
 ('uk-aisi', 'UK AI Security Institute', 'Government', r'AI Security Institute|\bAISI\b', 'The British government body that tests frontier AI.'),
 ('sam-altman', 'Sam Altman', 'Person', r'\bSam Altman\b|\bAltman\b', 'Chief executive of OpenAI.'),
 ('dario-amodei', 'Dario Amodei', 'Person', r'\bDario Amodei\b|\bAmodei\b', 'Chief executive of Anthropic.'),
 ('elon-musk', 'Elon Musk', 'Person', r'\bElon Musk\b|\bMusk\b', 'Runs xAI, Tesla and X; also a favourite face for AI scams.'),
]
RX = [(s, n, k, re.compile(p), d) for s, n, k, p, d in ENTITIES]
NAME = {s: n for s, n, *_ in ENTITIES}


def who(text):
    """Slugs of the followed names that appear in this text."""
    return [s for s, n, k, rx, d in RX if rx.search(text or '')]


def _j(p, d):
    try:
        return json.load(open(p, encoding='utf-8'))
    except (OSError, ValueError):
        return d


def load_all(root='.'):
    """Every item on the site that can be tied to a name, as plain dicts with kind, id, date, text and link."""
    J = lambda p, d=[]: _j(os.path.join(root, p), d)
    news = {n['id']: n for n in J('research/news_archive.json') + J('research/news.json')}
    inc = J('data/incidents.json')
    url2inc = {}
    for r in inc:
        for k in ('source_url', 'source2_url', 'source3_url'):
            if r.get(k): url2inc.setdefault(r[k].split('#')[0].rstrip('/'), r['id'])
    calls = J('research/calls.json'); ud = J('research/updown.json'); xp = J('research/x_posts.json'); bt = J('research/breakthroughs.json')
    return dict(news=news, inc=inc, url2inc=url2inc, calls=calls, ud=ud, xp=xp, bt=bt)


def text_of(kind, x):
    if kind == 'news': return ' '.join([x.get('tag') or '', x.get('title') or '', x.get('summary') or ''] + [o for k in ('orgs', 'vendors') for o in ((x.get('entities') or {}).get(k) or [])])
    if kind == 'inc': return ' '.join([x.get('title') or '', x.get('actors') or '', x.get('summary') or ''])
    if kind == 'call': return ' '.join([x.get('question') or '', x.get('plain') or ''])
    if kind == 'ud': return x.get('name') or ''   # a row belongs to the name it is about, not to names it mentions
    if kind == 'xp': return ' '.join([x.get('author') or '', x.get('what') or '', x.get('quote') or ''])
    if kind == 'bt': return ' '.join([x.get('payoff') or '', x.get('means') or ''])
    return ''


def index(root='.'):
    """{slug: {news, inc, call, ud, xp, bt}} for every followed name, plus link maps between items."""
    A = load_all(root)
    out = {s: {k: [] for k in ('news', 'inc', 'call', 'ud', 'xp', 'bt')} for s in NAME}
    for kind, items in (('news', A['news'].values()), ('inc', A['inc']), ('call', A['calls']), ('ud', A['ud']), ('xp', A['xp']), ('bt', A['bt'])):
        for x in items:
            for s in who(text_of(kind, x)):
                out[s][kind].append(x)
    # links: a story belongs to an incident when it is one of the incident's sources
    news2inc = {nid: A['url2inc'].get(n['url'].split('#')[0].rstrip('/')) for nid, n in A['news'].items()}
    news2inc = {k: v for k, v in news2inc.items() if v}
    pages = {s: sum(len(v) for v in d.values()) >= MIN_ITEMS for s, d in out.items()}
    return out, pages, news2inc, A
