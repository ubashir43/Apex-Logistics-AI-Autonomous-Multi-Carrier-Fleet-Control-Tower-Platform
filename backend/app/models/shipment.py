"""
Shipment Model — Logistics Shipment Tracking & Milestone Event Log
V6 NEW — Logistics Transformation

Tracks the full lifecycle of a shipment/consignment from pickup to delivery.
Operates as a standalone waybill entity with an optional link to CustomerOrder.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
from app.database import Base


class Shipment(Base):
    """Individual shipment/waybill with full lifecycle tracking."""
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Optional Link to retail order (Standalone support for 3PL / Freight / Couriers)
    order_id = Column(Integer, ForeignKey("customer_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    shipment_id = Column(String(100), nullable=False, unique=True, index=True)  # Waybill ID: e.g. SHP-20261022-A1B2C

    # Carrier details
    carrier = Column(String(100), nullable=True, index=True)   # FedEx, DHL, UPS, TCS, Leopard, etc.
    carrier_tracking_id = Column(String(200), nullable=True, index=True)
    service_type = Column(String(100), default="standard")  # express, standard, freight, overnight

    # Status lifecycle
    status = Column(String(50), default="created", index=True)
    # created → picked_up → in_transit → out_for_delivery → delivered → exception → returned

    # Geospatial — Origin
    origin_address = Column(Text, nullable=True)
    origin_lat = Column(Float, nullable=True)
    origin_lng = Column(Float, nullable=True)
    origin_city = Column(String(100), nullable=True)
    origin_country = Column(String(10), default="US")  # ISO 3166-1 alpha-2

    # Geospatial — Destination
    destination_address = Column(Text, nullable=True)
    destination_lat = Column(Float, nullable=True)
    destination_lng = Column(Float, nullable=True)
    destination_city = Column(String(100), nullable=True)
    destination_country = Column(String(10), default="US")

    # Geospatial — Current Location (updated by GPS pings and tracking events)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    current_location_name = Column(String(200), nullable=True)

    # Weight & Physical specs
    weight_kg = Column(Float, default=1.0)
    volume_cbm = Column(Float, nullable=True)  # cubic meters
    package_count = Column(Integer, default=1)

    # Delivery Zone Link
    delivery_zone_id = Column(Integer, ForeignKey("delivery_zones.id", ondelete="SET NULL"), nullable=True)

    # Timing Milestones
    pickup_date = Column(DateTime, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    predicted_delivery = Column(DateTime, nullable=True)  # ML-predicted ETA

    # Exception tracking
    has_exception = Column(Boolean, default=False, index=True)
    exception_type = Column(String(100), nullable=True)  # delay, damage, lost, address_issue, customs_hold, weather
    exception_description = Column(Text, nullable=True)
    exception_resolved = Column(Boolean, default=False)

    # Customer communication & Sentiment awareness
    customer_notified = Column(Boolean, default=False)
    notification_count = Column(Integer, default=0)
    customer_sentiment = Column(String(50), nullable=True)  # positive, neutral, negative, frustrated

    # Delivery attempt counter
    delivery_attempts = Column(Integer, default=0)
    max_delivery_attempts = Column(Integer, default=3)

    # Metadata & audit
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="manual")  # manual, csv_sync, carrier_api, webhook

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = relationship(
        "ShipmentEvent",
        back_populates="shipment",
        cascade="all, delete-orphan",
        order_by="desc(ShipmentEvent.event_time)"
    )
    order = relationship("CustomerOrder", back_populates="shipments")
    delivery_zone = relationship("DeliveryZone")

    __table_args__ = (
        Index('ix_shipments_tenant_status', 'tenant_id', 'status'),
        Index('ix_shipments_tenant_carrier', 'tenant_id', 'carrier'),
        Index('ix_shipments_exception', 'tenant_id', 'has_exception'),
    )

    def calculate_transit_time_hours(self) -> float:
        """Calculate transit time in hours from pickup to now or actual delivery."""
        start = self.pickup_date or self.created_at
        end = self.actual_delivery or datetime.utcnow()
        if not start:
            return 0.0
        delta = end - start
        return round(delta.total_seconds() / 3600.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        """Convert shipment model to comprehensive dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "shipment_id": self.shipment_id,
            "order_id": self.order_id,
            "carrier": self.carrier,
            "carrier_tracking_id": self.carrier_tracking_id,
            "service_type": self.service_type,
            "status": self.status,
            "origin": {
                "address": self.origin_address,
                "city": self.origin_city,
                "country": self.origin_country,
                "lat": self.origin_lat,
                "lng": self.origin_lng,
            },
            "destination": {
                "address": self.destination_address,
                "city": self.destination_city,
                "country": self.destination_country,
                "lat": self.destination_lat,
                "lng": self.destination_lng,
            },
            "current_location": {
                "name": self.current_location_name,
                "lat": self.current_lat,
                "lng": self.current_lng,
            },
            "weight_kg": self.weight_kg,
            "volume_cbm": self.volume_cbm,
            "package_count": self.package_count,
            "pickup_date": self.pickup_date.isoformat() if self.pickup_date else None,
            "estimated_delivery": self.estimated_delivery.isoformat() if self.estimated_delivery else None,
            "predicted_delivery": self.predicted_delivery.isoformat() if self.predicted_delivery else None,
            "actual_delivery": self.actual_delivery.isoformat() if self.actual_delivery else None,
            "has_exception": self.has_exception,
            "exception_type": self.exception_type,
            "exception_description": self.exception_description,
            "exception_resolved": self.exception_resolved,
            "delivery_attempts": self.delivery_attempts,
            "max_delivery_attempts": self.max_delivery_attempts,
            "customer_sentiment": self.customer_sentiment,
            "customer_notified": self.customer_notified,
            "transit_time_hours": self.calculate_transit_time_hours(),
            "notes": self.notes,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "recent_events": [e.to_dict() for e in self.events[:5]] if self.events else [],
        }

    def to_natural_language(self, language: str = "en") -> str:
        """Generate a natural language description of shipment status."""
        loc = self.current_location_name or self.destination_city or "in transit"
        carrier_str = f" via {self.carrier}" if self.carrier else ""
        eta_target = self.predicted_delivery or self.estimated_delivery
        eta_str = f", estimated delivery by {eta_target.strftime('%b %d, %Y')}" if eta_target else ""

        if self.status == "delivered":
            actual_str = f" on {self.actual_delivery.strftime('%b %d, %Y')}" if self.actual_delivery else ""
            return f"Shipment {self.shipment_id}{carrier_str} has been successfully delivered{actual_str} to {self.destination_city or 'destination'}."
        elif self.has_exception:
            desc = f" ({self.exception_description})" if self.exception_description else ""
            return f"Shipment {self.shipment_id}{carrier_str} encountered an exception: {self.exception_type or 'issue'}{desc}. Our operations team is actively resolving this."
        elif self.status == "out_for_delivery":
            return f"Shipment {self.shipment_id}{carrier_str} is out for delivery today in {loc}."
        elif self.status == "in_transit":
            return f"Shipment {self.shipment_id}{carrier_str} is currently in transit near {loc}{eta_str}."
        elif self.status == "picked_up":
            return f"Shipment {self.shipment_id}{carrier_str} has been picked up from origin ({self.origin_city or 'warehouse'}){eta_str}."
        else:
            return f"Shipment {self.shipment_id} has been registered and is preparing for carrier pickup."


class ShipmentEvent(Base):
    """Individual tracking event/milestone for a shipment."""
    __tablename__ = "shipment_events"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)

    # Event milestone type
    event_type = Column(String(50), nullable=False, index=True)
    # picked_up, departed_facility, arrived_facility, customs_cleared,
    # out_for_delivery, delivery_attempted, delivered, exception_reported, returned

    description = Column(Text, nullable=True)
    location_name = Column(String(200), nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)

    event_time = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to shipment
    shipment = relationship("Shipment", back_populates="events")

    def to_dict(self) -> Dict[str, Any]:
        """Convert tracking event to dictionary."""
        return {
            "id": self.id,
            "shipment_id": self.shipment_id,
            "event_type": self.event_type,
            "description": self.description,
            "location_name": self.location_name,
            "location_lat": self.location_lat,
            "location_lng": self.location_lng,
            "event_time": self.event_time.isoformat() if self.event_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
