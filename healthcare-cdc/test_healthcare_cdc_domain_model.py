#!/usr/bin/env python3
"""
Tests for Healthcare CDC Domain Model
"""

import json
from datetime import datetime

from healthcare_cdc_domain_model import (
    CDCEvent,
    ClaimStatus,
    EventType,
    HealthcareCDCDomainModel,
    HealthcareClaim,
    PatientInfo,
    PayerInfo,
    PaymentStatus,
    ProviderInfo,
)


class TestHealthcareCDCDomainModel:
    """Test the healthcare CDC domain model"""

    def test_domain_model_initialization(self):
        """Test domain model initialization"""
        model = HealthcareCDCDomainModel()

        assert model.infrastructure.dynamodb_table == "InsuranceClaims"
        assert model.infrastructure.kinesis_stream == "InsuranceClaimsStream"
        assert model.infrastructure.database == "CDC_DB"
        assert model.infrastructure.schema == "CDC_SCHEMA"
        assert model.infrastructure.destination_table == "openflow_insclaim_dest_tbl"
        assert model.infrastructure.cdc_table == "openflow_insclaim_cdc_tbl"
        assert (
            model.infrastructure.event_history_table
            == "openflow_insclaim_event_hist_tbl"
        )

    def test_pipeline_configuration(self):
        """Test pipeline configuration setup"""
        model = HealthcareCDCDomainModel()

        # Check that processors were added
        assert len(model.pipeline_config.processors) > 0

        # Check for required processors
        processor_types = [p["type"] for p in model.pipeline_config.processors]
        assert "KinesisConsumer" in processor_types
        assert "ParseJson" in processor_types
        assert "FlatJson" in processor_types
        assert "JoltTransformJson" in processor_types
        assert "RouteOnAttribute" in processor_types
        assert "PutDatabaseRecord" in processor_types
        assert "ExecuteSQLStatement" in processor_types

    def test_merge_sql_generation(self):
        """Test SQL merge statement generation"""
        model = HealthcareCDCDomainModel()
        merge_sql = model._get_merge_sql()

        # Check for key SQL components
        assert "MERGE INTO" in merge_sql
        assert "openflow_insclaim_dest_tbl" in merge_sql
        assert "openflow_insclaim_cdc_tbl" in merge_sql
        assert "WHEN MATCHED" in merge_sql
        assert "WHEN NOT MATCHED" in merge_sql
        assert "INSERT" in merge_sql
        assert "UPDATE" in merge_sql
        assert "DELETE" in merge_sql

    def test_cloudformation_template_generation(self):
        """Test CloudFormation template generation"""
        model = HealthcareCDCDomainModel()
        template = model.generate_cloudformation_template()

        # Check template structure
        assert template["AWSTemplateFormatVersion"] == "2010-09-09"
        assert "Healthcare CDC Infrastructure" in template["Description"]
        assert "Parameters" in template
        assert "Resources" in template
        assert "Outputs" in template

        # Check for required resources
        resources = template["Resources"]
        assert "InsuranceClaimsTable" in resources
        assert "InsuranceClaimsStream" in resources
        assert "EC2Instance" in resources

        # Check for required outputs
        outputs = template["Outputs"]
        assert "DynamoDBTableName" in outputs
        assert "KinesisStreamName" in outputs
        assert "EC2InstanceId" in outputs

    def test_snowflake_schema_generation(self):
        """Test Snowflake schema generation"""
        model = HealthcareCDCDomainModel()
        schema_sql = model.generate_snowflake_schema()

        # Check for required SQL components
        assert "CREATE DATABASE" in schema_sql
        assert "CREATE SCHEMA" in schema_sql
        assert "CREATE WAREHOUSE" in schema_sql
        assert "openflow_insclaim_dest_tbl" in schema_sql
        assert "openflow_insclaim_cdc_tbl" in schema_sql
        assert "openflow_insclaim_event_hist_tbl" in schema_sql


