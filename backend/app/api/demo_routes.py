"""
Demo Mode API Routes for OpsPilot AI.
Fulfills requirements:
45. Failure Simulation (Demonstrating partial failure recovery without full workflow restart)
49. Demo Mode [ RUN 2-MINUTE DEMO ] button triggering live multi-step execution.
"""
from fastapi import APIRouter
from typing import Dict, Any
from app.agents.agent import agent
from app.api.agent_routes import ACTIVE_RUNS

router = APIRouter(prefix="/api/demo", tags=["Demo Mode"])

PRIMARY_DEMO_PROMPT = (
    "Find failed and pending customer payments, determine which ones require action, "
    "create tasks for the finance team, contact the relevant customers, notify the ops team, "
    "update our business ops record, and give me a concise executive summary."
)


@router.post("/run-quick")
async def run_primary_demo():
    """
    Executes the canonical Track 6 2-minute demo using real agent orchestration and synthetic demo data.
    """
    last_event = None
    run_id = None

    async for event in agent.run(
        user_request=PRIMARY_DEMO_PROMPT,
        require_approval=False,
        demo_mode=True,
        simulate_failure=False
    ):
        if event["type"] == "RUN_STARTED":
            run_id = event["run_id"]
        elif event["type"] == "RUN_COMPLETED":
            last_event = event

    if run_id and last_event:
        ACTIVE_RUNS[run_id] = last_event["state"]
        return last_event["state"]

    return {"error": "Demo run failed to complete"}


@router.post("/simulate-failure")
async def run_failure_simulation():
    """
    Executes the workflow with Jira failure simulated, proving safe partial-failure containment.
    """
    last_event = None
    run_id = None

    async for event in agent.run(
        user_request=PRIMARY_DEMO_PROMPT,
        require_approval=False,
        demo_mode=True,
        simulate_failure=True
    ):
        if event["type"] == "RUN_STARTED":
            run_id = event["run_id"]
        elif event["type"] == "RUN_COMPLETED":
            last_event = event

    if run_id and last_event:
        ACTIVE_RUNS[run_id] = last_event["state"]
        return last_event["state"]

    return {"error": "Failure simulation completed"}
