# Cursor Changelog Tracker

A serverless application to track the Cursor changelog using AWS SAM.

## Overview

This application periodically scrapes the [Cursor changelog page](https://www.cursor.com/changelog) and stores new changelog entries in a structured format. It runs as a scheduled AWS Lambda function that executes daily at 07:00 UTC.

## Features

- Scheduled AWS Lambda function that runs daily
- Scrapes and parses the Cursor changelog page
- Extracts structured data (date, title, description, tags)
- Stores entries with basic deduplication
- Configurable via environment variables

## Project Structure

```
backend/
  handler/
    fetch_changelog/
      handler.py      # Lambda function code
  services/
    changelog_parser.py  # Logic for extracting data from HTML
  core/
    config.py         # Configuration using pydantic-settings
tests/
  test_fetch_changelog.py  # Unit tests
template.yaml         # AWS SAM template
.env                  # Environment variables
.pre-commit-config.yaml  # Pre-commit hook definitions
pyproject.toml        # Poetry project configuration
```

## Setup

### Prerequisites

- Python 3.10.13
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   poetry install
   ```
3. Set up pre-commit hooks:
   ```
   poetry run pre-commit install
   ```

## Local Development

### Running Tests

```
poetry run pytest
```

### Testing the Lambda Function Locally

```
sam local invoke FetchChangelogFunction
```

### Simulating the Scheduled Event

```
sam local start-schedule
```

## Deployment

```
sam build
sam deploy --guided
```

## Configuration

Configuration is managed through environment variables, which can be set in the `.env` file for local development or in the AWS Lambda configuration for deployment.

Key environment variables:
- `CHANGELOG_URL`: URL of the Cursor changelog page
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `STORAGE_TYPE`: Type of storage to use (memory, file, etc.)

## License

MIT
