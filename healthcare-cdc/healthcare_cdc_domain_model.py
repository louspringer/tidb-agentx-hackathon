#!/usr/bin/env python3
"""
Healthcare CDC Domain Model
Model-driven implementation of Snowflake Healthcare CDC with DynamoDB and Openflow

Based on: https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/
Original Contributors: Snowflake Inc.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json

class EventType(Enum):
    """CDC Event Types"""
    INSERT = "INSERT"
    MODIFY = "MODIFY" 
    REMOVE = "REMOVE"

class ClaimStatus(Enum):
    """Healthcare Claim Status"""
    PENDING = "Pending"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"

class PaymentStatus(Enum):
    """Payment Status"""
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

@dataclass
class PatientInfo:
    """Patient Information"""
    patient_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str
    gender: str
    street: str
    city: str
    state: str
    zip_code: str

@dataclass
class ProviderInfo:
    """Healthcare Provider Information"""
    provider_name: str
    provider_npi: str
    street: str
    city: str
    state: str
    zip_code: str

@dataclass
class PayerInfo:
    """Insurance Payer Information"""
    payer_name: str
    payer_id: str
    contact_number: str

@dataclass
class HealthcareClaim:
    """Healthcare Insurance Claim"""
    claim_id: str
    member_id: str
    insurance_plan: str
    diagnosis_codes: List[str]
    date_of_service: str
    total_charge: float
    procedure_details: Dict[str, Any]
    claim_status: ClaimStatus
    payment_status: PaymentStatus
    created_timestamp: str
    bill_submit_date: str
    patient: PatientInfo
    provider: ProviderInfo
    payer: PayerInfo

@dataclass
class CDCEvent:
    """Change Data Capture Event"""
    event_name: EventType
    event_creation_unix_time: int
    claim: HealthcareClaim
    
    def to_json(self) -> str:
        """Convert to JSON for DynamoDB stream"""
        return json.dumps({
            "eventName": self.event_name.value,
            "eventCreationUnixTime": self.event_creation_unix_time,
            "claimId": self.claim.claim_id,
            "claimStatus": self.claim.claim_status.value,
            "paymentStatus": self.claim.payment_status.value,
            "totalCharge": self.claim.total_charge,
            "insurancePlan": self.claim.insurance_plan,
            "memberId": self.claim.member_id,
            "providerName": self.claim.provider.provider_name,
            "patientFirstName": self.claim.patient.first_name,
            "patientLastName": self.claim.patient.last_name,
            "patientEmail": self.claim.patient.email,
            "patientPhone": self.claim.patient.phone,
            "patientDOB": self.claim.patient.date_of_birth,
            "patientGender": self.claim.patient.gender,
            "patientStreet": self.claim.patient.street,
            "patientCity": self.claim.patient.city,
            "patientState": self.claim.patient.state,
            "patientZip": self.claim.patient.zip_code,
            "providerNPI": self.claim.provider.provider_npi,
            "providerStreet": self.claim.provider.street,
            "providerCity": self.claim.provider.city,
            "providerState": self.claim.provider.state,
            "providerZip": self.claim.provider.zip_code,
            "payerName": self.claim.payer.payer_name,
            "payerId": self.claim.payer.payer_id,
            "payerContactNumber": self.claim.payer.contact_number,
            "diagnosisCodes": self.claim.diagnosis_codes,
            "dateOfService": self.claim.date_of_service,
            "procedureDetails": self.claim.procedure_details,
            "createdTimeStamp": self.claim.created_timestamp,
            "billSubmitDate": self.claim.bill_submit_date
        })

@dataclass
class InfrastructureComponents:
    """Infrastructure Components for Healthcare CDC"""
    # AWS Components
    dynamodb_table: str = "InsuranceClaims"
    kinesis_stream: str = "InsuranceClaimsStream"
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    ec2_instance_type: str = "t3.medium"
    
    # Snowflake Components
    database: str = "CDC_DB"
    schema: str = "CDC_SCHEMA"
    warehouse: str = "CDC_WH"
    role: str = "CDC_RL"
    
    # Openflow Components
    openflow_runtime: Optional[str] = None
    data_plane_url: Optional[str] = None
    control_plane_url: Optional[str] = None
    
    # Tables
    destination_table: str = "openflow_insclaim_dest_tbl"
    cdc_table: str = "openflow_insclaim_cdc_tbl"
    event_history_table: str = "openflow_insclaim_event_hist_tbl"

@dataclass
class PipelineConfiguration:
    """Openflow Pipeline Configuration"""
    pipeline_name: str = "HealthcareCDC"
    processors: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_processor(self, processor_type: str, config: Dict[str, Any]):
        """Add a processor to the pipeline"""
        self.processors.append({
            "type": processor_type,
            "config": config
        })

class HealthcareCDCDomainModel:
    """Domain Model for Healthcare CDC System"""
    
    def __init__(self, sql_template_path: Optional[str] = None):
        self.infrastructure = InfrastructureComponents()
        self.pipeline_config = PipelineConfiguration()
        self.sql_template_path = sql_template_path
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Setup the Openflow pipeline configuration"""
        # Kinesis Consumer
        self.pipeline_config.add_processor("KinesisConsumer", {
            "streamName": self.infrastructure.kinesis_stream,
            "region": "us-east-1"
        })
        
        # JSON Parser
        self.pipeline_config.add_processor("ParseJson", {
            "jsonPath": "$"
        })
        
        # Flat JSON (for nested structures)
        self.pipeline_config.add_processor("FlatJson", {
            "flattenArrays": True,
            "flattenObjects": True
        })
        
        # Jolt Transform (for data transformation)
        self.pipeline_config.add_processor("JoltTransformJson", {
            "joltSpec": [
                {
                    "operation": "shift",
                    "spec": {
                        "eventName": "eventName",
                        "eventCreationUnixTime": "eventCreationUnixTime",
                        "claimId": "claimId",
                        "claimStatus": "claimStatus",
                        "paymentStatus": "paymentStatus",
                        "totalCharge": "totalCharge",
                        "insurancePlan": "insurancePlan",
                        "memberId": "memberId",
                        "providerName": "providerName",
                        "patientFirstName": "patientFirstName",
                        "patientLastName": "patientLastName",
                        "patientEmail": "patientEmail",
                        "patientPhone": "patientPhone",
                        "patientDOB": "patientDOB",
                        "patientGender": "patientGender",
                        "patientStreet": "patientStreet",
                        "patientCity": "patientCity",
                        "patientState": "patientState",
                        "patientZip": "patientZip",
                        "providerNPI": "providerNPI",
                        "providerStreet": "providerStreet",
                        "providerCity": "providerCity",
                        "providerState": "providerState",
                        "providerZip": "providerZip",
                        "payerName": "payerName",
                        "payerId": "payerId",
                        "payerContactNumber": "payerContactNumber",
                        "diagnosisCodes": "diagnosisCodes",
                        "dateOfService": "dateOfService",
                        "procedureDetails": "procedureDetails",
                        "createdTimeStamp": "createdTimeStamp",
                        "billSubmitDate": "billSubmitDate"
                    }
                }
            ]
        })
        
        # Route to different tables based on event type
        self.pipeline_config.add_processor("RouteOnAttribute", {
            "Routing Strategy": "Route to Property name",
            "Route to Property name": "eventName"
        })
        
        # PutDatabaseRecord for destination table
        self.pipeline_config.add_processor("PutDatabaseRecord", {
            "tableName": self.infrastructure.destination_table,
            "databaseType": "SNOWFLAKE"
        })
        
        # PutDatabaseRecord for CDC table
        self.pipeline_config.add_processor("PutDatabaseRecord", {
            "tableName": self.infrastructure.cdc_table,
            "databaseType": "SNOWFLAKE"
        })
        
        # PutDatabaseRecord for event history table
        self.pipeline_config.add_processor("PutDatabaseRecord", {
            "tableName": self.infrastructure.event_history_table,
            "databaseType": "SNOWFLAKE"
        })
        
        # Execute SQL for merging CDC events
        self.pipeline_config.add_processor("ExecuteSQLStatement", {
            "sqlStatement": self._get_merge_sql()
        })
    
    def _get_merge_sql(self) -> str:
        """Get the SQL merge statement for CDC operations"""
        if self.sql_template_path:
            sql_file_path = Path(self.sql_template_path)
        else:
            sql_file_path = Path(__file__).parent / "sql" / "merge_cdc_operations.sql"
        
        try:
            with open(sql_file_path, 'r') as f:
                sql_template = f.read()
            
            return sql_template.format(
                cdc_table=self.infrastructure.cdc_table,
                dest_table=self.infrastructure.destination_table
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"SQL template file not found: {sql_file_path}")
        except (OSError, IOError) as e:
            raise OSError(f"Error reading SQL template file: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Error processing SQL template content: {e}")
    
    def generate_cloudformation_template(self) -> Dict[str, Any]:
        """Generate CloudFormation template for the healthcare CDC infrastructure"""
        return {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Healthcare CDC Infrastructure with DynamoDB, Kinesis, and Openflow",
            "Parameters": {
                "VpcId": {
                    "Type": "AWS::EC2::VPC::Id",
                    "Description": "VPC ID for the infrastructure"
                },
                "SubnetId": {
                    "Type": "AWS::EC2::Subnet::Id", 
                    "Description": "Subnet ID for the EC2 instance"
                },
                "EC2InstanceType": {
                    "Type": "String",
                    "Default": self.infrastructure.ec2_instance_type,
                    "Description": "EC2 instance type for data processing"
                }
            },
            "Resources": {
                "InsuranceClaimsTable": {
                    "Type": "AWS::DynamoDB::Table",
                    "Properties": {
                        "TableName": self.infrastructure.dynamodb_table,
                        "AttributeDefinitions": [
                            {
                                "AttributeName": "claim_id",
                                "AttributeType": "S"
                            }
                        ],
                        "KeySchema": [
                            {
                                "AttributeName": "claim_id",
                                "KeyType": "HASH"
                            }
                        ],
                        "BillingMode": "PAY_PER_REQUEST",
                        "StreamSpecification": {
                            "StreamEnabled": True,
                            "StreamViewType": "NEW_AND_OLD_IMAGES"
                        }
                    }
                },
                "InsuranceClaimsStream": {
                    "Type": "AWS::Kinesis::Stream",
                    "Properties": {
                        "Name": self.infrastructure.kinesis_stream,
                        "ShardCount": 1
                    }
                },
                "EC2SecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": "Security group for Healthcare CDC EC2 instance",
                        "VpcId": {"Ref": "VpcId"},
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": "22",
                                "ToPort": "22",
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "SecurityGroupEgress": [
                            {
                                "IpProtocol": "-1",
                                "CidrIp": "0.0.0.0/0"
                            }
                        ]
                    }
                },
                "EC2InstanceProfile": {
                    "Type": "AWS::IAM::InstanceProfile",
                    "Properties": {
                        "Roles": [{"Ref": "EC2InstanceRole"}]
                    }
                },
                "EC2InstanceRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"Service": "ec2.amazonaws.com"},
                                    "Action": "sts:AssumeRole"
                                }
                            ]
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
                            "arn:aws:iam::aws:policy/AmazonKinesisFullAccess"
                        ]
                    }
                },
                "EC2Instance": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "InstanceType": {"Ref": "EC2InstanceType"},
                        "ImageId": {"Fn::Sub": "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"},
                        "SubnetId": {"Ref": "SubnetId"},
                        "SecurityGroupIds": [{"Ref": "EC2SecurityGroup"}],
                        "IamInstanceProfile": {"Ref": "EC2InstanceProfile"},
                        "UserData": {
                            "Fn::Base64": {
                                "Fn::Sub": [
                                    "#!/bin/bash\n",
                                    "yum update -y\n",
                                    "yum install -y aws-cli python3\n",
                                    "pip3 install virtualenv\n",
                                    "virtualenv /opt/app_env\n",
                                    "source /opt/app_env/bin/activate\n",
                                    "pip install boto3\n",
                                    "echo 'Setting up Kinesis stream...' >> /var/log/user-data.log\n",
                                    "aws kinesis put-record --stream-name ${StreamName} --partition-key test --data test >> /var/log/user-data.log 2>&1\n",
                                    "echo 'Setup complete.' >> /var/log/user-data.log\n"
                                ],
                                "StreamName": {"Ref": "InsuranceClaimsStream"}
                            }
                        }
                    }
                }
            },
            "Outputs": {
                "DynamoDBTableName": {
                    "Description": "Name of the DynamoDB table",
                    "Value": self.infrastructure.dynamodb_table,
                    "Export": {
                        "Name": "HealthcareCDC-DynamoDBTableName"
                    }
                },
                "KinesisStreamName": {
                    "Description": "Name of the Kinesis Data Stream",
                    "Value": self.infrastructure.kinesis_stream,
                    "Export": {
                        "Name": "HealthcareCDC-KinesisStreamName"
                    }
                },
                "EC2InstanceId": {
                    "Description": "ID of the EC2 instance",
                    "Value": {"Ref": "EC2Instance"},
                    "Export": {
                        "Name": "HealthcareCDC-EC2InstanceId"
                    }
                }
            }
        }
    
    def generate_snowflake_schema(self) -> str:
        """Generate Snowflake schema creation SQL"""
        return f"""
        -- Create database and schema
        CREATE DATABASE IF NOT EXISTS {self.infrastructure.database};
        USE DATABASE {self.infrastructure.database};
        CREATE SCHEMA IF NOT EXISTS {self.infrastructure.schema};
        USE SCHEMA {self.infrastructure.schema};
        
        -- Create warehouse
        CREATE WAREHOUSE IF NOT EXISTS {self.infrastructure.warehouse} 
        WAREHOUSE_SIZE = 'SMALL' 
        AUTO_SUSPEND = 300 
        AUTO_RESUME = TRUE;
        
        -- Create destination table
        CREATE OR REPLACE TABLE {self.infrastructure.destination_table} (
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
        
        -- Create CDC table
        CREATE OR REPLACE TABLE {self.infrastructure.cdc_table} (
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
        
        -- Create event history table
        CREATE OR REPLACE TABLE {self.infrastructure.event_history_table} (
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
        """

