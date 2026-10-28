"""
Logistics Data Seeding Script — V6 Logistics
Generates 5 regional delivery zones, warehouse origins, and 50 realistic shipments
spanning multiple carriers (FedEx, DHL, UPS, TCS) with rich milestone event logs.

Includes:
- Completed deliveries for ML model training
- Active in-transit shipments
- Out-for-delivery shipments
- Real-world anomalies (customs holds, delays, damages, address issues, failed attempts)
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure UTF-8 output on Windows terminal
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


from app.database import Base, engine, SessionLocal
from app.models.tenant import Tenant
from app.models.delivery_zone import DeliveryZone
from app.models.shipment import Shipment, ShipmentEvent
from app.models.user import User

# City Hubs
CITIES = [
    {"name": "New York", "lat": 40.7128, "lng": -74.0060, "country": "US"},
    {"name": "Chicago", "lat": 41.8781, "lng": -87.6298, "country": "US"},
    {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "country": "US"},
    {"name": "Memphis", "lat": 35.1495, "lng": -90.0490, "country": "US"},
    {"name": "Dallas", "lat": 32.7767, "lng": -96.7970, "country": "US"},
    {"name": "Atlanta", "lat": 33.7490, "lng": -84.3880, "country": "US"},
    {"name": "Seattle", "lat": 47.6062, "lng": -122.3321, "country": "US"},
    {"name": "London", "lat": 51.5074, "lng": -0.1278, "country": "GB"},
    {"name": "Frankfurt", "lat": 50.1109, "lng": 8.6821, "country": "DE"},
    {"name": "Dubai", "lat": 25.2048, "lng": 55.2708, "country": "AE"},
]

CARRIERS = ["FedEx", "DHL", "UPS", "TCS"]
SERVICES = ["express", "standard", "freight", "overnight"]


def seed_logistics_dataset():
    db = SessionLocal()
    random.seed(42)

    try:
        print("🚚 Starting Logistics Data Seeding...")

        # 1. Ensure Tenant exists with logistics mode enabled
        tenant = db.query(Tenant).filter(Tenant.id == 1).first()
        if not tenant:
            user = db.query(User).filter(User.email == "admin@behavioral-ai.com").first()
            user_id = user.id if user else 1
            tenant = Tenant(
                id=1,
                name="Apex Global Logistics",
                industry="Logistics & Supply Chain",
                description="Autonomous Global 3PL & Courier Freight Network",
                logistics_mode=True,
                default_origin_address="100 Logistics Blvd, Memphis Global Hub, TN",
                default_origin_lat=35.1495,
                default_origin_lng=-90.0490,
                default_carrier="FedEx",
                sla_delivery_hours=48.0,
                widget_api_key="demo-logistics-api-key-100",
                owner_id=user_id
            )
            db.add(tenant)
            db.commit()
            print("  ✅ Created default logistics tenant: Apex Global Logistics")
        else:
            tenant.logistics_mode = True
            tenant.default_origin_lat = 35.1495
            tenant.default_origin_lng = -90.0490
            db.commit()
            print("  ✅ Updated Tenant #1 with logistics configuration")

        # 2. Seed Delivery Zones
        zone_definitions = [
            {"code": "ZA", "name": "Metro North East", "lat": 40.7128, "lng": -74.0060, "radius": 80.0, "hours": 24.0, "success": 0.97, "price": 15.0},
            {"code": "ZB", "name": "Midwest Freight Corridor", "lat": 41.8781, "lng": -87.6298, "radius": 120.0, "hours": 36.0, "success": 0.95, "price": 18.0},
            {"code": "ZC", "name": "West Coast Ports", "lat": 34.0522, "lng": -118.2437, "radius": 100.0, "hours": 24.0, "success": 0.96, "price": 16.5},
            {"code": "ZD", "name": "South Central SuperHub", "lat": 35.1495, "lng": -90.0490, "radius": 90.0, "hours": 24.0, "success": 0.98, "price": 14.0},
            {"code": "ZE", "name": "Transatlantic Gateway", "lat": 51.5074, "lng": -0.1278, "radius": 150.0, "hours": 72.0, "success": 0.92, "price": 45.0},
        ]

        created_zones = []
        for zd in zone_definitions:
            existing_zone = db.query(DeliveryZone).filter(
                DeliveryZone.tenant_id == tenant.id,
                DeliveryZone.zone_code == zd["code"]
            ).first()
            if not existing_zone:
                z = DeliveryZone(
                    tenant_id=tenant.id,
                    zone_name=zd["name"],
                    zone_code=zd["code"],
                    center_lat=zd["lat"],
                    center_lng=zd["lng"],
                    radius_km=zd["radius"],
                    base_delivery_hours=zd["hours"],
                    avg_delivery_hours=zd["hours"],
                    delivery_success_rate=zd["success"],
                    base_price=zd["price"],
                    price_per_kg=2.5,
                    currency="USD"
                )
                db.add(z)
                created_zones.append(z)
            else:
                created_zones.append(existing_zone)

        db.commit()
        print(f"  ✅ Seeded {len(created_zones)} Delivery Zones")

        # 3. Seed 50 Shipments
        now = datetime.utcnow()
        existing_count = db.query(Shipment).filter(Shipment.tenant_id == tenant.id).count()
        if existing_count >= 50:
            print(f"  ℹ️ Shipments already seeded ({existing_count} present).")
            return

        print("  📦 Seeding 50 diverse shipments across scenarios...")

        # Explicit test shipments for verification
        test_shipments_meta = [
            # 1. Normal in-transit
            {"id": "SHP-20261022-A1B2C", "status": "in_transit", "origin": 0, "dest": 1, "carrier": "FedEx", "service": "express", "exception": None},
            # 2. Delayed shipment
            {"id": "SHP-20261022-DELAY", "status": "in_transit", "origin": 0, "dest": 2, "carrier": "DHL", "service": "standard", "exception": "delay", "sentiment": "frustrated"},
            # 3. Customs hold
            {"id": "SHP-20261022-CUSTOMS", "status": "exception", "origin": 0, "dest": 7, "carrier": "DHL", "service": "express", "exception": "customs_hold", "sentiment": "negative"},
            # 4. Damaged parcel
            {"id": "SHP-20261022-DAMAGE", "status": "exception", "origin": 1, "dest": 4, "carrier": "UPS", "service": "standard", "exception": "damage", "sentiment": "frustrated"},
            # 5. Failed delivery attempt
            {"id": "SHP-20261022-ATTEMPT", "status": "in_transit", "origin": 3, "dest": 2, "carrier": "TCS", "service": "standard", "exception": "failed_attempt", "attempts": 2},
            # 6. Out for delivery
            {"id": "SHP-20261022-OUT", "status": "out_for_delivery", "origin": 3, "dest": 0, "carrier": "FedEx", "service": "overnight", "exception": None},
        ]

        # Generate 44 additional shipments
        scenarios = []
        # 20 Delivered (for training ML model)
        for i in range(20):
            scenarios.append({"status": "delivered", "exception": None})
        # 14 In Transit
        for i in range(14):
            scenarios.append({"status": "in_transit", "exception": None})
        # 4 Out for delivery
        for i in range(4):
            scenarios.append({"status": "out_for_delivery", "exception": None})
        # 3 Created
        for i in range(3):
            scenarios.append({"status": "created", "exception": None})
        # 3 Additional Exceptions
        scenarios.append({"status": "exception", "exception": "lost", "sentiment": "negative"})
        scenarios.append({"status": "exception", "exception": "address_issue", "sentiment": "neutral"})
        scenarios.append({"status": "in_transit", "exception": "delay", "sentiment": "frustrated"})

        all_specs = test_shipments_meta + [
            {
                "id": f"SHP-{now.strftime('%Y%m%d')}-{random.randint(10000, 99999)}",
                "status": sc["status"],
                "origin": random.randint(0, len(CITIES) - 1),
                "dest": random.randint(0, len(CITIES) - 1),
                "carrier": random.choice(CARRIERS),
                "service": random.choice(SERVICES),
                "exception": sc["exception"],
                "sentiment": sc.get("sentiment", "neutral"),
                "attempts": 2 if sc.get("exception") == "failed_attempt" else 0
            }
            for sc in scenarios
        ]

        shipments_added = 0
        for spec in all_specs:
            orig_city = CITIES[spec.get("origin", 0)]
            dest_city = CITIES[spec.get("dest", 1)]
            if orig_city["name"] == dest_city["name"]:
                dest_city = CITIES[(spec.get("dest", 1) + 1) % len(CITIES)]

            weight = round(random.uniform(0.5, 35.0), 1)
            pickup = now - timedelta(days=random.randint(2, 6), hours=random.randint(1, 12))
            pred_eta = pickup + timedelta(hours=random.randint(18, 54))

            has_exc = spec.get("exception") is not None
            actual_del = None
            if spec["status"] == "delivered":
                actual_del = pickup + timedelta(hours=random.randint(16, 48))

            shipment = Shipment(
                tenant_id=tenant.id,
                shipment_id=spec["id"],
                carrier=spec.get("carrier", "FedEx"),
                carrier_tracking_id=f"TRK{random.randint(100000000, 999999999)}",
                service_type=spec.get("service", "standard"),
                status=spec["status"],
                origin_city=orig_city["name"],
                origin_address=f"Depot {random.randint(1, 99)}, {orig_city['name']}",
                origin_lat=orig_city["lat"],
                origin_lng=orig_city["lng"],
                origin_country=orig_city["country"],
                destination_city=dest_city["name"],
                destination_address=f"{random.randint(100, 9999)} Commerce Way, {dest_city['name']}",
                destination_lat=dest_city["lat"],
                destination_lng=dest_city["lng"],
                destination_country=dest_city["country"],
                current_location_name=f"{dest_city['name']} Sorting Center" if spec["status"] in ("out_for_delivery", "delivered") else f"En route near {orig_city['name']}",
                current_lat=dest_city["lat"] if spec["status"] in ("out_for_delivery", "delivered") else orig_city["lat"] + 0.5,
                current_lng=dest_city["lng"] if spec["status"] in ("out_for_delivery", "delivered") else orig_city["lng"] + 0.5,
                weight_kg=weight,
                package_count=random.randint(1, 4),
                pickup_date=pickup,
                estimated_delivery=pred_eta + timedelta(hours=4),
                predicted_delivery=pred_eta,
                actual_delivery=actual_del,
                has_exception=has_exc,
                exception_type=spec.get("exception"),
                exception_description=f"Automated alert: {spec.get('exception')}" if has_exc else None,
                customer_sentiment=spec.get("sentiment", "neutral"),
                delivery_attempts=spec.get("attempts", 0),
                source="seed"
            )
            db.add(shipment)
            db.flush()

            # Add timeline events
            e1 = ShipmentEvent(
                shipment_id=shipment.id,
                event_type="picked_up",
                description=f"Package collected by {shipment.carrier} courier",
                location_name=orig_city["name"],
                location_lat=orig_city["lat"],
                location_lng=orig_city["lng"],
                event_time=pickup
            )
            db.add(e1)

            if spec["status"] in ("in_transit", "out_for_delivery", "delivered", "exception"):
                e2 = ShipmentEvent(
                    shipment_id=shipment.id,
                    event_type="in_transit",
                    description=f"Processed at facility in {orig_city['name']}",
                    location_name=orig_city["name"],
                    location_lat=orig_city["lat"],
                    location_lng=orig_city["lng"],
                    event_time=pickup + timedelta(hours=6)
                )
                db.add(e2)

            if spec["status"] in ("out_for_delivery", "delivered"):
                e3 = ShipmentEvent(
                    shipment_id=shipment.id,
                    event_type="out_for_delivery",
                    description="Package is out for delivery with local courier",
                    location_name=dest_city["name"],
                    location_lat=dest_city["lat"],
                    location_lng=dest_city["lng"],
                    event_time=now - timedelta(hours=3)
                )
                db.add(e3)

            if spec["status"] == "delivered":
                e4 = ShipmentEvent(
                    shipment_id=shipment.id,
                    event_type="delivered",
                    description="Package delivered to front door / reception. Signed by recipient.",
                    location_name=dest_city["name"],
                    location_lat=dest_city["lat"],
                    location_lng=dest_city["lng"],
                    event_time=actual_del or now
                )
                db.add(e4)

            if has_exc:
                e_exc = ShipmentEvent(
                    shipment_id=shipment.id,
                    event_type="exception_reported",
                    description=f"Delivery anomaly detected: {spec.get('exception')}",
                    location_name=dest_city["name"],
                    location_lat=dest_city["lat"],
                    location_lng=dest_city["lng"],
                    event_time=now - timedelta(hours=2)
                )
                db.add(e_exc)

            shipments_added += 1

        db.commit()
        print(f"  ✅ Successfully seeded {shipments_added} shipments with complete milestone timelines!")

    except Exception as e:
        db.rollback()
        print(f"  ❌ Seeding error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_logistics_dataset()
