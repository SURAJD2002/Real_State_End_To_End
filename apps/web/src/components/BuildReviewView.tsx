import React, { useState } from 'react';
import { 
  ProjectData, 
  HouseOption, 
  HandoffPackage 
} from '../types';
import { 
  Check, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  ArrowLeft, 
  Sliders, 
  AlertCircle, 
  FileCheck
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
  onOpenTechnicalView,
  isSubmitting = false
}) => {
  const [hasSubmitted, setHasSubmitted] = useState<boolean>(Boolean(activeRelease && activeReleaseId));
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const boq = selectedOption.boq;
  const layout = selectedOption.layout;

  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || 4520000;
  const buaSqFt = Math.round((layout.totalGrossBUASqm || 116) * 10.7639);
  const declaredSqFt = 1100; // Authoritative customer plot area

  const bedsCount = layout.rooms?.filter(r => 
    r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE'
  ).length || 2;

  const locationStr = project?.description 
    ? `${project.name} (${project.description})`
    : project?.name || 'Bandra West, Mumbai, Maharashtra';

  const formatINR = (val: number) => {
    return '₹' + Math.round(val).toLocaleString('en-IN');
  };

  const handleReviewSubmit = async () => {
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
    <div className="pw-page">
      <div className="pw-container">
        
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onBackToCost}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Cost</span>
          </button>

          <span className="pw-badge pw-badge-neutral">
            Step 5 of 6: Build Review
          </span>
        </div>

        {/* Headline (§14) */}
        <div>
          <h1 className="pw-title-xl">
            Ready to move forward?
          </h1>
          <p className="pw-body mt-1">
            Review your project package before submitting it for professional engineering verification.
          </p>
        </div>

        {/* Error banner if submission fails */}
        {submissionError && (
          <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <span className="font-semibold text-rose-200 block">Submission issue</span>
              <span className="text-rose-300/80">{submissionError}</span>
            </div>
          </div>
        )}

        {/* 4-Part Status Grid (§14) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* 1. Land */}
          <div className="pw-card p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Land</span>
              <span className="pw-badge pw-badge-success text-[10px]">
                <Check className="w-3 h-3" />
                Verified
              </span>
            </div>
            <div>
              <span className="text-sm font-bold text-white block truncate">{locationStr}</span>
              <span className="text-xs font-mono text-emerald-400">{declaredSqFt} sq ft Plot</span>
            </div>
          </div>

          {/* 2. Design */}
          <div className="pw-card p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Design</span>
              <span className="pw-badge pw-badge-success text-[10px]">
                <Check className="w-3 h-3" />
                Selected
              </span>
            </div>
            <div>
              <span className="text-sm font-bold text-white block">{bedsCount} BHK · G+{(layout.floors || 2) - 1}</span>
              <span className="text-xs text-slate-400 font-mono">{buaSqFt} sq ft built-up</span>
            </div>
          </div>

          {/* 3. Cost */}
          <div className="pw-card p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cost</span>
              <span className="pw-badge pw-badge-success text-[10px]">
                <Check className="w-3 h-3" />
                Estimated
              </span>
            </div>
            <div>
              <span className="text-sm font-mono font-bold text-white block">{formatINR(totalCost)}</span>
              <span className="text-xs text-slate-400">{boq.qualityTier || 'Standard'} Tier</span>
            </div>
          </div>

          {/* 4. Engineering */}
          <div className="pw-card p-4 space-y-2 bg-[#171b26] border-blue-500/30">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider">Engineering</span>
              <span className="pw-badge pw-badge-primary text-[10px]">
                Required
              </span>
            </div>
            <div>
              <span className="text-xs font-semibold text-white block">Professional review</span>
              <span className="text-[11px] text-slate-400">Structural, MEP &amp; Municipal</span>
            </div>
          </div>
        </div>

        {/* "What happens next?" (§14) */}
        <div className="pw-card space-y-5">
          <div>
            <h3 className="pw-title-md">What happens next?</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              The project transitions from preliminary design into formal engineering verification.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-lg bg-white/[0.02] border border-white/5 space-y-2">
              <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 font-mono text-xs font-bold flex items-center justify-center">
                1
              </span>
              <h4 className="text-xs font-bold text-white">Your selected design is frozen</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                The layout geometry, space areas, and baseline BOQ are version-locked into an immutable release record.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-white/[0.02] border border-white/5 space-y-2">
              <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 font-mono text-xs font-bold flex items-center justify-center">
                2
              </span>
              <h4 className="text-xs font-bold text-white">The project package is prepared</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                IFC4 structural models, site evidence manifests, and trade line-item BOQs are compiled.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-white/[0.02] border border-white/5 space-y-2">
              <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 font-mono text-xs font-bold flex items-center justify-center">
                3
              </span>
              <h4 className="text-xs font-bold text-white">A professional engineer reviews it</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Registered structural and MEP engineers verify soil capacity, column spans, and service ducting.
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-white/[0.02] border border-white/5 space-y-2">
              <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 font-mono text-xs font-bold flex items-center justify-center">
                4
              </span>
              <h4 className="text-xs font-bold text-white">Required approvals are completed</h4>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Statutory municipal submissions and technical sign-offs are conducted before contractor handoff.
              </p>
            </div>
          </div>
        </div>

        {/* Submission Confirmation / Status Banner */}
        {hasSubmitted || activeReleaseId ? (
          <div className="pw-card border-emerald-500/30 bg-[#0d1614] flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white">
                  Build Review Requested
                </h4>
                <p className="text-[11px] text-emerald-300/80 font-mono">
                  Release ID: {activeReleaseId || 'REL-SAMPLE-2026'} · In Professional Review
                </p>
              </div>
            </div>

            <button
              onClick={onGoToEngineerDashboard}
              className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
            >
              <span>View Engineer Review Status</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="pw-card flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-400 max-w-md">
              <span className="text-white font-semibold block mb-0.5">Submit for professional review</span>
              Freezes design parameters and compiles engineering documentation for certified sign-off.
            </div>

            <button
              onClick={handleReviewSubmit}
              disabled={isSubmitting}
              className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
            >
              {isSubmitting ? (
                <>
                  <Clock className="w-4 h-4 animate-spin" />
                  <span>Preparing Package...</span>
                </>
              ) : (
                <>
                  <FileCheck className="w-4 h-4" />
                  <span>Request Build Review</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Technical GIS Link */}
        {onOpenTechnicalView && (
          <div className="pt-1 flex justify-start">
            <button
              onClick={onOpenTechnicalView}
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Inspect Raw Manifest &amp; Immutable Handoff Package</span>
            </button>
          </div>
        )}

      </div>
    </div>
  );
};
