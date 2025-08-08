#!/usr/bin/env python3
"""
Healthcare CDC Package
Model-driven implementation of Snowflake Healthcare CDC with DynamoDB and Openflow

Based on: https://quickstarts.snowflake.com/guide/Streamline_Healthcare_CDC_DDB_And_Openflow/
Original Contributors: Snowflake Inc.
Enhanced by: OpenFlow Playground Team
"""

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

__version__ = "1.0.0"
__author__ = "OpenFlow Playground Team"
__description__ = "Healthcare CDC Implementation based on Snowflake Quickstart"

__all__ = [
    "HealthcareCDCDomainModel",
    "HealthcareClaim",
    "PatientInfo",
    "ProviderInfo",
    "PayerInfo",
    "CDCEvent",
    "EventType",
    "ClaimStatus",
    "PaymentStatus",
]
