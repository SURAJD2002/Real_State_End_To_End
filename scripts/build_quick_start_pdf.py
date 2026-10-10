#!/usr/bin/env python3
"""
Planwise Enterprise — Quick Start PDF Builder
Generates a concise, highly visual 4-page Customer Quick Start Guide PDF via Puppeteer.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def img_to_base64(rel_path: str) -> str:
    full_path = ROOT_DIR / rel_path
    if not full_path.exists():
        return ""
    with open(full_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def build_quick_start_html() -> str:
    img_land = img_to_base64("artifacts/e2e_live_test/01_1500_land_input.png")
    img_feas = img_to_base64("artifacts/e2e_live_test/02_1500_feasibility.png")
    img_options = img_to_base64("artifacts/e2e_live_test/04_1500_design_options.png")
    img_floorplan = img_to_base64("artifacts/e2e_live_test/06_1500_floor_plan_detail.png")
    img_cost = img_to_base64("artifacts/e2e_live_test/11_cost_summary.png")
    img_build = img_to_base64("artifacts/e2e_live_test/12_build_review.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Planwise Enterprise — Quick Start Guide</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 15mm 15mm 15mm 15mm;
  }}
  *, *::before, *::after {{
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.45;
    font-size: 9pt;
    margin: 0;
    padding: 0;
  }}
  h1, h2, h3 {{
    color: #0f172a;
    font-weight: 700;
    margin-top: 0;
  }}
  h1 {{
    font-size: 18pt;
    color: #1e3a8a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 4px;
    margin-bottom: 8pt;
  }}
  h2 {{
    font-size: 12pt;
    color: #0f172a;
    margin-top: 10pt;
    margin-bottom: 4pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 2px;
  }}
  p {{
    margin: 0 0 6pt 0;
  }}
  .step-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 10pt;
  }}
  .step-header {{
    font-weight: 700;
    color: #2563eb;
    font-size: 10pt;
    margin-bottom: 4pt;
    display: flex;
    justify-content: space-between;
  }}
  .step-badge {{
    background: #2563eb;
    color: #ffffff;
    font-size: 7.5pt;
    padding: 2px 6px;
    border-radius: 10px;
  }}
  .figure-img {{
    width: 100%;
    max-height: 175px;
    object-fit: contain;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    margin: 4pt 0;
  }}
  .page-break {{
    page-break-before: always;
    break-before: always;
  }}
  .cover-header {{
    text-align: center;
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 10px;
    margin-bottom: 12pt;
  }}
  .cover-title {{
    font-size: 22pt;
    font-weight: 800;
    color: #0f172a;
  }}
  .cover-sub {{
    font-size: 11pt;
    color: #475569;
    font-weight: 500;
  }}
  .callout {{
    padding: 6px 10px;
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    font-size: 8pt;
    color: #991b1b;
    margin-bottom: 8pt;
  }}
</style>
</head>
<body>

<!-- PAGE 1 -->
<div class="cover-header">
  <div style="font-size: 8pt; font-weight: 700; letter-spacing: 1px; color: #2563eb;">CUSTOMER FAST-TRACK GUIDE</div>
  <div class="cover-title">PLANWISE ENTERPRISE</div>
  <div class="cover-sub">Zero-Friction Quick Start: From Land Intake to Construction Release in 6 Steps</div>
</div>

<div class="callout">
  <strong>Statutory Notice:</strong> Planwise outputs support preliminary planning, feasibility analysis, and computational design synthesis. They do NOT constitute municipal sanctions or licensed structural certifications.
</div>

<p>Planwise Enterprise automates residential real estate feasibility, floor plan generation, quantity takeoffs, and contractor budgeting through an integrated 6-step workflow:</p>

<div class="step-card">
  <div class="step-header">
    <span>Step 1: Enter Land &amp; Property Details</span>
    <span class="step-badge">STEP 1: LAND</span>
  </div>
  <p>Input your site address (e.g. Bandra West, Mumbai), select your municipal jurisdiction (Mumbai DCPR 2034 or BBMP 2026), and enter your registered plot area (e.g. 1,500 sq ft). Specify access road widths (existing vs proposed master plan road) to calculate road widening surrender lines.</p>
  <img src="{img_land}" class="figure-img" alt="Step 1 Land">
  <p style="font-size: 8pt; color: #64748b; margin: 0;"><em>Action: Click <strong>"Confirm Land & Run Feasibility"</strong> to proceed.</em></p>
</div>

<div class="step-card">
  <div class="step-header">
    <span>Step 2: Instant Statutory Feasibility Analysis</span>
    <span class="step-badge">STEP 2: FEASIBILITY</span>
  </div>
  <p>The platform applies municipal building bye-laws to compute road widening surrender strips, front/rear/side setbacks, net buildable footprint, permissible Built-Up Area (BUA), and statutory height limits.</p>
  <img src="{img_feas}" class="figure-img" alt="Step 2 Feasibility">
  <p style="font-size: 8pt; color: #64748b; margin: 0;"><em>Action: Verify your buildable envelope and click <strong>"Proceed to Step 3: DESIGN"</strong>.</em></p>
</div>

<div class="page-break"></div>

<!-- PAGE 2 -->
<h1>Fast-Track Architectural Design Synthesis</h1>

<div class="step-card">
  <div class="step-header">
    <span>Step 3A: Specify Living Requirements</span>
    <span class="step-badge">DESIGN BRIEF</span>
  </div>
  <p>Configure your family's room brief: select bedrooms (1 to 5+ BHK), bathrooms (1 to 4+), floor configuration (Single Level vs G+1 Duplex), and architectural style (Contemporary, Minimalist, Traditional, or Modern Indian). Click <strong>"Synthesize Architectural Options"</strong> to run the Google OR-Tools CP-SAT solver.</p>
</div>

<div class="step-card">
  <div class="step-header">
    <span>Step 3B: Compare Pareto-Optimal Layout Candidates</span>
    <span class="step-badge">DESIGN OPTIONS</span>
  </div>
  <p>The CP-SAT solver generates collision-free floor plans adhering to NBC 2016 room dimensions, perimeter daylighting rules, and plumbing clustering. Compare candidates across Gross BUA, usable carpet area, spatial efficiency, and estimated budget.</p>
  <img src="{img_options}" class="figure-img" alt="Step 3 Options">
  <p style="font-size: 8pt; color: #64748b; margin: 0;"><em>Action: Select your preferred layout card and click <strong>"Choose This Design & Review Cost"</strong>.</em></p>
</div>

<div class="step-card">
  <div class="step-header">
    <span>Step 3C: Read the Architectural Floor Plan Blueprint</span>
    <span class="step-badge">CAD BLUEPRINT</span>
  </div>
  <p>Inspect the millimeter-accurate vector CAD drawing: 230mm external masonry, 115mm internal partitions, doors with 90&deg; swing arcs, sliding windows, dimension strings, and room labels. Click any room to adjust dimensions in real time.</p>
  <img src="{img_floorplan}" class="figure-img" alt="Step 3 Blueprint">
</div>

<div class="page-break"></div>

<!-- PAGE 3 -->
<h1>Budget Transparency &amp; Build Confirmation</h1>

<div class="step-card">
  <div class="step-header">
    <span>Step 4: Review Itemized Quantities &amp; Turnkey Cost</span>
    <span class="step-badge">STEP 4: COST</span>
  </div>
  <p>Quantities are calculated adhering strictly to <strong>IS 1200 measurement standards</strong> (masonry and concrete deducting openings &gt; 0.1 m²; plaster deducting openings &gt; 0.5 m²). The cost calculation executes a transparent financial waterfall:</p>
  <pre style="background: #0f172a; color: #f8fafc; padding: 6px 10px; border-radius: 4px; font-size: 7.5pt; margin: 4pt 0;">
Direct Hard Cost (Sum of BOQ Lines)
  + 8.0% Contractor Prelims & Site Overheads
  + 5.0% Physical Contingency Buffer
= Construction Subtotal
  + 18.0% Statutory Goods & Services Tax (GST)
= TOTAL TURNKEY ESTIMATED BUDGET</pre>
  <p>Toggle between <strong>ECONOMY, STANDARD, PREMIUM,</strong> and <strong>LUXURY</strong> quality tiers to instantly compare finishes.</p>
  <img src="{img_cost}" class="figure-img" alt="Step 4 Cost">
  <p style="font-size: 8pt; color: #64748b; margin: 0;"><em>Action: Confirm quality tier and click <strong>"Proceed to Step 5: BUILD"</strong>.</em></p>
</div>

<div class="step-card">
  <div class="step-header">
    <span>Step 5: Lock Build Release &amp; Freeze Design</span>
    <span class="step-badge">STEP 5: BUILD</span>
  </div>
  <p>Acknowledge statutory notices regarding geotechnical borehole soil tests and municipal sanction requirements. Click <strong>"Lock Build Release"</strong> to freeze the design with an immutable SHA-256 cryptographic fingerprint.</p>
  <img src="{img_build}" class="figure-img" alt="Step 5 Build">
</div>

<div class="page-break"></div>

<!-- PAGE 4 -->
<h1>Professional Review &amp; Document Exports</h1>

<div class="step-card">
  <div class="step-header">
    <span>Step 6: Professional Engineering Review Gates (G0–G6)</span>
    <span class="step-badge">STEP 6: ENGINEER</span>
  </div>
  <p>Licensed architects and civil engineers review the design against seven sequential verification gates before construction release:</p>
  <ul style="font-size: 8pt; margin: 4pt 0; padding-left: 14pt;">
    <li><strong>G0 (Site Truth):</strong> Validates boundary coordinates against land survey evidence.</li>
    <li><strong>G1 (Structural):</strong> Validates Manifold3D watertight 2-manifold solid geometry.</li>
    <li><strong>G2 (Architectural):</strong> Verifies NBC 2016 room dimensions, ceiling heights, and door clearances.</li>
    <li><strong>G3 (MEP):</strong> Audits electrical point quotas and wet stack vertical alignment.</li>
    <li><strong>G4 (Statutory):</strong> Confirms setback clearances, road widening surrender, and FSI caps.</li>
    <li><strong>G5 (Cost):</strong> Audits itemized BOQ lines against regional CPWD rate catalogs.</li>
    <li><strong>G6 (Construction Lock):</strong> Final authorization seal gating production drawing release.</li>
  </ul>
</div>

<h2>Available Project Document Exports</h2>
<table style="width: 100%; border-collapse: collapse; font-size: 8pt; margin-top: 6pt;">
  <thead>
    <tr style="background: #f8fafc;">
      <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Export Artifact</th>
      <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Format</th>
      <th style="padding: 5px; border: 1px solid #cbd5e1; text-align: left;">Description &amp; Use Case</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 5px; border: 1px solid #cbd5e1;"><strong>Architectural Drawing Sheets</strong></td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">PDF (A3 / A4)</td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">Site plans, ground floor plans, terrace plans, sections, and door/window schedules.</td>
    </tr>
    <tr>
      <td style="padding: 5px; border: 1px solid #cbd5e1;"><strong>Customer Home Report</strong></td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">PDF (15 pages)</td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">Executive summary report for homeowners and financing institutions.</td>
    </tr>
    <tr>
      <td style="padding: 5px; border: 1px solid #cbd5e1;"><strong>Open BIM Model</strong></td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">IFC4 (.ifc)</td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">buildingSMART standard BIM model for Revit, ArchiCAD, and Solibri.</td>
    </tr>
    <tr>
      <td style="padding: 5px; border: 1px solid #cbd5e1;"><strong>Itemized Bill of Quantities</strong></td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">CSV / JSON</td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">Structured trade quantities adhering to IS 1200 for contractor tendering.</td>
    </tr>
    <tr>
      <td style="padding: 5px; border: 1px solid #cbd5e1;"><strong>Handoff Release Archive</strong></td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">ZIP Package</td>
      <td style="padding: 5px; border: 1px solid #cbd5e1;">Cryptographically sealed bundle containing CBM JSON, IFC4, SVG, BOQ, and validation logs.</td>
    </tr>
  </tbody>
</table>

<div style="margin-top: 15pt; padding: 8px 12px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; font-size: 8pt; color: #1e40af;">
  <strong>System Support:</strong> For assistance, run <code>uvicorn apps.api_gateway.main:app --port 5001</code> to verify backend health. Refer to the full <em>Planwise Enterprise User Guide</em> (PW-DOC-MANUAL-2026) for comprehensive engineering specifications.
</div>

</body>
</html>
"""
    return html

