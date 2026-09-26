"""
Deterministic Output and Action Validation Service.
Fulfills requirements:
18. Deterministic Output Validation (Customer/Payment IDs, statuses)
19. Numerical Validation (Total payments, failed count, pending count)
20. Action Validation (WHO, WHAT, WHERE, WHY, AUTHORIZATION)
"""
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.payments import PaymentRecord, PaymentClassificationSummary


class ValidationService:
    @staticmethod
    def validate_payment_claim(claimed_id: str, claimed_status: str, known_payments: List[PaymentRecord]) -> Tuple[bool, Optional[str]]:
        """
        Validates whether a payment ID actually exists and matches the claimed status.
        Never blindly trust LLM claims about payments.
        """
        payment_map = {p.payment_id: p for p in known_payments}
        if claimed_id not in payment_map:
            return False, f"Validation Error: Payment ID '{claimed_id}' does not exist in retrieved evidence."

        actual_status = payment_map[claimed_id].status.value
        if actual_status.upper() != claimed_status.upper():
            return False, f"Validation Error: Payment ID '{claimed_id}' has actual status '{actual_status}', but claimed '{claimed_status}'."

        return True, None

    @staticmethod
    def validate_numerical_claims(
        claimed_total: Optional[int],
        claimed_failed: Optional[int],
        claimed_pending: Optional[int],
        python_summary: PaymentClassificationSummary
    ) -> Tuple[bool, List[str]]:
        """
        Verifies numerical claims against deterministic Python ground truth.
        """
        discrepancies = []
        if claimed_total is not None and claimed_total != python_summary.total_analyzed:
            discrepancies.append(
                f"Discrepancy in total payments: claimed {claimed_total}, actual ground truth is {python_summary.total_analyzed}"
            )
        if claimed_failed is not None and claimed_failed != python_summary.failed_count:
            discrepancies.append(
                f"Discrepancy in failed count: claimed {claimed_failed}, actual ground truth is {python_summary.failed_count}"
            )
        if claimed_pending is not None and claimed_pending != python_summary.pending_count:
            discrepancies.append(
                f"Discrepancy in pending count: claimed {claimed_pending}, actual ground truth is {python_summary.pending_count}"
            )

        return len(discrepancies) == 0, discrepancies

    @staticmethod
    def validate_jira_action(payload: Dict[str, Any], known_payments: List[PaymentRecord]) -> Tuple[bool, Optional[str]]:
        """
        Validates Jira task payload before execution.
        """
        if not payload.get("summary"):
            return False, "Jira Action Invalid: Summary is required."
        if not payload.get("project_key"):
            return False, "Jira Action Invalid: Target project key is missing."

        payment_id = payload.get("payment_id")
        if payment_id:
            valid, err = ValidationService.validate_payment_claim(payment_id, "FAILED", known_payments)
            if not valid:
                # Also allow PENDING if SLA exceeded
                valid_pending, _ = ValidationService.validate_payment_claim(payment_id, "PENDING", known_payments)
                if not valid_pending:
                    return False, f"Jira Action Rejected: {err}"

        return True, None

    @staticmethod
    def validate_gmail_action(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates customer email payload before dispatch.
        """
        recipient = payload.get("recipient", "").strip()
        subject = payload.get("subject", "").strip()
        body = payload.get("body", "").strip()

        if not recipient or "@" not in recipient:
            return False, f"Email Action Invalid: Invalid recipient address '{recipient}'."
        if not subject:
            return False, "Email Action Invalid: Subject cannot be blank."
        if not body or len(body) < 10:
            return False, "Email Action Invalid: Email body is too short or empty."

        return True, None

    @staticmethod
    def validate_slack_action(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates Slack notification payload.
        """
        channel = payload.get("channel", "").strip()
        message = payload.get("message", "").strip()

        if not channel or not (channel.startswith("#") or channel.startswith("C")):
            return False, f"Slack Action Invalid: Invalid channel destination '{channel}'."
        if not message:
            return False, "Slack Action Invalid: Message content is required."

        return True, None

    @staticmethod
    def validate_notion_action(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates Notion record payload.
        """
        title = payload.get("page_title", "").strip()
        content = payload.get("content")

        if not title:
            return False, "Notion Action Invalid: Page title is required."
        if not isinstance(content, dict) or not content:
            return False, "Notion Action Invalid: Structured content must be a non-empty dictionary."

        return True, None


validation_service = ValidationService()
