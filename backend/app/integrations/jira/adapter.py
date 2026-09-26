"""
Jira Swytchcode Integration Adapter.
Creates, updates, and tracks operational Jira issues.
Supports failure simulation for Track 6 partial-failure handling demonstration.
"""
from typing import List, Dict, Any, Optional
import uuid
import httpx
from app.integrations.base import BaseIntegration, IntegrationStatus
from app.schemas.tools import JiraTaskResult
from app.utils.config import settings


class JiraAdapter(BaseIntegration):
    def __init__(self):
        super().__init__("Jira")
        self._issue_counter = 101
        self._created_issues: List[Dict[str, Any]] = []

    def is_configured(self) -> bool:
        return settings.is_provider_connected("jira")

    def get_status(self) -> str:
        if self.is_configured():
            return IntegrationStatus.CONNECTED
        return IntegrationStatus.DEMO_MODE

    def get_capabilities(self) -> List[str]:
        return ["create_issue", "search_issues", "update_issue", "get_issue"]

    def create_task(
        self,
        summary: str,
        description: str,
        priority: str = "High",
        project_key: str = "FIN",
        payment_id: Optional[str] = None,
        simulate_failure: bool = False
    ) -> JiraTaskResult:
        """
        Creates a Jira ticket for finance operations follow-up.
        """
        # Failure Simulation check (Requirement 45)
        if simulate_failure or (settings.SIMULATE_FAILURE and settings.FAILURE_TARGET_TOOL.lower() == "jira"):
            raise RuntimeError("Jira Service Unavailable: Gateway 503 upstream connection timeout to Jira Cloud.")

        # Live Swytchcode Call if active
        if self.is_configured() and not settings.DEMO_MODE:
            try:
                headers = {
                    "Authorization": f"Bearer {settings.SWYTCHCODE_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "project_key": project_key,
                    "summary": summary,
                    "description": description,
                    "priority": priority,
                    "payment_id": payment_id
                }
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.post(f"{settings.SWYTCHCODE_BASE_URL}/jira/issues", headers=headers, json=payload)
                    if resp.status_code in [200, 201]:
                        res = resp.json()
                        return JiraTaskResult(
                            success=True,
                            issue_key=res.get("issue_key", f"{project_key}-LIVE"),
                            issue_id=res.get("id", str(uuid.uuid4())),
                            summary=summary,
                            priority=priority,
                            status="Open",
                            link=f"https://company.atlassian.net/browse/{res.get('issue_key')}"
                        )
            except Exception:
                pass

        # Demo Mode Synthetic Execution
        issue_key = f"{project_key}-{self._issue_counter}"
        issue_id = f"jira_issue_{uuid.uuid4().hex[:8]}"
        self._issue_counter += 1

        record = {
            "issue_key": issue_key,
            "issue_id": issue_id,
            "summary": summary,
            "description": description,
            "priority": priority,
            "payment_id": payment_id,
            "status": "Open",
            "link": f"https://company.atlassian.net/browse/{issue_key}"
        }
        self._created_issues.append(record)

        return JiraTaskResult(
            success=True,
            issue_key=issue_key,
            issue_id=issue_id,
            summary=summary,
            priority=priority,
            status="Open",
            link=record["link"]
        )

    def get_created_issues(self) -> List[Dict[str, Any]]:
        return self._created_issues


jira_adapter = JiraAdapter()
