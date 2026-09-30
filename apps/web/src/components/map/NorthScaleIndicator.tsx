import React from 'react';
import { Compass, Crosshair } from 'lucide-react';

interface NorthScaleIndicatorProps {
  cursorLat: number;
  cursorLng: number;
  zoom: number;
  bearing: number;
  onResetNorth: () => void;
}

export const NorthScaleIndicator: React.FC<NorthScaleIndicatorProps> = ({
  cursorLat,
  cursorLng,
  zoom,
  bearing,
  onResetNorth
}) => {
  // Approximate scale bar calculation at Mumbai latitude (~19.1° N)
  // At zoom 15: ~3.5 m/px, at zoom 16: ~1.75 m/px, at zoom 17: ~0.87 m/px
  const metersPerPixel = Math.max(0.2, (156543.03392 * Math.cos((cursorLat * Math.PI) / 180)) / Math.pow(2, zoom));
  const scaleBarWidthPx = 100;
  const scaleBarMeters = Math.round(metersPerPixel * scaleBarWidthPx);

  return (
    <div className="absolute left-4 bottom-4 z-20 flex items-center gap-3 select-none">
      {/* CAD Coordinate & CRS Readout */}
      <div className="glass-panel px-3 py-1.5 flex items-center gap-3 text-[11px] font-mono text-slate-300 border border-white/10 shadow-xl bg-slate-950/90 backdrop-blur-md rounded-lg">
        <div className="flex items-center gap-1.5 text-cyan-400">
          <Crosshair className="w-3.5 h-3.5 shrink-0" />
          <span>{cursorLat.toFixed(5)}°N, {cursorLng.toFixed(5)}°E</span>
        </div>
        <div className="h-3 w-px bg-white/10" />
        <span className="text-slate-400">Zoom: {zoom.toFixed(1)}x</span>
        <div className="h-3 w-px bg-white/10" />
        <span className="text-slate-400">Display: Web Mercator</span>
        <div className="h-3 w-px bg-white/10" />
        <span className="text-emerald-400 font-bold">Engine: UTM 43N (Metric)</span>
      </div>

      {/* Scale Bar */}
      <div className="glass-panel px-3 py-1.5 flex flex-col justify-center items-center border border-white/10 shadow-xl bg-slate-950/90 backdrop-blur-md rounded-lg text-[10px] font-mono text-slate-300">
        <span className="text-[9px] text-slate-400">{scaleBarMeters} m</span>
        <div className="w-[100px] h-1 border-b-2 border-l-2 border-r-2 border-cyan-400" />
      </div>

      {/* Interactive North Indicator Compass */}
      <button
        onClick={onResetNorth}
        title="Reset Map Orientation to True North (0°)"
        className="glass-panel w-9 h-9 flex items-center justify-center border border-white/10 shadow-xl bg-slate-950/90 hover:bg-slate-900 rounded-lg text-cyan-400 hover:text-white transition-all group"
      >
        <div
          className="transition-transform duration-200"
          style={{ transform: `rotate(${-bearing}deg)` }}
        >
          <Compass className="w-5 h-5 text-cyan-400 group-hover:text-cyan-300" />
        </div>
      </button>
    </div>
  );
};
