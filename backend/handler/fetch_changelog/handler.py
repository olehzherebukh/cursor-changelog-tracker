import json
import os
import sys
from typing import Dict, Any, List

import httpx
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.config import settings  # noqa: E402
from services.changelog_parser import ChangelogParser  # noqa: E402
from services.dynamodb_service import DynamoDBService  # noqa: E402
from services.email_service import EmailService  # noqa: E402

logger = Logger(service="fetch_changelog", level=settings.LOG_LEVEL)

dynamodb_service = DynamoDBService(
    table_name=settings.DYNAMODB_TABLE_NAME, region=settings.SES_REGION
)
email_service = EmailService(region=settings.SES_REGION)


def _process_new_versions(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process changelog entries and identify new versions that need notification.

    Args:
        entries: List of changelog entries to process

    Returns:
        List of new entries that need email notification
    """
    new_versions_to_notify = []

    for entry in entries:
        version_id = entry["id"]

        if dynamodb_service.is_version_notified(version_id):
            logger.info(f"Skipping already notified version: {version_id}")
            continue

        if dynamodb_service.mark_version_notified(version_id, entry):
            new_versions_to_notify.append(entry)
            logger.info(f"Added new version for notification: {version_id}")
        else:
            logger.error(f"Failed to mark version as notified: {version_id}")

    return new_versions_to_notify


def _send_email_notifications(entries: List[Dict[str, Any]]) -> int:
    """
    Send email notifications for new changelog entries.

    Args:
        entries: List of changelog entries to send notifications for

    Returns:
        Number of successful email notifications sent
    """
    successful_notifications = 0

    for entry in entries:
        try:
            success = email_service.send_changelog_notification(
                changelog_entry=entry,
                from_email=settings.SES_FROM_EMAIL,
                to_emails=settings.SES_TO_EMAILS,
            )

            if success:
                successful_notifications += 1
                logger.info(f"Email notification sent for version: {entry['id']}")
            else:
                logger.error(
                    f"Failed to send email notification for version: {entry['id']}"
                )

        except Exception as e:
            logger.error(f"Error sending email for version {entry['id']}: {e}")

    return successful_notifications


@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    AWS Lambda handler function for fetching and processing the Cursor changelog.

    Args:
        event: AWS Lambda event
        context: AWS Lambda context

    Returns:
        Response dictionary with status and results
    """
    logger.info("Starting changelog fetch process")

    try:
        logger.info(f"Fetching changelog from {settings.CHANGELOG_URL}")
        headers = {"User-Agent": settings.USER_AGENT}

        with httpx.Client(
            timeout=settings.REQUEST_TIMEOUT, follow_redirects=True
        ) as client:
            response = client.get(settings.CHANGELOG_URL, headers=headers)
            response.raise_for_status()

            html_content = response.text
            logger.info(
                f"Successfully fetched changelog page ({len(html_content)} bytes)"
            )

            parser = ChangelogParser()
            entries = parser.parse_changelog(html_content)
            logger.info(f"Parsed {len(entries)} changelog entries")

            new_versions = _process_new_versions(entries)
            logger.info(f"Found {len(new_versions)} new versions to notify")

            notifications_sent = _send_email_notifications(new_versions)
            logger.info(f"Sent {notifications_sent} email notifications")

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": "Changelog processing completed successfully",
                        "total_entries": len(entries),
                        "new_versions": len(new_versions),
                        "notifications_sent": notifications_sent,
                        "notified_versions": [entry["id"] for entry in new_versions],
                    }
                ),
            }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Failed to fetch changelog: {str(e)}"}),
        }

    except Exception as e:
        logger.error(f"Error processing changelog: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error processing changelog: {str(e)}"}),
        }
