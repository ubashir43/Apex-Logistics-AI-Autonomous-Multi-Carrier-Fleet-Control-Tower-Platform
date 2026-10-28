"""
Intent-Based Query Router — V6 Logistics & E-Commerce Hybrid (Zone 5)
Classifies user messages across 12 high-precision categories, extracts entities
(shipment IDs, order IDs, locations, weights), and routes to the most efficient handler.

Intents:
  SHIPMENT_TRACKING  → Fast-Path / Waybill status lookup
  ETA_INQUIRY        → ML ETA prediction engine
  DELIVERY_EXCEPTION → Emotion-Gated exception classifier & ReAct Agent
  BOOKING_REQUEST    → Shipment booking flow
  RATE_INQUIRY       → Zone & geospatial freight calculator
  PICKUP_SCHEDULE    → Courier dispatch scheduling
  ORDER_QUERY        → SQL order lookup
  ORDER_VERIFY       → Verify engine
  PURCHASE           → Widget order placement
  PRODUCT_INFO       → Product DB / RAG
  COMPLAINT          → Escalation engine + sentiment gating
  HUMAN_REQUEST      → Direct dispatcher/agent escalation
  GENERAL_CHAT       → Knowledge Base RAG + LLM (default)
"""

import re
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# Intent Categories
# ═══════════════════════════════════════════
INTENT_SHIPMENT_TRACKING = "SHIPMENT_TRACKING"
INTENT_ETA_INQUIRY       = "ETA_INQUIRY"
INTENT_DELIVERY_EXCEPTION= "DELIVERY_EXCEPTION"
INTENT_BOOKING_REQUEST   = "BOOKING_REQUEST"
INTENT_RATE_INQUIRY      = "RATE_INQUIRY"
INTENT_PICKUP_SCHEDULE   = "PICKUP_SCHEDULE"
INTENT_ORDER_QUERY       = "ORDER_QUERY"
INTENT_ORDER_VERIFY      = "ORDER_VERIFY"
INTENT_PURCHASE          = "PURCHASE"
INTENT_PRODUCT_INFO      = "PRODUCT_INFO"
INTENT_COMPLAINT         = "COMPLAINT"
INTENT_HUMAN_REQUEST     = "HUMAN_REQUEST"
INTENT_GENERAL_CHAT      = "GENERAL_CHAT"

# ═══════════════════════════════════════════
# Pattern Matching for Identifiers
# ═══════════════════════════════════════════

# Shipment tracking numbers: SHP-20261022-A1B2C, TCS1234567, DHL-98765432, etc.
SHIPMENT_ID_PATTERN = re.compile(
    r'\b(?:SHP|TRK|WAY|EXP|FEDEX|DHL|UPS|TCS)-?[A-Za-z0-9]{4,24}\b',
    re.IGNORECASE
)

# Standard order ID pattern: #ORD-12345, ORD12345, #12345, order 12345
ORDER_ID_PATTERN = re.compile(
    r'#?[A-Za-z]*-?\d{4,}',
    re.IGNORECASE
)

# Generic numeric tracking code (8 to 16 digits)
NUMERIC_TRACKING_PATTERN = re.compile(
    r'\b\d{8,16}\b'
)

# ═══════════════════════════════════════════
# Keyword Sets (Multilingual)
# ═══════════════════════════════════════════

TRACKING_KEYWORDS = {
    "track", "tracking", "where is", "shipment status", "delivery status",
    "package location", "current location", "in transit", "out for delivery",
    "where is my package", "where is my shipment", "track my shipment", "tracking number",
    "shipment update", "tracking update", "delivery update", "waybill", "consignment",
    "courier status", "parcel status", "check tracking",
    # Spanish
    "rastrear", "seguimiento", "dónde está mi paquete", "rastreo", "ubicación",
    # French
    "suivi", "où est mon colis", "statut de livraison",
    # German
    "sendungsverfolgung", "wo ist mein paket", "sendungsstatus",
    # Urdu
    "شپمنٹ", "ٹریکنگ", "میرا پارسل کہاں ہے",
    # Hindi
    "ट्रैकिंग", "मेरा पार्सल कहाँ है",
}

ETA_KEYWORDS = {
    "when will", "arrival time", "estimated delivery", "eta",
    "how long", "delivery date", "arrive", "expected delivery",
    "when does it arrive", "delivery time", "how many days", "expected date",
    "reach me", "delivery estimate",
    # Spanish
    "cuándo llega", "tiempo de entrega", "fecha estimada",
    # French
    "quand arrive", "délai de livraison", "date de livraison",
    # German
    "wann kommt", "lieferzeit", "voraussichtliche lieferung",
    # Urdu
    "کب پہنچے گا", "ڈیلیوری کا وقت",
}

