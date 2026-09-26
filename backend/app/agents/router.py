"""
Dynamic Next-Action Router for OpsPilot AI.
Fulfills requirements:
5. Agent Loop: Decides next action dynamically from current state rather than a rigid linear script.
24. Partial Failure Handling: Detects intermediate errors, preserves state, and stops downstream cascades safely.
"""
from typing import Dict, Any, Optional, Tuple
from app.agents.state import AgentState


class RoutingDecision:
    def __init__(self, action_type: str, tool_name: Optional[str] = None, reason: str = "", payload: Optional[Dict[str, Any]] = None):
        self.action_type = action_type  # CALL_TOOL, REQUEST_APPROVAL, VERIFY_AND_FINISH, STOP_ON_FAILURE
        self.tool_name = tool_name
        self.reason = reason
        self.payload = payload or {}


class AgentRouter:
    @staticmethod
    def decide_next_action(state: AgentState) -> RoutingDecision:
        """
        Dynamically examines state and intermediate results to determine the next agent step.
        """
        plan_tools = state.plan

        # 1. Check if an unrecoverable failure occurred in a prerequisite tool
        if state.failed_actions:
            failed_tool_names = [f.get("tool") for f in state.failed_actions]
            if "jira" in failed_tool_names or "jira_create_task" in failed_tool_names:
                return RoutingDecision(
                    action_type="STOP_ON_FAILURE",
                    reason="Jira task creation failed. Downstream customer outreach (Gmail) and Slack notifications were not executed because Jira task tracking is a prerequisite."
                )

        # 2. Check if PayPal data has been retrieved (if PayPal is in the plan)
        if "paypal_retrieve_payments" in plan_tools and "paypal_retrieve_payments" not in state.tool_results:
            return RoutingDecision(
                action_type="CALL_TOOL",
                tool_name="paypal_retrieve_payments",
                reason="Payment transaction data is required to identify at-risk and failed customer accounts."
            )

        # 3. Check if payments have been classified by deterministic Python business rules
        if state.retrieved_payments and not state.classification_summary:
            return RoutingDecision(
                action_type="APPLY_BUSINESS_RULES",
                reason="Execute deterministic Python business rules to calculate SLA aging and classify payments into COMPLETED, PENDING, and FAILED."
            )

        # 4. Check if Jira task creation is required
        if "jira_create_task" in plan_tools and "jira_create_task" not in state.tool_results:
            if state.classification_summary and state.classification_summary.require_attention > 0:
                return RoutingDecision(
                    action_type="CALL_TOOL",
                    tool_name="jira_create_task",
                    reason=f"Found {state.classification_summary.require_attention} payments requiring action. Creating operational remediation tasks in Jira."
                )
            elif not state.retrieved_payments and "jira_create_task" in plan_tools:
                return RoutingDecision(
                    action_type="CALL_TOOL",
                    tool_name="jira_create_task",
                    reason="Creating operational task in Jira as requested."
                )

        # 5. Check if Gmail customer emails need to be sent
        if "gmail_send_customer_email" in plan_tools and "gmail_send_customer_email" not in state.tool_results:
            if state.classification_summary and state.classification_summary.require_attention > 0:
                # If human approval is required and not yet approved, pause for approval
                if state.pending_approvals:
                    return RoutingDecision(
                        action_type="REQUEST_APPROVAL",
                        reason="Customer outreach emails prepared. Pausing execution for human operator review and sign-off."
                    )
                return RoutingDecision(
                    action_type="CALL_TOOL",
                    tool_name="gmail_send_customer_email",
                    reason="Notifying affected customers via Gmail with clear resolution steps."
                )

        # 6. Check if Slack ops alert needs to be dispatched
        if "slack_notify_channel" in plan_tools and "slack_notify_channel" not in state.tool_results:
            return RoutingDecision(
                action_type="CALL_TOOL",
                tool_name="slack_notify_channel",
                reason="Broadcasting incident summary and action report to #ops-alerts Slack channel."
            )

        # 7. Check if Notion operational database record needs updating
        if "notion_update_record" in plan_tools and "notion_update_record" not in state.tool_results:
            return RoutingDecision(
                action_type="CALL_TOOL",
                tool_name="notion_update_record",
                reason="Synchronizing business execution audit and reconciliation metrics into Notion database."
            )

        # 8. All planned tools executed -> Verify and synthesize outcome
        return RoutingDecision(
            action_type="VERIFY_AND_FINISH",
            reason="All planned operational actions completed. Executing verification audit and preparing executive summary."
        )


router = AgentRouter()
