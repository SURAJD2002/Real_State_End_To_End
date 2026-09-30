import React, { useEffect, useRef, useState } from 'react';
import maplibregl, { Map } from 'maplibre-gl';
import { ToolMode } from '../types';
import { Crosshair } from 'lucide-react';

interface MapCanvasProps {
  toolMode: ToolMode;
  coordinates: [number, number][];
  buildableCoordinates?: [number, number][];
  onAddCoordinate: (coord: [number, number]) => void;
  onUpdateCoordinates: (coords: [number, number][]) => void;
}

export const MapCanvas: React.FC<MapCanvasProps> = ({
  toolMode,
  coordinates,
  buildableCoordinates,
  onAddCoordinate
}) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const map = useRef<Map | null>(null);
  const [cursorPos, setCursorPos] = useState<{ lng: number; lat: number }>({ lng: 72.8697, lat: 19.1133 });

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Initialize MapLibre GL map instance
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm-tiles': {
            type: 'raster',
            tiles: [
              'https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
          }
        },
        layers: [
          {
            id: 'osm-tiles-layer',
            type: 'raster',
            source: 'osm-tiles',
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [72.8697, 19.1133], // Mumbai Suburban (Bandra / Andheri corridor)
      zoom: 15.2,
      pitch: 35,
      bearing: -15
    });

    map.current.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');

    map.current.on('mousemove', (e) => {
      setCursorPos({
        lng: Number(e.lngLat.lng.toFixed(5)),
        lat: Number(e.lngLat.lat.toFixed(5))
      });
    });

    map.current.on('load', () => {
      if (!map.current) return;

      // 1. Add GeoJSON source for Gross Parcel Polygon
      map.current.addSource('parcel-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      // Parcel Fill
      map.current.addLayer({
        id: 'parcel-fill',
        type: 'fill',
        source: 'parcel-source',
        paint: {
          'fill-color': '#0ea5e9',
          'fill-opacity': 0.22
        }
      });

      // Parcel Outer Boundary Outline
      map.current.addLayer({
        id: 'parcel-outline',
        type: 'line',
        source: 'parcel-source',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 2.5,
          'line-dasharray': [1, 0]
        }
      });

      // Parcel Vertices
      map.current.addLayer({
        id: 'parcel-vertices',
        type: 'circle',
        source: 'parcel-source',
        paint: {
          'circle-radius': 5,
          'circle-color': '#ffffff',
          'circle-stroke-color': '#0284c7',
          'circle-stroke-width': 2
        },
        filter: ['==', '$type', 'Point']
      });

      // 2. Add GeoJSON source for Net Buildable Setback Envelope
      map.current.addSource('buildable-source', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: []
        }
      });

      map.current.addLayer({
        id: 'buildable-fill',
        type: 'fill',
        source: 'buildable-source',
        paint: {
          'fill-color': '#10b981',
          'fill-opacity': 0.35
        }
      });

      map.current.addLayer({
        id: 'buildable-outline',
        type: 'line',
        source: 'buildable-source',
        paint: {
          'line-color': '#34d399',
          'line-width': 2,
          'line-dasharray': [3, 2]
        }
      });
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Update map canvas click handler based on current tool mode
  useEffect(() => {
    if (!map.current) return;

    const handleMapClick = (e: maplibregl.MapMouseEvent) => {
      if (toolMode === 'DRAW_PARCEL') {
        onAddCoordinate([e.lngLat.lng, e.lngLat.lat]);
      }
    };

    map.current.on('click', handleMapClick);
    return () => {
      if (map.current) {
        map.current.off('click', handleMapClick);
      }
    };
  }, [toolMode, onAddCoordinate]);

  // Sync Polygon Geometries to MapLibre Layers
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    const parcelSource = map.current.getSource('parcel-source') as maplibregl.GeoJSONSource;
    if (parcelSource) {
      if (coordinates.length >= 3) {
        const closedCoords = [...coordinates];
        if (closedCoords[0] !== closedCoords[closedCoords.length - 1]) {
          closedCoords.push(closedCoords[0]);
        }

        const features: GeoJSON.Feature[] = [
          {
            type: 'Feature',
            geometry: {
              type: 'Polygon',
              coordinates: [closedCoords]
            },
            properties: {}
          },
          ...coordinates.map((pt, i) => ({
            type: 'Feature' as const,
            geometry: {
              type: 'Point' as const,
              coordinates: pt
            },
            properties: { index: i }
          }))
        ];

        parcelSource.setData({
          type: 'FeatureCollection',
          features
        });
      } else {
        parcelSource.setData({
          type: 'FeatureCollection',
          features: []
        });
      }
    }

    const buildableSource = map.current.getSource('buildable-source') as maplibregl.GeoJSONSource;
    if (buildableSource) {
      if (buildableCoordinates && buildableCoordinates.length >= 3) {
        const closed = [...buildableCoordinates];
        if (closed[0] !== closed[closed.length - 1]) {
          closed.push(closed[0]);
        }
        buildableSource.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: {
                type: 'Polygon',
                coordinates: [closed]
              },
              properties: { label: 'Net Buildable Envelope' }
            }
          ]
        });
      } else {
        buildableSource.setData({
          type: 'FeatureCollection',
          features: []
        });
      }
    }
  }, [coordinates, buildableCoordinates]);

  return (
    <div className="relative w-full h-[calc(100vh-56px)] bg-[#080c14]">
      {/* Map Container */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* Coordinate & CAD Crosshair Readout Overlay */}
      <div className="absolute left-4 bottom-4 z-20 glass-toolbar px-3 py-1.5 flex items-center gap-3 text-[11px] font-mono text-slate-300">
        <div className="flex items-center gap-1.5 text-cyan-400">
          <Crosshair className="w-3.5 h-3.5" />
          <span>WGS84: {cursorPos.lat.toFixed(5)}°N, {cursorPos.lng.toFixed(5)}°E</span>
        </div>
        <div className="h-3 w-px bg-white/10" />
        <span className="text-slate-400">CRS: EPSG:4326 | UTM 43N</span>
        <div className="h-3 w-px bg-white/10" />
        <span className="text-emerald-400">{coordinates.length} Vertices</span>
      </div>

      {/* Drawing mode hint indicator */}
      {toolMode === 'DRAW_PARCEL' && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 bg-blue-600/90 backdrop-blur-md px-4 py-1.5 rounded-full text-white text-xs font-medium shadow-lg animate-pulse">
          Click on the map to place parcel boundary vertices. Add at least 3 vertices to close polygon.
        </div>
      )}
    </div>
  );
};
