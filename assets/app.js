/* The AI Incident Index — page script. Data lives in ./data/*.json; see build/ for how it is produced. */
(() => {
'use strict';
const SITE = (window.AII_SITE && window.AII_SITE.startsWith('http')) ? window.AII_SITE : location.href.split('#')[0];
const FILES = ['incidents', 'forecasts', 'pipeline', 'drivers', 'context', 'catalysts', 'horizon', 'deepdives', 'victims', 'timeline', 'implications', 'signals', 'live', 'watch', 'meta'];
const OPTIONAL = ['quotes', 'brief', 'news'];
const EMBED = new URLSearchParams(location.search).get('embed');
const D = {};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- theme */
const root = document.documentElement;
try { const t = localStorage.getItem('aii-theme'); if (t) root.dataset.theme = t; } catch (e) {}
document.getElementById('theme').addEventListener('click', () => {
  const dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme = dark ? 'light' : 'dark';
  try { localStorage.setItem('aii-theme', root.dataset.theme); } catch (e) {}
  drawAll(false);
});

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
function shareRow(node, o) {
  if (!node) return;
  node.replaceChildren();
  const link = SITE + (o.anchor ? '#' + o.anchor : '');
  const mk = (icon, label, fn) => { const b = el('button'); b.type = 'button'; b.innerHTML = ICON[icon]; b.append(txt(' ' + label)); b.addEventListener('click', (e) => { e.stopPropagation(); fn(); }); return b; };
  node.append(mk('link', 'Copy link', () => copy(link)));
  if (o.text) node.append(mk('text', 'Copy text', () => copy(o.text + ' ' + link)));
  if (o.text) { const a = el('a'); a.innerHTML = ICON.x; a.append(txt(' Post on X')); a.href = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(o.text) + '&url=' + encodeURIComponent(link); a.target = '_blank'; a.rel = 'noopener noreferrer'; node.append(a); }
  if (o.svgBox) node.append(mk('img', 'Save image', () => svgToPng(o.svgBox, o.name || 'chart', o.title || '')));
  if (o.embed) node.append(mk('embed', 'Embed', () => copy(`<iframe src="${SITE}?embed=${o.embed}" width="100%" height="${o.embedH || 560}" style="border:0;max-width:100%" loading="lazy" title="${(o.title || 'Warning Shots').replace(/"/g, '')}"></iframe>`)));
}
let fontB64 = null;
async function fontData() {
  if (fontB64 !== null) return fontB64;
  try { const b = await (await fetch('assets/fonts/archivo-latin-standard-normal.woff2')).arrayBuffer(); let s = ''; const u = new Uint8Array(b); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); fontB64 = btoa(s); }
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
  if (f) out.append('style').text(`@font-face{font-family:'Archivo';src:url(data:font/woff2;base64,${f}) format('woff2');font-weight:100 900;font-stretch:62% 125%;} text{font-family:'Archivo',system-ui,sans-serif}`);
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
  shareRow(document.getElementById('hero-share'), { anchor: 'top', text: `AI has started breaking in on its own. Severe AI incidents went from ${h.severe_prior12} to ${h.severe_last12} in a year; in ${pct(h.agentic_recent)} of this year's real-world cases the AI itself did the acting. Warning Shots:`, svgBox: document.getElementById('ch-timeline'), name: 'escalation', title: `Every major AI incident since 2023, scored 0–100 (severe: ${h.severe_prior12} → ${h.severe_last12} in a year)`, embed: 'timeline', embedH: 560 });
  const up = document.getElementById('tb-updated');
  const tickUp = () => { const ms = Date.now() - Date.parse(D.meta.as_of); const mins = Math.max(0, Math.round(ms / 6e4)); const nx = D.meta.next_check ? Date.parse(D.meta.next_check) - Date.now() : null; const nxs = nx != null && nx > 0 ? ', next check in ' + (nx > 3.6e6 ? Math.floor(nx / 3.6e6) + 'h ' + Math.round((nx % 3.6e6) / 6e4) + 'm' : Math.max(1, Math.round(nx / 6e4)) + ' min') : (nx != null ? ', refresh due' : ''); up.textContent = (mins < 60 ? 'Updated ' + mins + ' min ago' : 'Updated ' + relTime(D.meta.as_of)) + (window.innerWidth > 1100 ? nxs : ''); up.title = 'Last refresh ' + fmtET(D.meta.as_of) + '. ' + D.meta.schedule; };
  tickUp(); clearInterval(window._tickUp); window._tickUp = setInterval(tickUp, 30000);
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
    heroAnimated = true;
    const T = 2600, x0 = x.range()[0], x1 = x(today);
    const sweep = svg.append('line').attr('y1', m.t).attr('y2', H - m.b).attr('stroke', 'var(--alarm)').attr('stroke-width', 1.5).attr('x1', x0).attr('x2', x0).attr('opacity', 0.9);
    dots.attr('r', 0);
    dots.transition().delay((r) => T * (Math.min(x(r._d), x1) - x0) / (x1 - x0)).duration(420).ease(d3.easeBackOut.overshoot(2.2)).attr('r', rOf);
    yc.attr('opacity', 0).transition().delay(T + 200).duration(500).attr('opacity', 1);
    const L = path.node().getTotalLength(); path.attr('stroke-dasharray', L + ' ' + L).attr('stroke-dashoffset', L).transition().delay(T * (x(pts[0][0]) - x0) / (x1 - x0)).duration(T * (x(pts[pts.length - 1][0]) - x(pts[0][0])) / (x1 - x0)).ease(d3.easeLinear).attr('stroke-dashoffset', 0);
    lab.attr('opacity', 0).transition().delay(T + 200).duration(500).attr('opacity', 1);
    sweep.transition().duration(T).ease(d3.easeLinear).attr('x1', x1).attr('x2', x1).transition().duration(600).attr('opacity', 0).remove();
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
  document.getElementById('now-link').href = '#d=' + live.incident_id;
  document.getElementById('now-link').textContent = 'Full breakdown: every organization, the map, the timeline';
  const grid = document.getElementById('live-grid');
  const since = D.meta.live_since ? Date.parse(D.meta.live_since) : null;
  const clock = since ? (() => { const c = el('div', 'live clock'); const v = el('div', 'v'); const upd = () => { const ms = Date.now() - since; const h = Math.floor(ms / 3.6e6), mn = Math.floor((ms % 3.6e6) / 6e4), sc = Math.floor((ms % 6e4) / 1000); v.textContent = h + 'h ' + String(mn).padStart(2, '0') + 'm ' + String(sc).padStart(2, '0') + 's'; }; upd(); clearInterval(window._liveClock); window._liveClock = setInterval(upd, 1000); c.append(v, el('div', 'l', D.meta.live_since_label || 'since the fix shipped')); c.append(el('div', 'd', 'Counting from the coordinated release. The gap between a patch and a working exploit is now measured in hours.')); return c; })() : null;
  grid.replaceChildren(...(clock ? [clock] : []), ...D.live.map((r) => {
    const good = (r.key === 'confirmed' && r.value === '0') || (r.key === 'kev' && /not/i.test(r.value));
    const c = el('div', 'live' + (good ? ' ok' : ''));
    const v = el('div', 'v'); countUp(v, r.value, 'live:' + r.key); c.append(v, el('div', 'l', r.label));
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
  if (!world) { try { world = await (await fetch('assets/vendor/countries-110m.json')).json(); } catch (e) { fail(box); return; } }
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
const TOPIC = { php2shell: 'PHP2Shell', 'ai-attack': 'AI-driven attacks', 'ai-incident': 'AI incidents', regulation: 'Governments & regulators', deepfakes: 'Deepfakes', 'chatbot-harm': 'Chatbot harm', breakthrough: 'Breakthroughs', other: 'Other' };
const KIND = { breaking: 'Breaking', official: 'Official', analysis: 'Analysis' };
const wire = { topic: 'all', open: false };
const ageShort = (n) => { if (!n.published) return ''; const d = new Date(n.published); if (isNaN(d)) return ''; if (n.time_known === false) return ETd.format(d); const ms = Date.now() - d; const h = ms / 3.6e6; if (h < 1) return 'just now'; if (h < 24) return Math.floor(h) + 'h ago'; if (h < 72) return Math.floor(h / 24) + 'd ago'; return ETd.format(d); };
const SIREN_SVG = '<svg class="siren-ic" viewBox="0 0 34 34" aria-hidden="true"><path class="dome" d="M8 25a9 9 0 0 1 18 0z"/><ellipse class="glass" cx="13.5" cy="19" rx="2.6" ry="3.6" transform="rotate(-30 13.5 19)"/><rect class="base" x="5" y="25" width="24" height="4" rx="1.5"/><path class="ray" d="M17 4.5v4.5"/><path class="ray" d="M8.5 7.5l3 3.3"/><path class="ray" d="M25.5 7.5l-3 3.3"/><path class="ray" d="M3.5 17h4"/><path class="ray" d="M26.5 17h4"/></svg>';
function newsItems() { return (D.news || []).filter((n) => n && n.title && n.url).slice().sort((a, b) => String(b.published || '').localeCompare(String(a.published || ''))); }
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
  sirenBox.replaceChildren(ic.firstChild, st, sm, ...(siren.summary ? [el('p', 'siren-s', siren.summary)] : []));
  const rest = items.filter((n) => n !== siren);
  const topics = d3.rollups(rest, (v) => v.length, (n) => n.topic || 'other').sort((a, b) => b[1] - a[1]);
  if (!topics.find((t) => t[0] === wire.topic)) wire.topic = 'all';
  const chip = (k, label, n) => { const b = el('button', k === wire.topic ? 'on' : ''); b.type = 'button'; b.append(txt(label), el('b', null, String(n))); b.addEventListener('click', () => { wire.topic = k; drawWire(); }); return b; };
  chips.replaceChildren(chip('all', 'All', rest.length), ...topics.filter((t) => t[1] >= 1).map(([k, n]) => chip(k, TOPIC[k] || k, n)));
  const rows = rest.filter((n) => wire.topic === 'all' || (n.topic || 'other') === wire.topic);
  const limit = (wire.open || wire.topic !== 'all') ? rows.length : (window.innerWidth < 760 ? 12 : 40);
  const fresh = (n) => n.published && (Date.parse(D.meta.as_of) - Date.parse(n.published)) < 8 * 3.6e6;
  board.replaceChildren(...rows.slice(0, limit).map((n) => {
    const it = el('div', 'wi');
    const a = el('a', 'wi-t'); a.href = n.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; if (fresh(n)) a.append(el('i', 'nd')); a.append(txt(n.title));
    const m = el('div', 'wi-m'); const hours = n.published ? (Date.now() - Date.parse(n.published)) / 3.6e6 : 99; const k = n.kind === 'breaking' && hours >= 24 ? null : KIND[n.kind]; if (k) m.append(el('span', 'kind ' + n.kind, k)); m.append(el('b', null, n.outlet || ''), el('span', 'ag', ageShort(n)));
    if ((n.also || []).length) { const also = el('span', 'also'); also.append(txt('also ')); n.also.slice(0, 2).forEach((x, i) => { const l = el('a', null, x.outlet); l.href = x.url; l.target = '_blank'; l.rel = 'noopener noreferrer'; if (i) also.append(txt(', ')); also.append(l); }); m.append(also); }
    it.append(a, m); if (n.summary) it.append(el('div', 'wi-s', n.summary)); it.title = n.summary || ''; return it;
  }));
  const span = d3.extent(items, (n) => n.published);
  const hours = span[0] && span[1] ? Math.round((Date.parse(span[1]) - Date.parse(span[0])) / 3.6e6) : 0;
  cnt.textContent = items.length + ' reports from the last ' + (hours >= 48 ? Math.round(hours / 24) + ' days' : hours + ' hours') + ', newest first. Every headline links to the outlet.';
  more.replaceChildren();
  if (rows.length > limit) { const b = el('button', 'more-btn', 'Show all ' + rows.length + ' stories'); b.type = 'button'; b.addEventListener('click', () => { wire.open = true; drawWire(); }); more.append(b); }
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
let fcOpen = false;
function drawForecast() {
  const box = document.getElementById('forecast-list'), more = document.getElementById('forecast-more');
  const groups = d3.groups(D.forecasts, (r) => r.horizon).sort((a, b) => +a[1][0].horizon_months - +b[1][0].horizon_months);
  const LIMIT = 20; let shown = 0;
  box.replaceChildren(...groups.map(([hz, items]) => {
    const g = el('div', 'fc-group'); g.append(el('div', 'fc-ghead', hz + ', by ' + fmtDate(new Date(items[0].resolve_by))));
    items.slice().sort((a, b) => +b.probability - +a.probability).forEach((r) => {
      if (!fcOpen && shown >= LIMIT) return; shown++;
      const row = el('div', 'fc'); row.tabIndex = 0; row.id = 'fc-' + r.id;
      const bar = el('div', 'fc-bar'), track = el('div', 'fc-track'), fill = el('div', 'fc-fill'); const p = +r.probability; fill.style.width = (p * 100) + '%'; fill.style.background = p >= 0.5 ? 'var(--alarm)' : 'color-mix(in oklab, var(--alarm) 50%, var(--line-2))'; track.append(fill);
      bar.append(track, el('span', 'fc-pct', r.probability_label));
      const more = el('div', 'fc-more'); const b1 = el('div'); b1.append(el('b', null, 'Why: '), txt(r.basis)); const b2 = el('div'); b2.style.marginTop = '4px'; b2.append(el('b', null, 'Watch for: '), txt(r.signposts)); more.append(b1, b2);
      row.append(el('div', 'fc-event', r.event), bar, more);
      const toggle = () => row.classList.toggle('open');
      row.addEventListener('click', toggle); row.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
      g.append(row);
    });
    return g;
  }).filter((g) => g.children.length > 1));
  more.replaceChildren();
  if (D.forecasts.length > LIMIT) { const b = el('button', 'more-btn', fcOpen ? 'Show fewer' : 'Show all ' + D.forecasts.length + ' forecasts'); b.type = 'button'; b.addEventListener('click', () => { fcOpen = !fcOpen; drawForecast(); }); more.append(b); }
  const top = D.forecasts.slice().sort((a, b) => +b.probability - +a.probability)[0];
  shareRow(document.getElementById('share-forecast'), { anchor: 'card-forecast', text: `Twenty dated forecasts for AI safety over the next year, each with its reasoning. Highest: ${top.probability_label} that ${top.event.charAt(0).toLowerCase() + top.event.slice(1)}. Warning Shots:` });
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
const dd = { id: null, vfilter: 'all' };
const VSTAT = { confirmed: 'var(--alarm)', reported: 'color-mix(in oklab, var(--alarm) 50%, var(--paper))', attacked: 'var(--amber)', disrupted: 'var(--steel)', other: 'var(--line-2)', unnamed: 'var(--line-2)' };
function drawDeepDive() {
  const dds = D.deepdives.slice().sort((a, b) => +a.order - +b.order);
  if (!dd.id || !dds.find((d) => d.incident_id === dd.id)) dd.id = dds[0].incident_id;
  document.getElementById('dd-tabs').replaceChildren(...dds.map((d) => { const b = el('button', d.incident_id === dd.id ? 'on' : ''); b.id = 'dd-' + d.incident_id; b.setAttribute('role', 'tab'); b.setAttribute('aria-selected', String(d.incident_id === dd.id)); if (d.status === 'active') b.append(el('i')); b.append(txt(d.tab_label)); b.addEventListener('click', () => { dd.id = d.incident_id; dd.vfilter = 'all'; document.querySelectorAll('#seg-vstatus button').forEach((x) => x.classList.toggle('on', x.dataset.v === 'all')); history.replaceState(null, '', '#d=' + d.incident_id); drawDeepDive(); }); return b; }));
  const d = dds.find((x) => x.incident_id === dd.id);
  const h = el('h3'); h.append(txt(d.name), el('span', 'status' + (d.status === 'active' ? ' active' : ''), d.status_label));
  const rel = el('div', 'dd-rel');
  const relRows = String(d.related_ids || '').split(',').map((s) => s.trim()).map((id) => C.scored.find((r) => r.id === id)).filter(Boolean);
  if (relRows.length) { rel.append(el('span', 'lbl', relRows.length > 1 ? 'Scored on the index:' : 'Score on the index:')); relRows.forEach((r) => { const b = el('button', 'relchip'); b.type = 'button'; const sc = el('b', null, String(r.severity)); sc.style.color = tierColor(r.tier); b.append(sc, el('span', null, r.title)); b.addEventListener('click', () => openIncident(r.id)); rel.append(b); }); }
  const dq = (D.quotes || []).filter((q) => q.incident_id === d.incident_id && q.quote && q.verified !== false).sort((a, b) => (b.weight || 0) - (a.weight || 0)).slice(0, 2).map((q) => { const w = el('div', 'dd-quote'); const who = el('div', 'who'); who.append(el('b', null, q.speaker), txt(q.title ? ', ' + q.title : ''), txt(', ' + fmtDate(new Date(q.date)) + ' ')); const a = el('a', null, 'source'); a.href = q.url; a.target = '_blank'; a.rel = 'noopener noreferrer'; who.append(a); w.append(el('blockquote', null, q.quote), who); return w; });
  document.getElementById('dd-head').replaceChildren(h, el('p', 'dd-meta', d.dates_label), el('p', 'dd-one', d.one_liner), ...dq, rel);
  shareRow(document.getElementById('dd-share'), { anchor: 'd=' + d.incident_id, text: d.name + '. ' + d.one_liner.split('. ')[0] + '. Warning Shots:' });
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
  document.getElementById('dd-timeline').replaceChildren(...tl.map((t) => { const it = el('div', 'tl-item'); const sp = el('span', null, t.event); if (t.source_url) { const a = el('a', null, 'source'); a.href = t.source_url; a.target = '_blank'; a.rel = 'noopener noreferrer'; sp.append(a); } it.append(el('b', null, t.date_label || fmtDate(new Date(t.date))), sp); return it; }));
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
  cnt.textContent = all.length ? `Showing ${rows.length} of ${all.length} entries` : '';
  box.replaceChildren(...rows.map((v) => {
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
const sigColor = (g) => g === 'agency' ? 'var(--steel)' : g === 'gov' ? 'var(--indigo)' : 'var(--lab)';
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
  const pill = el('span', 'pill'); const pd = el('i'); pd.style.background = tierColor(r.tier); pill.append(pd, txt(r.tier)); big.append(pill);
  const h = el('h3', null, r.title);
  const meta = el('div', 'dmeta', [showDate(r), r.actors, r.category_label, r.setting === 'wild' ? 'in the wild' : 'in the lab'].filter(Boolean).join(', '));
  const share = el('div', 'share');
  body.replaceChildren(big, h, meta, ...detailNodes(r, true), share);
  shareRow(share, { anchor: 'i=' + r.id, text: `${r.title} (${r.severity}/100, ${r.tier.toLowerCase()}). ${r.summary.split('. ')[0]}. Warning Shots:` });
  document.getElementById('drawer').classList.add('on'); document.getElementById('drawer').setAttribute('aria-hidden', 'false'); document.getElementById('drawer-bg').classList.add('on');
  history.replaceState(null, '', '#i=' + r.id);
  document.getElementById('drawer-close').focus();
}
function closeDrawer() { document.getElementById('drawer').classList.remove('on'); document.getElementById('drawer').setAttribute('aria-hidden', 'true'); document.getElementById('drawer-bg').classList.remove('on'); if (location.hash.startsWith('#i=')) history.replaceState(null, '', location.pathname + location.search); }
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
    const mid = el('div'); const rt_ = el('div', 'rtitle', r.title); if (isNew(r.disclosed || r.date)) rt_.append(el('span', 'new-tag', 'new')); mid.append(rt_, el('div', 'rmeta', ['#' + rank.get(r.id), showDate(r), r.actors, r.category_label, r.setting === 'wild' ? 'in the wild' : 'in the lab'].filter(Boolean).join(', ')));
    const pill = el('span', 'pill'); const pd = el('i'); pd.style.background = tierColor(r.tier); pill.append(pd, txt(r.tier));
    const det = el('div', 'rdetail'); det.append(...detailNodes(r, false)); const sh = el('div', 'share'); shareRow(sh, { anchor: 'i=' + r.id, text: `${r.title} (${r.severity}/100, ${r.tier.toLowerCase()}). Warning Shots:` }); det.append(sh);
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
  const targets = { timeline: ['ch-timeline', 'lg-autonomy', 'hero-share'], now: ['now'], wire: ['siren', 'wire-board'], quarters: ['card-quarters'], disclosure: ['card-disclosure'], scatter: ['card-scatter'], horizon: ['card-horizon'], pipeline: ['card-pipeline'], words: ['quotes'], brief: ['brief'] };
  const ids = targets[EMBED] || targets.timeline;
  const host = el('div', 'embed-host wrap');
  if (EMBED === 'timeline') { const p = el('div', 'panel'); const t = el('div', 'panel-title'); t.append(txt('AI has started breaking in on its own: severe incidents went from '), el('b', null, String(C.headline.severe_prior12)), txt(' to '), el('b', null, String(C.headline.severe_last12)), txt(' in a year')); p.append(t, el('div', 'panel-note', 'Every major AI incident since 2023, scored 0–100. The stronger a dot’s color, the more the AI did on its own.')); ids.forEach((id) => { const n = document.getElementById(id); if (n) p.append(n); }); host.append(p); }
  else ids.forEach((id) => { const n = document.getElementById(id); if (n) { n.hidden = false; host.append(n); } });
  const f = el('div', 'embed-foot'); const a = el('a', null, 'Warning Shots, the AI Incident Index'); a.href = SITE; a.target = '_blank'; a.rel = 'noopener'; f.append(a, el('span', null, 'Updated ' + fmtET(D.meta.as_of))); host.append(f);
  document.querySelector('main').append(host);
  setTimeout(() => drawAll(false), 50);
}

/* ---------- chart tabs */
const CHART_DRAW = { 'card-quarters': () => drawQuarters(), 'card-disclosure': () => drawDisclosure(), 'card-scatter': () => drawScatter(), 'card-horizon': () => drawHorizon(), 'card-pipeline': () => drawPipeline() };
function showChart(id) {
  if (!CHART_DRAW[id]) return;
  document.querySelectorAll('#chart-panes > .pane').forEach((p) => { p.hidden = p.id !== id; });
  document.querySelectorAll('#chart-tabs button').forEach((b) => { const on = b.dataset.pane === id; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); });
  if (C.scored) CHART_DRAW[id]();
}
document.getElementById('chart-tabs').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) showChart(b.dataset.pane); });
const ALIAS = { escalation: 'charts', danger: 'charts', pipeline: 'charts', method: 'about', context: 'about', brief: 'wire' };

/* ---------- routing */
function go(hash) { location.hash = hash; route(); }
function route() {
  let h = location.hash.slice(1);
  if (ALIAS[h]) h = ALIAS[h];
  if (CHART_DRAW[h]) { showChart(h); document.getElementById('charts').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); return; }
  if (h.startsWith('i=')) { openIncident(decodeURIComponent(h.slice(2))); return; }
  if (h.startsWith('q=')) { const n = document.getElementById('q-' + decodeURIComponent(h.slice(2))); if (n) { quotesOpen = true; drawQuotes(); document.getElementById('q-' + decodeURIComponent(h.slice(2)))?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' }); } return; }
  if (h.startsWith('d=')) { const id = decodeURIComponent(h.slice(2)); if (D.deepdives.find((d) => d.incident_id === id)) { dd.id = id; dd.vfilter = 'all'; drawDeepDive(); document.getElementById('dives').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' }); } return; }
  const n = h && document.getElementById(h); if (n) n.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
}
window.addEventListener('hashchange', route);
document.querySelectorAll('a[href^="#"]').forEach((a) => a.addEventListener('click', (e) => { const h = a.getAttribute('href'); if (h.length < 2) return; e.preventDefault(); history.replaceState(null, '', h); route(); }));

/* ---------- draw everything */
function drawAll(first) {
  drawHeadline(); drawTimeline(first && !EMBED); drawTicker(); drawWire(); drawNow(); drawBrief(); drawQuotes(); drawHooks(); drawQuarters(); drawDisclosure(); drawScatter(); drawHorizon(); drawPipeline(); drawWatch(); drawDrivers(); drawForecast(); drawCalendar(); drawDeepDive(); drawSignals(); drawList(); drawContext();
}
let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { if (C.scored) drawAll(false); }, 160); });
async function checkForUpdate() {
  try {
    const m = await (await fetch('data/meta.json?t=' + Date.now(), { cache: 'no-store' })).json();
    if (!D.meta || m.as_of === D.meta.as_of) return;
    await Promise.all(FILES.concat(OPTIONAL).map((f) => fetch('data/' + f + '.json?t=' + Date.now(), { cache: 'no-store' }).then((r) => r.ok ? r.json() : null).then((j) => { if (j) D[f] = j; }).catch(() => {})));
    compute(); drawAll(false);
    const what = (m.changelog && m.changelog[0] && m.changelog[0].text) || 'new data';
    toastEl.classList.add('wide'); toast('Updated just now: ' + (what.length > 160 ? what.slice(0, 158) + '…' : what)); clearTimeout(toastT); toastT = setTimeout(() => { toastEl.classList.remove('on'); setTimeout(() => toastEl.classList.remove('wide'), 300); }, 9000);
  } catch (e) { /* offline or mid-deploy: try again next time */ }
}
setInterval(checkForUpdate, 5 * 60 * 1000);
Promise.all(FILES.map((f) => fetch('data/' + f + '.json?v=' + (window.AII_BUILD || '')).then((r) => { if (!r.ok) throw new Error(f); return r.json(); }).then((j) => { D[f] = j; }))
  .concat(OPTIONAL.map((f) => fetch('data/' + f + '.json?v=' + (window.AII_BUILD || '')).then((r) => r.ok ? r.json() : null).then((j) => { D[f] = j; }).catch(() => { D[f] = null; }))))
  .then(() => { compute(); if (EMBED) { embedMode(); } else { drawAll(true); route(); } })
  .catch((e) => { console.error(e); document.getElementById('headline').textContent = 'The data could not be loaded. Reload the page or try again shortly.'; });
})();
