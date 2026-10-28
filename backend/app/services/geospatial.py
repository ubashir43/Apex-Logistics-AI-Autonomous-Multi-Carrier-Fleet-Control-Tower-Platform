"""
Geospatial Service — V6 Logistics
Provides great-circle Haversine distance, delivery zone matching,
offline city coordinates dictionary, and cached geocoding.
"""

import math
import logging
from typing import Optional, Dict, Tuple, Any
from sqlalchemy.orm import Session

from app.models.delivery_zone import DeliveryZone

logger = logging.getLogger(__name__)

# Pre-cached coordinates for major commercial logistics hubs & cities
KNOWN_CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    # US Hubs
    "new york": (40.7128, -74.0060),
    "chicago": (41.8781, -87.6298),
    "los angeles": (34.0522, -118.2437),
    "memphis": (35.1495, -90.0490),  # Major FedEx Global Hub
    "louisville": (38.2527, -85.7585),  # Major UPS Worldport
    "dallas": (32.7767, -96.7970),
    "atlanta": (33.7490, -84.3880),
    "seattle": (47.6062, -122.3321),
    # European Hubs
    "london": (51.5074, -0.1278),
    "frankfurt": (50.1109, 8.6821),
    "amsterdam": (52.3676, 4.9041),
    "paris": (48.8566, 2.3522),
    # Asian / Middle East / Pakistan Hubs
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "tokyo": (35.6762, 139.6503),
    "karachi": (24.8607, 67.0011),
    "lahore": (31.5204, 74.3587),
    "islamabad": (33.6844, 73.0479),
    "rahim yar khan": (28.4212, 70.2989),
}


class GeoService:
    """Geospatial calculations and delivery zone operations."""

    def __init__(self):
        self._geocode_cache: Dict[str, Tuple[float, float]] = {}

    def haversine_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """
        Calculate great-circle distance in kilometers between two points.
        Uses the spherical law of haversines.
        """
        if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
            return 0.0

        R = 6371.0  # Earth mean radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlng / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 2)

    def find_delivery_zone(
        self,
        lat: float,
        lng: float,
        tenant_id: int,
        db: Session
    ) -> Optional[DeliveryZone]:
        """
        Find the matching delivery zone for given coordinates.
        Matches by radial coverage (center_lat, center_lng, radius_km).
        If multiple match, picks the closest zone.
        """
        if lat is None or lng is None:
            return None

        zones = db.query(DeliveryZone).filter(
            DeliveryZone.tenant_id == tenant_id,
            DeliveryZone.is_serviceable == True
        ).all()

        best_zone = None
        min_dist = float("inf")

        for zone in zones:
            if zone.center_lat is not None and zone.center_lng is not None:
                dist = self.haversine_distance(lat, lng, zone.center_lat, zone.center_lng)
                radius = zone.radius_km or 50.0  # default 50km if unspecified
                if dist <= radius and dist < min_dist:
                    min_dist = dist
                    best_zone = zone

        return best_zone

    def get_known_city_coordinates(self, city_or_address: str) -> Optional[Tuple[float, float]]:
        """Look up coordinates from pre-cached major logistics cities."""
        if not city_or_address:
            return None
        normalized = city_or_address.lower().strip()
        for city, coords in KNOWN_CITY_COORDINATES.items():
            if city in normalized:
                return coords
        return None

    def geocode_address(
        self,
        address: str,
        fallback_lat: Optional[float] = None,
        fallback_lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Geocode an address to lat/lng.
        Uses:
          1. In-memory cache
          2. Known logistics city centroids
          3. Provided fallbacks
        """
        if not address:
            return {"lat": fallback_lat, "lng": fallback_lng, "confidence": 0.0, "source": "empty"}

        normalized = address.lower().strip()

        # Check memory cache
        if normalized in self._geocode_cache:
            lat, lng = self._geocode_cache[normalized]
            return {"lat": lat, "lng": lng, "confidence": 0.95, "source": "cache"}

        # Check known cities
        coords = self.get_known_city_coordinates(normalized)
        if coords:
            self._geocode_cache[normalized] = coords
            return {"lat": coords[0], "lng": coords[1], "confidence": 0.90, "source": "city_centroid"}

        # Fallback
        if fallback_lat is not None and fallback_lng is not None:
            return {"lat": fallback_lat, "lng": fallback_lng, "confidence": 0.50, "source": "fallback"}

        return {"lat": 0.0, "lng": 0.0, "confidence": 0.0, "source": "unresolved"}

    def estimate_transit_distance(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> Dict[str, Any]:
        """
        Estimate road transit distance and drive duration between two points.
        Applies a road winding circuity factor of 1.30 and avg freight speed of 65 km/h.
        """
        crow_fly_km = self.haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        road_km = round(crow_fly_km * 1.30, 2)
        drive_hours = round(road_km / 65.0, 1) if road_km > 0 else 0.0

        return {
            "crow_fly_km": crow_fly_km,
            "estimated_road_km": road_km,
            "estimated_drive_hours": drive_hours,
        }


# Singleton instance
_geo_service_instance: Optional[GeoService] = None

def get_geo_service() -> GeoService:
    global _geo_service_instance
    if _geo_service_instance is None:
        _geo_service_instance = GeoService()
    return _geo_service_instance
