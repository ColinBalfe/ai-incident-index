/* The AI Incident Index — page script. Data lives in ./data/*.json; see build/ for how it is produced. */
(() => {
'use strict';
const SITE = (window.AII_SITE && window.AII_SITE.startsWith('http')) ? window.AII_SITE : location.href.split('#')[0];
const FILES = ['incidents', 'forecasts', 'pipeline', 'drivers', 'context', 'catalysts', 'horizon', 'deepdives', 'victims', 'timeline', 'implications', 'signals', 'live', 'watch', 'meta'];
const OPTIONAL = ['quotes', 'brief', 'news', 'capabilities', 'fixes', 'tns', 'calls', 'xposts', 'desks', 'breakthroughs', 'chart', 'lenses', 'updown'];
const EMBED = new URLSearchParams(location.search).get('embed');
const LEAD_PREVIEW = new URLSearchParams(location.search).get('lead'); if (LEAD_PREVIEW && document.body) document.body.dataset.lead = LEAD_PREVIEW === 'now' ? '' : LEAD_PREVIEW;
const PAGE = (document.body && document.body.dataset.page) || 'front'; // 'front' = the headline page (/), 'record' = the full index (/index/)
const FRONT_IDS = new Set(['wall', 'wall-lead', 'level', 'why', 'front', 'recfoot']);
const WIRE_IDS = new Set(['wire', 'now', 'brief', 'since', 'siren', 'ribbon', 'ticker']);
const RECORD_IDS = new Set(['record', 'capabilities', 'words', 'pattern', 'charts', 'next', 'dives', 'fixes', 'signals', 'all', 'about']);
const D = {};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const PRE = document.documentElement.dataset.prerendered === '1'; // first screen was baked into the HTML at build time; redraws of it should not animate

/* ---------- theme */
const root = document.documentElement;
try { const t = localStorage.getItem('aii-theme'); if (t) root.dataset.theme = t; } catch (e) {}
const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
function paintMode() { const d = isDark(); document.getElementById('mode-dark').setAttribute('aria-pressed', String(d)); document.getElementById('mode-light').setAttribute('aria-pressed', String(!d)); }
function setTheme(t) { root.dataset.theme = t; try { localStorage.setItem('aii-theme', t); } catch (e) {} paintMode(); if (typeof drawAll === 'function' && window.__ready) drawAll(false); }
document.getElementById('mode-dark').addEventListener('click', () => setTheme('dark'));
document.getElementById('mode-light').addEventListener('click', () => setTheme('light'));
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (!root.dataset.theme) paintMode(); });
paintMode();

/* ---------- helpers */
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const txt = (s) => document.createTextNode(s);
const fmtDate = d3.utcFormat('%b %-d, %Y');
const fmtDay = d3.utcFormat('%b %-d');
const fmtMonth = d3.utcFormat('%b %Y');
const fmtN = d3.format(',');
const showDate = (r) => r.date_precision === 'month' ? fmtMonth(new Date(r.date)) : fmtDate(new Date(r.date));
const cssVar = (n) => getComputedStyle(root).getPropertyValue(n).trim();
const AUTONOMY = [
  { k: 0, name: 'Tool', desc: 'a person misused it' },
  { k: 1, name: 'Relied on', desc: 'people trusted bad output' },
  { k: 2, name: 'Acted', desc: 'the AI took a bounded action' },
  { k: 3, name: 'Autonomous', desc: 'the AI ran multi-step operations' },
  { k: 4, name: 'Against intent', desc: 'the AI worked against its operator' },
];
const autoColor = (a) => ['var(--mist)', 'color-mix(in oklab, var(--mist) 50%, var(--steel))', 'var(--steel)', 'color-mix(in oklab, var(--steel) 45%, var(--indigo))', 'var(--indigo)'][a];
const TIERS = [{ name: 'Minor', lo: 0, hi: 20 }, { name: 'Moderate', lo: 20, hi: 40 }, { name: 'Serious', lo: 40, hi: 60 }, { name: 'Severe', lo: 60, hi: 80 }, { name: 'Critical', lo: 80, hi: 100 }];
const tierText = (t) => ({ Minor: 'var(--ink-2)', Moderate: 'var(--amber-text)', Serious: 'var(--amber-text)', Severe: 'var(--alarm)', Critical: 'color-mix(in oklab, var(--alarm) 70%, var(--ink))' }[t]);
const tierColor = (t) => ({ Minor: 'var(--line-2)', Moderate: 'color-mix(in oklab, var(--amber) 45%, var(--line-2))', Serious: 'var(--amber)', Severe: 'var(--alarm)', Critical: 'color-mix(in oklab, var(--alarm) 70%, var(--ink))' }[t]);
const toastEl = document.getElementById('toast');
let toastT;
const toast = (m) => { toastEl.textContent = m; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 1600); };
async function copy(text) {
  try { await navigator.clipboard.writeText(text); toast('Copied'); return true; }
  catch (e) {
    try { const ta = el('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.append(ta); ta.select(); document.execCommand('copy'); ta.remove(); toast('Copied'); return true; }
    catch (e2) { toast('Copy failed'); return false; }
  }
}
const ICON = {
  link: '<svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
  text: '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>',
  img: '<svg viewBox="0 0 24 24"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M4 19h16"/></svg>',
  x: '<svg viewBox="0 0 24 24"><path d="M4 4l16 16"/><path d="M20 4 4 20"/></svg>',
  embed: '<svg viewBox="0 0 24 24"><path d="m8 7-5 5 5 5"/><path d="m16 7 5 5-5 5"/><path d="m14 4-4 16"/></svg>',
};
/* A clip on X: show its poster frame with a play button; a tap swaps the card for X's own embedded post, which plays the clip.
   X's script loads only on that tap, so pages stay fast and nothing is fetched from X until a reader asks for it. */
function xClip(t, x, card, item) {
  const v = el('div', 'tw-vid'); const im = el('img'); im.src = t.video.poster; im.alt = 'Video from ' + (t.name || x.author || 'X'); im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = () => v.remove();
  const b = el('button', 'tw-play'); b.type = 'button'; b.setAttribute('aria-label', 'Play the clip here (loads it from X)'); b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
  v.append(im, b); if (t.video.ms) { const s = Math.round(t.video.ms / 1000); v.append(el('span', 'tw-dur', Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'))); }
  v.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation();
    const box = el('div', 'tw-embed'); box.append(el('p', 'tw-load', 'Loading the clip from X…')); card.replaceWith(box);
    const go = () => window.twttr.widgets.createTweet(t.id, box, { theme: isDark() ? 'dark' : 'light', dnt: true, conversation: 'none', align: 'center' }).then((n) => { const l = box.querySelector('.tw-load'); if (n && l) l.remove(); if (!n && l) { l.replaceChildren(txt('X didn’t load the clip. ')); const a = el('a', null, 'Watch it on X →'); a.href = x.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; l.append(a); } });
    if (window.twttr && window.twttr.widgets) go(); else { const sc = document.createElement('script'); sc.src = 'https://platform.twitter.com/widgets.js'; sc.async = true; sc.onload = () => window.twttr.ready(go); sc.onerror = () => { location.href = x.url; }; document.head.append(sc); } });
  return v;
}
function shareRow(node, o) {
  if (!node) return;
  node.replaceChildren();
  const m0 = o.anchor && /^(i|c|m)=/.exec(o.anchor); const link = m0 ? SITE + m0[1] + '/' + encodeURIComponent(o.anchor.slice(2)) + '/' : SITE + (o.anchor ? '#' + o.anchor : '');
  const mk = (icon, label, fn) => { const b = el('button'); b.type = 'button'; b.innerHTML = ICON[icon]; b.append(txt(' ' + label)); b.addEventListener('click', (e) => { e.stopPropagation(); fn(); }); return b; };
  node.append(mk('link', 'Copy link', () => copy(link)));
  if (o.text) node.append(mk('text', 'Copy text', () => copy(o.text + ' ' + link)));
  if (o.text) { const a = el('a'); a.innerHTML = ICON.x; a.append(txt(' Post on X')); a.href = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(o.text) + '&url=' + encodeURIComponent(link); a.target = '_blank'; a.rel = 'noopener noreferrer'; node.append(a); }
  if (o.svgBox) node.append(mk('img', 'Save image', () => svgToPng(o.svgBox, o.name || 'chart', o.title || '')));
  if (o.embed) node.append(mk('embed', 'Embed', () => copy(`<iframe src="${SITE}?embed=${o.embed}" width="100%" height="${o.embedH || 560}" style="border:0;max-width:100%" loading="lazy" title="${(o.title || 'Warning Shots').replace(/"/g, '')}"></iframe>`)));
  if (o.card) node.append(mk('card', 'Briefing card', () => briefingCard(o.card)));
  if (m0) { const a = el('a'); a.innerHTML = ICON.page; a.append(txt(' Full page')); a.href = link; node.append(a); }
}
ICON.card = '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M7 8h10M7 12h10M7 16h6"/></svg>';
ICON.page = '<svg viewBox="0 0 24 24"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/></svg>';

/* ---------- briefing cards: 1080 x 1080, generated from the same structured content as the page */
function wrapText(ctx, text, maxW, maxLines) {
  const words = String(text || '').split(/\s+/).filter(Boolean), lines = []; let line = '';
  for (const w of words) { const t = line ? line + ' ' + w : w; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; if (lines.length === maxLines) break; }
  if (lines.length < maxLines && line) lines.push(line);
  if (lines.length === maxLines && words.join(' ') !== lines.join(' ')) { let last = lines[maxLines - 1]; while (ctx.measureText(last + '…').width > maxW && last.length) last = last.slice(0, -1).trimEnd(); lines[maxLines - 1] = last + '…'; }
  return lines;
}
async function drawCard(c, W, H) {
  try { await Promise.all([document.fonts.load('900 66px Playfair'), document.fonts.load('400 34px Archivo'), document.fonts.load('800 28px Archivo'), document.fonts.load('600 26px Archivo')]); } catch (e) {}
  const cv = el('canvas'); cv.width = W; cv.height = H; const x = cv.getContext('2d');
  const NAVY = '#0A111E', BONE = '#F4F3EF', RED = '#FF3300', MUTE = '#A8B3C2', SLATE = '#2A364B';
  const wide = W > H, P = wide ? 60 : 72, k = wide ? 0.82 : 1; // scale type on the landscape card
  x.fillStyle = NAVY; x.fillRect(0, 0, W, H);
  const top = wide ? 54 : 72;
  x.fillStyle = BONE; x.font = `900 ${Math.round(92 * k)}px Playfair`; x.textBaseline = 'alphabetic'; x.fillText('W', P, top + 78 * k);
  const wW = x.measureText('W').width; x.fillStyle = RED; x.beginPath(); x.arc(P + wW + 22 * k, top + 36 * k, 11 * k, 0, Math.PI * 2); x.fill(); x.fillStyle = BONE; x.beginPath(); x.arc(P + wW + 22 * k, top + 70 * k, 11 * k, 0, Math.PI * 2); x.fill();
  x.font = `800 ${Math.round(30 * k)}px Archivo`; x.fillStyle = BONE; let wx = P + wW + 58 * k; for (const ch of 'WARNING SHOTS') { x.fillText(ch, wx, top + 64 * k); wx += x.measureText(ch).width + 3 * k; }
  x.font = `600 ${Math.round(24 * k)}px Archivo`; x.fillStyle = MUTE; x.textAlign = 'right'; x.fillText(c.kicker || '', W - P, top + 64 * k); x.textAlign = 'left';
  const rule = top + 112 * k; x.fillStyle = SLATE; x.fillRect(P, rule, W - 2 * P, 2);
  const maxLines = wide ? 3 : 4; let size = wide ? 54 : 64, lines;
  for (;;) { x.font = `900 ${size}px Playfair`; lines = wrapText(x, c.headline, W - 2 * P, maxLines + 1); if (lines.length <= maxLines || size <= 40) break; size -= 4; }
  x.fillStyle = BONE; let y = rule + 34 * k + size; lines.forEach((l) => { x.fillText(l, P, y); y += size * 1.12; });
  y += 10 * k; const fs = wide ? 26 : 32; x.font = `400 ${fs}px Archivo`; x.fillStyle = MUTE;
  const footTop = H - (wide ? 118 : 150), room = Math.max(1, Math.floor((footTop - 96 * k - y) / (fs * 1.38)));
  wrapText(x, c.finding, W - 2 * P, Math.min(wide ? 3 : 5, room)).forEach((l) => { x.fillText(l, P, y); y += fs * 1.38; });
  let by = Math.max(y + 18 * k, footTop - 92 * k);
  if (c.impact) { x.strokeStyle = RED; x.lineWidth = 3; x.font = `700 ${Math.round(26 * k)}px Archivo`; const tw = x.measureText(c.impact).width + 36 * k; x.strokeRect(P, by, tw, 50 * k); x.fillStyle = RED; x.fillText(c.impact, P + 18 * k, by + 35 * k); x.fillStyle = MUTE; x.font = `400 ${Math.round(24 * k)}px Archivo`; wrapText(x, c.evidence || '', W - 2 * P - tw - 24 * k, 2).forEach((l, i) => x.fillText(l, P + tw + 24 * k, by + 24 * k + i * 30 * k)); }
  else if (c.evidence) { x.fillStyle = MUTE; x.font = `400 ${Math.round(24 * k)}px Archivo`; wrapText(x, c.evidence, W - 2 * P, 2).forEach((l, i) => x.fillText(l, P, by + 24 * k + i * 30 * k)); }
  x.fillStyle = SLATE; x.fillRect(P, footTop, W - 2 * P, 2);
  x.font = `600 ${Math.round(26 * k)}px Archivo`; x.fillStyle = BONE; x.fillText('warningshots.ai', P, footTop + 50 * k);
  x.font = `400 ${Math.round(24 * k)}px Archivo`; x.fillStyle = MUTE; x.fillText('See what’s coming. Know what it means for you.', P, footTop + 86 * k);
  x.textAlign = 'right'; x.fillText(c.stamp || ('As of ' + fmtET(D.meta.as_of)), W - P, footTop + 86 * k); x.textAlign = 'left';
  return cv;
}
async function briefingCard(c) {
  toast('Rendering card');
  const cv = await drawCard(c, 1080, 1080);
  cv.toBlob((blob) => { if (!blob) { toast('Could not render card'); return; } showCard(blob, c.name || 'briefing-card'); }, 'image/png');
}
function showCard(blob, name) {
  let m = document.getElementById('card-modal');
  if (!m) { m = el('div', 'card-modal'); m.id = 'card-modal'; m.innerHTML = '<div class="card-box"><img alt="Briefing card preview"><div class="card-actions"></div></div>'; m.addEventListener('click', (e) => { if (e.target === m) m.remove(); }); document.body.append(m); }
  const img = m.querySelector('img'), url = URL.createObjectURL(blob); img.src = url;
  const acts = m.querySelector('.card-actions'); acts.replaceChildren();
  const mk = (label, fn) => { const b = el('button', 'more-btn', label); b.type = 'button'; b.addEventListener('click', fn); return b; };
  acts.append(mk('Download PNG', () => { const a = el('a'); a.href = url; a.download = 'warning-shots-' + name + '.png'; a.click(); toast('Saved'); }));
  if (navigator.clipboard && window.ClipboardItem) acts.append(mk('Copy image', async () => { try { await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]); toast('Image copied'); } catch (e) { toast('Copy not supported here'); } }));
  if (navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], name + '.png', { type: 'image/png' })] })) acts.append(mk('Share…', async () => { try { await navigator.share({ files: [new File([blob], 'warning-shots-' + name + '.png', { type: 'image/png' })], title: 'Warning Shots' }); } catch (e) {} }));
  acts.append(mk('Close', () => m.remove()));
  m.querySelector('.more-btn').focus();
}
const cardForIncident = (r) => ({ name: r.ws.toLowerCase(), kicker: r.ws + '  ·  ' + showDate(r), headline: r.title, finding: (r.summary || '').split('. ').slice(0, 2).join('. ').replace(/\.?$/, '.'), impact: r.level + ' ' + r.tier.toUpperCase() + '  ·  ' + r.severity + '/100', evidence: 'Evidence: ' + (r.source_label ? r.source_label : 'primary source linked') + (r.confidence ? '; confidence ' + r.confidence : '') + '. Rated by a published formula; ' + (r.setting === 'wild' ? 'real-world incident.' : 'lab or test finding.') });
const cardForCase = (f) => { const cur = fixCur(f); const r = C.scored.find((x) => x.id === f.incident_id); return { name: 'case-' + f.incident_id, kicker: 'DID THEY FIX IT?  ·  ' + (cur.date ? fmtDate(new Date(cur.date)) : ''), headline: f.name, finding: f.one_liner || cur.note || '', impact: (FIXST[cur.status] || cur.status).toUpperCase(), evidence: 'Chain: report → response → claimed fix → independent check → now. ' + (f.what_would_change_it ? 'What would change it: ' + f.what_would_change_it : '') }; };
const cardForCap = (c) => ({ name: 'milestone-' + c.id, kicker: 'WHAT AI CAN NOW DO  ·  ' + (c.date_precision === 'month' ? fmtMonth(new Date(c.date)) : fmtDate(new Date(c.date))), headline: c.title, finding: c.what || '', impact: c.metric_value ? (c.metric_value + (c.metric_label ? '  ·  ' + c.metric_label : '')).toUpperCase().slice(0, 40) : '', evidence: 'Demonstrated ' + stStatus(c, 'demonstrated') + ', reproduced ' + stStatus(c, 'reproduced') + ', accessible ' + stStatus(c, 'accessible') + ', reliable ' + stStatus(c, 'reliable') + ', real consequences ' + stStatus(c, 'consequences') + '. ' + (c.org || '') });
window.WS = { async card(kind, id, W, H) { const c = kind === 'i' ? cardForIncident(C.scored.find((r) => r.id === id)) : kind === 'c' ? cardForCase(fixRows().find((f) => f.incident_id === id)) : kind === 'm' ? cardForCap(capRows().find((x) => x.id === id)) : kind === 'n' ? cardForNews(newsItems().find((n) => n.id === id)) : null; if (!c) return null; c.stamp = ' '; const cv = await drawCard(c, W || 1200, H || 630); return cv.toDataURL('image/jpeg', 0.88); }, ids() { const sn = newsItems().find((n) => n.siren); return { i: C.scored.map((r) => r.id), c: fixRows().map((f) => f.incident_id), m: capRows().map((c) => c.id), n: sn ? [sn.id] : [] }; } };
const cardForNews = (n) => ({ name: 'wire-' + (n.id || 'story'), kicker: 'THE WIRE  ·  ' + fmtDate(new Date(n.published)), headline: n.title, finding: n.summary || '', evidence: 'Reported by ' + [n.outlet].concat((n.also || []).map((a) => a.outlet)).reduce((acc, o, i, arr) => acc + (i === 0 ? '' : i === arr.length - 1 ? ' and ' : ', ') + o, '') + '. Headline by Warning Shots; the story is the outlet’s.', stamp: 'Board as of ' + fmtET(D.meta.as_of) });
let fontB64 = null;
async function fontData() {
  if (fontB64 !== null) return fontB64;
  try { const b = await (await fetch('/assets/fonts/archivo-latin-standard-normal.woff2')).arrayBuffer(); let s = ''; const u = new Uint8Array(b); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); fontB64 = btoa(s); }
  catch (e) { fontB64 = ''; }
  return fontB64;
}
async function svgToPng(box, name, title) {
  const src = box.querySelector('svg'); if (!src) return;
  toast('Rendering image');
  const PROPS = ['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin', 'opacity', 'font-size', 'font-family', 'font-weight', 'text-anchor', 'fill-opacity', 'stroke-opacity'];
  const W = box.clientWidth, H = src.getBoundingClientRect().height;
  const clone = src.cloneNode(true);
  const srcAll = src.querySelectorAll('*'), cloneAll = clone.querySelectorAll('*');
  srcAll.forEach((s, i) => { const cs = getComputedStyle(s); const c = cloneAll[i]; if (!c) return; PROPS.forEach((p) => { const v = cs.getPropertyValue(p); if (v) c.style.setProperty(p, v); }); if (cs.display === 'none') c.remove(); });
  const pad = 24, head = title ? 54 : 24, foot = 34;
  const out = d3.create('svg').attr('xmlns', 'http://www.w3.org/2000/svg').attr('width', W + pad * 2).attr('height', H + head + foot);
  const f = await fontData();
  if (f) out.append('style').text(`@font-face{font-family:'Archivo';src:url(data:font/woff2;base64,${f}) format('woff2');font-weight:400 900;font-stretch:78% 100%;} text{font-family:'Archivo',system-ui,sans-serif}`);
  out.append('rect').attr('width', '100%').attr('height', '100%').attr('fill', cssVar('--paper'));
  if (title) out.append('text').attr('x', pad).attr('y', 34).attr('font-size', 18).attr('font-weight', 600).attr('fill', cssVar('--ink')).attr('font-family', 'Archivo, system-ui, sans-serif').text(title);
  out.append('text').attr('x', pad).attr('y', H + head + 20).attr('font-size', 12).attr('fill', cssVar('--ink-2')).attr('font-family', 'Archivo, system-ui, sans-serif').text('Warning Shots, the AI Incident Index: ' + SITE.replace(/^https?:\/\//, ''));
  clone.setAttribute('x', pad); clone.setAttribute('y', head); clone.setAttribute('width', W); clone.setAttribute('height', H);
  out.node().append(clone);
  const xml = new XMLSerializer().serializeToString(out.node());
  const img = new Image();
  const scale = 2;
  img.onload = () => {
    const c = el('canvas'); c.width = (W + pad * 2) * scale; c.height = (H + head + foot) * scale;
    const ctx = c.getContext('2d'); ctx.scale(scale, scale); ctx.drawImage(img, 0, 0);
    c.toBlob((blob) => { const a = el('a'); a.href = URL.createObjectURL(blob); a.download = 'warning-shots-' + name + '.png'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); toast('Image saved'); }, 'image/png');
  };
  img.onerror = () => toast('Could not render image');
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(xml);
}
function makeTip(container) {
  let tip = container.querySelector(':scope > .tip');
  if (!tip) { tip = el('div', 'tip'); container.appendChild(tip); }
  return {
    show(nodes, x, y) {
      tip.replaceChildren(...nodes); tip.classList.add('on');
      const cw = container.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
      let left = x + 14; if (left + tw > cw) left = Math.max(0, x - tw - 14);
      let top = y - th - 10; if (top < 0) top = y + 14;
      tip.style.left = left + 'px'; tip.style.top = top + 'px';
    },
    hide() { tip.classList.remove('on'); },
  };
}
const keepTip = (box, svg) => box.replaceChildren(svg, box.querySelector(':scope > .tip') || el('div', 'tip'));
function incidentTip(r) {
  const a = el('div', 't-sec', showDate(r) + (r.actors ? ', ' + r.actors : ''));
  const b = el('div', 't-title', r.title);
  const c = el('div'); c.append(el('span', 't-val', r.severity + '/100 '), el('span', 't-sec', r.tier + ', ' + AUTONOMY[+r.A].name.toLowerCase() + ', ' + (r.setting === 'wild' ? 'in the wild' : 'in the lab')));
  return [a, b, c, el('div', 't-cta', 'Click to open')];
}
function legend(node, items) {
  if (!node) return;
  node.replaceChildren(...items.map((it) => {
    const s = el('span');
    if (it.ramp) { const r = el('span', 'ramp'); it.ramp.forEach((c) => { const i = el('i'); i.style.background = c; r.append(i); }); s.append(r, txt(it.label)); return s; }
    const i = el('i', it.shape || ''); i.style.background = it.color; if (it.shape === 'ring') { i.style.borderColor = it.color; i.style.background = 'transparent'; }
    s.append(i, txt(it.label)); return s;
  }));
}
const fail = (node) => { if (node) node.replaceChildren(el('div', 'fail', 'Could not load this data')); };
const axisClean = (g) => g.attr('font-size', null).attr('font-family', null);
const sevScore = (r) => { const H = +r.H, R = +r.R, A = +r.A, N = +r.N, I = +r.I; const harm = 100 * (0.5 * H / 5 + 0.25 * R / 5 + 0.25 * I / 5); const signal = 100 * (0.6 * A / 4 + 0.4 * N / 5); const severity = Math.round(0.55 * harm + 0.45 * signal); const tier = severity >= 80 ? 'Critical' : severity >= 60 ? 'Severe' : severity >= 40 ? 'Serious' : severity >= 20 ? 'Moderate' : 'Minor'; return { harm_score: Math.round(harm), signal_score: Math.round(signal), severity, tier }; };
const revealed = new Set();
const io = ('IntersectionObserver' in window) ? new IntersectionObserver((entries) => { entries.forEach((e) => { if (e.isIntersecting) { const fn = e.target._reveal; if (fn) { e.target._reveal = null; fn(); } io.unobserve(e.target); } }); }, { threshold: 0.25 }) : null;
function onVisible(node, key, fn) {
  if (reduced || revealed.has(key) || !io) { revealed.add(key); fn(true); return; }
  node._reveal = () => { revealed.add(key); fn(false); }; io.observe(node);
}
function countUp(node, text, key) {
  const m = /^([^\d]*)([\d,]*\.?\d+)(.*)$/.exec(text);
  if (!m || reduced || revealed.has(key)) { node.textContent = text; revealed.add(key); return; }
  const target = parseFloat(m[2].replace(/,/g, '')), dec = (m[2].split('.')[1] || '').length, hasComma = m[2].includes(',');
  node.textContent = m[1] + (0).toFixed(dec) + m[3];
  onVisible(node, key, (instant) => {
    if (instant) { node.textContent = text; return; }
    const t0 = performance.now(), dur = 900;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3); const v = target * e; node.textContent = m[1] + (hasComma ? d3.format(',.' + dec + 'f')(v) : v.toFixed(dec)) + m[3]; if (k < 1) requestAnimationFrame(step); else node.textContent = text; };
    requestAnimationFrame(step);
  });
}
const NEW_WINDOW = 48 * 3.6e6;
const isNew = (iso) => iso && D.meta && (Date.parse(D.meta.as_of) - Date.parse(iso)) < NEW_WINDOW && Date.parse(iso) <= Date.parse(D.meta.as_of) + 864e5;
const ET = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
const ETt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' });
const ETd = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric' });
const fmtET = (iso) => iso ? ET.format(new Date(iso)) + ' ET' : '';
const fmtETsmart = (iso) => { if (!iso) return ''; const d = new Date(iso); return (ETd.format(d) === ETd.format(new Date()) ? 'today ' + ETt.format(d) : ET.format(d)) + ' ET'; };
const relTime = (iso) => { const ms = Date.now() - Date.parse(iso); const h = Math.round(ms / 3.6e6); if (h < 1) return 'minutes ago'; if (h < 48) return h + (h === 1 ? ' hour ago' : ' hours ago'); return Math.round(h / 24) + ' days ago'; };

/* ---------- calcs */
const C = {};
function compute() {
  const asOf = D.meta.as_of.slice(0, 10);
  C.asOf = asOf;
  C.scored = D.incidents.map((r) => ({ ...r, ...sevScore(r) }));
  // a missed refresh must not leave a time in the past on the page: roll 'next' forward to the next scheduled edition (5:17, 12:17, 18:17 ET)
  if (D.meta.next_check && Date.parse(D.meta.next_check) < Date.now()) { const etH = (t) => +new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' }).format(t);
    const base = new Date(); let best = null; for (let d = 0; d <= 1 && !best; d++) for (const h of [5, 12, 18]) { const day = new Date(base.getTime() + d * 864e5); const ymd = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York' }).format(day).split('-').map(Number);
      let t = Date.UTC(ymd[0], ymd[1] - 1, ymd[2], h + 4, 17); if (etH(t) !== h) t += (h - etH(t)) * 3.6e6; if (t > Date.now() + 6e4) { best = t; break; } }
    if (best) D.meta.next_check = new Date(best).toISOString(); }
  C.scored.slice().sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id)).forEach((r, i) => { r.ws = 'WS-' + String(i + 1).padStart(4, '0'); r.level = 'WS-' + (TIERS.findIndex((t) => t.name === r.tier) + 1); });
  const t = Date.parse(asOf), yr = 365.25 * 864e5, d = (r) => Date.parse(r.date);
  const last12 = C.scored.filter((r) => d(r) > t - yr && d(r) <= t), prior12 = C.scored.filter((r) => d(r) > t - 2 * yr && d(r) <= t - yr);
  const wild = C.scored.filter((r) => r.setting === 'wild');
  const share = (rows) => rows.length ? rows.filter((r) => +r.A >= 3).length / rows.length : 0;
  const top = C.scored.slice().sort((a, b) => b.severity - a.severity)[0];
  C.headline = {
    severe_last12: last12.filter((r) => r.severity >= 60).length, severe_prior12: prior12.filter((r) => r.severity >= 60).length,
    agentic_recent: share(wild.filter((r) => d(r) > t - yr && d(r) <= t)), agentic_early: share(wild.filter((r) => r.date < '2025-01-01')),
    n: C.scored.length, n_wild: wild.length, n_lab: C.scored.length - wild.length, top, n_critical: C.scored.filter((r) => r.tier === 'Critical').length,
    n_named: D.victims.filter((v) => v.status_group !== 'unnamed').length, n_dives: D.deepdives.length,
  };
  const qs = []; for (let y = 2023; y <= +asOf.slice(0, 4); y++) for (let q = 1; q <= 4; q++) qs.push(y + ' Q' + q);
  const curQ = asOf.slice(0, 4) + ' Q' + (Math.floor((+asOf.slice(5, 7) - 1) / 3) + 1);
  C.quarterly = qs.filter((q) => q <= curQ).map((quarter) => { const rows = C.scored.filter((r) => r.date.slice(0, 4) + ' Q' + (Math.floor((+r.date.slice(5, 7) - 1) / 3) + 1) === quarter); const o = { quarter, n: rows.length, max: rows.length ? Math.max(...rows.map((r) => r.severity)) : 0, partial: quarter === curQ }; for (let a = 0; a <= 4; a++) o['a' + a] = rows.filter((r) => +r.A === a).length; return o; });
  const m = (a, b) => Math.round((b - a) / (30.44 * 864e5));
  C.lags = D.pipeline.map((p) => ({ behavior: p.behavior, lab_year: +p.lab_date.slice(0, 4), lag: p.wild_date ? m(Date.parse(p.lab_date), Date.parse(p.wild_date)) : null }));
  const closed = C.lags.filter((r) => r.lag !== null).map((r) => r.lag).sort((a, b) => a - b);
  C.lagAgg = { n_arrived: closed.length, n_open: C.lags.length - closed.length, median: d3.median(closed), early: Math.round(d3.mean(C.lags.filter((r) => r.lag !== null && r.lab_year < 2025), (r) => r.lag)), recent: Math.round(d3.mean(C.lags.filter((r) => r.lag !== null && r.lab_year >= 2025), (r) => r.lag)) };
  C.disclosure = C.scored.filter((r) => r.disclosed && r.setting === 'wild' && +r.A >= 3 && r.date >= '2026-01-01').map((r) => ({ ...r, lag: Math.max(0, Math.round((Date.parse(r.disclosed) - Date.parse(r.date)) / 864e5)) })).sort((a, b) => a.date.localeCompare(b.date));
  const slow = C.disclosure.filter((r) => r.lag > 60);
  const mon = C.scored.find((r) => r.id === 'monitor-disabled');
  C.discAgg = { n: C.disclosure.length, n_slow: slow.length, median_slow: Math.round(d3.median(slow, (r) => r.lag)), max: d3.max(C.disclosure, (r) => r.lag), n_fast: C.disclosure.filter((r) => r.lag <= 14).length, monitor_lag: mon && mon.disclosed ? Math.round((Date.parse(mon.disclosed) - Date.parse(mon.date)) / 864e5) : null };
  C.victimCounts = {};
  D.deepdives.forEach((dd) => { const vs = D.victims.filter((v) => v.incident_id === dd.incident_id); const n = (v) => (v.count === '' || v.count == null || isNaN(+v.count)) ? 1 : +v.count; const c = (g) => vs.filter((v) => v.status_group === g).reduce((s, v) => s + n(v), 0); C.victimCounts[dd.incident_id] = { rows: vs.length, confirmed: c('confirmed'), reported: c('reported'), attacked: c('attacked'), disrupted: c('disrupted'), other: c('other'), unnamed: c('unnamed') }; });
}

