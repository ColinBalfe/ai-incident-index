// QA renderer: node shot.mjs [url] [out-prefix] — captures desktop + phone screenshots and prints console errors.
import { chromium } from 'playwright';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const out = process.argv[3] || 'shots/site';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
for (const [name, vp, dark] of [['desktop', { width: 1280, height: 900 }, false], ['phone', { width: 390, height: 844 }, false], ['desktop-dark', { width: 1280, height: 900 }, true]]) {
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, colorScheme: dark ? 'dark' : 'light', reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  const errs = [];
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${out}-${name}-top.png`, fullPage: false });
  await page.screenshot({ path: `${out}-${name}-full.png`, fullPage: true });
  const h = await page.evaluate(() => document.body.scrollHeight);
  console.log(name, 'height', h, 'errors', errs.length ? errs : 'none');
  await ctx.close();
}
await browser.close();
