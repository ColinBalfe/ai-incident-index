#!/usr/bin/env python3
"""Visitor analytics tag, shared by build_site.py (the front page) and pageshell.py (dispatch and tool pages).

Cloudflare Web Analytics: free, cookie-less, no consent banner, works without moving DNS. The token lives in analytics.json
({"cloudflare_token": "..."}; get it at dash.cloudflare.com -> Web Analytics -> Add a site -> warningshots.ai, then copy the token
from the JS snippet). An empty token emits nothing, so builds stay clean until it is set.

The beacon is added only when the page is served from a real host: local QA renders (prerender.mjs, shot.mjs, http://127.0.0.1)
make no outside requests and print no console errors for a blocked script.

It is also skipped (Oct 30) in automated browsers (navigator.webdriver: the refresh's Playwright checks of the live site were
counted as visitors) and in any browser that has opened a page with ?notrack once (Colin's own devices; ?track undoes it),
so the numbers count readers, not us."""
import json, os

def tag():
    try:
        tok = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analytics.json'), encoding='utf-8')).get('cloudflare_token', '')
    except (OSError, ValueError):
        tok = ''
    tok = ''.join(ch for ch in str(tok) if ch.isalnum())
    if not tok:
        return ''
    return ('<script>(function(){var h=location.hostname;if(!h||h==="localhost"||h==="127.0.0.1"||location.protocol==="file:")return;'
            'if(navigator.webdriver)return;'
            'try{var q=location.search;if(/[?&]notrack\\b/.test(q))localStorage.setItem("ws-notrack","1");else if(/[?&]track\\b/.test(q))localStorage.removeItem("ws-notrack");'
            'if(localStorage.getItem("ws-notrack")==="1")return;}catch(e){}'
            'var s=document.createElement("script");s.defer=true;s.src="https://static.cloudflareinsights.com/beacon.min.js";'
            's.setAttribute("data-cf-beacon",\'{"token": "' + tok + '"}\');document.body.appendChild(s);})();</script>')

if __name__ == '__main__':
    print(tag() or '(no token set in analytics.json)')