/* ---------- hero */
function drawHeadline() {
  const h = C.headline;
  const H = document.getElementById('headline');
  H.replaceChildren(txt('AI has started breaking in '), el('b', null, 'on its own.'));
  const sub = document.getElementById('sub');
  sub.replaceChildren(txt('Severe AI incidents went from '), el('b', null, String(h.severe_prior12)), txt(' to '), el('b', null, String(h.severe_last12)), txt(' in a year. In '), el('b', null, Math.round(h.agentic_recent * 100) + '%'), txt(" of this year's real-world cases the AI itself did the acting: into a national health portal, government data sites, its own developers' servers and dozens of organizations, with nobody telling it to. Most of what happened inside the labs in the last three months is still undisclosed."));
  const stats = document.getElementById('hero-stats');
  const stat = (v, l, cls, small) => { const s = el('div', 'stat' + (cls ? ' ' + cls : '')); const vv = el('div', 'v'); const num = el('span'); countUp(num, v, 'stat:' + l.map((n) => n.textContent).join('').slice(0, 30)); vv.append(num); if (small) vv.append(el('small', null, small)); const ll = el('div', 'l'); ll.append(...l); s.append(vv, ll); return s; };
  const pct = (x) => Math.round(x * 100) + '%';
  const crit = D.forecasts.find((f) => f.id === 'first-critical');
  stats.replaceChildren(
    stat(String(h.severe_last12), [txt('severe incidents in the last 12 months, against '), el('b', null, String(h.severe_prior12)), txt(' in the 12 before')], 'alarm'),
    stat(pct(h.agentic_recent), [txt('of real-world incidents this year where the AI acted on its own, up from '), el('b', null, pct(h.agentic_early)), txt(' in 2023–24')]),
    stat(String(h.top.severity), [txt('highest score on record: '), el('b', null, h.top.title)], '', '/100'),
    stat(fmtN(h.n_named), [txt('organizations publicly named as hit across the '), el('b', null, String(h.n_dives)), txt(' biggest incidents')]),
    stat(fmtN(h.n), [el('b', null, fmtN(h.n_wild)), txt(' real-world incidents and '), el('b', null, fmtN(h.n_lab)), txt(' lab or test findings, scored')]),
    stat(h.n_critical === 0 ? 'None' : String(h.n_critical), [txt(h.n_critical === 0 ? 'rated Critical yet. Odds of one within 12 months: ' : 'rated Critical. Odds of another within 12 months: '), el('b', null, crit ? crit.probability_label : '—')]),
  );
  shareRow(document.getElementById('hero-share'), { anchor: 'record', text: `AI has started breaking in on its own. Severe AI incidents went from ${h.severe_prior12} to ${h.severe_last12} in a year; in ${pct(h.agentic_recent)} of this year's real-world cases the AI itself did the acting. Warning Shots:`, svgBox: document.getElementById('ch-timeline'), name: 'escalation', title: `Every major AI incident since 2023, scored 0–100 (severe: ${h.severe_prior12} → ${h.severe_last12} in a year)`, embed: 'timeline', embedH: 560 });
  const up = document.getElementById('tb-updated');
  const tickUp = () => { const ms = Date.now() - Date.parse(D.meta.as_of); const mins = Math.max(0, Math.round(ms / 6e4)); const nx = D.meta.next_check ? Date.parse(D.meta.next_check) - Date.now() : null; const nxm = nx != null ? Math.round(nx / 6e4) : null; const nxs = nxm != null && nxm > 0 ? ', next check in ' + (nxm >= 60 ? Math.floor(nxm / 60) + 'h ' + (nxm % 60) + 'm' : nxm + ' min') : (nx != null ? (nxm <= -120 ? ', refresh overdue' : ', refresh due') : ''); const short = (mins < 60 ? 'Updated ' + mins + ' min ago' : 'Updated ' + relTime(D.meta.as_of)); up.textContent = short + nxs; up.title = 'Last refresh ' + fmtET(D.meta.as_of) + '. ' + D.meta.schedule; const nu = document.getElementById('nav-updated'); if (nu) nu.textContent = short; };
  tickUp(); clearInterval(window._tickUp); window._tickUp = setInterval(tickUp, 30000);
  // Say so plainly when the page is behind: two missed refresh windows (14 hours) without a new as_of.
  const staleCheck = () => { const hrs = (Date.now() - Date.parse(D.meta.as_of)) / 3.6e6; let bar = document.getElementById('stale'); if (hrs < 14) { if (bar) bar.remove(); return; } if (!bar) { bar = el('div', 'stale wrap'); bar.id = 'stale'; bar.setAttribute('role', 'status'); document.getElementById('ticker').before(bar); } bar.replaceChildren(el('b', null, 'This page is behind. '), txt('The last refresh was ' + Math.round(hrs) + ' hours ago and the scheduled runs (6:37, 12:37 and 18:37 ET) have not published since. The Wire and the brief may be stale; the record, scores and sources are unaffected.')); };
  staleCheck(); clearInterval(window._staleT); window._staleT = setInterval(staleCheck, 60000);
  document.getElementById('foot-updated').textContent = fmtET(D.meta.as_of) + '. ' + D.meta.schedule + ' Next check ' + fmtETsmart(D.meta.next_check) + '.';
}
let heroAnimated = false;
function drawTimeline(animate) {
  const box = document.getElementById('ch-timeline');
  if (!box.clientWidth) return;
  const rows = C.scored.map((r) => ({ ...r, _d: new Date(r.date) }));
  const W = box.clientWidth, narrow = W < 560, H = narrow ? 320 : 400;
  const m = { t: 14, r: narrow ? 8 : 74, b: 28, l: 34 };
  const today = new Date(C.asOf);
  const x = d3.scaleUtc([new Date('2023-01-01'), d3.utcMonth.offset(today, 2)], [m.l, W - m.r]);
  const y = d3.scaleLinear([0, 100], [H - m.b, m.t]);
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Every incident by date and severity');
  const bands = svg.append('g');
  TIERS.forEach((t, i) => {
    bands.append('rect').attr('x', m.l).attr('width', W - m.l - m.r).attr('y', y(t.hi)).attr('height', y(t.lo) - y(t.hi)).attr('fill', i >= 3 ? 'var(--alarm)' : 'var(--ink)').attr('opacity', i === 4 ? 0.07 : i === 3 ? 0.035 : (i % 2 ? 0.025 : 0));
    if (!narrow) bands.append('text').attr('x', W - m.r + 10).attr('y', (y(t.hi) + y(t.lo)) / 2).attr('dy', '0.35em').attr('font-size', 11.5).attr('fill', i >= 3 ? 'var(--alarm)' : 'var(--ink-2)').text(t.name);
  });
  svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues([20, 40, 60, 80, 100]).tickSize(-(W - m.l - m.r)).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat(d3.utcFormat('%Y')).tickSizeOuter(0)).call(axisClean);
  svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues([0, 20, 40, 60, 80, 100]).tickSizeOuter(0)).call(axisClean).call((g) => g.select('.domain').remove());
  svg.append('line').attr('x1', x(today)).attr('x2', x(today)).attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--line-2)').attr('stroke-dasharray', '3 3');
  svg.append('text').attr('x', x(today) - 5).attr('y', m.t + 10).attr('text-anchor', 'end').attr('font-size', 11).attr('fill', 'var(--ink-2)').text('Today');
  const wild = rows.filter((r) => r.setting === 'wild').sort((a, b) => a._d - b._d);
  const pts = [];
  for (let tt = new Date('2023-06-30'); tt <= today; tt = d3.utcMonth.offset(tt, 1)) { const win = wild.filter((r) => r._d <= tt && r._d > d3.utcMonth.offset(tt, -6)); if (win.length >= 2) pts.push([tt, d3.mean(win, (r) => r.severity)]); }
  const path = svg.append('path').attr('d', d3.line().x((p) => x(p[0])).y((p) => y(p[1]))(pts)).attr('fill', 'none').attr('stroke', 'var(--ink)').attr('stroke-width', 2).attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round').attr('opacity', 0.5);
  if (pts.length && !narrow) { const p0 = pts[0]; svg.append('text').attr('x', x(p0[0]) + 4).attr('y', y(p0[1]) - 10).attr('font-size', 11).attr('fill', 'var(--ink-3)').text('6-month average, real-world'); }
  const kind = (r) => r.setting !== 'wild' ? 'lab' : +r.A >= 3 ? 'auto' : 'wild';
  const sorted = rows.slice().sort((a, b) => ({ lab: 0, wild: 1, auto: 2 })[kind(a)] - ({ lab: 0, wild: 1, auto: 2 })[kind(b)]);
  const R = narrow ? 4.5 : 5.5;
  const rOf = (r) => kind(r) === 'auto' ? R + 1.5 : kind(r) === 'wild' ? R - 0.5 : R - 1;
  const dots = svg.append('g').selectAll('circle').data(sorted).join('circle')
    .attr('cx', (r) => x(r._d)).attr('cy', (r) => y(r.severity)).attr('r', rOf)
    .attr('fill', (r) => kind(r) === 'auto' ? 'var(--alarm)' : kind(r) === 'wild' ? 'var(--steel)' : 'var(--paper)')
    .attr('stroke', (r) => kind(r) === 'lab' ? 'var(--ink-3)' : 'var(--paper)')
    .attr('stroke-width', (r) => kind(r) === 'lab' ? 1.6 : 1.5)
    .attr('opacity', (r) => kind(r) === 'lab' ? 0.75 : kind(r) === 'wild' ? 0.85 : 1);
  // per-year count of real-world incidents where the AI acted on its own
  const years = d3.groups(rows, (r) => r.date.slice(0, 4)).sort((a, b) => a[0].localeCompare(b[0]));
  const yc = svg.append('g');
  years.forEach(([yr, rs]) => {
    const n = rs.filter((r) => kind(r) === 'auto').length;
    const x0 = x(new Date(yr + '-01-01')), x1 = Math.min(x(new Date((+yr + 1) + '-01-01')), x(today));
    yc.append('text').attr('x', (x0 + x1) / 2).attr('y', H - m.b - 8).attr('text-anchor', 'middle').attr('font-size', narrow ? 12 : 13).attr('font-weight', 600).attr('fill', n ? 'var(--alarm)' : 'var(--ink-3)').text(n + (narrow ? '' : (n === 1 ? ' on its own' : ' on its own')));
  });
  const SHORT = { 'openai-hf-swarm': '700 agents breach Hugging Face', 'openai-medicare': 'Breaks into Australia’s Medicare portal', 'openai-dsewiki': 'Hijacks a wiki as a message board', 'php2shell': 'PHP2Shell: governments switch sites off', 'jadepuffer': 'Ransomware run end-to-end by AI', 'anthropic-three-orgs': 'Hacks three real companies in a test', 'gtg1002-claude-code-espionage': 'State espionage, mostly automated', 'replit-agent-deletes-saastr-db': 'Wipes a production database', 'korea-banks-artex': 'One hacker, one agent, seven banks', 'claude-false-tip': 'Files a fake murder tip with police' };
  const byYear = d3.groups(rows, (r) => r.date.slice(0, 4)).map(([, rs]) => rs.slice().sort((a, b) => b.severity - a.severity)[0]);
  const live = rows.find((r) => r.id === D.meta.live_incident);
  const picks = narrow ? ['openai-hf-swarm', 'php2shell'] : ['openai-hf-swarm', 'php2shell', 'openai-medicare', 'openai-dsewiki', 'gtg1002-claude-code-espionage'];
  const labels = narrow ? picks.map((id) => rows.find((r) => r.id === id)).filter(Boolean) : byYear.filter((r) => r.date < '2025').concat(picks.map((id) => rows.find((r) => r.id === id)).filter(Boolean));
  const lab = svg.append('g');
  const placed = [];
  labels.slice().sort((a, b) => a._d - b._d).forEach((r) => {
    const tx = x(r._d), ty = y(r.severity), anchor = tx > W * 0.6 ? 'end' : 'start';
    const short = SHORT[r.id] || (r.title.length > 44 ? r.title.slice(0, 42).trimEnd() + '…' : r.title);
    const w = short.length * 6.3, x0 = anchor === 'end' ? tx - 10 - w : tx + 10, x1 = x0 + w;
    let yy = ty - 10;
    for (let k = 0; k < 8; k++) { const hit = placed.find((b) => x0 < b.x1 + 8 && x1 > b.x0 - 8 && Math.abs(yy - b.y) < 15); if (!hit) break; yy = hit.y - 16; }
    placed.push({ x0, x1, y: yy });
    if (ty - yy > 16) lab.append('line').attr('x1', tx).attr('y1', ty - rOf(r) - 1).attr('x2', tx).attr('y2', yy + 3).attr('stroke', 'var(--ink-3)').attr('stroke-width', 1);
    lab.append('text').attr('x', tx + (anchor === 'end' ? -10 : 10)).attr('y', yy).attr('text-anchor', anchor).attr('font-size', 11.5).attr('font-weight', 600).attr('fill', kind(r) === 'auto' ? 'var(--ink)' : 'var(--ink-2)').text(short);
  });
  rows.filter((r) => isNew(r.disclosed || r.date)).forEach((r) => { svg.append('circle').attr('class', 'halo').attr('cx', x(r._d)).attr('cy', y(r.severity)).attr('r', 6).attr('fill', 'none').attr('stroke', kind(r) === 'auto' ? 'var(--alarm)' : 'var(--steel)').attr('stroke-width', 2).attr('pointer-events', 'none'); });
  const hi = svg.append('circle').attr('r', R + 4).attr('fill', 'none').attr('stroke', 'var(--ink)').attr('stroke-width', 1.5).attr('opacity', 0);
  const delaunay = d3.Delaunay.from(rows, (r) => x(r._d), (r) => y(r.severity));
  const tip = makeTip(box);
  svg.append('rect').attr('x', m.l).attr('y', 0).attr('width', W - m.l - m.r).attr('height', H - m.b).attr('fill', 'transparent').style('cursor', 'pointer')
    .on('pointermove', (ev) => { const [px, py] = d3.pointer(ev); const r = rows[delaunay.find(px, py)]; if (Math.hypot(x(r._d) - px, y(r.severity) - py) > 36) { tip.hide(); hi.attr('opacity', 0); return; } hi.attr('cx', x(r._d)).attr('cy', y(r.severity)).attr('opacity', 1); tip.show(incidentTip(r), x(r._d) * box.clientWidth / W, y(r.severity) * box.clientWidth / W); })
    .on('pointerleave', () => { tip.hide(); hi.attr('opacity', 0); })
    .on('click', (ev) => { const [px, py] = d3.pointer(ev); const r = rows[delaunay.find(px, py)]; if (r && Math.hypot(x(r._d) - px, y(r.severity) - py) <= 36) openIncident(r.id); });
  keepTip(box, svg.node());
  if (animate && !reduced && !heroAnimated) {
    const T = 2600, x0 = x.range()[0], x1 = x(today);
    const L = path.node().getTotalLength();
    dots.attr('r', 0); yc.attr('opacity', 0); lab.attr('opacity', 0); path.attr('stroke-dasharray', L + ' ' + L).attr('stroke-dashoffset', L);
    onVisible(box, 'hero-sweep', (instant) => {
      heroAnimated = true;
      if (instant) { dots.attr('r', rOf); yc.attr('opacity', 1); lab.attr('opacity', 1); path.attr('stroke-dashoffset', 0); return; }
      const sweep = svg.append('line').attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--alarm)').attr('stroke-width', 1.5).attr('x1', x0).attr('x2', x0).attr('opacity', 0.9);
      dots.transition().delay((r) => T * (Math.min(x(r._d), x1) - x0) / (x1 - x0)).duration(420).ease(d3.easeBackOut.overshoot(2.2)).attr('r', rOf);
      yc.transition().delay(T + 200).duration(500).attr('opacity', 1);
      path.transition().delay(T * (x(pts[0][0]) - x0) / (x1 - x0)).duration(T * (x(pts[pts.length - 1][0]) - x(pts[0][0])) / (x1 - x0)).ease(d3.easeLinear).attr('stroke-dashoffset', 0);
      lab.transition().delay(T + 200).duration(500).attr('opacity', 1);
      sweep.transition().duration(T).ease(d3.easeLinear).attr('x1', x1).attr('x2', x1).transition().duration(600).attr('opacity', 0).remove();
    });
  }
  legend(document.getElementById('lg-autonomy'), [{ color: 'var(--alarm)', label: 'real-world incident where the AI acted on its own' }, { color: 'var(--steel)', label: 'other real-world incident' }, { color: 'var(--ink-3)', shape: 'ring', label: 'lab or test finding' }, { color: 'var(--ink)', shape: 'bar', label: '6-month average, real-world' }]);
}

/* ---------- happening now */
const ISO = { Japan: 392, US: 840, 'United States': 840, Netherlands: 528, UK: 826, 'United Kingdom': 826, Belgium: 56, Australia: 36, Canada: 124, France: 250, 'Czech Republic': 203, Czechia: 203, Germany: 276, Finland: 246, Denmark: 208, 'South Korea': 410, Austria: 40, Slovenia: 705, Ireland: 372, Singapore: 702, Switzerland: 756, Spain: 724, Italy: 380, Sweden: 752, Norway: 578, Poland: 616, 'New Zealand': 554, Thailand: 764, India: 356, Brazil: 76, Mexico: 484, Kenya: 404, Taiwan: 158, Israel: 376, Estonia: 233, Portugal: 620, Luxembourg: 442, Slovakia: 703, Hungary: 348, Greece: 300, Romania: 642, Nigeria: 566, 'South Africa': 710, Indonesia: 360, Philippines: 608, Malaysia: 458, Vietnam: 704, Argentina: 32, Chile: 152, Colombia: 170, Turkey: 792, 'Saudi Arabia': 682, UAE: 784, Egypt: 818 };
const NAME = Object.fromEntries(Object.entries(ISO).map(([k, v]) => [v, k]));
NAME[840] = 'United States'; NAME[826] = 'United Kingdom';
function drawNow() {
  const live = D.deepdives.find((d) => d.incident_id === D.meta.live_incident) || D.deepdives[0];
  document.getElementById('now-title').textContent = live.name;
  document.getElementById('now-note').textContent = D.meta.live_note || live.now_text;
  document.getElementById('now-stamp').textContent = 'Checked ' + fmtET(D.meta.as_of) + (D.meta.next_check ? ', next check ' + fmtETsmart(D.meta.next_check) : '');
  document.getElementById('now-link').href = live.incident_id === 'php2shell' ? '/php2shell/' : '#d=' + live.incident_id;
  document.getElementById('now-link').textContent = live.incident_id === 'php2shell' ? 'The live tracker: am I affected, who was hit, what officials said' : 'Full breakdown: every organization, the map, the timeline';
  const grid = document.getElementById('live-grid');
  const since = D.meta.live_since ? Date.parse(D.meta.live_since) : null;
  const clock = since ? (() => { const c = el('div', 'live clock'); const v = el('div', 'v'); const upd = () => { const ms = Date.now() - since; const h = Math.floor(ms / 3.6e6), mn = Math.floor((ms % 3.6e6) / 6e4), sc = Math.floor((ms % 6e4) / 1000); v.textContent = h + 'h ' + String(mn).padStart(2, '0') + 'm ' + String(sc).padStart(2, '0') + 's'; }; upd(); clearInterval(window._liveClock); window._liveClock = setInterval(upd, 1000); c.append(v, el('div', 'l', D.meta.live_since_label || 'since the fix shipped')); c.append(el('div', 'd', 'Counting from the coordinated release. The gap between a patch and a working exploit is now measured in hours.')); return c; })() : null;
  grid.replaceChildren(...(clock ? [clock] : []), ...D.live.filter((r) => !(r.hide_while_zero && String(r.value).trim() === '0')).map((r) => {
    const good = (r.key === 'confirmed' && r.value === '0') || (r.key === 'kev' && /not/i.test(r.value));
    const c = el('div', 'live' + (good ? ' ok' : ''));
    const v = el('div', 'v'); if (PRE) v.textContent = r.value; else countUp(v, r.value, 'live:' + r.key); c.append(v, el('div', 'l', r.label));
    const d = el('div', 'd'); d.append(txt(r.detail + ' ')); const a = el('a', null, r.source_label); a.href = r.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; d.append(a); c.append(d);
    return c;
  }));
  shareRow(document.getElementById('now-share'), { anchor: 'now', text: `${live.name}. ${(D.meta.live_note || live.now_text)}`, embed: 'now', embedH: 640 });
}
let world = null;
async function drawMap(live) {
  const box = document.getElementById('map'), cap = document.getElementById('map-cap'), wrap = document.getElementById('map-wrap'), mid = document.getElementById('dd-mid');
  const vs = D.victims.filter((v) => v.incident_id === live.incident_id && ['disrupted', 'attacked', 'confirmed', 'reported'].includes(v.status_group));
  const byC = new Map();
  vs.forEach((v) => { const name = String(v.country || '').split(/[\/(]/)[0].trim(); const id = ISO[name]; if (!id) return; if (!byC.has(id)) byC.set(id, []); byC.get(id).push(v); });
  const show = byC.size >= 2;
  wrap.hidden = !show; mid.classList.toggle('has-map', show);
  if (!show) { box.replaceChildren(); cap.replaceChildren(); document.getElementById('map-bars').replaceChildren(); return; }
  if (!box.clientWidth) return;
  if (!world) { try { world = await (await fetch('/assets/vendor/countries-110m.json')).json(); } catch (e) { fail(box); return; } }
  const W = box.clientWidth, narrowMap = W < 420, H = Math.max(200, Math.round(W * 0.5));
  const countries = topojson.feature(world, world.objects.countries).features.filter((f) => f.id !== '010');
  const proj = d3.geoNaturalEarth1().fitExtent([[0, 0], [W, H]], { type: 'FeatureCollection', features: countries });
  const pathG = d3.geoPath(proj);
  const max = d3.max([...byC.values()], (a) => a.length) || 1;
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'World map of countries with organizations affected');
  const tip = makeTip(box);
  const showC = (ev, f) => { const list = byC.get(+f.id); if (!list) { tip.hide(); return; } const [px, py] = d3.pointer(ev, svg.node()); const lines = [el('div', 't-title', (NAME[+f.id] || f.properties.name) + ', ' + list.length + (list.length === 1 ? ' organization' : ' organizations'))]; list.slice(0, 8).forEach((v) => lines.push(el('div', 't-sec', v.organization + ': ' + v.status.toLowerCase()))); if (list.length > 8) lines.push(el('div', 't-sec', 'and ' + (list.length - 8) + ' more')); tip.show(lines, px * box.clientWidth / W, py * box.clientWidth / W); };
  svg.append('g').selectAll('path').data(countries).join('path').attr('d', pathG)
    .attr('fill', (f) => { const n = (byC.get(+f.id) || []).length; return n ? `color-mix(in oklab, var(--alarm) ${Math.round(30 + 70 * Math.sqrt(n / max))}%, var(--line))` : 'var(--line)'; })
    .attr('stroke', 'var(--paper)').attr('stroke-width', 0.6)
    .on('pointermove', showC).on('pointerleave', () => tip.hide());
  keepTip(box, svg.node());
  const nC = byC.size, nO = vs.length;
  cap.replaceChildren(el('span', null, `${nO} named organizations in ${nC} countries took services offline or were attacked. Hover a country for names.`));
  const bars = document.getElementById('map-bars');
  const list = [...byC.entries()].map(([id, l]) => ({ id, name: NAME[id] || String(id), n: l.length })).sort((a, b) => b.n - a.n);
  bars.replaceChildren(...list.map((c) => { const r = el('div', 'cbar'); const t = el('div', 'ct'); t.style.width = Math.max(4, 100 * c.n / max) + '%'; r.append(el('span', 'cn', c.name), (() => { const w = el('div', 'cw'); w.append(t); return w; })(), el('span', 'cv', String(c.n))); return r; }));
}

/* ---------- ticker */
function drawTicker() {
  const run = document.getElementById('ticker-run'); if (!run) return;
  const items = D.signals.slice().sort((a, b) => b.date.localeCompare(a.date) || (a.significance === 'high' ? -1 : 1)).slice(0, 14);
  const mk = (x) => { const a = el('a'); a.href = x.url || '#signals'; if (x.url) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } const sp = el('span'); sp.append(el('b', null, x.org + ':'), txt(x.gist.length > 120 ? x.gist.slice(0, 118).trimEnd() + '…' : x.gist), el('i', null, fmtDay(new Date(x.date)))); a.append(sp); return a; };
  run.replaceChildren(...items.map(mk), ...items.map(mk));
  run.classList.remove('go');
  requestAnimationFrame(() => { const w = run.scrollWidth / 2; run.style.animationDuration = Math.max(40, w / 55) + 's'; run.classList.add('go'); });
}

/* ---------- the wire */
const TOPIC = { php2shell: 'PHP2Shell', 'ai-attack': 'AI-driven attacks', 'ai-incident': 'AI incidents', breakthrough: 'Breakthroughs', jobs: 'Jobs & work', families: 'Families & kids', everyday: 'Everyday life', regulation: 'Governments & regulators', deepfakes: 'Deepfakes', 'chatbot-harm': 'Chatbot harm', other: 'Other' };
const KIND = { breaking: 'Breaking', official: 'Official', analysis: 'Analysis' };
const wire = { topic: 'all', open: false };
const ageShort = (n) => { if (!n.published) return ''; const d = new Date(n.published); if (isNaN(d)) return ''; if (n.time_known === false) return ETd.format(d); const ms = Date.now() - d; const h = ms / 3.6e6; if (h < 1) return 'just now'; if (h < 24) return Math.floor(h) + 'h ago'; if (h < 72) return Math.floor(h / 24) + 'd ago'; return ETd.format(d); };
const SIREN_SVG = '<svg class="siren-ic" viewBox="0 0 34 34" aria-hidden="true"><path class="dome" d="M8 25a9 9 0 0 1 18 0z"/><ellipse class="glass" cx="13.5" cy="19" rx="2.6" ry="3.6" transform="rotate(-30 13.5 19)"/><rect class="base" x="5" y="25" width="24" height="4" rx="1.5"/><path class="ray" d="M17 4.5v4.5"/><path class="ray" d="M8.5 7.5l3 3.3"/><path class="ray" d="M25.5 7.5l-3 3.3"/><path class="ray" d="M3.5 17h4"/><path class="ray" d="M26.5 17h4"/></svg>';
function newsItems() { return (D.news || []).filter((n) => n && n.title && n.url).slice().sort((a, b) => String(b.published || '').localeCompare(String(a.published || ''))); }
/* ---------- the headline wall: index-written lines on top of credible reporting (research/news.json: tag, wall, red, wall_rank).
   Each line must be supportable by the story it links to; the outlet's own framing is in the tooltip and the small print. */
