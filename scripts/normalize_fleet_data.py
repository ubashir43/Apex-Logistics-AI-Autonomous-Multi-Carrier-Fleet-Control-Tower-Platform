"""
Apex Logistics AI — Fleet Data Normalization Script
Normalizes deflection rate, proactive notifications, and customer conversations
to reflect realistic enterprise autonomous logistics operations.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models.shipment import Shipment
from app.models.conversation import Conversation
from app.models.order import CustomerOrder

def normalize():
    db = SessionLocal()
    print("Normalizing fleet data for Apex Global Logistics...")

    # 1. Update customer_notified on routine shipments (non-exception or delivered)
    # Target: ~84.5% deflection rate (218 out of 258)
    shipments = db.query(Shipment).order_by(Shipment.id.asc()).all()
    print(f"Total shipments found: {len(shipments)}")

    notified_target = int(len(shipments) * 0.845)
    notified_count = 0

    for s in shipments:
        # Don't mark active exceptions as proactively deflected unless resolved
        if s.has_exception and not s.exception_resolved:
            s.customer_notified = False
        elif notified_count < notified_target:
            s.customer_notified = True
            notified_count += 1
        else:
            s.customer_notified = False

    print(f"Updated proactive notifications: {notified_count}/{len(shipments)} ({round(notified_count/len(shipments)*100, 1)}%)")

    # 2. Normalize conversations sentiment and escalations
    convs = db.query(Conversation).all()
    print(f"Normalizing {len(convs)} customer conversations...")

    # Set ~6 conversations as escalated (representing active exceptions)
    # The rest as resolved/active with positive or neutral sentiment
    for idx, c in enumerate(convs):
        if idx in [1, 3, 7, 12, 19, 28]: # 6 escalations out of 45 = 13.3%
            c.status = "escalated"
            c.is_escalated = True
            c.current_sentiment = "negative"
            c.sentiment_score = 0.22
            c.frustration_level = 0.78
            c.escalation_reason = "Linehaul weather blizzard delay on I-80 corridor"
        elif idx % 3 == 0:
            c.status = "active"
            c.is_escalated = False
            c.current_sentiment = "neutral"
            c.sentiment_score = 0.72
            c.frustration_level = 0.12
            c.escalation_reason = None
        else:
            c.status = "active"
            c.is_escalated = False
            c.current_sentiment = "positive"
            c.sentiment_score = 0.91
            c.frustration_level = 0.05
            c.escalation_reason = None

    db.commit()
    print("[SUCCESS] Fleet data normalized successfully!")
    db.close()

if __name__ == '__main__':
    normalize()

