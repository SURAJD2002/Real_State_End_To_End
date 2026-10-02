/**
 * Planwise Enterprise CAD & GIS Geometry Engine
 * Authoritative client-side geometric utilities for snapping, validation,
 * self-intersection detection, UTM Zone 43N conversion, and CAD precision tools.
 * 
 * Note: Statutory land area, setback offsets, and authoritative calculations
 * are calculated by the PostGIS/FastAPI backend. These client-side tools provide
 * instant 60fps interaction, snapping, and validation feedback.
 */

export interface Point2D {
  x: number;
  y: number;
}

export type Coordinate = [number, number]; // [lng, lat]

export interface SnapResult {
  coordinate: Coordinate;
  type: 'VERTEX' | 'EDGE' | 'GRID' | 'ORTHO' | 'ANGLE' | null;
  description?: string;
  sourceVertexIndex?: number;
  sourceEdgeIndex?: number;
}

export interface GeometryValidationResult {
  isValid: boolean;
  error: string | null;
  invalidEdgeIndices: number[];
  hasSelfIntersection: boolean;
  hasZeroLengthEdge: boolean;
  hasDuplicateVertices: boolean;
  isClockwise: boolean;
}

export interface CadEdgeInfo {
  index: number;
  id: string;
  start: Coordinate;
  end: Coordinate;
  lengthM: number;
  bearingDeg: number;
  midpoint: Coordinate;
  isFrontageCandidate?: boolean;
}

const WGS84_A = 6378137.0; // semi-major axis
const WGS84_E2 = 0.00669437999014; // first eccentricity squared
const UTM_K0 = 0.9996; // scale factor
const UTM_FALSE_EASTING = 500000.0;
const ZONE_43_CM = 75.0; // Central meridian for UTM Zone 43N (Mumbai region)

/**
 * Calculates geodesic distance in meters between two [lng, lat] coordinates
 */
export function calculateDistanceM(coord1: Coordinate, coord2: Coordinate): number {
  const [lng1, lat1] = coord1;
  const [lng2, lat2] = coord2;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const radLat1 = (lat1 * Math.PI) / 180;
  const radLat2 = (lat2 * Math.PI) / 180;

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(radLat1) * Math.cos(radLat2) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return 6371000 * c;
}

/**
 * Calculates initial bearing in degrees (0 - 360° clockwise from True North)
 */
