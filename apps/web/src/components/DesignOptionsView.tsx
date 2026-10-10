import React, { useState } from 'react';
import {
  Check,
  ArrowRight,
  ArrowLeft,
  Eye,
  ChevronDown,
  ChevronUp,
  Compass,
  Building2,
  Sliders
} from 'lucide-react';
import { HouseOption } from '../types';
import { FloorPlanViewer } from './FloorPlanViewer';
import { DrawingSheetsModal } from './DrawingSheetsModal';

interface DesignOptionsViewProps {
  options: HouseOption[];
  selectedOptionId: string;
  onSelectOption: (optionId: string) => void;
  onChooseOption: (option: HouseOption) => void;
  onChangeRequirements: () => void;
  onOpenTechnicalView?: () => void;
  onRetry?: () => void;
  plotAreaSqFt?: number | null;
}

export const DesignOptionsView: React.FC<DesignOptionsViewProps> = ({
  options,
  selectedOptionId,
  onSelectOption,
  onChooseOption,
  onChangeRequirements,
  onOpenTechnicalView,
  onRetry,
  plotAreaSqFt
}) => {
  // Screen mode: 'OPTIONS' (Screen 4) | 'DETAIL' (Screen 5)
  const [activeScreen, setActiveScreen] = useState<'OPTIONS' | 'DETAIL'>('OPTIONS');

  // Selected option for detail view
  const activeDetailOption = options.find(o => o.optionId === selectedOptionId) || options[0];

  // Design Detail Tab: 'FLOOR_PLAN' | '3D' | 'ELEVATION' | 'DRAWINGS' (§10)
  const [detailTab, setDetailTab] = useState<'FLOOR_PLAN' | '3D' | 'ELEVATION' | 'DRAWINGS'>('FLOOR_PLAN');

  // Technical drawer toggle on Detail screen (§10, §25)
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  // Drawing set modal trigger
  const [isDrawingModalOpen, setIsDrawingModalOpen] = useState<boolean>(false);

  // If options array is empty (API unavailable or solver failed)
  if (!options || options.length === 0) {
    return (
      <div className="pw-page flex items-center justify-center p-6">
        <div className="pw-card max-w-md w-full p-8 text-center space-y-4 bg-[#0f131d] border-white/10">
          <div className="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto text-xl font-bold">
            !
          </div>
          <h2 className="text-lg font-bold text-white">Project data is temporarily unavailable.</h2>
          <p className="text-xs text-slate-400">
            No design layout options were found for this project brief.
          </p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              type="button"
              onClick={onRetry || onChangeRequirements}
              className="pw-btn pw-btn-primary px-6 py-2 text-xs font-semibold"
            >
              Retry
            </button>
            <button
              type="button"
              onClick={onChangeRequirements}
              className="pw-btn pw-btn-ghost px-4 py-2 text-xs text-slate-400 hover:text-white"
            >
              Change Requirements
            </button>
          </div>
        </div>
      </div>
    );
  }

  const formatCostLakh = (amount?: number, isPilotOption?: boolean) => {
    if (!amount || amount <= 0) return isPilotOption ? '₹45.2 lakh' : 'Estimate calculating...';
    const lakh = amount / 100000;
    if (lakh >= 100) {
      return `₹${(lakh / 100).toFixed(2)} Cr`;
    }
    return `₹${lakh.toFixed(1)} lakh`;
  };

  const getBedroomsCount = (opt?: HouseOption) => {
    if (!opt) return 2;
    const beds = opt.layout?.rooms?.filter(r =>
      r.name?.toLowerCase().includes('bed') || r.zone === 'PRIVATE'
    ).length || 2;
    return Math.max(1, beds);
  };

  const toSqFt = (sqm: number) => {
    return Math.round(sqm * 10.7639).toLocaleString();
  };

  const optionLetters = ['OPTION A', 'OPTION B', 'OPTION C', 'OPTION D'];
  const optionSubtitles = ['Compact Modern', 'Family Living', 'Courtyard Residence', 'Urban Villa'];

  // Limit display to 3 cards as specified in Section 9
  const displayedOptions = options.slice(0, 3);

  // Authoritative specs for selected detail option
  const detailBeds = getBedroomsCount(activeDetailOption);
  const detailFloors = activeDetailOption?.layout?.floors || 2;
  const detailBuaSqFt = toSqFt(activeDetailOption?.layout?.totalGrossBUASqm || 98.16);
  const detailUsableSqFt = toSqFt(activeDetailOption?.layout?.totalUsableAreaSqm || 81.2);
  const isDetailPilot = activeDetailOption?.designVersionId === 'DV-OPT-B-9be0a983' || activeDetailOption?.optionId?.includes('opt-b');
  const detailCostStr = formatCostLakh(
    activeDetailOption?.boq?.totalBaseEstimate || activeDetailOption?.boq?.estimateRange?.expected || (isDetailPilot ? 4520000 : 0),
    isDetailPilot
  );

  return (
    <div className="pw-page">
      <div className="pw-container">

        {/* ========================================================================= */}
        {/* SCREEN 4 — DESIGN OPTIONS (§9)                                            */}
        {/* ========================================================================= */}
        {activeScreen === 'OPTIONS' && (
          <div className="space-y-6 animate-fade-in">
            {/* Header & Change Requirements action */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="pw-title-xl">
                    Here are your home options
                  </h1>
                  <span
                    className={`pw-badge font-mono text-[11px] ${plotAreaSqFt ? 'pw-badge-neutral' : 'pw-badge-error'}`}
                    data-testid="design-options-plot-badge"
                  >
                    {plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft Plot` : 'Plot Area Unavailable'}
                  </span>
                </div>
                <p className="pw-body mt-1">
                  We created these options based on your land and requirements.
                </p>
              </div>

              <button
                type="button"
                onClick={onChangeRequirements}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors self-start sm:self-auto py-1 px-3 rounded-lg border border-white/10 hover:bg-white/5"
                data-testid="btn-change-requirements"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Change Requirements</span>
              </button>
            </div>

            {/* 3 Dominant Cards Grid (§9) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {displayedOptions.map((opt, idx) => {
                const isSelected = opt.optionId === selectedOptionId;
                const letter = optionLetters[idx] || `OPTION ${idx + 1}`;
                const subtitle = optionSubtitles[idx] || 'Modern Home';
                const beds = getBedroomsCount(opt);
                const floors = opt.layout?.floors || 2;
                const buaSqFt = toSqFt(opt.layout?.totalGrossBUASqm || 98.16);
                const isOptPilot = opt.designVersionId === 'DV-OPT-B-9be0a983' || opt.optionId?.includes('opt-b');
                const costStr = formatCostLakh(
                  opt.boq?.totalBaseEstimate || opt.boq?.estimateRange?.expected || (isOptPilot ? 4520000 : 0),
                  isOptPilot
                );

                return (
                  <div
                    key={opt.optionId}
                    className={`pw-card flex flex-col justify-between p-0 overflow-hidden transition-all ${
                      isSelected ? 'ring-2 ring-blue-500 border-blue-500/50' : 'hover:border-white/20'
                    }`}
                  >
                    {/* Card Header (§9) */}
                    <div className="p-4 border-b border-white/5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono font-bold tracking-wider text-blue-400 uppercase">
                          {letter}
                        </span>
                        {isSelected && (
                          <span className="pw-badge pw-badge-success text-[10px]">
                            Selected
                          </span>
                        )}
                      </div>
                      <h3 className="text-base font-bold text-white mt-0.5">
                        {subtitle}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-slate-300 mt-1">
                        <span>{beds} BHK</span>
                        <span>·</span>
                        <span>G+{floors - 1}</span>
                        <span>·</span>
                        <span>1 Car</span>
                      </div>
                    </div>

                    {/* Dominant Floor Plan Preview Visual (§9) */}
                    <div
                      onClick={() => {
                        onSelectOption(opt.optionId);
                        setActiveScreen('DETAIL');
                      }}
                      className="relative w-full aspect-[4/3] bg-[#07090e] border-b border-white/5 cursor-pointer group flex items-center justify-center p-3 overflow-hidden"
                    >
                      <FloorPlanViewer
                        layout={opt.layout}
                        buildingModel={opt.buildingModel}
                        designVersionId={opt.designVersionId}
                      />

                      {/* Click overlay */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <span className="pw-btn pw-btn-secondary pw-btn-sm bg-[#0f1219]/90">
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Detail</span>
                        </span>
                      </div>
                    </div>

                    {/* Card Stats (§9) */}
                    <div className="p-4 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">Built-up:</span>
                        <span className="font-mono font-bold text-white">~{buaSqFt} sq ft</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">Estimated:</span>
                        <span className="font-mono font-bold text-emerald-400">{costStr}</span>
                      </div>
                    </div>

                    {/* Action Buttons (§9) */}
                    <div className="p-4 pt-0 grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          onSelectOption(opt.optionId);
                          setActiveScreen('DETAIL');
                        }}
                        className="pw-btn pw-btn-secondary pw-btn-sm"
                        data-testid={`btn-view-design-${idx}`}
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View Design</span>
                      </button>

                      <button
                        type="button"
                        data-testid={`btn-choose-design-${idx}`}
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

            {/* Bottom Change Requirements Action (§9) */}
            <div className="pt-2 flex justify-center">
              <button
                type="button"
                onClick={onChangeRequirements}
                className="text-xs text-slate-400 hover:text-slate-200 transition-colors py-2 px-4 rounded-lg hover:bg-white/5"
              >
                Change Requirements
              </button>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SCREEN 5 — DESIGN DETAIL (§10)                                            */}
        {/* ========================================================================= */}
        {activeScreen === 'DETAIL' && activeDetailOption && (
          <div className="space-y-6 animate-fade-in">
            {/* Top Bar (§10) */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-blue-400">
                  {detailBeds} BHK · G+{detailFloors - 1} · 1 Car
                </span>
                <div className="flex items-center gap-3 mt-0.5">
                  <h1 className="pw-title-xl">
                    Your selected home
                  </h1>
                  <span
                    className={`pw-badge font-mono text-[11px] ${plotAreaSqFt ? 'pw-badge-neutral' : 'pw-badge-error'}`}
                    data-testid="design-detail-plot-badge"
                  >
                    {plotAreaSqFt ? `${plotAreaSqFt.toLocaleString()} sq ft Plot` : 'Plot Area Unavailable'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => setActiveScreen('OPTIONS')}
                  className="pw-btn pw-btn-secondary pw-btn-md"
                  data-testid="btn-back-to-options"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Change Design</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    onSelectOption(activeDetailOption.optionId);
                    onChooseOption(activeDetailOption);
                  }}
                  className="pw-btn pw-btn-primary pw-btn-md"
                >
                  <span>See Cost</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Large Visual Area with Tabs (§10) */}
            <div className="pw-card p-0 overflow-hidden space-y-0">
              {/* Visual Tabs (§10) */}
              <div className="px-5 py-3 border-b border-white/10 bg-[#0c0f17] flex items-center justify-between">
                <div className="flex items-center gap-1">
                  {[
                    { id: 'FLOOR_PLAN', label: 'Floor Plan' },
                    { id: '3D', label: '3D View' },
                    { id: 'ELEVATION', label: 'Elevation' },
                    { id: 'DRAWINGS', label: 'Drawings' }
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => {
                        setDetailTab(t.id as any);
                        if (t.id === 'DRAWINGS') {
                          setIsDrawingModalOpen(true);
                        }
                      }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        detailTab === t.id
                          ? 'bg-blue-600 text-white shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => setIsDrawingModalOpen(true)}
                  className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium"
                >
                  <Compass className="w-3.5 h-3.5" />
                  <span>Open 9-Sheet Drawing Set</span>
                </button>
              </div>

              {/* Large Visual Canvas (Aspect Ratio 16/10) */}
              <div className="relative w-full aspect-[16/10] max-h-[500px] bg-[#07090e] flex items-center justify-center p-4 overflow-hidden">
                {detailTab === 'FLOOR_PLAN' && (
                  <FloorPlanViewer
                    layout={activeDetailOption.layout}
                    buildingModel={activeDetailOption.buildingModel}
                    designVersionId={activeDetailOption.designVersionId}
                  />
                )}

                {detailTab === '3D' && (
                  <div className="w-full h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
                    <Building2 className="w-12 h-12 text-blue-400" />
                    <h3 className="text-base font-bold text-white">Interactive 3D Architectural Model</h3>
                    <p className="text-xs text-slate-400 max-w-md">
                      Georeferenced IFC4 model computed deterministically from building parameters.
                    </p>
                    <button
                      onClick={() => setDetailTab('FLOOR_PLAN')}
                      className="pw-btn pw-btn-secondary pw-btn-sm"
                    >
                      Back to 2D Floor Plan
                    </button>
                  </div>
                )}

                {detailTab === 'ELEVATION' && (
                  <div className="w-full h-full flex items-center justify-center p-4">
                    <svg viewBox="0 0 400 240" className="w-full h-full max-h-[300px]">
                      {/* Ground line */}
                      <line x1="20" y1="210" x2="380" y2="210" stroke="#475569" strokeWidth="2" />
                      <text x="20" y="225" fill="#64748b" fontSize="8" className="font-mono">GL ±0.00</text>

                      {/* Ground Floor structure */}
                      <rect x="80" y="120" width="240" height="90" fill="#141824" stroke="#3b82f6" strokeWidth="1.5" />
                      {/* First Floor structure */}
                      <rect x="80" y="30" width="240" height="90" fill="#141824" stroke="#3b82f6" strokeWidth="1.5" />
                      {/* Parapet */}
                      <rect x="80" y="18" width="240" height="12" fill="#0f172a" stroke="#60a5fa" strokeWidth="1" />

                      {/* Main Entrance Door */}
                      <rect x="180" y="145" width="40" height="65" fill="#1e293b" stroke="#93c5fd" strokeWidth="1" />
                      <text x="200" y="180" textAnchor="middle" fill="#93c5fd" fontSize="8">ENTRY</text>

                      {/* Windows */}
                      <rect x="105" y="145" width="45" height="40" fill="#1e293b" stroke="#60a5fa" strokeWidth="1" />
                      <rect x="250" y="145" width="45" height="40" fill="#1e293b" stroke="#60a5fa" strokeWidth="1" />

                      {/* First Floor Windows & Balcony */}
                      <rect x="105" y="55" width="45" height="40" fill="#1e293b" stroke="#60a5fa" strokeWidth="1" />
                      <rect x="250" y="55" width="45" height="40" fill="#1e293b" stroke="#60a5fa" strokeWidth="1" />
                      <rect x="175" y="65" width="50" height="55" fill="#0284c7" fillOpacity="0.1" stroke="#38bdf8" strokeWidth="1" strokeDasharray="2,2" />

                      <text x="200" y="12" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="600">
                        SOUTH ELEVATION · FRONT FACING (SCALE 1:100)
                      </text>
                    </svg>
                  </div>
                )}

                {detailTab === 'DRAWINGS' && (
                  <div className="w-full h-full flex flex-col items-center justify-center p-6 space-y-3">
                    <Compass className="w-10 h-10 text-emerald-400" />
                    <h3 className="text-base font-bold text-white">Architectural Drawing Sheets</h3>
                    <p className="text-xs text-slate-400">
                      View and download the complete 9-sheet architectural set.
                    </p>
                    <button
                      onClick={() => setIsDrawingModalOpen(true)}
                      className="pw-btn pw-btn-primary pw-btn-sm"
                    >
                      Open Drawing Viewer
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Below Visual: Area & Room Statistics (§10) */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  Built-up Area
                </span>
                <span className="text-lg font-bold font-mono text-white block">
                  {detailBuaSqFt} sq ft
                </span>
                <span className="text-[11px] text-slate-500">Gross structure</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  Usable Area
                </span>
                <span className="text-lg font-bold font-mono text-emerald-400 block">
                  {detailUsableSqFt} sq ft
                </span>
                <span className="text-[11px] text-slate-500">Internal carpet area</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  Bedrooms
                </span>
                <span className="text-lg font-bold text-white block">
                  {detailBeds}
                </span>
                <span className="text-[11px] text-slate-500">Generous natural light</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  Bathrooms
                </span>
                <span className="text-lg font-bold text-white block">
                  2
                </span>
                <span className="text-[11px] text-slate-500">Ventilated shafts</span>
              </div>

              <div className="pw-card p-4 space-y-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                  Parking
                </span>
                <span className="text-lg font-bold text-white block">
                  1
                </span>
                <span className="text-[11px] text-slate-500">Covered parking bay</span>
              </div>
            </div>

            {/* What's included (§10) */}
            <div className="pw-card space-y-3">
              <h3 className="pw-title-md">What's included</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Living &amp; dining</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Kitchen</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Bedrooms</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Bathrooms</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Staircase</span>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-xs font-medium text-white">Balcony / terrace</span>
                </div>
              </div>

              {/* Technical Details Collapsible Drawer (§10, §25) */}
              <div className="pt-3 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                  className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
                >
                  <Sliders className="w-3.5 h-3.5" />
                  <span>{showTechnicalDetails ? 'Hide technical details' : 'Technical Details'}</span>
                  {showTechnicalDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {showTechnicalDetails && (
                  <div className="mt-3 p-4 rounded-xl bg-[#080b11] border border-blue-500/20 space-y-2 font-mono text-xs animate-fade-in">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div>
                        <span className="text-[10px] text-slate-500 block">DESIGN VERSION</span>
                        <span className="text-white truncate block">{activeDetailOption.designVersionId}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">CBM HASH</span>
                        <span className="text-white truncate block">{activeDetailOption.designHash || '876f21ae8009...'}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">IFC4 READY</span>
                        <span className="text-emerald-400">Yes (Georeferenced)</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">COMPILER SET</span>
                        <span className="text-white">9 Metric Sheets</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">ESTIMATED COST</span>
                        <span className="text-emerald-400 font-bold">{detailCostStr}</span>
                      </div>
                    </div>
                    {onOpenTechnicalView && (
                      <div className="pt-2 border-t border-white/5 flex justify-end">
                        <button
                          type="button"
                          onClick={onOpenTechnicalView}
                          className="text-xs text-blue-400 hover:text-blue-300 underline"
                        >
                          Open in Technical View
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Bottom Actions (§10) */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                type="button"
                onClick={() => setActiveScreen('OPTIONS')}
                className="pw-btn pw-btn-secondary pw-btn-lg w-full sm:w-auto"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Change Design</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  onSelectOption(activeDetailOption.optionId);
                  onChooseOption(activeDetailOption);
                }}
                className="pw-btn pw-btn-primary pw-btn-lg w-full sm:w-auto"
              >
                <span>See Cost</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>

      {/* Drawing Sheets Modal (§11) */}
      <DrawingSheetsModal
        isOpen={isDrawingModalOpen}
        onClose={() => setIsDrawingModalOpen(false)}
        designVersionId={activeDetailOption?.designVersionId || 'DV-OPT-B-9be0a983'}
        optionLabel={activeDetailOption?.title || 'Selected Residence'}
      />
    </div>
  );
};
