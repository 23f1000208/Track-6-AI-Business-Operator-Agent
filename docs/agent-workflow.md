# OpsPilot AI — Agent Workflow & Dynamic Loop

## The Real Agentic Loop

Unlike traditional linear API wrappers, OpsPilot AI implements a true reactive agent loop where **intermediate tool outputs dictate subsequent actions**.

```
USER REQUEST
     ↓
SECURITY SCAN (Prompt Injection Defense)
     ↓
UNDERSTAND & CLASSIFY INTENT
     ↓
DYNAMIC PLANNING (Select minimal necessary tools)
     ↓
[ AGENT LOOP BEGINS ]
     ↓
DECIDE NEXT ACTION (Inspect state & intermediate results)
     ├── Prerequisite Failed? → Safe Partial Termination
     ├── Prerequisite Needed? → Tool Selection
     ├── Raw Data Received? → Apply Deterministic Business Rules
     └── Actions Ready & Risky? → Pause for Human Approval
     ↓
EXECUTE TOOL (PayPal, Jira, Gmail, Slack, Notion)
     ↓
OBSERVE & RECORD LATENCY
     ↓
VALIDATE EVIDENCE (Zero LLM hallucinations)
     ↓
IDEMPOTENCY CHECK (SHA-256 Fingerprinting)
     ↓
[ REPEAT LOOP UNTIL OBJECTIVE SATISFIED ]
     ↓
MULTI-SYSTEM VERIFICATION (Issue keys, Message IDs, Delivery timestamps)
     ↓
EXECUTIVE SUMMARY (Dynamic Python Metrics)
```

---

## Canonical Multi-Step Scenario (Track 6 Primary Demo)

**Business Request:**
> "Find failed and pending customer payments, determine which ones require action, create tasks for the finance team, contact the relevant customers, notify the ops team, update our business ops record, and give me a concise executive summary."

### Dynamic Step Trace:

1. **Security Scan**: Checks user prompt. Rejects privilege escalation or injection vectors.
2. **Intent Analysis**: Maps intent to `AUTONOMOUS_OPERATIONS_RECOVERY`.
3. **Dynamic Planning**: Selects 5 tools (`paypal_retrieve_payments`, `jira_create_task`, `gmail_send_customer_email`, `slack_notify_channel`, `notion_update_record`). Excludes non-relevant integrations.
4. **Tool 1 (PayPal)**: Calls `paypal_retrieve_payments(limit=20)`. Retrieves 15 transactions. Verifies evidence hash.
5. **Business Rules Engine**: Deterministically identifies:
   - 10 Completed payments (no follow-up)
   - 3 Failed payments (`PAY-1004` $750 Insufficient Funds, `PAY-1008` $320 Expired Card, `PAY-1012` $95 Decline)
   - 2 Pending payments (`PAY-1002` $640 ACH 4 days old -> SLA breached, `PAY-1015` $180 Wire 0 days old -> Grace period)
   - **Total Requiring Action: 4**
   - **Total At-Risk Exposure: $1,805.00**
6. **Tool 2 (Jira)**: Dispatches remediation tasks for all 4 accounts (`FIN-101`, `FIN-102`, `FIN-103`, `FIN-104`).
7. **Tool 3 (Gmail)**: Generates tailored customer update notices with transaction references (`msg_e4d2...`).
8. **Tool 4 (Slack)**: Posts formatted incident breakdown to `#ops-alerts` with severity indicator.
9. **Tool 5 (Notion)**: Commits structured reconciliation page to operations knowledge base.
10. **Verification**: Verifies all created issue keys, email IDs, message timestamps, and page IDs.
11. **Executive Summary**: Generates dynamic executive dashboard report with measured execution duration.

---

## Partial Failure Handling (Requirement 45)

When a critical upstream prerequisite fails (e.g. Jira returns 503 during simulated outage):
1. The error is captured in `failed_actions`.
2. The dynamic router detects that `jira` failed.
3. The router orders **SAFE TERMINATION**:
   > *"Jira task creation failed. Downstream customer outreach (Gmail) and Slack notifications were not executed because Jira task tracking is a prerequisite."*
4. Downstream tools (Gmail, Slack, Notion) are **not executed**.
5. The state is preserved, and a `PARTIAL_FAILURE` report is produced.
