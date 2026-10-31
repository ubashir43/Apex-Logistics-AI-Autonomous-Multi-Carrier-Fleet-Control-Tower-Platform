"""
Apex Logistics AI — Single Enterprise Consolidation Script
Consolidates all database tables, users, shipments, orders, and conversations
under a single unified enterprise fleet: Apex Global Logistics.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.shipment import Shipment, ShipmentEvent
from app.models.order import CustomerOrder
from app.models.conversation import Conversation
from app.models.delivery_zone import DeliveryZone
from app.models.knowledge_document import KnowledgeDocument
from app.models.widget_config import WidgetConfig

def unify():
    db = SessionLocal()
    print("Beginning single-enterprise consolidation...")

    # 1. Clean up secondary tenants first to free up any unique keys
    other_tenants = db.query(Tenant).filter(Tenant.id != 1).all()
    for ot in other_tenants:
        print(f"Removing secondary tenant: {ot.id} - {ot.name}")
        db.delete(ot)
    db.flush()

    # 2. Primary Enterprise Tenant (ID = 1)
    primary = db.query(Tenant).filter(Tenant.id == 1).first()
    if not primary:
        print("Creating primary enterprise tenant...")
        primary = Tenant(
            id=1,
            name="Apex Global Logistics",
            support_email="dispatch@apexlogistics.com",
            widget_api_key="wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y",
            is_active=True,
            onboarding_completed=True,
            owner_id=1
        )
        db.add(primary)
    else:
        print(f"Updating primary enterprise tenant (ID {primary.id})...")
        primary.name = "Apex Global Logistics"
        primary.support_email = "dispatch@apexlogistics.com"
        primary.widget_api_key = "wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y"
        primary.is_active = True
        primary.onboarding_completed = True

    db.flush()

    # 2. Reassign all users to primary company
    users = db.query(User).all()
    print(f"Reassigning {len(users)} users to primary enterprise fleet...")
    for u in users:
        u.tenant_id = 1

    # 3. Reassign all shipments to primary company
    shipments = db.query(Shipment).all()
    print(f"Reassigning {len(shipments)} shipments to primary enterprise fleet...")
    for s in shipments:
        s.tenant_id = 1

    # 4. Reassign all customer orders
    orders = db.query(CustomerOrder).all()
    print(f"Reassigning {len(orders)} orders to primary enterprise fleet...")
    for o in orders:
        o.tenant_id = 1

    # 5. Reassign all conversations
    convs = db.query(Conversation).all()
    print(f"Reassigning {len(convs)} conversations to primary enterprise fleet...")
    for c in convs:
        c.tenant_id = 1

    # 6. Reassign all delivery zones
    zones = db.query(DeliveryZone).all()
    print(f"Reassigning {len(zones)} delivery zones to primary enterprise fleet...")
    for z in zones:
        z.tenant_id = 1

    # 7. Reassign all knowledge docs
    docs = db.query(KnowledgeDocument).all()
    print(f"Reassigning {len(docs)} knowledge documents to primary enterprise fleet...")
    for d in docs:
        d.tenant_id = 1

    # 8. Ensure WidgetConfig for tenant 1 has FedEx purple
    wconf = db.query(WidgetConfig).filter(WidgetConfig.tenant_id == 1).first()
    if not wconf:
        wconf = WidgetConfig(
            tenant_id=1,
            theme_color="#4d148c",
            bot_name="Apex Dispatch AI",
            welcome_message="Hello! I am your Apex Autonomous Dispatch AI. Enter a tracking waybill # or ask about your freight shipment."
        )
        db.add(wconf)
    else:
        wconf.theme_color = "#4d148c"
        wconf.bot_name = "Apex Dispatch AI"
        wconf.welcome_message = "Hello! I am your Apex Autonomous Dispatch AI. Enter a tracking waybill # or ask about your freight shipment."

    db.commit()
    print("[SUCCESS] All database records unified under single enterprise fleet: Apex Global Logistics!")
    db.close()

if __name__ == '__main__':
    unify()