def main():
    out_dir = ROOT_DIR / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    html_file = out_dir / "planwise_quick_start.html"
    pdf_file = ROOT_DIR / "PLANWISE_QUICK_START.pdf"

    print("[BUILD] Generating Quick Start HTML with genuine visual captures...")
    html_content = build_quick_start_html()
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Wrote Quick Start HTML: {html_file} ({len(html_content):,} bytes)")

    print("[BUILD] Compiling A4 Quick Start PDF via Chrome Puppeteer...")
    puppeteer_script = f"""
const puppeteer = require('puppeteer-core');
const path = require('path');

(async () => {{
    const browser = await puppeteer.launch({{
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--allow-file-access-from-files']
    }});
    const page = await browser.newPage();
    const url = 'file://' + path.resolve('{html_file}');
    console.log('[PDF BUILD] Navigating to: ' + url);
    await page.goto(url, {{ waitUntil: 'networkidle0', timeout: 120000 }});

    console.log('[PDF BUILD] Generating A4 Quick Start PDF...');
    await page.pdf({{
        path: '{pdf_file}',
        format: 'A4',
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-bottom: 1px solid #cbd5e1; padding: 0 15mm 4px 15mm; display: flex; justify-content: space-between;"><span>PLANWISE ENTERPRISE — CUSTOMER QUICK START GUIDE</span><span>FAST-TRACK WORKFLOW</span></div>',
        footerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-top: 1px solid #cbd5e1; padding: 4px 15mm 0 15mm; display: flex; justify-content: space-between;"><span>CONFIDENTIAL & PROPRIETARY</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin: {{
            top: '15mm',
            bottom: '15mm',
            left: '15mm',
            right: '15mm'
        }}
    }});

    await browser.close();
    console.log('[PDF BUILD] Completed! PDF saved to: {pdf_file}');
}})().catch(err => {{
    console.error('[PDF BUILD ERROR]', err);
    process.exit(1);
}});
"""
    tmp_js = ROOT_DIR / "scripts" / "render_quick_start_pdf.js"
    with open(tmp_js, "w", encoding="utf-8") as f:
        f.write(puppeteer_script)

    res = subprocess.run(["node", str(tmp_js)], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[ERROR] PDF generation failed:", res.stderr)
        sys.exit(1)

    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(pdf_file))
        page_count = len(pdf)
        print(f"\n=======================================================")
        print(f"  PLANWISE QUICK START PDF GENERATION SUCCESSFUL")
        print(f"  Total Rendered PDF Pages: {page_count} pages")
        print(f"  Output File: {pdf_file}")
        print(f"=======================================================\n")
    except Exception as e:
        print(f"[NOTE] pypdfium2 check: {e}")

if __name__ == "__main__":
    main()
