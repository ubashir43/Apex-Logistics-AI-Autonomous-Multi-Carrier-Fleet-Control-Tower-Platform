"""
Logistics Behavioral Predictor — V6 Logistics
Extends BehavioralPredictor with domain-specific logistics behavioral models.

PhD / Research Contribution:
Preemptive inquiry prediction (deflecting WISMO — "Where is my order?" tickets)
and dynamic exception risk scoring based on transit telemetry and emotional signals.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.services.prediction import BehavioralPredictor

logger = logging.getLogger(__name__)


class LogisticsPredictor(BehavioralPredictor):
    """
    Logistics-specific behavioral and risk prediction engine.
    """

    def predict_delivery_exception_risk(
        self,
        carrier: Optional[str],
        service_type: str,
        distance_km: float,
        current_transit_hours: float,
        zone_success_rate: float = 0.95,
        delivery_attempts: int = 0
    ) -> Dict[str, Any]:
        """
        Predict probability of a delivery exception occurring before destination arrival.
        """
        risk_score = 0.05  # baseline background risk
        factors = []

        # 1. Delivery attempts penalty
        if delivery_attempts >= 1:
            attempt_risk = 0.35 * delivery_attempts
            risk_score += attempt_risk
            factors.append(f"{delivery_attempts} previous delivery attempt failure(s)")

        # 2. Zone historical failure rate
        zone_failure_rate = max(0.0, 1.0 - (zone_success_rate or 0.95))
        if zone_failure_rate > 0.05:
            risk_score += (zone_failure_rate * 2.0)
            factors.append(f"Historical zone failure rate of {zone_failure_rate:.1%}")

        # 3. Distance & transit duration ratio
        expected_drive_hours = max(2.0, (distance_km or 100.0) / 60.0)
        if current_transit_hours > (expected_drive_hours * 2.5):
            overrun_factor = min(0.40, (current_transit_hours - expected_drive_hours) * 0.015)
            risk_score += overrun_factor
            factors.append(f"Transit duration ({round(current_transit_hours, 1)}h) exceeds expected timeline")

        # 4. Carrier specific risk factor
        carrier_lower = (carrier or "").lower()
        if carrier_lower in ("tcs", "leopard", "usps"):
            risk_score += 0.08
            factors.append(f"Carrier network variance ({carrier})")

        risk_score = min(0.98, max(0.02, round(risk_score, 3)))
        risk_level = "low" if risk_score < 0.30 else "medium" if risk_score < 0.65 else "high"

        return {
            "exception_risk_score": risk_score,
            "risk_level": risk_level,
            "primary_factors": factors,
            "recommended_action": "monitor" if risk_level == "low" else "preemptive_flag" if risk_level == "medium" else "dispatcher_review"
        }

    def predict_wismo_inquiry(
        self,
        hours_since_last_update: float,
        shipment_status: str,
        customer_sentiment_history: Optional[List[Dict]] = None,
        is_overdue: bool = False
    ) -> Dict[str, Any]:
        """
        Predict likelihood that customer will submit a 'Where is my order?' ticket
        within the next 4-6 hours.
        """
        prob = 0.10
        signals = []

        # Update silence factor
        if hours_since_last_update > 24:
            silence_prob = min(0.45, (hours_since_last_update - 24) * 0.015)
            prob += silence_prob
            signals.append(f"No tracking scan for {round(hours_since_last_update, 1)} hours")

        # Status factor
        if shipment_status == "out_for_delivery":
            prob += 0.20
            signals.append("Package out for delivery (high customer anticipation)")
        elif is_overdue:
            prob += 0.40
            signals.append("Package is past promised delivery window")

        # Sentiment history factor
        if customer_sentiment_history:
            neg_count = sum(1 for s in customer_sentiment_history if s.get("sentiment") in ("negative", "frustrated"))
            if neg_count > 0:
                prob += min(0.25, neg_count * 0.12)
                signals.append(f"Customer has history of {neg_count} negative/frustrated sentiment events")

        prob = min(0.99, max(0.05, round(prob, 2)))
        should_preempt = prob >= 0.60

        return {
            "inquiry_probability": prob,
            "should_preemptively_notify": should_preempt,
            "signals": signals,
            "recommended_cadence": "immediate_proactive_sms" if prob >= 0.75 else "next_regular_milestone"
        }

    def recommend_notification_timing(
        self,
        shipment_status: str,
        customer_sentiment: str,
        hours_until_eta: float,
        has_exception: bool
    ) -> Dict[str, Any]:
        """
        Determine optimal timestamp and urgency to deliver update notifications.
        """
        sentiment = (customer_sentiment or "neutral").lower()

        if has_exception:
            return {
                "action": "notify_immediately",
                "urgency": "critical" if sentiment in ("frustrated", "negative") else "high",
                "message_strategy": "lead_with_empathy_and_remedy" if sentiment in ("frustrated", "negative") else "informative_status_update"
            }

        if shipment_status == "out_for_delivery":
            return {
                "action": "notify_morning_window",
                "urgency": "medium",
                "message_strategy": "arrival_confirmation_and_safe_dropoff_instruction"
            }

        if hours_until_eta <= 4 and hours_until_eta > 0:
            return {
                "action": "notify_approaching",
                "urgency": "low",
                "message_strategy": "countdown_reassurance"
            }

        return {
            "action": "hold_until_next_milestone",
            "urgency": "none",
            "message_strategy": "silent_monitoring"
        }


# Singleton
_logistics_predictor_instance: Optional[LogisticsPredictor] = None

def get_logistics_predictor() -> LogisticsPredictor:
    global _logistics_predictor_instance
    if _logistics_predictor_instance is None:
        _logistics_predictor_instance = LogisticsPredictor()
    return _logistics_predictor_instance
