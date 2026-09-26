"""
Verification Service for OpsPilot AI.
Fulfills requirement 23:
Every external action must produce deterministic evidence of successful execution.
"""
from typing import Dict, Any, List, Tuple


class VerificationService:
    @staticmethod
    def verify_jira_task(task_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies that Jira created an issue with an issue key.
        """
        if task_result.get("success") and task_result.get("issue_key"):
            return True, f"Verified Jira task creation: {task_result.get('issue_key')}"
        return False, f"Failed Jira verification: {task_result.get('error', 'Missing issue key')}"

    @staticmethod
    def verify_gmail_dispatch(email_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies customer email dispatch with message ID.
        """
        if email_result.get("success") and email_result.get("message_id"):
            return True, f"Verified email dispatched to {email_result.get('recipient')} (MsgID: {email_result.get('message_id')})"
        return False, f"Failed email verification: {email_result.get('error', 'Missing message ID')}"

    @staticmethod
    def verify_slack_notification(slack_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies Slack notification with channel message timestamp.
        """
        if slack_result.get("success") and slack_result.get("message_ts"):
            return True, f"Verified Slack message posted to {slack_result.get('channel')} at TS: {slack_result.get('message_ts')}"
        return False, f"Failed Slack verification: {slack_result.get('error', 'Missing message TS')}"

    @staticmethod
    def verify_notion_update(notion_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies Notion business record creation with page ID.
        """
        if notion_result.get("success") and notion_result.get("page_id"):
            return True, f"Verified Notion record updated (PageID: {notion_result.get('page_id')})"
        return False, f"Failed Notion verification: {notion_result.get('error', 'Missing page ID')}"

    @staticmethod
    def compile_verification_report(actions_verified: List[str], actions_failed: List[str]) -> Dict[str, Any]:
        """
        Compiles the holistic verification audit.
        """
        total = len(actions_verified) + len(actions_failed)
        if total == 0:
            status = "NO_ACTIONS_REQUIRED"
        elif len(actions_failed) == 0:
            status = "ALL_ACTIONS_VERIFIED_SUCCESSFUL"
        elif len(actions_verified) > 0:
            status = "PARTIAL_SUCCESS"
        else:
            status = "ALL_ACTIONS_FAILED"

        return {
            "status": status,
            "total_actions": total,
            "verified_count": len(actions_verified),
            "failed_count": len(actions_failed),
            "verified_items": actions_verified,
            "failed_items": actions_failed
        }


verification_service = VerificationService()
