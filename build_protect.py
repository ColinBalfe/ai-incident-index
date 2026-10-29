#!/usr/bin/env python3
"""Protect: AI for your life, not just your job. The first track of the Academy: a short, ordered course built from the help,
learn and check pages that already exist, each taught with real cases from the record. One guide per sitting; a reader can
tick each off (saved in their browser only) and see their progress. No new claims here: every line points at a page that
carries its own sources."""
import json, os
from pagekit import write, footer_note, webpage, esc, SITE

STEPS = [
 ('/shield/', 'Set a family safe word', 'A voice that sounds like your kid is no longer proof it\'s your kid. Pick a word tonight and make the card.', '2 minutes'),
 ('/help/voice-clone-scam-call/', 'If a loved one calls in a panic asking for money', 'What to do in the first five minutes, how to check, and how to report it.', 'one read'),
 ('/help/ai-scam-texts/', 'Spot the new scam texts', 'They no longer have the typos. The five most common, the new warning signs, and what to do if you clicked.', 'one read'),
 ('/help/is-this-video-real/', 'Check a video before you share it', 'Eight checks that take a few minutes, and what not to rely on.', 'one read'),
 ('/checks/', 'Run the scam checks', 'Yes-or-no checks for the scams AI makes more convincing: celebrity investments, gift cards, romance crypto, QR codes, fake jobs.', 'a few minutes each'),
 ('/learn/ai-companions-parents-guide/', 'If your kid talks to an AI', 'What children actually use, the real risks, and what to set up together.', 'one read'),
 ('/learn/ai-helper-for-older-parent/', 'Set up an AI helper for an older parent, safely', 'Set one up together, the three rules to teach, and what to switch off.', '30 minutes'),
 ('/help/ai-fake-nude-image-what-to-do/', 'If someone makes a fake nude of you or your child', 'It\'s not your fault, and there are free ways to get it taken down. Know the steps before you need them.', 'one read'),
]
for u, *_ in STEPS:
    assert os.path.exists(u.strip('/') + '/index.html'), u
url = SITE + 'protect/'
lis = ''.join(f'<li data-step="{esc(u)}"><label class="pr-done"><input type="checkbox" aria-label="Mark as done: {esc(t)}"></label><div><a href="{esc(u)}"><b>{i}. {esc(t)}</b></a><span class="meta">{esc(d)} <i>· {esc(tm)}</i></span></div></li>' for i, (u, t, d, tm) in enumerate(STEPS, 1))
body = f"""<article class="pk"><nav class="kick" aria-label="Breadcrumb">The Academy · Protect</nav>
<h1>Protect: AI for your life, not just your job</h1>
<p class="aka">Eight short guides to keep your family safe from the AI scams, fakes and impersonations on our record. Each one is a single sitting, built from real cases, and ends with something to do. Tick each one off as you go.</p>
<section class="box"><b class="k">Your progress</b><p id="pr-prog">Start with the first one: it takes two minutes.</p></section>
<ol class="pr-list">{lis}</ol>
<p class="meta">Your ticks are saved only in this browser. Every guide links its sources; the cases come from <a href="/i/">the record</a>.</p>
<p><a href="/help/">Everything on what to do when AI is used against you →</a></p>
{footer_note(False)}</article>
<style>.pr-list{{list-style:none;padding:0;margin:14px 0}}.pr-list li{{display:grid;grid-template-columns:34px 1fr;gap:10px;align-items:start;padding:12px 0;border-bottom:1px solid var(--line)}}.pr-list a{{font-family:var(--serif);font-size:1.15rem;text-decoration:none}}.pr-list a:hover{{text-decoration:underline}}.pr-list .meta{{display:block;margin-top:3px;font-size:14.5px;color:var(--ink-2)}}.pr-done input{{width:22px;height:22px;margin-top:3px;accent-color:var(--alarm)}}.pr-list li.done a{{color:var(--ink-3)}}</style>
<script>(function(){{var K='ws-protect',S={{}};try{{S=JSON.parse(localStorage.getItem(K)||'{{}}')}}catch(e){{}}
var L=[].slice.call(document.querySelectorAll('.pr-list li')),P=document.getElementById('pr-prog');
function paint(){{var n=0;L.forEach(function(li){{var on=!!S[li.dataset.step];li.classList.toggle('done',on);li.querySelector('input').checked=on;if(on)n++}});
P.textContent=n===0?'Start with the first one: it takes two minutes.':n===L.length?'All '+L.length+' done. Share the safe-word card with someone you love.':n+' of '+L.length+' done.'}}
L.forEach(function(li){{li.querySelector('input').addEventListener('change',function(e){{S[li.dataset.step]=e.target.checked;try{{localStorage.setItem(K,JSON.stringify(S))}}catch(x){{}}paint()}})}});paint()}})();</script>"""
write('protect/index.html', url=url, title='Protect: AI safety for your family, in eight short guides', desc='Eight short guides to protect your family from AI scams, voice clones, deepfakes and fake images: a safe word, what to do in a panic call, scam checks and more.', body=body, draft=False,
      crumbs=[('Protect', '')], graph=[webpage(url, 'Protect', 'AI safety for your family', '2026-10-29', False, ''), {"@type": "Course", "name": "Protect: AI for your life", "description": "Eight short guides to protect your family from AI scams and fakes", "provider": {"@type": "Organization", "name": "Warning Shots", "url": SITE}, "url": url}])
tu_p = 'data/tool_urls.json'
tu = json.load(open(tu_p)) if os.path.exists(tu_p) else []
if url not in tu: tu.append(url)
json.dump(tu, open(tu_p, 'w'))
print('protect: 8 guides')