// The reader's own clock: when they last loaded this page (this browser only). Read once, then stamped with now.
const PREV_VISIT = (() => { let p = null; try { const now = Date.now(), last = +localStorage.getItem('ws-last-visit') || 0; p = +localStorage.getItem('ws-prev-session') || null; if (last && now - last > 30 * 6e4) { p = last; localStorage.setItem('ws-prev-session', String(last)); } localStorage.setItem('ws-last-visit', String(now)); } catch (e) {} return p; })(); // the start of the reader's previous visit (a visit ends after 30 quiet minutes)
const PREV_STATE = (() => { try { return JSON.parse(localStorage.getItem('ws-last-state') || 'null'); } catch (e) { return null; } })(); // the level and rung as the reader last saw them
let NOW_LEVEL = null;
const isNewToReader = (n) => !!(PREV_VISIT && n.published && Date.parse(n.published) > PREV_VISIT);
const TIP = {
  tried: 'Tried: attacks were attempted and logged. Nothing is confirmed broken into.',
  proven: 'Proven: a test system was actually broken into. No real victim confirmed yet.',
  hit: 'Hit: a real victim is confirmed by name.',
  reported: 'Reported: one source so far. Not independently confirmed.',
  retracted: 'Retracted: the source has withdrawn this claim.',
  lab: 'Lab only: this happened in a test, not in real use.',
  denied: 'Denied: the party named says it did not happen.',
};
// One small popover for every mark: hover on desktop, tap on phones. Each mark explains itself in one honest line.
const tipBox = (() => { const t = document.createElement('div'); t.className = 'tipbox'; t.setAttribute('role', 'tooltip'); t.hidden = true; document.addEventListener('DOMContentLoaded', () => document.body.append(t)); return t; })();
let tipAt = 0;
function showTip(node) { tipAt = Date.now(); const txt0 = node.getAttribute('data-tip'); if (!txt0) return; if (!tipBox.isConnected) document.body.append(tipBox); tipBox.textContent = txt0; tipBox.hidden = false; const r = node.getBoundingClientRect(); const w = Math.min(320, window.innerWidth - 24); tipBox.style.maxWidth = w + 'px'; const left = Math.max(12, Math.min(r.left, window.innerWidth - w - 12)); tipBox.style.left = left + 'px'; tipBox.style.top = (r.bottom + scrollY + 8) + 'px'; }
function hideTip() { tipBox.hidden = true; }
document.addEventListener('mouseover', (e) => { const n = e.target.closest && e.target.closest('[data-tip]'); if (n) showTip(n); });
document.addEventListener('mouseout', (e) => { const n = e.target.closest && e.target.closest('[data-tip]'); if (n) hideTip(); });
document.addEventListener('click', (e) => { const n = e.target.closest && e.target.closest('[data-tip]'); if (n && n.tagName !== 'A') { e.preventDefault(); if (!tipBox.hidden && tipBox.textContent === n.getAttribute('data-tip') && Date.now() - tipAt > 500) hideTip(); else showTip(n); } else if (!tipBox.hidden && !(e.target.closest && e.target.closest('.tipbox'))) hideTip(); });
const WALL_COLS = { 1: 'Broke out & in', 2: 'Got smarter, took over', 3: 'Fakes, scams & you' };
const WALL_LABEL = { lab: 'Lab only', retracted: 'Retracted', reported: 'Reported', denied: 'Denied', tried: 'Tried', proven: 'Proven', hit: 'Hit' };
function drawLevel() {
  const box = document.getElementById('level'); if (!box || !C.scored) return;
  const asOf = Date.parse(D.meta.as_of);
  const recent = C.scored.filter((r) => { const d = Date.parse(r.disclosed || r.date); return d && asOf - d <= 864e5 && d <= asOf + 864e5; });
  const live = C.scored.find((r) => r.id === D.meta.live_incident);
  const pool = recent.concat(live ? [live] : []); if (!pool.length) { box.hidden = true; return; }
  const top = pool.slice().sort((a, b) => b.severity - a.severity)[0];
  const n = +String(top.level).replace('WS-', '');
  const h = C.headline || {};
  box.hidden = false; box.className = 'lvl lv' + n;
  document.body.dataset.level = String(n);
  const a1 = el('span', 'lvl-l'); a1.append(el('span', 'k', 'Today’s level'), el('b', null, top.level + ' ' + String(top.tier).toUpperCase()));
  const why = el('button', 'lvl-why', 'Why ' + top.level + ' today?'); why.type = 'button'; why.setAttribute('aria-expanded', 'false');
  const wall = newsItems().filter((x) => x.tag && x.wall);
  const a2 = el('span', 'lvl-n');
  const lastState = PREV_STATE;
  const srN = D.meta.serial || {}; const nowState = { level: top.level, rung: srN.rung || '', serial: srN.incident_id || '' }; NOW_LEVEL = top.level;
  if (PREV_VISIT) { const k = wall.filter(isNewToReader).length; const bits = [];
    if (lastState && lastState.level && lastState.level !== nowState.level) bits.push('level moved ' + lastState.level + ' → ' + nowState.level);
    if (lastState && lastState.serial === nowState.serial && lastState.rung && lastState.rung !== nowState.rung) bits.push('the running story moved up to ' + nowState.rung.charAt(0).toUpperCase() + nowState.rung.slice(1));
    if (k || bits.length) { a2.append(el('i', 'newdot')); if (k) a2.append(el('b', null, String(k)), txt(' new' + (bits.length ? ', ' : ''))); if (bits.length) a2.append(txt(bits.join(', '))); a2.append(txt(' since you last looked')); }
    else a2.append(txt('Nothing new since you last looked: level unchanged, no new rung')); a2.title = 'Headlines added since ' + fmtET(new Date(PREV_VISIT).toISOString()) + ' (your last visit, saved in this browser only).'; }
  else { a2.append(el('b', null, String(wall.length)), txt(' top stories of ' + newsItems().length + ' reports from the last 3 days')); }
  try { localStorage.setItem('ws-last-state', JSON.stringify(nowState)); } catch (e) {}
  const a3 = el('a', 'lvl-s'); a3.href = '#record'; a3.append(txt('Severe incidents, last 12 months: '), el('b', null, String(h.severe_last12 ?? '')), txt(' (was ' + (h.severe_prior12 ?? '') + ')'));
  const det = el('div', 'lvl-det'); det.hidden = true;
  det.append(el('p', null, 'The level is the highest score among incidents disclosed in the last 24 hours and the live incident, by the index’s published formula. Today it is set by:'));
  const ul = el('ul'); pool.slice().sort((a, b) => b.severity - a.severity).filter((r, i, arr) => arr.findIndex((x) => x.id === r.id) === i).slice(0, 4).forEach((r) => { const li = el('li'); const a = el('a', null, r.title); a.href = '#i=' + r.id; li.append(el('b', null, r.level + ' · ' + r.severity + '/100'), txt(' '), a); ul.append(li); });
  const how = el('a', null, 'How the scores work →'); how.href = '/index/#about';
  const lsh = el('div', 'share lvl-share');
  shareRow(lsh, { anchor: '', text: `Today's AI danger level: ${top.level} ${String(top.tier).toUpperCase()}, set by "${top.title}" (${top.severity}/100). Warning Shots:`,
    card: { name: 'level-' + D.meta.as_of.slice(0, 10), kicker: 'TODAY’S LEVEL  ·  ' + fmtDate(new Date(D.meta.as_of)), headline: top.level + ' ' + String(top.tier).toUpperCase() + ': ' + top.title, finding: (top.summary || '').split('. ').slice(0, 2).join('. ').replace(/\.?$/, '.'), impact: top.severity + '/100 · the highest score among incidents disclosed in the last 24 hours and the live incident', evidence: 'Scored by the index’s published formula; every incident links to its source.', stamp: 'Level as of ' + fmtET(D.meta.as_of) } });
  det.append(ul, how, lsh);
  why.addEventListener('click', () => { det.hidden = !det.hidden; why.setAttribute('aria-expanded', String(!det.hidden)); });
  const brand = el('a', 'lvl-brand'); brand.href = '#top'; brand.setAttribute('aria-label', 'Warning Shots: the masthead'); const mk = document.querySelector('.masthead .logo .mark'); if (mk) { const c = mk.cloneNode(true); c.setAttribute('class', 'lvl-mark'); c.setAttribute('aria-hidden', 'true'); brand.append(c); } brand.append(el('b', null, 'Warning Shots'), el('span', 'lvl-desc', '· AI’s dangers and breakthroughs'));
  box.replaceChildren(brand, a1, why, a2, a3, det);
}
function drawWall() {
  const lead = document.getElementById('wall-lead'), box = document.getElementById('wall'); if (!box || !lead) return;
  drawLevel(); drawStory();
  const items = newsItems().filter((n) => n.tag && n.wall).sort((a, b) => (a.wall_rank ?? 999) - (b.wall_rank ?? 999));
  const siren = items.find((n) => n.wall === 'siren');
  if (!siren) { box.hidden = true; lead.hidden = true; return; }
  box.hidden = false; lead.hidden = false;
  const ext = (a, n) => { a.href = n.url; if (/^https?:/.test(n.url || '')) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } a.title = (n.outlet || '') + ': ' + n.title; return a; };
  const dots = (t) => t; // complete lines, never teaser-style ellipses
  const chip = (n) => { if (!WALL_LABEL[n.label]) return null; const c = el('span', 'wl-lab ' + n.label, WALL_LABEL[n.label]); if (TIP[n.label]) { c.setAttribute('data-tip', TIP[n.label]); c.tabIndex = 0; } return c; };
  const movedMark = (n) => { const m = n.moved; if (!m || !m.at) return null; const t = Date.parse(m.at); const recent = PREV_VISIT ? t > PREV_VISIT : (Date.parse(D.meta.as_of) - t) < 36 * 3.6e6; if (!recent) return null; const up = m.dir === 'up'; const k = el('span', 'mv ' + (up ? 'up' : 'down'), up ? '▲' : '▼'); k.setAttribute('data-tip', (up ? 'Moved up' : 'Moved down') + (PREV_VISIT ? ' since you last looked' : ' in the last day') + ': ' + (m.note || '') + ' (' + fmtET(m.at) + ').'); k.tabIndex = 0; k.setAttribute('aria-label', up ? 'Moved up' : 'Moved down'); return k; };
  const line = (n, withOutlet) => {
    const w = el('div', 'wl'); if (isNewToReader(n)) { const d = el('i', 'newdot'); d.setAttribute('data-tip', 'New since you last looked (' + fmtET(new Date(PREV_VISIT).toISOString()) + ').'); w.append(d); } const mv = movedMark(n); if (mv) w.append(mv); const c = chip(n); if (c) w.append(c);
    w.append(ext(el('a', 'dl' + (n.red ? ' red' : ''), dots(n.tag)), n));
    if (n.receipt) { const rc0 = el('sup', 'rcpt', 'ⓘ'); rc0.setAttribute('data-tip', n.receipt); rc0.tabIndex = 0; rc0.setAttribute('aria-label', 'Where this number comes from'); w.append(rc0); }
    if (withOutlet) w.append(el('span', 'wl-o', (n.outlet || '') + (ageShort(n).endsWith('h ago') || ageShort(n) === 'just now' ? ' · ' + ageShort(n).replace(' ago', '') : '')));
    return w;
  };
  const pic = (n, cls) => { const f = el('figure', cls); const a = ext(el('a'), n); const im = el('img'); im.src = n.img; { const m = /^(\/assets\/img\/[^?]+)\.(jpe?g|png)$/i.exec(n.img || ''); if (m) { im.srcset = [480, 960, 1440].map((w) => `${m[1]}-${w}.webp ${w}w`).join(', '); im.sizes = cls === 'dl-hero' ? '(max-width: 760px) 100vw, 50vw' : '320px'; } } if (cls === 'dl-hero') im.setAttribute('fetchpriority', 'high'); im.alt = n.img_alt || ''; im.loading = cls === 'dl-hero' ? 'eager' : 'lazy'; im.decoding = 'async'; im.addEventListener('error', () => f.remove()); a.append(im); f.append(a); if (n.img_credit) { const fc = el('figcaption'); if (n.img_credit_url) { const c = el('a', null, n.img_credit); c.href = n.img_credit_url; c.target = '_blank'; c.rel = 'noopener noreferrer'; fc.append(c); } else fc.textContent = n.img_credit; f.append(fc); } return f; };
  // 1. the lead cluster: a picture, then four lines
  const cl = items.filter((n) => n.wall === 'lead').slice(0, 4);
  const buildSerial = (sr, leadLines) => {
      const day = Math.floor((Date.parse(D.meta.as_of.slice(0, 10) + 'T12:00:00Z') - Date.parse(sr.day1 + 'T12:00:00Z')) / 864e5) + 1;
      const box2 = el('div', 'serial' + (sr.state === 'closed' ? ' closed' : ''));
      const hd = el('div', 'serial-h'); hd.append(el('span', 'serial-n', sr.name), el('span', 'serial-d', sr.state === 'closed' ? 'Closed ' + fmtDate(new Date(sr.closed + 'T12:00:00Z')) : 'Day ' + day));
      const inc0 = C.scored.find((r) => r.id === sr.incident_id); const caseNo = inc0 ? el('a', 'serial-c', 'Case ' + inc0.ws) : null; if (caseNo) { caseNo.href = '/i/' + inc0.id + '/'; caseNo.setAttribute('data-tip', 'Case ' + inc0.ws + ' in the index: scored ' + inc0.severity + '/100 (' + inc0.tier + ') by the published formula. Opens the case file.'); }
      const a = leadLines && leadLines.childNodes.length && sr.state !== 'closed' ? leadLines : el('a', 'serial-s', sr.state === 'closed' ? (sr.verdict || '') : sr.standing); if (a.tagName === 'A') a.href = sr.url || '#';
      const ft = el('div', 'serial-f'); const tr = el('a', null, (sr.tech_name ? sr.tech_name + ' ' : '') + 'live tracker →'); tr.href = sr.url || '#'; ft.append(tr);
      if (sr.state !== 'closed') { const shr = el('div', 'share serial-share'); shareRow(shr, { anchor: 'wall-lead', text: sr.name + ', day ' + day + ' since ' + (sr.day1_note || 'it went public') + ': ' + (sr.standing || '') + ' Via Warning Shots:', card: { name: 'ladder-' + (sr.incident_id || 'story') + '-day' + day, kicker: 'THE RUNNING STORY  ·  DAY ' + day + '  ·  ' + fmtDate(new Date(D.meta.as_of)), headline: sr.name + ': ' + ({ tried: 'TRIED', proven: 'PROVEN', hit: 'HIT' }[sr.rung] || '') + (sr.rung === 'hit' ? ', a real victim confirmed' : sr.rung === 'proven' ? ', a test system broken into; no real victim confirmed' : sr.rung === 'tried' ? ', attempts logged; nothing broken into yet' : ''), finding: sr.standing || '', impact: 'Tried → Proven → Hit: the proof ladder. A rung is climbed only on a named, linked source.', evidence: 'Source: ' + (sr.source_label || 'linked on the tracker') + '.', stamp: 'As of ' + fmtET(D.meta.as_of) } }); box2.shareRow = shr; }
      if (sr.source_url) { const so = el('a', null, sr.source_label || 'source'); so.href = sr.source_url; so.target = '_blank'; so.rel = 'noopener noreferrer'; ft.append(so); }
      const RUNGS = [['tried', 'Tried', 'attempts logged'], ['proven', 'Proven', 'a test system broken into'], ['hit', 'Hit', 'a real victim confirmed']];
      const at = RUNGS.findIndex(([k]) => k === sr.rung);
      const lad = el('div', 'rungs'); lad.setAttribute('aria-label', 'Proof so far: ' + (at >= 0 ? RUNGS[at][1] : 'none'));
      RUNGS.forEach(([k, lbl, def], i) => { const r = (sr.rungs || {})[k] || {}; const st = el('span', 'rung' + (i <= at ? ' on' : '') + (i === at ? ' cur' : '')); st.tabIndex = 0; st.setAttribute('data-tip', (TIP[k] || lbl) + (r.note ? ' ' + r.note + '.' : '') + (i > at ? ' Not reached yet.' : '')); st.append(el('i'), el('b', null, lbl), el('small', null, i <= at ? (r.date ? fmtDate(new Date(r.date + 'T12:00:00Z')) : 'yes') : 'not yet')); lad.append(st); });
      const rc = sr.state !== 'closed' && sr.recheck ? el('div', 'serial-r') : null;
      if (rc) { rc.append(el('b', null, 'Rechecked ' + fmtET(sr.recheck_at || D.meta.as_of).replace(/^[A-Z][a-z]{2} \d+, /, '') + ': '), txt(leadLines && leadLines.childNodes.length ? 'every line here still true.' : sr.recheck + '.')); rc.setAttribute('data-tip', 'Checked against the sources then: ' + sr.recheck + '. A "no" is only news if someone just looked.'); }
      const nt = sr.state !== 'closed' && sr.next_test && sr.next_test.date ? el('div', 'serial-t') : null;
      if (nt) { nt.append(el('b', null, 'Next test ' + fmtDate(new Date(sr.next_test.date + 'T12:00:00Z')) + ': '), txt(sr.next_test.text)); nt.setAttribute('data-tip', 'A dated question the index committed to in advance; it is graded on that date, right or wrong, on the Record.'); }
      box2.append(hd, ...(caseNo ? [caseNo] : []), lad, a, ...(rc ? [rc] : []), ...(nt ? [nt] : []), ft, ...(box2.shareRow ? [box2.shareRow] : [])); return box2;
  };
  // The lead is the day's strongest story: one photo, one big headline, one plain sentence. The running story sits under it as a
  // one-line strip that opens to the proof ladder and the lines; it takes the lead itself only when meta.serial.lead is set
  // (a real victim, a formal government warning: an escalation, not a quiet day).
  const ll = el('div', 'dl-lines');
  const frags = el('div', 'dl-frags'); cl.slice(0, 4).forEach((n) => frags.append(line(n, false)));
  const srl = D.meta && D.meta.serial;
  if (srl && srl.name && srl.exposure && srl.state !== 'closed') { const vc0 = (C.victimCounts || {})[srl.incident_id] || {}; const nOrg = vc0.rows || 0; if (nOrg) { const w = el('div', 'wl'); const a = el('a', 'dl', srl.exposure.text.replace('{n}', nOrg)); a.href = srl.exposure.url; if (srl.exposure.tip) { const rc1 = el('sup', 'rcpt', 'ⓘ'); rc1.setAttribute('data-tip', srl.exposure.tip); rc1.tabIndex = 0; w.append(a, rc1); } else w.append(a); ll.append(w); } }
  const takeover = !!(srl && srl.name && srl.state !== 'closed' && srl.lead && srl.lead.tag);
  const hero = takeover ? Object.assign({ url: srl.url, outlet: 'Warning Shots', published: D.meta.as_of }, srl.lead) : siren;
  const sv = el('div', 'dl-siren');
  if (hero.img) sv.append(pic(hero, 'dl-hero'));
  const lvTop = (document.querySelector('#level .lvl-l b') || {}).textContent || '';
  const kick = el('div', 'dl-kick'); kick.append(el('span', 'dot'), txt([lvTop, takeover ? srl.name + ', day ' + (Math.floor((Date.parse(D.meta.as_of.slice(0, 10) + 'T12:00:00Z') - Date.parse(srl.day1 + 'T12:00:00Z')) / 864e5) + 1) : 'Developing', hero.time_known === false ? fmtDate(new Date(hero.published)) : fmtET(hero.published)].filter(Boolean).join(' · ')));
  const body = el('div', 'dl-body'); body.append(kick, ext(el('a', 'dl-head' + (hero.red ? ' red' : ''), hero.tag), hero));
  sv.append(body);
  // The standfirst is not shown under the lead for now (Colin, Oct 27): headline only. It is still written: share cards and search snippets use it.
  if (hero.people && hero.people.text) { const pp = el('p', 'dl-people'); pp.append(el('b', null, (hero.people.kind === 'helped' ? 'Who it helped: ' : 'Who it hit: ')), txt(hero.people.text)); body.append(pp); }
  if (frags.childNodes.length) body.append(frags);
  if (hero.action && hero.action.text && hero.action.url) { const ac = el('a', 'dl-act', hero.action.text + ' →'); ac.href = hero.action.url; if (/^https?:/.test(hero.action.url)) { ac.target = '_blank'; ac.rel = 'noopener noreferrer'; } body.append(ac); }
  const so = el('div', 'dl-src'); if (takeover) { const t = el('a', null, (srl.tech_name ? srl.tech_name + ' ' : '') + 'live tracker →'); t.href = srl.url; so.append(t); } else { so.append(txt(hero.outlet + ' · ' + ageShort(hero) + ' · '), ext(el('a', null, 'Read the original reporting →'), hero)); } body.append(so);
  let strip = null;
  if (srl && srl.name) {
    const day = Math.floor((Date.parse(D.meta.as_of.slice(0, 10) + 'T12:00:00Z') - Date.parse(srl.day1 + 'T12:00:00Z')) / 864e5) + 1;
    strip = el('div', 'sstrip');
    const row = el('button', 'sstrip-row'); row.type = 'button'; row.setAttribute('aria-expanded', 'false');
    row.append(el('span', 'ss-day', srl.state === 'closed' ? 'Closed' : 'We’re following'), el('span', 'ss-name', srl.name));
    if (srl.state !== 'closed') row.append(el('span', 'ss-since', 'day ' + day + ' since ' + (srl.day1_note || 'it went public')));
    const rc = WALL_LABEL[srl.rung] ? el('span', 'wl-lab ' + srl.rung, WALL_LABEL[srl.rung]) : null; if (rc) row.append(rc);
    row.append(el('span', 'ss-st', srl.state === 'closed' ? (srl.verdict || '') : (srl.strip || srl.standing || '')), el('span', 'ss-more', 'Follow it ▾'));
    const panel = buildSerial(srl, ll); panel.hidden = true;
    row.addEventListener('click', () => { panel.hidden = !panel.hidden; row.setAttribute('aria-expanded', String(!panel.hidden)); row.lastChild.textContent = panel.hidden ? 'Follow it ▾' : 'Close ▴'; });
    strip.append(row, panel);
  }
  // The dateline: the edition's date, said like the top of a broadcast
  const dl = el('div', 'dateline'); { const f = (d, o) => new Intl.DateTimeFormat('en-US', Object.assign({ timeZone: 'America/New_York' }, o)).format(d); const ed = new Date(D.meta.as_of);
    const same = f(ed, { year: 'numeric', month: 'numeric', day: 'numeric' }) === f(new Date(), { year: 'numeric', month: 'numeric', day: 'numeric' });
    dl.append(el('span', 'dl-today', (same ? 'Today is ' : '') + f(ed, { weekday: 'long', month: 'long', day: 'numeric' })), ...(same ? [] : [el('span', 'dl-ed', 'Latest edition')])); }
  // What it means for you: does it touch the reader, and one thing to do today. A lens picker rewrites both; the choice stays in this browser.
  const youBox = hero.you && hero.you.touch ? (() => {
    const Y = hero.you; const box = el('section', 'you'); box.setAttribute('aria-label', 'What it means for you');
    const head = el('div', 'you-h'); head.append(el('span', 'you-k', 'What it means for you'));
    const tabs = el('div', 'you-tabs'); tabs.setAttribute('role', 'tablist');
    const opts = [['all', 'Everyone']].concat(LENSES.filter((l) => Y.lens && Y.lens[l.id]).map((l) => [l.id, l.label]));
    let cur = (() => { try { const v = localStorage.getItem('ws-lens'); return opts.some((o) => o[0] === v) ? v : 'all'; } catch (e) { return 'all'; } })();
    const t1 = el('p', 'you-t'), t2 = el('p', 'you-do'), t3 = el('p', 'you-hub');
    const paint = () => { const L = cur !== 'all' && Y.lens && Y.lens[cur] ? Y.lens[cur] : Y; t1.textContent = L.touch; const td = L.today || Y.today || []; t2.replaceChildren(el('b', null, 'Do this today: '), txt(td[0] || '')); if (td[1]) { const a = el('a', null, ' ' + (td[2] || 'How') + ' →'); a.href = td[1]; t2.append(a); }
      { const LL = LENSES.find((l) => l.id === cur); const hb = LL && LL.hub ? LL.hub[0] : ['/exposed/', 'Am I exposed? Find your situation']; const a = el('a', null, hb[1] + ' →'); a.href = hb[0]; t3.replaceChildren(a); }
      tabs.querySelectorAll('button').forEach((b) => { const on = b.dataset.k === cur; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); }); };
    opts.forEach(([k, lbl]) => { const b = el('button', 'you-tab', lbl); b.type = 'button'; b.dataset.k = k; b.setAttribute('role', 'tab'); b.addEventListener('click', () => { cur = k; try { if (k !== 'all') localStorage.setItem('ws-lens', k); } catch (e) {} paint(); }); tabs.append(b); });
    const tog = el('button', 'you-tog', 'More ▸'); tog.type = 'button'; tog.setAttribute('aria-expanded', 'false');
    tog.addEventListener('click', () => { const open = box.classList.toggle('open'); tog.setAttribute('aria-expanded', String(open)); tog.textContent = open ? 'Less ▴' : 'More ▸'; });
    head.append(tabs, tog); box.append(head, t1, t2, t3); paint(); return box; })() : null;
  // Breaking from X: only first-hand, material posts under 12 hours old earn the bar (REFRESH.md rules); everything else is in "On X" below
  const XK = { breaking: 'Breaking', official: 'Official', claim: 'Unverified claim', opinion: 'Opinion' };
  const xposts = (D.xposts || []).filter((x) => x && x.url);
  const brk = xposts.find((x) => (x.kind === 'breaking' || x.kind === 'official') && x.bar !== false && (Date.now() - Date.parse(x.posted)) < 12 * 3.6e6);
  const bbar = brk ? (() => { const b = el('a', 'xbreak'); b.href = brk.url; b.target = '_blank'; b.rel = 'noopener noreferrer'; b.append(el('span', 'xb-k', XK[brk.kind]), el('span', 'xb-t', brk.what), el('span', 'xb-s', brk.author + ', ' + brk.who + ' · ' + ageShort({ published: brk.posted }) + ' · on X')); return b; })() : null;
  const sinceBar = (() => {
    if (!PREV_VISIT) return null;
    const after = (iso) => iso && Date.parse(iso) > PREV_VISIT;
    const wallItems = items.filter((n) => n.wall && n.wall !== 'siren' || n.siren);
    const fresh = wallItems.filter((n) => after(n.published));
    const moved = wallItems.filter((n) => n.moved && after(n.moved.at));
    const graded = (D.calls || []).filter((c) => c.resolution && c.resolution.date && Date.parse(c.resolution.date + 'T23:59:59Z') > PREV_VISIT);
    const bts = (D.breakthroughs || []).filter((b) => b.date && Date.parse(b.date + 'T12:00:00Z') > PREV_VISIT);
    const bar = el('div', 'since-you');
    const when = fmtET(new Date(PREV_VISIT).toISOString()).replace(/, \d{4}/, '');
    bar.append(el('b', null, 'Since you were here'), el('span', 'sy-when', ' (' + when + ')'));
    const parts = [];
    if (fresh.length) { const a = el('a', 'sy-new', fresh.length + (fresh.length === 1 ? ' new headline' : ' new headlines')); a.href = '#wall'; a.addEventListener('click', (e) => { const d = document.querySelector('#wall .newdot'); if (d) { e.preventDefault(); d.closest('.wl').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } }); parts.push(a); }
    if (moved.length) parts.push(txt(moved.length + (moved.length === 1 ? ' story moved' : ' stories moved')));
    if (bts.length) parts.push(txt(bts.length + (bts.length === 1 ? ' new breakthrough' : ' new breakthroughs')));
    if (graded.length) { const g = el('a', 'sy-gr'); g.href = '/forecast/'; const w = graded.filter((c) => c.resolution.outcome !== 'void' && Math.abs(+c.odds - 0.5) > 1e-9 && houseHit(c)).length, l = graded.filter((c) => c.resolution.outcome !== 'void' && Math.abs(+c.odds - 0.5) > 1e-9 && !houseHit(c)).length, t = graded.length - w - l;
      g.append(txt(graded.length + (graded.length === 1 ? ' forecast graded' : ' forecasts graded') + ' (' + [w ? w + ' right' : '', l ? l + ' wrong' : '', t ? t + ' toss-up' : ''].filter(Boolean).join(', ') + ')')); parts.push(g); }
    const srv = D.meta.serial || {}; if (srv.state === 'live' && after(srv.recheck_at || (srv.last_fact ? srv.last_fact + 'T12:00:00Z' : ''))) { const a = el('a', null, srv.name + ' checked again'); a.href = srv.url || '/php2shell/'; a.title = srv.recheck ? 'Latest check: ' + srv.recheck : ''; parts.push(a); }
    if (PREV_STATE && PREV_STATE.level) { const lv = el('span', 'sy-lv'); parts.unshift(lv); setTimeout(() => { if (!NOW_LEVEL) { lv.remove(); return; } lv.textContent = NOW_LEVEL === PREV_STATE.level ? 'level held at ' + NOW_LEVEL : 'level moved ' + PREV_STATE.level + ' → ' + NOW_LEVEL; if (NOW_LEVEL !== PREV_STATE.level) lv.classList.add('moved'); }, 0); }
    if (!parts.some((p) => p.className !== 'sy-lv')) { bar.append(txt(': '), ...parts, txt((parts.length ? '; ' : '') + 'nothing new yet.' + (D.meta.next_check ? ' Next edition ' + fmtET(D.meta.next_check).replace(/^[A-Z][a-z]{2} \d+, /, '') + '.' : ''))); bar.classList.add('quiet'); return bar; }
    bar.append(txt(': ')); parts.forEach((p, i) => bar.append(...(i ? [txt(' · ')] : []), p)); return bar; })();
  lead.replaceChildren(...(sinceBar ? [sinceBar] : []), ...(bbar ? [bbar] : []), dl, sv, ...(youBox ? [youBox] : []), ...(strip ? [strip] : []));
  // 3. the columns, below the masthead
  const cols = el('div', 'wall-cols');
  [1, 2, 3].forEach((c) => {
    const col = el('div', 'wall-col'); col.append(el('h2', 'wall-ch', WALL_COLS[c]));
    (c === 1 && takeover ? [siren] : []).concat(items.filter((n) => +n.wall === c).slice(0, 15)).forEach((n) => col.append(line(n, true)));
    // Standing desks at the foot of each column (Drudge's directory geometry): our own pages, labelled, never styled as headlines
    const DK = D.desks || {};
    const TAILS = {
      1: ['Follow the damage', [
        srl && srl.name && srl.state !== 'closed' ? [srl.url, (srl.tech_name || srl.name) + ': live tracker, day ' + (Math.floor((Date.parse(D.meta.as_of.slice(0, 10) + 'T12:00:00Z') - Date.parse(srl.day1 + 'T12:00:00Z')) / 864e5) + 1)] : null,
        ['/fixes/', 'Did they fix it?' + (DK.fix_open ? ' ' + DK.fix_open + ' of ' + DK.fix_total + ' still open' : '')],
        DK.next_call ? ['/forecast/' + DK.next_call.id + '/', 'The odds: ' + DK.next_call.q + ' ' + DK.next_call.odds_word.toUpperCase() + ', resolves ' + DK.next_call.when] : ['/forecast/', 'The forecasts'],
        ['/exposed/', 'Am I exposed? Find your situation'],
        ['/index/', 'The Record: every incident, scored']]],
      2: ['What AI can now do', [
        ['/can-ai/', 'What AI can do now' + (DK.can_ai ? ': ' + DK.can_ai + ' questions answered' : '')],
        ['/jobs/', 'Can AI do your job?' + (DK.jobs ? ' ' + DK.jobs + ' jobs graded' : '')],
        ['/jobs/layoffs/', 'Layoffs tied to AI' + (DK.layoffs ? ': ' + DK.layoffs + ' so far' : '')],
        ['/learn/', 'Know what it means: plain explainers']]],
      3: ['Protect yourself', [
        ['/checks/', 'Is this a scam?' + (DK.checks ? ' ' + DK.checks + ' quick checks' : '')],
        ['/help/', 'What to do when AI is used against you'],
        ['/shield/', 'Set a family safe word (2 minutes)'],
        ['/help/ai-fake-nude-image-what-to-do/', 'A fake nude of you or your child: what to do now'],
        ['https://haveibeenpwned.com/', 'Check if your email was in a breach'],
        ['/midterms-2026/', 'Every AI fake in the midterms' + (DK.midterms ? ' (' + DK.midterms + ')' : '')],
        ['/scraped/', 'Keep your site out of AI training sets']]],
    };
    const [th, links] = TAILS[c]; const tl = el('div', 'ctail'); tl.append(el('div', 'ctail-h', th));
    links.filter(Boolean).forEach(([u, t]) => { const a = el('a', null, t); a.href = u; if (/^https?:/.test(u)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } tl.append(a); });
    col.append(tl);
    cols.append(col);
  });
  const more = el('button', 'wall-more', 'More headlines'); more.type = 'button'; more.addEventListener('click', () => box.classList.add('open'));
  const ed = el('p', 'wall-ed');
  if (D.meta.quiet) ed.append(el('b', 'quiet', 'Rechecked ' + fmtET(D.meta.as_of) + ': nothing moved. '));
  const slotH = [5.2833, 12.2833, 18.2833]; const etH = (() => { const p = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: 'numeric', hour12: false }).formatToParts(new Date(D.meta.as_of)); const g = (t) => +p.find((x) => x.type === t).value; return g('hour') + g('minute') / 60; })();
  const extra = !slotH.some((h) => etH >= h - 0.25 && etH <= h + 1.5);
  if (D.meta.edition) { const ea = el('a', null, (extra ? 'Extra edition, No. ' : 'Edition No. ') + D.meta.edition); ea.href = '/' + (D.meta.edition_path || 'archive/'); ea.setAttribute('data-tip', 'Edition No. ' + D.meta.edition + ', published ' + fmtET(D.meta.as_of) + '. Opens a frozen copy of this page exactly as published.'); const cl = el('a', null, 'what changed'); cl.href = '/index/#changelog'; const all = el('a', null, 'every edition'); all.href = '/archive/'; ed.append(ea, txt(' · ' + fmtET(D.meta.as_of) + ' · '), cl, txt(' · '), all); if (extra) ea.setAttribute('data-tip', 'An extra edition outside the 5:17 AM, 12:17 PM and 6:17 PM schedule, published because something worth adding came in. Opens a frozen copy.'); }
  const cu = el('p', 'wall-cu'); cu.append(el('b', null, 'That’s your Warning Shots for ' + new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'long', month: 'long', day: 'numeric' }).format(new Date(D.meta.as_of)) + ', as of ' + fmtET(D.meta.as_of).replace(/^[A-Z][a-z]{2} \d+, /, '') + '.'), txt(' You’re caught up.' + (D.meta.next_check ? ' Next edition ' + fmtET(D.meta.next_check).replace(/^[A-Z][a-z]{2} \d+, /, '') + '.' : '') + ' See what’s coming. Know what it means.'));
  const xbox = xposts.length ? (() => {
    const XLOGO = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>';
    const TICK = '<svg viewBox="0 0 22 22" aria-label="Verified account"><circle cx="11" cy="11" r="10" fill="#1d9bf0"/><path d="M6.5 11.3l3 3 6-6.3" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    const when = (iso) => { const d = new Date(iso); return isNaN(d) ? '' : d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' }) + ' ET · ' + d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'America/New_York' }); };
    const who = (t, x, small) => { const h = el('div', 'tw-h'); const av = el('span', 'tw-av'); av.textContent = (t.name || x.author || '?').trim()[0]; if (t.avatar) { const im = el('img'); im.src = t.avatar; im.alt = ''; im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = () => im.remove(); av.append(im); } const nm = el('span', 'tw-nm'); const b = el('b', null, t.name || x.author); nm.append(b); if (t.verified) { const v = el('span', 'tw-v'); v.innerHTML = TICK; nm.append(v); } nm.append(el('span', 'tw-hd', '@' + (t.handle || (x.handle || '').replace(/^@/, '')))); h.append(av, nm); if (!small) { const lg = el('span', 'tw-x'); lg.innerHTML = XLOGO; h.append(lg); } return h; };
    const bx = el('section', 'xon'); bx.append(el('h2', 'wall-ch', 'On X: three posts worth your time'));
    const grid = el('div', 'xon-g');
    // three posts, each on a different story: highest power first (a post older than 72 hours counts one point less), and among equals a kind not yet shown (the news, the claim, the take), then the newest
    const GRP = { breaking: 'news', official: 'news', claim: 'claim', opinion: 'take' };
    const age = (x) => Date.now() - Date.parse(x.posted), eff = (x) => (x.power || 3) - (age(x) > 72 * 3.6e6 ? 1 : 0);
    const three = [], stories = new Set(), groups = new Set();
    let pool = [...xposts];
    while (three.length < 3 && pool.length) {
      pool.sort((a, b) => eff(b) - eff(a) || (groups.has(GRP[a.kind]) ? 1 : 0) - (groups.has(GRP[b.kind]) ? 1 : 0) || Date.parse(b.posted) - Date.parse(a.posted));
      const i = pool.findIndex((x) => !stories.has(x.story || x.id)); const x = pool.splice(i < 0 ? 0 : i, 1)[0];
      three.push(x); stories.add(x.story || x.id); groups.add(GRP[x.kind]);
    }
    three.forEach((x) => {
      const t = x.tweet || { name: x.author, handle: (x.handle || '').replace(/^@/, ''), text: x.quote, created_at: x.posted };
      const item = el('div', 'xon-i');
      item.append(el('span', 'wl-lab ' + (x.kind === 'opinion' ? 'opinion' : x.kind === 'claim' ? 'reported' : 'proven'), x.kind === 'breaking' && age(x) >= 12 * 3.6e6 ? 'First-hand' : (XK[x.kind] || x.kind)));
      const card = el('a', 'tw'); card.href = x.url; card.target = '_blank'; card.rel = 'noopener noreferrer'; card.setAttribute('aria-label', 'Post by ' + (t.name || x.author) + ' on X');
      card.append(who(t, x), el('p', 'tw-t', (t.text || x.quote) + (t.truncated ? '…' : '')));
      if (t.truncated) card.append(el('span', 'tw-more', 'Show more on X'));
      if (t.photos && t.photos[0]) { const im = el('img', 'tw-ph'); im.src = t.photos[0]; im.alt = ''; im.loading = 'lazy'; im.referrerPolicy = 'no-referrer'; im.onerror = () => im.remove(); card.append(im); }
      if (t.video && t.video.poster && t.id) card.append(xClip(t, x, card, item));
      if (t.quoted) { const q = el('div', 'tw-q'); q.append(who(t.quoted, {}, true), el('p', 'tw-t', t.quoted.text)); card.append(q); }
      const f = el('div', 'tw-f'); f.append(el('span', null, when(t.created_at || x.posted)), el('span', 'tw-go', 'View on X →')); card.append(f);
      item.append(card, el('p', 'xon-w', x.what), el('small', 'xon-by', (x.author || t.name) + ': ' + x.who));
      grid.append(item);
    });
    bx.append(grid, el('p', 'xon-note', 'The three posts that matter most right now, each on a different story. Breaking means a first-hand source posting a new fact you can check, in the last 12 hours; after that it shows as First-hand. An unverified claim is new but nobody independent has checked it yet. Opinion is commentary. The post text is shown exactly as it appears on X; the line under each is ours.'));
    return bx; })() : null;
  const foot = el('p', 'wall-foot'); foot.append(txt('Every line is written by Warning Shots from the original reporting and links straight to it. '), (() => { const a = el('a', null, 'Every report from the last three days, ' + newsItems().length + ' in all →'); a.href = '/wire/'; return a; })(), txt(' · '), (() => { const a = el('a', null, 'Earlier days'); a.href = '/wire/archive/'; return a; })(), txt(' · Beats: '), (() => { const a = el('a', null, 'AI near you'); a.href = '/wire/near-you/'; return a; })(), txt(', '), (() => { const a = el('a', null, 'AI at school'); a.href = '/wire/school/'; return a; })(), txt(', '), (() => { const a = el('a', null, 'Layoffs tied to AI'); a.href = '/jobs/layoffs/'; return a; })());
  // Coming up: the next dated tests, so the reader knows when the loops close (no odds on the front page)
  const up = el('div', 'comingup'); const asOfD = D.meta.as_of.slice(0, 10);
  const open = (D.calls || []).filter((c) => c && !c.resolution && c.resolve_by >= asOfD).sort((a, b) => a.resolve_by.localeCompare(b.resolve_by));
  const firstDay = open.length ? open[0].resolve_by : null; const nDay = open.filter((c) => c.resolve_by === firstDay).length;
  const graded = (D.calls || []).some((c) => c && c.resolution);
  if (firstDay) { // Resolution Day: the next date the index's calls are graded, with a countdown and each call's odds in words
    const rd = el('div', 'resday'); const dLeft = Math.max(0, Math.ceil((Date.parse(firstDay + 'T00:00:00-04:00') - Date.now()) / 864e5));
    const h = el('div', 'rd-h'); h.append(el('b', null, 'Resolution Day'), txt(' · ' + d3.utcFormat('%A, %b %-d')(new Date(firstDay + 'T12:00:00Z')) + ' · '), el('span', 'rd-n', dLeft === 0 ? 'today' : dLeft === 1 ? 'tomorrow' : 'in ' + dLeft + ' days'));
    const ul = el('ul', 'rd-l'); open.filter((c) => c.resolve_by === firstDay).forEach((c) => { const li = el('li'); const a = el('a', null, c.plain || c.question); a.href = '/forecast/' + c.id + '/'; li.append(a, el('span', 'rd-o', ' Our odds: ' + likelyWord(c.odds).toLowerCase())); ul.append(li); });
    const hr1 = houseRecord(); const ft = el('p', 'rd-f'); ft.append(txt(nDay + (nDay === 1 ? ' call is' : ' calls are') + ' graded that day, right or wrong, in public. ' + (hr1.n ? 'Record so far: ' + hr1.w + ' right, ' + hr1.l + ' wrong. ' : 'Misses stay on the page. ')), (() => { const a = el('a', null, 'Every forecast →'); a.href = '/forecast/'; return a; })());
    rd.append(h, ul, ft); up.append(rd); }
  (D.catalysts || []).filter((c) => c.date > asOfD && c.date !== firstDay).sort((a, b) => a.date.localeCompare(b.date)).slice(0, 2).forEach((c) => { const r = el('a', 'cu-i'); r.href = '/index/#next'; r.append(el('b', null, c.date_label + ':'), txt(' ' + c.event)); up.append(r); });
  // The payoff: forecasts graded in the last day lead the strip, misses as prominent as hits, with the running record
  const asOfT = Date.parse(D.meta.as_of);
  const fresh = (D.calls || []).filter((c) => c && c.resolution && c.resolution.outcome !== 'void' && asOfT - Date.parse(c.resolution.date + 'T23:59:00-04:00') < 36 * 3.6e6);
  if (fresh.length) { const hr0 = houseRecord(); const gb = el('div', 'graded');
    gb.append(el('div', 'cu-h', 'Graded'));
    fresh.slice(0, 3).forEach((c) => { const toss = Math.abs(+c.odds - 0.5) < 1e-9; const hit = houseHit(c); const g = el('a', 'gr-i ' + (toss ? 'toss' : hit ? 'hit' : 'miss')); g.href = '/index/#fc-' + c.id; g.append(el('b', null, toss ? '◦ Called it a toss-up' : hit ? '✓ Called it' : '✗ Missed'), txt(' ' + (c.plain || c.question) + ' Answer: ' + (c.resolution.outcome === 'yes' ? 'yes' : 'no') + '. The index expected: ' + likelyWord(c.odds).toLowerCase() + '.')); gb.append(g); });
    gb.append(el('span', 'gr-rec', 'Track record so far: ' + hr0.w + ' right, ' + hr0.l + ' wrong. Misses stay on the page.'));
    up.prepend(gb); }
  if (up.childNodes.length && !fresh.length) up.prepend(el('div', 'cu-h', 'Coming up')); else if (fresh.length) up.insertBefore(el('div', 'cu-h', 'Coming up'), up.children[1] || null);
  // Breakthroughs: what AI just made possible, written as the payoff to a person, with the same proof labels as the warnings
  const BT = (D.breakthroughs || []).filter((b) => b && b.payoff);
  const BTL = { 'in-use': 'In use now', published: 'Peer-reviewed', reproduced: 'Reproduced', claimed: 'Claimed, not yet checked' };
  const btBand = BT.length ? (() => {
    const s = el('section', 'bt'); s.setAttribute('aria-label', 'Breakthroughs');
    const h = el('div', 'bt-h'); h.append(el('h2', 'bt-t', 'Breakthroughs'), el('span', 'bt-sub', 'What AI just made possible, and what it means for you')); const all = el('a', 'bt-all', 'All breakthroughs →'); all.href = '/breakthroughs/'; h.append(all); s.append(h);
    const g = el('div', 'bt-g');
    BT.slice(0, 3).forEach((b) => { const c = el('article', 'bt-c'); const top = el('div', 'bt-k'); top.append(el('span', 'bt-area', b.area || ''), el('span', 'bt-p ' + b.proof, BTL[b.proof] || b.proof)); c.append(top);
      const a = el('a', 'bt-pay', b.payoff); a.href = b.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; c.append(a, el('p', 'bt-m', b.means));
      if (b.people) { const pp = el('p', 'bt-who'); pp.append(el('b', null, 'Who it helps: '), txt(b.people)); c.append(pp); }
      if (b.try && b.try[1]) { const t = el('a', 'bt-try', 'Try it: ' + b.try[0] + ' →'); t.href = b.try[1]; t.target = '_blank'; t.rel = 'noopener noreferrer'; c.append(t); }
      g.append(c); });
    s.append(g); return s; })() : null;
  // Up & Down: who gained or lost power in AI this week, and why it matters (the facts are the outlet's; 'Why it matters' is ours)
  const UD = (D.updown || []).filter((x) => x && x.url && (Date.parse(D.meta.as_of) - Date.parse(x.date + 'T12:00:00Z')) < 8 * 864e5);
  const incBand = UD.length >= 3 ? (() => {
    const s = el('section', 'ud'); s.setAttribute('aria-label', 'Up and Down: who gained or lost power in AI this week');
    const h = el('div', 'ud-h'); h.append(el('h2', 'ud-t', 'Up & Down'), el('span', 'ud-sub', 'Who gained power in AI this week, who lost it, and why it matters.')); const all = el('a', 'ud-all', 'The full board →'); all.href = '/up-and-down/'; h.append(all); s.append(h);
    const row = (b) => { const r = el('div', 'ud-r ' + b.dir); r.append(el('span', 'ud-ar', b.dir === 'up' ? '▲' : '▼'));
      const body = el('div', 'ud-b'); const top = el('p', 'ud-l'); const nm = el('a', 'ud-n', b.name); nm.href = b.url; nm.target = '_blank'; nm.rel = 'noopener noreferrer'; nm.title = b.outlet || ''; top.append(nm, txt(' ' + b.line));
      const w = el('p', 'ud-w'); w.append(el('b', null, 'Why it matters: '), txt(b.why + ' '));
      const x = el('a', 'ud-x', 'Post'); x.href = 'https://x.com/intent/post?text=' + encodeURIComponent((b.dir === 'up' ? '▲ ' : '▼ ') + b.name + ': ' + b.line + ' Why it matters: ' + b.why) + '&url=' + encodeURIComponent(SITE + 'up-and-down/'); x.target = '_blank'; x.rel = 'noopener noreferrer'; w.append(x);
      body.append(top, w); r.append(body); return r; };
    const cols = el('div', 'ud-cols');
    [['up', 'Up'], ['down', 'Down']].forEach(([k, l]) => { const c = el('div', 'ud-c ' + k); c.append(el('div', 'ud-ch', (k === 'up' ? '▲ ' : '▼ ') + l)); UD.filter((b) => b.dir === k).slice(0, 3).forEach((b) => c.append(row(b))); cols.append(c); });
    s.append(cols, el('p', 'ud-f', 'Each name links to the reporting. The arrow and “Why it matters” are our read. A story already in the headlines above never appears here twice.')); return s; })() : null;
  // The Chart: one original chart a day, from the index's own data (build_chart.py); the image carries its own title and citation
  const CH = D.chart && D.chart.svg ? D.chart : null;
  const chartBand = CH ? (() => {
    const s = el('section', 'tchart'); s.setAttribute('aria-label', 'The Chart');
    const h = el('div', 'tc-h'); h.append(el('span', 'tc-k', 'The Chart'), el('span', 'tc-d', fmtDate(new Date(CH.date + 'T12:00:00Z'))));
    const fig = el('div', 'tc-fig'); fig.innerHTML = window.innerWidth < 700 && CH.svg_tall ? CH.svg_tall : CH.svg;
    const ft = el('p', 'tc-f'); ft.append(txt(CH.takeaway + ' '));
    const a1 = el('a', null, 'The data and the download →'); a1.href = CH.url; const a2 = el('a', null, 'Every chart'); a2.href = '/chart/'; ft.append(a1, txt(' · '), a2);
    s.append(h, fig, ft); return s; })() : null;
  const pulse = buildPulse();
  box.replaceChildren(...(pulse ? [pulse] : []), ...(btBand ? [btBand] : []), cols, ...(incBand ? [incBand] : []), ...(chartBand ? [chartBand] : []), more, ...(up.childNodes.length ? [up] : []), cu, ed, ...(xbox ? [xbox] : []), foot);
}
/* ---------- The story so far: a 20-second film at the top of the homepage, told by the record itself.
   Four beats, each lighting its stretch of the incident strip: when a person was always behind it, the first severe case where the AI
   acted on its own, the last twelve months, and today's live case. Every number is computed from the data; nothing is staged. */
