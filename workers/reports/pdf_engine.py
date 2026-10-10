"""
Planwise Enterprise — Core PDF Engine & Typography Architecture
===============================================================
Provides professional A4/A3 architectural documentation styling,
two-pass running headers/footers with 'Page X of Y' numbering,
flowable helpers, and strict branding for external distribution.
"""

import os
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
pt = 1

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Flowable, Image
)
from reportlab.pdfgen import canvas

# -------------------------------------------------------------
# Color Palette (Deep Slate, Warm Charcoal, Brand Accent Blue)
# -------------------------------------------------------------
COLOR_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
COLOR_SECONDARY = colors.HexColor("#1E293B")  # Dark Slate
COLOR_BRAND_BLUE = colors.HexColor("#2563EB") # Planwise Blue
COLOR_BRAND_CYAN = colors.HexColor("#0284C7") # Sky Cyan
COLOR_ACCENT_GREEN = colors.HexColor("#059669") # Verification Green
COLOR_ACCENT_AMBER = colors.HexColor("#D97706") # Warning Amber
COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")   # Crisp Off-white
COLOR_CARD_BG = colors.HexColor("#F1F5F9")    # Light Slate
COLOR_BORDER = colors.HexColor("#CBD5E1")     # Light Border
COLOR_TEXT_MAIN = colors.HexColor("#0F172A")  # Main Text
COLOR_TEXT_MUTED = colors.HexColor("#64748B") # Secondary Muted
COLOR_TEXT_LIGHT = colors.HexColor("#94A3B8") # Subtle Muted
COLOR_WHITE = colors.HexColor("#FFFFFF")


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that accumulates total page count and adds
    running headers, footers, and 'Page X of Y' page numbers.
    Suppresses headers and footers on Cover page (page 1).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.project_name = "Bandra West Residential Development"
        self.design_version_id = "DV-OPT-B-9be0a983"
        self.release_id = ""
        self.confidential_text = "CONFIDENTIAL & PROPRIETARY — PRELIMINARY COMPUTATIONAL REPORT"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        # Suppress on Cover (Page 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(COLOR_TEXT_MUTED)

        w, h = self._pagesize

        # Running Top Header
        header_y = h - 28
        self.drawString(36, header_y, "PLANWISE ENTERPRISE")
        self.setFont("Helvetica", 7.5)
        self.drawString(145, header_y, f"•   PROJECT: {self.project_name[:35]}")
        self.drawRightString(w - 36, header_y, f"VERSION: {self.design_version_id}")

        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(36, header_y - 4, w - 36, header_y - 4)

        # Running Bottom Footer
        footer_y = 25
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(36, footer_y + 10, w - 36, footer_y + 10)

        self.setFont("Helvetica", 7)
        self.drawString(36, footer_y, self.confidential_text)
        self.setFont("Helvetica-Bold", 7.5)
        self.drawRightString(w - 36, footer_y, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


def get_report_stylesheet():
    """Generates a cohesive typography stylesheet for Planwise documents."""
    styles = getSampleStyleSheet()

    # Document Title
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    ))

    # Document Subtitle
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=COLOR_BRAND_CYAN,
        spaceAfter=15
    ))

    # Section Heading (H1)
    styles.add(ParagraphStyle(
        name="SectionH1",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))

    # Subsection Heading (H2)
    styles.add(ParagraphStyle(
        name="SectionH2",
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=COLOR_BRAND_BLUE,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))

    # Category Pill / Eyebrow
    styles.add(ParagraphStyle(
        name="Eyebrow",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=COLOR_BRAND_BLUE,
        textTransform="uppercase",
        spaceAfter=4
    ))

    # Standard Body Text
    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT_MAIN,
        spaceAfter=6
    ))

    # Muted Body Text
    styles.add(ParagraphStyle(
        name="ReportBodyMuted",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_TEXT_MUTED,
        spaceAfter=4
    ))

    # Small Notice / Caption
    styles.add(ParagraphStyle(
        name="ReportCaption",
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=COLOR_TEXT_MUTED,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=6
    ))

    # Table Cell Normal
    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN
    ))

    # Table Cell Bold
    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN
    ))

    # Table Header Cell
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_WHITE
    ))

    # Table Cell Right (for amounts/numbers)
    styles.add(ParagraphStyle(
        name="TableCellRight",
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN,
        alignment=TA_RIGHT
    ))

    styles.add(ParagraphStyle(
        name="TableCellRightBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_TEXT_MAIN,
        alignment=TA_RIGHT
    ))

    return styles


def create_section_header(title: str, eyebrow: Optional[str] = None, styles=None) -> List[Flowable]:
    """Builds a standardized visual section header with eyebrow and divider line."""
    if not styles:
        styles = get_report_stylesheet()

    flowables = []
    if eyebrow:
        flowables.append(Paragraph(eyebrow.upper(), styles["Eyebrow"]))
    flowables.append(Paragraph(title, styles["SectionH1"]))
    flowables.append(HRFlowable(
        width="100%", thickness=1, color=COLOR_BRAND_BLUE,
        spaceBefore=2, spaceAfter=8
    ))
    return flowables


def create_callout_box(
    text: str,
    title: Optional[str] = None,
    alert_type: str = "INFO",
    width: float = 523.0
) -> Table:
    """
    Creates an architectural alert/callout box with colored left border.
    alert_type: 'INFO' (blue), 'SUCCESS' (green), 'WARNING' (amber), 'ERROR' (red)
    """
    styles = get_report_stylesheet()

    border_color = COLOR_BRAND_BLUE
    bg_color = colors.HexColor("#EFF6FF") # Light blue

    if alert_type == "SUCCESS":
        border_color = COLOR_ACCENT_GREEN
        bg_color = colors.HexColor("#ECFDF5")
    elif alert_type == "WARNING":
        border_color = COLOR_ACCENT_AMBER
        bg_color = colors.HexColor("#FFFBEB")
    elif alert_type == "ERROR":
        border_color = colors.HexColor("#DC2626")
        bg_color = colors.HexColor("#FEF2F2")

    content = []
    if title:
        content.append(Paragraph(f"<b>{title}</b>", styles["TableCellBold"]))
    content.append(Paragraph(text, styles["TableCell"]))

    t = Table([[content]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('LINELEFT', (0, 0), (0, -1), 3.0, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def create_kpi_cards_table(cards: List[Dict[str, str]], width: float = 523.0) -> Table:
    """
    Renders 2, 3, or 4 KPI summary cards across a single horizontal row.
    cards: [{'label': 'PLOT AREA', 'value': '1,100 sq ft', 'sub': '102.19 sqm'}, ...]
    """
    styles = get_report_stylesheet()
    n = len(cards)
    col_w = width / n

    row_data = []
    for c in cards:
        cell_flowables = [
            Paragraph(c.get("label", "").upper(), styles["Eyebrow"]),
            Spacer(1, 1),
            Paragraph(f"<b>{c.get('value', '')}</b>", styles["SectionH2"]),
            Spacer(1, 1),
            Paragraph(c.get("sub", ""), styles["ReportCaption"])
        ]
        row_data.append(cell_flowables)

    t = Table([row_data], colWidths=[col_w] * n)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_CARD_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t