class TestHealthcareClaim:
    """Test healthcare claim data structure"""

    def test_claim_creation(self):
        """Test creating a healthcare claim"""
        patient = PatientInfo(
            patient_id="P001",
            first_name="John",
            last_name="Doe",
            email="john.doe@email.com",
            phone="555-123-4567",
            date_of_birth="1980-01-15",
            gender="M",
            street="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="90210",
        )

        provider = ProviderInfo(
            provider_name="City Medical Center",
            provider_npi="1234567890",
            street="456 Medical Blvd",
            city="Anytown",
            state="CA",
            zip_code="90211",
        )

        payer = PayerInfo(
            payer_name="Blue Cross Blue Shield",
            payer_id="BCBS001",
            contact_number="555-987-6543",
        )

        claim = HealthcareClaim(
            claim_id="CLM001",
            member_id="M001",
            insurance_plan="Premium PPO",
            diagnosis_codes=["E11.9", "I10"],
            date_of_service="2024-01-15",
            total_charge=2500.00,
            procedure_details={
                "procedure_code": "99213",
                "description": "Office visit",
            },
            claim_status=ClaimStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            created_timestamp="2024-01-15T10:00:00Z",
            bill_submit_date="2024-01-15",
            patient=patient,
            provider=provider,
            payer=payer,
        )

        assert claim.claim_id == "CLM001"
        assert claim.member_id == "M001"
        assert claim.insurance_plan == "Premium PPO"
        assert claim.diagnosis_codes == ["E11.9", "I10"]
        assert claim.total_charge == 2500.00
        assert claim.claim_status == ClaimStatus.PENDING
        assert claim.payment_status == PaymentStatus.PENDING
        assert claim.patient.first_name == "John"
        assert claim.provider.provider_name == "City Medical Center"
        assert claim.payer.payer_name == "Blue Cross Blue Shield"


