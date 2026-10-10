const puppeteer = require('puppeteer-core');
const path = require('path');

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const APP_URL = 'http://localhost:5173';
const ARTIFACTS_DIR = path.resolve(__dirname, '../artifacts/e2e_live_test');

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function capture() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    defaultViewport: { width: 1440, height: 960 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.goto(APP_URL, { waitUntil: 'networkidle0' });

  // 1. Enter plot & generate
  await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 10000 });
  const plotInput = await page.$('[data-testid="input-plot-area"]');
  await plotInput.click({ clickCount: 3 });
  await plotInput.type('1500');
  await sleep(300);

  await page.click('[data-testid="btn-check-land"]');
  await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 10000 });
  await page.click('[data-testid="btn-see-what-you-can-build"]');

  await page.waitForSelector('[data-testid="btn-design-my-home"]', { timeout: 10000 });
  await page.click('[data-testid="btn-design-my-home"]');

  await page.waitForSelector('[data-testid="btn-generate-home-options"]', { timeout: 10000 });
  await page.click('[data-testid="btn-generate-home-options"]');

  await page.waitForSelector('[data-testid="btn-choose-design-0"]', { timeout: 25000 });

  // 2. Click "Choose This Design" to advance to COST
  await page.click('[data-testid="btn-choose-design-0"]');
  await sleep(1000);
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '11_cost_summary.png') });
  console.log('Saved 11_cost_summary.png');

  // 3. Click "Proceed to Build Lock" or advance to BUILD
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent && (b.textContent.includes('Proceed') || b.textContent.includes('Lock')));
    if (btn) btn.click();
  });
  await sleep(1000);
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '12_build_review.png') });
  console.log('Saved 12_build_review.png');

  // 4. Switch to Professional Mode
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const profBtn = btns.find(b => b.textContent && b.textContent.includes('Professional Mode'));
    if (profBtn) profBtn.click();
  });
  await sleep(1000);
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '13_engineer_review.png') });
  console.log('Saved 13_engineer_review.png');

  await browser.close();
  console.log('All remaining screenshots captured successfully!');
}

capture().catch(err => {
  console.error('Capture error:', err);
  process.exit(1);
});
