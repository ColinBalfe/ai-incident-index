// Renders the share card (1200x630) from the live page: node make_og.mjs <url> <out.png>
import { chromium } from 'playwright';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const out = process.argv[3] || new URL('./assets/og.png', import.meta.url).pathname;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 2, colorScheme: 'light', reducedMotion: 'reduce' });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.WS && window.WS.drawAll && window.WS.drawAll(), null, { timeout: 15000 }); await page.waitForTimeout(300);
await page.addStyleTag({ content: `
  #wall-lead, .masthead, .navbar, .sub.chart-note, #lg-autonomy, #hero-share, #hero-stats, main > :not(.hero-band), .drawer, .drawer-bg, .toast { display: none !important; }
  .hero-band { margin-top: 0 !important; }
  html, body { background: #0A111E; overflow: hidden; }
  .hero { padding: 34px 48px 0 !important; max-width: none !important; }
  .hero-band { border: 0 !important; }
  .hl { font-size: 50px !important; max-width: none !important; margin: 0 !important; }
  .sub { font-size: 21px !important; max-width: none !important; margin: 8px 0 0 !important; color: #E9EEF3 !important; }
  .sub b { color: #FF5B3E !important; }
  .hero-chart { margin-top: 6px !important; min-height: 0 !important; }
  .og-foot { position: fixed; left: 48px; right: 48px; bottom: 22px; display: flex; justify-content: space-between; font: 500 18px/1 'Archivo', system-ui, sans-serif; color: #A3AEB9; letter-spacing: -0.01em; }
  .og-foot b { color: #E9EEF3; font-weight: 600; }
` });
await page.evaluate(() => {
  const meta = JSON.parse(document.querySelector('meta[name="description"]').content ? '{}' : '{}');
  const f = document.createElement('div'); f.className = 'og-foot';
  const up = document.getElementById('tb-updated').title.split('.')[0].replace(/^Last refresh /, '');
  f.innerHTML = '<span><b>Warning Shots</b>. See what’s coming. Know what it means.</span><span>Updated ' + up + '</span>';
  document.body.append(f);
  window.dispatchEvent(new Event('resize'));
});
await page.waitForTimeout(700);
await page.evaluate(() => {
  const sub = document.getElementById('sub'); const keep = [];
  for (const node of [...sub.childNodes]) { keep.push(node); if (node.nodeType === 3 && node.textContent.includes('did the acting')) { node.textContent = node.textContent.split('did the acting')[0] + 'did the acting.'; break; } }
  sub.replaceChildren(...keep);
});
await page.waitForTimeout(100);
// The siren card: when the headline wall has a siren, the share card is that story (Drudge's front page is the share).
await page.evaluate(() => {
  const head = document.querySelector('#wall-lead .dl-head'); if (!head || document.getElementById('wall-lead').hidden) return;
  const img = document.querySelector('#wall-lead .dl-hero img');
  const up = document.getElementById('tb-updated').title.split('.')[0].replace(/^Last refresh /, '');
  const c = document.createElement('div'); c.id = 'og-siren';
  const lv = (document.querySelector('#level .lvl-l b') || {}).textContent || '';
  const day = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'short', month: 'short', day: 'numeric' }).format(new Date());
  c.innerHTML = '<div class="bg"></div><div class="shade"></div><div class="tx"><div class="k"><i></i>' + [lv ? "Today's level " + lv : '', day].filter(Boolean).join(' · ') + '</div><div class="h"></div></div><div class="ft"><b>WARNING SHOTS</b><span>See what’s coming. Know what it means · Updated ' + up + '</span></div>';
  if (img) c.querySelector('.bg').style.backgroundImage = 'url(' + img.src + ')';
  c.querySelector('.h').textContent = head.textContent;
  document.body.append(c);
});
await page.addStyleTag({ content: `
  #og-siren { position: fixed; inset: 0; z-index: 99999; background: #0A111E; font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif; }
  #og-siren .bg { position: absolute; inset: 0; background-size: cover; background-position: center; filter: saturate(.85); }
  #og-siren .shade { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10,17,30,.35) 0%, rgba(10,17,30,.72) 45%, rgba(10,17,30,.96) 100%); }
  #og-siren .tx { position: absolute; left: 56px; right: 56px; bottom: 104px; }
  #og-siren .k { display: flex; align-items: center; gap: 12px; color: #FF5B3E; font: 700 20px/1 Arial, sans-serif; letter-spacing: .12em; text-transform: uppercase; }
  #og-siren .k i { width: 16px; height: 16px; border-radius: 50%; background: #FF3300; box-shadow: 0 0 0 6px rgba(255,51,0,.25); }
  #og-siren .h { margin-top: 16px; color: #fff; font-weight: 700; font-size: 76px; line-height: .98; letter-spacing: -0.01em; text-transform: uppercase; text-decoration: underline; text-decoration-thickness: 5px; text-underline-offset: 8px; text-wrap: balance; }
  #og-siren .ft { position: absolute; left: 56px; right: 56px; bottom: 34px; display: flex; justify-content: space-between; align-items: baseline; color: #A8B3C2; font: 500 19px/1 Arial, sans-serif; border-top: 1px solid rgba(255,255,255,.18); padding-top: 18px; }
  #og-siren .ft b { color: #fff; font-size: 24px; letter-spacing: .16em; font-family: 'Playfair', Georgia, serif; font-weight: 700; }
` });
await page.waitForTimeout(500);
await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1200, height: 630 } });
await browser.close(); console.log('og written', out);