class TestCDCEvent:
    """Test CDC event data structure"""

    def test_cdc_event_creation(self):
        """Test creating a CDC event"""
        patient = PatientInfo(
            patient_id="P001",
            first_name="John",
            last_name="Doe",
            email="john.doe@email.com",
            phone="555-123-4567",
            date_of_birth="1980-01-15",
            gender="M",
            street="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="90210",
        )

        provider = ProviderInfo(
            provider_name="City Medical Center",
            provider_npi="1234567890",
            street="456 Medical Blvd",
            city="Anytown",
            state="CA",
            zip_code="90211",
        )

        payer = PayerInfo(
            payer_name="Blue Cross Blue Shield",
            payer_id="BCBS001",
            contact_number="555-987-6543",
        )

        claim = HealthcareClaim(
            claim_id="CLM001",
            member_id="M001",
            insurance_plan="Premium PPO",
            diagnosis_codes=["E11.9", "I10"],
            date_of_service="2024-01-15",
            total_charge=2500.00,
            procedure_details={
                "procedure_code": "99213",
                "description": "Office visit",
            },
            claim_status=ClaimStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            created_timestamp="2024-01-15T10:00:00Z",
            bill_submit_date="2024-01-15",
            patient=patient,
            provider=provider,
            payer=payer,
        )

        cdc_event = CDCEvent(
            event_name=EventType.INSERT,
            event_creation_unix_time=int(datetime.now().timestamp() * 1000000),
            claim=claim,
        )

        assert cdc_event.event_name == EventType.INSERT
        assert cdc_event.claim.claim_id == "CLM001"
        assert cdc_event.event_creation_unix_time > 0

    def test_cdc_event_json_serialization(self):
        """Test CDC event JSON serialization"""
        patient = PatientInfo(
            patient_id="P001",
            first_name="John",
            last_name="Doe",
            email="john.doe@email.com",
            phone="555-123-4567",
            date_of_birth="1980-01-15",
            gender="M",
            street="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="90210",
        )

        provider = ProviderInfo(
            provider_name="City Medical Center",
            provider_npi="1234567890",
            street="456 Medical Blvd",
            city="Anytown",
            state="CA",
            zip_code="90211",
        )

        payer = PayerInfo(
            payer_name="Blue Cross Blue Shield",
            payer_id="BCBS001",
            contact_number="555-987-6543",
        )

        claim = HealthcareClaim(
            claim_id="CLM001",
            member_id="M001",
            insurance_plan="Premium PPO",
            diagnosis_codes=["E11.9", "I10"],
            date_of_service="2024-01-15",
            total_charge=2500.00,
            procedure_details={
                "procedure_code": "99213",
                "description": "Office visit",
            },
            claim_status=ClaimStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            created_timestamp="2024-01-15T10:00:00Z",
            bill_submit_date="2024-01-15",
            patient=patient,
            provider=provider,
            payer=payer,
        )

        cdc_event = CDCEvent(
            event_name=EventType.INSERT,
            event_creation_unix_time=1705312800000000,  # Fixed timestamp for testing
            claim=claim,
        )

        json_data = cdc_event.to_json()
        parsed_data = json.loads(json_data)

        # Check required fields
        assert parsed_data["eventName"] == "INSERT"
        assert parsed_data["eventCreationUnixTime"] == 1705312800000000
        assert parsed_data["claimId"] == "CLM001"
        assert parsed_data["claimStatus"] == "Pending"
        assert parsed_data["paymentStatus"] == "Pending"
        assert parsed_data["totalCharge"] == 2500.00
        assert parsed_data["insurancePlan"] == "Premium PPO"
        assert parsed_data["memberId"] == "M001"
        assert parsed_data["providerName"] == "City Medical Center"
        assert parsed_data["patientFirstName"] == "John"
        assert parsed_data["patientLastName"] == "Doe"
        assert parsed_data["patientEmail"] == "john.doe@email.com"
        assert parsed_data["diagnosisCodes"] == ["E11.9", "I10"]
        assert parsed_data["procedureDetails"] == {
            "procedure_code": "99213",
            "description": "Office visit",
        }


class TestEnums:
    """Test enum values"""

    def test_event_types(self):
        """Test event type enum values"""
        assert EventType.INSERT.value == "INSERT"
        assert EventType.MODIFY.value == "MODIFY"
        assert EventType.REMOVE.value == "REMOVE"

    def test_claim_status(self):
        """Test claim status enum values"""
        assert ClaimStatus.PENDING.value == "Pending"
        assert ClaimStatus.IN_REVIEW.value == "In Review"
        assert ClaimStatus.APPROVED.value == "Approved"
        assert ClaimStatus.REJECTED.value == "Rejected"
        assert ClaimStatus.PAID.value == "Paid"

    def test_payment_status(self):
        """Test payment status enum values"""
        assert PaymentStatus.PENDING.value == "Pending"
        assert PaymentStatus.PROCESSING.value == "Processing"
        assert PaymentStatus.COMPLETED.value == "Completed"
        assert PaymentStatus.FAILED.value == "Failed"


def test_integration():
    """Integration test for the complete domain model"""
    model = HealthcareCDCDomainModel()

    # Test domain model functionality
    assert model.infrastructure.dynamodb_table == "InsuranceClaims"
    assert model.infrastructure.kinesis_stream == "InsuranceClaimsStream"

    # Test pipeline configuration
    assert len(model.pipeline_config.processors) > 0

    # Test SQL generation
    merge_sql = model._get_merge_sql()
    assert "MERGE INTO" in merge_sql

    # Test CloudFormation template
    template = model.generate_cloudformation_template()
    assert "AWSTemplateFormatVersion" in template

    # Test Snowflake schema
    schema_sql = model.generate_snowflake_schema()
    assert "CREATE DATABASE" in schema_sql


# Tests should be run externally with: pytest healthcare-cdc/test_healthcare_cdc_domain_model.py -v
