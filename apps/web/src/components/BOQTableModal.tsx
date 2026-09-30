import React from 'react';
import { HouseOption, BOQLineItem } from '../types';
import { X, Download, FileSpreadsheet, Info } from 'lucide-react';

interface BOQTableModalProps {
  option: HouseOption | null;
  onClose: () => void;
}

export const BOQTableModal: React.FC<BOQTableModalProps> = ({ option, onClose }) => {
  if (!option) return null;
  const boq = option.boq;

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
    link.setAttribute('download', `BOQ_${option.layout.archetype}_${boq.rateSnapshotId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="glass-panel w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl border border-white/20">
        {/* Modal Header */}
        <div className="p-4 bg-slate-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-600/30 border border-cyan-500/40 flex items-center justify-center">
              <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-display font-bold text-sm text-white">
                  Model-Linked Bill of Quantities (QTO / BOQ)
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800/40">
                  {option.layout.label}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Rate Snapshot: <span className="font-mono text-slate-200">{boq.rateSnapshotId}</span> • Tier: <span className="font-mono text-cyan-300">{boq.qualityTier}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={downloadCSV}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-500/20 transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Table Content */}
        <div className="p-4 overflow-y-auto flex-1 space-y-4">
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
                  <th className="py-2.5 px-3">Model Traceability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono text-[11px]">
                {boq.lines.map((line: BOQLineItem) => (
                  <tr key={line.code} className="hover:bg-white/5 transition-colors">
                    <td className="py-2 px-3 font-bold text-cyan-400">{line.code}</td>
                    <td className="py-2 px-3 font-sans text-slate-200">{line.description}</td>
                    <td className="py-2 px-3 text-right text-white font-bold">{line.quantity.toLocaleString()}</td>
                    <td className="py-2 px-3 text-slate-400">{line.unit}</td>
                    <td className="py-2 px-3 text-right">₹{line.unitRate.toLocaleString()}</td>
                    <td className="py-2 px-3 text-right text-emerald-400 font-bold">₹{line.amount.toLocaleString()}</td>
                    <td className="py-2 px-3 font-sans text-[10px] text-slate-400 max-w-[200px] truncate" title={line.sourceRefs}>
                      {line.sourceRefs}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Cost Summary Stack */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-slate-900/80 p-3 rounded-lg border border-white/5">
              <span className="text-[10px] text-slate-400 block uppercase">Direct Material & Labor</span>
              <span className="font-mono font-bold text-white text-sm">
                ₹{boq.directHardCost.toLocaleString()}
              </span>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-lg border border-white/5">
              <span className="text-[10px] text-slate-400 block uppercase">Contingency (5%) + Prelims (8%)</span>
              <span className="font-mono font-bold text-amber-300 text-sm">
                ₹{(boq.contingency + boq.contractorPrelims).toLocaleString()}
              </span>
            </div>

            <div className="bg-emerald-950/40 p-3 rounded-lg border border-emerald-800/40">
              <span className="text-[10px] text-emerald-400/80 block uppercase">Total Base Estimate</span>
              <span className="font-mono font-bold text-emerald-400 text-base">
                ₹{boq.totalBaseEstimate.toLocaleString()}
              </span>
              <span className="text-[10px] text-slate-400 block font-mono">
                ₹{Math.round(boq.costPerSqFtBUA)}/sqft • ₹{Math.round(boq.costPerSqmBUA)}/m²
              </span>
            </div>
          </div>

          {/* Traceability Note */}
          <div className="p-2.5 rounded-lg bg-blue-950/30 border border-blue-800/30 flex items-start gap-2 text-[11px] text-slate-300">
            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <span>
              <strong>NIBS & NBC 2016 Compliant:</strong> Every quantity is calculated deterministically from explicit building elements (wall faces minus openings, floor polygons, structural column grids). No black-box AI approximations.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
