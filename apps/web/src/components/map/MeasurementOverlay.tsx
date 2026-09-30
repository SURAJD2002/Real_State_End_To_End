import React from 'react';
import { Ruler, Trash2, CheckCircle2 } from 'lucide-react';
import { MeasurementState } from './types';

interface MeasurementOverlayProps {
  measurement: MeasurementState;
  onClearMeasurement: () => void;
  onSwitchMode: (mode: 'DISTANCE' | 'AREA') => void;
}

export const MeasurementOverlay: React.FC<MeasurementOverlayProps> = ({
  measurement,
  onClearMeasurement,
  onSwitchMode
}) => {
  if (!measurement.mode) return null;

  return (
    <div className="absolute top-20 right-4 z-20 w-72 glass-panel p-3.5 border border-purple-500/40 shadow-2xl bg-slate-950/95 backdrop-blur-md rounded-xl select-none space-y-2.5 animate-in fade-in">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex items-center gap-2">
          <Ruler className="w-4 h-4 text-purple-400" />
          <h4 className="font-display font-bold text-xs uppercase tracking-wider text-white">
            Map Measurement Tool
          </h4>
        </div>
        <button
          onClick={onClearMeasurement}
          className="text-slate-400 hover:text-rose-400 p-0.5"
          title="Clear Measurements"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Mode Switcher */}
      <div className="flex rounded-lg bg-slate-900 p-1 border border-white/10">
        <button
          onClick={() => onSwitchMode('DISTANCE')}
          className={`flex-1 py-1 rounded text-xs font-semibold transition-all ${
            measurement.mode === 'DISTANCE'
              ? 'bg-purple-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Distance
        </button>
        <button
          onClick={() => onSwitchMode('AREA')}
          className={`flex-1 py-1 rounded text-xs font-semibold transition-all ${
            measurement.mode === 'AREA'
              ? 'bg-purple-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Area
        </button>
      </div>

      {/* Result Card */}
      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/5 space-y-1 font-mono text-xs">
        {measurement.mode === 'DISTANCE' ? (
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-sans">
              Measured Distance (Total)
            </span>
            <span className="text-lg font-bold text-purple-300">
              {measurement.totalDistanceM.toFixed(1)} m
            </span>
            <span className="text-[10px] text-slate-500 block font-sans">
              ({(measurement.totalDistanceM * 3.28084).toFixed(1)} ft) • {measurement.points.length} points clicked
            </span>
          </div>
        ) : (
          <div>
            <span className="text-[10px] text-slate-400 uppercase block font-sans">
              Measured Enclosed Area
            </span>
            <span className="text-lg font-bold text-purple-300">
              {measurement.totalAreaSqm.toLocaleString()} m²
            </span>
            <span className="text-[10px] text-slate-500 block font-sans">
              ({Math.round(measurement.totalAreaSqm * 10.7639).toLocaleString()} sqft) • {measurement.points.length} vertices
            </span>
          </div>
        )}
      </div>

      <div className="text-[10px] text-slate-400 flex items-start gap-1 font-sans leading-tight">
        <CheckCircle2 className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
        <span>
          <strong>Map Measurement:</strong> Planar screen approximation. Distinct from authoritative PostGIS cadastral survey computations.
        </span>
      </div>
    </div>
  );
};
