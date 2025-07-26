# Snowflake Openflow Quickstart

This guide will help you deploy Snowflake Openflow infrastructure in under 30 minutes.

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Snowflake account with admin access**
3. **Python 3.6+** (for the setup wizard)

## Step 1: Snowflake Setup (5 minutes)

**Contact Snowflake support** to get your Openflow configuration values.

Run these commands in your Snowflake account:

```sql
-- Create admin role for Openflow
CREATE ROLE IF NOT EXISTS OPENFLOW_ADMIN;
GRANT ACCOUNTADMIN TO ROLE OPENFLOW_ADMIN;

-- Grant required privileges
GRANT CREATE OPENFLOW DATA PLANE INTEGRATION ON ACCOUNT TO ROLE OPENFLOW_ADMIN;
GRANT CREATE OPENFLOW RUNTIME INTEGRATION ON ACCOUNT TO ROLE OPENFLOW_ADMIN;
GRANT CREATE OPENFLOW CONNECTOR ON ACCOUNT TO ROLE OPENFLOW_ADMIN;

-- Set up user
CREATE USER IF NOT EXISTS openflow_user PASSWORD = 'YourSecurePassword123!';
GRANT ROLE OPENFLOW_ADMIN TO USER openflow_user;
ALTER USER openflow_user SET DEFAULT_SECONDARY_ROLES = ('ALL');
```

## Step 2: Get Snowflake Values (5 minutes)

**Contact Snowflake** to obtain these required values:

- `SNOWFLAKE_OAUTH_INTEGRATION_NAME`: OAuth integration name
- `SNOWFLAKE_OAUTH_CLIENT_ID`: OAuth client ID
- `SNOWFLAKE_OAUTH_CLIENT_SECRET`: OAuth client secret
- `DATA_PLANE_URL`: Data plane URL (provided by Snowflake)
- `DATA_PLANE_UUID`: Data plane UUID (provided by Snowflake)
- `TELEMETRY_URL`: Telemetry URL (provided by Snowflake)
- `CONTROL_PLANE_URL`: Control plane URL (provided by Snowflake)

## Step 3: Interactive Setup (2 minutes)

**No more manual configuration!** Just run the setup wizard:

```bash
# Run the interactive setup wizard
./deploy.sh setup

# The wizard will prompt for all required values
# It validates the format and generates config.env automatically
```

**The wizard will ask for:**
- Your Snowflake account URL
- Your organization and account identifiers
- All OAuth credentials from Snowflake
- All Openflow URLs and UUIDs from Snowflake
- AWS region (optional, defaults to us-east-1)

## Step 4: Validate Configuration (1 minute)

```bash
# Validate your configuration
./deploy.sh validate

# This checks that all required values are set correctly
```

## Step 5: Deploy Infrastructure (15 minutes)

```bash
# Deploy the infrastructure
./deploy.sh deploy

# This creates all AWS resources and sets up Openflow
```

## Step 6: Verify Deployment (5 minutes)

1. **Check deployment status:**
   ```bash
   ./deploy.sh status
   ```

2. **Monitor resources:**
   ```bash
   ./monitor.sh
   ```

3. **Test connectors** in Snowflake console

## Troubleshooting

### Common Issues

**Setup wizard fails:**
- Ensure Python 3.6+ is installed
- Check that you have all required Snowflake values

**Deployment fails:**
- Run `./deploy.sh validate` to check configuration
- Ensure AWS CLI is configured with proper permissions
- Check that all Snowflake values are correct

**Configuration issues:**
- Run `./deploy.sh setup` to reconfigure
- Contact Snowflake support if you're missing values

### Useful Commands

```bash
# Check deployment status
./deploy.sh status

# Validate configuration
./deploy.sh validate

# Update deployment
./deploy.sh update

# Delete deployment
./deploy.sh delete

# Monitor resources
./monitor.sh
```

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Snowflake │    │   AWS Cloud │    │   Openflow  │
│   Account   │◄──►│   Resources │◄──►│   Agent     │
└─────────────┘    └─────────────┘    └─────────────┘
```

The deployment creates a complete Openflow environment that connects your AWS infrastructure to Snowflake for data integration and processing.

## Security

- ✅ **No hardcoded credentials** - All values are parameterized
- ✅ **Secure configuration** - Values stored in config.env (not committed)
- ✅ **Validation** - All inputs are validated before deployment
- ✅ **Automated setup** - No manual file editing required

## Next Steps

1. **Test connectors** in Snowflake console
2. **Configure data sources** in AWS
3. **Set up data pipelines** using Openflow
4. **Monitor performance** using the provided tools

## Documentation

- **Snowflake Openflow**: [Snowflake Openflow Docs](https://docs.snowflake.com/alias/openflow/setup-deployment)
- **AWS CloudFormation**: [AWS CloudFormation Docs](https://docs.aws.amazon.com/cloudformation/)
- **Security Framework**: See `.cursorrules` for security best practices

## Support

- **Snowflake Support**: Contact Snowflake for Openflow configuration
- **AWS Support**: Contact AWS for infrastructure issues
- **Security Issues**: Run `./scripts/security-check.sh` to validate

---

**Remember:** This setup wizard makes deployment easy and secure. No more manual configuration files! 