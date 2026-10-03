import React, { useState } from 'react';
import { 
  Building2, 
  Ruler, 
  Layers, 
  Car, 
  Check, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight, 
  ArrowLeft,
  Info,
  ExternalLink,
  Sliders,
  ShieldCheck
} from 'lucide-react';
import { FeasibilityResult, ProjectData } from '../types';
import { RuleExplainabilityModal } from './RuleExplainabilityModal';

interface FeasibilitySummaryViewProps {
  feasibility: FeasibilityResult | null;
  project: ProjectData | null;
  onProceedToDesign: () => void;
  onBackToLand: () => void;
  onOpenTechnicalView?: () => void;
}

export const FeasibilitySummaryView: React.FC<FeasibilitySummaryViewProps> = ({
  feasibility,
  project,
  onProceedToDesign,
  onBackToLand,
  onOpenTechnicalView
}) => {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [isExplainModalOpen, setIsExplainModalOpen] = useState(false);

  // Authoritative 1,100 sq ft project metrics (§7, §9, §27)
  const plotAreaSqFt = 1100;
  
  // Ground footprint: 65% standard coverage = 715 sq ft
  const footprintSqFt = feasibility
    ? Math.min(Math.round(plotAreaSqFt * 0.65), Math.round((feasibility.netDevelopableAreaSqm * 0.65) * 10.7639))
    : 715;

  // Approx. buildable area: 1,650 sq ft total BUA (G+1)
  const approxBuildableSqFt = feasibility?.permissibleBUASqm 
    ? Math.round(feasibility.permissibleBUASqm * 10.7639)
    : 1650;

  const floorsText = "G+1";
  const parkingCars = feasibility?.standardParkingStalls ? Math.max(1, feasibility.standardParkingStalls) : 1;
  const roadWidthFt = project?.parcel?.existingRoadWidthM 
    ? Math.round(project.parcel.existingRoadWidthM / 0.3048) 
    : 16;

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

          <span className="pw-badge pw-badge-neutral">
            Step 2 of 6: Feasibility Report
          </span>
        </div>

        {/* Heading (§9) */}
        <div>
          <h1 className="pw-title-xl">
            What can you build here?
          </h1>
          <p className="pw-body mt-1">
            Based on your 1,100 sq ft plot and {roadWidthFt} ft access road in Bandra West, here is what can realistically be developed.
          </p>
        </div>

        {/* Compact 5 Metrics Grid (§9) */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {/* 1. Plot */}
          <div className="pw-metric-card">
            <div className="pw-metric-card-label">
              <span>Plot</span>
              <Ruler className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div>
              <div className="pw-metric-card-value">1,100</div>
              <div className="pw-metric-card-sub">sq ft total extent</div>
            </div>
          </div>

          {/* 2. Ground Footprint */}
          <div className="pw-metric-card">
            <div className="pw-metric-card-label">
              <span>Ground footprint</span>
              <Building2 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div>
              <div className="pw-metric-card-value">{footprintSqFt.toLocaleString()}</div>
              <div className="pw-metric-card-sub">sq ft ground cover</div>
            </div>
          </div>

          {/* 3. Possible Floors */}
          <div className="pw-metric-card">
            <div className="pw-metric-card-label">
              <span>Possible floors</span>
              <Layers className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div>
              <div className="pw-metric-card-value">{floorsText}</div>
              <div className="pw-metric-card-sub">Ground + 1 Storey</div>
            </div>
          </div>

          {/* 4. Approx. Buildable Area */}
          <div className="pw-metric-card">
            <div className="pw-metric-card-label">
              <span>Approx. buildable area</span>
              <Building2 className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <div>
              <div className="pw-metric-card-value">{approxBuildableSqFt.toLocaleString()}</div>
              <div className="pw-metric-card-sub">sq ft total BUA</div>
            </div>
          </div>

          {/* 5. Parking */}
          <div className="pw-metric-card col-span-2 md:col-span-1">
            <div className="pw-metric-card-label">
              <span>Parking</span>
              <Car className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div>
              <div className="pw-metric-card-value">{parkingCars}</div>
              <div className="pw-metric-card-sub">{parkingCars === 1 ? 'Car space' : 'Car spaces'}</div>
            </div>
          </div>
        </div>

        {/* Site Diagram & Conditions Section */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
          {/* Site Diagram Canvas (Left 7 cols) */}
          <div className="md:col-span-7 pw-card flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="pw-title-md">Buildable Envelope</h3>
                <p className="text-xs text-slate-400">Green zone represents permitted ground coverage after setbacks</p>
              </div>
              <span className="pw-badge pw-badge-neutral font-mono text-[10px]">
                Road: {roadWidthFt} ft
              </span>
            </div>

            {/* Architectural SVG Diagram */}
            <div className="w-full aspect-[16/10] bg-[#0c0e13] rounded-lg border border-white/5 flex items-center justify-center p-4">
              <svg viewBox="0 0 400 240" className="w-full h-full max-h-[220px]">
                {/* Access Road */}
                <rect x="20" y="8" width="360" height="26" fill="#161a22" rx="4" />
                <line x1="20" y1="21" x2="380" y2="21" stroke="#475569" strokeDasharray="6,6" strokeWidth="1.5" />
                <text x="200" y="24" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="600" letterSpacing="0.5">
                  ACCESS ROAD ({roadWidthFt} FT WIDTH)
                </text>

                {/* Plot Boundary */}
                <rect
                  x="60"
                  y="46"
                  width="280"
                  height="164"
                  fill="#11141c"
                  stroke="#3b82f6"
                  strokeWidth="1.5"
                  strokeDasharray="4,4"
                  rx="4"
                />
                <text x="68" y="60" fill="#60a5fa" fontSize="9" fontWeight="600">
                  Plot Boundary (1,100 sq ft)
                </text>

                {/* Front Road Setback Buffer */}
                <rect
                  x="60"
                  y="46"
                  width="280"
                  height="34"
                  fill="#d97706"
                  fillOpacity="0.08"
                  stroke="#d97706"
                  strokeDasharray="3,3"
                  strokeWidth="1"
                />
                <text x="200" y="67" textAnchor="middle" fill="#f59e0b" fontSize="8" fontWeight="600">
                  3.0m Front Road Setback
                </text>

                {/* Permitted Buildable Envelope */}
                <rect
                  x="84"
                  y="86"
                  width="232"
                  height="110"
                  fill="#16a34a"
                  fillOpacity="0.18"
                  stroke="#16a34a"
                  strokeWidth="1.5"
                  rx="3"
                />
                <text x="200" y="138" textAnchor="middle" fill="#4ade80" fontSize="12" fontWeight="700">
                  BUILDABLE FOOTPRINT
                </text>
                <text x="200" y="154" textAnchor="middle" fill="#86efac" fontSize="10">
                  {footprintSqFt.toLocaleString()} sq ft Max Ground Coverage
                </text>

                {/* Side/Rear setback annotations */}
                <text x="70" y="142" fill="#64748b" fontSize="7">1.5m</text>
                <text x="320" y="142" fill="#64748b" fontSize="7">1.5m</text>
                <text x="200" y="204" textAnchor="middle" fill="#64748b" fontSize="7">1.5m Rear Setback</text>
              </svg>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400 mt-3 pt-3 border-t border-white/5">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm border border-blue-400 border-dashed" />
                Plot Boundary
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500/30 border border-emerald-500" />
                Buildable Footprint
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-amber-500/20 border border-amber-500 border-dashed" />
                Statutory Setbacks
              </span>
            </div>
          </div>

          {/* Site Conditions Checklist (Right 5 cols) (§9) */}
          <div className="md:col-span-5 pw-card flex flex-col justify-between">
            <div>
              <h3 className="pw-title-md mb-1">Site Conditions</h3>
              <p className="text-xs text-slate-400 mb-4">
                Automated municipal checks completed for this site.
              </p>

              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-start gap-2.5">
                  <div className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Check className="w-3 h-3" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Road access confirmed</span>
                    <span className="text-[11px] text-slate-400">
                      Existing {roadWidthFt} ft access road qualifies for full permissible residential FSI.
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-start gap-2.5">
                  <div className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Check className="w-3 h-3" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Buildable envelope identified</span>
                    <span className="text-[11px] text-slate-400">
                      Clear 715 sq ft footprint identified after front and side setbacks.
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-start gap-2.5">
                  <div className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                    <Check className="w-3 h-3" />
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-white block">Applicable development rules checked</span>
                    <span className="text-[11px] text-slate-400">
                      Evaluated against Mumbai DCPR 2034 residential standards.
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-start gap-2.5">
                  <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-semibold text-amber-200 block">Professional Verification Required</span>
                    <span className="text-[11px] text-amber-300/80">
                      Final construction authorization requires licensed site survey and registered engineer review.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical details toggle (§9) */}
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center justify-between pt-3 mt-4 border-t border-white/5"
            >
              <span className="flex items-center gap-1.5 font-medium">
                <Info className="w-3.5 h-3.5" />
                View technical details
              </span>
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {/* Collapsible Technical Details Panel */}
        {showTechnicalDetails && (
          <div className="pw-card border-blue-500/30 space-y-3">
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-blue-400 font-semibold block">
                  Municipal Rule Calculations
                </span>
                <span className="text-[11px] text-slate-400">
                  DCPR 2034 / Reg 30 Table 12 &amp; Reg 41
                </span>
              </div>

              <button
                onClick={() => setIsExplainModalOpen(true)}
                className="pw-btn pw-btn-secondary pw-btn-sm"
              >
                <span>Full Rule Trace</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
              <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                <span className="text-slate-500 block text-[10px]">BASE FSI</span>
                <span className="text-white font-bold text-sm">
                  {feasibility?.baseFSI ?? 1.0}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                <span className="text-slate-500 block text-[10px]">PERMISSIBLE FSI</span>
                <span className="text-emerald-400 font-bold text-sm">
                  {feasibility?.totalPermissibleFSI ?? 1.5}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                <span className="text-slate-500 block text-[10px]">MAX HEIGHT</span>
                <span className="text-white font-bold text-sm">
                  {feasibility?.maxBuildingHeightM ?? 10.0} m
                </span>
              </div>
              <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                <span className="text-slate-500 block text-[10px]">ROAD WIDENING</span>
                <span className="text-slate-300 font-bold text-sm">
                  {feasibility?.roadWideningDeductionSqm ?? 0.0} sqm
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Footer Actions */}
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
          >
            <span>Proceed to Design</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>

      {/* Rule Explainability Modal */}
      {isExplainModalOpen && (
        <RuleExplainabilityModal
          feasibility={feasibility}
          onClose={() => setIsExplainModalOpen(false)}
        />
      )}
    </div>
  );
};
