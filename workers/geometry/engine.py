"""
Geometry Worker Engine
Handles authoritative projected coordinate transformations (EPSG:4326 -> EPSG:32643 UTM 43N),
polygon validation, setback buffering, and net developable envelope computation.
"""

from typing import List, Tuple, Dict, Any
import math

try:
    from shapely.geometry import Polygon, LineString, MultiPolygon
    from shapely.ops import transform
    import pyproj
    HAS_SPATIAL_LIBS = True
except ImportError:
    HAS_SPATIAL_LIBS = False

# Mumbai Projected CRS: UTM Zone 43N (EPSG:32643)
SRID_WGS84 = 4326
SRID_UTM43N = 32643


def shoelace_area(coords: List[Tuple[float, float]]) -> float:
    """Fallback planar polygon area using Shoelace formula."""
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Compute distance in meters between two [lng, lat] coordinates."""
    lng1, lat1 = coord1
    lng2, lat2 = coord2
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def compute_parcel_metrics(
    coordinates: List[List[float]],
    existing_road_width_m: float = 12.0,
    proposed_road_width_m: float = 18.0
) -> Dict[str, Any]:
    """
    Computes precise metric area, road widening setback deductions,
    and returns projected & WGS84 geometry metrics.
    """
    if len(coordinates) > 0 and coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    if HAS_SPATIAL_LIBS:
        # Reproject from WGS84 to UTM Zone 43N
        wgs84 = pyproj.CRS("EPSG:4326")
        utm43n = pyproj.CRS("EPSG:32643")
        project_to_utm = pyproj.Transformer.from_crs(wgs84, utm43n, always_xy=True).transform
        project_to_wgs84 = pyproj.Transformer.from_crs(utm43n, wgs84, always_xy=True).transform

        poly_wgs84 = Polygon(coordinates)
        if not poly_wgs84.is_valid:
            poly_wgs84 = poly_wgs84.buffer(0)

        poly_utm = transform(project_to_utm, poly_wgs84)
        gross_area_sqm = float(poly_utm.area)
        perimeter_m = float(poly_utm.length)

        # Road widening deduction: (Proposed Width - Existing Width) / 2 along frontage
        road_widening_delta = max(0.0, (proposed_road_width_m - existing_road_width_m) / 2.0)
        # Approximate frontage length as ~20% of perimeter for 4-sided plots
        estimated_frontage_m = perimeter_m * 0.22
        road_deduction_sqm = float(round(estimated_frontage_m * road_widening_delta, 2))

        # Public Open Space / Amenity Reservation per DCPR 2034
        if gross_area_sqm >= 10000.0:
            amenity_pct = 0.15
        elif gross_area_sqm >= 4000.0:
            amenity_pct = 0.10
        elif gross_area_sqm >= 2000.0:
            amenity_pct = 0.05
        else:
            amenity_pct = 0.0

        amenity_reservation_sqm = float(round((gross_area_sqm - road_deduction_sqm) * amenity_pct, 2))
        net_developable_area_sqm = float(round(gross_area_sqm - road_deduction_sqm - amenity_reservation_sqm, 2))

        # Generate inward setback envelope (e.g. 4.5m - 6m setback)
        setback_dist = 4.5 if proposed_road_width_m <= 12.0 else 6.0
        buildable_utm = poly_utm.buffer(-setback_dist)
        if buildable_utm.is_empty:
            buildable_utm = poly_utm.buffer(-1.0)

        buildable_wgs84 = transform(project_to_wgs84, buildable_utm)
        if hasattr(buildable_wgs84, "exterior"):
            buildable_coords = [list(pt) for pt in buildable_wgs84.exterior.coords]
        else:
            buildable_coords = coordinates
    else:
        # High-precision spherical calculation fallback
        # Reference latitude ~ 19.1 deg N for Mumbai
        ref_lat = coordinates[0][1] if coordinates else 19.0760
        meters_per_deg_lat = 111132.95
        meters_per_deg_lng = 111412.84 * math.cos(math.radians(ref_lat))

        utm_coords = [
            (c[0] * meters_per_deg_lng, c[1] * meters_per_deg_lat)
            for c in coordinates
        ]
        gross_area_sqm = round(shoelace_area(utm_coords), 2)
        perimeter_m = sum(
            haversine_distance((coordinates[i][0], coordinates[i][1]), (coordinates[i+1][0], coordinates[i+1][1]))
            for i in range(len(coordinates) - 1)
        )
        road_widening_delta = max(0.0, (proposed_road_width_m - existing_road_width_m) / 2.0)
        estimated_frontage_m = perimeter_m * 0.22
        road_deduction_sqm = round(estimated_frontage_m * road_widening_delta, 2)

        amenity_pct = 0.15 if gross_area_sqm >= 10000.0 else (0.10 if gross_area_sqm >= 4000.0 else 0.05)
        amenity_reservation_sqm = round((gross_area_sqm - road_deduction_sqm) * amenity_pct, 2)
        net_developable_area_sqm = round(gross_area_sqm - road_deduction_sqm - amenity_reservation_sqm, 2)
        buildable_coords = coordinates

    return {
        "grossAreaSqm": gross_area_sqm,
        "perimeterM": round(perimeter_m, 2),
        "roadWideningDeductionSqm": road_deduction_sqm,
        "amenityReservationSqm": amenity_reservation_sqm,
        "netDevelopableAreaSqm": net_developable_area_sqm,
        "buildableCoordinates": buildable_coords
    }
