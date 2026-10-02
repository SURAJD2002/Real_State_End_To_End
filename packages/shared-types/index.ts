/**
 * Real Estate Development Intelligence Platform
 * Shared Domain Types & Canonical Building Model Contracts
 */

export type LandTenureType =
  | 'PRIVATE_FREEHOLD'
  | 'COLLECTOR_CLASS_2'
  | 'COLLECTOR_LEASEHOLD'
  | 'GOVERNMENT_LEASEHOLD'
  | 'MHADA_REDEVELOPMENT'
  | 'MUNICIPAL_ALLOTMENT';

export type ConstraintSeverity =
  | 'HARD_ABSOLUTE_EXCLUSION'
  | 'CONDITIONAL_NOC_REQUIRED'
  | 'HEIGHT_RESTRICTION_SURFACE'
  | 'SETBACK_OFFSET_MODIFIER';

export type ProjectStatus =
  | 'DRAFT'
  | 'FEASIBILITY_RUNNING'
  | 'COMPLETED'
  | 'ARCHIVED';

export type ToolMode =
  | 'SELECT'
  | 'DRAW_PARCEL'
  | 'DRAW_ROAD'
  | 'DRAW_CONSTRAINT'
  | 'SETBACK_BUFFER'
  | 'MEASURE'
  | 'DELETE';

export interface RoadFrontage {
  id: string;
  name: string;
  existingWidthM: number;
  proposedWidthM?: number;
  isPrimaryAccess: boolean;
  coordinates: [number, number][]; // [[lng, lat], ...]
}

export interface ParcelConstraint {
  id: string;
  name: string;
  category: 'TREE_BUFFER' | 'UTILITY_CORRIDOR' | 'HIGH_TENSION_LINE' | 'WATER_BODY' | 'HERITAGE';
  severity: ConstraintSeverity;
  bufferDistanceM: number;
  coordinates: [number, number][] | [number, number]; // Polygon or Point
}

export interface ParcelGeometry {
  type: 'Feature';
  properties: {
    parcelId: string;
    cadastralNumber: string;
    tenureType: LandTenureType;
    sridProjected: number;
    version: number;
  };
  geometry: {
    type: 'Polygon';
    coordinates: [number, number][][];
  };
}

export interface FeasibilityRunResult {
  runId: string;
  projectId: string;
  parcelId: string;
  timestamp: string;
  regulationVersionId: string;
  engineVersion: string;
  grossPlotAreaSqm: number;
  roadWideningDeductionSqm: number;
  amenityReservationSqm: number;
  netDevelopableAreaSqm: number;
  baseFSI: number;
  premiumFSI: number;
  tdrFSI: number;
  totalPermissibleFSI: number;
  permissibleBUASqm: number;
  maxBuildingHeightM: number;
  standardParkingStalls: number;
  accessibleParkingStalls: number;
  financials: {
    currency: string;
    grossDevelopmentValue: number;
    civilConstructionCost: number;
    statutoryApprovalPremiums: number;
    financingCost: number;
    totalDevelopmentCost: number;
    netMarginValue: number;
    netMarginPercent: number;
    equityIRRPercent: number;
  };
  buildableFootprintCoordinates: [number, number][][];
}

// =========================================================================
// CANONICAL BUILDING MODEL CONTRACTS (Delta Spec §1, §7, §8, §12, §13, §26)
// =========================================================================

export type ElementType =
  | 'WALL'
  | 'COLUMN'
  | 'BEAM'
  | 'SLAB'
  | 'STAIR'
  | 'ROOF'
  | 'FOUNDATION'
  | 'PARAPET';

export type WallType =
  | 'EXTERNAL'
  | 'INTERNAL'
  | 'PARTITION'
  | 'RETAINING'
  | 'PARAPET';

export type OpeningType =
  | 'DOOR'
  | 'WINDOW'
  | 'OPENING_VOID';

export type StructuralRole =
  | 'LOADBEARING'
  | 'NON_LOADBEARING'
  | 'PRIMARY_FRAME'
  | 'FOUNDATION';

export interface BuildingLevel {
  levelId: string;
  levelIndex: number;
  name: string;
  elevationM: number;
  floorToFloorHeightM: number;
  usage: string;
}

export interface CanonicalSpace {
  spaceId: string;
  levelId: string;
  spaceType: string;
  name: string;
  zone: 'PUBLIC' | 'PRIVATE' | 'SERVICE' | 'CIRCULATION' | 'SEMI_OUTDOOR' | 'OUTDOOR';
  floor: string;
  color: string;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  polygon: [number, number][];
  areaSqm: number;
  perimeterM: number;
  centroid: [number, number];
  heightM: number;
  daylightRequirement: string;
  ventilationRequirement: string;
  privacyRating?: string;
  adjacentSpaceIds: string[];
  boundaryWallIds: string[];
}

export interface ElementGeometry {
  centerline?: [number, number][];
  footprintPolygon: [number, number][];
  baseZ: number;
  topZ: number;
  thicknessM?: number;
  heightM?: number;
  widthM?: number;
  depthM?: number;
}

export interface CanonicalElement {
  elementId: string;
  elementType: ElementType;
  levelId: string;
  name: string;
  geometry: ElementGeometry;
  materialId: string;
  structuralRole: StructuralRole;
  hostId?: string;
  properties?: Record<string, any>;
  wallType?: WallType;
  openingIds?: string[];
  connectedSpaceIds?: string[];
  gridReference?: string;
}

export interface CanonicalOpening {
  openingId: string;
  openingType: OpeningType;
  hostWallId: string;
  levelId: string;
  name: string;
  widthM: number;
  heightM: number;
  sillHeightM: number;
  positionRatio: number;
  positionM: [number, number];
  swing?: string;
  orientation?: string;
  materialId: string;
  properties?: Record<string, any>;
}

export interface GridLine {
  tag: string;
  coordinate: number;
  direction: 'X' | 'Y';
}

export interface StructuralGrid {
  gridLinesX: GridLine[];
  gridLinesY: GridLine[];
  baySpacingXM: number;
  baySpacingYM: number;
}

export interface CanonicalMaterial {
  materialId: string;
  catalogVersion: string;
  category: string;
  name: string;
  grade: string;
  unit: string;
  baseUnitRateInr: number;
}

export interface ValidationIssue {
  ruleId: string;
  category: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'BLOCKER';
  status: 'PASS' | 'FAIL';
  message: string;
  objectIds: string[];
}

export interface ValidationSummary {
  isValid: boolean;
  totalIssues: number;
  blockersCount: number;
  errorsCount: number;
  warningsCount: number;
  infoCount: number;
  issues: ValidationIssue[];
}

export interface CanonicalBuildingModel {
  schemaVersion: string;
  modelId: string;
  designVersionId: string;
  projectId: string;
  siteGeometryVersionId: string;
  regulationVersionId: string;
  name: string;
  archetype: string;
  description: string;
  buildingEnvelope: {
    widthM: number;
    lengthM: number;
    heightM: number;
  };
  totalGrossBUASqm: number;
  totalUsableAreaSqm: number;
  floorsCount: number;
  levels: BuildingLevel[];
  spaces: CanonicalSpace[];
  elements: CanonicalElement[];
  openings: CanonicalOpening[];
  structuralGrid: StructuralGrid;
  materials: CanonicalMaterial[];
  validation?: ValidationSummary;
  metadata: {
    engineName: string;
    engineVersion: string;
    compilationTimestamp: string;
    modelHash: string;
    isLocked: boolean;
  };
}
