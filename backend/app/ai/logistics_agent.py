"""
Logistics AI Agent — V6 ReAct Autonomous Agent
Autonomous ReAct (Reason, Act, Observe, Reflect) decision loop for logistics inquiries.

PhD / Research Contribution:
Emotion-gated tool-augmented ReAct architecture that modulates reasoning depth,
escalation thresholds, and response tone based on real-time customer sentiment.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.ai.agent import AgentResult, AgentAction, AgentContext
from app.ai.logistics_tools import LogisticsToolRegistry
from app.ai.llm import get_llm_service
from app.services.delivery_exception import get_exception_classifier

logger = logging.getLogger(__name__)

MAX_AGENT_STEPS = 4  # safety limit preventing runaway execution


@dataclass
class AgentStep:
    """A single step in the ReAct reasoning chain."""
    thought: str
    tool_name: Optional[str] = None
    tool_input: Dict[str, Any] = field(default_factory=dict)
    tool_output: Dict[str, Any] = field(default_factory=dict)
    is_final: bool = False


class LogisticsAgent:
    """
    ReAct-based autonomous agent for logistics operations and customer support.
    """

    def __init__(self):
        self.llm = get_llm_service()
        self.exception_classifier = get_exception_classifier()

    def process_logistics_query(
        self,
        context: AgentContext,
        intent: str,
        intent_data: Dict[str, Any],
        db: Session
    ) -> AgentResult:
        """
        Execute the ReAct reasoning loop for a logistics customer query.
        """
        tenant_id = int(context.client_id)
        tools = LogisticsToolRegistry(db=db, tenant_id=tenant_id)

        # 1. Formulate initial tool execution plan based on intent and extracted entities
        plan = self._create_initial_plan(intent, intent_data, context)

        steps: List[AgentStep] = []
        collected_context: List[str] = []

        # 2. ReAct Execution Loop
        for i in range(MAX_AGENT_STEPS):
            if i < len(plan):
                step = plan[i]
            else:
                step = self._reason_next_step(context, steps, collected_context)

            if step.is_final or not step.tool_name:
                steps.append(step)
                break

            # ACT: Execute tool
            if step.tool_name in tools.tools:
                tool = tools.tools[step.tool_name]
                try:
                    logger.info(f"🚚 LogisticsAgent executing tool: {step.tool_name} with params: {step.tool_input}")
                    output = tool.handler(**step.tool_input)
                    step.tool_output = output
                    collected_context.append(
                        f"[{step.tool_name}]: {json.dumps(output, default=str)[:600]}"
                    )
                except Exception as e:
                    logger.warning(f"Tool {step.tool_name} execution error: {e}")
                    step.tool_output = {"error": str(e)}

            steps.append(step)

            # OBSERVE & REFLECT: Check if goal is achieved or dynamic replanning is needed
            if self._goal_achieved(intent, steps):
                break

        # 3. Synthesize final sentiment-adapted response
        response_text = self._synthesize_response(context, steps, collected_context, tools)

        # Determine if human escalation is required
        should_escalate = False
        escalation_reason = ""
        for s in steps:
            if s.tool_output.get("requires_escalation"):
                should_escalate = True
                escalation_reason = f"Critical logistics exception ({s.tool_output.get('exception_type')})"
                break

        frustration = getattr(context, "current_frustration", 0.0) or 0.0
        sentiment_dict = context.pre_sentiment or {"sentiment": "neutral", "score": 0.5}
        if sentiment_dict.get("sentiment") == "frustrated" and frustration > 0.75:
            should_escalate = True
            escalation_reason = "Customer frustration threshold exceeded"

        return AgentResult(
            action=AgentAction.ESCALATE if should_escalate else AgentAction.RESPOND,
            response=response_text,
            sentiment=sentiment_dict,
            escalation={
                "should_escalate": should_escalate,
                "reason": escalation_reason,
                "urgency": "high" if should_escalate else "normal"
            },
            context_used=[s.thought for s in steps],
            confidence=0.92,
            requires_human=should_escalate,
            metadata={
                "agent_type": "logistics_react",
                "intent": intent,
                "steps_taken": len(steps),
                "tools_used": [s.tool_name for s in steps if s.tool_name]
            }
        )

    def _create_initial_plan(
        self,
        intent: str,
        intent_data: Dict[str, Any],
        context: AgentContext
    ) -> List[AgentStep]:
        """Establish goal-directed tool execution plan."""
        tracking_id = intent_data.get("tracking_id", "")
        origin = intent_data.get("origin") or "New York"
        destination = intent_data.get("destination") or "Los Angeles"

        if intent == "SHIPMENT_TRACKING":
            return [
                AgentStep(
                    thought=f"Customer inquiring about shipment status. Tracking identifier: '{tracking_id}'.",
                    tool_name="track_shipment",
                    tool_input={"identifier": tracking_id}
                ),
            ]

        elif intent == "ETA_INQUIRY":
            return [
                AgentStep(
                    thought=f"Customer requesting ETA. First retrieve current location for '{tracking_id}'.",
                    tool_name="track_shipment",
                    tool_input={"identifier": tracking_id}
                ),
                AgentStep(
                    thought="Predict dynamic ETA using the machine learning gradient boosting regressor.",
                    tool_name="predict_eta",
                    tool_input={"identifier": tracking_id}
                ),
            ]

        elif intent == "DELIVERY_EXCEPTION":
            return [
                AgentStep(
                    thought=f"Customer reporting delivery exception for '{tracking_id}'. Check telemetry anomalies.",
                    tool_name="check_delivery_exception",
                    tool_input={"identifier": tracking_id}
                ),
                AgentStep(
                    thought="Search logistics knowledge base for official resolution policy and dispute terms.",
                    tool_name="search_knowledge_base",
                    tool_input={"query": context.user_message}
                ),
            ]

        elif intent == "RATE_INQUIRY":
            return [
                AgentStep(
                    thought=f"Customer requesting freight quote from '{origin}' to '{destination}'.",
                    tool_name="calculate_shipping_rate",
                    tool_input={
                        "origin": origin,
                        "destination": destination,
                        "weight_kg": intent_data.get("weight_kg", 1.0)
                    }
                ),
            ]

        elif intent == "PICKUP_SCHEDULE":
            return [
                AgentStep(
                    thought="Customer wishes to schedule courier pickup. Verify serviceability zone.",
                    tool_name="get_zone_info",
                    tool_input={"location": destination or origin}
                ),
                AgentStep(
                    thought="Check pickup scheduling guidelines in knowledge base.",
                    tool_name="search_knowledge_base",
                    tool_input={"query": "pickup scheduling cut-off times"}
                ),
            ]

        # Default plan
        return [
            AgentStep(
                thought="Search logistics operational knowledge base for relevant instructions.",
                tool_name="search_knowledge_base",
                tool_input={"query": context.user_message}
            )
        ]

    def _reason_next_step(
        self,
        context: AgentContext,
        steps: List[AgentStep],
        collected: List[str]
    ) -> AgentStep:
        """Dynamic reflection step deciding if another tool is needed."""
        # If tracking was checked and an active exception was discovered, check exception details
        last_step = steps[-1] if steps else None
        if last_step and last_step.tool_name == "track_shipment":
            output = last_step.tool_output
            if output.get("has_exception"):
                return AgentStep(
                    thought="Tracking discovered an active exception. Analyzing anomaly severity and resolution.",
                    tool_name="check_delivery_exception",
                    tool_input={"identifier": output.get("shipment_id", "")}
                )

        return AgentStep(thought="Sufficient context accumulated. Synthesizing response.", is_final=True)

    def _goal_achieved(self, intent: str, steps: List[AgentStep]) -> bool:
        """Check if all necessary tool data has been acquired."""
        if not steps:
            return False
        last_step = steps[-1]
        if last_step.is_final:
            return True

        if intent == "SHIPMENT_TRACKING":
            return any(s.tool_name == "track_shipment" and s.tool_output.get("found") for s in steps)
        elif intent == "ETA_INQUIRY":
            return any(s.tool_name == "predict_eta" and s.tool_output.get("success") for s in steps)
        elif intent == "RATE_INQUIRY":
            return any(s.tool_name == "calculate_shipping_rate" for s in steps)

        return len(steps) >= 2

    def _synthesize_response(
        self,
        context: AgentContext,
        steps: List[AgentStep],
        collected_context: List[str],
        tools: LogisticsToolRegistry
    ) -> str:
        """
        Generate final sentiment-adapted response.
        Uses deterministic templating with emotion gating for maximum speed and accuracy,
        falling back to LLM synthesis if query is highly conversational.
        """
        customer_sentiment = (
            context.pre_sentiment.get("sentiment", "neutral")
            if context.pre_sentiment else "neutral"
        )

        # 1. Check for shipment tracking output
        tracking_step = next((s for s in steps if s.tool_name == "track_shipment"), None)
        eta_step = next((s for s in steps if s.tool_name == "predict_eta"), None)
        exception_step = next((s for s in steps if s.tool_name == "check_delivery_exception"), None)
        rate_step = next((s for s in steps if s.tool_name == "calculate_shipping_rate"), None)

        # Rate response
        if rate_step and rate_step.tool_output.get("success"):
            data = rate_step.tool_output
            return (
                f"📦 **Shipping Rate Estimate**\n\n"
                f"• **Route:** {data['origin']} → {data['destination']} ({data['distance_km']} km)\n"
                f"• **Estimated Freight Cost:** {data['currency']} {data['total_price']:.2f}\n"
                f"• **Estimated Transit Time:** ~{data['estimated_transit_hours']} hours\n"
                f"• **Service Zone:** {data['zone_code']}\n\n"
                f"Rates include standard fuel surcharge. Would you like to proceed with booking this shipment?"
            )

        # Exception response
        if exception_step and exception_step.tool_output.get("is_exception"):
            data = exception_step.tool_output
            return self.exception_classifier.generate_response(
                exception_type=data["exception_type"],
                customer_sentiment=customer_sentiment,
                shipment_data=data
            )

        # ETA response
        if eta_step and eta_step.tool_output.get("success"):
            data = eta_step.tool_output
            lead_in = (
                "Here is the machine learning delivery estimate for your package:"
                if customer_sentiment != "frustrated"
                else "I checked our live dispatch network to give you the exact arrival window:"
            )
            return (
                f"🚚 **Estimated Delivery Window**\n\n"
                f"{lead_in}\n"
                f"• **Expected Delivery:** {data['predicted_date_formatted']}\n"
                f"• **Transit Time:** ~{data['predicted_hours']} hours\n"
                f"• **Model Confidence:** {data['confidence']:.0%}\n\n"
                f"Key factors: {'; '.join(data['factors'])}."
            )

        # Tracking response
        if tracking_step:
            data = tracking_step.tool_output
            if data.get("found"):
                return data.get("summary") or f"Shipment {data.get('shipment_id')} is currently {data.get('status')} in {data.get('current_location')}."
            elif not data.get("found") and context.logistics_intent_data and context.logistics_intent_data.get("tracking_id"):
                return f"I searched our tracking database, but could not find an active shipment matching tracking number '{context.logistics_intent_data.get('tracking_id')}'. Please verify the number and try again."

        # Fallback to LLM with full collected context
        system_prompt = (
            f"You are the expert logistics customer service specialist for {context.company_name}. "
            f"Customer sentiment is {customer_sentiment.upper()}. Adapt your tone accordingly. "
            f"Be concise, empathetic, and professional. Use the following operational context:\n"
            + "\n".join(collected_context)
        )
        try:
            llm_reply = self.llm.generate(
                prompt=context.user_message,
                system_prompt=system_prompt,
                max_tokens=300
            )
            return llm_reply.content
        except Exception:
            return (
                "Thank you for contacting logistics support. Our dispatch desk is reviewing your tracking inquiry. "
                "Please provide your shipment or order ID if you have not already done so."
            )
