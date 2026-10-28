"""
Logistics AI Evaluation Suite — V6 Logistics Benchmark
Academic / PhD-grade benchmark evaluation for autonomous logistics operations.

Evaluates:
1. ML ETA Prediction Accuracy (MAE & RMSE vs actual historical deliveries)
2. Anomaly & Exception Classification (Macro-F1, Precision, Recall)
3. Emotion-Gated Sentiment Adaptation (Empathy scoring and tone matching)
4. Autonomous ReAct Agent Tool Selection Precision
5. Fast-Path End-to-End Latency (<500ms benchmark)
"""

import time
import pytest
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error, f1_score, accuracy_score

from app.database import SessionLocal
from app.models.shipment import Shipment
from app.services.eta_predictor import get_eta_predictor
from app.services.delivery_exception import get_exception_classifier
from app.services.intent_router import classify_intent
from app.ai.logistics_agent import LogisticsAgent
from app.ai.agent import AgentContext


@pytest.mark.evaluation
class TestETAPredictionAccuracy:
    """Benchmark ML ETA accuracy on completed deliveries."""

    def test_mae_and_rmse_within_thresholds(self):
        db = SessionLocal()
        try:
            completed = (
                db.query(Shipment)
                .filter(
                    Shipment.status == "delivered",
                    Shipment.pickup_date != None,
                    Shipment.actual_delivery != None
                )
                .all()
            )
            assert len(completed) >= 5, "Need at least 5 completed deliveries for benchmark evaluation"

            eta_pred = get_eta_predictor()
            # Train the tenant-specific model on completed historical deliveries
            train_info = eta_pred.train_model(tenant_id=1, db=db)
            assert train_info["success"] is True, f"Model training failed: {train_info}"

            actual_hours_list = []
            predicted_hours_list = []

            for s in completed:
                actual_hours = (s.actual_delivery - s.pickup_date).total_seconds() / 3600.0
                pred = eta_pred.predict_eta(
                    tenant_id=s.tenant_id,
                    origin_lat=s.origin_lat,
                    origin_lng=s.origin_lng,
                    dest_lat=s.destination_lat,
                    dest_lng=s.destination_lng,
                    carrier=s.carrier,
                    service_type=s.service_type,
                    weight_kg=s.weight_kg,
                    pickup_time=s.pickup_date,
                    db=db
                )
                actual_hours_list.append(actual_hours)
                predicted_hours_list.append(pred["predicted_hours"])

            mae = mean_absolute_error(actual_hours_list, predicted_hours_list)
            rmse = np.sqrt(mean_squared_error(actual_hours_list, predicted_hours_list))

            print(f"\n--- Benchmark: ETA ML Prediction Accuracy ---")
            print(f"Sample Count: {len(actual_hours_list)}")
            print(f"Mean Absolute Error (MAE): {mae:.2f} hours")
            print(f"Root Mean Squared Error (RMSE): {rmse:.2f} hours")

            # Academic assertion: MAE must be under 8.0 hours on diverse national routes
            assert mae < 8.0, f"MAE {mae:.2f}h exceeded academic SLA threshold of 8.0h"
        finally:
            db.close()


@pytest.mark.evaluation
class TestExceptionClassificationPerformance:
    """Benchmark anomaly classification Macro-F1 across known ground-truth cases."""

    def test_exception_classification_f1(self):
        classifier = get_exception_classifier()

        test_cases = [
            ({"has_exception": True, "exception_type": "delay", "delivery_attempts": 0}, "DELAY"),
            ({"has_exception": True, "exception_type": "customs_hold", "delivery_attempts": 0}, "CUSTOMS_HOLD"),
            ({"has_exception": True, "exception_type": "damage", "delivery_attempts": 0}, "DAMAGE"),
            ({"has_exception": True, "exception_type": "address_issue", "delivery_attempts": 0}, "ADDRESS_ISSUE"),
            ({"has_exception": True, "exception_type": "lost", "delivery_attempts": 0}, "LOST"),
            ({"has_exception": False, "delivery_attempts": 3, "status": "in_transit"}, "FAILED_ATTEMPT"),
            ({"has_exception": False, "delivery_attempts": 0, "status": "in_transit"}, "NORMAL"),
            ({"has_exception": False, "delivery_attempts": 0, "status": "delivered"}, "NORMAL"),
        ]

        y_true = [c[1] for c in test_cases]
        y_pred = []

        for data, _ in test_cases:
            res = classifier.classify(data)
            y_pred.append(res["type"])

        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="macro")

        print(f"\n--- Benchmark: Exception Classification ---")
        print(f"Accuracy: {acc * 100:.1f}% | Macro-F1: {f1:.3f}")

        assert acc >= 0.85, f"Classification accuracy {acc:.2f} fell below 0.85"
        assert f1 >= 0.85, f"Classification Macro-F1 {f1:.2f} fell below 0.85"


