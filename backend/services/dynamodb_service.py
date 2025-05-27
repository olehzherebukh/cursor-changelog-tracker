import boto3
from typing import Dict, Any
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

logger = Logger(service="dynamodb_service")


class DynamoDBService:
    """Service for managing DynamoDB operations for version tracking."""

    def __init__(self, table_name: str, region: str = "us-east-1"):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def is_version_notified(self, version_id: str) -> bool:
        """
        Check if a version has already been notified.

        Args:
            version_id: The version ID to check

        Returns:
            True if version was already notified, False otherwise
        """
        try:
            response = self.table.get_item(Key={"version_id": version_id})
            exists = "Item" in response
            logger.info(
                f"Version {version_id} notification status: {'already sent' if exists else 'not sent'}"
            )
            return exists
        except ClientError as e:
            logger.error(f"Error checking version notification status: {e}")
            return False

    def mark_version_notified(
        self, version_id: str, changelog_entry: Dict[str, Any]
    ) -> bool:
        """
        Mark a version as notified in DynamoDB.

        Args:
            version_id: The version ID to mark as notified
            changelog_entry: The full changelog entry data

        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.put_item(
                Item={
                    "version_id": version_id,
                    "notified_at": changelog_entry.get("date"),
                    "version": changelog_entry.get("version"),
                    "title": changelog_entry.get("title"),
                    "description": changelog_entry.get("description", "")[
                        :1000
                    ],  # Limit description length
                }
            )
            logger.info(f"Marked version {version_id} as notified")
            return True
        except ClientError as e:
            logger.error(f"Error marking version as notified: {e}")
            return False
