"""
Logistics Tool Registry — V6 Logistics
Defines the callable tools available to the Logistics AI ReAct Agent.
Each tool provides structured schema definitions and handles execution against
the database, ML predictors, and geospatial services.

PhD / Research Contribution:
Tool-augmented agent architecture applied to autonomous logistics customer support
with emotion-gated parameter adaptation.
"""

import json
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.shipment import Shipment, ShipmentEvent
from app.models.order import CustomerOrder
from app.models.delivery_zone import DeliveryZone
from app.services.shipment_tracker import get_shipment_tracker
from app.services.eta_predictor import get_eta_predictor
from app.services.delivery_exception import get_exception_classifier
from app.services.geospatial import get_geo_service

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """A tool the ReAct agent can inspect and invoke."""
    name: str
    description: str
    parameters: Dict[str, str]  # param_name -> human readable description
    handler: Callable
    requires_db: bool = True


class LogisticsToolRegistry:
    """Registry of tools available to the logistics agent."""

    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.tracker = get_shipment_tracker()
        self.eta_pred = get_eta_predictor()
        self.exception_classifier = get_exception_classifier()
        self.geo = get_geo_service()
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Tool]:
        return {
            "track_shipment": Tool(
                name="track_shipment",
                description="Look up real-time status, coordinates, carrier, and milestone timeline of a shipment or order",
                parameters={"identifier": "Tracking number, waybill code (e.g. SHP-...), or order ID"},
                handler=self._track_shipment,
            ),
            "predict_eta": Tool(
                name="predict_eta",
                description="Predict machine-learning estimated arrival time (ETA) for a shipment",
                parameters={"identifier": "Shipment ID or tracking number"},
                handler=self._predict_eta,
            ),
            "check_delivery_exception": Tool(
                name="check_delivery_exception",
                description="Analyze shipment telemetry for delays, failed delivery attempts, damage, or customs holds",
                parameters={"identifier": "Shipment ID or tracking number"},
                handler=self._check_exception,
            ),
            "calculate_shipping_rate": Tool(
                name="calculate_shipping_rate",
                description="Calculate freight/shipping cost and estimated transit duration between two cities",
                parameters={
                    "origin": "Origin city name or address",
                    "destination": "Destination city name or address",
                    "weight_kg": "Total weight in kilograms (default 1.0)"
                },
                handler=self._calculate_rate,
            ),
            "get_zone_info": Tool(
                name="get_zone_info",
                description="Look up delivery zone parameters, serviceability, and SLA hours for coordinates or a city",
                parameters={"location": "City name or address"},
                handler=self._get_zone_info,
            ),
            "search_knowledge_base": Tool(
                name="search_knowledge_base",
                description="Search logistics policies, customs guidelines, return instructions, and terms of service",
                parameters={"query": "The policy or procedural question"},
                handler=self._search_kb,
            ),
        }

    def _track_shipment(self, identifier: str) -> Dict[str, Any]:
        """Tool implementation: track shipment by identifier."""
        clean_id = (identifier or "").strip().lstrip("#")
        if not clean_id:
            return {"found": False, "error": "No tracking identifier provided"}

        # 1. Search Shipment table
        shipment = (
            self.db.query(Shipment)
            .filter(
                Shipment.tenant_id == self.tenant_id,
                (
                    (Shipment.shipment_id.ilike(f"%{clean_id}%"))
                    | (Shipment.carrier_tracking_id.ilike(f"%{clean_id}%"))
                )
            )
            .first()
        )

        if shipment:
            return {
                "found": True,
                "type": "shipment",
                "shipment_id": shipment.shipment_id,
                "carrier": shipment.carrier,
                "status": shipment.status,
                "current_location": shipment.current_location_name,
                "origin": f"{shipment.origin_city or ''}, {shipment.origin_country or ''}".strip(", "),
                "destination": f"{shipment.destination_city or ''}, {shipment.destination_country or ''}".strip(", "),
                "has_exception": shipment.has_exception,
                "exception_type": shipment.exception_type,
                "delivery_attempts": shipment.delivery_attempts,
                "estimated_delivery": shipment.estimated_delivery.isoformat() if shipment.estimated_delivery else None,
                "predicted_delivery": shipment.predicted_delivery.isoformat() if shipment.predicted_delivery else None,
                "summary": shipment.to_natural_language()
            }

        # 2. Search CustomerOrder table
        order = (
            self.db.query(CustomerOrder)
            .filter(
                CustomerOrder.tenant_id == self.tenant_id,
                (
                    (CustomerOrder.order_id.ilike(f"%{clean_id}%"))
                    | (CustomerOrder.tracking_number.ilike(f"%{clean_id}%"))
                )
            )
            .first()
        )

        if order:
            return {
                "found": True,
                "type": "order",
                "order_id": order.order_id,
                "carrier": order.carrier,
                "tracking_number": order.tracking_number,
                "status": order.status,
                "shipping_address": order.shipping_address,
                "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                "has_exception": order.has_exception,
                "summary": order.to_natural_language()
            }

        return {
            "found": False,
            "error": f"No shipment or order record found matching identifier '{clean_id}'"
        }

    def _predict_eta(self, identifier: str) -> Dict[str, Any]:
        """Tool implementation: predict ML ETA."""
        track_info = self._track_shipment(identifier)
        if not track_info.get("found"):
            return {"success": False, "error": track_info.get("error")}

        # Lookup coordinates for origin/destination
        shipment = (
            self.db.query(Shipment)
            .filter(
                Shipment.tenant_id == self.tenant_id,
                Shipment.shipment_id == track_info.get("shipment_id")
            )
            .first()
        )

        orig_lat = shipment.origin_lat if shipment else None
        orig_lng = shipment.origin_lng if shipment else None
        dest_lat = shipment.destination_lat if shipment else None
        dest_lng = shipment.destination_lng if shipment else None

        # Fallback to geocoding if coords missing
        if orig_lat is None or dest_lat is None:
            orig_geo = self.geo.geocode_address(shipment.origin_city if shipment else "New York", 40.7128, -74.0060)
            dest_geo = self.geo.geocode_address(shipment.destination_city if shipment else "Los Angeles", 34.0522, -118.2437)
            orig_lat, orig_lng = orig_geo["lat"], orig_geo["lng"]
            dest_lat, dest_lng = dest_geo["lat"], dest_geo["lng"]

        pred = self.eta_pred.predict_eta(
            tenant_id=self.tenant_id,
            origin_lat=orig_lat,
            origin_lng=orig_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            carrier=shipment.carrier if shipment else "standard",
            service_type=shipment.service_type if shipment else "standard",
            weight_kg=shipment.weight_kg if shipment else 1.0,
            db=self.db
        )

        # Update predicted_delivery on the shipment record
        if shipment:
            try:
                from datetime import datetime
                shipment.predicted_delivery = datetime.fromisoformat(pred["predicted_date"])
                self.db.commit()
            except Exception:
                pass

        return {
            "success": True,
            "shipment_id": shipment.shipment_id if shipment else identifier,
            "predicted_hours": pred["predicted_hours"],
            "predicted_date_formatted": pred["predicted_date_formatted"],
            "confidence": pred["confidence"],
            "method": pred["method"],
            "factors": pred["factors"]
        }

    def _check_exception(self, identifier: str) -> Dict[str, Any]:
        """Tool implementation: detect and classify delivery anomalies."""
        track_info = self._track_shipment(identifier)
        if not track_info.get("found"):
            return {"success": False, "error": track_info.get("error")}

        shipment = (
            self.db.query(Shipment)
            .filter(
                Shipment.tenant_id == self.tenant_id,
                Shipment.shipment_id == track_info.get("shipment_id")
            )
            .first()
        )

        if not shipment:
            return {"success": False, "error": "Shipment model not found"}

        classification = self.exception_classifier.classify(shipment.to_dict())
        return {
            "success": True,
            "shipment_id": shipment.shipment_id,
            "is_exception": classification["is_exception"],
            "exception_type": classification["type"],
            "severity": classification["severity"],
            "resolution_steps": classification["resolution_steps"],
            "requires_escalation": classification["requires_escalation"]
        }

    def _calculate_rate(
        self,
        origin: str,
        destination: str,
        weight_kg: float = 1.0
    ) -> Dict[str, Any]:
        """Tool implementation: calculate freight rate and transit ETA."""
        orig_geo = self.geo.geocode_address(origin, 40.7128, -74.0060)
        dest_geo = self.geo.geocode_address(destination, 41.8781, -87.6298)

        distance_info = self.geo.estimate_transit_distance(
            orig_geo["lat"], orig_geo["lng"], dest_geo["lat"], dest_geo["lng"]
        )
        road_km = distance_info["estimated_road_km"]

        # Check delivery zone
        zone = self.geo.find_delivery_zone(dest_geo["lat"], dest_geo["lng"], self.tenant_id, self.db)
        base_rate = zone.base_price if zone else 15.0
        rate_per_kg = zone.price_per_kg if zone else 2.5
        currency = zone.currency if zone else "USD"

        # Distance-based freight calculation
        distance_charge = round((road_km / 100.0) * 1.5, 2)
        weight_charge = round(float(weight_kg) * rate_per_kg, 2)
        total_price = round(base_rate + distance_charge + weight_charge, 2)

        transit_hours = zone.base_delivery_hours if zone else max(24.0, round(road_km / 45.0, 1))

        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "distance_km": road_km,
            "weight_kg": weight_kg,
            "total_price": total_price,
            "currency": currency,
            "estimated_transit_hours": transit_hours,
            "zone_code": zone.zone_code if zone else "STANDARD",
            "price_breakdown": {
                "base_rate": base_rate,
                "distance_surcharge": distance_charge,
                "weight_charge": weight_charge
            }
        }

    def _get_zone_info(self, location: str) -> Dict[str, Any]:
        """Tool implementation: delivery zone query."""
        geo_info = self.geo.geocode_address(location)
        zone = self.geo.find_delivery_zone(geo_info["lat"], geo_info["lng"], self.tenant_id, self.db)

        if not zone:
            return {
                "found": False,
                "location": location,
                "message": "Location falls outside dedicated regional zones; standard domestic SLA applies (48-72h)."
            }

        return {
            "found": True,
            "zone_name": zone.zone_name,
            "zone_code": zone.zone_code,
            "is_serviceable": zone.is_serviceable,
            "base_delivery_hours": zone.base_delivery_hours,
            "avg_delivery_hours": zone.avg_delivery_hours,
            "success_rate": f"{zone.delivery_success_rate:.0%}",
            "currency": zone.currency
        }

    def _search_kb(self, query: str) -> Dict[str, Any]:
        """Tool implementation: search knowledge documents for policies."""
        try:
            from app.ai.retrieval import get_retrieval_service
            retrieval = get_retrieval_service()
            docs, _ = retrieval.retrieve_context(
                client_id=str(self.tenant_id),
                query=query,
                limit=3
            )
            return {
                "success": True,
                "results_count": len(docs),
                "snippets": docs[:3] if docs else ["No specific policy document found matching query."]
            }
        except Exception as e:
            return {"success": False, "error": str(e), "snippets": []}

    def get_tool_descriptions(self) -> str:
        """Format tool descriptions for LLM prompt context."""
        lines = []
        for name, tool in self.tools.items():
            params = ", ".join(f"{k}: {v}" for k, v in tool.parameters.items())
            lines.append(f"- {name}({params}): {tool.description}")
        return "\n".join(lines)
