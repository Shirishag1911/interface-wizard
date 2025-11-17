# Interface Wizard - User Guide

## Overview

Interface Wizard is a Generative AI-powered tool that allows you to interact with healthcare EHR systems using natural language commands. Instead of manually crafting HL7 messages or writing database queries, you can simply describe what you want to do in plain English.

## Getting Started

### Accessing the Application

1. Ensure both backend and frontend are running (see [INSTALLATION.md](INSTALLATION.md))
2. Open your web browser to http://localhost:3000
3. You should see the Interface Wizard chat interface

### Interface Overview

The Interface Wizard interface consists of:
- **Header**: Shows connection status and controls
- **Chat Area**: Displays conversation history
- **Input Box**: Where you type your commands
- **Session ID**: Unique identifier for your session (bottom of screen)

## Supported Commands

### Patient Operations

#### Create a Single Patient
```
Create a test patient named John Doe
Create a patient with first name Alice, last name Smith, born on 1990-05-15
Add a new patient with blood type A+
```

#### Create Multiple Patients (Bulk)
```
Create 100 test patients with randomized demographics
Generate 50 patient records
Create 20 patients with allergies to penicillin
```

#### Retrieve Patient Information
```
Retrieve patient information for MRN 12345
Get details for patient ID 67890
Find patient John Doe
```

### Lab Results Operations

#### Create Lab Results
```
Create a CBC lab result for patient 12345
Generate lab results for MRN 67890
```

#### Retrieve Lab Results
```
Get the latest CBC result for patient John Doe
Retrieve lab results for patient MRN 12345
Show all lab tests for patient 67890
```

### Admission/Discharge Operations

#### Admit Patient
```
Admit patient MRN 12345 to General Ward
Register patient 67890 for admission
```

#### Discharge Patient
```
Discharge patient MRN 12345
Release patient 67890 from hospital
```

## Example Workflows

### Workflow 1: Setting Up Test Data

```
User: Create 50 test patients with random demographics
System: ✓ Success! 50 test patients were created in the EHR.
        Records affected: 50 (50 succeeded, 0 failed)
        Protocol: HL7V2

User: Create lab results for the first 10 patients
System: ✓ Processing... Creating CBC results for patients...
```

### Workflow 2: Querying Patient Data

```
User: Retrieve patient information for MRN 12345
System: ✓ Found patient: John Doe
        DOB: 1985-03-15
        Gender: M
        Phone: (555) 123-4567
        Address: 123 Main St, Boston, MA 02101

User: Get the latest lab results for this patient
System: ✓ Found 3 lab results:
        1. CBC - 2024-11-14 10:30 AM
        2. BMP - 2024-11-13 02:15 PM
        3. Lipid Panel - 2024-11-10 09:00 AM
```

### Workflow 3: Patient Admission Flow

```
User: Create a test patient named Sarah Johnson
System: ✓ Successfully created patient: Sarah Johnson (MRN: 98765)

User: Admit patient MRN 98765 to ICU
System: ✓ Patient admitted successfully
        Location: ICU
        Admission Time: 2024-11-14 14:30:00
```

## Understanding Responses

### Success Messages
Messages with a ✓ or green indicator show successful operations.

**Example:**
```
✓ Success! 5 patients were created in the TEST EHR.
Starting IDs are 1001 through 1005.
```

### Partial Success
When some operations succeed and some fail:

```
⚠ Bulk operation completed: 98 succeeded, 2 failed
Errors:
• Patient MRN 1234 already exists
• Patient DOB invalid for record #45
```

### Error Messages
Red indicators show when something went wrong:

```
✗ Failed to create patient
Error: Missing required field - last name
Please provide a last name and try again
```

## Tips for Best Results

### 1. Be Specific When Needed
```
Good: "Create a patient named John Doe, DOB 1985-03-15, gender M"
Also Good: "Create a test patient" (system will generate realistic data)
```

### 2. Use Clear Identifiers
```
Good: "Retrieve patient MRN 12345"
Good: "Get patient with ID 67890"
Avoid: "Show me the patient"  (which patient?)
```

### 3. Batch Operations
```
Good: "Create 100 test patients"
The system handles bulk operations efficiently
```

### 4. Follow Up Questions
The system maintains context within a session:
```
User: Create a patient named Alice Smith
System: ✓ Created patient Alice Smith (MRN: 55555)

User: Now admit her to the General Ward
System: ✓ Patient Alice Smith admitted to General Ward
```

## Technical Details

### Protocols Used

**HL7 v2 (via MLLP):**
- Patient creation (ADT^A28)
- Patient admission (ADT^A01)
- Patient discharge (ADT^A03)
- Lab result submission (ORU^R01)

**FHIR R4 (via REST API):**
- Patient queries
- Observation (lab result) queries
- Resource searches

### Operation Status

Each operation has a status:
- **Success**: Operation completed without errors
- **Partial Success**: Some records succeeded, some failed
- **Failed**: Operation could not be completed
- **Processing**: Operation in progress

### Records Summary

Each response shows:
- **Records Affected**: Total number of records involved
- **Records Succeeded**: Number that completed successfully
- **Records Failed**: Number that encountered errors
- **Protocol Used**: HL7V2 or FHIR

## Limitations

### Current Limitations

1. **Test Data**: Designed primarily for test/development environments
2. **Bulk Limits**: Practical limit of ~100 records per bulk operation
3. **Session Memory**: Context is session-based (cleared when browser closes)
4. **Real-time Only**: No scheduling of future operations

### Data Safety

⚠ **Important**: This tool creates real data in your EHR system.
- Use in test/development environments only
- Do not use with production patient data
- Always verify created records

## Troubleshooting

### "Cannot understand command"
- Rephrase your request more clearly
- Include specific identifiers (MRN, patient ID)
- Use examples from this guide

### "Timeout waiting for ACK"
- Check that Mirth Connect is running
- Verify the MLLP channel is active
- Check network connectivity

### "Patient not found"
- Verify the MRN or Patient ID is correct
- Check that the patient exists in the EHR

### Connection Issues
- Check the status indicator (top right)
- Ensure backend is running (green = healthy)
- Refresh the page

## Advanced Features

### Session Management

Each session maintains:
- Command history
- Operation results
- Contextual information

To start fresh, click the Refresh button in the header.

### Operation Details

Click on any operation result to see:
- Exact timestamp
- Full error messages (if any)
- Protocol details
- Generated message IDs

## Best Practices

1. **Start Simple**: Begin with single operations before bulk
2. **Verify Results**: Check the EHR to confirm operations
3. **Use Test Environment**: Never use in production
4. **Monitor Logs**: Check backend logs for detailed information
5. **Clear Sessions**: Start a new session for unrelated tasks

## Examples by Use Case

### Testing Interface Connectivity
```
Create a single test patient
Verify the patient appears in OpenEMR
```

### Populating Test Database
```
Create 100 test patients with random demographics
Create 50 patients with allergies to common medications
Generate lab results for all patients
```

### Integration Testing
```
Create a patient with specific demographics
Admit the patient
Create lab results
Discharge the patient
Verify all steps in the EHR
```

## Support and Feedback

### Getting Help
1. Check this User Guide
2. Review [INSTALLATION.md](INSTALLATION.md) for setup issues
3. Check backend logs at `backend/logs/interface-wizard.log`
4. Review API docs at http://localhost:8000/docs

### Reporting Issues
When reporting issues, include:
- The exact command you entered
- The error message received
- Backend log entries (if available)
- Browser console errors (F12 → Console)
