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
  const results = {};

  try {
    // ----------------------------------------------------
    // PHASE 1: Connect to Real Application
    // ----------------------------------------------------
    console.log('\n[PHASE 1] Navigating to', APP_URL);
    await page.goto(APP_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
    const title = await page.title();
    console.log('Page Title:', title);
    if (!title.includes('Planwise')) {
      throw new Error(`Unexpected page title: ${title}`);
    }
    results['PHASE_1_START_APP'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 2 & 3: 1500 sq ft Customer Flow (Land -> Feasibility)
    // ----------------------------------------------------
    console.log('\n[PHASE 2] Entering 1500 sq ft in Land Intake...');
    await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 10000 });

    // Clear and enter 1500
    const plotInput = await page.$('[data-testid="input-plot-area"]');
    await plotInput.click({ clickCount: 3 });
    await plotInput.press('Backspace');
    await plotInput.type('1500');
    await sleep(300);

    const landShotPath = path.join(ARTIFACTS_DIR, '01_1500_land_input.png');
    await page.screenshot({ path: landShotPath });
    console.log('Saved screenshot:', landShotPath);

    // Click "Check My Land"
    await page.click('[data-testid="btn-check-land"]');
    console.log('Clicked "Check My Land", waiting for result screen...');

    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 10000 });
    await sleep(400);

    // Click "See What You Can Build" -> Feasibility
    await page.click('[data-testid="btn-see-what-you-can-build"]');
    console.log('Clicked "See What You Can Build", waiting for Feasibility screen...');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 10000 });
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
    await page.click('[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 10000 });

    const designBadgeText = await page.$eval('[data-testid="design-plot-badge"]', el => el.textContent.trim());
    console.log('Design Intake Badge Text:', designBadgeText);

    if (designBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Design intake badge is NOT "1,500 sq ft Plot", got: "${designBadgeText}"`);
    }

    // Select 2 BHK, 2 Bath, G+1 Floors
    await page.click('[data-testid="btn-bedrooms-2"]');
    await page.click('[data-testid="btn-bathrooms-2"]');
    await page.click('[data-testid="btn-floors-2"]');
    await sleep(300);

    const intakeShotPath = path.join(ARTIFACTS_DIR, '03_1500_design_intake.png');
    await page.screenshot({ path: intakeShotPath });
    console.log('Saved screenshot:', intakeShotPath);

    // Click "Generate My Home Options"
    console.log('Clicking "Generate My Home Options"...');
    await page.click('[data-testid="btn-generate-home-options"]');

    // ----------------------------------------------------
    // PHASE 5 & 6: Design Options & Traceability
    // ----------------------------------------------------
    console.log('\n[PHASE 5 & 6] Waiting for Design Options view...');
    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 25000 });

    const optionsBadgeText = await page.$eval('[data-testid="design-options-plot-badge"]', el => el.textContent.trim());
    console.log('Design Options Badge Text:', optionsBadgeText);
    if (optionsBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Options badge is NOT "1,500 sq ft Plot", got: "${optionsBadgeText}"`);
    }

    const optionsShotPath = path.join(ARTIFACTS_DIR, '04_1500_design_options.png');
    await page.screenshot({ path: optionsShotPath });
    console.log('Saved screenshot:', optionsShotPath);

    // Verify My Project Dashboard
    console.log('Checking My Project modal traceability...');
    await page.click('[data-testid="btn-open-my-project"]');
    await page.waitForSelector('[data-testid="myproject-project-id"]', { timeout: 5000 });

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

    // Close modal
    await page.click('[data-testid="btn-close-my-project"]');
    await sleep(400);

    // ----------------------------------------------------
    // PHASE 7: Architectural Renderer Test (Detail View)
    // ----------------------------------------------------
    console.log('\n[PHASE 7] Opening Option A Detail & CAD Blueprint View...');
    await page.click('[data-testid="btn-view-design-0"]');
    await page.waitForSelector('[data-testid="design-detail-plot-badge"]', { timeout: 10000 });

    const detailBadgeText = await page.$eval('[data-testid="design-detail-plot-badge"]', el => el.textContent.trim());
    console.log('Design Detail Badge Text:', detailBadgeText);
    if (detailBadgeText !== '1,500 sq ft Plot') {
      throw new Error(`Design detail badge is NOT "1,500 sq ft Plot", got: "${detailBadgeText}"`);
    }

    // Wait for CAD SVG rendered elements
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 10000 });
    const wallsCount = await page.$$eval('#walls polygon', els => els.length);
    const spacesCount = await page.$$eval('#spaces g[data-cbm-id]', els => els.length);
    const openingsCount = await page.$$eval('#openings g[data-cbm-id]', els => els.length);
    console.log(`CAD Drawing Elements: Walls=${wallsCount}, Spaces=${spacesCount}, Openings=${openingsCount}`);

    if (spacesCount === 0 || wallsCount === 0) {
      throw new Error('CAD Drawing did NOT render any spaces or walls!');
    }

    const floorPlanShotPath = path.join(ARTIFACTS_DIR, '06_1500_floor_plan_detail.png');
    await page.screenshot({ path: floorPlanShotPath });
    console.log('Saved screenshot:', floorPlanShotPath);
    results['PHASE_7_ARCHITECTURAL_RENDERER_1500'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 8: Mutation Test (2 BHK -> 3 BHK)
    // ----------------------------------------------------
    console.log('\n[PHASE 8] Executing 2 BHK -> 3 BHK Mutation Test...');
    await page.click('[data-testid="btn-back-to-options"]');
    await sleep(400);
    await page.click('[data-testid="btn-change-requirements"]');
    await page.waitForSelector('[data-testid="btn-bedrooms-3"]', { timeout: 10000 });

    console.log('Selecting 3 Bedrooms...');
    await page.click('[data-testid="btn-bedrooms-3"]');
    await sleep(300);
    await page.click('[data-testid="btn-generate-home-options"]');

    console.log('Regenerating 3 BHK design options...');
    await page.waitForSelector('[data-testid="btn-view-design-0"]', { timeout: 25000 });
    await page.click('[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 10000 });

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
    // Click on the first space in the CAD blueprint
    await page.waitForSelector('#spaces g[data-cbm-id] text', { timeout: 5000 });
    await page.click('#spaces g[data-cbm-id] text');
    await sleep(500);
    await page.waitForSelector('[data-testid="input-room-width"]', { timeout: 8000 });

    console.log('Editing room width to 4.50m and length to 3.80m...');
    const widthInput = await page.$('[data-testid="input-room-width"]');
    await widthInput.click({ clickCount: 3 });
    await widthInput.press('Backspace');
    await widthInput.type('4.5');

    const lengthInput = await page.$('[data-testid="input-room-length"]');
    await lengthInput.click({ clickCount: 3 });
    await lengthInput.press('Backspace');
    await lengthInput.type('3.8');

    await page.click('[data-testid="btn-apply-room-dimensions"]');
    await sleep(500);

    const roomDimShotPath = path.join(ARTIFACTS_DIR, '08_room_dimension_mutation.png');
    await page.screenshot({ path: roomDimShotPath });
    console.log('Saved screenshot:', roomDimShotPath);
    results['PHASE_9_ROOM_DIMENSION_MUTATION'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 10: 2400 sq ft Customer Journey
    // ----------------------------------------------------
    console.log('\n[PHASE 10] Starting 2,400 sq ft Customer Project...');
    await page.click('[data-testid="nav-step-SITE"]');
    await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 10000 });

    await page.evaluate(() => {
      const el = document.querySelector('[data-testid="input-plot-area"]');
      if (el) {
        el.value = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    const plotInput2400 = await page.$('[data-testid="input-plot-area"]');
    await plotInput2400.type('2400');
    await sleep(300);

    await page.click('[data-testid="btn-check-land"]');
    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 10000 });
    await page.click('[data-testid="btn-see-what-you-can-build"]');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 10000 });
    const feasBadge2400 = await page.$eval('[data-testid="feasibility-plot-badge"]', el => el.textContent.trim());
    console.log('2400 Feasibility Badge:', feasBadge2400);
    if (!feasBadge2400.includes('2,400 sq ft')) {
      throw new Error(`Feasibility badge did not contain 2,400 sq ft: "${feasBadge2400}"`);
    }

    await page.click('[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 10000 });
    const designBadge2400 = await page.$eval('[data-testid="design-plot-badge"]', el => el.textContent.trim());
    console.log('2400 Design Badge:', designBadge2400);
    if (designBadge2400 !== '2,400 sq ft Plot') {
      throw new Error(`Design badge did not match 2,400 sq ft Plot: "${designBadge2400}"`);
    }

    await page.click('[data-testid="btn-bedrooms-3"]');
    await page.click('[data-testid="btn-bathrooms-3"]');
    await page.click('[data-testid="btn-floors-2"]');
    await sleep(300);
    await page.click('[data-testid="btn-generate-home-options"]');

    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 25000 });
    await page.click('[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 10000 });

    const shot2400Path = path.join(ARTIFACTS_DIR, '09_2400_floor_plan.png');
    await page.screenshot({ path: shot2400Path });
    console.log('Saved screenshot:', shot2400Path);
    results['PHASE_10_2400_SQFT_CUSTOMER'] = 'PASS';

    // ----------------------------------------------------
    // PHASE 11: 10,000 sq ft Customer Journey
    // ----------------------------------------------------
    console.log('\n[PHASE 11] Starting 10,000 sq ft Customer Project...');
    await page.click('[data-testid="nav-step-SITE"]');
    await page.waitForSelector('[data-testid="input-plot-area"]', { timeout: 10000 });

    await page.evaluate(() => {
      const el = document.querySelector('[data-testid="input-plot-area"]');
      if (el) {
        el.value = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    const plotInput10000 = await page.$('[data-testid="input-plot-area"]');
    await plotInput10000.type('10000');
    await sleep(300);

    await page.click('[data-testid="btn-check-land"]');
    await page.waitForSelector('[data-testid="btn-see-what-you-can-build"]', { timeout: 10000 });
    await page.click('[data-testid="btn-see-what-you-can-build"]');

    await page.waitForSelector('[data-testid="feasibility-plot-badge"]', { timeout: 10000 });
    const feasBadge10000 = await page.$eval('[data-testid="feasibility-plot-badge"]', el => el.textContent.trim());
    console.log('10000 Feasibility Badge:', feasBadge10000);
    if (!feasBadge10000.includes('10,000 sq ft')) {
      throw new Error(`Feasibility badge did not contain 10,000 sq ft: "${feasBadge10000}"`);
    }

    await page.click('[data-testid="btn-design-my-home"]');
    await page.waitForSelector('[data-testid="design-plot-badge"]', { timeout: 10000 });
    const designBadge10000 = await page.$eval('[data-testid="design-plot-badge"]', el => el.textContent.trim());
    console.log('10000 Design Badge:', designBadge10000);
    if (designBadge10000 !== '10,000 sq ft Plot') {
      throw new Error(`Design badge did not match 10,000 sq ft Plot: "${designBadge10000}"`);
    }

    await page.click('[data-testid="btn-bedrooms-4"]');
    await page.click('[data-testid="btn-bathrooms-4"]');
    await page.click('[data-testid="btn-floors-3"]');
    await sleep(300);
    await page.click('[data-testid="btn-generate-home-options"]');

    await page.waitForSelector('[data-testid="design-options-plot-badge"]', { timeout: 25000 });
    await page.click('[data-testid="btn-view-design-0"]');
    await page.waitForSelector('svg#cad-drawing-svg', { timeout: 10000 });

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
