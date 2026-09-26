"""
API Routes for Agent Execution, Status, and Real-time SSE Streaming.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import json
import asyncio
from app.agents.agent import agent
from app.schemas.agent import AgentRunRequest, AgentRunResponse, AgentStepResponse
from app.services.audit import audit_service

router = APIRouter(prefix="/api/agent", tags=["Agent"])

# In-memory store for runs
ACTIVE_RUNS: Dict[str, Dict[str, Any]] = {}


@router.post("/run")
async def run_agent(request: AgentRunRequest):
    """
    Executes the OpsPilot AI agent workflow end-to-end and returns the completed state.
    """
    last_event = None
    all_steps = []
    run_id = None

    async for event in agent.run(
        user_request=request.prompt,
        require_approval=request.require_approval,
        demo_mode=request.demo_mode,
        simulate_failure=request.simulate_failure
    ):
        if event["type"] == "RUN_STARTED":
            run_id = event["run_id"]
        elif event["type"] == "STEP_UPDATE":
            all_steps.append(event["step"])
        elif event["type"] == "RUN_COMPLETED":
            last_event = event

    if run_id and last_event:
        ACTIVE_RUNS[run_id] = last_event["state"]
        return last_event["state"]
    elif run_id and run_id in ACTIVE_RUNS:
        return ACTIVE_RUNS[run_id]

    raise HTTPException(status_code=500, detail="Workflow did not complete normally.")


@router.get("/runs/{run_id}/stream")
async def stream_agent_execution(run_id: str = None, prompt: str = "Find failed and pending customer payments, determine which ones require action, create tasks for the finance team, contact the relevant customers, notify the ops team, update our business ops record, and give me a concise executive summary."):
    """
    Server-Sent Events (SSE) streaming endpoint for live execution trace.
    """
    async def event_generator():
        async for event in agent.run(user_request=prompt, demo_mode=True):
            if event["type"] == "RUN_STARTED":
                ACTIVE_RUNS[event["run_id"]] = {"run_id": event["run_id"], "status": "RUNNING"}
            elif event["type"] == "RUN_COMPLETED":
                ACTIVE_RUNS[event["run_id"]] = event["state"]

            payload = json.dumps(event)
            yield f"data: {payload}\n\n"
            await asyncio.sleep(0.05)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/runs/{run_id}")
async def get_run_status(run_id: str):
    """
    Retrieves status and details of a specific agent run.
    """
    if run_id in ACTIVE_RUNS:
        return ACTIVE_RUNS[run_id]
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")


@router.get("/runs/{run_id}/steps")
async def get_run_steps(run_id: str):
    """
    Retrieves execution steps for a specific agent run.
    """
    if run_id in ACTIVE_RUNS:
        return ACTIVE_RUNS[run_id].get("steps", [])
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")
