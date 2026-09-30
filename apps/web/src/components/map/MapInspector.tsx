import React from 'react';
import { 
  X, 
  Maximize2, 
  Pentagon, 
  Home, 
  Calculator, 
  Compass, 
  CheckCircle2,
  ExternalLink 
} from 'lucide-react';
import { SelectedMapElement } from './types';

interface MapInspectorProps {
  selectedElement: SelectedMapElement;
  onClose: () => void;
  onOpenFeasibility: () => void;
  onOpenDesign: () => void;
}

export const MapInspector: React.FC<MapInspectorProps> = ({
  selectedElement,
  onClose,
  onOpenFeasibility,
  onOpenDesign
}) => {
  if (!selectedElement) return null;

  return (
    <div className="absolute right-4 bottom-14 z-20 w-80 glass-panel p-4 border border-white/10 shadow-2xl bg-slate-950/95 backdrop-blur-md rounded-xl select-none animate-in fade-in space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex items-center gap-2">
          {selectedElement.type === 'BUILDABLE' && <Maximize2 className="w-4 h-4 text-emerald-400" />}
          {selectedElement.type === 'PARCEL' && <Pentagon className="w-4 h-4 text-cyan-400" />}
          {selectedElement.type === 'BUILDING_FOOTPRINT' && <Home className="w-4 h-4 text-indigo-400" />}
          <div>
            <h4 className="font-display font-bold text-xs uppercase tracking-wider text-white">
              {selectedElement.type === 'BUILDABLE' && 'Net Buildable Envelope'}
              {selectedElement.type === 'PARCEL' && 'Gross Land Parcel'}
              {selectedElement.type === 'BUILDING_FOOTPRINT' && 'Proposed Building Footprint'}
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">
              Status: <strong className="text-emerald-400">CALCULATED</strong>
            </span>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white p-0.5">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Content depending on selected element */}
      {selectedElement.type === 'BUILDABLE' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase block font-sans">
              Net Buildable Footprint Area
            </span>
            <span className="font-bold text-emerald-400 text-lg">
              {selectedElement.areaSqm.toLocaleString()} m²
            </span>
            <span className="text-[10px] text-slate-400 block font-sans">
              ({Math.round(selectedElement.areaSqm * 10.7639).toLocaleString()} sqft buildable ground plate)
            </span>
          </div>

          <div className="grid grid-cols-3 gap-1.5 text-center">
            <div className="p-2 rounded bg-slate-900/60 border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Front</span>
              <span className="text-white font-bold text-xs">{selectedElement.setbackFrontM} m</span>
            </div>
            <div className="p-2 rounded bg-slate-900/60 border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Rear</span>
              <span className="text-white font-bold text-xs">{selectedElement.setbackRearM} m</span>
            </div>
            <div className="p-2 rounded bg-slate-900/60 border border-white/5">
              <span className="text-[9px] text-slate-500 uppercase block">Side</span>
              <span className="text-white font-bold text-xs">{selectedElement.setbackSideM} m</span>
            </div>
          </div>

          <div className="flex items-center gap-1 text-[10px] text-slate-400 font-sans">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Complies with Mumbai DCPR 2034 Reg 41 Open Space Requirements</span>
          </div>

          <button
            onClick={onOpenFeasibility}
            className="w-full py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-blue-600/20"
          >
            <Calculator className="w-3.5 h-3.5" />
            <span>VIEW STATUTORY FEASIBILITY HUD →</span>
          </button>
        </div>
      )}

      {selectedElement.type === 'PARCEL' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase block font-sans">
              Gross Cadastral Land Area
            </span>
            <span className="font-bold text-cyan-400 text-lg">
              {selectedElement.areaSqm.toLocaleString()} m²
            </span>
            <div className="flex justify-between text-[10px] text-slate-400 pt-1">
              <span>Perimeter: {selectedElement.perimeterM.toFixed(1)} m</span>
              <span>Vertices: {selectedElement.verticesCount}</span>
            </div>
          </div>

          <div className="text-[10px] text-slate-400 space-y-1 font-sans">
            <div>• <strong>Data Provenance:</strong> CUSTOMER_DIGITIZED (WGS84 &rarr; UTM 43N)</div>
            <div>• <strong>Coordinate Reference:</strong> EPSG:32643 Metric Engine</div>
          </div>
        </div>
      )}

      {selectedElement.type === 'BUILDING_FOOTPRINT' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-lg border border-white/5 space-y-1">
            <span className="text-[10px] text-slate-400 uppercase block font-sans">
              Selected Design Option Footprint
            </span>
            <span className="font-bold text-indigo-300 text-base">
              {selectedElement.widthM}m &times; {selectedElement.lengthM}m ({selectedElement.buaSqm} m² BUA)
            </span>
            <div className="text-[10px] text-cyan-300 pt-0.5">
              Design Version: {selectedElement.designVersionId}
            </div>
          </div>

          <div className="text-[10px] text-slate-400 flex items-center gap-1 font-sans">
            <Compass className="w-3.5 h-3.5 text-amber-400" />
            <span>Optimized Orientation: Frontage facing primary road access</span>
          </div>

          <button
            onClick={onOpenDesign}
            className="w-full py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-indigo-600/20"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>INSPECT CANONICAL 2D FLOOR PLAN →</span>
          </button>
        </div>
      )}
    </div>
  );
};
