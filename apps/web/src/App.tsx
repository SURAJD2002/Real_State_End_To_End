import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { CADToolbar } from './components/CADToolbar';
import { MapCanvas } from './components/MapCanvas';
import { FeasibilityHUD } from './components/FeasibilityHUD';
import { HouseOptionsCarousel } from './components/HouseOptionsCarousel';
import { FloorPlanViewer } from './components/FloorPlanViewer';
import { CostExperienceView } from './components/CostExperienceView';
import { BuildReleaseView } from './components/BuildReleaseView';
import { BOQTableModal } from './components/BOQTableModal';
import { BuildLockModal } from './components/BuildLockModal';
import { EngineerDashboard } from './components/EngineerDashboard';
import { 
  ToolMode, 
  WorkflowStep, 
  ProjectData, 
  FeasibilityResult, 
  HouseOption, 
  HandoffPackage 
} from './types';
import { ArrowRight, ShieldCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [project, setProject] = useState<ProjectData | null>(null);
  const [activeStep, setActiveStep] = useState<WorkflowStep>('DESIGN');
  const [toolMode, setToolMode] = useState<ToolMode>('SELECT');
  const [coordinates, setCoordinates] = useState<[number, number][]>([]);
  const [existingRoadWidth, setExistingRoadWidth] = useState<number>(12.0);
  const [proposedRoadWidth, setProposedRoadWidth] = useState<number>(18.0);
  const [feasibility, setFeasibility] = useState<FeasibilityResult | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);

  // House Generation & Delivery State
  const [houseOptions, setHouseOptions] = useState<HouseOption[]>([]);
  const [selectedOptionId, setSelectedOptionId] = useState<string>('opt-compact_2bhk');
  const [selectedBOQOption, setSelectedBOQOption] = useState<HouseOption | null>(null);
  const [buildModalOption, setBuildModalOption] = useState<HouseOption | null>(null);
  const [isLockingBuild, setIsLockingBuild] = useState<boolean>(false);
  const [activeReleaseId, setActiveReleaseId] = useState<string>('');
  const [handoffPackage, setHandoffPackage] = useState<HandoffPackage | null>(null);

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
            setExistingRoadWidth(p.parcel.existingRoadWidthM || 12.0);
            setProposedRoadWidth(p.parcel.proposedRoadWidthM || 18.0);
          }
          if (p.latestFeasibility) {
            setFeasibility(p.latestFeasibility);
          }
        }
      })
      .catch((err) => {
        console.warn('API Gateway offline. Using fallback initial coordinates.', err);
        const defaultCoords: [number, number][] = [
          [72.86850, 19.11280],
          [72.86950, 19.11400],
          [72.87100, 19.11330],
          [72.87000, 19.11210],
          [72.86850, 19.11280]
        ];
        setCoordinates(defaultCoords);
      });

    // Fetch initial house options
    fetch(`${apiBase}/projects/proj-mumbai-default-01/house-options`)
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
      const projId = project?.id || 'proj-mumbai-default-01';
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
    const projId = project?.id || 'proj-mumbai-default-01';

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
    const projId = project?.id || 'proj-mumbai-default-01';
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
      // Auto-transition to Step 6: ENGINEER
      setActiveStep('ENGINEER');
    } catch (err) {
      alert(`Error locking build: ${err}`);
    } finally {
      setIsLockingBuild(false);
    }
  };

  // 7. Handle Gate Sign-Off in Engineer Dashboard
  const handleApproveGate = async (gateId: string, decision: string, notes: string) => {
    if (!activeReleaseId) return;

    try {
      const res = await fetch(`${apiBase}/releases/${activeReleaseId}/approvals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gate: gateId,
          decision: decision,
          professionalId: 'ENG-MH-48201',
          notes: notes
        })
      });
      if (res.ok) {
        const data = await res.json();
        setHandoffPackage(data.handoffPackage);
      }
    } catch (err) {
      console.error('Error updating gate', err);
    }
  };

  const selectedOption = houseOptions.find((o) => o.optionId === selectedOptionId) || houseOptions[0];

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
      />

      {/* Main Workspace Body Organized by Workflow Step */}
      <div className="relative flex-1 w-full h-[calc(100vh-56px)] flex overflow-hidden">
        {/* STEP 1: SITE (Full CAD Map Canvas with Road Controls) */}
        {activeStep === 'SITE' && (
          <main className="relative flex-1 w-full h-full flex flex-col">
            <CADToolbar
              toolMode={toolMode}
              onSelectTool={setToolMode}
              existingRoadWidth={existingRoadWidth}
              proposedRoadWidth={proposedRoadWidth}
              onChangeRoadWidths={(ext, prop) => {
                setExistingRoadWidth(ext);
                setProposedRoadWidth(prop);
              }}
              onClear={() => {
                setCoordinates([]);
                setFeasibility(null);
              }}
            />

            <MapCanvas
              toolMode={toolMode}
              coordinates={coordinates}
              buildableCoordinates={feasibility?.buildableCoordinates}
              onAddCoordinate={(coord) => setCoordinates((prev) => [...prev, coord])}
              onUpdateCoordinates={setCoordinates}
            />

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
          </main>
        )}

        {/* STEP 2: FEASIBILITY (Map with Buildable Envelope + Statutory Feasibility HUD) */}
        {activeStep === 'FEASIBILITY' && (
          <main className="relative flex-1 w-full h-full flex">
            {/* Left: Map Preview */}
            <div className="flex-1 h-full relative">
              <CADToolbar
                toolMode={toolMode}
                onSelectTool={setToolMode}
                existingRoadWidth={existingRoadWidth}
                proposedRoadWidth={proposedRoadWidth}
                onChangeRoadWidths={(ext, prop) => {
                  setExistingRoadWidth(ext);
                  setProposedRoadWidth(prop);
                }}
                onClear={() => {
                  setCoordinates([]);
                  setFeasibility(null);
                }}
              />
              <MapCanvas
                toolMode={toolMode}
                coordinates={coordinates}
                buildableCoordinates={feasibility?.buildableCoordinates}
                onAddCoordinate={(coord) => setCoordinates((prev) => [...prev, coord])}
                onUpdateCoordinates={setCoordinates}
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
        )}

        {/* STEP 3: DESIGN (The Architectural Floor Plan Canvas is the Hero!) */}
        {activeStep === 'DESIGN' && (
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
                <FloorPlanViewer layout={selectedOption.layout} />
              ) : (
                <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
                  Generating CP-SAT Pareto options...
                </div>
              )}
            </div>
          </main>
        )}

        {/* STEP 4: COST (Model-Linked Traceable BOQ & QTO Experience) */}
        {activeStep === 'COST' && (
          <main className="relative flex-1 w-full h-full">
            {selectedOption ? (
              <CostExperienceView
                selectedOption={selectedOption}
                onUpdateTier={handleUpdateTier}
                onRequestBuild={(opt) => {
                  setBuildModalOption(opt);
                  setActiveStep('BUILD');
                }}
              />
            ) : (
              <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
                Select a design option to view its itemized Bill of Quantities.
              </div>
            )}
          </main>
        )}

        {/* STEP 5: BUILD (Design Release & Immutable Lock Workflow) */}
        {activeStep === 'BUILD' && (
          <main className="relative flex-1 w-full h-full">
            {selectedOption ? (
              <BuildReleaseView
                selectedOption={selectedOption}
                activeRelease={handoffPackage}
                activeReleaseId={activeReleaseId}
                onLockBuild={handleConfirmBuild}
                onGoToEngineerDashboard={() => setActiveStep('ENGINEER')}
                isLocking={isLockingBuild}
              />
            ) : (
              <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
                Select a design option to prepare for professional build release.
              </div>
            )}
          </main>
        )}

        {/* STEP 6: ENGINEER (Licensed Engineer & Contractor Dashboard) */}
        {activeStep === 'ENGINEER' && (
          <main className="relative flex-1 w-full h-full">
            {handoffPackage ? (
              <EngineerDashboard
                handoffPackage={handoffPackage}
                releaseId={activeReleaseId || 'REL-SAMPLE-2026'}
                onBackToStudio={() => setActiveStep('DESIGN')}
                onApproveGate={handleApproveGate}
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
                <ShieldCheck className="w-12 h-12 text-slate-600" />
                <h3 className="font-display font-bold text-base text-white">No Frozen Release in Review</h3>
                <p className="text-xs text-slate-400 max-w-md leading-normal">
                  In Step 5: BUILD, click <strong className="text-emerald-400">REQUEST BUILD</strong> to generate an immutable release package. It will automatically lock the design and populate the verification gates here.
                </p>
                <button
                  onClick={() => setActiveStep('BUILD')}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
                >
                  Go to Step 5: BUILD
                </button>
              </div>
            )}
          </main>
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