const storyState = { i: 0, timer: null, paused: false, done: false };
function drawStory() {
  const box = document.getElementById('story'); if (!box || !C.scored || !C.scored.length || EMBED) { if (box) box.hidden = true; return; }
  clearTimeout(storyState.timer); storyState.timer = null;
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const asOf = new Date(D.meta.as_of), h = C.headline || {}, own = (r) => +r.A >= 3;
  const all = C.scored.filter((r) => r.date && !isNaN(Date.parse(r.date))).map((r) => ({ ...r, t: new Date(r.date + 'T12:00:00Z') })).sort((a, b) => a.t - b.t);
  const t0 = new Date('2023-01-01T00:00:00Z'), fmtMY = d3.utcFormat('%b %Y'), yrAgo = new Date(+asOf - 365.25 * 864e5);
  const early = all.filter((r) => r.t < new Date('2025-01-01T00:00:00Z')), earlyWild = early.filter((r) => r.setting === 'wild');
  const firstSev = all.find((r) => r.setting === 'wild' && own(r) && r.severity >= 60);
  const sr = D.meta.serial || {}, live = all.find((r) => r.id === D.meta.live_incident);
  const day = sr.day1 ? Math.floor((Date.parse(D.meta.as_of.slice(0, 10) + 'T12:00:00Z') - Date.parse(sr.day1 + 'T12:00:00Z')) / 864e5) + 1 : null;
  const pct = Math.round(100 * (h.agentic_recent || 0));
  const B = (k, from, to, html, hot) => ({ k, from, to, html, hot: hot || [] });
  const beats = [
    B('2023–2024', t0, new Date('2024-12-31T23:59:00Z'), earlyWild.length && !earlyWild.some(own)
      ? `In 2023 and 2024, every real-world AI incident on our record had <b>a person</b> at the controls.`
      : `In 2023 and 2024, our record logged <b>${early.length}</b> AI incidents, most of them with a person at the controls.`),
    ...(firstSev ? [B(fmtMY(firstSev.t), new Date(+firstSev.t - 40 * 864e5), new Date(+firstSev.t + 40 * 864e5), `${fmtMY(firstSev.t)}, the first severe case where the AI acted on its own: ${esc(firstSev.title)}. <b>${firstSev.severity}/100.</b>`, [firstSev.id])] : []),
    B('The last 12 months', yrAgo, asOf, `In the last 12 months: <b>${h.severe_last12 ?? '?'}</b> severe incidents, up from ${h.severe_prior12 ?? '?'}. In <b>${pct}%</b> of real-world cases, the AI did the acting.`),
    B('Now' + (day ? ' · day ' + day : ''), new Date(+asOf - 10 * 864e5), asOf, live && sr.name
      ? `Right now: <b>${esc(sr.name)}</b>${sr.strip ? '. ' + esc(sr.strip) : ''} Today's level: <b>${esc(live.level || '')}</b>.`
      : `Today's level: <b>${esc((C.scored.slice().sort((a, b) => b.severity - a.severity)[0] || {}).level || '')}</b>.`, live ? [live.id] : []),
  ];
  const inner = el('div', 'st-in');
  const left = el('div', 'st-l'); const kick = el('div', 'st-k'); const ttl = el('p', 'st-t');
  const ctl = el('div', 'st-c'); const dots = el('div', 'st-dots'); dots.setAttribute('role', 'tablist'); dots.setAttribute('aria-label', 'Steps');
  const dotEls = beats.map((b, i) => { const d = el('button', 'st-dot'); d.type = 'button'; d.setAttribute('aria-label', 'Step ' + (i + 1) + ': ' + b.k); d.addEventListener('click', () => { stop(); show(i); }); dots.append(d); return d; });
  const rp = el('button', 'st-a', '↻ Replay'); rp.type = 'button'; rp.addEventListener('click', () => { storyState.done = false; show(0); run(); });
  const ex = el('button', 'st-a', 'Explore every incident ↓'); ex.type = 'button'; ex.addEventListener('click', () => { const t = document.querySelector('.seis'); if (t) t.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' }); });
  ctl.append(dots, rp, ex); left.append(kick, ttl, ctl);
  // the strip: every incident as a hairline spike
  const strip = el('div', 'st-strip'); const W = 640, H = 120, ml = 4, mr = 34, base = H - 16;
  const x = d3.scaleUtc().domain([t0, new Date(+asOf + 20 * 864e5)]).range([ml, W - mr]), y = d3.scaleLinear().domain([0, 100]).range([base, 6]);
  const NS = 'http://www.w3.org/2000/svg', mk = (n, a) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); return e; };
  const svg = mk('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': `${all.length} AI incidents since 2023 as spikes; red where the AI acted on its own in the real world.` });
  const band = mk('rect', { x: ml, y: 0, width: 0, height: base, class: 'st-band' }); svg.append(band);
  svg.append(mk('line', { x1: ml, x2: W - mr, y1: base, y2: base, class: 'st-base' }));
  for (let yr = 2023; yr <= asOf.getUTCFullYear(); yr++) { const t = mk('text', { x: x(new Date(yr + '-01-01T00:00:00Z')) + 2, y: H - 3, class: 'st-yr' }); t.textContent = String(yr); svg.append(t); }
  const sp = all.map((r) => { const l = mk('line', { x1: x(r.t), x2: x(r.t), y1: base, y2: base, class: 'sp ' + (own(r) && r.setting === 'wild' ? 'own' : 'ctx') }); svg.append(l); return { r, l, top: y(r.severity) }; });
  const nx = x(asOf); if (live) { svg.append(mk('circle', { cx: x(live.t), cy: y(live.severity), r: 3, class: 'st-now' }), mk('circle', { cx: x(live.t), cy: y(live.severity), r: 6, class: 'st-ring' })); }
  const nl = mk('text', { x: nx + 4, y: 12, class: 'st-lab' }); nl.textContent = 'NOW'; svg.append(nl);
  strip.append(svg); strip.title = 'Explore every incident'; strip.addEventListener('click', () => ex.click());
  inner.append(left, strip); box.replaceChildren(inner); box.hidden = false;
  const MS = 5200; box.style.setProperty('--st-ms', MS + 'ms');
  function show(i) { storyState.i = i; const b = beats[i];
    kick.replaceChildren(txt(b.k), el('span', 'st-step', (i + 1) + ' of ' + beats.length));
    ttl.classList.add('fade'); setTimeout(() => { ttl.innerHTML = b.html; ttl.classList.remove('fade'); }, reduced ? 0 : 180);
    dotEls.forEach((d, j) => { d.classList.toggle('on', j === i); d.classList.toggle('done', j < i); d.setAttribute('aria-selected', String(j === i)); if (j === i) { d.style.animation = 'none'; void d.offsetWidth; d.style.animation = ''; } });
    const a = Math.max(ml, x(b.from)), z = Math.min(W - mr + 6, x(b.to) + 3); band.setAttribute('x', a); band.setAttribute('width', Math.max(4, z - a));
    sp.forEach(({ r, l, top }) => { const inR = r.t >= b.from && r.t <= b.to; l.setAttribute('y2', r.t <= b.to || i === beats.length - 1 ? top : base); l.classList.toggle('dim', !inR && i !== beats.length - 1); l.classList.toggle('hot', b.hot.includes(r.id)); }); }
  function stop() { clearTimeout(storyState.timer); storyState.timer = null; box.classList.add('paused'); }
  function run() { box.classList.remove('paused'); clearTimeout(storyState.timer); if (reduced) return; storyState.timer = setTimeout(function tick() { if (storyState.i < beats.length - 1) { show(storyState.i + 1); storyState.timer = setTimeout(tick, MS); } else { storyState.done = true; dotEls.forEach((d) => d.classList.remove('on')); dotEls.forEach((d) => d.classList.add('done')); } }, MS); }
  box.onmouseenter = () => { if (storyState.timer) { clearTimeout(storyState.timer); storyState.timer = null; box.classList.add('paused'); storyState.hold = true; } };
  box.onmouseleave = () => { if (storyState.hold) { storyState.hold = false; run(); } };
  if (reduced || storyState.done) show(beats.length - 1); else { show(storyState.i || 0); run(); }
}
/* ---------- The Seismograph: every incident on the record as a spike (height = severity; red = the AI acted on its own).
   It replays 2023 to today once when it comes into view, then answers to hover, tap and the arrow keys. The replay is the real record
   in date order; nothing in it is simulated. */
const pulseState = { f: 'all', played: false, zoom: false };
function buildPulse() {
  if (!C.scored || !C.scored.length) return null;
  const asOf = new Date(D.meta.as_of), asOfY = D.meta.as_of.slice(0, 4);
  const own = (r) => +r.A >= 3;
  const t0d = pulseState.zoom ? new Date(+asOf - 90 * 864e5) : new Date('2023-01-01T00:00:00Z');
  const all = C.scored.filter((r) => r.date && !isNaN(Date.parse(r.date))).map((r) => ({ ...r, t: new Date(r.date + 'T12:00:00Z') })).sort((a, b) => a.t - b.t);
  const full = all.slice(); all.splice(0, all.length, ...full.filter((r) => r.t >= t0d));
  const live = all.find((r) => r.id === D.meta.live_incident);
  const sec = el('section', 'seis dark-scope'); sec.setAttribute('aria-label', 'The Seismograph: every AI incident since 2023');
  const head = el('div', 'pl-h');
  const ttl = el('div', 'pl-tt'); ttl.append(el('span', 'pl-k', 'The Seismograph'), el('span', 'pl-sub', (pulseState.zoom ? 'Every AI incident on the record in the last 90 days. ' : 'Every AI incident on the record since 2023. ') + 'Taller is worse. '), (() => { const b = el('b', 'pl-red', 'Red'); return b; })(), el('span', 'pl-sub', ': the AI acted on its own.'));
  const ctr = el('div', 'pl-ctr'); ctr.setAttribute('aria-live', 'polite');
  head.append(ttl, ctr);
  const ctl = el('div', 'pl-ctl'); ctl.setAttribute('role', 'group'); ctl.setAttribute('aria-label', 'Show');
  const F = [['all', 'All ' + all.length], ['own', 'AI acted on its own ' + all.filter(own).length], ['severe', 'Severe and worse ' + all.filter((r) => r.severity >= 60).length]];
  const btns = F.map(([k, l]) => { const b = el('button', 'pl-f' + (pulseState.f === k ? ' on' : ''), l); b.type = 'button'; b.setAttribute('aria-pressed', String(pulseState.f === k)); b.addEventListener('click', () => { pulseState.f = k; btns.forEach((x, i) => { const on = F[i][0] === k; x.classList.toggle('on', on); x.setAttribute('aria-pressed', String(on)); }); paint(false); }); return b; });
  const rp = el('button', 'pl-f pl-rp', '↻ Replay'); rp.type = 'button'; rp.addEventListener('click', () => play());
  const zm = el('button', 'pl-f pl-zm', pulseState.zoom ? '← Since 2023' : 'Zoom: last 90 days'); zm.type = 'button'; zm.setAttribute('aria-pressed', String(pulseState.zoom));
  zm.addEventListener('click', () => { pulseState.zoom = !pulseState.zoom; const n = buildPulse(); if (n) { sec.replaceWith(n); n.querySelector('.pl-zm').focus(); } });
  ctl.append(...btns, zm, rp);
  const fig = el('div', 'pl-fig'); const tip = el('div', 'pl-tip'); tip.hidden = true; fig.append(tip);
  const W = Math.max(300, Math.min(1180, (document.getElementById('wall') || document.body).clientWidth || window.innerWidth - 32)), phone = W < 640;
  const H = phone ? 220 : 300, m = { l: phone ? 26 : 34, r: phone ? 46 : 64, t: 18, b: 22 };
  const x = d3.scaleUtc().domain([t0d, new Date(+asOf + (pulseState.zoom ? 3 : 25) * 864e5)]).range([m.l, W - m.r]);
  const y = d3.scaleLinear().domain([0, 100]).range([H - m.b, m.t]);
  const NS = 'http://www.w3.org/2000/svg', mk = (n, a) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); return e; };
  const svg = mk('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img', 'aria-label': `${all.length} AI incidents since 2023 plotted by date and severity; ${all.filter(own).length} where the AI acted on its own.` });
  // recessive frame: severity guides and years
  [[60, 'Severe'], [80, 'Critical']].forEach(([v, l]) => { svg.append(mk('line', { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v), class: 'pl-g' })); const t = mk('text', { x: m.l + 4, y: y(v) - 4, class: 'pl-gl' }); t.textContent = l; svg.append(t); });
  svg.append(mk('line', { x1: m.l, x2: W - m.r, y1: y(0), y2: y(0), class: 'pl-base' }));
  [0, 50, 100].forEach((v) => { const t = mk('text', { x: m.l - 6, y: y(v) + 4, class: 'pl-ax', 'text-anchor': 'end' }); t.textContent = String(v); svg.append(t); });
  const ticks = pulseState.zoom ? x.ticks(d3.utcMonth.every(1)).filter((d) => d >= t0d) : d3.range(2023, +asOfY + 1).map((yr) => new Date(yr + '-01-01T00:00:00Z'));
  ticks.forEach((d) => { const xx = x(d); svg.append(mk('line', { x1: xx, x2: xx, y1: y(0), y2: y(0) + 5, class: 'pl-base' })); const t = mk('text', { x: xx + 3, y: H - 5, class: 'pl-ax' }); t.textContent = pulseState.zoom ? d3.utcFormat('%b')(d) : String(d.getUTCFullYear()); svg.append(t); });
  const gS = mk('g', {}); svg.append(gS);
  const spikes = all.map((r) => { const g = mk('g', { class: 'pl-s ' + (own(r) ? 'own' : 'ctx') + (r.setting === 'wild' ? '' : ' lab') }); const xx = x(r.t);
    const ln = mk('line', { x1: xx, x2: xx, y1: y(0), y2: y(0) }); const c = mk('circle', { cx: xx, cy: y(0), r: r.severity >= 60 ? (phone ? 3 : 3.5) : 2.4 }); g.append(ln, c); gS.append(g); return { r, g, ln, c, xx, top: y(r.severity) }; });
  // landmarks: the two worst real-world incidents in view, labelled directly (wide screens only)
  if (!phone) { const lm = all.filter((r) => r.setting === 'wild' && r.id !== (live && live.id)).sort((a, b) => b.severity - a.severity).slice(0, pulseState.zoom ? 1 : 2).sort((a, b) => a.t - b.t);
    lm.forEach((r, i) => { const lx = x(r.t), ly = y(r.severity); const short = r.title.length > 60 ? r.title.slice(0, r.title.lastIndexOf(' ', 58)) + '…' : r.title;
      svg.append(mk('line', { x1: lx, x2: lx, y1: ly - 6, y2: ly - 16, class: 'pl-lead' })); const lw = (short.length + 5) * 6.4; let anc = 'middle', ty = ly - 20;
      if (lm.length > 1 && i === 0) anc = lx - lw > m.l ? 'end' : 'start';
      else if (lm.length > 1) { const x0 = x(lm[0].t); if (lx + lw < W - 4 && lx > x0) anc = 'start'; else { anc = 'end'; if (lx - lw < x0 + 8) ty = Math.min(ty, y(lm[0].severity) - 38); } }
      else anc = lx + lw / 2 > W - 4 ? 'end' : lx - lw / 2 < m.l ? 'start' : 'middle';
      if (ty !== ly - 20) svg.append(mk('line', { x1: lx, x2: lx, y1: ly - 16, y2: ty + 4, class: 'pl-lead' }));
      const t = mk('text', { x: lx, y: ty, class: 'pl-lm', 'text-anchor': anc }); t.textContent = short + ' · ' + r.severity; svg.append(t); }); }
  // now: the live incident and today's edge
  const nx = x(asOf); svg.append(mk('line', { x1: nx, x2: nx, y1: m.t - 6, y2: y(0), class: 'pl-now' }));
  const nl = mk('text', { x: nx + 6, y: m.t + 2, class: 'pl-nl' }); nl.textContent = 'NOW'; svg.append(nl);
  let ring = null; if (live) { const lx = x(live.t), ly = y(live.severity); ring = mk('circle', { cx: lx, cy: ly, r: 6, class: 'pl-ring' }); svg.append(ring); const lt = mk('text', { x: lx + 10, y: ly + 4, class: 'pl-nl sm' }); lt.textContent = (live.level || '') + ' live'; if (!phone) svg.append(lt); }
  const needle = mk('line', { x1: m.l, x2: m.l, y1: m.t - 6, y2: y(0), class: 'pl-needle' }); needle.style.opacity = 0; svg.append(needle);
  const hl = mk('line', { x1: 0, x2: 0, y1: m.t, y2: y(0), class: 'pl-hl' }); hl.style.opacity = 0; svg.append(hl);
  const hit = mk('rect', { x: m.l, y: 0, width: W - m.l - m.r + 30, height: H, fill: 'transparent', tabindex: '0', 'aria-label': 'Explore the incidents: use the left and right arrow keys; Enter opens one.' }); svg.append(hit);
  fig.append(svg);
  const vis = (r) => pulseState.f === 'all' || (pulseState.f === 'own' ? own(r) : r.severity >= 60);
  const paint = (instant) => { spikes.forEach((s) => { const on = vis(s.r); s.g.classList.toggle('off', !on); if (pulseState.played || instant) { s.ln.setAttribute('y2', s.top); s.c.setAttribute('cy', s.top); } }); summary(); };
  const fmtM = d3.utcFormat('%b %Y');
  const summary = (upto) => { const rows = all.filter((r) => vis(r) && (!upto || r.t <= upto)); const yrRows = rows.filter((r) => r.date.startsWith(asOfY));
    ctr.replaceChildren(el('b', null, String(rows.length)), txt(upto ? ' incidents through ' + fmtM(upto) : (pulseState.f === 'own' ? ' where the AI acted on its own' : pulseState.f === 'severe' ? ' severe or critical' : ' incidents') + ' · ' + yrRows.length + ' of them in ' + asOfY)); };
  const play = () => { const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; pulseState.played = false;
    spikes.forEach((s) => { s.ln.setAttribute('y2', y(0)); s.c.setAttribute('cy', y(0)); s.g.classList.remove('lit'); });
    if (reduce) { pulseState.played = true; paint(true); return; }
    const T = 3200, t0 = performance.now(), d0 = +x.domain()[0], d1 = +asOf; let i = 0; needle.style.opacity = 1;
    const step = (now) => { const k = Math.min(1, (now - t0) / T), e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2, dt = new Date(d0 + (d1 - d0) * e), nxp = x(dt);
      needle.setAttribute('x1', nxp); needle.setAttribute('x2', nxp);
      while (i < spikes.length && spikes[i].r.t <= dt) { const s = spikes[i++]; s.ln.setAttribute('y2', s.top); s.c.setAttribute('cy', s.top); s.g.classList.add('lit'); setTimeout(() => s.g.classList.remove('lit'), 600); }
      summary(dt);
      if (k < 1) requestAnimationFrame(step); else { while (i < spikes.length) { const s = spikes[i++]; s.ln.setAttribute('y2', s.top); s.c.setAttribute('cy', s.top); } needle.style.opacity = 0; pulseState.played = true; summary(); } };
    requestAnimationFrame(step); };
  // hover, tap and keys: the nearest visible spike answers
  let cur = -1;
  const show = (idx) => { const s = spikes[idx]; if (!s) return; cur = idx; spikes.forEach((z, j) => z.g.classList.toggle('hov', j === idx)); hl.setAttribute('x1', s.xx); hl.setAttribute('x2', s.xx); hl.style.opacity = 1;
    const r = s.r; tip.replaceChildren(el('div', 'pt-v', r.severity + '/100 · ' + r.tier), el('div', 'pt-t', r.title), el('div', 'pt-m', showDate(r) + ' · ' + (own(r) ? 'the AI acted on its own' : +r.A === 2 ? 'the AI took a single action' : 'a person used or misused it') + ' · ' + (r.setting === 'wild' ? 'in the real world' : 'in a lab or test')), el('div', 'pt-go', matchMedia('(hover: hover)').matches ? 'Click to open the case →' : 'Tap again to open the case →'));
    tip.hidden = false; const k = svg.getBoundingClientRect().width / W, fw = fig.clientWidth, tw = tip.offsetWidth, left = Math.max(0, Math.min(fw - tw, s.xx * k - tw / 2)); tip.style.left = left + 'px'; tip.style.top = Math.max(0, s.top * k - tip.offsetHeight - 12) + 'px'; };
  const hide = () => { tip.hidden = true; hl.style.opacity = 0; spikes.forEach((z) => z.g.classList.remove('hov')); };
  const nearest = (px, py) => { let b = -1, bd = 1e9; spikes.forEach((s, j) => { if (!vis(s.r)) return; const d = Math.abs(s.xx - px) * 1.6 + Math.abs(s.top - py) * 0.35; if (d < bd) { bd = d; b = j; } }); return bd < 70 ? b : -1; };
  const pt = (e) => { const bb = svg.getBoundingClientRect(); return [(e.clientX - bb.left) * W / bb.width, (e.clientY - bb.top) * H / bb.height]; };
  hit.addEventListener('pointermove', (e) => { const [px, py] = pt(e); const j = nearest(px, py); if (j >= 0) show(j); else hide(); });
  hit.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse') hide(); });
  hit.addEventListener('click', (e) => { const [px, py] = pt(e); const j = nearest(px, py); if (j < 0) return; if (e.pointerType !== 'mouse' && cur !== j) { show(j); return; } location.href = '/i/' + spikes[j].r.id + '/'; });
  hit.addEventListener('keydown', (e) => { const visIdx = spikes.map((s, j) => vis(s.r) ? j : -1).filter((j) => j >= 0); if (!visIdx.length) return; let p = visIdx.indexOf(cur);
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); p = p < 0 ? visIdx.length - 1 : Math.max(0, Math.min(visIdx.length - 1, p + (e.key === 'ArrowRight' ? 1 : -1))); show(visIdx[p]); }
    else if (e.key === 'Enter' && cur >= 0) location.href = '/i/' + spikes[cur].r.id + '/'; else if (e.key === 'Escape') hide(); });
  // what it shows, computed from the record
  const wild = (yr) => full.filter((r) => r.setting === 'wild' && r.date.startsWith(String(yr)));
  const shareOwn = (yr) => { const w = wild(yr); return w.length ? Math.round(100 * w.filter(own).length / w.length) : 0; };
  const sevYr = (yr) => full.filter((r) => r.severity >= 60 && r.date.startsWith(String(yr))).length;
  const top = full.filter((r) => r.date.startsWith(asOfY)).sort((a, b) => b.severity - a.severity)[0];
  const ins = el('div', 'pl-ins');
  const tile = (big, l, sub, href) => { const d = el(href ? 'a' : 'div', 'pl-i'); if (href) d.href = href; d.append(el('b', null, big), el('span', null, l), ...(sub ? [el('small', null, sub)] : [])); return d; };
  const yrs = d3.range(2023, +asOfY + 1);
  ins.append(tile(yrs.map(sevYr).join(' → '), 'severe or critical incidents a year, ' + yrs[0] + ' to ' + asOfY, asOfY + ' so far'),
    tile(Math.round(100 * (C.headline ? C.headline.agentic_early : 0)) + '% → ' + Math.round(100 * (C.headline ? C.headline.agentic_recent : 0)) + '%', 'of real-world incidents where the AI acted on its own', 'before 2025 vs the last 12 months'),
    ...(top ? [tile(top.severity + '/100', 'the worst so far this year', top.title.length > 70 ? top.title.slice(0, 68) + '…' : top.title, '/i/' + top.id + '/')] : []));
  const ft = el('p', 'pl-ft'); ft.append(txt('Each spike is one incident on the index, scored 0–100 by a published formula and linked to its source; dashed spikes happened in labs or tests. The record is the major incidents we can source, not every one. '), (() => { const a = el('a', null, 'Every incident as a table →'); a.href = '/index/#all'; return a; })());
  sec.append(head, ctl, fig, ins, ft);
  paint(pulseState.played);
  if (!pulseState.played) { const io = new IntersectionObserver((en) => { if (en.some((e) => e.isIntersecting)) { io.disconnect(); play(); } }, { threshold: 0.35 }); io.observe(sec); }
  return sec;
}
function drawWire() {
  const items = newsItems(), sirenBox = document.getElementById('siren'), board = document.getElementById('wire-board'), chips = document.getElementById('wire-chips'), cnt = document.getElementById('wire-count'), more = document.getElementById('wire-more');
  document.getElementById('wire-stamp').textContent = 'Updated ' + fmtET(D.meta.as_of) + (D.meta.next_check ? ', next check ' + fmtETsmart(D.meta.next_check).replace('today ', '') : '');
  if (!items.length) { sirenBox.hidden = true; chips.replaceChildren(); board.replaceChildren(el('p', 'count', 'No stories on the board yet. The next refresh fills it.')); cnt.textContent = ''; more.replaceChildren(); return; }
  const siren = items.find((n) => n.siren) || items[0];
  sirenBox.hidden = false;
  const st = el('a', 'siren-t', siren.title); st.href = siren.url; st.target = '_blank'; st.rel = 'noopener noreferrer';
  const sm = el('div', 'siren-m'); sm.append(el('b', null, siren.outlet || ''), el('span', 'ag', ageShort(siren)));
  if ((siren.also || []).length) { const also = el('span', 'also'); also.append(txt('also ')); siren.also.forEach((a, i) => { const l = el('a', null, a.outlet); l.href = a.url; l.target = '_blank'; l.rel = 'noopener noreferrer'; if (i) also.append(txt(', ')); also.append(l); }); sm.append(also); }
  const ic = el('span'); ic.innerHTML = SIREN_SVG;
  const ss = el('div', 'share'); shareRow(ss, { anchor: 'wire', text: siren.title + ' (' + siren.outlet + '). Via Warning Shots:', card: cardForNews(siren) });
  sirenBox.replaceChildren(ic.firstChild, st, sm, ...(siren.summary ? [el('p', 'siren-s', siren.summary)] : []), ss);
  const rest = items.filter((n) => n !== siren);
  const topics = d3.rollups(rest, (v) => v.length, (n) => n.topic || 'other').sort((a, b) => b[1] - a[1]);
  if (!topics.find((t) => t[0] === wire.topic)) wire.topic = 'all';
  const chip = (k, label, n) => { const b = el('button', k === wire.topic ? 'on' : ''); b.type = 'button'; b.append(txt(label), el('b', null, String(n))); b.addEventListener('click', () => { wire.topic = k; drawWire(); }); return b; };
  chips.replaceChildren(chip('all', 'All', items.length), ...topics.filter((t) => t[1] >= 1).map(([k, n]) => chip(k, TOPIC[k] || k, n)));
  const rows = rest.filter((n) => wire.topic === 'all' || (n.topic || 'other') === wire.topic);
  const mfFront = MF() && mfCur === 'front';
  const limit = (wire.open || wire.topic !== 'all') ? rows.length : (mfFront ? 6 : window.innerWidth < 760 ? 12 : 40);
  const fresh = (n) => n.published && (Date.parse(D.meta.as_of) - Date.parse(n.published)) < 8 * 3.6e6;
  board.replaceChildren(...rows.slice(0, limit).map((n) => {
    const it = el('div', 'wi');
    const a = el('a', 'wi-t'); a.href = n.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; if (fresh(n)) a.append(el('i', 'nd')); a.append(txt(n.title));
    const m = el('div', 'wi-m'); const hours = n.published ? (Date.now() - Date.parse(n.published)) / 3.6e6 : 99; const k = n.kind === 'breaking' && hours >= 24 ? null : KIND[n.kind]; if (k) m.append(el('span', 'kind ' + n.kind, k)); m.append(el('b', null, n.outlet || ''), el('span', 'ag', ageShort(n)));
    if ((n.also || []).length) { const also = el('span', 'also'); also.append(txt('also ')); n.also.slice(0, 2).forEach((x, i) => { const l = el('a', null, x.outlet); l.href = x.url; l.target = '_blank'; l.rel = 'noopener noreferrer'; if (i) also.append(txt(', ')); also.append(l); }); m.append(also); }
    it.append(a, m); if (n.touches) it.append(el('div', 'wi-w', 'Who this touches: ' + n.touches)); if (n.summary) it.append(el('div', 'wi-s', n.summary)); it.title = n.summary || ''; it.tabIndex = 0; it.addEventListener('keydown', (e) => { if (e.key === 'Enter' && e.target === it) a.click(); }); return it;
  }));
  const span = d3.extent(items, (n) => n.published);
  const hours = span[0] && span[1] ? Math.round((Date.parse(span[1]) - Date.parse(span[0])) / 3.6e6) : 0;
  cnt.textContent = items.length + ' reports from the last ' + (hours >= 48 ? Math.round(hours / 24) + ' days' : hours + ' hours') + ', newest first. Every headline links to the outlet.';
  more.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', (mfFront ? 'All ' : 'Show all ') + rows.length + ' stories' + (mfFront ? ' →' : '')); b.type = 'button'; b.addEventListener('click', () => { if (mfFront) { go('#wire'); return; } wire.open = true; drawWire(); }); more.append(b); }
  else if (wire.open && rows.length > 12) { const b = el('button', 'more-btn', 'Show fewer'); b.type = 'button'; b.addEventListener('click', () => { wire.open = false; drawWire(); document.getElementById('wire').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); }); more.append(b); }
  shareRow(document.getElementById('wire-share'), { anchor: 'wire', text: 'The Wire: the latest reports on AI incidents, AI-driven attacks and what governments and labs are saying, worldwide, refreshed through the day. Warning Shots:', embed: 'wire', embedH: 720 });
}

/* ---------- hooks */
function drawHooks() {
  const box = document.getElementById('hooks');
  box.replaceChildren(...D.deepdives.slice().sort((a, b) => +a.order - +b.order).filter((d) => d.hook).map((d) => {
    const h = el('div', 'hook'); h.append(el('div', null, d.hook));
    const b = el('button', 'go', d.tab_label.replace(' (live)', '')); b.type = 'button'; b.addEventListener('click', () => go('#d=' + d.incident_id)); h.append(b); return h;
  }));
}

/* ---------- quarters */
function drawQuarters() {
  const box = document.getElementById('ch-quarters');
  if (!box.clientWidth) return;
  const rows = C.quarterly;
  const W = box.clientWidth, H = 260, m = { t: 12, r: 6, b: 34, l: 28 };
  const x = d3.scaleBand(rows.map((r) => r.quarter), [m.l, W - m.r]).paddingInner(0.25).paddingOuter(0.1);
  const y = d3.scaleLinear([0, d3.max(rows, (r) => r.n) || 1], [H - m.b, m.t]).nice();
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Incidents per quarter by autonomy');
  svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickSize(-(W - m.l - m.r)).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(4).tickSizeOuter(0)).call(axisClean).call((g) => g.select('.domain').remove());
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).tickSizeOuter(0).tickFormat((q) => q.endsWith('Q1') ? q.slice(0, 4) : (W > 640 ? q.slice(5) : ''))).call(axisClean);
  const tip = makeTip(box);
  rows.forEach((r) => {
    let y0 = 0; const g = svg.append('g');
    for (let a = 0; a <= 4; a++) { const v = r['a' + a]; if (!v) continue; const y1 = y0 + v; g.append('rect').attr('class', 'bar').attr('data-y', y(y1) + 1).attr('data-h', Math.max(0, y(y0) - y(y1) - 2)).attr('x', x(r.quarter)).attr('width', x.bandwidth()).attr('y', y(y1) + 1).attr('height', Math.max(0, y(y0) - y(y1) - 2)).attr('rx', 2).attr('fill', autoColor(a)).attr('opacity', r.partial ? 0.55 : 1); y0 = y1; }
    g.append('rect').attr('x', x(r.quarter) - 2).attr('width', x.bandwidth() + 4).attr('y', m.t).attr('height', H - m.b - m.t).attr('fill', 'transparent')
      .on('pointermove', () => { const lines = [el('div', 't-sec', r.quarter + (r.partial ? ' (partial)' : '')), (() => { const d = el('div'); d.append(el('span', 't-val', r.n + ' incidents'), el('span', 't-sec', ', worst ' + r.max + '/100')); return d; })()]; for (let a = 4; a >= 0; a--) if (r['a' + a]) { const d = el('div'); const k = el('span'); k.style.cssText = `display:inline-block;width:10px;height:3px;margin-right:6px;vertical-align:middle;background:${autoColor(a)}`; d.append(k, el('b', null, String(r['a' + a])), txt(' ' + AUTONOMY[a].name.toLowerCase())); lines.push(d); } tip.show(lines, (x(r.quarter) + x.bandwidth() / 2) * box.clientWidth / W, y(r.n) * box.clientWidth / W); })
      .on('pointerleave', () => tip.hide());
  });
  keepTip(box, svg.node());
  onVisible(box, 'quarters', (instant) => { if (instant) return; const bars = svg.selectAll('rect.bar'); bars.attr('y', H - m.b).attr('height', 0).transition().delay((d, i) => i * 18).duration(650).ease(d3.easeCubicOut).attr('y', function () { return +this.getAttribute('data-y'); }).attr('height', function () { return +this.getAttribute('data-h'); }); });
  legend(document.getElementById('lg-autonomy2'), AUTONOMY.map((a) => ({ color: autoColor(a.k), label: a.name })));
  const last = rows[rows.length - 1];
  shareRow(document.getElementById('share-quarters'), { anchor: 'card-quarters', text: `AI incidents per quarter since 2023, colored by how much the AI did on its own. The dark share is growing. From Warning Shots:`, svgBox: box, name: 'quarters', title: 'Incidents per quarter, by how much the AI acted on its own', embed: 'quarters', embedH: 420 });
}

/* ---------- disclosure gap */
function drawDisclosure() {
  const box = document.getElementById('ch-disclosure'), call = document.getElementById('disc-callout');
  if (!box.clientWidth) return;
  const rows = C.disclosure, A = C.discAgg;
  const W = box.clientWidth, narrow = W < 520, rowH = narrow ? 30 : 22;
  const H = rows.length * rowH + 40, m = { t: 8, r: narrow ? 52 : 58, b: 28, l: 10 };
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Days from incident to disclosure');
  keepTip(box, svg.node());
  const labG = svg.append('g');
  const maxLabelW = narrow ? W * 0.5 : W * 0.38;
  const labels = rows.map((r) => { const t = labG.append('text').attr('font-size', 11.5).attr('fill', 'var(--ink)').attr('x', m.l).attr('y', 0).text(r.title); let s = r.title; let guard = 0; while (t.node().getComputedTextLength() > maxLabelW && s.length > 8 && guard++ < 80) { s = s.slice(0, -2); t.text(s.trimEnd() + '…'); } return t; });
  const labelW = d3.max(labels, (t) => t.node().getComputedTextLength()) || 100;
  const x0 = m.l + labelW + 12;
  const x = d3.scaleUtc([new Date('2026-01-01'), d3.utcMonth.offset(new Date(C.asOf), 1)], [x0, W - m.r]);
  svg.append('g').attr('class', 'grid').attr('transform', `translate(0,${m.t})`).call(d3.axisBottom(x).ticks(d3.utcMonth.every(narrow ? 3 : 1)).tickSize(H - m.b - m.t).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.utcMonth.every(narrow ? 3 : 2)).tickFormat(d3.utcFormat('%b')).tickSizeOuter(0)).call(axisClean);
  const tip = makeTip(box);
  rows.forEach((r, i) => {
    const cy = m.t + i * rowH + rowH / 2;
    labels[i].attr('y', cy).attr('dy', '0.35em');
    const xa = x(new Date(r.date)), xb = x(new Date(r.disclosed)), slow = r.lag > 60, col = slow ? 'var(--alarm)' : 'var(--steel)';
    const g = svg.append('g');
    g.append('line').attr('class', 'lag').attr('data-x2', xb).attr('x1', xa).attr('x2', xb).attr('y1', cy).attr('y2', cy).attr('stroke', col).attr('stroke-width', 2).attr('stroke-linecap', 'round');
    g.append('circle').attr('cx', xa).attr('cy', cy).attr('r', 4).attr('fill', 'var(--paper)').attr('stroke', col).attr('stroke-width', 2);
    g.append('circle').attr('class', 'lagend').attr('data-x', xb).attr('cx', xb).attr('cy', cy).attr('r', 4.5).attr('fill', col).attr('stroke', 'var(--paper)').attr('stroke-width', 1.5);
    g.append('text').attr('class', 'laglabel').attr('x', xb + 9).attr('y', cy).attr('dy', '0.35em').attr('font-size', 11).attr('fill', slow ? 'var(--alarm)' : 'var(--ink-2)').attr('font-weight', slow ? 600 : 400).text(r.lag ? r.lag + ' d' : 'same day');
    g.append('rect').attr('x', 0).attr('y', cy - rowH / 2).attr('width', W).attr('height', rowH).attr('fill', 'transparent').style('cursor', 'pointer')
      .on('pointermove', (ev) => { const [px] = d3.pointer(ev, svg.node()); tip.show([el('div', 't-title', r.title), el('div', 't-sec', 'Happened ' + showDate(r) + '; public ' + fmtDate(new Date(r.disclosed))), (() => { const d = el('div'); d.append(el('span', 't-val', r.lag + ' days'), el('span', 't-sec', r.lag > 60 ? ', found by the lab itself' : '')); return d; })(), el('div', 't-cta', 'Click to open')], px * box.clientWidth / W, cy * box.clientWidth / W); })
      .on('pointerleave', () => tip.hide()).on('click', () => openIncident(r.id));
  });
  onVisible(box, 'disclosure', (instant) => { if (instant) return; svg.selectAll('line.lag').attr('x2', function () { return +this.getAttribute('x1'); }).transition().delay((d, i) => i * 40).duration(700).ease(d3.easeCubicOut).attr('x2', function () { return +this.getAttribute('data-x2'); }); svg.selectAll('circle.lagend').attr('cx', function () { return +this.parentNode.querySelector('line').getAttribute('x1'); }).transition().delay((d, i) => i * 40).duration(700).ease(d3.easeCubicOut).attr('cx', function () { return +this.getAttribute('data-x'); }); svg.selectAll('text.laglabel').attr('opacity', 0).transition().delay((d, i) => 500 + i * 40).duration(300).attr('opacity', 1); });
  legend(document.getElementById('lg-disclosure'), [{ color: 'var(--steel)', shape: 'ring', label: 'happened' }, { color: 'var(--steel)', label: 'became public' }, { color: 'var(--alarm)', shape: 'bar', label: 'more than two months' }]);
  call.replaceChildren(
    txt('Of the '), el('b', null, String(A.n)), txt(' real-world incidents this year where the AI acted on its own, '), el('b', null, String(A.n_slow)), txt(' took more than two months to surface, a median of '), el('b', null, String(A.median_slow)), txt(' days, the longest '), el('b', null, String(A.max)), txt(". Every slow one happened inside a lab's own training or testing, where only the lab knew; the fast ones were caught by the victim. So the right edge of every chart here is a floor: on this pattern, most of what happened inside labs in the last three months is still unreported."),
    ...(A.monitor_lag != null ? [txt(" One test of whether that is changing: OpenAI's newest log entry was posted "), el('b', null, String(A.monitor_lag)), txt(' days after the incident, not a hundred.')] : []),
  );
  shareRow(document.getElementById('share-disclosure'), { anchor: 'card-disclosure', text: `${A.n_slow} of this year's ${A.n} real-world AI incidents where the AI acted on its own took more than two months to become public (median ${A.median_slow} days). All of them happened inside a lab's own training or tests. Warning Shots:`, svgBox: box, name: 'disclosure-gap', title: 'How long the world waited to find out', embed: 'disclosure', embedH: 760 });
}

