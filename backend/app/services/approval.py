"""
Human-In-The-Loop Approval Service.
Fulfills requirement 21:
Consequential actions (customer emails, high-severity escalations) can be reviewed and approved by human operators.
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone


class ApprovalService:
    def __init__(self):
        # In-memory registry of pending approvals: action_id -> approval_data
        self._approvals: Dict[str, Dict[str, Any]] = {}

    def create_approval_request(
        self,
        run_id: str,
        action_type: str,
        target: str,
        description: str,
        impact: str,
        risk_level: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a new pending human approval request.
        """
        action_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        approval = {
            "action_id": action_id,
            "run_id": run_id,
            "action_type": action_type,
            "target": target,
            "description": description,
            "impact": impact,
            "risk_level": risk_level,
            "evidence": evidence,
            "status": "PENDING",
            "created_at": datetime.now(timezone.utc),
            "decided_at": None,
            "decided_by": None,
            "comment": None
        }
        self._approvals[action_id] = approval
        return approval

    def get_approval(self, action_id: str) -> Optional[Dict[str, Any]]:
        return self._approvals.get(action_id)

    def list_pending_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        return [
            app for app in self._approvals.values()
            if app["run_id"] == run_id and app["status"] == "PENDING"
        ]

    def list_all_pending(self) -> List[Dict[str, Any]]:
        return [app for app in self._approvals.values() if app["status"] == "PENDING"]

    def decide(self, action_id: str, approved: bool, user: str = "business_operator", comment: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Records human operator decision (APPROVED or REJECTED).
        """
        if action_id not in self._approvals:
            return None

        app = self._approvals[action_id]
        app["status"] = "APPROVED" if approved else "REJECTED"
        app["decided_at"] = datetime.now(timezone.utc)
        app["decided_by"] = user
        app["comment"] = comment
        return app


approval_service = ApprovalService()
