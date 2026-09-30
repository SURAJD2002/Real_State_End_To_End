import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Ruler, 
  Car, 
  Building, 
  Coins, 
  ChevronRight, 
  ChevronDown, 
  ShieldCheck, 
  HelpCircle,
  CheckCircle2
} from 'lucide-react';
import { FeasibilityResult } from '../types';

interface FeasibilityHUDProps {
  feasibility: FeasibilityResult | null;
  cadastralNumber: string;
}

export const FeasibilityHUD: React.FC<FeasibilityHUDProps> = ({
  feasibility,
  cadastralNumber
}) => {
  const [activeTab, setActiveTab] = useState<'STATUTORY' | 'FINANCIALS'>('STATUTORY');
  const [isWhyFSIShown, setIsWhyFSIShown] = useState<boolean>(false);
  const [isWhyDeductionShown, setIsWhyDeductionShown] = useState<boolean>(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!feasibility) {
    return (
      <aside className="w-80 glass-panel p-4 flex flex-col items-center justify-center text-center select-none">
        <Building className="w-8 h-8 text-slate-500 mb-2" />
        <h3 className="font-display font-semibold text-xs text-slate-200">Awaiting Parcel Digitization</h3>
        <p className="text-[11px] text-slate-400 mt-1 leading-normal">
          Draw a parcel polygon on the map or click <strong className="text-blue-400">Load Benchmark</strong> to run Mumbai DCPR 2034 feasibility.
        </p>
      </aside>
    );
  }

  const formatINR = (val: number) => {
    const inCrores = val / 10000000;
    return `₹${inCrores.toFixed(2)} Cr`;
  };

  const toSqFt = (sqm: number) => {
    return (sqm * 10.7639).toLocaleString(undefined, { maximumFractionDigits: 0 });
  };

  return (
    <aside className="w-80 glass-panel overflow-hidden transition-all duration-300 select-none flex flex-col h-full">
      {/* Header */}
      <div className="p-3 bg-slate-900/90 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-blue-600/30 border border-blue-500/40 flex items-center justify-center">
            <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div>
            <h2 className="font-display font-bold text-xs text-white uppercase tracking-wider">
              Feasibility Intelligence
            </h2>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
              <span className="text-emerald-400 font-bold flex items-center gap-0.5">
                <CheckCircle2 className="w-3 h-3" />
                VERIFIED FEASIBLE
              </span>
              <span>•</span>
              <span>{cadastralNumber}</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-slate-400 hover:text-white p-1"
        >
          {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {!isCollapsed && (
        <div className="p-3 space-y-3 overflow-y-auto flex-1 text-xs">
          {/* Tabs */}
          <div className="flex rounded-lg bg-slate-950 p-1 border border-white/10">
            <button
              onClick={() => setActiveTab('STATUTORY')}
              className={`flex-1 py-1 text-[11px] font-semibold rounded-md transition-all ${
                activeTab === 'STATUTORY'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Statutory Potential
            </button>
            <button
              onClick={() => setActiveTab('FINANCIALS')}
              className={`flex-1 py-1 text-[11px] font-semibold rounded-md transition-all ${
                activeTab === 'FINANCIALS'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Pro-Forma Returns
            </button>
          </div>

          {activeTab === 'STATUTORY' ? (
            <>
              {/* Primary Spatial Metrics */}
              <div className="rounded-lg bg-slate-900/80 p-2.5 border border-white/5 space-y-2">
                <div className="flex items-center justify-between border-b border-white/5 pb-1 text-[11px] font-semibold text-slate-300">
                  <div className="flex items-center gap-1 text-cyan-400">
                    <Ruler className="w-3.5 h-3.5" />
                    <span>Spatial Deductions</span>
                  </div>
                  <button
                    onClick={() => setIsWhyDeductionShown(!isWhyDeductionShown)}
                    className="flex items-center gap-0.5 text-[10px] text-blue-400 hover:text-blue-300"
                  >
                    <HelpCircle className="w-3 h-3" />
                    <span>Why?</span>
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div>
                    <span className="text-slate-500 text-[9px] block uppercase">Gross Plot Area</span>
                    <span className="font-bold text-white text-xs">{feasibility.grossPlotAreaSqm.toLocaleString()} m²</span>
                    <span className="text-[9px] text-slate-500 block font-sans">({toSqFt(feasibility.grossPlotAreaSqm)} sqft)</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[9px] block uppercase">Road Widening</span>
                    <span className="font-bold text-rose-400 text-xs">-{feasibility.roadWideningDeductionSqm} m²</span>
                    <span className="text-[9px] text-slate-500 block font-sans">DP Road Reserve</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[9px] block uppercase">Amenity (POS)</span>
                    <span className="font-bold text-amber-400 text-xs">-{feasibility.amenityReservationSqm} m²</span>
                    <span className="text-[9px] text-slate-500 block font-sans">15% Open Space</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[9px] block uppercase">Net Developable</span>
                    <span className="font-bold text-emerald-400 text-xs">{feasibility.netDevelopableAreaSqm.toLocaleString()} m²</span>
                    <span className="text-[9px] text-emerald-500 block font-sans">100% Net Footprint</span>
                  </div>
                </div>

                {isWhyDeductionShown && (
                  <div className="p-2 rounded bg-slate-950 border border-white/5 text-[10px] text-slate-300 space-y-1 font-sans leading-normal">
                    <div>• <strong>Road Widening:</strong> Frontage length × (18m proposed - 12m existing)/2 per MCGM DP Road.</div>
                    <div>• <strong>POS Amenity Quota:</strong> Plots &gt;4,000 m² mandate 15% open space surrendered to authority under DCPR Reg 41.</div>
                  </div>
                )}
              </div>

              {/* FSI & BUA Breakdown */}
              <div className="rounded-lg bg-slate-900/80 p-2.5 border border-white/5 space-y-2">
                <div className="flex items-center justify-between border-b border-white/5 pb-1 text-[11px] font-semibold text-slate-300">
                  <div className="flex items-center gap-1 text-blue-400">
                    <Building className="w-3.5 h-3.5" />
                    <span>Statutory FSI = {feasibility.totalPermissibleFSI.toFixed(2)}</span>
                  </div>
                  <button
                    onClick={() => setIsWhyFSIShown(!isWhyFSIShown)}
                    className="flex items-center gap-0.5 text-[10px] text-blue-400 hover:text-blue-300"
                  >
                    <HelpCircle className="w-3 h-3" />
                    <span>Why?</span>
                  </button>
                </div>

                <div className="space-y-1 text-[11px] font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Base FSI:</span>
                    <span className="text-slate-200">{feasibility.baseFSI.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Premium FSI:</span>
                    <span className="text-blue-300">+{feasibility.premiumFSI.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>TDR Allowance:</span>
                    <span className="text-cyan-300">+{feasibility.tdrFSI.toFixed(2)}</span>
                  </div>
                </div>

                {isWhyFSIShown && (
                  <div className="p-2 rounded bg-slate-950 border border-white/5 text-[10px] text-slate-300 space-y-1 font-sans leading-normal">
                    <div>• <strong>Base FSI (1.0):</strong> Statutory baseline for Greater Mumbai Suburban R2 Zone.</div>
                    <div>• <strong>Premium FSI (0.5):</strong> Purchasable at 50% Ready Reckoner rate per Reg 30.</div>
                    <div>• <strong>TDR FSI (1.0):</strong> Transferable rights allowed on roads ≥18.0m width.</div>
                  </div>
                )}

                <div className="pt-2 border-t border-white/5 flex items-center justify-between">
                  <div>
                    <span className="text-[9px] text-slate-500 uppercase font-mono block">Permissible BUA</span>
                    <span className="font-mono font-bold text-white text-xs">
                      {feasibility.permissibleBUASqm.toLocaleString()} m²
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] text-slate-500 uppercase font-mono block">Max Height Cap</span>
                    <span className="font-mono font-bold text-cyan-400 text-xs">
                      {feasibility.maxBuildingHeightM} m (Road &ge;18m)
                    </span>
                  </div>
                </div>
              </div>

              {/* Parking Quota */}
              <div className="rounded-lg bg-slate-900/80 p-2 border border-white/5 flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-300">
                  <Car className="w-3.5 h-3.5 text-slate-400" />
                  <span>Required Stalls:</span>
                </div>
                <span className="font-mono text-white font-bold">
                  {feasibility.standardParkingStalls} Std <span className="text-slate-500">|</span> <span className="text-cyan-400">{feasibility.accessibleParkingStalls} ADA</span>
                </span>
              </div>
            </>
          ) : (
            <>
              {/* Financial Underwriting */}
              <div className="rounded-lg bg-slate-900/80 p-2.5 border border-blue-500/20 space-y-2">
                <div className="flex items-center justify-between border-b border-white/5 pb-1 text-[11px] font-semibold text-slate-200">
                  <div className="flex items-center gap-1 text-emerald-400">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Capital Underwriting</span>
                  </div>
                  <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                    IRR: {feasibility.financials.equityIRRPercent}%
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div className="bg-slate-950 p-1.5 rounded">
                    <span className="text-[9px] text-slate-500 block uppercase">GDV (Revenue)</span>
                    <span className="font-bold text-white text-xs">{formatINR(feasibility.financials.grossDevelopmentValue)}</span>
                  </div>
                  <div className="bg-slate-950 p-1.5 rounded">
                    <span className="text-[9px] text-slate-500 block uppercase">Total Dev Cost</span>
                    <span className="font-bold text-rose-300 text-xs">{formatINR(feasibility.financials.totalDevelopmentCost)}</span>
                  </div>
                </div>

                <div className="bg-emerald-950/40 p-2 rounded flex items-center justify-between font-mono">
                  <div>
                    <span className="text-[9px] text-emerald-400/80 uppercase block">Net Margin</span>
                    <span className="font-bold text-emerald-400 text-xs">{formatINR(feasibility.financials.netMarginValue)}</span>
                  </div>
                  <span className="text-xs font-bold text-white">{feasibility.financials.netMarginPercent}%</span>
                </div>
              </div>

              {/* Cost Decomposition */}
              <div className="rounded-lg bg-slate-900/80 p-2.5 border border-white/5 space-y-1.5 text-[11px]">
                <div className="flex items-center gap-1 text-amber-400 font-semibold border-b border-white/5 pb-1">
                  <Coins className="w-3.5 h-3.5" />
                  <span>Cost Stack Decomposition</span>
                </div>
                <div className="flex justify-between py-0.5 text-slate-400 font-mono">
                  <span>Civil Works:</span>
                  <span className="text-slate-200">{formatINR(feasibility.financials.civilConstructionCost)}</span>
                </div>
                <div className="flex justify-between py-0.5 text-slate-400 font-mono">
                  <span>Municipal Premiums:</span>
                  <span className="text-amber-300">{formatINR(feasibility.financials.statutoryApprovalPremiums)}</span>
                </div>
                <div className="flex justify-between py-0.5 text-slate-400 font-mono">
                  <span>Financing & Debt:</span>
                  <span className="text-slate-300">{formatINR(feasibility.financials.financingCost)}</span>
                </div>
                <div className="flex justify-between py-0.5 text-slate-400 font-mono">
                  <span>Soft Costs (7%):</span>
                  <span className="text-slate-300">{formatINR(feasibility.financials.softCostsAndMarketing)}</span>
                </div>
              </div>
            </>
          )}

          {/* Statutory Verification Footnote */}
          <div className="p-2 rounded bg-slate-950/90 border border-white/5 flex items-start gap-1.5 text-[10px] text-slate-400 leading-normal">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
            <span>
              <strong>Rule Check — Review Required:</strong> Calculations derived deterministically under Mumbai DCPR 2034. Requires licensed architect sign-off before municipal submission.
            </span>
          </div>
        </div>
      )}
    </aside>
  );
};
