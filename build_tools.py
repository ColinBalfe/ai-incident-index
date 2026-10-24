#!/usr/bin/env python3
"""Two free tools, built as static pages in the site's shell (no accounts, nothing leaves the browser):
  shield/   The family safe word: a printable protocol card against voice-clone and imposter scams, plus what to do with a suspicious call or text.
  scraped/  Keep your work out of AI training sets: a robots.txt generator for the AI crawlers in the community-maintained ai.robots.txt list
            (refreshed from GitHub at build time when reachable; the last good copy is kept in data/ai-bots.json).
Run after build_site.py. Adds both pages to the sitemap via build_pages.py (EXTRA_URLS)."""
import json, os, sys, html, urllib.request
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
sys.path.insert(0, here)
from pageshell import shell, site, build, esc

# ---------- the crawler list
BOTS_URL = 'https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/main/robots.json'
bots_path = 'data/ai-bots.json'
bots = None
try:
    with urllib.request.urlopen(urllib.request.Request(BOTS_URL, headers={'User-Agent': 'warningshots.ai build'}), timeout=20) as r:
        fetched = json.loads(r.read().decode('utf-8'))
    if isinstance(fetched, dict) and len(fetched) > 50:
        bots = dict(source=BOTS_URL, fetched=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(timespec='seconds'), bots=fetched)
        json.dump(bots, open(bots_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
except Exception as e:  # offline or rate-limited: use the last good copy
    print('ai-bots: using the committed copy (' + str(e)[:60] + ')')
if bots is None:
    bots = json.load(open(bots_path, encoding='utf-8'))
nbots = len(bots['bots'])

def page(path, title, desc, body, css='', js=''):
    url = f'{site}{path}/'
    jsonld = json.dumps({"@context": "https://schema.org", "@type": "WebApplication", "name": title, "url": url, "description": desc, "applicationCategory": "UtilityApplication", "operatingSystem": "Any", "isAccessibleForFree": True, "publisher": {"@type": "NewsMediaOrganization", "name": "Warning Shots", "url": site}}, ensure_ascii=False)
    html_ = shell(title=title, desc=desc, url=url, img=f'{site}assets/og.png?v={build}', body=body, jsonld=jsonld, kind='tool')
    if css: html_ = html_.replace('</head>', css + '\n</head>', 1)
    if js: html_ = html_.replace('</body>', js + '\n</body>', 1)
    os.makedirs(path, exist_ok=True); open(os.path.join(path, 'index.html'), 'w', encoding='utf-8').write(html_)
    return url

# ---------- 1. the family safe word
SHIELD_CSS = """<style>
.tool-grid { display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 18px; }
@media (min-width: 760px) { .tool-grid { grid-template-columns: 1fr 1fr; align-items: start; } }
.form { border: 1px solid var(--line); background: var(--panel); padding: 16px; }
.form label { display: block; font-size: 13px; color: var(--ink-2); margin-top: 12px; }
.form label:first-child { margin-top: 0; }
.form input[type=text] { width: 100%; font: inherit; font-size: 16px; padding: 9px 10px; border: 1px solid var(--line-2); background: var(--paper); color: var(--ink); margin-top: 4px; }
.form .row { display: flex; gap: 8px; align-items: center; margin-top: 4px; }
.form .row input { margin-top: 0; }
.form button, .actions button, .actions a { font: inherit; font-size: 13.5px; border: 1px solid var(--line-2); background: var(--panel); color: var(--ink); padding: 8px 12px; cursor: pointer; text-decoration: none; min-height: 36px; }
.form button:hover, .actions button:hover { border-color: var(--ink); }
.form .rules label { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; color: var(--ink); margin-top: 10px; }
.form .rules input { margin-top: 4px; flex: none; }
.card { border: 2px solid var(--ink); background: var(--panel); padding: 20px; }
.card .cardk { font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-3); }
.card h2 { font-family: var(--serif); font-weight: 900; font-size: 1.6rem; margin-top: 6px; }
.card .word { margin: 14px 0; padding: 12px 14px; border: 1px dashed var(--line-2); font-size: 13px; color: var(--ink-2); }
.card .word b { display: block; font-family: var(--serif); font-size: 2rem; font-weight: 900; color: var(--ink); letter-spacing: -0.01em; margin-top: 2px; }
.card ol { margin: 10px 0 0; padding-left: 20px; font-size: 15px; }
.card ol li { margin-top: 8px; }
.card .who { margin-top: 14px; font-size: 13.5px; color: var(--ink-2); }
.card .foot { margin-top: 16px; font-size: 12px; color: var(--ink-3); border-top: 1px solid var(--line); padding-top: 10px; }
.actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.triage { margin-top: 10px; }
.triage li { margin-top: 8px; }
@media print { .mast, footer, .form, .actions, .triage-wrap, .toast, .skip, .tool-intro, section.src { display: none !important; } .tool-grid { display: block; } .card { border-width: 3px; } body { background: #fff; color: #000; } }
</style>"""
SHIELD_JS = r"""<script>
(function () {
  var A = ['amber', 'copper', 'cobalt', 'harbor', 'maple', 'granite', 'saffron', 'willow', 'cinder', 'juniper', 'velvet', 'marble', 'tundra', 'lantern', 'orchard', 'pebble', 'quartz', 'thistle', 'walnut', 'ember'];
  var B = ['otter', 'kettle', 'compass', 'anvil', 'canoe', 'ladder', 'falcon', 'biscuit', 'trombone', 'satchel', 'pelican', 'tractor', 'beacon', 'walrus', 'teapot', 'hammock', 'badger', 'violin', 'parrot', 'sundial'];
  var q = function (s) { return document.querySelector(s); };
  var fam = q('#fam'), word = q('#word'), names = q('#names'), out = q('#card');
  function suggest() { var r = new Uint32Array(2); (window.crypto || {}).getRandomValues ? crypto.getRandomValues(r) : (r[0] = Math.random() * 1e9, r[1] = Math.random() * 1e9); word.value = A[r[0] % A.length] + ' ' + B[r[1] % B.length]; render(); }
  function rules() { return Array.prototype.filter.call(document.querySelectorAll('.rules input'), function (c) { return c.checked; }).map(function (c) { return c.parentNode.textContent.trim(); }); }
  function render() {
    q('#c-fam').textContent = (fam.value.trim() || 'Our family') + ' · safe word card';
    q('#c-word').textContent = word.value.trim() || '— choose a word —';
    var rl = q('#c-rules'); rl.innerHTML = ''; rules().forEach(function (t) { var li = document.createElement('li'); li.textContent = t; rl.appendChild(li); });
    q('#c-who').textContent = names.value.trim() ? 'Shared with: ' + names.value.trim() + '.' : '';
    q('#c-date').textContent = 'Made ' + new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) + ' at warningshots.ai/shield. Keep it off social media; change the word if it ever leaks.';
  }
  function asText() { return (fam.value.trim() || 'Our family') + ' — safe word: ' + (word.value.trim() || '(choose one)') + '\n\n' + rules().map(function (t, i) { return (i + 1) + '. ' + t; }).join('\n') + '\n\n' + (names.value.trim() ? 'Shared with: ' + names.value.trim() + '\n' : '') + 'Card: ' + location.href.split('#')[0]; }
  q('#suggest').addEventListener('click', suggest);
  ['input', 'change'].forEach(function (ev) { document.querySelector('.form').addEventListener(ev, render); });
  q('#print').addEventListener('click', function () { window.print(); });
  q('#copy').addEventListener('click', function () { var t = asText(); var done = function () { var x = document.getElementById('toast'); x.textContent = 'Copied. Paste it into the family group chat.'; x.classList.add('on'); setTimeout(function () { x.classList.remove('on'); }, 1800); }; if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () { window.prompt('Copy this', t); }); else window.prompt('Copy this', t); });
  render();
})();
</script>"""
shield_body = f"""
<div class="kicker"><span>Free tool</span><span class="dot">·</span><b>The family safe word</b><span class="dot">·</span><span>nothing you type leaves your browser</span></div>
<h1>A voice that sounds like your kid is no longer proof it’s your kid.</h1>
<p class="lede tool-intro">Voice cloning needs a few seconds of audio, and caller ID can be faked. The defence is older than the technology: a word only your family knows, and one rule — hang up and call back on a number you already have. Make the card, print it or paste it into the group chat, and agree on it before anyone needs it.</p>
<div class="tool-grid">
  <div class="form" aria-label="Make your card">
    <label>Family or group name<input type="text" id="fam" placeholder="The Rivera family" maxlength="60"></label>
    <label>Your safe word<div class="row"><input type="text" id="word" placeholder="two ordinary words nobody would guess" maxlength="40"><button type="button" id="suggest">Suggest one</button></div></label>
    <p class="k" style="margin:6px 0 0">Pick something you would never post online: not a pet, a street or a birthday. Two unrelated words work well.</p>
    <label>Who shares it (optional)<input type="text" id="names" placeholder="Mom, Dad, Sam, Grandma June" maxlength="120"></label>
    <div class="rules" role="group" aria-label="Rules on the card">
      <label><input type="checkbox" checked> Any urgent call about money, a code, an accident or an arrest: hang up and call the person back on the number you already have for them.</label>
      <label><input type="checkbox" checked> Ask for the safe word. A real family member knows it. Never say it first, and never say it to someone who asks you to.</label>
      <label><input type="checkbox" checked> Never read out a one-time code, PIN, password or Social Security number to anyone who called or texted you, including “your bank”.</label>
      <label><input type="checkbox" checked> No bank, police force, court or government agency asks for payment in gift cards, crypto or a wire transfer. Anyone who does is a scammer.</label>
      <label><input type="checkbox" checked> Toll, parcel, tax or “account locked” texts: don’t tap the link. Open the official app or type the address yourself.</label>
      <label><input type="checkbox" checked> If something still feels wrong, call a second family member before doing anything. Scammers need you alone and in a hurry.</label>
    </div>
    <div class="actions"><button type="button" id="print">Print or save as PDF</button><button type="button" id="copy">Copy as text for the group chat</button></div>
  </div>
  <div class="card" id="card" aria-live="polite">
    <div class="cardk" id="c-fam">Our family · safe word card</div>
    <h2>If a call doesn’t feel right, it isn’t. Hang up. Call back.</h2>
    <div class="word">Our safe word<b id="c-word">— choose a word —</b></div>
    <ol id="c-rules"></ol>
    <div class="who" id="c-who"></div>
    <div class="foot" id="c-date"></div>
  </div>
</div>
<section class="triage-wrap"><h2>Got a suspicious call, text or email right now?</h2>
<ol class="triage">
  <li><b>Stop.</b> Don’t pay, don’t read out a code, don’t tap the link. Urgency is the tell.</li>
  <li><b>Call back.</b> Use a number from the back of your card, your statement or the official website, never the one in the message.</li>
  <li><b>Verify the person.</b> Ask for the safe word, or ask something only they would know and a clone could not have learned from the internet.</li>
  <li><b>If money moved,</b> call your bank immediately; the first hours matter most. Then report it: in the US at <a href="https://reportfraud.ftc.gov/" target="_blank" rel="noopener noreferrer">reportfraud.ftc.gov</a> and, for online crime, <a href="https://www.ic3.gov/" target="_blank" rel="noopener noreferrer">ic3.gov</a> (the FBI); elsewhere, your national fraud line.</li>
  <li><b>Tell the family.</b> A scammer who has your relative’s voice will try the others next.</li>
</ol></section>
<section class="src"><h2>Why this exists</h2><p>The index behind this site records AI voice-clone and deepfake fraud as it happens, alongside everything else AI has done to real people. The protocol above is the standard advice of consumer-protection agencies, written to fit on one card. It is not legal or financial advice, and nothing you type here is stored or sent anywhere.</p><p class="k"><a href="/">Warning Shots</a> · <a href="/i/">every incident on the index</a> · <a href="/#all">search the index for “deepfake”</a></p></section>
"""
u1 = page('shield', 'The family safe word', 'A printable safe-word protocol card against voice-clone and imposter scams, and what to do with a suspicious call or text. Free, nothing leaves your browser. From Warning Shots.', shield_body, SHIELD_CSS, SHIELD_JS)

# ---------- 2. keep your work out of AI training sets
groups = {}
for name, b in bots['bots'].items():
    op = (b.get('operator') or 'Unclear').strip(); op = op if not op.lower().startswith('unclear') else 'Operator unclear'
    op = __import__('re').sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', op)
    groups.setdefault(op, []).append((name, b))
def opkey(k): return (k == 'Operator unclear', -len(groups[k]), k.lower())
ops_sorted = sorted(groups, key=opkey)
rows = []
for op in ops_sorted:
    items = sorted(groups[op], key=lambda x: x[0].lower())
    rows.append(f'<div class="opgrp"><div class="ophead"><label><input type="checkbox" class="op" data-op="{esc(op)}" checked> <b>{esc(op)}</b></label> <button type="button" class="tgl" aria-expanded="false">{len(items)} {"bot" if len(items) == 1 else "bots"}</button></div><div class="botlist" hidden>' + ''.join(
        f'<label><input type="checkbox" class="bot" data-op="{esc(op)}" value="{esc(name)}" checked> <code>{esc(name)}</code> <span class="k">{esc((b.get("function") or "").strip())}</span><small>{esc((b.get("description") or "").split(" More info")[0][:220])}{(" · respects robots.txt: " + esc(str(b.get("respect")))) if b.get("respect") and not str(b.get("respect")).lower().startswith("unclear") else ""}</small></label>' for name, b in items) + '</div></div>')
SCRAPED_CSS = """<style>
.tool-grid { display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 18px; }
@media (min-width: 900px) { .tool-grid { grid-template-columns: 1.1fr .9fr; align-items: start; } }
.opgrp { border-top: 1px solid var(--line); padding: 8px 0; }
.ophead { display: flex; gap: 10px; align-items: baseline; }
.ophead label { cursor: pointer; }
.ophead .tgl { font: inherit; font-size: 12.5px; color: var(--ink-3); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; min-height: 24px; }
.botlist { padding: 6px 0 4px 24px; display: grid; gap: 6px; }
.botlist label { display: block; font-size: 13.5px; }
.botlist code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12.5px; }
.botlist small { display: block; color: var(--ink-3); font-size: 12px; margin-left: 22px; }
.ctl { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.ctl button, .outbox button, .outbox a { font: inherit; font-size: 13px; border: 1px solid var(--line-2); background: var(--panel); color: var(--ink); padding: 7px 11px; cursor: pointer; text-decoration: none; min-height: 34px; }
.ctl button:hover, .outbox button:hover { border-color: var(--ink); }
.outbox { position: sticky; top: 16px; border: 1px solid var(--line); background: var(--panel); padding: 14px; }
.outbox h2 { font-family: var(--sans); font-size: 1rem; }
.outbox textarea { width: 100%; height: 320px; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; border: 1px solid var(--line-2); background: var(--paper); color: var(--ink); padding: 10px; margin-top: 8px; resize: vertical; }
.outbox .acts { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.outbox .n { font-size: 13px; color: var(--ink-2); margin-top: 8px; }
.steps li { margin-top: 8px; }
</style>"""
SCRAPED_JS = r"""<script>
(function () {
  var ta = document.getElementById('out'), n = document.getElementById('n'), tdm = document.getElementById('tdm'), meta = document.getElementById('metaout');
  function picked() { return Array.prototype.filter.call(document.querySelectorAll('input.bot'), function (c) { return c.checked; }).map(function (c) { return c.value; }); }
  function render() {
    var names = picked(); var lines = ['# AI crawler block list from warningshots.ai/scraped (' + names.length + ' user agents, list dated ' + document.body.getAttribute('data-listdate') + ').', '# Add these lines to the robots.txt at the root of your site. Keep any existing rules for search engines below them.', ''];
    names.forEach(function (u) { lines.push('User-agent: ' + u); }); lines.push('Disallow: /'); lines.push('');
    if (document.getElementById('keepsearch').checked) lines.push('User-agent: *', 'Allow: /', '');
    ta.value = lines.join('\n'); n.textContent = names.length + ' of ' + document.querySelectorAll('input.bot').length + ' crawlers blocked.';
  }
  document.addEventListener('change', function (e) { var t = e.target; if (t.classList && t.classList.contains('op')) { Array.prototype.forEach.call(document.querySelectorAll('input.bot[data-op="' + CSS.escape(t.dataset.op) + '"]'), function (c) { c.checked = t.checked; }); } if (t.classList && t.classList.contains('bot')) { var op = t.dataset.op; var all = document.querySelectorAll('input.bot[data-op="' + CSS.escape(op) + '"]'); document.querySelector('input.op[data-op="' + CSS.escape(op) + '"]').checked = Array.prototype.every.call(all, function (c) { return c.checked; }); } render(); });
  document.getElementById('all').addEventListener('click', function () { document.querySelectorAll('input.bot, input.op').forEach(function (c) { c.checked = true; }); render(); });
  document.getElementById('none').addEventListener('click', function () { document.querySelectorAll('input.bot, input.op').forEach(function (c) { c.checked = false; }); render(); });
  function setOpen(grp, open) { var list = grp.querySelector('.botlist'), b = grp.querySelector('.tgl'); list.hidden = !open; b.setAttribute('aria-expanded', String(open)); }
  document.querySelectorAll('.opgrp .tgl').forEach(function (b) { b.addEventListener('click', function () { var g = b.closest('.opgrp'); setOpen(g, g.querySelector('.botlist').hidden); }); });
  document.getElementById('open').addEventListener('click', function () { document.querySelectorAll('.opgrp').forEach(function (d) { setOpen(d, true); }); });
  document.getElementById('close').addEventListener('click', function () { document.querySelectorAll('.opgrp').forEach(function (d) { setOpen(d, false); }); });
  function dl(name, text, type) { var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: type || 'text/plain' })); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  document.getElementById('dl').addEventListener('click', function () { dl('robots.txt', ta.value); });
  document.getElementById('cp').addEventListener('click', function () { var done = function () { var x = document.getElementById('toast'); x.textContent = 'Copied'; x.classList.add('on'); setTimeout(function () { x.classList.remove('on'); }, 1500); }; if (navigator.clipboard) navigator.clipboard.writeText(ta.value).then(done); else { ta.select(); document.execCommand('copy'); done(); } });
  document.getElementById('dltdm').addEventListener('click', function () { dl('tdmrep.json', tdm.textContent, 'application/json'); });
  render();
})();
</script>"""
scraped_body = f"""
<div class="kicker"><span>Free tool</span><span class="dot">·</span><b>Keep your work out of AI training sets</b><span class="dot">·</span><span>{nbots} crawlers · list refreshed each build</span></div>
<h1>A robots.txt for the bots that scrape for AI.</h1>
<p class="lede">Every crawler below identifies itself by name when it visits a site. This builds the block list for yours from the community-maintained <a href="https://github.com/ai-robots-txt/ai.robots.txt" target="_blank" rel="noopener noreferrer">ai.robots.txt</a> list, grouped by who operates each bot. Untick anything you want to allow (AI search crawlers send some sites traffic; training crawlers send nothing back), then download or copy the file.</p>
<div class="tool-grid">
  <div>
    <div class="ctl"><button type="button" id="all">Block all</button><button type="button" id="none">Clear</button><button type="button" id="open">Expand</button><button type="button" id="close">Collapse</button><label style="font-size:13px;display:inline-flex;align-items:center;gap:6px;margin-left:auto"><input type="checkbox" id="keepsearch" checked> add “allow everyone else” for search engines</label></div>
    <div class="ops">{''.join(rows)}</div>
  </div>
  <div class="outbox">
    <h2>Your robots.txt</h2>
    <textarea id="out" readonly aria-label="Generated robots.txt"></textarea>
    <div class="acts"><button type="button" id="dl">Download robots.txt</button><button type="button" id="cp">Copy</button></div>
    <div class="n" id="n"></div>
    <h2 style="margin-top:16px">Also: the machine-readable opt-out</h2>
    <p class="k">The W3C’s TDM Reservation Protocol lets a site state that text-and-data mining rights are reserved, which the EU’s copyright rules recognise. Two files: <code>/.well-known/tdmrep.json</code> and a tag in each page’s head.</p>
    <pre id="tdm" style="font-size:12px;border:1px solid var(--line-2);background:var(--paper);padding:10px;overflow:auto">[
  {{ "location": "/", "tdm-reservation": 1 }}
]</pre>
    <pre style="font-size:12px;border:1px solid var(--line-2);background:var(--paper);padding:10px;overflow:auto">&lt;meta name="tdm-reservation" content="1"&gt;</pre>
    <div class="acts"><button type="button" id="dltdm">Download tdmrep.json</button></div>
  </div>
</div>
<section><h2>What this does and doesn’t do</h2>
<ol class="steps">
  <li><b>robots.txt is a request, not a wall.</b> Operators that say they respect it (noted per bot above where known) will stop; the ones that don’t need a firewall rule or your host’s bot controls. Your web host or CDN usually has a one-click “block AI crawlers” setting that enforces the same list at the network edge.</li>
  <li><b>It only stops future crawls.</b> Work already collected stays in the datasets it was collected into. The reservation file above is the legal signal; the block list is the technical one. Use both.</li>
  <li><b>Check it worked.</b> After uploading, open <code>yoursite.com/robots.txt</code> in a browser and look for the names. Server logs will show which bots still visit.</li>
  <li><b>Re-run this every few months.</b> New crawlers appear constantly; the list here is rebuilt from the maintained source each time the site refreshes ({nbots} entries today).</li>
</ol></section>
<section class="src"><h2>Sources</h2><p>Crawler names, operators and behaviour notes: the <a href="https://github.com/ai-robots-txt/ai.robots.txt" target="_blank" rel="noopener noreferrer">ai.robots.txt</a> project (MIT licence), fetched {esc(bots.get('fetched', '')[:10])}. The reservation format: the <a href="https://www.w3.org/community/tdmrep/" target="_blank" rel="noopener noreferrer">W3C TDM Reservation Protocol community group</a>. Nothing you select here is sent anywhere; the file is assembled in your browser.</p></section>
"""
u2 = page('scraped', 'Keep your work out of AI training sets', f'A robots.txt generator for the {nbots} AI crawlers in the community-maintained ai.robots.txt list, grouped by operator, plus the machine-readable opt-out. Free, built in your browser. From Warning Shots.', scraped_body, SCRAPED_CSS, SCRAPED_JS)
# stamp the list date into the body for the generated header comment
p2 = 'scraped/index.html'; t = open(p2, encoding='utf-8').read().replace('<body data-kind="tool">', f'<body data-kind="tool" data-listdate="{esc(bots.get("fetched", "")[:10])}">', 1); open(p2, 'w', encoding='utf-8').write(t)
json.dump([u1, u2], open('data/tool_urls.json', 'w'))
print('tools: shield, scraped (' + str(nbots) + ' crawlers)')
