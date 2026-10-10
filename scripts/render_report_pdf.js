
const puppeteer = require('puppeteer-core');
const path = require('path');

(async () => {
    console.log('[PDF BUILD] Launching Chrome to render master report PDF...');
    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
    });
    const page = await browser.newPage();
    const url = 'file://' + path.resolve('artifacts/planwise_enterprise_forensic_technical_master_report.html');
    console.log('[PDF BUILD] Navigating to: ' + url);
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });

    console.log('[PDF BUILD] Generating A4 PDF document with running headers/footers...');
    await page.pdf({
        path: 'artifacts/planwise_enterprise_forensic_technical_master_report.pdf',
        format: 'A4',
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-bottom: 1px solid #cbd5e1; padding: 0 15mm 4px 15mm; display: flex; justify-content: space-between;"><span>PLANWISE ENTERPRISE — FORENSIC TECHNICAL & MATHEMATICAL MASTER REPORT</span><span>VERSION: 2.0.0 • COMMIT: d678846</span></div>',
        footerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-top: 1px solid #cbd5e1; padding: 4px 15mm 0 15mm; display: flex; justify-content: space-between;"><span>CONFIDENTIAL & PROPRIETARY — ZERO FABRICATION FORENSIC AUDIT</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin: {
            top: '18mm',
            bottom: '18mm',
            left: '15mm',
            right: '15mm'
        }
    });

    await browser.close();
    console.log('[PDF BUILD] Completed! PDF saved to: artifacts/planwise_enterprise_forensic_technical_master_report.pdf');
})().catch(err => {
    console.error('[PDF BUILD ERROR]', err);
    process.exit(1);
});
