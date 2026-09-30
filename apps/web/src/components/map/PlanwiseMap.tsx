import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { 
  MapInteractionMode, 
  MapLayersVisibility, 
  SiteLocationMetadata, 
  MeasurementState,
  SelectedMapElement 
} from './types';
import { LocationSearch } from './LocationSearch';
import { MapToolbar } from './MapToolbar';
import { LayerControl } from './LayerControl';
import { MapInspector } from './MapInspector';
import { NorthScaleIndicator } from './NorthScaleIndicator';
import { MeasurementOverlay } from './MeasurementOverlay';
import { HouseOption, FeasibilityResult } from '../../types';
import { AlertTriangle, Info } from 'lucide-react';

interface PlanwiseMapProps {
  coordinates: [number, number][];
  buildableCoordinates?: [number, number][];
  selectedOption?: HouseOption | null;
  feasibility?: FeasibilityResult | null;
  existingRoadWidth: number;
  proposedRoadWidth: number;
  onChangeRoadWidths: (existing: number, proposed: number) => void;
  onAddCoordinate: (coord: [number, number]) => void;
  onUpdateCoordinates: (coords: [number, number][]) => void;
  onClearCoordinates: () => void;
  onSaveSiteGeometry: (metadata: SiteLocationMetadata) => Promise<void>;
  onSelectSiteLocation?: (metadata: SiteLocationMetadata) => void;
  onOpenFeasibility?: () => void;
  onOpenDesign?: () => void;
  isSavingGeometry?: boolean;
}

// Compute client-side spherical metric area and distance for live HUD display
function computeSphericalMetrics(coords: [number, number][]): { areaSqm: number; perimeterM: number } {
  if (coords.length < 3) return { areaSqm: 0, perimeterM: 0 };
  const refLat = coords[0][1];
  const mPerDegLat = 111132.95;
  const mPerDegLng = 111412.84 * Math.cos((refLat * Math.PI) / 180);

  // Shoelace area
  let area = 0;
  let perimeter = 0;
  for (let i = 0; i < coords.length; i++) {
    const j = (i + 1) % coords.length;
    const xi = coords[i][0] * mPerDegLng;
    const yi = coords[i][1] * mPerDegLat;
    const xj = coords[j][0] * mPerDegLng;
    const yj = coords[j][1] * mPerDegLat;
    area += xi * yj - xj * yi;

    const dx = xj - xi;
    const dy = yj - yi;
    perimeter += Math.sqrt(dx * dx + dy * dy);
  }
  return {
    areaSqm: Math.round(Math.abs(area) / 2),
    perimeterM: Math.round(perimeter * 10) / 10
  };
}

