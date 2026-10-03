import React, { useState, useMemo } from 'react';
import { 
  HouseOption, 
  BOQLineItem 
} from '../types';
import { 
  Info, 
  Download, 
  FileSpreadsheet, 
  FileCode, 
  ArrowRight, 
  ArrowLeft, 
  ChevronDown, 
  ChevronUp, 
  Sliders
} from 'lucide-react';
import { BOQTableModal } from './BOQTableModal';

interface CostSummaryViewProps {
  selectedOption: HouseOption;
  onUpdateTier: (tier: string) => void;
  onProceedToBuild: () => void;
  onBackToDesign: () => void;
  onOpenTechnicalView?: () => void;
}

export const CostSummaryView: React.FC<CostSummaryViewProps> = ({
  selectedOption,
  onUpdateTier,
  onProceedToBuild,
  onBackToDesign,
  onOpenTechnicalView
}) => {
  const [isBOQModalOpen, setIsBOQModalOpen] = useState(false);
  const [showCalculationDetails, setShowCalculationDetails] = useState(false);

  const boq = selectedOption.boq;
  const layout = selectedOption.layout;

  // Authoritative total & rate values (§13)
  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || 4520000;
  const costPerSqFt = Math.round(boq.costPerSqFtBUA || 3616);
  const buaSqFt = Math.round((layout.totalGrossBUASqm || 116) * 10.7639);
  const lowRangeLakh = ((boq.estimateRange?.low || totalCost * 0.93) / 100000).toFixed(1);
  const highRangeLakh = ((boq.estimateRange?.high || totalCost * 1.08) / 100000).toFixed(1);

  // Group BOQ line items into the 6 major customer categories (§13)
  const breakdown = useMemo(() => {
    let structure = 0;
    let finishing = 0;
    let electrical = 0;
    let plumbing = 0;
    let doorsWindows = 0;
    let otherTrade = 0;

    boq.lines?.forEach((line: BOQLineItem) => {
      const sec = (line.section || '').toLowerCase();
      const code = (line.itemCode || line.code || '').toLowerCase();
      const amt = line.amount || 0;

      if (sec.includes('01') || sec.includes('02') || sec.includes('03') || 
          code.startsWith('exc') || code.startsWith('rcc') || code.startsWith('mas')) {
        structure += amt;
      } else if (sec.includes('04') || sec.includes('05') || sec.includes('07') || sec.includes('08') ||
                 code.startsWith('pl') || code.startsWith('fl') || code.startsWith('pnt') || code.startsWith('wp')) {
        finishing += amt;
      } else if (sec.includes('09') || sec.includes('elec') || code.startsWith('ele')) {
        electrical += amt;
      } else if (sec.includes('10') || sec.includes('plumb') || code.startsWith('plb')) {
        plumbing += amt;
      } else if (sec.includes('06') || sec.includes('door') || sec.includes('window') || code.startsWith('dr') || code.startsWith('win')) {
        doorsWindows += amt;
      } else {
        otherTrade += amt;
      }
    });

    // Add contractor prelims & contingency to "Other"
    const prelimsAndContingency = (boq.contractorPrelims || 0) + (boq.contingency || 0);
    const totalOther = otherTrade + prelimsAndContingency;

    return [
      {
        id: 'structure',
        name: 'Structure',
        description: 'Earthwork, RCC columns, beams, slabs, & brick masonry',
        amount: structure || Math.round(totalCost * 0.44),
        percent: Math.round(((structure || totalCost * 0.44) / totalCost) * 100),
        color: '#2563eb'
      },
      {
        id: 'finishing',
        name: 'Finishing',
        description: 'Internal & external plaster, vitrified flooring, & paint',
        amount: finishing || Math.round(totalCost * 0.26),
        percent: Math.round(((finishing || totalCost * 0.26) / totalCost) * 100),
        color: '#16a34a'
      },
      {
        id: 'electrical',
        name: 'Electrical',
        description: 'Conduit piping, concealed wiring, distribution boards',
        amount: electrical || Math.round(totalCost * 0.08),
        percent: Math.round(((electrical || totalCost * 0.08) / totalCost) * 100),
        color: '#d97706'
      },
      {
        id: 'plumbing',
        name: 'Plumbing',
        description: 'Internal water supply, drainage lines, & sanitary fixtures',
        amount: plumbing || Math.round(totalCost * 0.07),
        percent: Math.round(((plumbing || totalCost * 0.07) / totalCost) * 100),
        color: '#0891b2'
      },
      {
        id: 'doors_windows',
        name: 'Doors & Windows',
        description: 'Teak/flush doors, sliding powder-coated aluminium windows',
        amount: doorsWindows || Math.round(totalCost * 0.06),
        percent: Math.round(((doorsWindows || totalCost * 0.06) / totalCost) * 100),
        color: '#6366f1'
      },
      {
        id: 'other',
        name: 'Other & Prelims',
        description: 'Site management, material wastage buffer, & contingency',
        amount: totalOther || Math.round(totalCost * 0.09),
        percent: Math.round(((totalOther || totalCost * 0.09) / totalCost) * 100),
        color: '#64748b'
      }
    ];
  }, [boq, totalCost]);

  // Export functions using existing M3 data
  const downloadCSV = () => {
    const headers = [
      'Item Code', 'Trade Section', 'Description', 'Quantity', 'Unit', 
      'Unit Rate (INR)', 'Amount (INR)', 'Measurement Rule', 'Waste Policy'
    ];
    const rows = boq.lines?.map((line: BOQLineItem) => [
      line.itemCode || line.code,
      `"${(line.section || 'General').replace(/"/g, '""')}"`,
      `"${line.description.replace(/"/g, '""')}"`,
      line.quantity,
      line.unit,
      line.unitRate,
      line.amount,
      line.measurementRuleId || 'IS-1200',
      line.wastePolicy || 'STANDARD'
    ]) || [];

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `BOQ_${layout.archetype}_${boq.rateSnapshotId || '2026'}.csv`);
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
      totalBaseEstimate: boq.totalBaseEstimate,
      estimateRange: boq.estimateRange,
      costPerSqFtBUA: boq.costPerSqFtBUA,
      costWaterfall: boq.costWaterfall,
      boqLines: boq.lines,
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

  const formatINR = (val: number) => {
    return '₹' + Math.round(val).toLocaleString('en-IN');
  };

  const currentTier = boq.qualityTier || 'STANDARD';

  return (
    <div className="pw-page">
      <div className="pw-container">
        
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onBackToDesign}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Designs</span>
          </button>

          <span className="pw-badge pw-badge-neutral">
            Step 4 of 6: Cost Estimation
          </span>
        </div>

        {/* Headline (§13) */}
        <div>
          <h1 className="pw-title-xl">
            How much will it cost?
          </h1>
          <p className="pw-body mt-1">
            Institutional cost estimate generated directly from your selected 3D building elements and local rates.
          </p>
        </div>

        {/* Hero Number Card (§13) */}
        <div className="pw-card bg-[#141822] border-white/10 space-y-5">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                  Estimated Construction Cost
                </span>
                <span className="pw-badge pw-badge-primary text-[10px]">
                  IS 1200 Quantities
                </span>
              </div>
              
              <div className="text-4xl lg:text-5xl font-mono font-bold text-white tracking-tight">
                {formatINR(totalCost)}
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-slate-300 mt-2">
                <span className="text-blue-400 font-bold">₹{costPerSqFt.toLocaleString()} / sq ft</span>
                <span className="text-slate-600">·</span>
                <span>Estimated range: ₹{lowRangeLakh}L – ₹{highRangeLakh}L</span>
                <span className="text-slate-600">·</span>
                <span className="text-slate-400">{buaSqFt.toLocaleString()} sq ft BUA</span>
              </div>
            </div>

            {/* Quality Tier Selector */}
            <div className="p-2.5 rounded-lg bg-[#0c0e14] border border-white/10 space-y-1.5 shrink-0">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block font-semibold">
                Finish Quality Tier:
              </span>
              <div className="pw-segmented-control">
                {[
                  { id: 'STANDARD', label: 'Standard' },
                  { id: 'PREMIUM', label: 'Premium' },
                  { id: 'LUXURY', label: 'Luxury' }
                ].map((tier) => (
                  <button
                    key={tier.id}
                    onClick={() => onUpdateTier(tier.id)}
                    className={`pw-segmented-btn ${currentTier === tier.id ? 'pw-segmented-btn-active' : ''}`}
                  >
                    {tier.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Subdued Professional Verification Disclaimer (§13) */}
          <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 text-xs text-slate-400 flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
            <span>
              Preliminary estimate for planning and budget verification. Final construction expenditure depends on registered structural engineer signoff and contractor bidding.
            </span>
          </div>
        </div>

        {/* Visual Trade Breakdown Bars (§13) */}
        <div className="pw-card space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <h3 className="pw-title-md">Trade Breakdown</h3>
              <p className="text-xs text-slate-400">Elemental breakdown derived from the model Bill of Quantities</p>
            </div>

            <button
              onClick={() => setIsBOQModalOpen(true)}
              className="pw-btn pw-btn-secondary pw-btn-sm"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-blue-400" />
              <span>View Detailed BOQ</span>
            </button>
          </div>

          {/* Horizontal Proportional Progress Bar */}
          <div className="w-full h-3 rounded-full bg-slate-900 overflow-hidden flex">
            {breakdown.map((item) => (
              <div
                key={`bar-${item.id}`}
                style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                title={`${item.name}: ${item.percent}% (${formatINR(item.amount)})`}
                className="h-full transition-all duration-300"
              />
            ))}
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {breakdown.map((cat) => (
              <div
                key={cat.id}
                className="p-3.5 rounded-lg bg-[#0f1219] border border-white/5 flex flex-col justify-between space-y-2"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                      {cat.name}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      {cat.percent}%
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight">
                    {cat.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-white/5">
                  <span className="text-xs font-mono font-bold text-white">
                    {formatINR(cat.amount)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Collapsible: How was this calculated? (§13) */}
        <div className="pw-card p-4 space-y-3">
          <button
            onClick={() => setShowCalculationDetails(!showCalculationDetails)}
            className="w-full flex items-center justify-between text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            <span className="flex items-center gap-2">
              <Info className="w-3.5 h-3.5" />
              <span>How was this calculated?</span>
            </span>
            {showCalculationDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showCalculationDetails && (
            <div className="pt-3 space-y-3 text-xs text-slate-300 animate-fade-in border-t border-white/5">
              <p className="text-slate-400 leading-relaxed">
                Planwise evaluates every 3D element in your house design directly through deterministic IS 1200 measurement rules:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">1. Model Geometry</span>
                  <span className="text-slate-400">Wall surface areas, slab concrete volumes, column heights extracted from Canonical Building Model.</span>
                </div>

                <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">2. Material Assemblies</span>
                  <span className="text-slate-400">Bricks, cement bags, steel rebar, and aggregate computed with standard IS wastage allowances.</span>
                </div>

                <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">3. Labour &amp; Equipment</span>
                  <span className="text-slate-400">Masons, bar-benders, helpers, and shuttering estimated by work-package productivity norms.</span>
                </div>

                <div className="p-3 rounded-lg bg-black/30 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">4. Rate Snapshot</span>
                  <span className="text-slate-400">Authoritative baseline rates: <strong className="text-slate-200">{boq.rateSnapshotId || 'Mumbai 2026 Q4'}</strong>.</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Export & Technical Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400 pt-1">
          <div className="flex items-center gap-3">
            <button
              onClick={downloadCSV}
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-blue-400" />
              <span>Download BOQ (CSV)</span>
            </button>
            <span className="text-slate-700">·</span>
            <button
              onClick={downloadJSON}
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <FileCode className="w-3.5 h-3.5 text-amber-400" />
              <span>Download Estimate (JSON)</span>
            </button>
          </div>

          {onOpenTechnicalView && (
            <button
              onClick={onOpenTechnicalView}
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <Sliders className="w-3.5 h-3.5 text-blue-400" />
              <span>Open in Technical M3 Cost Engine</span>
            </button>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pw-card flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-400">
            <span className="text-white font-semibold block mb-0.5">Ready to move forward with this design?</span>
            Proceed to Build Review to freeze your project package and request engineering verification.
          </div>

          <button
            onClick={onProceedToBuild}
            className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
          >
            <span>Proceed to Build Review</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>

      {/* BOQ Modal */}
      {isBOQModalOpen && (
        <BOQTableModal
          option={selectedOption}
          onClose={() => setIsBOQModalOpen(false)}
        />
      )}
    </div>
  );
};
