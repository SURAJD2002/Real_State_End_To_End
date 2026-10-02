import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { PlanwiseMap } from './components/map/PlanwiseMap';
import { SiteLocationMetadata } from './components/map/types';
import { FeasibilityHUD } from './components/FeasibilityHUD';
import { HouseOptionsCarousel } from './components/HouseOptionsCarousel';
import { FloorPlanViewer } from './components/FloorPlanViewer';
import { CostExperienceView } from './components/CostExperienceView';
import { BuildReleaseView } from './components/BuildReleaseView';
import { BOQTableModal } from './components/BOQTableModal';
import { BuildLockModal } from './components/BuildLockModal';
import { SiteEvidencePanel } from './components/SiteEvidencePanel';
import { LandIntakeView } from './components/LandIntakeView';
import { FeasibilitySummaryView } from './components/FeasibilitySummaryView';
import { DesignIntakeView, CustomerDesignRequirements } from './components/DesignIntakeView';
import { DesignOptionsView } from './components/DesignOptionsView';
import { CostSummaryView } from './components/CostSummaryView';
import { BuildReviewView } from './components/BuildReviewView';
import { EngineerReviewView } from './components/EngineerReviewView';
import { 
  WorkflowStep, 
  ProjectData, 
  FeasibilityResult, 
  HouseOption, 
  HandoffPackage 
} from './types';
import { ArrowRight, ShieldCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [project, setProject] = useState<ProjectData | null>(null);
  const [activeStep, setActiveStep] = useState<WorkflowStep>('SITE');
  const [viewMode, setViewMode] = useState<'CUSTOMER' | 'TECHNICAL'>('CUSTOMER');
  const [coordinates, setCoordinates] = useState<[number, number][]>([]);
  const [existingRoadWidth, setExistingRoadWidth] = useState<number>(12.0);
  const [proposedRoadWidth, setProposedRoadWidth] = useState<number>(18.0);
  const [feasibility, setFeasibility] = useState<FeasibilityResult | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const [isEvidencePanelOpen, setIsEvidencePanelOpen] = useState<boolean>(true);

  // House Generation & Delivery State
  const [houseOptions, setHouseOptions] = useState<HouseOption[]>([]);
  const [selectedOptionId, setSelectedOptionId] = useState<string>('opt-compact_2bhk');
  const [selectedBOQOption, setSelectedBOQOption] = useState<HouseOption | null>(null);
  const [buildModalOption, setBuildModalOption] = useState<HouseOption | null>(null);
  const [isLockingBuild, setIsLockingBuild] = useState<boolean>(false);
  const [activeReleaseId, setActiveReleaseId] = useState<string>('');
  const [handoffPackage, setHandoffPackage] = useState<HandoffPackage | null>(null);

  // Customer Mode: Design Intake & Options Step State
  const [designPhase, setDesignPhase] = useState<'INTAKE' | 'OPTIONS'>('INTAKE');
  const [isGeneratingDesign, setIsGeneratingDesign] = useState<boolean>(false);
  const [customerRequirements, setCustomerRequirements] = useState<CustomerDesignRequirements | null>(null);

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const apiBase = '/api/v1';

  // 1. Initial Load: Fetch default project and house options
  useEffect(() => {
    fetch(`${apiBase}/projects`)
      .then((res) => res.json())
      .then((projects: ProjectData[]) => {
        if (projects && projects.length > 0) {
          const p = projects[0];
          setProject(p);
          if (p.parcel && p.parcel.coordinates) {
            setCoordinates(p.parcel.coordinates);
            setExistingRoadWidth(p.parcel.existingRoadWidthM || 4.88);
            setProposedRoadWidth(p.parcel.proposedRoadWidthM || 4.88);
          }
          if (p.latestFeasibility) {
            setFeasibility(p.latestFeasibility);
          }
        }
      })
      .catch((err) => {
        console.warn('API Gateway offline. Using fallback initial coordinates.', err);
        const defaultCoords: [number, number][] = [
          [72.82950, 19.05960],
          [72.82958, 19.05960],
          [72.82958, 19.05971],
          [72.82950, 19.05971],
          [72.82950, 19.05960]
        ];
        setCoordinates(defaultCoords);
      });

    // Fetch initial house options
    fetch(`${apiBase}/projects/proj-mumbai-real-1100/house-options`)
      .then((res) => res.json())
      .then((opts: HouseOption[]) => {
        if (opts && opts.length > 0) {
          setHouseOptions(opts);
          setSelectedOptionId(opts[0].optionId);
        }
      })
      .catch((err) => console.warn('Could not load house options from API', err));
  }, []);

  // 2. Debounced Auto-Save Mechanism (600ms)
  useEffect(() => {
    if (coordinates.length < 3) return;

    setIsSaving(true);
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      const projId = project?.id || 'proj-mumbai-real-1100';
      fetch(`${apiBase}/projects/${projId}/geometries`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: project?.parcel?.version || 1,
          coordinates,
          existingRoadWidthM: existingRoadWidth,
          proposedRoadWidthM: proposedRoadWidth,
          tenureType: 'PRIVATE_FREEHOLD',
          cadastralSurveyNumber: project?.parcel?.cadastralNumber || 'CTS-1842-BANDRA'
        })
      })
        .then((res) => res.json())
        .then(() => setIsSaving(false))
        .catch(() => setIsSaving(false));
    }, 600);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [coordinates, existingRoadWidth, proposedRoadWidth, project?.id, project?.parcel?.version]);

  // 3. Trigger Feasibility DAG Run & Regenerate House Options
  const handleRunFeasibility = useCallback(async () => {
    if (coordinates.length < 3) {
      alert('Please draw at least 3 vertices to form a closed parcel polygon.');
      return;
    }

    setIsCalculating(true);
    const projId = project?.id || 'proj-mumbai-real-1100';

    try {
      const res = await fetch(`${apiBase}/projects/${projId}/calculate-feasibility`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Feasibility run failed');
      const data: FeasibilityResult = await res.json();
      setFeasibility(data);

      // Refresh house options
      const optRes = await fetch(`${apiBase}/projects/${projId}/house-options`);
      if (optRes.ok) {
        const opts = await optRes.json();
        setHouseOptions(opts);
      }
    } catch (err) {
      console.warn('API call error', err);
    } finally {
      setIsCalculating(false);
    }
  }, [coordinates, project?.id]);

  // 4. Load Golden Benchmark
  const handleLoadGoldenDataset = useCallback(async () => {
    setIsCalculating(true);
    try {
      const res = await fetch(`${apiBase}/projects/load-golden-dataset`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setProject(data.project);
        setCoordinates(data.project.parcel.coordinates);
        setExistingRoadWidth(data.project.parcel.existingRoadWidthM);
        setProposedRoadWidth(data.project.parcel.proposedRoadWidthM);
        setFeasibility(data.feasibility);

        // Fetch refreshed house options
        const optRes = await fetch(`${apiBase}/projects/${data.project.id}/house-options`);
        if (optRes.ok) {
          const opts = await optRes.json();
          setHouseOptions(opts);
          if (opts.length > 0) setSelectedOptionId(opts[0].optionId);
        }
        setIsCalculating(false);
        return;
      }
    } catch (err) {
      console.warn('Golden dataset load fallback', err);
    }
    setIsCalculating(false);
  }, []);

  // 5. Handle Quality Tier Update in Cost View
  const handleUpdateTier = async (tier: string) => {
    const projId = project?.id || 'proj-mumbai-real-1100';
    try {
      const res = await fetch(`${apiBase}/projects/${projId}/house-options?quality_tier=${tier}`);
      if (res.ok) {
        const opts = await res.json();
        setHouseOptions(opts);
      }
    } catch (err) {
      console.warn('Failed to update tier', err);
    }
  };

  // 6. Handle Build Confirmation & Immutable Lock
  const handleConfirmBuild = async (qualityTier: string, acknowledgements: string[]) => {
    const targetOption = buildModalOption || houseOptions.find(o => o.optionId === selectedOptionId);
    if (!targetOption) return;

    setIsLockingBuild(true);
    try {
      const res = await fetch(`${apiBase}/design-versions/${targetOption.designVersionId}/build-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          designVersionId: targetOption.designVersionId,
          optionId: targetOption.optionId,
          requestedQualityTier: qualityTier,
          customerAcknowledgements: acknowledgements
        })
      });

      if (!res.ok) throw new Error('Failed to create build request');
      const data = await res.json();

      setActiveReleaseId(data.releaseId);
      setHandoffPackage(data.package);
      setBuildModalOption(null);
      if (viewMode === 'TECHNICAL') {
        setActiveStep('ENGINEER');
      }
    } catch (err) {
      alert(`Error locking build: ${err}`);
    } finally {
      setIsLockingBuild(false);
    }
  };

  // 6b. Generate Design Options from Customer Requirements
  const handleGenerateDesignOptions = async (reqs: CustomerDesignRequirements): Promise<boolean> => {
    setIsGeneratingDesign(true);
    setCustomerRequirements(reqs);
    const projId = project?.id || 'proj-mumbai-real-1100';

    try {
      // Call M2 generation pipeline
      const genRes = await fetch(`${apiBase}/sites/${projId}/design-options/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bedrooms: reqs.bedrooms,
          bathrooms: reqs.bathrooms,
          floors: reqs.floors,
          parkingRequired: reqs.parkingCars > 0,
          preferredStyle: reqs.preferredStyle,
          budgetInr: reqs.budgetInr,
          qualityTier: 'STANDARD'
        })
      });

      if (genRes.ok) {
        const genData = await genRes.json();
        const opts: HouseOption[] = genData.options || [];
        if (opts.length > 0) {
          setHouseOptions(opts);
          setSelectedOptionId(opts[0].optionId);
          setDesignPhase('OPTIONS');
          setIsGeneratingDesign(false);
          return true;
        }
      }

      // Fallback to project house-options
      const optRes = await fetch(`${apiBase}/projects/${projId}/house-options`);
      if (optRes.ok) {
        const opts: HouseOption[] = await optRes.json();
        if (opts.length > 0) {
          setHouseOptions(opts);
          setSelectedOptionId(opts[0].optionId);
          setDesignPhase('OPTIONS');
          setIsGeneratingDesign(false);
          return true;
        }
      }

      if (houseOptions.length > 0) {
        setDesignPhase('OPTIONS');
        setIsGeneratingDesign(false);
        return true;
      }

      setIsGeneratingDesign(false);
      return false;
    } catch (err) {
      console.warn('Design generation API error', err);
      if (houseOptions.length > 0) {
        setDesignPhase('OPTIONS');
        setIsGeneratingDesign(false);
        return true;
      }
      setIsGeneratingDesign(false);
      return false;
    }
  };


  const selectedOption = houseOptions.find((o) => o.optionId === selectedOptionId) || houseOptions[0];

  // 5. Handle Manual Site Geometry Save with Provenance (Section 8 & 26)
  const handleSaveSiteGeometry = async (metadata: SiteLocationMetadata) => {
    setIsSaving(true);
    const projId = project?.id || 'proj-mumbai-real-1100';
    try {
      const res = await fetch(`${apiBase}/projects/${projId}/geometries`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          version: project?.parcel?.version || 1,
          coordinates,
          existingRoadWidthM: existingRoadWidth,
          proposedRoadWidthM: proposedRoadWidth,
          tenureType: project?.parcel?.tenureType || 'PRIVATE_FREEHOLD',
          cadastralSurveyNumber: project?.parcel?.cadastralNumber || 'CTS-1842-BANDRA',
          geometryVersion: metadata.geometryVersion
        })
      });
      if (res.ok) {
        const data = await res.json();
        setProject((prev) => {
          if (!prev) return null;
          return {
            ...prev,
            parcel: prev.parcel
              ? {
                  ...prev.parcel,
                  coordinates,
                  version: data.version
                }
              : {
                  coordinates,
                  cadastralNumber: 'CTS-1842-BANDRA',
                  tenureType: 'PRIVATE_FREEHOLD',
                  existingRoadWidthM: existingRoadWidth,
                  proposedRoadWidthM: proposedRoadWidth,
                  version: data.version
                }
          };
        });
      }
    } catch (err) {
      console.warn('Save geometry failed', err);
    } finally {
      setIsSaving(false);
    }
  };

  // 6. Handle Mapbox Location Selection (Section 6)
  const handleSelectSiteLocation = (site: SiteLocationMetadata) => {
    setProject((prev) => ({
      id: prev?.id || 'proj-mumbai-real-1100',
      name: site.address.split(',')[0] || 'Selected Project Site',
      description: `Site location reference: ${site.city}, ${site.state}`,
      jurisdiction: 'MUMBAI_DCPR_2034',
      status: prev?.status || 'DRAFT',
      createdAt: prev?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      parcel: {
        coordinates:
          prev?.parcel?.coordinates && prev.parcel.coordinates.length > 0
            ? prev.parcel.coordinates
            : [site.coordinates],
        cadastralNumber: prev?.parcel?.cadastralNumber || 'CTS-SITE-REF',
        tenureType: 'PRIVATE_FREEHOLD',
        existingRoadWidthM: existingRoadWidth,
        proposedRoadWidthM: proposedRoadWidth,
        version: (prev?.parcel?.version || 1) + 1
      },
      latestFeasibility: feasibility,
      activeRelease:
        prev?.activeRelease ||
        (activeReleaseId && handoffPackage
          ? {
              releaseId: activeReleaseId,
              fingerprint: handoffPackage.releaseFingerprint,
              lifecycleState: handoffPackage.lifecycleState,
              handoffPackage
            }
          : null)
    }));
  };

  const handleConfirmLandPlot = (landData: {
    location: string;
    city: string;
    state: string;
    country: string;
    declaredAreaSqft: number;
    unit: 'sqft' | 'sqm';
    shape: 'regular' | 'irregular' | 'unknown';
    roadWidthFt: number;
    roadFacingSide: string;
    coordinates?: [number, number][];
  }) => {
    if (landData.coordinates && landData.coordinates.length >= 3) {
      setCoordinates(landData.coordinates);
    }
    const rwm = Math.round((landData.roadWidthFt * 0.3048) * 10) / 10;
    setExistingRoadWidth(rwm);
    setProposedRoadWidth(Math.max(rwm * 1.5, 12.0));

    setProject((prev) => ({
      id: prev?.id || 'proj-mumbai-real-1100',
      name: landData.location,
      description: `${landData.city}, ${landData.state}`,
      jurisdiction: 'MUMBAI_DCPR_2034',
      status: 'DRAFT',
      createdAt: prev?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      parcel: {
        coordinates: landData.coordinates || coordinates,
        cadastralNumber: prev?.parcel?.cadastralNumber || 'CTS-1842-BANDRA',
        tenureType: 'PRIVATE_FREEHOLD',
        existingRoadWidthM: rwm,
        proposedRoadWidthM: Math.max(rwm * 1.5, 12.0),
        version: (prev?.parcel?.version || 1) + 1
      },
      latestFeasibility: feasibility,
      activeRelease: prev?.activeRelease || null
    }));

    handleRunFeasibility();
    setActiveStep('FEASIBILITY');
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-[#07090e] overflow-hidden select-none">
      {/* Top Application Bar with 6-stage workflow tabs */}
      <Navbar
        project={project}
        isSaving={isSaving}
        isCalculating={isCalculating}
        activeStep={activeStep}
        onChangeStep={setActiveStep}
        hasActiveRelease={!!activeReleaseId}
        onRunFeasibility={handleRunFeasibility}
        onLoadGoldenDataset={handleLoadGoldenDataset}
        viewMode={viewMode}
        onToggleViewMode={setViewMode}
      />

      {/* Main Workspace Body Organized by Workflow Step */}
      <div
        className="relative flex-1 w-full h-[calc(100vh-56px)] flex overflow-hidden"
        style={{ width: '100%', height: 'calc(100vh - 56px)', minHeight: 0 }}
      >
        {/* STEP 1: LAND (Simple Customer Intake by Default; Technical CAD Map in Technical Mode) */}
        {activeStep === 'SITE' && (
          <main
            className="relative flex-1 w-full h-full flex flex-col"
            style={{ width: '100%', height: '100%', minHeight: 0 }}
          >
            {viewMode === 'CUSTOMER' ? (
              <LandIntakeView
                initialLocation={project?.name || 'Bandra West, Mumbai'}
                initialCoordinates={coordinates}
                onConfirmPlot={handleConfirmLandPlot}
                onOpenTechnicalMap={() => setViewMode('TECHNICAL')}
              />
            ) : (
              <>
                <PlanwiseMap
                  coordinates={coordinates}
                  buildableCoordinates={feasibility?.buildableCoordinates}
                  selectedOption={selectedOption}
                  feasibility={feasibility}
                  existingRoadWidth={existingRoadWidth}
                  proposedRoadWidth={proposedRoadWidth}
                  onChangeRoadWidths={(ext, prop) => {
                    setExistingRoadWidth(ext);
                    setProposedRoadWidth(prop);
                  }}
                  onAddCoordinate={(coord) => setCoordinates((prev) => [...prev, coord])}
                  onUpdateCoordinates={setCoordinates}
                  onClearCoordinates={() => {
                    setCoordinates([]);
                    setFeasibility(null);
                  }}
                  onSaveSiteGeometry={handleSaveSiteGeometry}
                  onSelectSiteLocation={handleSelectSiteLocation}
                  onOpenFeasibility={() => setActiveStep('FEASIBILITY')}
                  onOpenDesign={() => setActiveStep('DESIGN')}
                  isSavingGeometry={isSaving}
                  isReleaseLocked={Boolean(activeReleaseId)}
                  releaseId={activeReleaseId || undefined}
                />

                {/* Top-Right Floating Site Evidence & Truth Panel (§1, §2, §13) */}
                <div className="absolute top-4 right-4 z-20 flex flex-col items-end gap-2">
                  {!isEvidencePanelOpen && (
                    <button
                      onClick={() => setIsEvidencePanelOpen(true)}
                      className="px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-white/10 text-white font-display font-semibold text-xs shadow-xl flex items-center gap-1.5 transition-all"
                    >
                      <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Site Evidence &amp; Truth</span>
                    </button>
                  )}
                  {isEvidencePanelOpen && (
                    <SiteEvidencePanel
                      siteId={project?.id || 'proj-mumbai-real-1100'}
                      onClose={() => setIsEvidencePanelOpen(false)}
                    />
                  )}
                </div>

                {/* Bottom Step Guide Bar */}
                <div className="absolute bottom-4 right-4 z-20 flex items-center gap-2">
                  <button
                    onClick={() => setActiveStep('FEASIBILITY')}
                    className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-bold text-xs shadow-lg shadow-blue-500/30 flex items-center gap-1.5 transition-all"
                  >
                    <span>Proceed to Step 2: FEASIBILITY</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </>
            )}
          </main>
        )}

        {/* STEP 2: FEASIBILITY */}
        {activeStep === 'FEASIBILITY' && (
          viewMode === 'CUSTOMER' ? (
            <FeasibilitySummaryView
              feasibility={feasibility}
              project={project}
              onProceedToDesign={() => setActiveStep('DESIGN')}
              onBackToLand={() => setActiveStep('SITE')}
              onOpenTechnicalView={() => setViewMode('TECHNICAL')}
            />
          ) : (
            <main
              className="relative flex-1 w-full h-full flex"
              style={{ width: '100%', height: '100%', minHeight: 0 }}
            >
              {/* Left: Map Preview */}
              <div
                className="flex-1 h-full relative"
                style={{ height: '100%', minHeight: 0 }}
              >
                <PlanwiseMap
                  coordinates={coordinates}
                  buildableCoordinates={feasibility?.buildableCoordinates}
                  selectedOption={selectedOption}
                  feasibility={feasibility}
                  existingRoadWidth={existingRoadWidth}
                  proposedRoadWidth={proposedRoadWidth}
                  onChangeRoadWidths={(ext, prop) => {
                    setExistingRoadWidth(ext);
                    setProposedRoadWidth(prop);
                  }}
                  onAddCoordinate={(coord) => setCoordinates((prev) => [...prev, coord])}
                  onUpdateCoordinates={setCoordinates}
                  onClearCoordinates={() => {
                    setCoordinates([]);
                    setFeasibility(null);
                  }}
                  onSaveSiteGeometry={handleSaveSiteGeometry}
                  onSelectSiteLocation={handleSelectSiteLocation}
                  onOpenFeasibility={() => setActiveStep('FEASIBILITY')}
                  onOpenDesign={() => setActiveStep('DESIGN')}
                  isSavingGeometry={isSaving}
                  isReleaseLocked={Boolean(activeReleaseId)}
                  releaseId={activeReleaseId || undefined}
                />
              </div>

              {/* Right: Feasibility Intelligence HUD */}
              <div className="h-full p-4 pl-0">
                <FeasibilityHUD
                  feasibility={feasibility}
                  cadastralNumber={project?.parcel?.cadastralNumber || 'CTS-1842-BANDRA'}
                />
              </div>

              {/* Bottom Proceed Button */}
              <div className="absolute bottom-4 left-4 z-20">
                <button
                  onClick={() => setActiveStep('DESIGN')}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-bold text-xs shadow-lg shadow-blue-500/30 flex items-center gap-1.5 transition-all"
                >
                  <span>Proceed to Step 3: DESIGN</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </main>
          )
        )}

        {/* STEP 3: DESIGN */}
        {activeStep === 'DESIGN' && (
          viewMode === 'CUSTOMER' ? (
            designPhase === 'INTAKE' ? (
              <DesignIntakeView
                initialRequirements={customerRequirements || undefined}
                isGenerating={isGeneratingDesign}
                onGenerateOptions={handleGenerateDesignOptions}
                onBackToFeasibility={() => setActiveStep('FEASIBILITY')}
              />
            ) : (
              <DesignOptionsView
                options={houseOptions}
                selectedOptionId={selectedOptionId}
                onSelectOption={setSelectedOptionId}
                onChooseOption={(opt) => {
                  setSelectedOptionId(opt.optionId);
                  setActiveStep('COST');
                }}
                onChangeRequirements={() => setDesignPhase('INTAKE')}
                onOpenTechnicalView={() => setViewMode('TECHNICAL')}
              />
            )
          ) : (
            <main className="relative flex-1 w-full h-full flex p-4 gap-4 overflow-hidden">
              {/* Left 320px: Compact House Options Sidebar */}
              <HouseOptionsCarousel
                options={houseOptions}
                selectedOptionId={selectedOptionId}
                onSelectOption={setSelectedOptionId}
                onOpenBOQ={(opt) => setSelectedBOQOption(opt)}
                onOpenBuildModal={(opt) => setBuildModalOption(opt)}
              />

              {/* Center: The Floor Plan Canvas Hero (Flex-1) */}
              <div className="flex-1 h-full min-w-0">
                {selectedOption ? (
                  <FloorPlanViewer 
                    layout={selectedOption.layout} 
                    buildingModel={selectedOption.buildingModel}
                    designVersionId={selectedOption.designVersionId}
                  />
                ) : (
                  <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
                    Generating CP-SAT Pareto options...
                  </div>
                )}
              </div>
            </main>
          )
        )}

        {/* STEP 4: COST */}
        {activeStep === 'COST' && (
          selectedOption ? (
            viewMode === 'CUSTOMER' ? (
              <CostSummaryView
                selectedOption={selectedOption}
                onUpdateTier={handleUpdateTier}
                onProceedToBuild={() => setActiveStep('BUILD')}
                onBackToDesign={() => setActiveStep('DESIGN')}
                onOpenTechnicalView={() => setViewMode('TECHNICAL')}
              />
            ) : (
              <main className="relative flex-1 w-full h-full">
                <CostExperienceView
                  selectedOption={selectedOption}
                  onUpdateTier={handleUpdateTier}
                  onRequestBuild={(opt) => {
                    setBuildModalOption(opt);
                    setActiveStep('BUILD');
                  }}
                />
              </main>
            )
          ) : (
            <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
              Select a design option to view its estimated construction cost.
            </div>
          )
        )}

        {/* STEP 5: BUILD */}
        {activeStep === 'BUILD' && (
          selectedOption ? (
            viewMode === 'CUSTOMER' ? (
              <BuildReviewView
                project={project}
                selectedOption={selectedOption}
                activeRelease={handoffPackage}
                activeReleaseId={activeReleaseId}
                onRequestBuildReview={async (tier, acks) => {
                  await handleConfirmBuild(tier, acks);
                }}
                onGoToEngineerDashboard={() => setActiveStep('ENGINEER')}
                onBackToCost={() => setActiveStep('COST')}
                onRecalculateCost={() => setActiveStep('COST')}
                onOpenTechnicalView={() => setViewMode('TECHNICAL')}
                isSubmitting={isLockingBuild}
              />
            ) : (
              <main className="relative flex-1 w-full h-full">
                <BuildReleaseView
                  selectedOption={selectedOption}
                  activeRelease={handoffPackage}
                  activeReleaseId={activeReleaseId}
                  onLockBuild={handleConfirmBuild}
                  onGoToEngineerDashboard={() => setActiveStep('ENGINEER')}
                  isLocking={isLockingBuild}
                />
              </main>
            )
          ) : (
            <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
              Select a design option to prepare for project review.
            </div>
          )
        )}

        {/* STEP 6: ENGINEER (Professional Review & Verification Layer) */}
        {activeStep === 'ENGINEER' && (
          selectedOption ? (
            <EngineerReviewView
              project={project}
              selectedOption={selectedOption}
              activeRelease={handoffPackage}
              activeReleaseId={activeReleaseId || 'REL-SAMPLE-2026'}
              onBackToBuild={() => setActiveStep('BUILD')}
              onBackToDesign={() => setActiveStep('DESIGN')}
            />
          ) : (
            <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
              Select a design option to open professional review.
            </div>
          )
        )}
      </div>

      {/* Global Modals (Traceable BOQ Modal & Build Request Modal) */}
      <BOQTableModal
        option={selectedBOQOption}
        onClose={() => setSelectedBOQOption(null)}
      />

      <BuildLockModal
        option={buildModalOption}
        onClose={() => setBuildModalOption(null)}
        onConfirmBuild={handleConfirmBuild}
        isLocking={isLockingBuild}
      />
    </div>
  );
};
export default App;
