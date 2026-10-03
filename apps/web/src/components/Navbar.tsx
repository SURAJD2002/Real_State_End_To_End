import React from 'react';
import { 
  Building2, 
  CheckCircle2, 
  RefreshCw, 
  Zap, 
  MapPin, 
  HardHat, 
  Home, 
  Ruler, 
  Calculator, 
  FileSpreadsheet, 
  Lock, 
  ChevronRight,
  Check
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
  onLoadGoldenDataset?: () => void;
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
  viewMode = 'CUSTOMER',
  onToggleViewMode
}) => {
  const steps: { id: WorkflowStep; number: number; label: string; icon: React.ReactNode }[] = [
    { id: 'SITE', number: 1, label: 'Land', icon: <Ruler className="w-3.5 h-3.5" /> },
    { id: 'FEASIBILITY', number: 2, label: 'Feasibility', icon: <Calculator className="w-3.5 h-3.5" /> },
    { id: 'DESIGN', number: 3, label: 'Design', icon: <Home className="w-3.5 h-3.5" /> },
    { id: 'COST', number: 4, label: 'Cost', icon: <FileSpreadsheet className="w-3.5 h-3.5" /> },
    { id: 'BUILD', number: 5, label: 'Build', icon: <Lock className="w-3.5 h-3.5" /> },
    { id: 'ENGINEER', number: 6, label: 'Engineer', icon: <HardHat className="w-3.5 h-3.5" /> }
  ];

  const currentStepIndex = steps.findIndex(s => s.id === activeStep);
  const isTechnical = viewMode === 'TECHNICAL';

  return (
    <header className="h-14 px-4 bg-[#10131a] border-b border-white/10 flex items-center justify-between z-30 select-none">
      {/* Brand & Persistent Project Context Bar (§6, §7) */}
      <div className="flex items-center gap-3">
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-[#2563eb] flex items-center justify-center shadow-sm">
            <Building2 className="w-4 h-4 text-white" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-display font-bold text-sm tracking-tight text-white">
              PLANWISE
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10 uppercase">
              Enterprise
            </span>
          </div>
        </div>

        <div className="h-4 w-px bg-white/10 mx-1 hidden sm:block" />

        {/* Project Context Bar (§7) */}
        <div className="hidden sm:flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <MapPin className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span className="font-medium text-white truncate max-w-[150px]" title={project?.name || "Bandra West, Mumbai"}>
              {project?.name || "Bandra West, Mumbai"}
            </span>
            <span className="text-slate-500">·</span>
            <span className="text-slate-300">Residential</span>
            <span className="text-slate-500">·</span>
            <span className="font-mono font-medium text-emerald-400">1,100 sq ft</span>
          </div>

          {hasActiveRelease && (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Build Frozen
            </span>
          )}
        </div>
      </div>

      {/* Primary Persistent Workflow Navigation Stepper (§6) */}
      <nav className="flex items-center bg-[#0a0d13] p-1 rounded-lg border border-white/10 shadow-inner">
        {steps.map((s, index) => {
          const isActive = activeStep === s.id;
          const isCompleted = index < currentStepIndex;

          return (
            <React.Fragment key={s.id}>
              {index > 0 && (
                <ChevronRight className="w-3 h-3 text-slate-700 mx-0.5 shrink-0" />
              )}
              <button
                onClick={() => onChangeStep(s.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : isCompleted
                    ? 'text-slate-300 hover:text-white hover:bg-white/5'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}
                title={`Go to step ${s.number}: ${s.label}`}
              >
                {/* Step indicator: checkmark if completed, number otherwise */}
                {isCompleted ? (
                  <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px]">
                    <Check className="w-2.5 h-2.5" />
                  </span>
                ) : (
                  <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-mono ${
                    isActive ? 'bg-black/30 text-white font-bold' : 'bg-white/5 text-slate-400'
                  }`}>
                    {s.number}
                  </span>
                )}

                <span className="tracking-wide hidden md:inline">{s.label}</span>
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Right Controls: Customer / Technical Toggle & Actions (§16) */}
      <div className="flex items-center gap-2.5">
        {/* Persistent View Mode Toggle */}
        <div className="flex items-center bg-[#0a0d13] p-0.5 rounded-lg border border-white/10">
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('CUSTOMER')}
            className={`px-2.5 py-1 rounded-md text-xs transition-all ${
              viewMode === 'CUSTOMER'
                ? 'bg-blue-600 text-white font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Customer View: Clean, intuitive, progressive disclosure"
          >
            Customer View
          </button>
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('TECHNICAL')}
            className={`px-2.5 py-1 rounded-md text-xs transition-all ${
              viewMode === 'TECHNICAL'
                ? 'bg-[#1e2430] text-blue-300 font-semibold border border-white/10 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Technical View: CAD geometry, CBM, QTO, rule traces, and engineer gates"
          >
            Technical View
          </button>
        </div>

        {/* Technical Status & Trigger (Only shown in Technical Mode) */}
        {isTechnical && (
          <div className="flex items-center gap-2">
            <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 bg-[#0a0d13] px-2.5 py-1 rounded-md border border-white/5">
              {isSaving ? (
                <>
                  <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" />
                  <span className="text-amber-400 font-mono text-[11px]">Syncing...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  <span className="text-slate-300 font-mono text-[11px]">Synced (UTM 43N)</span>
                </>
              )}
            </div>

            <button
              onClick={onRunFeasibility}
              disabled={isCalculating}
              className="pw-btn pw-btn-primary pw-btn-sm"
              title="Run Feasibility Calculation Engine"
            >
              <Zap className={`w-3.5 h-3.5 ${isCalculating ? 'animate-bounce' : ''}`} />
              <span>{isCalculating ? "Calculating..." : "Run"}</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
