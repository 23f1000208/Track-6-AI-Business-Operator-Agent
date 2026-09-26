# OpsPilot AI — 2.5-Minute Jury Demo Script

This script is structured for the **2.5-minute finalist presentation + 1.5-minute Q&A** before the jury.

---

## Demo Timeline

### 0:00 – 0:20 | Introduction & The Problem
- **Speaker:** "Judges, modern operations managers spend 40% of their workday jumping between disparate SaaS tools—checking failed Stripe/PayPal payments, manually creating Jira tickets, drafting emails in Gmail, alerting team members on Slack, and logging notes in Notion."
- **Speaker:** "Most 'AI agents' are just chatbots with API buttons. OpsPilot AI is an **actual autonomous business operator** built on Google ADK, Gemini, and Swytchcode that turns natural language intent into multi-step execution."

### 0:20 – 0:45 | Executing the Intent
- Click the **[ RUN 2-MINUTE DEMO ]** button in the Command Center (or enter the canonical prompt).
- **Show Screen:** Observe the **Live Agent Workflow Timeline** and **Safe Agent Trace** updating in real time.
- **Key Talking Point:** "Notice our core architectural principle: **LLM ≠ Source of Truth**. The agent uses Google ADK for orchestration and Gemini for reasoning, but **all financial math, SLA aging, and classification are 100% deterministic Python code**."

### 0:45 – 1:30 | Multi-Step Swytchcode Execution
- Point to the live trace as tools fire:
  1. **PayPal:** Retrieves 15 transactions. Python classifies 4 at-risk items ($1,805.00 exposure).
  2. **Jira:** Automatically creates remediation tasks (`FIN-101`, `FIN-102`, `FIN-103`, `FIN-104`).
  3. **Gmail:** Generates tailored payment update emails for the affected customer accounts.
  4. **Slack:** Posts an incident alert to the `#ops-alerts` channel.
  5. **Notion:** Synchronizes the reconciliation record to the knowledge base.

### 1:30 – 2:00 | Security, Verification & Ground Truth
- Scroll to the **Final Executive Summary**:
  - Show the dynamic numbers: 15 payments analyzed, 4 require attention, 3 failed, 1 pending SLA breach.
  - Point to the **Multi-System Verification Panel**: Every action is verified with issue keys, message IDs, and delivery timestamps.
  - Point to the **Measured Metrics**: Exact duration, actions executed, zero duplicates (SHA-256 idempotency).

### 2:00 – 2:30 | Failure Containment & Conclusion
- Demonstrate the **[ Simulate Jira Failure ]** toggle:
  - Show that when Jira is unavailable, the agent halts downstream customer outreach safely instead of sending un-tracked emails.
- **Closing:** "OpsPilot AI: From Business Intent to Autonomous Execution. Ready to answer your questions."
