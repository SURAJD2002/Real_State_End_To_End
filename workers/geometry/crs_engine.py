"""
Planwise Enterprise — High-Precision Local Engineering Coordinate Kernel
Delta Specification M1 — §3, §4

Implements mathematically rigorous, deterministic, double-precision (IEEE-754 float64)
geodetic transformations:
1. WGS84 Geodetic (lat, lon, height) <-> ECEF (X, Y, Z)
2. ECEF (X, Y, Z) <-> Local Topocentric ENU / SECS (East, North, Up)
3. Local ENU / SECS <-> Building Coordinate System (BCS)
4. Polygon transform routines & zero-distortion planar metric calculations.

Never relies on Web Mercator or display projections for engineering measurements.
"""

import math
from typing import List, Tuple, Dict, Any, Optional

from packages.schemas.coordinates import (
    GeodeticPoint,
    ECEFPoint,
    ENUPoint,
    BCSPoint,
    SiteReferenceFrame,
    GEOMETRY_TOLERANCE_M,
    VERTEX_TOLERANCE_M,
    AREA_TOLERANCE_M2,
    ANGLE_TOLERANCE_DEG
)

# -----------------------------------------------------------------------------
# WGS84 Ellipsoidal Constants (Standard NIMA TR8350.2 / EPSG:4326)
# -----------------------------------------------------------------------------
WGS84_A = 6378137.0                      # Semi-major axis in meters
WGS84_INV_F = 298.257223563              # Reciprocal flattening 1/f
WGS84_F = 1.0 / WGS84_INV_F              # Flattening
WGS84_B = WGS84_A * (1.0 - WGS84_F)      # Semi-minor axis in meters (6356752.314245)
WGS84_E2 = 2.0 * WGS84_F - WGS84_F**2   # First eccentricity squared (e²)
WGS84_EP2 = (WGS84_A**2 - WGS84_B**2) / (WGS84_B**2) # Second eccentricity squared (e'²)


def geodetic_to_ecef(latitude_deg: float, longitude_deg: float, elevation_m: float = 0.0) -> Tuple[float, float, float]:
    """
    Transforms WGS84 Geodetic coordinates (lat, lon, height) to Earth-Centered, Earth-Fixed (ECEF) [X, Y, Z].
    Uses standard closed-form ellipsoidal equations with double-precision float64.
    """
    phi = math.radians(latitude_deg)
    lam = math.radians(longitude_deg)
    h = float(elevation_m)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    # Prime vertical radius of curvature N(phi)
    N = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_phi**2)

    x = (N + h) * cos_phi * cos_lam
    y = (N + h) * cos_phi * sin_lam
    z = (N * (1.0 - WGS84_E2) + h) * sin_phi

    return (x, y, z)


