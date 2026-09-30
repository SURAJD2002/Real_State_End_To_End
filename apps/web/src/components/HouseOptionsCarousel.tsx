import React, { useState } from 'react';
import { HouseOption } from '../types';
import { 
  Sparkles, 
  Clock, 
  FileSpreadsheet, 
  Lock, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp 
} from 'lucide-react';

interface HouseOptionsCarouselProps {
  options: HouseOption[];
  selectedOptionId: string;
  onSelectOption: (id: string) => void;
  onOpenBOQ: (option: HouseOption) => void;
  onOpenBuildModal: (option: HouseOption) => void;
}

export const HouseOptionsCarousel: React.FC<HouseOptionsCarouselProps> = ({
  options,
  selectedOptionId,
  onSelectOption,
  onOpenBOQ,
  onOpenBuildModal
}) => {
  const [expandedWhy, setExpandedWhy] = useState<string | null>(null);

  if (!options || options.length === 0) {
    return (
      <div className="glass-panel p-4 text-center text-slate-500 text-xs">
        Generating CP-SAT Pareto options...
      </div>
    );
  }

  const getWhyExplanation = (arch: string) => {
    switch (arch) {
      case 'compact_2bhk':
        return 'Maximizes area efficiency (95.2%) by eliminating redundant hallway circulation corridors. Places living and master bed along primary frontage for maximum morning daylight.';
      case 'family_3bhk':
        return 'Features a central sky courtyard lightwell that brings continuous natural illumination and passive stack ventilation into the dining core and internal bedrooms.';
      case 'duplex_3bhk':
        return 'Separates public entertainment on Ground (L0) from executive master suites on First (L1). Minimizes ground footprint to preserve garden setbacks and parking.';
      default:
        return 'Deterministic layout optimized for NBC 2016 room dimensions and setback compliance.';
    }
  };

  return (
    <aside className="w-80 flex flex-col gap-3 h-full overflow-y-auto pr-1 select-none">
      <div className="flex items-center justify-between pb-1 border-b border-white/10">
        <div className="flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <h3 className="font-display font-bold text-xs uppercase tracking-wider text-white">
            Design Options (CP-SAT)
          </h3>
        </div>
        <span className="text-[10px] font-mono text-cyan-400 px-1.5 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40">
          3 Pareto Candidates
        </span>
      </div>

      {/* Cards List */}
      <div className="flex flex-col gap-2.5">
        {options.map((opt, idx) => {
          const isSelected = opt.optionId === selectedOptionId;
          const layout = opt.layout;
          const boq = opt.boq;
          const schedule = opt.schedule;
          const scores = opt.scores;
          const isWhyOpen = expandedWhy === opt.optionId;

          const bedrooms = opt.layout.rooms.filter(r => r.id.includes('bed') || r.id.includes('suite')).length;
          const bathrooms = opt.layout.rooms.filter(r => r.id.includes('bath') || r.id.includes('toilet')).length;

          return (
            <div
              key={opt.optionId}
              onClick={() => onSelectOption(opt.optionId)}
              className={`glass-panel p-3 flex flex-col justify-between cursor-pointer transition-all duration-150 ${
                isSelected
                  ? 'border-blue-500 bg-blue-950/30 ring-1 ring-blue-500 shadow-md shadow-blue-500/20'
                  : 'hover:border-white/20 hover:bg-slate-900/60'
              }`}
            >
              <div>
                {/* Header: Option Tag & Label */}
                <div className="flex items-start justify-between gap-1 mb-1.5">
                  <div>
                    <span className="text-[10px] font-mono font-bold text-blue-400 uppercase">
                      Option {String.fromCharCode(65 + idx)} • {layout.archetype.replace('_', ' ')}
                    </span>
                    <h4 className="font-display font-bold text-xs text-white leading-tight">
                      {layout.label}
                    </h4>
                  </div>
                  <span className="text-[11px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/50 shrink-0">
                    ★ {scores.overallScore}
                  </span>
                </div>

                {/* Compact Spec Grid */}
                <div className="grid grid-cols-4 gap-1 bg-slate-950/80 p-1.5 rounded-md border border-white/5 text-[10px] font-mono text-center mb-2">
                  <div>
                    <span className="text-slate-500 block">BUA</span>
                    <span className="text-white font-bold">{Math.round(layout.totalGrossBUASqm)}m²</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Beds</span>
                    <span className="text-slate-200 font-bold">{bedrooms} BHK</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Baths</span>
                    <span className="text-slate-200 font-bold">{bathrooms}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Floors</span>
                    <span className="text-cyan-400 font-bold">{layout.floors}</span>
                  </div>
                </div>

                {/* Cost & Timeline Strip */}
                <div className="flex items-center justify-between text-[11px] mb-2 font-mono">
                  <span className="text-emerald-400 font-bold">
                    ₹{(boq.totalBaseEstimate / 100000).toFixed(1)}L <span className="text-[9px] text-slate-500">Est.</span>
                  </span>
                  <span className="text-slate-400 flex items-center gap-1 text-[10px]">
                    <Clock className="w-3 h-3 text-amber-400" />
                    <span>{schedule.totalDurationWeeks} wks</span>
                  </span>
                </div>

                {/* Compact Performance Micro-Bars */}
                <div className="space-y-1 mb-2">
                  <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
                    <span>Daylight</span>
                    <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${scores.daylightProxy}%` }} />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
                    <span>Ventilation</span>
                    <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${scores.ventilationProxy}%` }} />
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
                    <span>Efficiency</span>
                    <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-400 rounded-full" style={{ width: `${scores.areaEfficiencyPercent}%` }} />
                    </div>
                  </div>
                </div>

                {/* "Why this option?" Expandable Section */}
                <div className="mb-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setExpandedWhy(isWhyOpen ? null : opt.optionId);
                    }}
                    className="flex items-center gap-1 text-[10px] text-blue-400 hover:text-blue-300 font-medium transition-colors"
                  >
                    <HelpCircle className="w-3 h-3" />
                    <span>Why this option?</span>
                    {isWhyOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                  {isWhyOpen && (
                    <p className="text-[10px] text-slate-300 bg-slate-950 p-2 rounded mt-1 border border-white/5 leading-normal">
                      {getWhyExplanation(layout.archetype)}
                    </p>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-white/10 flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenBOQ(opt);
                  }}
                  className="flex-1 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[10px] font-mono flex items-center justify-center gap-1 transition-colors"
                >
                  <FileSpreadsheet className="w-3 h-3 text-cyan-400" />
                  <span>BOQ</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenBuildModal(opt);
                  }}
                  className="flex-1 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold flex items-center justify-center gap-1 shadow-sm transition-all"
                >
                  <Lock className="w-3 h-3 text-white" />
                  <span>BUILD →</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </aside>
  );
};