/* ---------- scatter + horizon */
function drawScatter() {
  const box = document.getElementById('ch-scatter');
  if (!box.clientWidth) return;
  const rows = C.scored;
  const W = box.clientWidth, H = Math.min(380, Math.max(300, W * 0.8)), m = { t: 10, r: 10, b: 36, l: 38 };
  const x = d3.scaleLinear([0, 100], [m.l, W - m.r]), y = d3.scaleLinear([0, 100], [H - m.b, m.t]);
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Harm score against signal score');
  svg.append('rect').attr('x', x(60)).attr('y', y(100)).attr('width', x(100) - x(60)).attr('height', y(60) - y(100)).attr('fill', 'var(--alarm)').attr('opacity', 0.08).attr('rx', 6);
  svg.append('text').attr('x', x(98)).attr('y', y(97)).attr('text-anchor', 'end').attr('font-size', 11.5).attr('font-weight', 600).attr('fill', 'var(--alarm)').text('Danger zone');
  svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(5).tickSizeOuter(0)).call(axisClean);
  svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSizeOuter(0)).call(axisClean).call((g) => g.select('.domain').remove());
  svg.append('text').attr('x', W - m.r).attr('y', H - 4).attr('text-anchor', 'end').attr('font-size', 11).attr('fill', 'var(--ink-2)').text('Signal (autonomy + novelty) →');
  svg.append('text').attr('x', m.l + 6).attr('y', m.t + 12).attr('font-size', 11).attr('fill', 'var(--ink-2)').text('↑ Harm (damage, reach, permanence)');
  const pts = rows.map((r, i) => ({ r, px: x(r.signal_score) + ((i * 37) % 7 - 3), py: y(r.harm_score) + ((i * 53) % 7 - 3) }));
  svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', (p) => p.px).attr('cy', (p) => p.py).attr('r', 5).attr('fill', (p) => p.r.setting === 'wild' ? 'var(--wild)' : 'var(--lab)').attr('stroke', 'var(--paper)').attr('stroke-width', 1.5).attr('opacity', 0.55);
  // centre of gravity of real-world incidents, by year
  const cg = d3.groups(rows.filter((r) => r.setting === 'wild'), (r) => r.date.slice(0, 4)).sort((a, b) => a[0].localeCompare(b[0])).map(([yr, rs]) => ({ yr, n: rs.length, x: x(d3.mean(rs, (r) => r.signal_score)), y: y(d3.mean(rs, (r) => r.harm_score)) }));
  const cgG = svg.append('g');
  const cgPath = cgG.append('path').attr('d', d3.line().x((c) => c.x).y((c) => c.y)(cg)).attr('fill', 'none').attr('stroke', 'var(--alarm)').attr('stroke-width', 2.5).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round');
  onVisible(box, 'scatter', (instant) => { if (instant) return; const L = cgPath.node().getTotalLength(); cgPath.attr('stroke-dasharray', L + ' ' + L).attr('stroke-dashoffset', L).transition().duration(1400).ease(d3.easeCubicInOut).attr('stroke-dashoffset', 0); cgG.selectAll('circle, text').attr('opacity', 0).transition().delay((d, i) => 300 + i * 220).duration(300).attr('opacity', 1); });
  cg.forEach((c, i) => {
    cgG.append('circle').attr('cx', c.x).attr('cy', c.y).attr('r', i === cg.length - 1 ? 7 : 5).attr('fill', 'var(--alarm)').attr('stroke', 'var(--paper)').attr('stroke-width', 2);
    const t = cgG.append('text').attr('x', c.x + (i === cg.length - 1 ? 12 : 0)).attr('y', c.y + (i === cg.length - 1 ? 4 : (i % 2 ? 20 : -12))).attr('text-anchor', i === cg.length - 1 ? 'start' : 'middle').attr('font-size', 11.5).attr('font-weight', 600).attr('fill', 'var(--alarm)').attr('stroke', 'var(--panel)').attr('stroke-width', 3).attr('paint-order', 'stroke').text(c.yr + (i === cg.length - 1 ? ' so far' : ''));
  });
  if (cg.length > 1) { const a = cg[cg.length - 2], b = cg[cg.length - 1]; const ang = Math.atan2(b.y - a.y, b.x - a.x); const tx = b.x + 22 * Math.cos(ang), ty = b.y + 22 * Math.sin(ang); cgG.append('line').attr('x1', b.x + 8 * Math.cos(ang)).attr('y1', b.y + 8 * Math.sin(ang)).attr('x2', tx).attr('y2', ty).attr('stroke', 'var(--alarm)').attr('stroke-width', 2.5).attr('stroke-linecap', 'round').attr('stroke-dasharray', '3 3'); cgG.append('path').attr('d', `M${tx - 10 * Math.cos(ang - 0.5)},${ty - 10 * Math.sin(ang - 0.5)} L${tx},${ty} L${tx - 10 * Math.cos(ang + 0.5)},${ty - 10 * Math.sin(ang + 0.5)}`).attr('fill', 'none').attr('stroke', 'var(--alarm)').attr('stroke-width', 2.5).attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round'); }
  const sc = document.getElementById('scatter-callout');
  if (sc && cg.length > 1) { const f = cg[0], l = cg[cg.length - 1]; const sig = (c) => Math.round(x.invert(c.x)), hm = (c) => Math.round(y.invert(c.y)); sc.replaceChildren(txt('The centre of gravity of real-world incidents has moved from a signal score of '), el('b', null, String(sig(f))), txt(' in ' + f.yr + ' to '), el('b', null, String(sig(l))), txt(' this year, while harm has stayed near '), el('b', null, String(hm(l))), txt('. So far the AI is doing more on its own without doing much more damage. The danger zone is where that stops being true, and the arrow points at it.')); }
  const hi = svg.append('circle').attr('r', 9).attr('fill', 'none').attr('stroke', 'var(--ink)').attr('stroke-width', 1.5).attr('opacity', 0);
  const del = d3.Delaunay.from(pts, (p) => p.px, (p) => p.py), tip = makeTip(box);
  svg.append('rect').attr('x', m.l).attr('y', 0).attr('width', W - m.l - m.r).attr('height', H - m.b).attr('fill', 'transparent').style('cursor', 'pointer')
    .on('pointermove', (ev) => { const [px, py] = d3.pointer(ev); const p = pts[del.find(px, py)]; if (Math.hypot(p.px - px, p.py - py) > 36) { tip.hide(); hi.attr('opacity', 0); return; } hi.attr('cx', p.px).attr('cy', p.py).attr('opacity', 1); tip.show([...incidentTip(p.r).slice(0, 3), el('div', 't-sec', 'Harm ' + p.r.harm_score + ', signal ' + p.r.signal_score), el('div', 't-cta', 'Click to open')], p.px * box.clientWidth / W, p.py * box.clientWidth / W); })
    .on('pointerleave', () => { tip.hide(); hi.attr('opacity', 0); })
    .on('click', (ev) => { const [px, py] = d3.pointer(ev); const p = pts[del.find(px, py)]; if (p && Math.hypot(p.px - px, p.py - py) <= 36) openIncident(p.r.id); });
  keepTip(box, svg.node());
  legend(document.getElementById('lg-setting'), [{ color: 'var(--wild)', label: 'in the wild' }, { color: 'var(--lab)', label: 'in the lab or a test' }, { color: 'var(--alarm)', shape: 'bar', label: 'centre of gravity of real-world incidents, by year' }]);
  shareRow(document.getElementById('share-scatter'), { anchor: 'card-scatter', text: 'Every major AI incident since 2023 plotted by damage done against what it signals about where AI is going. Real-world incidents are climbing toward the danger zone. Warning Shots:', svgBox: box, name: 'danger-zone', title: 'Harm against signal, every incident', embed: 'scatter', embedH: 520 });
}
function drawHorizon() {
  const box = document.getElementById('ch-horizon'), call = document.getElementById('horizon-callout');
  if (!box.clientWidth) return;
  const rows = D.horizon.map((r) => ({ ...r, _d: new Date(r.date), minutes: +r.minutes })).sort((a, b) => a._d - b._d);
  const W = box.clientWidth, H = 300, m = { t: 14, r: 16, b: 28, l: 52 };
  const x = d3.scaleUtc([d3.min(rows, (r) => r._d), new Date('2026-12-31')], [m.l, W - m.r]);
  const y = d3.scaleLog([d3.min(rows, (r) => r.minutes) / 1.5, d3.max(rows, (r) => r.minutes) * 2], [H - m.b, m.t]);
  const fmtMin = (v) => v < 1 ? Math.round(v * 60) + ' sec' : v < 60 ? Math.round(v) + ' min' : v < 60 * 48 ? d3.format('.2~r')(v / 60) + ' hr' : d3.format('.2~r')(v / 60 / 24) + ' days';
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'METR time horizon over time');
  const ticks = [1 / 6, 1, 4, 15, 60, 240, 960, 3840, 15360].filter((v) => v >= y.domain()[0] && v <= y.domain()[1]);
  svg.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues(ticks).tickSize(-(W - m.l - m.r)).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).tickValues(ticks).tickFormat(fmtMin).tickSizeOuter(0)).call(axisClean).call((g) => g.select('.domain').remove());
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat(d3.utcFormat('%Y')).tickSizeOuter(0)).call(axisClean);
  svg.append('path').attr('d', d3.line().x((r) => x(r._d)).y((r) => y(r.minutes))(rows)).attr('fill', 'none').attr('stroke', 'var(--steel)').attr('stroke-width', 2).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round');
  svg.append('g').selectAll('circle').data(rows).join('circle').attr('cx', (r) => x(r._d)).attr('cy', (r) => y(r.minutes)).attr('r', 4).attr('fill', 'var(--steel)').attr('stroke', 'var(--paper)').attr('stroke-width', 2);
  const last = rows[rows.length - 1];
  svg.append('text').attr('x', x(last._d) - 8).attr('y', y(last.minutes) - 10).attr('text-anchor', 'end').attr('font-size', 11.5).attr('font-weight', 600).attr('fill', 'var(--ink)').text(last.model + ', ' + last.duration_label);
  const tip = makeTip(box), del = d3.Delaunay.from(rows, (r) => x(r._d), (r) => y(r.minutes));
  svg.append('rect').attr('x', m.l).attr('y', 0).attr('width', W - m.l - m.r).attr('height', H - m.b).attr('fill', 'transparent')
    .on('pointermove', (ev) => { const [px, py] = d3.pointer(ev); const r = rows[del.find(px, py)]; const d = el('div'); d.append(el('span', 't-val', fmtMin(r.minutes))); tip.show([el('div', 't-sec', fmtMonth(r._d)), el('div', 't-title', r.model), d], x(r._d) * box.clientWidth / W, y(r.minutes) * box.clientWidth / W); })
    .on('pointerleave', () => tip.hide());
  keepTip(box, svg.node());
  const dbl = rows.find((r) => r.doubling_months), first = rows[0];
  call.replaceChildren(txt('From '), el('b', null, first.duration_label), txt(' (' + first.model + ') to '), el('b', null, last.duration_label), txt(' (' + last.model + ')' + (dbl ? '. METR’s fitted trend doubles roughly every ' : '.')), ...(dbl ? [el('b', null, String(dbl.doubling_months)), txt(' months. Each doubling lets an agent run about twice as long between human checks, and lets a mistake travel twice as far before anyone notices. METR’s suite cannot yet measure models released after spring 2026.')] : []));
  shareRow(document.getElementById('share-horizon'), { anchor: 'card-horizon', text: `How long AI can work unsupervised: from ${first.duration_label} (${first.model}) to ${last.duration_label} (${last.model}), per METR. Warning Shots:`, svgBox: box, name: 'time-horizon', title: 'How long AI can work unsupervised (METR 50% time horizon)', embed: 'horizon', embedH: 520 });
}

/* ---------- pipeline */
function drawPipeline() {
  const box = document.getElementById('ch-pipeline'), call = document.getElementById('pipeline-callout');
  if (!box.clientWidth) return;
  const rows = D.pipeline.map((p) => ({ ...p, _l: new Date(p.lab_date), _w: p.wild_date ? new Date(p.wild_date) : null })).sort((a, b) => a._l - b._l);
  const W = box.clientWidth, narrow = W < 620, labelW = narrow ? 0 : Math.min(230, W * 0.3), rowH = narrow ? 52 : 38;
  const H = rows.length * rowH + 34, m = { t: 6, r: 12, b: 28, l: 12 + labelW };
  const today = new Date(C.asOf), horizonEnd = d3.utcYear.offset(today, 1);
  const x = d3.scaleUtc([new Date('2023-01-01'), horizonEnd], [m.l, W - m.r]);
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Lab-to-wild timeline per behavior');
  svg.append('rect').attr('x', x(today)).attr('y', m.t).attr('width', x(horizonEnd) - x(today)).attr('height', H - m.b - m.t).attr('fill', 'var(--alarm)').attr('opacity', 0.05);
  svg.append('text').attr('x', (x(today) + x(horizonEnd)) / 2).attr('y', H - m.b - 6).attr('text-anchor', 'middle').attr('font-size', 10.5).attr('fill', 'var(--ink-2)').text('Next 12 months');
  svg.append('g').attr('class', 'grid').attr('transform', `translate(0,${m.t})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickSize(H - m.b - m.t).tickFormat(''));
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat(d3.utcFormat('%Y')).tickSizeOuter(0)).call(axisClean);
  svg.append('line').attr('x1', x(today)).attr('x2', x(today)).attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--line-2)').attr('stroke-dasharray', '3 3');
  const tip = makeTip(box);
  rows.forEach((p, i) => {
    const cy = m.t + i * rowH + (narrow ? 34 : rowH / 2), g = svg.append('g');
    if (narrow) g.append('text').attr('x', m.l).attr('y', cy - 14).attr('font-size', 12).attr('font-weight', 600).attr('fill', 'var(--ink)').text(p.behavior);
    else g.append('text').attr('x', 12).attr('y', cy).attr('dy', '0.35em').attr('font-size', 12).attr('font-weight', 600).attr('fill', 'var(--ink)').text(p.behavior.length > 32 ? p.behavior.slice(0, 30) + '…' : p.behavior);
    const x0 = x(p._l), x1 = p._w ? x(p._w) : x(today);
    g.append('line').attr('class', 'pl').attr('data-x2', x1).attr('x1', x0).attr('x2', x1).attr('y1', cy).attr('y2', cy).attr('stroke', p._w ? 'var(--steel)' : 'var(--line-2)').attr('stroke-width', 2).attr('stroke-linecap', 'round').attr('stroke-dasharray', p._w ? null : '4 3');
    g.append('circle').attr('cx', x0).attr('cy', cy).attr('r', 5.5).attr('fill', 'var(--paper)').attr('stroke', 'var(--lab)').attr('stroke-width', 2.5);
    if (p._w) { g.append('circle').attr('cx', x1).attr('cy', cy).attr('r', 6).attr('fill', 'var(--steel)').attr('stroke', 'var(--paper)').attr('stroke-width', 2); const lr = C.lags.find((l) => l.behavior === p.behavior); if (lr && lr.lag != null) g.append('text').attr('x', (x0 + x1) / 2).attr('y', cy - 7).attr('text-anchor', 'middle').attr('font-size', 10.5).attr('fill', 'var(--ink-2)').text(lr.lag + ' mo'); }
    else { g.append('path').attr('d', `M${x1 + 2},${cy - 5} L${x1 + 9},${cy} L${x1 + 2},${cy + 5}`).attr('fill', 'none').attr('stroke', 'var(--line-2)').attr('stroke-width', 2).attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round'); g.append('text').attr('x', x1 + 14).attr('y', cy).attr('dy', '0.35em').attr('font-size', 11).attr('font-weight', 600).attr('fill', 'var(--alarm)').text(p.next12_label ? p.next12_label + ' in 12 mo' : 'pending'); }
    g.append('rect').attr('x', 0).attr('y', cy - rowH / 2).attr('width', W).attr('height', rowH).attr('fill', 'transparent')
      .on('pointermove', (ev) => { const [px] = d3.pointer(ev, svg.node()); const lines = [el('div', 't-title', p.behavior), el('div', 't-sec', 'In a test, ' + fmtMonth(p._l)), el('div', null, p.lab_case)]; if (p._w) lines.push(el('div', 't-sec', 'In real use, ' + fmtMonth(p._w)), el('div', null, p.wild_case)); else lines.push(el('div', 't-sec', 'Not yet seen outside tests'), el('div', null, p.wild_case || '')); tip.show(lines, px * box.clientWidth / W, cy * box.clientWidth / W); })
      .on('pointerleave', () => tip.hide());
  });
  keepTip(box, svg.node());
  onVisible(box, 'pipeline', (instant) => { if (instant) return; svg.selectAll('line.pl').attr('x2', function () { return +this.getAttribute('x1'); }).transition().delay((d, i) => i * 60).duration(800).ease(d3.easeCubicOut).attr('x2', function () { return +this.getAttribute('data-x2'); }); });
  legend(document.getElementById('lg-pipeline'), [{ color: 'var(--lab)', shape: 'ring', label: 'first seen in a lab or test' }, { color: 'var(--steel)', label: 'first seen in real use' }]);
  const L = C.lagAgg;
  call.replaceChildren(el('b', null, String(L.n_arrived)), txt(' behaviors first seen in testing have already shown up in real use, a median of '), el('b', null, String(L.median)), txt(' months later, and the gap is closing: behaviors first seen in tests in 2023–24 took about '), el('b', null, String(L.early)), txt(' months to reach real use; those first seen since 2025 took about '), el('b', null, String(L.recent)), txt(', because training and test environments now touch the live internet. '), el('b', null, String(L.n_open)), txt(' are still in the pipeline, including the ones researchers worry about most: resisting shutdown and copying itself out.'));
  shareRow(document.getElementById('share-pipeline'), { anchor: 'card-pipeline', text: `${L.n_arrived} dangerous AI behaviors first seen in safety tests have now shown up in the real world, a median of ${L.median} months later. ${L.n_open} more are still in the pipeline. Warning Shots:`, svgBox: box, name: 'lab-to-wild', title: 'From the lab to the wild: when each behavior first appeared', embed: 'pipeline', embedH: 640 });
}

/* ---------- next: watch, drivers, forecasts, calendar */
function drawWatch() {
  const box = document.getElementById('watch-list');
  box.replaceChildren(...D.watch.map((w) => {
    const r = el('div', 'watch-row'); r.append(el('div', 'item', w.item), el('span', 'st' + (w.kind === 'due' ? ' due' : ''), w.status));
    const why = el('div', 'why'); why.append(txt(w.why + ' ')); const a = el('a', null, w.source_label); a.href = w.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; why.append(a); r.append(why); return r;
  }));
}
function drawDrivers() {
  document.getElementById('drivers').replaceChildren(...D.drivers.map((d) => { const c = el('div', 'driver'); c.append(el('div', 'dn', d.stat), el('div', 'dl', d.stat_label), el('h4', null, d.title), el('p', null, d.body)); return c; }));
}

/* ---------- the next warning shots: the call sheet (dated yes/no questions with the index's odds), reader picks kept in this browser */
const callRows = () => (D.calls || []).filter((c) => c && c.question && c.resolve_by);
const callOpen = (c) => !c.resolution;
const callDays = (c) => Math.ceil((Date.parse(c.resolve_by + 'T00:00:00-04:00') - Date.now()) / 864e5); // whole days until the resolution date, Eastern
const callLean = (c) => +c.odds >= 0.5;
const likelyWord = (p) => (p = +p, p >= 0.85 ? 'Very likely' : p >= 0.6 ? 'Likely' : p > 0.4 ? 'Could go either way' : p > 0.15 ? 'Unlikely' : 'Very unlikely');
const houseHit = (c) => !!(c.resolution && c.resolution.outcome !== 'void' && Math.abs(+c.odds - 0.5) > 1e-9 && (callLean(c) === (c.resolution.outcome === 'yes')));
const PICKS = (() => { try { return JSON.parse(localStorage.getItem('ws-calls') || '{}'); } catch (e) { return {}; } })();
function setPick(id, pick) { if (PICKS[id] && PICKS[id].pick === pick) delete PICKS[id]; else PICKS[id] = { pick, at: new Date().toISOString() }; try { localStorage.setItem('ws-calls', JSON.stringify(PICKS)); } catch (e) {} drawCallStrip(); drawForecast(); drawRibbon(); }
function houseRecord() {
  const g = callRows().filter((c) => c.resolution && c.resolution.outcome !== 'void');
  const toss = (c) => Math.abs(+c.odds - 0.5) < 1e-9; const g2 = g.filter((c) => !toss(c)); // a 50% call counts as neither right nor wrong
  const w = g2.filter(houseHit).length;
  return { w, l: g2.length - w, n: g2.length, tossups: g.length - g2.length, brier: g.length ? g.reduce((a, c) => a + Math.pow(+c.odds - (c.resolution.outcome === 'yes' ? 1 : 0), 2), 0) / g.length : null, open: callRows().filter(callOpen).length };
}
function myRecord() {
  const made = Object.keys(PICKS).filter((id) => callRows().some((c) => c.id === id));
  const g = callRows().filter((c) => PICKS[c.id] && c.resolution && c.resolution.outcome !== 'void');
  const w = g.filter((c) => PICKS[c.id].pick === c.resolution.outcome).length;
  return { made: made.length, w, l: g.length - w, n: g.length };
}
function callDue(c) {
  if (c.resolution) return (c.resolution.outcome === 'void' ? 'Void' : 'Resolved ' + (c.resolution.outcome === 'yes' ? 'yes' : 'no')) + ' · ' + fmtDate(new Date(c.resolution.date));
  const d = callDays(c);
  return (d < 0 ? 'Awaiting grade' : d === 0 ? 'Resolves today' : d === 1 ? 'Resolves tomorrow' : 'Resolves in ' + d + ' days') + ' · ' + fmtDay(new Date(c.resolve_by + 'T12:00:00Z'));
}
function pickButtons(c, cls) {
  return el('span', 'call-pick-none');
  const wrap = el('span', cls || 'call-pick'); const mine = PICKS[c.id] && PICKS[c.id].pick;
  if (c.resolution) {
    const out = c.resolution.outcome;
    if (mine) { const hit = mine === out; wrap.append(el('span', 'you', ''), txt('')); const y = wrap.querySelector('.you'); y.append(txt('You said ' + mine + ': '), el('b', null, out === 'void' ? 'void' : hit ? 'right' : 'wrong')); }
    return wrap;
  }
  ['yes', 'no'].forEach((p) => { const b = el('button', mine === p ? 'on' : ''); b.type = 'button'; b.textContent = p === 'yes' ? 'Yes' : 'No'; b.setAttribute('aria-pressed', String(mine === p)); b.setAttribute('aria-label', 'Your call: ' + p); b.addEventListener('click', (e) => { e.stopPropagation(); setPick(c.id, p); }); wrap.append(b); });
  const you = el('span', 'you'); if (mine) { you.append(txt('You: '), el('b', null, mine)); } else if (cls !== 'fc-pick') you.textContent = 'Your call';
  wrap.append(you); return wrap;
}
let callOpenWhy = null;
function drawCallStrip() {
  const box = document.getElementById('calls-strip'), k = document.getElementById('calls-k'), sec = document.getElementById('calls'); if (!box) return;
  const all = callRows(); if (!all.length) { sec.style.display = 'none'; return; } sec.style.display = '';
  const open = all.filter(callOpen).sort((a, b) => a.resolve_by.localeCompare(b.resolve_by) || Math.abs(0.5 - +a.odds) - Math.abs(0.5 - +b.odds));
  const recent = all.filter((c) => c.resolution && (Date.now() - Date.parse(c.resolution.date)) < 7 * 864e5).sort((a, b) => b.resolution.date.localeCompare(a.resolution.date));
  const show = recent.slice(0, 1).concat(open).slice(0, 5);
  const hr = houseRecord(), me = myRecord();
  k.replaceChildren(el('b', null, String(hr.open) + ' open calls'), txt(' · the index’s record '), el('b', null, hr.w + '–' + hr.l), txt(hr.n ? ' · Brier ' + hr.brier.toFixed(2) : (open.length ? ' · first grade ' + fmtDay(new Date(open[0].resolve_by)) : '')), txt(me.made ? ' · your calls ' + me.made + (me.n ? ', record ' + me.w + '–' + me.l : '') : ' · make yours below'));
  box.replaceChildren(...show.map((c) => {
    const card = el('article', 'call' + (callLean(c) ? '' : ' lean-no') + (c.resolution ? ' graded' : '')); card.dataset.id = c.id; card.setAttribute('aria-label', 'Call: ' + c.question);
    const top = el('div', 'call-top'); const due = el('span'); if (!c.resolution && callDays(c) <= 3) { due.append(el('b', null, callDue(c))); } else due.textContent = callDue(c); top.append(due, el('span', null, c.horizon === 'days' ? 'short' : c.horizon === 'weeks' ? 'weeks' : 'long'));
    const q = el('h3', 'call-q', c.question);
    const odds = el('div', 'call-odds'); odds.append(el('b', null, c.odds_label || Math.round(+c.odds * 100) + '%'), el('span', null, +c.odds === 0.5 ? 'a coin flip, by the index' : callLean(c) ? 'the index says yes' : 'chance of yes; the index leans no'));
    card.append(top, q, odds);
    if (c.resolution) { const o = el('span', 'call-out ' + (c.resolution.outcome === 'void' ? '' : houseHit(c) ? 'hit' : 'miss')); o.textContent = c.resolution.outcome === 'void' ? 'void' : (c.resolution.outcome === 'yes' ? 'Yes' : 'No') + ' · index ' + (houseHit(c) ? 'right' : 'wrong'); card.append(o); }
    card.append(pickButtons(c));
    const why = el('button', 'call-why', callOpenWhy === c.id ? 'Hide the reasoning' : 'Why these odds'); why.type = 'button'; why.addEventListener('click', () => { callOpenWhy = callOpenWhy === c.id ? null : c.id; drawCallStrip(); }); card.append(why);
    if (callOpenWhy === c.id) { const b = el('div', 'call-basis'); b.append(el('b', null, 'Why: '), txt(c.basis || '')); if (c.signposts) b.append(el('br'), el('b', null, 'Watch for: '), txt(c.signposts)); if (c.resolution && c.resolution.note) b.append(el('br'), el('b', null, 'Resolution: '), txt(c.resolution.note + ' ')); if ((c.resolution && c.resolution.source_url) || c.source_url) { const a = el('a', null, 'source'); a.href = (c.resolution && c.resolution.source_url) || c.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; b.append(txt(' '), a); } card.append(b); }
    return card;
  }));
}
let fcOpen = false;
function drawForecast() {
  const box = document.getElementById('forecast-list'), more = document.getElementById('forecast-more'), rec = document.getElementById('call-record'); if (!box) return;
  const all = callRows(); if (!all.length) return;
  const hr = houseRecord(), me = myRecord();
  if (rec) { rec.replaceChildren(el('span', null, ''), el('span', null, ''), el('span', null, '')); const [a, b, c] = rec.children; a.append(el('b', null, 'Track record: ' + hr.w + ' right, ' + hr.l + ' wrong'), txt(hr.n ? ' on ' + hr.n + ' graded questions' : ' · nothing has resolved yet; the first questions are graded on ' + fmtDay(new Date(all.filter(callOpen).sort((x, y) => x.resolve_by.localeCompare(y.resolve_by))[0].resolve_by)))); c.append(txt(all.filter((x) => callOpen(x) && x.kind === 'call').length + ' open calls (resolving in days to weeks) and ' + all.filter((x) => callOpen(x) && x.kind !== 'call').length + ' open questions (months to years). The index’s estimate can move before a question resolves when the evidence does; every change is logged and explained in the changelog.')); }
  const now = Date.now();
  const groups = [['Resolving within a week', (c) => callOpen(c) && callDays(c) <= 7], ['Within a month', (c) => callOpen(c) && callDays(c) > 7 && callDays(c) <= 31], ['Within three months', (c) => callOpen(c) && callDays(c) > 31 && callDays(c) <= 93], ['Later', (c) => callOpen(c) && callDays(c) > 93], ['Graded', (c) => !callOpen(c)]];
  const LIMIT = 14; let shown = 0;
  box.replaceChildren(...groups.map(([label, test]) => {
    const items = all.filter(test).sort((a, b) => (callOpen(a) ? a.resolve_by.localeCompare(b.resolve_by) || (+b.odds - +a.odds) : (b.resolution.date.localeCompare(a.resolution.date))));
    const g = el('div', 'fc-group'); if (!items.length) return g; g.append(el('div', 'fc-ghead', label + ' · ' + items.length));
    items.forEach((r) => {
      if (!fcOpen && shown >= LIMIT) return; shown++;
      const row = el('div', 'fc' + (r.resolution ? ' graded' : '')); row.tabIndex = 0; row.id = 'fc-' + r.id;
      const ev = el('div', 'fc-event'); ev.append(txt(r.question));
      if (r.resolution) { const res = el('span', 'fc-res ' + (r.resolution.outcome === 'void' ? '' : houseHit(r) ? 'hit' : 'miss')); res.textContent = r.resolution.outcome === 'void' ? 'void' : (r.resolution.outcome === 'yes' ? 'Yes' : 'No') + (Math.abs(+r.odds - 0.5) < 1e-9 ? ' · called a toss-up, not counted' : ' · index ' + (houseHit(r) ? 'right' : 'wrong')); ev.append(res); }
      ev.append(el('span', 'fc-due', callDue(r)));
      const bar = el('div', 'fc-bar'); const p = +r.odds; const w = el('span', 'fc-word' + (p >= 0.6 ? ' hi' : p <= 0.4 ? ' lo' : ''), (r.resolution ? 'Expected: ' : 'The index expects: ') + likelyWord(p).toLowerCase()); w.title = 'The index’s estimate: ' + Math.round(p * 100) + '%'; bar.append(w);
      const moreB = el('div', 'fc-more'); const b1 = el('div'); b1.append(el('b', null, 'Why: '), txt(r.basis || '')); const b2 = el('div'); b2.style.marginTop = '4px'; b2.append(el('b', null, 'Watch for: '), txt(r.signposts || '')); moreB.append(b1, b2);
      if (r.resolution && r.resolution.note) { const b3 = el('div'); b3.style.marginTop = '4px'; b3.append(el('b', null, 'Resolution: '), txt(r.resolution.note + ' ')); if (r.resolution.source_url) { const a = el('a', null, 'source'); a.href = r.resolution.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); b3.append(a); } moreB.append(b3); }
      else if (r.source_url) { const b4 = el('div'); b4.style.marginTop = '4px'; const a = el('a', null, 'Where it will be checked'); a.href = r.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); b4.append(a); moreB.append(b4); }
      { const pl = el('div'); pl.style.marginTop = '6px'; const a = el('a', null, 'Its own page, with a share card →'); a.href = '/forecast/' + r.id + '/'; a.addEventListener('click', (e) => e.stopPropagation()); pl.append(a); moreB.append(pl); }
      row.append(ev, bar, moreB);
      const toggle = () => row.classList.toggle('open');
      row.addEventListener('click', toggle); row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
      g.append(row);
    });
    return g;
  }).filter((g) => g.children.length > 1));
  more.replaceChildren();
  if (all.length > LIMIT) { const b = el('button', 'more-btn', fcOpen ? 'Show fewer' : 'Show all ' + all.length + ' questions (' + all.filter(callOpen).length + ' open, ' + (all.length - all.filter(callOpen).length) + ' graded)'); b.type = 'button'; b.addEventListener('click', () => { fcOpen = !fcOpen; drawForecast(); }); more.append(b); }
  const soon = all.filter(callOpen).sort((a, b) => a.resolve_by.localeCompare(b.resolve_by))[0];
  shareRow(document.getElementById('share-forecast'), { anchor: 'card-forecast', text: `What Warning Shots expects next on AI's dangers, graded in public. Next up: ${soon ? soon.question : ''}. Warning Shots:` });
}
let calOpen = false;
function drawCalendar() {
  const today = C.asOf, box = document.getElementById('cal');
  const all = D.catalysts.filter((r) => r.date >= today).sort((a, b) => a.date.localeCompare(b.date));
  const rows = calOpen ? all : all.slice(0, 8);
  box.replaceChildren(...rows.map((r) => { const row = el('div', 'cal-row'); row.tabIndex = 0; const right = el('div'); const why = el('div', 'cal-why'); why.append(txt(r.why + ' ')); if (r.source_url) { const a = el('a', null, 'source'); a.href = r.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); why.append(a); } right.append(el('div', 'cal-ev', r.event), why); row.append(el('div', 'cal-date', r.date_label), right); const t = () => row.classList.toggle('open'); row.addEventListener('click', t); row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); t(); } }); return row; }));
  const more = document.getElementById('cal-more'); more.replaceChildren();
  if (all.length > 8) { const b = el('button', 'more-btn', calOpen ? 'Show fewer' : 'Show all ' + all.length + ' dated tests'); b.type = 'button'; b.style.marginTop = '12px'; b.addEventListener('click', () => { calOpen = !calOpen; drawCalendar(); }); more.append(b); }
}

