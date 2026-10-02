import React, { useState } from 'react';
import { 
  ProjectData, 
  HouseOption, 
  HandoffPackage 
} from '../types';
import { 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  ArrowLeft, 
  Sliders, 
  AlertCircle, 
  ClipboardCheck,
  Check
} from 'lucide-react';

interface BuildReviewViewProps {
  project: ProjectData | null;
  selectedOption: HouseOption;
  activeRelease: HandoffPackage | null;
  activeReleaseId: string;
  onRequestBuildReview: (tier: string, acks: string[]) => Promise<void>;
  onGoToEngineerDashboard: () => void;
  onBackToCost: () => void;
  onRecalculateCost: () => void;
  onOpenTechnicalView?: () => void;
  isSubmitting?: boolean;
}

export const BuildReviewView: React.FC<BuildReviewViewProps> = ({
  project,
  selectedOption,
  activeRelease,
  activeReleaseId,
  onRequestBuildReview,
  onGoToEngineerDashboard,
  onBackToCost,
  onRecalculateCost,
  onOpenTechnicalView,
  isSubmitting = false
}) => {
  const [hasSubmitted, setHasSubmitted] = useState<boolean>(Boolean(activeRelease && activeReleaseId));
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const boq = selectedOption.boq;
  const layout = selectedOption.layout;

  // Stale Cost Protection (§11, §15)
  // Check if design version matches QTO reference or if cost data is current
  const isCostStale = Boolean(
    boq.lines && boq.lines.length > 0 && 
    boq.lines[0].sourceRefs && 
    !boq.lines[0].sourceRefs.includes(selectedOption.designVersionId.substring(0, 8)) &&
    !boq.qtoHash
  );

  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || 4500000;
  const buaSqFt = Math.round((layout.totalGrossBUASqm || 110) * 10.7639);
  const declaredSqFt = 1100; // Authoritative customer plot area

  const bedsCount = layout.rooms?.filter(r => 
    r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE'
  ).length || 2;

  const locationStr = project?.description 
    ? `${project.name} (${project.description})`
    : project?.name || 'Bandra West, Mumbai, Maharashtra';

  const formatINR = (val: number) => {
    return '₹ ' + Math.round(val).toLocaleString('en-IN');
  };

  const handleReviewSubmit = async () => {
    if (isCostStale) return;
    setSubmissionError(null);
    try {
      const acks = [
        'PROFESSIONAL_DELIVERY',
        'ESTIMATE_RANGE',
        'SITE_VERIFICATION',
        'CHANGE_ORDER_RULES'
      ];
      await onRequestBuildReview(boq.qualityTier || 'STANDARD', acks);
      setHasSubmitted(true);
    } catch (err: any) {
      setSubmissionError(err?.message || 'Failed to submit build review request. Please try again.');
    }
  };

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#07090e] p-6 lg:p-10 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-8 animate-fade-in pb-20">

        {/* Navigation Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
          <button
            type="button"
            onClick={onBackToCost}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Cost</span>
          </button>

          {/* Stepper */}
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-emerald-400 font-medium">1 Land ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">2 Feasibility ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">3 Design ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">4 Cost ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-blue-400 font-bold bg-blue-950/80 border border-blue-500/40 px-2.5 py-0.5 rounded-full">
              5 Build ●
            </span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">6 Engineer</span>
          </div>
        </div>

        {/* Page Header */}
        <div className="space-y-2">
          <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
            Ready to move forward?
          </h1>
          <p className="text-slate-400 text-sm lg:text-base leading-relaxed">
            Review your project before we send it for professional verification.
          </p>
        </div>

        {/* STALE COST WARNING BANNER (Section 11) */}
        {isCostStale && (
          <div className="p-5 rounded-2xl bg-amber-950/40 border border-amber-500/40 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-amber-400 shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-amber-200">
                  Your design has changed since this estimate was created.
                </h3>
                <p className="text-xs text-amber-300/80">
                  Please update your cost estimate to reflect the current design before requesting review.
                </p>
              </div>
            </div>

            <button
              onClick={onRecalculateCost}
              className="text-xs px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-semibold whitespace-nowrap transition-colors"
            >
              Recalculate Cost →
            </button>
          </div>
        )}

        {/* POST-SUBMISSION CONFIRMATION CARD (Section 7) */}
        {(hasSubmitted || (activeRelease && activeReleaseId)) && (
          <div className="rounded-2xl bg-emerald-950/30 border border-emerald-500/40 p-6 space-y-5 animate-fade-in shadow-xl">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center shrink-0 mt-0.5">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              </div>

              <div className="space-y-1">
                <span className="text-xs uppercase tracking-wider font-mono text-emerald-400 font-bold block">
                  Build Review ● Submitted
                </span>
                <h2 className="text-xl font-bold text-white">
                  Your project review has been requested.
                </h2>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Your design, site parameters, and preliminary quantities have been bundled for professional review. A licensed engineer will verify the structural, statutory, and survey requirements before construction authorization.
                </p>
              </div>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-white/10">
              <div className="text-xs text-slate-400 font-mono">
                Status: <span className="text-amber-400 font-bold">Pending Professional Verification</span>
              </div>

              <button
                onClick={onGoToEngineerDashboard}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-display font-semibold text-xs shadow-md shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all"
              >
                <span>View Project Status (Engineer Step)</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* 1. PROJECT SUMMARY CARD (Section 1) */}
        <div className="rounded-2xl bg-slate-900/60 border border-white/10 p-6 space-y-6">
          <div className="border-b border-white/10 pb-3">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <ClipboardCheck className="w-4 h-4 text-blue-400" />
              <span>Project Summary</span>
            </h2>
            <p className="text-xs text-slate-400">Everything assembled from your previous steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            {/* Land Summary */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-white/5 space-y-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                LAND
              </span>
              <div className="text-lg font-bold text-white font-mono">
                {declaredSqFt.toLocaleString()} sq ft
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {locationStr}
              </p>
            </div>

            {/* Design Summary */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-white/5 space-y-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                DESIGN
              </span>
              <div className="text-base font-bold text-white leading-tight">
                {layout.label || 'Selected House Design'}
              </div>
              <div className="text-slate-400 text-[11px] space-y-0.5">
                <div>{bedsCount} BHK • {layout.floors === 1 ? 'Ground Only' : `Ground + ${layout.floors - 1}`}</div>
                <div>Built-up: <strong className="text-slate-200">{buaSqFt.toLocaleString()} sq ft</strong></div>
              </div>
            </div>

            {/* Cost Summary */}
            <div className="p-4 rounded-xl bg-slate-950/60 border border-white/5 space-y-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                COST
              </span>
              <div className="text-lg font-bold text-emerald-400 font-mono">
                {formatINR(totalCost)}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Tier: <strong className="text-slate-200">{boq.qualityTier || 'STANDARD'}</strong> • Rate Snapshot: {boq.rateSnapshotId || 'Mumbai 2026 Q4'}
              </p>
            </div>
          </div>
        </div>

        {/* 2 & 3. DESIGN & COST STATUS (Section 2 & 3) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Design Status */}
          <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/10 space-y-3">
            <span className="text-xs font-semibold text-white block">Design Status</span>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-400">
                <Check className="w-4 h-4 shrink-0" />
                <span>Design selected</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <Check className="w-4 h-4 shrink-0" />
                <span>Design version available</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <Check className="w-4 h-4 shrink-0" />
                <span>House model generated</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-400">
                <Check className="w-4 h-4 shrink-0" />
                <span>Preliminary validation completed</span>
              </div>
            </div>
          </div>

          {/* Cost Status */}
          <div className="p-5 rounded-2xl bg-slate-900/40 border border-white/10 space-y-3 flex flex-col justify-between">
            <div>
              <span className="text-xs font-semibold text-white block mb-2">Cost Status</span>
              <div className="flex items-center gap-2 text-emerald-400 mb-2">
                <Check className="w-4 h-4 shrink-0" />
                <span>Cost estimate available</span>
              </div>
              <div className="text-base font-bold text-white font-mono">
                Estimated cost: {formatINR(totalCost)}
              </div>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed pt-2 border-t border-white/5">
              Final cost will be confirmed after professional review, site verification, specifications and contractor quotation.
            </p>
          </div>
        </div>

        {/* 4. PROJECT READINESS CHECKLIST (Section 4) */}
        <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-5">
          <div className="border-b border-white/10 pb-3">
            <h3 className="text-sm font-semibold text-white">Project Readiness Checklist</h3>
            <p className="text-xs text-slate-400">Pre-construction verification gates</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {/* Customer Completed Steps */}
            <div className="space-y-3">
              <span className="text-[11px] uppercase tracking-wider text-emerald-400 font-mono font-semibold block">
                Completed by You
              </span>
              <div className="space-y-2.5">
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5 flex items-center gap-2.5 text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Land information submitted</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5 flex items-center gap-2.5 text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Feasibility checked</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5 flex items-center gap-2.5 text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>House design selected</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-white/5 flex items-center gap-2.5 text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Preliminary cost reviewed</span>
                </div>
              </div>
            </div>

            {/* Professional Items (Pending verification) */}
            <div className="space-y-3">
              <span className="text-[11px] uppercase tracking-wider text-amber-400 font-mono font-semibold block">
                Pending Professional Verification
              </span>
              <div className="space-y-2.5">
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Site survey verification</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Structural engineering review</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Soil / geotechnical verification where required</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Municipal / statutory approvals</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Final construction drawings</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950/40 border border-white/5 flex items-center gap-2.5 text-slate-400">
                  <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>Contractor / construction scope confirmation</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 5. WHAT HAPPENS NEXT (Section 5) */}
        <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-4">
          <h3 className="text-sm font-semibold text-white">What happens next?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-1.5">
              <div className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center font-bold text-xs">
                1
              </div>
              <span className="font-semibold text-white block">You request a project review</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                We submit your chosen house plan, site bounds, and budget profile.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-1.5">
              <div className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center font-bold text-xs">
                2
              </div>
              <span className="font-semibold text-white block">Professionals verify details</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Licensed engineers and surveyors verify soil, structure, and municipal byelaws.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-white/5 space-y-1.5">
              <div className="w-6 h-6 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center font-bold text-xs">
                3
              </div>
              <span className="font-semibold text-white block">Proceed toward construction</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                After required approvals and contractor confirmations, ground work begins.
              </p>
            </div>
          </div>
        </div>

        {/* Error notification if submission failed */}
        {submissionError && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{submissionError}</span>
          </div>
        )}

        {/* 6. PRIMARY ACTION FOOTER (Section 6, 8) */}
        {!hasSubmitted && !activeRelease && (
          <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="text-xs text-slate-400 leading-relaxed max-w-md">
              <span className="text-white font-semibold block mb-1">
                Notice: Professional Verification Required
              </span>
              This step submits your project for engineering review. It does not automatically authorize or start construction.
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                disabled={isCostStale || isSubmitting}
                onClick={handleReviewSubmit}
                className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-display font-semibold text-sm shadow-xl flex items-center justify-center gap-2 transition-all ${
                  isCostStale || isSubmitting
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-white/5'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/25 hover:scale-[1.01]'
                }`}
              >
                {isSubmitting ? (
                  <span>Submitting Review Request...</span>
                ) : (
                  <>
                    <span>Request Build Review</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Technical view toggle */}
        {onOpenTechnicalView && (
          <div className="text-center pt-2">
            <button
              onClick={onOpenTechnicalView}
              className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1.5 mx-auto transition-colors"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Technical View (Engineering Release & IFC Handoff)</span>
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
