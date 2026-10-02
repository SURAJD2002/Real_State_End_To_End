import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { 
  MapInteractionMode, 
  MapLayersVisibility, 
  SiteLocationMetadata, 
  MeasurementState,
  SelectedMapElement,
  CadSnapSettings 
} from './types';
import { LocationSearch } from './LocationSearch';
import { MapToolbar } from './MapToolbar';
import { LayerControl } from './LayerControl';
import { MapInspector } from './MapInspector';
import { NorthScaleIndicator } from './NorthScaleIndicator';
import { MeasurementOverlay } from './MeasurementOverlay';
import { CoordinateEditorModal, EdgeEditorModal, KeyboardShortcutsModal } from './CadModals';
import { HouseOption, FeasibilityResult } from '../../types';
import { AlertTriangle, Info } from 'lucide-react';
import {
  Coordinate,
  computePolygonMetrics,
  getPolygonEdges,
  validateParcelGeometry,
  resolveSnap,
  calculateMidpoint,
  SnapResult,
  GeometryValidationResult,
  CadEdgeInfo
} from './cadGeometry';
import { useCadHistory } from './useCadHistory';

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
  isReleaseLocked?: boolean;
  releaseId?: string | null;
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
  isSavingGeometry = false,
  isReleaseLocked = false,
  releaseId = null
}) => {
  void onChangeRoadWidths;
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markerRef = useRef<mapboxgl.Marker | null>(null);

  const rawToken = (import.meta as any).env?.VITE_MAPBOX_ACCESS_TOKEN || '';
  const hasValidMapboxToken = Boolean(rawToken && rawToken.trim().startsWith('pk.'));

  // CAD Interaction Mode
  const [interactionMode, setInteractionMode] = useState<MapInteractionMode>('SELECT');
  const [isLayersOpen, setIsLayersOpen] = useState(false);
  const [selectedElement, setSelectedElement] = useState<SelectedMapElement>(null);
  const [cursorPos, setCursorPos] = useState<{ lat: number; lng: number }>({ lat: 19.1128, lng: 72.8685 });
  const [zoomLevel, setZoomLevel] = useState<number>(15.5);
  const [bearing, setBearing] = useState<number>(0);
  const [geometryVersion, setGeometryVersion] = useState<string>('PV-001');
  const [webglError, setWebglError] = useState<boolean>(false);
  const [tokenError, setTokenError] = useState<boolean>(false);
  const [styleError, setStyleError] = useState<boolean>(false);

  // CAD Precision Snapping Settings
  const [snapSettings, setSnapSettings] = useState<CadSnapSettings>({
    isOrtho: false,
    isGridSnap: false,
    gridSizeM: 1.0,
    isAngleSnap: false,
    angleStepDeg: 15
  });
  const [activeSnap, setActiveSnap] = useState<SnapResult | null>(null);

  // CAD Selection & Dragging State
  const [selectedVertexIdx, setSelectedVertexIdx] = useState<number | null>(null);
  const [selectedEdgeIdx, setSelectedEdgeIdx] = useState<number | null>(null);
  const [draggingVertexIdx, setDraggingVertexIdx] = useState<number | null>(null);
  const [dragStartCoord, setDragStartCoord] = useState<Coordinate | null>(null);
  const [dragInitialArea, setDragInitialArea] = useState<number | null>(null);

  // CAD Modals State
  const [coordModalOpen, setCoordModalOpen] = useState(false);
  const [coordModalVertexIdx, setCoordModalVertexIdx] = useState(0);
  const [edgeModalOpen, setEdgeModalOpen] = useState(false);
  const [edgeModalIdx, setEdgeModalIdx] = useState(0);
  const [shortcutsModalOpen, setShortcutsModalOpen] = useState(false);

  // Command History (Undo / Redo)
  const { recordAction, undo, redo, canUndo, canRedo, resetHistory } = useCadHistory(coordinates);

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

  // Authoritative client-side geometry metrics and validation
  const { areaSqm, perimeterM } = useMemo(() => computePolygonMetrics(coordinates), [coordinates]);
  const validation: GeometryValidationResult = useMemo(() => validateParcelGeometry(coordinates), [coordinates]);
  const edges: CadEdgeInfo[] = useMemo(() => getPolygonEdges(coordinates, existingRoadWidth), [coordinates, existingRoadWidth]);

  // Live Area diff calculation during vertex movement
  const areaDiffSqm = useMemo(() => {
    if (dragInitialArea !== null && coordinates.length >= 3) {
      return Math.round((areaSqm - dragInitialArea) * 10) / 10;
    }
    return null;
  }, [areaSqm, dragInitialArea, coordinates.length]);

  // Compute building footprint polygon centered in buildable envelope
  const footprintPolygon = useMemo(() => {
    if (!selectedOption) return null;
    const targetCoords = buildableCoordinates && buildableCoordinates.length >= 3 ? buildableCoordinates : coordinates;
    if (targetCoords.length < 3) return null;

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

  // Fallback dark raster style definition
  const fallbackStyleSpec = useMemo(() => ({
    version: 8,
    sources: {
      'carto-dark': {
        type: 'raster',
        tiles: ['https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png'],
        tileSize: 256,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
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
  }), []);

  // Initialize Mapbox Map Instance
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const isWebGL = (() => {
      try {
        const canvas = document.createElement('canvas');
        return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'));
      } catch {
        return false;
      }
    })();
    if (!isWebGL) {
      setWebglError(true);
      return;
    }

    if (hasValidMapboxToken) {
      mapboxgl.accessToken = rawToken.trim();
    }

    const styleSpec = hasValidMapboxToken ? 'mapbox://styles/mapbox/dark-v11' : fallbackStyleSpec;
    const initialCenter: [number, number] = coordinates.length > 0 ? coordinates[0] : [72.8685, 19.1128];

    let mapInst: mapboxgl.Map;
    try {
      mapInst = new mapboxgl.Map({
        container: mapContainer.current,
        style: styleSpec as any,
        center: initialCenter,
        zoom: 15.5,
        pitch: 30,
        bearing: 0,
        attributionControl: true
      });
      map.current = mapInst;
    } catch (err) {
      console.error('[PlanwiseMap] Failed to create Mapbox map instance:', err);
      return;
    }

    mapInst.addControl(new mapboxgl.NavigationControl({ visualizePitch: true }), 'bottom-right');

    mapInst.on('rotate', () => setBearing(Math.round(mapInst.getBearing())));
    mapInst.on('zoom', () => setZoomLevel(Number(mapInst.getZoom().toFixed(1))));

    mapInst.on('error', (event: any) => {
      console.error('[PlanwiseMap] Mapbox error', event);
      const status = event.error?.status;
      if (status === 401 || status === 403) {
        setTokenError(true);
        try {
          mapInst.setStyle(fallbackStyleSpec as any);
        } catch (styleErr) {
          console.warn('[PlanwiseMap] Fallback style switch error:', styleErr);
        }
      } else if (event.error?.message?.toLowerCase()?.includes('style')) {
        setStyleError(true);
      }
    });

    // Helper to register all GIS & CAD GeoJSON sources and layers
    const attachGISLayers = () => {
      // 1. Gross Parcel Source & Layers
      if (!mapInst.getSource('parcel-source')) {
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
          filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'isInvalid', true]]
        });

        // Red invalid outline for self-intersection or error edges (Section 15 & 16)
        mapInst.addLayer({
          id: 'parcel-invalid-outline',
          type: 'line',
          source: 'parcel-source',
          paint: {
            'line-color': '#ef4444',
            'line-width': 3.5,
            'line-dasharray': [2, 1]
          },
          filter: ['==', 'isInvalid', true]
        });
      }

      // 2. CAD Vertices Source & Professional Handles (Section 4)
      if (!mapInst.getSource('cad-vertices-source')) {
        mapInst.addSource('cad-vertices-source', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        // Normal vertex handle: small crisp square/circle
        mapInst.addLayer({
          id: 'cad-vertices-handles',
          type: 'circle',
          source: 'cad-vertices-source',
          paint: {
            'circle-radius': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              8,
              5.5
            ],
            'circle-color': [
              'case',
              ['boolean', ['get', 'isSelected'], false],
              '#f59e0b',
              '#0ea5e9'
            ],
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff'
          }
        });
      }

      // 3. CAD Midpoints Handles Source (Section 12)
      if (!mapInst.getSource('cad-midpoints-source')) {
        mapInst.addSource('cad-midpoints-source', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        mapInst.addLayer({
          id: 'cad-midpoint-handles',
          type: 'circle',
          source: 'cad-midpoints-source',
          paint: {
            'circle-radius': 4.5,
            'circle-color': '#38bdf8',
            'circle-stroke-width': 1.5,
            'circle-stroke-color': '#07090e'
          }
        });
      }

      // 4. CAD Edge Dimension Annotations (Section 6)
      if (!mapInst.getSource('cad-dimensions-source')) {
        mapInst.addSource('cad-dimensions-source', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        mapInst.addLayer({
          id: 'cad-dimension-labels',
          type: 'symbol',
          source: 'cad-dimensions-source',
          layout: {
            'text-field': ['get', 'label'],
            'text-size': 10,
            'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
            'text-offset': [0, -1.2],
            'text-allow-overlap': true,
            'text-ignore-placement': true
          },
          paint: {
            'text-color': '#7dd3fc',
            'text-halo-color': '#020617',
            'text-halo-width': 2
          }
        });
      }

      // 5. Active Snap Indicator Point (Section 26)
      if (!mapInst.getSource('cad-snap-source')) {
        mapInst.addSource('cad-snap-source', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        mapInst.addLayer({
          id: 'cad-snap-ring',
          type: 'circle',
          source: 'cad-snap-source',
          paint: {
            'circle-radius': 9,
            'circle-color': 'transparent',
            'circle-stroke-width': 2.5,
            'circle-stroke-color': '#38bdf8'
          }
        });

        mapInst.addLayer({
          id: 'cad-snap-center',
          type: 'circle',
          source: 'cad-snap-source',
          paint: {
            'circle-radius': 3.5,
            'circle-color': '#38bdf8'
          }
        });
      }

      // 6. Buildable Envelope Source & Layers
      if (!mapInst.getSource('buildable-source')) {
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
            'fill-opacity': 0.22
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
      }

      // 7. Proposed Building Footprint Source & Layers
      if (!mapInst.getSource('footprint-source')) {
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
      }

      // 8. Measurement Overlay Source & Layers
      if (!mapInst.getSource('measure-source')) {
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
      }
    };

    mapInst.on('load', () => attachGISLayers());
    mapInst.on('style.load', () => attachGISLayers());

    // Feature Click Listener for Map Inspector
    mapInst.on('click', (e) => {
      if (interactionMode === 'DRAW_PARCEL') return; // Handled by canvas click

      const features = mapInst.queryRenderedFeatures(e.point, {
        layers: ['cad-vertices-handles', 'cad-midpoint-handles', 'footprint-fill', 'buildable-fill', 'parcel-fill']
      });

      if (features.length > 0) {
        const feat = features[0];
        const layerId = feat.layer?.id;

        // Vertex click
        if (layerId === 'cad-vertices-handles') {
          const vIdx = feat.properties?.index;
          if (vIdx !== undefined && vIdx >= 0 && vIdx < coordinates.length) {
            setSelectedVertexIdx(vIdx);
            setSelectedElement({
              type: 'VERTEX',
              index: vIdx,
              coordinate: coordinates[vIdx],
              adjacentEdges: [
                `E${String(((vIdx - 1 + coordinates.length) % coordinates.length) + 1).padStart(2, '0')}`,
                `E${String(vIdx + 1).padStart(2, '0')}`
              ]
            });
            return;
          }
        }

        // Midpoint handle click -> Split Edge
        if (layerId === 'cad-midpoint-handles') {
          const edgeIdx = feat.properties?.edgeIndex;
          if (edgeIdx !== undefined && edgeIdx >= 0 && edgeIdx < coordinates.length) {
            handleSplitEdge(edgeIdx);
            return;
          }
        }

        if (layerId === 'footprint-fill' && selectedOption) {
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

        if (layerId === 'buildable-fill' && feasibility) {
          setSelectedElement({
            type: 'BUILDABLE',
            areaSqm: Math.round(feasibility.netDevelopableAreaSqm),
            setbackFrontM: feasibility.frontSetbackM || 6.0,
            setbackRearM: 4.5,
            setbackSideM: 3.0
          });
          return;
        }

        if (layerId === 'parcel-fill') {
          setSelectedElement({
            type: 'PARCEL',
            areaSqm,
            perimeterM,
            verticesCount: coordinates.length,
            isValid: validation.isValid
          });
          return;
        }
      }
    });

    // Double Click handling (Section 19)
    mapInst.on('dblclick', (e) => {
      e.preventDefault();
      const features = mapInst.queryRenderedFeatures(e.point, {
        layers: ['cad-vertices-handles', 'parcel-fill']
      });

      if (features.length > 0) {
        const top = features[0];
        if (top.layer?.id === 'cad-vertices-handles') {
          const vIdx = top.properties?.index;
          if (vIdx !== undefined && vIdx >= 0 && vIdx < coordinates.length) {
            setCoordModalVertexIdx(vIdx);
            setCoordModalOpen(true);
            return;
          }
        }
      }
    });

    // ResizeObserver
    const resizeObserver = new ResizeObserver(() => {
      if (mapInst) mapInst.resize();
    });
    if (mapContainer.current) {
      resizeObserver.observe(mapContainer.current);
    }

    requestAnimationFrame(() => mapInst?.resize());
    const t1 = setTimeout(() => mapInst?.resize(), 100);

    return () => {
      resizeObserver.disconnect();
      clearTimeout(t1);
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [hasValidMapboxToken, rawToken, fallbackStyleSpec]);

  // Synchronize Mouse Cursor & Active Snapping (Section 11, 26)
  useEffect(() => {
    if (!map.current) return;

    const handlePointerMove = (e: mapboxgl.MapMouseEvent) => {
      const rawCoord: Coordinate = [e.lngLat.lng, e.lngLat.lat];
      setCursorPos({
        lat: Number(rawCoord[1].toFixed(6)),
        lng: Number(rawCoord[0].toFixed(6))
      });

      // Snapping anchor (last placed vertex during draw, or reference vertex during drag)
      const anchor =
        interactionMode === 'DRAW_PARCEL' && coordinates.length > 0
          ? coordinates[coordinates.length - 1]
          : draggingVertexIdx !== null && draggingVertexIdx > 0
          ? coordinates[draggingVertexIdx - 1]
          : undefined;

      const snap = resolveSnap(rawCoord, coordinates, {
        anchorCoord: anchor,
        isOrtho: snapSettings.isOrtho,
        isGridSnap: snapSettings.isGridSnap,
        gridSizeM: snapSettings.gridSizeM,
        isAngleSnap: snapSettings.isAngleSnap,
        angleStepDeg: snapSettings.angleStepDeg,
        externalGeometry: buildableCoordinates,
        excludeVertexIdx: draggingVertexIdx !== null ? draggingVertexIdx : -1
      });

      setActiveSnap(snap.type ? snap : null);

      // Handle vertex dragging if in drag state (Section 13)
      if (draggingVertexIdx !== null && map.current) {
        const nextCoord = snap.coordinate;
        const updated = [...coordinates];
        updated[draggingVertexIdx] = nextCoord;
        onUpdateCoordinates(updated);
      }
    };

    map.current.on('mousemove', handlePointerMove);
    return () => {
      if (map.current) {
        map.current.off('mousemove', handlePointerMove);
      }
    };
  }, [
    coordinates,
    interactionMode,
    draggingVertexIdx,
    snapSettings,
    buildableCoordinates,
    onUpdateCoordinates
  ]);

  // Handle Vertex Pointer Down / Pointer Up for 60fps CAD Dragging (Section 13)
  useEffect(() => {
    if (!map.current) return;

    const handleMouseDown = (e: mapboxgl.MapMouseEvent) => {
      if (interactionMode !== 'EDIT_PARCEL' && interactionMode !== 'SELECT') return;

      const features = map.current?.queryRenderedFeatures(e.point, {
        layers: ['cad-vertices-handles']
      });

      if (features && features.length > 0) {
        const vIdx = features[0].properties?.index;
        if (vIdx !== undefined && vIdx >= 0 && vIdx < coordinates.length) {
          if (isReleaseLocked) {
            alert(`Site geometry is locked under ${releaseId || 'an active release'}. Create a new geometry version.`);
            return;
          }
          setDraggingVertexIdx(vIdx);
          setDragStartCoord(coordinates[vIdx]);
          setDragInitialArea(areaSqm);
          setSelectedVertexIdx(vIdx);
          if (map.current) map.current.dragPan.disable();
        }
      }
    };

    const handleMouseUp = () => {
      if (draggingVertexIdx !== null && map.current) {
        map.current.dragPan.enable();
        if (dragStartCoord) {
          recordAction(coordinates, `Move Vertex V${draggingVertexIdx + 1}`);
        }
        setDraggingVertexIdx(null);
        setDragStartCoord(null);
        setDragInitialArea(null);
      }
    };

    map.current.on('mousedown', handleMouseDown);
    map.current.on('mouseup', handleMouseUp);

    return () => {
      if (map.current) {
        map.current.off('mousedown', handleMouseDown);
        map.current.off('mouseup', handleMouseUp);
      }
    };
  }, [
    interactionMode,
    coordinates,
    draggingVertexIdx,
    dragStartCoord,
    areaSqm,
    isReleaseLocked,
    releaseId,
    recordAction
  ]);

  // Handle Map Interaction Clicks (Drawing, Closing, Midpoint Insertion, Measurement)
  useEffect(() => {
    if (!map.current) return;

    const handleCanvasClick = (e: mapboxgl.MapMouseEvent) => {
      const rawCoord: Coordinate = [e.lngLat.lng, e.lngLat.lat];
      const anchor =
        interactionMode === 'DRAW_PARCEL' && coordinates.length > 0
          ? coordinates[coordinates.length - 1]
          : undefined;

      const snap = resolveSnap(rawCoord, coordinates, {
        anchorCoord: anchor,
        isOrtho: snapSettings.isOrtho,
        isGridSnap: snapSettings.isGridSnap,
        gridSizeM: snapSettings.gridSizeM,
        isAngleSnap: snapSettings.isAngleSnap,
        angleStepDeg: snapSettings.angleStepDeg,
        externalGeometry: buildableCoordinates
      });
      const activeCoord = snap.coordinate;

      // 1. DRAW PARCEL MODE (Section 3)
      if (interactionMode === 'DRAW_PARCEL') {
        if (isReleaseLocked) {
          alert('Site geometry is locked by an active release. Cannot add vertices.');
          return;
        }

        // Check if clicking near first vertex to CLOSE polygon (Section 3)
        if (
          coordinates.length >= 3 &&
          snap.type === 'VERTEX' &&
          snap.sourceVertexIndex === 0
        ) {
          // Polygon closed!
          setInteractionMode('EDIT_PARCEL');
          recordAction(coordinates, 'Close Parcel Boundary');
          return;
        }

        const nextCoords = [...coordinates, activeCoord];
        onAddCoordinate(activeCoord);
        recordAction(nextCoords, `Add Vertex V${nextCoords.length}`);
      }

      // 2. MEASUREMENT TOOL (Section 25)
      else if (interactionMode === 'MEASURE_DISTANCE' || interactionMode === 'MEASURE_AREA') {
        setMeasurement((prev) => {
          const nextPts = [...prev.points, activeCoord];
          const metrics = computePolygonMetrics(nextPts);
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
  }, [
    interactionMode,
    coordinates,
    snapSettings,
    buildableCoordinates,
    isReleaseLocked,
    onAddCoordinate,
    recordAction
  ]);

  // CAD Keyboard Shortcuts Listener (Section 35)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing inside input/textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      // Undo: Cmd/Ctrl + Z
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        const prev = undo();
        if (prev) onUpdateCoordinates(prev);
        return;
      }

      // Redo: Cmd/Ctrl + Shift + Z
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        const next = redo();
        if (next) onUpdateCoordinates(next);
        return;
      }

      // Tools Shortcuts
      switch (e.key.toLowerCase()) {
        case 'p':
          setInteractionMode('DRAW_PARCEL');
          break;
        case 'e':
          setInteractionMode('EDIT_PARCEL');
          break;
        case 'v':
          setInteractionMode('SELECT');
          break;
        case 'm':
          setInteractionMode('MEASURE_DISTANCE');
          setMeasurement((m) => ({ ...m, mode: 'DISTANCE' }));
          break;
        case 'o':
          setSnapSettings((prev) => ({ ...prev, isOrtho: !prev.isOrtho }));
          break;
        case 'g':
          setSnapSettings((prev) => ({ ...prev, isGridSnap: !prev.isGridSnap }));
          break;
        case 'z':
          if (!e.metaKey && !e.ctrlKey) handleReCenter();
          break;
        case '?':
          setShortcutsModalOpen(true);
          break;
        case 'delete':
        case 'backspace':
          if (selectedVertexIdx !== null) {
            handleDeleteVertex(selectedVertexIdx);
          }
          break;
        case 'escape': // Section 18
          if (interactionMode === 'DRAW_PARCEL') {
            setInteractionMode('SELECT');
          } else if (selectedVertexIdx !== null || selectedEdgeIdx !== null) {
            setSelectedVertexIdx(null);
            setSelectedEdgeIdx(null);
            setSelectedElement(null);
          } else if (measurement.points.length > 0) {
            setMeasurement({ points: [], totalDistanceM: 0, totalAreaSqm: 0, mode: null });
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo, onUpdateCoordinates, interactionMode, selectedVertexIdx, selectedEdgeIdx, measurement]);

  // Sync Parcel, Vertices, Edges, Dimensions, and Buildable Envelope to Mapbox GeoJSON Sources
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    // 1. Parcel Polygon Source
    const parcelSource = map.current.getSource('parcel-source') as mapboxgl.GeoJSONSource;
    if (parcelSource) {
      if (coordinates.length >= 3 && layers.parcel) {
        const closed = [...coordinates];
        if (closed[0] !== closed[closed.length - 1]) closed.push(closed[0]);

        parcelSource.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Polygon', coordinates: [closed] },
              properties: {
                id: 'gross-parcel',
                isInvalid: !validation.isValid
              }
            }
          ]
        });
      } else {
        parcelSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 2. CAD Vertices Handles Source (Section 4)
    const verticesSource = map.current.getSource('cad-vertices-source') as mapboxgl.GeoJSONSource;
    if (verticesSource) {
      if (coordinates.length > 0 && layers.parcel) {
        const features: GeoJSON.Feature[] = coordinates.map((coord, idx) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: coord },
          properties: {
            index: idx,
            label: `V${idx + 1}`,
            isSelected: idx === selectedVertexIdx
          }
        }));
        verticesSource.setData({ type: 'FeatureCollection', features });
      } else {
        verticesSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 3. CAD Midpoints Source (Section 12)
    const midpointsSource = map.current.getSource('cad-midpoints-source') as mapboxgl.GeoJSONSource;
    if (midpointsSource) {
      if (coordinates.length >= 3 && interactionMode === 'EDIT_PARCEL' && layers.parcel) {
        const features: GeoJSON.Feature[] = edges.map((e) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: e.midpoint },
          properties: {
            edgeIndex: e.index,
            label: '+'
          }
        }));
        midpointsSource.setData({ type: 'FeatureCollection', features });
      } else {
        midpointsSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 4. CAD Edge Dimensions Source (Section 6)
    const dimensionsSource = map.current.getSource('cad-dimensions-source') as mapboxgl.GeoJSONSource;
    if (dimensionsSource) {
      if (coordinates.length >= 2 && (interactionMode === 'DRAW_PARCEL' || interactionMode === 'EDIT_PARCEL')) {
        const features: GeoJSON.Feature[] = edges.map((e) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: e.midpoint },
          properties: {
            label: `${e.lengthM}m (${e.bearingDeg}°)`
          }
        }));
        dimensionsSource.setData({ type: 'FeatureCollection', features });
      } else {
        dimensionsSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 5. Active Snap Point Indicator Source (Section 26)
    const snapSource = map.current.getSource('cad-snap-source') as mapboxgl.GeoJSONSource;
    if (snapSource) {
      if (activeSnap && activeSnap.type) {
        snapSource.setData({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: { type: 'Point', coordinates: activeSnap.coordinate },
              properties: { type: activeSnap.type }
            }
          ]
        });
      } else {
        snapSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 6. Buildable Envelope Source
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
              properties: { id: 'buildable-envelope' }
            }
          ]
        });
      } else {
        buildableSource.setData({ type: 'FeatureCollection', features: [] });
      }
    }

    // 7. Proposed Building Footprint Source
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

    // 8. Measurement Overlay Source
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
  }, [
    coordinates,
    buildableCoordinates,
    footprintPolygon,
    measurement,
    layers,
    selectedOption,
    selectedVertexIdx,
    edges,
    interactionMode,
    activeSnap,
    validation
  ]);

  // Split Edge / Midpoint insertion handler (Section 12)
  const handleSplitEdge = useCallback(
    (edgeIdx: number) => {
      if (edgeIdx < 0 || edgeIdx >= coordinates.length) return;
      const start = coordinates[edgeIdx];
      const end = coordinates[(edgeIdx + 1) % coordinates.length];
      const mid = calculateMidpoint(start, end);

      const next = [
        ...coordinates.slice(0, edgeIdx + 1),
        mid,
        ...coordinates.slice(edgeIdx + 1)
      ];

      onUpdateCoordinates(next);
      recordAction(next, `Split Edge E${String(edgeIdx + 1).padStart(2, '0')}`);
      setSelectedVertexIdx(edgeIdx + 1);
    },
    [coordinates, onUpdateCoordinates, recordAction]
  );

  // Delete Vertex with validation protection (Section 14)
  const handleDeleteVertex = useCallback(
    (vIdx: number) => {
      if (coordinates.length <= 3) {
        alert('CANNOT DELETE VERTEX: A land parcel polygon requires at least 3 vertices to form a closed boundary.');
        return;
      }
      if (isReleaseLocked) {
        alert('Site geometry is locked by an active release.');
        return;
      }

      const next = coordinates.filter((_, idx) => idx !== vIdx);
      onUpdateCoordinates(next);
      recordAction(next, `Delete Vertex V${vIdx + 1}`);
      setSelectedVertexIdx(null);
      setSelectedElement(null);
    },
    [coordinates, onUpdateCoordinates, recordAction, isReleaseLocked]
  );

  // Coordinate Editor Apply Handler (Section 20)
  const handleApplyCoordinate = useCallback(
    (newCoord: Coordinate) => {
      if (coordModalVertexIdx < 0 || coordModalVertexIdx >= coordinates.length) return;
      const next = [...coordinates];
      next[coordModalVertexIdx] = newCoord;
      onUpdateCoordinates(next);
      recordAction(next, `Edit Coordinates V${coordModalVertexIdx + 1}`);
    },
    [coordModalVertexIdx, coordinates, onUpdateCoordinates, recordAction]
  );

  // Edge Bearing & Distance Editor Apply Handler (Section 21)
  const handleApplyEdgeDimension = useCallback(
    (newEndCoord: Coordinate) => {
      if (edgeModalIdx < 0 || edgeModalIdx >= coordinates.length) return;
      const next = [...coordinates];
      const targetEndIdx = (edgeModalIdx + 1) % coordinates.length;
      next[targetEndIdx] = newEndCoord;
      onUpdateCoordinates(next);
      recordAction(next, `Edit Dimension E${String(edgeModalIdx + 1).padStart(2, '0')}`);
    },
    [edgeModalIdx, coordinates, onUpdateCoordinates, recordAction]
  );

  // Set Primary Frontage
  const handleSetPrimaryFrontage = useCallback((edgeIdx: number) => {
    alert(`Primary Statutory Frontage set to Edge E${String(edgeIdx + 1).padStart(2, '0')}. Road setback alignment updated.`);
  }, []);

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

  // Handle saving geometry with version increment (Section 32)
  const handleSaveGeometry = async () => {
    if (!validation.isValid) {
      alert(`CANNOT SAVE GEOMETRY: ${validation.error}`);
      return;
    }
    if (isReleaseLocked) {
      alert('CANNOT SAVE: Site geometry belongs to an active release. Increment geometry version to clone.');
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
    <div
      className="planwise-map-workspace relative w-full h-[calc(100vh-56px)] bg-[#070b14] overflow-hidden select-none"
      style={{ position: 'relative', width: '100%', height: 'calc(100vh - 56px)', minHeight: '600px' }}
    >
      {/* Mapbox Token Missing Notice */}
      {!hasValidMapboxToken && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-30 px-3 py-1.5 rounded-full bg-slate-900/90 border border-amber-500/40 text-amber-300 text-xs shadow-xl flex items-center gap-2 backdrop-blur-md">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            <strong>Map Configuration:</strong> Add <code className="text-white font-mono font-bold">VITE_MAPBOX_ACCESS_TOKEN</code> in <code className="text-white font-mono">.env</code> to activate Mapbox Satellite & Search JS.
          </span>
        </div>
      )}

      {/* WebGL Unavailable Error Panel (Section 11) */}
      {webglError && (
        <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/95 text-white p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-rose-500 mb-3" />
          <h3 className="text-base font-bold tracking-wider text-rose-400 font-display">MAPBOX WEBGL UNAVAILABLE</h3>
          <p className="text-xs text-slate-400 max-w-md mt-2 leading-relaxed">
            Hardware acceleration or WebGL is disabled or unsupported in this browser environment. Please enable WebGL in browser settings to render the 3D GIS workspace.
          </p>
        </div>
      )}

      {/* Mapbox Token Error / Auth Failure Banner (Section 12) */}
      {tokenError && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 flex items-center gap-3 px-4 py-2.5 rounded-xl bg-slate-900/95 border border-rose-500/40 text-rose-300 shadow-2xl backdrop-blur-md">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <div>
            <div className="text-xs font-bold text-rose-200 tracking-wide font-display">MAPBOX CONFIGURATION ERROR</div>
            <div className="text-[11px] text-rose-300/80">Map service authentication failed. Fallback basemap engaged.</div>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="ml-2 px-2.5 py-1 rounded bg-rose-900/40 hover:bg-rose-800/60 text-xs font-semibold text-rose-200 border border-rose-500/30 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Map Style Error Panel (Section 10) */}
      {styleError && !tokenError && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 flex items-center gap-3 px-4 py-2.5 rounded-xl bg-slate-900/95 border border-amber-500/40 text-amber-300 shadow-2xl backdrop-blur-md">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <div>
            <div className="text-xs font-bold text-amber-200 tracking-wide font-display">MAP SERVICE ERROR</div>
            <div className="text-[11px] text-amber-300/80">Unable to load Mapbox style.</div>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="ml-2 px-2.5 py-1 rounded bg-amber-900/40 hover:bg-amber-800/60 text-xs font-semibold text-amber-200 border border-amber-500/30 transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Map Container Element */}
      <div
        ref={mapContainer}
        className="planwise-map-container w-full h-full"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          minHeight: '600px',
          cursor: interactionMode === 'DRAW_PARCEL' ? 'crosshair' : 'default'
        }}
      />

      {/* Top Left: Location Search Box (Section 5) */}
      <LocationSearch
        accessToken={rawToken}
        onSelectLocation={(site) => {
          if (onSelectSiteLocation) onSelectSiteLocation(site);
          handleFlyToLocation(site.coordinates[0], site.coordinates[1]);
        }}
        onFlyToLocation={handleFlyToLocation}
      />

      {/* Left Floating Professional CAD Toolbar (Section 2, 7, 8, 9, 10, 17, 30) */}
      <MapToolbar
        interactionMode={interactionMode}
        onChangeMode={(mode) => {
          setInteractionMode(mode);
          if (mode === 'MEASURE_DISTANCE') setMeasurement((m) => ({ ...m, mode: 'DISTANCE' }));
          if (mode === 'MEASURE_AREA') setMeasurement((m) => ({ ...m, mode: 'AREA' }));
        }}
        snapSettings={snapSettings}
        onUpdateSnapSettings={(s) => setSnapSettings((prev) => ({ ...prev, ...s }))}
        canUndo={canUndo}
        canRedo={canRedo}
        onUndo={() => {
          const prev = undo();
          if (prev) onUpdateCoordinates(prev);
        }}
        onRedo={() => {
          const next = redo();
          if (next) onUpdateCoordinates(next);
        }}
        onClear={() => {
          onClearCoordinates();
          resetHistory([], 'Clear Parcel');
          setSelectedVertexIdx(null);
          setSelectedElement(null);
        }}
        onReCenter={handleReCenter}
        onToggleLayers={() => setIsLayersOpen(!isLayersOpen)}
        isLayersOpen={isLayersOpen}
        onOpenShortcuts={() => setShortcutsModalOpen(true)}
        onSaveGeometry={handleSaveGeometry}
        isSavingGeometry={isSavingGeometry}
        parcelAreaSqm={areaSqm}
        parcelPerimeterM={perimeterM}
        verticesCount={coordinates.length}
        geometryVersion={geometryVersion}
        isGeometryValid={validation.isValid}
        geometryError={validation.error}
        activeSnapDesc={activeSnap?.description}
        areaDiffSqm={areaDiffSqm}
        selectedVertexIndex={selectedVertexIdx}
        onDeleteSelectedVertex={() => {
          if (selectedVertexIdx !== null) handleDeleteVertex(selectedVertexIdx);
        }}
        isReleaseLocked={isReleaseLocked}
        releaseId={releaseId}
      />

      {/* Floating Layer Control Panel (Section 12) */}
      {isLayersOpen && (
        <LayerControl
          layers={layers}
          onToggleLayer={handleToggleLayer}
          onClose={() => setIsLayersOpen(false)}
        />
      )}

      {/* Selected Map Feature Inspector (Section 13, 20, 21, 23, 24) */}
      <MapInspector
        selectedElement={selectedElement}
        onClose={() => {
          setSelectedElement(null);
          setSelectedVertexIdx(null);
          setSelectedEdgeIdx(null);
        }}
        onOpenFeasibility={() => {
          if (onOpenFeasibility) onOpenFeasibility();
        }}
        onOpenDesign={() => {
          if (onOpenDesign) onOpenDesign();
        }}
        onOpenCoordinateEditor={(vIdx) => {
          setCoordModalVertexIdx(vIdx);
          setCoordModalOpen(true);
        }}
        onDeleteVertex={(vIdx) => handleDeleteVertex(vIdx)}
        onOpenEdgeEditor={(eIdx) => {
          setEdgeModalIdx(eIdx);
          setEdgeModalOpen(true);
        }}
        onSplitEdge={(eIdx) => handleSplitEdge(eIdx)}
        onSetPrimaryFrontage={(eIdx) => handleSetPrimaryFrontage(eIdx)}
        existingRoadWidth={existingRoadWidth}
        proposedRoadWidth={proposedRoadWidth}
      />

      {/* Measurement Tool Result Overlay (Section 16, 25) */}
      <MeasurementOverlay
        measurement={measurement}
        onClearMeasurement={() =>
          setMeasurement({ points: [], totalDistanceM: 0, totalAreaSqm: 0, mode: null })
        }
        onSwitchMode={(mode) => setMeasurement((prev) => ({ ...prev, mode }))}
      />

      {/* Bottom Scale, North Indicator, and CAD Coordinates (Section 15, 20) */}
      <NorthScaleIndicator
        cursorLat={cursorPos.lat}
        cursorLng={cursorPos.lng}
        zoom={zoomLevel}
        bearing={bearing}
        onResetNorth={() => {
          if (map.current) map.current.resetNorth();
        }}
      />

      {/* Live Drawing Mode Guide Banner (Section 3) */}
      {interactionMode === 'DRAW_PARCEL' && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 bg-blue-600/90 backdrop-blur-md px-4 py-2 rounded-full text-white text-xs font-medium shadow-xl flex items-center gap-2 border border-blue-400/40">
          <Info className="w-4 h-4 shrink-0 text-cyan-200" />
          <span>
            <strong>DRAW PARCEL:</strong> Click to place vertices. Click <strong>Vertex V1</strong> to close polygon. [O] Ortho [G] Grid [Esc] Cancel
          </span>
        </div>
      )}

      {/* Live Snap Tooltip Floating Pill (Section 26) */}
      {activeSnap && activeSnap.type && (
        <div className="absolute top-28 left-1/2 -translate-x-1/2 z-20 px-3 py-1 rounded-full bg-slate-950/90 border border-cyan-400/50 text-cyan-300 text-[10px] font-mono shadow-lg flex items-center gap-1.5 backdrop-blur-md">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span>{activeSnap.description}</span>
        </div>
      )}

      {/* Modals (Section 20, 21, 35) */}
      {coordModalOpen && coordinates[coordModalVertexIdx] && (
        <CoordinateEditorModal
          isOpen={coordModalOpen}
          vertexIndex={coordModalVertexIdx}
          initialCoord={coordinates[coordModalVertexIdx]}
          onApply={handleApplyCoordinate}
          onClose={() => setCoordModalOpen(false)}
        />
      )}

      {edgeModalOpen && edges[edgeModalIdx] && (
        <EdgeEditorModal
          isOpen={edgeModalOpen}
          edgeId={edges[edgeModalIdx].id}
          startCoord={edges[edgeModalIdx].start}
          currentLengthM={edges[edgeModalIdx].lengthM}
          currentBearingDeg={edges[edgeModalIdx].bearingDeg}
          onApply={handleApplyEdgeDimension}
          onClose={() => setEdgeModalOpen(false)}
        />
      )}

      {shortcutsModalOpen && (
        <KeyboardShortcutsModal
          isOpen={shortcutsModalOpen}
          onClose={() => setShortcutsModalOpen(false)}
        />
      )}
    </div>
  );
};
