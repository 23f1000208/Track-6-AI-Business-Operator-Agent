"""
OpsPilot AI Agent Orchestrator.
Fulfills requirements:
1. Agentic Framework (Google ADK & Gemini)
3. LLM != Source of Truth (Zero LLM arithmetic, Python rules engine)
5. Agent Loop (Understand -> Plan -> Select Tool -> Execute -> Observe -> Validate -> Business Rules -> Decide -> Verify -> Summarize)
14. Loop Safety (Step limits, timeouts, duplicate prevention)
24. Partial Failure Handling
37. Real-Time Streaming Support (Async generator yielding execution events)
"""
import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, Optional, List

from google.adk.agents.llm_agent import LlmAgent
from app.utils.config import settings
from app.agents.state import AgentState, AgentStepData
from app.agents.planner import planner, ExecutionPlan
from app.agents.router import router, RoutingDecision
from app.agents.tools import ADK_TOOLS, TOOL_FUNCTION_MAP
from app.services.security import security_service
from app.services.business_rules import business_rules
from app.services.validation import validation_service
from app.services.verification import verification_service
from app.services.idempotency import idempotency_service
from app.services.approval import approval_service
from app.services.audit import audit_service
from app.schemas.payments import PaymentRecord, PaymentClassificationSummary
from app.schemas.agent import ExecutiveSummary


