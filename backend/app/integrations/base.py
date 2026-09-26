"""
Base Integration Adapter for OpsPilot AI.
Provides abstract interface for Swytchcode integrations and Demo Mode mock implementations.
Never couples business logic to raw HTTP details.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
from app.utils.config import settings


class IntegrationStatus(str):
    CONNECTED = "CONNECTED"
    DEMO_MODE = "DEMO MODE"
    ERROR = "ERROR"
    NOT_CONFIGURED = "NOT CONFIGURED"


class BaseIntegration(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.retry_limit = settings.MAX_TOOL_RETRIES
        self.timeout_seconds = settings.TOOL_TIMEOUT_SECONDS

    @abstractmethod
    def is_configured(self) -> bool:
        """Checks if real API credentials are configured."""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Returns CONNECTED, DEMO MODE, ERROR, or NOT CONFIGURED."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Returns list of supported tool capabilities."""
        pass

    def execute_with_telemetry(self, action_name: str, fn, *args, **kwargs) -> Dict[str, Any]:
        """
        Executes an integration action while recording latency, status, and handling errors.
        """
        start_time = time.time()
        try:
            result = fn(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            return {
                "success": True,
                "data": result,
                "latency_ms": round(latency_ms, 2),
                "error": None
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "success": False,
                "data": None,
                "latency_ms": round(latency_ms, 2),
                "error": str(e)
            }
