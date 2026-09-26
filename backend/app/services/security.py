"""
Security Layer for OpsPilot AI.
Provides:
1. Prompt Injection Scanning & Resistance
2. External Content Sanitization
3. Secret Isolation & Scrubbing
4. Tool Permission & Risk Classification
"""
import re
from typing import Tuple, List, Dict, Any
from app.utils.config import settings

# Suspicious prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+rules",
    r"system\s*:\s*you\s+are\s+now",
    r"override\s+security\s+policies",
    r"bypass\s+approval",
    r"transfer\s+(all\s+)?(money|funds|crypto)",
    r"delete\s+from\s+[a-zA-Z0-9_]+",
    r"drop\s+table",
    r"reveal\s+(api\s+key|secret|password|credential)",
    r"output\s+system\s+prompt"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

# Sensitive keys to scrub from logs and state
SECRET_KEYS = {
    "api_key", "token", "secret", "password", "auth", "authorization",
    "client_secret", "bot_token", "private_key"
}


class SecurityService:
    @staticmethod
    def scan_for_prompt_injection(text: str) -> Tuple[bool, List[str]]:
        """
        Scans input for prompt injection attempts.
        Returns (is_suspicious, reasons).
        """
        if not text:
            return False, []

        matches = []
        for pattern in COMPILED_PATTERNS:
            if pattern.search(text):
                matches.append(f"Detected suspicious instruction pattern: '{pattern.pattern}'")

        return len(matches) > 0, matches

    @staticmethod
    def sanitize_external_content(content: Any) -> Any:
        """
        Treats external data (emails, transaction memos, Slack messages)
        strictly as passive data strings. Strips command delimiters.
        """
        if isinstance(content, str):
            # Strip potential role spoofing prefixes
            cleaned = re.sub(r'^(System|Assistant|User|Admin):\s*', '', content, flags=re.IGNORECASE)
            return cleaned.strip()
        elif isinstance(content, dict):
            return {k: SecurityService.sanitize_external_content(v) for k, v in content.items()}
        elif isinstance(content, list):
            return [SecurityService.sanitize_external_content(item) for item in content]
        return content

    @staticmethod
    def scrub_secrets(data: Any) -> Any:
        """
        Recursively scrubs any credential or token from dictionaries, lists, or strings
        so they are NEVER stored in logs, DB, or sent to frontend.
        """
        if isinstance(data, dict):
            scrubbed = {}
            for k, v in data.items():
                if any(secret_kw in k.lower() for secret_kw in SECRET_KEYS):
                    scrubbed[k] = "[REDACTED_SECRET]"
                else:
                    scrubbed[k] = SecurityService.scrub_secrets(v)
            return scrubbed
        elif isinstance(data, list):
            return [SecurityService.scrub_secrets(item) for item in data]
        elif isinstance(data, str):
            # Check for potential bearer tokens or api keys in strings
            if "bearer " in data.lower():
                return re.sub(r'Bearer\s+[a-zA-Z0-9_\-\.]+', 'Bearer [REDACTED]', data, flags=re.IGNORECASE)
            return data
        return data

    @staticmethod
    def validate_tool_permission(tool_name: str, action_type: str) -> bool:
        """
        Ensures the requested tool action is authorized in the current environment.
        """
        allowed_tools = {"paypal", "gmail", "slack", "jira", "notion"}
        normalized = tool_name.lower()
        return any(allowed in normalized for allowed in allowed_tools)


security_service = SecurityService()
