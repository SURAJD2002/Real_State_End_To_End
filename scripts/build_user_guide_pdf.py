#!/usr/bin/env python3
"""
Planwise Enterprise — User Guide PDF Builder
Renders high-definition customer manual HTML and compiles it to A4 PDF via Puppeteer.
Embeds real 1440x960 browser screenshots directly as base64 data URIs for 100% offline reliability.
Uses template string replacement to avoid Python f-string brace/backslash escaping conflicts.
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
        print(f"[WARN] Image not found: {full_path}")
        return ""
    with open(full_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def get_template_html() -> str:
    # Read the template with placeholder tokens
    tmpl = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Planwise Enterprise — Step-by-Step User Guide</title>
<style>
  @page {
    size: A4 portrait;
    margin: 18mm 15mm 18mm 15mm;
  }
  *, *::before, *::after {
    box-sizing: border-box;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.55;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }
  h1, h2, h3, h4 {
    color: #0f172a;
    font-weight: 700;
    page-break-after: avoid;
    break-after: avoid;
  }
  h1 {
    font-size: 19pt;
    color: #0f172a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 6px;
    margin-top: 24pt;
    margin-bottom: 12pt;
  }
  h2 {
    font-size: 13.5pt;
    color: #1e3a8a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-top: 18pt;
    margin-bottom: 8pt;
  }
  h3 {
    font-size: 11pt;
    color: #334155;
    margin-top: 12pt;
    margin-bottom: 6pt;
  }
  p {
    margin: 0 0 8pt 0;
    text-align: justify;
  }
  ul, ol {
    margin: 0 0 10pt 0;
    padding-left: 18pt;
  }
  li {
    margin-bottom: 4pt;
  }
  code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 8.5pt;
    background: #f1f5f9;
    padding: 1.5px 4px;
    border-radius: 3px;
    color: #0f172a;
    border: 1px solid #e2e8f0;
  }
  pre {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 8pt;
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 8pt 0 12pt 0;
    line-height: 1.4;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0 14pt 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  th, td {
    padding: 6px 8px;
    border: 1px solid #cbd5e1;
    text-align: left;
    vertical-align: top;
  }
  th {
    background: #f8fafc;
    color: #0f172a;
    font-weight: 700;
  }
  tr:nth-child(even) {
    background: #f8fafc;
  }
  .callout {
    padding: 10px 14px;
    border-radius: 6px;
    margin: 12pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .callout-warning {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
  }
  .callout-info {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
  }
  .callout-danger {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #991b1b;
  }
  .callout-success {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    color: #166534;
  }
  .figure-container {
    margin: 12pt 0 16pt 0;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .figure-img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
  }
  .figure-caption {
    font-size: 8pt;
    color: #64748b;
    font-style: italic;
    margin-top: 5px;
  }
  .page-break {
    page-break-before: always;
    break-before: always;
  }
  .cover-page {
    text-align: center;
    padding-top: 35mm;
    page-break-after: always;
    break-after: always;
  }
  .cover-badge {
    display: inline-block;
    padding: 4px 12px;
    background: #1e3a8a;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 700;
    border-radius: 20px;
    letter-spacing: 1px;
    margin-bottom: 20px;
  }
  .cover-title {
    font-size: 28pt;
    color: #0f172a;
    font-weight: 800;
    margin-bottom: 10px;
    line-height: 1.2;
  }
  .cover-subtitle {
    font-size: 13.5pt;
    color: #475569;
    font-weight: 500;
    margin-bottom: 40px;
    max-width: 550px;
    margin-left: auto;
    margin-right: auto;
  }
  .cover-meta {
    margin-top: 60mm;
    border-top: 1px solid #e2e8f0;
    padding-top: 15px;
    font-size: 9pt;
    color: #64748b;
    display: flex;
    justify-content: space-around;
  }
  .meta-block {
    text-align: left;
  }
  .toc-list {
    list-style: none;
    padding: 0;
  }
  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9.5pt;
  }
  .toc-item a {
    text-decoration: none;
    color: #0f172a;
    font-weight: 600;
  }
  .toc-item span {
    color: #64748b;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <div class="cover-badge">ENTERPRISE USER MANUAL</div>
  <div class="cover-title">PLANWISE ENTERPRISE</div>
  <div class="cover-subtitle">Complete Step-by-Step Operating Guide for Property Owners, Real Estate Developers & Engineering Teams</div>

  <div style="margin: 30px auto; max-width: 480px; padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; text-align: left; font-size: 8.5pt; color: #475569;">
    <strong>Scope of this Manual:</strong><br/>
    This guide explains how to operate the Planwise Enterprise web application from end to end: parcel intake, statutory feasibility checks, customer design briefs, mathematical CP-SAT layout generation, architectural floor plan blueprints, IS 1200 quantity takeoffs, turnkey cost estimation, and professional engineering review gates.
  </div>

  <div class="cover-meta">
    <div class="meta-block">
      <strong>Product Version:</strong> 2.0.0-Enterprise<br/>
      <strong>Document Reference:</strong> PW-DOC-MANUAL-2026<br/>
      <strong>Publication Date:</strong> October 2026
    </div>
    <div class="meta-block">
      <strong>Verification Standard:</strong> Zero-Fabrication Audit<br/>
      <strong>Target Jurisdictions:</strong> Mumbai DCPR 2034 & BBMP 2026<br/>
      <strong>Architecture:</strong> Canonical Building Model (CBM)
    </div>
  </div>
</div>

<!-- STATUTORY NOTICE & TOC -->
<div>
  <h2>Statutory & Legal Warning Notice</h2>
  <div class="callout callout-danger">
    <strong>MANDATORY STATUTORY NOTICE:</strong><br/>
    Planwise Enterprise is a computational land-to-home development platform that connects land constraints, statutory feasibility, architectural building design, quantity takeoffs, cost estimation, and controlled engineering handoff through a Canonical Building Model (CBM).<br/><br/>
    <strong>Planwise outputs support preliminary planning, feasibility analysis, and computational design synthesis. They do NOT constitute statutory municipal sanctions, structural engineering certifications, licensed architectural sign-offs, or authorization to commence construction.</strong><br/><br/>
    All generated designs, structural elements, and quantity takeoffs must be reviewed, sealed, and submitted by a licensed Architect registered with the Council of Architecture (COA), a licensed Structural Engineer, and relevant municipal authorities (e.g., MCGM / BBMP) prior to physical execution.
  </div>

  <h2>Table of Contents</h2>
  <div class="toc-list">
    <div class="toc-item"><a href="#ch1">Chapter 1: Introduction to Planwise Enterprise</a> <span>Overview & Capabilities</span></div>
    <div class="toc-item"><a href="#ch2">Chapter 2: Getting Started & System Navigation</a> <span>Workspace & Mode Controls</span></div>
    <div class="toc-item"><a href="#ch3">Chapter 3: Creating a Land Project (Step 1: LAND)</a> <span>Plot Intake & Dimensions</span></div>
    <div class="toc-item"><a href="#ch4">Chapter 4: Site Evidence & Statutory Feasibility (Step 2: FEASIBILITY)</a> <span>Setbacks & FSI Analysis</span></div>
    <div class="toc-item"><a href="#ch5">Chapter 5: Entering the Customer Design Brief (Step 3: DESIGN — Intake)</a> <span>Configuring Living Spaces</span></div>
    <div class="toc-item"><a href="#ch6">Chapter 6: Generating & Comparing Design Options (Step 3: DESIGN — Options)</a> <span>CP-SAT Pareto Selection</span></div>
    <div class="toc-item"><a href="#ch7">Chapter 7: Reading Architectural Floor Plans (Step 3: DESIGN — Viewer)</a> <span>CAD Conventions & Room Mutation</span></div>
    <div class="toc-item"><a href="#ch8">Chapter 8: Quantity Takeoff, BOQ & Cost Estimation (Step 4: COST)</a> <span>IS 1200 & Cost Waterfall</span></div>
    <div class="toc-item"><a href="#ch9">Chapter 9: Build Review, Release Locking & Handoff Packages (Step 5: BUILD)</a> <span>Cryptographic Fingerprints</span></div>
    <div class="toc-item"><a href="#ch10">Chapter 10: Professional Engineer Review & Approval Gates (Step 6: ENGINEER)</a> <span>G0–G6 Gates & Sign-Off</span></div>
    <div class="toc-item"><a href="#ch11">Chapter 11: Practical Troubleshooting Guide</a> <span>Diagnostic Matrix</span></div>
    <div class="toc-item"><a href="#ch12">Chapter 12: System Limitations & Safe Use Boundaries</a> <span>Technical Constraints</span></div>
  </div>
</div>

<div class="page-break"></div>

<!-- CHAPTER 1 -->
<div id="ch1">
  <h1>Chapter 1: Introduction to Planwise Enterprise</h1>
  <p><strong>Planwise Enterprise</strong> is an integrated computational land-to-home development platform. In conventional real estate workflows, land boundary surveys, zoning checks, floor planning, structural engineering, quantity surveying, and contractor budgeting exist in isolated silos. This causes months of delay, design discrepancies, and budget blowouts.</p>

  <p>Planwise unifies these disciplines through a single <strong>Canonical Building Model (CBM)</strong>. When a property owner or developer inputs land dimensions, the platform applies municipal development regulations, optimizes spatial layouts via mathematical constraint programming, extracts physical construction quantities adhering to national measurement standards, and computes turnkey budgets linked to localized rate catalogs.</p>

  <h2>1.1 Core System Capabilities</h2>
  <ul>
    <li><strong>Zero Distortion Land Projection:</strong> Projects geodetic latitude and longitude coordinates into a local topocentric Site Engineering Coordinate System (SECS) with sub-millimeter precision.</li>
    <li><strong>Statutory Feasibility Automation:</strong> Evaluates directional setbacks, statutory road widening land surrenders, permissible Floor Space Index (FSI), ground coverage, and height limits.</li>
    <li><strong>Constraint Programming Floor Plan Synthesis:</strong> Uses Google OR-Tools CP-SAT to synthesize room layouts that guarantee zero room overlap, compliance with National Building Code (NBC 2016) room sizes, and forbidden adjacency rules.</li>
    <li><strong>Rigorous 3D Solid Geometry:</strong> Evaluates watertight 2-manifold CAD solids via Manifold3D, guaranteeing positive volume and topological integrity.</li>
    <li><strong>IS 1200 Quantity Extraction:</strong> Deducts door, window, and shaft voids from wall masonry and concrete slabs using standardized thresholds.</li>
    <li><strong>Controlled Engineering Handoff:</strong> Enforces seven sequential review gates (G0 to G6) and packages release baselines into open buildingSMART IFC4 models.</li>
  </ul>

  <h2>1.2 Intended User Personas</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">User Persona</th>
        <th style="width: 35%;">Primary Workflow</th>
        <th style="width: 40%;">Key Deliverables Used</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Property Owner / Homebuilder</strong></td>
        <td>Tests what house typologies fit their land, reviews setbacks, and explores budget options.</td>
        <td>Customer Floor Plan View, Feasibility Summary, Turnkey Cost Waterfall.</td>
      </tr>
      <tr>
        <td><strong>Real Estate Developer</strong></td>
        <td>Rapid plot yield analysis, comparison of single-family vs duplex options across plot portfolios.</td>
        <td>FSI Yield Metrics, Pareto Option Cards, Financial Waterfall Breakdown.</td>
      </tr>
      <tr>
        <td><strong>Design Manager / Architect</strong></td>
        <td>Synthesizes compliant room configurations, inspects dimension ticks, and mutates room widths.</td>
        <td>Architectural CAD Blueprint Viewer, SVG Vector Drawing Export, CBM JSON.</td>
      </tr>
      <tr>
        <td><strong>Civil Engineer / Quantity Surveyor</strong></td>
        <td>Audits itemized trade quantities, inspects opening deductions, and signs off review gates.</td>
        <td>IS 1200 BOQ Spreadsheet, Engineer Review Dashboard, IFC4 Model.</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="page-break"></div>

<!-- CHAPTER 2 -->
<div id="ch2">
  <h1>Chapter 2: Getting Started & System Navigation</h1>
  <p>Planwise Enterprise operates as a web-based client connecting to a high-performance Python FastAPI backend.</p>

  <h2>2.1 Accessing the Application</h2>
  <p>Open Google Chrome or any Chromium-compatible browser and navigate to:</p>
  <pre><code>http://localhost:5173</code></pre>

  <div class="callout callout-info">
    <strong>Note on Single-Tenant Prototype State:</strong> User authentication, login credentials, and multi-tenant organization management are not implemented in the current prototype. The application loads immediately into your active project workspace. All team members sharing the same local deployment share the current project state.
  </div>

  <h2>2.2 Top Navigation Header</h2>
  <p>The top navigation header provides access to the six sequential workflow steps, view modes, and project metadata:</p>

  <div class="figure-container">
    <img src="__IMG_LAND__" class="figure-img" alt="Planwise Header Navigation">
    <div class="figure-caption">Figure 2.1: The Planwise Enterprise Top Navigation Bar showing workflow tabs, Customer/Technical mode toggle, and project status.</div>
  </div>

  <ol>
    <li><strong>Workflow Progression Tabs:</strong>
      <ul>
        <li><strong>Step 1: LAND:</strong> Enter location, declared plot area, boundary geometry, and road access.</li>
        <li><strong>Step 2: FEASIBILITY:</strong> Review statutory setbacks, road widening surrender, and buildable footprint.</li>
        <li><strong>Step 3: DESIGN:</strong> Configure living requirements, generate layouts, and inspect CAD floor plans.</li>
        <li><strong>Step 4: COST:</strong> Review the turnkey cost waterfall, switch quality tiers, and inspect the BOQ.</li>
        <li><strong>Step 5: BUILD:</strong> Confirm customer acknowledgements and lock the build release.</li>
        <li><strong>Step 6: ENGINEER:</strong> Inspect professional verification gates G0–G6 and sign digital stamps.</li>
      </ul>
    </li>
    <li><strong>View Mode Switcher:</strong>
      <ul>
        <li><strong>CUSTOMER Mode:</strong> Clean visual cards, interactive sliders, and plain-language summaries.</li>
        <li><strong>TECHNICAL Mode:</strong> Dense engineering HUDs, Mapbox spatial tools, CAD layer toggles, and raw statutory citations.</li>
      </ul>
    </li>
    <li><strong>My Project Button:</strong> Opens the Project Status Modal displaying project metadata, declared area, and quick jumps to previous steps.</li>
  </ol>

  <div class="figure-container">
    <img src="__IMG_MODAL__" class="figure-img" alt="My Project Modal">
    <div class="figure-caption">Figure 2.2: My Project Modal showing project metadata, declared area (1,500 sq ft), cadastral number, and step navigation.</div>
  </div>
</div>

<div class="page-break"></div>

<!-- CHAPTER 3 -->
<div id="ch3">
  <h1>Chapter 3: Creating a Land Project (Step 1: LAND)</h1>
  <p>Every development begins with defining the site parcel in <strong>Step 1: LAND</strong>.</p>

  <div class="figure-container">
    <img src="__IMG_LAND__" class="figure-img" alt="Land Intake Form">
    <div class="figure-caption">Figure 3.1: Land Intake Screen (Customer Mode) showing project location, declared area of 1,500 sq ft, and road parameters.</div>
  </div>

  <h2>3.1 Entering Land Details (Customer Mode)</h2>
  <ol>
    <li><strong>Project Location & Address:</strong> Enter the site address (e.g., <code>Bandra West, Mumbai</code>).</li>
    <li><strong>Jurisdiction:</strong> Select the municipal building code. Planwise includes verified rule packs for <code>MUMBAI_DCPR_2034</code> and <code>BBMP_BENGALURU_2026</code>.</li>
    <li><strong>Declared Plot Area:</strong> Enter the legal registered area from your title deed (e.g., <code>1500</code>) and select the unit (<code>sq ft</code> or <code>sq m</code>).</li>
    <li><strong>Plot Geometry Shape:</strong>
      <ul>
        <li><strong>Regular (Rectangular / Square):</strong> The engine computes an optimal 16:9 aspect ratio envelope.</li>
        <li><strong>Irregular:</strong> Prompts for coordinate vertices or map drawing.</li>
      </ul>
    </li>
    <li><strong>Existing Road Width:</strong> Enter the current physical road width (e.g., <code>16 ft</code> / <code>4.88 m</code>).</li>
    <li><strong>Proposed Master Plan Road Width:</strong> Enter the statutory widened road width (e.g., <code>40 ft</code> / <code>12.19 m</code>).</li>
    <li><strong>Road-Facing Orientation:</strong> Select which parcel edge faces the access road (<code>North</code>, <code>South</code>, <code>East</code>, or <code>West</code>).</li>
  </ol>

  <p>Click <strong>Confirm Land & Run Feasibility</strong> to save parcel parameters and advance to Step 2.</p>

  <h2>3.2 Technical Mode: Mapbox Canvas & Boundary Manipulation</h2>
  <p>Switching to <strong>TECHNICAL</strong> mode displays the full GIS map canvas:</p>
  <ul>
    <li><strong>Adding Vertices:</strong> Click anywhere on the map to add parcel boundary nodes. A minimum of 3 vertices is required to form a closed polygon.</li>
    <li><strong>Editing Vertices:</strong> Click and drag any vertex to adjust boundaries.</li>
    <li><strong>Debounced Auto-Save:</strong> The map automatically debounces updates and saves changes to <code>PUT /api/v1/projects/{id}/geometries</code> within 600ms.</li>
  </ul>

  <h2>3.3 Critical Area Concepts</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Area Metric</th>
        <th style="width: 35%;">Definition & Calculation</th>
        <th style="width: 40%;">Significance for Homeowners</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Declared Plot Area</strong></td>
        <td>Gross registered land area (e.g. 1,500 sq ft = 139.35 m²).</td>
        <td>Your legal ownership boundary recorded on sale deeds.</td>
      </tr>
      <tr>
        <td><strong>Road Widening Surrender</strong></td>
        <td>Land surrendered along road frontage: depth = max(0, (ProposedRoad - ExistingRoad)/2).</td>
        <td>Must be left unbuilt and surrendered to the municipality.</td>
      </tr>
      <tr>
        <td><strong>Net Developable Area</strong></td>
        <td>Net Area = Declared Area - Surrender Area.</td>
        <td>The statutory base area used to compute your permissible FSI.</td>
      </tr>
      <tr>
        <td><strong>Buildable Footprint</strong></td>
        <td>Buildable Area = Net Area - Directional Setbacks.</td>
        <td>The physical ground area inside which your house walls can sit.</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="page-break"></div>

<!-- CHAPTER 4 -->
<div id="ch4">
  <h1>Chapter 4: Site Evidence & Statutory Feasibility (Step 2: FEASIBILITY)</h1>
  <p>Once land parameters are saved, Planwise evaluates statutory feasibility in <strong>Step 2: FEASIBILITY</strong>.</p>

  <div class="figure-container">
    <img src="__IMG_FEAS__" class="figure-img" alt="Feasibility Summary">
    <div class="figure-caption">Figure 4.1: Feasibility Summary Screen showing statutory compliance status, setback deductions, and permissible BUA.</div>
  </div>

  <h2>4.1 Reviewing Feasibility Metrics</h2>
  <ul>
    <li><strong>Statutory Feasibility Status:</strong> Displays <code>FEASIBLE</code> (green badge) if the parcel accommodates residential construction. If setbacks leave less than 10 m² buildable area, the system alerts <code>INFEASIBLE_SETBACK_COLLAPSE</code>.</li>
    <li><strong>Road Widening Surrender:</strong> Displays the calculated surrender depth and deducted area.</li>
    <li><strong>Directional Building Setbacks:</strong>
      <ul>
        <li><strong>Front Setback:</strong> Required distance from the road boundary (e.g., 4.5m for Mumbai roads 9m-12m).</li>
        <li><strong>Rear Setback:</strong> Rear property clearance (statutory 3.0m).</li>
        <li><strong>Side Setbacks:</strong> Lateral side buffers (statutory 1.5m each).</li>
      </ul>
    </li>
    <li><strong>Permissible Built-Up Area (BUA):</strong> The maximum allowable constructed floor area across all storeys:
      <code>Permissible BUA = Net Area * (Base FSI + Premium FSI + TDR FSI)</code>
    </li>
    <li><strong>Usable Carpet Area:</strong> Estimated usable floor area calculated at 70% of permissible BUA per RERA rules.</li>
    <li><strong>Maximum Permissible Height:</strong> Statutory height cap corresponding to road width (e.g., 16.0m for roads under 9m, up to 120.0m for roads 27m or wider).</li>
  </ul>

  <h2>4.2 Site Evidence & Confidence Tiers (L0 to L3)</h2>
  <p>The <strong>Site Evidence & Truth Panel</strong> in the top-right corner shows your site's confidence rating:</p>
  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Tier</th>
        <th style="width: 25%;">Confidence Category</th>
        <th style="width: 35%;">Data Provenance</th>
        <th style="width: 25%;">Release Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>L0</strong></td>
        <td>Unverified Declaration</td>
        <td>User manually entered area without spatial boundary nodes.</td>
        <td><strong style="color: #ef4444;">BLOCKED</strong> (Draft only)</td>
      </tr>
      <tr>
        <td><strong>L1</strong></td>
        <td>Desktop Geometry</td>
        <td>Drawn on map satellite canvas (±2.5m error).</td>
        <td><strong style="color: #ef4444;">BLOCKED</strong> (Layout exploration only)</td>
      </tr>
      <tr>
        <td><strong>L2</strong></td>
        <td>Municipal Cadastral</td>
        <td>Official municipality GIS parcel boundary shapefile.</td>
        <td><strong style="color: #f59e0b;">CONDITIONAL</strong> (Sanction review)</td>
      </tr>
      <tr>
        <td><strong>L3</strong></td>
        <td>Licensed Land Survey</td>
        <td>Total Station / RTK-GNSS licensed land surveyor boundary with monuments.</td>
        <td><strong style="color: #22c55e;">UNLOCKED</strong> (Construction Release)</td>
      </tr>
    </tbody>
  </table>

  <p>Click <strong>Proceed to Step 3: DESIGN</strong> to start floor plan synthesis.</p>
</div>

<div class="page-break"></div>

<!-- CHAPTER 5 -->
<div id="ch5">
  <h1>Chapter 5: Entering the Customer Design Brief (Step 3: DESIGN — Intake)</h1>
  <p>In <strong>Step 3: DESIGN</strong>, you specify your family's living requirements.</p>

  <div class="figure-container">
    <img src="__IMG_INTAKE__" class="figure-img" alt="Design Intake Brief">
    <div class="figure-caption">Figure 5.1: Customer Design Intake Screen for selecting bedrooms, bathrooms, floor levels, and architectural styles.</div>
  </div>

  <h2>5.1 Configuring Requirements</h2>
  <ol>
    <li><strong>Bedrooms (BHK Typology):</strong> Select <code>1 BHK</code>, <code>2 BHK</code>, <code>3 BHK</code>, <code>4 BHK</code>, or <code>5+ BHK</code>.</li>
    <li><strong>Bathrooms:</strong> Select <code>1 Bath</code>, <code>2 Baths</code>, <code>3 Baths</code>, or <code>4+ Baths</code>.</li>
    <li><strong>Floor Configuration:</strong>
      <ul>
        <li><strong>1 Floor (Single Level):</strong> All living spaces arranged on the ground level (L0).</li>
        <li><strong>2 Floors (G+1 Duplex):</strong> Living, kitchen, and guest suite on ground level (L0); master suite, secondary bedrooms, and family lounge on first floor (L1), connected by an internal RCC staircase.</li>
      </ul>
    </li>
    <li><strong>Architectural Style:</strong>
      <ul>
        <li><strong>Contemporary:</strong> Open-plan living/dining, expansive window glazing.</li>
        <li><strong>Minimalist:</strong> Compact circulation corridors, efficient modular room proportions.</li>
        <li><strong>Traditional:</strong> Distinct kitchen compartmentalization, formal entrance foyer.</li>
        <li><strong>Modern Indian:</strong> Dedicated prayer/pooja alcove, separate utility wash yard.</li>
      </ul>
    </li>
    <li><strong>Parking Spaces:</strong> Configure covered or stilt parking allocation (1 to 2 ECS).</li>
  </ol>

  <p>Click <strong>Synthesize Architectural Options (CP-SAT)</strong> to trigger the layout solver.</p>
</div>

<div class="page-break"></div>

<!-- CHAPTER 6 -->
<div id="ch6">
  <h1>Chapter 6: Generating & Comparing Design Options (Step 3: DESIGN — Options)</h1>
  <p>Planwise uses <strong>Google OR-Tools CP-SAT</strong> to synthesize floor plans mathematically.</p>

  <div class="figure-container">
    <img src="__IMG_OPTIONS__" class="figure-img" alt="Design Options Carousel">
    <div class="figure-caption">Figure 6.1: Generated Design Options View showing Pareto candidate cards, area metrics, and estimated budgets.</div>
  </div>

  <h2>6.1 Mathematical Principles of Generation</h2>
  <ul>
    <li><strong>100mm Integer Grid:</strong> Rooms are placed on a 100mm (0.1m) coordinate grid.</li>
    <li><strong>Zero Overlap:</strong> Model interval variables and <code>AddNoOverlap2D</code> guarantee that rooms never collide.</li>
    <li><strong>NBC 2016 Room Area Bounds:</strong> Every room satisfies minimum areas (Living ≥ 9.5m², Master Bed ≥ 9.5m², Kitchen ≥ 4.5m², Bath ≥ 1.8m²).</li>
    <li><strong>Perimeter Daylighting:</strong> Habitable rooms earn objective bonuses when positioned along exterior envelope walls.</li>
    <li><strong>Wet Area Clustering:</strong> Wet spaces (baths, kitchen, utility) are clustered to minimize plumbing runs.</li>
    <li><strong>Pareto Frontier Filtering:</strong> Filters candidates down to optimal options balancing spatial efficiency, daylight, and circulation.</li>
  </ul>

  <h2>6.2 Comparing Design Cards</h2>
  <p>Each synthesized candidate card presents key metrics:</p>
  <ul>
    <li><strong>Gross Built-Up Area (BUA):</strong> Total constructed area (e.g., 139.35 m² / 1,500 sq ft).</li>
    <li><strong>Usable Carpet Area:</strong> Net usable interior floor area (e.g., 105.8 m² / 1,139 sq ft).</li>
    <li><strong>Spatial Efficiency:</strong> Ratio of usable carpet area to BUA (typically 75% - 82%).</li>
    <li><strong>Estimated Budget:</strong> Real-time estimate from the preliminary BOQ (e.g., ₹39.2 Lakhs).</li>
    <li><strong>2D Plan Thumbnail:</strong> Interactive preview showing room layout and circulation.</li>
  </ul>

  <p>Click on any candidate card to select it, or click <strong>Choose This Design & Review Cost</strong> to proceed.</p>
</div>

<div class="page-break"></div>

<!-- CHAPTER 7 -->
<div id="ch7">
  <h1>Chapter 7: Reading Architectural Floor Plans (Step 3: DESIGN — Viewer)</h1>
  <p>Selecting an option displays the architectural CAD blueprint.</p>

  <div class="figure-container">
    <img src="__IMG_FLOORPLAN__" class="figure-img" alt="Architectural Blueprint CAD View">
    <div class="figure-caption">Figure 7.1: Architectural Floor Plan Blueprint showing room layouts, door swing arcs, sliding windows, and dimension strings.</div>
  </div>

  <h2>7.1 Architectural Drafting Conventions</h2>
  <ol>
    <li><strong>Walls:</strong>
      <ul>
        <li><strong>External Walls:</strong> Thick 1.6pt black strokes with subtle grey fill (230mm / 9" load-bearing structural walls).</li>
        <li><strong>Internal Partitions:</strong> Thin 1.0pt strokes (115mm / 4.5" non-load-bearing AAC blocks).</li>
      </ul>
    </li>
    <li><strong>Doors & Swing Arcs:</strong> Rendered with a solid door leaf at 90° and a dashed quarter-circle arc showing swing clearance.</li>
    <li><strong>Windows:</strong> Rendered as double lines along exterior walls with outer cut lines and inner glass centerlines.</li>
    <li><strong>Stairs (for Duplexes):</strong> Rendered with parallel step tread lines, landing dividers, and an arrow pointing upward with the label <strong>"UP"</strong>.</li>
    <li><strong>Dimension Strings:</strong> Lines with 45° architectural tick marks showing imperial feet-and-inches (e.g., 14'-6") and metric millimeters.</li>
    <li><strong>Room Labels:</strong> Bold room titles with net carpet area (e.g., <strong>MASTER BEDROOM</strong>, 14.2 m²).</li>
  </ol>

  <h2>7.2 Interactive Room Dimension Mutation</h2>
  <p>Clicking on any room in the floor plan opens the <strong>Room Inspector Panel</strong>:</p>

  <div class="figure-container">
    <img src="__IMG_MUT_DIM__" class="figure-img" alt="Room Dimension Mutation">
    <div class="figure-caption">Figure 7.2: Interactive Room Mutation showing dimension adjustments and live area re-validation.</div>
  </div>

  <ul>
    <li><strong>Width & Depth Controls:</strong> Use +0.2m / -0.2m buttons to fine-tune room dimensions.</li>
    <li><strong>NBC Re-validation:</strong> Checks whether modified dimensions continue to satisfy NBC minimums.</li>
    <li><strong>Instant Cost Recalculation:</strong> Modifying boundaries instantly recalculates wall lengths, finishes, and the cost estimate.</li>
  </ul>

  <h2>7.3 Verified Multi-Plot Scalability</h2>
  <p>Planwise dynamically synthesizes layouts across all plot sizes without template distortion:</p>

  <div class="figure-container">
    <img src="__IMG_2400__" class="figure-img" alt="2,400 sq ft Duplex Floor Plan">
    <div class="figure-caption">Figure 7.3: 2,400 sq ft Duplex Floor Plan (19.91m x 11.20m envelope) showing ground floor living, master bedroom, and staircase.</div>
  </div>

  <div class="figure-container">
    <img src="__IMG_10000__" class="figure-img" alt="10,000 sq ft Estate Villa Floor Plan">
    <div class="figure-caption">Figure 7.4: 10,000 sq ft Estate Villa Floor Plan (40.64m x 22.86m envelope) showing double-height living, dining, and suites.</div>
  </div>
</div>

<div class="page-break"></div>

<!-- CHAPTER 8 -->
<div id="ch8">
  <h1>Chapter 8: Quantity Takeoff, BOQ & Cost Estimation (Step 4: COST)</h1>
  <p>In <strong>Step 4: COST</strong>, Planwise translates building geometry into an itemized construction budget.</p>

  <div class="figure-container">
    <img src="__IMG_COST__" class="figure-img" alt="Cost Summary Screen">
    <div class="figure-caption">Figure 8.1: Cost Summary Screen displaying turnkey construction estimate, cost per sq ft BUA, quality tiers, and financial waterfall.</div>
  </div>

  <h2>8.1 IS 1200 Measurement Standards</h2>
  <p>Quantities are calculated from model solids adhering to <strong>IS 1200: Indian Standard Method of Measurement</strong>:</p>
  <ul>
    <li><strong>IS 1200 Part 3 (Masonry):</strong> Gross wall volume (Length * Height * Thickness) less door and window openings greater than 0.1 m².</li>
    <li><strong>IS 1200 Part 2 (Concrete):</strong> Column volumes (Width * Depth * Height) and slab volumes, deducting stair openings greater than 0.1 m².</li>
    <li><strong>IS 1200 Part 12 (Plastering):</strong> Wall faces and ceiling soffits, deducting openings greater than 0.5 m² per Clause 4.2.</li>
    <li><strong>IS 1200 Part 11 (Flooring):</strong> Room carpet areas for tiling, and perimeters less doorway widths for skirting.</li>
  </ul>

  <h2>8.2 The Turnkey Cost Waterfall</h2>
  <pre><code>[ Direct Gross Hard Cost (Sum of BOQ Lines) ]
                      |
                      +---> + 8.0% Contractor Prelims & Site Overheads
                      |
                      +---> + 5.0% Physical Contingency Buffer
                      |
           [ Construction Subtotal ]
                      |
                      +---> + 18.0% Statutory Goods & Services Tax (GST)
                      |
        [ TOTAL TURNKEY ESTIMATED CONSTRUCTION COST ]</code></pre>

  <p><em>Example: 1,500 sq ft Residence (Standard Tier):</em></p>
  <ul>
    <li><strong>Direct Hard Construction Cost:</strong> ₹31,45,200.00</li>
    <li><strong>Contractor Prelims & Site Overheads (8%):</strong> ₹2,51,616.00</li>
    <li><strong>Physical Contingency Buffer (5%):</strong> ₹1,57,260.00</li>
    <li><strong>Construction Subtotal:</strong> ₹35,54,076.00</li>
    <li><strong>Statutory GST (18% on Subtotal):</strong> ₹6,39,733.68</li>
    <li><strong>Total Estimated Turnkey Cost:</strong> <strong>₹41,93,809.68</strong></li>
    <li><strong>Cost per Sq Ft BUA:</strong> <strong>₹2,795.87 / sq ft</strong></li>
  </ul>

  <h2>8.3 Quality Tier Switching</h2>
  <ul>
    <li><strong>ECONOMY:</strong> Country brick, vitrified tiles (600x600mm), standard flush doors (~₹2,350 / sq ft BUA).</li>
    <li><strong>STANDARD (Default):</strong> AAC blocks, nano-polished tiles (800x800mm), UPVC windows (~₹2,795 / sq ft BUA).</li>
    <li><strong>PREMIUM:</strong> Italian composite marble, teakwood main door frame, double-glazed windows (~₹3,450 / sq ft BUA).</li>
    <li><strong>LUXURY:</strong> Imported marble, concealed VRV air conditioning, automated smart home electricals (~₹4,200 / sq ft BUA).</li>
  </ul>

  <p>Click <strong>Proceed to Step 5: BUILD</strong> to prepare for project release.</p>
</div>

<div class="page-break"></div>

<!-- CHAPTER 9 -->
<div id="ch9">
  <h1>Chapter 9: Build Review, Release Locking & Handoff Packages (Step 5: BUILD)</h1>
  <p>In <strong>Step 5: BUILD</strong>, you review and freeze the approved design baseline.</p>

  <div class="figure-container">
    <img src="__IMG_BUILD__" class="figure-img" alt="Build Review Screen">
    <div class="figure-caption">Figure 9.1: Build Review Screen displaying customer statutory acknowledgements, release gating summary, and build confirmation controls.</div>
  </div>

  <h2>9.1 Customer Statutory Acknowledgements</h2>
  <p>Before locking the build release, the user must acknowledge three statutory statements:</p>
  <ol>
    <li><code>[x]</code> <em>I understand that soil bearing capacity and foundation design require a site-specific geotechnical borehole test.</em></li>
    <li><code>[x]</code> <em>I acknowledge that architectural drawings must be sanctioned by the local municipal corporation prior to construction.</em></li>
    <li><code>[x]</code> <em>I confirm that the selected quality tier and preliminary budget reflect my requested specifications.</em></li>
  </ol>

  <p>Click <strong>Lock Build Release (G6 Release Gate)</strong> to freeze the design baseline.</p>

  <h2>9.2 The Release Handoff Package</h2>
  <p>Locking the build triggers a deterministic cryptographic freeze:</p>
  <ul>
    <li><strong>Release ID:</strong> Assigns an immutable release identifier (e.g., <code>rel-pilot-20261002-aedf9830</code>).</li>
    <li><strong>Cryptographic SHA-256 Fingerprint:</strong> Generates a 64-character hash over the model geometry, rates, and quantities. Any subsequent edit generates a new design version, preventing silent tampering.</li>
    <li><strong>Handoff Package Contents:</strong>
      <ul>
        <li><code>model_cbm.json</code> — Canonical Building Model definition.</li>
        <li><code>model_ifc4.ifc</code> — buildingSMART IFC4 architectural model with georeferenced metadata.</li>
        <li><code>floor_plan_ground.svg</code> — Vector CAD floor plan drawing.</li>
        <li><code>bill_of_quantities.csv</code> & <code>.json</code> — Itemized IS 1200 trade quantities and rates.</li>
        <li><code>cost_waterfall_summary.pdf</code> — Turnkey financial breakdown.</li>
        <li><code>validation_report.json</code> — Manifold3D watertightness and compliance logs.</li>
      </ul>
    </li>
  </ul>
</div>

<div class="page-break"></div>

<!-- CHAPTER 10 -->
<div id="ch10">
  <h1>Chapter 10: Professional Engineer Review & Approval Gates (Step 6: ENGINEER)</h1>
  <p><strong>Step 6: ENGINEER</strong> provides an auditable review dashboard for licensed engineers and architects.</p>

  <div class="figure-container">
    <img src="__IMG_ENGINEER__" class="figure-img" alt="Engineer Review Dashboard">
    <div class="figure-caption">Figure 10.1: Professional Engineer Review Dashboard showing the G0–G6 verification gates, issue tracker, digital stamp, and export actions.</div>
  </div>

  <h2>10.1 Verification Gates G0–G6</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Gate</th>
        <th style="width: 25%;">Gate Title</th>
        <th style="width: 45%;">Engineering Verification Invariant</th>
        <th style="width: 15%;">Gating Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>G0</strong></td>
        <td>Site Truth Gate</td>
        <td>Boundary coordinates verified against survey evidence. Rejects unverified L0/L1 parcels.</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G1</strong></td>
        <td>Structural Integrity</td>
        <td>Manifold3D watertight 2-manifold solid geometry (Volume > 0, Errors = 0).</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G2</strong></td>
        <td>Architectural Gate</td>
        <td>NBC 2016 room dimensions, clear ceiling heights, and door clearances.</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G3</strong></td>
        <td>MEP Infrastructure</td>
        <td>Preliminary electrical fixture counts and wet stack vertical alignments.</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G4</strong></td>
        <td>Statutory Bye-Laws</td>
        <td>Municipal setback clearances, road widening surrender, and FSI caps.</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G5</strong></td>
        <td>Cost & BOQ Audit</td>
        <td>All BOQ line items map to verified CBM element IDs and regional rate catalogs.</td>
        <td>Strictly Enforced</td>
      </tr>
      <tr>
        <td><strong>G6</strong></td>
        <td>Construction Lock</td>
        <td>Final sign-off gating production drawing issuance and IFC model export.</td>
        <td>Release Gated</td>
      </tr>
    </tbody>
  </table>

  <h2>10.2 Recording Decisions & Digital Stamp Signing</h2>
  <ul>
    <li><strong>Review Issues:</strong> Inspect warnings and compliance issues (e.g., <code>WAR-GEO-001: Geotechnical investigation required</code>).</li>
    <li><strong>Override Permissions:</strong> Senior review engineers can record justification notes to override non-critical warnings.</li>
    <li><strong>Digital Stamp Signing:</strong> Entering a licensed registration number (e.g., <code>PE-STR-MUM-48291</code>) applies a cryptographic signature seal to all exported drawing sheets and reports.</li>
  </ul>

  <h2>10.3 Downloading Project Documents</h2>
  <ul>
    <li><strong>Download A3 Drawing Sheets (PDF):</strong> Opens the <code>DrawingSheetsModal</code> to download architectural drawings (Title Sheet, Site Plan, Ground Plan, Terrace Plan, Sections, Schedules).</li>
    <li><strong>Download Customer Home Report (PDF):</strong> Downloads the customer project summary report.</li>
    <li><strong>Export IFC4 Model:</strong> Downloads the open BIM model for Revit, ArchiCAD, or Solibri.</li>
    <li><strong>Export BOQ Spreadsheet (CSV):</strong> Downloads itemized quantities for tender packaging.</li>
  </ul>
</div>

<div class="page-break"></div>

<!-- CHAPTER 11 -->
<div id="ch11">
  <h1>Chapter 11: Practical Troubleshooting Guide</h1>
  <p>Diagnostic reference for common issues encountered during project execution:</p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Issue / Symptom</th>
        <th style="width: 25%;">Likely Cause</th>
        <th style="width: 30%;">Recommended Safe Action</th>
        <th style="width: 20%;">When to Escalate</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>"Infeasible Setback Collapse" on Feasibility</strong></td>
        <td>Plot area is too small or setbacks exceed plot width (less than 10 m² buildable area).</td>
        <td>Verify road widths. If road width was entered too high, reduce to measured access road.</td>
        <td>If plot is genuinely narrow, escalate to an architect for setback variances.</td>
      </tr>
      <tr>
        <td><strong>"Road Widening Strip Consumes Entire Plot"</strong></td>
        <td>Proposed road width was entered incorrectly (e.g., 30m instead of 12m).</td>
        <td>Check city master plan road width. Update road width in Step 1.</td>
        <td>If widening line is contested, verify with municipal development plan remarks.</td>
      </tr>
      <tr>
        <td><strong>CP-SAT Layout Generation Times Out (> 10s)</strong></td>
        <td>Brief requested too many rooms for the buildable footprint (e.g., 5 BHK in 600 sq ft).</td>
        <td>Reduce bedroom count, or change floor configuration to <code>2 Floors (G+1 Duplex)</code>.</td>
        <td>If solver fails repeatedly on valid plots, check backend API gateway logs.</td>
      </tr>
      <tr>
        <td><strong>"Cannot Lock Build: Release Gated by Site Evidence"</strong></td>
        <td>Project is at site confidence level L0 or L1. System blocks releases without survey data.</td>
        <td>Upload a Total Station survey or municipal CTS cadastral vector in Site Evidence Panel.</td>
        <td>Escalate to licensed land surveyor to conduct on-site monument survey.</td>
      </tr>
      <tr>
        <td><strong>Doorway Opens Across Room Boundary</strong></td>
        <td>Room dimensions were manually mutated beyond host wall extent.</td>
        <td>Click <strong>Reset Layout</strong> in Floor Plan Viewer to restore optimal placement.</td>
        <td>If reset fails, re-generate options from Step 3.</td>
      </tr>
      <tr>
        <td><strong>Cost Estimate Displays "₹0.00"</strong></td>
        <td>Rate snapshot not loaded or model lacks compiled CBM elements.</td>
        <td>Click <strong>Retry</strong> on Cost Summary card. Verify network connection to API gateway.</td>
        <td>If rates remain empty, restart local backend service (<code>apps/api-gateway</code>).</td>
      </tr>
      <tr>
        <td><strong>3D Solid View Shows Missing Walls</strong></td>
        <td>Browser WebGL context lost or Manifold3D library compiling.</td>
        <td>Refresh page or toggle <strong>3D Solid</strong> button in CAD toolbar.</td>
        <td>Ensure Chrome hardware acceleration is enabled in browser settings.</td>
      </tr>
      <tr>
        <td><strong>IFC Export Fails or File is 0 Bytes</strong></td>
        <td>Disk permissions error in local <code>artifacts/</code> folder.</td>
        <td>Verify local disk write permissions in workspace directory.</td>
        <td>Escalate to system administrator.</td>
      </tr>
      <tr>
        <td><strong>Changes to Declared Area Do Not Reflect in Design</strong></td>
        <td>Cached browser session holding previous design version.</td>
        <td>Click <strong>My Project</strong> -> <strong>Clear & Start Fresh</strong>, then re-enter declared plot area.</td>
        <td>Ensure API gateway is running and not returning 304 Not Modified.</td>
      </tr>
      <tr>
        <td><strong>Browser Shows "API Connection Failed / Offline"</strong></td>
        <td>Backend FastAPI server on port 5001 is stopped.</td>
        <td>Run <code>uvicorn apps.api_gateway.main:app --port 5001</code> in terminal workspace.</td>
        <td>Verify port 5001 is not blocked by a local firewall.</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="page-break"></div>

<!-- CHAPTER 12 -->
<div id="ch12">
  <h1>Chapter 12: System Limitations & Safe Use Boundaries</h1>
  <p>To ensure safe, ethical, and legally compliant use, Planwise Enterprise discloses the following operational boundaries:</p>

  <h2>12.1 Security & Multi-Tenancy Prototype Status</h2>
  <ul>
    <li><strong>PostgreSQL Row-Level Security (RLS):</strong> Not active in the current prototype. The application runs as a local single-tenant workspace. Do not deploy to an untrusted public network without adding authentication middleware.</li>
    <li><strong>Session Isolation:</strong> Projects are stored in an in-memory application cache. Clearing the server restarts the baseline project state.</li>
  </ul>

  <h2>12.2 Architectural & Engineering Scope Limits</h2>
  <ul>
    <li><strong>Multi-Floor Generation:</strong> The CP-SAT solver optimizes ground floor layouts directly; upper levels on multi-storey duplexes are generated sequentially using staircase core alignment.</li>
    <li><strong>Structural Finite Element Analysis (FEA):</strong> The platform places structural RCC columns along standard room intersections. It does <strong>not</strong> perform 3D structural frame analysis, wind load calculations, or seismic moment distribution. A licensed Structural Engineer must size all reinforcement rebar and footing dimensions.</li>
    <li><strong>Dynamic MEP Routing:</strong> The system calculates fixture point counts and vertical plumbing stacks; it does not model 3D spatial piping slope or electrical conduit runs.</li>
    <li><strong>Municipal Sanctions:</strong> Planwise generates compliance dossiers, but does <strong>not</strong> connect automatically to municipal sanction portals (e.g., MCGM AutoDCR or BBMP Suvarna). Formal submission requires an architect's council registration number.</li>
    <li><strong>Geotechnical Foundations:</strong> Default foundation excavation depths assume standard empirical soil conditions (150 kN/m²). Actual footing design requires physical soil borehole testing.</li>
  </ul>

  <h2>12.3 Safe Use Notice</h2>
  <div class="callout callout-warning">
    <strong>OPERATIONAL USE POLICY:</strong><br/>
    Planwise outputs support preliminary planning, feasibility analysis, and computational design synthesis. They do NOT constitute statutory municipal sanctions, structural engineering certifications, licensed architectural sign-offs, or authorization to commence construction.<br/><br/>
    Always obtain formal reviews and statutory approvals from qualified professionals and relevant municipal authorities before breaking ground on any construction site.
  </div>
</div>

</body>
</html>
"""
    return tmpl

