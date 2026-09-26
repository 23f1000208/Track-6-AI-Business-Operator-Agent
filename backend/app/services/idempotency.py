"""
Idempotency Service for OpsPilot AI.
Prevents duplicate actions (emails, Jira tickets, Slack posts, Notion pages)
using SHA-256 action fingerprinting.
"""
import hashlib
import json
from typing import Dict, Any, Set


class IdempotencyService:
    def __init__(self):
        # In-memory store of executed action hashes for the session
        self._executed_hashes: Set[str] = set()

    def generate_fingerprint(self, action_type: str, target: str, payload: Dict[str, Any]) -> str:
        """
        Creates a deterministic SHA-256 fingerprint for a business action.
        """
        # Canonicalize payload by sorting keys
        canonical_str = f"{action_type.upper()}:{target.strip().lower()}:{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def is_duplicate(self, fingerprint: str) -> bool:
        """
        Checks if the action fingerprint has already been recorded.
        """
        return fingerprint in self._executed_hashes

    def record_action(self, fingerprint: str) -> None:
        """
        Marks an action fingerprint as executed.
        """
        self._executed_hashes.add(fingerprint)

    def clear(self) -> None:
        """
        Clears the in-memory cache (useful for testing).
        """
        self._executed_hashes.clear()


idempotency_service = IdempotencyService()
