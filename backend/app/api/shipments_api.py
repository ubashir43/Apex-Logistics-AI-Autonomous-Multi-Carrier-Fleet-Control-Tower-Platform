"""
Shipments API — V6 Logistics
Complete CRUD, event ingestion, exception detection, and operational analytics
for shipments, consignments, and waybills.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.shipment import Shipment, ShipmentEvent
from app.middleware.jwt import get_current_user
from app.services.shipment_tracker import get_shipment_tracker
from app.services.eta_predictor import get_eta_predictor
from app.services.geospatial import get_geo_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/shipments", tags=["Logistics Shipments"])


# ═══════════════════════════════════════════════════════════════
# Pydantic Schemas
# ═══════════════════════════════════════════════════════════════

class CreateShipmentRequest(BaseModel):
    shipment_id: Optional[str] = Field(None, description="Custom waybill number, e.g. SHP-20261022-A1B2")
    order_id: Optional[int] = Field(None, description="Optional link to customer order")
    carrier: Optional[str] = Field("FedEx", description="Carrier name (FedEx, DHL, UPS, TCS, etc.)")
    carrier_tracking_id: Optional[str] = None
    service_type: Optional[str] = Field("standard", description="express, standard, freight, overnight")
    origin_city: Optional[str] = "New York"
    origin_address: Optional[str] = None
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    destination_city: Optional[str] = "Los Angeles"
    destination_address: Optional[str] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None
    weight_kg: Optional[float] = 1.0
    package_count: Optional[int] = 1
    notes: Optional[str] = None


class AddEventRequest(BaseModel):
    event_type: str = Field(..., description="picked_up, in_transit, out_for_delivery, delivered, exception_reported")
    location_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    description: Optional[str] = None
    event_time: Optional[datetime] = None


class UpdateStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("")
def list_shipments(
    status: Optional[str] = None,
    carrier: Optional[str] = None,
    has_exception: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List and filter shipments scoped to current tenant."""
    tenant_id = current_user.tenant_id or 1
    query = db.query(Shipment).filter(Shipment.tenant_id == tenant_id)

    if status:
        query = query.filter(Shipment.status == status.lower())
    if carrier:
        query = query.filter(Shipment.carrier.ilike(f"%{carrier}%"))
    if has_exception is not None:
        query = query.filter(Shipment.has_exception == has_exception)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Shipment.shipment_id.ilike(search_filter))
            | (Shipment.carrier_tracking_id.ilike(search_filter))
            | (Shipment.destination_city.ilike(search_filter))
            | (Shipment.origin_city.ilike(search_filter))
        )

    total_count = query.count()
    shipments = query.order_by(desc(Shipment.created_at)).offset(offset).limit(limit).all()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "shipments": [s.to_dict() for s in shipments]
    }


@router.get("/exceptions")
def list_active_exceptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all shipments with active unresolved exceptions."""
    tenant_id = current_user.tenant_id or 1
    exceptions = (
        db.query(Shipment)
        .filter(
            Shipment.tenant_id == tenant_id,
            Shipment.has_exception == True,
            Shipment.exception_resolved == False
        )
        .order_by(desc(Shipment.updated_at))
        .all()
    )
    return {
        "count": len(exceptions),
        "exceptions": [s.to_dict() for s in exceptions]
    }


@router.get("/stats")
def get_shipment_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Operational KPI metrics for dispatcher dashboard."""
    tenant_id = current_user.tenant_id or 1
    total = db.query(Shipment).filter(Shipment.tenant_id == tenant_id).count()
    delivered = db.query(Shipment).filter(Shipment.tenant_id == tenant_id, Shipment.status == "delivered").count()
    in_transit = db.query(Shipment).filter(Shipment.tenant_id == tenant_id, Shipment.status.in_(["in_transit", "picked_up", "out_for_delivery"])).count()
    exceptions = db.query(Shipment).filter(Shipment.tenant_id == tenant_id, Shipment.has_exception == True).count()

    exception_rate = round((exceptions / total * 100), 1) if total > 0 else 0.0

    # Carrier distribution
    carrier_counts = (
        db.query(Shipment.carrier, func.count(Shipment.id))
        .filter(Shipment.tenant_id == tenant_id)
        .group_by(Shipment.carrier)
        .all()
    )

    return {
        "total_shipments": total,
        "delivered": delivered,
        "active_in_transit": in_transit,
        "active_exceptions": exceptions,
        "exception_rate_percent": exception_rate,
        "carriers": {carrier or "Unassigned": count for carrier, count in carrier_counts}
    }


