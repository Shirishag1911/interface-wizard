# CSV Upload Guide for Interface Wizard

## Overview

Interface Wizard now supports bulk patient data import via CSV file upload. This feature allows you to upload a CSV file containing patient information, which will be automatically processed and sent to OpenEMR/Mirth via HL7 messages.

---

## Features

- **Bulk Patient Creation**: Upload CSV files with multiple patient records
- **Flexible Column Mapping**: Supports various column name formats (case-insensitive)
- **Data Validation**: Automatic validation of CSV structure and data
- **HL7 Integration**: Each patient is sent via HL7 ADT^A28 messages
- **Progress Tracking**: Real-time feedback on upload status
- **Error Reporting**: Detailed error messages for failed records

---

## CSV File Format

### Required Columns

At minimum, your CSV file must contain:
- **First Name** OR **Last Name** (at least one is required)

### Supported Columns

The CSV parser recognizes the following columns (case-insensitive):

| Field | Accepted Column Names |
|-------|----------------------|
| **Patient ID** | `patient_id`, `patientid`, `id`, `patient id` |
| **MRN** | `mrn`, `medical_record_number`, `medical record number`, `patient mrn` |
| **First Name** | `first_name`, `firstname`, `first name`, `fname`, `given_name` |
| **Last Name** | `last_name`, `lastname`, `last name`, `lname`, `family_name`, `surname` |
| **Middle Name** | `middle_name`, `middlename`, `middle name`, `mname`, `middle` |
| **Date of Birth** | `date_of_birth`, `dob`, `birth_date`, `birthdate`, `date of birth` |
| **Gender** | `gender`, `sex` |
| **SSN** | `ssn`, `social_security_number`, `social security number` |
| **Address** | `address`, `street`, `street_address`, `address1` |
| **City** | `city` |
| **State** | `state`, `province` |
| **Zip Code** | `zip_code`, `zip`, `zipcode`, `postal_code`, `postalcode` |
| **Phone** | `phone`, `phone_number`, `telephone`, `mobile`, `contact` |
| **Email** | `email`, `email_address`, `e-mail` |
| **Blood Type** | `blood_type`, `bloodtype`, `blood group`, `blood_group` |
| **Allergies** | `allergies`, `allergy` |

---

## Sample CSV File

Here's an example CSV file with properly formatted patient data:

```csv
first_name,last_name,date_of_birth,gender,phone,email,address,city,state,zip_code,blood_type,allergies
John,Doe,1985-05-15,Male,555-0101,john.doe@email.com,123 Main St,Springfield,IL,62701,O+,Penicillin
Jane,Smith,1990-08-22,Female,555-0102,jane.smith@email.com,456 Oak Ave,Chicago,IL,60601,A+,None
Michael,Johnson,1978-12-03,Male,555-0103,m.johnson@email.com,789 Elm St,Peoria,IL,61602,B-,Peanuts;Shellfish
```

A sample file is available at: [`backend/sample_patients.csv`](backend/sample_patients.csv)

---

## Data Format Guidelines

### Date of Birth

Supported formats:
- `YYYY-MM-DD` (e.g., `1985-05-15`)
- `MM/DD/YYYY` (e.g., `05/15/1985`)
- `DD/MM/YYYY` (e.g., `15/05/1985`)
- `YYYYMMDD` (e.g., `19850515`)
- `MM-DD-YYYY` (e.g., `05-15-1985`)
- `DD-MM-YYYY` (e.g., `15-05-1985`)

### Gender

Accepted values:
- **Male**: `M`, `Male`, `Man`
- **Female**: `F`, `Female`, `Woman`
- **Other**: `O`, `Other`, `Non-binary`, `NB`, `Unknown`, `U`

Values are normalized to standard format (`Male`, `Female`, `Other`).

### Allergies

Multiple allergies can be specified using:
- **Semicolon-separated**: `Penicillin;Aspirin;Codeine`
- **Comma-separated**: `Peanuts,Shellfish,Latex`
- **Single value**: `None` or `Penicillin`

### MRN (Medical Record Number)

- If not provided in CSV, the system will auto-generate MRNs with format: `CSVxxxxxxxx` (where x is a unique hex ID)
- If provided, the value from CSV will be used

---

## How to Upload CSV

### Using Angular Frontend

1. Click the **attachment icon** (📎) next to the message input box
2. Select your `.csv` file from the file picker
3. (Optional) Type a message like "Upload patients from CSV"
4. Click **Send** button
5. The system will process the file and display results

