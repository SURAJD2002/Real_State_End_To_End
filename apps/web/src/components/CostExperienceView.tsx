import React, { useState } from 'react';
import { HouseOption, BOQLineItem } from '../types';
import { 
  Download, 
  Info 
} from 'lucide-react';

interface CostExperienceViewProps {
  selectedOption: HouseOption;
  onUpdateTier: (tier: string) => void;
  onRequestBuild: (option: HouseOption) => void;
}

export const CostExperienceView: React.FC<CostExperienceViewProps> = ({
  selectedOption,
  onUpdateTier,
  onRequestBuild
}) => {
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const boq = selectedOption.boq;
  const layout = selectedOption.layout;

  // Group BOQ lines by work category
  const categories = [
    { id: 'ALL', label: 'All Items' },
    { id: 'EARTHWORK', label: '1. Earthwork & Foundation', codes: ['EXC-01', 'RCC-01'] },
    { id: 'MASONRY', label: '2. Masonry & Plaster', codes: ['MAS-01', 'PL-01'] },
    { id: 'FINISHES', label: '3. Finishes & Flooring', codes: ['FL-01', 'PNT-01'] },
    { id: 'JOINERY', label: '4. Doors & Windows', codes: ['DR-01', 'WIN-01'] },
    { id: 'MEP', label: '5. Electrical & Plumbing', codes: ['ELE-01', 'PLB-01'] }
  ];

  const filteredLines = activeCategory === 'ALL'
    ? boq.lines
    : boq.lines.filter(line => {
        const cat = categories.find(c => c.id === activeCategory);
        return cat?.codes ? cat.codes.includes(line.code) : true;
      });

  const downloadCSV = () => {
    const headers = ['Code', 'Description', 'Quantity', 'Unit', 'Unit Rate (INR)', 'Amount (INR)', 'Source Model Ref', 'Waste Policy'];
    const rows = boq.lines.map((line: BOQLineItem) => [
      line.code,
      `"${line.description.replace(/"/g, '""')}"`,
      line.quantity,
      line.unit,
      line.unitRate,
      line.amount,
      `"${line.sourceRefs}"`,
      `"${line.wastePolicy}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `BOQ_${layout.archetype}_${boq.rateSnapshotId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b12] text-slate-200 overflow-y-auto p-6 space-y-6 select-none">
      {/* Cost Hero Summary Banner */}
      <div className="glass-panel p-6 bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-950 border border-blue-500/30 flex items-center justify-between">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-blue-600/30 text-blue-400 border border-blue-500/30 uppercase">
              Model-Derived Takeoff (QTO / BOQ)
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/40">
              Confidence: Preliminary Estimate
            </span>
          </div>
          <h2 className="font-display font-bold text-2xl text-white">
            ₹{(boq.totalBaseEstimate / 100000).toFixed(2)} Lakhs
            <span className="text-sm font-normal text-slate-400 ml-2 font-mono">
              (Expected Base Cost)
            </span>
          </h2>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-300 pt-1">
            <span>Range: <strong className="text-cyan-400">₹{(boq.estimateRange.low / 100000).toFixed(2)}L – ₹{(boq.estimateRange.high / 100000).toFixed(2)}L</strong></span>
            <span>•</span>
            <span>Unit Rate: <strong className="text-white">₹{Math.round(boq.costPerSqFtBUA)}/sqft</strong> (₹{Math.round(boq.costPerSqmBUA)}/m²)</span>
            <span>•</span>
            <span className="text-slate-400">Rate Snapshot: {boq.rateSnapshotId}</span>
          </div>
        </div>

        {/* Quality Specification Tier Selector */}
        <div className="flex flex-col items-end gap-2 shrink-0 pl-6 border-l border-white/10">
          <span className="text-[10px] text-slate-400 uppercase font-mono">Finish & Structural Specification:</span>
          <div className="flex rounded-lg bg-slate-950 p-1 border border-white/10">
            {['STANDARD', 'PREMIUM', 'LUXURY'].map((tier) => (
              <button
                key={tier}
                onClick={() => onUpdateTier(tier)}
                className={`px-3 py-1 rounded text-xs font-semibold font-mono transition-all ${
                  boq.qualityTier === tier
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tier}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 mt-1">
            <button
              onClick={downloadCSV}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Export BOQ (.CSV)</span>
            </button>
            <button
              onClick={() => onRequestBuild(selectedOption)}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-600/30 flex items-center gap-1.5 transition-all"
            >
              <span>REQUEST BUILD →</span>
            </button>
          </div>
        </div>
      </div>

      {/* Cost Decomposition Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-panel p-3.5 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Direct Civil Materials</span>
          <span className="font-mono font-bold text-white text-lg">₹{(boq.directHardCost * 0.62 / 100000).toFixed(2)} L</span>
          <span className="text-[10px] text-slate-500 block">Cement, steel, sand, aggregate</span>
        </div>

        <div className="glass-panel p-3.5 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Direct Trade Labor</span>
          <span className="font-mono font-bold text-white text-lg">₹{(boq.directHardCost * 0.38 / 100000).toFixed(2)} L</span>
          <span className="text-[10px] text-slate-500 block">Masons, carpenters, bar benders</span>
        </div>

        <div className="glass-panel p-3.5 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Site Prelims & Safety (8%)</span>
          <span className="font-mono font-bold text-amber-300 text-lg">₹{(boq.contractorPrelims / 100000).toFixed(2)} L</span>
          <span className="text-[10px] text-slate-500 block">Scaffolding, water, electricity</span>
        </div>

        <div className="glass-panel p-3.5 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Statutory Contingency (5%)</span>
          <span className="font-mono font-bold text-cyan-300 text-lg">₹{(boq.contingency / 100000).toFixed(2)} L</span>
          <span className="text-[10px] text-slate-500 block">Buffer for price volatility</span>
        </div>
      </div>

      {/* Itemized Traceable BOQ Table Section */}
      <div className="glass-panel p-4 space-y-4">
        {/* Table Category Filter Tabs */}
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-1.5 overflow-x-auto">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeCategory === cat.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <span className="text-xs font-mono text-slate-400">
            {filteredLines.length} of {boq.lines.length} Line Items
          </span>
        </div>

        {/* BOQ Data Table */}
        <div className="overflow-x-auto rounded-lg border border-white/10">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] border-b border-white/10 uppercase">
              <tr>
                <th className="py-2.5 px-3">Item Code</th>
                <th className="py-2.5 px-3">Work Package & Description</th>
                <th className="py-2.5 px-3 text-right">Quantity</th>
                <th className="py-2.5 px-3">Unit</th>
                <th className="py-2.5 px-3 text-right">Rate (₹)</th>
                <th className="py-2.5 px-3 text-right">Amount (₹)</th>
                <th className="py-2.5 px-3">Model Object Traceability</th>
                <th className="py-2.5 px-3">Waste Factor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono text-[11px]">
              {filteredLines.map((line: BOQLineItem) => (
                <tr key={line.code} className="hover:bg-white/5 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-cyan-400">{line.code}</td>
                  <td className="py-2.5 px-3 font-sans text-slate-200 max-w-xs">{line.description}</td>
                  <td className="py-2.5 px-3 text-right text-white font-bold">{line.quantity.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-slate-400">{line.unit}</td>
                  <td className="py-2.5 px-3 text-right">₹{line.unitRate.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-400 font-bold">₹{line.amount.toLocaleString()}</td>
                  <td className="py-2.5 px-3 font-sans text-[11px] text-slate-300 max-w-[200px] truncate" title={line.sourceRefs}>
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/5 text-[10px]">
                      {line.sourceRefs}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-400 text-[10px]">{line.wastePolicy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Traceability Guarantee Footer */}
        <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-800/30 flex items-start gap-2.5 text-xs text-slate-300 leading-normal">
          <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <span>
            <strong>Deterministic Model-to-Quantity Traceability:</strong> Every line in this Bill of Quantities is directly computed from the 3D canonical object graph (surfaces minus openings, structural column volumes, room floor polygons). No black-box statistical estimates.
          </span>
        </div>
      </div>
    </div>
  );
};
