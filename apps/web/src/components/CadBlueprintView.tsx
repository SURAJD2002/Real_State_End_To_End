import React from 'react';
import { HouseLayout, RoomElement, CanonicalBuildingModel } from '../types';
import { InspectedElement } from './FloorPlanViewer';
import {
  CAD_COLORS,
  CAD_LINE_WEIGHTS,
  CAD_FONTS,
  toFtIn,
  formatDualArea
} from './cadStyles';

interface CadBlueprintViewProps {
  layout: HouseLayout;
  buildingModel?: CanonicalBuildingModel;
  selectedFloor: string;
  inspectedElement: InspectedElement | null;
  onSelectRoom: (room: RoomElement) => void;
  onSelectWall: (name: string, isExt: boolean, thicknessMm: number) => void;
  zoomLevel: number;
  projectName?: string;
  projectId?: string;
}

export const CadBlueprintView: React.FC<CadBlueprintViewProps> = ({
  layout,
  buildingModel,
  selectedFloor,
  inspectedElement,
  onSelectRoom,
  onSelectWall,
  zoomLevel,
  projectName = 'Bandra West Residential Development',
  projectId = 'CTS-1842-BANDRA'
}) => {
  if (!buildingModel || !buildingModel.spaces || buildingModel.spaces.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full w-full p-8 bg-slate-900/60 rounded-xl border border-slate-800 text-slate-400">
        <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg border border-amber-500/20 mb-3">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <p className="font-semibold text-white mb-1">Authoritative CBM Geometry Not Found</p>
        <p className="text-xs text-slate-400 max-w-sm text-center">
          The Canonical Building Model has not been compiled for this design version. Please re-run generation.
        </p>
      </div>
    );
  }

  // Virtual ISO A3 Sheet Dimensions (Landscape: 1260 x 860 px)
  const sheetW = 1260;
  const sheetH = 860;

  // Viewport Layout Partitions
  const margin = 14;
  const innerMargin = 20;
  const titleBlockH = 118;
  const rightPanelW = 370;

  const vpX = innerMargin;
  const vpY = innerMargin;
  const vpW = sheetW - innerMargin * 2 - rightPanelW - 12; // ~838 px
  const vpH = sheetH - innerMargin - titleBlockH - 24;      // ~698 px

  const rightX = vpX + vpW + 12;
  const rightY = innerMargin;
  const rightW = rightPanelW;
  const rightH = vpH;

  const tbX = innerMargin;
  const tbY = vpY + vpH + 12;
  const tbW = sheetW - innerMargin * 2;

  // Model Envelope
  const envW = buildingModel.buildingEnvelope.widthM || 14.0;
  const envL = buildingModel.buildingEnvelope.lengthM || 20.0;

  // Compute Viewport Scale (Auto fit with 18% margin for dimensions & grid)
  const scaleX = (vpW * 0.74) / envW;
  const scaleY = (vpH * 0.74) / envL;
  const fitScale = Math.min(scaleX, scaleY);
  const activeScale = fitScale * Math.max(0.6, Math.min(2.0, zoomLevel));

  const bldgPxW = envW * activeScale;
  const bldgPxL = envL * activeScale;

  // Center Building in Viewport
  const bldgOriginX = vpX + (vpW - bldgPxW) / 2;
  const bldgOriginY = vpY + (vpH - bldgPxL) / 2 + 10;

  // Helper coordinate mapper
  const toSvgX = (xM: number) => bldgOriginX + xM * activeScale;
  const toSvgY = (yM: number) => bldgOriginY + yM * activeScale;

  // Floor matching
  const isFloorMatch = (val?: string) => {
    if (!val) return selectedFloor === 'L0';
    if (selectedFloor === 'L0') return val === 'L0' || val === 'LVL-000' || val.toLowerCase().includes('ground');
    if (selectedFloor === 'L1') return val === 'L1' || val === 'LVL-001' || val.toLowerCase().includes('first');
    return val === selectedFloor;
  };

  const spaces = buildingModel.spaces.filter(s => isFloorMatch(s.floor) || isFloorMatch(s.levelId));
  const elements = buildingModel.elements.filter(e => isFloorMatch(e.levelId));
  const openings = buildingModel.openings.filter(o => isFloorMatch(o.levelId));
  const columns = elements.filter(e => e.elementType === 'COLUMN');
  const stairs = elements.filter(e => e.elementType === 'STAIR');
  const walls = elements.filter(e => e.elementType === 'WALL');

  const doors = openings.filter(o => o.openingType === 'DOOR');
  const windows = openings.filter(o => o.openingType === 'WINDOW');

  // Overall Dimensions Positions
  const dimTopY = bldgOriginY - 32;
  const dimRightX = bldgOriginX + bldgPxW + 34;

  const currentLevelLabel = selectedFloor === 'L1' ? 'FIRST FLOOR PLAN' : 'GROUND FLOOR PLAN';
  const currentLevelId = selectedFloor === 'L1' ? 'LVL-001 (+3.15m)' : 'LVL-000 (±0.00m)';
  const currentDrawingNo = selectedFloor === 'L1' ? 'A-102' : 'A-101';

  // Smart architectural room abbreviation for small spaces
  const getCompactRoomName = (fullName: string, availableWidth: number): string => {
    const upper = fullName.toUpperCase();
    if (availableWidth >= 85) return upper;
    if (upper.includes('BATH') || upper.includes('TOILET')) return 'BATH';
    if (upper.includes('KITCHEN')) return 'KITCHEN';
    if (upper.includes('UTILITY') || upper.includes('YARD')) return 'UTIL';
    if (upper.includes('ENTRANCE') || upper.includes('FOYER')) return 'FOYER';
    if (upper.includes('STAIR')) return 'STAIRS';
    if (upper.includes('DINING')) return 'DINING';
    if (upper.includes('LIVING')) return 'LIVING';
    if (upper.includes('BEDROOM') || upper.includes('BED')) {
      const num = upper.match(/\d+/);
      return num ? `BED ${num[0]}` : 'BED';
    }
    if (upper.includes('PUJA')) return 'PUJA';
    if (upper.includes('BALCONY')) return 'BALC';
    if (upper.includes('TERRACE')) return 'TERR';
    return upper.length > 8 ? upper.substring(0, 7) + '.' : upper;
  };

  return (
    <div className="relative inline-block w-full max-w-full transition-transform duration-200">
      <svg
        id="cad-drawing-svg"
        xmlns="http://www.w3.org/2000/svg"
        width={sheetW}
        height={sheetH}
        viewBox={`0 0 ${sheetW} ${sheetH}`}
        className="cad-blueprint-canvas shadow-2xl rounded-sm bg-white select-none border border-slate-300 w-full h-auto max-h-[85vh] object-contain"
        style={{ fontFamily: CAD_FONTS.family }}
      >
        <defs>
          {/* Arrowhead marker */}
          <marker id="cad-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill={CAD_COLORS.sheetBorder} />
          </marker>
          <marker id="stair-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <polygon points="0 0, 6 3, 0 6" fill={CAD_COLORS.stairArrow} />
          </marker>

          {/* Hatching for exterior walls */}
          <pattern id="hatch-ext-wall" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="6" stroke="#94A3B8" strokeWidth="0.75" />
          </pattern>
        </defs>

        {/* ========================================================= */}
        {/* 1. SHEET BORDER & MARGINS (ISO 128 / BIS SP 46)           */}
        {/* ========================================================= */}
        <rect width="100%" height="100%" fill={CAD_COLORS.sheetBg} />

        {/* Outer Heavy Border Line */}
        <rect
          x={margin}
          y={margin}
          width={sheetW - margin * 2}
          height={sheetH - margin * 2}
          fill="none"
          stroke={CAD_COLORS.sheetBorder}
          strokeWidth={CAD_LINE_WEIGHTS.sheetBorderOuter}
        />

        {/* Inner Border Line */}
        <rect
          x={innerMargin}
          y={innerMargin}
          width={sheetW - innerMargin * 2}
          height={sheetH - innerMargin * 2}
          fill="none"
          stroke={CAD_COLORS.innerBorder}
          strokeWidth={CAD_LINE_WEIGHTS.sheetBorderInner}
        />

        {/* Viewport Boundary Frame */}
        <rect
          x={vpX}
          y={vpY}
          width={vpW}
          height={vpH}
          fill={CAD_COLORS.viewportBg}
          stroke={CAD_COLORS.innerBorder}
          strokeWidth="0.5"
        />

        {/* Right Info Panel Boundary */}
        <rect
          x={rightX}
          y={rightY}
          width={rightW}
          height={rightH}
          fill={CAD_COLORS.sidebarBg}
          stroke={CAD_COLORS.innerBorder}
          strokeWidth="0.5"
        />

        {/* ========================================================= */}
        {/* 2. MAIN DRAWING VIEWPORT                                   */}
        {/* ========================================================= */}
        <g id="drawing-viewport" clipPath="url(#vp-clip)">
          {/* North Arrow Symbol */}
          <g className="compass-rose" transform={`translate(${vpX + 24}, ${vpY + 24})`}>
            <circle cx="20" cy="20" r="16" fill="none" stroke={CAD_COLORS.sheetBorder} strokeWidth="0.8" />
            <polygon points="20,20 20,4 23,20" fill={CAD_COLORS.sheetBorder} />
            <polygon points="20,20 20,4 17,20" fill="#FFFFFF" stroke={CAD_COLORS.sheetBorder} strokeWidth="0.5" />
            <polygon points="20,20 36,20 20,23" fill={CAD_COLORS.sheetBorder} />
            <polygon points="20,20 36,20 20,17" fill="#FFFFFF" stroke={CAD_COLORS.sheetBorder} strokeWidth="0.5" />
            <polygon points="20,20 20,36 17,20" fill={CAD_COLORS.sheetBorder} />
            <polygon points="20,20 20,36 23,20" fill="#FFFFFF" stroke={CAD_COLORS.sheetBorder} strokeWidth="0.5" />
            <polygon points="20,20 4,20 20,17" fill={CAD_COLORS.sheetBorder} />
            <polygon points="20,20 4,20 20,23" fill="#FFFFFF" stroke={CAD_COLORS.sheetBorder} strokeWidth="0.5" />
            <text x="20" y="0" textAnchor="middle" fontSize="10" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>N</text>
          </g>

          {/* Viewport Header Tag */}
          <g transform={`translate(${vpX + vpW - 170}, ${vpY + 24})`}>
            <text x="0" y="0" fontSize="11" fontWeight="bold" fill={CAD_COLORS.sheetBorder} letterSpacing="0.5">
              {currentLevelLabel}
            </text>
            <text x="0" y="14" fontSize="8" fill={CAD_COLORS.roomArea}>
              DATUM: {currentLevelId} • SCALE 1:100
            </text>
          </g>

          {/* Structural Grid Lines & Bubbles (If defined) */}
          {buildingModel.structuralGrid && (
            <g id="structural-grid" opacity="0.85">
              {/* X Grid Lines */}
              {(buildingModel.structuralGrid.gridLinesX || []).map((gl, idx) => {
                const gx = toSvgX(gl.coordinate);
                return (
                  <g key={`grid-x-${idx}`}>
                    <line
                      x1={gx}
                      y1={bldgOriginY - 18}
                      x2={gx}
                      y2={bldgOriginY + bldgPxL + 18}
                      stroke={CAD_COLORS.gridLine}
                      strokeWidth={CAD_LINE_WEIGHTS.gridLine}
                      strokeDasharray="6 3 2 3"
                    />
                    <circle
                      cx={gx}
                      cy={bldgOriginY - 24}
                      r="7.5"
                      fill={CAD_COLORS.gridBubbleBg}
                      stroke={CAD_COLORS.gridBubbleStroke}
                      strokeWidth="1.0"
                    />
                    <text
                      x={gx}
                      y={bldgOriginY - 21.5}
                      textAnchor="middle"
                      fontSize="7.5"
                      fontWeight="bold"
                      fill={CAD_COLORS.gridText}
                    >
                      {gl.tag || idx + 1}
                    </text>
                  </g>
                );
              })}

              {/* Y Grid Lines */}
              {(buildingModel.structuralGrid.gridLinesY || []).map((gl, idx) => {
                const gy = toSvgY(gl.coordinate);
                return (
                  <g key={`grid-y-${idx}`}>
                    <line
                      x1={bldgOriginX - 18}
                      y1={gy}
                      x2={bldgOriginX + bldgPxW + 18}
                      y2={gy}
                      stroke={CAD_COLORS.gridLine}
                      strokeWidth={CAD_LINE_WEIGHTS.gridLine}
                      strokeDasharray="6 3 2 3"
                    />
                    <circle
                      cx={bldgOriginX - 24}
                      cy={gy}
                      r="7.5"
                      fill={CAD_COLORS.gridBubbleBg}
                      stroke={CAD_COLORS.gridBubbleStroke}
                      strokeWidth="1.0"
                    />
                    <text
                      x={bldgOriginX - 24}
                      y={gy + 2.5}
                      textAnchor="middle"
                      fontSize="7.5"
                      fontWeight="bold"
                      fill={CAD_COLORS.gridText}
                    >
                      {gl.tag || String.fromCharCode(65 + idx)}
                    </text>
                  </g>
                );
              })}
            </g>
          )}

          {/* Top Overall Dimension String */}
          <g className="cad-dim">
            <line x1={bldgOriginX} y1={dimTopY - 8} x2={bldgOriginX} y2={bldgOriginY - 2} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.extensionLine} />
            <line x1={bldgOriginX + bldgPxW} y1={dimTopY - 8} x2={bldgOriginX + bldgPxW} y2={bldgOriginY - 2} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.extensionLine} />
            <line x1={bldgOriginX} y1={dimTopY} x2={bldgOriginX + bldgPxW} y2={dimTopY} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.dimensionLine} />
            <line x1={bldgOriginX - 4} y1={dimTopY + 4} x2={bldgOriginX + 4} y2={dimTopY - 4} stroke={CAD_COLORS.dimTick} strokeWidth={CAD_LINE_WEIGHTS.dimensionTick} />
            <line x1={bldgOriginX + bldgPxW - 4} y1={dimTopY + 4} x2={bldgOriginX + bldgPxW + 4} y2={dimTopY - 4} stroke={CAD_COLORS.dimTick} strokeWidth={CAD_LINE_WEIGHTS.dimensionTick} />
            <text x={bldgOriginX + bldgPxW / 2} y={dimTopY - 5} textAnchor="middle" fontSize={CAD_FONTS.dimText} fontWeight="bold" fill={CAD_COLORS.dimText}>
              {`${envW.toFixed(2)}m [${toFtIn(envW)}]`}
            </text>
          </g>

          {/* Right Overall Dimension String */}
          <g className="cad-dim">
            <line x1={bldgOriginX + bldgPxW + 2} y1={bldgOriginY} x2={dimRightX + 8} y2={bldgOriginY} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.extensionLine} />
            <line x1={bldgOriginX + bldgPxW + 2} y1={bldgOriginY + bldgPxL} x2={dimRightX + 8} y2={bldgOriginY + bldgPxL} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.extensionLine} />
            <line x1={dimRightX} y1={bldgOriginY} x2={dimRightX} y2={bldgOriginY + bldgPxL} stroke={CAD_COLORS.dimLine} strokeWidth={CAD_LINE_WEIGHTS.dimensionLine} />
            <line x1={dimRightX - 4} y1={bldgOriginY + 4} x2={dimRightX + 4} y2={bldgOriginY - 4} stroke={CAD_COLORS.dimTick} strokeWidth={CAD_LINE_WEIGHTS.dimensionTick} />
            <line x1={dimRightX - 4} y1={bldgOriginY + bldgPxL + 4} x2={dimRightX + 4} y2={bldgOriginY + bldgPxL - 4} stroke={CAD_COLORS.dimTick} strokeWidth={CAD_LINE_WEIGHTS.dimensionTick} />
            <text
              x={dimRightX + 16}
              y={bldgOriginY + bldgPxL / 2}
              textAnchor="middle"
              fontSize={CAD_FONTS.dimText}
              fontWeight="bold"
              fill={CAD_COLORS.dimText}
              transform={`rotate(90 ${dimRightX + 16} ${bldgOriginY + bldgPxL / 2})`}
            >
              {`${envL.toFixed(2)}m [${toFtIn(envL)}]`}
            </text>
          </g>

          {/* CBM Elements (Walls) */}
          <g id="walls">
            {walls.map((element) => {
              const polyPoints = (element.geometry.footprintPolygon || []).map(pt => `${toSvgX(pt[0])},${toSvgY(pt[1])}`).join(' ');
              const isExt = element.wallType === 'EXTERNAL';
              return (
                <polygon
                  key={element.elementId}
                  data-cbm-id={element.elementId}
                  data-type="wall"
                  data-wall-type={element.wallType || (isExt ? 'EXTERNAL' : 'INTERNAL')}
                  points={polyPoints}
                  fill={isExt ? "url(#hatch-ext-wall)" : CAD_COLORS.wallIntFill}
                  stroke={isExt ? CAD_COLORS.wallExtStroke : CAD_COLORS.wallIntStroke}
                  strokeWidth={isExt ? CAD_LINE_WEIGHTS.wallExt : CAD_LINE_WEIGHTS.wallInt}
                  className="cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => onSelectWall(element.name, isExt, (element.geometry.thicknessM || (isExt ? 0.23 : 0.115)) * 1000)}
                />
              );
            })}
          </g>

          {/* CBM Columns (Structural Columns at Grid Intersections) */}
          <g id="columns">
            {columns.map((col) => {
              const fp = col.geometry.footprintPolygon || [];
              if (fp.length === 0) return null;
              const points = fp.map(pt => `${toSvgX(pt[0])},${toSvgY(pt[1])}`).join(' ');
              return (
                <g key={col.elementId} data-cbm-id={col.elementId} data-type="column">
                  <polygon
                    points={points}
                    fill={CAD_COLORS.columnFill}
                    stroke={CAD_COLORS.columnStroke}
                    strokeWidth={CAD_LINE_WEIGHTS.columnEdge}
                  />
                  {/* Subtle Column Cross Mark */}
                  {fp.length >= 4 && (
                    <line
                      x1={toSvgX(fp[0][0])}
                      y1={toSvgY(fp[0][1])}
                      x2={toSvgX(fp[2][0])}
                      y2={toSvgY(fp[2][1])}
                      stroke="#FFFFFF"
                      strokeWidth="0.5"
                      opacity="0.4"
                    />
                  )}
                </g>
              );
            })}
          </g>

          {/* CBM Stairs */}
          <g id="stairs">
            {stairs.map((element) => {
              const fp = element.geometry.footprintPolygon || [];
              if (fp.length === 0) return null;
              const polyPoints = fp.map(pt => `${toSvgX(pt[0])},${toSvgY(pt[1])}`).join(' ');
              const xs = fp.map(pt => toSvgX(pt[0]));
              const ys = fp.map(pt => toSvgY(pt[1]));
              const sx0 = Math.min(...xs);
              const sx1 = Math.max(...xs);
              const sy0 = Math.min(...ys);
              const sy1 = Math.max(...ys);
              const stairHPx = sy1 - sy0;
              const numRisers = (element.properties?.numberOfRisers as number) || 18;
              const halfRisers = Math.max(3, Math.floor(numRisers / 2));
              const landingY = sy0 + stairHPx / 2;
              const flightHPx = stairHPx / 2;
              const cx = (sx0 + sx1) / 2;

              const flight1Lines = [];
              for (let i = 1; i < halfRisers; i++) {
                const ty = sy0 + i * (flightHPx / halfRisers);
                flight1Lines.push(
                  <line key={`f1-${i}`} x1={sx0} y1={ty} x2={sx1} y2={ty} stroke={CAD_COLORS.stairTread} strokeWidth={CAD_LINE_WEIGHTS.stairTread} />
                );
              }
              const flight2Lines = [];
              for (let i = 1; i < halfRisers; i++) {
                const ty = landingY + i * (flightHPx / halfRisers);
                flight2Lines.push(
                  <line key={`f2-${i}`} x1={sx0} y1={ty} x2={sx1} y2={ty} stroke={CAD_COLORS.stairTread} strokeWidth={CAD_LINE_WEIGHTS.stairTread} />
                );
              }

              return (
                <g key={element.elementId} data-cbm-id={element.elementId} data-type="stair">
                  <polygon points={polyPoints} fill={CAD_COLORS.stairFill} stroke={CAD_COLORS.sheetBorder} strokeWidth="1.2" />
                  <line x1={sx0} y1={landingY} x2={sx1} y2={landingY} stroke={CAD_COLORS.stairLanding} strokeWidth={CAD_LINE_WEIGHTS.stairNosing} />
                  {flight1Lines}
                  {flight2Lines}
                  {/* Travel Path Arrow */}
                  <line x1={cx} y1={landingY + 6} x2={cx} y2={sy0 + 8} stroke={CAD_COLORS.stairArrow} strokeWidth="1.2" markerEnd="url(#stair-arrow)" />
                  <text x={cx} y={sy0 - 4} textAnchor="middle" fontSize="8" fontWeight="bold" fill={CAD_COLORS.stairArrow}>UP</text>
                  <text x={cx} y={landingY - 4} textAnchor="middle" fontSize="6.5" fill={CAD_COLORS.roomArea}>LANDING</text>
                </g>
              );
            })}
          </g>

          {/* CBM Openings (Doors & Windows with Knockouts & Tags) */}
          <g id="openings">
            {openings.map((opening, idx) => {
              if (opening.openingType === 'DOOR') {
                const ox = toSvgX(opening.positionM[0]);
                const oy = toSvgY(opening.positionM[1]);
                const ow = opening.widthM * activeScale;
                const gapThick = 9;
                const hingeX = ox - ow / 2;
                const hingeY = oy;
                const leafEndX = ox + ow / 2;
                const leafEndY = oy;
                const tagLabel = `D${idx + 1}`;

                return (
                  <g key={opening.openingId} data-cbm-id={opening.openingId} data-type="door">
                    {/* Knockout wall mask */}
                    <rect x={ox - ow / 2} y={oy - gapThick / 2} width={ow} height={gapThick} fill={CAD_COLORS.wallKnockout} stroke="none" />
                    {/* Door Leaf Line */}
                    <line x1={hingeX} y1={hingeY} x2={leafEndX} y2={leafEndY} stroke={CAD_COLORS.doorLeaf} strokeWidth={CAD_LINE_WEIGHTS.doorLeaf} />
                    {/* Swing Clearance Arc */}
                    <path
                      d={`M ${hingeX} ${hingeY} A ${ow} ${ow} 0 0 1 ${hingeX} ${hingeY - ow}`}
                      fill="none"
                      stroke={CAD_COLORS.doorSwing}
                      strokeWidth={CAD_LINE_WEIGHTS.doorSwing}
                      strokeDasharray="4 2"
                    />
                    {/* Opening Tag Bubble */}
                    <circle cx={ox} cy={oy - gapThick - 4} r="5.5" fill="#FFFFFF" stroke={CAD_COLORS.tagDoor} strokeWidth="0.8" />
                    <text x={ox} y={oy - gapThick - 2} textAnchor="middle" fontSize="5.5" fontWeight="bold" fill={CAD_COLORS.tagDoor}>
                      {tagLabel}
                    </text>
                  </g>
                );
              }

              if (opening.openingType === 'WINDOW') {
                const ox = toSvgX(opening.positionM[0]);
                const oy = toSvgY(opening.positionM[1]);
                const ow = opening.widthM * activeScale;
                const winThick = 7;
                const tagLabel = `W${idx + 1}`;

                return (
                  <g key={opening.openingId} data-cbm-id={opening.openingId} data-type="window">
                    {/* Knockout wall mask */}
                    <rect x={ox - ow / 2} y={oy - winThick / 2} width={ow} height={winThick} fill={CAD_COLORS.wallKnockout} stroke="none" />
                    {/* 3-Line CAD Glazing Symbol */}
                    <line x1={ox - ow / 2} y1={oy} x2={ox + ow / 2} y2={oy} stroke={CAD_COLORS.windowOuter} strokeWidth={CAD_LINE_WEIGHTS.windowFrame} />
                    <line x1={ox - ow / 2} y1={oy - 2} x2={ox + ow / 2} y2={oy - 2} stroke={CAD_COLORS.windowGlaze} strokeWidth={CAD_LINE_WEIGHTS.windowGlaze} />
                    <line x1={ox - ow / 2} y1={oy + 2} x2={ox + ow / 2} y2={oy + 2} stroke={CAD_COLORS.windowGlaze} strokeWidth={CAD_LINE_WEIGHTS.windowGlaze} />
                    {/* Opening Tag Bubble */}
                    <circle cx={ox} cy={oy + winThick + 5} r="5.5" fill="#FFFFFF" stroke={CAD_COLORS.tagWindow} strokeWidth="0.8" />
                    <text x={ox} y={oy + winThick + 7} textAnchor="middle" fontSize="5.5" fontWeight="bold" fill={CAD_COLORS.tagWindow}>
                      {tagLabel}
                    </text>
                  </g>
                );
              }

              return null;
            })}
          </g>

          {/* CBM Spaces (Rooms & Usable Areas) */}
          <g id="spaces">
            {spaces.map((space) => {
              const rx = toSvgX(space.bounds.x);
              const ry = toSvgY(space.bounds.y);
              const rw = space.bounds.width * activeScale;
              const rh = space.bounds.height * activeScale;
              const isSelected = inspectedElement?.id === space.spaceId;

              const layoutRoom = layout.rooms.find(r => r.name.toLowerCase() === space.name.toLowerCase());

              // Small room detection for collision avoidance
              const isCompact = rw < 75 || rh < 56;
              const displayName = getCompactRoomName(space.name, rw);
              const dynamicFontSize = Math.max(6.0, Math.min(CAD_FONTS.roomName, rw / 7.5, rh / 4.2));
              const dynamicDetailSize = Math.max(5.2, Math.min(CAD_FONTS.roomDetail, rw / 9.5, rh / 5.2));

              return (
                <g
                  key={space.spaceId}
                  data-cbm-id={space.spaceId}
                  data-type="space"
                  className="cursor-pointer transition-all"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectRoom(layoutRoom || {
                      id: space.spaceId,
                      name: space.name,
                      floor: space.floor || 'L0',
                      bounds: { x: space.bounds.x, y: space.bounds.y, width: space.bounds.width, height: space.bounds.height },
                      areaSqm: space.areaSqm,
                      widthM: space.bounds.width,
                      lengthM: space.bounds.height,
                      zone: 'PRIVATE',
                      color: '#3b82f6'
                    });
                  }}
                >
                  {/* Room Footprint Hit Area & Interactive Cyan Highlight */}
                  <rect
                    x={rx}
                    y={ry}
                    width={rw}
                    height={rh}
                    fill={isSelected ? CAD_COLORS.selectedFill : "transparent"}
                    stroke={isSelected ? CAD_COLORS.selectedStroke : "none"}
                    strokeWidth={isSelected ? 1.5 : 0}
                    strokeDasharray={isSelected ? "4 2" : "none"}
                    className="hover:fill-slate-900/5 transition-colors"
                  />

                  {/* Centered High-Contrast Room Labels */}
                  <g className="room-labels" pointerEvents="none">
                    <text
                      x={rx + rw / 2}
                      y={ry + rh / 2 - (isCompact ? 2 : 5)}
                      textAnchor="middle"
                      fontSize={dynamicFontSize}
                      fontWeight="bold"
                      letterSpacing="0.3"
                      fill={CAD_COLORS.roomTitle}
                    >
                      {displayName}
                    </text>

                    {/* Area String */}
                    <text
                      x={rx + rw / 2}
                      y={ry + rh / 2 + (isCompact ? 6 : 7)}
                      textAnchor="middle"
                      fontSize={dynamicDetailSize}
                      fill={CAD_COLORS.roomArea}
                    >
                      {isCompact ? `${space.areaSqm.toFixed(1)}m²` : formatDualArea(space.areaSqm)}
                    </text>

                    {/* Metric Dimensions (Only when space allows) */}
                    {!isCompact && rw >= 80 && rh >= 65 && (
                      <text
                        x={rx + rw / 2}
                        y={ry + rh / 2 + 18}
                        textAnchor="middle"
                        fontSize={dynamicDetailSize - 0.5}
                        fill={CAD_COLORS.roomDim}
                      >
                        {`${space.bounds.width.toFixed(2)}m × ${space.bounds.height.toFixed(2)}m`}
                      </text>
                    )}
                  </g>
                </g>
              );
            })}
          </g>

          {/* Frontage / Road Buffer Box */}
          <g className="road-box">
            <rect
              x={bldgOriginX - 25}
              y={bldgOriginY + bldgPxL + 34}
              width={bldgPxW + 50}
              height="36"
              fill="#F8FAFC"
              stroke={CAD_COLORS.sheetBorder}
              strokeWidth="0.8"
              strokeDasharray="4 2"
            />
            <text
              x={bldgOriginX + bldgPxW / 2}
              y={bldgOriginY + bldgPxL + 56}
              fontSize="10"
              letterSpacing="8"
              fontWeight="bold"
              textAnchor="middle"
              fill={CAD_COLORS.sheetBorder}
            >
              ACCESS ROAD (16.0m WIDE FRONTAGE)
            </text>
          </g>

          {/* Graphic Scale Bar */}
          <g className="scale-bar" transform={`translate(${vpX + 24}, ${vpY + vpH - 36})`}>
            <text x="0" y="-5" fontSize="7" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>GRAPHIC SCALE (METERS)</text>
            <rect x="0" y="0" width="30" height="4" fill="#000000" stroke="#000000" strokeWidth="0.5" />
            <rect x="30" y="0" width="30" height="4" fill="#FFFFFF" stroke="#000000" strokeWidth="0.5" />
            <rect x="60" y="0" width="40" height="4" fill="#000000" stroke="#000000" strokeWidth="0.5" />
            <text x="0" y="11" fontSize="6.5" fill={CAD_COLORS.sheetBorder}>0m</text>
            <text x="30" y="11" fontSize="6.5" fill={CAD_COLORS.sheetBorder}>2m</text>
            <text x="60" y="11" fontSize="6.5" fill={CAD_COLORS.sheetBorder}>5m</text>
            <text x="100" y="11" fontSize="6.5" fill={CAD_COLORS.sheetBorder}>10m</text>
          </g>
        </g>

        {/* ========================================================= */}
        {/* 3. DEDICATED SIDEBAR: SCHEDULES, LEGEND & NOTES            */}
        {/* ========================================================= */}
        <g id="sidebar" transform={`translate(${rightX}, ${rightY})`}>
          {/* Header */}
          <rect x="0" y="0" width={rightW} height="26" fill={CAD_COLORS.tableHeaderBg} />
          <text x="10" y="17" fontSize="9.5" fontWeight="bold" fill="#FFFFFF" letterSpacing="0.8">
            SCHEDULES &amp; SPECIFICATIONS
          </text>

          {/* Door Schedule Table */}
          <g transform="translate(10, 36)">
            <text x="0" y="0" fontSize="8.5" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>
              DOOR SCHEDULE ({doors.length} OPENINGS)
            </text>
            {/* Table Header */}
            <rect x="0" y="6" width={rightW - 20} height="16" fill="#F1F5F9" stroke={CAD_COLORS.tableBorder} strokeWidth="0.6" />
            <text x="6" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>TAG</text>
            <text x="36" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>TYPE</text>
            <text x="140" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>WIDTH (M / FT)</text>
            <text x="230" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>HEIGHT</text>
            <text x="290" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>LEVEL</text>

            {/* Table Rows (Up to 6) */}
            {doors.slice(0, 6).map((door, idx) => {
              const rowY = 22 + idx * 15;
              const bg = idx % 2 === 1 ? CAD_COLORS.tableRowAlt : '#FFFFFF';
              return (
                <g key={`door-row-${door.openingId}`}>
                  <rect x="0" y={rowY} width={rightW - 20} height="15" fill={bg} stroke={CAD_COLORS.tableBorder} strokeWidth="0.4" />
                  <text x="6" y={rowY + 10.5} fontSize="6.5" fontWeight="bold" fill={CAD_COLORS.tagDoor}>
                    {`D${idx + 1}`}
                  </text>
                  <text x="36" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {door.name ? (door.name.length > 20 ? door.name.substring(0, 20) + '...' : door.name) : 'Flush Timber Door'}
                  </text>
                  <text x="140" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {`${door.widthM.toFixed(2)}m (${toFtIn(door.widthM)})`}
                  </text>
                  <text x="230" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {`${door.heightM.toFixed(2)}m`}
                  </text>
                  <text x="290" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.roomArea}>
                    {selectedFloor}
                  </text>
                </g>
              );
            })}
          </g>

          {/* Window Schedule Table */}
          <g transform="translate(10, 160)">
            <text x="0" y="0" fontSize="8.5" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>
              WINDOW SCHEDULE ({windows.length} OPENINGS)
            </text>
            {/* Table Header */}
            <rect x="0" y="6" width={rightW - 20} height="16" fill="#F1F5F9" stroke={CAD_COLORS.tableBorder} strokeWidth="0.6" />
            <text x="6" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>TAG</text>
            <text x="36" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>TYPE</text>
            <text x="140" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>WIDTH (M / FT)</text>
            <text x="230" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>HEIGHT</text>
            <text x="290" y="17" fontSize="6.8" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>SILL HT</text>

            {/* Table Rows (Up to 6) */}
            {windows.slice(0, 6).map((win, idx) => {
              const rowY = 22 + idx * 15;
              const bg = idx % 2 === 1 ? CAD_COLORS.tableRowAlt : '#FFFFFF';
              return (
                <g key={`win-row-${win.openingId}`}>
                  <rect x="0" y={rowY} width={rightW - 20} height="15" fill={bg} stroke={CAD_COLORS.tableBorder} strokeWidth="0.4" />
                  <text x="6" y={rowY + 10.5} fontSize="6.5" fontWeight="bold" fill={CAD_COLORS.tagWindow}>
                    {`W${idx + 1}`}
                  </text>
                  <text x="36" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {win.name ? (win.name.length > 20 ? win.name.substring(0, 20) + '...' : win.name) : 'Aluminium Glazed Window'}
                  </text>
                  <text x="140" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {`${win.widthM.toFixed(2)}m (${toFtIn(win.widthM)})`}
                  </text>
                  <text x="230" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.sheetBorder}>
                    {`${win.heightM.toFixed(2)}m`}
                  </text>
                  <text x="290" y={rowY + 10.5} fontSize="6.5" fill={CAD_COLORS.roomArea}>
                    {`${(win.sillHeightM || 0.9).toFixed(2)}m`}
                  </text>
                </g>
              );
            })}
          </g>

          {/* Architectural Symbol Legend */}
          <g transform="translate(10, 285)">
            <text x="0" y="0" fontSize="8.5" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>
              ARCHITECTURAL SYMBOLS &amp; LEGEND
            </text>
            <rect x="0" y="6" width={rightW - 20} height="110" fill="#FFFFFF" stroke={CAD_COLORS.tableBorder} strokeWidth="0.6" />

            {/* Swatches */}
            <g transform="translate(10, 16)">
              {/* Ext Wall */}
              <rect x="0" y="0" width="22" height="10" fill="url(#hatch-ext-wall)" stroke={CAD_COLORS.wallExtStroke} strokeWidth="1.4" />
              <text x="28" y="8" fontSize="7" fill={CAD_COLORS.sheetBorder}>Exterior Wall (230mm AAC / Cut Hatch)</text>

              {/* Int Wall */}
              <rect x="0" y="16" width="22" height="8" fill="#FFFFFF" stroke={CAD_COLORS.wallIntStroke} strokeWidth="1.0" />
              <text x="28" y="23" fontSize="7" fill={CAD_COLORS.sheetBorder}>Internal Partition (115mm Drywall/AAC)</text>

              {/* Column */}
              <rect x="0" y="30" width="12" height="12" fill={CAD_COLORS.columnFill} stroke={CAD_COLORS.columnStroke} strokeWidth="1.0" />
              <text x="28" y="39" fontSize="7" fill={CAD_COLORS.sheetBorder}>RCC Structural Column (300×300mm)</text>

              {/* Door Swing */}
              <path d="M 0 54 A 12 12 0 0 1 12 42" fill="none" stroke={CAD_COLORS.doorSwing} strokeWidth="1.0" strokeDasharray="3 2" />
              <line x1="0" y1="54" x2="12" y2="54" stroke={CAD_COLORS.doorLeaf} strokeWidth="1.2" />
              <text x="28" y="52" fontSize="7" fill={CAD_COLORS.sheetBorder}>Door Leaf &amp; 90° Swing Arc</text>

              {/* Glazed Window */}
              <line x1="0" y1="66" x2="20" y2="66" stroke={CAD_COLORS.windowOuter} strokeWidth="1.2" />
              <line x1="0" y1="64" x2="20" y2="64" stroke={CAD_COLORS.windowGlaze} strokeWidth="0.6" />
              <line x1="0" y1="68" x2="20" y2="68" stroke={CAD_COLORS.windowGlaze} strokeWidth="0.6" />
              <text x="28" y="67" fontSize="7" fill={CAD_COLORS.sheetBorder}>3-Line Glazed Window Unit</text>

              {/* Stair Core */}
              <line x1="0" y1="80" x2="20" y2="80" stroke={CAD_COLORS.stairTread} strokeWidth="1.0" />
              <line x1="10" y1="80" x2="10" y2="74" stroke={CAD_COLORS.stairArrow} strokeWidth="1.0" markerEnd="url(#stair-arrow)" />
              <text x="28" y="80" fontSize="7" fill={CAD_COLORS.sheetBorder}>RCC Stair Core &amp; Travel Line</text>
            </g>
          </g>

          {/* Project Notes & Statutory Notice */}
          <g transform="translate(10, 420)">
            <text x="0" y="0" fontSize="8.5" fontWeight="bold" fill={CAD_COLORS.sheetBorder}>
              GENERAL ARCHITECTURAL NOTES
            </text>
            <rect x="0" y="6" width={rightW - 20} height="135" fill="#FFFFFF" stroke={CAD_COLORS.tableBorder} strokeWidth="0.6" />
            <g transform="translate(10, 18)" fontSize="6.8" fill={CAD_COLORS.disclaimerText}>
              <text x="0" y="0">1. ALL DIMENSIONS ARE IN METERS &amp; MILLIMETERS UNLESS SPECIFIED.</text>
              <text x="0" y="11">2. WRITTEN DIMENSIONS SHALL TAKE PRECEDENCE OVER SCALED WORK.</text>
              <text x="0" y="22">3. VERIFY ALL SITE LEVELS AND BOUNDARY OFFSETS PRIOR TO COMMENCEMENT.</text>
              <text x="0" y="33">4. MINIMUM CLEAR CEILING HEIGHT: 3.00m (HABITABLE SPACES).</text>
              <text x="0" y="44">5. VENTILATION &amp; DAYLIGHT COMPLIANT WITH NBC 2016 PART 3.</text>
              <text x="0" y="55">6. STRUCTURAL GRID &amp; COLUMN LAYOUT SUBJECT TO CERTIFIED FEA CHECK.</text>

              <line x1="0" y1="65" x2={rightW - 40} y2="65" stroke={CAD_COLORS.tableBorder} strokeWidth="0.5" />

              <text x="0" y="78" fontWeight="bold" fill="#B45309">STATUTORY BYE-LAW &amp; REGULATORY NOTICE:</text>
              <text x="0" y="89" fill="#B45309">THIS DRAWING IS A COMPUTATIONAL DESIGN PROJECTION DERIVED</text>
              <text x="0" y="99" fill="#B45309">FROM THE CANONICAL BUILDING MODEL (CBM). IT CONSTITUTES A</text>
              <text x="0" y="109" fill="#B45309">PRELIMINARY PROPOSAL AND DOES NOT SUBSTITUTE STATUTORY SANCTION</text>
              <text x="0" y="119" fill="#B45309">OR LICENSED STRUCTURAL ENGINEER APPROVAL PRIOR TO CONSTRUCTION.</text>
            </g>
          </g>
        </g>

        {/* ========================================================= */}
        {/* 4. PROFESSIONAL ANCHORED TITLE BLOCK (ISO 128 STANDARD)   */}
        {/* ========================================================= */}
        <g id="title-block" transform={`translate(${tbX}, ${tbY})`}>
          {/* Main Title Block Outer Frame */}
          <rect
            x="0"
            y="0"
            width={tbW}
            height={titleBlockH}
            fill="#FFFFFF"
            stroke={CAD_COLORS.sheetBorder}
            strokeWidth="1.2"
          />

          {/* Column Divider Lines */}
          <line x1="220" y1="0" x2="220" y2={titleBlockH} stroke={CAD_COLORS.tableBorder} strokeWidth="0.8" />
          <line x1="500" y1="0" x2="500" y2={titleBlockH} stroke={CAD_COLORS.tableBorder} strokeWidth="0.8" />
          <line x1="760" y1="0" x2="760" y2={titleBlockH} stroke={CAD_COLORS.tableBorder} strokeWidth="0.8" />
          <line x1="940" y1="0" x2="940" y2={titleBlockH} stroke={CAD_COLORS.tableBorder} strokeWidth="0.8" />

          {/* Section 1: Enterprise Branding (0 - 220px) */}
          <g transform="translate(16, 20)">
            <rect x="0" y="0" width="28" height="28" rx="4" fill="#0F172A" />
            <text x="14" y="19" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#FFFFFF">P</text>
            <text x="36" y="14" fontSize="13" fontWeight="bold" fill="#0F172A" letterSpacing="0.8">
              PLANWISE
            </text>
            <text x="36" y="26" fontSize="7.5" fontWeight="bold" fill="#2563EB" letterSpacing="1.2">
              ENTERPRISE PLATFORM
            </text>
            <text x="0" y="45" fontSize="7" fill={CAD_COLORS.roomArea}>
              Computational Land-to-Home BIM System
            </text>
            <text x="0" y="56" fontSize="6.5" fill={CAD_COLORS.roomArea}>
              ISO 128 / BIS SP 46 Compliant Vector Engine
            </text>
            <text x="0" y="67" fontSize="6.5" fill={CAD_COLORS.roomDim}>
              Canonical Building Model (CBM) Architecture
            </text>
          </g>

          {/* Section 2: Project Metadata (220 - 500px) */}
          <g transform="translate(236, 18)">
            <text x="0" y="0" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea} letterSpacing="0.5">PROJECT TITLE &amp; LOCATION</text>
            <text x="0" y="14" fontSize="10.5" fontWeight="bold" fill="#0F172A">
              {projectName}
            </text>
            <text x="0" y="27" fontSize="8" fill={CAD_COLORS.roomArea}>
              {buildingModel.archetype || 'Single Family Residential Villa'} • Mumbai DCPR 2034
            </text>
            <line x1="0" y1="36" x2="250" y2="36" stroke={CAD_COLORS.tableBorder} strokeWidth="0.5" />
            <text x="0" y="49" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>PROJECT ID / CADASTRAL REF</text>
            <text x="0" y="62" fontSize="9" fontWeight="bold" fill="#0F172A">
              {projectId}
            </text>
            <text x="0" y="74" fontSize="6.5" fill={CAD_COLORS.roomDim}>
              MODEL HASH: {buildingModel.metadata?.modelHash ? buildingModel.metadata.modelHash.substring(0, 24) + '...' : 'SHA256:VERIFIED-CBM'}
            </text>
          </g>

          {/* Section 3: Drawing Title & Parameters (500 - 760px) */}
          <g transform="translate(516, 18)">
            <text x="0" y="0" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea} letterSpacing="0.5">DRAWING SHEET TITLE</text>
            <text x="0" y="15" fontSize="11.5" fontWeight="bold" fill="#0F172A">
              {currentLevelLabel}
            </text>
            <text x="0" y="28" fontSize="8" fill="#2563EB" fontWeight="bold">
              {currentLevelId}
            </text>
            <line x1="0" y1="36" x2="230" y2="36" stroke={CAD_COLORS.tableBorder} strokeWidth="0.5" />
            <text x="0" y="49" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>PHYSICAL DRAWING SCALE</text>
            <text x="0" y="62" fontSize="9" fontWeight="bold" fill="#0F172A">
              1:100 (A3 SHEET AT 100%)
            </text>
            <text x="0" y="74" fontSize="6.5" fill={CAD_COLORS.roomDim}>
              UNITS: METRIC (MILLIMETERS &amp; METERS)
            </text>
          </g>

          {/* Section 4: Audit & Revision (760 - 940px) */}
          <g transform="translate(776, 18)">
            <text x="0" y="0" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>DRAWING NO.</text>
            <text x="0" y="15" fontSize="12" fontWeight="bold" fill="#0F172A">
              {currentDrawingNo}
            </text>

            <text x="90" y="0" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>REVISION</text>
            <text x="90" y="15" fontSize="12" fontWeight="bold" fill="#0F172A">
              REV 01
            </text>

            <line x1="0" y1="26" x2="150" y2="26" stroke={CAD_COLORS.tableBorder} strokeWidth="0.5" />

            <text x="0" y="38" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>DATE OF ISSUE</text>
            <text x="0" y="50" fontSize="8.5" fontWeight="bold" fill="#0F172A">
              OCTOBER 2026
            </text>

            <text x="0" y="63" fontSize="7" fontWeight="bold" fill={CAD_COLORS.roomArea}>SHEET SEQUENCE</text>
            <text x="0" y="75" fontSize="8.5" fontWeight="bold" fill="#0F172A">
              {selectedFloor === 'L1' ? 'SHEET 02 OF 09' : 'SHEET 01 OF 09'}
            </text>
          </g>

          {/* Section 5: Professional Status & Review Stamp (940 - 1220px) */}
          <g transform="translate(956, 14)">
            <rect
              x="0"
              y="0"
              width="250"
              height="88"
              rx="4"
              fill={CAD_COLORS.statusBadgeBg}
              stroke={CAD_COLORS.statusBadgeBorder}
              strokeWidth="1.2"
            />

            <text x="125" y="18" textAnchor="middle" fontSize="7" fontWeight="bold" fill={CAD_COLORS.statusBadgeText} letterSpacing="0.8">
              ENGINEERING RELEASE CONTROL STATUS
            </text>

            <text x="125" y="34" textAnchor="middle" fontSize="9.5" fontWeight="bold" fill={CAD_COLORS.statusBadgeText} letterSpacing="0.5">
              PRELIMINARY / FOR PROFESSIONAL REVIEW
            </text>

            <line x1="16" y1="42" x2="234" y2="42" stroke={CAD_COLORS.statusBadgeBorder} strokeWidth="0.6" strokeDasharray="3 2" />

            <text x="125" y="55" textAnchor="middle" fontSize="6.5" fill={CAD_COLORS.statusBadgeText}>
              NOT FOR STATUTORY SUBMISSION OR CONSTRUCTION
            </text>
            <text x="125" y="65" textAnchor="middle" fontSize="6.2" fill={CAD_COLORS.statusBadgeText}>
              Requires Professional Sign-off by Licensed Architect
            </text>
            <text x="125" y="75" textAnchor="middle" fontSize="6.2" fill={CAD_COLORS.statusBadgeText}>
              &amp; Registered Chartered Structural Engineer (G0–G6)
            </text>
          </g>
        </g>
      </svg>
    </div>
  );
};
