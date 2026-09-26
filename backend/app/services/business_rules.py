"""
Deterministic Python Business Rules Engine for OpsPilot AI.
ZERO LLM ARITHMETIC:
All calculations, payment classification, priorities, SLA logic,
and task requirements are strictly computed in deterministic Python code.
"""
from typing import List, Dict, Any, Tuple
from app.schemas.payments import (
    PaymentRecord, PaymentStatus, PriorityLevel, PaymentClassificationSummary
)
from app.utils.config import settings


class BusinessRulesEngine:
    @staticmethod
    def classify_payment(payment: PaymentRecord) -> PaymentRecord:
        """
        Applies deterministic business logic to a single payment record.
        """
        # Rules:
        # COMPLETED -> No follow-up needed
        if payment.status == PaymentStatus.COMPLETED:
            payment.requires_action = False
            payment.priority = PriorityLevel.LOW
            payment.recommended_action = "None - Payment successfully settled."
            return payment

        # PENDING -> Check SLA / Age
        if payment.status == PaymentStatus.PENDING:
            if payment.age_days >= settings.SLA_PENDING_DAYS_THRESHOLD:
                payment.requires_action = True
                if payment.age_days >= 7 or payment.amount >= settings.CRITICAL_AMOUNT_THRESHOLD:
                    payment.priority = PriorityLevel.HIGH
                    payment.recommended_action = f"Escalate pending payment ({payment.age_days}d old) for customer outreach."
                else:
                    payment.priority = PriorityLevel.MEDIUM
                    payment.recommended_action = f"Monitor pending settlement ({payment.age_days}d old) and verify payment gateway status."
            else:
                payment.requires_action = False
                payment.priority = PriorityLevel.LOW
                payment.recommended_action = f"Within standard grace period ({payment.age_days}d old)."
            return payment

        # FAILED -> Always requires action
        if payment.status == PaymentStatus.FAILED:
            payment.requires_action = True
            # Enterprise customer or high dollar value -> CRITICAL
            if payment.tier.lower() == "enterprise" or payment.amount >= settings.CRITICAL_AMOUNT_THRESHOLD:
                payment.priority = PriorityLevel.CRITICAL
                payment.recommended_action = f"Immediate executive escalation: Enterprise/High-value failed payment of ${payment.amount:.2f}."
            elif payment.amount >= 200.0 or payment.age_days >= 2:
                payment.priority = PriorityLevel.HIGH
                payment.recommended_action = f"Standard finance escalation: Failed payment of ${payment.amount:.2f} requires retry and customer notice."
            else:
                payment.priority = PriorityLevel.MEDIUM
                payment.recommended_action = f"Automated customer retry and payment method update notice."
            return payment

        return payment

    @staticmethod
    def classify_batch(payments: List[PaymentRecord]) -> Tuple[List[PaymentRecord], PaymentClassificationSummary]:
        """
        Classifies an entire batch of payments and computes deterministic aggregates.
        """
        processed_payments = []
        total_analyzed = len(payments)
        require_attention = 0
        failed_count = 0
        pending_count = 0
        completed_count = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        total_at_risk_amount = 0.0
        affected_customers = []

        for p in payments:
            classified = BusinessRulesEngine.classify_payment(p)
            processed_payments.append(classified)

            if classified.status == PaymentStatus.FAILED:
                failed_count += 1
            elif classified.status == PaymentStatus.PENDING:
                pending_count += 1
            elif classified.status == PaymentStatus.COMPLETED:
                completed_count += 1

            if classified.requires_action:
                require_attention += 1
                total_at_risk_amount += classified.amount
                if classified.customer_name not in affected_customers:
                    affected_customers.append(classified.customer_name)

                if classified.priority == PriorityLevel.CRITICAL:
                    critical_count += 1
                elif classified.priority == PriorityLevel.HIGH:
                    high_count += 1
                elif classified.priority == PriorityLevel.MEDIUM:
                    medium_count += 1
            else:
                low_count += 1

        summary = PaymentClassificationSummary(
            total_analyzed=total_analyzed,
            require_attention=require_attention,
            failed_count=failed_count,
            pending_count=pending_count,
            completed_count=completed_count,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            total_at_risk_amount=round(total_at_risk_amount, 2),
            affected_customers=affected_customers
        )

        return processed_payments, summary

    @staticmethod
    def determine_jira_tasks(payments: List[PaymentRecord]) -> List[Dict[str, Any]]:
        """
        Generates deterministic Jira task payloads for all payments requiring finance operational attention.
        """
        tasks = []
        for p in payments:
            if p.requires_action:
                tasks.append({
                    "project_key": settings.JIRA_PROJECT_KEY,
                    "summary": f"[FIN-OPS] Resolve {p.status.value} payment {p.payment_id} for {p.customer_name} (${p.amount:.2f})",
                    "description": (
                        f"Customer: {p.customer_name} ({p.customer_email})\n"
                        f"Amount: ${p.amount:.2f} {p.currency}\n"
                        f"Status: {p.status.value}\n"
                        f"Reason: {p.failure_reason or 'Pending SLA Exceeded'}\n"
                        f"Priority: {p.priority.value}\n"
                        f"Recommended Action: {p.recommended_action}"
                    ),
                    "priority": p.priority.value,
                    "payment_id": p.payment_id,
                    "assignee": "finance-ops@company.internal"
                })
        return tasks

    @staticmethod
    def determine_customer_emails(payments: List[PaymentRecord]) -> List[Dict[str, Any]]:
        """
        Generates deterministic customer notification email payloads for payments requiring customer action.
        """
        emails = []
        for p in payments:
            if p.requires_action and p.status in [PaymentStatus.FAILED, PaymentStatus.PENDING]:
                if p.status == PaymentStatus.FAILED:
                    subject = f"Action Required: Payment Update for {p.payment_id}"
                    body = (
                        f"Dear {p.customer_name},\n\n"
                        f"We noticed that your recent payment of ${p.amount:.2f} (Ref: {p.payment_id}) could not be completed "
                        f"due to: {p.failure_reason or 'payment processing issue'}.\n\n"
                        f"Please review your billing details or update your payment method to ensure uninterrupted service.\n\n"
                        f"Thank you,\nFinance Operations Team"
                    )
                else:
                    subject = f"Notice: Pending Payment Update ({p.payment_id})"
                    body = (
                        f"Dear {p.customer_name},\n\n"
                        f"Your transaction of ${p.amount:.2f} (Ref: {p.payment_id}) has been pending settlement for {p.age_days} days.\n"
                        f"Please verify authorization with your banking provider.\n\n"
                        f"Warm regards,\nFinance Operations Team"
                    )

                emails.append({
                    "recipient": p.customer_email,
                    "customer_name": p.customer_name,
                    "subject": subject,
                    "body": body,
                    "payment_id": p.payment_id
                })
        return emails

    @staticmethod
    def determine_slack_notification(summary: PaymentClassificationSummary, run_id: str) -> Dict[str, Any]:
        """
        Generates deterministic Slack alert payload for the internal operations channel.
        """
        severity = "CRITICAL" if summary.critical_count > 0 else "HIGH" if summary.high_count > 0 else "INFO"
        msg = (
            f":warning: *OpsPilot AI Business Incident Alert* (Run ID: `{run_id}`)\n\n"
            f"• *Payments Analyzed:* {summary.total_analyzed}\n"
            f"• *Requiring Attention:* {summary.require_attention} (Failed: {summary.failed_count}, Pending: {summary.pending_count})\n"
            f"• *Total At-Risk Exposure:* ${summary.total_at_risk_amount:,.2f} USD\n"
            f"• *Severity Breakdown:* Critical: {summary.critical_count} | High: {summary.high_count} | Medium: {summary.medium_count}\n"
            f"• *Affected Entities:* {', '.join(summary.affected_customers) if summary.affected_customers else 'None'}\n\n"
            f"Automated follow-ups and Jira tickets have been queued for ops resolution."
        )
        return {
            "channel": settings.SLACK_CHANNEL_DEFAULT,
            "message": msg,
            "severity": severity,
            "incident_id": run_id
        }

    @staticmethod
    def determine_notion_record(summary: PaymentClassificationSummary, run_id: str, timestamp_str: str) -> Dict[str, Any]:
        """
        Generates deterministic Notion page payload for business operations records.
        """
        return {
            "page_title": f"Operations Run - Payment Reconciliation ({run_id})",
            "category": "Payment Operations",
            "content": {
                "run_id": run_id,
                "timestamp": timestamp_str,
                "total_analyzed": summary.total_analyzed,
                "require_attention": summary.require_attention,
                "failed_count": summary.failed_count,
                "pending_count": summary.pending_count,
                "completed_count": summary.completed_count,
                "total_at_risk_amount": summary.total_at_risk_amount,
                "critical_incidents": summary.critical_count,
                "affected_customers": summary.affected_customers,
                "status": "PROCESSED"
            }
        }


business_rules = BusinessRulesEngine()
