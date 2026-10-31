"""
Insert Figure 13 Chat Data and Shipment Telemetry into the Live Database (Fixed)
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = r"behavioral-agentic-ai\backend\data\app.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

now = datetime.now()
t_start = now - timedelta(minutes=15)

# 1. Insert or update shipment WB-6B762917
c.execute("DELETE FROM shipments WHERE shipment_id = 'WB-6B762917'")
c.execute("""
    INSERT INTO shipments (
        tenant_id, shipment_id, carrier, carrier_tracking_id, service_type,
        status, origin_address, origin_city, origin_country,
        destination_address, destination_city, destination_country,
        current_location_name, weight_kg, volume_cbm, package_count,
        pickup_date, estimated_delivery, predicted_delivery,
        has_exception, exception_type, exception_description,
        exception_resolved, customer_notified, notification_count,
        customer_sentiment, notes, source, created_at, updated_at
    ) VALUES (
        1, 'WB-6B762917', 'TCS Express', 'TCS-PK-982140', 'Priority Express Ground',
        'in_transit', 'Lahore Fulfillment Hub, Punjab', 'Lahore', 'PK',
        'Karachi Port Gateway, Sindh', 'Karachi', 'PK',
        'Sukkur Distribution Center, Sindh (N-5 Corridor)', 18.5, 0.12, 1,
        ?, ?, ?,
        1, 'highway_congestion', 'Seasonal heavy linehaul congestion along N-5 highway near Sukkur',
        0, 1, 2,
        'de-escalated', 'Figure 13 Live Demo shipment. Priority review ESC-2026-8917 logged.', 'system', ?, ?
    )
""", (
    (t_start - timedelta(days=2)).isoformat(),
    (t_start - timedelta(days=1)).isoformat(),
    (now + timedelta(hours=22)).isoformat(),
    (t_start - timedelta(days=2)).isoformat(),
    now.isoformat()
))
shipment_pk = c.lastrowid

# Insert milestone events for this shipment
c.execute("DELETE FROM shipment_events WHERE shipment_id = ?", (shipment_pk,))
events = [
    ('picked_up', 'Shipment picked up at Lahore Fulfillment Hub', 'Lahore Hub, PK', 31.5204, 74.3587, (t_start - timedelta(days=2)).isoformat()),
    ('in_transit', 'Departed Lahore terminal; linehaul transit via N-5 highway', 'Lahore N-5 Gateway', 31.4500, 74.2800, (t_start - timedelta(days=2, hours=-6)).isoformat()),
    ('in_transit', 'Processed at Multan Sort Facility', 'Multan Hub, PK', 30.1575, 71.5249, (t_start - timedelta(days=1, hours=8)).isoformat()),
    ('exception', 'Linehaul delayed due to severe highway congestion near Sukkur bypass', 'Sukkur Terminal, PK', 27.7052, 68.8574, (t_start - timedelta(hours=4)).isoformat()),
    ('in_transit', 'Arrived at Sukkur Distribution Center; priority transfer scheduled', 'Sukkur Distribution Center, PK', 27.7138, 68.8488, (t_start - timedelta(hours=2)).isoformat())
]
for ev_type, desc, loc, lat, lng, ev_time in events:
    c.execute("""
        INSERT INTO shipment_events (
            shipment_id, event_type, description, location_name, location_lat, location_lng, event_time, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (shipment_pk, ev_type, desc, loc, lat, lng, ev_time, now.isoformat()))

print("Inserted shipment WB-6B762917 and milestone events!")

