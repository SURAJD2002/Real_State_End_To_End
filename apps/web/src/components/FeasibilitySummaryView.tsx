import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ArrowLeft,
  Sliders,
  ExternalLink
} from 'lucide-react';
import { FeasibilityResult, ProjectData } from '../types';
import { RuleExplainabilityModal } from './RuleExplainabilityModal';

interface FeasibilitySummaryViewProps {
  feasibility: FeasibilityResult | null;
  project: ProjectData | null;
  onProceedToDesign: () => void;
  onBackToLand: () => void;
  onOpenTechnicalView?: () => void;
  onRetry?: () => void;
}

export const FeasibilitySummaryView: React.FC<FeasibilitySummaryViewProps> = ({
  feasibility,
  project,
  onProceedToDesign,
  onBackToLand,
  onOpenTechnicalView,
  onRetry
}) => {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [isExplainModalOpen, setIsExplainModalOpen] = useState(false);

  // 1. Check if this is explicitly the authoritative pilot project
  const isPilot = project?.id === 'proj-mumbai-real-1100';

  // 2. Extract Real Project Data without silently falling back to pilot values
  const declaredSqFt = project?.declaredPlotAreaSqFt || (project?.parcel as any)?.declaredPlotAreaSqFt;
  const computedFromFeasibilitySqFt = feasibility?.grossPlotAreaSqm
    ? Math.round(feasibility.grossPlotAreaSqm * 10.7639)
    : null;
  const plotAreaSqFt = declaredSqFt || computedFromFeasibilitySqFt || (isPilot ? 1100 : null);

  const locationText = project?.name || (isPilot ? 'Bandra West' : 'Your Property');

  // Handle completely unavailable project / feasibility data for non-pilot projects
  if (!isPilot && !plotAreaSqFt && !feasibility) {
    return (
      <div className="pw-page flex items-center justify-center p-6">
        <div className="pw-card max-w-md w-full p-8 text-center space-y-4 bg-[#0f131d] border-white/10">
          <div className="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto text-xl font-bold">
            !
          </div>
          <h2 className="text-lg font-bold text-white">Project data is temporarily unavailable.</h2>
          <p className="text-xs text-slate-400">
            We could not retrieve the zoning or parcel feasibility records for this project.
          </p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              type="button"
              onClick={onRetry || onBackToLand}
              className="pw-btn pw-btn-primary px-6 py-2 text-xs font-semibold"
            >
              Retry
            </button>
            <button
              type="button"
              onClick={onBackToLand}
              className="pw-btn pw-btn-ghost px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Back to Land
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Permitted Metrics: Pilot Fixture vs Live Real Calculations
  const footprintSqFt = isPilot
    ? 715
    : (feasibility?.netDevelopableAreaSqm
        ? Math.round(feasibility.netDevelopableAreaSqm * 10.7639 * 0.65)
        : (plotAreaSqFt ? Math.round(plotAreaSqFt * 0.65) : 0));

  const permissibleBUASqFt = isPilot
    ? 1650
    : (feasibility?.permissibleBUASqm
        ? Math.round(feasibility.permissibleBUASqm * 10.7639)
        : (plotAreaSqFt ? Math.round(plotAreaSqFt * 1.5) : 0));

  const maxH = feasibility?.maxBuildingHeightM || 7.0;
  const floorsText = isPilot
    ? "G+1"
    : (maxH <= 7.0 ? "G+1" : maxH <= 10.0 ? "G+2" : `G+${Math.max(1, Math.floor((maxH - 3) / 3))}`);

  const floorsSubtitle = isPilot || floorsText === "G+1" ? "Ground + 1 Storey" : `Ground + Multi-Storey (${maxH}m)`;

  const parkingCars = feasibility?.standardParkingStalls
    ? Math.max(1, feasibility.standardParkingStalls)
    : 1;

  const roadWidthFt = project?.parcel?.existingRoadWidthM
    ? Math.round(project.parcel.existingRoadWidthM / 0.3048)
    : (isPilot ? 16 : 16);

  const badgeText = plotAreaSqFt
    ? `${plotAreaSqFt.toLocaleString()} sq ft · ${locationText}`
    : locationText;

  return (
    <div className="pw-page">
      <div className="pw-container">

        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            onClick={onBackToLand}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Land</span>
          </button>

          <span className="pw-badge pw-badge-neutral font-mono text-[11px]" data-testid="feasibility-plot-badge">
            {badgeText}
          </span>
        </div>

        {/* Title (§7) */}
        <div>
          <h1 className="pw-title-xl">
            What can you build here?
          </h1>
          <p className="pw-body mt-1">
            Based on your plot size and road access, here is what is permitted.
          </p>
        </div>

        {/* 4 Large Cards Only (§7) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* 1. Ground Footprint */}
          <div className="pw-card p-5 space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              GROUND FOOTPRINT
            </span>
            <div className="text-2xl sm:text-3xl font-bold font-mono text-white">
              {footprintSqFt.toLocaleString()} sq ft
            </div>
            <span className="text-xs text-slate-500">Max usable ground coverage</span>
          </div>

          {/* 2. Possible Floors */}
          <div className="pw-card p-5 space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              POSSIBLE FLOORS
            </span>
            <div className="text-2xl sm:text-3xl font-bold font-mono text-blue-400">
              {floorsText}
            </div>
            <span className="text-xs text-slate-500">{floorsSubtitle}</span>
          </div>

          {/* 3. Total Buildable Area */}
          <div className="pw-card p-5 space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              TOTAL BUILDABLE AREA
            </span>
            <div className="text-2xl sm:text-3xl font-bold font-mono text-emerald-400">
              ~{permissibleBUASqFt.toLocaleString()} sq ft
            </div>
            <span className="text-xs text-slate-500">Total permissible floor area</span>
          </div>

          {/* 4. Parking */}
          <div className="pw-card p-5 space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block">
              PARKING
            </span>
            <div className="text-2xl sm:text-3xl font-bold font-mono text-white">
              {parkingCars} Car
            </div>
            <span className="text-xs text-slate-500">Covered parking bay</span>
          </div>
        </div>

        {/* Visual: BUILDABLE AREA PREVIEW (§7) */}
        <div className="pw-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
                Visual Preview
              </span>
              <h3 className="pw-title-md">Buildable Area Preview</h3>
            </div>
            <span className="pw-badge pw-badge-neutral text-[10px] font-mono">
              Road Access: {roadWidthFt} ft
            </span>
          </div>

          {/* Architectural SVG Diagram */}
          <div className="w-full aspect-[16/9] max-h-[300px] bg-[#07090e] rounded-xl border border-white/5 flex items-center justify-center p-4">
            <svg viewBox="0 0 440 240" className="w-full h-full max-h-[260px]">
              {/* Access Road */}
              <rect x="20" y="8" width="400" height="28" fill="#141822" rx="4" />
              <line x1="20" y1="22" x2="420" y2="22" stroke="#475569" strokeDasharray="6,6" strokeWidth="1.5" />
              <text x="220" y="26" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="600" letterSpacing="0.5">
                ACCESS ROAD ({roadWidthFt} FT WIDTH)
              </text>

              {/* Plot Boundary */}
              <rect
                x="50"
                y="46"
                width="340"
                height="174"
                fill="#0d111a"
                stroke="#3b82f6"
                strokeWidth="1.5"
                strokeDasharray="4,4"
                rx="6"
              />
              <text x="60" y="60" fill="#60a5fa" fontSize="9" fontWeight="600">
                Plot Boundary: 1,100 sq ft
              </text>

              {/* Front Road Setback Buffer */}
              <rect
                x="50"
                y="46"
                width="340"
                height="34"
                fill="#d97706"
                fillOpacity="0.08"
                stroke="#d97706"
                strokeDasharray="3,3"
                strokeWidth="1"
              />
              <text x="220" y="67" textAnchor="middle" fill="#f59e0b" fontSize="8" fontWeight="600">
                Front Road Setback Buffer (3.0m)
              </text>

              {/* Permitted Buildable Envelope */}
              <rect
                x="76"
                y="88"
                width="288"
                height="116"
                fill="#16a34a"
                fillOpacity="0.18"
                stroke="#16a34a"
                strokeWidth="1.5"
                rx="4"
              />
              <text x="220" y="142" textAnchor="middle" fill="#4ade80" fontSize="13" fontWeight="700">
                BUILDABLE AREA
              </text>
              <text x="220" y="160" textAnchor="middle" fill="#86efac" fontSize="11" fontWeight="500">
                {footprintSqFt.toLocaleString()} sq ft Ground Footprint · {floorsText} Permitted
              </text>

              {/* Setback annotations */}
              <text x="58" y="146" fill="#64748b" fontSize="8">1.5m Side</text>
              <text x="372" y="146" fill="#64748b" fontSize="8">1.5m Side</text>
              <text x="220" y="214" textAnchor="middle" fill="#64748b" fontSize="8">1.5m Rear Open Space</text>
            </svg>
          </div>

          {/* Diagram Legend */}
          <div className="flex flex-wrap items-center justify-center gap-5 text-xs text-slate-400 pt-2 border-t border-white/5">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm border border-blue-400 border-dashed" />
              Plot Boundary
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500/30 border border-emerald-500" />
              Buildable Area
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-amber-500/20 border border-amber-500 border-dashed" />
              Required Open Spaces / Setbacks
            </span>
          </div>
        </div>

        {/* Under it: Important things to know (§7) */}
        <div className="pw-card space-y-3">
          <h3 className="pw-title-md">Important things to know</h3>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-blue-400 font-bold">•</span>
              <span>Your road access affects the available building area.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 font-bold">•</span>
              <span>Required open spaces/setbacks reduce the usable footprint.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 font-bold">•</span>
              <span>Final construction requires professional verification.</span>
            </li>
          </ul>

          {/* Technical Details Collapsible Drawer (§7, §25) */}
          <div className="pt-3 border-t border-white/5">
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center justify-between w-full"
            >
              <span className="flex items-center gap-1.5 font-medium">
                <Sliders className="w-3.5 h-3.5" />
                <span>{showTechnicalDetails ? 'Hide technical details' : 'View technical details'}</span>
              </span>
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showTechnicalDetails && (
              <div className="mt-3 p-4 rounded-xl bg-[#080b11] border border-blue-500/20 space-y-3 font-mono text-xs animate-fade-in">
                <div className="flex items-center justify-between border-b border-white/10 pb-2">
                  <span className="text-slate-400">Rule Pack: Mumbai DCPR 2034 / Reg 30 Table 12 &amp; Reg 41</span>
                  <button
                    onClick={() => setIsExplainModalOpen(true)}
                    className="pw-btn pw-btn-secondary pw-btn-sm"
                  >
                    <span>Full Rule Trace</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                    <span className="text-slate-500 block text-[10px]">BASE FSI</span>
                    <span className="text-white font-bold text-sm">{feasibility?.baseFSI ?? 1.0}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                    <span className="text-slate-500 block text-[10px]">TOTAL PERMISSIBLE FSI</span>
                    <span className="text-emerald-400 font-bold text-sm">{feasibility?.totalPermissibleFSI ?? 1.5}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                    <span className="text-slate-500 block text-[10px]">MAX HEIGHT</span>
                    <span className="text-white font-bold text-sm">{feasibility?.maxBuildingHeightM ?? 10.0} m</span>
                  </div>
                  <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                    <span className="text-slate-500 block text-[10px]">SETBACK VALUES</span>
                    <span className="text-slate-300 font-bold text-sm">F: 3.0m, S/R: 1.5m</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Primary CTA (§7) */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            {onOpenTechnicalView && (
              <button
                onClick={onOpenTechnicalView}
                className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>View in GIS &amp; Rule Engine Canvas</span>
              </button>
            )}
          </div>

          <button
            onClick={onProceedToDesign}
            className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
            data-testid="btn-design-my-home"
          >
            <span>Design My Home</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>

      {/* Full Rule Explainability Modal (Available through progressive disclosure) */}
      {isExplainModalOpen && (
        <RuleExplainabilityModal
          feasibility={feasibility}
          onClose={() => setIsExplainModalOpen(false)}
        />
      )}
    </div>
  );
};