### Using React Frontend

1. Click the **attachment icon** (📎) next to the message input box
2. Select your `.csv` file from the file picker
3. (Optional) Type a message like "Upload patients from CSV"
4. Click **Send** button
5. The system will process the file and display results

### Command Options

You can upload a CSV with any of these messages:
- *Leave empty* - System will auto-detect and use: "Create X patients from uploaded CSV file"
- `"Upload CSV"` - Explicit upload command
- `"Import patients from file"` - Natural language command
- `"Process this patient data"` - Natural language command

---

## Backend Processing Flow

1. **File Upload**: Frontend sends CSV file via `multipart/form-data` to `/api/v1/command` endpoint
2. **CSV Parsing**: Backend reads and parses CSV content using `CSVProcessingService`
3. **Column Mapping**: Flexible column name matching (case-insensitive)
4. **Patient Creation**: Each row is converted to a `Patient` entity
5. **HL7 Message Generation**: For each patient, an HL7 ADT^A28 message is created
6. **MLLP Transmission**: Messages are sent to OpenEMR/Mirth via MLLP protocol
7. **ACK Processing**: System waits for and validates HL7 ACK responses
8. **Result Aggregation**: Success/failure counts are collected and reported

---

## Response Format

After processing, you'll receive a detailed response:

```json
{
  "operation_id": "op_abc123",
  "status": "success",
  "message": "Successfully created all 10 patients from CSV file",
  "data": {
    "total_patients": 10,
    "successful": 10,
    "failed": 0,
    "source": "csv_upload"
  },
  "records_affected": 10,
  "records_succeeded": 10,
  "records_failed": 0,
  "errors": [],
  "warnings": [],
  "protocol_used": "hl7v2",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:45Z"
}
```

### Status Values

- **`success`**: All patients created successfully
- **`partial_success`**: Some patients succeeded, some failed (check `errors` array)
- **`failed`**: All patients failed to create

---

## Error Handling

### Common Errors

1. **Missing Required Fields**
   - Error: `"CSV file must contain headers"`
   - Solution: Ensure first row contains column names

2. **No Name Fields**
   - Warning: `"No name fields detected (first_name or last_name)"`
   - Solution: Add `first_name` or `last_name` column

3. **Invalid Date Format**
   - Warning: `"Invalid date format for date_of_birth: xyz"`
   - Solution: Use one of the supported date formats

4. **Invalid CSV Encoding**
   - Error: `"Invalid CSV encoding. Please ensure file is utf-8 encoded"`
   - Solution: Save CSV file with UTF-8 encoding

5. **File Type Error**
   - Error: `"Invalid file type. Only .csv files are accepted"`
   - Solution: Ensure file extension is `.csv`

### Row-Level Errors

If individual rows fail, the system will report:
- Row number
- Patient name (if available)
- Specific error message

Example:
```
"Row 5: John Doe - ACK Error: Patient already exists"
"Row 8: SSN format invalid"
```

Only the first 10 errors are displayed in the response to prevent overflow.

---

## Best Practices

1. **Validate CSV Structure**
   - Use a sample file as a template
   - Ensure consistent column names
   - Check for required fields

2. **Data Quality**
   - Use standard date formats
   - Normalize gender values
   - Remove special characters from phone numbers

3. **File Size**
   - Recommended: **< 1000 patients per file**
   - For larger datasets, split into multiple files

4. **Encoding**
   - Always save CSV files as **UTF-8** encoding
   - Avoid Excel's default encoding (Windows-1252)

5. **Testing**
   - Test with a small sample file first (5-10 patients)
   - Verify data in OpenEMR before uploading large batches

6. **Backup**
   - Keep a copy of original CSV files
   - Export existing patient data before large imports

---

## Technical Implementation

### Backend Components

**Files Modified/Created:**
- `backend/app/infrastructure/csv_service.py` - CSV parsing service
- `backend/app/presentation/routes.py` - File upload endpoint
- `backend/app/presentation/schemas.py` - CSV response schemas
- `backend/app/application/use_cases.py` - CSV processing use case
- `backend/app/presentation/dependencies.py` - Dependency injection

**Key Classes:**
- `CSVProcessingService` - Handles CSV parsing and patient entity creation
- `ProcessCommandUseCase._handle_csv_upload()` - Bulk patient creation handler

### Frontend Components

**Angular:**
- `frontend-angular/src/app/chat/chat.component.html` - File input accepts `.csv`
- `frontend-angular/src/app/chat/chat.service.ts` - FormData upload support