@pytest.mark.evaluation
class TestEmotionGatedAdaptation:
    """Verify that response language adapts to customer sentiment."""

    def test_sentiment_tone_adaptation(self):
        classifier = get_exception_classifier()
        shipment_data = {
            "shipment_id": "SHP-BENCHMARK-001",
            "current_location_name": "Chicago Hub",
            "predicted_delivery": "2026-10-25",
            "delivery_attempts": 1
        }

        # 1. Frustrated/Negative customer
        frustrated_reply = classifier.generate_response(
            exception_type="DELAY",
            customer_sentiment="frustrated",
            shipment_data=shipment_data
        )
        empathy_markers = ["apologize", "sorry", "frustrating", "inconvenience", "priority"]
        found_empathy = any(marker in frustrated_reply.lower() for marker in empathy_markers)
        print("\n--- Frustrated Response Sample ---")
        print(frustrated_reply[:120], "...")
        assert found_empathy, "Frustrated customer response lacked empathy markers"

        # 2. Neutral customer
        neutral_reply = classifier.generate_response(
            exception_type="DELAY",
            customer_sentiment="neutral",
            shipment_data=shipment_data
        )
        print("\n--- Neutral Response Sample ---")
        print(neutral_reply[:120], "...")
        assert len(neutral_reply) <= len(frustrated_reply), "Neutral response should be concise and direct"


@pytest.mark.evaluation
class TestReActToolSelection:
    """Verify that the autonomous agent selects appropriate tools for diverse logistics intents."""

    def test_tool_selection_for_intents(self):
        db = SessionLocal()
        agent = LogisticsAgent()

        queries = [
            ("Where is shipment SHP-20261022-A1B2C?", "SHIPMENT_TRACKING", "track_shipment"),
            ("When will my delivery arrive?", "ETA_INQUIRY", "track_shipment"),
            ("How much does it cost to ship from New York to Chicago?", "RATE_INQUIRY", "calculate_shipping_rate"),
            ("My package was broken and damaged", "DELIVERY_EXCEPTION", "check_delivery_exception"),
        ]

        print("\n--- Benchmark: Autonomous Tool Selection ---")
        for text, expected_intent, expected_tool in queries:
            intent_res = classify_intent(text)
            assert intent_res["intent"] == expected_intent, f"Query '{text}' got intent {intent_res['intent']}"

            ctx = AgentContext(
                client_id="1",
                conversation_id="conv-eval",
                user_message=text,
                company_name="Apex Logistics"
            )
            result = agent.process_logistics_query(
                context=ctx,
                intent=intent_res["intent"],
                intent_data=intent_res["extracted_data"],
                db=db
            )
            tools_used = result.metadata.get("tools_used", [])
            print(f"Query: '{text[:35]}...' -> Intent: {intent_res['intent']} -> Tools: {tools_used}")
            assert expected_tool in tools_used, f"Expected tool '{expected_tool}' not in {tools_used}"

        db.close()


@pytest.mark.evaluation
class TestFastPathLatencyBenchmark:
    """Verify that Fast-Path tracking queries execute well under 500ms."""

    def test_fast_path_latency(self):
        db = SessionLocal()
        from app.ai.logistics_tools import LogisticsToolRegistry

        tools = LogisticsToolRegistry(db=db, tenant_id=1)
        latencies = []

        # Run 20 iterations
        for _ in range(20):
            t0 = time.perf_counter()
            res = tools._track_shipment("SHP-20261022-A1B2C")
            dt = (time.perf_counter() - t0) * 1000.0  # ms
            latencies.append(dt)

        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)

        print("\n--- Benchmark: Fast-Path Latency ---")
        print(f"Mean Latency: {avg_latency:.2f} ms")
        print(f"95th Percentile: {p95_latency:.2f} ms")

        db.close()
        # Fast path with SQLite WAL should be sub-50ms, easily beating 500ms SLA
        assert p95_latency < 500.0, f"95th percentile latency {p95_latency:.2f}ms exceeded 500ms"
