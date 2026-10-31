"""
Create Apex Logistics Copilot Tenant & Widget Configuration
Sets up Apex Logistics Copilot as the personal AI for the Fleet Management System.
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.widget_config import WidgetConfig

def setup_copilot():
    db = SessionLocal()
    print("Setting up Apex Logistics Copilot tenant...")

    # 1. Check or create Tenant 2: Apex Logistics Copilot
    t2 = db.query(Tenant).filter(Tenant.id == 2).first()
    if not t2:
        t2 = db.query(Tenant).filter(Tenant.name == "Apex Logistics Copilot").first()
    
    if not t2:
        print("Creating Tenant #2: Apex Logistics Copilot...")
        t2 = Tenant(
            id=2,
            name="Apex Logistics Copilot",
            industry="Autonomous Fleet Management & Logistics AI",
            description="Personal AI for the Fleet Management System under Apex Logistics",
            support_email="copilot@apexlogistics.com",
            store_url="http://localhost:5500",
            store_platform="Apex Fleet Management System",
            logistics_mode=True,
            default_carrier="FedEx",
            widget_api_key="wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y",
            is_active=True,
            onboarding_completed=True,
            owner_id=1
        )
        db.add(t2)
    else:
        print(f"Updating Tenant #{t2.id}: Apex Logistics Copilot...")
        t2.name = "Apex Logistics Copilot"
        t2.industry = "Autonomous Fleet Management & Logistics AI"
        t2.description = "Personal AI for the Fleet Management System under Apex Logistics"
        t2.support_email = "copilot@apexlogistics.com"
        t2.store_url = "http://localhost:5500"
        t2.store_platform = "Apex Fleet Management System"
        t2.logistics_mode = True
        t2.default_carrier = "FedEx"
        t2.widget_api_key = "wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y"
        t2.is_active = True
        t2.onboarding_completed = True

    db.flush()

    # 2. Setup WidgetConfig for Tenant 2
    w2 = db.query(WidgetConfig).filter(WidgetConfig.tenant_id == t2.id).first()
    if not w2:
        w2 = WidgetConfig(
            tenant_id=t2.id,
            theme_color="#4d148c",
            bot_name="Apex Logistics Copilot",
            welcome_message="Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs.",
            placeholder_text="Ask Apex Copilot about your shipment or dispatch...",
            is_active=True,
            show_branding=True,
            pre_chat_form_enabled=False,
            widget_type="full"
        )
        db.add(w2)
    else:
        w2.theme_color = "#4d148c"
        w2.bot_name = "Apex Logistics Copilot"
        w2.welcome_message = "Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs."
        w2.placeholder_text = "Ask Apex Copilot about your shipment or dispatch..."
        w2.is_active = True
        w2.show_branding = True
        w2.pre_chat_form_enabled = False
        w2.widget_type = "full"

    # 3. Also ensure Tenant 1 WidgetConfig has Apex Logistics Copilot
    w1 = db.query(WidgetConfig).filter(WidgetConfig.tenant_id == 1).first()
    if w1:
        w1.theme_color = "#4d148c"
        w1.bot_name = "Apex Logistics Copilot"
        w1.welcome_message = "Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs."
        w1.placeholder_text = "Ask Apex Copilot about your shipment or dispatch..."
        w1.is_active = True
        w1.show_branding = True
        w1.pre_chat_form_enabled = False
        w1.widget_type = "full"

    db.commit()
    print("[SUCCESS] Tenant 2 created and WidgetConfig updated!")
    db.close()

    # Also synchronize backend/data/app.db directly via sqlite
    backend_db = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'app.db')
    if os.path.exists(backend_db):
        print(f"Synchronizing {backend_db}...")
        conn = sqlite3.connect(backend_db)
        cur = conn.cursor()
        cur.execute("SELECT id FROM tenants WHERE id = 2 OR name = 'Apex Logistics Copilot'")
        row = cur.fetchone()
        if not row:
            cur.execute("""
                INSERT INTO tenants (id, name, industry, description, support_email, store_url, store_platform, logistics_mode, default_carrier, widget_api_key, is_active, onboarding_completed, owner_id)
                VALUES (2, 'Apex Logistics Copilot', 'Autonomous Fleet Management & Logistics AI', 'Personal AI for the Fleet Management System under Apex Logistics', 'copilot@apexlogistics.com', 'http://localhost:5500', 'Apex Fleet Management System', 1, 'FedEx', 'wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y', 1, 1, 1)
            """)
        else:
            cur.execute("""
                UPDATE tenants SET name = 'Apex Logistics Copilot', widget_api_key = 'wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y', is_active = 1 WHERE id = ?
            """, (row[0],))
        
        cur.execute("SELECT id FROM widget_configs WHERE tenant_id = 2")
        wrow = cur.fetchone()
        if not wrow:
            cur.execute("""
                INSERT INTO widget_configs (tenant_id, theme_color, bot_name, welcome_message, placeholder_text, is_active, show_branding, pre_chat_form_enabled, widget_type)
                VALUES (2, '#4d148c', 'Apex Logistics Copilot', 'Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs.', 'Ask Apex Copilot about your shipment or dispatch...', 1, 1, 0, 'full')
            """)
        else:
            cur.execute("""
                UPDATE widget_configs SET bot_name = 'Apex Logistics Copilot', theme_color = '#4d148c',
                welcome_message = 'Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs.',
                placeholder_text = 'Ask Apex Copilot about your shipment or dispatch...', is_active = 1, pre_chat_form_enabled = 0 WHERE tenant_id = 2
            """)

        cur.execute("""
            UPDATE widget_configs SET bot_name = 'Apex Logistics Copilot', theme_color = '#4d148c',
            welcome_message = 'Hello! I am your Apex Logistics Copilot, your personal AI for the Fleet Management System. Enter a waybill tracking # or ask about live telemetry, route disruptions, or carrier SLAs.',
            placeholder_text = 'Ask Apex Copilot about your shipment or dispatch...', is_active = 1, pre_chat_form_enabled = 0 WHERE tenant_id = 1
        """)
        conn.commit()
        conn.close()
        print("[SUCCESS] Synchronized backend/data/app.db successfully!")

if __name__ == '__main__':
    setup_copilot()
