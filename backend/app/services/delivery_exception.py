"""
Delivery Exception Classifier & Emotion-Gated Resolution Generator — V6 Logistics
Classifies delivery anomalies and generates sentiment-adapted customer communications.

PhD / Research Contribution:
Emotion-gated resolution generator that tailors tone, urgency, and actionable
remediation steps according to the customer's real-time emotional state.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DeliveryExceptionClassifier:
    """
    Classifies shipment exceptions and generates emotion-adapted responses.
    """

    EXCEPTION_DEFINITIONS = {
        "DELAY": {
            "severity": "medium",
            "resolution_steps": [
                "Track the carrier's latest GPS transit milestone",
                "Recalculate dynamic ETA using the machine learning predictor",
                "Contact carrier dispatch for expedited handling if past SLA"
            ],
            "templates": {
                "frustrated": (
                    "I completely understand how frustrating it is to wait for a delayed package, "
                    "and I am very sorry for the inconvenience. Your shipment ({shipment_id}) is running "
                    "behind schedule near {location}. I have flagged this with our priority operations team, "
                    "and our updated arrival window is {eta}. Here are the immediate steps we are taking: {steps}."
                ),
                "negative": (
                    "I apologize for the delay with your delivery. Your package ({shipment_id}) is currently "
                    "delayed near {location}. We estimate delivery by {eta}. We are monitoring this closely to avoid further delays."
                ),
                "neutral": (
                    "Your shipment {shipment_id} is slightly delayed in transit near {location}. "
                    "The current updated delivery estimate is {eta}."
                ),
                "positive": (
                    "Thank you for checking in! Shipment {shipment_id} encountered a minor delay near {location}, "
                    "but it is on track for delivery by {eta}."
                )
            }
        },
        "CUSTOMS_HOLD": {
            "severity": "high",
            "resolution_steps": [
                "Review commercial invoice and commodity clearance documents",
                "Contact customs broker to verify tariff clearance status",
                "Notify recipient if import duties or identity verification are required"
            ],
            "templates": {
                "frustrated": (
                    "I deeply apologize for the hold-up. Your international shipment ({shipment_id}) is currently "
                    "under standard regulatory customs clearance in {location}. We know this delay is stressful. "
                    "Our trade compliance team is actively liaising with the clearance broker today to expedite release."
                ),
                "negative": (
                    "We apologize for the delay. Shipment {shipment_id} is currently awaiting customs inspection in {location}. "
                    "Our logistics desk is in contact with customs to release the package as quickly as possible."
                ),
                "neutral": (
                    "Shipment {shipment_id} is currently undergoing standard customs processing at {location}. "
                    "International shipments typically clear within 24 to 48 business hours."
                ),
                "positive": (
                    "Shipment {shipment_id} has arrived in {location} and is progressing through customs clearance."
                )
            }
        },
        "ADDRESS_ISSUE": {
            "severity": "high",
            "resolution_steps": [
                "Confirm full street address, apartment/suite number, and zip code with customer",
                "Transmit updated dispatch instructions to the local delivery driver",
                "Reschedule next delivery attempt"
            ],
            "templates": {
                "frustrated": (
                    "I am so sorry for this mix-up. The carrier attempted delivery for {shipment_id} but reported "
                    "an issue locating the delivery address in {location}. Please provide your exact address or nearest "
                    "landmark, and I will immediately transmit the correction to the local driver."
                ),
                "negative": (
                    "The courier reported difficulty locating your delivery address for shipment {shipment_id}. "
                    "Could you please confirm your complete street address so we can schedule redelivery?"
                ),
                "neutral": (
                    "A delivery attempt was made for {shipment_id}, but the driver noted an address discrepancy. "
                    "Please verify your delivery address to proceed."
                ),
                "positive": (
                    "To ensure your package {shipment_id} reaches you promptly, please confirm your delivery address "
                    "and any gate code or access notes."
                )
            }
        },
        "FAILED_ATTEMPT": {
            "severity": "medium",
            "resolution_steps": [
                "Verify recipient availability or safe drop-off location",
                "Reschedule delivery for the next business day",
                "Hold at local carrier depot for direct customer pickup if requested"
            ],
            "templates": {
                "frustrated": (
                    "I understand how annoying it is to miss a delivery. The courier attempted delivery for {shipment_id} "
                    "today but was unable to complete it (Attempt #{attempt}). We can either reschedule for tomorrow or have "
                    "it held at your local facility for safe pickup. Which would you prefer?"
                ),
                "negative": (
                    "The driver attempted delivery for shipment {shipment_id} today but was unable to reach you. "
                    "A re-attempt is scheduled for the next business day."
                ),
                "neutral": (
                    "Delivery attempt #{attempt} for shipment {shipment_id} was unsuccessful. "
                    "The carrier will re-attempt delivery on the next business day."
                ),
                "positive": (
                    "The driver stopped by today with shipment {shipment_id}! Redelivery is scheduled for tomorrow."
                )
            }
        },
        "DAMAGE": {
            "severity": "critical",
            "resolution_steps": [
                "Document damaged item condition and request photographs if delivered",
                "Initiate immediate carrier damage claim inspection",
                "Trigger automatic free replacement dispatch or full refund"
            ],
            "templates": {
                "frustrated": (
                    "I am genuinely sorry and shocked to hear your package arrived damaged. That is completely unacceptable, "
                    "and I am escalating your case ({shipment_id}) to our senior team immediately. "
                    "We will arrange a priority replacement or full refund right away. Please rest assured we will make this right."
                ),
                "negative": (
                    "We are very sorry for the damage to your package {shipment_id}. "
                    "Our customer protection policy covers this in full. We are opening an immediate replacement claim."
                ),
                "neutral": (
                    "We have logged the damage report for shipment {shipment_id}. "
                    "A support specialist will assist you with a replacement or claim promptly."
                ),
                "positive": (
                    "Thank you for alerting us regarding shipment {shipment_id}. We are initiating your claim and will resolve it quickly."
                )
            }
        },
        "LOST": {
            "severity": "critical",
            "resolution_steps": [
                "Perform physical depot dock search at last known facility",
                "File official loss inquiry with carrier network",
                "Authorize replacement dispatch"
            ],
            "templates": {
                "frustrated": (
                    "I understand your deep concern and frustration. It is unacceptable that shipment {shipment_id} has had "
                    "no tracking movement for several days. I have initiated an urgent depot dock search and escalated this "
                    "to high priority. If no movement is confirmed within 24 hours, we will dispatch a replacement immediately."
                ),
                "negative": (
                    "We apologize for the prolonged absence of tracking updates for {shipment_id}. "
                    "We have opened an official carrier trace to locate your package."
                ),
                "neutral": (
                    "Shipment {shipment_id} is undergoing an internal carrier trace to verify its current facility location."
                ),
                "positive": (
                    "We are following up with the carrier to verify the current status of shipment {shipment_id}."
                )
            }
        }
    }

    def classify(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify exception type and severity from shipment attributes.
        """
        has_exception = shipment_data.get("has_exception", False)
        raw_type = (shipment_data.get("exception_type") or "").upper().replace(" ", "_")
        attempts = shipment_data.get("delivery_attempts", 0)
        status = shipment_data.get("status", "created")

        # Check explicit type first
        for key in self.EXCEPTION_DEFINITIONS:
            if key in raw_type:
                def_info = self.EXCEPTION_DEFINITIONS[key]
                return {
                    "is_exception": True,
                    "type": key,
                    "severity": def_info["severity"],
                    "resolution_steps": def_info["resolution_steps"],
                    "requires_escalation": def_info["severity"] in ("high", "critical")
                }

        # Check implicit anomalies
        if attempts >= 2:
            return {
                "is_exception": True,
                "type": "FAILED_ATTEMPT",
                "severity": "high" if attempts >= 3 else "medium",
                "resolution_steps": self.EXCEPTION_DEFINITIONS["FAILED_ATTEMPT"]["resolution_steps"],
                "requires_escalation": attempts >= 3
            }

        if has_exception:
            return {
                "is_exception": True,
                "type": "DELAY",
                "severity": "medium",
                "resolution_steps": self.EXCEPTION_DEFINITIONS["DELAY"]["resolution_steps"],
                "requires_escalation": False
            }

        return {
            "is_exception": False,
            "type": "NORMAL",
            "severity": "none",
            "resolution_steps": [],
            "requires_escalation": False
        }

    def generate_response(
        self,
        exception_type: str,
        customer_sentiment: str,
        shipment_data: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Generate emotion-adapted exception response text.
        """
        normalized_type = exception_type.upper().replace(" ", "_")
        if normalized_type not in self.EXCEPTION_DEFINITIONS:
            normalized_type = "DELAY"

        def_info = self.EXCEPTION_DEFINITIONS[normalized_type]
        sentiment_key = (customer_sentiment or "neutral").lower()
        if sentiment_key not in ("frustrated", "negative", "neutral", "positive"):
            sentiment_key = "neutral"

        template = def_info["templates"].get(sentiment_key, def_info["templates"]["neutral"])

        # Format placeholders
        shipment_id = shipment_data.get("shipment_id") or "your package"
        location = (
            shipment_data.get("current_location", {}).get("name")
            or shipment_data.get("current_location_name")
            or shipment_data.get("destination_city")
            or "the transit network"
        )
        eta = (
            shipment_data.get("predicted_delivery")
            or shipment_data.get("estimated_delivery")
            or "the next 1-2 business days"
        )
        if isinstance(eta, str) and "T" in eta:
            try:
                eta = datetime.fromisoformat(eta.replace("Z", "")).strftime("%b %d, %Y")
            except Exception:
                pass

        attempt = shipment_data.get("delivery_attempts", 1)
        steps = "; ".join(def_info["resolution_steps"][:2])

        return template.format(
            shipment_id=shipment_id,
            location=location,
            eta=eta,
            attempt=attempt,
            steps=steps
        )


# Singleton
_exception_classifier_instance: Optional[DeliveryExceptionClassifier] = None

def get_exception_classifier() -> DeliveryExceptionClassifier:
    global _exception_classifier_instance
    if _exception_classifier_instance is None:
        _exception_classifier_instance = DeliveryExceptionClassifier()
    return _exception_classifier_instance
