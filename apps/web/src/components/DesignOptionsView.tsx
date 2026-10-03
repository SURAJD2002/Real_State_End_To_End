import React, { useState } from 'react';
import { 
  Car, 
  Check, 
  ArrowRight, 
  ArrowLeft, 
  Eye, 
  X,
  Sliders
} from 'lucide-react';
import { HouseOption } from '../types';
import { FloorPlanViewer } from './FloorPlanViewer';

interface DesignOptionsViewProps {
  options: HouseOption[];
  selectedOptionId: string;
  onSelectOption: (optionId: string) => void;
  onChooseOption: (option: HouseOption) => void;
  onChangeRequirements: () => void;
  onOpenTechnicalView?: () => void;
}

export const DesignOptionsView: React.FC<DesignOptionsViewProps> = ({
  options,
  selectedOptionId,
  onSelectOption,
  onChooseOption,
  onChangeRequirements,
  onOpenTechnicalView
}) => {
  // Detail Modal state (§12)
  const [activeModalOption, setActiveModalOption] = useState<HouseOption | null>(null);
  const [modalTab, setModalTab] = useState<'OVERVIEW' | 'FLOOR_PLAN' | '3D' | 'SPACES' | 'MATERIALS' | 'COST'>('OVERVIEW');

  const formatCostLakh = (amount: number) => {
    if (!amount) return '₹45.2 Lakh';
    const lakh = amount / 100000;
    if (lakh >= 100) {
      return `₹${(lakh / 100).toFixed(2)} Cr`;
    }
    return `₹${lakh.toFixed(1)} Lakh`;
  };

  const getBedroomsCount = (opt: HouseOption) => {
    const beds = opt.layout?.rooms?.filter(r => 
      r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE'
    ).length || 2;
    return Math.max(1, beds);
  };

  const toSqFt = (sqm: number) => {
    return Math.round(sqm * 10.7639).toLocaleString();
  };

  const optionLetters = ['Option A', 'Option B', 'Option C', 'Option D', 'Option E'];
  const lifestyleTags = [
    'Family living',
    'Rental / Dual occupancy',
    'Open courtyard living',
    'Compact urban layout'
  ];

  return (
    <div className="pw-page">
      <div className="pw-container-wide">
        
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onChangeRequirements}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Change Requirements</span>
          </button>

          <span className="pw-badge pw-badge-neutral">
            Step 3 of 6: Design Options
          </span>
        </div>

        {/* Header (§11) */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
          <div>
            <h1 className="pw-title-xl">
              Choose your house design
            </h1>
            <p className="pw-body mt-1">
              Architectural options tailored to your 1,100 sq ft plot and municipal setbacks.
            </p>
          </div>

          <span className="pw-badge pw-badge-primary self-start sm:self-auto font-mono">
            {options.length} Options Generated
          </span>
        </div>

        {/* Large Architectural Cards Grid (§11) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {options.map((opt, idx) => {
            const isSelected = opt.optionId === selectedOptionId;
            const letter = optionLetters[idx] || `Option ${idx + 1}`;
            const beds = getBedroomsCount(opt);
            const floors = opt.layout?.floors || 2;
            const buaSqFt = toSqFt(opt.layout?.totalGrossBUASqm || 116);
            const costStr = formatCostLakh(opt.boq?.totalBaseEstimate || opt.boq?.estimateRange?.expected || 4520000);
            const tag = lifestyleTags[idx % lifestyleTags.length];

            return (
              <div
                key={opt.optionId}
                className={`pw-card flex flex-col justify-between p-0 overflow-hidden transition-all ${
                  isSelected ? 'pw-card-selected' : 'hover:border-white/20'
                }`}
              >
                {/* Card Header */}
                <div className="p-4 border-b border-white/5 flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-display font-bold text-sm text-white">
                        {letter}
                      </span>
                      <span className="text-slate-500">·</span>
                      <span className="text-xs text-slate-300 font-medium">
                        {beds} BHK · G+{floors - 1}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-0.5 block">
                      {opt.layout?.label || 'Residential Villa'}
                    </span>
                  </div>

                  {isSelected && (
                    <span className="pw-badge pw-badge-success text-[10px]">
                      Selected
                    </span>
                  )}
                </div>

                {/* Floor Plan / 3D Visual Preview Canvas (§11) */}
                <div 
                  onClick={() => {
                    setActiveModalOption(opt);
                    setModalTab('OVERVIEW');
                  }}
                  className="relative w-full aspect-[4/3] bg-[#0c0e13] border-b border-white/5 cursor-pointer group flex items-center justify-center p-3 overflow-hidden"
                >
                  <FloorPlanViewer
                    layout={opt.layout}
                    buildingModel={opt.buildingModel}
                    designVersionId={opt.designVersionId}
                  />

                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <span className="pw-btn pw-btn-secondary pw-btn-sm bg-[#12151c]/90">
                      <Eye className="w-3.5 h-3.5" />
                      <span>Inspect Plan</span>
                    </span>
                  </div>
                </div>

                {/* Card Body Metrics */}
                <div className="p-4 space-y-3">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-[11px] text-slate-500 block">Built-up area</span>
                      <span className="font-mono font-bold text-white text-sm">
                        {buaSqFt} sq ft
                      </span>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-500 block">Estimated cost</span>
                      <span className="font-mono font-bold text-emerald-400 text-sm">
                        {costStr}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-2 border-t border-white/5">
                    <div className="flex items-center gap-1.5 text-slate-300">
                      <Car className="w-3.5 h-3.5 text-slate-400" />
                      <span>1 car parking</span>
                    </div>
                    <span className="text-[11px] text-slate-400">
                      Good for: <strong className="text-slate-200 font-medium">{tag}</strong>
                    </span>
                  </div>
                </div>

                {/* Card Actions (§11) */}
                <div className="p-4 pt-0 grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setActiveModalOption(opt);
                      setModalTab('OVERVIEW');
                    }}
                    className="pw-btn pw-btn-secondary pw-btn-sm"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Design</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      onSelectOption(opt.optionId);
                      onChooseOption(opt);
                    }}
                    className="pw-btn pw-btn-primary pw-btn-sm"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Choose This</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Technical GIS Link */}
        {onOpenTechnicalView && (
          <div className="pt-2 flex justify-start">
            <button
              onClick={onOpenTechnicalView}
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Inspect CP-SAT solver Pareto frontier in Technical View</span>
            </button>
          </div>
        )}

      </div>

      {/* ========================================================================= */}
      {/* DESIGN DETAIL MODAL (§12) */}
      {/* ========================================================================= */}
      {activeModalOption && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="pw-card w-full max-w-5xl h-[85vh] p-0 flex flex-col overflow-hidden animate-fade-in border-white/15">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-[#10131a]">
              <div className="flex items-center gap-3">
                <h3 className="pw-title-md">
                  {activeModalOption.layout?.label || 'Design Option Details'}
                </h3>
                <span className="pw-badge pw-badge-neutral font-mono">
                  {getBedroomsCount(activeModalOption)} BHK · G+{(activeModalOption.layout?.floors || 2) - 1} · {toSqFt(activeModalOption.layout?.totalGrossBUASqm || 116)} sq ft
                </span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    onSelectOption(activeModalOption.optionId);
                    onChooseOption(activeModalOption);
                    setActiveModalOption(null);
                  }}
                  className="pw-btn pw-btn-primary pw-btn-sm"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Choose This Design</span>
                </button>

                <button
                  onClick={() => setActiveModalOption(null)}
                  className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-white/10 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modal Tabs (§12) */}
            <div className="px-6 border-b border-white/10 flex items-center gap-1 bg-[#0d1017]">
              {[
                { id: 'OVERVIEW', label: 'Overview' },
                { id: 'FLOOR_PLAN', label: 'Floor Plan' },
                { id: '3D', label: '3D Model' },
                { id: 'SPACES', label: 'Spaces' },
                { id: 'MATERIALS', label: 'Materials' },
                { id: 'COST', label: 'Cost Breakdown' }
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setModalTab(t.id as any)}
                  className={`px-3 py-2.5 text-xs font-semibold border-b-2 transition-all ${
                    modalTab === t.id
                      ? 'border-blue-500 text-white'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6 bg-[#0a0d13]">
              {/* TAB 1: OVERVIEW */}
              {modalTab === 'OVERVIEW' && (
                <div className="space-y-6">
                  {/* Summary Bar */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="pw-metric-card">
                      <span className="pw-metric-card-label">Typology</span>
                      <span className="pw-metric-card-value">{getBedroomsCount(activeModalOption)} BHK</span>
                      <span className="pw-metric-card-sub">G+{(activeModalOption.layout?.floors || 2) - 1} Storeys</span>
                    </div>
                    <div className="pw-metric-card">
                      <span className="pw-metric-card-label">Built-Up Area</span>
                      <span className="pw-metric-card-value font-mono">{toSqFt(activeModalOption.layout?.totalGrossBUASqm || 116)}</span>
                      <span className="pw-metric-card-sub">sq ft total BUA</span>
                    </div>
                    <div className="pw-metric-card">
                      <span className="pw-metric-card-label">Estimated Cost</span>
                      <span className="pw-metric-card-value font-mono text-emerald-400">
                        {formatCostLakh(activeModalOption.boq?.totalBaseEstimate || 4520000)}
                      </span>
                      <span className="pw-metric-card-sub">Standard quality tier</span>
                    </div>
                    <div className="pw-metric-card">
                      <span className="pw-metric-card-label">Parking</span>
                      <span className="pw-metric-card-value">1 Car</span>
                      <span className="pw-metric-card-sub">Dedicated covered space</span>
                    </div>
                  </div>

                  {/* Room Breakdown (§12) */}
                  <div className="pw-card">
                    <h4 className="pw-title-md mb-3">Included Spaces</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {(activeModalOption.layout?.rooms || [
                        { name: 'Living & Dining', areaSqm: 24 },
                        { name: 'Kitchen', areaSqm: 10 },
                        { name: 'Master Bedroom', areaSqm: 16 },
                        { name: 'Bedroom 2', areaSqm: 13 },
                        { name: 'Bathrooms (2)', areaSqm: 8 },
                        { name: 'Balcony & Foyer', areaSqm: 9 }
                      ]).map((r: any, i: number) => (
                        <div key={i} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center justify-between">
                          <span className="text-xs text-white font-medium">{r.name}</span>
                          <span className="text-xs font-mono text-slate-400">
                            {r.areaSqm ? Math.round(r.areaSqm * 10.7639) : '—'} sq ft
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2 & 3: FLOOR PLAN & 3D */}
              {(modalTab === 'FLOOR_PLAN' || modalTab === '3D') && (
                <div className="w-full h-full min-h-[420px] rounded-lg border border-white/10 overflow-hidden bg-black">
                  <FloorPlanViewer
                    layout={activeModalOption.layout}
                    buildingModel={activeModalOption.buildingModel}
                    designVersionId={activeModalOption.designVersionId}
                  />
                </div>
              )}

              {/* TAB 4: SPACES */}
              {modalTab === 'SPACES' && (
                <div className="pw-card space-y-4">
                  <h4 className="pw-title-md">Architectural Room Dimensions</h4>
                  <div className="space-y-2">
                    {(activeModalOption.layout?.rooms || []).map((r, i) => (
                      <div key={i} className="p-3 rounded-lg bg-white/[0.02] border border-white/5 flex items-center justify-between text-xs">
                        <div>
                          <span className="text-white font-semibold">{r.name}</span>
                          <span className="text-slate-500 ml-2">Zone: {r.zone || 'Habitable'}</span>
                        </div>
                        <span className="font-mono text-slate-300">
                          {r.areaSqm ? Math.round(r.areaSqm * 10.7639) : '—'} sq ft
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 5: MATERIALS */}
              {modalTab === 'MATERIALS' && (
                <div className="pw-card space-y-4">
                  <h4 className="pw-title-md">Standard Quality Specifications</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                      <span className="text-slate-400 block font-semibold uppercase tracking-wider text-[10px]">Structure</span>
                      <span className="text-white">RCC Framed Structure with IS 456 M25 concrete &amp; Fe500 TMT steel.</span>
                    </div>
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                      <span className="text-slate-400 block font-semibold uppercase tracking-wider text-[10px]">Flooring</span>
                      <span className="text-white">Vitrified tiles (800mm × 800mm) in living/dining; anti-skid in bathrooms.</span>
                    </div>
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                      <span className="text-slate-400 block font-semibold uppercase tracking-wider text-[10px]">Windows</span>
                      <span className="text-white">Powder-coated aluminium 3-track sliding windows with mosquito mesh.</span>
                    </div>
                    <div className="p-3 rounded-lg bg-white/[0.02] border border-white/5 space-y-1">
                      <span className="text-slate-400 block font-semibold uppercase tracking-wider text-[10px]">Plumbing &amp; Electrical</span>
                      <span className="text-white">Concealed CPVC piping (Astral/Ashirvad) &amp; modular switches (Legrand/Schneider).</span>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 6: COST */}
              {modalTab === 'COST' && (
                <div className="pw-card space-y-4">
                  <h4 className="pw-title-md">Preliminary Cost Summary</h4>
                  <div className="p-4 rounded-lg bg-black/30 border border-white/5 flex items-center justify-between">
                    <div>
                      <span className="text-xs text-slate-400 block">Total Base Estimate</span>
                      <span className="font-mono text-xl font-bold text-emerald-400">
                        {formatCostLakh(activeModalOption.boq?.totalBaseEstimate || 4520000)}
                      </span>
                    </div>
                    <button
                      onClick={() => {
                        onSelectOption(activeModalOption.optionId);
                        onChooseOption(activeModalOption);
                        setActiveModalOption(null);
                      }}
                      className="pw-btn pw-btn-primary"
                    >
                      <span>Proceed to Full Cost Sheet</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
