export type MapInteractionMode = 
  | 'SELECT' 
  | 'DRAW_PARCEL' 
  | 'EDIT_PARCEL' 
  | 'MEASURE_DISTANCE' 
  | 'MEASURE_AREA';

export interface MapLayersVisibility {
  parcel: boolean;
  roadContext: boolean;
  setbacks: boolean;
  buildableEnvelope: boolean;
  buildingFootprint: boolean;
  parking: boolean;
  measurements: boolean;
}

export interface SiteLocationMetadata {
  address: string;
  city: string;
  state: string;
  coordinates: [number, number]; // [lng, lat]
  mapboxFeatureId?: string;
  provenance: 'MAPBOX' | 'CUSTOMER_DIGITIZED' | 'SURVEY_DOCUMENT';
  geometryVersion: string;
  timestamp: string;
}

export interface MeasurementState {
  points: [number, number][];
  totalDistanceM: number;
  totalAreaSqm: number;
  mode: 'DISTANCE' | 'AREA' | null;
}

export type SelectedMapElement = 
  | { type: 'PARCEL'; areaSqm: number; perimeterM: number; verticesCount: number }
  | { type: 'BUILDABLE'; areaSqm: number; setbackFrontM: number; setbackRearM: number; setbackSideM: number }
  | { type: 'BUILDING_FOOTPRINT'; designVersionId: string; archetype: string; widthM: number; lengthM: number; buaSqm: number }
  | null;
