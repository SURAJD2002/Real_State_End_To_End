import React from 'react';
import {
  Building2,
  CheckCircle2,
  RefreshCw,
  Zap,
  ChevronRight,
  Check,
  LogOut
} from 'lucide-react';
import { ProjectData, WorkflowStep } from '../types';
import { useAuth } from '../context/AuthContext';

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
  onOpenMyProject?: () => void;
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
  onToggleViewMode,
  onOpenMyProject
}) => {
  const { user, organization, role, logout } = useAuth();

  // Customer 5-step journey vs Professional 6-step journey
  const customerSteps: { id: WorkflowStep; label: string }[] = [
    { id: 'SITE', label: 'Land' },
    { id: 'FEASIBILITY', label: 'Feasibility' },
    { id: 'DESIGN', label: 'Design' },
    { id: 'COST', label: 'Cost' },
    { id: 'BUILD', label: 'Review' }
  ];

  const professionalSteps: { id: WorkflowStep; label: string }[] = [
    { id: 'SITE', label: 'Land' },
    { id: 'FEASIBILITY', label: 'Feasibility' },
    { id: 'DESIGN', label: 'Design' },
    { id: 'COST', label: 'Cost' },
    { id: 'BUILD', label: 'Build' },
    { id: 'ENGINEER', label: 'Engineer' }
  ];

  const isTechnical = viewMode === 'TECHNICAL';
  const displayedSteps = isTechnical ? professionalSteps : customerSteps;

  const getIsActive = (stepId: WorkflowStep) => {
    if (!isTechnical && stepId === 'BUILD') {
      return activeStep === 'BUILD' || activeStep === 'ENGINEER';
    }
    return activeStep === stepId;
  };

  const getStepIndex = (stepId: WorkflowStep) => {
    return displayedSteps.findIndex(s => s.id === stepId);
  };

  const activeIndex = !isTechnical && activeStep === 'ENGINEER' ? 4 : getStepIndex(activeStep);

  return (
    <header className="h-14 px-4 sm:px-6 bg-[#0c0f17] border-b border-white/10 flex items-center justify-between z-30 select-none">
      {/* Left: Brand & Subtitle (§4) */}
      <button
        type="button"
        onClick={onOpenMyProject}
        className="flex items-center gap-3 text-left hover:opacity-90 transition-opacity cursor-pointer group"
        title="View My Project Dashboard"
        data-testid="btn-open-my-project"
      >
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
          <Building2 className="w-4 h-4 text-white" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 leading-none">
            <span className="font-display font-bold text-sm tracking-tight text-white">
              PLANWISE
            </span>
            {hasActiveRelease && (
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" title="Active Release Immutable" />
            )}
          </div>
          <span className="text-[11px] text-slate-400 font-medium tracking-wide leading-none mt-1" title={project?.name || (project?.declaredPlotAreaSqFt ? `${project.declaredPlotAreaSqFt} sq ft` : undefined)}>
            Build with confidence.
          </span>
        </div>
      </button>

      {/* Center: Simplified Customer Stepper (§2, §4) */}
      <nav className="flex items-center bg-[#07090e] p-1 rounded-xl border border-white/10 shadow-inner">
        {displayedSteps.map((s, index) => {
          const isActive = getIsActive(s.id);
          const isCompleted = index < activeIndex;

          return (
            <React.Fragment key={s.id}>
              {index > 0 && (
                <ChevronRight className="w-3.5 h-3.5 text-slate-700 mx-1 shrink-0" />
              )}
              <button
                onClick={() => onChangeStep(s.id)}
                data-testid={`nav-step-${s.id}`}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : isCompleted
                    ? 'text-slate-300 hover:text-white hover:bg-white/5'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}
                title={`Go to ${s.label}`}
              >
                {isCompleted ? (
                  <span className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px]">
                    <Check className="w-2.5 h-2.5" />
                  </span>
                ) : (
                  <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-mono ${
                    isActive ? 'bg-black/30 text-white font-bold' : 'bg-white/5 text-slate-400'
                  }`}>
                    {index + 1}
                  </span>
                )}
                <span className="font-medium tracking-wide">{s.label}</span>
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Right: Customer Mode vs Professional Mode (§3, §4) */}
      <div className="flex items-center gap-2">
        <div className="flex items-center bg-[#07090e] p-1 rounded-xl border border-white/10">
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('CUSTOMER')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'CUSTOMER'
                ? 'bg-blue-600 text-white font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Customer Mode: Plain language, streamlined experience"
          >
            Customer Mode
          </button>
          <button
            onClick={() => onToggleViewMode && onToggleViewMode('TECHNICAL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'TECHNICAL'
                ? 'bg-[#1e2538] text-blue-300 font-semibold border border-blue-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Professional Mode: CBM, IFC, rule traces, QTO, BOQ, and engineer gates"
          >
            Professional Mode
          </button>
        </div>

        {/* Technical Status (Only in Professional Mode) */}
        {isTechnical && (
          <div className="hidden xl:flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-[#07090e] px-2.5 py-1.5 rounded-lg border border-white/5">
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
              <span>{isCalculating ? "Calculating..." : "Run Engine"}</span>
            </button>
          </div>
        )}

        {/* User Profile & Logout */}
        <div className="flex items-center gap-2 pl-2 border-l border-white/10">
          {user ? (
            <div className="flex items-center gap-2">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-xs font-medium text-slate-200 leading-tight">
                  {organization?.name || user.email}
                </span>
                <span className="text-[10px] text-blue-400 font-mono leading-tight">
                  {role || 'MEMBER'}
                </span>
              </div>
              <button
                onClick={logout}
                className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                title="Log out of enterprise workspace"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => { window.location.pathname = '/login'; }}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition-colors"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