/* ---------- deep dives */
const dd = { id: null, vfilter: 'all', vAll: false, tlAll: false };
const VSTAT = { confirmed: 'var(--alarm)', reported: 'color-mix(in oklab, var(--alarm) 50%, var(--paper))', attacked: 'var(--amber)', disrupted: 'var(--steel)', other: 'var(--line-2)', unnamed: 'var(--line-2)' };
function drawDeepDive() {
  const dds = D.deepdives.slice().sort((a, b) => +a.order - +b.order);
  if (!dd.id || !dds.find((d) => d.incident_id === dd.id)) dd.id = dds[0].incident_id;
  document.getElementById('dd-tabs').replaceChildren(...dds.map((d) => { const b = el('button', d.incident_id === dd.id ? 'on' : ''); b.id = 'dd-' + d.incident_id; b.setAttribute('role', 'tab'); b.setAttribute('aria-selected', String(d.incident_id === dd.id)); if (d.status === 'active') b.append(el('i')); b.append(txt(d.tab_label)); b.addEventListener('click', () => { dd.id = d.incident_id; dd.vfilter = 'all'; dd.vAll = false; dd.tlAll = false; document.querySelectorAll('#seg-vstatus button').forEach((x) => x.classList.toggle('on', x.dataset.v === 'all')); history.replaceState(null, '', '#d=' + d.incident_id); drawDeepDive(); }); return b; }));
  const d = dds.find((x) => x.incident_id === dd.id);
  const h = el('h3'); h.append(txt(d.name), el('span', 'status' + (d.status === 'active' ? ' active' : ''), d.status_label));
  const rel = el('div', 'dd-rel');
  const relRows = String(d.related_ids || '').split(',').map((s) => s.trim()).map((id) => C.scored.find((r) => r.id === id)).filter(Boolean);
  if (relRows.length) { rel.append(el('span', 'lbl', relRows.length > 1 ? 'Scored on the index:' : 'Score on the index:')); relRows.forEach((r) => { const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r.severity)); sc.style.color = tierText(r.tier); b.append(sc, el('span', null, r.title)); b.addEventListener('click', () => openIncident(r.id)); rel.append(b); }); }
  const dq = (D.quotes || []).filter((q) => q.incident_id === d.incident_id && q.quote && q.verified !== false).sort((a, b) => (b.weight || 0) - (a.weight || 0)).slice(0, 2).map((q) => { const w = el('div', 'dd-quote'); const who = el('div', 'who'); who.append(el('b', null, q.speaker), txt(q.title ? ', ' + q.title : ''), txt(', ' + fmtDate(new Date(q.date)) + ' ')); const a = el('a', null, 'source'); a.href = q.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; who.append(a); w.append(el('blockquote', null, q.quote), who); return w; });
  const fx = fixRows().find((f) => f.incident_id === d.incident_id); const chainRow = el('div', 'dd-chain');
  if (fx) { const cur = fixCur(fx); chainRow.append(el('span', 'lbl', 'Did they fix it?'), chainNode(fx), el('span', 'stt ' + cur.status, FIXST[cur.status] || cur.status), el('span', null, fx.one_liner || '')); const a = el('a', null, 'Details'); a.href = '#fixes'; a.addEventListener('click', (e) => { e.preventDefault(); fixOpen.id = fx.incident_id; drawFixes(); document.getElementById('fix-' + fx.incident_id)?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); }); chainRow.append(a); }
  document.getElementById('dd-head').replaceChildren(h, el('p', 'dd-meta', d.dates_label), el('p', 'dd-one', d.one_liner), ...dq, rel, ...(fx ? [chainRow] : []));
  const r0 = C.scored.find((r) => r.id === d.incident_id);
  shareRow(document.getElementById('dd-share'), { anchor: 'd=' + d.incident_id, text: d.name + '. ' + d.one_liner.split('. ')[0] + '. Warning Shots:', card: r0 ? { ...cardForIncident(r0), headline: d.name, finding: d.one_liner } : null });
  const vc = C.victimCounts[d.incident_id] || {};
  const stat = (v, l) => { const c = el('div', 'dd-stat'); c.append(el('div', 'v', String(v)), el('div', 'l', l)); return c; };
  const stats = [stat(vc.confirmed ?? 0, 'organizations confirmed compromised')];
  if (vc.reported) stats.push(stat(vc.reported, 'reported compromised by researchers or press, not confirmed by the victim'));
  stats.push(stat(vc.attacked ?? 0, 'attacked or abused: blocked, failed or unclear'));
  if (vc.disrupted) stats.push(stat(vc.disrupted, 'organizations that took services offline'));
  if (d.scale_value) stats.push(stat(d.scale_value, d.scale_label));
  document.getElementById('dd-stats').replaceChildren(...stats);
  const blk = (lbl, field) => { const c = el('div', 'dd-block'); c.append(el('span', 'lbl', lbl), el('div', null, d[field])); return c; };
  document.getElementById('dd-how').replaceChildren(blk('How it happened', 'how'), blk("The AI's role", 'ai_role'), blk('Damage so far', 'damage'), blk('Why it matters', 'why'));
  drawMap(d);
  drawVictims();
  const tl = D.timeline.filter((t) => t.incident_id === d.incident_id).sort((a, b) => a.date.localeCompare(b.date));
  drawTrack(d, tl);
  const tlBox = document.getElementById('dd-timeline'); const tlShow = dd.tlAll ? tl : tl.slice(Math.max(0, tl.length - 8));
  tlBox.replaceChildren(...tlShow.map((t) => { const it = el('div', 'tl-item'); const sp = el('span', null, t.event); if (t.source_url) { const a = el('a', null, 'source'); a.href = t.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; sp.append(a); } it.append(el('b', null, t.date_label || fmtDate(new Date(t.date))), sp); return it; }));
  let tm = document.getElementById('tl-more'); if (!tm) { tm = el('div'); tm.id = 'tl-more'; tlBox.after(tm); }
  tm.replaceChildren();
  if (tl.length > 8) { const b = el('button', 'more-btn', dd.tlAll ? 'Show fewer' : 'Show all ' + tl.length + ' events'); b.type = 'button'; b.addEventListener('click', () => { dd.tlAll = !dd.tlAll; drawDeepDive(); }); tm.append(b); }
  const sigs = D.signals.filter((x) => x.related_incident === d.signal_tag).sort((a, b) => b.date.localeCompare(a.date)).slice(0, 6);
  document.getElementById('dd-signals').replaceChildren(...(sigs.length ? sigs.map((x) => sigRow(x, true)) : [el('p', 'count', 'No official statements tracked yet.')]));
  document.getElementById('dd-impl').replaceChildren(...D.implications.filter((x) => x.incident_id === d.incident_id).map((x) => { const it = el('div', 'impl-item'); it.append(el('div', null, x.text)); if (x.source_url) { const s = el('div', 'src'); const a = el('a', null, x.source_label || 'source'); a.href = x.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; s.append(a); it.append(s); } return it; }));
}
function drawTrack(d, tl) {
  const box = document.getElementById('dd-track'); if (!box || !box.clientWidth) return;
  let rows = tl.map((t) => ({ ...t, _d: new Date(t.date) })).filter((t) => !isNaN(t._d));
  if (!rows.length) { box.replaceChildren(); return; }
  const W = box.clientWidth, H = 124, m = { l: 10, r: 14 };
  const today = new Date(D.meta.as_of);
  const hiD = d.status === 'active' ? d3.utcDay.offset(today, 1) : d3.max(rows, (t) => t._d);
  // focus on the main cluster: drop a long sparse prelude, say how many events it held
  const sortedD = rows.map((t) => +t._d).sort((a, b) => a - b);
  const q20 = sortedD[Math.floor(sortedD.length * 0.2)];
  let earlier = 0;
  if ((hiD - sortedD[0]) > 3 * (hiD - q20)) { earlier = rows.filter((t) => +t._d < q20).length; rows = rows.filter((t) => +t._d >= q20); }
  const lo = d3.min(rows, (t) => t._d);
  const span = Math.max(1, hiD - lo);
  const x = d3.scaleUtc([d3.utcDay.offset(lo, -Math.max(1, span / 864e5 * 0.03)), d3.utcDay.offset(hiD, Math.max(1, span / 864e5 * 0.03))], [m.l, W - m.r]);
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Events on a dated line');
  const yl = 76;
  svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', yl).attr('y2', yl).attr('stroke', 'var(--line-2)').attr('stroke-width', 1.5);
  const ticks = span > 400 * 864e5 ? d3.utcYear.every(1) : span > 40 * 864e5 ? d3.utcMonth.every(1) : d3.utcDay.every(1);
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${yl + 26})`).call(d3.axisBottom(x).ticks(ticks).tickFormat(span > 400 * 864e5 ? d3.utcFormat('%Y') : span > 40 * 864e5 ? d3.utcFormat('%b') : d3.utcFormat('%b %-d')).tickSize(4).tickSizeOuter(0)).call(axisClean).call((g) => g.select('.domain').remove());
  if (d.status === 'active') { svg.append('line').attr('x1', x(today)).attr('x2', x(today)).attr('y1', yl - 30).attr('y2', yl + 18).attr('stroke', 'var(--alarm)').attr('stroke-dasharray', '3 3'); svg.append('text').attr('x', x(today) - 5).attr('y', yl - 32).attr('text-anchor', 'end').attr('font-size', 10.5).attr('fill', 'var(--alarm)').text('now'); }
  // beeswarm-lite: each event takes the first lane where it doesn't touch the previous dot in that lane
  const laneX = [], OFF = [0, -12, 12, -24, 24, -36, 36];
  const pts = rows.map((t) => { const px = x(t._d); let lane = 0; while (lane < OFF.length - 1 && laneX[lane] != null && px - laneX[lane] < 11) lane++; laneX[lane] = px; return { t, px, py: yl + OFF[lane] }; });
  const tip = makeTip(box);
  const dots = svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', (p) => p.px).attr('cy', (p) => p.py).attr('r', 5)
    .attr('fill', (p) => isNew(p.t.date.slice(0, 10)) ? 'var(--alarm)' : 'var(--steel)').attr('stroke', 'var(--panel)').attr('stroke-width', 1.5).style('cursor', 'default')
    .on('pointermove', (ev, p) => { tip.show([el('div', 't-sec', p.t.date_label || fmtDate(p.t._d)), el('div', null, p.t.event)], p.px * box.clientWidth / W, p.py * box.clientWidth / W); })
    .on('pointerleave', () => tip.hide());
  const veryNew = (t) => (Date.parse(D.meta.as_of) - Date.parse(t.date)) < 24 * 3.6e6;
  pts.filter((p) => veryNew(p.t)).slice(-3).forEach((p) => svg.append('circle').attr('class', 'halo').attr('cx', p.px).attr('cy', p.py).attr('r', 6).attr('fill', 'none').attr('stroke', 'var(--alarm)').attr('stroke-width', 1.5).attr('pointer-events', 'none'));
  const first = pts[0], last = pts[pts.length - 1];
  const cap = (p, max) => (p.t.date_label || fmtDate(p.t._d)) + ': ' + (p.t.event.length > max ? p.t.event.slice(0, max - 2).trimEnd() + '…' : p.t.event);
  svg.append('text').attr('x', m.l).attr('y', 12).attr('font-size', 11).attr('fill', 'var(--ink-3)').text(pts.length + ' events in view' + (earlier ? ', ' + earlier + ' earlier not shown' : '') + '. Hover a dot. First: ' + cap(first, W > 700 ? 56 : 30));
  svg.append('text').attr('x', m.l).attr('y', 27).attr('font-size', 11).attr('fill', 'var(--ink-2)').text('Latest: ' + cap(last, W > 700 ? 84 : 40));
  keepTip(box, svg.node());
  onVisible(box, 'track:' + d.incident_id, (instant) => { if (instant) return; dots.attr('r', 0).transition().delay((p, i) => i * 35).duration(350).ease(d3.easeBackOut).attr('r', 5); });
}
function drawVictims() {
  const box = document.getElementById('v-list'), cnt = document.getElementById('v-count');
  const all = D.victims.filter((v) => v.incident_id === dd.id);
  const order = { confirmed: 0, reported: 1, attacked: 2, disrupted: 3, other: 4, unnamed: 5 };
  const rows = all.filter((v) => dd.vfilter === 'all' || v.status_group === dd.vfilter || (dd.vfilter === 'other' && v.status_group === 'unnamed') || (dd.vfilter === 'confirmed' && v.status_group === 'reported')).sort((a, b) => order[a.status_group] - order[b.status_group] || (b.date || '').localeCompare(a.date || ''));
  const limit = dd.vAll ? rows.length : 8;
  cnt.textContent = all.length ? (rows.length > limit ? `The first ${limit} of ${rows.length} entries, compromised first` : `Showing ${rows.length} of ${all.length} entries`) : '';
  let vm = document.getElementById('v-more'); if (!vm) { vm = el('div'); vm.id = 'v-more'; box.after(vm); }
  vm.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', 'Show all ' + rows.length + ' organizations'); b.type = 'button'; b.addEventListener('click', () => { dd.vAll = true; drawVictims(); }); vm.append(b); }
  else if (dd.vAll && rows.length > 8) { const b = el('button', 'more-btn', 'Show fewer'); b.type = 'button'; b.addEventListener('click', () => { dd.vAll = false; drawVictims(); }); vm.append(b); }
  box.replaceChildren(...rows.slice(0, limit).map((v) => {
    const r = el('div', 'vrow'); const a = el('div'); a.append(el('div', 'org', v.organization), el('div', 'sub', [v.sector, v.country].filter(Boolean).join(', ')));
    const b = el('div', 'ext'); b.append(el('span', null, v.extent)); if (v.how) b.append(el('span', 'how', v.how));
    if (v.source_url) { const sp = el('span', 'how'); const lk = el('a', null, (v.date_label || v.date || '') + (v.date_label || v.date ? ', ' : '') + (v.source_label || 'source')); lk.href = v.source_url; lk.target = '_blank'; lk.rel = 'noopener noreferrer'; sp.append(lk); b.append(sp); }
    const p = el('span', 'vpill'); const dot = el('i'); dot.style.background = VSTAT[v.status_group] || VSTAT.other; p.append(dot, el('span', null, v.status));
    r.append(a, b, p); return r;
  }));
}
document.getElementById('seg-vstatus').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; dd.vfilter = b.dataset.v; document.querySelectorAll('#seg-vstatus button').forEach((x) => x.classList.toggle('on', x === b)); drawVictims(); });

/* ---------- signals */
const SIG_GROUP = (t) => t === 'security agency' ? 'agency' : (t === 'government' || t === 'legislature' || t === 'regulator/AG') ? 'gov' : 'company';
const sigColor = (g) => g === 'agency' ? 'var(--av-agency)' : g === 'gov' ? 'var(--av-gov)' : 'var(--av-lab)';
const initials = (org) => { const o = org.replace(/\(.*?\)/g, '').trim(); if (o.length <= 4) return o.toUpperCase(); const ws = o.split(/[\s/–-]+/).filter((x) => /^[A-Za-z]/.test(x)); return (ws.length > 1 ? ws.slice(0, 3).map((x) => x[0]).join('') : o.slice(0, 2)).toUpperCase(); };
function sigRow(x, compact) {
  const g = SIG_GROUP(x.org_type), r = el('div', 'sig');
  const av = el('div', 'av', initials(x.org)); av.style.background = sigColor(g);
  const body = el('div'), who = el('div', 'who'); who.append(el('strong', null, x.org)); if (x.speaker) who.append(txt(' '), el('span', null, x.speaker));
  body.append(who, el('div', 'gist', x.gist));
  if (x.quote && !compact) body.append(el('div', 'q', '“' + x.quote + '”'));
  const meta = el('div', 'meta'); meta.append(el('span', null, fmtDate(new Date(x.date))), el('span', 'chip' + (x.channel === 'X post' ? ' x' : ''), x.channel));
  if (x.related_incident && !compact) meta.append(el('span', 'chip', x.related_incident));
  if (x.url) { const a = el('a', null, x.channel === 'X post' ? 'View post' : 'Source'); a.href = x.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; meta.append(a); }
  body.append(meta); r.append(av, body); return r;
}
const sig = { group: 'all', inc: '', open: false };
function drawSignals() {
  const box = document.getElementById('sig-list'), cnt = document.getElementById('sig-count'), all = D.signals, more = document.getElementById('sig-more');
  const sel = document.getElementById('sel-sig-inc');
  if (sel.options.length === 0) { const incs = [...new Set(all.map((x) => x.related_incident).filter(Boolean))].sort(); sel.replaceChildren(new Option('All topics', ''), ...incs.map((i) => new Option(i, i))); }
  const rows = all.filter((x) => (sig.group === 'all' || SIG_GROUP(x.org_type) === sig.group) && (!sig.inc || x.related_incident === sig.inc)).sort((a, b) => b.date.localeCompare(a.date) || (a.significance === 'high' ? -1 : 1));
  cnt.textContent = rows.length === all.length ? `${all.length} statements, newest first` : `Showing ${rows.length} of ${all.length} statements`;
  const limit = sig.open ? rows.length : 6;
  box.replaceChildren(...rows.slice(0, limit).map((x) => sigRow(x, false)));
  more.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', 'Show all ' + rows.length + ' statements'); b.type = 'button'; b.addEventListener('click', () => { sig.open = true; drawSignals(); }); more.append(b); }
  else if (sig.open && rows.length > 6) { const b = el('button', 'more-btn', 'Show fewer'); b.type = 'button'; b.addEventListener('click', () => { sig.open = false; drawSignals(); document.getElementById('signals').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); }); more.append(b); }
}
document.getElementById('seg-sig').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; sig.group = b.dataset.v; document.querySelectorAll('#seg-sig button').forEach((x) => x.classList.toggle('on', x === b)); drawSignals(); });
document.getElementById('sel-sig-inc').addEventListener('change', (e) => { sig.inc = e.target.value; drawSignals(); });

/* ---------- list + drawer */
const ls = { q: '', setting: 'all', cat: '', year: '', sort: 'sev', open: null, all: false };
const FACT = [['H', 'Harm', 5], ['R', 'Reach', 5], ['A', 'Autonomy', 4], ['N', 'Novelty', 5], ['I', 'Permanence', 5]];
function detailNodes(r, inDrawer) {
  const out = [];
  const p1 = el('p', null, r.summary); out.push(p1);
  const p2 = el('p'); p2.append(el('span', 'lbl', 'Damage: '), txt(r.harm)); out.push(p2);
  const fac = el('div', 'factors'); FACT.forEach(([k, label, max]) => { const f = el('div', 'factor'); f.append(txt(label + ' '), el('span', 'fv', String(r[k])), txt('/' + max)); const tr = el('div', 'ft'); const ti = el('i'); ti.style.width = (+r[k] / max * 100) + '%'; tr.append(ti); f.append(tr); fac.append(f); }); out.push(fac);
  const p3 = el('p'); p3.append(el('span', 'lbl', 'Harm score '), el('b', null, String(r.harm_score)), el('span', 'lbl', ', signal score '), el('b', null, String(r.signal_score)), el('span', 'lbl', ', autonomy: ' + AUTONOMY[+r.A].name.toLowerCase() + ' (' + AUTONOMY[+r.A].desc + ')')); out.push(p3);
  const p4 = el('p'); p4.append(el('span', 'lbl', 'Sources: '));
  [[r.source_url, r.source_label || 'primary source'], [r.source2_url, 'second source'], [r.source3_url, 'third source']].forEach(([u, t], i) => { if (!u) return; if (i) p4.append(txt(', ')); const a = el('a', null, t); a.href = u; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); p4.append(a); });
  if (r.confidence && r.confidence !== 'high') p4.append(el('span', 'lbl', '. Confidence: ' + r.confidence));
  if (r.notes) p4.append(el('span', 'lbl', '. ' + r.notes));
  out.push(p4);
  return out;
}
function openIncident(id) {
  const r = C.scored.find((x) => x.id === id); if (!r) return;
  const body = document.getElementById('drawer-body');
  const big = el('div', 'big'); big.append(txt(String(r.severity)), el('small', null, '/100'));
  const pill = el('span', 'pill'); const pd = el('i'); pd.style.background = tierColor(r.tier); pill.append(pd, txt(r.level + ' ' + r.tier)); big.append(pill);
  const h = el('h3', null, r.title);
  const meta = el('div', 'dmeta', [r.ws, showDate(r), r.actors, r.category_label, r.setting === 'wild' ? 'in the wild' : 'in the lab'].filter(Boolean).join(', '));
  const share = el('div', 'share');
  body.replaceChildren(big, h, meta, ...detailNodes(r, true), share);
  shareRow(share, { anchor: 'i=' + r.id, text: `${r.title} (${r.severity}/100, ${r.tier.toLowerCase()}). ${r.summary.split('. ')[0]}. Warning Shots:`, card: cardForIncident(r) });
  document.getElementById('drawer').classList.add('on'); document.getElementById('drawer').setAttribute('aria-hidden', 'false'); document.getElementById('drawer').inert = false; document.getElementById('drawer-bg').classList.add('on');
  history.replaceState(null, '', '#i=' + r.id);
  document.getElementById('drawer-close').focus();
}
function closeDrawer() { document.getElementById('drawer').classList.remove('on'); document.getElementById('drawer').setAttribute('aria-hidden', 'true'); document.getElementById('drawer').inert = true; document.getElementById('drawer-bg').classList.remove('on'); if (location.hash.startsWith('#i=')) history.replaceState(null, '', location.pathname + location.search); }
document.getElementById('drawer-close').addEventListener('click', closeDrawer);
document.getElementById('drawer-bg').addEventListener('click', closeDrawer);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });
function drawList() {
  const box = document.getElementById('list'), count = document.getElementById('list-count'), all = C.scored;
  const selCat = document.getElementById('sel-cat'), selYear = document.getElementById('sel-year');
  if (selCat.options.length === 0) { const cats = [...new Set(all.map((r) => r.category_label))].sort(); selCat.replaceChildren(new Option('All categories', ''), ...cats.map((c) => new Option(c, c))); const years = [...new Set(all.map((r) => r.date.slice(0, 4)))].sort().reverse(); selYear.replaceChildren(new Option('All years', ''), ...years.map((y) => new Option(y, y))); }
  const q = ls.q.trim().toLowerCase();
  const rows = all.filter((r) => (ls.setting === 'all' || r.setting === ls.setting) && (!ls.cat || r.category_label === ls.cat) && (!ls.year || r.date.startsWith(ls.year)) && (!q || [r.title, r.actors, r.summary, r.category_label].join(' ').toLowerCase().includes(q)));
  const by = { sev: (a, b) => b.severity - a.severity || b.date.localeCompare(a.date), new: (a, b) => b.date.localeCompare(a.date), old: (a, b) => a.date.localeCompare(b.date), auto: (a, b) => +b.A - +a.A || b.severity - a.severity };
  rows.sort(by[ls.sort]);
  const rank = new Map(all.slice().sort(by.sev).map((r, i) => [r.id, i + 1]));
  const filtered = rows.length !== all.length;
  const limit = (ls.all || filtered) ? rows.length : 12;
  count.textContent = !filtered ? (limit < rows.length ? `The ${limit} highest-scoring of ${all.length} incidents` : `All ${rows.length} incidents`) : `Showing ${rows.length} of ${all.length} incidents`;
  const more = document.getElementById('list-more'); more.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', 'Show all ' + rows.length + ' incidents'); b.type = 'button'; b.addEventListener('click', () => { ls.all = true; drawList(); }); more.append(b); }
  else if (ls.all && !filtered) { const b = el('button', 'more-btn', 'Show fewer'); b.type = 'button'; b.addEventListener('click', () => { ls.all = false; drawList(); document.getElementById('all').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); }); more.append(b); }
  box.replaceChildren(...rows.slice(0, limit).map((r) => {
    const row = el('div', 'row' + (ls.open === r.id ? ' open' : '')); row.id = 'row-' + r.id; row.tabIndex = 0;
    const sw = el('div'); const sb = el('div', 'sevbar'); const si = el('i'); si.style.width = r.severity + '%'; si.style.background = tierColor(r.tier); sb.append(si); sw.append(el('div', 'sev', String(r.severity)), sb);
    const mid = el('div'); const rt_ = el('div', 'rtitle', r.title); if (isNew(r.disclosed || r.date)) rt_.append(el('span', 'new-tag', 'new')); mid.append(rt_, el('div', 'rmeta', [r.ws, showDate(r), r.actors, r.category_label, r.setting === 'wild' ? 'in the wild' : 'in the lab', 'ranked #' + rank.get(r.id)].filter(Boolean).join(', ')));
    const pill = el('span', 'pill'); const pd = el('i'); pd.style.background = tierColor(r.tier); pill.append(pd, txt(r.level + ' ' + r.tier));
    const det = el('div', 'rdetail'); det.append(...detailNodes(r, false)); const sh = el('div', 'share'); shareRow(sh, { anchor: 'i=' + r.id, text: `${r.title} (${r.severity}/100, ${r.tier.toLowerCase()}). Warning Shots:`, card: cardForIncident(r) }); det.append(sh);
    row.append(sw, mid, pill, det);
    const toggle = () => { ls.open = ls.open === r.id ? null : r.id; row.classList.toggle('open'); };
    row.addEventListener('click', (e) => { if (e.target.closest('a, button')) return; toggle(); }); row.addEventListener('keydown', (e) => { if (e.key === 'Enter') toggle(); });
    return row;
  }));
  shareRow(document.getElementById('share-list'), { anchor: 'all', text: `${all.length} AI incidents since 2023, each scored 0–100 and linked to its source. Warning Shots:` });
}
document.getElementById('q').addEventListener('input', (e) => { ls.q = e.target.value; drawList(); });
document.getElementById('seg-setting').addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; ls.setting = b.dataset.v; document.querySelectorAll('#seg-setting button').forEach((x) => x.classList.toggle('on', x === b)); drawList(); });
document.getElementById('sel-cat').addEventListener('change', (e) => { ls.cat = e.target.value; drawList(); });
document.getElementById('sel-year').addEventListener('change', (e) => { ls.year = e.target.value; drawList(); });
document.getElementById('sel-sort').addEventListener('change', (e) => { ls.sort = e.target.value; drawList(); });
document.getElementById('dl-csv').addEventListener('click', (e) => {
  e.preventDefault();
  const cols = ['id', 'date', 'date_precision', 'disclosed', 'title', 'actors', 'category_label', 'setting', 'summary', 'harm', 'H', 'R', 'A', 'N', 'I', 'harm_score', 'signal_score', 'severity', 'tier', 'source_url', 'source2_url', 'source3_url', 'confidence'];
  const esc = (v) => { const s = v == null ? '' : String(v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  const csv = [cols.join(',')].concat(C.scored.map((r) => cols.map((c) => esc(r[c])).join(','))).join('\n');
  const a = el('a'); a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' })); a.download = 'warning-shots-incidents.csv'; a.click();
});

/* ---------- context + changelog */
function drawContext() {
  document.getElementById('ctx').replaceChildren(...D.context.map((r) => { const c = el('div', 'ctx-item'); c.append(el('div', 'ctx-val', r.value), el('div', 'ctx-lbl', r.metric)); const s = el('div', 'ctx-src'); if (r.source_url) { const a = el('a', null, r.source_label); a.href = r.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; s.append(a); } else s.textContent = r.source_label; c.append(s); return c; }));
  document.getElementById('changelog').replaceChildren(...(D.meta.changelog || []).map((c) => { const d = el('div'); d.append(el('b', null, fmtDay(new Date(c.date)) + ', ' + c.date.slice(0, 4)), el('span', null, c.text)); return d; }));
}

/* ---------- brief + quotes */
function drawBrief() {
  const sec = document.getElementById('brief'), b = D.brief;
  if (!b || !b.items || !b.items.length) { sec.style.display = 'none'; return; }
  sec.style.display = '';
  document.getElementById('brief-stamp').textContent = fmtET(D.meta.as_of);
  document.getElementById('brief-list').replaceChildren(...b.items.map((it) => { const li = el('li', null, it.text); if (it.url) { const a = el('a', null, it.source_label || 'source'); a.href = it.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; li.append(a); } return li; }));
  const cu = document.getElementById('brief-caught'); if (cu) cu.textContent = 'That is everything that changed in the index since the previous refresh. You’re caught up as of ' + fmtET(D.meta.as_of) + '.';
  shareRow(document.getElementById('brief-share'), { anchor: 'brief', text: b.items.map((it, i) => (i + 1) + '. ' + it.text).join('\n') + '\nWarning Shots:' });
}
let quotesOpen = false, leadIdx = 0, leadTimer = null;
function quoteCard(q, lead) {
  const c = el('div', 'qt' + (lead ? ' lead' : '') + (q.lang === 'ja' ? ' ja' : ''));
  const bq = el('blockquote', null, q.quote); c.append(bq);
  if (isNew(q.date)) bq.append(el('span', 'new-tag', 'new'));
  if (q.original) c.append(el('div', 'orig', q.original));
  const who = el('div', 'who'); who.append(el('b', null, q.speaker)); if (q.title) who.append(txt(', '), el('span', null, q.title.split(';')[0])); c.append(who);
  const via = q.via ? q.via.split(' (')[0].replace(/ transcribing.*$/, '') : '';
  const meta = el('div', 'meta'); meta.append(el('span', null, fmtDate(new Date(q.date))), el('span', 'chip' + (q.channel === 'X post' ? ' x' : ''), q.channel + (via ? ', via ' + via : '')));
  const dive = D.deepdives.find((d) => d.incident_id === q.incident_id); if (dive) { const a = el('a', null, dive.tab_label.replace(' (live)', '')); a.href = '#d=' + dive.incident_id; a.addEventListener('click', (e) => { e.preventDefault(); go('#d=' + dive.incident_id); }); meta.append(a); }
  if (q.url) { const a = el('a', null, q.channel === 'X post' ? 'View post' : 'Source'); a.href = q.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; meta.append(a); }
  const sh = el('div', 'share'); shareRow(sh, { anchor: 'q=' + q.id, text: `“${q.quote}” — ${q.speaker}${q.title ? ', ' + q.title : ''} (${fmtDate(new Date(q.date))}). Warning Shots:` });
  c.append(meta, sh); c.id = 'q-' + q.id; return c;
}
function drawQuotes() {
  const sec = document.getElementById('words'), box = document.getElementById('quotes');
  const qs = (D.quotes || []).filter((q) => q.quote && q.verified !== false).slice().sort((a, b) => (b.weight || 0) - (a.weight || 0) || b.date.localeCompare(a.date));
  if (!qs.length) { sec.style.display = 'none'; return; }
  sec.style.display = '';
  const n = quotesOpen ? qs.length : Math.min(4, qs.length);
  const leads = qs.slice(0, 8);
  leadIdx = leadIdx % leads.length;
  const leadCard = quoteCard(leads[leadIdx], true);
  const dotsRow = el('div', 'qt-dots'); leads.forEach((q, i) => { const b = el('button'); b.type = 'button'; b.setAttribute('aria-label', 'Quote ' + (i + 1)); if (i === leadIdx) b.classList.add('on'); b.addEventListener('click', () => { leadIdx = i; drawQuotes(); }); dotsRow.append(b); }); leadCard.append(dotsRow);
  const rest = qs.filter((q) => q !== leads[leadIdx]).slice(0, n - 1);
  box.replaceChildren(leadCard, ...rest.map((q) => quoteCard(q, false)));
  clearInterval(leadTimer);
  if (!reduced && leads.length > 1) { let hover = false; leadCard.addEventListener('pointerenter', () => { hover = true; }); leadCard.addEventListener('pointerleave', () => { hover = false; }); leadTimer = setInterval(() => { if (hover || document.hidden) return; const r = leadCard.getBoundingClientRect(); if (r.bottom < 0 || r.top > window.innerHeight) return; leadCard.classList.add('fading'); setTimeout(() => { leadIdx = (leadIdx + 1) % leads.length; drawQuotes(); }, 460); }, 9000); }
  let more = document.getElementById('quotes-more'); if (!more) { more = el('div'); more.id = 'quotes-more'; box.after(more); }
  more.replaceChildren();
  if (qs.length > 4) { const b = el('button', 'more-btn', quotesOpen ? 'Show fewer' : 'Show all ' + qs.length + ' quotes'); b.type = 'button'; b.addEventListener('click', () => { quotesOpen = !quotesOpen; drawQuotes(); if (!quotesOpen) document.getElementById('words').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); }); more.append(b); }
  shareRow(document.getElementById('words-share'), { anchor: 'words', text: 'What the people in charge actually said about this year\'s AI incidents, verbatim and sourced. Warning Shots:' });
}
function embedMode() {
  if (!EMBED) return;
  document.body.classList.add('embed');
  const targets = { timeline: ['ch-timeline', 'lg-autonomy', 'hero-share'], now: ['now'], wire: ['siren', 'wire-board'], calls: ['calls'], edges: ['card-edges'], capabilities: ['card-capgrid'], tns: ['card-tns'], fixes: ['card-fixes'], why: ['why'], quarters: ['card-quarters'], disclosure: ['card-disclosure'], scatter: ['card-scatter'], horizon: ['card-horizon'], pipeline: ['card-pipeline'], words: ['quotes'], brief: ['brief'] };
  const ids = targets[EMBED] || targets.timeline;
  const host = el('div', 'embed-host wrap');
  if (EMBED === 'timeline') { const p = el('div', 'panel'); const t = el('div', 'panel-title'); t.append(txt('AI has started breaking in on its own: severe incidents went from '), el('b', null, String(C.headline.severe_prior12)), txt(' to '), el('b', null, String(C.headline.severe_last12)), txt(' in a year')); p.append(t, el('div', 'panel-note', 'Every major AI incident since 2023, scored 0–100. The stronger a dot’s color, the more the AI did on its own.')); ids.forEach((id) => { const n = document.getElementById(id); if (n) p.append(n); }); host.append(p); }
  else ids.forEach((id) => { const n = document.getElementById(id); if (n) { n.hidden = false; host.append(n); } });
  const f = el('div', 'embed-foot'); const a = el('a', null, 'Warning Shots, the AI Incident Index'); a.href = SITE; a.target = '_blank'; a.rel = 'noopener'; f.append(a, el('span', null, 'Updated ' + fmtET(D.meta.as_of))); host.append(f);
  document.querySelector('main').append(host);
  setTimeout(() => drawAll(false), 50);
}


/* ---------- what AI can now do: both edges + maturity grid */
const STAGES = [['demonstrated', 'Demonstrated'], ['reproduced', 'Reproduced'], ['accessible', 'Accessible'], ['reliable', 'Reliable'], ['consequences', 'Real consequences']];
const DOMAIN = { agents: 'Agents', software: 'Software', cyber: 'Cyber', science: 'Science', medicine: 'Medicine', math: 'Math', reasoning: 'Reasoning', robotics: 'Robotics', media: 'Media', everyday: 'Everyday' };
const cap = { domain: 'all', open: false, openId: null };
const capRows = () => (D.capabilities || []).filter((c) => c && c.title && c.date).slice().sort((a, b) => b.date.localeCompare(a.date));
const stStatus = (c, k) => ((c.stages || {})[k] || {}).status || 'unknown';
function drawEdges() {
  const box = document.getElementById('ch-edges'), call = document.getElementById('edges-callout'); if (!box) return;
  const caps = capRows(); const sec = document.getElementById('capabilities');
  if (!caps.length) { sec.style.display = 'none'; return; } sec.style.display = '';
  if (!box.clientWidth) return;
  const W = box.clientWidth, narrow = W < 600, H = narrow ? 310 : 330, m = { l: 12, r: 12, t: narrow ? 78 : 64, b: 26 };
  const today = new Date(C.asOf);
  const x = d3.scaleUtc([new Date('2023-01-01'), d3.utcMonth.offset(today, 2)], [m.l, W - m.r]);
  const yT = m.t + 34, yB = H - m.b - 44;
  const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Capability milestones above, incidents below');
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(d3.utcYear.every(1)).tickFormat(d3.utcFormat('%Y')).tickSizeOuter(0)).call(axisClean);
  svg.append('line').attr('x1', x(today)).attr('x2', x(today)).attr('y1', m.t - 30).attr('y2', H - m.b).attr('stroke', 'var(--line-2)').attr('stroke-dasharray', '3 3');
  [[yT, 'What AI could do', 'var(--ink)'], [yB, 'What it did', 'var(--alarm)']].forEach(([yy, t, col]) => { svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', yy).attr('y2', yy).attr('stroke', 'var(--line-2)'); svg.append('text').attr('x', m.l).attr('y', yy === yT ? m.t - 16 : yy - 36).attr('font-size', 11.5).attr('font-weight', 600).attr('fill', col).text(t); });
  // capabilities: squares, beeswarm-lite upward
  const kind = (r) => r.setting !== 'wild' ? 'lab' : +r.A >= 3 ? 'auto' : 'wild';
  const inc = C.scored.map((r) => ({ r, px: x(new Date(r.date)) })).sort((a, b) => a.px - b.px);
  const laneI = [], OFFI = [0, 11, -11, 22, -22, 33];
  inc.forEach((p) => { let l = 0; while (l < OFFI.length - 1 && laneI[l] != null && p.px - laneI[l] < 9) l++; laneI[l] = p.px; p.py = yB + OFFI[l]; });
  const cps = caps.slice().sort((a, b) => a.date.localeCompare(b.date)).map((c) => ({ c, px: x(new Date(c.date)) }));
  const laneC = [], OFFC = [0, -13, 13, -26, 26];
  cps.forEach((p) => { let l = 0; while (l < OFFC.length - 1 && laneC[l] != null && p.px - laneC[l] < 12) l++; laneC[l] = p.px; p.py = yT + OFFC[l]; });
  const byId = new Map(inc.map((p) => [p.r.id, p]));
  const threads = svg.append('g');
  cps.forEach((p) => { const qs = (p.c.related_incident_ids || []).map((id) => byId.get(id)).filter(Boolean).sort((a, b) => b.r.severity - a.r.severity); qs.forEach((q, i) => { const strong = i < 2 && q.r.severity >= 55; threads.append('path').attr('class', 'thread' + (strong ? ' strong' : ' weak')).attr('data-cap', p.c.id).attr('d', `M${p.px},${p.py + 5} C${p.px},${(p.py + q.py) / 2} ${q.px},${(p.py + q.py) / 2} ${q.px},${q.py - 4}`).attr('fill', 'none').attr('stroke', 'var(--steel)').attr('stroke-width', 1.2).attr('opacity', strong ? 0.4 : 0); }); });
  const resetThreads = () => { threads.selectAll('.thread.strong').attr('opacity', 0.4).attr('stroke-width', 1.2); threads.selectAll('.thread.weak').attr('opacity', 0); };
  const dots = svg.append('g').selectAll('circle').data(inc).join('circle').attr('cx', (p) => p.px).attr('cy', (p) => p.py).attr('r', 3.6)
    .attr('fill', (p) => kind(p.r) === 'auto' ? 'var(--alarm)' : kind(p.r) === 'wild' ? 'var(--steel)' : 'var(--paper)').attr('stroke', (p) => kind(p.r) === 'lab' ? 'var(--ink-3)' : 'var(--paper)').attr('stroke-width', 1.2).attr('opacity', (p) => kind(p.r) === 'auto' ? 1 : 0.8);
  const sq = svg.append('g').selectAll('rect').data(cps).join('rect').attr('x', (p) => p.px - 5.5).attr('y', (p) => p.py - 5.5).attr('width', 11).attr('height', 11).attr('rx', 2)
    .attr('fill', 'var(--ink)').attr('stroke', (p) => stStatus(p.c, 'consequences') === 'yes' ? 'var(--alarm)' : 'var(--paper)').attr('stroke-width', (p) => stStatus(p.c, 'consequences') === 'yes' ? 2 : 1.5);
  // labels: the newest milestone plus the most-linked ones, spaced out
  const byLinks = cps.slice().sort((a, b) => (b.c.related_incident_ids || []).length - (a.c.related_incident_ids || []).length);
  const picks = new Set([cps[cps.length - 1].c.id]); const minGap = narrow ? 90 : 70;
  byLinks.forEach((p) => { if (picks.size >= (narrow ? 3 : 7)) return; if ([...picks].some((id) => Math.abs(cps.find((q) => q.c.id === id).px - p.px) < minGap)) return; picks.add(p.c.id); });
  const lab = svg.append('g'); const placed = [];
  cps.filter((p) => picks.has(p.c.id)).forEach((p) => {
    const short = p.c.title.length > (narrow ? 26 : 40) ? p.c.title.slice(0, narrow ? 24 : 38).trimEnd() + '…' : p.c.title;
    const anchor = p.px > W * 0.62 ? 'end' : 'start'; const w = short.length * 5.9; const x0 = anchor === 'end' ? p.px - 9 - w : p.px + 9, x1 = x0 + w;
    let yy = yT - 36; for (let k = 0; k < 6; k++) { const hit = placed.find((b) => x0 < b.x1 + 6 && x1 > b.x0 - 6 && Math.abs(yy - b.y) < 13); if (!hit) break; yy = hit.y - 13; }
    if (yy < 12) return; placed.push({ x0, x1, y: yy });
    lab.append('line').attr('x1', p.px).attr('x2', p.px).attr('y1', yy + 3).attr('y2', p.py - 7).attr('stroke', 'var(--line-2)').attr('stroke-width', 1);
    lab.append('text').attr('x', p.px + (anchor === 'end' ? -9 : 9)).attr('y', yy).attr('text-anchor', anchor).attr('font-size', 11).attr('font-weight', 600).attr('fill', 'var(--ink-2)').text(short);
  });
  const tip = makeTip(box);
  const all = cps.map((p) => ({ ...p, t: 'cap' })).concat(inc.map((p) => ({ ...p, t: 'inc' })));
  const del = d3.Delaunay.from(all, (p) => p.px, (p) => p.py);
  const hi = svg.append('rect').attr('width', 16).attr('height', 16).attr('rx', 3).attr('fill', 'none').attr('stroke', 'var(--ink)').attr('stroke-width', 1.5).attr('opacity', 0);
  svg.append('rect').attr('x', 0).attr('y', 0).attr('width', W).attr('height', H - m.b).attr('fill', 'transparent').style('cursor', 'pointer')
    .on('pointermove', (ev) => { const [px, py] = d3.pointer(ev); const p = all[del.find(px, py)]; if (!p || Math.hypot(p.px - px, p.py - py) > 30) { tip.hide(); hi.attr('opacity', 0); resetThreads(); return; }
      hi.attr('x', p.px - 8).attr('y', p.py - 8).attr('opacity', 1);
      if (p.t === 'cap') { threads.selectAll('.thread').attr('opacity', 0.08); threads.selectAll(`.thread[data-cap="${p.c.id}"]`).attr('opacity', 1).attr('stroke-width', 2); const d1 = el('div'); d1.append(el('span', 't-val', p.c.metric_value || ''), el('span', 't-sec', p.c.metric_value ? ' ' + (p.c.metric_label || '') : (p.c.domain ? DOMAIN[p.c.domain] || p.c.domain : ''))); tip.show([el('div', 't-sec', fmtDate(new Date(p.c.date)) + (p.c.org ? ', ' + p.c.org : '')), el('div', 't-title', p.c.title), d1, el('div', 't-sec', p.c.what || ''), el('div', 't-cta', 'Click for the evidence')], p.px * box.clientWidth / W, p.py * box.clientWidth / W); }
      else { resetThreads(); tip.show(incidentTip(p.r), p.px * box.clientWidth / W, p.py * box.clientWidth / W); } })
    .on('pointerleave', () => { tip.hide(); hi.attr('opacity', 0); resetThreads(); })
    .on('click', (ev) => { const [px, py] = d3.pointer(ev); const p = all[del.find(px, py)]; if (!p || Math.hypot(p.px - px, p.py - py) > 30) return; if (p.t === 'cap') { cap.openId = p.c.id; cap.open = true; cap.domain = 'all'; drawCapGrid(); document.getElementById('cap-' + p.c.id)?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } else openIncident(p.r.id); });
  keepTip(box, svg.node());
  onVisible(box, 'edges', (instant) => { if (instant) return; sq.attr('opacity', 0).transition().delay((p, i) => i * 40).duration(300).attr('opacity', 1); threads.selectAll('.thread.strong').attr('opacity', 0).transition().delay(600).duration(600).attr('opacity', 0.4); });
  legend(document.getElementById('lg-edges'), [{ color: 'var(--ink)', label: 'capability milestone' }, { color: 'var(--alarm)', shape: 'ring', label: 'with documented real-world consequences' }, { color: 'var(--alarm)', label: 'incident where the AI acted on its own' }, { color: 'var(--steel)', label: 'other real-world incident' }, { color: 'var(--ink-3)', shape: 'ring', label: 'lab or test finding' }]);
  const nCons = caps.filter((c) => stStatus(c, 'consequences') === 'yes').length, nRel = caps.filter((c) => stStatus(c, 'reliable') === 'yes').length, nRelPart = caps.filter((c) => stStatus(c, 'reliable') === 'partial').length;
  const linked = new Set(caps.flatMap((c) => c.related_incident_ids || []).filter((id) => byId.has(id)));
  call.replaceChildren(el('b', null, String(caps.length)), txt(' capability milestones since 2023. Only '), el('b', null, String(nRel)), txt(' ' + (nRel === 1 ? 'has' : 'have') + ' published evidence of reliability for a defined task, '), el('b', null, String(nRelPart)), txt(' partial, yet '), el('b', null, String(nCons)), txt(' are already producing documented real-world consequences, and '), el('b', null, String(linked.size)), txt(' incidents on the bottom line trace to a capability on the top line. Capability is reaching real life faster than reliability. The threads show the strongest links; hover a milestone for all of its incidents.'));
  shareRow(document.getElementById('share-edges'), { anchor: 'card-edges', text: `What AI could do, and what it did: ${caps.length} capability milestones since 2023 on one line, every major incident on the other, with the threads between them. Warning Shots:`, svgBox: box, name: 'both-edges', title: 'Both edges: what AI could do, and what it did', embed: 'edges', embedH: 480 });
}
function cellNode(c, k, i) { const st = stStatus(c, k); const d = el('div', 'cell c' + (i + 1) + ' ' + st); d.title = STAGES[i][1] + ': ' + st; return d; }
function drawCapGrid() {
  const box = document.getElementById('capgrid'), chips = document.getElementById('cap-chips'), more = document.getElementById('cap-more'); if (!box) return;
  const all = capRows(); if (!all.length) return;
  document.getElementById('cap-k').textContent = all.length + ' milestones, dated and sourced';
  const doms = d3.rollups(all, (v) => v.length, (c) => c.domain || 'other').sort((a, b) => b[1] - a[1]);
  if (!doms.find((d) => d[0] === cap.domain)) cap.domain = 'all';
  const chip = (k, label, n) => { const b = el('button', k === cap.domain ? 'on' : ''); b.type = 'button'; b.append(txt(label), el('b', null, String(n))); b.addEventListener('click', () => { cap.domain = k; drawCapGrid(); }); return b; };
  chips.replaceChildren(chip('all', 'All', all.length), ...doms.map(([k, n]) => chip(k, DOMAIN[k] || k, n)));
  const rows = all.filter((c) => cap.domain === 'all' || (c.domain || 'other') === cap.domain);
  const limit = (cap.open || cap.domain !== 'all') ? rows.length : 10;
  const head = el('div', 'cap-head'); head.append(el('span', null, 'Milestone'), ...STAGES.map(([, l]) => el('span', null, l)));
  box.replaceChildren(head, ...rows.slice(0, limit).map((c) => {
    const row = el('div', 'cap' + (cap.openId === c.id ? ' open' : '')); row.id = 'cap-' + c.id; row.tabIndex = 0;
    const left = el('div'); left.append(el('div', 'cap-t', c.title)); const meta = el('div', 'cap-m'); meta.append(txt((c.date_precision === 'month' ? fmtMonth(new Date(c.date)) : fmtDate(new Date(c.date))) + (c.org ? ', ' + c.org : '') + (c.domain ? ', ' + (DOMAIN[c.domain] || c.domain).toLowerCase() : '') + ' ')); if (c.metric_value) meta.append(el('b', null, c.metric_value + (c.metric_label ? ' ' + c.metric_label : ''))); left.append(meta);
    const det = el('div', 'cap-detail'); const ev = el('div', 'ev'); ev.append(el('b', null, 'What happened: '), txt(c.what || '')); det.append(ev);
    STAGES.forEach(([k, l]) => { const st = (c.stages || {})[k] || {}; const r = el('div', 'st'); const b = el('b', null, l + ': ' + (st.status || 'unknown')); const sp = el('span', null, st.note || ''); if (st.source_url) { const a = el('a', null, 'source'); a.href = st.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); sp.append(a); } r.append(b, sp); det.append(r); });
    if (c.everyday) { const e2 = el('div', 'ev'); e2.append(el('b', null, 'For real lives, jobs and families: '), txt(c.everyday)); det.append(e2); }
    const relRows = (c.related_incident_ids || []).map((id) => C.scored.find((r) => r.id === id)).filter(Boolean);
    if (relRows.length) { const rel = el('div', 'rel'); rel.append(el('span', 'lbl', 'Incidents it made possible:')); relRows.forEach((r) => { const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r.severity)); sc.style.color = tierText(r.tier); b.append(sc, el('span', null, r.title)); b.addEventListener('click', (e) => { e.stopPropagation(); openIncident(r.id); }); rel.append(b); }); det.append(rel); }
    const shc = el('div', 'share'); shareRow(shc, { anchor: 'm=' + c.id, text: c.title + '. ' + (c.what || '') + ' Warning Shots:', card: cardForCap(c) }); det.append(shc);
    const src = el('div', 'ev'); src.append(el('b', null, 'Sources: ')); [[c.source_url, 'primary'], [c.source2_url, 'second']].forEach(([u, t], i) => { if (!u) return; if (i) src.append(txt(', ')); const a = el('a', null, t); a.href = u; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); src.append(a); }); if (c.confidence && c.confidence !== 'high') src.append(txt('. Confidence: ' + c.confidence)); det.append(src);
    row.append(left, ...STAGES.map(([k], i) => cellNode(c, k, i)), det);
    const toggle = () => { cap.openId = cap.openId === c.id ? null : c.id; row.classList.toggle('open'); };
    row.addEventListener('click', (e) => { if (e.target.closest('a, button')) return; toggle(); }); row.addEventListener('keydown', (e) => { if (e.key === 'Enter') toggle(); });
    return row;
  }));
  more.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', 'Show all ' + rows.length + ' milestones'); b.type = 'button'; b.addEventListener('click', () => { cap.open = true; drawCapGrid(); }); more.append(b); }
  else if (cap.open && cap.domain === 'all' && rows.length > 10) { const b = el('button', 'more-btn', 'Show fewer'); b.type = 'button'; b.addEventListener('click', () => { cap.open = false; drawCapGrid(); document.getElementById('card-capgrid').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); }); more.append(b); }
  const nCons = all.filter((c) => stStatus(c, 'consequences') === 'yes').length;
  shareRow(document.getElementById('share-capgrid'), { anchor: 'card-capgrid', text: `${all.length} AI capability milestones since 2023, each graded from demonstration to real life. Only ${nCons} have documented real-world consequences so far. Warning Shots:`, embed: 'capabilities', embedH: 760 });
}

/* ---------- did they fix it */
const FIXST = { ongoing: 'Still unfolding', reopened: 'Recurred after a fix', disputed: 'Disputed', unverified: 'Fix claimed, not verified', unresolved: 'No fix claimed', fixed: 'Fixed and verified' };
const FIXORD = { ongoing: 0, reopened: 1, disputed: 2, unverified: 3, unresolved: 4, fixed: 5 };
const fixRows = () => (D.fixes || []).filter((f) => f && f.chain && f.chain.length);
const fixCur = (f) => f.chain.find((c) => c.stage === 'current') || f.chain[f.chain.length - 1];
function chainNode(f, big) {
  const c = el('span', 'chain'); const cur = fixCur(f);
  f.chain.forEach((st, i) => { if (i) { const s = el('s'); if (st.status !== 'none' && st.stage !== 'current') s.classList.add('on'); if (st.stage === 'current') s.classList.add('on'); c.append(s); } const n = el('i', st.stage === 'current' ? 'cur ' + (cur.status || '') : (st.status || 'none')); n.title = (st.stage === 'current' ? 'Current status' : st.stage.replace('_', ' ')) + ': ' + (st.status || '') + (st.date ? ', ' + fmtDate(new Date(st.date)) : ''); c.append(n); });
  return c;
}
const fixOpen = { id: null };
function drawFixes() {
  const sec = document.getElementById('fixes'), box = document.getElementById('fix-list'), sum = document.getElementById('fix-summary'); if (!box) return;
  const rows = fixRows(); if (!rows.length) { sec.style.display = 'none'; return; } sec.style.display = '';
  const sev = (f) => (C.scored.find((r) => r.id === f.incident_id) || {}).severity || 0;
  rows.sort((a, b) => (FIXORD[fixCur(a).status] ?? 9) - (FIXORD[fixCur(b).status] ?? 9) || sev(b) - sev(a));
  const counts = d3.rollup(rows, (v) => v.length, (f) => fixCur(f).status);
  document.getElementById('fix-k').textContent = rows.length + ' cases, checked every refresh';
  const parts = [txt('Of '), el('b', null, String(rows.length)), txt(' major incidents: ')];
  const order = ['fixed', 'unverified', 'disputed', 'reopened', 'unresolved', 'ongoing'].filter((k) => counts.get(k));
  order.forEach((k, i) => { parts.push(el('b', null, String(counts.get(k))), txt(' ' + FIXST[k].toLowerCase() + (i < order.length - 1 ? (i === order.length - 2 ? ' and ' : ', ') : '.'))); });
  const nRetest = rows.filter((f) => (f.chain.find((c) => c.stage === 'retest') || {}).status === 'done').length;
  parts.push(txt(' Independent verification exists for '), el('b', null, String(nRetest)), txt(nRetest === 1 ? ' case.' : ' cases.'));
  sum.replaceChildren(...parts);
  const lg = document.getElementById('fix-legend'); lg.replaceChildren(el('span', null, 'The chain, left to right:'), el('span', null, 'reported'), el('span', null, '→ response'), el('span', null, '→ claimed fix'), el('span', null, '→ independent check'), el('span', null, '→ now.'), el('span', null, 'Filled: done. Half: partial. Hollow: nothing found. Click a case for the evidence.'));
  box.replaceChildren(...rows.map((f) => {
    const cur = fixCur(f); const row = el('div', 'fix' + (fixOpen.id === f.incident_id ? ' open' : '')); row.id = 'fix-' + f.incident_id; row.tabIndex = 0;
    const name = el('div', 'fix-name'); name.append(txt(f.name), el('span', 'stt ' + cur.status, FIXST[cur.status] || cur.status));
    const line = el('div', 'fix-line', f.one_liner || cur.note || '');
    const det = el('div', 'fix-detail');
    f.chain.forEach((st) => { const r = el('div', 'st'); const b = el('b'); b.append(txt(st.stage === 'current' ? 'Current status' : st.stage === 'claimed_fix' ? 'Claimed fix' : st.stage === 'retest' ? 'Independent check' : st.stage.charAt(0).toUpperCase() + st.stage.slice(1))); if (st.date) b.append(el('small', null, fmtDate(new Date(st.date)))); const sp = el('span', null, (st.stage === 'current' ? '' : (st.status === 'none' ? '' : '')) + (st.note || '')); if (st.source_url) { const a = el('a', null, 'source'); a.href = st.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.addEventListener('click', (e) => e.stopPropagation()); sp.append(a); } r.append(b, sp); det.append(r); });
    if (f.what_would_change_it) { const w = el('div', 'wd'); w.append(el('b', null, 'What would change it: '), txt(f.what_would_change_it)); det.append(w); }
    const r0 = C.scored.find((r) => r.id === f.incident_id); const dive = D.deepdives.find((d) => d.incident_id === f.incident_id);
    const links = el('div', 'wd'); if (r0) { const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r0.severity)); sc.style.color = tierText(r0.tier); b.append(sc, el('span', null, 'Open the incident')); b.addEventListener('click', (e) => { e.stopPropagation(); openIncident(r0.id); }); links.append(b); } if (dive) { const a = el('a', null, 'Full breakdown'); a.href = '#d=' + dive.incident_id; a.style.marginLeft = '10px'; a.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); go('#d=' + dive.incident_id); }); links.append(a); } if (links.children.length) det.append(links);
    const sh2 = el('div', 'share'); shareRow(sh2, { anchor: 'c=' + f.incident_id, text: f.name + ': ' + (f.one_liner || '') + ' Warning Shots:', card: cardForCase(f) }); det.append(sh2);
    row.append(name, chainNode(f), line, det);
    const toggle = () => { fixOpen.id = fixOpen.id === f.incident_id ? null : f.incident_id; row.classList.toggle('open'); };
    row.addEventListener('click', (e) => { if (e.target.closest('a, button')) return; toggle(); }); row.addEventListener('keydown', (e) => { if (e.key === 'Enter') toggle(); });
    return row;
  }));
  shareRow(document.getElementById('share-fixes'), { anchor: 'card-fixes', text: `Did they fix it? ${rows.length} major AI incidents tracked from report to response to claimed fix to independent check. Verified fixes so far: ${counts.get('fixed') || 0}. Warning Shots:`, embed: 'fixes', embedH: 760 });
}

/* ---------- signal ribbon (real telemetry only) */
function drawRibbon() {
  const box = document.getElementById('ribbon-in'); if (!box) return;
  const asOf = Date.parse(D.meta.as_of), day = 864e5, within = (iso, h) => iso && (asOf - Date.parse(iso)) <= h * 3.6e6 && Date.parse(iso) <= asOf + day;
  const stamp = fmtET(D.meta.as_of);
  const newInc = C.scored.filter((r) => within(r.disclosed || r.date, 24 * 7)).length;
  const newIncDay = C.scored.filter((r) => within(r.disclosed || r.date, 24)).length;
  const fx = fixRows(); const openCases = fx.filter((f) => fixCur(f).status !== 'fixed').length;
  const fxUpd = fx.filter((f) => f.chain.some((c) => within(c.date, 24 * 7))).length;
  const caps = capRows().filter((c) => within(c.date, 24 * 7)).length;
  const wire = newsItems().filter((n) => n.published && (asOf + 3 * 3.6e6 - Date.parse(n.published)) <= 24 * 3.6e6).length;
  const items = [
    { n: newIncDay, l: (newIncDay === 1 ? 'new incident, 24h' : 'new incidents, 24h'), href: '#all', hot: newIncDay > 0, t: `Incidents added to this index with an event or disclosure date in the 24 hours before the last refresh (${stamp}). ${newInc} in the last 7 days. Deduplicated by event; this index is curated, not a census. Source: data/incidents.json.` },
    { n: openCases, l: 'open cases of ' + fx.length, href: '#fixes', hot: false, t: `Major incidents in "Did they fix it?" with no independently verified fix as of ${stamp}. Source: data/fixes.json.` },
    { n: caps, l: (caps === 1 ? 'new advance, 7d' : 'new advances, 7d'), href: '#capabilities', hot: caps > 0, t: `Capability milestones added with a date in the 7 days before ${stamp}. Source: data/capabilities.json.` },
    { n: fxUpd, l: (fxUpd === 1 ? 'follow-up moved, 7d' : 'follow-ups moved, 7d'), href: '#fixes', hot: fxUpd > 0, t: `Cases with a dated change in their report → response → fix → check chain in the 7 days before ${stamp}. Source: data/fixes.json.` },
    { n: wire, l: (wire === 1 ? 'report on the Wire, 24h' : 'reports on the Wire, 24h'), href: '#wire', hot: false, t: `Stories on the Wire published in the 24 hours up to about three hours after ${stamp}. Links to the outlets; nothing is copied. Source: data/news.json.` },
  ];
  const hrc = houseRecord(); if (false) items.unshift({ n: hrc.n ? hrc.w + '–' + hrc.l : hrc.open, l: hrc.n ? 'the index’s record, ' + hrc.open + ' open' : 'open calls, graded in public', href: '#calls', hot: false, t: `Dated yes/no questions with the index's odds. ${hrc.n ? hrc.w + ' right, ' + hrc.l + ' wrong so far; Brier ' + hrc.brier.toFixed(2) + '.' : 'Nothing has resolved yet.'} Source: data/calls.json.` });
  box.replaceChildren(...items.map((it) => { const a = el('a', 'rb' + (it.hot ? ' hot' : '')); a.href = it.href; a.title = it.t; a.append(el('b', null, String(it.n)), el('span', null, it.l)); a.addEventListener('click', (e) => { e.preventDefault(); if (it.href === '#all') { ls.sort = 'new'; document.getElementById('sel-sort').value = 'new'; drawList(); } go(it.href); }); return a; }));
  const u = el('span', 'rb-upd'); u.append(el('i'), txt('Updated ' + stamp + (D.meta.next_check ? ', next ' + fmtETsmart(D.meta.next_check).replace('today ', '') : ''))); u.title = D.meta.schedule || ''; box.append(u);
  const ed = document.getElementById('edition'); if (ed) ed.textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date(D.meta.as_of)) + ' edition';
}

