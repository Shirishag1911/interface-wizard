# CSV Test Data Files for Interface Wizard

This folder contains 10 comprehensive CSV test files designed to test various healthcare scenarios and HL7 message types.

## Test Files Overview

| File | Scenario | Patients | HL7 Message Type | Use Case |
|------|----------|----------|------------------|----------|
| **01_new_patient_registration.csv** | New Patient Registration | 10 | ADT^A28 | Add new persons to the system without visit context |
| **02_outpatient_registration.csv** | Outpatient Registration | 10 | ADT^A04 | Register patients for OPD/clinic visits |
| **03_inpatient_admission.csv** | Hospital Admission | 10 | ADT^A01 | Admit patients for inpatient care |
| **04_emergency_department.csv** | Emergency Department | 10 | ADT^A01/A04 | Emergency admissions and registrations |
| **05_cardiology_patients.csv** | Cardiology Department | 10 | ADT^A28/A04 | Cardiac patients with specific drug allergies |
| **06_oncology_patients.csv** | Oncology Department | 10 | ADT^A28/A04 | Cancer patients with chemotherapy allergies |
| **07_maternity_patients.csv** | Maternity Ward | 10 | ADT^A01/A04 | Pregnant women for prenatal/delivery care |
| **08_orthopedic_patients.csv** | Orthopedic Department | 10 | ADT^A28/A04 | Patients with bone/joint conditions |
| **09_pediatric_surgery.csv** | Pediatric Surgery | 10 | ADT^A01/A04 | Children scheduled for surgical procedures |
| **10_multispecialty_clinic.csv** | Multi-specialty Clinic | 10 | ADT^A04/A28 | Mixed patient population with various allergies |

---

## File Format

All CSV files follow the same structure with these columns:

```
first_name,last_name,date_of_birth,gender,phone,email,address,city,state,zip_code,blood_type,allergies
```

### Column Descriptions

- **first_name**: Patient's first name
- **last_name**: Patient's last name
- **date_of_birth**: Format: YYYY-MM-DD (e.g., 1985-03-15)
- **gender**: Male or Female
- **phone**: Format: 555-XXXX
- **email**: Patient's email address
- **address**: Street address
- **city**: City name
- **state**: Two-letter state code (e.g., TX, IL, NY)
- **zip_code**: 5-digit ZIP code
- **blood_type**: O+, O-, A+, A-, B+, B-, AB+, AB-
- **allergies**: Semicolon-separated list or "None"

---

## Test Scenarios

### 1. New Patient Registration (ADT^A28)
**File**: `01_new_patient_registration.csv`

Tests adding new patient demographic records without visit context. Includes patients with Indian names and Texas addresses.

**Example Natural Language Commands**:
- "Add person Rajesh Kumar, DOB March 15, 1985, address 120 Main Street, Houston, Texas"
- "Register new patient Priya Sharma born July 22, 1990"

### 2. Outpatient Registration (ADT^A04)
**File**: `02_outpatient_registration.csv`

Tests outpatient clinic registration with visit details. Illinois-based patients for OPD visits.

**Example Natural Language Commands**:
- "Register patient Michael Chen for outpatient visit"
- "Create OPD registration for Sarah Johnson"

### 3. Inpatient Admission (ADT^A01)
**File**: `03_inpatient_admission.csv`

Tests hospital admission process. Massachusetts patients requiring inpatient beds.

**Example Natural Language Commands**:
- "Admit patient Thomas Moore to Ward 1"
- "Register inpatient admission for Nancy Jackson"

### 4. Emergency Department (ADT^A01/A04)
**File**: `04_emergency_department.csv`

Tests emergency admission scenarios. Florida patients with urgent care needs.

**Example Natural Language Commands**:
- "Emergency admission for Daniel Rodriguez"
- "Register ER patient Patricia Lewis"

### 5. Cardiology Patients (ADT^A28/A04)
**File**: `05_cardiology_patients.csv`

Tests cardiac department registrations. Arizona patients with cardiac medication allergies (Statins, Beta Blockers, ACE Inhibitors, Warfarin, Heparin).

**Example Natural Language Commands**:
- "Add cardiology patient Richard Scott with aspirin allergy"
- "Register cardiac patient Barbara Green for consultation"

### 6. Oncology Patients (ADT^A28/A04)
**File**: `06_oncology_patients.csv`

Tests cancer treatment registrations. Washington state patients with chemotherapy drug allergies (Cisplatin, Carboplatin, Paclitaxel, Doxorubicin).

**Example Natural Language Commands**:
- "Register oncology patient William Turner"
- "Add cancer patient Mary Phillips with Carboplatin allergy"

### 7. Maternity Patients (ADT^A01/A04)
**File**: `07_maternity_patients.csv`

Tests maternity ward registrations. Colorado patients (all female, childbearing age).

**Example Natural Language Commands**:
- "Register maternity patient Ashley Rogers"
- "Admit pregnant patient Amanda Reed for delivery"

### 8. Orthopedic Patients (ADT^A28/A04)
**File**: `08_orthopedic_patients.csv`

Tests orthopedic department registrations. Oregon patients with pain medication allergies.

**Example Natural Language Commands**:
- "Register orthopedic patient Andrew Cox"
- "Add bone fracture patient Brandon Howard"

