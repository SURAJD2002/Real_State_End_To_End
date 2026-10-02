import React from 'react';
import { 
  MousePointer, 
  Pentagon, 
  Edit3, 
  MinusCircle,
  Ruler, 
  RotateCcw, 
  RotateCw,
  Save, 
  Layers, 
  LocateFixed, 
  Trash2,
  Compass,
  Grid,
  HelpCircle,
  Lock,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { MapInteractionMode, CadSnapSettings } from './types';

interface MapToolbarProps {
  interactionMode: MapInteractionMode;
  onChangeMode: (mode: MapInteractionMode) => void;
  snapSettings: CadSnapSettings;
  onUpdateSnapSettings: (settings: Partial<CadSnapSettings>) => void;
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  onClear: () => void;
  onReCenter: () => void;
  onToggleLayers: () => void;
  isLayersOpen: boolean;
  onOpenShortcuts: () => void;
  onSaveGeometry: () => void;
  isSavingGeometry: boolean;
  parcelAreaSqm: number;
  parcelPerimeterM: number;
  verticesCount: number;
  geometryVersion: string;
  isGeometryValid: boolean;
  geometryError: string | null;
  activeSnapDesc?: string | null;
  areaDiffSqm?: number | null;
  selectedVertexIndex?: number | null;
  onDeleteSelectedVertex?: () => void;
  isReleaseLocked?: boolean;
  releaseId?: string | null;
}

export const MapToolbar: React.FC<MapToolbarProps> = ({
  interactionMode,
  onChangeMode,
  snapSettings,
  onUpdateSnapSettings,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  onClear,
  onReCenter,
  onToggleLayers,
  isLayersOpen,
  onOpenShortcuts,
  onSaveGeometry,
  isSavingGeometry,
  parcelAreaSqm,
  parcelPerimeterM,
  verticesCount,
  geometryVersion,
  isGeometryValid,
  geometryError,
  activeSnapDesc,
  areaDiffSqm,
  selectedVertexIndex,
  onDeleteSelectedVertex,
  isReleaseLocked = false,
  releaseId = null
}) => {
  const gridOptions = [0.5, 1.0, 5.0, 10.0];
  const angleOptions = [5, 10, 15, 30, 45, 90];

  const handleCycleGrid = () => {
    if (!snapSettings.isGridSnap) {
      onUpdateSnapSettings({ isGridSnap: true });
      return;
    }
    const currentIdx = gridOptions.indexOf(snapSettings.gridSizeM);
    if (currentIdx === -1 || currentIdx === gridOptions.length - 1) {
      onUpdateSnapSettings({ isGridSnap: false, gridSizeM: gridOptions[0] });
    } else {
      onUpdateSnapSettings({ isGridSnap: true, gridSizeM: gridOptions[currentIdx + 1] });
    }
  };

  const handleCycleAngle = () => {
    if (!snapSettings.isAngleSnap) {
      onUpdateSnapSettings({ isAngleSnap: true });
      return;
    }
    const currentIdx = angleOptions.indexOf(snapSettings.angleStepDeg);
    if (currentIdx === -1 || currentIdx === angleOptions.length - 1) {
      onUpdateSnapSettings({ isAngleSnap: false, angleStepDeg: angleOptions[0] });
    } else {
      onUpdateSnapSettings({ isAngleSnap: true, angleStepDeg: angleOptions[currentIdx + 1] });
    }
  };

  const primaryTools: {
    mode: MapInteractionMode;
    label: string;
    icon: React.ReactNode;
    shortcut: string;
  }[] = [
    { mode: 'SELECT', label: 'Select & Pan (V)', icon: <MousePointer className="w-4 h-4" />, shortcut: 'V' },
    { mode: 'DRAW_PARCEL', label: 'Draw Land Parcel (P)', icon: <Pentagon className="w-4 h-4" />, shortcut: 'P' },
    { mode: 'EDIT_PARCEL', label: 'Edit Vertices & Edges (E)', icon: <Edit3 className="w-4 h-4" />, shortcut: 'E' },
    { mode: 'MEASURE_DISTANCE', label: 'CAD Distance Measurement (M)', icon: <Ruler className="w-4 h-4" />, shortcut: 'M' }
  ];

  return (
    <aside className="absolute left-4 top-20 z-20 flex flex-col gap-2 select-none">
      {/* Primary CAD Toolbar */}
      <div className="glass-panel p-1.5 flex flex-col gap-1 w-12 items-center border border-white/10 shadow-2xl bg-slate-950/95 backdrop-blur-md rounded-2xl">
        {primaryTools.map((t) => {
          const isActive = interactionMode === t.mode;
          return (
            <button
              key={t.mode}
              onClick={() => onChangeMode(t.mode)}
              title={t.label}
              className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              {t.icon}
            </button>
          );
        })}

        <div className="w-6 h-px bg-white/10 my-0.5" />

        {/* Undo Action */}
        <button
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo Geometry Operation (Cmd/Ctrl + Z)"
          className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-all disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Redo Action */}
        <button
          onClick={onRedo}
          disabled={!canRedo}
          title="Redo Geometry Operation (Cmd/Ctrl + Shift + Z)"
          className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-all disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <div className="w-6 h-px bg-white/10 my-0.5" />

        {/* Toggle Layers Panel */}
        <button
          onClick={onToggleLayers}
          title="Toggle Map Layers Panel (L)"
          className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
            isLayersOpen
              ? 'bg-cyan-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          <Layers className="w-4 h-4" />
        </button>

        {/* Re-center Map to Parcel */}
        <button
          onClick={onReCenter}
          title="Zoom to Parcel Extents (Z)"
          className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-cyan-400 hover:bg-white/5 transition-all"
        >
          <LocateFixed className="w-4 h-4" />
        </button>

        {/* Keyboard Shortcuts Helper */}
        <button
          onClick={onOpenShortcuts}
          title="CAD Keyboard Shortcuts (?)"
          className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-all"
        >
          <HelpCircle className="w-4 h-4" />
        </button>

        <div className="w-6 h-px bg-white/10 my-0.5" />

        {/* Clear Geometry */}
        <button
          onClick={onClear}
          title="Clear Parcel Polygon"
          className="w-9 h-9 rounded-xl flex items-center justify-center text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* CAD Precision & Snapping Controls Strip */}
      <div className="glass-panel p-1.5 flex items-center gap-1 border border-white/10 shadow-xl bg-slate-950/95 backdrop-blur-md rounded-xl text-xs font-mono">
        {/* Ortho Mode Toggle (O) */}
        <button
          onClick={() => onUpdateSnapSettings({ isOrtho: !snapSettings.isOrtho })}
          title="Toggle ORTHO Mode (0°, 45°, 90°) [O]"
          className={`px-2 py-1 rounded-lg text-[10px] font-bold tracking-wider flex items-center gap-1 transition-all ${
            snapSettings.isOrtho
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          <Compass className="w-3 h-3" />
          <span>ORTHO</span>
        </button>

        {/* Metric Grid Snap Toggle & Selector (G) */}
        <div className="relative">
          <button
            onClick={handleCycleGrid}
            title="Toggle / Cycle Metric Grid Snapping [G] (0.5m, 1m, 5m, 10m)"
            className={`px-2 py-1 rounded-lg text-[10px] font-bold tracking-wider flex items-center gap-1 transition-all ${
              snapSettings.isGridSnap
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            <Grid className="w-3 h-3" />
            <span>GRID {snapSettings.gridSizeM}m</span>
          </button>
        </div>

        {/* Angle Snap Toggle & Selector */}
        <div className="relative">
          <button
            onClick={handleCycleAngle}
            title="Toggle / Cycle Angle Incremental Snapping (5°, 10°, 15°, 30°, 45°, 90°)"
            className={`px-2 py-1 rounded-lg text-[10px] font-bold tracking-wider flex items-center gap-1 transition-all ${
              snapSettings.isAngleSnap
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            <span>∠ {snapSettings.angleStepDeg}°</span>
          </button>
        </div>
      </div>

      {/* Live Parcel CAD HUD Pill (Section 3, 22, 30) */}
      {verticesCount >= 3 && (
        <div className="glass-panel p-3.5 w-64 border border-white/10 bg-slate-950/95 shadow-2xl rounded-2xl space-y-2.5 text-xs font-mono">
          <div className="flex items-center justify-between border-b border-white/10 pb-1.5 font-sans">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1.5">
              <span>Land Parcel HUD</span>
              {isGeometryValid ? (
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-3 h-3 text-rose-400" />
              )}
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40">
              {geometryVersion}
            </span>
          </div>

          {/* Area & Perimeter Display */}
          <div className="grid grid-cols-2 gap-2 bg-slate-900/60 p-2 rounded-xl border border-white/5">
            <div>
              <span className="text-[9px] text-slate-500 uppercase block">Digitized Area</span>
              <span className="font-bold text-white text-xs">{parcelAreaSqm.toLocaleString()} m²</span>
              {areaDiffSqm !== null && areaDiffSqm !== undefined && areaDiffSqm !== 0 && (
                <span className={`text-[9px] block ${areaDiffSqm > 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {areaDiffSqm > 0 ? `+${areaDiffSqm.toFixed(1)}` : areaDiffSqm.toFixed(1)} m²
                </span>
              )}
              <span className="text-[9px] text-slate-500 block">
                ({Math.round(parcelAreaSqm * 10.7639).toLocaleString()} sqft)
              </span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 uppercase block">Perimeter</span>
              <span className="font-bold text-cyan-300 text-xs">{parcelPerimeterM.toFixed(1)} m</span>
              <span className="text-[9px] text-slate-500 block">{verticesCount} Vertices</span>
            </div>
          </div>

          {/* Active Snap State Indicator (Section 26) */}
          {(activeSnapDesc || snapSettings.isOrtho) && (
            <div className="px-2 py-1 rounded-lg bg-blue-950/60 border border-blue-500/30 text-blue-300 text-[10px] flex items-center justify-between">
              <span>ACTIVE SNAP:</span>
              <span className="font-bold text-cyan-200">
                {activeSnapDesc || (snapSettings.isOrtho ? 'ORTHO (45°/90°)' : 'NORMAL')}
              </span>
            </div>
          )}

          {/* Geometry Validation Warning (Section 15 & 16) */}
          {!isGeometryValid && geometryError && (
            <div className="p-2 rounded-xl bg-rose-950/80 border border-rose-500/50 text-rose-300 text-[10px] leading-relaxed flex items-start gap-1.5 animate-pulse">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
              <span>{geometryError}</span>
            </div>
          )}

          {/* Release Lock Warning (Section 34) */}
          {isReleaseLocked && (
            <div className="p-2 rounded-xl bg-amber-950/80 border border-amber-500/50 text-amber-300 text-[10px] leading-relaxed flex items-start gap-1.5">
              <Lock className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong>SITE GEOMETRY LOCKED</strong>
                <div className="text-[9px] text-amber-300/80">
                  Locked by {releaseId || 'Active Release'}. Direct mutation restricted.
                </div>
              </div>
            </div>
          )}

          {/* Selected Vertex Delete Option */}
          {selectedVertexIndex !== null && selectedVertexIndex !== undefined && onDeleteSelectedVertex && (
            <button
              onClick={onDeleteSelectedVertex}
              className="w-full py-1 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-[10px] font-sans flex items-center justify-center gap-1 transition-colors"
            >
              <MinusCircle className="w-3 h-3 text-rose-400" />
              <span>Delete Selected Vertex V{selectedVertexIndex + 1}</span>
            </button>
          )}

          {/* Save Site Geometry Button */}
          <button
            onClick={onSaveGeometry}
            disabled={isSavingGeometry || !isGeometryValid}
            className="w-full py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-blue-600/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isSavingGeometry ? (
              <>
                <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                <span>Hashing & Persisting...</span>
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5" />
                <span>SAVE SITE GEOMETRY</span>
              </>
            )}
          </button>
        </div>
      )}
    </aside>
  );
};