export function calculateBearingDeg(coord1: Coordinate, coord2: Coordinate): number {
  const [lng1, lat1] = coord1;
  const [lng2, lat2] = coord2;
  const radLat1 = (lat1 * Math.PI) / 180;
  const radLat2 = (lat2 * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;

  const y = Math.sin(dLng) * Math.cos(radLat2);
  const x =
    Math.cos(radLat1) * Math.sin(radLat2) -
    Math.sin(radLat1) * Math.cos(radLat2) * Math.cos(dLng);
  const bearing = (Math.atan2(y, x) * 180) / Math.PI;
  return (bearing + 360) % 360;
}

/**
 * Computes midpoint between two coordinates
 */
export function calculateMidpoint(coord1: Coordinate, coord2: Coordinate): Coordinate {
  return [(coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2];
}

/**
 * Converts WGS84 [lng, lat] to local metric flat coordinates centered at refLat
 */
export function toLocalMetric(coord: Coordinate, refLat: number): Point2D {
  const mPerDegLat = 111132.95;
  const mPerDegLng = 111412.84 * Math.cos((refLat * Math.PI) / 180);
  return {
    x: coord[0] * mPerDegLng,
    y: coord[1] * mPerDegLat
  };
}

/**
 * Converts local metric point back to WGS84 [lng, lat]
 */
export function fromLocalMetric(pt: Point2D, refLat: number): Coordinate {
  const mPerDegLat = 111132.95;
  const mPerDegLng = 111412.84 * Math.cos((refLat * Math.PI) / 180);
  return [pt.x / mPerDegLng, pt.y / mPerDegLat];
}

/**
 * Converts WGS84 [lng, lat] to UTM Zone 43N (EPSG:32643) Easting & Northing
 */
export function wgs84ToUtm43N(coord: Coordinate): { easting: number; northing: number; crs: string } {
  const [lng, lat] = coord;
  const radLat = (lat * Math.PI) / 180;
  const radLng = (lng * Math.PI) / 180;
  const radCm = (ZONE_43_CM * Math.PI) / 180;

  const ePrimeSq = WGS84_E2 / (1 - WGS84_E2);
  const n = WGS84_A / Math.sqrt(1 - WGS84_E2 * Math.sin(radLat) * Math.sin(radLat));
  const t = Math.tan(radLat) * Math.tan(radLat);
  const c = ePrimeSq * Math.cos(radLat) * Math.cos(radLat);
  const a = Math.cos(radLat) * (radLng - radCm);

  // Meridian distance
  const m =
    WGS84_A *
    ((1 - WGS84_E2 / 4 - (3 * WGS84_E2 * WGS84_E2) / 64 - (5 * WGS84_E2 * WGS84_E2 * WGS84_E2) / 256) * radLat -
      ((3 * WGS84_E2) / 8 + (3 * WGS84_E2 * WGS84_E2) / 32 + (45 * WGS84_E2 * WGS84_E2 * WGS84_E2) / 1024) *
        Math.sin(2 * radLat) +
      ((15 * WGS84_E2 * WGS84_E2) / 256 + (45 * WGS84_E2 * WGS84_E2 * WGS84_E2) / 1024) * Math.sin(4 * radLat) -
      ((35 * WGS84_E2 * WGS84_E2 * WGS84_E2) / 3072) * Math.sin(6 * radLat));

  const easting =
    UTM_FALSE_EASTING +
    UTM_K0 *
      n *
      (a +
        ((1 - t + c) * Math.pow(a, 3)) / 6 +
        ((5 - 18 * t + t * t + 72 * c - 58 * ePrimeSq) * Math.pow(a, 5)) / 120);

  const northing =
    UTM_K0 *
    (m +
      n *
        Math.tan(radLat) *
        ((a * a) / 2 +
          ((5 - t + 9 * c + 4 * c * c) * Math.pow(a, 4)) / 24 +
          ((61 - 58 * t + t * t + 600 * c - 330 * ePrimeSq) * Math.pow(a, 6)) / 720));

  return {
    easting: Math.round(easting * 100) / 100,
    northing: Math.round(northing * 100) / 100,
    crs: 'EPSG:32643 (UTM 43N)'
  };
}

/**
 * Computes polygon spherical metric area in m² and perimeter in meters
 */
export function computePolygonMetrics(coords: Coordinate[]): { areaSqm: number; perimeterM: number } {
  if (coords.length < 3) return { areaSqm: 0, perimeterM: 0 };
  const refLat = coords[0][1];
  const mPerDegLat = 111132.95;
  const mPerDegLng = 111412.84 * Math.cos((refLat * Math.PI) / 180);

  let area = 0;
  let perimeter = 0;
  const n = coords.length;

  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const xi = coords[i][0] * mPerDegLng;
    const yi = coords[i][1] * mPerDegLat;
    const xj = coords[j][0] * mPerDegLng;
    const yj = coords[j][1] * mPerDegLat;

    area += xi * yj - xj * yi;
    const dx = xj - xi;
    const dy = yj - yi;
    perimeter += Math.sqrt(dx * dx + dy * dy);
  }

  return {
    areaSqm: Math.round(Math.abs(area) / 2 * 100) / 100,
    perimeterM: Math.round(perimeter * 10) / 10
  };
}

/**
 * Computes properties of all edges of the polygon
 */
export function getPolygonEdges(coords: Coordinate[], _roadContextWidth?: number): CadEdgeInfo[] {
  if (coords.length < 2) return [];
  const edges: CadEdgeInfo[] = [];
  const n = coords.length;

  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const start = coords[i];
    const end = coords[j];
    const lengthM = Math.round(calculateDistanceM(start, end) * 100) / 100;
    const bearingDeg = Math.round(calculateBearingDeg(start, end) * 10) / 10;
    const midpoint = calculateMidpoint(start, end);

    // Frontage candidate heuristic: longest edges or edges facing standard road alignments
    const isFrontageCandidate = lengthM >= 20.0;

    edges.push({
      index: i,
      id: `E${String(i + 1).padStart(2, '0')}`,
      start,
      end,
      lengthM,
      bearingDeg,
      midpoint,
      isFrontageCandidate
    });
  }

  return edges;
}

/**
 * Tests whether two 2D line segments AB and CD intersect
 */
function ccw(p1: Point2D, p2: Point2D, p3: Point2D): number {
  return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x);
}

