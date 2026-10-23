// Renders the share card (1200x630) from the live page: node make_og.mjs <url> <out.png>
import { chromium } from 'playwright';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const out = process.argv[3] || new URL('./assets/og.png', import.meta.url).pathname;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 2, colorScheme: 'light', reducedMotion: 'reduce' });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle' });
await page.addStyleTag({ content: `
  .topbar, .sub, #lg-autonomy, #hero-share, #hero-stats, main > :not(.hero), .drawer, .drawer-bg, .toast { display: none !important; }
  html, body { background: #F2F4F6; overflow: hidden; }
  .hero { padding: 34px 48px 0 !important; max-width: none !important; }
  .hl { font-size: 46px !important; max-width: none !important; margin: 0 !important; }
  .hero-chart { margin-top: 12px !important; min-height: 0 !important; }
  .og-foot { position: fixed; left: 48px; right: 48px; bottom: 22px; display: flex; justify-content: space-between; font: 500 18px/1 'Archivo', system-ui, sans-serif; color: #55616E; letter-spacing: -0.01em; }
  .og-foot b { color: #141A21; font-weight: 600; }
` });
await page.evaluate(() => {
  const meta = JSON.parse(document.querySelector('meta[name="description"]').content ? '{}' : '{}');
  const f = document.createElement('div'); f.className = 'og-foot';
  const up = document.getElementById('tb-updated').title.split('.')[0];
  f.innerHTML = '<span><b>Warning Shots</b>: the AI Incident Index. Every major incident since 2023, scored and sourced</span><span>Updated ' + up + '</span>';
  document.body.append(f);
  window.dispatchEvent(new Event('resize'));
});
await page.waitForTimeout(700);
await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1200, height: 630 } });
await browser.close(); console.log('og written', out);
