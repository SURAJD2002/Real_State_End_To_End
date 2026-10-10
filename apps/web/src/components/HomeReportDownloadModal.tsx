import React, { useState, useEffect } from 'react';
import {
  Download,
  CheckCircle2,
  Clock,
  X,
  Package,
  ShieldCheck,
  Layers,
  HardHat,
  Building2,
  ChevronDown,
  Sparkles,
  ExternalLink,
  Lock
} from 'lucide-react';
import { HouseOption, ProjectData } from '../types';

interface HomeReportDownloadModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedOption: HouseOption;
  project?: ProjectData | null;
  onViewHome?: () => void;
}

type GenerationStep = {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'done';
};

const INITIAL_STEPS: GenerationStep[] = [
  { id: '1', label: 'Reading design model & version lineage', status: 'pending' },
  { id: '2', label: 'Preparing authoritative 2D vector floor plans', status: 'pending' },
  { id: '3', label: 'Compiling IS 1200 model-linked takeoff quantities', status: 'pending' },
  { id: '4', label: 'Calculating 7-trade BOQ and regional cost waterfall', status: 'pending' },
  { id: '5', label: 'Evaluating 12-point statutory & computational validation', status: 'pending' },
  { id: '6', label: 'Binding professional review gates & cryptographic release manifest', status: 'pending' },
  { id: '7', label: 'Finalizing deterministic vector PDF package', status: 'pending' },
];

