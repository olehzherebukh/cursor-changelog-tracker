import boto3
from typing import List, Dict, Any
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

logger = Logger(service="email_service")


class EmailService:
    """Service for sending email notifications via AWS SES."""

    def __init__(self, region: str = "us-east-1"):
        self.ses_client = boto3.client("ses", region_name=region)

    def send_changelog_notification(
        self, changelog_entry: Dict[str, Any], from_email: str, to_emails: List[str]
    ) -> bool:
        """
        Send changelog notification email.

        Args:
            changelog_entry: The changelog entry to send
            from_email: Sender email address
            to_emails: List of recipient email addresses

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = f"New Cursor Update: {changelog_entry.get('title', 'Version ' + changelog_entry.get('version', 'Unknown'))}"

            html_body = self._create_html_email_body(changelog_entry)
            text_body = self._create_text_email_body(changelog_entry)

            response = self.ses_client.send_email(
                Source=from_email,
                Destination={"ToAddresses": to_emails},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                    },
                },
            )

            logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")
            return True

        except ClientError as e:
            logger.error(f"Error sending email: {e}")
            return False

    def _create_html_email_body(self, changelog_entry: Dict[str, Any]) -> str:
        """Create HTML email body for changelog notification."""
        version = changelog_entry.get("version", "Unknown")
        title = changelog_entry.get("title", "New Update")
        date = changelog_entry.get("date", "Unknown date")
        description = changelog_entry.get("description", "No description available")
        tags = ", ".join(changelog_entry.get("tags", []))

        return f"""
        <html>
        <body>
            <h2>🚀 New Cursor Update Available!</h2>
            <h3>Version {version} - {title}</h3>
            <p><strong>Release Date:</strong> {date}</p>
            <p><strong>Description:</strong></p>
            <p>{description}</p>
            {f'<p><strong>Features:</strong> {tags}</p>' if tags else ''}
            <hr>
            <p><small>You received this notification because you're subscribed to Cursor changelog updates.</small></p>
        </body>
        </html>
        """

    def _create_text_email_body(self, changelog_entry: Dict[str, Any]) -> str:
        """Create plain text email body for changelog notification."""
        version = changelog_entry.get("version", "Unknown")
        title = changelog_entry.get("title", "New Update")
        date = changelog_entry.get("date", "Unknown date")
        description = changelog_entry.get("description", "No description available")
        tags = ", ".join(changelog_entry.get("tags", []))

        return f"""
🚀 New Cursor Update Available!

Version {version} - {title}
Release Date: {date}

Description:
{description}

{f'Features: {tags}' if tags else ''}

---
You received this notification because you're subscribed to Cursor changelog updates.
        """
