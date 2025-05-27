# Deployment Guide

This document provides instructions for deploying the Cursor Changelog Tracker application to AWS.

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.10.13 and Poetry installed
- AWS SES verified email address for sending notifications
- Permissions to create DynamoDB tables and use SES

## AWS Service Setup

### 1. Verify SES Email Address

Before deploying, you need to verify the email address that will be used to send notifications:

```bash
# Verify the sender email address
aws ses verify-email-identity --email-address your-sender-email@example.com
```

Check your email and follow the verification link.

### 2. Update Environment Variables

Update the `.env` file with your verified email address:

```
SES_FROM_EMAIL=your-verified-email@example.com
SES_TO_EMAILS=["oleh.zherebukh@inoxoft.com", "ruslan.pitula@inoxoft.com"]
```

## Deployment Steps

1. **Build the application**

```bash
sam build
```

2. **Deploy the application to AWS**

For first-time deployment, use the guided deployment:

```bash
sam deploy --guided
```

Follow the prompts to configure your deployment:
- Stack Name: `cursor-changelog-tracker`
- AWS Region: Choose your preferred region (ensure it's the same region where you verified your SES email)
- Confirm changes before deployment: `Y`
- Allow SAM CLI to create IAM roles: `Y`
- Save arguments to samconfig.toml: `Y`

For subsequent deployments, you can simply use:

```bash
sam deploy
```

3. **Verify the deployment**

Check that all resources have been created:

```bash
# Check Lambda function
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'cursor-changelog-tracker')]"

# Check EventBridge rule
aws events list-rules --query "Rules[?starts_with(Name, 'cursor-changelog-tracker')]"

# Check DynamoDB table
aws dynamodb describe-table --table-name cursor-changelog-versions
```

## Monitoring

You can monitor the Lambda function executions in the AWS CloudWatch Logs:

```bash
# Get the function name
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'cursor-changelog-tracker')].FunctionName" --output text

# View the logs (replace FUNCTION_NAME with the actual function name)
aws logs get-log-events --log-group-name /aws/lambda/FUNCTION_NAME --limit 100
```

To check the DynamoDB table contents:

```bash
aws dynamodb scan --table-name cursor-changelog-versions
```

## Testing

To manually trigger the Lambda function:

```bash
# Get the function name
FUNCTION_NAME=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'cursor-changelog-tracker')].FunctionName" --output text)

# Invoke the function
aws lambda invoke --function-name $FUNCTION_NAME --payload '{}' /tmp/output.json
```

## Updating the Application

To update the application after making changes:

1. Make your changes to the code
2. Run tests to ensure everything works correctly
3. Build and deploy the updated application:

```bash
sam build && sam deploy
```

## Cleanup

To remove the application from AWS:

```bash
sam delete
```

This will delete all resources created by the SAM template, including the Lambda function, DynamoDB table, IAM roles, and EventBridge rule.