def main():
    out_dir = ROOT_DIR / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    html_file = out_dir / "planwise_enterprise_user_guide.html"
    pdf_file = ROOT_DIR / "PLANWISE_ENTERPRISE_USER_GUIDE.pdf"

    print("[BUILD] Preloading genuine visual captures as base64...")
    img_land = img_to_base64("artifacts/e2e_live_test/01_1500_land_input.png")
    img_feas = img_to_base64("artifacts/e2e_live_test/02_1500_feasibility.png")
    img_intake = img_to_base64("artifacts/e2e_live_test/03_1500_design_intake.png")
    img_options = img_to_base64("artifacts/e2e_live_test/04_1500_design_options.png")
    img_modal = img_to_base64("artifacts/e2e_live_test/05_1500_my_project_modal.png")
    img_floorplan = img_to_base64("artifacts/e2e_live_test/06_1500_floor_plan_detail.png")
    img_mut_plan = img_to_base64("artifacts/e2e_live_test/07_3bhk_mutation_floor_plan.png")
    img_mut_dim = img_to_base64("artifacts/e2e_live_test/08_room_dimension_mutation.png")
    img_2400 = img_to_base64("artifacts/e2e_live_test/09_2400_floor_plan.png")
    img_10000 = img_to_base64("artifacts/e2e_live_test/10_10000_floor_plan.png")
    img_cost = img_to_base64("artifacts/e2e_live_test/11_cost_summary.png")
    img_build = img_to_base64("artifacts/e2e_live_test/12_build_review.png")
    img_engineer = img_to_base64("artifacts/e2e_live_test/13_engineer_review.png")

    print("[BUILD] Generating User Guide HTML with embedded genuine screenshots...")
    html_content = get_template_html()
    html_content = html_content.replace("__IMG_LAND__", img_land)
    html_content = html_content.replace("__IMG_FEAS__", img_feas)
    html_content = html_content.replace("__IMG_INTAKE__", img_intake)
    html_content = html_content.replace("__IMG_OPTIONS__", img_options)
    html_content = html_content.replace("__IMG_MODAL__", img_modal)
    html_content = html_content.replace("__IMG_FLOORPLAN__", img_floorplan)
    html_content = html_content.replace("__IMG_MUT_PLAN__", img_mut_plan)
    html_content = html_content.replace("__IMG_MUT_DIM__", img_mut_dim)
    html_content = html_content.replace("__IMG_2400__", img_2400)
    html_content = html_content.replace("__IMG_10000__", img_10000)
    html_content = html_content.replace("__IMG_COST__", img_cost)
    html_content = html_content.replace("__IMG_BUILD__", img_build)
    html_content = html_content.replace("__IMG_ENGINEER__", img_engineer)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Wrote HTML guide: {html_file} ({len(html_content):,} bytes)")

    print("[BUILD] Compiling A4 User Guide PDF via Chrome Puppeteer...")
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

    console.log('[PDF BUILD] Generating A4 PDF document with running headers/footers...');
    await page.pdf({{
        path: '{pdf_file}',
        format: 'A4',
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-bottom: 1px solid #cbd5e1; padding: 0 15mm 4px 15mm; display: flex; justify-content: space-between;"><span>PLANWISE ENTERPRISE — STEP-BY-STEP USER GUIDE</span><span>VERSION 2.0.0</span></div>',
        footerTemplate: '<div style="font-size: 8px; color: #64748b; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; width: 100%; border-top: 1px solid #cbd5e1; padding: 4px 15mm 0 15mm; display: flex; justify-content: space-between;"><span>CONFIDENTIAL & PROPRIETARY — PRODUCT MANUAL</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin: {{
            top: '18mm',
            bottom: '18mm',
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
    tmp_js = ROOT_DIR / "scripts" / "render_user_guide_pdf.js"
    with open(tmp_js, "w", encoding="utf-8") as f:
        f.write(puppeteer_script)

    res = subprocess.run(["node", str(tmp_js)], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[ERROR] PDF generation failed:", res.stderr)
        sys.exit(1)

    # Check page count via pypdfium2
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(pdf_file))
        page_count = len(pdf)
        print(f"\n=======================================================")
        print(f"  PLANWISE USER GUIDE PDF GENERATION SUCCESSFUL")
        print(f"  Total Rendered PDF Pages: {page_count} pages")
        print(f"  Output File: {pdf_file}")
        print(f"=======================================================\n")
    except Exception as e:
        print(f"[NOTE] pypdfium2 check: {e}")

if __name__ == "__main__":
    main()
