/**
 * Real Estate Development Intelligence Platform
 * Shared Domain Types & GeoJSON Contracts
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

export interface ProjectEntity {
  id: string;
  name: string;
  description?: string;
  jurisdiction: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
  parcel?: ParcelGeometry;
  roads?: RoadFrontage[];
  constraints?: ParcelConstraint[];
  latestFeasibility?: FeasibilityRunResult;
}
