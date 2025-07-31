-- Healthcare CDC Snowflake Schema
-- Based on: https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/
-- Original Contributors: Snowflake Inc.
-- Enhanced by: OpenFlow Playground Team

-- Set variables for the healthcare CDC setup
SET DB = 'CDC_DB';
SET SCHEMA = 'CDC_SCHEMA';
SET WH = 'CDC_WH';
SET ROLE = 'CDC_RL';

-- Create role and grant permissions
USE ROLE ACCOUNTADMIN;

-- CREATE ROLES
CREATE OR REPLACE ROLE IDENTIFIER($ROLE);

-- CREATE DATABASE AND WAREHOUSE
CREATE DATABASE IF NOT EXISTS IDENTIFIER($DB);
USE DATABASE IDENTIFIER($DB);
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($SCHEMA);
CREATE OR REPLACE WAREHOUSE IDENTIFIER($WH) WITH WAREHOUSE_SIZE = 'SMALL';

-- GRANTS
-- Removed overly permissive GRANT CREATE WAREHOUSE ON ACCOUNT statement
-- Removed overly broad role grant to follow principle of least privilege
-- GRANT ROLE IDENTIFIER($ROLE) TO USER IDENTIFIER($USER);
GRANT ROLE IDENTIFIER($ROLE) TO ROLE ACCOUNTADMIN;
GRANT OWNERSHIP ON DATABASE IDENTIFIER($DB) TO ROLE IDENTIFIER($ROLE);
GRANT OWNERSHIP ON SCHEMA IDENTIFIER($SCHEMA) TO ROLE IDENTIFIER($ROLE);
GRANT USAGE ON WAREHOUSE IDENTIFIER($WH) TO ROLE IDENTIFIER($ROLE);

-- Switch to the new role and schema
USE ROLE IDENTIFIER($ROLE);
USE DATABASE IDENTIFIER($DB);
USE SCHEMA IDENTIFIER($SCHEMA);
USE WAREHOUSE IDENTIFIER($WH);

-- Create destination table (synchronized with DynamoDB)
CREATE OR REPLACE TABLE openflow_insclaim_dest_tbl (
    eventName STRING,
    eventCreationUnixTime NUMBER,
    claimId STRING,
    diagnosisCodes ARRAY,
    dateOfService STRING,
    totalCharge FLOAT,
    procedureDetails VARIANT,
    memberId STRING,
    insurancePlan STRING,
    patientZip STRING,
    patientState STRING,
    patientCity STRING,
    patientStreet STRING,
    patientGender STRING,
    patientDOB STRING,
    patientLastName STRING,
    patientPhone STRING,
    patientFirstName STRING,
    patientEmail STRING,
    claimStatus STRING,
    createdTimeStamp STRING,
    providerName STRING,
    providerNPI STRING,
    providerZip STRING,
    providerState STRING,
    providerCity STRING,
    providerStreet STRING,
    billSubmitDate STRING,
    payerName STRING,
    payerId STRING,
    payerContactNumber STRING,
    paymentStatus STRING
);

-- Create CDC table (staging area for changes)
CREATE OR REPLACE TABLE openflow_insclaim_cdc_tbl (
    eventName STRING,
    eventCreationUnixTime NUMBER,
    claimId STRING,
    diagnosisCodes ARRAY,
    dateOfService STRING,
    totalCharge FLOAT,
    procedureDetails VARIANT,
    memberId STRING,
    insurancePlan STRING,
    patientZip STRING,
    patientState STRING,
    patientCity STRING,
    patientStreet STRING,
    patientGender STRING,
    patientDOB STRING,
    patientLastName STRING,
    patientPhone STRING,
    patientFirstName STRING,
    patientEmail STRING,
    claimStatus STRING,
    createdTimeStamp STRING,
    providerName STRING,
    providerNPI STRING,
    providerZip STRING,
    providerState STRING,
    providerCity STRING,
    providerStreet STRING,
    billSubmitDate STRING,
    payerName STRING,
    payerId STRING,
    payerContactNumber STRING,
    paymentStatus STRING
);

