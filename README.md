# OpenFlow Playground

A comprehensive playground for setting up and experimenting with Snowflake Openflow infrastructure.

## Overview

This project contains a CloudFormation template that automates the deployment of Snowflake Openflow infrastructure on AWS. The template creates all necessary AWS resources including VPC, networking, IAM roles, and an EC2 instance that automatically sets up the Openflow agent.

## Security Notice

⚠️ **IMPORTANT**: This template requires you to provide your own Snowflake-specific values. All hardcoded credentials and account-specific data have been removed for security.

## Prerequisites

### Snowflake Account Setup

Before deploying the infrastructure, you need to set up your Snowflake account:

1. **Create Image Repository**:
```sql
USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS OPENFLOW;
USE OPENFLOW;
CREATE SCHEMA IF NOT EXISTS OPENFLOW;
USE SCHEMA OPENFLOW;
CREATE IMAGE REPOSITORY IF NOT EXISTS OPENFLOW;
GRANT USAGE ON DATABASE OPENFLOW TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA OPENFLOW TO ROLE PUBLIC;
GRANT READ ON IMAGE REPOSITORY OPENFLOW.OPENFLOW.OPENFLOW TO ROLE PUBLIC;
```

2. **Grant Openflow Privileges**:
```sql
-- Replace $OPENFLOW_ADMIN_ROLE with your admin role name
GRANT CREATE OPENFLOW DATA PLANE INTEGRATION ON ACCOUNT TO ROLE $OPENFLOW_ADMIN_ROLE;
GRANT CREATE OPENFLOW RUNTIME INTEGRATION ON ACCOUNT TO ROLE $OPENFLOW_ADMIN_ROLE;
```

3. **Configure User Roles**:
```sql
-- Replace $OPENFLOW_USER with your user name
ALTER USER $OPENFLOW_USER SET DEFAULT_SECONDARY_ROLES = ('ALL');
```

### AWS Requirements

- AWS CLI installed and configured with appropriate permissions
- CloudFormation permissions
- IAM permissions for creating roles and policies

## Configuration

### Required Values from Snowflake

You must obtain these values from Snowflake and configure them:

1. **Copy the example configuration**:
   ```bash
   cp config.env.example config.env
   ```

2. **Edit `config.env` with your Snowflake values**:
   ```bash
   nano config.env
   ```

   **Required Snowflake Values** (obtain from Snowflake):
   - `SNOWFLAKE_ACCOUNT_URL`: Your Snowflake account URL
   - `SNOWFLAKE_ORGANIZATION`: Your Snowflake organization
   - `SNOWFLAKE_ACCOUNT`: Your Snowflake account identifier
   - `SNOWFLAKE_OAUTH_INTEGRATION_NAME`: OAuth integration name
   - `SNOWFLAKE_OAUTH_CLIENT_ID`: OAuth client ID
   - `SNOWFLAKE_OAUTH_CLIENT_SECRET`: OAuth client secret
   - `DATA_PLANE_URL`: Data plane URL (provided by Snowflake)
   - `DATA_PLANE_UUID`: Data plane UUID (provided by Snowflake)
   - `TELEMETRY_URL`: Telemetry URL (provided by Snowflake)
   - `CONTROL_PLANE_URL`: Control plane URL (provided by Snowflake)

   **Your Values**:
   - `DATA_PLANE_KEY`: A unique identifier for your deployment

## Deployment

### Option 1: Automated Deployment

```bash
# Validate configuration first
./deploy.sh validate

# Deploy the infrastructure
./deploy.sh deploy

# Monitor deployment
./monitor.sh all
```

### Option 2: Manual Deployment

```bash
# Deploy the CloudFormation stack
aws cloudformation create-stack \
  --stack-name openflow-playground \
  --template-body file://models/Openflow-Playground.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=SnowflakeAccountURL,ParameterValue="https://your-account.snowflakecomputing.com" \
  --parameters ParameterKey=SnowflakeOrganization,ParameterValue="YOUR_ORG" \
  --parameters ParameterKey=SnowflakeAccount,ParameterValue="YOUR_ACCOUNT" \
  # ... (add all required parameters)

# Monitor deployment
aws cloudformation describe-stacks --stack-name openflow-playground
```

## Architecture

The CloudFormation template creates:

- **VPC**: Custom VPC with public and private subnets
- **Networking**: NAT Gateway, Internet Gateway, and routing tables
- **IAM**: Roles and policies for Openflow agent
- **EC2 Instance**: Agent instance that automatically sets up Openflow
- **S3 Bucket**: For Terraform state management
- **Secrets Manager**: For OAuth2 credentials

## Monitoring

### Check Deployment Status

```bash
# Check all components
./monitor.sh all

# Check specific components
./monitor.sh stack
./monitor.sh instances
./monitor.sh eks
```

### View Logs

The EC2 instance runs setup scripts that you can monitor:

```bash
# Check instance logs (if accessible)
aws ec2-instance-connect send-ssh-public-key \
  --instance-id <instance-id> \
  --availability-zone <az> \
  --instance-os-user ec2-user \
  --ssh-public-key file://~/.ssh/id_rsa.pub
```

## Configuration Management

### Security Best Practices

1. **Never commit `config.env`** - it contains sensitive data
2. **Use environment variables** for production deployments
3. **Rotate OAuth credentials** regularly
4. **Use AWS Secrets Manager** for sensitive values in production

### Environment-Specific Configuration

```bash
# Development
cp config.env.example config.dev.env
# Edit with development values

# Production
cp config.env.example config.prod.env
# Edit with production values

# Use specific config
SNOWFLAKE_ACCOUNT_URL=https://your-account.snowflakecomputing.com ./deploy.sh deploy
```

## Troubleshooting

### Common Issues

1. **Missing Required Parameters**:
   ```bash
   ./deploy.sh validate
   ```
   This will show which parameters are missing.

2. **Stack creation fails**:
   ```bash
   aws cloudformation describe-stack-events --stack-name openflow-playground
   ```

3. **Instance not starting**:
   ```bash
   ./monitor.sh instances
   ```

### Useful Commands

```bash
# Validate everything before deployment
./deploy.sh validate

# Check deployment status
./monitor.sh all

# View stack events
aws cloudformation describe-stack-events --stack-name openflow-playground

# Update stack with new configuration
./deploy.sh update
```

## Cleanup

To remove all resources:

```bash
./deploy.sh delete
```

## Next Steps

After successful deployment:

1. **Test connectors** in Snowflake console
2. **Create data flows** using the available connectors
3. **Monitor performance** and costs
4. **Scale resources** as needed

## Support

- **Documentation**: [Snowflake Openflow Docs](https://docs.snowflake.com/alias/openflow/setup-deployment)
- **Issues**: Check CloudFormation events for detailed error messages
- **Logs**: Use `./monitor.sh logs` for log locations

## Security Improvements

This template has been secured by:

- ✅ **Removed all hardcoded credentials**
- ✅ **Made all Snowflake-specific parameters required**
- ✅ **Added parameter validation**
- ✅ **Improved error handling**
- ✅ **Added configuration validation**
- ✅ **Separated secrets from infrastructure**
