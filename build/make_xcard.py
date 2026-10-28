"""The daily X card: one native image for Colin's X account, built only from data that has already passed the refresh's
two fact-check rounds (the lead in data/news.json and the stats in assets/build.json). No link to the site on the card or in
the post text (Colin's X rule). Writes build/xcard_out/xcard.html and post.txt; build/make_xcard.mjs renders the PNGs.
Run after build_site.py:  python3 build/make_xcard.py && node build/make_xcard.mjs"""
import json, os, html, datetime
from zoneinfo import ZoneInfo
os.makedirs('build/xcard_out', exist_ok=True)
news = json.load(open('data/news.json', encoding='utf-8'))
lead = next((n for n in news if n.get('wall') == 'siren' and n.get('tag')), None)
if not lead: raise SystemExit('no lead story (wall: siren) in data/news.json; no card today')
b = json.load(open('assets/build.json', encoding='utf-8'))
E = lambda s: html.escape(s or '', quote=False)
et = datetime.datetime.now(ZoneInfo('America/New_York'))
pub = datetime.datetime.fromisoformat(lead['published'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/New_York'))
ppl = lead.get('people') or {}
who = (('Who it helped: ' if ppl.get('kind') == 'helped' else 'Who it hit: ') + ppl['text']) if ppl.get('text') else (lead.get('summary') or '')
TH = {'navy': dict(bg='#0A111E', ink='#F4F3EF', mute='#B4BECC', faint='#7E8C9F', red='#FF3300', top='none'),
      'white': dict(bg='#F4F3EF', ink='#0A111E', mute='#3F4B5C', faint='#5F6B7B', red='#D92D00', top='10px solid #D92D00')}
def card(t, W, H):
    c = TH[t]
    return f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/dispatch.css"><style>
html,body{{margin:0;background:{c['bg']}}} .c{{width:{W}px;height:{H}px;background:{c['bg']};color:{c['ink']};border-top:{c['top']};box-sizing:border-box;padding:76px 76px 64px;display:flex;flex-direction:column;font-family:Archivo,sans-serif}}
.k{{color:{c['red']};font-weight:800;letter-spacing:.16em;font-size:21px;text-transform:uppercase}}
h1{{margin:0;font-family:Playfair,serif;font-weight:900;font-size:96px;line-height:1.02;letter-spacing:-.015em;text-wrap:balance}}
.w{{margin-top:30px;font-size:32px;line-height:1.38;color:{c['mute']}}} .w b{{color:{c['red']};font-weight:800;font-size:.72em;letter-spacing:.12em;text-transform:uppercase;margin-right:8px}}
.st{{margin-top:64px;display:grid;grid-template-columns:1fr 1fr;gap:36px;padding-top:40px;border-top:2px solid {c['red']}}} .mid{{margin:auto 0}} .st b{{display:block;font-family:Playfair,serif;font-weight:900;font-size:84px;line-height:1;color:{c['red']};font-variant-numeric:lining-nums}} .st span{{display:block;margin-top:12px;font-size:22px;line-height:1.35;color:{c['ink']}}}
.f{{margin-top:0;display:flex;justify-content:space-between;align-items:flex-end;gap:28px;font-size:18px;color:{c['faint']};line-height:1.45}} .f b{{white-space:nowrap;font-family:Playfair,serif;font-weight:700;letter-spacing:.16em;color:{c['ink']};font-size:22px}} .f b i{{color:{c['red']};font-style:normal}}
</style></head><body><div class="c"><div class="k">The biggest AI story today · {et.strftime('%a %b')} {et.day}</div>
<div class="mid"><h1 id="h">{E(lead['tag'])}</h1>
<div class="w">{('<b>' + E(who.split(': ', 1)[0]) + '</b>' + E(who.split(': ', 1)[1])) if ': ' in who and ppl.get('text') else E(who)}</div>
<div class="st"><div><b>{b['severe_prior12']} → {b['severe_last12']}</b><span>severe AI incidents, the 12 months before vs. the last 12</span></div><div><b>{b['agentic_share']}%</b><span>of real-world AI incidents in the last 12 months where the AI itself did the acting</span></div></div></div>
<div class="f"><span>Story: {E(lead.get('outlet'))}, {pub.strftime('%b')} {pub.day}. Figures: the Warning Shots incident record ({b['n']} incidents since 2023).</span><b>W<i>:</i> WARNING SHOTS</b></div></div>
<script>const h=document.getElementById('h'),c=document.querySelector('.c');let s=96;while(c.scrollHeight>c.clientHeight&&s>48){{s-=4;h.style.fontSize=s+'px'}}</script></body></html>'''
for t in TH:
    open(f'build/xcard_out/xcard-{t}.html', 'w', encoding='utf-8').write(card(t, 1080, 1350))
post = lead['tag'] + ('\n\n' + who if who else '') + f"\n\nSevere AI incidents: {b['severe_prior12']} → {b['severe_last12']} in a year."
open('build/xcard_out/post.txt', 'w', encoding='utf-8').write(post + '\n')
print('xcard:', lead['id'], '|', lead['tag'])