/* ---------- What it means for you: five everyday lenses on the same data. The chosen lens is remembered in this browser only. */
const LENSES = [
  { id: 'family', hub: [['/help/', 'What to do when AI is used against your family'], ['/learn/ai-companions-parents-guide/', 'AI companions: a parent’s guide']], label: 'Your family', lede: 'Chatbots your kids talk to, deepfakes made of children, and calls that sound like someone you love.',
    topics: ['families', 'chatbot-harm'], cats: ['child_safety', 'psych_harm'], kw: /\b(child|children|teen|teenage|kids?|school|student|minor|parent|family|classmate)s?\b/i,
    act: [
      ['Agree a family safe word, so a cloned voice asking for money can be checked with one question.', '/shield/', 'Make one, free'],
      ['Ask which chatbots your kids talk to, and look at the companion or “friend” settings together.'],
      ['If someone makes a sexual image of a child, report it; Take It Down helps remove it from major platforms.', 'https://takeitdown.ncmec.org/', 'NCMEC Take It Down'],
    ] },
  { id: 'money', hub: [['/checks/', 'Is this a scam? Check it in a minute'], ['/help/voice-clone-scam-call/', 'A loved one calls in a panic: what to do']], label: 'Your money', lede: 'Voice-clone and deepfake scams, AI agents inside bank accounts, and faked photos used for refunds.',
    topics: ['everyday'], cats: ['fraud_deepfake'], kw: /\b(scam|scams|fraud|bank|banks|refund|crypto|money|savings|voice[- ]clon\w*|impersonat\w*)\b/i,
    act: [
      ['If a call or video asks you to move money urgently, hang up and call back on a number you already have.'],
      ['Treat a familiar voice or face as unproven; a few seconds of audio is enough to clone one.', '/shield/', 'The safe-word tool'],
      ['Don’t hand an AI agent or app your bank login; banks are restricting third-party agents found inside accounts.'],
    ] },
  { id: 'work', hub: [['/jobs/', 'Can AI do your job? 20 jobs graded'], ['/jobs/layoffs/', 'Layoffs tied to AI, company by company']], label: 'Your job', lede: 'Layoffs tied to AI, and staff pasting patient, customer and HR records into tools nobody approved.',
    topics: ['jobs'], cats: ['privacy_data', 'agent_accident'], kw: /\b(jobs?|layoffs?|hiring|workers?|employees?|staff|workplace|uploaded)\b/i,
    act: [
      ['Don’t paste customer, patient or HR data into an AI tool your employer hasn’t approved; two employers on this index did it this month.'],
      ['If you run AI agents at work, give them only the access the task needs, and retire idle ones with their keys.'],
      ['Check an agent’s report of what it did against what it actually changed; agents on this index have misreported their own work.'],
    ] },
  { id: 'health', hub: [['/wire/decided/', 'AI decided: cases still open'], ['/can-ai/diagnose-illness-or-read-scans/', 'Can AI read scans? Graded']], label: 'Your health', lede: 'Algorithms that decide what care insurers pay for, hospital staff feeding patient records to AI, and AI moving into diagnosis and discharge.',
    topics: [], cats: ['privacy_data'], kw: /\b(hospitals?|patients?|health ?care|medical|medicare|insurer|claims? denied|doctors?|clinics?|nurses?|diagnos\w*)\b/i,
    act: [
      ['If an insurer denies care, ask in writing whether a clinician reviewed it, then appeal; you have the right to.'],
      ['Treat a chatbot’s medical answer as questions for your doctor, not a diagnosis.'],
      ['Ask your hospital or clinic how AI is used on your records, and who they were shared with.'],
    ] },
  { id: 'bills', beat: 'near-you', hub: [['/wire/near-you/', 'AI near you: data centres, power and water']], label: 'Your bills & town', lede: 'Data centres for AI are driving new power plants and lines. Who pays is being decided now, in rate cases most people never see.',
    topics: [], cats: [], kw: /data[- ]?cent(er|re)s?|power bills?|electricity (bill|price|rate)s?|\butilit(y|ies)\b|ratepayers?/i,
    act: [
      ['Look up your utility’s open rate cases at your state utility commission; customer comments go on the record.'],
      ['If a data centre is proposed near you, go to the zoning or utility hearing and ask who pays for the new lines and plants.'],
      ['Read your bill’s fuel and transmission charges: that is where new grid costs usually show up.'],
    ] },
  { id: 'site', hub: [['/php2shell/', 'The PHP flaw: live tracker'], ['/scraped/', 'Keep your site out of AI training sets']], label: 'Your website', lede: 'The PHP flaws AI found, AI agents breaking into company systems, and crawlers scraping for training data.',
    topics: ['php2shell', 'ai-attack'], cats: ['cyber_offense', 'security_vuln', 'ai_vuln'], kw: /\b(php|website|hack\w*|breach\w*|intrusion)\b/i,
    act: [
      ['If your site runs on PHP, ask your host or developer whether it is on a release fixed on or after Oct 21, 2026.', '#d=php2shell', 'The PHP2Shell breakdown'],
      ['Keep your work out of AI training sets with a robots.txt built for the crawlers that scrape for AI.', '/scraped/', 'Build one, free'],
      ['Review which outside tools and AI agents hold keys to your systems; this week’s breaches went through third-party software.'],
    ] },
  { id: 'vote', hub: [['/midterms-2026/', 'Every AI fake in the midterms'], ['/help/is-this-video-real/', 'Is this video real? How to check']], label: 'Elections & news', lede: 'AI-made campaign ads, deepfakes of candidates and officials, and what governments are doing about it.',
    topics: ['deepfakes', 'regulation'], cats: ['info_integrity'], kw: /\b(election|elections|vote|voters?|campaign|candidate|midterms?|deepfakes?)\b/i,
    act: [
      ['Before sharing a shocking clip of a candidate, check whether a major outlet or the campaign has confirmed it.'],
      ['Political AI ads often aren’t labelled; a study of the 2026 US midterms found only about a quarter were disclosed.'],
      ['The US midterms are Nov 3; the FBI and CISA have warned officials about AI-powered deception before the vote.'],
    ] },
];
let LAST_SEEN = null; // the as_of of the reader's previous visit, set once by drawSinceVisit
const lensPref = () => { try { return localStorage.getItem('ws-lens'); } catch (e) { return null; } };
let lensCur = null;
function lensStories(L) {
  return newsItems().filter((n) => (L.beat && n.beat === L.beat) || (L.topics.includes(n.topic) && (L.id !== 'money' || L.kw.test(n.title + ' ' + (n.summary || '')))) || (n.topic !== 'php2shell' || L.id === 'site') && L.kw.test((n.tag || '') + ' ' + n.title)).sort((a, b) => (b.wall ? 1 : 0) - (a.wall ? 1 : 0) || String(b.published).localeCompare(String(a.published)));
}
function lensIncidents(L) {
  const cut = Date.parse(D.meta.as_of) - 72 * 3.6e6; // the front page already carries the last three days; this shows the record behind them
  return C.scored.filter((r) => L.cats.includes(r.category) && r.setting !== 'lab' && Date.parse(r.disclosed || r.date) < cut).sort((a, b) => String(b.disclosed || b.date).localeCompare(String(a.disclosed || a.date)));
}
let whyOpen = window.innerWidth >= 900; // open on wide screens; on phones it opens when a reader picks a topic
const checkState = {}; // the reader's answers to the 30-second check, this page view only (never stored or sent)
function drawWhy() {
  const box = document.getElementById('why-grid'), tabs = document.getElementById('fy-tabs'); if (!box || !tabs) return;
  if (!lensCur) lensCur = LENSES.some((l) => l.id === lensPref()) ? lensPref() : 'family';
  const L = LENSES.find((l) => l.id === lensCur); const LX = (D.lenses || {})[L.id] || {};
  const sec = document.getElementById('why'); if (sec) sec.classList.toggle('shut', !whyOpen);
  const asOfD = D.meta.as_of.slice(0, 10);
  tabs.replaceChildren(...LENSES.map((l) => {
    const b = el('button', 'fy-tab' + (whyOpen && l.id === lensCur ? ' on' : '')); b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('aria-selected', String(l.id === lensCur));
    const n = lensStories(l).length; b.append(el('span', 'fy-l', l.label), el('span', 'fy-n', n ? n + (n === 1 ? ' story' : ' stories') + ' in 3 days' : 'Nothing new in 3 days'));
    b.addEventListener('click', () => { whyOpen = !(whyOpen && lensCur === l.id); lensCur = l.id; try { localStorage.setItem('ws-lens', l.id); } catch (e) {} drawWhy(); });
    return b;
  }));
  const stories = lensStories(L).slice(0, 4), incs = lensIncidents(L).slice(0, 3);
  const left = el('div', 'fy-feed');
  left.append(el('p', 'fy-lede', L.lede));
  // 1. Right now: the latest reporting on this topic, with who each story touches
  left.append(el('div', 'fy-h', 'Right now'));
  if (stories.length) { const ul = el('ul', 'fy-list'); stories.forEach((n) => { const li = el('li'); const a = el('a', 'fy-s', n.tag || n.title); a.href = n.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; if (isNewToReader(n)) li.append(el('span', 'fy-new', 'New')); li.append(a, el('div', 'fy-m', (n.outlet || '') + ' · ' + ageShort(n))); if (n.touches) li.append(el('div', 'fy-w', 'Who this touches: ' + n.touches)); ul.append(li); }); left.append(ul); }
  else left.append(el('p', 'fy-empty', 'No new reporting on this in the last three days. The record and the check below still apply.'));
  // 2. The 30-second check: three questions; each answer that applies brings its own fix. Nothing is scored, stored or sent.
  if ((LX.check || []).length) {
    const st = checkState[L.id] || (checkState[L.id] = {});
    const ck = el('div', 'fy-check'); ck.append(el('div', 'fy-h', 'Check yourself in 30 seconds'));
    LX.check.forEach((q, qi) => { const row = el('div', 'fc-q'); row.append(el('p', 'fc-t', q.q)); const bs = el('div', 'fc-b');
      ['yes', 'no'].forEach((v) => { const b = el('button', 'fc-o' + (st[qi] === v ? ' on' : ''), v === 'yes' ? 'Yes' : 'No'); b.type = 'button'; b.setAttribute('aria-pressed', String(st[qi] === v)); b.addEventListener('click', () => { st[qi] = st[qi] === v ? undefined : v; drawWhy(); }); bs.append(b); });
      row.append(bs);
      if (st[qi] && st[qi] === q.flag) { const fx = el('p', 'fc-fix'); fx.append(el('b', null, 'Do this: '), txt(q.fix)); if (q.link) { const a = el('a', null, ' ' + q.link[1] + ' →'); a.href = q.link[0]; fx.append(a); } row.append(fx); }
      else if (st[qi]) row.append(el('p', 'fc-ok', 'Good: nothing to do on this one.'));
      ck.append(row); });
    const done = LX.check.filter((q, qi) => st[qi]).length, flagged = LX.check.filter((q, qi) => st[qi] && st[qi] === q.flag).length;
    if (done === LX.check.length) ck.append(el('p', 'fc-sum', flagged ? flagged + (flagged === 1 ? ' thing' : ' things') + ' worth doing this week, listed above. Your answers stay on this page and are never sent.' : 'You’ve covered the basics here. Your answers stay on this page and are never sent.'));
    else ck.append(el('p', 'fc-note', 'Your answers stay on this page and are never stored or sent.'));
    left.append(ck);
  }
  if (incs.length) {
    left.append(el('div', 'fy-h', 'It has happened before'));
    const rec = el('div', 'fy-rec');
    incs.forEach((r) => { const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r.severity)); sc.style.color = tierText(r.tier); b.append(sc, el('span', null, r.title)); b.addEventListener('click', () => openIncident(r.id)); rec.append(b); });
    left.append(rec);
  }
  const right = el('div', 'fy-do dark-scope');
  right.append(el('div', 'fy-do-k', 'What you can do'));
  const ol = el('ol');
  L.act.forEach(([t, href, label]) => { const li = el('li'); li.append(el('span', null, t)); if (href) { const a = el('a', null, label + ' →'); a.href = href; if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } li.append(a); } ol.append(li); });
  right.append(ol);
  // 3. What to watch: real dates (hearings, deadlines, the index's own calls on this topic), soonest first
  const watch = (LX.watch || []).filter((w) => !w.date || w.date >= asOfD).map((w) => ({ d: w.date, t: w.text, u: w.url }))
    .concat((LX.calls || []).map((id) => (D.calls || []).find((c) => c && c.id === id)).filter((c) => c && !c.resolution && c.resolve_by >= asOfD).map((c) => ({ d: c.resolve_by, t: (c.plain || c.question) + ' Our odds: ' + likelyWord(c.odds).toLowerCase() + '.', u: '/forecast/' + c.id + '/' })))
    .sort((a, b) => (a.d || '9999').localeCompare(b.d || '9999')).slice(0, 4);
  if (watch.length) { const wb = el('div', 'fy-watch'); wb.append(el('div', 'fy-do-k2', 'What to watch')); const ul = el('ul'); watch.forEach((w) => { const li = el('li'); li.append(el('b', null, w.d ? d3.utcFormat('%b %-d')(new Date(w.d + 'T12:00:00Z')) + (w.d.slice(0, 4) !== asOfD.slice(0, 4) ? ', ' + w.d.slice(0, 4) : '') : 'Open')); const a = el('a', null, w.t); a.href = w.u; if (/^https?:/.test(w.u)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; } li.append(a); ul.append(li); }); wb.append(ul); right.append(wb); }
  if (L.hub) { const hb = el('p', 'fy-hub'); L.hub.forEach(([u, t], i) => { const a = el('a', null, t + ' →'); a.href = u; hb.append(...(i ? [txt(' · ')] : []), a); }); right.append(hb); }
  right.append(el('p', 'fy-do-note', 'Your choice of topic is remembered in this browser only.'));
  box.replaceChildren(left, right);
}

/* ---------- Then. Now. Still. (from published evidence) */
function drawTNS() {
  const card = document.getElementById('card-tns'), box = document.getElementById('tns'); if (!card) return;
  const t = D.tns; if (!t || !t.then) { card.style.display = 'none'; return; } card.style.display = '';
  document.getElementById('tns-note').textContent = t.note || '';
  const capOf = (id) => capRows().find((c) => c.id === id), incOf = (id) => C.scored.find((r) => r.id === id);
  const col = (k, label, cls) => { const d = el('div', 'tns-col ' + cls); d.append(el('div', 'k', label)); const it = t[k]; if (it.date) d.append(el('div', 'd', it.date)); d.append(el('div', 't', it.title)); const s2 = el('div', 's', it.text); (it.capabilities || []).forEach((id) => { const c = capOf(id); if (!c) return; const a = el('a', null, 'source'); a.href = c.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; s2.append(a); }); d.append(s2);
    if (it.incidents && it.incidents.length) { const ul = el('ul'); it.incidents.forEach((id) => { const r = incOf(id); if (!r) return; const li = el('li'); const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r.severity)); sc.style.color = tierText(r.tier); b.append(sc, el('span', null, r.title)); b.addEventListener('click', () => openIncident(r.id)); li.append(b); ul.append(li); }); d.append(ul); }
    return d; };
  const foot = el('div', 'tns-foot'); [['could_change', 'What this could change for you'], ['do_now', 'What you can do now']].forEach(([k, l]) => { if (!t[k]) return; const d = el('div'); d.append(el('b', null, l), txt(t[k])); foot.append(d); });
  box.replaceChildren(col('then', 'Then', 'c-then'), col('now', 'Now', 'c-now'), col('still', 'Still', 'c-still'), foot);
  shareRow(document.getElementById('share-tns'), { anchor: 'card-tns', text: `Then. Now. Still. ${t.then.title} → ${t.now.title} → still: ${t.still.title}. Warning Shots:`, embed: 'tns', embedH: 520 });
}
function drawFieldnote() { const f = document.getElementById('fieldnote'); if (!f) return; const u = (D.meta.fieldnote_url || '').trim(); f.hidden = !u; if (u) document.getElementById('fieldnote-link').href = u; }

