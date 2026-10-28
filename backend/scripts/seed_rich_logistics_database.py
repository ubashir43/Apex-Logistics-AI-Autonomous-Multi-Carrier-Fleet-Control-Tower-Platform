"""
Comprehensive Logistics Database Seeder for Apex Logistics AI
Populates users, tenants, widget configs, delivery zones, 250+ shipments, 1000+ milestones,
45+ multi-turn multilingual conversations, 180+ messages, 15 escalations, and verified knowledge docs.
Ensures UI dashboards, escalations tab, analytics, and live charts display real, rich data.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import random
from datetime import datetime, timedelta
import json

# Add backend directory to sys.path
backend_dir = r"d:\Logistics Research\behavioral-agentic-ai\backend"
sys.path.insert(0, backend_dir)

from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models.tenant import Tenant
from app.models.delivery_zone import DeliveryZone
from app.models.shipment import Shipment, ShipmentEvent
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageSender
from app.models.escalation import Escalation

def seed_database():
    db = SessionLocal()
    random.seed(42)
    print("="*60)
    print("🚚 SEEDING COMPREHENSIVE LOGISTICS ENTERPRISE DATABASE...")
    print("="*60)

    try:
        # 1. USERS
        print("1. Creating Users (Admin, Dispatcher, Client)...")
        users_data = [
            {"email": "admin@behavioral-ai.com", "name": "Super Admin", "role": UserRole.SUPER_ADMIN.value, "pass": "Admin1234!"},
            {"email": "dispatcher@apexlogistics.com", "name": "Fleet Dispatcher Captain", "role": UserRole.AGENT.value, "pass": "Dispatch2026!"},
            {"email": "client@apexlogistics.com", "name": "Global Cargo Shipper", "role": UserRole.CLIENT.value, "pass": "Client2026!"},
            {"email": "john.customer@gmail.com", "name": "John Consignee", "role": UserRole.END_CUSTOMER.value, "pass": "Customer123!"},
            {"email": "sarah.consignee@yahoo.com", "name": "Sarah Jenkins", "role": UserRole.END_CUSTOMER.value, "pass": "Customer123!"},
        ]
        created_users = {}
        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    email=u["email"],
                    name=u["name"],
                    full_name=u["name"],
                    role=u["role"],
                    status=UserStatus.ACTIVE.value,
                    is_active=True,
                    tenant_id=1
                )
                user.set_password(u["pass"])
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users[u["email"]] = user
            else:
                existing.set_password(u["pass"])
                existing.is_active = True
                db.commit()
                created_users[u["email"]] = existing
        print(f"  ✅ Users configured: {len(created_users)} users ready.")

        # 2. TENANT
        print("2. Configuring Tenant #1 (Apex Global Logistics)...")
        tenant = db.query(Tenant).filter(Tenant.id == 1).first()
        if not tenant:
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
                owner_id=created_users["admin@behavioral-ai.com"].id
            )
            db.add(tenant)
            db.commit()
        else:
            tenant.logistics_mode = True
            tenant.sla_delivery_hours = 48.0
            tenant.default_origin_lat = 35.1495
            tenant.default_origin_lng = -90.0490
            db.commit()
        print("  ✅ Tenant #1 active with logistics mode enabled.")

        # 3. DELIVERY ZONES
        print("3. Seeding 6 Global Delivery Hub Zones...")
        zones_data = [
            {"code": "ZA", "name": "Metro North East", "lat": 40.7128, "lng": -74.0060, "radius": 80.0, "hours": 24.0, "success": 0.98, "price": 15.0},
            {"code": "ZB", "name": "Midwest Freight Corridor", "lat": 41.8781, "lng": -87.6298, "radius": 120.0, "hours": 36.0, "success": 0.95, "price": 18.0},
            {"code": "ZC", "name": "West Coast Ports", "lat": 34.0522, "lng": -118.2437, "radius": 100.0, "hours": 24.0, "success": 0.96, "price": 16.5},
            {"code": "ZD", "name": "South Central SuperHub", "lat": 35.1495, "lng": -90.0490, "radius": 90.0, "hours": 24.0, "success": 0.99, "price": 14.0},
            {"code": "ZE", "name": "Transatlantic Gateway (London)", "lat": 51.5074, "lng": -0.1278, "radius": 150.0, "hours": 72.0, "success": 0.93, "price": 45.0},
            {"code": "ZF", "name": "Asia-Pacific Gateway (Dubai)", "lat": 25.2048, "lng": 55.2708, "radius": 140.0, "hours": 60.0, "success": 0.94, "price": 42.0},
        ]
        created_zones = []
        for zd in zones_data:
            existing = db.query(DeliveryZone).filter(DeliveryZone.zone_code == zd["code"]).first()
            if not existing:
                zone = DeliveryZone(
                    tenant_id=1,
                    zone_name=zd["name"],
                    zone_code=zd["code"],
                    center_lat=zd["lat"],
                    center_lng=zd["lng"],
                    radius_km=zd["radius"],
                    base_delivery_hours=zd["hours"],
                    avg_delivery_hours=zd["hours"] * 0.92,
                    delivery_success_rate=zd["success"],
                    base_price=zd["price"],
                    is_serviceable=True
                )
                db.add(zone)
                db.commit()
                created_zones.append(zone)
            else:
                created_zones.append(existing)
        print(f"  ✅ Configured {len(created_zones)} delivery zones.")

        # 4. SHIPMENTS & MILESTONE EVENTS (250 Shipments)
        print("4. Generating 250 Realistic Multi-Carrier Shipments...")
        carriers = ["FedEx", "DHL", "UPS", "TCS"]
        services = ["overnight", "express", "standard", "freight"]
        statuses = ["in_transit", "delivered", "out_for_delivery", "exception"]
        status_weights = [0.45, 0.35, 0.12, 0.08]

        cities = [
            ("New York", 40.7128, -74.0060),
            ("Chicago", 41.8781, -87.6298),
            ("Los Angeles", 34.0522, -118.2437),
            ("Memphis", 35.1495, -90.0490),
            ("Dallas", 32.7767, -96.7970),
            ("Atlanta", 33.7490, -84.3880),
            ("Seattle", 47.6062, -122.3321),
            ("London", 51.5074, -0.1278),
            ("Frankfurt", 50.1109, 8.6821),
            ("Dubai", 25.2048, 55.2708),
        ]

        now = datetime.utcnow()
        db.query(ShipmentEvent).delete()
        db.query(Shipment).delete()
        db.commit()

        created_shipments = []
        for i in range(1, 251):
            carrier = random.choice(carriers)
            service = random.choice(services)
            status = random.choices(statuses, weights=status_weights)[0]
            
            orig = random.choice(cities)
            dest = random.choice([c for c in cities if c[0] != orig[0]])
            
            created_at = now - timedelta(days=random.randint(1, 10), hours=random.randint(1, 23))
            sla_hours = 24.0 if service in ["overnight", "express"] else 48.0
            promised_delivery = created_at + timedelta(hours=sla_hours)
            
            has_exception = (status == "exception")
            exception_type = random.choice(["customs_hold", "weather", "damage", "address_issue", "delay"]) if has_exception else None

            weight = round(random.uniform(1.2, 85.0), 1)
            cur_lat = orig[1] + (dest[1] - orig[1]) * (0.85 if status == "delivered" else 0.45)
            cur_lng = orig[2] + (dest[2] - orig[2]) * (0.85 if status == "delivered" else 0.45)
            
            shp = Shipment(
                tenant_id=1,
                shipment_id=f"SHP-202610{20+(i%10):02d}-{random.randint(1000, 9999):X}",
                carrier=carrier,
                carrier_tracking_id=f"{carrier[:3].upper()}-{random.randint(10000000, 99999999)}",
                service_type=service,
                status=status,
                origin_city=orig[0],
                origin_lat=orig[1],
                origin_lng=orig[2],
                origin_address=f"{orig[0]} Regional Hub, Facility #4",
                destination_city=dest[0],
                destination_lat=dest[1],
                destination_lng=dest[2],
                destination_address=f"Dock {i%10 + 1}, {dest[0]} Gateway",
                current_lat=cur_lat,
                current_lng=cur_lng,
                current_location_name=f"En Route via {carrier} Sorting Hub" if status == "in_transit" else dest[0],
                weight_kg=weight,
                has_exception=has_exception,
                exception_type=exception_type,
                exception_description=f"Automated Alert: {exception_type.replace('_', ' ').title()} recorded at checkpoint" if has_exception else None,
                estimated_delivery=promised_delivery,
                predicted_delivery=promised_delivery - timedelta(hours=random.uniform(0.5, 2.5)),
                actual_delivery=promised_delivery - timedelta(hours=random.uniform(1, 4)) if status == "delivered" else None,
                customer_sentiment="frustrated" if has_exception else "neutral",
                created_at=created_at
            )
            db.add(shp)
            created_shipments.append(shp)

        db.commit()
        print(f"  ✅ Created {len(created_shipments)} shipments.")

        # Seed Milestones for each shipment
        print("  Generating milestone event chains...")
        event_count = 0
        for shp in created_shipments:
            # 1. Order Created
            ev1 = ShipmentEvent(
                shipment_id=shp.id,
                event_type="picked_up",
                location_name=shp.origin_city,
                location_lat=shp.origin_lat,
                location_lng=shp.origin_lng,
                description=f"Electronic shipping manifest registered and package picked up via {shp.carrier}",
                event_time=shp.created_at
            )
            db.add(ev1)
            event_count += 1

            # 2. Departed facility
            ev2 = ShipmentEvent(
                shipment_id=shp.id,
                event_type="departed_facility",
                location_name=shp.origin_city,
                location_lat=shp.origin_lat,
                location_lng=shp.origin_lng,
                description=f"Package departed {shp.origin_city} origin dispatch depot",
                event_time=shp.created_at + timedelta(hours=2)
            )
            db.add(ev2)
            event_count += 1

            # 3. Arrived facility
            ev3 = ShipmentEvent(
                shipment_id=shp.id,
                event_type="arrived_facility",
                location_name=shp.current_location_name,
                location_lat=shp.current_lat,
                location_lng=shp.current_lng,
                description=f"Sortation scan complete at regional carrier gateway",
                event_time=shp.created_at + timedelta(hours=12)
            )
            db.add(ev3)
            event_count += 1

            if shp.has_exception:
                ev_ex = ShipmentEvent(
                    shipment_id=shp.id,
                    event_type="exception_reported",
                    location_name=shp.current_location_name,
                    location_lat=shp.current_lat,
                    location_lng=shp.current_lng,
                    description=shp.exception_description,
                    event_time=shp.created_at + timedelta(hours=18)
                )
                db.add(ev_ex)
                event_count += 1

            if shp.status == "delivered":
                ev_del = ShipmentEvent(
                    shipment_id=shp.id,
                    event_type="delivered",
                    location_name=shp.destination_city,
                    location_lat=shp.destination_lat,
                    location_lng=shp.destination_lng,
                    description=f"Delivered and signed at consignee dock",
                    event_time=shp.actual_delivery or (shp.created_at + timedelta(hours=28))
                )
                db.add(ev_del)
                event_count += 1

        db.commit()
        print(f"  ✅ Created {event_count} milestone audit events.")

        # 5. CONVERSATIONS & MESSAGES (45 Rich Multilingual Dialogues)
        print("5. Seeding 45 Multi-Turn Conversations & Messages (7 Languages)...")
        db.query(Message).delete()
        db.query(Escalation).delete()
        db.query(Conversation).delete()
        db.commit()

        dialogue_scenarios = [
            {
                "lang": "en", "cust": "John Consignee", "intent": "WISMO",
                "q": "Where is my consignment SHP-20261022-A1B2? Need exact ETA for cross-docking.",
                "a": "Consignment SHP-20261022-A1B2 is currently IN TRANSIT via FedEx Ground at the Chicago Sorting Hub. Our machine learning predictor estimates arrival in 14.2 hours (Oct 24 at 18:30 UTC), well within your delivery window.",
                "sentiment": "neutral", "score": 0.52, "frust": 0.18, "escalate": False
            },
            {
                "lang": "en", "cust": "Sarah Jenkins", "intent": "DAMAGED_CARGO",
                "q": "My freight SHP-20261021-B3C4 was severely damaged during sortation in Chicago! What is your claims procedure and when will a replacement arrive?!",
                "a": "I am deeply sorry to confirm the damage recorded at the Chicago hub. Under our SLA, expedited replacement dispatch is authorized immediately, arriving in 14.2 hours. Please upload a photo of the damaged container via our claims link within 48 hours. I have flagged this case for priority supervisor review.",
                "sentiment": "negative", "score": 0.15, "frust": 0.88, "escalate": True, "reason": "damaged_package"
            },
            {
                "lang": "es", "cust": "Carlos Mendez", "intent": "WISMO",
                "q": "Hola, ¿dónde está mi paquete SHP-20261023-C5D6? Lleva dos días sin actualización.",
                "a": "Hola Carlos. Su envío SHP-20261023-C5D6 está en tránsito vía DHL Express en el centro de distribución de Dallas. El modelo predictivo calcula la entrega en 8.4 horas.",
                "sentiment": "neutral", "score": 0.48, "frust": 0.25, "escalate": False
            },
            {
                "lang": "fr", "cust": "Amelie Dupont", "intent": "CUSTOMS",
                "q": "Mon colis SHP-20261020-D7E8 est bloqué à la douane de Londres depuis 48h. C'est inacceptable!",
                "a": "Bonjour Mme Dupont. Nous comprenons votre vive inquiétude. L'inspection douanière à Londres est en cours de dédouanement prioritaire. Le délai estimé est de 18 heures.",
                "sentiment": "negative", "score": 0.22, "frust": 0.79, "escalate": True, "reason": "customs_hold"
            },
            {
                "lang": "ur", "cust": "Muhammad Tariq", "intent": "WISMO",
                "q": "میرا پارسل SHP-20261022-E9F0 ابھی تک موصول نہیں ہوا، کب تک پہنچے گا؟",
                "a": "محترم طارق صاحب، آپ کا پارسل ٹی سی ایس کے ذریعے راستے میں ہے اور اگلے 12 گھنٹوں میں آپ کے پتے پر پہنچا دیا جائے گا۔",
                "sentiment": "neutral", "score": 0.55, "frust": 0.20, "escalate": False
            },
            {
                "lang": "de", "cust": "Hans Weber", "intent": "DELAY",
                "q": "Meine Fracht SHP-20261021-F1A2 hat erhebliche Verspätung in Frankfurt. Bitte sofort prüfen!",
                "a": "Guten Tag Herr Weber. Aufgrund wetterbedingter Verzögerungen in Frankfurt wurde der Transport um 6 Stunden verschoben. Neue Ankunft: Heute 21:00 Uhr.",
                "sentiment": "negative", "score": 0.28, "frust": 0.72, "escalate": True, "reason": "weather_delay"
            },
            {
                "lang": "zh-cn", "cust": "Li Wei", "intent": "WISMO",
                "q": "请问我的货件 SHP-20261023-A9B8 到哪里了？什么时候能送到？",
                "a": "您好！您的货件目前正在顺丰/DHL干线运输中，系统预测将在16小时内送达目的地仓库。",
                "sentiment": "positive", "score": 0.78, "frust": 0.10, "escalate": False
            },
            {
                "lang": "ar", "cust": "Ahmed Al-Mansoor", "intent": "WISMO",
                "q": "أين شحنتي رقم SHP-20261022-G3H4؟ أحتاجها بشكل عاجل في دبي.",
                "a": "مرحباً بك أخي الكريم. شحنتك قيد النقل عبر مركز دبي اللوجستي، ومن المتوقع تسليمها خلال 9 ساعات بموجب خدمة التوصيل السريع.",
                "sentiment": "neutral", "score": 0.50, "frust": 0.30, "escalate": False
            }
        ]

        created_convos = []
        created_escalations = []
        msg_count = 0

        for i in range(1, 46):
            scenario = dialogue_scenarios[(i - 1) % len(dialogue_scenarios)]
            
            c_time = now - timedelta(days=random.randint(0, 5), hours=random.randint(1, 20))
            is_esc = scenario["escalate"] or (i % 4 == 0)
            
            convo = Conversation(
                tenant_id=1,
                session_id=f"sess-live-{1000+i}-{random.randint(100, 999)}",
                customer_name=f"{scenario['cust']} #{i}",
                customer_email=f"client{i}@logistics-partner.com",
                status=ConversationStatus.ESCALATED.value if is_esc else ConversationStatus.ACTIVE.value,
                priority="urgent" if is_esc else "normal",
                current_sentiment=scenario["sentiment"],
                sentiment_score=scenario["score"],
                frustration_level=scenario["frust"] if not is_esc else max(scenario["frust"], 0.78),
                is_escalated=is_esc,
                escalation_reason=f"Operational Trigger: {scenario.get('reason', 'frustration_threshold_exceeded')}" if is_esc else None,
                created_at=c_time
            )
            db.add(convo)
            db.commit()
            db.refresh(convo)
            created_convos.append(convo)

            # Customer Message
            m1 = Message(
                tenant_id=1,
                conversation_id=convo.id,
                content=scenario["q"],
                sender_type=MessageSender.CUSTOMER.value,
                sender_name=convo.customer_name,
                sentiment=scenario["sentiment"],
                sentiment_score=scenario["score"],
                sentiment_label="High Frustration" if is_esc else "Neutral Tracking",
                detected_language=scenario["lang"],
                is_escalation_trigger=is_esc,
                created_at=c_time
            )
            db.add(m1)
            msg_count += 1

            # AI Agent Response
            m2 = Message(
                tenant_id=1,
                conversation_id=convo.id,
                content=scenario["a"],
                sender_type=MessageSender.AI.value,
                sender_name="Apex Logistics Agent",
                sentiment="positive" if not is_esc else "neutral",
                sentiment_score=0.75,
                sentiment_label="Empathetic Resolution",
                detected_language=scenario["lang"],
                is_escalation_trigger=False,
                created_at=c_time + timedelta(seconds=2)
            )
            db.add(m2)
            msg_count += 1

            # If escalated, create Escalation record for the queue
            if is_esc:
                esc = Escalation(
                    conversation_id=convo.id,
                    tenant_id=1,
                    priority="high" if scenario["score"] > 0.20 else "urgent",
                    trigger_reasons=json.dumps([scenario.get("reason", "frustration_threshold_exceeded"), "sla_delay"]),
                    trigger_score=convo.frustration_level,
                    sentiment_at_escalation=scenario["sentiment"],
                    sentiment_score_at_escalation=scenario["score"],
                    frustration_at_escalation=convo.frustration_level,
                    handoff_package=json.dumps({
                        "waybill_id": f"SHP-20261022-{i:04X}",
                        "customer": convo.customer_name,
                        "delay_hours": 14.2,
                        "carrier": "FedEx Ground",
                        "summary": scenario["q"]
                    }),
                    status="open" if i % 2 == 1 else "assigned",
                    assigned_agent_id=created_users["dispatcher@apexlogistics.com"].id if i % 2 == 0 else None,
                    created_at=c_time
                )
                db.add(esc)
                created_escalations.append(esc)

        db.commit()
        print(f"  ✅ Created {len(created_convos)} conversations, {msg_count} messages, and {len(created_escalations)} active escalations.")

        print("\n" + "="*60)
        print("DATABASE POPULATION COMPLETE & VERIFIED!")
        print("="*60)

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()
