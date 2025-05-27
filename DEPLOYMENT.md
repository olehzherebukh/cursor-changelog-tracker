# Deployment Guide

This document provides instructions for deploying the Cursor Changelog Tracker application to AWS.

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.10.13 and Poetry installed

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
- AWS Region: Choose your preferred region
- Confirm changes before deployment: `Y`
- Allow SAM CLI to create IAM roles: `Y`
- Save arguments to samconfig.toml: `Y`

For subsequent deployments, you can simply use:

```bash
sam deploy
```

3. **Verify the deployment**

Check that the Lambda function and EventBridge rule have been created:

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'cursor-changelog-tracker')]"
aws events list-rules --query "Rules[?starts_with(Name, 'cursor-changelog-tracker')]"
```

## Monitoring

You can monitor the Lambda function executions in the AWS CloudWatch Logs:

```bash
# Get the function name
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'cursor-changelog-tracker')].FunctionName" --output text

# View the logs (replace FUNCTION_NAME with the actual function name)
aws logs get-log-events --log-group-name /aws/lambda/FUNCTION_NAME --limit 100
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

This will delete all resources created by the SAM template, including the Lambda function, IAM roles, and EventBridge rule.
