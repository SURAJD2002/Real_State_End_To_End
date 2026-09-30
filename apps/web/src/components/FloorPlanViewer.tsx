import React, { useState } from 'react';
import { HouseLayout, RoomElement } from '../types';
import { Compass, Layers } from 'lucide-react';

interface FloorPlanViewerProps {
  layout: HouseLayout;
}

export const FloorPlanViewer: React.FC<FloorPlanViewerProps> = ({ layout }) => {
  const [selectedFloor, setSelectedFloor] = useState<string>('L0');
  const [hoveredRoom, setHoveredRoom] = useState<RoomElement | null>(null);

  const roomsOnFloor = layout.rooms.filter((r) => (r.floor || 'L0') === selectedFloor);

  // SVG coordinate transformation
  const scale = 24; // 24 pixels per meter
  const padding = 30;
  const svgWidth = Math.max(400, layout.buildingEnvelope.widthM * scale + padding * 2);
  const svgHeight = Math.max(380, layout.buildingEnvelope.lengthM * scale + padding * 2);

  return (
    <div className="flex flex-col bg-slate-950/80 rounded-xl border border-white/10 overflow-hidden shadow-2xl">
      {/* Floor Plan Header */}
      <div className="px-4 py-2.5 bg-slate-900/90 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span className="font-display font-semibold text-xs text-white uppercase tracking-wider">
            Canonical 2D Floor Plan (NBC 2016 Coordinated)
          </span>
        </div>

        {/* Floor Selector if multi-story */}
        {layout.floors > 1 && (
          <div className="flex rounded-md bg-slate-950 p-0.5 border border-white/10">
            <button
              onClick={() => setSelectedFloor('L0')}
              className={`px-2.5 py-0.5 text-[11px] font-mono rounded transition-all ${
                selectedFloor === 'L0' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              L0 Ground
            </button>
            <button
              onClick={() => setSelectedFloor('L1')}
              className={`px-2.5 py-0.5 text-[11px] font-mono rounded transition-all ${
                selectedFloor === 'L1' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              L1 Upper
            </button>
          </div>
        )}

        <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
          <Compass className="w-3.5 h-3.5 text-blue-400" />
          <span>North ↑</span>
          <span>•</span>
          <span>Scale 1:{Math.round(1000 / scale)}</span>
        </div>
      </div>

      {/* SVG Canvas Container */}
      <div className="relative p-4 flex items-center justify-center min-h-[360px] bg-[#070b12] overflow-auto">
        <svg
          width={svgWidth}
          height={svgHeight}
          className="select-none filter drop-shadow-md"
        >
          {/* Subtle Background Grid */}
          <defs>
            <pattern id="grid" width={scale} height={scale} patternUnits="userSpaceOnUse">
              <path d={`M ${scale} 0 L 0 0 0 ${scale}`} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width={svgWidth} height={svgHeight} fill="url(#grid)" />

          {/* Exterior Building Envelope Outline */}
          <rect
            x={padding}
            y={padding}
            width={layout.buildingEnvelope.widthM * scale}
            height={layout.buildingEnvelope.lengthM * scale}
            fill="none"
            stroke="#1e293b"
            strokeWidth="8"
            rx="4"
          />

          {/* Room Spaces */}
          {roomsOnFloor.map((room) => {
            const rx = padding + room.bounds.x * scale;
            const ry = padding + room.bounds.y * scale;
            const rw = room.bounds.width * scale;
            const rh = room.bounds.height * scale;
            const isHovered = hoveredRoom?.id === room.id;

            return (
              <g
                key={room.id}
                onMouseEnter={() => setHoveredRoom(room)}
                onMouseLeave={() => setHoveredRoom(null)}
                className="cursor-pointer transition-all"
              >
                {/* Room Fill */}
                <rect
                  x={rx}
                  y={ry}
                  width={rw}
                  height={rh}
                  fill={room.color}
                  fillOpacity={isHovered ? 0.45 : 0.22}
                  stroke={isHovered ? '#38bdf8' : '#334155'}
                  strokeWidth={isHovered ? '2.5' : '1.5'}
                  rx="2"
                />

                {/* Room Label & Area */}
                {rw > 45 && rh > 35 && (
                  <>
                    <text
                      x={rx + rw / 2}
                      y={ry + rh / 2 - 6}
                      textAnchor="middle"
                      fill="#f8fafc"
                      fontSize={rw < 80 ? "10" : "11"}
                      fontWeight="600"
                      fontFamily="Inter, sans-serif"
                    >
                      {room.name}
                    </text>
                    <text
                      x={rx + rw / 2}
                      y={ry + rh / 2 + 10}
                      textAnchor="middle"
                      fill="#94a3b8"
                      fontSize="9.5"
                      fontFamily="JetBrains Mono, monospace"
                    >
                      {room.areaSqm} m² ({Math.round(room.areaSqm * 10.7639)} sqft)
                    </text>
                  </>
                )}
              </g>
            );
          })}

          {/* Structural Columns Grid */}
          {layout.columns.map((col) => {
            const cx = padding + col.x * scale - 4;
            const cy = padding + col.y * scale - 6;
            return (
              <rect
                key={col.id}
                x={cx}
                y={cy}
                width={8}
                height={12}
                fill="#f43f5e"
                stroke="#ffffff"
                strokeWidth="1"
                rx="1"
              >
                <title>{`Structural Column ${col.id} (300x450mm)`}</title>
              </rect>
            );
          })}
        </svg>

        {/* Hover Info Tooltip */}
        {hoveredRoom && (
          <div className="absolute bottom-3 left-4 glass-panel px-3 py-1.5 flex items-center gap-3 text-xs font-mono">
            <span className="text-white font-bold">{hoveredRoom.name}</span>
            <span className="text-slate-400">Dim: {hoveredRoom.widthM}m × {hoveredRoom.lengthM}m</span>
            <span className="text-cyan-400 font-bold">{hoveredRoom.areaSqm} m²</span>
            <span className="text-slate-500 uppercase">{hoveredRoom.zone}</span>
          </div>
        )}
      </div>

      {/* Legend & Column Schedule */}
      <div className="px-4 py-2 bg-slate-900/60 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm bg-blue-500/40 border border-blue-400" />
            <span>Public / Living</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm bg-indigo-500/40 border border-indigo-400" />
            <span>Private Suites</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm bg-amber-500/40 border border-amber-400" />
            <span>Kitchen / Wet Service</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-3 rounded-sm bg-rose-500 border border-white" />
            <span>RCC Column (300x450)</span>
          </div>
        </div>

        <span className="font-mono text-emerald-400">NBC 2016 Compliant</span>
      </div>
    </div>
  );
};