**React:**
- `frontend-react/src/components/ChatInputComponent.tsx` - File input accepts `.csv`
- `frontend-react/src/services/api.ts` - FormData upload support
- `frontend-react/src/pages/Chat.tsx` - File handling in sendMessage

---

## Troubleshooting

### Issue: File upload not working

**Check:**
1. Backend server is running: `http://localhost:8000`
2. File extension is `.csv`
3. Browser console for JavaScript errors
4. Backend logs at `backend/logs/interface-wizard.log`

### Issue: Patients not appearing in OpenEMR

**Check:**
1. Mirth Connect is running
2. HL7 listener channel is active
3. OpenEMR database credentials in `.env` file
4. Check response for ACK errors

### Issue: All rows failing with same error

**Check:**
1. OpenEMR connection settings
2. Database schema compatibility
3. Required fields in OpenEMR patient table

---

## Example Usage Scenarios

### Scenario 1: Migrating Existing Patients

You have patient data in Excel:

1. **Export to CSV**:
   - Open Excel file
   - File → Save As → CSV (UTF-8)

2. **Rename Columns** (if needed):
   - `FirstName` → `first_name`
   - `DOB` → `date_of_birth`
   - `PhoneNumber` → `phone`

3. **Upload via Interface Wizard**:
   - Open application
   - Click attachment icon
   - Select CSV file
   - Type: "Import patients from migration file"
   - Click Send

4. **Verify Results**:
   - Check response message
   - Verify in OpenEMR patient list

### Scenario 2: Daily Patient Batch Upload

Automated CSV generation from external system:

1. External system exports daily patient registrations as CSV
2. Place file in known location
3. Upload via Interface Wizard UI
4. Review success/error report
5. Handle failed records manually

### Scenario 3: Testing with Sample Data

Generate test patients for development:

1. Use `backend/sample_patients.csv` as template
2. Modify patient data as needed
3. Upload to test environment
4. Verify HL7 messages in Mirth
5. Confirm data in OpenEMR test database

---

## API Reference

### Endpoint

```
POST /api/v1/command
```

### Request (Multipart Form Data)

```
Content-Type: multipart/form-data

Fields:
- command: string (required) - Command text or "Upload CSV"
- session_id: string (optional) - Session identifier
- file: file (optional) - CSV file upload
```

### Example cURL

```bash
curl -X POST http://localhost:8000/api/v1/command \
  -F "command=Upload patients from CSV" \
  -F "session_id=session-123" \
  -F "file=@sample_patients.csv"
```

---

## Security Considerations

1. **File Size Limits**: Backend should implement max file size (e.g., 10MB)
2. **File Type Validation**: Only `.csv` files are processed
3. **Content Validation**: All CSV data is validated before processing
4. **SQL Injection Prevention**: Pydantic models and parameterized queries
5. **PHI Protection**: CSV files are not persisted to disk
6. **Access Control**: Consider adding authentication/authorization

---

## Future Enhancements

Potential improvements for CSV upload feature:

1. **Async Processing**: Queue large CSV files for background processing
2. **Progress Bar**: Real-time upload/processing progress indicator
3. **Preview Mode**: Show parsed data before committing
4. **Template Download**: Generate CSV template from UI
5. **Column Mapper UI**: Visual mapping of CSV columns to patient fields
6. **Duplicate Detection**: Check for existing patients before insert
7. **Update Support**: Allow CSV to update existing patient records
8. **Lab Results Upload**: Support CSV uploads for lab data
9. **Batch Status Dashboard**: View all CSV upload operations history
10. **Excel Support**: Direct `.xlsx` file upload without conversion

---

## Support

For issues or questions about CSV upload:

1. Check backend logs: `backend/logs/interface-wizard.log`
2. Review Mirth Connect channel logs
3. Verify OpenEMR database connectivity
4. Consult [BACKEND_MIRTH_INTEGRATION.md](docs/BACKEND_MIRTH_INTEGRATION.md)
5. Check [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for troubleshooting

---

## Summary

The CSV upload feature provides a powerful way to bulk import patient data into OpenEMR via HL7 messages. Key benefits:

- **Fast**: Process hundreds of patients in seconds
- **Flexible**: Supports various column name formats
- **Reliable**: Comprehensive error handling and reporting
- **Integrated**: Uses existing HL7/MLLP infrastructure
- **User-Friendly**: Simple drag-and-drop interface

Just prepare your CSV file with patient data, upload via the UI, and let Interface Wizard handle the rest!