function segmentsIntersect(a: Point2D, b: Point2D, c: Point2D, d: Point2D): boolean {
  const ccw1 = ccw(a, b, c);
  const ccw2 = ccw(a, b, d);
  const ccw3 = ccw(c, d, a);
  const ccw4 = ccw(c, d, b);

  return (
    ((ccw1 > 0 && ccw2 < 0) || (ccw1 < 0 && ccw2 > 0)) &&
    ((ccw3 > 0 && ccw4 < 0) || (ccw3 < 0 && ccw4 > 0))
  );
}

/**
 * Validates parcel polygon geometry against standard cadastral rules:
 * - Minimum 3 vertices
 * - No duplicate consecutive vertices
 * - No zero-length edges
 * - No self-intersections
 */
export function validateParcelGeometry(coords: Coordinate[]): GeometryValidationResult {
  if (coords.length < 3) {
    return {
      isValid: false,
      error: 'A parcel polygon requires at least 3 vertices to form a closed boundary.',
      invalidEdgeIndices: [],
      hasSelfIntersection: false,
      hasZeroLengthEdge: false,
      hasDuplicateVertices: false,
      isClockwise: false
    };
  }

  const refLat = coords[0][1];
  const pts = coords.map((c) => toLocalMetric(c, refLat));
  const n = pts.length;
  const invalidEdges = new Set<number>();
  let hasZeroLengthEdge = false;
  let hasDuplicateVertices = false;

  // 1. Check duplicate consecutive vertices / zero-length edges
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const dx = pts[j].x - pts[i].x;
    const dy = pts[j].y - pts[i].y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < 0.2) {
      // Less than 20cm
      hasZeroLengthEdge = true;
      hasDuplicateVertices = true;
      invalidEdges.add(i);
    }
  }

  // 2. Check self-intersections (pairwise segment intersection)
  let hasSelfIntersection = false;
  let selfIntersectDesc: string | null = null;

  for (let i = 0; i < n; i++) {
    const iNext = (i + 1) % n;
    const seg1A = pts[i];
    const seg1B = pts[iNext];

    for (let j = i + 2; j < n; j++) {
      const jNext = (j + 1) % n;
      // Skip closing edge adjacency with first vertex
      if (i === 0 && jNext === 0) continue;

      const seg2A = pts[j];
      const seg2B = pts[jNext];

      if (segmentsIntersect(seg1A, seg1B, seg2A, seg2B)) {
        hasSelfIntersection = true;
        invalidEdges.add(i);
        invalidEdges.add(j);
        if (!selfIntersectDesc) {
          selfIntersectDesc = `Self-intersection detected between Edge E${String(i + 1).padStart(2, '0')} and Edge E${String(j + 1).padStart(2, '0')}.`;
        }
      }
    }
  }

  // 3. Compute winding order
  let signedArea = 0;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    signedArea += pts[i].x * pts[j].y - pts[j].x * pts[i].y;
  }
  const isClockwise = signedArea < 0;

  if (hasSelfIntersection) {
    return {
      isValid: false,
      error: selfIntersectDesc || 'Self-intersection detected in parcel boundary.',
      invalidEdgeIndices: Array.from(invalidEdges),
      hasSelfIntersection: true,
      hasZeroLengthEdge,
      hasDuplicateVertices,
      isClockwise
    };
  }

  if (hasZeroLengthEdge) {
    return {
      isValid: false,
      error: 'Duplicate or zero-length edges detected. Vertices must be distinct by ≥0.20m.',
      invalidEdgeIndices: Array.from(invalidEdges),
      hasSelfIntersection: false,
      hasZeroLengthEdge: true,
      hasDuplicateVertices: true,
      isClockwise
    };
  }

  return {
    isValid: true,
    error: null,
    invalidEdgeIndices: [],
    hasSelfIntersection: false,
    hasZeroLengthEdge: false,
    hasDuplicateVertices: false,
    isClockwise
  };
}

/**
 * Snaps a cursor coordinate against existing vertices within a screen/world metric tolerance
 */
export function snapToVertex(
  cursorCoord: Coordinate,
  vertices: Coordinate[],
  toleranceM: number = 6.0,
  excludeIndex: number = -1
): { snapped: Coordinate; index: number } | null {
  let closestDist = Infinity;
  let closestIndex = -1;

  for (let i = 0; i < vertices.length; i++) {
    if (i === excludeIndex) continue;
    const dist = calculateDistanceM(cursorCoord, vertices[i]);
    if (dist <= toleranceM && dist < closestDist) {
      closestDist = dist;
      closestIndex = i;
    }
  }

  if (closestIndex !== -1) {
    return { snapped: vertices[closestIndex], index: closestIndex };
  }
  return null;
}

