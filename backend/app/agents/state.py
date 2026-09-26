"""
Structured Agent State for OpsPilot AI.
Fulfills requirements 13 (Agent State) and 5 (Agent Loop).
Maintains full execution state across multi-step workflows.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.schemas.payments import PaymentRecord, PaymentClassificationSummary


class AgentStepData(BaseModel):
    step_number: int
    action: str  # UNDERSTAND, PLAN, TOOL_SELECT, EXECUTE, OBSERVE, DECIDE, VERIFY, SUMMARIZE
    tool: Optional[str] = None
    status: str = "COMPLETED"  # STARTED, COMPLETED, FAILED, SKIPPED, PAUSED_APPROVAL
    result_summary: str
    structured_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentState(BaseModel):
    run_id: str
    user_request: str
    intent: Optional[str] = None
    objective: Optional[str] = None
    plan: List[str] = Field(default_factory=list)
    current_step: int = 0
    max_steps: int = 25
    is_demo_mode: bool = True
    simulate_failure: bool = False

    # Intermediate Tool Results & Ground Truth
    retrieved_payments: List[PaymentRecord] = Field(default_factory=list)
    classification_summary: Optional[PaymentClassificationSummary] = None

    # Step History & Actions
    steps: List[AgentStepData] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    decisions: List[str] = Field(default_factory=list)

    # Actions Execution
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list)
    completed_actions: List[Dict[str, Any]] = Field(default_factory=list)
    failed_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Human Approvals
    pending_approvals: List[Dict[str, Any]] = Field(default_factory=list)
    approved_actions: List[Dict[str, Any]] = Field(default_factory=list)
    rejected_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Verification & Metrics
    verification_results: List[str] = Field(default_factory=list)
    workflow_metrics: Dict[str, Any] = Field(default_factory=dict)
    final_result: Optional[Dict[str, Any]] = None
    status: str = "INITIALIZED"  # INITIALIZED, RUNNING, PENDING_APPROVAL, COMPLETED, FAILED, STOPPED
    error_message: Optional[str] = None

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def add_step(self, action: str, result_summary: str, tool: Optional[str] = None, details: Optional[Dict[str, Any]] = None, status: str = "COMPLETED") -> AgentStepData:
        self.current_step += 1
        step_data = AgentStepData(
            step_number=self.current_step,
            action=action,
            tool=tool,
            status=status,
            result_summary=result_summary,
            structured_details=details or {},
            timestamp=datetime.now(timezone.utc)
        )
        self.steps.append(step_data)
        return step_data
