import React from 'react';
import { 
  Pentagon, 
  Route, 
  ShieldAlert, 
  Maximize2, 
  Home, 
  Car, 
  Ruler, 
  Layers, 
  X 
} from 'lucide-react';
import { MapLayersVisibility } from './types';

interface LayerControlProps {
  layers: MapLayersVisibility;
  onToggleLayer: (key: keyof MapLayersVisibility) => void;
  onClose: () => void;
}

export const LayerControl: React.FC<LayerControlProps> = ({
  layers,
  onToggleLayer,
  onClose
}) => {
  const layerItems: {
    key: keyof MapLayersVisibility;
    label: string;
    description: string;
    icon: React.ReactNode;
    color: string;
  }[] = [
    {
      key: 'parcel',
      label: 'Gross Parcel Boundary',
      description: 'Cadastral land perimeter & digitized vertices',
      icon: <Pentagon className="w-3.5 h-3.5" />,
      color: 'text-sky-400'
    },
    {
      key: 'roadContext',
      label: 'Road & Frontage Context',
      description: 'Frontage edge & statutory road widening band',
      icon: <Route className="w-3.5 h-3.5" />,
      color: 'text-amber-400'
    },
    {
      key: 'setbacks',
      label: 'Marginal Setbacks',
      description: 'DCPR 2034 front, rear & side open spaces',
      icon: <ShieldAlert className="w-3.5 h-3.5" />,
      color: 'text-rose-400'
    },
    {
      key: 'buildableEnvelope',
      label: 'Net Buildable Envelope',
      description: 'Permissible build zone post deductions',
      icon: <Maximize2 className="w-3.5 h-3.5" />,
      color: 'text-emerald-400'
    },
    {
      key: 'buildingFootprint',
      label: 'Proposed Building Footprint',
      description: 'Parametric house option silhouette (Option A/B/C)',
      icon: <Home className="w-3.5 h-3.5" />,
      color: 'text-indigo-400'
    },
    {
      key: 'parking',
      label: 'Parking & Circulation Layout',
      description: 'Mandatory standard & accessible stalls',
      icon: <Car className="w-3.5 h-3.5" />,
      color: 'text-cyan-400'
    },
    {
      key: 'measurements',
      label: 'Map Distance & Area Overlays',
      description: 'User-measured metric distance & area paths',
      icon: <Ruler className="w-3.5 h-3.5" />,
      color: 'text-purple-400'
    }
  ];

  return (
    <div className="absolute right-4 top-20 z-20 w-72 glass-panel p-3.5 border border-white/10 shadow-2xl bg-slate-950/95 backdrop-blur-md rounded-xl select-none animate-in fade-in">
      <div className="flex items-center justify-between border-b border-white/10 pb-2 mb-2.5">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h4 className="font-display font-bold text-xs uppercase tracking-wider text-white">
            GIS Layer Control
          </h4>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white p-0.5">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-1.5">
        {layerItems.map((item) => {
          const isChecked = layers[item.key];
          return (
            <label
              key={item.key}
              className={`flex items-start gap-2.5 p-2 rounded-lg cursor-pointer transition-colors ${
                isChecked ? 'bg-white/5 border border-white/5' : 'hover:bg-white/5 opacity-60'
              }`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => onToggleLayer(item.key)}
                className="mt-0.5 accent-blue-500 w-3.5 h-3.5 rounded"
              />
              <div className="flex-1">
                <div className="flex items-center gap-1.5">
                  <span className={item.color}>{item.icon}</span>
                  <span className="text-xs font-semibold text-white">{item.label}</span>
                </div>
                <span className="text-[10px] text-slate-400 block leading-tight mt-0.5">
                  {item.description}
                </span>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
};
