"""
Google ADK Tools for OpsPilot AI.
Wraps the central ToolRegistry into Google ADK FunctionTools.
Strictly defines schemas, descriptions, and type annotations for tool discovery and execution.
"""
from typing import Dict, Any, Optional, List
from google.adk.tools import FunctionTool
from app.integrations.registry import tool_registry
from app.integrations.paypal.adapter import paypal_adapter
from app.integrations.stripe.adapter import stripe_adapter
from app.integrations.jira.adapter import jira_adapter
from app.integrations.gmail.adapter import gmail_adapter
from app.integrations.slack.adapter import slack_adapter
from app.integrations.notion.adapter import notion_adapter
from app.schemas.tools import (
    PayPalPaymentResult, JiraTaskResult, GmailEmailResult,
    SlackNotifyResult, NotionRecordResult
)


def paypal_retrieve_payments(limit: int = 20, status_filter: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves customer payment transactions from PayPal to audit transaction statuses, identify failed payments, and detect aging pending transactions."""
    res: PayPalPaymentResult = paypal_adapter.retrieve_payments(limit=limit, status_filter=status_filter)
    return res.model_dump()


def stripe_retrieve_payments(limit: int = 20, status_filter: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves customer payment charges and payment intents from Stripe to audit transaction statuses and detect card declines or failed transfers."""
    res: PayPalPaymentResult = stripe_adapter.retrieve_payments(limit=limit, status_filter=status_filter)
    return res.model_dump()


def jira_create_task(summary: str, description: str, priority: str = "High", project_key: str = "FIN", payment_id: Optional[str] = None, simulate_failure: bool = False) -> Dict[str, Any]:
    """Creates operational or financial remediation task in Jira for unresolved or failed customer transactions."""
    res: JiraTaskResult = jira_adapter.create_task(
        summary=summary,
        description=description,
        priority=priority,
        project_key=project_key,
        payment_id=payment_id,
        simulate_failure=simulate_failure
    )
    return res.model_dump()


def gmail_send_customer_email(recipient: str, subject: str, body: str, payment_id: Optional[str] = None, customer_name: Optional[str] = None) -> Dict[str, Any]:
    """Sends customer communications regarding failed or pending payments with instructions to update billing details."""
    res: GmailEmailResult = gmail_adapter.send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        payment_id=payment_id,
        customer_name=customer_name
    )
    return res.model_dump()


def slack_notify_channel(channel: str = "#ops-alerts", message: str = "", severity: str = "HIGH", incident_id: Optional[str] = None) -> Dict[str, Any]:
    """Posts alert broadcast to the operations Slack channel regarding payment incidents, escalations, and workflow summaries."""
    res: SlackNotifyResult = slack_adapter.notify_channel(
        channel=channel,
        message=message,
        severity=severity,
        incident_id=incident_id
    )
    return res.model_dump()


def notion_update_record(page_title: str, content: Dict[str, Any], category: str = "Payment Operations") -> Dict[str, Any]:
    """Synchronizes operational outcome, reconciliation metrics, and actions taken into the corporate Notion database."""
    res: NotionRecordResult = notion_adapter.update_record(
        page_title=page_title,
        content=content,
        category=category
    )
    return res.model_dump()


# Create Google ADK FunctionTool instances
adk_paypal_tool = FunctionTool(paypal_retrieve_payments)
adk_stripe_tool = FunctionTool(stripe_retrieve_payments)
adk_jira_tool = FunctionTool(jira_create_task)
adk_gmail_tool = FunctionTool(gmail_send_customer_email, require_confirmation=True)
adk_slack_tool = FunctionTool(slack_notify_channel)
adk_notion_tool = FunctionTool(notion_update_record)

ADK_TOOLS = [
    adk_paypal_tool,
    adk_stripe_tool,
    adk_jira_tool,
    adk_gmail_tool,
    adk_slack_tool,
    adk_notion_tool
]

TOOL_FUNCTION_MAP = {
    "paypal_retrieve_payments": paypal_retrieve_payments,
    "stripe_retrieve_payments": stripe_retrieve_payments,
    "jira_create_task": jira_create_task,
    "gmail_send_customer_email": gmail_send_customer_email,
    "slack_notify_channel": slack_notify_channel,
    "notion_update_record": notion_update_record
}
