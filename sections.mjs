import { chromium } from 'playwright';
const url = process.argv[2] || 'http://127.0.0.1:8765/index.html';
const out = 'shots/sec';
const width = +(process.argv[3] || 1280);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce' });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: 'networkidle' }); await page.waitForTimeout(600);
for (const id of (process.argv[4] || 'now,pattern,escalation,danger,pipeline,next,dives,signals,all,context,method').split(',')) {
  const h = await page.locator('#' + id); await h.scrollIntoViewIfNeeded(); await page.waitForTimeout(150);
  await h.screenshot({ path: `${out}-${width}-${id}.png` });
}
await browser.close(); console.log('ok');
