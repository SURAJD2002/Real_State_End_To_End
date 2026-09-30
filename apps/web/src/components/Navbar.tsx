import React from 'react';
import { Building2, CheckCircle2, RefreshCw, Zap, MapPin, Sparkles } from 'lucide-react';
import { ProjectData } from '../types';

interface NavbarProps {
  project: ProjectData | null;
  isSaving: boolean;
  isCalculating: boolean;
  onRunFeasibility: () => void;
  onLoadGoldenDataset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  project,
  isSaving,
  isCalculating,
  onRunFeasibility,
  onLoadGoldenDataset
}) => {
  return (
    <header className="h-14 px-4 bg-[#090d16]/90 backdrop-blur-md border-b border-white/10 flex items-center justify-between z-30 select-none">
      {/* Brand & Project Context */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-sm tracking-wide text-white">
                PLANWISE <span className="text-cyan-400 font-normal text-xs uppercase px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40">Enterprise</span>
              </span>
            </div>
          </div>
        </div>

        <div className="h-5 w-px bg-white/10" />

        {/* Project Name & Tenure */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-300 font-medium">
            <MapPin className="w-3.5 h-3.5 text-blue-400" />
            <span>{project?.name || "Bandra East Transit Corridor"}</span>
          </div>

          <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700/60">
            {project?.parcel?.cadastralNumber || "CTS-1842-BANDRA"}
          </span>

          <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 font-mono">
            DCPR 2034 (Mumbai)
          </span>
        </div>
      </div>

      {/* Center Auto-Save / Engine Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-md border border-white/5">
          {isSaving ? (
            <>
              <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" />
              <span className="text-amber-400 font-mono">Syncing Geometry...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span className="text-slate-300 font-mono">Auto-Saved (UTM 43N)</span>
            </>
          )}
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={onLoadGoldenDataset}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-200 border border-slate-700/60 text-xs font-medium transition-all hover:border-slate-500 shadow-sm"
          title="Load canonical 10,000 sqm Mumbai Benchmark plot"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Load Golden Benchmark</span>
        </button>

        <button
          onClick={onRunFeasibility}
          disabled={isCalculating}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all active:scale-95 disabled:opacity-50"
        >
          <Zap className={`w-3.5 h-3.5 text-white ${isCalculating ? 'animate-bounce' : ''}`} />
          <span>{isCalculating ? "Executing DAG..." : "Calculate Feasibility"}</span>
        </button>
      </div>
    </header>
  );
};
