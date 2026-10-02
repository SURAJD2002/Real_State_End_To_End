"""
Planwise Enterprise — Deterministic BOQ & Cost Export Engine
Delta Specification & M3 Master Specification §20

Generates CSV, XLSX-compatible XML, JSON, and printable HTML/PDF summaries
strictly consuming the authoritative CostEstimate object.
No secondary or diverging calculations.
"""

import io
import csv
import json
from typing import Dict, Any
from packages.schemas.cost_model import CostEstimate


class CostEstimateExporter:
    """Exports CostEstimate into standard formats."""

    @staticmethod
    def to_json(estimate: CostEstimate) -> str:
        """Returns pretty-printed machine-readable JSON."""
        return json.dumps(estimate.dict(), indent=2, sort_keys=True)

    @staticmethod
    def to_csv(estimate: CostEstimate) -> str:
        """Returns standard CSV of all BOQ items with cost waterfall summary."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header block
        writer.writerow(["PLANWISE ENTERPRISE — BILL OF QUANTITIES & COST ESTIMATE"])
        writer.writerow(["Estimate ID", estimate.estimateId])
        writer.writerow(["Design Version ID", estimate.designVersionId])
        writer.writerow(["Rate Snapshot", estimate.rateSnapshotId])
        writer.writerow(["Quality Tier", estimate.qualityTier])
        writer.writerow(["Calculated At", estimate.calculatedAt])
        writer.writerow([])

        # Table header
        writer.writerow([
            "Item Code",
            "Section",
            "Description",
            "Specification",
            "Quantity",
            "Unit",
            "Material Rate (INR)",
            "Labour Rate (INR)",
            "Equipment Rate (INR)",
            "Unit Rate (INR)",
            "Amount (INR)",
            "Confidence",
            "Source Type",
            "Measurement Rule",
            "CBM Element Count"
        ])

        for line in estimate.boqLines:
            writer.writerow([
                line.itemCode,
                line.section,
                line.description,
                line.specification,
                line.quantity,
                line.unit,
                line.materialRate,
                line.labourRate,
                line.equipmentRate,
                line.unitRate,
                line.amount,
                line.confidence.value if hasattr(line.confidence, "value") else str(line.confidence),
                line.sourceType.value if hasattr(line.sourceType, "value") else str(line.sourceType),
                line.measurementRuleId,
                len(line.sourceElementIds)
            ])

        # Waterfall summary
        wf = estimate.costWaterfall
        writer.writerow([])
        writer.writerow(["COST WATERFALL BREAKDOWN"])
        writer.writerow(["Direct Raw Materials", wf.directMaterialCost])
        writer.writerow(["Direct Site Labour", wf.directLabourCost])
        writer.writerow(["Plant & Equipment", wf.directEquipmentCost])
        writer.writerow(["Material Wastage Allowance", wf.materialWastageCost])
        writer.writerow(["Gross Direct Hard Cost", wf.grossHardCost])
        writer.writerow(["Contractor Prelims & Site Overheads (8%)", wf.overheadAndPrelims])
        writer.writerow(["Physical Contingency Buffer (5%)", wf.contingency])
        writer.writerow(["Statutory Taxes (18% if applied)", wf.statutoryTaxes])
        writer.writerow(["Total Preliminary Construction Cost", wf.totalConstructionCost])
        writer.writerow(["Cost per Sq.Ft (BUA)", wf.costPerSqFtBUA])
        writer.writerow(["Cost per Sq.M (BUA)", wf.costPerSqmBUA])
        writer.writerow(["Cost per Carpet Sq.Ft", wf.costPerCarpetSqFt])
        writer.writerow(["Cost per Carpet Sq.M", wf.costPerCarpetSqm])
        writer.writerow([])
        writer.writerow(["DISCLAIMER", estimate.disclaimer])

        return output.getvalue()

    @staticmethod
    def to_xlsx_xml(estimate: CostEstimate) -> str:
        """
        Generates standard Microsoft Excel 2003 XML spreadsheet (native Excel format).
        Opens directly in Microsoft Excel, Google Sheets, LibreOffice Calc.
        """
        wf = estimate.costWaterfall
        lines_xml = []
        for line in estimate.boqLines:
            lines_xml.append(f"""
            <Row>
                <Cell><Data ss:Type="String">{line.itemCode}</Data></Cell>
                <Cell><Data ss:Type="String">{line.section}</Data></Cell>
                <Cell><Data ss:Type="String">{line.description}</Data></Cell>
                <Cell><Data ss:Type="Number">{line.quantity}</Data></Cell>
                <Cell><Data ss:Type="String">{line.unit}</Data></Cell>
                <Cell><Data ss:Type="Number">{line.unitRate}</Data></Cell>
                <Cell><Data ss:Type="Number">{line.amount}</Data></Cell>
                <Cell><Data ss:Type="String">{line.confidence.value if hasattr(line.confidence, 'value') else line.confidence}</Data></Cell>
                <Cell><Data ss:Type="String">{line.measurementRuleId}</Data></Cell>
            </Row>""")

        xml = f"""<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <Worksheet ss:Name="BOQ_Cost_Schedule">
  <Table>
   <Row>
    <Cell><Data ss:Type="String">Planwise Enterprise — {estimate.estimateId}</Data></Cell>
   </Row>
   <Row>
    <Cell><Data ss:Type="String">Rate Snapshot: {estimate.rateSnapshotId} | Tier: {estimate.qualityTier}</Data></Cell>
   </Row>
   <Row><Cell><Data ss:Type="String"></Data></Cell></Row>
   <Row>
    <Cell><Data ss:Type="String">Item Code</Data></Cell>
    <Cell><Data ss:Type="String">Section</Data></Cell>
    <Cell><Data ss:Type="String">Description</Data></Cell>
    <Cell><Data ss:Type="String">Quantity</Data></Cell>
    <Cell><Data ss:Type="String">Unit</Data></Cell>
    <Cell><Data ss:Type="String">Rate (INR)</Data></Cell>
    <Cell><Data ss:Type="String">Amount (INR)</Data></Cell>
    <Cell><Data ss:Type="String">Confidence</Data></Cell>
    <Cell><Data ss:Type="String">Rule</Data></Cell>
   </Row>
   {''.join(lines_xml)}
   <Row><Cell><Data ss:Type="String"></Data></Cell></Row>
   <Row>
    <Cell><Data ss:Type="String">TOTAL CONSTRUCTION COST (INR)</Data></Cell>
    <Cell><Data ss:Type="Number">{wf.totalConstructionCost}</Data></Cell>
   </Row>
   <Row>
    <Cell><Data ss:Type="String">Cost / Sq.Ft BUA (INR)</Data></Cell>
    <Cell><Data ss:Type="Number">{wf.costPerSqFtBUA}</Data></Cell>
   </Row>
  </Table>
 </Worksheet>