# 2. Insert Conversation and Messages for Fig 13 (Session linked to Tenant 2)
for tid in [2]:
    session_id_val = "session_fig13_wb6b762917"
    c.execute("DELETE FROM conversations WHERE session_id = ?", (session_id_val,))
    c.execute("""
        INSERT INTO conversations (
            tenant_id, session_id, customer_name, customer_email, status, priority,
            current_sentiment, sentiment_score, frustration_level, is_escalated,
            escalation_reason, escalated_at, detected_language, language_name, language_flag,
            last_message_preview, message_count, created_at, updated_at
        ) VALUES (
            ?, ?, 'Engr. Umer Bashir', 'umer.bashir@apexlogistics.com', 'escalated', 'urgent',
            'satisfied', 0.763, 0.28, 1,
            'Critical frustration (Ft=0.91) and legal threat regarding 2-day Express delivery delay on WB-6B762917. Priority review ESC-2026-8917 logged.',
            ?, 'en', 'English', '🇺🇸',
            'Ok thank you for the honest update. Please make sure it arrives tomorrow.', 6, ?, ?
        )
    """, (
        tid, session_id_val, (t_start + timedelta(minutes=2)).isoformat(), t_start.isoformat(), now.isoformat()
    ))
    conv_id = c.lastrowid

    # Insert the 6 chat turns
    turns = [
        # Turn 1
        ("Where is my shipment WB-6B762917?\nIt was supposed to arrive yesterday!",
         "customer", "Engr. Umer Bashir", "frustrated", 0.32, "Annoyed", "en", 0, None, (t_start).isoformat()),
        # Turn 2
        ("""Hello! I've pulled up your shipment details instantly:

📦 Waybill: WB-6B762917
🚚 Carrier: TCS Express (Priority Ground)
📍 Route:   Lahore ➔ Karachi (N-5 Highway)
⏱ Status:  IN-TRANSIT (Delayed)
📅 Orig ETA: Oct 30, 14:00 PKT
⚡ Updated:  Oct 31, 18:30 PKT (D-TAC Calibrated)
🏢 Last Scan: Sukkur Hub, Oct 31 06:15 PKT

Your package is currently moving through the Sukkur corridor. I understand it's past the original window — let me look into the delay details for you.""",
         "ai", "Apex Logistics Copilot", "neutral", 0.60, "Factual", "en", 0, None, (t_start + timedelta(seconds=2)).isoformat()),
        # Turn 3
        ("""THIS IS UNACCEPTABLE!!!
I PAID FOR EXPRESS DELIVERY AND IT'S BEEN 2 DAYS LATE!! I WANT A FULL REFUND RIGHT NOW OR I'M CALLING MY LAWYER!!!""",
         "customer", "Engr. Umer Bashir", "enraged", 0.08, "Enraged", "en", 1, "legal, lawyer, full refund, unacceptable", (t_start + timedelta(minutes=1, seconds=33)).isoformat()),
        # Turn 4
        ("""I completely understand your frustration, and I sincerely apologize for this delay. You have every right to be upset — a 2-day delay on Express service is not what you paid for.

Here is the verified telemetry breakdown:
• Root Cause: Highway congestion on N-5 near Sukkur bypass due to seasonal linehaul freight traffic (verified at 06:15).
• Current Location: Sukkur Distribution Center.
• D-TAC Revised ETA: Tomorrow by 18:30 PKT (High Confidence).

Regarding compensation, I have initiated a Priority Review of your account under case ref ESC-2026-8917. Our Senior Dispatch Care team will contact you within 2 hours with an expedited resolution.

🛡️ Policy Gate: G(a) Confirmed PASS. No unauthorized commitments made. Automated SMS telemetry tracking is active.""",
         "ai", "Apex Logistics Copilot", "empathetic", 0.85, "Empathetic De-escalation", "en", 0, None, (t_start + timedelta(minutes=1, seconds=35)).isoformat()),
        # Turn 5
        ("""Ok thank you for the honest update.
Please make sure it arrives tomorrow. The case reference helps.""",
         "customer", "Engr. Umer Bashir", "satisfied", 0.78, "Relieved", "en", 0, None, (t_start + timedelta(minutes=2, seconds=5)).isoformat()),
        # Turn 6
        ("""You're very welcome! I've confirmed your priority notification flag. You'll receive instant SMS updates as soon as your truck departs the Sukkur terminal. Have a wonderful rest of your day, and feel free to reach back out anytime!""",
         "ai", "Apex Logistics Copilot", "positive", 0.92, "Warm Closing", "en", 0, None, (t_start + timedelta(minutes=2, seconds=7)).isoformat())
    ]

    for content, sender_type, sender_name, sentiment, score, label, lang, is_trig, trig_kws, created_at in turns:
        c.execute("""
            INSERT INTO messages (
                tenant_id, conversation_id, content, sender_type, sender_name,
                sentiment, sentiment_score, sentiment_label, detected_language,
                is_escalation_trigger, trigger_keywords, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tid, conv_id, content, sender_type, sender_name,
            sentiment, score, label, lang, is_trig, trig_kws, created_at
        ))

    # Insert into escalations table
    c.execute("""
        INSERT INTO escalations (
            conversation_id, tenant_id, priority, trigger_reasons, trigger_score,
            sentiment_at_escalation, sentiment_score_at_escalation, frustration_at_escalation,
            handoff_package, status, created_at, updated_at
        ) VALUES (
            ?, ?, 'urgent',
            'Legal threat detected, typographic caps-lock shouting (Icaps=0.94), 2-day Express delay',
            0.91, 'enraged', 0.08, 0.91,
            '{"waybill":"WB-6B762917","carrier":"TCS Express","location":"Sukkur Distribution Center","revised_eta":"Tomorrow 18:30 PKT","case_ref":"ESC-2026-8917"}',
            'in_progress', ?, ?
        )
    """, (conv_id, tid, (t_start + timedelta(minutes=1, seconds=35)).isoformat(), now.isoformat()))

conn.commit()
conn.close()
print(f"Successfully inserted Fig 13 conversation and escalation for session: {session_id_val}!")
