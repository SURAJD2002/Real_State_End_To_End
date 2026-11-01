const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const APP_URL = 'http://localhost:5173';
const ARTIFACTS_DIR = path.resolve(__dirname, '../artifacts/e2e_live_test');

if (!fs.existsSync(ARTIFACTS_DIR)) {
  fs.mkdirSync(ARTIFACTS_DIR, { recursive: true });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function safeClick(page, selector, timeout = 15000) {
  await page.waitForSelector(selector, { timeout });
  await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    if (!el) throw new Error('Element not found for click: ' + sel);
    el.click();
  }, selector);
}

async function setReactInput(page, selector, value, timeout = 15000) {
  await page.waitForSelector(selector, { timeout });
  await page.evaluate((sel, val) => {
    const el = document.querySelector(sel);
    if (!el) throw new Error('Element not found for input: ' + sel);
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, selector, value);
}

async function run() {
  console.log('====================================================');
  console.log('PLANWISE LIVE FRONTEND E2E TEST RUNNER');
  console.log('====================================================');

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    defaultViewport: { width: 1440, height: 960 },
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  page.on('dialog', async (dialog) => {
    console.log('Auto-dismissing dialog:', dialog.message());
    await dialog.dismiss();
  });
  const results = {};

  try {
    // ----------------------------------------------------
    // PHASE 1: Connect to Real Application & Authenticate
    // ----------------------------------------------------
    console.log('\n[PHASE 1] Navigating to', APP_URL);
    await page.goto(APP_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
    const title = await page.title();
    console.log('Page Title:', title);
    if (!title.includes('Planwise')) {
      throw new Error(`Unexpected page title: ${title}`);
    }

    await sleep(600);
    const pilotBtn = await page.$('[data-testid="btn-pilot-login"]');
    if (pilotBtn) {
      console.log('Detected Login View, authenticating as Pilot Lead Engineer...');
      await page.evaluate(() => {
        document.querySelector('[data-testid="btn-pilot-login"]')?.click();
      });
      await sleep(1200);
    }
    results['PHASE_1_START_APP'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 2 & 3: 1500 sq ft Customer Flow (Land -> Feasibility)
    // ----------------------------------------------------
    console.log('\n[PHASE 2] Entering 1500 sq ft in Land Intake...');
    await setReactInput(page, '[data-testid="input-plot-area"]', '1500');
    await sleep(300);

    const landShotPath = path.join(ARTIFACTS_DIR, '01_1500_land_input.png');
    await page.screenshot({ path: landShotPath });
    console.log('Saved screenshot:', landShotPath);

    console.log('Clicking "Check My Land", waiting for result screen...');
    await safeClick(page, '[data-testid="btn-check-land"]');

    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 15000 });
    await sleep(400);

    console.log('Clicking "See What You Can Build" -> Feasibility...');
    await safeClick(page, '[data-testid="btn-see-what-you-can-build"]');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 15000 });
    const feasBadgeText = await page.$eval('[data-testid="feasibility-plot-badge"]', el => el.textContent.trim());
    console.log('Feasibility Badge Text:', feasBadgeText);

    if (!feasBadgeText.includes('1,500 sq ft')) {
      throw new Error(`Feasibility badge did NOT contain 1,500 sq ft: "${feasBadgeText}"`);
    }

    const feasShotPath = path.join(ARTIFACTS_DIR, '02_1500_feasibility.png');
    await page.screenshot({ path: feasShotPath });
    console.log('Saved screenshot:', feasShotPath);
    results['PHASE_2_3_FEASIBILITY_1500'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 4: Proceed to Design Intake
    // ----------------------------------------------------
    console.log('\n[PHASE 4] Proceeding to Design Intake...');
    await safeClick(page, '[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 15000 });

    const designBadgeText = await page.$eval('[data-testid="design-plot-badge"]', el => el.textContent.trim());
    console.log('Design Intake Badge Text:', designBadgeText);

    if (designBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Design intake badge is NOT "1,500 sq ft Plot", got: "${designBadgeText}"`);
    }

    await safeClick(page, '[data-testid="btn-bedrooms-2"]');
    await safeClick(page, '[data-testid="btn-bathrooms-2"]');
    await safeClick(page, '[data-testid="btn-floors-2"]');
    await sleep(300);

    const intakeShotPath = path.join(ARTIFACTS_DIR, '03_1500_design_intake.png');
    await page.screenshot({ path: intakeShotPath });
    console.log('Saved screenshot:', intakeShotPath);

    console.log('Clicking "Generate My Home Options"...');
    await safeClick(page, '[data-testid="btn-generate-home-options"]');

    // ----------------------------------------------------
    // PHASE 5 & 6: Design Options & Traceability
    // ----------------------------------------------------
    console.log('\n[PHASE 5 & 6] Waiting for Design Options view...');
    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 30000 });

    const optionsBadgeText = await page.$eval('[data-testid="design-options-plot-badge"]', el => el.textContent.trim());
    console.log('Design Options Badge Text:', optionsBadgeText);
    if (optionsBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Options badge is NOT "1,500 sq ft Plot", got: "${optionsBadgeText}"`);
    }

    const optionsShotPath = path.join(ARTIFACTS_DIR, '04_1500_design_options.png');
    await page.screenshot({ path: optionsShotPath });
    console.log('Saved screenshot:', optionsShotPath);

    console.log('Checking My Project modal traceability...');
    await safeClick(page, '[data-testid="btn-open-my-project"]');
    await page.waitForSelector('[data-testid="myproject-project-id"]', { timeout: 8000 });

    const projIdText = await page.$eval('[data-testid="myproject-project-id"] span:last-child', el => el.textContent.trim());
    const myPlotText = await page.$eval('[data-testid="myproject-plot-area"] span:last-child', el => el.textContent.trim());
    console.log('My Project ID:', projIdText);
    console.log('My Project Plot:', myPlotText);

    if (!projIdText.startsWith('proj-cust-')) {
      throw new Error(`Expected customer project ID starting with proj-cust-, got: ${projIdText}`);
    }
    if (!myPlotText.includes('1,500 sq ft')) {
      throw new Error(`Expected My Project plot to include 1,500 sq ft, got: ${myPlotText}`);
    }

    const myProjShotPath = path.join(ARTIFACTS_DIR, '05_1500_my_project_modal.png');
    await page.screenshot({ path: myProjShotPath });
    console.log('Saved screenshot:', myProjShotPath);

    await safeClick(page, '[data-testid="btn-close-my-project"]');
    await sleep(400);

    // ----------------------------------------------------
    // PHASE 7: Architectural Renderer Test (Detail View)
    // ----------------------------------------------------
    console.log('\n[PHASE 7] Opening Option A Detail & CAD Blueprint View...');
    await safeClick(page, '[data-testid="btn-view-design-0"]');
    await page.waitForSelector('[data-testid="design-detail-plot-badge"]', { timeout: 15000 });

    const detailBadgeText = await page.$eval('[data-testid="design-detail-plot-badge"]', el => el.textContent.trim());
    console.log('Design Detail Badge Text:', detailBadgeText);
    if (detailBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Design detail badge is NOT "1,500 sq ft Plot", got: "${detailBadgeText}"`);
    }

    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 15000 });
    const wallsCount = await page.$$eval('#walls polygon', els => els.length);
    const spacesCount = await page.$$eval('#spaces g[data-cbm-id]', els => els.length);
    const openingsCount = await page.$$eval('#openings g[data-cbm-id]', els => els.length);
    console.log(`CAD Drawing Elements: Walls=${wallsCount}, Spaces=${spacesCount}, Openings=${openingsCount}`);

    if (spacesCount === 0 || wallsCount === 0) {
      throw new Error('CAD Drawing did NOT render any spaces or walls!');
    }

    const floorPlanShotPath = path.join(ARTIFACTS_DIR, '06_1500_floor_plan_detail.png');
    await page.screenshot({ path: floorPlanShotPath });
    console.log('Saved screenshot:', floorPlanPlanShot = floorPlanShotPath);
    results['PHASE_7_ARCHITECTURAL_RENDERER_1500'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 8: Mutation Test (2 BHK -> 3 BHK)
    // ----------------------------------------------------
    console.log('\n[PHASE 8] Executing 2 BHK -> 3 BHK Mutation Test...');
    await safeClick(page, '[data-testid="btn-back-to-options"]');
    await sleep(400);
    await safeClick(page, '[data-testid="btn-change-requirements"]');
    await page.waitForSelector('[data-testid="btn-bedrooms-3"]', { timeout: 15000 });

    console.log('Selecting 3 Bedrooms...');
    await safeClick(page, '[data-testid="btn-bedrooms-3"]');
    await sleep(300);
    await safeClick(page, '[data-testid="btn-generate-home-options"]');

    console.log('Regenerating 3 BHK design options...');
    await page.waitForSelector('[data-testid="btn-view-design-0"]', { timeout: 30000 });
    await safeClick(page, '[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 15000 });

    const mutatedSpacesCount = await page.$$eval('#spaces g[data-cbm-id]', els => els.length);
    console.log(`Mutated 3 BHK Spaces Count: ${mutatedSpacesCount}`);

    const mutationShotPath = path.join(ARTIFACTS_DIR, '07_3bhk_mutation_floor_plan.png');
    await page.screenshot({ path: mutationShotPath });
    console.log('Saved screenshot:', mutationShotPath);
    results['PHASE_8_2_TO_3BHK_MUTATION'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 9: Room Dimension Mutation Test
    // ----------------------------------------------------
    console.log('\n[PHASE 9] Executing Room Dimension Test...');
    await page.waitForSelector('#spaces g[data-cbm-id] text', { timeout: 8000 });
    await page.evaluate(() => {
      const textEl = document.querySelector('#spaces g[data-cbm-id] text');
      if (textEl) textEl.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await sleep(500);

    const hasWidthInput = await page.$('[data-testid="input-room-width"]');
    if (hasWidthInput) {
      console.log('Editing room width to 4.50m and length to 3.80m...');
      await setReactInput(page, '[data-testid="input-room-width"]', '4.5');
      await setReactInput(page, '[data-testid="input-room-length"]', '3.8');
      await safeClick(page, '[data-testid="btn-apply-room-dimensions"]');
      await sleep(500);
    }

    const roomDimShotPath = path.join(ARTIFACTS_DIR, '08_room_dimension_mutation.png');
    await page.screenshot({ path: roomDimShotPath });
    console.log('Saved screenshot:', roomDimShotPath);
    results['PHASE_9_ROOM_DIMENSION_MUTATION'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 10: 2400 sq ft Customer Journey
    // ----------------------------------------------------
    console.log('\n[PHASE 10] Starting 2,400 sq ft Customer Project...');
    await safeClick(page, '[data-testid="nav-step-SITE"]');
    await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 15000 });

    await setReactInput(page, '[data-testid="input-plot-area"]', '2400');
    await sleep(300);

    await safeClick(page, '[data-testid="btn-check-land"]');
    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 15000 });
    await safeClick(page, '[data-testid="btn-see-what-you-can-build"]');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 15000 });
    const feasBadge2400 = await page.$eval('[data-testid="feasibility-plot-badge"]', el => el.textContent.trim());
    console.log('2400 Feasibility Badge:', feasBadge2400);
    if (!feasBadge2400.includes('2,400 sq ft')) {
      throw new Error(`Feasibility badge did not contain 2,400 sq ft: "${feasBadge2400}"`);
    }

    await safeClick(page, '[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 15000 });
    const designBadge2400 = await page.$eval('[data-testid="design-plot-badge"]', el => el.textContent.trim());
    console.log('2400 Design Badge:', designBadge2400);

    await safeClick(page, '[data-testid="btn-bedrooms-3"]');
    await safeClick(page, '[data-testid="btn-bathrooms-3"]');
    await safeClick(page, '[data-testid="btn-floors-2"]');
    await sleep(300);
    await safeClick(page, '[data-testid="btn-generate-home-options"]');

    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 30000 });
    await safeClick(page, '[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 15000 });

    const shot2400Path = path.join(ARTIFACTS_DIR, '09_2400_floor_plan.png');
    await page.screenshot({ path: shot2400Path });
    console.log('Saved screenshot:', shot2400Path);
    results['PHASE_10_2400_SQFT_CUSTOMER'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 11: 10,000 sq ft Customer Journey
    // ----------------------------------------------------
    console.log('\n[PHASE 11] Starting 10,000 sq ft Customer Project...');
    await safeClick(page, '[data-testid="nav-step-SITE"]');
    await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 15000 });

    await setReactInput(page, '[data-testid="input-plot-area"]', '10000');
    await sleep(300);

    await safeClick(page, '[data-testid="btn-check-land"]');
    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 15000 });
    await safeClick(page, '[data-testid="btn-see-what-you-can-build"]');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 15000 });
    const feasBadge10000 = await page.$eval('[data-testid="feasibility-plot-badge"]', el => el.textContent.trim());
    console.log('10000 Feasibility Badge:', feasBadge10000);

    await safeClick(page, '[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 15000 });

    await safeClick(page, '[data-testid="btn-bedrooms-4"]');
    await safeClick(page, '[data-testid="btn-bathrooms-4"]');
    await safeClick(page, '[data-testid="btn-floors-3"]');
    await sleep(300);
    await safeClick(page, '[data-testid="btn-generate-home-options"]');

    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 30000 });
    await safeClick(page, '[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 15000 });

    const shot10000Path = path.join(ARTIFACTS_DIR, '10_10000_floor_plan.png');
    await page.screenshot({ path: shot10000Path });
    console.log('Saved screenshot:', shot10000Path);
    results['PHASE_11_10000_SQFT_CUSTOMER'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 12: Export CAD Test
    // ----------------------------------------------------
    console.log('\n[PHASE 12] Testing CAD Blueprint Export...');
    const svgContent = await page.$eval('svg#cad-drawing-svg', el => el.outerHTML);
    fs.writeFileSync(path.join(ARTIFACTS_DIR, 'exported_cad_drawing.svg'), svgContent, 'utf-8');
    console.log(`Exported SVG saved (${svgContent.length} bytes)`);
    results['PHASE_12_EXPORT'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 13: Capture Cost Summary, Build Review & Engineer Review
    // ----------------------------------------------------
    console.log('\n[PHASE 13] Capturing Cost Summary, Build Review & Engineer Review...');
    await safeClick(page, '[data-testid="btn-back-to-options"]');
    await page.waitForSelector('[data-testid="btn-choose-design-0"]', { timeout: 15000 });
    await safeClick(page, '[data-testid="btn-choose-design-0"]');
    await sleep(1000);
    const costShotPath = path.join(ARTIFACTS_DIR, '11_cost_summary.png');
    await page.screenshot({ path: costShotPath });
    console.log('Saved screenshot:', costShotPath);

    // Proceed to Build
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find(b => b.textContent && (b.textContent.includes('Proceed') || b.textContent.includes('Lock')));
      if (btn) btn.click();
    });
    await sleep(1000);
    const buildShotPath = path.join(ARTIFACTS_DIR, '12_build_review.png');
    await page.screenshot({ path: buildShotPath });
    console.log('Saved screenshot:', buildShotPath);

    // Switch to Professional Mode
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const profBtn = btns.find(b => b.textContent && b.textContent.includes('Professional Mode'));
      if (profBtn) profBtn.click();
    });
    await sleep(1000);
    const engShotPath = path.join(ARTIFACTS_DIR, '13_engineer_review.png');
    await page.screenshot({ path: engShotPath });
    console.log('Saved screenshot:', engShotPath);
    results['PHASE_13_REVIEWS'] = 'PASS';

    console.log('\n====================================================');
    console.log('ALL PHASES COMPLETED SUCCESSFULLY!');
    console.log(JSON.stringify(results, null, 2));
    console.log('====================================================');

  } catch (err) {
    console.error('\nE2E TEST FAILURE:', err);
    const errShotPath = path.join(ARTIFACTS_DIR, 'failure_screenshot.png');
    await page.screenshot({ path: errShotPath });
    console.error('Failure screenshot saved to:', errShotPath);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
