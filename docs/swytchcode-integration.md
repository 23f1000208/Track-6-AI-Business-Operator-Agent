# Swytchcode Integration Guide (Track 6)

Track 6 (AI Business Operator Agent) requires meaningful multi-step orchestration across business tools. OpsPilot AI integrates 5 tools through Swytchcode:

| Integration | Primary Purpose | Capabilities | Mode |
|---|---|---|---|
| **PayPal** | Payment transaction audit & dispute tracking | `retrieve_transactions`, `search_payments`, `get_payment_details` | Live or Demo Mode |
| **Jira** | Operational task remediation for finance staff | `create_issue`, `search_issues`, `update_issue`, `get_issue` | Live or Demo Mode |
| **Gmail** | Customer outreach & payment resolution notices | `send_email`, `draft_email`, `search_messages` | Live or Demo Mode |
| **Slack** | Internal operations team alerts & briefings | `send_message`, `notify_channel`, `search_messages` | Live or Demo Mode |
| **Notion** | Operations knowledge base synchronization | `create_page`, `update_record`, `search_pages` | Live or Demo Mode |

---

## Adapter Architecture

All integrations inherit from `BaseIntegration` (`backend/app/integrations/base.py`):
```
Google ADK FunctionTool
          ↓
     ToolRegistry
          ↓
  Integration Adapter (e.g. PayPalAdapter)
          ↓
   [ DEMO_MODE? ]
    ├── True  → Synthetic Business Repository (15 payments, 10 customers)
    └── False → Swytchcode REST Gateway API
```

## Configuring Live Credentials

To switch from Demo Mode to Live Swytchcode:
1. In `backend/.env`, set:
   ```env
   DEMO_MODE=false
   SWYTCHCODE_API_KEY=your_swytchcode_key_here
   SWYTCHCODE_BASE_URL=https://api.swytchcode.com/v1
   ```
2. The Integration Status cards in the UI will automatically update from `DEMO MODE` to `CONNECTED`.
3. If credentials are empty or remote servers are unreachable, OpsPilot AI gracefully falls back to Demo Mode without crashing.
