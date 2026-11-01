"""
Planwise Enterprise — Technical Encyclopedia Common Formatting & CSS
Defines print-perfect typography, A4 page geometries, table styling, code formatting,
and reusable SVG diagrams for the 200-300+ page technical reference.
"""

def get_encyclopedia_css() -> str:
    return """
    @page {
        size: A4 portrait;
        margin-top: 20mm;
        margin-bottom: 20mm;
        margin-left: 16mm;
        margin-right: 16mm;
        @top-center {
            content: "PLANWISE ENTERPRISE — COMPLETE APPLICATION TECHNICAL ENCYCLOPEDIA";
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
            border-bottom: 0.5pt solid #cbd5e1;
            padding-bottom: 3mm;
            width: 100%;
        }
        @bottom-left {
            content: "CONFIDENTIAL & PROPRIETARY — STRICT ZERO-FABRICATION FORENSIC AUDIT";
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 7.5pt;
            color: #64748b;
        }
        @bottom-right {
            content: "Page " counter(page);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 7.5pt;
            font-weight: bold;
            color: #0f172a;
        }
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8.5pt;
        line-height: 1.45;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }

    .cover-page {
        page-break-after: always;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 40px 20px;
        box-sizing: border-box;
    }

    .cover-badge {
        display: inline-block;
        background: #1e293b;
        color: #f8fafc;
        font-size: 9pt;
        font-weight: 700;
        letter-spacing: 2px;
        padding: 6px 16px;
        border-radius: 4px;
        margin-bottom: 24px;
        text-transform: uppercase;
    }

    .cover-title {
        font-size: 26pt;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.15;
        margin: 0 0 16px 0;
        max-width: 900px;
    }

    .cover-subtitle {
        font-size: 13pt;
        font-weight: 500;
        color: #334155;
        line-height: 1.4;
        margin: 0 0 32px 0;
        max-width: 800px;
    }

    .cover-meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        max-width: 750px;
        width: 100%;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: left;
        margin-bottom: 24px;
    }

    .meta-item {
        font-size: 8pt;
        color: #475569;
    }

    .meta-item strong {
        color: #0f172a;
    }

    .toc-page {
        page-break-after: always;
        padding-top: 10px;
    }

    .toc-title {
        font-size: 18pt;
        font-weight: 800;
        color: #0f172a;
        border-bottom: 2pt solid #0f172a;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    .toc-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }

    .toc-item {
        font-size: 8.5pt;
        margin-bottom: 8px;
        line-height: 1.35;
    }

    .toc-volume-num {
        font-weight: bold;
        color: #2563eb;
    }

    .volume-header {
        page-break-before: always;
        margin-top: 10px;
        margin-bottom: 20px;
        border-bottom: 2pt solid #1e293b;
        padding-bottom: 8px;
    }

    .volume-badge {
        font-size: 8pt;
        font-weight: 700;
        text-transform: uppercase;
        color: #2563eb;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }

    h1 {
        font-size: 18pt;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0 10px 0;
        line-height: 1.2;
    }

    h2 {
        font-size: 12.5pt;
        font-weight: 700;
        color: #1e293b;
        margin: 16px 0 8px 0;
        border-bottom: 0.5pt solid #e2e8f0;
        padding-bottom: 4px;
        page-break-after: avoid;
    }

    h3 {
        font-size: 10pt;
        font-weight: 700;
        color: #334155;
        margin: 12px 0 6px 0;
        page-break-after: avoid;
    }

    h4 {
        font-size: 9pt;
        font-weight: 600;
        color: #475569;
        margin: 10px 0 4px 0;
        page-break-after: avoid;
    }

    p {
        margin: 0 0 8px 0;
        text-align: justify;
    }

    ul, ol {
        margin: 0 0 10px 0;
        padding-left: 18px;
    }

    li {
        margin-bottom: 4px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 7.5pt;
        margin: 10px 0 14px 0;
        page-break-inside: avoid;
    }

    th {
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        text-align: left;
        padding: 5px 7px;
        border: 0.5pt solid #cbd5e1;
        font-size: 7.5pt;
    }

    td {
        padding: 4.5px 7px;
        border: 0.5pt solid #e2e8f0;
        vertical-align: top;
    }

    tr:nth-child(even) {
        background-color: #f8fafc;
    }

    .badge-verified {
        display: inline-block;
        background-color: #dcfce7;
        color: #15803d;
        font-size: 6.5pt;
        font-weight: 700;
        padding: 1.5px 5px;
        border-radius: 3px;
        border: 0.5pt solid #86efac;
        text-transform: uppercase;
    }

    .badge-partial {
        display: inline-block;
        background-color: #fef9c3;
        color: #a16207;
        font-size: 6.5pt;
        font-weight: 700;
        padding: 1.5px 5px;
        border-radius: 3px;
        border: 0.5pt solid #fde047;
        text-transform: uppercase;
    }

    .badge-failed {
        display: inline-block;
        background-color: #fee2e2;
        color: #b91c1c;
        font-size: 6.5pt;
        font-weight: 700;
        padding: 1.5px 5px;
        border-radius: 3px;
        border: 0.5pt solid #fca5a5;
        text-transform: uppercase;
    }

    .callout {
        background: #f8fafc;
        border-left: 3pt solid #3b82f6;
        padding: 8px 12px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8pt;
    }

    .callout-warning {
        background: #fffbeb;
        border-left: 3pt solid #f59e0b;
        padding: 8px 12px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8pt;
    }

    .callout-critical {
        background: #fef2f2;
        border-left: 3pt solid #ef4444;
        padding: 8px 12px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8pt;
    }

    pre {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
        font-size: 7pt;
        line-height: 1.35;
        padding: 8px 10px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 8px 0 12px 0;
        page-break-inside: avoid;
    }

    code {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
        font-size: 7.5pt;
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 1px 3px;
        border-radius: 3px;
        border: 0.5pt solid #e2e8f0;
    }

    pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        font-size: 7pt;
    }

    .diagram-container {
        margin: 14px 0;
        text-align: center;
        page-break-inside: avoid;
    }

    .diagram-caption {
        font-size: 7.5pt;
        color: #475569;
        font-style: italic;
        margin-top: 4px;
    }

    .screenshot-img {
        max-width: 100%;
        height: auto;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        margin: 8px 0;
    }

    .page-break {
        page-break-before: always;
    }
    """
