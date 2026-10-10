/**
 * Planwise Enterprise — Architectural CAD Styling Standards
 * Centralizes all ISO 128 / BIS SP 46 CAD graphical tokens, colors, line weights,
 * typography scales, and drawing sheet layout coordinates.
 */

export interface SheetDimensions {
  width: number;
  height: number;
  viewportWidth: number;
  viewportHeight: number;
  sidebarWidth: number;
  titleBlockHeight: number;
  margin: number;
}

// Standard A3 Landscape Virtual Drafting Canvas (1280 x 880 px)
export const CAD_SHEET: SheetDimensions = {
  width: 1280,
  height: 880,
  viewportWidth: 860,
  viewportHeight: 710,
  sidebarWidth: 380,
  titleBlockHeight: 120,
  margin: 16
};

// Professional CAD Color Palette (High Contrast Monochrome + Restrained Blue Accents)
export const CAD_COLORS = {
  // Sheet & Backgrounds
  sheetBg: '#FFFFFF',
  sheetBorder: '#0F172A',
  innerBorder: '#334155',
  viewportBg: '#FAFAFC',
  sidebarBg: '#F8FAFC',
  tableHeaderBg: '#0F172A',
  tableRowAlt: '#F1F5F9',
  tableBorder: '#CBD5E1',

  // Architectural Linework
  wallExtStroke: '#0F172A',
  wallExtFill: '#F1F5F9',
  wallIntStroke: '#334155',
  wallIntFill: '#FFFFFF',
  wallKnockout: '#FFFFFF',

  // Structural Elements
  columnFill: '#0F172A',
  columnStroke: '#0F172A',
  slabStroke: '#0F172A',
  gridLine: '#64748B',
  gridBubbleBg: '#FFFFFF',
  gridBubbleStroke: '#2563EB',
  gridText: '#0F172A',

  // Openings & Circulation
  doorLeaf: '#0F172A',
  doorSwing: '#2563EB',
  windowOuter: '#0F172A',
  windowGlaze: '#0284C7',
  windowFill: '#FFFFFF',
  stairFill: '#F8FAFC',
  stairTread: '#334155',
  stairLanding: '#0F172A',
  stairArrow: '#2563EB',

  // Annotations & Text
  dimLine: '#1E293B',
  dimTick: '#0F172A',
  dimText: '#0F172A',
  roomTitle: '#0F172A',
  roomArea: '#475569',
  roomDim: '#64748B',
  tagDoor: '#2563EB',
  tagWindow: '#0284C7',

  // Interactive Selection
  selectedFill: 'rgba(2, 132, 199, 0.12)',
  selectedStroke: '#0284C7',
  hoverFill: 'rgba(15, 23, 42, 0.05)',

  // Status & Notes
  statusBadgeBg: '#FEF3C7',
  statusBadgeBorder: '#D97706',
  statusBadgeText: '#92400E',
  disclaimerText: '#64748B'
};

// Line Weight Hierarchy (px)
export const CAD_LINE_WEIGHTS = {
  sheetBorderOuter: 1.8,
  sheetBorderInner: 0.8,
  wallExt: 1.8,
  wallInt: 1.0,
  columnEdge: 1.2,
  slabEdge: 1.2,
  doorLeaf: 1.2,
  doorSwing: 0.8,
  windowFrame: 1.2,
  windowGlaze: 0.6,
  stairTread: 0.7,
  stairNosing: 1.4,
  dimensionLine: 0.75,
  extensionLine: 0.5,
  dimensionTick: 1.2,
  gridLine: 0.6,
  tableBorder: 0.6
};

// Typography Hierarchy
export const CAD_FONTS = {
  family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  titleSheet: 13,
  viewTitle: 11,
  headerSub: 9,
  roomName: 9.5,
  roomNameSmall: 8,
  roomDetail: 7.5,
  roomDetailSmall: 6.5,
  dimText: 7.5,
  scheduleHeader: 7.5,
  scheduleCell: 7,
  notes: 6.8,
  disclaimer: 6.2
};

/**
 * Converts meters to architectural feet and inches string, e.g. 4.20m -> 13'-9"
 */
export const toFtIn = (meters: number): string => {
  if (!meters || isNaN(meters)) return "0'-0\"";
  const totalInches = Math.round(meters * 39.3700787);
  const feet = Math.floor(totalInches / 12);
  const inches = totalInches % 12;
  return `${feet}'-${inches}"`;
};

/**
 * Formats dimensions with both metric and imperial units: e.g. 4.20m x 3.45m [13'-9" x 11'-4"]
 */
export const formatDualDim = (widthM: number, lengthM: number): string => {
  return `${widthM.toFixed(2)}m × ${lengthM.toFixed(2)}m (${toFtIn(widthM)} × ${toFtIn(lengthM)})`;
};

/**
 * Formats area with both square meters and square feet: e.g. 14.50 m² (156 sq ft)
 */
export const formatDualArea = (areaSqm: number): string => {
  const sqft = Math.round(areaSqm * 10.7639);
  return `${areaSqm.toFixed(1)} m² (${sqft} sq ft)`;
};
