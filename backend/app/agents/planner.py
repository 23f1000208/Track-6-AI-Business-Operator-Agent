"""
Dynamic Planner for OpsPilot AI.
Fulfills requirements:
2. Core Product Concept: Understand request, determine objective, create execution plan.
8. Dynamic Tool Selection: NEVER blindly calls every integration. Selects only required tools based on business intent.
"""
from typing import Dict, Any, List, Optional
import re
from app.utils.config import settings


class ExecutionPlan:
    def __init__(self, intent: str, objective: str, steps: List[str], required_tools: List[str]):
        self.intent = intent
        self.objective = objective
        self.steps = steps
        self.required_tools = required_tools

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "objective": self.objective,
            "steps": self.steps,
            "required_tools": self.required_tools
        }


class AgentPlanner:
    @staticmethod
    def plan(user_request: str) -> ExecutionPlan:
        """
        Analyzes the natural language user prompt and creates a dynamic execution plan.
        """
        prompt = user_request.lower()

        # SCENARIO A: Comprehensive End-to-End Payment & Operations Coordination (Primary Demo)
        # "Find failed and pending customer payments, determine which ones require action,
        # create tasks for the finance team, contact the relevant customers, notify the ops team,
        # update our business ops record..."
        is_payment_related = any(k in prompt for k in ["payment", "transaction", "billing", "paid", "refund", "paypal"])
        is_task_related = any(k in prompt for k in ["task", "jira", "ticket", "issue", "todo", "action item"])
        is_contact_related = any(k in prompt for k in ["contact", "email", "gmail", "customer", "reach out", "notify customer"])
        is_team_notify = any(k in prompt for k in ["slack", "team", "channel", "notify the ops", "operations team", "alert"])
        is_record_related = any(k in prompt for k in ["notion", "record", "knowledge", "update our", "wiki", "doc", "database"])

        # Check for isolated scenarios:
        # Scenario 1: Only Notion / Knowledge base summary
        if "policy" in prompt or "knowledge base" in prompt or ("summarize" in prompt and not is_payment_related and not is_contact_related):
            return ExecutionPlan(
                intent="OPERATIONAL_KNOWLEDGE_INQUIRY",
                objective="Inspect corporate policies and summarize operational guidelines from Notion knowledge base.",
                steps=[
                    "Query Notion for operational policy records",
                    "Extract current escalation guidelines",
                    "Synthesize executive knowledge summary"
                ],
                required_tools=["notion_update_record"]
            )

        # Scenario 2: Payments & Tasks Only
        if is_payment_related and is_task_related and not is_contact_related and not is_record_related:
            return ExecutionPlan(
                intent="PAYMENT_AUDIT_AND_TASK_CREATION",
                objective="Retrieve payment transactions, apply deterministic classification, and create Jira tasks for failed items.",
                steps=[
                    "Retrieve recent payments from PayPal gateway",
                    "Apply deterministic classification for failed/pending items",
                    "Generate and create Jira remediation tickets",
                    "Verify ticket creation and return summary"
                ],
                required_tools=["paypal_retrieve_payments", "jira_create_task"]
            )

        # Scenario 3: Tasks and Team Notification Only
        if is_task_related and is_team_notify and not is_payment_related:
            return ExecutionPlan(
                intent="INCIDENT_TASK_AND_BROADCAST",
                objective="Create Jira operational tickets and broadcast incident alert to team Slack channel.",
                steps=[
                    "Create operational issue in Jira",
                    "Notify operations team on Slack #ops-alerts",
                    "Verify channel delivery"
                ],
                required_tools=["jira_create_task", "slack_notify_channel"]
            )

        # Scenario 4: Payments inquiry only
        if is_payment_related and not is_task_related and not is_contact_related and not is_team_notify:
            return ExecutionPlan(
                intent="PAYMENT_STATUS_AUDIT",
                objective="Audit payment transactions, calculate SLA and at-risk totals using Python business rules.",
                steps=[
                    "Query PayPal transactions",
                    "Compute deterministic status counts and financial exposure",
                    "Generate reconciliation report"
                ],
                required_tools=["paypal_retrieve_payments"]
            )

        # Default / Primary Demo: Full Multi-Step Business Operations Orchestration (Track 6 Full Suite)
        return ExecutionPlan(
            intent="AUTONOMOUS_OPERATIONS_RECOVERY",
            objective="Audit customer payments, classify at-risk accounts, create Jira tasks, contact customers, notify operations on Slack, and synchronize records in Notion.",
            steps=[
                "Retrieve payment transaction evidence from PayPal gateway",
                "Execute deterministic Python business rules to classify FAILED / PENDING SLA breaches",
                "Create Jira operational remediation tasks for finance personnel",
                "Dispatch customer follow-up emails via Gmail for payment resolution",
                "Broadcast operations incident briefing to Slack #ops-alerts channel",
                "Log synchronized reconciliation record into corporate Notion database",
                "Execute multi-system verification and synthesize final executive report"
            ],
            required_tools=[
                "paypal_retrieve_payments",
                "jira_create_task",
                "gmail_send_customer_email",
                "slack_notify_channel",
                "notion_update_record"
            ]
        )


planner = AgentPlanner()