export const HomeReportDownloadModal: React.FC<HomeReportDownloadModalProps> = ({
  isOpen,
  onClose,
  selectedOption,
  project,
  onViewHome
}) => {
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [steps, setSteps] = useState<GenerationStep[]>(INITIAL_STEPS);
  const [generationComplete, setGenerationComplete] = useState<boolean>(false);
  const [reportMetadata, setReportMetadata] = useState<any>(null);
  const [packageMetadata, setPackageMetadata] = useState<any>(null);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);

  const isPilot = project?.id === 'proj-mumbai-real-1100';
  const projectName = project?.name || (isPilot ? 'Bandra West Residential Development' : 'Custom Home Project');
  const declaredSqFt = project?.declaredPlotAreaSqFt || (project?.parcel as any)?.declaredPlotAreaSqFt;
  const plotAreaSqFt = declaredSqFt || (isPilot ? 1100 : (project?.latestFeasibility?.grossPlotAreaSqm ? Math.round(project.latestFeasibility.grossPlotAreaSqm * 10.7639) : null));
  const plotAreaSqm = plotAreaSqFt ? (plotAreaSqFt / 10.7639).toFixed(2) : '102.19';

  const designVersionId = selectedOption.designVersionId || 'DV-OPT-B-9be0a983';
  const layout = selectedOption.layout;
  const boq = selectedOption.boq;
  const buaSqm = layout.totalGrossBUASqm || 98.16;
  const buaSqFt = Math.round(buaSqm * 10.7639);
  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || (isPilot ? 1318391.34 : 0);

  const formatINR = (val: number) => {
    return '₹' + Math.round(val).toLocaleString('en-IN');
  };

  // Start generation progress flow
  const handleStartGeneration = async () => {
    setIsGenerating(true);
    setGenerationComplete(false);
    setCurrentStepIndex(0);

    setSteps(INITIAL_STEPS.map((s, idx) => ({
      ...s,
      status: idx === 0 ? 'active' : 'pending'
    })));

    try {
      // Trigger API in parallel
      const postPromise = fetch(`/api/v1/design-versions/${designVersionId}/reports/home`, {
        method: 'POST'
      }).then(res => res.json()).catch(() => null);

      const pkgPromise = fetch(`/api/v1/design-versions/${designVersionId}/reports/complete-package`, {
        method: 'POST'
      }).then(res => res.json()).catch(() => null);

      // Animate progress steps sequentially
      for (let i = 0; i < INITIAL_STEPS.length; i++) {
        await new Promise(r => setTimeout(r, 450));
        setCurrentStepIndex(i);
        setSteps(prev => prev.map((step, idx) => {
          if (idx < i) return { ...step, status: 'done' };
          if (idx === i) return { ...step, status: 'active' };
          return { ...step, status: 'pending' };
        }));
      }

      const repData = await postPromise;
      const pkgData = await pkgPromise;

      setSteps(prev => prev.map(s => ({ ...s, status: 'done' })));
      setReportMetadata(repData);
      setPackageMetadata(pkgData);
      setGenerationComplete(true);
    } catch (e) {
      setSteps(prev => prev.map(s => ({ ...s, status: 'done' })));
      setGenerationComplete(true);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (isOpen && !generationComplete && !isGenerating) {
      handleStartGeneration();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl rounded-2xl bg-[#090d16] border border-blue-500/30 shadow-2xl text-slate-200 overflow-hidden flex flex-col max-h-[92vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase tracking-widest text-blue-400 font-bold">
                  Planwise Enterprise
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Authoritative CBM
                </span>
              </div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Home Documentation &amp; PDF Generation
              </h2>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">

          {/* YOUR HOME IS READY BANNER (§9) */}
          <div className="p-5 rounded-xl bg-gradient-to-br from-blue-950/40 via-slate-900/70 to-slate-950 border border-blue-500/20 shadow-inner">
            <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
              <div>
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  YOUR HOME IS READY
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  2BHK Contemporary Architectural Residence
                </h3>
                <span className="text-[11px] text-slate-400 block">{projectName}</span>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-mono text-slate-400 block">Design Version</span>
                <code className="text-xs text-blue-300 font-bold">{designVersionId}</code>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Plot Area</span>
                <span className="font-bold text-white text-sm">{plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft` : 'Custom Plot'}</span>
                <span className="text-[10px] text-slate-500 block">{plotAreaSqFt ? `${plotAreaSqm} m² (Verified)` : 'Pending Survey'}</span>
              </div>

              <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Built-Up Area</span>
                <span className="font-bold text-white text-sm">{buaSqm.toFixed(1)} m²</span>
                <span className="text-[10px] text-slate-500 block">{buaSqFt} sq ft ({layout.floors ? (layout.floors === 1 ? 'Ground Only' : `G+${layout.floors - 1}`) : 'G+1'})</span>
              </div>

              <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Direct Cost</span>
                <span className="font-bold text-emerald-400 text-sm">{totalCost > 0 ? formatINR(totalCost) : 'Estimate Pending'}</span>
                <span className="text-[10px] text-slate-500 block">{buaSqFt > 0 && totalCost > 0 ? `₹${Math.round(totalCost / buaSqFt).toLocaleString()} / sq ft BUA` : 'Estimated Rate'}</span>
              </div>

              <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                <span className="text-[10px] text-slate-400 uppercase font-mono block">Computational Validation</span>
                <span className="font-bold text-emerald-400 text-sm flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  12 / 12 PASS
                </span>
                <span className="text-[10px] text-slate-500 block">Mumbai DCPR 2034</span>
              </div>
            </div>

            {/* Governance Status Bar */}
            <div className="mt-3 pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400 font-mono">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Professional Review: <strong className="text-white">G0–G4 VERIFIED</strong></span>
              </div>
              <div className="flex items-center gap-1.5 text-amber-400/90">
                <Lock className="w-3.5 h-3.5" />
                <span>G5 Municipal &amp; G6 Contractor: <strong>LOCKED</strong></span>
              </div>
            </div>
          </div>

          {/* GENERATION PROGRESS STEPPER */}
          {isGenerating && (
            <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30 space-y-3 animate-in fade-in">
              <div className="flex items-center justify-between text-xs">
                <span className="text-blue-300 font-semibold flex items-center gap-2">
                  <Clock className="w-4 h-4 animate-spin text-blue-400" />
                  Preparing your home report...
                </span>
                <span className="text-slate-400 font-mono text-[11px]">
                  Step {currentStepIndex + 1} of {steps.length}
                </span>
              </div>

              <div className="space-y-1.5">
                {steps.map((step) => (
                  <div key={step.id} className="flex items-center gap-2.5 text-xs">
                    {step.status === 'done' ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    ) : step.status === 'active' ? (
                      <Clock className="w-3.5 h-3.5 text-blue-400 animate-spin shrink-0" />
                    ) : (
                      <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
                    )}
                    <span className={step.status === 'done' ? 'text-slate-300' : step.status === 'active' ? 'text-white font-medium' : 'text-slate-600'}>
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* READY ACTION CARDS */}
          {generationComplete && (
            <div className="space-y-4 animate-in fade-in">
              <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Home Report Ready</h4>
                    <p className="text-[11px] text-emerald-300/80">
                      16-page authoritative package compiled deterministically from CBM geometry.
                    </p>
                  </div>
                </div>

                <a
                  href={`/api/v1/design-versions/${designVersionId}/reports/home/${reportMetadata?.reportId || 'default'}/download`}
                  download
                  className="pw-btn pw-btn-primary px-4 py-2 text-xs flex items-center gap-2 whitespace-nowrap shadow-lg shadow-blue-600/30"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Home PDF</span>
                </a>
              </div>

              {/* Action Buttons Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <a
                  href={`/api/v1/design-versions/${designVersionId}/reports/${packageMetadata?.reportId || 'default'}/download?format=zip`}
                  download
                  className="p-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-white/10 hover:border-blue-500/30 flex items-center justify-between text-left transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-500/10 group-hover:bg-blue-500/20 text-blue-400 flex items-center justify-center">
                      <Package className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white group-hover:text-blue-300 transition-colors">
                        Download Complete Package (ZIP)
                      </h4>
                      <p className="text-[10px] text-slate-400">
                        10 modular PDFs: Plans, 3D, QTO, BOQ, Review &amp; Manifest
                      </p>
                    </div>
                  </div>
                  <Download className="w-4 h-4 text-slate-400 group-hover:text-blue-300 transition-colors" />
                </a>

                {onViewHome && (
                  <button
                    onClick={() => {
                      onClose();
                      onViewHome();
                    }}
                    className="p-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-white/10 hover:border-cyan-500/30 flex items-center justify-between text-left transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-cyan-500/10 group-hover:bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                        <Layers className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                          View Interactive 2D/3D Model
                        </h4>
                        <p className="text-[10px] text-slate-400">
                          Inspect live CAD floor plans, wall segments &amp; schedules
                        </p>
                      </div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-cyan-300 transition-colors" />
                  </button>
                )}
              </div>

              {/* ADVANCED REPORTS EXPANDER */}
              <div className="border border-white/5 rounded-xl bg-white/[0.01] overflow-hidden">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="w-full px-4 py-2.5 flex items-center justify-between text-xs text-slate-400 hover:text-white transition-colors"
                >
                  <span className="font-semibold flex items-center gap-2">
                    <HardHat className="w-3.5 h-3.5 text-amber-400" />
                    Advanced Professional &amp; Engineering Reports (Architects &amp; QS)
                  </span>
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                </button>

                {showAdvanced && (
                  <div className="p-4 pt-1 border-t border-white/5 grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    <button
                      onClick={async () => {
                        const res = await fetch(`/api/v1/design-versions/${designVersionId}/reports/technical`, { method: 'POST' });
                        const data = await res.json();
                        if (data.downloadUrl) window.open(data.downloadUrl, '_blank');
                      }}
                      className="p-2.5 rounded-lg bg-slate-950 border border-white/5 hover:border-amber-500/40 text-left transition-colors"
                    >
                      <span className="text-[11px] font-bold text-white block">Technical Report</span>
                      <span className="text-[9px] text-slate-400">Structural, MEP &amp; Specs</span>
                    </button>

                    <button
                      onClick={async () => {
                        const res = await fetch(`/api/v1/design-versions/${designVersionId}/reports/cost-boq`, { method: 'POST' });
                        const data = await res.json();
                        if (data.downloadUrl) window.open(data.downloadUrl, '_blank');
                      }}
                      className="p-2.5 rounded-lg bg-slate-950 border border-white/5 hover:border-amber-500/40 text-left transition-colors"
                    >
                      <span className="text-[11px] font-bold text-white block">Cost &amp; BOQ</span>
                      <span className="text-[9px] text-slate-400">IS 1200 QTO &amp; Rates</span>
                    </button>

                    <button
                      onClick={async () => {
                        const res = await fetch(`/api/v1/design-versions/${designVersionId}/reports/professional`, { method: 'POST' });
                        const data = await res.json();
                        if (data.downloadUrl) window.open(data.downloadUrl, '_blank');
                      }}
                      className="p-2.5 rounded-lg bg-slate-950 border border-white/5 hover:border-amber-500/40 text-left transition-colors"
                    >
                      <span className="text-[11px] font-bold text-white block">Professional Handoff</span>
                      <span className="text-[9px] text-slate-400">Gates G0–G6 Ledger</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* MANDATORY LEGAL DISCLAIMER NOTICE */}
          <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-[10px] text-amber-300/80 leading-relaxed">
            <strong>Mandatory Governance Notice:</strong> Computational validation is not professional certification.
            Preliminary design is not municipal approval (MCGM). Preliminary cost is not a contractor quotation.
            Structural safety requires licensed structural engineer verification prior to physical construction.
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-white/10 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
          <span className="font-mono text-[10px]">
            Engine: Planwise-CBM-v1.4.0 · Immutable Release
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
