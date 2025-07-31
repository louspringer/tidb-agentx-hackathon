-- CDC Merge Operations for Healthcare Claims
-- This file contains the SQL merge statement for CDC operations

BEGIN
-- Create temporary table with all claimIds to be processed
CREATE OR REPLACE TEMPORARY TABLE temp_claim_ids AS
SELECT DISTINCT claimId 
FROM {cdc_table};

-- Perform the merge operation
MERGE INTO {dest_table} tgt
    USING {cdc_table} src
    ON tgt.claimId = src.claimId

    -- Delete rows
    WHEN MATCHED AND src.eventName = 'REMOVE' THEN DELETE

    -- Update existing rows
    WHEN MATCHED AND src.eventName = 'MODIFY'
    THEN
        UPDATE SET
            tgt.eventName = src.eventName,
            tgt.eventCreationUnixTime = src.eventCreationUnixTime,
            tgt.claimId = src.claimId,
            tgt.diagnosisCodes = src.diagnosisCodes,
            tgt.dateOfService = src.dateOfService,
            tgt.totalCharge = src.totalCharge,
            tgt.procedureDetails = src.procedureDetails,
            tgt.memberId = src.memberId,
            tgt.insurancePlan = src.insurancePlan,
            tgt.patientZip = src.patientZip,
            tgt.patientState = src.patientState,
            tgt.patientCity = src.patientCity,
            tgt.patientStreet = src.patientStreet,
            tgt.patientGender = src.patientGender,
            tgt.patientDOB = src.patientDOB,
            tgt.patientLastName = src.patientLastName,
            tgt.patientPhone = src.patientPhone,
            tgt.patientFirstName = src.patientFirstName,
            tgt.patientEmail = src.patientEmail,
            tgt.claimStatus = src.claimStatus,
            tgt.createdTimeStamp = src.createdTimeStamp,
            tgt.providerName = src.providerName,
            tgt.providerNPI = src.providerNPI,
            tgt.providerZip = src.providerZip,
            tgt.providerState = src.providerState,
            tgt.providerCity = src.providerCity,
            tgt.providerStreet = src.providerStreet,
            tgt.billSubmitDate = src.billSubmitDate,
            tgt.payerName = src.payerName,
            tgt.payerId = src.payerId,
            tgt.payerContactNumber = src.payerContactNumber,
            tgt.paymentStatus = src.paymentStatus

    -- Insert new rows that don't exist in target_table
    WHEN NOT MATCHED AND src.eventName = 'INSERT' THEN
        INSERT (
            eventName, 
            eventCreationUnixTime, 
            claimId, 
            diagnosisCodes, 
            dateOfService, 
            totalCharge, 
            procedureDetails, 
            memberId, 
            insurancePlan, 
            patientZip, 
            patientState, 
            patientCity, 
            patientStreet, 
            patientGender, 
            patientDOB, 
            patientLastName, 
            patientPhone, 
            patientFirstName, 
            patientEmail, 
            claimStatus, 
            createdTimeStamp, 
            providerName, 
            providerNPI, 
            providerZip, 
            providerState, 
            providerCity, 
            providerStreet, 
            billSubmitDate, 
            payerName, 
            payerId, 
            payerContactNumber, 
            paymentStatus
        )
        VALUES (
            src.eventName, 
            src.eventCreationUnixTime, 
            src.claimId, 
            src.diagnosisCodes, 
            src.dateOfService, 
            src.totalCharge, 
            src.procedureDetails, 
            src.memberId, 
            src.insurancePlan, 
            src.patientZip, 
            src.patientState, 
            src.patientCity, 
            src.patientStreet, 
            src.patientGender, 
            src.patientDOB, 
            src.patientLastName, 
            src.patientPhone, 
            src.patientFirstName, 
            src.patientEmail, 
            src.claimStatus, 
            src.createdTimeStamp, 
            src.providerName, 
            src.providerNPI, 
            src.providerZip, 
            src.providerState, 
            src.providerCity, 
            src.providerStreet, 
            src.billSubmitDate, 
            src.payerName, 
            src.payerId, 
            src.payerContactNumber, 
            src.paymentStatus
        );

-- Delete processed records in the cdc table from temp table
DELETE FROM {cdc_table} 
WHERE claimId IN (SELECT claimId FROM temp_claim_ids);

END; 