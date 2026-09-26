"""
Configuration settings for OpsPilot AI.
Strict secret isolation: secrets are never hardcoded and read strictly via environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "OpsPilot AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True

    # Mode: When DEMO_MODE is true, mock adapters execute with synthetic business data
    # without requiring live external API credentials.
    DEMO_MODE: bool = True
    SIMULATE_FAILURE: bool = False
    FAILURE_TARGET_TOOL: str = "jira"  # Tool to simulate failure on if SIMULATE_FAILURE is true

    # LLM / Gemini Credentials
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Swytchcode Credentials
    SWYTCHCODE_API_KEY: Optional[str] = None
    SWYTCHCODE_BASE_URL: str = "https://api.swytchcode.com/v1"
    SWYTCHCODE_MCP_URL: str = "http://127.0.0.1:5476/sse"

    # Direct Integrations (Fallback or direct credentials)
    STRIPE_API_KEY: Optional[str] = None
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_MODE: str = "sandbox"

    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None

    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_CHANNEL_DEFAULT: str = "#ops-alerts"

    JIRA_HOST: Optional[str] = None
    JIRA_EMAIL: Optional[str] = None
    JIRA_API_TOKEN: Optional[str] = None
    JIRA_PROJECT_KEY: str = "FIN"

    NOTION_API_KEY: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None

    # Safety & Agent Loop Boundaries
    MAX_AGENT_STEPS: int = 25
    MAX_TOOL_RETRIES: int = 3
    TOOL_TIMEOUT_SECONDS: int = 30
    WORKFLOW_TIMEOUT_SECONDS: int = 180

    # Business Rules Thresholds (Deterministic Python)
    SLA_PENDING_DAYS_THRESHOLD: int = 3
    CRITICAL_AMOUNT_THRESHOLD: float = 500.0

    # Database
    DATABASE_URL: str = "sqlite:///./opspilot.db"

    model_config = SettingsConfigDict(
        env_file=["backend/.env", ".env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and not self.GEMINI_API_KEY.startswith("YOUR_"))

    @property
    def has_swytchcode_key(self) -> bool:
        return bool(self.SWYTCHCODE_API_KEY and self.SWYTCHCODE_API_KEY.strip())

    def is_provider_connected(self, provider_name: str) -> bool:
        """
        Auto-detects if provider is connected via Swytchcode CLI credentials.db
        or direct environment configuration.
        """
        import os
        import json

        norm = provider_name.lower()
        if norm == "stripe" and self.STRIPE_API_KEY:
            return True
        if norm == "paypal" and self.PAYPAL_CLIENT_ID:
            return True
        if norm == "slack" and self.SLACK_BOT_TOKEN:
            return True
        if norm == "jira" and self.JIRA_API_TOKEN:
            return True
        if norm == "gmail" and self.GMAIL_CLIENT_ID:
            return True
        if norm == "notion" and self.NOTION_API_KEY:
            return True

        # Check Swytchcode CLI local configuration
        swy_dir = os.path.expanduser("~/.swytchcode")
        tooling_file = os.path.join(swy_dir, "tooling.json")
        creds_db = os.path.join(swy_dir, "credentials.db")

        if os.path.exists(tooling_file):
            try:
                with open(tooling_file, "r", encoding="utf-8") as f:
                    tooling = json.load(f)
                integrations = tooling.get("integrations", {})
                for k in integrations.keys():
                    if norm in k.lower():
                        # If credentials.db exists or auth.json exists, marked connected!
                        if os.path.exists(creds_db) and os.path.getsize(creds_db) > 0:
                            return True
            except Exception:
                pass

        return False


settings = Settings()
