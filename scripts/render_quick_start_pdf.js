
const puppeteer = require('puppeteer-core');
const path = require('path');

(async () => {
    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--allow-file-access-from-files']
    });
    const page = await browser.newPage();
    const url = 'file://' + path.resolve('/Users/surajkumar/Desktop/Real_state_dev/artifacts/planwise_quick_start.html');
    console.log('[PDF BUILD] Navigating to: ' + url);
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });

    console.log('[PDF BUILD] Generating A4 Quick Start PDF...');
    await page.pdf({
        path: '/Users/surajkumar/Desktop/Real_state_dev/PLANWISE_QUICK_START.pdf',
        format: 'A4',
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-bottom: 1px solid #cbd5e1; padding: 0 15mm 4px 15mm; display: flex; justify-content: space-between;"><span>PLANWISE ENTERPRISE — CUSTOMER QUICK START GUIDE</span><span>FAST-TRACK WORKFLOW</span></div>',
        footerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-top: 1px solid #cbd5e1; padding: 4px 15mm 0 15mm; display: flex; justify-content: space-between;"><span>CONFIDENTIAL & PROPRIETARY</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin: {
            top: '15mm',
            bottom: '15mm',
            left: '15mm',
            right: '15mm'
        }
    });

    await browser.close();
    console.log('[PDF BUILD] Completed! PDF saved to: /Users/surajkumar/Desktop/Real_state_dev/PLANWISE_QUICK_START.pdf');
})().catch(err => {
    console.error('[PDF BUILD ERROR]', err);
    process.exit(1);
});
