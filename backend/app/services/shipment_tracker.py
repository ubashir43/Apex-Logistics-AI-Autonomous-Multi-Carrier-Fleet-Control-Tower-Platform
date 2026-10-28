"""
Shipment Tracker Service — V6 Logistics
Real-time tracking engine, milestone event ingestion, exception detection,
and sentiment-aware customer notification intelligence.

PhD / Research Contribution:
Combines real-time shipment event processing with recipient sentiment signals
to decide WHEN, HOW, and with WHAT URGENCY to communicate transit updates.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.shipment import Shipment, ShipmentEvent
from app.services.delivery_exception import get_exception_classifier
from app.services.geospatial import get_geo_service

logger = logging.getLogger(__name__)


class ShipmentTracker:
    """
    Core shipment tracking and anomaly detection engine.
    """

    # Anomaly thresholds
    DELAY_THRESHOLD_HOURS = 24.0      # Flag as delay if 24 hours past ETA
    STALL_THRESHOLD_HOURS = 48.0      # Flag as stalled if in_transit with no scan in 48 hours
    MAX_ATTEMPTS_BEFORE_FLAG = 2      # Flag if 2 or more delivery attempts failed

    def process_tracking_update(
        self,
        shipment_id_or_code: str,
        event_type: str,
        location_name: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        description: Optional[str] = None,
        event_time: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Ingest a new tracking milestone event, update shipment state,
        and run real-time anomaly detection.
        """
        if db is None:
            raise ValueError("Database session required for tracking update")

        # Lookup by waybill code or primary key
        shipment = (
            db.query(Shipment)
            .filter(
                (Shipment.shipment_id == shipment_id_or_code)
                | (Shipment.carrier_tracking_id == shipment_id_or_code)
            )
            .first()
        )
        if not shipment:
            try:
                sid = int(shipment_id_or_code)
                shipment = db.query(Shipment).filter(Shipment.id == sid).first()
            except ValueError:
                pass

        if not shipment:
            return {
                "success": False,
                "error": f"Shipment '{shipment_id_or_code}' not found"
            }

        timestamp = event_time or datetime.utcnow()

        # Create tracking milestone
        event = ShipmentEvent(
            shipment_id=shipment.id,
            event_type=event_type,
            description=description or f"Status updated to {event_type}",
            location_name=location_name or shipment.current_location_name,
            location_lat=lat or shipment.current_lat,
            location_lng=lng or shipment.current_lng,
            event_time=timestamp
        )
        db.add(event)

        # Update shipment current coordinates and status
        if location_name:
            shipment.current_location_name = location_name
        if lat is not None:
            shipment.current_lat = lat
        if lng is not None:
            shipment.current_lng = lng

        # Transition lifecycle status according to event
        if event_type in ("delivered", "delivery_confirmed"):
            shipment.status = "delivered"
            shipment.actual_delivery = timestamp
            shipment.has_exception = False
        elif event_type in ("out_for_delivery",):
            shipment.status = "out_for_delivery"
        elif event_type in ("picked_up", "package_received"):
            shipment.status = "picked_up"
            shipment.pickup_date = shipment.pickup_date or timestamp
        elif event_type in ("in_transit", "departed_facility", "arrived_facility", "customs_cleared"):
            shipment.status = "in_transit"
        elif event_type in ("delivery_attempted", "failed_attempt"):
            shipment.delivery_attempts = (shipment.delivery_attempts or 0) + 1
        elif event_type in ("exception_reported", "damage_reported", "customs_hold"):
            shipment.status = "exception"
            shipment.has_exception = True
            shipment.exception_type = event_type
            shipment.exception_description = description

        # Run exception detection
        anomaly = self.detect_exceptions(shipment)
        if anomaly["has_exception"]:
            shipment.has_exception = True
            shipment.exception_type = anomaly["type"]
            shipment.exception_description = anomaly["description"]

        shipment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(shipment)

        return {
            "success": True,
            "shipment_id": shipment.shipment_id,
            "status": shipment.status,
            "current_location": shipment.current_location_name,
            "has_exception": shipment.has_exception,
            "exception_type": shipment.exception_type,
            "event_id": event.id,
        }

    def detect_exceptions(self, shipment: Shipment) -> Dict[str, Any]:
        """
        Evaluate shipment telemetry and transit timestamps to detect exceptions.
        Detects:
          - Overdue delivery (past estimated/predicted delivery)
          - Stalled in transit (no events in 48+ hours)
          - Excessive delivery attempts
        """
        now = datetime.utcnow()

        # If already delivered or returned, no active exception
        if shipment.status in ("delivered", "returned"):
            return {"has_exception": False, "type": None, "severity": "none", "description": ""}

        # 1. Check excessive delivery attempts
        if (shipment.delivery_attempts or 0) >= self.MAX_ATTEMPTS_BEFORE_FLAG:
            return {
                "has_exception": True,
                "type": "FAILED_ATTEMPT",
                "severity": "high" if shipment.delivery_attempts >= 3 else "medium",
                "description": f"Failed {shipment.delivery_attempts} delivery attempts"
            }

        # 2. Check overdue delivery
        target_eta = shipment.predicted_delivery or shipment.estimated_delivery
        if target_eta and now > (target_eta + timedelta(hours=self.DELAY_THRESHOLD_HOURS)):
            overdue_hours = round((now - target_eta).total_seconds() / 3600.0, 1)
            return {
                "has_exception": True,
                "type": "DELAY",
                "severity": "high" if overdue_hours > 72 else "medium",
                "description": f"Shipment is {overdue_hours} hours past scheduled delivery"
            }

        # 3. Check stalled in transit
        if shipment.status == "in_transit" and shipment.events:
            latest_event = shipment.events[0]
            if latest_event.event_time:
                hours_since_scan = (now - latest_event.event_time).total_seconds() / 3600.0
                if hours_since_scan > self.STALL_THRESHOLD_HOURS:
                    return {
                        "has_exception": True,
                        "type": "LOST" if hours_since_scan > 120 else "DELAY",
                        "severity": "critical" if hours_since_scan > 120 else "medium",
                        "description": f"No carrier tracking scan for {round(hours_since_scan, 1)} hours"
                    }

        if shipment.has_exception:
            return {
                "has_exception": True,
                "type": shipment.exception_type or "DELAY",
                "severity": "medium",
                "description": shipment.exception_description or "General logistics exception"
            }

        return {"has_exception": False, "type": None, "severity": "none", "description": ""}

    def should_notify_customer(
        self,
        shipment: Shipment,
        customer_sentiment: str = "neutral",
        notification_count: int = 0
    ) -> Dict[str, Any]:
        """
        Decide whether to trigger proactive customer notification.
        Uses sentiment to modulate urgency and thresholding:
          - Frustrated/Negative: Trigger immediately on any anomaly to deflect complaints.
          - Neutral/Positive: Trigger on major milestones (out for delivery, delivered, significant delay).
        """
        sentiment = (customer_sentiment or "neutral").lower()
        has_exception = shipment.has_exception

        # High sentiment risk
        if sentiment in ("frustrated", "negative"):
            if has_exception:
                return {
                    "should_notify": True,
                    "urgency": "high",
                    "channel": "priority_chat_or_sms",
                    "reason": "Proactive apology and resolution for frustrated customer",
                    "tone": "empathetic_urgent"
                }
            if shipment.status == "out_for_delivery":
                return {
                    "should_notify": True,
                    "urgency": "medium",
                    "channel": "chat",
                    "reason": "Reassurance that package is arriving today",
                    "tone": "reassuring"
                }

        # Normal milestone cadence
        if shipment.status == "delivered" and notification_count < 1:
            return {
                "should_notify": True,
                "urgency": "low",
                "channel": "chat",
                "reason": "Delivery confirmation",
                "tone": "celebratory"
            }

        if has_exception and notification_count < 2:
            return {
                "should_notify": True,
                "urgency": "medium",
                "channel": "email_or_chat",
                "reason": f"Operational notification of {shipment.exception_type}",
                "tone": "informative"
            }

        return {
            "should_notify": False,
            "urgency": "none",
            "channel": None,
            "reason": "No notification threshold met",
            "tone": "standard"
        }

    def get_shipment_summary(
        self,
        shipment: Shipment,
        customer_sentiment: str = "neutral",
        language: str = "en"
    ) -> str:
        """
        Generate a comprehensive, sentiment-adapted shipment summary.
        """
        if shipment.has_exception and shipment.exception_type:
            classifier = get_exception_classifier()
            return classifier.generate_response(
                exception_type=shipment.exception_type,
                customer_sentiment=customer_sentiment,
                shipment_data=shipment.to_dict(),
                language=language
            )

        return shipment.to_natural_language(language=language)


# Singleton
_shipment_tracker_instance: Optional[ShipmentTracker] = None

def get_shipment_tracker() -> ShipmentTracker:
    global _shipment_tracker_instance
    if _shipment_tracker_instance is None:
        _shipment_tracker_instance = ShipmentTracker()
    return _shipment_tracker_instance
