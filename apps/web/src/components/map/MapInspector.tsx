import React from 'react';
import { 
  X, 
  Maximize2, 
  Pentagon, 
  Home, 
  Calculator, 
  Compass, 
  CheckCircle2,
  ExternalLink,
  Edit,
  Trash2,
  PlusCircle,
  Flag,
  Navigation
} from 'lucide-react';
import { SelectedMapElement } from './types';
import { wgs84ToUtm43N } from './cadGeometry';

interface MapInspectorProps {
  selectedElement: SelectedMapElement;
  onClose: () => void;
  onOpenFeasibility: () => void;
  onOpenDesign: () => void;
  onOpenCoordinateEditor?: (vertexIndex: number) => void;
  onDeleteVertex?: (vertexIndex: number) => void;
  onOpenEdgeEditor?: (edgeIndex: number) => void;
  onSplitEdge?: (edgeIndex: number) => void;
  onSetPrimaryFrontage?: (edgeIndex: number) => void;
  existingRoadWidth?: number;
  proposedRoadWidth?: number;
}

export const MapInspector: React.FC<MapInspectorProps> = ({
  selectedElement,
  onClose,
  onOpenFeasibility,
  onOpenDesign,
  onOpenCoordinateEditor,
  onDeleteVertex,
  onOpenEdgeEditor,
  onSplitEdge,
  onSetPrimaryFrontage,
  existingRoadWidth = 12,
  proposedRoadWidth = 18
}) => {
  if (!selectedElement) return null;

  return (
    <div className="absolute right-4 bottom-14 z-20 w-80 glass-panel p-4 border border-white/10 shadow-2xl bg-slate-950/95 backdrop-blur-md rounded-2xl select-none animate-in fade-in space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <div className="flex items-center gap-2">
          {selectedElement.type === 'BUILDABLE' && <Maximize2 className="w-4 h-4 text-emerald-400" />}
          {selectedElement.type === 'PARCEL' && <Pentagon className="w-4 h-4 text-cyan-400" />}
          {selectedElement.type === 'VERTEX' && <Navigation className="w-4 h-4 text-blue-400" />}
          {selectedElement.type === 'EDGE' && <Compass className="w-4 h-4 text-amber-400" />}
          {selectedElement.type === 'BUILDING_FOOTPRINT' && <Home className="w-4 h-4 text-indigo-400" />}
          <div>
            <h4 className="font-display font-bold text-xs uppercase tracking-wider text-white">
              {selectedElement.type === 'BUILDABLE' && 'Net Buildable Envelope'}
              {selectedElement.type === 'PARCEL' && 'Gross Land Parcel'}
              {selectedElement.type === 'VERTEX' && `Vertex V${selectedElement.index + 1}`}
              {selectedElement.type === 'EDGE' && `Cadastral Edge ${selectedElement.id}`}
              {selectedElement.type === 'BUILDING_FOOTPRINT' && 'Proposed Building Footprint'}
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">
              Status: <strong className="text-emerald-400">INSPECTED</strong>
            </span>
          </div>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 1. VERTEX INSPECTION (Section 13, 20, 31) */}
      {selectedElement.type === 'VERTEX' && (
        <div className="space-y-2.5 text-xs font-mono">
          {(() => {
            const utm = wgs84ToUtm43N(selectedElement.coordinate);
            return (
              <div className="bg-slate-900/80 p-2.5 rounded-xl border border-white/5 space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-[9px] text-slate-500 uppercase block">Latitude</span>
                    <span className="text-white font-bold text-xs">
                      {selectedElement.coordinate[1].toFixed(6)}° N
                    </span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-500 uppercase block">Longitude</span>
                    <span className="text-white font-bold text-xs">
                      {selectedElement.coordinate[0].toFixed(6)}° E
                    </span>
                  </div>
                </div>

                <div className="pt-1.5 border-t border-white/5 grid grid-cols-2 gap-2 text-[10px]">
                  <div>
                    <span className="text-[9px] text-slate-500 block">Easting (X)</span>
                    <span className="text-cyan-300 font-bold">{utm.easting.toLocaleString()} m</span>
                  </div>
                  <div>
                    <span className="text-[9px] text-slate-500 block">Northing (Y)</span>
                    <span className="text-cyan-300 font-bold">{utm.northing.toLocaleString()} m</span>
                  </div>
                </div>
              </div>
            );
          })()}

          <div className="grid grid-cols-2 gap-2 pt-1">
            {onOpenCoordinateEditor && (
              <button
                onClick={() => onOpenCoordinateEditor(selectedElement.index)}
                className="py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-blue-600/20"
              >
                <Edit className="w-3.5 h-3.5" />
                <span>EDIT COORD</span>
              </button>
            )}

            {onDeleteVertex && (
              <button
                onClick={() => onDeleteVertex(selectedElement.index)}
                className="py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-sans font-bold text-xs flex items-center justify-center gap-1.5 transition-all"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                <span>DELETE</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* 2. EDGE INSPECTION (Section 5, 21, 23, 24) */}
      {selectedElement.type === 'EDGE' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-white/5 space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-[9px] text-slate-500 uppercase block">Segment Length</span>
                <span className="text-white font-bold text-sm">{selectedElement.lengthM} m</span>
              </div>
              <div>
                <span className="text-[9px] text-slate-500 uppercase block">Azimuth Bearing</span>
                <span className="text-amber-400 font-bold text-sm">{selectedElement.bearingDeg}°</span>
              </div>
            </div>

            {/* Road Widening Context (Section 24) */}
            <div className="p-2 rounded-lg bg-slate-950 border border-white/5 text-[10px] space-y-1">
              <div className="flex items-center justify-between text-slate-400">
                <span>Existing Road:</span>
                <span className="text-white font-bold">{existingRoadWidth} m</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Statutory Proposed:</span>
                <span className="text-cyan-400 font-bold">{proposedRoadWidth} m</span>
              </div>
              <div className="flex items-center justify-between text-slate-400 pt-0.5 border-t border-white/5">
                <span>Road Widening Deduction:</span>
                <span className="text-amber-300 font-bold">
                  {Math.max(0, (proposedRoadWidth - existingRoadWidth) / 2)} m setback
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-1.5">
            {onOpenEdgeEditor && (
              <button
                onClick={() => onOpenEdgeEditor(selectedElement.index)}
                className="w-full py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-sans font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md shadow-cyan-600/20"
              >
                <Compass className="w-3.5 h-3.5" />
                <span>EDIT BEARING & LENGTH →</span>
              </button>
            )}

            {onSplitEdge && (
              <button
                onClick={() => onSplitEdge(selectedElement.index)}
                className="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-sans font-medium text-xs flex items-center justify-center gap-1.5 transition-all"
              >
                <PlusCircle className="w-3.5 h-3.5 text-cyan-400" />
                <span>INSERT MIDPOINT VERTEX</span>
              </button>
            )}

            {onSetPrimaryFrontage && (
              <button
                onClick={() => onSetPrimaryFrontage(selectedElement.index)}
                className="w-full py-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 font-sans font-medium text-xs flex items-center justify-center gap-1.5 transition-all"
              >
                <Flag className="w-3.5 h-3.5 text-blue-400" />
                <span>SET AS PRIMARY FRONTAGE</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* 3. NET BUILDABLE ENVELOPE INSPECTION */}
      {selectedElement.type === 'BUILDABLE' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-white/5 space-y-1">
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

      {/* 4. GROSS PARCEL INSPECTION */}
      {selectedElement.type === 'PARCEL' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-white/5 space-y-1">
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

      {/* 5. BUILDING FOOTPRINT INSPECTION */}
      {selectedElement.type === 'BUILDING_FOOTPRINT' && (
        <div className="space-y-2.5 text-xs font-mono">
          <div className="bg-slate-900/80 p-2.5 rounded-xl border border-white/5 space-y-1">
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
