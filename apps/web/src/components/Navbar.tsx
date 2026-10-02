import React from 'react';
import { 
  Building2, 
  CheckCircle2, 
  RefreshCw, 
  Zap, 
  MapPin, 
  Sparkles, 
  HardHat, 
  Home, 
  Ruler, 
  Calculator, 
  FileSpreadsheet, 
  Lock, 
  ChevronRight
} from 'lucide-react';
import { ProjectData, WorkflowStep } from '../types';

interface NavbarProps {
  project: ProjectData | null;
  isSaving: boolean;
  isCalculating: boolean;
  activeStep: WorkflowStep;
  onChangeStep: (step: WorkflowStep) => void;
  hasActiveRelease: boolean;
  onRunFeasibility: () => void;
  onLoadGoldenDataset: () => void;
  viewMode?: 'CUSTOMER' | 'TECHNICAL';
  onToggleViewMode?: (mode: 'CUSTOMER' | 'TECHNICAL') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  project,
  isSaving,
  isCalculating,
  activeStep,
  onChangeStep,
  hasActiveRelease,
  onRunFeasibility,
  onLoadGoldenDataset,
  viewMode = 'CUSTOMER',
  onToggleViewMode
}) => {
  const steps: { id: WorkflowStep; number: string; label: string; icon: React.ReactNode }[] = [
    { id: 'SITE', number: '1', label: 'Land', icon: <Ruler className="w-3.5 h-3.5" /> },
    { id: 'FEASIBILITY', number: '2', label: 'Feasibility', icon: <Calculator className="w-3.5 h-3.5" /> },
    { id: 'DESIGN', number: '3', label: 'Design', icon: <Home className="w-3.5 h-3.5" /> },
    { id: 'COST', number: '4', label: 'Cost', icon: <FileSpreadsheet className="w-3.5 h-3.5" /> },
    { id: 'BUILD', number: '5', label: 'Build', icon: <Lock className="w-3.5 h-3.5" /> },
    { id: 'ENGINEER', number: '6', label: 'Engineer', icon: <HardHat className="w-3.5 h-3.5" /> }
  ];

  const isTechnical = viewMode === 'TECHNICAL';

  return (
    <header className="h-14 px-4 bg-[#07090e]/95 backdrop-blur-md border-b border-white/10 flex items-center justify-between z-30 select-none">
      {/* Brand & Project Metadata */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Building2 className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-display font-bold text-sm tracking-wide text-white">
                PLANWISE
              </span>
              {isTechnical && (
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950/70 text-cyan-400 border border-cyan-800/40 uppercase">
                  Enterprise
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="h-4 w-px bg-white/10" />

        {/* Project Name & Context */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-xs text-slate-200 font-medium">
            <MapPin className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span className="truncate max-w-[170px]" title={project?.name || "Bandra West, Mumbai"}>
              {project?.name || "Bandra West, Mumbai"}
            </span>
          </div>

          {isTechnical && (
            <>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-700/60">
                {project?.parcel?.cadastralNumber || "CTS-1842-BANDRA"}
              </span>

              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/70 text-emerald-400 border border-emerald-800/40">
                DCPR 2034 Verified
              </span>
            </>
          )}
        </div>
      </div>

      {/* Primary Workflow Navigation Tabs: 1. Land -> 2. Feasibility -> 3. Design -> 4. Cost -> 5. Build -> 6. Engineer */}
      <nav className="flex items-center bg-slate-950/90 p-1 rounded-lg border border-white/10 shadow-inner">
        {steps.map((s, index) => {
          const isActive = activeStep === s.id;
          const isEngineer = s.id === 'ENGINEER';

          return (
            <React.Fragment key={s.id}>
              {index > 0 && <ChevronRight className="w-3 h-3 text-slate-600 mx-0.5" />}
              <button
                onClick={() => onChangeStep(s.id)}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-all relative ${
                  isActive
                    ? isEngineer
                      ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                      : 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <span className={`text-[10px] font-mono px-1 rounded ${isActive ? 'bg-black/30 text-white' : 'bg-white/5 text-slate-400'}`}>
                  {s.number}
                </span>
                {s.icon}
                <span className="font-display tracking-wider text-[11px]">{s.label}</span>

                {isEngineer && hasActiveRelease && (
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse ml-0.5" title="Active Frozen Release" />
                )}
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Right Controls: Mode Toggle, Auto-Save Status, Benchmark/Run Actions */}
      <div className="flex items-center gap-2.5">
        {/* Simple Customer Mode vs Advanced Technical Mode Toggle */}
        <div className="flex items-center bg-slate-950 p-0.5 rounded-lg border border-white/10">
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('CUSTOMER')}
            className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
              viewMode === 'CUSTOMER'
                ? 'bg-blue-600 text-white font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Simplified step-by-step customer experience"
          >
            Simple
          </button>
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('TECHNICAL')}
            className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
              viewMode === 'TECHNICAL'
                ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Engineering CAD, GIS, and rule traces view"
          >
            Technical View
          </button>
        </div>

        {isTechnical && (
          <>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950 px-2.5 py-1 rounded-md border border-white/5">
              {isSaving ? (
                <>
                  <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" />
                  <span className="text-amber-400 font-mono text-[11px]">Syncing...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  <span className="text-slate-300 font-mono text-[11px]">Auto-Saved (UTM 43N)</span>
                </>
              )}
            </div>

            <button
              onClick={onLoadGoldenDataset}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/60 text-xs font-medium transition-all hover:border-slate-500 shadow-sm"
              title="Load canonical 10,000 sqm Mumbai Benchmark plot"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Benchmark</span>
            </button>

            <button
              onClick={onRunFeasibility}
              disabled={isCalculating}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold shadow-md shadow-blue-500/20 transition-all active:scale-95 disabled:opacity-50"
            >
              <Zap className={`w-3.5 h-3.5 text-white ${isCalculating ? 'animate-bounce' : ''}`} />
              <span>{isCalculating ? "Calculating..." : "Run"}</span>
            </button>
          </>
        )}
      </div>
    </header>
  );
};
