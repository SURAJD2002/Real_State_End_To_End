export type ToolMode =
  | 'SELECT'
  | 'DRAW_PARCEL'
  | 'DRAW_ROAD'
  | 'DRAW_CONSTRAINT'
  | 'SETBACK_BUFFER'
  | 'DELETE';

export interface FinancialMetrics {
  currency: string;
  grossDevelopmentValue: number;
  civilConstructionCost: number;
  statutoryApprovalPremiums: number;
  softCostsAndMarketing: number;
  financingCost: number;
  totalDevelopmentCost: number;
  netMarginValue: number;
  netMarginPercent: number;
  equityIRRPercent: number;
}

export interface FeasibilityResult {
  runId: string;
  projectId: string;
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
  carpetAreaSqm: number;
  maxBuildingHeightM: number;
  frontSetbackM: number;
  standardParkingStalls: number;
  accessibleParkingStalls: number;
  financials: FinancialMetrics;
  buildableCoordinates?: [number, number][];
}

export interface ProjectData {
  id: string;
  name: string;
  description?: string;
  jurisdiction: string;
  status: 'DRAFT' | 'FEASIBILITY_RUNNING' | 'COMPLETED' | 'ARCHIVED';
  createdAt: string;
  updatedAt: string;
  parcel?: {
    coordinates: [number, number][];
    cadastralNumber: string;
    tenureType: string;
    existingRoadWidthM: number;
    proposedRoadWidthM: number;
    version: number;
  };
  latestFeasibility?: FeasibilityResult | null;
}
