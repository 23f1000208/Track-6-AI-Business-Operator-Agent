"""
Pydantic schemas for Agent requests, responses, execution steps, and executive summaries.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.payments import PaymentClassificationSummary


class AgentRunRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Natural language business request from user")
    require_approval: bool = Field(default=False, description="Whether consequential actions must pause for user approval")
    demo_mode: bool = Field(default=True, description="Whether to run in Demo Mode")
    simulate_failure: bool = Field(default=False, description="Simulate partial failure (e.g. Jira down)")


class AgentStepResponse(BaseModel):
    step_number: int
    action: str
    tool: Optional[str] = None
    status: str
    result_summary: str
    structured_details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ToolCallResponse(BaseModel):
    tool_name: str
    input_summary: str
    output_summary: str
    status: str
    latency_ms: float
    timestamp: datetime


class ApprovalItemResponse(BaseModel):
    action_id: str
    action_type: str
    description: str
    target: str
    impact: str
    risk_level: str
    evidence: Dict[str, Any]
    status: str
    created_at: datetime


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    approved_by: str = "business_user"
    comment: Optional[str] = None


class ExecutiveSummary(BaseModel):
    title: str = "OPERATIONS RUN COMPLETED"
    user_request: str
    payments_analyzed: int
    require_attention: int
    failed_count: int
    pending_count: int
    total_at_risk_amount: float
    actions_taken: List[str]
    actions_failed: List[str]
    verification: List[str]
    exceptions: List[str]
    workflow_metrics: Dict[str, Any]
    next_steps: List[str]


class AgentRunResponse(BaseModel):
    run_id: str
    user_request: str
    status: str
    intent: Optional[str] = None
    objective: Optional[str] = None
    is_demo_mode: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    steps: List[AgentStepResponse] = []
    tool_calls: List[ToolCallResponse] = []
    pending_approvals: List[ApprovalItemResponse] = []
    classification_summary: Optional[PaymentClassificationSummary] = None
    final_result: Optional[ExecutiveSummary] = None
    error_message: Optional[str] = None


class DashboardStats(BaseModel):
    active_workflows: int
    pending_actions: int
    completed_today: int
    failed_actions: int
    total_recovered_or_tracked: float
    integrations_active: int
    recent_runs: List[Dict[str, Any]]


class IntegrationStatusResponse(BaseModel):
    name: str
    service_id: str
    status: str  # CONNECTED, DEMO MODE, ERROR, NOT CONFIGURED
    is_live: bool
    capabilities: List[str]
    description: str
