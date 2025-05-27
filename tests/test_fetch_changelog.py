import json
import pytest
from unittest.mock import patch, MagicMock

from backend.handler.fetch_changelog.handler import lambda_handler
from backend.services.changelog_parser import ChangelogParser


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <main>
        <section>
            <article>
                May 15, 20250.50
                <h2>
                    <span>Simplified Pricing, Background Agent and Refreshed Inline Edit</span>
                </h2>
                Introducing unified request-based pricing, Max Mode for all top models, and Background Agent for parallel task execution.
                <h3>Simpler, unified pricing</h3>
                We've heard your feedback and are rolling out a unified pricing model to make it less confusing.
            </article>
            <article>
                April 15, 20250.49
                <h2>
                    <span>Rules generation, improved agent terminal and MCP images</span>
                </h2>
                <h3>Automated and improved rules</h3>
                You can now generate rules directly from a conversation.
            </article>
        </section>
    </main>
    """


def test_changelog_parser(sample_html):
    """Test the changelog parser with sample HTML."""
    parser = ChangelogParser()
    entries = parser.parse_changelog(sample_html)

    assert len(entries) == 2
    assert entries[0]["date"] == "2025-05-15"
    assert entries[0]["version"] == "0.50"
    assert "Simplified Pricing" in entries[0]["title"]
    assert "unified request-based pricing" in entries[0]["description"]
    assert "Simpler, unified pricing" in entries[0]["tags"]

    assert entries[1]["date"] == "2025-04-15"
    assert entries[1]["version"] == "0.49"
    assert "Rules generation" in entries[1]["title"]


@patch("httpx.Client")
@patch("backend.handler.fetch_changelog.handler.dynamodb_service")
@patch("backend.handler.fetch_changelog.handler.email_service")
def test_lambda_handler_with_new_versions(
    mock_email_service, mock_dynamodb_service, mock_client, sample_html
):
    """Test the Lambda handler function with new versions."""
    mock_response = MagicMock()
    mock_response.text = sample_html
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    mock_dynamodb_service.is_version_notified.return_value = False
    mock_dynamodb_service.mark_version_notified.return_value = True

    mock_email_service.send_changelog_notification.return_value = True

    event = {}
    context = MagicMock()
    response = lambda_handler(event, context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["total_entries"] == 2
    assert body["new_versions"] == 2
    assert body["notifications_sent"] == 2


@patch("httpx.Client")
@patch("backend.handler.fetch_changelog.handler.dynamodb_service")
@patch("backend.handler.fetch_changelog.handler.email_service")
def test_lambda_handler_with_existing_versions(
    mock_email_service, mock_dynamodb_service, mock_client, sample_html
):
    """Test the Lambda handler function with already notified versions."""
    mock_response = MagicMock()
    mock_response.text = sample_html
    mock_response.raise_for_status = MagicMock()

    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance

    mock_dynamodb_service.is_version_notified.return_value = True

    event = {}
    context = MagicMock()
    response = lambda_handler(event, context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["total_entries"] == 2
    assert body["new_versions"] == 0
    assert body["notifications_sent"] == 0

    mock_email_service.send_changelog_notification.assert_not_called()
