import React from 'react';
import {
  ArrowRight,
  X
} from 'lucide-react';
import { WorkflowStep, ProjectData } from '../types';

interface MyProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  project: ProjectData | null;
  activeStep: WorkflowStep;
  onContinue: (step: WorkflowStep) => void;
}

export const MyProjectModal: React.FC<MyProjectModalProps> = ({
  isOpen,
  onClose,
  project,
  activeStep,
  onContinue
}) => {
  if (!isOpen) return null;

  const steps: { id: WorkflowStep; label: string }[] = [
    { id: 'SITE', label: 'Land' },
    { id: 'FEASIBILITY', label: 'Feasibility' },
    { id: 'DESIGN', label: 'Design' },
    { id: 'COST', label: 'Cost' },
    { id: 'BUILD', label: 'Review' }
  ];

  const currentStepIndex = steps.findIndex(s => s.id === (activeStep === 'ENGINEER' ? 'BUILD' : activeStep));
  const currentStageLabel = steps[currentStepIndex]?.label?.toUpperCase() || 'DESIGN';

  const isPilot = project?.id === 'proj-mumbai-real-1100';
  const declaredSqFt = project?.declaredPlotAreaSqFt || (project?.parcel as any)?.declaredPlotAreaSqFt;
  const plotAreaSqFt = declaredSqFt || (isPilot ? 1100 : (project?.latestFeasibility?.grossPlotAreaSqm ? Math.round(project.latestFeasibility.grossPlotAreaSqm * 10.7639) : null));
  const locationText = project?.name || (isPilot ? 'Bandra West, Mumbai' : 'Your Property');
  const roadWidthFt = project?.parcel?.existingRoadWidthM ? Math.round(project.parcel.existingRoadWidthM / 0.3048) : (isPilot ? 16 : null);
  const jurisdictionText = project?.jurisdiction || (isPilot ? 'Mumbai DCPR 2034' : 'Municipal Jurisdiction');

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in">
      <div className="pw-card w-full max-w-lg p-6 bg-[#0f131d] border-white/15 space-y-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-white/10 pb-4">
          <div>
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-400 block">
              MY PROJECT
            </span>
            <h2 className="text-xl font-bold text-white mt-1">
              {project?.name || (isPilot ? 'Bandra West Home' : 'My Project')}
            </h2>
            <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
              <span className="font-mono text-emerald-400 font-semibold">{plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft` : 'Custom Plot'}</span>
              <span>·</span>
              <span>{locationText}</span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
            data-testid="btn-close-my-project"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Current Stage */}
        <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
            Current stage
          </span>
          <div className="text-lg font-bold text-blue-400 font-mono tracking-wide">
            {currentStageLabel}
          </div>
        </div>

        {/* Progress (§24) */}
        <div className="space-y-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 block">
            Progress
          </span>
          <div className="space-y-1.5 text-xs font-mono">
            {steps.map((s, idx) => {
              const isPast = idx < currentStepIndex;
              const isCurrent = idx === currentStepIndex;

              return (
                <div key={s.id} className="flex items-center gap-2.5 py-1">
                  {isPast ? (
                    <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold">
                      ✓
                    </span>
                  ) : isCurrent ? (
                    <span className="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold shadow-sm">
                      →
                    </span>
                  ) : (
                    <span className="w-5 h-5 rounded-full bg-white/5 text-slate-500 flex items-center justify-center text-[10px]">
                      ○
                    </span>
                  )}
                  <span className={`${isCurrent ? 'text-white font-bold' : isPast ? 'text-slate-300' : 'text-slate-500'}`}>
                    {s.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Primary CTA (§24) */}
        <button
          onClick={() => {
            onContinue(activeStep);
            onClose();
          }}
          className="pw-btn pw-btn-primary pw-btn-lg w-full"
        >
          <span>Continue Project</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        {/* Below: Recent Project Information (§24) */}
        <div className="pt-3 border-t border-white/5 text-xs text-slate-400 space-y-1.5 font-mono">
          <span className="text-[10px] uppercase text-slate-500 block font-semibold">
            Recent project information
          </span>
          <div className="flex justify-between" data-testid="myproject-project-id">
            <span>Project ID:</span>
            <span className="text-blue-400">{project?.id || 'Pending'}</span>
          </div>
          <div className="flex justify-between">
            <span>Location:</span>
            <span className="text-slate-200">{locationText}</span>
          </div>
          <div className="flex justify-between" data-testid="myproject-plot-area">
            <span>Authoritative Plot:</span>
            <span className="text-slate-200">
              {plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft / ${(plotAreaSqFt / 10.7639).toFixed(2)} m²` : 'Pending Survey'}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Road Access:</span>
            <span className="text-slate-200">
              {roadWidthFt ? `${roadWidthFt} ft road width` : 'Direct Road Access'}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Jurisdiction:</span>
            <span className="text-slate-200">{jurisdictionText}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
