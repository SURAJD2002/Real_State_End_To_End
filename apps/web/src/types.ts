export type ToolMode =
  | 'SELECT'
  | 'DRAW_PARCEL'
  | 'DRAW_ROAD'
  | 'DRAW_CONSTRAINT'
  | 'SETBACK_BUFFER'
  | 'DELETE';

export type AppViewMode = 'CUSTOMER_STUDIO' | 'ENGINEER_DASHBOARD';

export interface RoomBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface RoomElement {
  id: string;
  name: string;
  zone: string;
  floor: string;
  color: string;
  areaSqm: number;
  widthM: number;
  lengthM: number;
  bounds: RoomBounds;
}

export interface ColumnElement {
  id: string;
  x: number;
  y: number;
  widthMm: number;
  depthMm: number;
}

export interface HouseLayout {
  solverStatus: string;
  archetype: string;
  label: string;
  description: string;
  floors: number;
  totalUsableAreaSqm: number;
  totalGrossBUASqm: number;
  buildingEnvelope: {
    widthM: number;
    lengthM: number;
    heightM: number;
  };
  rooms: RoomElement[];
  columns: ColumnElement[];
}

export interface ParetoScores {
  overallScore: number;
  areaEfficiencyPercent: number;
  daylightProxy: number;
  ventilationProxy: number;
  privacyProxy: number;
  circulationQuality: number;
  budgetFitScore: number;
  constructabilityScore: number;
}

export interface BOQLineItem {
  code: string;
  description: string;
  quantity: number;
  unit: string;
  unitRate: number;
  amount: number;
  sourceRefs: string;
  wastePolicy: string;
}

export interface BOQData {
  rateSnapshotId: string;
  qualityTier: string;
  currency: string;
  directHardCost: number;
  contingency: number;
  contractorPrelims: number;
  totalBaseEstimate: number;
  estimateRange: {
    low: number;
    expected: number;
    high: number;
  };
  costPerSqmBUA: number;
  costPerSqFtBUA: number;
  lines: BOQLineItem[];
}

export interface CPMActivity {
  code: string;
  name: string;
  workPackage: string;
  durationWeeks: number;
  startWeek: number;
  endWeek: number;
  predecessors: string[];
  critical: boolean;
  crew: string;
}

export interface CPMSchedule {
  scheduleMethod: string;
  totalDurationWeeks: number;
  totalDurationMonths: number;
  estimatedDays: number;
  criticalPathCount: number;
  activities: CPMActivity[];
}

export interface HouseOption {
  optionId: string;
  designVersionId: string;
  designHash: string;
  layout: HouseLayout;
  scores: ParetoScores;
  boq: BOQData;
  schedule: CPMSchedule;
  compliance: {
    statutorySetbacks: string;
    nbcRoomMinimums: string;
    lightVentilation: string;
    fireEgress: string;
    structuralGridCheck: string;
  };
}

export interface VerificationGate {
  gate: string;
  title: string;
  status: 'APPROVED' | 'PENDING_REVIEW' | 'LOCKED' | 'AWAITING_PREREQUISITE' | 'REJECTED';
  requiredBy: string;
  verifiedBy?: string;
  verifiedAt?: string;
  notes?: string;
}

export interface ArtifactItem {
  name: string;
  type: string;
  hash: string;
}

export interface HandoffPackage {
  handoffPackageId: string;
  releaseFingerprint: string;
  releaseStatus: string;
  lifecycleState: string;
  createdAt: string;
  projectContext: {
    projectName: string;
    jurisdiction: string;
    statutoryRuleSet: string;
    buildingCode: string;
    cadastralSurveyNo: string;
    surveyConfidence: string;
  };
  designOption: {
    archetype: string;
    title: string;
    totalGrossBUASqm: number;
    totalUsableAreaSqm: number;
    floors: number;
    roomCount: number;
    columnCount: number;
  };
  financialSummary: {
    currency: string;
    baseEstimate: number;
    lowRange: number;
    highRange: number;
    costPerSqFt: number;
  };
  constructionSummary: {
    durationWeeks: number;
    durationMonths: number;
    activitiesCount: number;
    criticalPathActivities: number;
  };
  humanVerificationGates: VerificationGate[];
  artifactManifest: ArtifactItem[];
}

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
  activeRelease?: {
    releaseId: string;
    fingerprint: string;
    lifecycleState: string;
    handoffPackage: HandoffPackage;
  } | null;
}