### 9. Pediatric Surgery (ADT^A01/A04)
**File**: `09_pediatric_surgery.csv`

Tests pediatric surgical admissions. Georgia patients (all children aged 5-14).

**Example Natural Language Commands**:
- "Register pediatric surgery patient Oliver Kelly"
- "Admit child Sophia Sanders for surgical procedure"

### 10. Multi-specialty Clinic (ADT^A04/A28)
**File**: `10_multispecialty_clinic.csv`

Tests mixed patient population. New York patients with diverse allergies including multiple drug and food allergies.

**Example Natural Language Commands**:
- "Register clinic patient Alexander Perry"
- "Add patient Samantha Powell to multi-specialty clinic"

---

## Testing Instructions

### Upload via UI

1. **Start Backend**:
   ```bash
   cd backend
   venv\Scripts\activate
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend** (Angular or React):
   ```bash
   # Angular:
   cd frontend-angular
   npm start

   # OR React:
   cd frontend-react
   npm start
   ```

3. **Upload CSV File**:
   - Open the application UI
   - Click the attachment icon (📎)
   - Select one of the test CSV files
   - Click Send
   - Wait for processing confirmation

### Expected Results

For each successful upload, you should receive a response like:

```json
{
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
  "records_failed": 0
}
```

### Verification Steps

1. **Check Backend Logs**:
   ```bash
   tail -f backend/logs/interface-wizard.log
   ```

2. **Verify Mirth Connect**:
   - Open Mirth Connect Administrator
   - Check channel statistics for ADT messages received
   - View message logs

3. **Verify OpenEMR**:
   - Log into OpenEMR
   - Navigate to Patient/Client → Patients
   - Search for uploaded patients by name
   - Verify demographic data matches CSV

---

## Data Characteristics

### Geographic Distribution

- **Texas (TX)**: New Patient Registration
- **Illinois (IL)**: Outpatient Registration
- **Massachusetts (MA)**: Inpatient Admission
- **Florida (FL)**: Emergency Department
- **Arizona (AZ)**: Cardiology Patients
- **Washington (WA)**: Oncology Patients
- **Colorado (CO)**: Maternity Patients
- **Oregon (OR)**: Orthopedic Patients
- **Georgia (GA)**: Pediatric Surgery
- **New York (NY)**: Multi-specialty Clinic

### Age Distribution

- **Pediatric (0-18)**: Files 09
- **Adult (19-64)**: Files 01, 02, 04, 05, 06, 07, 08, 10
- **Geriatric (65+)**: File 03, some patients in files 05, 06

### Allergy Patterns

- **No Allergies**: "None"
- **Single Allergy**: "Penicillin"
- **Multiple Allergies**: "Penicillin;Amoxicillin" or "Peanuts;Shellfish"
- **Drug Allergies**: Penicillin, Sulfa drugs, Aspirin, Codeine, NSAIDs
- **Food Allergies**: Peanuts, Shellfish, Eggs, Milk, Soy
- **Other Allergies**: Latex, Iodine, Contrast Dye

### Blood Type Distribution

All major blood types represented: O+, O-, A+, A-, B+, B-, AB+, AB-

---

## Common Issues and Solutions

### Issue: "Missing required fields"
**Solution**: Ensure CSV has headers in first row

### Issue: "Invalid date format"
**Solution**: Use YYYY-MM-DD format (e.g., 1985-03-15)

### Issue: "All patients failed"
**Solution**:
- Check Mirth Connect is running
- Verify OpenEMR database connectivity
- Review backend logs for errors

### Issue: "Some patients succeeded, some failed"
**Solution**:
- Check error messages in response
- Verify duplicate patients aren't already in system
- Review Mirth channel logs

---

## Performance Benchmarks

Expected processing times (on standard hardware):

| Patients | Processing Time | HL7 Messages Generated |
|----------|----------------|------------------------|
| 10 | 5-10 seconds | 10 ADT messages |
| 50 | 20-30 seconds | 50 ADT messages |
| 100 | 40-60 seconds | 100 ADT messages |

---

## Advanced Testing Scenarios

### Bulk Import All Files

Test uploading all 10 files sequentially to create 100 patients:

```bash
# Upload files in order:
01_new_patient_registration.csv
02_outpatient_registration.csv
03_inpatient_admission.csv
...
10_multispecialty_clinic.csv

# Result: 100 total patients registered
```

### Error Testing

Intentionally modify CSV files to test error handling:

1. **Remove headers**: Test missing column names error
2. **Invalid dates**: Use "invalid-date" to test date parsing
3. **Missing names**: Remove first_name and last_name
4. **Special characters**: Add unicode characters to test encoding

---

## Data Sources

Test data is fictional and generated for testing purposes only. Names, addresses, phone numbers, and emails are not real.

---

## Summary

- **10 CSV files** covering major healthcare scenarios
- **100 total patients** with realistic demographic data
- **Multiple HL7 message types** (ADT^A28, ADT^A04, ADT^A01)
- **Diverse allergy profiles** including drugs, foods, and materials
- **Geographic variety** across 10 US states
- **Age range diversity** from pediatric to geriatric
- **Ready to test** with complete documentation

Use these files to thoroughly test the CSV upload feature and verify HL7 integration with OpenEMR!