</Workbook>"""
        return xml

    @staticmethod
    def to_html_summary(estimate: CostEstimate) -> str:
        """Generates self-contained, printable HTML/PDF executive cost report."""
        wf = estimate.costWaterfall
        rows = "".join(
            f"""<tr>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0; font-family:monospace; font-weight:600;">{l.itemCode}</td>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0;">{l.description}</td>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0; text-align:right;">{l.quantity:.2f} {l.unit}</td>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0; text-align:right;">₹{l.unitRate:,.2f}</td>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0; text-align:right; font-weight:600;">₹{l.amount:,.2f}</td>
                <td style="padding:6px 10px; border-bottom:1px solid #e2e8f0; text-align:center;"><span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:11px;">{l.confidence.value if hasattr(l.confidence, 'value') else l.confidence}</span></td>
            </tr>"""
            for l in estimate.boqLines
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Preliminary Cost Estimate — {estimate.estimateId}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #1e293b; }}
h1 {{ margin: 0 0 4px 0; color: #0f172a; font-size: 24px; }}
.badge {{ display: inline-block; background: #0284c7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
.card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 20px 0; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 12px; }}
.metric-box {{ background: white; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; }}
.metric-val {{ font-size: 20px; font-weight: 700; color: #0f172a; }}
.metric-lbl {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; margin-top: 4px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
th {{ background: #f1f5f9; padding: 8px 10px; text-align: left; font-size: 12px; text-transform: uppercase; color: #475569; }}
.disclaimer {{ font-size: 11px; color: #64748b; line-height: 1.5; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 12px; }}
</style>
</head>
<body>
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <h1>PLANWISE ENTERPRISE</h1>
            <div style="color:#64748b; font-size:14px;">Preliminary Model-Linked Cost Estimate & BOQ</div>
        </div>
        <div style="text-align:right;">
            <span class="badge">{estimate.qualityTier} TIER</span>
            <div style="font-family:monospace; font-size:12px; margin-top:6px; color:#64748b;">Snapshot: {estimate.rateSnapshotId}</div>
        </div>
    </div>

    <div class="card">
        <div style="font-size:13px; font-weight:600; color:#334155;">COST WATERFALL OVERVIEW</div>
        <div class="grid">
            <div class="metric-box">
                <div class="metric-val">₹{wf.totalConstructionCost/100000:.2f} L</div>
                <div class="metric-lbl">Total Estimated Cost</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">₹{wf.costPerSqFtBUA:.0f} / sq.ft</div>
                <div class="metric-lbl">Built-Up Area Rate</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">₹{wf.directMaterialCost/100000:.2f} L</div>
                <div class="metric-lbl">Direct Raw Materials</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">₹{wf.directLabourCost/100000:.2f} L</div>
                <div class="metric-lbl">Direct Skilled Labour</div>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width:10%;">Code</th>
                <th style="width:40%;">Trade Description</th>
                <th style="width:12%; text-align:right;">Qty</th>
                <th style="width:12%; text-align:right;">Rate</th>
                <th style="width:14%; text-align:right;">Amount</th>
                <th style="width:12%; text-align:center;">Confidence</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <div class="disclaimer">
        <strong>Statutory Notice:</strong> {estimate.disclaimer}<br/>
        Deterministic Fingerprints: QTO={estimate.qtoHash[:16]}... | BOQ={estimate.boqHash[:16]}... | Cost={estimate.costHash[:16]}...
    </div>
</body>
</html>"""
        return html