EXCEPTION_KEYWORDS = {
    "damaged", "broken", "lost package", "missing", "not delivered",
    "wrong address", "failed delivery", "delivery failed", "no one home",
    "customs", "customs hold", "held up", "stuck", "delayed", "late delivery",
    "never arrived", "package damaged", "incorrect delivery", "tampered", "crushed",
    # Spanish
    "paquete dañado", "no entregado", "perdido", "retrasado", "aduana",
    # French
    "colis endommagé", "non livré", "perdu", "retard", "douane",
    # German
    "paket beschädigt", "nicht geliefert", "verloren", "verspätung",
    # Urdu
    "خراب", "نقصان", "پہنچا نہیں", "گم ہو گیا",
}

BOOKING_KEYWORDS = {
    "book shipment", "send a package", "ship this", "create shipment",
    "new shipment", "arrange delivery", "book delivery", "i need to ship",
    "want to send", "dispatch a parcel", "create parcel",
    # Spanish
    "enviar paquete", "crear envío",
    # French
    "envoyer un colis", "créer un envoi",
    # German
    "paket versenden", "sendung buchen",
    # Urdu
    "پارسل بھیجنا", "شپمنٹ بک کرنا",
}

RATE_KEYWORDS = {
    "shipping cost", "delivery cost", "how much to ship", "how much does it cost to ship",
    "cost to ship", "cost of shipping", "shipping rate", "shipping price", "delivery price",
    "freight rate", "freight cost", "price to deliver", "shipping fee", "delivery charge",
    "rate card", "price list", "shipping quote", "rate calculator", "quote to send",
    # Spanish
    "costo de envío", "tarifa de envío",
    # French
    "frais de port", "coût de livraison",
    # German
    "versandkosten", "lieferpreis",
    # Urdu
    "شپنگ کے اخراجات", "کرایہ",
}

PICKUP_KEYWORDS = {
    "schedule pickup", "arrange pickup", "courier pickup", "pick up my parcel",
    "come collect", "collection time", "pickup date", "schedule collection",
    # Spanish
    "programar recogida", "recoger paquete",
    # French
    "planifier un ramassage", "enlèvement",
    # German
    "abholung vereinbaren",
}

ORDER_KEYWORDS = {
    "order", "order status", "order number", "my order", "order details",
    # Spanish
    "pedido", "mi pedido",
    # French
    "commande", "ma commande",
    # German
    "bestellung", "meine bestellung",
    # Urdu
    "آرڈر", "میرا آرڈر",
}

VERIFY_KEYWORDS = {
    "verify order", "confirm my order", "verify my", "order verification",
    "check order", "validate order",
}

PURCHASE_KEYWORDS = {
    "i want to buy", "i want to order", "place order", "place an order",
    "add to cart", "i'll take", "order this", "buy this", "purchase this",
    "checkout", "buy it",
}

PRODUCT_KEYWORDS = {
    "price", "cost", "stock", "available", "product", "catalog", "inventory",
    "item", "tell me about",
}

COMPLAINT_KEYWORDS = {
    "refund", "terrible", "worst", "complaint", "complain", "awful",
    "horrible", "unacceptable", "disgusting", "ruined", "angry", "furious",
}

HUMAN_KEYWORDS = {
    "human", "real person", "agent", "manager", "talk to someone",
    "speak to", "real human", "actual person", "customer service",
    "representative", "supervisor", "operator", "dispatcher",
}

KB_KEYWORDS = {
    "policy", "rules", "contact", "email", "phone", "address",
    "hours", "location", "terms", "conditions", "refund policy",
    "return policy", "shipping policy", "about", "who we are",
    "company", "support", "help", "guide", "faq",
}

# ═══════════════════════════════════════════
# Intent Permission Map by Widget Mode
# ═══════════════════════════════════════════
WIDGET_INTENT_MAP = {
    "full": {
        INTENT_SHIPMENT_TRACKING, INTENT_ETA_INQUIRY, INTENT_DELIVERY_EXCEPTION,
        INTENT_BOOKING_REQUEST, INTENT_RATE_INQUIRY, INTENT_PICKUP_SCHEDULE,
        INTENT_ORDER_QUERY, INTENT_ORDER_VERIFY, INTENT_PURCHASE,
        INTENT_PRODUCT_INFO, INTENT_COMPLAINT, INTENT_HUMAN_REQUEST,
        INTENT_GENERAL_CHAT
    },
    "logistics": {
        INTENT_SHIPMENT_TRACKING, INTENT_ETA_INQUIRY, INTENT_DELIVERY_EXCEPTION,
        INTENT_BOOKING_REQUEST, INTENT_RATE_INQUIRY, INTENT_PICKUP_SCHEDULE,
        INTENT_COMPLAINT, INTENT_HUMAN_REQUEST, INTENT_GENERAL_CHAT
    },
    "order": {
        INTENT_SHIPMENT_TRACKING, INTENT_ETA_INQUIRY, INTENT_ORDER_QUERY,
        INTENT_ORDER_VERIFY, INTENT_PURCHASE, INTENT_COMPLAINT, INTENT_HUMAN_REQUEST
    },
    "info": {
        INTENT_GENERAL_CHAT, INTENT_PRODUCT_INFO, INTENT_RATE_INQUIRY
    },
    "verify": {
        INTENT_ORDER_VERIFY, INTENT_SHIPMENT_TRACKING
    }
}


