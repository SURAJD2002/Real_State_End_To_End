import React, { useState } from 'react';
import { HouseOption, BOQLineItem } from '../types';
import { 
  Download, 
  Info,
  Layers,
  FileCode,
  Printer,
  ChevronRight,
  ShieldCheck
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
  const [selectedLineForTrace, setSelectedLineForTrace] = useState<BOQLineItem | null>(null);

  const boq = selectedOption.boq;
  const layout = selectedOption.layout;
  const wf = boq.costWaterfall;

  // Categories matching trade sections
  const categories = [
    { id: 'ALL', label: 'All Items' },
    { id: 'EARTHWORK', label: '01 Earthwork', prefix: 'EXC' },
    { id: 'RCC', label: '02 RCC Structure', prefix: 'RCC' },
    { id: 'MASONRY', label: '03 Masonry', prefix: 'MAS' },
    { id: 'PLASTER', label: '04 Plaster', prefix: 'PL' },
    { id: 'FLOORING', label: '05 Flooring', prefix: 'FL' },
    { id: 'JOINERY', label: '06 Doors & Windows', prefix: 'DR' },
    { id: 'FINISHES', label: '07 Painting & Finishes', prefix: 'PNT' },
    { id: 'WATERPROOF', label: '08 Waterproofing', prefix: 'WP' },
    { id: 'MEP', label: '09-10 Preliminary MEP', prefix: 'ELE' }
  ];

  const filteredLines = activeCategory === 'ALL'
    ? boq.lines
    : boq.lines.filter(line => {
        const itemCode = line.itemCode || line.code;
        if (activeCategory === 'EARTHWORK') return itemCode.startsWith('EXC');
        if (activeCategory === 'RCC') return itemCode.startsWith('RCC');
        if (activeCategory === 'MASONRY') return itemCode.startsWith('MAS');
        if (activeCategory === 'PLASTER') return itemCode.startsWith('PL-');
        if (activeCategory === 'FLOORING') return itemCode.startsWith('FL-');
        if (activeCategory === 'JOINERY') return itemCode.startsWith('DR') || itemCode.startsWith('WIN');
        if (activeCategory === 'FINISHES') return itemCode.startsWith('PNT');
        if (activeCategory === 'WATERPROOF') return itemCode.startsWith('WP');
        if (activeCategory === 'MEP') return itemCode.startsWith('ELE') || itemCode.startsWith('PLB');
        return true;
      });

  const downloadCSV = () => {
    const headers = [
      'Item Code', 'Trade Section', 'Description', 'Quantity', 'Unit', 
      'Material Rate (INR)', 'Labour Rate (INR)', 'Equipment Rate (INR)', 'Unit Rate (INR)', 
      'Amount (INR)', 'Confidence', 'Measurement Rule', 'CBM Elements Count'
    ];
    const rows = boq.lines.map((line: BOQLineItem) => [
      line.itemCode || line.code,
      `"${(line.section || 'General').replace(/"/g, '""')}"`,
      `"${line.description.replace(/"/g, '""')}"`,
      line.quantity,
      line.unit,
      line.materialRate || (line.unitRate * 0.6),
      line.labourRate || (line.unitRate * 0.35),
      line.equipmentRate || (line.unitRate * 0.05),
      line.unitRate,
      line.amount,
      line.confidence || 'HIGH',
      line.measurementRuleId || 'IS-1200',
      (line.sourceElementIds || line.canonicalElementIds || []).length
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

  const downloadJSON = () => {
    const payload = {
      designVersionId: selectedOption.designVersionId,
      archetype: layout.archetype,
      rateSnapshotId: boq.rateSnapshotId,
      qualityTier: boq.qualityTier,
      costWaterfall: wf,
      boqLines: boq.lines,
      hashes: {
        qtoHash: boq.qtoHash,
        boqHash: boq.boqHash,
        costHash: boq.costHash
      },
      exportedAt: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `CostEstimate_${layout.archetype}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const printSummary = () => {
    window.print();
  };

  return (
    <div className="w-full h-full flex flex-col bg-[#070b12] text-slate-200 overflow-y-auto p-6 space-y-6 select-none">
      {/* Cost Hero Summary Banner */}
      <div className="glass-panel p-6 bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-950 border border-blue-500/30 flex items-center justify-between">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-blue-600/30 text-blue-400 border border-blue-500/30 uppercase flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-cyan-400" />
              M3 Model-Linked QTO + BOQ + Cost Engine
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">
              Deterministic IS 1200
            </span>
            {boq.costHash && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-white/5" title={`Cost Hash: ${boq.costHash}`}>
                Hash: {boq.costHash.substring(0, 10)}...
              </span>
            )}
          </div>

          <h2 className="font-display font-bold text-2xl text-white">
            ₹{(boq.totalBaseEstimate / 100000).toFixed(2)} Lakhs
            <span className="text-sm font-normal text-slate-400 ml-2 font-mono">
              (Total Preliminary Construction Cost)
            </span>
          </h2>

          <div className="flex items-center gap-3 text-xs font-mono text-slate-300 pt-1 flex-wrap">
            <span>Range: <strong className="text-cyan-400">₹{(boq.estimateRange.low / 100000).toFixed(2)}L – ₹{(boq.estimateRange.high / 100000).toFixed(2)}L</strong></span>
            <span>•</span>
            <span>BUA Rate: <strong className="text-white">₹{Math.round(boq.costPerSqFtBUA)}/sqft</strong> (₹{Math.round(boq.costPerSqmBUA)}/m²)</span>
            <span>•</span>
            <span>Carpet Rate: <strong className="text-amber-300">₹{Math.round(wf?.costPerCarpetSqFt || (boq.costPerSqFtBUA * 1.18))}/sqft</strong></span>
            <span>•</span>
            <span className="text-slate-400">Snapshot: <strong className="text-slate-200">{boq.rateSnapshotId}</strong></span>
          </div>
        </div>

        {/* Quality Specification Tier & Actions */}
        <div className="flex flex-col items-end gap-2 shrink-0 pl-6 border-l border-white/10">
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Specification Tier:</span>
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
          </div>

          <div className="flex items-center gap-2 mt-1">
            <button
              onClick={downloadCSV}
              title="Download CSV Table"
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>CSV</span>
            </button>
            <button
              onClick={downloadJSON}
              title="Download Machine-Readable JSON"
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <FileCode className="w-3.5 h-3.5 text-amber-400" />
              <span>JSON</span>
            </button>
            <button
              onClick={printSummary}
              title="Print Summary Report"
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Printer className="w-3.5 h-3.5 text-emerald-400" />
              <span>Print</span>
            </button>
            <button
              onClick={() => onRequestBuild(selectedOption)}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-600/30 flex items-center gap-1.5 transition-all"
            >
              <span>LOCK & BUILD →</span>
            </button>
          </div>
        </div>
      </div>

      {/* Cost Waterfall Decomposition Cards */}
      <div className="grid grid-cols-5 gap-3.5">
        <div className="glass-panel p-3 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Raw Materials</span>
          <span className="font-mono font-bold text-white text-lg">
            ₹{((wf?.directMaterialCost ?? (boq.directHardCost * 0.60)) / 100000).toFixed(2)} L
          </span>
          <span className="text-[10px] text-slate-500 block">Cement, rebar, AAC, tiles, paint</span>
        </div>

        <div className="glass-panel p-3 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Skilled Labour</span>
          <span className="font-mono font-bold text-white text-lg">
            ₹{((wf?.directLabourCost ?? (boq.directHardCost * 0.35)) / 100000).toFixed(2)} L
          </span>
          <span className="text-[10px] text-slate-500 block">Masons, bar-benders, carpenters</span>
        </div>

        <div className="glass-panel p-3 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Plant & Wastage</span>
          <span className="font-mono font-bold text-cyan-300 text-lg">
            ₹{(((wf?.directEquipmentCost || 0) + (wf?.materialWastageCost || (boq.directHardCost * 0.05))) / 100000).toFixed(2)} L
          </span>
          <span className="text-[10px] text-slate-500 block">Shuttering, staging & 4% waste</span>
        </div>

        <div className="glass-panel p-3 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Prelims & Safety (8%)</span>
          <span className="font-mono font-bold text-amber-300 text-lg">
            ₹{(boq.contractorPrelims / 100000).toFixed(2)} L
          </span>
          <span className="text-[10px] text-slate-500 block">Site supervisor, power, dewatering</span>
        </div>

        <div className="glass-panel p-3 bg-slate-900/70 border border-white/5 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase font-mono block">Contingency (5%)</span>
          <span className="font-mono font-bold text-emerald-400 text-lg">
            ₹{(boq.contingency / 100000).toFixed(2)} L
          </span>
          <span className="text-[10px] text-slate-500 block">Unforeseen site condition buffer</span>
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
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  activeCategory === cat.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-slate-400">
              {filteredLines.length} of {boq.lines.length} Line Items
            </span>
          </div>
        </div>

        {/* BOQ Data Table with clickable rows for deep explainability */}
        <div className="overflow-x-auto rounded-lg border border-white/10">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 font-mono text-[11px] border-b border-white/10 uppercase">
              <tr>
                <th className="py-2.5 px-3">Item Code</th>
                <th className="py-2.5 px-3">Trade Scope & Specification</th>
                <th className="py-2.5 px-3 text-right">Quantity</th>
                <th className="py-2.5 px-3">Unit</th>
                <th className="py-2.5 px-3 text-right">Unit Rate</th>
                <th className="py-2.5 px-3 text-right">Total Amount</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">CBM Trace</th>
                <th className="py-2.5 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono text-[11px]">
              {filteredLines.map((line: BOQLineItem) => {
                const itemCode = line.itemCode || line.code;
                const sourceIds = line.sourceElementIds || line.canonicalElementIds || [];
                const conf = line.confidence || 'HIGH';
                const isSelected = selectedLineForTrace?.code === line.code;

                return (
                  <tr 
                    key={itemCode} 
                    onClick={() => setSelectedLineForTrace(line)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-950/40 border-l-2 border-blue-500' : 'hover:bg-white/5'
                    }`}
                  >
                    <td className="py-2.5 px-3 font-bold text-cyan-400">{itemCode}</td>
                    <td className="py-2.5 px-3 font-sans text-slate-200 max-w-xs">
                      <div className="font-semibold text-slate-100">{line.description}</div>
                      {line.specification && (
                        <div className="text-[10px] text-slate-400">{line.specification}</div>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-right text-white font-bold">{line.quantity.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-slate-400">{line.unit}</td>
                    <td className="py-2.5 px-3 text-right text-slate-200">₹{line.unitRate.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-right text-emerald-400 font-bold">₹{line.amount.toLocaleString()}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        conf === 'HIGH' ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/40' :
                        conf === 'PRELIMINARY' ? 'bg-amber-950/80 text-amber-300 border border-amber-800/40' :
                        'bg-blue-950/80 text-blue-300 border border-blue-800/40'
                      }`}>
                        {conf}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-sans text-[11px] text-slate-300 max-w-[160px] truncate" title={`${sourceIds.length} CBM elements: ${sourceIds.slice(0, 4).join(', ')}`}>
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-white/5 text-[10px]">
                        {sourceIds.length} CBM elements
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-center">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLineForTrace(line);
                        }}
                        className="text-[10px] font-sans font-semibold text-cyan-400 hover:text-cyan-300 hover:underline flex items-center justify-center gap-1 mx-auto"
                      >
                        <span>Audit</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Traceability Guarantee Footer */}
        <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-800/30 flex items-start gap-2.5 text-xs text-slate-300 leading-normal">
          <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <span>
            <strong>Deterministic Model-to-Quantity Traceability:</strong> Every line in this Bill of Quantities is directly computed from the 3D canonical object graph (surfaces minus door/window openings, structural column volumes, room floor polygons). Click any row above to inspect the geometric formula and source elements.
          </span>
        </div>
      </div>

      {/* Traceability / Audit Modal */}
      {selectedLineForTrace && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="glass-panel w-full max-w-2xl bg-slate-900 border border-blue-500/40 p-6 rounded-xl shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-blue-600/30 border border-blue-500/40 flex items-center justify-center">
                  <Layers className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">
                    Quantity & Rate Audit: {selectedLineForTrace.itemCode || selectedLineForTrace.code}
                  </h3>
                  <div className="text-[11px] text-slate-400">{selectedLineForTrace.description}</div>
                </div>
              </div>
              <button 
                onClick={() => setSelectedLineForTrace(null)}
                className="text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-white/10 text-xs font-bold"
              >
                ✕ Close
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="bg-slate-950/70 p-3 rounded-lg border border-white/5 space-y-1.5">
                <span className="text-[10px] text-cyan-400 uppercase font-bold block">1. Why this quantity?</span>
                <div>Computed Quantity: <strong className="text-white text-sm">{selectedLineForTrace.quantity} {selectedLineForTrace.unit}</strong></div>
                <div className="text-[11px] text-slate-400">
                  Measurement Rule: <span className="text-slate-200">{selectedLineForTrace.measurementRuleId || 'IS-1200'}</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  IS 1200 Principle: Deducts door & window voids from gross wall surfaces.
                </div>
                <div className="text-[11px] text-slate-400">
                  Source CBM Elements: <span className="text-emerald-400 font-bold">{(selectedLineForTrace.sourceElementIds || selectedLineForTrace.canonicalElementIds || []).length} objects</span>
                </div>
                <div className="text-[10px] text-slate-500 truncate">
                  IDs: {(selectedLineForTrace.sourceElementIds || selectedLineForTrace.canonicalElementIds || []).join(', ')}
                </div>
              </div>

              <div className="bg-slate-950/70 p-3 rounded-lg border border-white/5 space-y-1.5">
                <span className="text-[10px] text-amber-400 uppercase font-bold block">2. Why this rate?</span>
                <div>Applied Unit Rate: <strong className="text-white text-sm">₹{selectedLineForTrace.unitRate.toLocaleString()} / {selectedLineForTrace.unit}</strong></div>
                <div className="text-[11px] text-slate-400">
                  Rate Snapshot: <span className="text-slate-200">{selectedLineForTrace.rateSnapshotId || boq.rateSnapshotId}</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Jurisdiction: <span className="text-slate-200">Maharashtra / Mumbai MMR</span>
                </div>
                <div className="space-y-0.5 pt-1 text-[10px]">
                  <div className="flex justify-between text-slate-300">
                    <span>Direct Material:</span>
                    <span>₹{selectedLineForTrace.materialRate || Math.round(selectedLineForTrace.unitRate * 0.60)}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Direct Labour:</span>
                    <span>₹{selectedLineForTrace.labourRate || Math.round(selectedLineForTrace.unitRate * 0.35)}</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Equipment/Plant:</span>
                    <span>₹{selectedLineForTrace.equipmentRate || Math.round(selectedLineForTrace.unitRate * 0.05)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-300">Total Item Amount = Quantity × Unit Rate:</span>
              <span className="text-emerald-400 font-bold text-base">₹{selectedLineForTrace.amount.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
