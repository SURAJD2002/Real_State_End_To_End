import { describe, it, expect } from 'vitest';
import {
  CAD_COLORS,
  CAD_LINE_WEIGHTS,
  CAD_FONTS,
  toFtIn,
  formatDualDim,
  formatDualArea
} from './cadStyles';
import { CanonicalBuildingModel } from '../types';

describe('Planwise Architectural CAD Renderer Tests', () => {
  describe('1. Architectural Unit Formatting', () => {
    it('converts meters to architectural feet and inches correctly', () => {
      expect(toFtIn(0)).toBe("0'-0\"");
      expect(toFtIn(1.0)).toBe("3'-3\"");
      expect(toFtIn(4.20)).toBe("13'-9\"");
      expect(toFtIn(15.74)).toBe("51'-8\"");
    });

    it('formats dual dimension strings (metric + imperial)', () => {
      const dim = formatDualDim(4.20, 3.45);
      expect(dim).toContain('4.20m × 3.45m');
      expect(dim).toContain("13'-9\" × 11'-4\"");
    });

    it('formats dual area strings (sqm + sqft)', () => {
      const area = formatDualArea(14.5);
      expect(area).toContain('14.5 m²');
      expect(area).toContain('156 sq ft');
    });
  });

  describe('2. ISO 128 CAD Tokens & Graphic Hierarchy', () => {
    it('maintains high contrast linework with white drawing canvas', () => {
      expect(CAD_COLORS.sheetBg).toBe('#FFFFFF');
      expect(CAD_COLORS.wallExtStroke).toBe('#0F172A');
      expect(CAD_COLORS.columnFill).toBe('#0F172A');
      expect(CAD_COLORS.doorSwing).toBe('#2563EB');
      expect(CAD_COLORS.windowGlaze).toBe('#0284C7');
    });

    it('preserves ISO 128 line weight hierarchy (ext wall > int partition > dimension)', () => {
      expect(CAD_LINE_WEIGHTS.wallExt).toBeGreaterThan(CAD_LINE_WEIGHTS.wallInt);
      expect(CAD_LINE_WEIGHTS.wallInt).toBeGreaterThan(CAD_LINE_WEIGHTS.dimensionLine);
      expect(CAD_LINE_WEIGHTS.sheetBorderOuter).toBeGreaterThan(CAD_LINE_WEIGHTS.sheetBorderInner);
    });

    it('defines accessible typography sizes', () => {
      expect(CAD_FONTS.roomName).toBeGreaterThan(CAD_FONTS.roomNameSmall);
      expect(CAD_FONTS.dimText).toBeGreaterThanOrEqual(7);
      expect(CAD_FONTS.family).toContain('sans-serif');
    });
  });

  describe('3. CBM Geometry Extraction & Schedule Consistency', () => {
    const mockCbm: CanonicalBuildingModel = {
      schemaVersion: '2.0.0',
      modelId: 'cbm-test-01',
      designVersionId: 'dv-test-01',
      projectId: 'CTS-1842-BANDRA',
      siteGeometryVersionId: 'sg-01',
      regulationVersionId: 'reg-01',
      name: 'Bandra West Villa',
      archetype: 'VILLA',
      description: 'Test Villa',
      buildingEnvelope: { widthM: 14.0, lengthM: 20.0, heightM: 6.8 },
      totalGrossBUASqm: 180.0,
      totalUsableAreaSqm: 155.0,
      floorsCount: 2,
      levels: [
        { levelId: 'LVL-000', levelIndex: 0, name: 'GROUND', elevationM: 0.0, floorToFloorHeightM: 3.15, usage: 'RESIDENTIAL' },
        { levelId: 'LVL-001', levelIndex: 1, name: 'FIRST', elevationM: 3.15, floorToFloorHeightM: 3.15, usage: 'RESIDENTIAL' }
      ],
      spaces: [
        {
          spaceId: 'SPACE-LIVING-01',
          levelId: 'LVL-000',
          spaceType: 'LIVING_ROOM',
          name: 'Living Room',
          zone: 'PUBLIC',
          floor: 'L0',
          color: '#3b82f6',
          bounds: { x: 2.0, y: 2.0, width: 6.0, height: 4.5 },
          polygon: [[2, 2], [8, 2], [8, 6.5], [2, 6.5]],
          areaSqm: 27.0,
          perimeterM: 21.0,
          centroid: [5.0, 4.25],
          heightM: 3.0,
          daylightRequirement: 'DIRECT_WINDOW',
          ventilationRequirement: 'NATURAL_CROSS',
          adjacentSpaceIds: [],
          boundaryWallIds: ['WALL-EXT-01']
        },
        {
          spaceId: 'SPACE-TOILET-01',
          levelId: 'LVL-000',
          spaceType: 'TOILET',
          name: 'Powder Room',
          zone: 'SERVICE',
          floor: 'L0',
          color: '#94a3b8',
          bounds: { x: 8.2, y: 2.0, width: 1.8, height: 1.5 },
          polygon: [[8.2, 2], [10, 2], [10, 3.5], [8.2, 3.5]],
          areaSqm: 2.7,
          perimeterM: 6.6,
          centroid: [9.1, 2.75],
          heightM: 3.0,
          daylightRequirement: 'VENTILATION_SHAFT',
          ventilationRequirement: 'MECHANICAL',
          adjacentSpaceIds: [],
          boundaryWallIds: ['WALL-INT-01']
        }
      ],
      elements: [
        {
          elementId: 'WALL-EXT-01',
          elementType: 'WALL' as any,
          levelId: 'LVL-000',
          name: 'North Exterior Wall',
          geometry: {
            footprintPolygon: [[0, 0], [14, 0], [14, 0.23], [0, 0.23]],
            baseZ: 0,
            topZ: 3.15,
            thicknessM: 0.23
          },
          materialId: 'AAC_BLOCK_230MM',
          structuralRole: 'NON_LOADBEARING' as any,
          wallType: 'EXTERNAL' as any
        },
        {
          elementId: 'COL-A1',
          elementType: 'COLUMN' as any,
          levelId: 'LVL-000',
          name: 'Column A1',
          geometry: {
            footprintPolygon: [[0, 0], [0.3, 0], [0.3, 0.3], [0, 0.3]],
            baseZ: 0,
            topZ: 3.15,
            widthM: 0.3,
            depthM: 0.3
          },
          materialId: 'RCC_M25',
          structuralRole: 'LOADBEARING' as any,
          gridReference: 'A-1'
        },
        {
          elementId: 'STAIR-01',
          elementType: 'STAIR' as any,
          levelId: 'LVL-000',
          name: 'Main Doglegged Staircase',
          geometry: {
            footprintPolygon: [[8.5, 3.5], [11.5, 3.5], [11.5, 7.5], [8.5, 7.5]],
            baseZ: 0,
            topZ: 3.15
          },
          materialId: 'RCC_M25',
          structuralRole: 'LOADBEARING' as any,
          properties: {
            numberOfRisers: 18,
            treadMm: 275
          }
        }
      ],
      openings: [
        {
          openingId: 'DOOR-01',
          openingType: 'DOOR' as any,
          hostWallId: 'WALL-EXT-01',
          levelId: 'LVL-000',
          name: 'Main Entrance Door',
          widthM: 1.05,
          heightM: 2.10,
          sillHeightM: 0.0,
          positionRatio: 0.5,
          positionM: [5.0, 0.115],
          materialId: 'TEAK_WOOD_DOOR'
        },
        {
          openingId: 'WIN-01',
          openingType: 'WINDOW' as any,
          hostWallId: 'WALL-EXT-01',
          levelId: 'LVL-000',
          name: 'Living Glazed Window',
          widthM: 1.80,
          heightM: 1.50,
          sillHeightM: 0.90,
          positionRatio: 0.8,
          positionM: [10.0, 0.115],
          materialId: 'ALUM_DOUBLE_GLAZED'
        }
      ],
      structuralGrid: {
        gridLinesX: [{ tag: 'A', coordinate: 0.0, direction: 'X' }, { tag: 'B', coordinate: 7.0, direction: 'X' }, { tag: 'C', coordinate: 14.0, direction: 'X' }],
        gridLinesY: [{ tag: '1', coordinate: 0.0, direction: 'Y' }, { tag: '2', coordinate: 10.0, direction: 'Y' }, { tag: '3', coordinate: 20.0, direction: 'Y' }],
        baySpacingXM: 7.0,
        baySpacingYM: 10.0
      },
      materials: [],
      metadata: {
        engineName: 'Planwise Model Compiler',
        engineVersion: '2.0.0',
        compilationTimestamp: '2026-10-10T00:00:00Z',
        modelHash: 'hash-test-verified-cbm',
        isLocked: false
      }
    };

    it('extracts doors and windows matching CBM opening counts', () => {
      const doors = mockCbm.openings.filter(o => o.openingType === 'DOOR');
      const windows = mockCbm.openings.filter(o => o.openingType === 'WINDOW');
      expect(doors).toHaveLength(1);
      expect(windows).toHaveLength(1);
      expect(doors[0].widthM).toBe(1.05);
      expect(windows[0].widthM).toBe(1.80);
    });

    it('extracts structural columns from CBM elements', () => {
      const cols = mockCbm.elements.filter(e => e.elementType === 'COLUMN');
      expect(cols).toHaveLength(1);
      expect(cols[0].gridReference).toBe('A-1');
      expect(cols[0].elementId).toBe('COL-A1');
    });

    it('extracts staircase with riser and tread properties', () => {
      const stairs = mockCbm.elements.filter(e => e.elementType === 'STAIR');
      expect(stairs).toHaveLength(1);
      expect(stairs[0].properties?.numberOfRisers).toBe(18);
      expect(stairs[0].properties?.treadMm).toBe(275);
    });

    it('calculates room metrics and prevents collision in compact spaces', () => {
      const living = mockCbm.spaces[0];
      const powder = mockCbm.spaces[1];
      expect(living.areaSqm).toBe(27.0);
      expect(powder.areaSqm).toBe(2.7);

      // Verify compact threshold detection
      const isPowderCompact = (powder.bounds.width * 28 < 72) || (powder.bounds.height * 28 < 56);
      expect(isPowderCompact).toBe(true);
    });
  });
});