def extract_tracking_id(text: str) -> Optional[str]:
    """Extract shipment tracking or waybill ID from text."""
    # 1. Prefixed shipment ID (SHP-..., TCS-..., etc.)
    shp_match = SHIPMENT_ID_PATTERN.search(text)
    if shp_match:
        return shp_match.group(0).upper().strip("#")

    # 2. Generic order ID pattern
    ord_match = ORDER_ID_PATTERN.search(text)
    if ord_match:
        return ord_match.group(0).upper().lstrip("#")

    # 3. Numeric tracking number
    num_match = NUMERIC_TRACKING_PATTERN.search(text)
    if num_match:
        return num_match.group(0)

    return None


def extract_location_entities(text: str) -> Dict[str, Optional[str]]:
    """Simple heuristic extraction for origin and destination cities/locations."""
    origin = None
    dest = None

    # Matches: "from [origin] to [destination]"
    from_to = re.search(r'\bfrom\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:[,\.\?]|$)', text, re.IGNORECASE)
    if from_to:
        origin = from_to.group(1).strip()
        dest = from_to.group(2).strip()
    else:
        # Matches: "to [destination]"
        to_match = re.search(r'\bto\s+([A-Za-z\s]+?)(?:[,\.\?]|$)', text, re.IGNORECASE)
        if to_match:
            dest = to_match.group(1).strip()

    return {"origin": origin, "destination": dest}


