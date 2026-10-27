#!/usr/bin/env python3
"""The shared page shell for the site's static pages (dispatch pages, tools): masthead, nav, footer, head tags, copy-link script.
Imported by build_pages.py and build_tools.py. Reads data/meta.json, assets/build.json and the masthead mark from index.template.html."""
import json, os, re, html, datetime as dt
from zoneinfo import ZoneInfo
here = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, here)
from analytics import tag as _analytics_tag
ANALYTICS = _analytics_tag()
meta = json.load(open(os.path.join(here, 'data', 'meta.json'), encoding='utf-8')); site = meta['site_url']
build = json.load(open(os.path.join(here, 'assets', 'build.json')))['build']
esc = html.escape
AS_OF = meta['as_of']
as_of_label = dt.datetime.fromisoformat(AS_OF).astimezone(ZoneInfo('America/New_York')).strftime('%b %-d, %Y, %-I:%M %p ET')
# ---------- the shell
tpl = open(os.path.join(here, 'index.template.html'), encoding='utf-8').read()
MARK = re.search(r'<a class="logo"[^>]*>\s*(<svg class="mark nf".*?</svg>)', tpl, re.S).group(1)
def _live_nav():
    sr = meta.get('serial') or {}
    if not sr.get('name') or sr.get('state') == 'closed' or not sr.get('day1'):
        return ''   # the live slot goes dark when nothing is live
    day = (dt.date.fromisoformat(AS_OF[:10]) - dt.date.fromisoformat(sr['day1'])).days + 1
    return f'<a href="{esc(sr.get("url") or "/")}" class="live-nav" title="{esc(sr["name"])}: day {day} since it went public"><span class="live-dot" aria-hidden="true">●</span> Live case · day {day}</a>'
LIVE_NAV = _live_nav()
NAV = '<nav aria-label="Sections"><a href="/wire/">The Wire</a>' + LIVE_NAV + '<a href="/exposed/">Am I exposed?</a><a href="/i/">Incidents</a><a href="/index/#about">About</a></nav>'
FOOT = f'<footer><div class="wrap"><span><b>Warning Shots</b>. See what’s coming. Know what it means.</span><span>Scores are the index’s own, by a <a href="/index/#about">published formula</a>; facts link to their sources. Last refresh {esc(as_of_label)}. <a href="/learn/">Know What It Means</a> · <a href="/help/">What to do</a> · <a href="/checks/">Is this a scam?</a> · <a href="/exposed/">Am I exposed?</a> · <a href="/jobs/">Can AI do your job?</a> · <a href="/can-ai/">What AI can do</a> · <a href="/press/">Press</a> · <a href="/badge/">Embed the level</a></span></div></footer>'
SCRIPT = """<script>
document.querySelectorAll('[data-copy]').forEach(function (b) { b.addEventListener('click', function () { var t = b.getAttribute('data-copy'); var done = function () { var x = document.getElementById('toast'); x.textContent = 'Copied'; x.classList.add('on'); setTimeout(function () { x.classList.remove('on'); }, 1500); };
  if (navigator.clipboard) navigator.clipboard.writeText(t).then(done, function () { window.prompt('Copy this link', t); }); else window.prompt('Copy this link', t); }); });
</script>"""

def _short(t, n=62):
    t = (t or '').strip()
    if len(t) <= n: return t
    cut = t[:n].rsplit(' ', 1)[0].rstrip(' ,;:—-')
    return cut + '…'

def shell(*, title, desc, url, img, body, jsonld, kind):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(_short(title))} | Warning Shots</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(url)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta property="og:type" content="article"><meta property="og:site_name" content="Warning Shots"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(img)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(img)}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#F4F3EF" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0A111E" media="(prefers-color-scheme: dark)">
<link rel="alternate" type="application/rss+xml" title="Warning Shots: the Wire and the daily brief" href="/feed.xml">
<link rel="preload" href="/assets/fonts/archivo-latin-standard-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/playfair-display-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/dispatch.css?v={build}">
<script>try {{ var t = localStorage.getItem('aii-theme'); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script type="application/ld+json">{jsonld}</script>
</head>
<body data-kind="{kind}">
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap"><a class="logo" href="/" aria-label="Warning Shots, home">{MARK}<span class="wm">Warning Shots</span></a>{NAV}</div></header>
<main id="main"><div class="wrap">
{body}
</div></main>
{FOOT}
<div class="toast" id="toast" role="status" aria-live="polite"></div>
{SCRIPT}
{ANALYTICS}
</body>
</html>
"""

