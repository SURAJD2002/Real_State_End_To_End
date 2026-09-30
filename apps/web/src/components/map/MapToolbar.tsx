import React from 'react';
import { 
  MousePointer, 
  Pentagon, 
  Edit3, 
  Ruler, 
  RotateCcw, 
  Sliders, 
  Save, 
  Layers, 
  LocateFixed, 
  CheckCircle2,
  Trash2
} from 'lucide-react';
import { MapInteractionMode } from './types';

interface MapToolbarProps {
  interactionMode: MapInteractionMode;
  onChangeMode: (mode: MapInteractionMode) => void;
  existingRoadWidth: number;
  proposedRoadWidth: number;
  onChangeRoadWidths: (existing: number, proposed: number) => void;
  onClear: () => void;
  onReCenter: () => void;
  onToggleLayers: () => void;
  isLayersOpen: boolean;
  onSaveGeometry: () => void;
  isSavingGeometry: boolean;
  parcelAreaSqm: number;
  parcelPerimeterM: number;
  verticesCount: number;
  geometryVersion: string;
}

export const MapToolbar: React.FC<MapToolbarProps> = ({
  interactionMode,
  onChangeMode,
  existingRoadWidth,
  proposedRoadWidth,
  onChangeRoadWidths,
  onClear,
  onReCenter,
  onToggleLayers,
  isLayersOpen,
  onSaveGeometry,
  isSavingGeometry,
  parcelAreaSqm,
  parcelPerimeterM,
  verticesCount,
  geometryVersion
}) => {
  const tools: { mode: MapInteractionMode; label: string; icon: React.ReactNode; shortcut: string }[] = [
    { mode: 'SELECT', label: 'Select & Pan (V)', icon: <MousePointer className="w-4 h-4" />, shortcut: 'V' },
    { mode: 'DRAW_PARCEL', label: 'Draw Land Parcel (P)', icon: <Pentagon className="w-4 h-4" />, shortcut: 'P' },
    { mode: 'EDIT_PARCEL', label: 'Edit Vertices (E)', icon: <Edit3 className="w-4 h-4" />, shortcut: 'E' },
    { mode: 'MEASURE_DISTANCE', label: 'Measure Distance & Area (M)', icon: <Ruler className="w-4 h-4" />, shortcut: 'M' }
  ];

  return (
    <aside className="absolute left-4 top-20 z-20 flex flex-col gap-3 select-none">
      {/* Primary CAD Toolbar */}
      <div className="glass-panel p-1.5 flex flex-col gap-1 w-12 items-center border border-white/10 shadow-2xl bg-slate-950/90 backdrop-blur-md rounded-xl">
        {tools.map((t) => {
          const isActive = interactionMode === t.mode;
          return (
            <button
              key={t.mode}
              onClick={() => onChangeMode(t.mode)}
              title={t.label}
              className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`}
            >
              {t.icon}
            </button>
          );
        })}

        <div className="w-6 h-px bg-white/10 my-1" />

        {/* Toggle Layers Panel */}
        <button
          onClick={onToggleLayers}
          title="Toggle Map Layers Panel (L)"
          className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all ${
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
          className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-400 hover:text-cyan-400 hover:bg-white/5 transition-all"
        >
          <LocateFixed className="w-4 h-4" />
        </button>

        <div className="w-6 h-px bg-white/10 my-1" />

        {/* Clear Geometry */}
        <button
          onClick={onClear}
          title="Clear Parcel Polygon"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Live Parcel CAD HUD Pill (Section 7) */}
      {verticesCount >= 3 && (
        <div className="glass-panel p-3 w-56 border border-white/10 bg-slate-950/90 shadow-2xl rounded-xl space-y-2 text-xs font-mono">
          <div className="flex items-center justify-between border-b border-white/10 pb-1.5 font-sans">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Land Parcel HUD
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40">
              {geometryVersion}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-[9px] text-slate-500 uppercase block">Area</span>
              <span className="font-bold text-white text-xs">{parcelAreaSqm.toLocaleString()} m²</span>
              <span className="text-[9px] text-slate-500 block">({Math.round(parcelAreaSqm * 10.7639).toLocaleString()} sqft)</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 uppercase block">Perimeter</span>
              <span className="font-bold text-cyan-300 text-xs">{parcelPerimeterM.toFixed(1)} m</span>
              <span className="text-[9px] text-slate-500 block">{verticesCount} Vertices</span>
            </div>
          </div>

          {/* Explicit Save Site Geometry Action (Section 8) */}
          <button
            onClick={onSaveGeometry}
            disabled={isSavingGeometry}
            className="w-full py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
          >
            {isSavingGeometry ? (
              <>
                <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                <span>Hashing Geometry...</span>
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

      {/* Statutory Road Width Regulation Controls (Section 14 & 18) */}
      <div className="glass-panel p-3 w-56 border border-white/10 bg-slate-950/90 shadow-2xl rounded-xl flex flex-col gap-2.5 text-xs">
        <div className="flex items-center gap-1.5 text-slate-300 font-semibold border-b border-white/10 pb-1.5">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span>Statutory Road Widths</span>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Existing Frontage:</span>
            <span className="font-mono text-slate-200">{existingRoadWidth} m</span>
          </div>
          <input
            type="range"
            min="6"
            max="30"
            step="1"
            value={existingRoadWidth}
            onChange={(e) =>
              onChangeRoadWidths(
                Number(e.target.value),
                Math.max(Number(e.target.value), proposedRoadWidth)
              )
            }
            className="w-full accent-blue-500 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div className="space-y-1">
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Proposed DP Road:</span>
            <span className="font-mono text-cyan-400 font-semibold">{proposedRoadWidth} m</span>
          </div>
          <input
            type="range"
            min={existingRoadWidth}
            max="45"
            step="1"
            value={proposedRoadWidth}
            onChange={(e) => onChangeRoadWidths(existingRoadWidth, Number(e.target.value))}
            className="w-full accent-cyan-400 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div className="text-[10px] text-slate-500 flex items-center gap-1 pt-1 border-t border-white/5 font-mono">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          <span>Widening buffer: {((proposedRoadWidth - existingRoadWidth) / 2).toFixed(1)}m</span>
        </div>
      </div>
    </aside>
  );
};
