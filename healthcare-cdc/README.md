# Healthcare CDC Implementation

## Overview

This directory contains the complete Healthcare Change Data Capture (CDC) implementation based on the [Snowflake Healthcare CDC Quickstart](https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/).

## Directory Structure

```
healthcare-cdc/
├── __init__.py                           # Package initialization
├── README.md                             # This file
├── healthcare_cdc_domain_model.py        # Core domain model
├── test_healthcare_cdc_domain_model.py   # Unit tests
├── models/
│   └── healthcare-cdc-infrastructure.yaml # CloudFormation template
├── sql/
│   └── healthcare-cdc-schema.sql         # Snowflake schema
└── docs/
    └── HEALTHCARE_CDC_README.md          # Comprehensive documentation
```

## Quick Start

### 1. Import and Use

```python
from healthcare_cdc import HealthcareCDCDomainModel

# Create domain model
model = HealthcareCDCDomainModel()

# Generate infrastructure
template = model.generate_cloudformation_template()
schema = model.generate_snowflake_schema()

# Create sample claim
from healthcare_cdc import HealthcareClaim, PatientInfo, ProviderInfo, PayerInfo
# ... create claim data
```

### 2. Run Tests

```bash
cd healthcare-cdc
python -m pytest test_healthcare_cdc_domain_model.py -v
```

### 3. Deploy Infrastructure

```bash
# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name healthcare-cdc-demo \
  --template-body file://models/healthcare-cdc-infrastructure.yaml \
  --parameters ParameterKey=VpcId,ParameterValue=vpc-12345678 \
               ParameterKey=SubnetId,ParameterValue=subnet-12345678 \
  --capabilities CAPABILITY_NAMED_IAM
```

### 4. Setup Snowflake Schema

```sql
-- Run the schema creation script
source sql/healthcare-cdc-schema.sql
```

## Features

- ✅ **Real-time CDC Operations** (INSERT, MODIFY, REMOVE)
- ✅ **Healthcare-Specific Data Model** (patients, providers, payers)
- ✅ **Automated Infrastructure** (CloudFormation deployment)
- ✅ **Snowflake Integration** (tables, views, schemas)
- ✅ **Comprehensive Testing** (unit and integration tests)
- ✅ **Production Ready** (security, monitoring, documentation)

## Attribution

- **Original Contributors**: Snowflake Inc.
- **Enhanced by**: OpenFlow Playground Team
- **Source**: [Snowflake Healthcare CDC Quickstart](https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/)

## Documentation

See `docs/HEALTHCARE_CDC_README.md` for comprehensive documentation including:
- Architecture diagrams
- Data flow examples
- Troubleshooting guides
- Monitoring and observability
- Security considerations 