/**
 * Snaps a cursor coordinate against polygon edges (orthogonal projection)
 */
export function snapToEdge(
  cursorCoord: Coordinate,
  vertices: Coordinate[],
  toleranceM: number = 5.0
): { snapped: Coordinate; edgeIndex: number } | null {
  if (vertices.length < 2) return null;
  const refLat = cursorCoord[1];
  const cursorPt = toLocalMetric(cursorCoord, refLat);
  const pts = vertices.map((c) => toLocalMetric(c, refLat));

  let closestDist = Infinity;
  let bestSnappedPt: Point2D | null = null;
  let bestEdgeIdx = -1;

  const n = pts.length;
  for (let i = 0; i < n; i++) {
    const j = (i + 1) % n;
    const p1 = pts[i];
    const p2 = pts[j];

    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const lenSq = dx * dx + dy * dy;

    if (lenSq === 0) continue;

    // Projection scalar t on line segment
    const t = Math.max(0, Math.min(1, ((cursorPt.x - p1.x) * dx + (cursorPt.y - p1.y) * dy) / lenSq));
    const projX = p1.x + t * dx;
    const projY = p1.y + t * dy;

    const dist = Math.hypot(cursorPt.x - projX, cursorPt.y - projY);
    if (dist <= toleranceM && dist < closestDist) {
      closestDist = dist;
      bestSnappedPt = { x: projX, y: projY };
      bestEdgeIdx = i;
    }
  }

  if (bestSnappedPt && bestEdgeIdx !== -1) {
    return {
      snapped: fromLocalMetric(bestSnappedPt, refLat),
      edgeIndex: bestEdgeIdx
    };
  }

  return null;
}

/**
 * Snaps an edge to Ortho angles (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°) from anchor
 */
export function snapToOrtho(anchor: Coordinate, cursor: Coordinate): Coordinate {
  const refLat = anchor[1];
  const aPt = toLocalMetric(anchor, refLat);
  const cPt = toLocalMetric(cursor, refLat);

  const dx = cPt.x - aPt.x;
  const dy = cPt.y - aPt.y;
  const dist = Math.hypot(dx, dy);

  if (dist < 0.1) return cursor;

  let angleRad = Math.atan2(dy, dx);
  // Round to nearest 45° (PI / 4)
  const stepRad = Math.PI / 4;
  angleRad = Math.round(angleRad / stepRad) * stepRad;

  const snappedPt: Point2D = {
    x: aPt.x + dist * Math.cos(angleRad),
    y: aPt.y + dist * Math.sin(angleRad)
  };

  return fromLocalMetric(snappedPt, refLat);
}

/**
 * Snaps to arbitrary angle increment (e.g. 5°, 10°, 15°, 30°, 45°, 90°) from anchor
 */
export function snapToAngleIncrement(
  anchor: Coordinate,
  cursor: Coordinate,
  stepDeg: number = 15
): Coordinate {
  const refLat = anchor[1];
  const aPt = toLocalMetric(anchor, refLat);
  const cPt = toLocalMetric(cursor, refLat);

  const dx = cPt.x - aPt.x;
  const dy = cPt.y - aPt.y;
  const dist = Math.hypot(dx, dy);

  if (dist < 0.1) return cursor;

  let angleDeg = (Math.atan2(dy, dx) * 180) / Math.PI;
  angleDeg = Math.round(angleDeg / stepDeg) * stepDeg;
  const angleRad = (angleDeg * Math.PI) / 180;

  const snappedPt: Point2D = {
    x: aPt.x + dist * Math.cos(angleRad),
    y: aPt.y + dist * Math.sin(angleRad)
  };

  return fromLocalMetric(snappedPt, refLat);
}

/**
 * Snaps cursor coordinate to metric grid interval (e.g. 0.5m, 1m, 5m, 10m) relative to anchor
 */
export function snapToMetricGrid(cursor: Coordinate, anchor: Coordinate, gridM: number = 1.0): Coordinate {
  const refLat = anchor[1];
  const aPt = toLocalMetric(anchor, refLat);
  const cPt = toLocalMetric(cursor, refLat);

  const dx = cPt.x - aPt.x;
  const dy = cPt.y - aPt.y;

  const snappedDx = Math.round(dx / gridM) * gridM;
  const snappedDy = Math.round(dy / gridM) * gridM;

  const snappedPt: Point2D = {
    x: aPt.x + snappedDx,
    y: aPt.y + snappedDy
  };

  return fromLocalMetric(snappedPt, refLat);
}

