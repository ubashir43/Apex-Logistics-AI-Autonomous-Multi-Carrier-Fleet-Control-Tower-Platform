"""
Logistics API — V6 Logistics
Endpoints for dynamic ML ETA prediction, regional delivery zones, freight quotes,
geocoding, and autonomous dispatcher dashboard analytics.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.delivery_zone import DeliveryZone
from app.models.shipment import Shipment
from app.middleware.jwt import get_current_user
from app.services.eta_predictor import get_eta_predictor
from app.services.geospatial import get_geo_service
from app.services.logistics_predictor import get_logistics_predictor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/logistics", tags=["Logistics Operations & ETA"])


# ═══════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════

class PredictETARequest(BaseModel):
    origin: Optional[str] = "New York"
    destination: Optional[str] = "Los Angeles"
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lng: Optional[float] = None
    carrier: Optional[str] = "fedex"
    service_type: Optional[str] = "standard"
    weight_kg: Optional[float] = 1.0


class CalculateRateRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    carrier: Optional[str] = "fedex"
    service_type: Optional[str] = "standard"
    weight_kg: Optional[float] = 1.0


class CreateZoneRequest(BaseModel):
    zone_name: str
    zone_code: str
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius_km: Optional[float] = 50.0
    base_delivery_hours: Optional[float] = 24.0
    delivery_success_rate: Optional[float] = 0.95
    base_price: Optional[float] = 15.0
    price_per_kg: Optional[float] = 2.5
    currency: Optional[str] = "USD"


# ═══════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════

@router.post("/predict-eta")
def predict_delivery_eta(
    data: PredictETARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict dynamic arrival time using GradientBoosting ML Regressor."""
    tenant_id = current_user.tenant_id or 1
    geo = get_geo_service()
    eta_pred = get_eta_predictor()

    orig_lat, orig_lng = data.origin_lat, data.origin_lng
    if orig_lat is None:
        orig_geo = geo.geocode_address(data.origin or "New York", 40.7128, -74.0060)
        orig_lat, orig_lng = orig_geo["lat"], orig_geo["lng"]

    dest_lat, dest_lng = data.dest_lat, data.dest_lng
    if dest_lat is None:
        dest_geo = geo.geocode_address(data.destination or "Los Angeles", 34.0522, -118.2437)
        dest_lat, dest_lng = dest_geo["lat"], dest_geo["lng"]

    return eta_pred.predict_eta(
        tenant_id=tenant_id,
        origin_lat=orig_lat,
        origin_lng=orig_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        carrier=data.carrier,
        service_type=data.service_type or "standard",
        weight_kg=data.weight_kg or 1.0,
        db=db
    )


@router.post("/quote")
@router.post("/calculate-rate")
def calculate_shipping_rate(
    data: CalculateRateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate freight quote and estimated transit hours between two locations."""
    tenant_id = current_user.tenant_id or 1
    from app.ai.logistics_tools import LogisticsToolRegistry
    tools = LogisticsToolRegistry(db=db, tenant_id=tenant_id)
    orig = data.origin or data.origin_city or "New York"
    dest = data.destination or data.destination_city or "Los Angeles"
    res = tools._calculate_rate(
        origin=orig,
        destination=dest,
        weight_kg=data.weight_kg or 1.0
    )
    res["total_quote_usd"] = res.get("total_price", 45.0)
    return res


@router.get("/zones")
def list_delivery_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List regional delivery zones for current tenant."""
    tenant_id = current_user.tenant_id or 1
    zones = db.query(DeliveryZone).filter(DeliveryZone.tenant_id == tenant_id).all()
    return {
        "count": len(zones),
        "zones": [z.to_dict() for z in zones]
    }


@router.post("/zones")
def create_delivery_zone(
    data: CreateZoneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a new regional delivery zone."""
    tenant_id = current_user.tenant_id or 1

    existing = db.query(DeliveryZone).filter(
        DeliveryZone.tenant_id == tenant_id,
        DeliveryZone.zone_code == data.zone_code.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Zone code '{data.zone_code}' already exists")

    zone = DeliveryZone(
        tenant_id=tenant_id,
        zone_name=data.zone_name,
        zone_code=data.zone_code.upper(),
        center_lat=data.center_lat,
        center_lng=data.center_lng,
        radius_km=data.radius_km or 50.0,
        base_delivery_hours=data.base_delivery_hours or 24.0,
        avg_delivery_hours=data.base_delivery_hours or 24.0,
        delivery_success_rate=data.delivery_success_rate or 0.95,
        base_price=data.base_price or 15.0,
        price_per_kg=data.price_per_kg or 2.5,
        currency=data.currency or "USD"
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone.to_dict()


@router.delete("/zones/{zone_id}")
def delete_delivery_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a delivery zone."""
    tenant_id = current_user.tenant_id or 1
    zone = db.query(DeliveryZone).filter(
        DeliveryZone.tenant_id == tenant_id,
        DeliveryZone.id == zone_id
    ).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Delivery zone not found")

    db.delete(zone)
    db.commit()
    return {"success": True, "deleted_zone_id": zone_id}


@router.post("/geocode")
def geocode_location(
    address: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
):
    """Geocode city or address using offline coordinate cache."""
    geo = get_geo_service()
    return geo.geocode_address(address)


@router.post("/train-model")
def retrain_eta_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger retraining of the tenant's GradientBoosting delivery time model."""
    tenant_id = current_user.tenant_id or 1
    eta_pred = get_eta_predictor()
    return eta_pred.train_model(tenant_id=tenant_id, db=db)


@router.get("/dashboard")
def get_logistics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive operations and AI metrics for dispatcher control tower."""
    tenant_id = current_user.tenant_id or 1

    total_shipments = db.query(Shipment).filter(Shipment.tenant_id == tenant_id).count()
    active_in_transit = db.query(Shipment).filter(
        Shipment.tenant_id == tenant_id,
        Shipment.status.in_(["picked_up", "in_transit", "out_for_delivery"])
    ).count()
    active_exceptions = db.query(Shipment).filter(
        Shipment.tenant_id == tenant_id,
        Shipment.has_exception == True,
        Shipment.exception_resolved == False
    ).count()
    delivered = db.query(Shipment).filter(
        Shipment.tenant_id == tenant_id,
        Shipment.status == "delivered"
    ).count()

    zones_count = db.query(DeliveryZone).filter(DeliveryZone.tenant_id == tenant_id).count()

    # Preemptive WISMO deflection rate (shipments notified proactively without user complaints)
    notified_count = db.query(Shipment).filter(
        Shipment.tenant_id == tenant_id,
        Shipment.customer_notified == True
    ).count()
    wismo_deflection_rate = round((notified_count / max(1, total_shipments)) * 100, 1)

    return {
        "status": "operational",
        "system_version": "6.0.0",
        "metrics": {
            "total_shipments": total_shipments,
            "active_in_transit": active_in_transit,
            "active_exceptions": active_exceptions,
            "delivered": delivered,
            "active_delivery_zones": zones_count,
            "proactive_notifications_sent": notified_count,
            "wismo_deflection_rate_pct": wismo_deflection_rate,
            "ml_eta_model_status": "active_gradient_boosting"
        }
    }