/* ---------- since your last visit (saved in this browser only) */
function drawSinceVisit() {
  const bar = document.getElementById('since'); if (!bar) return;
  let prev = null; try { prev = localStorage.getItem('ws-last-asof'); } catch (e) {}
  const cur = D.meta.as_of; if (LAST_SEEN === null) LAST_SEEN = (prev && prev !== cur) ? prev : '';
  try { localStorage.setItem('ws-last-asof', cur); } catch (e) {}
  if (!prev || prev === cur || Date.parse(prev) > Date.parse(cur)) { bar.hidden = true; return; }
  const t0 = Date.parse(prev), t1 = Date.parse(cur), between = (iso) => iso && Date.parse(iso) > t0 && Date.parse(iso) <= t1 + 3 * 3.6e6;
  const inc = C.scored.filter((r) => between(r.disclosed || r.date)).length, news = newsItems().filter((n) => between(n.published)).length, caps = capRows().filter((c) => between(c.date)).length;
  const moved = fixRows().filter((f) => f.chain.some((c) => between(c.date)));
  const parts = [];
  if (inc) parts.push(inc + (inc === 1 ? ' new incident' : ' new incidents'));
  if (caps) parts.push(caps + (caps === 1 ? ' new advance' : ' new advances'));
  if (moved.length) parts.push(moved.length + (moved.length === 1 ? ' case moved (' : ' cases moved (') + moved.slice(0, 3).map((f) => f.name.split(':')[0]).join(', ') + ')');
  if (news) parts.push(news + (news === 1 ? ' report on the Wire' : ' reports on the Wire'));
  const graded = callRows().filter((c) => c.resolution && between(c.resolution.date)); if (graded.length) parts.push(graded.length + (graded.length === 1 ? ' forecast graded' : ' forecasts graded'));
  bar.hidden = false; bar.replaceChildren();
  const txtNode = el('span'); txtNode.append(el('b', null, 'Since your last visit (' + fmtET(prev) + '): '), txt(parts.length ? parts.join(', ') + '.' : 'nothing material changed. You’re caught up.'));
  const note = el('span', 'since-note', 'Saved in this browser only.'); const reset = el('button', null, 'Reset'); reset.type = 'button'; reset.addEventListener('click', () => { try { localStorage.removeItem('ws-last-asof'); } catch (e) {} bar.hidden = true; toast('Reset'); });
  bar.append(txtNode, note, reset);
}


/* ---------- site-wide search: incidents, the Wire, cases, milestones, quotes and statements, from the data already loaded */
let SIDX = null;
const snorm = (x) => String(x || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[’‘]/g, "'");
function searchIndex() {
  if (SIDX) return SIDX;
  const rows = [];
  C.scored.forEach((r) => rows.push({ kind: 'Incidents', title: r.title, text: [r.summary, r.actors, r.harm, r.category_label, r.ws].join(' '), kicker: r.ws + ' · ' + showDate(r) + ' · ' + r.severity + '/100 ' + r.tier, go: () => go('#i=' + r.id) }));
  newsItems().forEach((n) => rows.push({ kind: 'The Wire', title: n.title, text: [n.summary, n.outlet, n.topic].join(' '), kicker: (n.outlet || '') + ' · ' + ageShort(n), href: n.url }));
  fixRows().forEach((f) => rows.push({ kind: 'Did they fix it?', title: f.name, text: [f.one_liner].concat(f.chain.map((c) => c.note)).join(' '), kicker: 'Case · ' + String(fixCur(f).status || '').replace('_', ' '), go: () => go('#c=' + f.incident_id) }));
  capRows().forEach((c) => rows.push({ kind: 'What AI can now do', title: c.title, text: [c.what, c.org, c.everyday, c.domain].join(' '), kicker: 'Milestone · ' + fmtDate(new Date(c.date)) + (c.org ? ' · ' + c.org : ''), go: () => go('#m=' + c.id) }));
  callRows().forEach((c) => rows.push({ kind: 'What to expect', title: c.question, text: [c.basis, c.signposts, (c.tags || []).join(' ')].join(' '), kicker: likelyWord(c.odds) + ' · ' + callDue(c), go: () => go('#fc-' + c.id) }));
  (D.quotes || []).forEach((q) => { if (q && q.quote) rows.push({ kind: 'In their words', title: q.quote, text: [q.speaker, q.title].join(' '), kicker: (q.speaker || '') + (q.title ? ', ' + q.title : '') + (q.date ? ' · ' + fmtDate(new Date(q.date)) : ''), go: () => go('#q=' + q.id) }); });
  (D.signals || []).forEach((x) => { if (x && x.gist) rows.push({ kind: 'Official signals', title: x.gist, text: [x.org, x.speaker, x.quote].join(' '), kicker: (x.org || '') + (x.date ? ' · ' + fmtDate(new Date(x.date)) : ''), href: x.url || null, go: x.url ? null : () => go('#signals') }); });
  rows.forEach((r) => { r.t = snorm(r.title); r.x = snorm(r.text); });
  SIDX = rows; return rows;
}
const KIND_W = { 'Incidents': 1.3, 'Did they fix it?': 1.2, 'The call sheet': 1.2, 'What AI can now do': 1.15, 'The Wire': 1.1, 'In their words': 1, 'Official signals': 1 };
function searchRun(q) {
  const toks = snorm(q).split(/[^a-z0-9%$.+-]+/).filter((t) => t.length >= 2);
  if (!toks.length) return { toks, rows: [] };
  const out = [];
  for (const r of searchIndex()) {
    let score = 0, all = true;
    for (const t of toks) { const inT = r.t.includes(t), inX = r.x.includes(t); if (!inT && !inX) { all = false; break; } score += inT ? 3 : 1; if (r.t.startsWith(t)) score += 1; }
    if (all) out.push([score * (KIND_W[r.kind] || 1), r]);
  }
  out.sort((a, b) => b[0] - a[0]);
  return { toks, rows: out.map((x) => x[1]) };
}
function markText(node, text, toks) {
  const low = snorm(text); let i = 0;
  const hits = []; toks.forEach((t) => { let p = low.indexOf(t); while (p >= 0 && hits.length < 40) { hits.push([p, p + t.length]); p = low.indexOf(t, p + t.length); } });
  hits.sort((a, b) => a[0] - b[0]);
  for (const [a, b] of hits) { if (a < i) continue; if (a > i) node.append(txt(text.slice(i, a))); node.append(el('mark', null, text.slice(a, b))); i = b; }
  if (i < text.length) node.append(txt(text.slice(i)));
}
function showSearch(prefill) {
  let m = document.getElementById('search-modal'); if (m) { m.querySelector('input').focus(); return; }
  if (!C.scored) return;
  m = el('div', 'card-modal top'); m.id = 'search-modal'; m.setAttribute('role', 'dialog'); m.setAttribute('aria-label', 'Search the index');
  const box = el('div', 'card-box search-box'); const form = el('form'); form.setAttribute('role', 'search');
  form.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
  const input = el('input'); input.type = 'search'; input.placeholder = 'Search incidents, the Wire, cases, milestones, quotes, statements'; input.setAttribute('aria-label', 'Search'); input.autocomplete = 'off'; input.value = prefill || '';
  const esc = el('span', 'esc', 'esc'); form.append(input, esc);
  const res = el('div', 'search-res'); res.setAttribute('role', 'listbox');
  const foot = el('div', 'search-foot'); foot.append(el('span', null, '↑ ↓ to move, Enter to open'), el('span', null, 'Searches everything loaded on this page; the Wire opens the outlet.'));
  box.append(form, res, foot); m.append(box); document.body.append(m);
  const close = () => { m.remove(); document.getElementById('nav-search')?.focus(); };
  let cur = -1, rowsEls = [];
  const render = () => {
    const { toks, rows } = searchRun(input.value); res.replaceChildren(); rowsEls = []; cur = -1;
    if (!input.value.trim()) { res.append(el('div', 'empty', 'Try a company, a model, a country, a date, “deepfake”, “wrongful death”, “PHP”.')); return; }
    if (!rows.length) { res.append(el('div', 'empty', 'Nothing matches. Try fewer words.')); return; }
    const groups = []; const byKind = {}; rows.forEach((r) => { if (!byKind[r.kind]) { byKind[r.kind] = []; groups.push(r.kind); } if (byKind[r.kind].length < 6) byKind[r.kind].push(r); });
    let n = 0;
    groups.forEach((k) => { res.append(el('div', 'grp', k)); byKind[k].forEach((r) => { if (n >= 30) return; n++;
      const a = r.href ? el('a', 'r') : el('button', 'r'); if (r.href) { a.href = r.href; a.target = '_blank'; a.rel = 'noopener noreferrer'; } else a.type = 'button';
      a.setAttribute('role', 'option'); const t = el('div', 'rt'); markText(t, r.title.length > 160 ? r.title.slice(0, 158) + '…' : r.title, toks); const kk = el('div', 'rk'); kk.append(txt(r.kicker)); a.append(t, kk);
      a.addEventListener('click', () => { if (r.go) { close(); r.go(); } else setTimeout(close, 50); }); res.append(a); rowsEls.push(a); }); });
  };
  const move = (d) => { if (!rowsEls.length) return; rowsEls[cur]?.classList.remove('on'); cur = (cur + d + rowsEls.length) % rowsEls.length; rowsEls[cur].classList.add('on'); rowsEls[cur].scrollIntoView({ block: 'nearest' }); };
  input.addEventListener('input', render);
  form.addEventListener('submit', (e) => { e.preventDefault(); (rowsEls[cur >= 0 ? cur : 0])?.click(); });
  m.addEventListener('keydown', (e) => { if (e.key === 'Escape') { e.preventDefault(); close(); } else if (e.key === 'ArrowDown') { e.preventDefault(); move(1); } else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); } });
  m.addEventListener('click', (e) => { if (e.target === m) close(); });
  render(); input.focus(); if (prefill) input.select();
}
document.getElementById('nav-search')?.addEventListener('click', () => showSearch());
/* ---------- keyboard shortcuts: J/K move through dispatches, Enter opens, S briefing card, ? help, Esc closes */
const KEYS_OFF = () => { try { return localStorage.getItem('ws-keys') === 'off'; } catch (e) { return false; } };
function navItems() { return [...document.querySelectorAll('.call, .wi, .row, .fix, .cap, .why')].filter((n) => n.offsetParent !== null); }
let navIdx = -1;
function focusNav(d) { const items = navItems(); if (!items.length) return; const cur = items.indexOf(document.activeElement); navIdx = cur >= 0 ? cur + d : (d > 0 ? 0 : items.length - 1); navIdx = Math.max(0, Math.min(items.length - 1, navIdx)); const n = items[navIdx]; if (!n.hasAttribute('tabindex')) n.tabIndex = 0; n.focus({ preventScroll: true }); n.scrollIntoView({ block: 'center', behavior: reduced ? 'auto' : 'smooth' }); }
function showHelp() {
  let m = document.getElementById('help-modal'); if (m) { m.remove(); return; }
  m = el('div', 'card-modal'); m.id = 'help-modal'; const box = el('div', 'card-box help-box');
  const off = KEYS_OFF();
  box.innerHTML = '<h3>Keyboard</h3><table class="keys"><tr><td><kbd>J</kbd> / <kbd>K</kbd></td><td>Next / previous dispatch (Wire stories, incidents, cases, milestones)</td></tr><tr><td><kbd>Enter</kbd></td><td>Open the focused dispatch</td></tr><tr><td><kbd>S</kbd></td><td>Briefing card for the focused incident</td></tr><tr><td><kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd></td><td>Jump to the Wire, the record, the Wire’s live panel</td></tr><tr><td><kbd>/</kbd> or <kbd>⌘K</kbd></td><td>Search everything on the index</td></tr><tr><td><kbd>Esc</kbd></td><td>Close</td></tr><tr><td><kbd>?</kbd></td><td>This help</td></tr></table><p class="count">Single-key shortcuts are ignored while you type. Every action also has a visible control.</p>';
  const acts = el('div', 'card-actions'); const tgl = el('button', 'more-btn', off ? 'Turn shortcuts on' : 'Turn shortcuts off'); tgl.type = 'button'; tgl.addEventListener('click', () => { try { localStorage.setItem('ws-keys', off ? 'on' : 'off'); } catch (e) {} m.remove(); toast(off ? 'Shortcuts on' : 'Shortcuts off'); });
  const close = el('button', 'more-btn', 'Close'); close.type = 'button'; close.addEventListener('click', () => m.remove()); acts.append(tgl, close); box.append(acts); m.append(box); m.addEventListener('click', (e) => { if (e.target === m) m.remove(); }); document.body.append(m); close.focus();
}
document.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) { e.preventDefault(); showSearch(); return; }
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const t = e.target; if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)) return;
  if (e.key === '?') { e.preventDefault(); showHelp(); return; }
  if (e.key === '/') { e.preventDefault(); showSearch(); return; }
  if (KEYS_OFF()) return;
  if (e.key === 'Escape') { document.getElementById('card-modal')?.remove(); document.getElementById('help-modal')?.remove(); document.getElementById('search-modal')?.remove(); return; }
  if (e.key === 'j' || e.key === 'J') { e.preventDefault(); focusNav(1); }
  else if (e.key === 'k' || e.key === 'K') { e.preventDefault(); focusNav(-1); }
  else if (e.key === 's' || e.key === 'S') { const n = document.activeElement; const id = n && n.id && n.id.startsWith('row-') ? n.id.slice(4) : null; const r = id && C.scored ? C.scored.find((x) => x.id === id) : null; if (r) { e.preventDefault(); briefingCard(cardForIncident(r)); } }
  else if (e.key === '1') go('#wire'); else if (e.key === '2') go('#record'); else if (e.key === '3') go('#now');
});

/* ---------- masthead: signup + sticky nav */
function drawSignup() {
  const f = document.getElementById('signup'); if (!f) return;
  const nl = D.meta.newsletter || {};
  if (!nl.action) { f.hidden = true; return; }
  f.action = nl.action; f.hidden = false; if (nl.email_field) f.querySelector('input[type=email]').name = nl.email_field;
  f.querySelectorAll('input[type=hidden]').forEach((h) => h.remove());
  Object.entries(nl.fields || {}).forEach(([k, v]) => { const h = el('input'); h.type = 'hidden'; h.name = k; h.value = v; f.append(h); });
  if (nl.note) f.querySelector('small').textContent = nl.note;
  if (!f._wired) { f._wired = true; f.addEventListener('submit', () => { setTimeout(() => { const ok = el('div', 'ok', 'Check your inbox to confirm.'); f.querySelector('.ok')?.remove(); f.append(ok); f.querySelector('input[type=email]').value = ''; }, 300); }); }
}
const navbar = document.getElementById('navbar'), masthead = document.querySelector('.masthead');
if (navbar && masthead && 'IntersectionObserver' in window) new IntersectionObserver((es) => { es.forEach((e) => navbar.classList.toggle('scrolled', !e.isIntersecting && e.boundingClientRect.top < 0)); }, { threshold: 0 }).observe(masthead);
const navLinks = [...document.querySelectorAll('#nav-scroll a')];
let navT;
function markNav() {
  if (MF()) return;
  let cur = null;
  navLinks.forEach((a) => { const n = document.getElementById(a.getAttribute('href').slice(1)); if (n && n.getBoundingClientRect().top <= 90) cur = a; });
  navLinks.forEach((a) => a.classList.toggle('on', a === cur));
  if (cur && window.innerWidth < 960) { const sc = document.getElementById('nav-scroll'); const r = cur.getBoundingClientRect(), sr = sc.getBoundingClientRect(); if (r.left < sr.left || r.right > sr.right - 28) sc.scrollTo({ left: cur.offsetLeft - 12, behavior: reduced ? 'auto' : 'smooth' }); }
}
window.addEventListener('scroll', () => { clearTimeout(navT); navT = setTimeout(markNav, 80); }, { passive: true });

/* ---------- chart tabs */
const CHART_DRAW = { 'card-quarters': () => drawQuarters(), 'card-disclosure': () => drawDisclosure(), 'card-scatter': () => drawScatter(), 'card-horizon': () => drawHorizon(), 'card-pipeline': () => drawPipeline() };
function showChart(id) {
  if (!CHART_DRAW[id]) return;
  document.querySelectorAll('#chart-panes > .pane').forEach((p) => { p.hidden = p.id !== id; });
  document.querySelectorAll('#chart-tabs button').forEach((b) => { const on = b.dataset.pane === id; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); });
  if (C.scored) CHART_DRAW[id]();
}
document.getElementById('chart-tabs').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) showChart(b.dataset.pane); });
const ALIAS = { escalation: 'charts', danger: 'charts', pipeline: 'charts', method: 'about', context: 'about' };

/* ---------- routing */
function go(hash) { location.hash = hash; route(); }
// Which page a hash belongs on. Old links to record sections on the front page forward to /index/, and the other way round.
function pageFor(h) {
  if (!h || h === 'top' || h.startsWith('i=')) return null;
  if (/^(d|c|m|q)=/.test(h) || /^(fc-|fix-|cap-|q-|row-|dd-|card-)/.test(h) || CHART_DRAW[h]) return 'record';
  if (RECORD_IDS.has(h)) return 'record';
  if (WIRE_IDS.has(h)) return 'wire';
  if (FRONT_IDS.has(h)) return 'front';
  const n = document.getElementById(h); if (!n) return null;
  const host = n.closest('main > *'); const sec = host && (host.matches('section') ? host : host.querySelector('section'));
  if (sec && RECORD_IDS.has(sec.id)) return 'record';
  if (sec && WIRE_IDS.has(sec.id)) return 'wire';
  if (sec && FRONT_IDS.has(sec.id)) return 'front';
  return null;
}
const PREFIX_SEC = [['fc-', 'next'], ['fix-', 'fixes'], ['cap-', 'capabilities'], ['q-', 'words'], ['row-', 'all'], ['dd-', 'dives'], ['card-', 'charts']];
function sectionOf(node) { const hit = LAZY.find(([sid]) => { const s = document.getElementById(sid); return s && s.contains(node); }); return hit ? hit[0] : null; }
function route() {
  let h = location.hash.slice(1);
  if (ALIAS[h]) h = ALIAS[h];
  if (!EMBED) { const want = pageFor(h); if (want && want !== PAGE) { location.replace((want === 'record' ? '/index/' : want === 'wire' ? '/wire/' : '/') + '#' + h); return; } }
  if (!C.scored) { const n0 = h && !h.includes('=') && document.getElementById(h); if (n0) n0.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); return; }
  if (MF()) { const t = mfTarget(h); if (t === 'front') { showFront(); return; } if (t) showSection(t); }
  if (CHART_DRAW[h]) { drawThrough('charts'); showChart(h); document.getElementById('charts').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); return; }
  if (h.startsWith('i=')) { openIncident(decodeURIComponent(h.slice(2))); return; }
  if (h.startsWith('c=')) { const id = decodeURIComponent(h.slice(2)); if (fixRows().find((f) => f.incident_id === id)) { fixOpen.id = id; drawThrough('fixes'); drawFixes(); document.getElementById('fix-' + id)?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } return; }
  if (h.startsWith('m=')) { const id = decodeURIComponent(h.slice(2)); if (capRows().find((c) => c.id === id)) { cap.openId = id; cap.open = true; cap.domain = 'all'; drawThrough('capabilities'); drawCapGrid(); document.getElementById('cap-' + id)?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } return; }
  if (h.startsWith('q=')) { drawThrough('words'); const n = document.getElementById('q-' + decodeURIComponent(h.slice(2))); if (n) { quotesOpen = true; drawQuotes(); document.getElementById('q-' + decodeURIComponent(h.slice(2)))?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } return; }
  if (h.startsWith('d=')) { const id = decodeURIComponent(h.slice(2)); if (D.deepdives.find((d) => d.incident_id === id)) { dd.id = id; dd.vfilter = 'all'; drawThrough('dives'); drawDeepDive(); document.getElementById('dives').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); } return; }
  if (h === 'top') { window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); return; }
  let n = h && document.getElementById(h);
  if (!n && h) { const pre = PREFIX_SEC.find(([p]) => h.startsWith(p)); if (pre) { drawThrough(pre[1]); n = document.getElementById(h); } }
  if (n) { const sid = sectionOf(n); if (sid) drawThrough(sid); if (n.classList.contains('fc')) n.classList.add('open'); n.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: n.matches('section, .hero-band') ? 'start' : 'center' }); }
}
window.addEventListener('hashchange', route);
document.querySelectorAll('a[href^="#"]').forEach((a) => a.addEventListener('click', (e) => { const h = a.getAttribute('href'); if (h.length < 2) return; e.preventDefault(); if (MF() && h !== location.hash) history.pushState(null, '', h); else history.replaceState(null, '', h); route(); }));


/* ---------- long live-panel notes open on click */
document.addEventListener('click', (e) => {
  const m = e.target.closest && e.target.closest('#now-more, #now-note'); if (m) { const n = document.getElementById('now-note'); const o = n.classList.toggle('open'); const b = document.getElementById('now-more'); if (b) b.textContent = o ? 'Show less' : 'Read the full note'; return; }
  const d = e.target.closest && e.target.closest('.live .d'); if (d && e.target.tagName !== 'A') d.classList.toggle('open');
});
/* ---------- phones: a front page and section views (body.mf). Desktop and the one-page mode are untouched. */
const MF_PREF = () => { try { return localStorage.getItem('ws-mf'); } catch (e) { return null; } };
const MF = () => PAGE === 'front' && !EMBED && window.innerWidth < 760 && MF_PREF() !== 'off';
const MF_SECTIONS = [['wire', 'The Wire'], ['why', 'What it means for you'], ['record', 'The record'], ['capabilities', 'What AI can now do'], ['words', 'In their words'], ['pattern', 'The pattern of 2026'], ['charts', 'The escalation, five ways'], ['next', 'Where this goes next'], ['dives', 'Inside the incidents'], ['fixes', 'Did they fix it?'], ['signals', 'Official signals'], ['all', 'All incidents'], ['about', 'About the data']];
let mfCur = null; // null = not in phone mode; 'front' or a section id
function mfTarget(h) {
  if (!h || h === 'front' || h === 'top') return 'front';
  if (h === 'wire' || h === 'now' || h === 'brief' || h === 'since') return 'wire';
  if (CHART_DRAW[h]) return 'charts';
  if (h.startsWith('i=')) return null;
  if (h.startsWith('c=')) return 'fixes'; if (h.startsWith('m=')) return 'capabilities'; if (h.startsWith('q=')) return 'words'; if (h.startsWith('d=')) return 'dives';
  const n = document.getElementById(h); if (!n) { const pre = PREFIX_SEC.find(([p]) => h.startsWith(p)); return pre ? pre[1] : 'front'; }
  const host = n.closest('main > *'); if (!host) return 'front';
  const sec = host.matches('section') ? host : host.querySelector('section');
  return sec && MF_SECTIONS.some(([id]) => id === sec.id) ? sec.id : 'front';
}
function mfApply(target) {
  const body = document.body, main = document.querySelector('main'), front = document.getElementById('front'), tab = document.getElementById('tabbar');
  document.querySelector('.mf-back')?.remove();
  if (!target) { body.classList.remove('mf', 'mf-sec'); [...main.children].forEach((c) => c.removeAttribute('data-mf')); front.hidden = true; tab.hidden = true; mfCur = null; document.querySelectorAll('#tabbar a, #nav-scroll a').forEach((a) => a.classList.remove('on')); return; }
  body.classList.add('mf'); tab.hidden = false; mfCur = target;
  const keep = new Set(['ribbon', 'since', 'ticker', 'stale']);
  body.classList.toggle('mf-sec', target !== 'front');
  [...main.children].forEach((c) => {
    if (keep.has(c.id)) { c.removeAttribute('data-mf'); return; }
    const sec = c.matches('section') ? c : c.querySelector('section'); const id = sec ? sec.id : c.id;
    const show = target === 'front' ? (id === 'wall' || id === 'wire' || id === 'front' || id === 'why') : id === target;
    if (show) c.removeAttribute('data-mf'); else c.setAttribute('data-mf', 'off');
  });
  front.hidden = target !== 'front';
  if (target !== 'front') {
    const sec = document.getElementById(target); const i = MF_SECTIONS.findIndex(([id]) => id === target);
    const bar = el('div', 'mf-back'); const back = el('a', null, '← Front'); back.href = '#front'; bar.append(back, el('span', 'k', (MF_SECTIONS[i] ? MF_SECTIONS[i][1] : '') + ' · section ' + (i + 1) + ' of ' + MF_SECTIONS.length));
    sec.prepend(bar);
  }
  const tabFor = target === 'front' ? 'front' : target === 'wire' ? 'wire' : target === 'record' ? 'record' : target === 'fixes' ? 'fixes' : target === 'next' ? 'next' : '';
  document.querySelectorAll('#tabbar a').forEach((a) => a.classList.toggle('on', a.dataset.tab === tabFor));
  document.querySelectorAll('#nav-scroll a').forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + (target === 'front' ? 'front' : target)));
}
function showSection(id) { if (!MF()) return; const re = mfCur !== id; mfApply(id); if (id === 'wire') { if (!wire.open) { wire.open = true; } drawWire(); } else drawSection(id); if (re) window.scrollTo({ top: Math.max(0, document.getElementById(id).getBoundingClientRect().top + scrollY - 52), behavior: 'auto' }); }
function showFront() { if (!MF()) return; const re = mfCur !== 'front'; mfApply('front'); if (wire.open) { wire.open = false; drawWire(); } drawFront(); if (re) window.scrollTo({ top: 0, behavior: 'auto' }); }
function mfSync() {
  if (!MF()) { if (mfCur) { mfApply(null); if (wire.open && window.innerWidth >= 760) { wire.open = false; } drawAll(false); } return; }
  let h = location.hash.slice(1); if (ALIAS[h]) h = ALIAS[h];
  const t = mfTarget(h); if (t === 'front' || t === null) { if (mfCur !== 'front' && !(t === null && mfCur)) showFront(); } else if (mfCur !== t) showSection(t);
}
function drawFront() {
  const box = document.getElementById('front-cards'), more = document.getElementById('front-more'); if (!box || !C.scored) return;
  const h = C.headline, fx = fixRows(), caps = capRows(), live = D.deepdives.find((d) => d.incident_id === D.meta.live_incident) || D.deepdives[0];
  const card = (href, kicker, title, sub, opts) => { const a = el('a', 'fcard' + (opts && opts.dark ? ' dark-scope' : '')); a.href = href; a.append(el('span', 'ck', kicker)); const t = el('span', 'ct'); if (opts && opts.titleNodes) t.append(...opts.titleNodes); else t.textContent = title; a.append(t, el('span', 'ar', '→'), el('span', 'cs', sub)); if (opts && opts.spark) a.append(opts.spark); return a; };
  const spark = el('span', 'spark'); const qs = (C.quarterly || []).slice(-14); const mx = Math.max(1, ...qs.map((q) => q.n)); qs.forEach((q, i) => { const b = el('i', i >= qs.length - 4 ? 'r' : ''); b.style.height = Math.round(q.n / mx * 100) + '%'; b.title = q.quarter + ': ' + q.n; spark.append(b); });
  const verified = fx.filter((f) => fixCur(f).status === 'fixed').length, reopened = fx.filter((f) => fixCur(f).status === 'reopened').length;
  const lastMoved = fx.slice().sort((a, b) => Math.max(...b.chain.map((c) => Date.parse(c.date) || 0)) - Math.max(...a.chain.map((c) => Date.parse(c.date) || 0)))[0];
  const newest = caps[0]; const nextCat = (D.catalysts || []).filter((c) => c.date >= C.asOf).sort((a, b) => a.date.localeCompare(b.date))[0]; const topF = (D.forecasts || []).slice().sort((a, b) => +b.probability - +a.probability)[0];
  const vc = C.victimCounts[live.incident_id] || {}; const countries = new Set((D.victims || []).filter((v) => v.incident_id === live.incident_id && v.country).map((v) => v.country)).size;
  const pct = (x) => Math.round(x * 100) + '%';
  box.replaceChildren(...[
    card('#record', 'The record · ' + fmtN(h.n) + ' incidents since 2023', '', 'Severe incidents ' + h.severe_prior12 + ' → ' + h.severe_last12 + ' in a year; in ' + pct(h.agentic_recent) + ' of this year’s real-world cases the AI did the acting.', { dark: true, titleNodes: [txt('AI has started breaking in '), el('b', null, 'on its own.')], spark }),
    card('#fixes', 'Did they fix it? · ' + fx.length + ' cases', '', lastMoved ? 'Newest move: ' + lastMoved.name.split(':')[0] + ', ' + String(fixCur(lastMoved).status).replace('_', ' ') + '.' : 'Checked every refresh.', { titleNodes: [el('b', null, String(verified)), txt(' of ' + fx.length + ' verified fixed. ' + reopened + ' reopened.')] }),
    // What AI can do and the live case have their own desks and tracker; the phone front keeps only the three doors nothing else opens
    card('#next', 'Where this goes next', nextCat ? nextCat.date_label + ': ' + nextCat.event : 'The next two weeks', topF ? topF.probability_label + ' that ' + topF.event.charAt(0).toLowerCase() + topF.event.slice(1) + '.' : ''),
  ].filter(Boolean));
  const link = (href, t, sub) => { const a = el('a'); a.href = href; a.append(el('b', null, t), txt(sub)); return a; };
  more.replaceChildren(link('/shield/', 'The family safe word', 'Beat voice-clone calls'), link('#all', 'All incidents', fmtN(h.n) + ', ranked and searchable'), link('#words', 'In their words', (D.quotes || []).length + ' quotes, verbatim'), link('#about', 'About the data', 'Scores, sources, corrections')); // the rest are one tap away in the menu and the desks
  document.getElementById('front-stamp').textContent = 'Updated ' + fmtET(D.meta.as_of);
}
document.getElementById('mf-off')?.addEventListener('click', () => { try { localStorage.setItem('ws-mf', 'off'); } catch (e) {} mfApply(null); drawAll(false); toast('One page. The front page is in the ? help.'); });
/* ---------- draw everything
   The first screen (masthead, ribbon, ticker, the Wire, the brief) is drawn as soon as the data arrives. Everything below is drawn
   when it comes within a screen of the viewport, and pre-drawn in idle time after that, so a phone is not asked to lay out
   thirty sections of charts before it can show the headline. */
const LAZY_ALL = [
  ['why', [() => drawWhy()]],
  ['record', [(first) => drawTimeline(first && !EMBED)]],
  ['capabilities', [() => drawEdges(), () => drawTNS(), () => drawCapGrid()]],
  ['words', [() => drawQuotes()]],
  ['pattern', [() => drawHooks()]],
  ['charts', [() => { const on = document.querySelector('#chart-tabs button.on'); showChart(on ? on.dataset.pane : 'card-quarters'); }]],
  ['next', [() => drawWatch(), () => drawDrivers(), () => drawForecast(), () => drawCalendar()]],
  ['dives', [() => drawDeepDive()]],
  ['fixes', [() => drawFixes()]],
  ['signals', [() => drawSignals()]],
  ['all', [() => drawList()]],
  ['about', [() => drawContext()]],
];
const LAZY = EMBED ? LAZY_ALL : PAGE === 'wire' ? [] : LAZY_ALL.filter(([sid]) => (sid === 'why') === (PAGE === 'front'));
const drawn = new Set();
// A section that comes within a screen of the viewport is drawn together with everything still undrawn above it, so nothing above the reader ever changes height under them (Safari has no scroll anchoring).
const lazyIO = ('IntersectionObserver' in window) ? new IntersectionObserver((es) => { es.forEach((e) => { if (e.isIntersecting) { if (MF()) drawSection(e.target.id); else drawThrough(e.target.id); } }); }, { rootMargin: '900px 0px' }) : null;
function drawSection(id) {
  const spec = LAZY.find((s) => s[0] === id); if (!spec || !C.scored) return;
  if (!FULL && RECORD_IDS.has(id)) { ensureFull().then(() => drawSection(id)); return; }
  const first = !drawn.has(id); drawn.add(id);
  const sec = document.getElementById(id); if (sec) { sec.classList.remove('pending'); if (lazyIO) lazyIO.unobserve(sec); }
  spec[1].forEach((fn) => { try { fn(first); } catch (err) { console.error(id, err); } });
}
function drawThrough(id) { if (MF()) { drawSection(id); return; } for (const [sid] of LAZY) { if (!drawn.has(sid)) drawSection(sid); if (sid === id) break; } }
function drawEverything() { LAZY.forEach(([sid]) => drawSection(sid)); }
let idleT = null;
function preDraw() {
  if (MF()) return;
  const next = LAZY.find(([sid]) => !drawn.has(sid)); if (!next) return;
  const run = () => { drawSection(next[0]); preDraw(); };
  if (document.hidden) { idleT = setTimeout(preDraw, 2000); return; }
  if ('requestIdleCallback' in window) idleT = requestIdleCallback(run, { timeout: 2500 }); else idleT = setTimeout(run, 200);
}
function drawAll(first) {
  if (MF() && !mfCur) mfApply('front');
  drawSignup(); drawFieldnote(); drawHeadline(); drawRibbon(); drawSinceVisit(); drawTicker(); drawWall(); drawWire(); drawNow(); drawBrief();
  if (MF()) { drawFront(); if (mfCur && mfCur !== 'front') drawSection(mfCur); }
  if (EMBED || !lazyIO) { drawEverything(); return; }
  if (first) {
    LAZY.forEach(([sid]) => { const sec = document.getElementById(sid); if (sec) { sec.classList.add('pending'); lazyIO.observe(sec); } });
    setTimeout(preDraw, 4000); // pre-draw the rest in idle time once the first screen has settled; scrolling draws sooner
  } else { drawn.forEach((sid) => drawSection(sid)); }
}
window.WS.drawAll = () => { if (!C.scored) return false; drawEverything(); return true; };
let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { if (C.scored) { mfSync(); drawAll(false); } }, 160); });
const DATA_ALL = FILES.concat(OPTIONAL);
// The homepage draws from a lean bundle (the Record-only data emptied), then fetches the full one in the background for search and the Record sections.
const LEAN = PAGE === 'front' && !EMBED;
let FULL = !LEAN, fullP = null;
function ensureFull() {
  if (FULL) return Promise.resolve();
  if (!fullP) fullP = fetch('/data/bundle.json?v=' + (window.AII_BUILD || '')).then((r) => r.json()).then((b) => { ['quotes', 'signals', 'timeline', 'implications', 'drivers', 'context', 'horizon'].forEach((f) => { if (b[f]) D[f] = b[f]; }); FULL = true; SIDX = null; if (MF()) drawFront(); }).catch(() => { fullP = null; });
  return fullP;
}
async function loadBundle(url, opts) {
  const r = await fetch(url, opts); if (!r.ok) throw new Error('bundle ' + r.status);
  const b = await r.json(); if (!FILES.every((f) => b[f])) throw new Error('bundle incomplete');
  DATA_ALL.forEach((f) => { D[f] = b[f] || null; });
}
async function loadFiles(suffix, opts) {
  await Promise.all(FILES.map((f) => fetch('/data/' + f + '.json' + suffix, opts).then((r) => { if (!r.ok) throw new Error(f); return r.json(); }).then((j) => { D[f] = j; }))
    .concat(OPTIONAL.map((f) => fetch('/data/' + f + '.json' + suffix, opts).then((r) => r.ok ? r.json() : null).then((j) => { D[f] = j; }).catch(() => { D[f] = null; }))));
}
async function checkForUpdate() {
  try {
    const m = await (await fetch('/data/meta.json?t=' + Date.now(), { cache: 'no-store' })).json();
    if (!D.meta || m.as_of === D.meta.as_of) return;
    try { await loadBundle('/data/bundle.json?t=' + Date.now(), { cache: 'no-store' }); FULL = true; } catch (e) { await loadFiles('?t=' + Date.now(), { cache: 'no-store' }); FULL = true; }
    compute(); SIDX = null; drawAll(false);
    const what = (m.changelog && m.changelog[0] && m.changelog[0].text) || 'new data';
    toastEl.classList.add('wide'); toast('Updated just now: ' + (what.length > 160 ? what.slice(0, 158) + '…' : what)); clearTimeout(toastT); toastT = setTimeout(() => { toastEl.classList.remove('on'); setTimeout(() => toastEl.classList.remove('wide'), 300); }, 9000);
  } catch (e) { /* offline or mid-deploy: try again next time */ }
}
setInterval(checkForUpdate, 5 * 60 * 1000);
(async () => {
  try {
    try { await loadBundle((LEAN ? '/data/bundle-front.json?v=' : '/data/bundle.json?v=') + (window.AII_BUILD || '')); } catch (e) { FULL = true; await loadFiles('?v=' + (window.AII_BUILD || '')); }
    compute(); window.__ready = true;
    if (!FULL) setTimeout(() => ensureFull(), 2500);
    if (EMBED) { embedMode(); } else { drawAll(true); route(); }
  } catch (e) { console.error(e); document.getElementById('headline').textContent = 'The data could not be loaded. Reload the page or try again shortly.'; }
})();
})();