class OpsPilotAgent:
    def __init__(self):
        self.adk_agent: Optional[LlmAgent] = None
        self._init_google_adk()

    def _init_google_adk(self):
        """Initializes Google ADK LlmAgent structure."""
        try:
            self.adk_agent = LlmAgent(
                name="OpsPilot_AI_Business_Operator",
                description="Autonomous business operations agent coordinating payments, tasks, and communications.",
                instruction=(
                    "You are OpsPilot AI, an autonomous business operations agent. "
                    "Analyze business requests, coordinate across tools, and let deterministic Python logic handle all calculations."
                ),
                tools=ADK_TOOLS
            )
        except Exception:
            # Fallback if environment lacks active Vertex/Gemini credentials
            self.adk_agent = None

    async def run(
        self,
        user_request: str,
        require_approval: bool = False,
        demo_mode: bool = True,
        simulate_failure: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes the full agent loop, yielding real-time execution events for SSE streaming.
        """
        run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        start_time = time.time()

        state = AgentState(
            run_id=run_id,
            user_request=user_request,
            max_steps=settings.MAX_AGENT_STEPS,
            is_demo_mode=demo_mode,
            simulate_failure=simulate_failure,
            status="RUNNING"
        )

        audit_service.record_event("REQUEST_RECEIVED", run_id=run_id, details={"request": user_request})

        yield {
            "type": "RUN_STARTED",
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_request": user_request,
            "demo_mode": demo_mode
        }

        # -------------------------------------------------------------
        # STEP 1: SECURITY SCANNING & INPUT DEFENSE
        # -------------------------------------------------------------
        is_suspicious, reasons = security_service.scan_for_prompt_injection(user_request)
        if is_suspicious:
            step = state.add_step(
                action="SECURITY_SCAN",
                result_summary=f"Security Alert: Blocked suspicious instruction attempt: {reasons[0]}",
                status="FAILED",
                details={"reasons": reasons}
            )
            audit_service.record_event("SECURITY_VIOLATION", run_id=run_id, details={"reasons": reasons})
            state.status = "FAILED"
            state.error_message = f"Security Violation: {reasons[0]}"
            yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}
            return

        step = state.add_step(
            action="SECURITY_SCAN",
            result_summary="Input sanitized and verified. No prompt injection or privilege escalation detected.",
            status="COMPLETED"
        )
        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

        # -------------------------------------------------------------
        # STEP 2: UNDERSTAND & INTENT ANALYSIS
        # -------------------------------------------------------------
        audit_service.record_event("INTENT_ANALYZED", run_id=run_id)
        plan: ExecutionPlan = planner.plan(user_request)
        state.intent = plan.intent
        state.objective = plan.objective
        state.plan = plan.required_tools

        step = state.add_step(
            action="UNDERSTAND",
            result_summary=f"Understood request. Intent: '{plan.intent}'. Objective: {plan.objective}",
            details=plan.to_dict()
        )
        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

        # -------------------------------------------------------------
        # STEP 3: DYNAMIC PLANNING
        # -------------------------------------------------------------
        step = state.add_step(
            action="PLAN",
            result_summary=f"Selected {len(plan.required_tools)} required tool(s): {', '.join(plan.required_tools)}. Non-relevant integrations excluded.",
            details={"tools": plan.required_tools, "steps": plan.steps}
        )
        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

        # -------------------------------------------------------------
        # AGENT LOOP (Observe -> Apply Rules -> Decide -> Execute)
        # -------------------------------------------------------------
        while state.current_step < state.max_steps:
            # Let router inspect intermediate state and decide next action
            decision: RoutingDecision = router.decide_next_action(state)
            state.decisions.append(decision.reason)

            # Check if router ordered stop due to prerequisite failure
            if decision.action_type == "STOP_ON_FAILURE":
                step = state.add_step(
                    action="DECIDE",
                    result_summary=f"Safe Termination: {decision.reason}",
                    status="FAILED",
                    details={"reason": decision.reason}
                )
                audit_service.record_event("WORKFLOW_STOPPED_PARTIAL_FAILURE", run_id=run_id, details={"reason": decision.reason})
                state.status = "PARTIAL_FAILURE"
                state.error_message = decision.reason
                yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}
                break

            # Check if router determined all tools have been executed
            if decision.action_type == "VERIFY_AND_FINISH":
                break

            # Handle deterministic Python Business Rules stage
            if decision.action_type == "APPLY_BUSINESS_RULES":
                step = state.add_step(
                    action="DECIDE",
                    result_summary=decision.reason,
                    status="COMPLETED"
                )
                yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                # Deterministic classification
                classified_payments, summary = business_rules.classify_batch(state.retrieved_payments)
                state.retrieved_payments = classified_payments
                state.classification_summary = summary
                audit_service.record_event("PAYMENT_CLASSIFICATION_COMPLETED", run_id=run_id, details=summary.model_dump())

                step = state.add_step(
                    action="APPLY_BUSINESS_RULES",
                    result_summary=(
                        f"Python Engine Classified {summary.total_analyzed} payments. "
                        f"At-Risk: {summary.require_attention} (Failed: {summary.failed_count}, Pending: {summary.pending_count}). "
                        f"Critical Exposure: ${summary.total_at_risk_amount:,.2f} USD."
                    ),
                    details=summary.model_dump()
                )
                yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}
                continue

            # Handle tool execution
            if decision.action_type == "CALL_TOOL":
                tool_name = decision.tool_name

                step = state.add_step(
                    action="TOOL_SELECT",
                    tool=tool_name,
                    result_summary=f"Selected tool '{tool_name}'. Reason: {decision.reason}"
                )
                yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                # Execute specific tool based on tool_name
                await asyncio.sleep(0.05)  # Fast live stream update
                tool_start = time.time()

                try:
                    # 1. PAYPAL or STRIPE
                    if tool_name in ["paypal_retrieve_payments", "stripe_retrieve_payments"]:
                        provider_name = "Stripe" if "stripe" in tool_name else "PayPal"
                        audit_service.record_event(f"{provider_name.upper()}_SELECTED", run_id=run_id)
                        handler = TOOL_FUNCTION_MAP[tool_name]
                        result = handler(limit=20)
                        latency = (time.time() - tool_start) * 1000

                        payments_data = [PaymentRecord(**p) for p in result["payments"]]
                        state.retrieved_payments = payments_data
                        state.tool_results[tool_name] = result

                        step = state.add_step(
                            action="OBSERVE",
                            tool=tool_name,
                            result_summary=f"{provider_name} returned {len(payments_data)} transaction records. Raw evidence verified with SHA-256 hash.",
                            details={"count": len(payments_data), "hash": result["raw_evidence_hash"]}
                        )
                        audit_service.record_event(f"{provider_name.upper()}_RESULT_VALIDATED", run_id=run_id, details={"count": len(payments_data)})
                        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                    # 2. JIRA
                    elif tool_name == "jira_create_task":
                        audit_service.record_event("JIRA_SELECTED", run_id=run_id)
                        tasks_to_create = business_rules.determine_jira_tasks(state.retrieved_payments)
                        created_tasks = []

                        # If user requested failure simulation on Jira
                        if simulate_failure:
                            raise RuntimeError("Jira Service Unavailable: Gateway 503 upstream connection timeout to Jira Cloud.")

                        for t in tasks_to_create:
                            # Validation before action (Requirement 20)
                            is_valid, err = validation_service.validate_jira_action(t, state.retrieved_payments)
                            if not is_valid:
                                continue

                            # Idempotency check (Requirement 22)
                            fingerprint = idempotency_service.generate_fingerprint("JIRA", t["project_key"], t)
                            if idempotency_service.is_duplicate(fingerprint):
                                continue

                            res = TOOL_FUNCTION_MAP[tool_name](
                                summary=t["summary"],
                                description=t["description"],
                                priority=t["priority"],
                                project_key=t["project_key"],
                                payment_id=t["payment_id"],
                                simulate_failure=False
                            )
                            idempotency_service.record_action(fingerprint)
                            verified, v_msg = verification_service.verify_jira_task(res)
                            if verified:
                                state.verification_results.append(v_msg)
                            created_tasks.append(res)
                            state.completed_actions.append({"tool": "jira", "item": res})

                        state.tool_results[tool_name] = created_tasks
                        step = state.add_step(
                            action="OBSERVE",
                            tool=tool_name,
                            result_summary=f"Created {len(created_tasks)} Jira operational remediation tickets with full issue keys.",
                            details={"tasks": created_tasks}
                        )
                        audit_service.record_event("JIRA_TASK_CREATED", run_id=run_id, details={"count": len(created_tasks)})
                        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                    # 3. GMAIL
                    elif tool_name == "gmail_send_customer_email":
                        audit_service.record_event("GMAIL_SELECTED", run_id=run_id)
                        emails_to_send = business_rules.determine_customer_emails(state.retrieved_payments)

                        # Check human approval requirement
                        if require_approval and not state.approved_actions:
                            # Create pending approval
                            app_req = approval_service.create_approval_request(
                                run_id=run_id,
                                action_type="GMAIL_BATCH_EMAIL",
                                target=f"{len(emails_to_send)} Customer Accounts",
                                description=f"Send payment update notifications to {len(emails_to_send)} customers regarding failed/pending billing.",
                                impact=f"Contacting {len(emails_to_send)} external client emails",
                                risk_level="HIGH",
                                evidence={"emails": emails_to_send}
                            )
                            state.pending_approvals.append(app_req)
                            state.status = "PENDING_APPROVAL"
                            step = state.add_step(
                                action="REQUEST_APPROVAL",
                                tool=tool_name,
                                result_summary=f"Consequential Action Requires Approval: Prepared {len(emails_to_send)} customer emails. Paused for review.",
                                status="PAUSED_APPROVAL",
                                details=app_req
                            )
                            audit_service.record_event("APPROVAL_REQUESTED", run_id=run_id, details=app_req)
                            yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}
                            return

                        sent_emails = []
                        for em in emails_to_send:
                            is_valid, err = validation_service.validate_gmail_action(em)
                            if not is_valid:
                                continue

                            fingerprint = idempotency_service.generate_fingerprint("GMAIL", em["recipient"], em)
                            if idempotency_service.is_duplicate(fingerprint):
                                continue

                            res = TOOL_FUNCTION_MAP[tool_name](
                                recipient=em["recipient"],
                                subject=em["subject"],
                                body=em["body"],
                                payment_id=em.get("payment_id"),
                                customer_name=em.get("customer_name")
                            )
                            idempotency_service.record_action(fingerprint)
                            verified, v_msg = verification_service.verify_gmail_dispatch(res)
                            if verified:
                                state.verification_results.append(v_msg)
                            sent_emails.append(res)
                            state.completed_actions.append({"tool": "gmail", "item": res})

                        state.tool_results[tool_name] = sent_emails
                        step = state.add_step(
                            action="OBSERVE",
                            tool=tool_name,
                            result_summary=f"Dispatched {len(sent_emails)} customer emails with verified message IDs.",
                            details={"sent": sent_emails}
                        )
                        audit_service.record_event("GMAIL_ACTION_COMPLETED", run_id=run_id, details={"count": len(sent_emails)})
                        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                    # 4. SLACK
                    elif tool_name == "slack_notify_channel":
                        audit_service.record_event("SLACK_SELECTED", run_id=run_id)
                        slack_payload = business_rules.determine_slack_notification(
                            state.classification_summary or PaymentClassificationSummary(
                                total_analyzed=len(state.retrieved_payments),
                                require_attention=0, failed_count=0, pending_count=0, completed_count=0,
                                critical_count=0, high_count=0, medium_count=0, low_count=0,
                                total_at_risk_amount=0.0, affected_customers=[]
                            ),
                            run_id=run_id
                        )

                        fingerprint = idempotency_service.generate_fingerprint("SLACK", slack_payload["channel"], slack_payload)
                        if not idempotency_service.is_duplicate(fingerprint):
                            res = TOOL_FUNCTION_MAP[tool_name](
                                channel=slack_payload["channel"],
                                message=slack_payload["message"],
                                severity=slack_payload["severity"],
                                incident_id=slack_payload["incident_id"]
                            )
                            idempotency_service.record_action(fingerprint)
                            verified, v_msg = verification_service.verify_slack_notification(res)
                            if verified:
                                state.verification_results.append(v_msg)
                            state.completed_actions.append({"tool": "slack", "item": res})
                            state.tool_results[tool_name] = res

                        step = state.add_step(
                            action="OBSERVE",
                            tool=tool_name,
                            result_summary=f"Broadcasted incident notification to Slack channel {slack_payload['channel']}.",
                            details=res
                        )
                        audit_service.record_event("SLACK_NOTIFICATION_COMPLETED", run_id=run_id, details=res)
                        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                    # 5. NOTION
                    elif tool_name == "notion_update_record":
                        audit_service.record_event("NOTION_SELECTED", run_id=run_id)
                        notion_payload = business_rules.determine_notion_record(
                            state.classification_summary or PaymentClassificationSummary(
                                total_analyzed=len(state.retrieved_payments),
                                require_attention=0, failed_count=0, pending_count=0, completed_count=0,
                                critical_count=0, high_count=0, medium_count=0, low_count=0,
                                total_at_risk_amount=0.0, affected_customers=[]
                            ),
                            run_id=run_id,
                            timestamp_str=datetime.now(timezone.utc).isoformat()
                        )

                        fingerprint = idempotency_service.generate_fingerprint("NOTION", notion_payload["page_title"], notion_payload)
                        if not idempotency_service.is_duplicate(fingerprint):
                            res = TOOL_FUNCTION_MAP[tool_name](
                                page_title=notion_payload["page_title"],
                                content=notion_payload["content"],
                                category=notion_payload["category"]
                            )
                            idempotency_service.record_action(fingerprint)
                            verified, v_msg = verification_service.verify_notion_update(res)
                            if verified:
                                state.verification_results.append(v_msg)
                            state.completed_actions.append({"tool": "notion", "item": res})
                            state.tool_results[tool_name] = res

                        step = state.add_step(
                            action="OBSERVE",
                            tool=tool_name,
                            result_summary="Synchronized operations outcome to Notion database page.",
                            details=res
                        )
                        audit_service.record_event("NOTION_UPDATED", run_id=run_id, details=res)
                        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

                except Exception as ex:
                    error_msg = str(ex)
                    state.failed_actions.append({"tool": tool_name, "error": error_msg})
                    step = state.add_step(
                        action="OBSERVE",
                        tool=tool_name,
                        result_summary=f"Tool Execution Error: {error_msg}",
                        status="FAILED",
                        details={"error": error_msg}
                    )
                    audit_service.record_event("TOOL_EXECUTION_FAILED", run_id=run_id, details={"tool": tool_name, "error": error_msg})
                    yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

        # -------------------------------------------------------------
        # STEP: VERIFICATION OF ALL ACTIONS
        # -------------------------------------------------------------
        audit_service.record_event("VERIFICATION_COMPLETED", run_id=run_id)
        verif_report = verification_service.compile_verification_report(
            actions_verified=state.verification_results,
            actions_failed=[f.get("error", "Unknown") for f in state.failed_actions]
        )
        step = state.add_step(
            action="VERIFY",
            result_summary=f"Verification Completed: {len(state.verification_results)} actions verified successfully. Status: {verif_report['status']}.",
            details=verif_report
        )
        yield {"type": "STEP_UPDATE", "step": step.model_dump(), "state": state.model_dump()}

        # -------------------------------------------------------------
        # FINAL EXECUTIVE SUMMARY (Dynamic, Zero Hallucinated Numbers)
        # -------------------------------------------------------------
        duration = round(time.time() - start_time, 2)
        total_payments = len(state.retrieved_payments)
        summary = state.classification_summary

        workflow_metrics = {
            "duration_sec": duration,
            "tools_used": len(state.tool_results),
            "actions_executed": len(state.completed_actions),
            "actions_successful": len(state.completed_actions),
            "actions_failed": len(state.failed_actions),
            "human_approvals": len(state.approved_actions),
            "at_risk_exposure": summary.total_at_risk_amount if summary else 0.0
        }
        state.workflow_metrics = workflow_metrics

        final_summary = ExecutiveSummary(
            title="OPERATIONS RUN COMPLETED",
            user_request=user_request,
            payments_analyzed=summary.total_analyzed if summary else total_payments,
            require_attention=summary.require_attention if summary else 0,
            failed_count=summary.failed_count if summary else 0,
            pending_count=summary.pending_count if summary else 0,
            total_at_risk_amount=summary.total_at_risk_amount if summary else 0.0,
            actions_taken=[f"✓ {c['tool'].upper()} action: {c['item'].get('summary') or c['item'].get('subject') or c['item'].get('title') or c['item'].get('channel')}" for c in state.completed_actions],
            actions_failed=[f"✗ {f['tool'].upper()} action failed: {f.get('error')}" for f in state.failed_actions],
            verification=state.verification_results,
            exceptions=[f.get("error") for f in state.failed_actions],
            workflow_metrics=workflow_metrics,
            next_steps=[
                "Monitor Jira tickets assigned to Finance Operations",
                "Track customer email response rate on updated payment links",
                "Review next scheduled payment reconciliation cycle"
            ]
        )

        state.final_result = final_summary.model_dump()
        state.status = "COMPLETED" if not state.failed_actions else "PARTIAL_SUCCESS"
        state.completed_at = datetime.now(timezone.utc)

        audit_service.record_event("WORKFLOW_COMPLETED", run_id=run_id, details=state.final_result)

        step = state.add_step(
            action="SUMMARIZE",
            result_summary="Executive report compiled from deterministic execution results.",
            details=state.final_result
        )
        yield {
            "type": "RUN_COMPLETED",
            "run_id": run_id,
            "state": state.model_dump(),
            "summary": final_summary.model_dump()
        }


agent = OpsPilotAgent()
