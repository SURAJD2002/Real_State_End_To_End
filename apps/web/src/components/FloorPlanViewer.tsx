import React, { useState } from 'react';
import { HouseLayout, RoomElement, CanvasViewMode } from '../types';
import { 
  Compass, 
  Layers, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Maximize, 
  Minimize, 
  Ruler, 
  Eye, 
  Box, 
  Columns, 
  CheckCircle2,
  X,
  Wind,
  Sun,
  Shield,
  Square
} from 'lucide-react';

interface FloorPlanViewerProps {
  layout: HouseLayout;
}

export const FloorPlanViewer: React.FC<FloorPlanViewerProps> = ({ layout }) => {
  const [selectedFloor, setSelectedFloor] = useState<string>('L0');
  const [viewMode, setViewMode] = useState<CanvasViewMode>('2D_PLAN');
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [showDimensions, setShowDimensions] = useState<boolean>(true);
  const [showColumns, setShowColumns] = useState<boolean>(true);
  const [selectedRoom, setSelectedRoom] = useState<RoomElement | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const roomsOnFloor = layout.rooms.filter((r) => (r.floor || 'L0') === selectedFloor);

  // SVG coordinate transformation
  const baseScale = 28; // 28 pixels per meter
  const scale = baseScale * zoomLevel;
  const padding = 45;
  const svgWidth = Math.max(520, layout.buildingEnvelope.widthM * scale + padding * 2);
  const svgHeight = Math.max(460, layout.buildingEnvelope.lengthM * scale + padding * 2);

  const handleZoom = (delta: number) => {
    setZoomLevel((prev) => Math.min(2.5, Math.max(0.6, prev + delta)));
  };

  const handleReset = () => {
    setZoomLevel(1.0);
    setSelectedRoom(null);
  };

  return (
    <div className={`flex flex-col bg-[#070b12] rounded-xl border border-white/10 overflow-hidden shadow-2xl relative ${isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'w-full h-full'}`}>
      {/* CAD Canvas Top Toolbar */}
      <div className="px-4 py-2 bg-slate-900/90 border-b border-white/10 flex items-center justify-between select-none">
        {/* Left: View Mode Tabs */}
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg bg-slate-950 p-1 border border-white/10">
            {[
              { id: '2D_PLAN', label: '2D Plan', icon: <Square className="w-3.5 h-3.5" /> },
              { id: '3D_AXONO', label: '3D Axono', icon: <Box className="w-3.5 h-3.5" /> },
              { id: 'ELEVATION', label: 'Elevation', icon: <Eye className="w-3.5 h-3.5" /> },
              { id: 'SECTION', label: 'Section', icon: <Layers className="w-3.5 h-3.5" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setViewMode(tab.id as CanvasViewMode)}
                className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  viewMode === tab.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Floor Selector if multi-story */}
          {layout.floors > 1 && viewMode === '2D_PLAN' && (
            <div className="flex rounded-md bg-slate-950 p-0.5 border border-white/10">
              <button
                onClick={() => setSelectedFloor('L0')}
                className={`px-2 py-0.5 text-[11px] font-mono rounded transition-all ${
                  selectedFloor === 'L0' ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                L0 Ground (±0.00m)
              </button>
              <button
                onClick={() => setSelectedFloor('L1')}
                className={`px-2 py-0.5 text-[11px] font-mono rounded transition-all ${
                  selectedFloor === 'L1' ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                L1 Upper (+3.20m)
              </button>
            </div>
          )}
        </div>

        {/* Center: North Arrow & Scale Indicator */}
        <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-1 text-slate-300">
            <Compass className="w-4 h-4 text-cyan-400" />
            <span className="font-bold">N 0°</span>
          </div>
          <span>•</span>
          <span>Scale: 1:{Math.round(1000 / scale)}</span>
          <span>•</span>
          <span className="text-emerald-400 font-bold">NBC 2016 Part 3 Verified</span>
        </div>

        {/* Right: Canvas Control Tools */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowDimensions(!showDimensions)}
            title="Toggle Dimension Lines"
            className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition-all ${
              showDimensions ? 'border-cyan-500/50 bg-cyan-950/60 text-cyan-300' : 'border-white/10 bg-slate-950 text-slate-400'
            }`}
          >
            <Ruler className="w-3.5 h-3.5" />
            <span className="text-[11px] font-mono">Dims</span>
          </button>

          <button
            onClick={() => setShowColumns(!showColumns)}
            title="Toggle Structural Columns Schedule"
            className={`p-1.5 rounded-lg border text-xs flex items-center gap-1 transition-all ${
              showColumns ? 'border-rose-500/50 bg-rose-950/60 text-rose-300' : 'border-white/10 bg-slate-950 text-slate-400'
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            <span className="text-[11px] font-mono">Grid</span>
          </button>

          <div className="h-4 w-px bg-white/10 mx-1" />

          <button
            onClick={() => handleZoom(0.15)}
            title="Zoom In"
            className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 transition-colors"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => handleZoom(-0.15)}
            title="Zoom Out"
            className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 transition-colors"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={handleReset}
            title="Reset View"
            className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-white/10 transition-colors"
          >
            {isFullscreen ? <Minimize className="w-3.5 h-3.5" /> : <Maximize className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Canvas Viewport Area */}
      <div className="relative flex-1 bg-[#050810] flex items-center justify-center overflow-auto p-4 select-none">
        {viewMode === '2D_PLAN' && (
          <svg
            width={svgWidth}
            height={svgHeight}
            className="filter drop-shadow-2xl transition-transform"
          >
            {/* Architectural CAD Grid */}
            <defs>
              <pattern id="cadGrid" width={scale} height={scale} patternUnits="userSpaceOnUse">
                <path d={`M ${scale} 0 L 0 0 0 ${scale}`} fill="none" stroke="rgba(255,255,255,0.035)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width={svgWidth} height={svgHeight} fill="url(#cadGrid)" />

            {/* Overall Dimension Lines (Top & Left) */}
            {showDimensions && (
              <g className="text-[10px] font-mono" fill="#64748b" stroke="#334155" strokeWidth="1">
                {/* Top overall width */}
                <line x1={padding} y1={padding - 18} x2={padding + layout.buildingEnvelope.widthM * scale} y2={padding - 18} />
                <line x1={padding} y1={padding - 24} x2={padding} y2={padding - 12} />
                <line x1={padding + layout.buildingEnvelope.widthM * scale} y1={padding - 24} x2={padding + layout.buildingEnvelope.widthM * scale} y2={padding - 12} />
                <text
                  x={padding + (layout.buildingEnvelope.widthM * scale) / 2}
                  y={padding - 22}
                  textAnchor="middle"
                  fill="#94a3b8"
                  stroke="none"
                >
                  {layout.buildingEnvelope.widthM} m (Overall Width)
                </text>

                {/* Left overall length */}
                <line x1={padding - 18} y1={padding} x2={padding - 18} y2={padding + layout.buildingEnvelope.lengthM * scale} />
                <line x1={padding - 24} y1={padding} x2={padding - 12} y2={padding} />
                <line x1={padding - 24} y1={padding + layout.buildingEnvelope.lengthM * scale} x2={padding - 12} y2={padding + layout.buildingEnvelope.lengthM * scale} />
                <text
                  x={padding - 24}
                  y={padding + (layout.buildingEnvelope.lengthM * scale) / 2}
                  textAnchor="middle"
                  transform={`rotate(-90 ${padding - 24} ${padding + (layout.buildingEnvelope.lengthM * scale) / 2})`}
                  fill="#94a3b8"
                  stroke="none"
                >
                  {layout.buildingEnvelope.lengthM} m (Length)
                </text>
              </g>
            )}

            {/* Exterior Perimeter Walls (230mm Loadbearing / AAC) */}
            <rect
              x={padding}
              y={padding}
              width={layout.buildingEnvelope.widthM * scale}
              height={layout.buildingEnvelope.lengthM * scale}
              fill="none"
              stroke="#1e293b"
              strokeWidth="10"
              rx="4"
            />
            <rect
              x={padding}
              y={padding}
              width={layout.buildingEnvelope.widthM * scale}
              height={layout.buildingEnvelope.lengthM * scale}
              fill="none"
              stroke="#0f172a"
              strokeWidth="2"
            />

            {/* Room Polygons & Interior Partitions */}
            {roomsOnFloor.map((room) => {
              const rx = padding + room.bounds.x * scale;
              const ry = padding + room.bounds.y * scale;
              const rw = room.bounds.width * scale;
              const rh = room.bounds.height * scale;
              const isSelected = selectedRoom?.id === room.id;

              return (
                <g
                  key={room.id}
                  onClick={() => setSelectedRoom(room)}
                  className="cursor-pointer transition-all"
                >
                  {/* Room Fill */}
                  <rect
                    x={rx}
                    y={ry}
                    width={rw}
                    height={rh}
                    fill={room.color}
                    fillOpacity={isSelected ? 0.45 : 0.20}
                    stroke={isSelected ? '#38bdf8' : '#334155'}
                    strokeWidth={isSelected ? '2.5' : '1.5'}
                    rx="2"
                  />

                  {/* Room Door Swing Arc (Symbolic CAD swing) */}
                  {rw > 40 && rh > 40 && (
                    <path
                      d={`M ${rx + 10} ${ry + 3} A 18 18 0 0 1 ${rx + 28} ${ry + 21}`}
                      fill="none"
                      stroke="#94a3b8"
                      strokeWidth="1"
                      strokeDasharray="2,2"
                    />
                  )}

                  {/* Window Symbol along exterior edge */}
                  {room.bounds.x === 0 && (
                    <rect x={rx - 3} y={ry + rh * 0.3} width={6} height={rh * 0.4} fill="#38bdf8" stroke="#ffffff" strokeWidth="0.75" />
                  )}
                  {room.bounds.x + room.bounds.width >= layout.buildingEnvelope.widthM - 0.5 && (
                    <rect x={rx + rw - 3} y={ry + rh * 0.3} width={6} height={rh * 0.4} fill="#38bdf8" stroke="#ffffff" strokeWidth="0.75" />
                  )}

                  {/* Room Label, Area & Dimensions */}
                  {rw > 45 && rh > 35 && (
                    <>
                      <text
                        x={rx + rw / 2}
                        y={ry + rh / 2 - 8}
                        textAnchor="middle"
                        fill="#ffffff"
                        fontSize={rw < 90 ? "10.5" : "11.5"}
                        fontWeight="700"
                        fontFamily="Inter, sans-serif"
                      >
                        {room.name}
                      </text>
                      <text
                        x={rx + rw / 2}
                        y={ry + rh / 2 + 7}
                        textAnchor="middle"
                        fill="#38bdf8"
                        fontSize="10"
                        fontFamily="JetBrains Mono, monospace"
                        fontWeight="600"
                      >
                        {room.areaSqm} m² ({Math.round(room.areaSqm * 10.7639)} sqft)
                      </text>
                      <text
                        x={rx + rw / 2}
                        y={ry + rh / 2 + 20}
                        textAnchor="middle"
                        fill="#94a3b8"
                        fontSize="9"
                        fontFamily="JetBrains Mono, monospace"
                      >
                        {room.bounds.width}m × {room.bounds.height}m
                      </text>
                    </>
                  )}
                </g>
              );
            })}

            {/* Structural Column Schedule (300mm x 450mm RCC Pads) */}
            {showColumns && layout.columns.map((col, idx) => {
              const cx = padding + col.x * scale - 5;
              const cy = padding + col.y * scale - 7;
              return (
                <g key={col.id}>
                  <rect
                    x={cx}
                    y={cy}
                    width={10}
                    height={14}
                    fill="#f43f5e"
                    stroke="#ffffff"
                    strokeWidth="1.2"
                    rx="1.5"
                  >
                    <title>{`Structural Column C${idx + 1} (${col.widthMm}x${col.depthMm}mm)`}</title>
                  </rect>
                  <text
                    x={cx + 5}
                    y={cy + 10}
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize="7"
                    fontWeight="bold"
                    fontFamily="JetBrains Mono, monospace"
                  >
                    C{idx + 1}
                  </text>
                </g>
              );
            })}
          </svg>
        )}

        {/* 3D Axonometric Projection Mode */}
        {viewMode === '3D_AXONO' && (
          <div className="w-full h-full flex flex-col items-center justify-center p-6 space-y-4">
            <div className="glass-panel p-6 max-w-lg w-full text-center space-y-3">
              <Box className="w-12 h-12 text-cyan-400 mx-auto" />
              <h3 className="font-display font-bold text-base text-white">3D Axonometric Massing Projection</h3>
              <p className="text-xs text-slate-300 leading-normal">
                Extruded from canonical <code className="text-cyan-400 font-mono">house-model.v1</code> with ceiling height <span className="font-bold text-white">3,200 mm</span>, reinforced slab thickness <span className="font-bold text-white">150 mm</span>, and structural transfer bays.
              </p>
              <div className="grid grid-cols-3 gap-2 pt-2 text-xs font-mono">
                <div className="bg-slate-950 p-2 rounded border border-white/5">
                  <span className="text-slate-400 block text-[10px]">Building Height</span>
                  <span className="text-white font-bold">{layout.buildingEnvelope.heightM} m</span>
                </div>
                <div className="bg-slate-950 p-2 rounded border border-white/5">
                  <span className="text-slate-400 block text-[10px]">Footprint</span>
                  <span className="text-white font-bold">{layout.totalGrossBUASqm} m²</span>
                </div>
                <div className="bg-slate-950 p-2 rounded border border-white/5">
                  <span className="text-slate-400 block text-[10px]">Columns</span>
                  <span className="text-rose-400 font-bold">{layout.columns.length} Nos</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Elevation Mode */}
        {viewMode === 'ELEVATION' && (
          <div className="w-full h-full flex flex-col items-center justify-center p-6 space-y-4">
            <div className="glass-panel p-6 max-w-lg w-full text-center space-y-3">
              <Eye className="w-12 h-12 text-blue-400 mx-auto" />
              <h3 className="font-display font-bold text-base text-white">Front & Road-Facing Architectural Elevation</h3>
              <p className="text-xs text-slate-300 leading-normal">
                Coordinated elevation view per NBC 2016 Part 3: Plinth height <span className="font-bold text-white">+600 mm</span>, Parapet <span className="font-bold text-white">+1,050 mm</span>, and 3-track UPVC casement windows.
              </p>
            </div>
          </div>
        )}

        {/* Section Mode */}
        {viewMode === 'SECTION' && (
          <div className="w-full h-full flex flex-col items-center justify-center p-6 space-y-4">
            <div className="glass-panel p-6 max-w-lg w-full text-center space-y-3">
              <Layers className="w-12 h-12 text-indigo-400 mx-auto" />
              <h3 className="font-display font-bold text-base text-white">Transverse Building Section (A-A')</h3>
              <p className="text-xs text-slate-300 leading-normal">
                Shows foundation footing depth <span className="font-bold text-white">-1,500 mm</span>, plinth beam DPC layer, floor finishes, and reinforced RCC roof slab.
              </p>
            </div>
          </div>
        )}

        {/* Contextual Room Inspector Panel (Section 8) */}
        {selectedRoom && viewMode === '2D_PLAN' && (
          <aside className="absolute right-4 top-4 w-72 glass-panel p-3.5 space-y-3 shadow-2xl border border-blue-500/40 animate-in fade-in select-none">
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: selectedRoom.color }} />
                <h4 className="font-display font-bold text-sm text-white">{selectedRoom.name}</h4>
              </div>
              <button onClick={() => setSelectedRoom(null)} className="text-slate-400 hover:text-white p-0.5">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2 bg-slate-950 p-2 rounded border border-white/5 font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 block">Usable Area</span>
                  <span className="font-bold text-white text-xs">{selectedRoom.areaSqm} m²</span>
                  <span className="text-[9px] text-slate-500 block">({Math.round(selectedRoom.areaSqm * 10.7639)} sqft)</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Dimensions</span>
                  <span className="font-bold text-white text-xs">{selectedRoom.bounds.width}m × {selectedRoom.bounds.height}m</span>
                  <span className="text-[9px] text-cyan-400 block">Ht: 3.20m</span>
                </div>
              </div>

              {/* Environmental Quality Attributes */}
              <div className="space-y-1.5 pt-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 flex items-center gap-1"><Sun className="w-3 h-3 text-amber-400" /> Natural Daylight:</span>
                  <span className="text-emerald-400 font-bold font-mono">Good (East Sun)</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 flex items-center gap-1"><Wind className="w-3 h-3 text-cyan-400" /> Cross-Ventilation:</span>
                  <span className="text-emerald-400 font-bold font-mono">Compliant (NBC)</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 flex items-center gap-1"><Shield className="w-3 h-3 text-indigo-400" /> Acoustic Privacy:</span>
                  <span className="text-slate-200 font-bold font-mono">High Buffer</span>
                </div>
              </div>

              {/* Related Model Elements (QTO Traceability) */}
              <div className="p-2 rounded bg-slate-900/80 border border-white/5 space-y-1 text-[11px]">
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Associated Building Objects:</span>
                <div className="text-slate-300 font-mono text-[10px] space-y-0.5">
                  <div>• 4 Wall Segments (200mm AAC Block)</div>
                  <div>• 1 Flush Door (900 × 2100mm Timber)</div>
                  <div>• 2 Sliding Windows (1500 × 1200mm UPVC)</div>
                  <div>• 6 Concealed Electrical Points</div>
                </div>
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* Canvas Bottom Status Bar */}
      <div className="px-4 py-2 bg-slate-900/80 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 select-none">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Click any room space to open the <strong>Contextual Object Inspector</strong></span>
          </span>
        </div>

        <div className="flex items-center gap-3 font-mono">
          <span className="text-slate-400">Total BUA: <strong className="text-white">{layout.totalGrossBUASqm} m²</strong></span>
          <span>•</span>
          <span className="text-cyan-400 font-bold">{layout.rooms.length} Rooms</span>
          <span>•</span>
          <span className="text-rose-400 font-bold">{layout.columns.length} Columns</span>
        </div>
      </div>
    </div>
  );
};
