export type ToolMode =
  | 'SELECT'
  | 'DRAW_PARCEL'
  | 'DRAW_ROAD'
  | 'DRAW_CONSTRAINT'
  | 'SETBACK_BUFFER'
  | 'DELETE';

export type WorkflowStep =
  | 'SITE'
  | 'FEASIBILITY'
  | 'DESIGN'
  | 'COST'
  | 'BUILD'
  | 'ENGINEER';

export type CanvasViewMode =
  | '2D_PLAN'
  | 'SITE_MAP'
  | '3D_AXONO'
  | 'ELEVATION'
  | 'SECTION';

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
  orientation?: string;
  daylight?: string;
  ventilation?: string;
  privacy?: string;
  doorsCount?: number;
  windowsCount?: number;
  finishes?: string;
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
  itemCode?: string;
  boqItemId?: string;
  section?: string;
  description: string;
  specification?: string;
  category?: string;
  quantity: number;
  unit: string;
  unitRate: number;
  amount: number;
  materialRate?: number;
  labourRate?: number;
  equipmentRate?: number;
  materialAmount?: number;
  labourAmount?: number;
  equipmentAmount?: number;
  wastageAmount?: number;
  sourceRefs: string;
  canonicalElementIds?: string[];
  sourceElementIds?: string[];
  measurementRuleId?: string;
  wastePolicy: string;
  confidence?: string;
  sourceType?: string;
  rateSnapshotId?: string;
  assemblyId?: string;
  status?: string;
}

export interface CostWaterfallData {
  grossHardCost: number;
  directMaterialCost: number;
  directLabourCost: number;
  directEquipmentCost: number;
  materialWastageCost: number;
  overheadAndPrelims: number;
  contingency: number;
  statutoryTaxes: number;
  totalConstructionCost: number;
  costPerSqFtBUA: number;
  costPerSqmBUA: number;
  costPerCarpetSqFt: number;
  costPerCarpetSqm: number;
  areaBasis?: {
    grossBUASqm: number;
    grossBUASqFt: number;
    carpetAreaSqm: number;
    carpetAreaSqFt: number;
  };
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
  costWaterfall?: CostWaterfallData;
  lines: BOQLineItem[];
  qtoHash?: string;
  boqHash?: string;
  costHash?: string;
  confidenceSummary?: Record<string, number>;
  disclaimer?: string;
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
  buildingModelId?: string;
  buildingModel?: CanonicalBuildingModel;
  validation?: ValidationSummary;
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

export type GateCode = 'G0' | 'G1' | 'G2' | 'G3' | 'G4' | 'G5' | 'G6';

export type GateStatus = 
  | 'PENDING' 
  | 'SYSTEM_VERIFIED' 
  | 'PROFESSIONAL_REVIEW' 
  | 'VERIFIED' 
  | 'REVIEWED' 
  | 'CHANGES_REQUIRED' 
  | 'LOCKED';

export type IssueSeverity = 'INFO' | 'WARNING' | 'BLOCKER';

export type IssueStatus = 'OPEN' | 'RESOLVED' | 'WAIVED';

export type ReviewDecisionType = 'APPROVE_STAGE' | 'REQUEST_CHANGES' | 'CANNOT_PROCEED';

export type ReviewStatus = 
  | 'PENDING_ASSIGNMENT' 
  | 'IN_REVIEW' 
  | 'CHANGES_REQUIRED' 
  | 'APPROVED' 
  | 'REJECTED' 
  | 'STALE';

export interface ReviewGate {
  id: string;
  engineerReviewId: string;
  gateCode: GateCode;
  title: string;
  status: GateStatus;
  reviewedBy?: string;
  reviewedAt?: string;
  notes?: string;
  requiredForRelease: boolean;
}

export interface ReviewIssue {
  id: string;
  engineerReviewId: string;
  gateCode: GateCode;
  severity: IssueSeverity;
  category: string;
  description: string;
  requiredAction: string;
  status: IssueStatus;
  createdBy: string;
  createdAt: string;
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface ReviewDecision {
  id: string;
  engineerReviewId: string;
  decision: ReviewDecisionType;
  decidedBy: string;
  decidedAt: string;
  reason: string;
}

export interface EngineerReviewData {
  id: string;
  projectId: string;
  buildRequestId: string;
  releaseId: string;
  designVersionId: string;
  reviewerId: string;
  status: ReviewStatus;
  createdAt: string;
  updatedAt: string;
  inputManifestHash: string;
  designVersionHash: string;
  declaredPlotAreaSqFt: number;
  gates: ReviewGate[];
  issues: ReviewIssue[];
  decisions: ReviewDecision[];
}
