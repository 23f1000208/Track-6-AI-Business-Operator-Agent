"""
Strongly-typed schemas for Google ADK tools and Swytchcode integrations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.payments import PaymentRecord, PaymentStatus


# ==========================================
# PAYPAL TOOL SCHEMAS
# ==========================================
class PayPalRetrievePaymentsInput(BaseModel):
    limit: int = Field(default=20, ge=1, le=100, description="Max number of transactions to retrieve")
    status_filter: Optional[str] = Field(default=None, description="Optional filter: FAILED, PENDING, COMPLETED")


class PayPalPaymentResult(BaseModel):
    success: bool
    total_count: int
    payments: List[PaymentRecord]
    raw_evidence_hash: str
    message: str


# ==========================================
# JIRA TOOL SCHEMAS
# ==========================================
class JiraCreateTaskInput(BaseModel):
    project_key: str = Field(default="FIN", description="Target Jira project key e.g. FIN")
    summary: str = Field(..., description="Concise task title")
    description: str = Field(..., description="Detailed description of the issue and action items")
    priority: str = Field(default="High", description="Priority: Critical, High, Medium, Low")
    payment_id: Optional[str] = Field(default=None, description="Associated payment ID for traceability")
    assignee: Optional[str] = Field(default="finance-ops@company.internal", description="Task assignee")


class JiraTaskResult(BaseModel):
    success: bool
    issue_key: str
    issue_id: str
    summary: str
    priority: str
    status: str
    link: str


# ==========================================
# GMAIL TOOL SCHEMAS
# ==========================================
class GmailSendEmailInput(BaseModel):
    recipient: str = Field(..., description="Target customer email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content in plain text or markdown")
    payment_id: Optional[str] = Field(default=None, description="Associated payment ID for verification")
    customer_name: Optional[str] = Field(default=None, description="Customer recipient name")


class GmailEmailResult(BaseModel):
    success: bool
    message_id: str
    recipient: str
    subject: str
    status: str
    sent_timestamp: str


# ==========================================
# SLACK TOOL SCHEMAS
# ==========================================
class SlackNotifyChannelInput(BaseModel):
    channel: str = Field(default="#ops-alerts", description="Target Slack channel")
    message: str = Field(..., description="Formatted message to post in channel")
    severity: str = Field(default="HIGH", description="Severity tag: INFO, WARNING, HIGH, CRITICAL")
    incident_id: Optional[str] = Field(default=None, description="Optional incident or run reference ID")


class SlackNotifyResult(BaseModel):
    success: bool
    channel: str
    timestamp: str
    message_ts: str
    status: str


# ==========================================
# NOTION TOOL SCHEMAS
# ==========================================
class NotionUpdateRecordInput(BaseModel):
    page_title: str = Field(..., description="Page or entry title in Notion database")
    category: str = Field(default="Payment Operations", description="Category of the business record")
    content: Dict[str, Any] = Field(..., description="Structured metrics, actions taken, and summary table")


class NotionRecordResult(BaseModel):
    success: bool
    page_id: str
    url: str
    title: str
    updated_at: str
    status: str
