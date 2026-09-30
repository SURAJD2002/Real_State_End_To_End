import React from 'react';
import { MousePointer, Pentagon, Route, ShieldAlert, RotateCcw, Sliders } from 'lucide-react';
import { ToolMode } from '../types';

interface CADToolbarProps {
  toolMode: ToolMode;
  onSelectTool: (mode: ToolMode) => void;
  existingRoadWidth: number;
  proposedRoadWidth: number;
  onChangeRoadWidths: (existing: number, proposed: number) => void;
  onClear: () => void;
}

export const CADToolbar: React.FC<CADToolbarProps> = ({
  toolMode,
  onSelectTool,
  existingRoadWidth,
  proposedRoadWidth,
  onChangeRoadWidths,
  onClear
}) => {
  const tools: { mode: ToolMode; label: string; icon: React.ReactNode; shortcut: string }[] = [
    { mode: 'SELECT', label: 'Select & Pan', icon: <MousePointer className="w-4 h-4" />, shortcut: 'V' },
    { mode: 'DRAW_PARCEL', label: 'Draw Parcel Polygon', icon: <Pentagon className="w-4 h-4" />, shortcut: 'P' },
    { mode: 'DRAW_ROAD', label: 'Road Frontage Edge', icon: <Route className="w-4 h-4" />, shortcut: 'R' },
    { mode: 'DRAW_CONSTRAINT', label: 'Utility / Tree Buffer', icon: <ShieldAlert className="w-4 h-4" />, shortcut: 'C' }
  ];

  return (
    <aside className="absolute left-4 top-20 z-20 flex flex-col gap-3">
      {/* Tool Buttons Panel */}
      <div className="glass-toolbar p-1.5 flex flex-col gap-1 w-12 items-center">
        {tools.map((t) => {
          const isActive = toolMode === t.mode;
          return (
            <button
              key={t.mode}
              onClick={() => onSelectTool(t.mode)}
              title={`${t.label} (${t.shortcut})`}
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

        <button
          onClick={onClear}
          title="Reset Geometry (X)"
          className="w-9 h-9 rounded-lg flex items-center justify-center text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Road Width Municipal Control Pill */}
      <div className="glass-panel p-3 w-52 flex flex-col gap-2.5 text-xs">
        <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          <span>Statutory Road Width</span>
        </div>

        <div className="space-y-1.5">
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
            onChange={(e) => onChangeRoadWidths(Number(e.target.value), Math.max(Number(e.target.value), proposedRoadWidth))}
            className="w-full accent-blue-500 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div className="space-y-1.5">
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

        <div className="text-[10px] text-slate-500 leading-tight pt-1 border-t border-white/5">
          Road widening deduction is computed automatically as statutory deduction per DCPR 2034.
        </div>
      </div>
    </aside>
  );
};
