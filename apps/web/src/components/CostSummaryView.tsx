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

  // Authoritative total & rate values
  const totalCost = boq.totalBaseEstimate || boq.estimateRange?.expected || 4500000;
  const costPerSqFt = Math.round(boq.costPerSqFtBUA || 3600);
  const buaSqFt = Math.round((layout.totalGrossBUASqm || 110) * 10.7639);
  const lowRangeLakh = ((boq.estimateRange?.low || totalCost * 0.93) / 100000).toFixed(1);
  const highRangeLakh = ((boq.estimateRange?.high || totalCost * 1.08) / 100000).toFixed(1);

  // Group BOQ line items into the 6 major customer categories
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

    // Add contractor prelims & contingency to "Other / Preliminaries"
    const prelimsAndContingency = (boq.contractorPrelims || 0) + (boq.contingency || 0);
    const totalOther = otherTrade + prelimsAndContingency;

    return [
      {
        id: 'structure',
        name: 'Structure',
        description: 'Earthwork, RCC columns, beams, slabs, & brickwork',
        amount: structure,
        percent: Math.round((structure / totalCost) * 100) || 45,
        color: '#3b82f6'
      },
      {
        id: 'finishing',
        name: 'Finishing',
        description: 'Internal & external plaster, vitrified flooring, & paint',
        amount: finishing,
        percent: Math.round((finishing / totalCost) * 100) || 25,
        color: '#10b981'
      },
      {
        id: 'electrical',
        name: 'Electrical',
        description: 'Conduit piping, concealed wiring, distribution boards',
        amount: electrical,
        percent: Math.round((electrical / totalCost) * 100) || 8,
        color: '#f59e0b'
      },
      {
        id: 'plumbing',
        name: 'Plumbing',
        description: 'Internal water supply, drainage lines, & sanitary ware',
        amount: plumbing,
        percent: Math.round((plumbing / totalCost) * 100) || 7,
        color: '#06b6d4'
      },
      {
        id: 'doors_windows',
        name: 'Doors & Windows',
        description: 'Teak/flush doors, UPVC/aluminium sliding windows',
        amount: doorsWindows,
        percent: Math.round((doorsWindows / totalCost) * 100) || 6,
        color: '#8b5cf6'
      },
      {
        id: 'other',
        name: 'Other / Preliminaries',
        description: 'Site management, material wastage buffer, & contingency',
        amount: totalOther,
        percent: Math.max(1, 100 - (
          Math.round((structure / totalCost) * 100) +
          Math.round((finishing / totalCost) * 100) +
          Math.round((electrical / totalCost) * 100) +
          Math.round((plumbing / totalCost) * 100) +
          Math.round((doorsWindows / totalCost) * 100)
        )),
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
    return '₹ ' + Math.round(val).toLocaleString('en-IN');
  };

  const bedsCount = layout.rooms?.filter(r => 
    r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE'
  ).length || 2;

  const currentTier = boq.qualityTier || 'STANDARD';

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#07090e] p-6 lg:p-10 flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-8 animate-fade-in pb-20">

        {/* Navigation Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
          <button
            type="button"
            onClick={onBackToDesign}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Designs</span>
          </button>

          {/* Stepper */}
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-emerald-400 font-medium">1 Land ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">2 Feasibility ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">3 Design ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-blue-400 font-bold bg-blue-950/80 border border-blue-500/40 px-2.5 py-0.5 rounded-full">
              4 Cost ●
            </span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">5 Build</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">6 Engineer</span>
          </div>
        </div>

        {/* Page Title */}
        <div className="space-y-2">
          <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
            How much will it cost?
          </h1>
          <p className="text-slate-400 text-sm lg:text-base leading-relaxed">
            Here's an estimated construction cost based on the house design you selected.
          </p>
        </div>

        {/* 1. TOP SUMMARY CARD */}
        <div className="rounded-2xl bg-slate-900/60 border border-white/10 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block">
              Selected Home
            </span>
            <h2 className="text-base font-bold text-white">
              {layout.label || 'Selected Design Option'}
            </h2>
            <p className="text-xs text-slate-400">
              {layout.description || 'Optimized layout designed for your plot.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-white/5 text-slate-200">
              {bedsCount} BHK
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-white/5 text-slate-200">
              {layout.floors === 1 ? 'Ground Only' : `Ground + ${layout.floors - 1}`}
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-white/5 text-slate-200">
              Built-up: {buaSqFt.toLocaleString()} sq ft
            </span>
            <span className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-white/5 text-slate-200">
              Parking: 1 Car
            </span>
          </div>
        </div>

        {/* 2. MAIN COST HERO CARD */}
        <div className="rounded-2xl bg-gradient-to-br from-blue-950/40 via-slate-900/80 to-slate-900/90 border border-blue-500/30 p-6 lg:p-8 space-y-6 shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                  Estimated Construction Cost
                </span>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Preliminary Estimate
                </span>
              </div>
              <div className="text-4xl lg:text-5xl font-display font-bold text-white font-mono tracking-tight">
                {formatINR(totalCost)}
              </div>
              <div className="text-xs font-mono text-cyan-400 mt-2 flex items-center gap-2">
                <span>Approx. ₹ {costPerSqFt.toLocaleString()} / sq ft</span>
                <span>•</span>
                <span className="text-slate-300">
                  Estimated Range: ₹ {lowRangeLakh} Lakh — ₹ {highRangeLakh} Lakh
                </span>
              </div>
            </div>

            {/* Quality Tier Selector */}
            <div className="p-3 rounded-xl bg-slate-950/70 border border-white/10 space-y-2 shrink-0">
              <span className="text-[10px] font-mono text-slate-400 uppercase block font-semibold">
                Finish Specification Tier:
              </span>
              <div className="flex rounded-lg bg-slate-900 p-1 border border-white/5 gap-1">
                {[
                  { id: 'STANDARD', label: 'Standard' },
                  { id: 'PREMIUM', label: 'Premium' },
                  { id: 'LUXURY', label: 'Luxury' }
                ].map((tier) => (
                  <button
                    key={tier.id}
                    onClick={() => onUpdateTier(tier.id)}
                    className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                      currentTier === tier.id
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {tier.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Preliminary Notice */}
          <div className="p-3.5 rounded-xl bg-slate-950/50 border border-white/5 text-xs text-slate-400 leading-relaxed flex items-start gap-2.5">
            <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
            <p>
              Final cost may change after professional structural design, site soil testing, detailed finishes specification, and contractor quotations.
            </p>
          </div>
        </div>

        {/* 3. SIMPLE COST BREAKDOWN */}
        <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Cost Breakdown by Major Category</h3>
              <p className="text-xs text-slate-400">Summarized from model-linked Bill of Quantities</p>
            </div>

            <button
              onClick={() => setIsBOQModalOpen(true)}
              className="text-xs px-3.5 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-white/10 flex items-center gap-1.5 transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
              <span>View Detailed BOQ</span>
            </button>
          </div>

          {/* Visual Percentage Bar */}
          <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden flex">
            {breakdown.map((item) => (
              <div
                key={`bar-${item.id}`}
                style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                title={`${item.name}: ${item.percent}%`}
                className="h-full transition-all duration-500"
              />
            ))}
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
            {breakdown.map((cat) => (
              <div
                key={cat.id}
                className="p-4 rounded-xl bg-slate-900/60 border border-white/5 hover:border-white/15 transition-all flex flex-col justify-between space-y-2"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }} />
                      {cat.name}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {cat.percent}%
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight">
                    {cat.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-white/5">
                  <span className="text-sm font-bold font-mono text-slate-100">
                    {formatINR(cat.amount)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 5. "HOW WAS THIS CALCULATED?" COLLAPSIBLE */}
        <div className="rounded-2xl bg-slate-900/40 border border-white/10 p-5 space-y-3">
          <button
            onClick={() => setShowCalculationDetails(!showCalculationDetails)}
            className="w-full flex items-center justify-between text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
          >
            <span className="flex items-center gap-2">
              <Info className="w-4 h-4" />
              <span>How was this calculated?</span>
            </span>
            {showCalculationDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showCalculationDetails && (
            <div className="pt-3 space-y-4 text-xs text-slate-300 animate-fade-in border-t border-white/5">
              <p className="leading-relaxed text-slate-400">
                Planwise links every 3D element in your house design directly to deterministic Indian Standard (IS 1200) measurement rules and local schedule of rates:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">1. Model Geometry</span>
                  <span className="text-slate-400">Wall surface areas, slab concrete volumes, column heights extracted directly from the Canonical Building Model.</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">2. Material Assemblies</span>
                  <span className="text-slate-400">Bricks, cement bags, steel rebar, and aggregate calculated with standard IS wastage allowances.</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">3. Labour & Equipment</span>
                  <span className="text-slate-400">Masons, bar-benders, helpers, and shuttering equipment estimated by work-package productivity norms.</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-white/5">
                  <span className="text-white font-semibold block mb-0.5">4. Rate Snapshot</span>
                  <span className="text-slate-400">Authoritative baseline rates: <strong className="text-slate-200">{boq.rateSnapshotId || 'Mumbai 2026 Q4'}</strong>.</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 6. EXPORT ACTIONS & TECHNICAL DETAILS */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-3">
            <button
              onClick={downloadCSV}
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>Download BOQ (CSV)</span>
            </button>
            <span>•</span>
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
              <span>Open Detailed M3 Cost Engine</span>
            </button>
          )}
        </div>

        {/* 7. PROFESSIONAL NOTICE & PRIMARY CTA FOOTER */}
        <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="text-xs text-slate-400 leading-relaxed max-w-md">
            <span className="text-white font-semibold block mb-1">Ready to review project build scope?</span>
            This estimate moves to project readiness checklist. Final construction begins only after licensed professional verification.
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={onProceedToBuild}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-display font-semibold text-sm shadow-xl shadow-blue-500/25 flex items-center justify-center gap-2 transition-all hover:scale-[1.01]"
            >
              <span>Review & Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>

      {/* Detailed BOQ Table Modal */}
      {isBOQModalOpen && (
        <BOQTableModal
          option={selectedOption}
          onClose={() => setIsBOQModalOpen(false)}
        />
      )}
    </div>
  );
};
