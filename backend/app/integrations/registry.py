"""
Central Tool Registry for OpsPilot AI.
Fulfills requirement 9:
Every tool is registered with its description, schemas, risk level, timeout, and approval requirements.
Exposes tools to Google ADK.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from app.integrations.paypal.adapter import paypal_adapter
from app.integrations.stripe.adapter import stripe_adapter
from app.integrations.gmail.adapter import gmail_adapter
from app.integrations.slack.adapter import slack_adapter
from app.integrations.jira.adapter import jira_adapter
from app.integrations.notion.adapter import notion_adapter
from app.schemas.tools import (
    PayPalRetrievePaymentsInput, PayPalPaymentResult,
    JiraCreateTaskInput, JiraTaskResult,
    GmailSendEmailInput, GmailEmailResult,
    SlackNotifyChannelInput, SlackNotifyResult,
    NotionUpdateRecordInput, NotionRecordResult
)


@dataclass
class ToolDefinition:
    name: str
    description: str
    integration: str
    input_schema: Any
    output_schema: Any
    permission_level: str  # READ, WRITE, ADMIN
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    timeout_seconds: int = 30
    retry_policy: int = 3
    requires_approval: bool = False
    handler: Any = None


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def _register_default_tools(self):
        # 1. PayPal: Retrieve Payments
        self.register(ToolDefinition(
            name="paypal_retrieve_payments",
            description="Retrieves customer payment transactions from PayPal to audit transaction statuses, identify failed payments, and detect aging pending transactions.",
            integration="PayPal",
            input_schema=PayPalRetrievePaymentsInput,
            output_schema=PayPalPaymentResult,
            permission_level="READ",
            risk_level="LOW",
            requires_approval=False,
            handler=lambda limit=20, status_filter=None: paypal_adapter.retrieve_payments(limit, status_filter)
        ))

        # 1b. Stripe: Retrieve Charges & Payment Intents
        self.register(ToolDefinition(
            name="stripe_retrieve_payments",
            description="Retrieves customer payment charges and payment intents from Stripe to audit transaction statuses and detect card declines or failed transfers.",
            integration="Stripe",
            input_schema=PayPalRetrievePaymentsInput,
            output_schema=PayPalPaymentResult,
            permission_level="READ",
            risk_level="LOW",
            requires_approval=False,
            handler=lambda limit=20, status_filter=None: stripe_adapter.retrieve_payments(limit, status_filter)
        ))

        # 2. Jira: Create Task
        self.register(ToolDefinition(
            name="jira_create_task",
            description="Creates operational or financial remediation task in Jira for unresolved or failed customer transactions.",
            integration="Jira",
            input_schema=JiraCreateTaskInput,
            output_schema=JiraTaskResult,
            permission_level="WRITE",
            risk_level="MEDIUM",
            requires_approval=False,
            handler=lambda summary, description, priority="High", project_key="FIN", payment_id=None, assignee=None, simulate_failure=False: jira_adapter.create_task(
                summary=summary,
                description=description,
                priority=priority,
                project_key=project_key,
                payment_id=payment_id,
                simulate_failure=simulate_failure
            )
        ))

        # 3. Gmail: Send Customer Email
        self.register(ToolDefinition(
            name="gmail_send_customer_email",
            description="Sends customer communications regarding failed or pending payments with instructions to update billing details.",
            integration="Gmail",
            input_schema=GmailSendEmailInput,
            output_schema=GmailEmailResult,
            permission_level="WRITE",
            risk_level="HIGH",
            requires_approval=True,  # Consequential external action
            handler=lambda recipient, subject, body, payment_id=None, customer_name=None: gmail_adapter.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                payment_id=payment_id,
                customer_name=customer_name
            )
        ))

        # 4. Slack: Notify Channel
        self.register(ToolDefinition(
            name="slack_notify_channel",
            description="Posts alert broadcast to the operations Slack channel regarding payment incidents, escalations, and workflow summaries.",
            integration="Slack",
            input_schema=SlackNotifyChannelInput,
            output_schema=SlackNotifyResult,
            permission_level="WRITE",
            risk_level="MEDIUM",
            requires_approval=False,
            handler=lambda channel="#ops-alerts", message="", severity="HIGH", incident_id=None: slack_adapter.notify_channel(
                channel=channel,
                message=message,
                severity=severity,
                incident_id=incident_id
            )
        ))

        # 5. Notion: Update Business Record
        self.register(ToolDefinition(
            name="notion_update_record",
            description="Synchronizes operational outcome, reconciliation metrics, and actions taken into the corporate Notion database.",
            integration="Notion",
            input_schema=NotionUpdateRecordInput,
            output_schema=NotionRecordResult,
            permission_level="WRITE",
            risk_level="LOW",
            requires_approval=False,
            handler=lambda page_title, content, category="Payment Operations": notion_adapter.update_record(
                page_title=page_title,
                content=content,
                category=category
            )
        ))


tool_registry = ToolRegistry()
