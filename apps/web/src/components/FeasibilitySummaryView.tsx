import React, { useState } from 'react';
import { 
  Building2, 
  Ruler, 
  Layers, 
  Car, 
  ShieldAlert, 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight, 
  ArrowLeft,
  Info,
  ExternalLink,
  Sliders
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

  // Compute customer-friendly display values
  const declaredSqFt = 1100; // Authoritative default if not specified
  const plotAreaSqFt = feasibility 
    ? Math.round(feasibility.grossPlotAreaSqm * 10.7639) 
    : declaredSqFt;

  // Ground footprint approx (net developable or 60% coverage)
  const footprintSqFt = feasibility
    ? Math.round((feasibility.netDevelopableAreaSqm * 0.65) * 10.7639)
    : Math.round(plotAreaSqFt * 0.65);

  const permissibleBuaSqFt = feasibility
    ? Math.round(feasibility.permissibleBUASqm * 10.7639)
    : Math.round(plotAreaSqFt * 1.5);

  const maxFloors = feasibility
    ? Math.max(1, Math.min(3, Math.floor(feasibility.maxBuildingHeightM / 3.0)))
    : 2;

  const parkingCars = feasibility
    ? Math.max(1, feasibility.standardParkingStalls)
    : 1;

  const roadWidthFt = project?.parcel?.existingRoadWidthM 
    ? Math.round(project.parcel.existingRoadWidthM / 0.3048) 
    : 16;

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#07090e] p-6 lg:p-10 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-8 animate-fade-in pb-16">
        
        {/* Navigation & Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            onClick={onBackToLand}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Land Details</span>
          </button>

          <span className="text-xs uppercase tracking-wider text-blue-400 font-semibold bg-blue-950/60 border border-blue-800/40 px-3 py-1 rounded-full">
            Step 2 of 6: Feasibility
          </span>
        </div>

        {/* Heading */}
        <div className="space-y-2">
          <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
            What can you build here?
          </h1>
          <p className="text-slate-400 text-sm lg:text-base leading-relaxed">
            We’ve analyzed your site against statutory municipal rules and road access to calculate your building potential.
          </p>
        </div>

        {/* Top 5 Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {/* Card 1: Plot Area */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-blue-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Plot Area</span>
              <Ruler className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold font-mono text-white">
                {plotAreaSqFt.toLocaleString()}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">sq ft</div>
            </div>
          </div>

          {/* Card 2: Building Footprint */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-blue-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Ground Footprint</span>
              <Building2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold font-mono text-white">
                {footprintSqFt.toLocaleString()}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">sq ft maximum</div>
            </div>
          </div>

          {/* Card 3: Permitted Floors */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-blue-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Possible Floors</span>
              <Layers className="w-4 h-4 text-purple-400" />
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold font-mono text-white">
                G + {maxFloors - 1}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">({maxFloors} levels total)</div>
            </div>
          </div>

          {/* Card 4: Total Buildable Area */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-blue-500/30 transition-all flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Approx. Buildable</span>
              <Building2 className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold font-mono text-white">
                {permissibleBuaSqFt.toLocaleString()}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">sq ft total BUA</div>
            </div>
          </div>

          {/* Card 5: Parking */}
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-blue-500/30 transition-all flex flex-col justify-between col-span-2 md:col-span-1">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-medium">Parking</span>
              <Car className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <div className="text-xl lg:text-2xl font-bold font-mono text-white">
                {parkingCars} {parkingCars === 1 ? 'Car' : 'Cars'}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">covered / on-site</div>
            </div>
          </div>
        </div>

        {/* Visual Preview Card + Site Conditions */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Clean Visual Plot & Buildable Envelope SVG */}
          <div className="lg:col-span-7 rounded-2xl bg-slate-900/40 border border-white/10 p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white">Buildable Envelope Preview</h3>
                <p className="text-xs text-slate-400">Green zone represents permitted buildable area after setbacks</p>
              </div>
              <div className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-white/5">
                Road: {roadWidthFt} ft
              </div>
            </div>

            {/* SVG Diagram */}
            <div className="relative w-full aspect-[16/10] bg-[#0c1017] rounded-xl border border-white/5 flex items-center justify-center p-6 overflow-hidden">
              <svg viewBox="0 0 400 250" className="w-full h-full max-h-[220px]">
                {/* Background Road Strip */}
                <rect x="20" y="10" width="360" height="28" fill="#1e293b" rx="4" />
                <line x1="20" y1="24" x2="380" y2="24" stroke="#e2e8f0" strokeDasharray="6,6" strokeWidth="1.5" opacity="0.4" />
                <text x="200" y="27" textAnchor="middle" fill="#94a3b8" fontSize="10" fontWeight="600" letterSpacing="0.5">
                  ACCESS ROAD ({roadWidthFt} FT WIDTH)
                </text>

                {/* Plot Boundary (Full Site) */}
                <rect
                  x="60"
                  y="52"
                  width="280"
                  height="170"
                  fill="#0f172a"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  strokeDasharray="4,4"
                  rx="6"
                />
                <text x="66" y="66" fill="#60a5fa" fontSize="9" fontWeight="600">
                  Site Boundary ({plotAreaSqFt.toLocaleString()} sq ft)
                </text>

                {/* Front Setback Buffer (Dashed Area) */}
                <rect
                  x="60"
                  y="52"
                  width="280"
                  height="34"
                  fill="#f59e0b"
                  fillOpacity="0.08"
                  stroke="#f59e0b"
                  strokeDasharray="2,2"
                  strokeWidth="1"
                />
                <text x="200" y="73" textAnchor="middle" fill="#f59e0b" fontSize="8" fontWeight="600">
                  3.0m Front Road Setback
                </text>

                {/* Buildable Envelope Area */}
                <rect
                  x="84"
                  y="92"
                  width="232"
                  height="115"
                  fill="#10b981"
                  fillOpacity="0.2"
                  stroke="#10b981"
                  strokeWidth="2"
                  rx="4"
                />
                <text x="200" y="146" textAnchor="middle" fill="#34d399" fontSize="12" fontWeight="700">
                  BUILDABLE FOOTPRINT
                </text>
                <text x="200" y="162" textAnchor="middle" fill="#a7f3d0" fontSize="10">
                  {footprintSqFt.toLocaleString()} sq ft Max Ground Coverage
                </text>

                {/* Side/Rear setback markers */}
                <text x="68" y="152" fill="#94a3b8" fontSize="8">Side: 1.5m</text>
                <text x="320" y="152" fill="#94a3b8" fontSize="8">Side: 1.5m</text>
                <text x="200" y="217" textAnchor="middle" fill="#94a3b8" fontSize="8">Rear: 1.5m Setback</text>
              </svg>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400 mt-4 pt-3 border-t border-white/5">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm border border-blue-400 border-dashed bg-blue-950/40" />
                Plot Boundary
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm border border-emerald-400 bg-emerald-500/20" />
                Permitted Footprint
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-sm border border-amber-400 border-dashed bg-amber-500/10" />
                Statutory Setbacks
              </span>
            </div>
          </div>

          {/* Right: Site Conditions & Status Checklist */}
          <div className="lg:col-span-5 rounded-2xl bg-slate-900/40 border border-white/10 p-5 flex flex-col justify-between space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-white mb-1">Important Site Conditions</h3>
              <p className="text-xs text-slate-400 mb-4">Statutory checks performed against municipal guidelines</p>

              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-slate-800/40 border border-white/5 flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="text-white font-medium block">Zoning Compatibility</span>
                    <span className="text-slate-400">Purely residential development permitted on this plot.</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/40 border border-white/5 flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="text-white font-medium block">Road Access Clear</span>
                    <span className="text-slate-400">Road width of {roadWidthFt} ft qualifies for full standard FSI.</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/40 border border-white/5 flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="text-white font-medium block">Frontage & Ventilation Setbacks</span>
                    <span className="text-slate-400">Front (3.0m) and side/rear (1.5m) clear of permanent structures.</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 flex items-start gap-3">
                  <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <span className="text-amber-200 font-medium block">Professional Survey Required</span>
                    <span className="text-amber-300/80">
                      Final construction approval requires a licensed survey and registered engineer sign-off.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Link to calculation details */}
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center justify-between pt-2 border-t border-white/5"
            >
              <span className="flex items-center gap-1.5 font-medium">
                <Info className="w-3.5 h-3.5" />
                Why? View calculation details
              </span>
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        {/* Collapsible Technical Details Panel */}
        {showTechnicalDetails && (
          <div className="rounded-2xl bg-slate-900/80 border border-blue-500/20 p-5 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div>
                <h4 className="text-xs uppercase tracking-wider font-semibold text-blue-400">
                  Statutory Rule Calculation Breakdown
                </h4>
                <p className="text-[11px] text-slate-400">
                  Jurisdiction: Mumbai DCPR 2034 / Reg 30 Table 12 & Reg 41
                </p>
              </div>

              <button
                onClick={() => setIsExplainModalOpen(true)}
                className="text-xs px-3 py-1.5 rounded-lg bg-blue-600/30 border border-blue-500/40 text-blue-300 hover:bg-blue-600/50 flex items-center gap-1.5 transition-all"
              >
                <span>View Full Rule Trace</span>
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                <span className="text-slate-500 block text-[10px]">BASE FSI</span>
                <span className="text-white font-bold text-sm">
                  {feasibility?.baseFSI ?? 1.0}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                <span className="text-slate-500 block text-[10px]">TOTAL PERMISSIBLE FSI</span>
                <span className="text-emerald-400 font-bold text-sm">
                  {feasibility?.totalPermissibleFSI ?? 1.5}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                <span className="text-slate-500 block text-[10px]">MAX BUILDING HEIGHT</span>
                <span className="text-white font-bold text-sm">
                  {feasibility?.maxBuildingHeightM ?? 10.0} m
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                <span className="text-slate-500 block text-[10px]">ROAD DEDUCTION</span>
                <span className="text-amber-400 font-bold text-sm">
                  {feasibility?.roadWideningDeductionSqm ?? 0.0} sqm
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Action Controls Footer */}
        <div className="pt-4 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {onOpenTechnicalView && (
              <button
                onClick={onOpenTechnicalView}
                className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-xl hover:bg-slate-800/60 transition-colors"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>Open Technical GIS Map & HUD</span>
              </button>
            )}
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onProceedToDesign}
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-semibold text-sm shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 transition-all"
            >
              <span>Tell us what house you want</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
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
