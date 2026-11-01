
const puppeteer = require('puppeteer-core');
const path = require('path');

(async () => {
    console.log('[PDF BUILD] Launching Chrome to render encyclopedia PDF...');
    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    const page = await browser.newPage();
    const url = 'file://' + path.resolve('/Users/surajkumar/Desktop/Real_state_dev/artifacts/technical_encyclopedia/Planwise_Enterprise_Complete_Technical_Encyclopedia.html');
    console.log('[PDF BUILD] Navigating to: ' + url);
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 180000 });

    console.log('[PDF BUILD] Generating A4 PDF document with running headers/footers...');
    await page.pdf({
        path: '/Users/surajkumar/Desktop/Real_state_dev/artifacts/technical_encyclopedia/Planwise_Enterprise_Complete_Technical_Encyclopedia.pdf',
        format: 'A4',
        printBackground: true,
        scale: 0.88,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 7.5px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-bottom: 0.5px solid #cbd5e1; padding: 0 15mm 3px 15mm; display: flex; justify-content: space-between;"><span>PLANWISE ENTERPRISE — COMPLETE TECHNICAL ENCYCLOPEDIA</span><span>BRANCH: feature/complete-project-documentation • COMMIT: 80a7077</span></div>',
        footerTemplate: '<div style="font-size: 7.5px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-top: 0.5px solid #cbd5e1; padding: 3px 15mm 0 15mm; display: flex; justify-content: space-between;"><span>CONFIDENTIAL & PROPRIETARY — ZERO-FABRICATION FORENSIC AUDIT</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin: {
            top: '18mm',
            bottom: '18mm',
            left: '15mm',
            right: '15mm'
        }
    });

    await browser.close();
    console.log('[PDF BUILD] Master encyclopedia PDF rendered successfully!');
})().catch(err => {
    console.error('[PDF BUILD ERROR]', err);
    process.exit(1);
});
