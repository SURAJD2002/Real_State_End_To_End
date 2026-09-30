import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, X, Check, AlertCircle, Building2 } from 'lucide-react';
import { SiteLocationMetadata } from './types';

interface LocationSearchProps {
  accessToken: string;
  onSelectLocation: (site: SiteLocationMetadata) => void;
  onFlyToLocation: (lng: number, lat: number) => void;
}

interface GeocodeFeature {
  id: string;
  place_name: string;
  text: string;
  center: [number, number]; // [lng, lat]
  context?: Array<{ id: string; text: string }>;
}

export const LocationSearch: React.FC<LocationSearchProps> = ({
  accessToken,
  onSelectLocation,
  onFlyToLocation
}) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<GeocodeFeature[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [pendingLocation, setPendingLocation] = useState<SiteLocationMetadata | null>(null);
  const searchRef = useRef<HTMLDivElement | null>(null);

  // Prominent Mumbai real estate development benchmarks for instant reference / offline fallback
  const presetLocations: GeocodeFeature[] = [
    {
      id: 'loc-bandra-east',
      place_name: 'Bandra East Transit Corridor, Western Express Highway, Mumbai, Maharashtra 400051',
      text: 'Bandra East Transit Corridor',
      center: [72.8685, 19.1128],
      context: [{ id: 'place', text: 'Mumbai' }, { id: 'region', text: 'Maharashtra' }]
    },
    {
      id: 'loc-bkc-gblock',
      place_name: 'Bandra Kurla Complex (BKC) G-Block, Mumbai, Maharashtra 400051',
      text: 'BKC G-Block Commercial & Mixed-Use',
      center: [72.8647, 19.0664],
      context: [{ id: 'place', text: 'Mumbai' }, { id: 'region', text: 'Maharashtra' }]
    },
    {
      id: 'loc-worli-seaface',
      place_name: 'Worli Sea Face, Coastal Road Interchange, Mumbai, Maharashtra 400030',
      text: 'Worli Coastal Development Zone',
      center: [72.8162, 19.0144],
      context: [{ id: 'place', text: 'Mumbai' }, { id: 'region', text: 'Maharashtra' }]
    },
    {
      id: 'loc-andheri-midc',
      place_name: 'MIDC Central Road, Andheri East, Mumbai, Maharashtra 400093',
      text: 'Andheri East Urban Hub',
      center: [72.8777, 19.1235],
      context: [{ id: 'place', text: 'Mumbai' }, { id: 'region', text: 'Maharashtra' }]
    },
    {
      id: 'loc-navi-mumbai-aerocity',
      place_name: 'Navi Mumbai International Airport Zone, Ulwe, Navi Mumbai 410206',
      text: 'Navi Mumbai Aero-City Node',
      center: [73.0694, 18.9902],
      context: [{ id: 'place', text: 'Navi Mumbai' }, { id: 'region', text: 'Maharashtra' }]
    }
  ];

  // Debounced search query
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      if (accessToken && accessToken.trim().startsWith('pk.')) {
        try {
          const endpoint = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(
            query
          )}.json?access_token=${accessToken}&country=IN&types=address,poi,neighborhood,locality&limit=5`;
          const res = await fetch(endpoint);
          if (res.ok) {
            const data = await res.json();
            if (data.features && data.features.length > 0) {
              setSuggestions(data.features);
              setIsLoading(false);
              return;
            }
          }
        } catch (err) {
          console.warn('Mapbox Geocoding API failed, falling back to local dataset', err);
        }
      }

      // Filter preset benchmarks if token missing or API returned empty
      const lower = query.toLowerCase();
      const filtered = presetLocations.filter(
        (p) => p.text.toLowerCase().includes(lower) || p.place_name.toLowerCase().includes(lower)
      );
      setSuggestions(filtered.length > 0 ? filtered : presetLocations.slice(0, 3));
      setIsLoading(false);
    }, 280);

    return () => clearTimeout(timer);
  }, [query, accessToken]);

  // Click outside listener to close suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectFeature = (feat: GeocodeFeature) => {
    const city = feat.context?.find((c) => c.id.startsWith('place'))?.text || 'Mumbai';
    const state = feat.context?.find((c) => c.id.startsWith('region'))?.text || 'Maharashtra';

    const locationMeta: SiteLocationMetadata = {
      address: feat.place_name,
      city,
      state,
      coordinates: feat.center,
      mapboxFeatureId: feat.id,
      provenance: 'MAPBOX',
      geometryVersion: 'PV-001',
      timestamp: new Date().toISOString()
    };

    setPendingLocation(locationMeta);
    setQuery(feat.text);
    setIsOpen(false);
    onFlyToLocation(feat.center[0], feat.center[1]);
  };

  const handleConfirmLocation = () => {
    if (!pendingLocation) return;
    onSelectLocation(pendingLocation);
    setPendingLocation(null);
  };

  return (
    <div ref={searchRef} className="absolute left-4 top-4 z-30 w-96 select-none">
      {/* Search Input Box */}
      <div className="glass-panel p-1.5 flex items-center gap-2 border border-white/10 shadow-2xl bg-slate-950/90 backdrop-blur-md">
        <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0">
          <Search className="w-4 h-4 text-cyan-400" />
        </div>

        <input
          type="text"
          value={query}
          onFocus={() => setIsOpen(true)}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          placeholder="Search address, locality, landmark..."
          className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-400 focus:outline-none font-sans"
        />

        {query && (
          <button
            onClick={() => {
              setQuery('');
              setSuggestions([]);
              setPendingLocation(null);
            }}
            className="p-1 hover:text-white text-slate-400 rounded"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Auto-complete Suggestions Dropdown */}
      {isOpen && (
        <div className="glass-panel mt-1.5 p-1 border border-white/10 shadow-2xl bg-[#090d16]/95 backdrop-blur-lg rounded-xl max-h-64 overflow-y-auto">
          {isLoading ? (
            <div className="p-3 text-center text-xs text-slate-400 font-mono">
              Searching Mapbox Geocoding...
            </div>
          ) : suggestions.length > 0 ? (
            <div className="divide-y divide-white/5">
              {suggestions.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleSelectFeature(item)}
                  className="p-2.5 hover:bg-blue-600/10 hover:border-l-2 hover:border-cyan-400 cursor-pointer transition-all flex items-start gap-2.5 rounded-lg"
                >
                  <MapPin className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-xs font-bold text-white block">{item.text}</span>
                    <span className="text-[10px] text-slate-400 block line-clamp-1">
                      {item.place_name}
                    </span>
                    <span className="text-[9px] font-mono text-slate-500 block mt-0.5">
                      {item.center[1].toFixed(5)}°N, {item.center[0].toFixed(5)}°E
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 text-center text-xs text-slate-400">
              No matching locations found.
            </div>
          )}
        </div>
      )}

      {/* Selected Location Confirmation Card (Section 6) */}
      {pendingLocation && (
        <div className="glass-panel mt-2 p-3.5 border border-cyan-500/40 shadow-2xl bg-slate-950/95 rounded-xl space-y-2.5 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <div className="flex items-center gap-1.5">
              <Building2 className="w-4 h-4 text-cyan-400" />
              <h4 className="font-display font-bold text-xs text-white uppercase tracking-wider">
                Site Location Found
              </h4>
            </div>
            <button
              onClick={() => setPendingLocation(null)}
              className="text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-1 text-xs">
            <div className="text-slate-300 font-medium line-clamp-2">
              {pendingLocation.address}
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400 pt-0.5">
              <span>City: <strong className="text-white">{pendingLocation.city}</strong></span>
              <span>•</span>
              <span>State: <strong className="text-white">{pendingLocation.state}</strong></span>
            </div>
            <div className="text-[10px] font-mono text-cyan-300">
              Coordinates: {pendingLocation.coordinates[1].toFixed(5)}°N, {pendingLocation.coordinates[0].toFixed(5)}°E
            </div>
          </div>

          {/* Statutory Evidence Disclaimer */}
          <div className="p-2 rounded bg-amber-950/30 border border-amber-800/40 flex items-start gap-1.5 text-[10px] text-amber-300/90 leading-tight">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
            <span>
              <strong>Initial Site Reference:</strong> Mapbox search establishes project geographic context. Legal parcel boundaries require CAD polygon digitization or official revenue CTS revenue maps.
            </span>
          </div>

          {/* Confirm Button */}
          <button
            onClick={handleConfirmLocation}
            className="w-full py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-display font-bold text-xs shadow-md shadow-blue-500/20 flex items-center justify-center gap-1.5 transition-all active:scale-95"
          >
            <Check className="w-3.5 h-3.5" />
            <span>USE THIS LOCATION AS PROJECT SITE</span>
          </button>
        </div>
      )}
    </div>
  );
};