-- Create event history table (audit trail)
CREATE OR REPLACE TABLE openflow_insclaim_event_hist_tbl (
    eventName STRING,
    eventCreationUnixTime NUMBER,
    claimId STRING,
    diagnosisCodes ARRAY,
    dateOfService STRING,
    totalCharge FLOAT,
    procedureDetails VARIANT,
    memberId STRING,
    insurancePlan STRING,
    patientZip STRING,
    patientState STRING,
    patientCity STRING,
    patientStreet STRING,
    patientGender STRING,
    patientDOB STRING,
    patientLastName STRING,
    patientPhone STRING,
    patientFirstName STRING,
    patientEmail STRING,
    claimStatus STRING,
    createdTimeStamp STRING,
    providerName STRING,
    providerNPI STRING,
    providerZip STRING,
    providerState STRING,
    providerCity STRING,
    providerStreet STRING,
    billSubmitDate STRING,
    payerName STRING,
    payerId STRING,
    payerContactNumber STRING,
    paymentStatus STRING
);

-- Create views for easier querying
CREATE OR REPLACE VIEW v_healthcare_claims_summary AS
SELECT 
    claimId,
    claimStatus,
    paymentStatus,
    totalCharge,
    insurancePlan,
    memberId,
    providerName,
    patientFirstName || ' ' || patientLastName AS patientName,
    patientEmail,
    dateOfService,
    createdTimeStamp,
    TO_TIMESTAMP(TO_NUMBER(eventCreationUnixTime) / 1000000) AS eventCreationUTC
FROM openflow_insclaim_dest_tbl
ORDER BY eventCreationUnixTime DESC;

-- Create view for recent events
CREATE OR REPLACE VIEW v_recent_events AS
SELECT 
    eventName,
    claimId,
    claimStatus,
    paymentStatus,
    totalCharge,
    providerName,
    patientFirstName || ' ' || patientLastName AS patientName,
    TO_TIMESTAMP(TO_NUMBER(eventCreationUnixTime) / 1000000) AS eventCreationUTC
FROM openflow_insclaim_event_hist_tbl
ORDER BY eventCreationUnixTime DESC
LIMIT 100;

-- Create view for pending claims
CREATE OR REPLACE VIEW v_pending_claims AS
SELECT 
    claimId,
    claimStatus,
    paymentStatus,
    totalCharge,
    insurancePlan,
    memberId,
    providerName,
    patientFirstName || ' ' || patientLastName AS patientName,
    dateOfService,
    createdTimeStamp
FROM openflow_insclaim_dest_tbl
WHERE claimStatus IN ('Pending', 'In Review')
ORDER BY createdTimeStamp DESC;

-- Grant permissions on views
GRANT SELECT ON VIEW v_healthcare_claims_summary TO ROLE IDENTIFIER($ROLE);
GRANT SELECT ON VIEW v_recent_events TO ROLE IDENTIFIER($ROLE);
GRANT SELECT ON VIEW v_pending_claims TO ROLE IDENTIFIER($ROLE);

-- Create sample data for testing
INSERT INTO openflow_insclaim_dest_tbl (
    eventName, eventCreationUnixTime, claimId, diagnosisCodes, dateOfService, 
    totalCharge, procedureDetails, memberId, insurancePlan, patientZip, 
    patientState, patientCity, patientStreet, patientGender, patientDOB, 
    patientLastName, patientPhone, patientFirstName, patientEmail, claimStatus, 
    createdTimeStamp, providerName, providerNPI, providerZip, providerState, 
    providerCity, providerStreet, billSubmitDate, payerName, payerId, 
    payerContactNumber, paymentStatus
) VALUES (
    'INSERT', 
    EXTRACT(EPOCH_NANOSECOND FROM CURRENT_TIMESTAMP()), 
    'CLM-SAMPLE-001',
    ARRAY_CONSTRUCT('E11.9', 'I10'),
    '2024-01-15',
    2500.00,
    PARSE_JSON('{"procedure_code": "99213", "description": "Office visit"}'),
    'M1001',
    'Premium PPO',
    '90210',
    'CA',
    'Anytown',
    '123 Main St',
    'M',
    '1980-01-15',
    'Doe',
    '555-123-4567',
    'John',
    'john.doe@email.com',
    'Pending',
    '2024-01-15T10:00:00Z',
    'City Medical Center',
    '1234567890',
    '90211',
    'CA',
    'Anytown',
    '456 Medical Blvd',
    '2024-01-15',
    'Blue Cross Blue Shield',
    'BCBS001',
    '555-987-6543',
    'Pending'
);

-- Verify the setup
SELECT 'Healthcare CDC Schema Setup Complete' AS status;
SELECT COUNT(*) AS total_claims FROM openflow_insclaim_dest_tbl;
SELECT COUNT(*) AS total_events FROM openflow_insclaim_event_hist_tbl; 