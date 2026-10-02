"""
Planwise Enterprise — Coordinate Systems & Reference Frame Schema
Delta Specification M1 — §3, §4

Defines:
- WGS84 Geodetic coordinates [latitude, longitude, elevation]
- ECEF (Earth-Centered, Earth-Fixed) 3D Cartesian coordinates [X, Y, Z]
- SECS (Site Engineering Coordinate System) Local ENU [East, North, Up]
- BCS (Building Coordinate System) local model metric frame
- SiteReferenceFrame metadata and immutability controls
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime


# Authoritative Named Engineering Tolerances (M1 §3, Precision Rules)
GEOMETRY_TOLERANCE_M = 0.001     # 1 mm tolerance for construction geometry
VERTEX_TOLERANCE_M = 0.005       # 5 mm vertex coincidence tolerance
SNAP_TOLERANCE_M = 0.050         # 50 mm snap tolerance
AREA_TOLERANCE_M2 = 0.010        # 0.01 m² area closure tolerance
ANGLE_TOLERANCE_DEG = 0.050      # 0.05 degree angular alignment tolerance


class GeodeticPoint(BaseModel):
    """WGS84 Geodetic coordinates (EPSG:4326)."""
    latitude: float = Field(..., description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., description="Longitude in decimal degrees (-180 to 180)")
    elevationM: float = Field(0.0, description="Height above WGS84 ellipsoid in meters")


class ECEFPoint(BaseModel):
    """Earth-Centered, Earth-Fixed (ECEF) 3D Cartesian coordinates (EPSG:4978)."""
    x: float = Field(..., description="X coordinate in meters (along prime meridian / equator)")
    y: float = Field(..., description="Y coordinate in meters (along 90° E meridian / equator)")
    z: float = Field(..., description="Z coordinate in meters (along Earth rotational axis)")


class ENUPoint(BaseModel):
    """Site Engineering Coordinate System (SECS) - Local Topocentric ENU."""
    east: float = Field(..., description="Easting relative to site origin in meters (+X East)")
    north: float = Field(..., description="Northing relative to site origin in meters (+Y North)")
    up: float = Field(0.0, description="Up / vertical elevation relative to origin in meters (+Z Up)")


class BCSPoint(BaseModel):
    """Building Coordinate System (BCS) - Local Building Model Metric Frame."""
    x: float = Field(..., description="Local building X axis in meters (along primary facade)")
    y: float = Field(..., description="Local building Y axis in meters (transverse to facade)")
    z: float = Field(0.0, description="Local building Z axis in meters (elevation above ground)")


class SiteReferenceFrame(BaseModel):
    """
    Topocentric Engineering Reference Frame (§3).
    Binds a local site coordinate system (SECS / ENU) to the global WGS84 ellipsoid.
    Immutable once referenced by a released site geometry or design version.
    """
    referenceFrameId: str = Field(..., description="Stable ID e.g. RF-MUM-CTS1842-01")
    siteId: str = Field(..., description="Associated Site / Parcel ID")
    version: int = Field(1, description="Sequential frame version")
    
    # Origin Geodetics (Topocentric Tangent Point)
    originLatitude: float = Field(..., description="Origin latitude in decimal degrees")
    originLongitude: float = Field(..., description="Origin longitude in decimal degrees")
    originElevationM: float = Field(0.0, description="Origin height above WGS84 ellipsoid in meters")
    
    # Orientation & Geodetic Datum
    trueNorthBearingDeg: float = Field(0.0, description="Angle from local ENU North to Grid True North in degrees")
    ellipsoid: str = Field("WGS84", description="Reference ellipsoid definition")
    datum: str = Field("WGS84 / EPSG:4326", description="Geodetic datum")
    coordinateSystem: str = Field("SECS_ENU_TOPOCENTRIC", description="Local metric coordinate system identifier")
    
    isLocked: bool = Field(False, description="Frozen when bound to released designs")
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def compute_frame_hash(self) -> str:
        """Deterministic fingerprint of the reference frame origin."""
        data = {
            "id": self.referenceFrameId,
            "siteId": self.siteId,
            "lat": round(self.originLatitude, 9),
            "lng": round(self.originLongitude, 9),
            "elev": round(self.originElevationM, 4),
            "bearing": round(self.trueNorthBearingDeg, 4),
            "ellipsoid": self.ellipsoid,
            "version": self.version
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
