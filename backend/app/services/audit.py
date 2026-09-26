"""
Audit Trail Logging Service for OpsPilot AI.
Fulfills requirement 25:
Records every meaningful agent step, decision, tool invocation, and action with timestamps.
Never stores secrets in audit logs.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.services.security import security_service


class AuditService:
    def __init__(self):
        # In-memory storage for active run audit trails
        self._logs: List[Dict[str, Any]] = []

    def record_event(self, event_name: str, run_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Records a timestamped audit event with automatic secret scrubbing.
        """
        safe_details = security_service.scrub_secrets(details or {})
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_name.upper(),
            "run_id": run_id,
            "details": safe_details
        }
        self._logs.append(entry)
        return entry

    def get_logs_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        return [log for log in self._logs if log.get("run_id") == run_id]

    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(reversed(self._logs[-limit:]))


audit_service = AuditService()
