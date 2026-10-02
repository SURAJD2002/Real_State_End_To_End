import React, { useState, useEffect } from 'react';
import { X, Check, Compass, HelpCircle } from 'lucide-react';
import { Coordinate, wgs84ToUtm43N, computeDestinationCoord } from './cadGeometry';

// ==========================================
// 1. COORDINATE EDITOR MODAL (Section 20)
// ==========================================
interface CoordinateEditorModalProps {
  isOpen: boolean;
  vertexIndex: number;
  initialCoord: Coordinate;
  onApply: (newCoord: Coordinate) => void;
  onClose: () => void;
}

export const CoordinateEditorModal: React.FC<CoordinateEditorModalProps> = ({
  isOpen,
  vertexIndex,
  initialCoord,
  onApply,
  onClose
}) => {
  const [lng, setLng] = useState<string>(String(initialCoord[0]));
  const [lat, setLat] = useState<string>(String(initialCoord[1]));
  const [utm, setUtm] = useState(wgs84ToUtm43N(initialCoord));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLng(String(initialCoord[0]));
    setLat(String(initialCoord[1]));
    setUtm(wgs84ToUtm43N(initialCoord));
    setError(null);
  }, [initialCoord]);

  if (!isOpen) return null;

  const handleApply = () => {
    const parsedLng = parseFloat(lng);
    const parsedLat = parseFloat(lat);

    if (isNaN(parsedLng) || parsedLng < -180 || parsedLng > 180) {
      setError('Invalid Longitude. Must be between -180 and 180.');
      return;
    }
    if (isNaN(parsedLat) || parsedLat < -90 || parsedLat > 90) {
      setError('Invalid Latitude. Must be between -90 and 90.');
      return;
    }

    onApply([parsedLng, parsedLat]);
    onClose();
  };

  const handleLatChange = (val: string) => {
    setLat(val);
    const pLat = parseFloat(val);
    const pLng = parseFloat(lng);
    if (!isNaN(pLat) && !isNaN(pLng)) {
      setUtm(wgs84ToUtm43N([pLng, pLat]));
    }
  };

  const handleLngChange = (val: string) => {
    setLng(val);
    const pLat = parseFloat(lat);
    const pLng = parseFloat(val);
    if (!isNaN(pLat) && !isNaN(pLng)) {
      setUtm(wgs84ToUtm43N([pLng, pLat]));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm select-none">
      <div className="w-96 glass-panel p-5 bg-slate-950/95 border border-white/10 rounded-2xl shadow-2xl text-xs space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-mono font-bold">
              V{vertexIndex + 1}
            </div>
            <div>
              <h3 className="text-white font-display font-bold text-sm">Coordinate Editor</h3>
              <p className="text-[10px] text-slate-400 font-mono">Cadastral Vertex Precision Entry</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-white/5">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[11px]">
            {error}
          </div>
        )}

        {/* Inputs */}
        <div className="space-y-3">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-mono mb-1">
              Latitude (WGS84 EPSG:4326)
            </label>
            <input
              type="number"
              step="0.000001"
              value={lat}
              onChange={(e) => handleLatChange(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-white font-mono text-xs focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-mono mb-1">
              Longitude (WGS84 EPSG:4326)
            </label>
            <input
              type="number"
              step="0.000001"
              value={lng}
              onChange={(e) => handleLngChange(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-white font-mono text-xs focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Projected Engineering Survey Coordinates (UTM 43N) */}
        <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1.5 font-mono">
          <div className="text-[9px] uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Projected Engineering Survey Grid</span>
            <span className="text-cyan-400 font-bold">{utm.crs}</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
            <div>
              <span className="text-[9px] text-slate-500 block">Easting (X)</span>
              <span className="text-slate-200 font-bold">{utm.easting.toLocaleString()} m</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 block">Northing (Y)</span>
              <span className="text-slate-200 font-bold">{utm.northing.toLocaleString()} m</span>
            </div>
          </div>
          <p className="text-[9px] text-slate-500 pt-1 leading-normal">
            Authoritative statutory calculations are resolved by the PostGIS backend engine.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-sans font-medium text-xs transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs flex items-center gap-1.5 shadow-md shadow-blue-600/30 transition-all"
          >
            <Check className="w-3.5 h-3.5" />
            <span>APPLY COORDINATES</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 2. BEARING & DISTANCE EDITOR (Section 21)
// ==========================================
interface EdgeEditorModalProps {
  isOpen: boolean;
  edgeId: string;
  startCoord: Coordinate;
  currentLengthM: number;
  currentBearingDeg: number;
  onApply: (newEndCoord: Coordinate) => void;
  onClose: () => void;
}

export const EdgeEditorModal: React.FC<EdgeEditorModalProps> = ({
  isOpen,
  edgeId,
  startCoord,
  currentLengthM,
  currentBearingDeg,
  onApply,
  onClose
}) => {
  const [lengthM, setLengthM] = useState<string>(String(currentLengthM));
  const [bearingDeg, setBearingDeg] = useState<string>(String(currentBearingDeg));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLengthM(String(currentLengthM));
    setBearingDeg(String(currentBearingDeg));
    setError(null);
  }, [currentLengthM, currentBearingDeg]);

  if (!isOpen) return null;

  const handleApply = () => {
    const pLength = parseFloat(lengthM);
    const pBearing = parseFloat(bearingDeg);

    if (isNaN(pLength) || pLength <= 0.2) {
      setError('Length must be greater than 0.20 meters.');
      return;
    }
    if (isNaN(pBearing) || pBearing < 0 || pBearing >= 360) {
      setError('Bearing must be between 0° and 359.9° (clockwise from True North).');
      return;
    }

    const nextEndCoord = computeDestinationCoord(startCoord, pLength, pBearing);
    onApply(nextEndCoord);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm select-none">
      <div className="w-96 glass-panel p-5 bg-slate-950/95 border border-white/10 rounded-2xl shadow-2xl text-xs space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-mono font-bold">
              {edgeId}
            </div>
            <div>
              <h3 className="text-white font-display font-bold text-sm">Edge Dimension Editor</h3>
              <p className="text-[10px] text-slate-400 font-mono">Bearing & Distance Geometric Precision</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-white/5">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[11px]">
            {error}
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-mono mb-1">
              Length (Meters)
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.01"
                min="0.2"
                value={lengthM}
                onChange={(e) => setLengthM(e.target.value)}
                className="w-full px-3 py-1.5 pr-8 rounded-lg bg-slate-900 border border-white/10 text-white font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
              <span className="absolute right-3 top-1.5 text-slate-500 font-mono text-xs">m</span>
            </div>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-mono mb-1">
              Bearing (Degrees Clockwise from True North)
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.1"
                min="0"
                max="359.9"
                value={bearingDeg}
                onChange={(e) => setBearingDeg(e.target.value)}
                className="w-full px-3 py-1.5 pr-8 rounded-lg bg-slate-900 border border-white/10 text-white font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
              <span className="absolute right-3 top-1.5 text-slate-500 font-mono text-xs">°</span>
            </div>
          </div>
        </div>

        <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 flex items-start gap-2 text-[10px] text-slate-400 leading-normal">
          <Compass className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <span>
            Applying updates the terminating vertex position deterministically using ellipsoidal forward projection from the origin vertex.
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-sans font-medium text-xs transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-sans font-bold text-xs flex items-center gap-1.5 shadow-md shadow-cyan-600/30 transition-all"
          >
            <Check className="w-3.5 h-3.5" />
            <span>APPLY DIMENSION</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 3. KEYBOARD SHORTCUTS MODAL (Section 35)
// ==========================================
interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const KeyboardShortcutsModal: React.FC<KeyboardShortcutsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const shortcuts = [
    { key: 'V', desc: 'Select & Pan tool' },
    { key: 'P', desc: 'Draw Land Parcel mode' },
    { key: 'E', desc: 'Edit Vertices & Edges mode' },
    { key: 'M', desc: 'Measure Distance & Area mode' },
    { key: 'O', desc: 'Toggle ORTHO mode (0°, 45°, 90°)' },
    { key: 'G', desc: 'Toggle Metric Grid snap' },
    { key: 'Z', desc: 'Zoom / Fit extents to Parcel' },
    { key: 'Cmd/Ctrl + Z', desc: 'Undo geometry operation' },
    { key: 'Cmd/Ctrl + Shift + Z', desc: 'Redo geometry operation' },
    { key: 'Delete / Backspace', desc: 'Delete selected vertex' },
    { key: 'Esc', desc: 'Cancel drawing / Deselect element' },
    { key: 'Double Click Edge', desc: 'Insert midpoint vertex' },
    { key: 'Double Click Vertex', desc: 'Open coordinate editor' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm select-none">
      <div className="w-[420px] glass-panel p-5 bg-slate-950/95 border border-white/10 rounded-2xl shadow-2xl text-xs space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-white font-display font-bold text-sm">CAD Keyboard Shortcuts</h3>
              <p className="text-[10px] text-slate-400 font-mono">Planwise CAD Digitization Controls</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-white/5">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-1.5 max-h-[380px] overflow-y-auto pr-1">
          {shortcuts.map((s) => (
            <div
              key={s.key}
              className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-white/5 hover:border-white/10 transition-colors"
            >
              <span className="text-slate-300 font-sans text-xs">{s.desc}</span>
              <kbd className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-cyan-300 font-mono font-bold text-[11px] shadow-sm">
                {s.key}
              </kbd>
            </div>
          ))}
        </div>

        <div className="pt-2 border-t border-white/10 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-bold text-xs transition-all"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
