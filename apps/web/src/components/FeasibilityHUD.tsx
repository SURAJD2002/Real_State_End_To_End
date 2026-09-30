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
  ShieldCheck
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
  const [activeTab, setActiveTab] = useState<'METRICS' | 'FINANCIALS'>('METRICS');
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!feasibility) {
    return (
      <aside className="absolute right-4 top-20 z-20 w-80 glass-panel p-4 flex flex-col items-center justify-center text-center">
        <Building className="w-8 h-8 text-slate-500 mb-2" />
        <h3 className="font-display font-semibold text-sm text-slate-200">Awaiting Parcel Digitization</h3>
        <p className="text-xs text-slate-400 mt-1">
          Draw a parcel polygon on the map or click <strong className="text-blue-400">Load Golden Benchmark</strong> to run Mumbai DCPR 2034 feasibility.
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
    <aside className="absolute right-4 top-20 z-20 w-96 glass-panel overflow-hidden transition-all duration-300">
      {/* HUD Header */}
      <div className="p-3.5 bg-slate-900/80 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-blue-600/30 border border-blue-500/40 flex items-center justify-center">
            <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div>
            <h2 className="font-display font-bold text-xs text-white uppercase tracking-wider">
              Feasibility Intelligence HUD
            </h2>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
              <span className="text-emerald-400 font-mono font-medium">DCPR 2034 Verified</span>
              <span>•</span>
              <span className="font-mono">{cadastralNumber}</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-slate-400 hover:text-white transition-colors"
        >
          {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {!isCollapsed && (
        <div className="p-3.5 space-y-4 max-h-[calc(100vh-140px)] overflow-y-auto">
          {/* Tabs */}
          <div className="flex rounded-lg bg-slate-950/60 p-1 border border-white/5">
            <button
              onClick={() => setActiveTab('METRICS')}
              className={`flex-1 py-1 text-xs font-medium rounded-md transition-all ${
                activeTab === 'METRICS'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Statutory Potential
            </button>
            <button
              onClick={() => setActiveTab('FINANCIALS')}
              className={`flex-1 py-1 text-xs font-medium rounded-md transition-all ${
                activeTab === 'FINANCIALS'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Pro-Forma Returns
            </button>
          </div>

          {activeTab === 'METRICS' ? (
            <>
              {/* Spatial Balance Sheet Card */}
              <div className="rounded-lg bg-slate-900/60 p-3 border border-white/5 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-300 font-semibold border-b border-white/5 pb-1.5">
                  <div className="flex items-center gap-1.5">
                    <Ruler className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Spatial Deductions</span>
                  </div>
                  <span className="font-mono text-cyan-400">UTM 43N</span>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Gross Plot Area</span>
                    <span className="font-mono font-bold text-slate-100">
                      {feasibility.grossPlotAreaSqm.toLocaleString()} m²
                    </span>
                    <span className="text-[10px] text-slate-500 block">({toSqFt(feasibility.grossPlotAreaSqm)} sqft)</span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[10px]">Road Widening</span>
                    <span className="font-mono font-bold text-rose-400">
                      -{feasibility.roadWideningDeductionSqm.toLocaleString()} m²
                    </span>
                    <span className="text-[10px] text-slate-500 block">Ded. for DP Road</span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[10px]">Amenity (POS)</span>
                    <span className="font-mono font-bold text-amber-400">
                      -{feasibility.amenityReservationSqm.toLocaleString()} m²
                    </span>
                    <span className="text-[10px] text-slate-500 block">Open Space Quota</span>
                  </div>

                  <div>
                    <span className="text-slate-400 block text-[10px]">Net Developable Area</span>
                    <span className="font-mono font-bold text-emerald-400 text-xs">
                      {feasibility.netDevelopableAreaSqm.toLocaleString()} m²
                    </span>
                    <span className="text-[10px] text-emerald-500/80 block">100% Net Footprint</span>
                  </div>
                </div>
              </div>

              {/* FSI & BUA Allocation Card */}
              <div className="rounded-lg bg-gradient-to-br from-slate-900/80 to-slate-950/80 p-3 border border-white/5 space-y-2.5">
                <div className="flex items-center justify-between text-xs text-slate-300 font-semibold border-b border-white/5 pb-1.5">
                  <div className="flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-blue-400" />
                    <span>Statutory FSI Allocation</span>
                  </div>
                  <span className="text-[11px] font-mono font-bold text-blue-400">
                    FSI {feasibility.totalPermissibleFSI.toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-400 text-[11px]">Base FSI:</span>
                  <span className="font-mono text-slate-200">{feasibility.baseFSI.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-400 text-[11px]">Premium FSI (Govt. Purchase):</span>
                  <span className="font-mono text-blue-300">+{feasibility.premiumFSI.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between text-xs py-1">
                  <span className="text-slate-400 text-[11px]">TDR Utilization (DCPR 33):</span>
                  <span className="font-mono text-cyan-300">+{feasibility.tdrFSI.toFixed(2)}</span>
                </div>

                <div className="pt-2 border-t border-white/10 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Permissible BUA</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {feasibility.permissibleBUASqm.toLocaleString()} m²
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Max Height</span>
                    <span className="font-mono font-bold text-cyan-400 text-sm">
                      {feasibility.maxBuildingHeightM} m
                    </span>
                  </div>
                </div>
              </div>

              {/* Parking Allocation */}
              <div className="rounded-lg bg-slate-900/60 p-2.5 border border-white/5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Car className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-300 text-[11px]">Required Stalls (Podium):</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="text-slate-100 font-bold">{feasibility.standardParkingStalls} Standard</span>
                  <span className="text-slate-500">|</span>
                  <span className="text-blue-400">{feasibility.accessibleParkingStalls} ADA</span>
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Financial Underwriting Overview */}
              <div className="rounded-lg bg-gradient-to-br from-blue-950/40 to-slate-900/80 p-3 border border-blue-500/20 space-y-3">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                  <div className="flex items-center gap-1.5">
                    <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Underwriting Summary</span>
                  </div>
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                    IRR: {feasibility.financials.equityIRRPercent}%
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-900/70 p-2 rounded-md border border-white/5">
                    <span className="text-[10px] text-slate-400 block">Gross Dev. Value (GDV)</span>
                    <span className="font-mono font-bold text-white text-xs">
                      {formatINR(feasibility.financials.grossDevelopmentValue)}
                    </span>
                  </div>

                  <div className="bg-slate-900/70 p-2 rounded-md border border-white/5">
                    <span className="text-[10px] text-slate-400 block">Total Dev. Cost (TDC)</span>
                    <span className="font-mono font-bold text-rose-300 text-xs">
                      {formatINR(feasibility.financials.totalDevelopmentCost)}
                    </span>
                  </div>
                </div>

                <div className="bg-emerald-950/30 p-2.5 rounded-md border border-emerald-800/30 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-emerald-300/80 block uppercase">Projected Net Profit</span>
                    <span className="font-mono font-bold text-emerald-400 text-sm">
                      {formatINR(feasibility.financials.netMarginValue)}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block uppercase">Developer Margin</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {feasibility.financials.netMarginPercent}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Cost Stack Breakdown */}
              <div className="rounded-lg bg-slate-900/60 p-3 border border-white/5 space-y-2 text-[11px]">
                <div className="flex items-center gap-1.5 text-xs text-slate-300 font-semibold border-b border-white/5 pb-1.5">
                  <Coins className="w-3.5 h-3.5 text-amber-400" />
                  <span>Cost Stack Decomposition</span>
                </div>

                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Civil & Structural Works:</span>
                  <span className="font-mono text-slate-200">{formatINR(feasibility.financials.civilConstructionCost)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Statutory Municipal Premiums:</span>
                  <span className="font-mono text-amber-300">{formatINR(feasibility.financials.statutoryApprovalPremiums)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Financing & Debt Service:</span>
                  <span className="font-mono text-slate-300">{formatINR(feasibility.financials.financingCost)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Soft Costs & Marketing (7%):</span>
                  <span className="font-mono text-slate-300">{formatINR(feasibility.financials.softCostsAndMarketing)}</span>
                </div>
              </div>
            </>
          )}

          {/* Statutory Verification Footnote */}
          <div className="text-[10px] text-slate-500 flex items-start gap-1.5 pt-1">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
            <span>
              Calculations derived deterministically using UTM 32643 metric projections and Mumbai MCGM DCPR 2034 Statutory Rules.
            </span>
          </div>
        </div>
      )}
    </aside>
  );
};
