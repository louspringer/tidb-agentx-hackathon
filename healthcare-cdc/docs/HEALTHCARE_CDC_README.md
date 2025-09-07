# Healthcare CDC Implementation

## Overview

This implementation provides a complete **Change Data Capture (CDC) pipeline** for healthcare insurance claims processing, based on the [Snowflake Healthcare CDC Quickstart](https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/). The system synchronizes healthcare claims data between Amazon DynamoDB and Snowflake using Openflow in real-time.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DynamoDB      │    │   Kinesis Data   │    │   Openflow      │    │   Snowflake     │
│   (Front-end)   │───▶│   Streams        │───▶│   Connector     │───▶│   (Analytics)   │
│                 │    │                  │    │                 │    │                 │
│ • Real-time     │    │ • Event capture  │    │ • Data transform│    │ • Complex queries│
│ • High scale    │    │ • Stream process │    │ • CDC merge     │    │ • Reporting     │
│ • Flexible      │    │ • Buffer events  │    │ • Audit trail   │    │ • Data sharing  │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Components

### 1. Domain Model (`healthcare_cdc_domain_model.py`)
- **HealthcareClaim**: Complete claim data structure
- **CDCEvent**: Change data capture events (INSERT, MODIFY, REMOVE)
- **InfrastructureComponents**: AWS and Snowflake resource configuration
- **PipelineConfiguration**: Openflow pipeline setup

### 2. Infrastructure (`models/healthcare-cdc-infrastructure.yaml`)
- **DynamoDB Table**: `InsuranceClaims` with stream enabled
- **Kinesis Stream**: `InsuranceClaimsStream` for event capture
- **EC2 Instance**: Automated data ingestion and monitoring
- **IAM Roles**: Secure permissions for all components

### 3. Snowflake Schema (`sql/healthcare-cdc-schema.sql`)
- **Destination Table**: `openflow_insclaim_dest_tbl` (synchronized)
- **CDC Table**: `openflow_insclaim_cdc_tbl` (staging)
- **Event History**: `openflow_insclaim_event_hist_tbl` (audit)
- **Views**: Summary, recent events, pending claims

## Features

### ✅ Real-time CDC Operations
- **INSERT**: New claims automatically synchronized
- **MODIFY**: Claim updates propagated instantly
- **REMOVE**: Claim deletions reflected immediately

### ✅ Healthcare-Specific Data Model
- Patient information (demographics, contact)
- Provider details (NPI, location)
- Payer information (insurance company)
- Claim details (diagnosis codes, procedures)
- Status tracking (claim status, payment status)

### ✅ Automated Data Ingestion
- Python script generates realistic healthcare claims
- Continuous data flow simulation
- Monitoring and logging capabilities

### ✅ Audit and Compliance
- Complete event history tracking
- Timestamp-based audit trail
- Data lineage and traceability

## Quick Start

### 1. Deploy Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name healthcare-cdc-demo \
  --template-body file://models/healthcare-cdc-infrastructure.yaml \
  --parameters ParameterKey=VpcId,ParameterValue=vpc-12345678 \
               ParameterKey=SubnetId,ParameterValue=subnet-12345678 \
  --capabilities CAPABILITY_NAMED_IAM
```

### 2. Setup Snowflake Schema

```sql
-- Run the schema creation script
-- This creates databases, tables, and sample data
source sql/healthcare-cdc-schema.sql
```

### 3. Configure Openflow Pipeline

1. **Access Openflow Console**
2. **Create New Pipeline**: `HealthcareCDC`
3. **Add Processors**:
   - Kinesis Consumer
   - JSON Parser
   - Flat JSON
   - Jolt Transform
   - Route on Attribute
   - Put Database Record (3 instances)
   - Execute SQL Statement

### 4. Monitor the System

```bash
# Connect to EC2 instance
aws ssm start-session --target <instance-id>

# Check system status
/opt/healthcare-cdc/monitor.sh

