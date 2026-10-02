import { describe, it, expect } from 'vitest';
import {
  calculateDistanceM,
  calculateBearingDeg,
  calculateMidpoint,
  computePolygonMetrics,
  getPolygonEdges,
  validateParcelGeometry,
  snapToVertex,
  snapToEdge,
  snapToOrtho,
  snapToAngleIncrement,
  snapToMetricGrid,
  resolveSnap,
  wgs84ToUtm43N,
  computeDestinationCoord,
  Coordinate
} from './cadGeometry';

describe('CAD Geometry Engine Tests', () => {
  // Benchmark Bandra East coordinates
  const p1: Coordinate = [72.8685, 19.1128];
  const p2: Coordinate = [72.8715, 19.1128];
  const p3: Coordinate = [72.8715, 19.1155];
  const p4: Coordinate = [72.8685, 19.1155];

  // 1. Draw Triangle
  it('1. Calculates valid metrics for a 3-vertex triangle', () => {
    const triangle: Coordinate[] = [p1, p2, p3];
    const metrics = computePolygonMetrics(triangle);
    expect(metrics.areaSqm).toBeGreaterThan(10000);
    expect(metrics.perimeterM).toBeGreaterThan(300);

    const validation = validateParcelGeometry(triangle);
    expect(validation.isValid).toBe(true);
    expect(validation.hasSelfIntersection).toBe(false);
  });

  // 2. Draw Rectangle
  it('2. Calculates valid metrics for a 4-vertex rectangle', () => {
    const rect: Coordinate[] = [p1, p2, p3, p4];
    const metrics = computePolygonMetrics(rect);
    expect(metrics.areaSqm).toBeGreaterThan(90000); // ~94,000 sqm
    expect(metrics.perimeterM).toBeGreaterThan(1000);

    const validation = validateParcelGeometry(rect);
    expect(validation.isValid).toBe(true);
  });

  // 3. Close Polygon
  it('3. Successfully generates polygon edges with IDs and midpoints', () => {
    const rect: Coordinate[] = [p1, p2, p3, p4];
    const edges = getPolygonEdges(rect);
    expect(edges).toHaveLength(4);
    expect(edges[0].id).toBe('E01');
    expect(edges[3].id).toBe('E04');
    expect(edges[0].lengthM).toBeGreaterThan(300);
    expect(edges[0].bearingDeg).toBeCloseTo(90, 0); // East
  });

  // 4. Add Vertex / Split Edge
  it('4. Inserts a vertex onto an edge splitting it correctly', () => {
    const rect: Coordinate[] = [p1, p2, p3, p4];
    const mid = calculateMidpoint(rect[0], rect[1]);
    const withNewVertex = [rect[0], mid, ...rect.slice(1)];
    expect(withNewVertex).toHaveLength(5);

    const validation = validateParcelGeometry(withNewVertex);
    expect(validation.isValid).toBe(true);

    const edges = getPolygonEdges(withNewVertex);
    expect(edges).toHaveLength(5);
  });

  // 5. Move Vertex
  it('5. Updates polygon metrics when moving a vertex', () => {
    const initial: Coordinate[] = [p1, p2, p3, p4];
    const initialMetrics = computePolygonMetrics(initial);

    const movedP3: Coordinate = [72.8720, 19.1160];
    const modified: Coordinate[] = [p1, p2, movedP3, p4];
    const modifiedMetrics = computePolygonMetrics(modified);

    expect(modifiedMetrics.areaSqm).toBeGreaterThan(initialMetrics.areaSqm);
  });

  // 6. Delete Vertex
  it('6. Allows deleting a vertex while length >= 3', () => {
    const pentagon: Coordinate[] = [p1, [72.8700, 19.1120], p2, p3, p4];
    const reduced = pentagon.filter((_, idx) => idx !== 1);
    expect(reduced).toHaveLength(4);
    expect(validateParcelGeometry(reduced).isValid).toBe(true);
  });

  // 7. Prevent deletion below 3 vertices
  it('7. Rejects polygons with fewer than 3 vertices', () => {
    const twoPoints: Coordinate[] = [p1, p2];
    const validation = validateParcelGeometry(twoPoints);
    expect(validation.isValid).toBe(false);
    expect(validation.error).toContain('requires at least 3 vertices');
  });

  // 8. Self-Intersection Detection
  it('8. Detects butterfly / figure-8 self-intersection', () => {
    // Cross p2 and p4 to create self-intersecting polygon
    const bowtie: Coordinate[] = [p1, p3, p2, p4];
    const validation = validateParcelGeometry(bowtie);
    expect(validation.isValid).toBe(false);
    expect(validation.hasSelfIntersection).toBe(true);
    expect(validation.invalidEdgeIndices.length).toBeGreaterThanOrEqual(2);
  });

  // 9. Duplicate Vertex Detection
  it('9. Detects duplicate consecutive vertices / zero-length edges', () => {
    const duplicate: Coordinate[] = [p1, p1, p2, p3];
    const validation = validateParcelGeometry(duplicate);
    expect(validation.isValid).toBe(false);
    expect(validation.hasZeroLengthEdge).toBe(true);
  });

  // 10. Distance and Bearing Calculation
  it('10. Accurately calculates geodesic distance and cardinal bearing', () => {
    const dist = calculateDistanceM(p1, p2);
    expect(dist).toBeGreaterThan(300);
    expect(dist).toBeLessThan(350);

    const bearingEast = calculateBearingDeg(p1, p2);
    expect(bearingEast).toBeCloseTo(90, 0);

    const bearingNorth = calculateBearingDeg(p1, p4);
    expect(bearingNorth).toBeCloseTo(0, 0);
  });

  // 11. Midpoint Calculation
  it('11. Accurately finds midpoint between two coordinates', () => {
    const mid = calculateMidpoint(p1, p2);
    expect(mid[0]).toBeCloseTo(72.8700, 4);
    expect(mid[1]).toBeCloseTo(19.1128, 4);
  });

  // 12. Vertex Snapping
  it('12. Snaps cursor to nearby vertex within tolerance', () => {
    const cursorNearP1: Coordinate = [72.868502, 19.112802];
    const snap = snapToVertex(cursorNearP1, [p1, p2, p3], 5.0);
    expect(snap).not.toBeNull();
    expect(snap?.snapped).toEqual(p1);
    expect(snap?.index).toBe(0);
  });

  // 13. Edge Snapping
  it('13. Snaps cursor to orthogonal projection on an edge', () => {
    // Point slightly north of horizontal edge p1 -> p2
    const cursorNearEdge: Coordinate = [72.8700, 19.11282];
    const snap = snapToEdge(cursorNearEdge, [p1, p2, p3, p4], 5.0);
    expect(snap).not.toBeNull();
    expect(snap?.edgeIndex).toBe(0);
    expect(snap?.snapped[1]).toBeCloseTo(19.1128, 4);
  });

  // 14. Ortho Snapping
  it('14. Snaps cursor to nearest 45/90 degree axis in Ortho mode', () => {
    // Anchor at p1, cursor at ~87 degrees
    const cursorNear90: Coordinate = [72.8700, 19.11281];
    const snapped = snapToOrtho(p1, cursorNear90);
    const bearing = calculateBearingDeg(p1, snapped);
    expect([0, 45, 90, 135, 180, 225, 270, 315]).toContain(Math.round(bearing));
  });

  // 15. Angle Increment Snapping
  it('15. Snaps cursor to configured 15° step', () => {
    const cursor: Coordinate = [72.8700, 19.1132];
    const snapped = snapToAngleIncrement(p1, cursor, 15);
    const bearing = calculateBearingDeg(p1, snapped);
    expect(Math.round(bearing) % 15).toBe(0);
  });

  // 16. Metric Grid Snapping
  it('16. Snaps to 1m metric grid', () => {
    const cursor: Coordinate = [72.8685123, 19.1128123];
    const snapped = snapToMetricGrid(cursor, p1, 1.0);
    const mPerDegLat = 111132.95;
    const mPerDegLng = 111412.84 * Math.cos((p1[1] * Math.PI) / 180);
    const dx = (snapped[0] - p1[0]) * mPerDegLng;
    const dy = (snapped[1] - p1[1]) * mPerDegLat;
    expect(Math.abs(dx - Math.round(dx))).toBeLessThan(0.01);
    expect(Math.abs(dy - Math.round(dy))).toBeLessThan(0.01);
  });

  // 17. Complete Snapping Hierarchy
  it('17. Resolves snapping priority: Vertex > Edge > Grid', () => {
    const cursorDirectlyOnP1: Coordinate = [72.8685001, 19.1128001];
    const result = resolveSnap(cursorDirectlyOnP1, [p1, p2, p3, p4], {
      anchorCoord: p4,
      isOrtho: true,
      isGridSnap: true
    });
    expect(result.type).toBe('VERTEX');
    expect(result.sourceVertexIndex).toBe(0);
  });

  // 18. UTM Zone 43N Coordinate Conversion
  it('18. Converts WGS84 to valid UTM Zone 43N coordinates', () => {
    const utm = wgs84ToUtm43N(p1);
    expect(utm.crs).toBe('EPSG:32643 (UTM 43N)');
    expect(utm.easting).toBeGreaterThan(200000);
    expect(utm.easting).toBeLessThan(400000);
    expect(utm.northing).toBeGreaterThan(2000000);
    expect(utm.northing).toBeLessThan(2200000);
  });

  // 19. Destination Coordinate Calculation
  it('19. Accurately projects coordinate given distance and bearing', () => {
    const dest = computeDestinationCoord(p1, 100, 90);
    const measuredDist = calculateDistanceM(p1, dest);
    const measuredBearing = calculateBearingDeg(p1, dest);
    expect(measuredDist).toBeCloseTo(100, 0);
    expect(measuredBearing).toBeCloseTo(90, 0);
  });

  // 20. Frontage candidate detection
  it('20. Identifies edges with length >= 20m as frontage candidates', () => {
    const rect: Coordinate[] = [p1, p2, p3, p4];
    const edges = getPolygonEdges(rect);
    edges.forEach((e) => {
      expect(e.isFrontageCandidate).toBe(true);
    });
  });
});
