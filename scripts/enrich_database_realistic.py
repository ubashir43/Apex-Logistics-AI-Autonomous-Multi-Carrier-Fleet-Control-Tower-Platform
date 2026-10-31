"""
Apex Logistics AI — Database Enrichment Script
Adds realistic multi-carrier shipments, milestones, orders, and customer conversations
for both Tenant 1 (Apex Global Logistics) and Tenant 2 (FedEx Global Logistics Hub).
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.shipment import Shipment, ShipmentEvent
from app.models.order import CustomerOrder
from app.models.conversation import Conversation
from app.models.message import Message

def seed():
    db = SessionLocal()
    print("Enriching database with realistic multi-carrier records...")

    tenants = db.query(Tenant).all()
    tenant_ids = [t.id for t in tenants]
    print(f"Found tenants: {[t.name for t in tenants]} (IDs: {tenant_ids})")

    now = datetime.utcnow()

    # Define realistic dataset
    shipment_templates = [
        {
            "shipment_id": "WB-FEDEX-8812A",
            "carrier": "FedEx",
            "carrier_tracking_id": "FX-992014812A",
            "service_type": "express",
            "status": "in_transit",
            "origin_city": "Memphis",
            "origin_country": "US",
            "origin_address": "FedEx SuperHub, 2903 Democrat Rd, Memphis, TN 38118",
            "origin_lat": 35.0424,
            "origin_lng": -89.9767,
            "destination_city": "Salt Lake City",
            "destination_country": "US",
            "destination_address": "Intermountain Life Sciences, 5121 S Cottonwood St, Salt Lake City, UT 84107",
            "destination_lat": 40.7608,
            "destination_lng": -111.8910,
            "current_location_name": "Denver Intermodal Sort Facility, CO",
            "current_lat": 39.7392,
            "current_lng": -104.9903,
            "weight_kg": 14.8,
            "package_count": 2,
            "pickup_date": now - timedelta(hours=26),
            "estimated_delivery": now + timedelta(hours=6),
            "predicted_delivery": now + timedelta(hours=5, minutes=15),
            "has_exception": False,
            "customer_sentiment": "neutral",
            "notes": "Priority Cold-Chain Pharmaceutical Consignment - active GPS & temperature telemetry",
            "order": {
                "order_id": "#ORD-FX-8812",
                "customer_name": "Dr. Sarah Jenkins",
                "customer_email": "s.jenkins@intermountainhealth.org",
                "total_amount": 1420.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=26), "picked_up", "Memphis SuperHub, TN", "Consignment picked up and scanned into FedEx World Hub automated matrix."),
                (now - timedelta(hours=18), "in_transit", "FedEx Air Cargo Flight FX-412", "Departed Memphis World Hub en route to Denver distribution gateway."),
                (now - timedelta(hours=7), "in_transit", "Denver Intermodal Sort Facility, CO", "Inbound sorting complete. Dispatched on linehaul 408 toward Salt Lake City.")
            ]
        },
        {
            "shipment_id": "WB-FEDEX-7729B",
            "carrier": "FedEx",
            "carrier_tracking_id": "FX-881029471B",
            "service_type": "freight",
            "status": "in_transit",
            "origin_city": "Dallas",
            "origin_country": "US",
            "origin_address": "DFW Logistics Center, 2400 E 28th St, Dallas, TX 75261",
            "origin_lat": 32.8998,
            "origin_lng": -97.0403,
            "destination_city": "Billings",
            "destination_country": "US",
            "destination_address": "Montana Industrial Equipment, 1200 S 24th St W, Billings, MT 59102",
            "destination_lat": 45.7833,
            "destination_lng": -108.5007,
            "current_location_name": "Cheyenne Linehaul Checkpoint, WY",
            "current_lat": 41.1400,
            "current_lng": -104.8202,
            "weight_kg": 420.0,
            "package_count": 3,
            "pickup_date": now - timedelta(hours=48),
            "estimated_delivery": now + timedelta(hours=4),
            "predicted_delivery": now + timedelta(hours=22),
            "has_exception": True,
            "exception_type": "weather",
            "exception_description": "Severe winter blizzard closure along I-80 corridor. Dispatch AI autonomous re-routing via southern corridor.",
            "customer_sentiment": "frustrated",
            "customer_notified": True,
            "notes": "Industrial CNC machine bearings. Sensitive customer timeline.",
            "order": {
                "order_id": "#ORD-FX-7729",
                "customer_name": "Marcus Vance",
                "customer_email": "m.vance@montanamachinery.com",
                "total_amount": 5890.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=48), "picked_up", "Dallas Fort Worth Hub, TX", "Heavy palletized freight received at dock door 14."),
                (now - timedelta(hours=24), "in_transit", "Denver North Terminal, CO", "Linehaul transfer complete. En route to Wyoming."),
                (now - timedelta(hours=5), "exception_reported", "Cheyenne Checkpoint, WY", "Blizzard advisory closure on I-80. Dispatch AI rerouting initiated.")
            ]
        },
        {
            "shipment_id": "WB-DHL-91823B",
            "carrier": "DHL",
            "carrier_tracking_id": "DHL-552819234",
            "service_type": "express",
            "status": "in_transit",
            "origin_city": "Frankfurt",
            "origin_country": "DE",
            "origin_address": "Frankfurt CargoCity South, Bldg 543, Frankfurt, Germany",
            "origin_lat": 50.0379,
            "origin_lng": 8.5622,
            "destination_city": "Chicago",
            "destination_country": "US",
            "destination_address": "Apex Precision Auto, 4400 W Ohio St, Chicago, IL 60624",
            "destination_lat": 41.9742,
            "destination_lng": -87.9073,
            "current_location_name": "Leipzig European Air Hub, Germany",
            "current_lat": 51.4239,
            "current_lng": 12.2364,
            "weight_kg": 62.5,
            "package_count": 4,
            "pickup_date": now - timedelta(hours=20),
            "estimated_delivery": now + timedelta(hours=24),
            "predicted_delivery": now + timedelta(hours=21),
            "has_exception": False,
            "customer_sentiment": "positive",
            "notes": "Automotive ECU microcontrollers. Customs clearance pre-approved.",
            "order": {
                "order_id": "#ORD-DHL-9182",
                "customer_name": "Elena Rostova",
                "customer_email": "elena.r@apexprecision.com",
                "total_amount": 8340.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=20), "picked_up", "Frankfurt CargoCity, DE", "Consignment scanned into DHL Express export handling."),
                (now - timedelta(hours=10), "in_transit", "Leipzig European Air Hub, DE", "Transatlantic air cargo flight D0-214 manifesting.")
            ]
        },
        {
            "shipment_id": "WB-UPS-44910C",
            "carrier": "UPS",
            "carrier_tracking_id": "1Z9999999999999999",
            "service_type": "express",
            "status": "out_for_delivery",
            "origin_city": "Louisville",
            "origin_country": "US",
            "origin_address": "UPS Worldport, 810 Grade Ln, Louisville, KY 40213",
            "origin_lat": 38.1744,
            "origin_lng": -85.7360,
            "destination_city": "Los Angeles",
            "destination_country": "US",
            "destination_address": "Pacific Cloud Tech, 700 S Flower St, Los Angeles, CA 90017",
            "destination_lat": 34.0522,
            "destination_lng": -118.2437,
            "current_location_name": "Los Angeles Downtown Hub, CA",
            "current_lat": 34.0200,
            "current_lng": -118.2100,
            "weight_kg": 8.4,
            "package_count": 1,
            "pickup_date": now - timedelta(hours=36),
            "estimated_delivery": now + timedelta(hours=2),
            "predicted_delivery": now + timedelta(hours=1, minutes=30),
            "has_exception": False,
            "customer_sentiment": "positive",
            "notes": "Enterprise core optical router for data center.",
            "order": {
                "order_id": "#ORD-UPS-4491",
                "customer_name": "David Chen",
                "customer_email": "dchen@pacificcloud.io",
                "total_amount": 3150.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=36), "picked_up", "UPS Worldport, Louisville, KY", "Optical scanner validated package in sorting matrix."),
                (now - timedelta(hours=12), "in_transit", "Ontario Gateway Hub, CA", "Arrival scan at regional freight terminal."),
                (now - timedelta(hours=3), "out_for_delivery", "Los Angeles Downtown, CA", "Loaded onto final mile courier delivery van.")
            ]
        },
        {
            "shipment_id": "WB-TCS-77201D",
            "carrier": "TCS",
            "carrier_tracking_id": "TCS-44102981",
            "service_type": "standard",
            "status": "in_transit",
            "origin_city": "Karachi",
            "origin_country": "PK",
            "origin_address": "TCS Air Cargo Terminal, Shahrah-e-Faisal, Karachi",
            "origin_lat": 24.9056,
            "origin_lng": 67.1608,
            "destination_city": "Lahore",
            "destination_country": "PK",
            "destination_address": "Gulberg Logistics Depot, Lahore, Punjab",
            "destination_lat": 31.5204,
            "destination_lng": 74.3587,
            "current_location_name": "Multan Hub, Punjab, PK",
            "current_lat": 30.1575,
            "current_lng": 71.5249,
            "weight_kg": 185.0,
            "package_count": 6,
            "pickup_date": now - timedelta(hours=18),
            "estimated_delivery": now + timedelta(hours=7),
            "predicted_delivery": now + timedelta(hours=6),
            "has_exception": False,
            "customer_sentiment": "neutral",
            "notes": "Commercial textile organic pigments shipment.",
            "order": {
                "order_id": "#ORD-TCS-7720",
                "customer_name": "Tariq Mahmood",
                "customer_email": "tariq@lahoretextiles.com.pk",
                "total_amount": 950.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=18), "picked_up", "Karachi Cargo Complex, PK", "Manifested and loaded on domestic freight connection."),
                (now - timedelta(hours=6), "in_transit", "Multan Hub, PK", "Cross-docking in progress for morning departure to Lahore.")
            ]
        },
        {
            "shipment_id": "WB-FEDEX-9941X",
            "carrier": "FedEx",
            "carrier_tracking_id": "FX-339182749X",
            "service_type": "standard",
            "status": "delivered",
            "origin_city": "Atlanta",
            "origin_country": "US",
            "origin_address": "FedEx Ground Atlanta, 3600 Hartsfield Center Pkwy, Atlanta, GA",
            "origin_lat": 33.6407,
            "origin_lng": -84.4277,
            "destination_city": "Miami",
            "destination_country": "US",
            "destination_address": "Biscayne Maritime Supply, 1000 Biscayne Blvd, Miami, FL 33132",
            "destination_lat": 25.7617,
            "destination_lng": -80.1918,
            "current_location_name": "Miami Delivery Depot, FL",
            "current_lat": 25.7617,
            "current_lng": -80.1918,
            "weight_kg": 34.0,
            "package_count": 1,
            "pickup_date": now - timedelta(hours=72),
            "estimated_delivery": now - timedelta(hours=4),
            "predicted_delivery": now - timedelta(hours=4, minutes=15),
            "actual_delivery": now - timedelta(hours=4, minutes=20),
            "has_exception": False,
            "customer_sentiment": "positive",
            "notes": "Commercial marine navigation radar module. Signed by R. Rodriguez.",
            "order": {
                "order_id": "#ORD-FX-9941",
                "customer_name": "Robert Rodriguez",
                "customer_email": "r.rodriguez@biscaynemaritime.com",
                "total_amount": 2750.00,
                "status": "delivered"
            },
            "events": [
                (now - timedelta(hours=72), "picked_up", "Atlanta Hub, GA", "Scanned into linehaul container."),
                (now - timedelta(hours=28), "in_transit", "Orlando Regional Sort, FL", "Processed through automated sorter."),
                (now - timedelta(hours=8), "out_for_delivery", "Miami Depot, FL", "Courier vehicle dispatch confirmed."),
                (now - timedelta(hours=4, minutes=20), "delivered", "Miami, FL", "Delivered and electronic signature captured.")
            ]
        },
        {
            "shipment_id": "WB-DHL-66120E",
            "carrier": "DHL",
            "carrier_tracking_id": "DHL-887192031",
            "service_type": "express",
            "status": "in_transit",
            "origin_city": "London",
            "origin_country": "GB",
            "origin_address": "London Heathrow Cargo Center, Hounslow, UK",
            "origin_lat": 51.4700,
            "origin_lng": -0.4543,
            "destination_city": "New York",
            "destination_country": "US",
            "destination_address": "Fifth Avenue Luxury Group, 727 5th Ave, New York, NY 10022",
            "destination_lat": 40.6413,
            "destination_lng": -73.7781,
            "current_location_name": "JFK Bonded Customs Warehouse, NY",
            "current_lat": 40.6413,
            "current_lng": -73.7781,
            "weight_kg": 48.0,
            "package_count": 2,
            "pickup_date": now - timedelta(hours=40),
            "estimated_delivery": now + timedelta(hours=8),
            "predicted_delivery": now + timedelta(hours=14),
            "has_exception": True,
            "exception_type": "customs_hold",
            "exception_description": "US Customs & Border Protection declaration review. Dispatch AI submitted automated commercial invoice annex.",
            "customer_sentiment": "frustrated",
            "customer_notified": True,
            "notes": "High-value luxury textile collection.",
            "order": {
                "order_id": "#ORD-DHL-6612",
                "customer_name": "Claire Dupont",
                "customer_email": "c.dupont@fifthaveluxury.com",
                "total_amount": 12800.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=40), "picked_up", "Heathrow Airport, UK", "Export documentation accepted."),
                (now - timedelta(hours=16), "in_transit", "JFK International Airport, NY", "Transatlantic air freight arrival."),
                (now - timedelta(hours=6), "exception_reported", "JFK Customs Warehouse, NY", "Customs declaration review triggered.")
            ]
        },
        {
            "shipment_id": "WB-FEDEX-3310M",
            "carrier": "FedEx",
            "carrier_tracking_id": "FX-110294821M",
            "service_type": "express",
            "status": "out_for_delivery",
            "origin_city": "Seattle",
            "origin_country": "US",
            "origin_address": "FedEx Pacific Hub, 18000 International Blvd, Seattle, WA",
            "origin_lat": 47.4502,
            "origin_lng": -122.3088,
            "destination_city": "San Francisco",
            "destination_country": "US",
            "destination_address": "Mission Bay Biotech Park, 1700 4th St, San Francisco, CA 94158",
            "destination_lat": 37.7749,
            "destination_lng": -122.4194,
            "current_location_name": "San Francisco South Hub, CA",
            "current_lat": 37.7749,
            "current_lng": -122.4194,
            "weight_kg": 6.2,
            "package_count": 1,
            "pickup_date": now - timedelta(hours=16),
            "estimated_delivery": now + timedelta(hours=3),
            "predicted_delivery": now + timedelta(hours=2, minutes=10),
            "has_exception": False,
            "customer_sentiment": "positive",
            "notes": "Cryogenic cell sample container with temperature telemetry.",
            "order": {
                "order_id": "#ORD-FX-3310",
                "customer_name": "Dr. Alan Turing",
                "customer_email": "alan.t@missionbiotech.com",
                "total_amount": 2100.00,
                "status": "shipped"
            },
            "events": [
                (now - timedelta(hours=16), "picked_up", "Seattle Hub, WA", "Consignment scanned into refrigerated container."),
                (now - timedelta(hours=4), "in_transit", "Oakland Air Cargo Hub, CA", "Flight arrival and sort scan completed."),
                (now - timedelta(hours=1), "out_for_delivery", "San Francisco, CA", "Courier en route for temperature-verified delivery.")
            ]
        }
    ]

    for tid in tenant_ids:
        print(f"\nPopulating realistic records for Tenant ID {tid}...")
        prefix = "" if tid == 2 else "APX-"
        for tpl in shipment_templates:
            ship_code = f"{prefix}{tpl['shipment_id']}" if prefix else tpl["shipment_id"]
            ord_code = f"{prefix}{tpl['order']['order_id'].lstrip('#')}" if prefix else tpl["order"]["order_id"]
            if not ord_code.startswith("#"):
                ord_code = f"#{ord_code}"

            # Check if shipment already exists
            existing = db.query(Shipment).filter(
                Shipment.shipment_id == ship_code
            ).first()

            if existing:
                print(f" - Shipment {ship_code} already exists (Tenant {existing.tenant_id}). Updating details...")
                shipment = existing
                shipment.tenant_id = tid
            else:
                print(f" + Creating new shipment {ship_code} for tenant {tid}...")
                shipment = Shipment(
                    tenant_id=tid,
                    shipment_id=ship_code
                )
                db.add(shipment)

            # Link / create customer order
            ord_data = tpl.get("order")
            if ord_data:
                order = db.query(CustomerOrder).filter(
                    CustomerOrder.tenant_id == tid,
                    CustomerOrder.order_id == ord_code
                ).first()
                if not order:
                    order = CustomerOrder(
                        tenant_id=tid,
                        order_id=ord_code,
                        customer_name=ord_data["customer_name"],
                        customer_email=ord_data["customer_email"],
                        total_amount=ord_data["total_amount"],
                        status=ord_data["status"],
                        tracking_number=ship_code,
                        carrier=tpl["carrier"],
                        shipping_address=tpl["destination_address"],
                        order_date=tpl["pickup_date"],
                        estimated_delivery=tpl["estimated_delivery"]
                    )
                    db.add(order)
                    db.flush()
                shipment.order_id = order.id

            # Populate shipment fields
            shipment.carrier = tpl["carrier"]
            shipment.carrier_tracking_id = tpl["carrier_tracking_id"]
            shipment.service_type = tpl["service_type"]
            shipment.status = tpl["status"]
            shipment.origin_city = tpl["origin_city"]
            shipment.origin_country = tpl["origin_country"]
            shipment.origin_address = tpl["origin_address"]
            shipment.origin_lat = tpl["origin_lat"]
            shipment.origin_lng = tpl["origin_lng"]
            shipment.destination_city = tpl["destination_city"]
            shipment.destination_country = tpl["destination_country"]
            shipment.destination_address = tpl["destination_address"]
            shipment.destination_lat = tpl["destination_lat"]
            shipment.destination_lng = tpl["destination_lng"]
            shipment.current_location_name = tpl["current_location_name"]
            shipment.current_lat = tpl["current_lat"]
            shipment.current_lng = tpl["current_lng"]
            shipment.weight_kg = tpl["weight_kg"]
            shipment.package_count = tpl["package_count"]
            shipment.pickup_date = tpl["pickup_date"]
            shipment.estimated_delivery = tpl["estimated_delivery"]
            shipment.predicted_delivery = tpl["predicted_delivery"]
            shipment.actual_delivery = tpl.get("actual_delivery")
            shipment.has_exception = tpl["has_exception"]
            shipment.exception_type = tpl.get("exception_type")
            shipment.exception_description = tpl.get("exception_description")
            shipment.exception_resolved = False
            shipment.customer_sentiment = tpl["customer_sentiment"]
            shipment.customer_notified = tpl.get("customer_notified", False)
            shipment.notes = tpl["notes"]
            shipment.source = "carrier_api"

            db.flush()

            # Add milestone events
            for ev_time, ev_type, ev_loc, ev_desc in tpl.get("events", []):
                ev_exist = db.query(ShipmentEvent).filter(
                    ShipmentEvent.shipment_id == shipment.id,
                    ShipmentEvent.event_type == ev_type,
                    ShipmentEvent.location_name == ev_loc
                ).first()
                if not ev_exist:
                    event = ShipmentEvent(
                        shipment_id=shipment.id,
                        event_type=ev_type,
                        location_name=ev_loc,
                        description=ev_desc,
                        event_time=ev_time
                    )
                    db.add(event)

    db.commit()
    print("Database enrichment complete! Commits saved successfully.")
    db.close()

if __name__ == '__main__':
    seed()