# View logs
journalctl -u healthcare-cdc-ingestion.service -f
```

## Data Flow

### 1. Claim Creation
```python
# Sample claim data
claim = {
    "claim_id": "CLM-ABC123",
    "member_id": "M1001",
    "insurance_plan": "Premium PPO",
    "diagnosis_codes": ["E11.9", "I10"],
    "total_charge": 2500.00,
    "claim_status": "Pending",
    "patient": {...},
    "provider": {...},
    "payer": {...}
}
```

### 2. DynamoDB Stream Capture
- Changes automatically captured
- Stream events sent to Kinesis
- Real-time event processing

### 3. Openflow Processing
- **Parse JSON**: Extract event data
- **Flat JSON**: Flatten nested structures
- **Jolt Transform**: Standardize data format
- **Route Events**: Direct to appropriate tables
- **Database Records**: Insert into Snowflake tables
- **SQL Merge**: Synchronize destination table

### 4. Snowflake Analytics
```sql
-- Query recent claims
SELECT * FROM v_healthcare_claims_summary 
WHERE claimStatus = 'Pending'
ORDER BY eventCreationUTC DESC;

-- Analyze claim trends
SELECT 
    claimStatus,
    COUNT(*) as claim_count,
    AVG(totalCharge) as avg_charge
FROM openflow_insclaim_dest_tbl
GROUP BY claimStatus;
```

## Monitoring and Observability

### AWS CloudWatch Metrics
- DynamoDB table metrics
- Kinesis stream metrics
- EC2 instance metrics

### Snowflake Query History
```sql
-- Monitor query performance
SELECT 
    query_text,
    execution_time,
    bytes_scanned
FROM table(information_schema.query_history())
WHERE query_text LIKE '%openflow_insclaim%'
ORDER BY start_time DESC;
```

### Openflow Pipeline Monitoring
- Queue depths and throughput
- Processor status and errors
- Data transformation logs

## Security Considerations

### ✅ Data Encryption
- DynamoDB streams encrypted at rest
- Kinesis streams with KMS encryption
- Snowflake data encrypted in transit and at rest

### ✅ Access Control
- IAM roles with least privilege
- Snowflake role-based access control
- Network security groups

### ✅ Audit Logging
- Complete event history
- Change tracking and traceability
- Compliance-ready audit trail

## Performance Optimization

### DynamoDB
- On-demand billing for variable workloads
- Stream enabled for real-time CDC
- Efficient key schema design

### Kinesis
- Single shard for demo (scale as needed)
- KMS encryption for security
- Real-time stream processing

### Snowflake
- Small warehouse for cost optimization
- Auto-suspend/resume for efficiency
- Optimized table structure

## Troubleshooting

### Common Issues

1. **DynamoDB Stream Not Capturing**
   ```bash
   # Check stream status
   aws dynamodb describe-table --table-name InsuranceClaims
   ```

2. **Kinesis Stream Errors**
   ```bash
   # Verify stream exists
   aws kinesis describe-stream --stream-name InsuranceClaimsStream
   ```

3. **Openflow Pipeline Issues**
   - Check processor status in Openflow console
   - Verify Snowflake connection
   - Review error logs

4. **Snowflake Connection Problems**
   ```sql
   -- Test connection
   SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE();
   ```

## Attribution

This implementation is based on the [Snowflake Healthcare CDC Quickstart](https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/) with the following enhancements:

- **Original Contributors**: Snowflake Inc.
- **Enhanced by**: OpenFlow Playground Team
- **Improvements**:
  - Comprehensive domain model
  - Automated infrastructure deployment
  - Enhanced monitoring and observability
  - Production-ready security practices
  - Detailed documentation and examples

## License

Copyright (c) 2025 Snowflake Inc. All rights reserved.
This software is proprietary and may not be disclosed to third parties without the express written consent of Snowflake Inc.
Any unauthorized reproduction, distribution, modification, or use is strictly prohibited.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs and metrics
3. Consult Snowflake documentation
4. Open an issue in this repository 