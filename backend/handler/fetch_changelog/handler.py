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

logger = Logger(service="fetch_changelog", level=settings.LOG_LEVEL)

_changelog_entries = {}


def _store_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Store changelog entries with deduplication.

    Args:
        entries: List of changelog entries to store

    Returns:
        List of new entries that were stored
    """
    new_entries = []

    for entry in entries:
        entry_id = entry["id"]

        if entry_id in _changelog_entries:
            logger.info(f"Skipping existing entry: {entry_id}")
            continue

        _changelog_entries[entry_id] = entry
        new_entries.append(entry)
        logger.info(f"Stored new entry: {entry_id}")

    return new_entries


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

            new_entries = _store_entries(entries)
            logger.info(f"Stored {len(new_entries)} new changelog entries")

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": "Changelog processing completed successfully",
                        "total_entries": len(entries),
                        "new_entries": len(new_entries),
                        "entries": [entry["id"] for entry in new_entries],
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
