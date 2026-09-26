"""
API Routes for Human-In-The-Loop Approvals.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.approval import approval_service
from app.schemas.agent import ApprovalDecisionRequest

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])


@router.get("")
async def list_pending_approvals():
    """
    Returns all consequential actions currently waiting for human approval.
    """
    return approval_service.list_all_pending()


@router.post("/{action_id}/decision")
async def decide_approval(action_id: str, request: ApprovalDecisionRequest):
    """
    Records a human review decision (Approve or Reject) for a pending action.
    """
    result = approval_service.decide(
        action_id=action_id,
        approved=request.approved,
        user=request.approved_by,
        comment=request.comment
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Approval request {action_id} not found.")

    return {
        "success": True,
        "action_id": action_id,
        "status": result["status"],
        "decided_by": result["decided_by"]
    }
