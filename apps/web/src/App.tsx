import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { CADToolbar } from './components/CADToolbar';
import { MapCanvas } from './components/MapCanvas';
import { FeasibilityHUD } from './components/FeasibilityHUD';
import { HouseOptionsCarousel } from './components/HouseOptionsCarousel';
import { FloorPlanViewer } from './components/FloorPlanViewer';
import { BOQTableModal } from './components/BOQTableModal';
import { BuildLockModal } from './components/BuildLockModal';
import { EngineerDashboard } from './components/EngineerDashboard';
import { 
  ToolMode, 
  AppViewMode, 
  ProjectData, 
  FeasibilityResult, 
  HouseOption, 
  HandoffPackage 
} from './types';

export const App: React.FC = () => {
  const [project, setProject] = useState<ProjectData | null>(null);
  const [viewMode, setViewMode] = useState<AppViewMode>('CUSTOMER_STUDIO');
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

  // 5. Handle Build Confirmation & Immutable Lock
  const handleConfirmBuild = async (qualityTier: string, acknowledgements: string[]) => {
    if (!buildModalOption) return;

    setIsLockingBuild(true);
    try {
      const res = await fetch(`${apiBase}/design-versions/${buildModalOption.designVersionId}/build-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          designVersionId: buildModalOption.designVersionId,
          optionId: buildModalOption.optionId,
          requestedQualityTier: qualityTier,
          customerAcknowledgements: acknowledgements
        })
      });

      if (!res.ok) throw new Error('Failed to create build request');
      const data = await res.json();

      setActiveReleaseId(data.releaseId);
      setHandoffPackage(data.package);
      setBuildModalOption(null);
      // Auto-transition to Engineer Dashboard to inspect the newly locked release!
      setViewMode('ENGINEER_DASHBOARD');
    } catch (err) {
      alert(`Error locking build: ${err}`);
    } finally {
      setIsLockingBuild(false);
    }
  };

  // 6. Handle Gate Sign-Off in Engineer Dashboard
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
    <div className="w-screen h-screen flex flex-col bg-[#080c14] overflow-hidden select-none">
      {/* Top Application Bar */}
      <Navbar
        project={project}
        isSaving={isSaving}
        isCalculating={isCalculating}
        viewMode={viewMode}
        onChangeViewMode={setViewMode}
        hasActiveRelease={!!activeReleaseId}
        onRunFeasibility={handleRunFeasibility}
        onLoadGoldenDataset={handleLoadGoldenDataset}
      />

      {/* Main Workspace Body */}
      {viewMode === 'CUSTOMER_STUDIO' ? (
        <main className="relative flex-1 w-full h-[calc(100vh-56px)] flex flex-col">
          {/* Top Half: CAD Toolbar + MapCanvas + Feasibility HUD */}
          <div className="relative w-full h-[54%] border-b border-white/10">
            {/* CAD Toolbar */}
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

            {/* Map Canvas */}
            <MapCanvas
              toolMode={toolMode}
              coordinates={coordinates}
              buildableCoordinates={feasibility?.buildableCoordinates}
              onAddCoordinate={(coord) => setCoordinates((prev) => [...prev, coord])}
              onUpdateCoordinates={setCoordinates}
            />

            {/* Feasibility HUD */}
            <FeasibilityHUD
              feasibility={feasibility}
              cadastralNumber={project?.parcel?.cadastralNumber || 'CTS-1842-BANDRA'}
            />
          </div>

          {/* Bottom Half: House Options & Interactive Floor Plan Studio */}
          <div className="w-full h-[46%] bg-[#080c14] p-4 flex gap-4 overflow-hidden">
            {/* Left 45%: Generated House Options Carousel */}
            <div className="w-[45%] h-full overflow-y-auto pr-1">
              <HouseOptionsCarousel
                options={houseOptions}
                selectedOptionId={selectedOptionId}
                onSelectOption={setSelectedOptionId}
                onOpenBOQ={(opt) => setSelectedBOQOption(opt)}
                onOpenBuildModal={(opt) => setBuildModalOption(opt)}
              />
            </div>

            {/* Right 55%: Interactive 2D Floor Plan Viewer */}
            <div className="w-[55%] h-full">
              {selectedOption ? (
                <FloorPlanViewer layout={selectedOption.layout} />
              ) : (
                <div className="h-full glass-panel flex items-center justify-center text-slate-500 text-xs">
                  Awaiting House Option Generation
                </div>
              )}
            </div>
          </div>
        </main>
      ) : (
        /* Licensed Engineer & Contractor Verification Dashboard */
        <main className="relative flex-1 w-full h-[calc(100vh-56px)]">
          {handoffPackage ? (
            <EngineerDashboard
              handoffPackage={handoffPackage}
              releaseId={activeReleaseId}
              onBackToStudio={() => setViewMode('CUSTOMER_STUDIO')}
              onApproveGate={handleApproveGate}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
              <h3 className="font-display font-bold text-base text-white">No Frozen Release Selected</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Select an architectural house option in the Customer Studio and click <strong className="text-emerald-400">REQUEST BUILD</strong> to generate an immutable release and review it here.
              </p>
              <button
                onClick={() => setViewMode('CUSTOMER_STUDIO')}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
              >
                Go to Customer Studio
              </button>
            </div>
          )}
        </main>
      )}

      {/* Traceable BOQ Takeoff Modal */}
      <BOQTableModal
        option={selectedBOQOption}
        onClose={() => setSelectedBOQOption(null)}
      />

      {/* Build Request & Immutable Lock Modal */}
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
