# OpsPilot AI — Security & Guardrail Architecture

OpsPilot AI implements enterprise defense-in-depth principles:

## 1. Prompt Injection Resistance
- **Input Inspection**: User input is checked against known jailbreak, instruction hijack, and privilege escalation patterns.
- **Untrusted External Data**: Customer email contents, Slack incoming messages, and payment transaction memos are treated strictly as passive data strings and never evaluated as executable system instructions.

## 2. Zero LLM Arithmetic & Deterministic Validation
- The LLM is never trusted to perform counts, math, status determinations, or financial aggregation.
- All numbers displayed in the executive summary or transmitted in tool calls are computed by the Python Business Rules Engine.
- If an LLM response references a non-existent payment ID or an inaccurate amount, the Claim Validation Service rejects the action.

## 3. Secret Isolation
- Secrets (`GEMINI_API_KEY`, `SWYTCHCODE_API_KEY`, etc.) are read strictly through environment variables (`backend/app/utils/config.py`).
- Automatic Secret Scrubber (`services/security.py`) sanitizes dictionaries, logs, and state objects before persisting or transmitting them.
- Secrets are NEVER printed in agent traces or sent to the browser.

## 4. Human-In-The-Loop Approval Gates
- Consequential external actions (sending customer emails, bulk alerts, critical Jira tickets) can trigger a pause in the agent loop.
- The state enters `PENDING_APPROVAL`, exposing the planned payload in the interactive UI Approval Panel for human review.
- Actions cannot proceed without explicit operator sign-off (`APPROVED` or `REJECTED`).

## 5. Idempotency & Action Fingerprinting
- Prevents accidental duplicates caused by retries or repeated runs.
- Every external action is fingerprinted using a SHA-256 hash:
  `SHA-256(ACTION_TYPE + TARGET + CANONICAL_JSON_PAYLOAD)`
- If a hash has already been recorded, duplicate execution is skipped.

## 6. Execution Loop Boundaries
- `MAX_AGENT_STEPS`: 25 steps max per workflow.
- `MAX_TOOL_RETRIES`: 3 retries max per failed tool.
- `TOOL_TIMEOUT_SECONDS`: 30 seconds max per API call.
- `WORKFLOW_TIMEOUT_SECONDS`: 180 seconds max total duration.
