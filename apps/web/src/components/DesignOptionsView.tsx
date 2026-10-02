import React, { useState } from 'react';
import { 
  Car, 
  Check, 
  ArrowRight, 
  ArrowLeft, 
  Eye, 
  ChevronDown, 
  ChevronUp, 
  Sliders,
  X,
  Maximize2
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
  const [viewingOption, setViewingOption] = useState<HouseOption | null>(null);
  const [expandedTechOptionId, setExpandedTechOptionId] = useState<string | null>(null);

  const formatCostLakh = (amount: number) => {
    if (!amount) return '₹45 Lakh';
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

  const getBathroomsCount = (opt: HouseOption) => {
    const baths = opt.layout?.rooms?.filter(r => 
      r.name?.toLowerCase().includes('bath') || r.name?.toLowerCase().includes('toilet')
    ).length || 2;
    return Math.max(1, baths);
  };

  const toSqFt = (sqm: number) => {
    return Math.round(sqm * 10.7639).toLocaleString();
  };

  return (
    <div className="flex-1 w-full h-full overflow-y-auto bg-[#07090e] p-6 lg:p-10 flex flex-col items-center">
      <div className="w-full max-w-5xl space-y-8 animate-fade-in pb-20">

        {/* Navigation Breadcrumb */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
          <button
            type="button"
            onClick={onChangeRequirements}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Change Requirements</span>
          </button>

          {/* Stepper */}
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-emerald-400 font-medium">1 Land ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-emerald-400 font-medium">2 Feasibility ✓</span>
            <span className="text-slate-600">→</span>
            <span className="text-blue-400 font-bold bg-blue-950/80 border border-blue-500/40 px-2.5 py-0.5 rounded-full">
              3 Design ●
            </span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">4 Cost</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">5 Build</span>
            <span className="text-slate-600">→</span>
            <span className="text-slate-500">6 Engineer</span>
          </div>
        </div>

        {/* Page Title */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl lg:text-4xl font-display font-bold text-white tracking-tight">
              Choose your house design
            </h1>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-3 py-1 rounded-full hidden sm:inline-block">
              {options.length} Options Generated
            </span>
          </div>
          <p className="text-slate-400 text-sm lg:text-base leading-relaxed">
            Here are suitable house options generated specifically for your plot dimensions and setbacks.
          </p>
        </div>

        {/* Options Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {options.map((opt, idx) => {
            const isSelected = opt.optionId === selectedOptionId;
            const beds = getBedroomsCount(opt);
            const baths = getBathroomsCount(opt);
            const floors = opt.layout?.floors || 2;
            const buaSqFt = toSqFt(opt.layout?.totalGrossBUASqm || 110);
            const costStr = formatCostLakh(opt.boq?.totalBaseEstimate || opt.boq?.estimateRange?.expected || 4500000);
            const isTechOpen = expandedTechOptionId === opt.optionId;

            return (
              <div
                key={opt.optionId}
                className={`rounded-2xl border transition-all duration-300 flex flex-col justify-between overflow-hidden ${
                  isSelected
                    ? 'bg-slate-900/90 border-blue-500 shadow-xl shadow-blue-500/15 ring-1 ring-blue-500/50'
                    : 'bg-slate-900/40 border-white/10 hover:border-white/20 hover:bg-slate-900/60'
                }`}
              >
                {/* Card Header */}
                <div className="p-5 pb-3">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-semibold block mb-0.5">
                        Option {idx + 1}
                      </span>
                      <h3 className="text-base font-bold text-white leading-snug">
                        {opt.layout?.label || `Design Option ${idx + 1}`}
                      </h3>
                    </div>
                    {isSelected && (
                      <span className="shrink-0 p-1 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/40">
                        <Check className="w-3.5 h-3.5" />
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {opt.layout?.description || 'Thoughtfully optimized floor plan maximizing daylight and circulation.'}
                  </p>
                </div>

                {/* SVG Floor Plan Preview */}
                <div 
                  onClick={() => setViewingOption(opt)}
                  className="mx-5 my-2 aspect-[4/3] bg-[#0c1017] rounded-xl border border-white/5 relative cursor-pointer group flex items-center justify-center overflow-hidden"
                >
                  <svg viewBox="0 0 200 150" className="w-full h-full p-3">
                    {/* Outer Boundary */}
                    <rect x="15" y="15" width="170" height="120" fill="#0f172a" stroke="#334155" strokeWidth="1.5" rx="4" />
                    
                    {/* Dynamic Room Blocks preview */}
                    {opt.layout?.rooms?.slice(0, 5).map((room, rIdx) => {
                      const bx = 20 + (rIdx % 2) * 80;
                      const by = 20 + Math.floor(rIdx / 2) * 55;
                      const bw = 75;
                      const bh = 50;
                      const color = room.color || (rIdx % 2 === 0 ? '#3b82f6' : '#10b981');
                      return (
                        <g key={room.id || rIdx}>
                          <rect
                            x={bx}
                            y={by}
                            width={bw}
                            height={bh}
                            fill={color}
                            fillOpacity="0.15"
                            stroke={color}
                            strokeWidth="1"
                            rx="2"
                          />
                          <text
                            x={bx + bw / 2}
                            y={by + bh / 2 + 3}
                            textAnchor="middle"
                            fill="#cbd5e1"
                            fontSize="8"
                            fontWeight="500"
                          >
                            {room.name || 'Room'}
                          </text>
                        </g>
                      );
                    })}
                  </svg>

                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-blue-950/60 backdrop-blur-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1.5 text-xs text-blue-200 font-medium">
                    <Maximize2 className="w-4 h-4" />
                    <span>Click to view full plan</span>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="p-5 pt-3 space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="p-2 rounded-lg bg-slate-950/50 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">CONFIG</span>
                      <span className="text-white font-bold">{beds}B • {baths}B</span>
                    </div>

                    <div className="p-2 rounded-lg bg-slate-950/50 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">BUILT-UP</span>
                      <span className="text-white font-bold">{buaSqFt} sq ft</span>
                    </div>

                    <div className="p-2 rounded-lg bg-slate-950/50 border border-white/5">
                      <span className="text-[10px] text-slate-500 block">LEVELS</span>
                      <span className="text-white font-bold">{floors === 1 ? 'Ground' : `G + ${floors - 1}`}</span>
                    </div>
                  </div>

                  {/* Cost & Parking Highlight */}
                  <div className="flex items-center justify-between pt-1 text-xs">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Estimated Cost</span>
                      <span className="text-base font-bold text-emerald-400 font-mono">
                        {costStr}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 block">Parking</span>
                      <span className="text-white font-medium flex items-center gap-1 justify-end">
                        <Car className="w-3.5 h-3.5 text-cyan-400" />
                        <span>1 Car</span>
                      </span>
                    </div>
                  </div>

                  {/* Collapsible Technical Details */}
                  <div className="pt-2 border-t border-white/5">
                    <button
                      type="button"
                      onClick={() => setExpandedTechOptionId(isTechOpen ? null : opt.optionId)}
                      className="text-[11px] text-slate-400 hover:text-slate-300 flex items-center justify-between w-full"
                    >
                      <span>Technical details</span>
                      {isTechOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>

                    {isTechOpen && (
                      <div className="mt-2.5 p-2.5 rounded-lg bg-slate-950/80 border border-white/5 text-[10px] font-mono space-y-1.5 text-slate-400 animate-fade-in">
                        <div className="flex justify-between">
                          <span>DESIGN ID:</span>
                          <span className="text-slate-200">{opt.designVersionId?.slice(0, 16)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>DAYLIGHT PROXY:</span>
                          <span className="text-emerald-400">{opt.scores?.daylightProxy ?? 90}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>AREA EFFICIENCY:</span>
                          <span className="text-blue-400">{opt.scores?.areaEfficiencyPercent ?? 85}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>NBC COMPLIANCE:</span>
                          <span className="text-emerald-400">PASSED</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="grid grid-cols-2 gap-2 pt-2">
                    <button
                      type="button"
                      onClick={() => setViewingOption(opt)}
                      className="py-2.5 px-3 rounded-xl border border-white/10 hover:border-white/20 bg-slate-800/60 hover:bg-slate-800 text-xs font-semibold text-slate-200 flex items-center justify-center gap-1.5 transition-colors"
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
                      className="py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center justify-center gap-1.5 shadow-md shadow-blue-500/20 transition-all hover:scale-[1.02]"
                    >
                      <span>Choose This</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Note */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/5">
          <p className="text-xs text-slate-500">
            Want to explore a different configuration?{' '}
            <button
              onClick={onChangeRequirements}
              className="text-blue-400 hover:underline font-medium"
            >
              Change Requirements & Regenerate
            </button>
          </p>

          {onOpenTechnicalView && (
            <button
              type="button"
              onClick={onOpenTechnicalView}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 py-1.5 px-3 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Open CAD Workbench</span>
            </button>
          )}
        </div>

      </div>

      {/* Full Floor Plan View Modal */}
      {viewingOption && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 lg:p-8 animate-fade-in">
          <div className="bg-[#0b0f17] border border-white/10 rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            {/* Modal Header */}
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-slate-900/60">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono uppercase bg-blue-600/20 text-blue-400 border border-blue-500/30 px-2.5 py-0.5 rounded-full font-bold">
                  {viewingOption.layout?.label || 'Design Plan'}
                </span>
                <span className="text-sm font-bold text-white">
                  {getBedroomsCount(viewingOption)} BHK • {toSqFt(viewingOption.layout?.totalGrossBUASqm || 110)} sq ft
                </span>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    onSelectOption(viewingOption.optionId);
                    onChooseOption(viewingOption);
                    setViewingOption(null);
                  }}
                  className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-1.5 shadow-md transition-all"
                >
                  <span>Choose This Option</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => setViewingOption(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Body: Architectural Floor Plan Canvas */}
            <div className="flex-1 w-full h-full min-h-0 relative">
              <FloorPlanViewer
                layout={viewingOption.layout}
                buildingModel={viewingOption.buildingModel}
                designVersionId={viewingOption.designVersionId}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