export const PlanwiseMap: React.FC<PlanwiseMapProps> = ({
  coordinates,
  buildableCoordinates,
  selectedOption,
  feasibility,
  existingRoadWidth,
  proposedRoadWidth,
  onChangeRoadWidths,
  onAddCoordinate,
  onUpdateCoordinates,
  onClearCoordinates,
  onSaveSiteGeometry,
  onSelectSiteLocation,
  onOpenFeasibility,
  onOpenDesign,
  isSavingGeometry = false
}) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markerRef = useRef<mapboxgl.Marker | null>(null);

  const rawToken = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || '';
  const hasValidMapboxToken = Boolean(rawToken && rawToken.trim().startsWith('pk.'));

  // UI state
  const [interactionMode, setInteractionMode] = useState<MapInteractionMode>('SELECT');
  const [isLayersOpen, setIsLayersOpen] = useState(false);
  const [selectedElement, setSelectedElement] = useState<SelectedMapElement>(null);
  const [cursorPos, setCursorPos] = useState<{ lat: number; lng: number }>({ lat: 19.1128, lng: 72.8685 });
  const [zoomLevel, setZoomLevel] = useState<number>(15.5);
  const [bearing, setBearing] = useState<number>(0);
  const [geometryVersion, setGeometryVersion] = useState<string>('PV-001');

  // Layers visibility
  const [layers, setLayers] = useState<MapLayersVisibility>({
    parcel: true,
    roadContext: true,
    setbacks: true,
    buildableEnvelope: true,
    buildingFootprint: true,
    parking: false,
    measurements: true
  });

  // Measurement tool state
  const [measurement, setMeasurement] = useState<MeasurementState>({
    points: [],
    totalDistanceM: 0,
    totalAreaSqm: 0,
    mode: null
  });

  const { areaSqm, perimeterM } = useMemo(() => computeSphericalMetrics(coordinates), [coordinates]);

  // Compute building footprint polygon centered in buildable envelope
  const footprintPolygon = useMemo(() => {
    if (!selectedOption) return null;
    const targetCoords = buildableCoordinates && buildableCoordinates.length >= 3 ? buildableCoordinates : coordinates;
    if (targetCoords.length < 3) return null;

    // Centroid of target envelope
    let sumLng = 0;
    let sumLat = 0;
    targetCoords.forEach(([lng, lat]) => {
      sumLng += lng;
      sumLat += lat;
    });
    const cLng = sumLng / targetCoords.length;
    const cLat = sumLat / targetCoords.length;

    const wM = selectedOption.layout.buildingEnvelope.widthM || 13.5;
    const lM = selectedOption.layout.buildingEnvelope.lengthM || 12.5;

    const dLat = (lM / 2) / 111132.95;
    const dLng = (wM / 2) / (111412.84 * Math.cos((cLat * Math.PI) / 180));

    return [
      [cLng - dLng, cLat - dLat],
      [cLng + dLng, cLat - dLat],
      [cLng + dLng, cLat + dLat],
      [cLng - dLng, cLat + dLat],
      [cLng - dLng, cLat - dLat]
    ];
  }, [selectedOption, buildableCoordinates, coordinates]);

  // Initialize Mapbox Map Instance
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    if (hasValidMapboxToken) {
      mapboxgl.accessToken = rawToken;
    }

    // Default to Mapbox dark-v11 if token valid, or fallback Carto dark raster if token not yet set
    const styleSpec = hasValidMapboxToken
      ? 'mapbox://styles/mapbox/dark-v11'
      : {
          version: 8,
          sources: {
            'carto-dark': {
              type: 'raster',
              tiles: ['https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap &copy; CARTO'
            }
          },
          layers: [
            {
              id: 'carto-dark-layer',
              type: 'raster',
              source: 'carto-dark',
              minzoom: 0,
              maxzoom: 19
            }
          ]
        };

    const initialCenter: [number, number] = coordinates.length > 0 ? coordinates[0] : [72.8685, 19.1128];

    const mapInst = new mapboxgl.Map({
      container: mapContainer.current,
      style: styleSpec as any,
      center: initialCenter,
      zoom: 15.5,
      pitch: 30,
      bearing: 0,
      attributionControl: true
    });

    mapInst.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'bottom-right');

    mapInst.on('mousemove', (e) => {
      setCursorPos({
        lat: Number(e.lngLat.lat.toFixed(5)),
        lng: Number(e.lngLat.lng.toFixed(5))
      });
    });

    mapInst.on('rotate', () => {
      setBearing(Math.round(mapInst.getBearing()));
    });

    mapInst.on('zoom', () => {
      setZoomLevel(Number(mapInst.getZoom().toFixed(1)));
    });

    mapInst.on('load', () => {
      if (!map.current) return;

      // 1. Gross Parcel Source & Layers
      mapInst.addSource('parcel-source', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInst.addLayer({
        id: 'parcel-fill',
        type: 'fill',
        source: 'parcel-source',
        paint: {
          'fill-color': '#0ea5e9',
          'fill-opacity': 0.18
        },
        filter: ['==', '$type', 'Polygon']
      });

      mapInst.addLayer({
        id: 'parcel-outline',
        type: 'line',
        source: 'parcel-source',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 2.5
        },
        filter: ['==', '$type', 'Polygon']
      });

      mapInst.addLayer({
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

      // 2. Net Buildable Envelope Source & Layers
      mapInst.addSource('buildable-source', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInst.addLayer({
        id: 'buildable-fill',
        type: 'fill',
        source: 'buildable-source',
        paint: {
          'fill-color': '#10b981',
          'fill-opacity': 0.32
        }
      });

      mapInst.addLayer({
        id: 'buildable-outline',
        type: 'line',
        source: 'buildable-source',
        paint: {
          'line-color': '#34d399',
          'line-width': 2,
          'line-dasharray': [3, 2]
        }
      });

      // 3. Proposed Building Footprint Source & Layer
      mapInst.addSource('footprint-source', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInst.addLayer({
        id: 'footprint-fill',
        type: 'fill',
        source: 'footprint-source',
        paint: {
          'fill-color': '#6366f1',
          'fill-opacity': 0.45
        }
      });

      mapInst.addLayer({
        id: 'footprint-outline',
        type: 'line',
        source: 'footprint-source',
        paint: {
          'line-color': '#a5b4fc',
          'line-width': 2.5
        }
      });

      // 4. Measurement Tool Source & Layer
      mapInst.addSource('measure-source', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInst.addLayer({
        id: 'measure-line',
        type: 'line',
        source: 'measure-source',
        paint: {
          'line-color': '#c084fc',
          'line-width': 2,
          'line-dasharray': [2, 2]
        },
        filter: ['==', '$type', 'LineString']
      });

      mapInst.addLayer({
        id: 'measure-fill',
        type: 'fill',
        source: 'measure-source',
        paint: {
          'fill-color': '#c084fc',
          'fill-opacity': 0.25
        },
        filter: ['==', '$type', 'Polygon']
      });

      mapInst.addLayer({
        id: 'measure-points',
        type: 'circle',
        source: 'measure-source',
        paint: {
          'circle-radius': 4.5,
          'circle-color': '#ffffff',
          'circle-stroke-color': '#9333ea',
          'circle-stroke-width': 2
        },
        filter: ['==', '$type', 'Point']
      });

      // Feature Click Listener for Map Inspector
      mapInst.on('click', (e) => {
        const features = mapInst.queryRenderedFeatures(e.point, {
          layers: ['footprint-fill', 'buildable-fill', 'parcel-fill']
        });

        if (features.length > 0) {
          const topLayerId = features[0].layer?.id;
          if (topLayerId === 'footprint-fill' && selectedOption) {
            setSelectedElement({
              type: 'BUILDING_FOOTPRINT',
              designVersionId: selectedOption.designVersionId,
              archetype: selectedOption.layout.archetype,
              widthM: selectedOption.layout.buildingEnvelope.widthM,
              lengthM: selectedOption.layout.buildingEnvelope.lengthM,
              buaSqm: Math.round(selectedOption.layout.totalGrossBUASqm)
            });
            return;
          }

          if (topLayerId === 'buildable-fill' && feasibility) {
            setSelectedElement({
              type: 'BUILDABLE',
              areaSqm: Math.round(feasibility.netDevelopableAreaSqm),
              setbackFrontM: feasibility.frontSetbackM || 6.0,
              setbackRearM: 4.5,
              setbackSideM: 3.0
            });
            return;
          }

          if (topLayerId === 'parcel-fill') {
            setSelectedElement({
              type: 'PARCEL',
              areaSqm: areaSqm,
              perimeterM: perimeterM,
              verticesCount: coordinates.length
            });
            return;
          }
        }
      });
    });

    map.current = mapInst;

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [hasValidMapboxToken, rawToken]);

  // Handle map interaction clicks (Draw, Measure, Inspect, Edit)
  useEffect(() => {
    if (!map.current) return;

    const handleCanvasClick = (e: mapboxgl.MapMouseEvent) => {
      const clickedPt: [number, number] = [e.lngLat.lng, e.lngLat.lat];

      if (interactionMode === 'DRAW_PARCEL') {
        onAddCoordinate(clickedPt);
      } else if (interactionMode === 'EDIT_PARCEL') {
        // Vertex selection/removal or insertion
        const threshold = 0.0003;
        const existingIdx = coordinates.findIndex(
          ([lng, lat]) => Math.abs(lng - clickedPt[0]) < threshold && Math.abs(lat - clickedPt[1]) < threshold
        );
        if (existingIdx !== -1 && coordinates.length > 3) {
          onUpdateCoordinates(coordinates.filter((_, i) => i !== existingIdx));
        } else {
          onUpdateCoordinates([...coordinates, clickedPt]);
        }
      } else if (interactionMode === 'MEASURE_DISTANCE' || interactionMode === 'MEASURE_AREA') {
        setMeasurement((prev) => {
          const nextPts = [...prev.points, clickedPt];
          const metrics = computeSphericalMetrics(nextPts);
          return {
            ...prev,
            points: nextPts,
            totalDistanceM: metrics.perimeterM,
            totalAreaSqm: metrics.areaSqm,
            mode: interactionMode === 'MEASURE_DISTANCE' ? 'DISTANCE' : 'AREA'
          };
        });
      }
    };

    map.current.on('click', handleCanvasClick);
    return () => {
      if (map.current) {
        map.current.off('click', handleCanvasClick);
      }
    };
  }, [interactionMode, onAddCoordinate, onUpdateCoordinates, coordinates]);

  // Sync Parcel & Buildable Coordinates to Mapbox GeoJSON Sources
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    // 1. Parcel Source
    const parcelSource = map.current.getSource('parcel-source') as mapboxgl.GeoJSONSource;
    if (parcelSource) {
      if (coordinates.length >= 3 && layers.parcel) {
        const closed = [...coordinates];
        if (closed[0] !== closed[closed.length - 1]) closed.push(closed[0]);

        const features: GeoJSON.Feature[] = [
          {
            type: 'Feature',
            geometry: { type: 'Polygon', coordinates: [closed] },
            properties: { id: 'gross-parcel' }
          },
          ...coordinates.map((pt, i) => ({
            type: 'Feature' as const,
            geometry: { type: 'Point' as const, coordinates: pt },
            properties: { vertexIndex: i }
          }))
        ];

        parcelSource.setData({ type: 'FeatureCollection', features });
      } else {
        parcelSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 2. Net Buildable Envelope Source
    const buildableSource = map.current.getSource('buildable-source') as mapboxgl.GeoJSONSource;
    if (buildableSource) {
      if (buildableCoordinates && buildableCoordinates.length >= 3 && layers.buildableEnvelope) {
        const closed = [...buildableCoordinates];
        if (closed[0] !== closed[closed.length - 1]) closed.push(closed[0]);

        buildableSource.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Polygon', coordinates: [closed] },
              properties: { id: 'net-buildable-envelope' }
            }
          ]
        });
      } else {
        buildableSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 3. Proposed Building Footprint Source
    const footprintSource = map.current.getSource('footprint-source') as mapboxgl.GeoJSONSource;
    if (footprintSource) {
      if (footprintPolygon && layers.buildingFootprint) {
        footprintSource.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Polygon', coordinates: [footprintPolygon] },
              properties: {
                id: 'proposed-footprint',
                optionId: selectedOption?.optionId,
                designVersion: selectedOption?.designVersionId
              }
            }
          ]
        });
      } else {
        footprintSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 4. Measurement Overlay Source
    const measureSource = map.current.getSource('measure-source') as mapboxgl.GeoJSONSource;
    if (measureSource) {
      if (measurement.points.length >= 2 && layers.measurements) {
        const features: GeoJSON.Feature[] = [
          {
            type: 'Feature',
            geometry: { type: 'LineString', coordinates: measurement.points },
            properties: {}
          },
          ...measurement.points.map((pt) => ({
            type: 'Feature' as const,
            geometry: { type: 'Point' as const, coordinates: pt },
            properties: {}
          }))
        ];

        if (measurement.mode === 'AREA' && measurement.points.length >= 3) {
          const closed = [...measurement.points, measurement.points[0]];
          features.push({
            type: 'Feature',
            geometry: { type: 'Polygon', coordinates: [closed] },
            properties: {}
          });
        }

        measureSource.setData({ type: 'FeatureCollection', features });
      } else {
        measureSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }
  }, [coordinates, buildableCoordinates, footprintPolygon, measurement, layers, selectedOption]);

  // Fly to location handler
  const handleFlyToLocation = useCallback((lng: number, lat: number) => {
    if (!map.current) return;
    map.current.flyTo({
      center: [lng, lat],
      zoom: 16.5,
      pitch: 35,
      essential: true
    });

    if (markerRef.current) markerRef.current.remove();
    markerRef.current = new mapboxgl.Marker({ color: '#06b6d4' })
      .setLngLat([lng, lat])
      .addTo(map.current);
  }, []);

  // Re-center to current parcel
  const handleReCenter = useCallback(() => {
    if (!map.current || coordinates.length === 0) return;
    const bounds = new mapboxgl.LngLatBounds();
    coordinates.forEach((pt) => bounds.extend(pt));
    map.current.fitBounds(bounds, { padding: 60, maxZoom: 17.5 });
  }, [coordinates]);

  // Handle saving geometry with version increment
  const handleSaveGeometry = async () => {
    if (coordinates.length < 3) {
      alert('Please digitize at least 3 vertices to form a closed polygon before saving.');
      return;
    }
    const nextVer = `PV-${String(parseInt(geometryVersion.split('-')[1] || '1') + 1).padStart(3, '0')}`;
    setGeometryVersion(nextVer);

    const siteMeta: SiteLocationMetadata = {
      address: 'Bandra East Transit Mixed-Use Development, CTS-1842',
      city: 'Mumbai',
      state: 'Maharashtra',
      coordinates: coordinates[0],
      provenance: 'CUSTOMER_DIGITIZED',
      geometryVersion: nextVer,
      timestamp: new Date().toISOString()
    };

    await onSaveSiteGeometry(siteMeta);
  };

  const handleToggleLayer = (key: keyof MapLayersVisibility) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="relative w-full h-[calc(100vh-56px)] bg-[#070b14] overflow-hidden select-none">
      {/* Mapbox Token Missing Notice (Section 24 - Error Handling) */}
      {!hasValidMapboxToken && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-30 px-3 py-1.5 rounded-full bg-slate-900/90 border border-amber-500/40 text-amber-300 text-xs shadow-xl flex items-center gap-2 backdrop-blur-md">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            <strong>Map Configuration:</strong> Add <code className="text-white font-mono font-bold">VITE_MAPBOX_ACCESS_TOKEN</code> in <code className="text-white font-mono">.env</code> to activate Mapbox Satellite & Search JS.
          </span>
        </div>
      )}

      {/* Map Container Element */}
      <div ref={mapContainer} className="w-full h-full" />

      {/* Top Left: Location Search Box (Section 5) */}
      <LocationSearch
        accessToken={rawToken}
        onSelectLocation={(site) => {
          if (onSelectSiteLocation) onSelectSiteLocation(site);
          handleFlyToLocation(site.coordinates[0], site.coordinates[1]);
        }}
        onFlyToLocation={handleFlyToLocation}
      />

      {/* Left CAD Toolbar (Section 7 & 8) */}
      <MapToolbar
        interactionMode={interactionMode}
        onChangeMode={(mode) => {
          setInteractionMode(mode);
          if (mode === 'MEASURE_DISTANCE') setMeasurement((m) => ({ ...m, mode: 'DISTANCE' }));
          if (mode === 'MEASURE_AREA') setMeasurement((m) => ({ ...m, mode: 'AREA' }));
        }}
        existingRoadWidth={existingRoadWidth}
        proposedRoadWidth={proposedRoadWidth}
        onChangeRoadWidths={onChangeRoadWidths}
        onClear={onClearCoordinates}
        onReCenter={handleReCenter}
        onToggleLayers={() => setIsLayersOpen(!isLayersOpen)}
        isLayersOpen={isLayersOpen}
        onSaveGeometry={handleSaveGeometry}
        isSavingGeometry={isSavingGeometry}
        parcelAreaSqm={areaSqm}
        parcelPerimeterM={perimeterM}
        verticesCount={coordinates.length}
        geometryVersion={geometryVersion}
      />

      {/* Floating Layer Control Panel (Section 12) */}
      {isLayersOpen && (
        <LayerControl
          layers={layers}
          onToggleLayer={handleToggleLayer}
          onClose={() => setIsLayersOpen(false)}
        />
      )}

      {/* Selected Map Feature Inspector (Section 13) */}
      <MapInspector
        selectedElement={selectedElement}
        onClose={() => setSelectedElement(null)}
        onOpenFeasibility={() => {
          if (onOpenFeasibility) onOpenFeasibility();
        }}
        onOpenDesign={() => {
          if (onOpenDesign) onOpenDesign();
        }}
      />

      {/* Measurement Tool Result Overlay (Section 16) */}
      <MeasurementOverlay
        measurement={measurement}
        onClearMeasurement={() =>
          setMeasurement({ points: [], totalDistanceM: 0, totalAreaSqm: 0, mode: null })
        }
        onSwitchMode={(mode) => setMeasurement((prev) => ({ ...prev, mode }))}
      />

      {/* Bottom Scale, North Indicator, and CAD Coordinates (Section 15) */}
      <NorthScaleIndicator
        cursorLat={cursorPos.lat}
        cursorLng={cursorPos.lng}
        zoom={zoomLevel}
        bearing={bearing}
        onResetNorth={() => {
          if (map.current) map.current.resetNorth();
        }}
      />

      {/* Live Drawing Mode Guide Banner */}
      {interactionMode === 'DRAW_PARCEL' && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 bg-blue-600/90 backdrop-blur-md px-4 py-1.5 rounded-full text-white text-xs font-medium shadow-lg animate-pulse flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5" />
          <span>Click on the map to place parcel boundary vertices. Place &ge;3 vertices to close the polygon.</span>
        </div>
      )}
    </div>
  );
};
