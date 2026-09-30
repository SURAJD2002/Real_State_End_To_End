import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { CADToolbar } from './components/CADToolbar';
import { MapCanvas } from './components/MapCanvas';
import { FeasibilityHUD } from './components/FeasibilityHUD';
import { ToolMode, ProjectData, FeasibilityResult } from './types';

export const App: React.FC = () => {
  const [project, setProject] = useState<ProjectData | null>(null);
  const [toolMode, setToolMode] = useState<ToolMode>('SELECT');
  const [coordinates, setCoordinates] = useState<[number, number][]>([]);
  const [existingRoadWidth, setExistingRoadWidth] = useState<number>(12.0);
  const [proposedRoadWidth, setProposedRoadWidth] = useState<number>(18.0);
  const [feasibility, setFeasibility] = useState<FeasibilityResult | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const apiBase = '/api/v1';

  // 1. Initial Load: Fetch default project
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
        console.warn('API Gateway offline or proxy not connected. Using local benchmark fallback.', err);
        // Local default state
        const defaultCoords: [number, number][] = [
          [72.86850, 19.11280],
          [72.86950, 19.11400],
          [72.87100, 19.11330],
          [72.87000, 19.11210],
          [72.86850, 19.11280]
        ];
        setCoordinates(defaultCoords);
      });
  }, []);

  // 2. Debounced Auto-Save Mechanism
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
        .then(() => {
          setIsSaving(false);
        })
        .catch(() => {
          setIsSaving(false);
        });
    }, 600);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [coordinates, existingRoadWidth, proposedRoadWidth, project?.id, project?.parcel?.version]);

  // 3. Trigger Feasibility DAG Run
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
    } catch (err) {
      console.warn('API call failed, running deterministic local client fallback calculation:', err);
      // Deterministic fallback for standalone offline preview
      const approxArea = 10000;
      const roadDeduction = 800;
      const amenity = 1380;
      const netDev = approxArea - roadDeduction - amenity;
      const fsi = proposedRoadWidth >= 18 ? 2.5 : 2.0;
      const bua = netDev * fsi;
      const gdv = bua * 185000;
      const civilCost = bua * 46000;
      const premiums = bua * 0.25 * 40000;
      const tdc = civilCost + premiums + (gdv * 0.07);

      setFeasibility({
        runId: 'run-offline-fallback',
        projectId: projId,
        timestamp: new Date().toISOString(),
        regulationVersionId: 'MUMBAI_DCPR_2034_V1',
        engineVersion: '1.0.0',
        grossPlotAreaSqm: approxArea,
        roadWideningDeductionSqm: roadDeduction,
        amenityReservationSqm: amenity,
        netDevelopableAreaSqm: netDev,
        baseFSI: 1.0,
        premiumFSI: 0.5,
        tdrFSI: fsi - 1.5,
        totalPermissibleFSI: fsi,
        permissibleBUASqm: bua,
        carpetAreaSqm: bua * 0.7,
        maxBuildingHeightM: 50.0,
        frontSetbackM: 6.0,
        standardParkingStalls: Math.round((bua * 0.7) / 70),
        accessibleParkingStalls: 3,
        financials: {
          currency: 'INR',
          grossDevelopmentValue: gdv,
          civilConstructionCost: civilCost,
          statutoryApprovalPremiums: premiums,
          softCostsAndMarketing: gdv * 0.07,
          financingCost: (civilCost + premiums) * 0.12,
          totalDevelopmentCost: tdc,
          netMarginValue: gdv - tdc,
          netMarginPercent: Number(((gdv - tdc) / gdv * 100).toFixed(2)),
          equityIRRPercent: 24.8
        },
        buildableCoordinates: coordinates
      });
    } finally {
      setIsCalculating(false);
    }
  }, [coordinates, project?.id, proposedRoadWidth]);

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
        setIsCalculating(false);
        return;
      }
    } catch {
      // Fallback
    }

    // Default Golden Mumbai Coordinates
    const goldenCoords: [number, number][] = [
      [72.86850, 19.11280],
      [72.86950, 19.11400],
      [72.87100, 19.11330],
      [72.87000, 19.11210],
      [72.86850, 19.11280]
    ];
    setCoordinates(goldenCoords);
    setExistingRoadWidth(12.0);
    setProposedRoadWidth(18.0);
    setIsCalculating(false);
  }, []);

  const handleAddCoordinate = (coord: [number, number]) => {
    setCoordinates((prev) => [...prev, coord]);
  };

  const handleClear = () => {
    setCoordinates([]);
    setFeasibility(null);
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-[#080c14] overflow-hidden">
      {/* Top Application Bar */}
      <Navbar
        project={project}
        isSaving={isSaving}
        isCalculating={isCalculating}
        onRunFeasibility={handleRunFeasibility}
        onLoadGoldenDataset={handleLoadGoldenDataset}
      />

      {/* Main CAD Map Workspace */}
      <main className="relative flex-1 w-full h-[calc(100vh-56px)]">
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
          onClear={handleClear}
        />

        {/* Map Canvas */}
        <MapCanvas
          toolMode={toolMode}
          coordinates={coordinates}
          buildableCoordinates={feasibility?.buildableCoordinates}
          onAddCoordinate={handleAddCoordinate}
          onUpdateCoordinates={setCoordinates}
        />

        {/* Floating Intelligence HUD */}
        <FeasibilityHUD
          feasibility={feasibility}
          cadastralNumber={project?.parcel?.cadastralNumber || 'CTS-1842-BANDRA'}
        />
      </main>
    </div>
  );
};
export default App;
