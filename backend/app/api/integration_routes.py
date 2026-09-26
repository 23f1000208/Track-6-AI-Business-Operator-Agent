"""
API Routes for Inspecting Swytchcode Integrations.
Fulfills requirements:
33. Integration Status: PayPal, Gmail, Slack, Jira, Notion.
Clearly shows CONNECTED or DEMO MODE. Never falsely shows CONNECTED.
"""
from fastapi import APIRouter, Response
from typing import List
from app.schemas.agent import IntegrationStatusResponse
from app.integrations.paypal.adapter import paypal_adapter
from app.integrations.stripe.adapter import stripe_adapter
from app.integrations.gmail.adapter import gmail_adapter
from app.integrations.slack.adapter import slack_adapter
from app.integrations.jira.adapter import jira_adapter
from app.integrations.notion.adapter import notion_adapter

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])


@router.get("", response_model=List[IntegrationStatusResponse])
async def list_integrations(response: Response):
    """
    Returns current health, live vs demo status, and capabilities for all Track 6 integrations.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return [
        IntegrationStatusResponse(
            name="Stripe",
            service_id="stripe",
            status=stripe_adapter.get_status(),
            is_live=stripe_adapter.get_status() == "CONNECTED",
            capabilities=stripe_adapter.get_capabilities(),
            description="Payment gateway for customer charge auditing, dispute identification, and balance reconciliation."
        ),
        IntegrationStatusResponse(
            name="PayPal",
            service_id="paypal",
            status=paypal_adapter.get_status(),
            is_live=paypal_adapter.get_status() == "CONNECTED",
            capabilities=paypal_adapter.get_capabilities(),
            description="Payment gateway for transaction auditing, payment status inspection, and billing disputes."
        ),
        IntegrationStatusResponse(
            name="Gmail",
            service_id="gmail",
            status=gmail_adapter.get_status(),
            is_live=gmail_adapter.get_status() == "CONNECTED",
            capabilities=gmail_adapter.get_capabilities(),
            description="Customer communications for dispatching payment updates and billing reminders."
        ),
        IntegrationStatusResponse(
            name="Slack",
            service_id="slack",
            status=slack_adapter.get_status(),
            is_live=slack_adapter.get_status() == "CONNECTED",
            capabilities=slack_adapter.get_capabilities(),
            description="Team collaboration for real-time operations alerts, incidents, and workflow notices."
        ),
        IntegrationStatusResponse(
            name="Jira",
            service_id="jira",
            status=jira_adapter.get_status(),
            is_live=jira_adapter.get_status() == "CONNECTED",
            capabilities=jira_adapter.get_capabilities(),
            description="Issue tracking for finance operations remediation tasks and assignee coordination."
        ),
        IntegrationStatusResponse(
            name="Notion",
            service_id="notion",
            status=notion_adapter.get_status(),
            is_live=notion_adapter.get_status() == "CONNECTED",
            capabilities=notion_adapter.get_capabilities(),
            description="Business knowledge database for persisting operations logs, audit records, and reconciliation metrics."
        ),
    ]
