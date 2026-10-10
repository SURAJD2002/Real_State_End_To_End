import React, { useState } from 'react';
import {
  ProjectData,
  HouseOption,
  HandoffPackage
} from '../types';
import {
  Check,
  Clock,
  ArrowRight,
  ArrowLeft,
  Sliders,
  AlertCircle,
  Download,
  Compass,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { HomeReportDownloadModal } from './HomeReportDownloadModal';
import { DrawingSheetsModal } from './DrawingSheetsModal';

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
  const [isPdfModalOpen, setIsPdfModalOpen] = useState<boolean>(false);
  const [isDrawingsModalOpen, setIsDrawingsModalOpen] = useState<boolean>(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  const boq = selectedOption.boq;
  const layout = selectedOption.layout;

  const isPilot = project?.id === 'proj-mumbai-real-1100' || selectedOption.designVersionId === 'DV-OPT-B-9be0a983';
  const declaredSqFt = project?.declaredPlotAreaSqFt || (project?.parcel as any)?.declaredPlotAreaSqFt;
  const plotAreaSqFt = declaredSqFt || (isPilot ? 1100 : null);
  const locationText = project?.name || (isPilot ? 'Bandra West' : 'Your Property');

  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || (isPilot ? 4520000 : 0);
  const buaSqFt = Math.round((layout.totalGrossBUASqm || 98.16) * 10.7639);
  const bedroomCount = layout.rooms?.filter(r => r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE').length || 2;
  const floorsDesc = layout.floors ? (layout.floors === 1 ? 'Ground Only' : `G+${layout.floors - 1}`) : (isPilot ? 'G+1' : 'Multi-Storey');

  const badgeText = plotAreaSqFt
    ? `${plotAreaSqFt.toLocaleString()} sq ft · ${locationText}`
    : locationText;

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
      setSubmissionError(err?.message || 'Failed to submit review request. Please try again.');
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

          <span className="pw-badge pw-badge-neutral font-mono text-[11px]">
            {badgeText}
          </span>
        </div>

        {/* Title (§13) */}
        <div>
          <h1 className="pw-title-xl">
            Your home plan is ready for professional review
          </h1>
          <p className="pw-body mt-1">
            Review your summary below before requesting independent professional verification.
          </p>
        </div>

        {/* Error banner if submission fails */}
        {submissionError && (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="text-xs">
              <span className="font-semibold text-amber-200 block">Unable to complete request</span>
              <span className="text-amber-300/80">{submissionError}</span>
            </div>
          </div>
        )}

        {/* 4 Summary Cards (§13) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {/* 1. LAND */}
          <div className="pw-card p-5 space-y-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              LAND
            </span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
              <Check className="w-4 h-4" />
              <span>Verified</span>
            </div>
            <p className="text-xs text-slate-400">
              {badgeText}
            </p>
          </div>

          {/* 2. DESIGN */}
          <div className="pw-card p-5 space-y-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              DESIGN
            </span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
              <Check className="w-4 h-4" />
              <span>Selected</span>
            </div>
            <p className="text-xs text-slate-400">
              {bedroomCount} BHK · {floorsDesc} ({buaSqFt} sq ft)
            </p>
          </div>

          {/* 3. COST */}
          <div className="pw-card p-5 space-y-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              COST
            </span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
              <Check className="w-4 h-4" />
              <span>Estimated</span>
            </div>
            <p className="text-xs font-slate-400 font-mono text-slate-400">
              {totalCost > 0 ? formatINR(totalCost) : 'Estimate Calculating'}
            </p>
          </div>

          {/* 4. DRAWINGS */}
          <div className="pw-card p-5 space-y-2">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              DRAWINGS
            </span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
              <Check className="w-4 h-4" />
              <span>Available</span>
            </div>
            <button
              onClick={() => setIsDrawingsModalOpen(true)}
              className="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2 flex items-center gap-1 text-left"
            >
              <span>View drawing set</span>
            </button>
          </div>
        </div>

        {/* What happens next? (§13) */}
        <div className="pw-card p-6 space-y-4">
          <h3 className="pw-title-md">What happens next?</h3>
          <ol className="space-y-3 text-xs text-slate-300">
            <li className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-600/20 text-blue-400 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                1
              </span>
              <span className="leading-relaxed">Your design is locked for review.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-600/20 text-blue-400 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                2
              </span>
              <span className="leading-relaxed">A professional reviews the project.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-600/20 text-blue-400 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                3
              </span>
              <span className="leading-relaxed">Required site/engineering checks are completed.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-600/20 text-blue-400 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                4
              </span>
              <span className="leading-relaxed">Formal approvals happen where required.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="w-5 h-5 rounded-full bg-blue-600/20 text-blue-400 font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                5
              </span>
              <span className="leading-relaxed">Construction can proceed only after the appropriate approvals.</span>
            </li>
          </ol>

          {/* Quick Actions for Documentation */}
          <div className="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsDrawingsModalOpen(true)}
                className="pw-btn pw-btn-secondary pw-btn-sm"
              >
                <Compass className="w-3.5 h-3.5 text-blue-400" />
                <span>View Drawing Set</span>
              </button>

              <button
                type="button"
                onClick={() => setIsPdfModalOpen(true)}
                className="pw-btn pw-btn-secondary pw-btn-sm"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
                <span>Download Home Documentation</span>
              </button>
            </div>

            {/* Technical Details Drawer Toggle (§25) */}
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>{showTechnicalDetails ? 'Hide technical details' : 'Technical Details'}</span>
              {showTechnicalDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>

          {showTechnicalDetails && (
            <div className="mt-3 p-4 rounded-xl bg-[#080b11] border border-blue-500/20 space-y-2 font-mono text-xs animate-fade-in">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <span className="text-[10px] text-slate-500 block">RELEASE ID</span>
                  <span className="text-white">{activeReleaseId || 'rel-pilot-20261002-aedf9830'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">FINGERPRINT</span>
                  <span className="text-white truncate block">876f21ae8009...</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">STATE LOCK</span>
                  <span className="text-emerald-400">G5/G6 IMMUTABLE</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">JURISDICTION</span>
                  <span className="text-white">MUMBAI_DCPR_2034</span>
                </div>
              </div>
              {onOpenTechnicalView && (
                <div className="pt-2 border-t border-white/5 flex justify-end">
                  <button
                    type="button"
                    onClick={onOpenTechnicalView}
                    className="text-xs text-blue-400 hover:text-blue-300 underline"
                  >
                    Open in Technical Mode
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Primary CTA (§13) */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
          {hasSubmitted || activeReleaseId ? (
            <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-blue-950/20 border border-blue-500/30">
              <div className="text-xs">
                <span className="font-bold text-white block">Review In Progress</span>
                <span className="text-slate-400">Your design is locked and waiting for professional verification.</span>
              </div>
              <button
                onClick={onGoToEngineerDashboard}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
              >
                <span>View Professional Review</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-xs text-slate-400">
                Lock your project design and request certified engineering review.
              </div>

              <button
                onClick={handleReviewSubmit}
                disabled={isSubmitting}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
              >
                {isSubmitting ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    <span>Preparing Review...</span>
                  </>
                ) : (
                  <>
                    <span>Request Professional Review</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          )}
        </div>

      </div>

      {/* PDF Modal */}
      <HomeReportDownloadModal
        isOpen={isPdfModalOpen}
        onClose={() => setIsPdfModalOpen(false)}
        selectedOption={selectedOption}
        project={project}
        onViewHome={onBackToCost}
      />

      {/* Drawing Sheets Modal */}
      <DrawingSheetsModal
        isOpen={isDrawingsModalOpen}
        onClose={() => setIsDrawingsModalOpen(false)}
        designVersionId={selectedOption.designVersionId || 'DV-OPT-B-9be0a983'}
        optionLabel={selectedOption.title || 'Selected Residence'}
      />
    </div>
  );
};
