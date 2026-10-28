"""
Delivery Zone Model — Geographic zone definitions for ETA & pricing.
V6 NEW — Logistics Transformation

Allows tenants to partition delivery areas into distinct zones with
specific SLAs, pricing rates, and historical performance tracking.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index
from datetime import datetime
from app.database import Base


class DeliveryZone(Base):
    """Geographic delivery zone for a tenant."""
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    zone_name = Column(String(100), nullable=False)     # e.g., "Zone A - Metropolitan Center"
    zone_code = Column(String(20), nullable=False)       # e.g., "ZA", "ZB", "ZC"

    # Geographic bounds (radial coverage around depot or coordinates)
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)
    radius_km = Column(Float, nullable=True)  # radius-based coverage

    # Delivery performance & SLA parameters
    base_delivery_hours = Column(Float, default=24.0)     # base SLA ETA for this zone
    avg_delivery_hours = Column(Float, nullable=True)     # historical average delivery duration (updated by ML)
    delivery_success_rate = Column(Float, default=0.95)   # historical first-attempt success rate
    is_serviceable = Column(Boolean, default=True)

    # Zone Pricing
    base_price = Column(Float, default=0.0)
    price_per_kg = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_delivery_zones_tenant_code', 'tenant_id', 'zone_code'),
    )

    def to_dict(self) -> dict:
        """Convert zone entity to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "zone_name": self.zone_name,
            "zone_code": self.zone_code,
            "center_lat": self.center_lat,
            "center_lng": self.center_lng,
            "radius_km": self.radius_km,
            "base_delivery_hours": self.base_delivery_hours,
            "avg_delivery_hours": self.avg_delivery_hours or self.base_delivery_hours,
            "delivery_success_rate": self.delivery_success_rate,
            "is_serviceable": self.is_serviceable,
            "base_price": self.base_price,
            "price_per_kg": self.price_per_kg,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