def main():
    """Main function to demonstrate the domain model"""
    model = HealthcareCDCDomainModel()
    
    print("Healthcare CDC Domain Model")
    print("=" * 50)
    print(f"Database: {model.infrastructure.database}")
    print(f"Schema: {model.infrastructure.schema}")
    print(f"Destination Table: {model.infrastructure.destination_table}")
    print(f"CDC Table: {model.infrastructure.cdc_table}")
    print(f"Event History Table: {model.infrastructure.event_history_table}")
    
    # Generate sample claim
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
        zip_code="90210"
    )
    
    provider = ProviderInfo(
        provider_name="City Medical Center",
        provider_npi="1234567890",
        street="456 Medical Blvd",
        city="Anytown",
        state="CA",
        zip_code="90211"
    )
    
    payer = PayerInfo(
        payer_name="Blue Cross Blue Shield",
        payer_id="BCBS001",
        contact_number="555-987-6543"
    )
    
    claim = HealthcareClaim(
        claim_id="CLM001",
        member_id="M001",
        insurance_plan="Premium PPO",
        diagnosis_codes=["E11.9", "I10"],
        date_of_service="2024-01-15",
        total_charge=2500.00,
        procedure_details={"procedure_code": "99213", "description": "Office visit"},
        claim_status=ClaimStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        created_timestamp="2024-01-15T10:00:00Z",
        bill_submit_date="2024-01-15",
        patient=patient,
        provider=provider,
        payer=payer
    )
    
    cdc_event = CDCEvent(
        event_name=EventType.INSERT,
        event_creation_unix_time=int(datetime.now().timestamp() * 1000000),
        claim=claim
    )
    
    print("\nSample CDC Event JSON:")
    print(cdc_event.to_json())

if __name__ == "__main__":
    main() 