/**
 * Complete Snapping Hierarchy Engine:
 * 1. Existing Vertex (highest priority)
 * 2. Existing Edge
 * 3. Additional Context (Building Footprint / Buildable Envelope)
 * 4. Metric Grid
 * 5. Ortho / Angle Snap
 */
export function resolveSnap(
  cursorCoord: Coordinate,
  parcelVertices: Coordinate[],
  options: {
    anchorCoord?: Coordinate;
    isOrtho?: boolean;
    isGridSnap?: boolean;
    gridSizeM?: number;
    isAngleSnap?: boolean;
    angleStepDeg?: number;
    externalGeometry?: Coordinate[];
    excludeVertexIdx?: number;
    vertexToleranceM?: number;
    edgeToleranceM?: number;
  }
): SnapResult {
  const {
    anchorCoord,
    isOrtho = false,
    isGridSnap = false,
    gridSizeM = 1.0,
    isAngleSnap = false,
    angleStepDeg = 15,
    externalGeometry,
    excludeVertexIdx = -1,
    vertexToleranceM = 6.0,
    edgeToleranceM = 4.5
  } = options;

  // 1. Parcel Vertex Snap
  const vSnap = snapToVertex(cursorCoord, parcelVertices, vertexToleranceM, excludeVertexIdx);
  if (vSnap) {
    return {
      coordinate: vSnap.snapped,
      type: 'VERTEX',
      description: `SNAP VERTEX V${vSnap.index + 1}`,
      sourceVertexIndex: vSnap.index
    };
  }

  // 2. External Geometry Vertex Snap (e.g. Buildable Envelope or Building Footprint)
  if (externalGeometry && externalGeometry.length > 0) {
    const extSnap = snapToVertex(cursorCoord, externalGeometry, vertexToleranceM);
    if (extSnap) {
      return {
        coordinate: extSnap.snapped,
        type: 'VERTEX',
        description: `SNAP SITE FEATURE`,
        sourceVertexIndex: extSnap.index
      };
    }
  }

  // 3. Parcel Edge Snap
  const eSnap = snapToEdge(cursorCoord, parcelVertices, edgeToleranceM);
  if (eSnap) {
    return {
      coordinate: eSnap.snapped,
      type: 'EDGE',
      description: `SNAP EDGE E${String(eSnap.edgeIndex + 1).padStart(2, '0')}`,
      sourceEdgeIndex: eSnap.edgeIndex
    };
  }

  // 4. Metric Grid Snap
  if (isGridSnap && anchorCoord) {
    const gridCoord = snapToMetricGrid(cursorCoord, anchorCoord, gridSizeM);
    return {
      coordinate: gridCoord,
      type: 'GRID',
      description: `SNAP GRID (${gridSizeM}m)`
    };
  }

  // 5. Ortho Snap
  if (isOrtho && anchorCoord) {
    const orthoCoord = snapToOrtho(anchorCoord, cursorCoord);
    return {
      coordinate: orthoCoord,
      type: 'ORTHO',
      description: `ORTHO SNAP`
    };
  }

  // 6. Configurable Angle Snap
  if (isAngleSnap && anchorCoord) {
    const angleCoord = snapToAngleIncrement(anchorCoord, cursorCoord, angleStepDeg);
    return {
      coordinate: angleCoord,
      type: 'ANGLE',
      description: `ANGLE SNAP ${angleStepDeg}°`
    };
  }

  return {
    coordinate: cursorCoord,
    type: null
  };
}

/**
 * Computes destination point given start coordinate, distance (meters), and bearing (degrees)
 */
export function computeDestinationCoord(start: Coordinate, distanceM: number, bearingDeg: number): Coordinate {
  const [lng1, lat1] = start;
  const radLat1 = (lat1 * Math.PI) / 180;
  const radLng1 = (lng1 * Math.PI) / 180;
  const radBearing = (bearingDeg * Math.PI) / 180;
  const angularDist = distanceM / 6371000;

  const radLat2 = Math.asin(
    Math.sin(radLat1) * Math.cos(angularDist) +
      Math.cos(radLat1) * Math.sin(angularDist) * Math.cos(radBearing)
  );
  const radLng2 =
    radLng1 +
    Math.atan2(
      Math.sin(radBearing) * Math.sin(angularDist) * Math.cos(radLat1),
      Math.cos(angularDist) - Math.sin(radLat1) * Math.sin(radLat2)
    );

  return [((radLng2 * 180) / Math.PI + 540) % 360 - 180, (radLat2 * 180) / Math.PI];
}
