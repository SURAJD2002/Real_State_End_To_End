import os
import base64
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ARTIFACTS_DIR = os.path.join(REPO_ROOT, "artifacts")
SCREENSHOTS_DIR = os.path.join(ARTIFACTS_DIR, "e2e_live_test")

MANIFEST_ENTRIES = []

def record_evidence(claim, source_file, function_or_class, test_file, artifact_ref="", status="IMPLEMENTED"):
    MANIFEST_ENTRIES.append({
        "claim": claim,
        "sourceFile": source_file,
        "functionOrClass": function_or_class,
        "testFile": test_file,
        "artifactRef": artifact_ref,
        "status": status
    })

def img_b64(rel_name):
    p = os.path.join(SCREENSHOTS_DIR, rel_name)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

def embed_image_base64(file_path: str, caption: str = "", css_class: str = "") -> str:
    """Reads an image file and returns an HTML img tag with base64 data URI."""
    if not os.path.isabs(file_path):
        file_path = os.path.join(REPO_ROOT, file_path)
    if not os.path.exists(file_path):
        return f'<div class="missing-image">[IMAGE NOT FOUND: {file_path}]</div>'
    with open(file_path, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("utf-8")
    mime = "image/png" if file_path.endswith(".png") else "image/jpeg"
    caption_html = f'<div class="img-caption">{caption}</div>' if caption else ""
    return f'<div class="img-container {css_class}"><img src="data:{mime};base64,{b64_str}" alt="{caption}" />{caption_html}</div>'

def badge(text, b_type="implemented"):
    colors = {
        "implemented": ("#065f46", "#d1fae5", "IMPLEMENTED"),
        "tested": ("#1e40af", "#dbeafe", "TESTED"),
        "browser": ("#5b21b6", "#ede9fe", "BROWSER VERIFIED"),
        "visual": ("#0e7490", "#cffafe", "VISUALLY VERIFIED"),
        "partially": ("#854d0e", "#fef9c3", "PARTIALLY IMPLEMENTED"),
        "experimental": ("#9a3412", "#ffedd5", "EXPERIMENTAL"),
        "test-only": ("#374151", "#f3f4f6", "TEST-ONLY"),
        "planned": ("#475569", "#e2e8f0", "PLANNED"),
        "not-verified": ("#991b1b", "#fee2e2", "NOT VERIFIED"),
        "not-implemented": ("#b91c1c", "#fecaca", "NOT IMPLEMENTED")
    }
    key = b_type.lower().replace(" ", "-")
    c_text, c_bg, default_label = colors.get(key, ("#1f2937", "#f3f4f6", text))
    label = text if text else default_label
    return f'<span class="badge" style="background-color: {c_bg}; color: {c_text}; border: 1px solid {c_text}40;">[{label}]</span>'

# Specific badge helpers
def badge_implemented(): return badge("IMPLEMENTED", "implemented")
def badge_tested(): return badge("TESTED", "tested")
def badge_browser_verified(): return badge("BROWSER VERIFIED", "browser")
def badge_visually_verified(): return badge("VISUALLY VERIFIED", "visual")
def badge_partially_implemented(): return badge("PARTIALLY IMPLEMENTED", "partially")
def badge_experimental(): return badge("EXPERIMENTAL", "experimental")
def badge_test_only(): return badge("TEST-ONLY", "test-only")
def badge_planned(): return badge("PLANNED", "planned")
def badge_not_verified(): return badge("NOT VERIFIED", "not-verified")
def badge_not_implemented(): return badge("NOT IMPLEMENTED", "not-implemented")

def code_block(code: str, lang: str = "python", title: str = "") -> str:
    """Renders a styled syntax highlighted code block with title."""
    header = f'<div class="code-header" style="font-size: 7.5pt; font-weight: 600; color: #94a3b8; background: #1e293b; padding: 3pt 8pt; border-top-left-radius: 3pt; border-top-right-radius: 3pt;">{title or lang.upper()}</div>' if title else ""
    return f'<div class="code-wrapper" style="margin: 2.5mm 0; page-break-inside: avoid;">{header}<pre style="margin-top:0;"><code class="language-{lang}">{code}</code></pre></div>'

def math_block(latex_or_text: str) -> str:
    """Renders a formal mathematical display box."""
    return f'<div class="formula-box">{latex_or_text}</div>'

def alert(title: str, body: str, alert_type: str = "warning") -> str:
    """Renders a GitHub-style alert callout box."""
    type_map = {
        "warning": "callout-warning",
        "danger": "callout-danger",
        "success": "callout-success",
        "note": "callout"
    }
    cls = type_map.get(alert_type.lower(), "callout")
    return f'<div class="callout {cls}"><strong>{title}</strong><div style="margin-top: 1.5mm;">{body}</div></div>'

def table(headers: list, rows: list) -> str:
    """Renders a structured HTML table."""
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    tr_html = []
    for row in rows:
        td_html = "".join(f"<td>{cell}</td>" for cell in row)
        tr_html.append(f"<tr>{td_html}</tr>")
    return f'<table><thead><tr>{th_html}</tr></thead><tbody>{"".join(tr_html)}</tbody></table>'

CSS_STYLES = """
@page {
  size: A4 portrait;
  margin: 18mm 15mm 20mm 15mm;
  @top-left {
    content: "PLANWISE ENTERPRISE — FORENSIC TECHNICAL MASTER REPORT";
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 7pt;
    font-weight: 700;
    color: #475569;
    border-bottom: 0.5pt solid #cbd5e1;
    padding-bottom: 4px;
    margin-bottom: 8px;
  }
  @top-right {
    content: "SYSTEM VERSION 2.0.0 • COMMIT d678846 • STRICT ZERO-FABRICATION AUDIT";
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 7pt;
    color: #64748b;
    border-bottom: 0.5pt solid #cbd5e1;
    padding-bottom: 4px;
    margin-bottom: 8px;
  }
  @bottom-left {
    content: "CONFIDENTIAL & PROPRIETARY — STRICT SOURCE-GROUNDED TECHNICAL AUDIT";
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 6.5pt;
    color: #94a3b8;
    border-top: 0.5pt solid #cbd5e1;
    padding-top: 4px;
  }
  @bottom-right {
    content: "Page " counter(page) " of " counter(pages);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 7.5pt;
    font-weight: 600;
    color: #334155;
    border-top: 0.5pt solid #cbd5e1;
    padding-top: 4px;
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 9pt;
  line-height: 1.45;
  color: #0f172a;
  background-color: #ffffff;
  margin: 0;
  padding: 0;
}

.cover-page {
  padding-top: 25mm;
  padding-bottom: 20mm;
}

.cover-logo-badge {
  display: inline-block;
  background: #0f172a;
  color: #38bdf8;
  font-weight: 800;
  font-size: 11pt;
  letter-spacing: 2px;
  padding: 4pt 10pt;
  border-radius: 4pt;
  margin-bottom: 8mm;
}

h1.cover-title {
  font-size: 26pt;
  line-height: 1.15;
  font-weight: 800;
  color: #0f172a;
  margin-top: 5mm;
  margin-bottom: 4mm;
  letter-spacing: -0.5px;
}

h2.cover-subtitle {
  font-size: 13pt;
  line-height: 1.35;
  font-weight: 500;
  color: #2563eb;
  margin-top: 0;
  margin-bottom: 12mm;
}

.cover-meta {
  background-color: #f8fafc;
  border: 1pt solid #e2e8f0;
  border-radius: 4pt;
  padding: 8pt 10pt;
  margin-bottom: 6mm;
  font-size: 8.5pt;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5mm;
}

.meta-item {
  color: #334155;
}

.table-of-contents {
  margin-top: 10mm;
  margin-bottom: 10mm;
}

.toc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2mm 8mm;
  margin-top: 4mm;
}

.toc-item {
  font-size: 8pt;
  display: flex;
  justify-content: space-between;
  border-bottom: 0.5pt dotted #cbd5e1;
  padding-bottom: 1pt;
}

.toc-num {
  font-weight: 700;
  color: #2563eb;
  margin-right: 4pt;
}

.toc-title {
  color: #1e293b;
}

.report-section {
  margin-bottom: 6mm;
}

.section-header {
  border-bottom: 1.5pt solid #2563eb;
  padding-bottom: 2.5mm;
  margin-top: 6mm;
  margin-bottom: 3.5mm;
  page-break-after: avoid;
}

.section-number {
  font-size: 8pt;
  font-weight: 800;
  text-transform: uppercase;
  color: #2563eb;
  letter-spacing: 1px;
  display: block;
  margin-bottom: 1mm;
}

h1 {
  font-size: 15pt;
  line-height: 1.25;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 1.5pt solid #2563eb;
  padding-bottom: 2.5mm;
  margin-top: 6mm;
  margin-bottom: 3.5mm;
  page-break-after: avoid;
}

.section-header h2 {
  font-size: 14pt;
  line-height: 1.25;
  font-weight: 700;
  color: #0f172a;
  border-left: none;
  padding-left: 0;
  margin: 0;
}

.status-badges {
  margin-top: 2mm;
}

h2 {
  font-size: 11.5pt;
  line-height: 1.3;
  font-weight: 600;
  color: #1e293b;
  margin-top: 4.5mm;
  margin-bottom: 2mm;
  border-left: 3pt solid #2563eb;
  padding-left: 2mm;
  page-break-after: avoid;
}

h3 {
  font-size: 9.8pt;
  line-height: 1.3;
  font-weight: 600;
  color: #334155;
  margin-top: 3.5mm;
  margin-bottom: 1.5mm;
  page-break-after: avoid;
}

p {
  margin-top: 0;
  margin-bottom: 2.5mm;
  text-align: justify;
}

p.lead-text {
  font-size: 9.5pt;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 3.5mm;
}

ul, ol {
  margin-top: 0;
  margin-bottom: 2.5mm;
  padding-left: 5mm;
}

li {
  margin-bottom: 1mm;
}

.page-break {
  page-break-before: always;
}

.avoid-break {
  page-break-inside: avoid;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 7.8pt;
  margin-top: 2.5mm;
  margin-bottom: 3.5mm;
  page-break-inside: auto;
}

tr {
  page-break-inside: avoid;
  page-break-after: auto;
}

th, td {
  border: 0.5pt solid #cbd5e1;
  padding: 4.5pt 5.5pt;
  vertical-align: top;
  text-align: left;
}

th {
  background-color: #f1f5f9;
  font-weight: 700;
  color: #0f172a;
}

tr:nth-child(even) td {
  background-color: #f8fafc;
}

code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  font-size: 7.6pt;
  background-color: #f1f5f9;
  padding: 1pt 3pt;
  border-radius: 2pt;
  border: 0.5pt solid #e2e8f0;
  color: #0f172a;
}

pre {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  font-size: 7.2pt;
  line-height: 1.35;
  background-color: #0f172a;
  color: #f8fafc;
  padding: 6pt 8pt;
  border-radius: 3pt;
  overflow-x: auto;
  margin-top: 2mm;
  margin-bottom: 3.5mm;
  page-break-inside: avoid;
}

pre code {
  background-color: transparent;
  color: #f8fafc;
  border: none;
  padding: 0;
}

.badge {
  display: inline-block;
  font-size: 6.8pt;
  font-weight: 700;
  padding: 1pt 3.5pt;
  border-radius: 2pt;
  text-transform: uppercase;
  margin-right: 2pt;
  vertical-align: middle;
}

.callout {
  border-left: 3pt solid #2563eb;
  background-color: #f8fafc;
  padding: 4pt 7pt;
  margin-top: 2.5mm;
  margin-bottom: 3mm;
  font-size: 8.2pt;
  page-break-inside: avoid;
}

.callout-warning {
  border-left-color: #d97706;
  background-color: #fffbeb;
}

.callout-danger {
  border-left-color: #dc2626;
  background-color: #fef2f2;
}

.callout-success {
  border-left-color: #059669;
  background-color: #ecfdf5;
}

.formula-box {
  background-color: #f8fafc;
  border: 1pt solid #cbd5e1;
  border-left: 3.5pt solid #0284c7;
  padding: 5pt 8pt;
  margin: 2.5mm 0;
  font-family: "Cambria Math", "Times New Roman", serif;
  font-size: 8.8pt;
  page-break-inside: avoid;
}

.img-container {
  text-align: center;
  margin: 3mm 0;
  page-break-inside: avoid;
}

.img-container img {
  max-width: 95%;
  max-height: 110mm;
  border: 0.5pt solid #cbd5e1;
  border-radius: 3pt;
  box-shadow: 0 1pt 3pt rgba(0,0,0,0.08);
}

.img-caption {
  font-size: 7.2pt;
  color: #64748b;
  margin-top: 1.5mm;
  font-style: italic;
}

.figure-container {
  margin: 4mm 0;
  page-break-inside: avoid;
}

.figure-description {
  font-size: 7.5pt;
  color: #475569;
  margin-top: 1mm;
  text-align: center;
}

.svg-diagram {
  display: block;
  margin: 3mm auto;
  max-width: 100%;
  page-break-inside: avoid;
}

.ascii-flow {
  background: #0f172a;
  color: #38bdf8;
  font-size: 7.2pt;
  line-height: 1.25;
  padding: 6pt;
  border-radius: 4pt;
}
"""

def get_base_css():
    return CSS_STYLES
