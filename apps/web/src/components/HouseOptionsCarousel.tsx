import React from 'react';
import { HouseOption } from '../types';
import { Sparkles, Clock, FileSpreadsheet, Lock } from 'lucide-react';

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
  if (!options || options.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <h3 className="font-display font-bold text-xs uppercase tracking-wider text-white">
            Parametric House Options (CP-SAT Solved)
          </h3>
        </div>
        <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
          {options.length} Feasible Pareto Candidates
        </span>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-3 gap-3">
        {options.map((opt) => {
          const isSelected = opt.optionId === selectedOptionId;
          const layout = opt.layout;
          const boq = opt.boq;
          const schedule = opt.schedule;

          const formatLakhs = (val: number) => {
            return `₹${(val / 100000).toFixed(2)} L`;
          };

          return (
            <div
              key={opt.optionId}
              onClick={() => onSelectOption(opt.optionId)}
              className={`glass-panel p-3.5 flex flex-col justify-between cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'border-blue-500 bg-blue-950/30 shadow-lg shadow-blue-500/20 ring-1 ring-blue-500'
                  : 'hover:border-white/20 hover:bg-slate-900/60'
              }`}
            >
              <div>
                {/* Header & Score */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block uppercase">
                      {layout.archetype.replace('_', ' ')}
                    </span>
                    <h4 className="font-display font-bold text-sm text-white leading-tight">
                      {layout.label}
                    </h4>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
                      ★ {opt.scores.overallScore}
                    </span>
                    <span className="text-[9px] text-slate-500 mt-0.5">Pareto Rank</span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-300 line-clamp-2 mb-3">
                  {layout.description}
                </p>

                {/* Spatial Specs */}
                <div className="grid grid-cols-2 gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5 text-[11px] mb-3">
                  <div>
                    <span className="text-slate-400 text-[10px] block">Gross BUA</span>
                    <span className="font-mono font-bold text-slate-100">{layout.totalGrossBUASqm} m²</span>
                    <span className="text-[9px] text-slate-500 block">({Math.round(layout.totalGrossBUASqm * 10.7639)} sqft)</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[10px] block">Floors & Rooms</span>
                    <span className="font-mono font-bold text-slate-100">{layout.floors} Flr • {layout.rooms.length} Rooms</span>
                    <span className="text-[9px] text-cyan-400 block">Eff. {opt.scores.areaEfficiencyPercent}%</span>
                  </div>
                </div>

                {/* Pricing Range */}
                <div className="bg-slate-900/80 p-2 rounded-lg border border-white/5 space-y-1 text-xs mb-3">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 text-[11px]">Estimate:</span>
                    <span className="font-mono font-bold text-emerald-400">{formatLakhs(boq.totalBaseEstimate)}</span>
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                    <span>Range: {formatLakhs(boq.estimateRange.low)} - {formatLakhs(boq.estimateRange.high)}</span>
                    <span>₹{Math.round(boq.costPerSqFtBUA)}/sqft</span>
                  </div>
                </div>

                {/* Schedule badge */}
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mb-3">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <span>Timeline: <strong className="text-slate-200">{schedule.totalDurationMonths} Months</strong> ({schedule.totalDurationWeeks} wks)</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-white/10 flex items-center gap-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenBOQ(opt);
                  }}
                  className="flex-1 py-1.5 px-2 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-[11px] font-medium flex items-center justify-center gap-1 transition-colors"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Traceable BOQ</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenBuildModal(opt);
                  }}
                  className="flex-1 py-1.5 px-2 rounded-md bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-[11px] font-bold shadow-md shadow-emerald-600/20 flex items-center justify-center gap-1 transition-all active:scale-95"
                >
                  <Lock className="w-3.5 h-3.5 text-white" />
                  <span>REQUEST BUILD</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
