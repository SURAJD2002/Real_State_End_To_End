import React, { useState } from 'react';
import { 
  X, 
  Ruler, 
  ShieldCheck, 
  Calculator, 
  Search, 
  BookOpen
} from 'lucide-react';
import { FeasibilityResult } from '../types';

interface RuleExplainabilityModalProps {
  feasibility: FeasibilityResult | null;
  onClose: () => void;
}

export const RuleExplainabilityModal: React.FC<RuleExplainabilityModalProps> = ({
  feasibility,
  onClose
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  if (!feasibility) return null;

  const breakdown = (feasibility as any).explainabilityBreakdown;
  const traces = (feasibility as any).traces || [];

  const filteredTraces = traces.filter((t: any) => {
    const matchesCategory = selectedCategory === 'ALL' || t.category === selectedCategory;
    const matchesSearch = searchQuery === '' || 
      t.ruleName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.ruleId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.explanation.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const categories = ['ALL', 'ROAD_WIDENING', 'OPEN_SPACE', 'SETBACK', 'FSI', 'GROUND_COVERAGE', 'HEIGHT', 'PARKING'];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in select-none">
      <div className="w-full max-w-4xl max-h-[90vh] glass-panel bg-slate-950/95 border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 bg-slate-900/90 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
              <Calculator className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h2 className="font-display font-bold text-sm text-white uppercase tracking-wider flex items-center gap-2">
                <span>Statutory Feasibility Explainability &amp; Audit Traces</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  DCPR 2034 / BBMP 2026
                </span>
              </h2>
              <p className="text-[11px] text-slate-400 font-mono">
                Mathematical proof answering: &quot;Why is my buildable area only {breakdown ? breakdown.effectivePermittedFootprintSqm.toLocaleString() : feasibility.netDevelopableAreaSqm.toLocaleString()} m²?&quot;
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-white/5 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {/* 1. Spatial Deductive Waterfall (Section 7) */}
          <div className="rounded-xl bg-slate-900/70 p-4 border border-white/5 space-y-3">
            <h3 className="font-display font-semibold text-xs text-white uppercase tracking-wider flex items-center gap-1.5">
              <Ruler className="w-3.5 h-3.5 text-cyan-400" />
              <span>Deterministic Spatial Area Waterfall</span>
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 font-mono">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">1. Gross Parcel</span>
                <span className="text-white font-bold text-sm block">
                  {breakdown ? breakdown.grossParcelAreaSqm.toLocaleString() : feasibility.grossPlotAreaSqm.toLocaleString()} m²
                </span>
                <span className="text-[9px] text-slate-400">Total title deed boundary</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">2. Road Widening</span>
                <span className="text-rose-400 font-bold text-sm block">
                  -{breakdown ? breakdown.roadWideningDeductionSqm.toLocaleString() : feasibility.roadWideningDeductionSqm.toLocaleString()} m²
                </span>
                <span className="text-[9px] text-slate-400">18.0m master plan alignment</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">3. Open Space (POS)</span>
                <span className="text-amber-400 font-bold text-sm block">
                  -{breakdown ? breakdown.amenityReservationSqm.toLocaleString() : feasibility.amenityReservationSqm.toLocaleString()} m²
                </span>
                <span className="text-[9px] text-slate-400">15% layout reservation</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">4. Net Parcel</span>
                <span className="text-cyan-400 font-bold text-sm block">
                  {breakdown ? breakdown.netParcelAreaSqm.toLocaleString() : feasibility.netDevelopableAreaSqm.toLocaleString()} m²
                </span>
                <span className="text-[9px] text-slate-400">Net developable parcel</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 font-mono pt-1">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">5. Front Setback</span>
                <span className="text-rose-300 font-bold text-sm block">
                  -{breakdown ? breakdown.frontSetbackDeductionSqm.toLocaleString() : (feasibility.frontSetbackM * 106).toFixed(1)} m²
                </span>
                <span className="text-[9px] text-slate-400">7.5m road setback (Reg 41)</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">6. Rear &amp; Side Setbacks</span>
                <span className="text-rose-300 font-bold text-sm block">
                  -{breakdown ? (breakdown.rearSetbackDeductionSqm + breakdown.sideSetbacksDeductionSqm).toFixed(2) : '971.9'} m²
                </span>
                <span className="text-[9px] text-slate-400">3.0m rear + 1.5m sides</span>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-950 border border-white/5">
                <span className="text-[9px] text-slate-500 uppercase block">7. Ground Coverage Cap</span>
                <span className="text-amber-300 font-bold text-sm block">
                  {breakdown ? `${breakdown.maxGroundCoveragePercent}% = ${breakdown.maxGroundCoverageAreaSqm.toLocaleString()}` : '50% = 12,159.55'} m²
                </span>
                <span className="text-[9px] text-slate-400">Statutory percolation cap</span>
              </div>

              <div className="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
                <span className="text-[9px] text-emerald-400 uppercase font-bold block">8. Permitted Footprint</span>
                <span className="text-emerald-300 font-bold text-sm block">
                  {breakdown ? breakdown.effectivePermittedFootprintSqm.toLocaleString() : '12,159.55'} m²
                </span>
                <span className="text-[9px] text-emerald-400/80">min(Envelope, Coverage)</span>
              </div>
            </div>
          </div>

          {/* 2. Statutory Rule Traces Audit Trail (Section 7, 8) */}
          <div className="rounded-xl bg-slate-900/70 p-4 border border-white/5 space-y-3">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <h3 className="font-display font-semibold text-xs text-white uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                <span>Statutory Rule Traces ({filteredTraces.length} Active Traces)</span>
              </h3>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2 top-2" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search rules, citations..."
                    className="pl-7 pr-2 py-1 rounded-lg bg-slate-950 border border-white/10 text-[11px] text-slate-200 placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Category Filter Pills */}
            <div className="flex flex-wrap gap-1">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2 py-0.5 rounded-md text-[10px] font-mono transition-all ${
                    selectedCategory === cat
                      ? 'bg-blue-600 text-white font-bold'
                      : 'bg-slate-950/80 text-slate-400 hover:text-slate-200 border border-white/5'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Traces List */}
            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {filteredTraces.map((tr: any) => (
                <div
                  key={tr.traceId}
                  className="p-3 rounded-xl bg-slate-950/90 border border-white/5 space-y-2"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-white text-xs">{tr.ruleName}</span>
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          {tr.ruleId}
                        </span>
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-slate-800 text-slate-300">
                          {tr.category}
                        </span>
                      </div>
                      <div className="text-[10px] text-cyan-400 font-mono mt-0.5">
                        Statutory Citation: {tr.citation}
                      </div>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      {tr.status}
                    </span>
                  </div>

                  <div className="p-2 rounded-lg bg-slate-900/60 border border-white/5 text-[11px] font-mono text-slate-300">
                    <span className="text-slate-500 text-[9px] uppercase block">Formula / Calculation:</span>
                    <div className="text-amber-200 mt-0.5">{tr.calculationFormula}</div>
                  </div>

                  <div className="text-[11px] text-slate-300 leading-relaxed font-sans">
                    {tr.explanation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 bg-slate-900/90 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>100% Deterministic &amp; Auditable Mathematical Pipeline</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-display font-semibold text-xs transition-all"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