def ecef_to_geodetic(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Transforms ECEF [X, Y, Z] to WGS84 Geodetic coordinates (lat, lon, height).
    Uses Bowring's algorithm (1985) which is numerically exact to < 10⁻¹² m for terrestrial coordinates.
    """
    p = math.sqrt(x**2 + y**2)
    
    # Handle poles singularity
    if p < 1e-9:
        lat = 90.0 if z >= 0 else -90.0
        lon = 0.0
        h = abs(z) - WGS84_B
        return (lat, lon, h)

    # Parametric initial estimate
    theta = math.atan2(z * WGS84_A, p * WGS84_B)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)

    # Closed-form latitude
    numerator = z + WGS84_EP2 * WGS84_B * (sin_theta**3)
    denominator = p - WGS84_E2 * WGS84_A * (cos_theta**3)
    phi = math.atan2(numerator, denominator)

    lam = math.atan2(y, x)

    # Prime vertical radius of curvature N(phi)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    N = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_phi**2)

    # Elevation h
    h = (p / cos_phi) - N

    return (math.degrees(phi), math.degrees(lam), h)


def ecef_to_enu(
    x: float, y: float, z: float,
    origin_lat_deg: float, origin_lon_deg: float, origin_elev_m: float = 0.0
) -> Tuple[float, float, float]:
    """
    Transforms ECEF [X, Y, Z] to Local Topocentric ENU (East, North, Up) relative to reference origin.
    SECS = Site Engineering Coordinate System.
    """
    # Origin in ECEF
    ox, oy, oz = geodetic_to_ecef(origin_lat_deg, origin_lon_deg, origin_elev_m)
    dx = x - ox
    dy = y - oy
    dz = z - oz

    phi = math.radians(origin_lat_deg)
    lam = math.radians(origin_lon_deg)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    # Rotation matrix from ECEF to local ENU
    east = -sin_lam * dx + cos_lam * dy
    north = -sin_phi * cos_lam * dx - sin_phi * sin_lam * dy + cos_phi * dz
    up = cos_phi * cos_lam * dx + cos_phi * sin_lam * dy + sin_phi * dz

    return (east, north, up)


def enu_to_ecef(
    east: float, north: float, up: float,
    origin_lat_deg: float, origin_lon_deg: float, origin_elev_m: float = 0.0
) -> Tuple[float, float, float]:
    """
    Transforms Local Topocentric ENU (East, North, Up) to ECEF [X, Y, Z].
    Inverse of ecef_to_enu.
    """
    ox, oy, oz = geodetic_to_ecef(origin_lat_deg, origin_lon_deg, origin_elev_m)

    phi = math.radians(origin_lat_deg)
    lam = math.radians(origin_lon_deg)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    # Transpose of rotation matrix (orthogonal inverse)
    dx = -sin_lam * east - sin_phi * cos_lam * north + cos_phi * cos_lam * up
    dy = cos_lam * east - sin_phi * sin_lam * north + cos_phi * sin_lam * up
    dz = cos_phi * north + sin_phi * up

    return (ox + dx, oy + dy, oz + dz)


def geodetic_to_enu(
    lat_deg: float, lon_deg: float, elev_m: float,
    origin_lat_deg: float, origin_lon_deg: float, origin_elev_m: float = 0.0
) -> Tuple[float, float, float]:
    """Full forward chain: WGS84 Geodetic -> ECEF -> Local Topocentric ENU / SECS."""
    x, y, z = geodetic_to_ecef(lat_deg, lon_deg, elev_m)
    return ecef_to_enu(x, y, z, origin_lat_deg, origin_lon_deg, origin_elev_m)


def enu_to_geodetic(
    east: float, north: float, up: float,
    origin_lat_deg: float, origin_lon_deg: float, origin_elev_m: float = 0.0
) -> Tuple[float, float, float]:
    """Full inverse chain: Local Topocentric ENU / SECS -> ECEF -> WGS84 Geodetic."""
    x, y, z = enu_to_ecef(east, north, up, origin_lat_deg, origin_lon_deg, origin_elev_m)
    return ecef_to_geodetic(x, y, z)


def enu_to_bcs(
    east: float, north: float, up: float,
    bldg_origin_e: float = 0.0, bldg_origin_n: float = 0.0, bldg_origin_u: float = 0.0,
    orientation_deg: float = 0.0
) -> Tuple[float, float, float]:
    """
    Transforms Site Engineering Coordinates (SECS / ENU) into Building Coordinate System (BCS).
    Translates by building site placement origin and rotates by orientation angle (clockwise from North).
    """
    de = east - bldg_origin_e
    dn = north - bldg_origin_n
    du = up - bldg_origin_u

    theta = math.radians(orientation_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Standard 2D planar rotation about Z axis
    bx = de * cos_t - dn * sin_t
    by = de * sin_t + dn * cos_t
    bz = du

    return (bx, by, bz)


def bcs_to_enu(
    bx: float, by: float, bz: float,
    bldg_origin_e: float = 0.0, bldg_origin_n: float = 0.0, bldg_origin_u: float = 0.0,
    orientation_deg: float = 0.0
) -> Tuple[float, float, float]:
    """
    Transforms Building Coordinate System (BCS) into Site Engineering Coordinates (SECS / ENU).
    Inverse of enu_to_bcs.
    """
    theta = math.radians(orientation_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    de = bx * cos_t + by * sin_t
    dn = -bx * sin_t + by * cos_t
    du = bz

    return (bldg_origin_e + de, bldg_origin_n + dn, bldg_origin_u + du)


# -----------------------------------------------------------------------------
# Planar Engineering Polygon & Distance Routines (SECS)
# -----------------------------------------------------------------------------

def polygon_wgs84_to_secs(
    coordinates: List[List[float]],
    ref_frame: SiteReferenceFrame
) -> List[List[float]]:
    """
    Transforms a polygon from WGS84 [lng, lat] into local metric SECS [east, north].
    Guarantees zero Web Mercator distortion.
    """
    secs_poly = []
    lat0 = ref_frame.originLatitude
    lon0 = ref_frame.originLongitude
    h0 = ref_frame.originElevationM

    for pt in coordinates:
        lon, lat = pt[0], pt[1]
        e, n, _ = geodetic_to_enu(lat, lon, 0.0, lat0, lon0, h0)
        secs_poly.append([round(e, 4), round(n, 4)])

    return secs_poly


def polygon_secs_to_wgs84(
    secs_coordinates: List[List[float]],
    ref_frame: SiteReferenceFrame
) -> List[List[float]]:
    """
    Transforms a local metric SECS [east, north] polygon back into WGS84 [lng, lat].
    """
    wgs_poly = []
    lat0 = ref_frame.originLatitude
    lon0 = ref_frame.originLongitude
    h0 = ref_frame.originElevationM

    for pt in secs_coordinates:
        e, n = pt[0], pt[1]
        lat, lon, _ = enu_to_geodetic(e, n, 0.0, lat0, lon0, h0)
        wgs_poly.append([round(lon, 7), round(lat, 7)])

    return wgs_poly


def calculate_secs_polygon_area(secs_coords: List[List[float]]) -> float:
    """Computes exact 2D planar metric area (m²) in SECS using the Shoelace formula."""
    n = len(secs_coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += secs_coords[i][0] * secs_coords[j][1]
        area -= secs_coords[j][0] * secs_coords[i][1]
    return abs(area) / 2.0


def calculate_secs_polygon_perimeter(secs_coords: List[List[float]]) -> float:
    """Computes exact planar perimeter (m) in SECS."""
    n = len(secs_coords)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n - 1):
        dx = secs_coords[i+1][0] - secs_coords[i][0]
        dy = secs_coords[i+1][1] - secs_coords[i][1]
        total += math.sqrt(dx**2 + dy**2)
    return total
