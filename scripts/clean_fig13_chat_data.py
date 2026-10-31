# -*- coding: utf-8 -*-
"""
Clean and insert the exact Figure 13 6-turn chat data into both app.db databases.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATHS = [
    r"behavioral-agentic-ai\backend\data\app.db",
    r"behavioral-agentic-ai\data\app.db"
]

now = datetime.now()
t0 = now - timedelta(minutes=10)

turns = [
    # Turn 1: Customer
    (
        "Where is my shipment WB-6B762917?\nIt was supposed to arrive yesterday!",
        "customer", "Engr. Umer Bashir", "frustrated", 0.32, "Annoyed", "en", 0, None,
        (t0).isoformat()
    ),
    # Turn 2: AI
    (
        "Hello! I've pulled up your shipment details instantly:\n\n"
        "📦 Waybill: WB-6B762917\n"
        "🚚 Carrier: TCS Express (Priority Ground)\n"
        "📍 Route: Lahore → Karachi (N-5 Highway)\n"
        "⏱ Status: IN-TRANSIT (Delayed)\n"
        "📅 Orig ETA: Oct 30, 14:00 PKT\n"
        "⚡ Updated: Oct 31, 18:30 PKT (D-TAC Calibrated)\n"
        "🏢 Last Scan: Sukkur Hub, Oct 31 06:15 PKT\n\n"
        "Your package is currently moving through the Sukkur corridor. I understand it's past the original window — let me look into the delay details for you.",
        "ai", "Apex Logistics Copilot", "neutral", 0.60, "Factual", "en", 0, None,
        (t0 + timedelta(seconds=2)).isoformat()
    ),
    # Turn 3: Customer (Escalation trigger)
    (
        "THIS IS UNACCEPTABLE!!!\n"
        "I PAID FOR EXPRESS DELIVERY AND IT'S BEEN 2 DAYS LATE!! I WANT A FULL REFUND RIGHT NOW OR I'M CALLING MY LAWYER!!!",
        "customer", "Engr. Umer Bashir", "enraged", 0.08, "Enraged", "en", 1, "legal, lawyer, full refund, unacceptable",
        (t0 + timedelta(minutes=1, seconds=33)).isoformat()
    ),
    # Turn 4: AI (Empathetic de-escalation + Policy Gated)
    (
        "I completely understand your frustration, and I sincerely apologize for this delay. You have every right to be upset — a 2-day delay on Express service is not what you paid for.\n\n"
        "Here is the verified telemetry breakdown:\n"
        "• Root Cause: Highway congestion on N-5 near Sukkur bypass due to seasonal linehaul freight traffic (verified at 06:15).\n"
        "• Current Location: Sukkur Distribution Center.\n"
        "• D-TAC Revised ETA: Tomorrow by 18:30 PKT (High Confidence).\n\n"
        "Regarding compensation, I have initiated a Priority Review of your account under case ref ESC-2026-8917. Our Senior Dispatch Care team will contact you within 2 hours with an expedited resolution.\n\n"
        "🛡️ Policy Gate: G(a) Confirmed PASS. No unauthorized commitments made. Automated SMS telemetry tracking is active.",
        "ai", "Apex Logistics Copilot", "empathetic", 0.85, "Empathetic De-escalation", "en", 0, None,
        (t0 + timedelta(minutes=1, seconds=35)).isoformat()
    ),
    # Turn 5: Customer (Sentiment Recovery)
    (
        "Ok thank you for the honest update.\nPlease make sure it arrives tomorrow. The case reference helps.",
        "customer", "Engr. Umer Bashir", "satisfied", 0.78, "Relieved", "en", 0, None,
        (t0 + timedelta(minutes=2, seconds=5)).isoformat()
    ),
    # Turn 6: AI (Warm Closing)
    (
        "You're very welcome! I've confirmed your priority notification flag. You'll receive instant SMS updates as soon as your truck departs the Sukkur terminal. Have a wonderful rest of your day, and feel free to reach back out anytime!",
        "ai", "Apex Logistics Copilot", "positive", 0.92, "Warm Closing", "en", 0, None,
        (t0 + timedelta(minutes=2, seconds=7)).isoformat()
    )
]

for db_path in DB_PATHS:
    if not os.path.exists(db_path):
        continue
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Find conversation for session_fig13_wb6b762917
    c.execute("SELECT id, tenant_id FROM conversations WHERE session_id = 'session_fig13_wb6b762917'")
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO conversations (
                tenant_id, session_id, customer_name, customer_email, status, priority,
                current_sentiment, sentiment_score, frustration_level, is_escalated,
                escalation_reason, escalated_at, detected_language, language_name, language_flag,
                last_message_preview, message_count, created_at, updated_at
            ) VALUES (
                2, 'session_fig13_wb6b762917', 'Engr. Umer Bashir', 'umer.bashir@apexlogistics.com',
                'escalated', 'urgent', 'positive', 0.92, 0.08, 1,
                'Legal threat detected, typographic caps-lock shouting (Icaps=0.94), 2-day Express delay',
                ?, 'en', 'English', '🇬🇧',
                'You''re very welcome! I''ve confirmed your priority notification flag...',
                6, ?, ?
            )
        """, ((t0 + timedelta(minutes=1, seconds=35)).isoformat(), (t0).isoformat(), now.isoformat()))
        conv_id = c.lastrowid
        tid = 2
    else:
        conv_id, tid = row
        c.execute("""
            UPDATE conversations SET
                status = 'escalated',
                priority = 'urgent',
                current_sentiment = 'positive',
                sentiment_score = 0.92,
                frustration_level = 0.08,
                is_escalated = 1,
                escalation_reason = 'Legal threat detected, typographic caps-lock shouting (Icaps=0.94), 2-day Express delay',
                escalated_at = ?,
                last_message_preview = 'You''re very welcome! I''ve confirmed your priority notification flag...',
                message_count = 6,
                updated_at = ?
            WHERE id = ?
        """, ((t0 + timedelta(minutes=1, seconds=35)).isoformat(), now.isoformat(), conv_id))

    # Delete existing messages for this conversation to prevent duplication
    c.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))

    # Insert exactly the 6 clean turns
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

    # Clean and insert escalation
    c.execute("DELETE FROM escalations WHERE conversation_id = ?", (conv_id,))
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
    """, (conv_id, tid, (t0 + timedelta(minutes=1, seconds=35)).isoformat(), now.isoformat()))

    conn.commit()
    conn.close()
    print(f"Cleaned and updated {db_path} with 6 turns!")