@router.post("")
def create_shipment(
    data: CreateShipmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new shipment and calculate dynamic initial ETA."""
    tenant_id = current_user.tenant_id or 1
    geo = get_geo_service()
    eta_pred = get_eta_predictor()

    # Generate waybill code if absent
    shipment_code = data.shipment_id
    if not shipment_code:
        rand_code = uuid.uuid4().hex[:6].upper()
        shipment_code = f"SHP-{datetime.utcnow().strftime('%Y%m%d')}-{rand_code}"

    # Verify uniqueness
    existing = db.query(Shipment).filter(Shipment.shipment_id == shipment_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Shipment code '{shipment_code}' already exists")

    # Geocode coordinates if missing
    orig_lat, orig_lng = data.origin_lat, data.origin_lng
    if orig_lat is None:
        orig_geo = geo.geocode_address(data.origin_city or "New York", 40.7128, -74.0060)
        orig_lat, orig_lng = orig_geo["lat"], orig_geo["lng"]

    dest_lat, dest_lng = data.destination_lat, data.destination_lng
    if dest_lat is None:
        dest_geo = geo.geocode_address(data.destination_city or "Los Angeles", 34.0522, -118.2437)
        dest_lat, dest_lng = dest_geo["lat"], dest_geo["lng"]

    # Calculate initial predicted delivery
    eta_info = eta_pred.predict_eta(
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
    predicted_dt = datetime.fromisoformat(eta_info["predicted_date"])
    estimated_dt = predicted_dt + timedelta(hours=6)  # conservative carrier SLA estimate

    shipment = Shipment(
        tenant_id=tenant_id,
        order_id=data.order_id,
        shipment_id=shipment_code,
        carrier=data.carrier,
        carrier_tracking_id=data.carrier_tracking_id or shipment_code,
        service_type=data.service_type or "standard",
        status="created",
        origin_city=data.origin_city,
        origin_address=data.origin_address,
        origin_lat=orig_lat,
        origin_lng=orig_lng,
        destination_city=data.destination_city,
        destination_address=data.destination_address,
        destination_lat=dest_lat,
        destination_lng=dest_lng,
        current_location_name=data.origin_city or "Origin Sorting Facility",
        current_lat=orig_lat,
        current_lng=orig_lng,
        weight_kg=data.weight_kg or 1.0,
        package_count=data.package_count or 1,
        estimated_delivery=estimated_dt,
        predicted_delivery=predicted_dt,
        notes=data.notes,
        source="api"
    )
    db.add(shipment)
    db.flush()

    # Initial creation milestone
    init_event = ShipmentEvent(
        shipment_id=shipment.id,
        event_type="created",
        description=f"Shipment registered via {data.carrier} ({data.service_type})",
        location_name=data.origin_city,
        location_lat=orig_lat,
        location_lng=orig_lng,
        event_time=datetime.utcnow()
    )
    db.add(init_event)
    db.commit()
    db.refresh(shipment)

    logger.info(f"🚚 Shipment created: {shipment.shipment_id} (ETA: {eta_info['predicted_date_formatted']})")
    return shipment.to_dict()


@router.get("/{identifier}")
def get_shipment_details(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full shipment profile and milestone timeline."""
    tenant_id = current_user.tenant_id or 1
    shipment = (
        db.query(Shipment)
        .filter(
            Shipment.tenant_id == tenant_id,
            (
                (Shipment.shipment_id == identifier)
                | (Shipment.carrier_tracking_id == identifier)
            )
        )
        .first()
    )
    if not shipment:
        try:
            sid = int(identifier)
            shipment = db.query(Shipment).filter(Shipment.tenant_id == tenant_id, Shipment.id == sid).first()
        except ValueError:
            pass

    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment '{identifier}' not found")

    return shipment.to_dict()


@router.post("/{identifier}/events")
def add_tracking_event(
    identifier: str,
    data: AddEventRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest tracking milestone and update live telemetry."""
    tracker = get_shipment_tracker()
    result = tracker.process_tracking_update(
        shipment_id_or_code=identifier,
        event_type=data.event_type,
        location_name=data.location_name,
        lat=data.lat,
        lng=data.lng,
        description=data.description,
        event_time=data.event_time,
        db=db
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))

    return result


@router.get("/{identifier}/timeline")
def get_shipment_timeline(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete chronological milestone history."""
    shipment = get_shipment_details(identifier, current_user, db)
    events = (
        db.query(ShipmentEvent)
        .filter(ShipmentEvent.shipment_id == shipment["id"])
        .order_by(desc(ShipmentEvent.event_time))
        .all()
    )
    return {
        "shipment_id": shipment["shipment_id"],
        "count": len(events),
        "timeline": [e.to_dict() for e in events]
    }


@router.post("/{identifier}/notify")
def evaluate_customer_notification(
    identifier: str,
    customer_sentiment: str = Body("neutral", embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PhD Contribution: Evaluate if proactive update is required based on sentiment signals."""
    tenant_id = current_user.tenant_id or 1
    shipment = (
        db.query(Shipment)
        .filter(Shipment.tenant_id == tenant_id, Shipment.shipment_id == identifier)
        .first()
    )
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    tracker = get_shipment_tracker()
    decision = tracker.should_notify_customer(
        shipment=shipment,
        customer_sentiment=customer_sentiment,
        notification_count=shipment.notification_count or 0
    )
    summary_text = tracker.get_shipment_summary(shipment, customer_sentiment=customer_sentiment)

    if decision["should_notify"]:
        shipment.customer_notified = True
        shipment.notification_count = (shipment.notification_count or 0) + 1
        db.commit()

    return {
        "shipment_id": shipment.shipment_id,
        "recommendation": decision,
        "generated_message": summary_text
    }