def classify_intent(
    text: str,
    widget_type: str = "full",
    sentiment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify incoming user message intent with confidence and extracted parameters.
    """
    text_lower = text.lower().strip()
    allowed_intents = WIDGET_INTENT_MAP.get(widget_type, WIDGET_INTENT_MAP["full"])
    tracking_id = extract_tracking_id(text)
    locations = extract_location_entities(text)

    # ── Priority 1: Human / Dispatcher Request ──
    human_matches = sum(1 for kw in HUMAN_KEYWORDS if kw in text_lower)
    if human_matches > 0 and INTENT_HUMAN_REQUEST in allowed_intents:
        return {
            "intent": INTENT_HUMAN_REQUEST,
            "confidence": min(0.65 + human_matches * 0.15, 0.98),
            "extracted_data": {"tracking_id": tracking_id},
            "reason": f"Matched human/dispatcher request keywords: {human_matches}"
        }

    # ── Priority 2: Explicit Delivery Exception / Issue ──
    exception_matches = sum(1 for kw in EXCEPTION_KEYWORDS if kw in text_lower)
    if exception_matches > 0 and INTENT_DELIVERY_EXCEPTION in allowed_intents:
        return {
            "intent": INTENT_DELIVERY_EXCEPTION,
            "confidence": min(0.70 + exception_matches * 0.10, 0.96),
            "extracted_data": {
                "tracking_id": tracking_id,
                "exception_hints": [kw for kw in EXCEPTION_KEYWORDS if kw in text_lower]
            },
            "reason": f"Matched delivery exception keywords: {exception_matches}"
        }

    # ── Priority 3: ETA Inquiry ──
    eta_matches = sum(1 for kw in ETA_KEYWORDS if kw in text_lower)
    if eta_matches > 0 and INTENT_ETA_INQUIRY in allowed_intents:
        return {
            "intent": INTENT_ETA_INQUIRY,
            "confidence": min(0.65 + eta_matches * 0.12, 0.95),
            "extracted_data": {"tracking_id": tracking_id},
            "reason": f"Matched ETA inquiry keywords: {eta_matches}"
        }

    # ── Priority 4: Shipment Tracking (Explicit Tracking ID or Keywords) ──
    tracking_matches = sum(1 for kw in TRACKING_KEYWORDS if kw in text_lower)
    if (tracking_id or tracking_matches > 0) and INTENT_SHIPMENT_TRACKING in allowed_intents:
        conf = 0.95 if tracking_id else min(0.60 + tracking_matches * 0.12, 0.90)
        return {
            "intent": INTENT_SHIPMENT_TRACKING,
            "confidence": conf,
            "extracted_data": {"tracking_id": tracking_id},
            "reason": "Explicit tracking ID detected" if tracking_id else f"Tracking keywords: {tracking_matches}"
        }

    # ── Priority 5: Rate Inquiry ──
    rate_matches = sum(1 for kw in RATE_KEYWORDS if kw in text_lower)
    if rate_matches > 0 and INTENT_RATE_INQUIRY in allowed_intents:
        return {
            "intent": INTENT_RATE_INQUIRY,
            "confidence": min(0.65 + rate_matches * 0.12, 0.95),
            "extracted_data": {
                "origin": locations["origin"],
                "destination": locations["destination"]
            },
            "reason": f"Rate inquiry keywords matched: {rate_matches}"
        }

    # ── Priority 6: Booking Request ──
    booking_matches = sum(1 for kw in BOOKING_KEYWORDS if kw in text_lower)
    if booking_matches > 0 and INTENT_BOOKING_REQUEST in allowed_intents:
        return {
            "intent": INTENT_BOOKING_REQUEST,
            "confidence": min(0.65 + booking_matches * 0.12, 0.95),
            "extracted_data": {
                "origin": locations["origin"],
                "destination": locations["destination"]
            },
            "reason": f"Booking keywords matched: {booking_matches}"
        }

    # ── Priority 7: Pickup Scheduling ──
    pickup_matches = sum(1 for kw in PICKUP_KEYWORDS if kw in text_lower)
    if pickup_matches > 0 and INTENT_PICKUP_SCHEDULE in allowed_intents:
        return {
            "intent": INTENT_PICKUP_SCHEDULE,
            "confidence": min(0.65 + pickup_matches * 0.12, 0.95),
            "extracted_data": {},
            "reason": f"Pickup keywords matched: {pickup_matches}"
        }

    # ── Priority 8: Knowledge Base Keywords ──
    kb_matches = sum(1 for kw in KB_KEYWORDS if kw in text_lower)
    if kb_matches > 0:
        return {
            "intent": INTENT_GENERAL_CHAT,
            "confidence": 0.88,
            "extracted_data": {},
            "reason": f"Matched KB policy keywords (count: {kb_matches})"
        }

    # ── Priority 9: Complaint / Frustration ──
    complaint_matches = sum(1 for kw in COMPLAINT_KEYWORDS if kw in text_lower)
    if (complaint_matches > 0 or sentiment in ("negative", "frustrated")) and INTENT_COMPLAINT in allowed_intents:
        return {
            "intent": INTENT_COMPLAINT,
            "confidence": min(0.65 + complaint_matches * 0.10, 0.90),
            "extracted_data": {"tracking_id": tracking_id},
            "reason": f"Complaint keywords ({complaint_matches}) or negative sentiment"
        }

    # ── Priority 10: E-Commerce Retail Fallbacks ──
    order_matches = sum(1 for kw in ORDER_KEYWORDS if kw in text_lower)
    if order_matches > 0 and INTENT_ORDER_QUERY in allowed_intents:
        return {
            "intent": INTENT_ORDER_QUERY,
            "confidence": 0.80,
            "extracted_data": {"order_id": tracking_id},
            "reason": "Retail order query keywords"
        }

    purchase_matches = sum(1 for kw in PURCHASE_KEYWORDS if kw in text_lower)
    if purchase_matches > 0 and INTENT_PURCHASE in allowed_intents:
        return {
            "intent": INTENT_PURCHASE,
            "confidence": 0.85,
            "extracted_data": {"product_query": text_lower},
            "reason": "Retail purchase keywords"
        }

    product_matches = sum(1 for kw in PRODUCT_KEYWORDS if kw in text_lower)
    if product_matches > 0 and INTENT_PRODUCT_INFO in allowed_intents:
        return {
            "intent": INTENT_PRODUCT_INFO,
            "confidence": 0.75,
            "extracted_data": {},
            "reason": "Product inquiry keywords"
        }

    # ── Default ──
    default_intent = INTENT_GENERAL_CHAT
    if default_intent not in allowed_intents and allowed_intents:
        default_intent = list(allowed_intents)[0]

    return {
        "intent": default_intent,
        "confidence": 0.50,
        "extracted_data": {"tracking_id": tracking_id},
        "reason": "Default conversational classification"
    }


def extract_order_id(text: str) -> Optional[str]:
    """Backward compatibility helper."""
    return extract_tracking_id(text)
