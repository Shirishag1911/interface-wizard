# HL7 Test Scenarios - Comprehensive CSV Test Data

This folder contains **10 CSV test files** with complete HL7 message scenario information including trigger events, required segments, natural language commands, patient demographics, and use cases.

---

## 📋 File Overview

| # | File | HL7 Trigger Event | Scenario | Patients | Use Case |
|---|------|-------------------|----------|----------|----------|
| 1 | `01_person_registration_ADT_A28.csv` | **ADT^A28** | Add Person/Patient Information | 10 | New patient demographic records without visit context |
| 2 | `02_patient_registration_ADT_A04.csv` | **ADT^A04** | Register a Patient | 10 | Outpatient registration, ER visits, pre-admission |
| 3 | `03_inpatient_admission_ADT_A01.csv` | **ADT^A01** | Admit/Visit Notification | 10 | Hospital inpatient admissions with bed assignment |
| 4 | `04_appointment_booking_SIU_S12.csv` | **SIU^S12** | New Appointment Booking | 10 | Outpatient appointment scheduling |
| 5 | `05_lab_results_ORU_R01.csv` | **ORU^R01** | Laboratory Results | 10 | Lab test results (CBC, lipids, chemistry panels) |
| 6 | `06_patient_discharge_ADT_A03.csv` | **ADT^A03** | Patient Discharge | 10 | Hospital discharge notifications |
| 7 | `07_patient_transfer_ADT_A02.csv` | **ADT^A02** | Patient Transfer | 10 | Inter-department transfers within hospital |
| 8 | `08_update_patient_ADT_A08.csv` | **ADT^A08** | Update Patient Info | 10 | Demographic updates and corrections |
| 9 | `09_cancel_admission_ADT_A11.csv` | **ADT^A11** | Cancel Admission | 10 | Cancel scheduled admissions |
| 10 | `10_merge_patients_ADT_A40.csv` | **ADT^A40** | Merge Patient Records | 10 | Merge duplicate patient accounts |

---

## 📊 CSV File Structure

Each CSV file contains the following columns:

```
no,trigger_event,required_segments,natural_language_command,first_name,last_name,date_of_birth,gender,phone,email,address,city,state,zip_code,blood_type,allergies,use_case
```

### Column Descriptions

| Column | Description | Example |
|--------|-------------|---------|
| **no** | Record number (1-10) | `1` |
| **trigger_event** | HL7 message type | `ADT^A28` |
| **required_segments** | HL7 segments needed | `MSH;EVN;PID;PV1` |
| **natural_language_command** | AI command to generate message | `Add person Nilesh Patel DOB 27 March 1990` |
| **first_name** | Patient's first name | `Rajesh` |
| **last_name** | Patient's last name | `Kumar` |
| **date_of_birth** | Format: YYYY-MM-DD | `1985-03-15` |
| **gender** | Male or Female | `Male` |
| **phone** | Contact number | `555-1001` |
| **email** | Email address | `rajesh.kumar@email.com` |
| **address** | Street address | `120 Main Street` |
| **city** | City name | `Houston` |
| **state** | Two-letter state code | `TX` |
| **zip_code** | 5-digit ZIP | `77001` |
| **blood_type** | Blood group | `O+` |
| **allergies** | Semicolon-separated or "None" | `Penicillin` |
| **use_case** | HL7 scenario description | `A new patient is added to the system` |

---

## 🎯 HL7 Message Type Details

### 1. ADT^A28 - Add Person or Patient Information
**File**: `01_person_registration_ADT_A28.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Create new patient demographic records without clinical encounter context.

**Use Cases**:
- New patient registration at health system
- Person record creation before first visit
- Non-visit-based demographic updates
- Master Patient Index (MPI) updates

**Sample Natural Language Command**:
```
"Add person Rajesh Kumar date of birth 15 March 1985. Address 120 Main Street Houston Texas"
```

**Geographic Focus**: Texas (TX)

---

### 2. ADT^A04 - Register a Patient
**File**: `02_patient_registration_ADT_A04.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Register patients for outpatient visits or emergency department encounters.

**Use Cases**:
- Outpatient clinic registration
- Emergency Department visits
- Pre-admission registration
- Walk-in patient registration

**Sample Natural Language Command**:
```
"Register patient Michael Chen DOB 12 January 1975 for outpatient visit"
```

**Geographic Focus**: Illinois (IL)

---

### 3. ADT^A01 - Admit/Visit Notification
**File**: `03_inpatient_admission_ADT_A01.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Admit patients to inpatient beds with location assignment.

**Use Cases**:
- Inpatient hospital admission
- Emergency admission to ward
- Transfer from outpatient to inpatient
- Clinical system notification of admission

**Sample Natural Language Command**:
```
"Admit patient Thomas Moore DOB 20 May 1960 to Ward 1 Bed 12"
```

**Geographic Focus**: Massachusetts (MA)

---

### 4. SIU^S12 - Notification of New Appointment Booking
**File**: `04_appointment_booking_SIU_S12.csv`

**Required Segments**: MSH, SCH, PID, AIP

**Purpose**: Schedule outpatient appointments with providers.

**Use Cases**:
- Outpatient clinic appointments
- Specialist consultations
- Follow-up visit scheduling
- Diagnostic procedure appointments

**Sample Natural Language Command**:
```
"Schedule appointment for Daniel Rodriguez DOB 15 January 1987 with Dr Smith at 10AM tomorrow"
```

**Geographic Focus**: Florida (FL)

---

### 5. ORU^R01 - Observation Result (Unsolicited)
**File**: `05_lab_results_ORU_R01.csv`

**Required Segments**: MSH, PID, PV1, ORC, OBR, OBX

**Purpose**: Transmit laboratory and diagnostic test results.

**Use Cases**:
- Laboratory test results (CBC, chemistry panels)
- Microbiology culture results
- Radiology findings
- Pathology reports

**Sample Natural Language Command**:
```
"Create CBC lab result for patient Richard Scott DOB 10 June 1952"
```

**Lab Tests Included**:
- Complete Blood Count (CBC)
- Lipid Panel
- Comprehensive Metabolic Panel (CMP)
- HbA1c (Diabetes monitoring)
- Thyroid Function Tests
- Liver Function Tests (LFT)
- Cardiac Enzymes
- Urinalysis
- Coagulation Panel
- Blood Cultures

**Geographic Focus**: Arizona (AZ)

---

### 6. ADT^A03 - Discharge a Patient
**File**: `06_patient_discharge_ADT_A03.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Notify systems of patient discharge from inpatient care.

**Use Cases**:
- Discharge to home
- Discharge to skilled nursing facility
- Discharge with home health services
- Discharge against medical advice (AMA)
- Post-discharge follow-up

**Sample Natural Language Command**:
```
"Discharge patient William Turner DOB 12 May 1965 from oncology ward"
```

**Geographic Focus**: Washington (WA)

---

### 7. ADT^A02 - Transfer a Patient
**File**: `07_patient_transfer_ADT_A02.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Transfer patients between departments or care units.

**Use Cases**:
- Ward to ICU transfer
- ICU to step-down unit
- Emergency to surgical floor
- Inter-departmental transfers

**Sample Natural Language Command**:
```
"Transfer patient Ashley Rogers DOB 10 March 1992 from Ward 1 to ICU"
```

**Transfer Types**:
- General Ward → ICU
- ER → Surgical Floor
- ICU → Step-Down Unit
- Maternity → Postpartum
- Medical Ward → Telemetry
- Pediatrics → PICU

**Geographic Focus**: Colorado (CO)

---

### 8. ADT^A08 - Update Patient Information
**File**: `08_update_patient_ADT_A08.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Update existing patient demographic or account information.

**Use Cases**:
- Address change
- Phone number update
- Email update
- Insurance information update
- Allergy list update
- Emergency contact update
- Primary care provider change
- Marital status change
- Language preference update

**Sample Natural Language Command**:
```
"Update patient information for Andrew Cox DOB 14 February 1970. New address 161 Orthopedic Way Portland OR"
```

**Geographic Focus**: Oregon (OR)

---

### 9. ADT^A11 - Cancel Admit/Visit Notification
**File**: `09_cancel_admission_ADT_A11.csv`

**Required Segments**: MSH, EVN, PID, PV1

**Purpose**: Cancel previously scheduled admissions.

**Use Cases**:
- Patient no-show
- Surgery postponed
- Condition improved (no longer needed)
- Insurance authorization pending
- Transfer to another facility
- Family declined admission
- Duplicate entry correction
- Emergency elsewhere
- Clinical decision changed

**Sample Natural Language Command**:
```
"Cancel admission for Oliver Kelly DOB 12 April 2010. Patient did not show"
```

**Geographic Focus**: Georgia (GA) - Pediatric patients

---

### 10. ADT^A40 - Merge Patient - Patient Identifier List
**File**: `10_merge_patients_ADT_A40.csv`

**Required Segments**: MSH, EVN, PID, MRG

**Purpose**: Merge duplicate patient records into single account.

**Use Cases**:
- Duplicate MRN consolidation
- Same patient with different identifiers
- Registration error correction
- Name change (marriage/legal)
- Link fragmented records
- Database cleanup
- Consolidate medical history

**Sample Natural Language Command**:
```
"Merge patient records for Alexander Perry DOB 15 January 1968. Duplicate MRN found"
```

**Geographic Focus**: New York (NY)

---

## 🧪 Testing Instructions

### Option 1: Upload via Interface Wizard UI

1. **Start Backend Server**:
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
   - Open application in browser
   - Click attachment icon (📎) next to message input
   - Select one of the CSV files from `docs/hl7_test_scenarios/`
   - Click Send button
   - Wait for processing confirmation

4. **Verify Results**:
   - Check response message showing success/failure counts
   - Verify HL7 messages in Mirth Connect
   - Confirm patient data in OpenEMR database

### Option 2: API Testing with cURL

```bash
curl -X POST http://localhost:8000/api/v1/command \
  -F "command=Process patient data from CSV" \
  -F "session_id=test-session-123" \
  -F "file=@docs/hl7_test_scenarios/01_person_registration_ADT_A28.csv"
```

### Option 3: Batch Testing All Scenarios

Upload all 10 files sequentially to test complete HL7 workflow:

1. Person Registration (ADT^A28)
2. Patient Registration (ADT^A04)
3. Inpatient Admission (ADT^A01)
4. Appointment Booking (SIU^S12)
5. Lab Results (ORU^R01)
6. Patient Discharge (ADT^A03)
7. Patient Transfer (ADT^A02)
8. Update Patient (ADT^A08)
9. Cancel Admission (ADT^A11)
10. Merge Patients (ADT^A40)

**Expected Result**: 100 total patients processed across all HL7 message types

---

## ✅ Expected Results

### Successful Upload Response

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
  "protocol_used": "hl7v2",
  "created_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:30:15Z"
}
```

### HL7 Message Verification

**Check Mirth Connect**:
1. Open Mirth Connect Administrator
2. Navigate to Dashboard
3. View channel statistics for:
   - ADT messages received (A01, A02, A03, A04, A08, A11, A28, A40)
   - SIU messages received (S12)
   - ORU messages received (R01)
4. Click "Messages" to view detailed HL7 content

**Check OpenEMR Database**:
```sql
-- Verify patients created
SELECT * FROM patient_data
WHERE fname IN ('Rajesh', 'Michael', 'Thomas')
ORDER BY date DESC
LIMIT 10;

-- Check admissions
SELECT * FROM form_encounter
WHERE date >= CURDATE()
ORDER BY date DESC;
```

---

## 📈 Data Characteristics

### Geographic Distribution

Each file focuses on different US states for realistic testing:

- **Texas (TX)**: Person Registration (ADT^A28)
- **Illinois (IL)**: Patient Registration (ADT^A04)
- **Massachusetts (MA)**: Inpatient Admission (ADT^A01)
- **Florida (FL)**: Appointment Booking (SIU^S12)
- **Arizona (AZ)**: Lab Results (ORU^R01)
- **Washington (WA)**: Patient Discharge (ADT^A03)
- **Colorado (CO)**: Patient Transfer (ADT^A02)
- **Oregon (OR)**: Update Patient (ADT^A08)
- **Georgia (GA)**: Cancel Admission (ADT^A11) - Pediatric
- **New York (NY)**: Merge Patients (ADT^A40)

### Age Demographics

- **Pediatric (0-18)**: File 09 (ages 5-14)
- **Adult (19-64)**: Files 01, 02, 04, 05, 07, 08, 10
- **Geriatric (65+)**: Files 03, 06 (some patients)

### Allergy Profiles

- **Drug Allergies**: Penicillin, Sulfa drugs, Aspirin, Codeine, NSAIDs, Statins, Beta Blockers, ACE Inhibitors, Warfarin, Heparin
- **Food Allergies**: Peanuts, Shellfish, Eggs, Milk, Soy, Tree Nuts
- **Material Allergies**: Latex, Iodine, Contrast Dye, Adhesive
- **Chemotherapy Allergies**: Cisplatin, Carboplatin, Paclitaxel, Doxorubicin, 5-FU, Methotrexate

### Blood Type Distribution

All major blood types represented: O+, O-, A+, A-, B+, B-, AB+, AB-

---

## 🔍 Natural Language Processing

Each CSV includes realistic natural language commands that demonstrate how users would interact with the system:

### Examples by Message Type

**ADT^A28 (Add Person)**:
- "Add person Rajesh Kumar date of birth 15 March 1985. Address 120 Main Street Houston Texas"
- "Register new patient Priya Sharma born 22 July 1990"

**ADT^A04 (Register Patient)**:
- "Register patient Michael Chen DOB 12 January 1975 for outpatient visit"
- "Register Sarah Johnson born 25 June 1988 for OPD appointment"

**ADT^A01 (Admit Patient)**:
- "Admit patient Thomas Moore DOB 20 May 1960 to Ward 1 Bed 12"
- "Admit Nancy Jackson born 15 October 1968 to ICU Room 3"

**SIU^S12 (Schedule Appointment)**:
- "Schedule appointment for Daniel Rodriguez with Dr Smith at 10AM tomorrow"
- "Book appointment for Patricia Lewis with Dr Johnson at cardiology clinic"

**ORU^R01 (Lab Results)**:
- "Create CBC lab result for patient Richard Scott"
- "Generate lipid panel results for Barbara Green"

---

## 🚨 Troubleshooting

### Issue: CSV Upload Fails

**Check**:
1. File encoding is UTF-8
2. All required columns are present
3. Date format is YYYY-MM-DD
4. No special characters causing parsing errors

### Issue: Some Patients Fail to Create

**Check**:
1. Mirth Connect is running
2. HL7 listener channel is active
3. OpenEMR database connection
4. Review error messages in response
5. Check backend logs: `backend/logs/interface-wizard.log`

### Issue: HL7 Messages Not Received

**Check**:
1. MLLP connection to Mirth (default port: 6661)
2. Mirth channel is started
3. Firewall settings allow MLLP traffic
4. Backend .env file has correct MLLP_HOST and MLLP_PORT

---

## 📚 Documentation References

- **HL7 v2.x Specification**: http://www.hl7.org/implement/standards/product_brief.cfm?product_id=185
- **Mirth Connect User Guide**: https://www.nextgen.com/products-and-services/mirth-connect
- **OpenEMR Documentation**: https://www.open-emr.org/wiki/
- **CSV Upload Guide**: `../CSV_UPLOAD_GUIDE.md`
- **Backend Integration**: `../BACKEND_MIRTH_INTEGRATION.md`

---

## 📊 Summary

- **10 CSV files** covering major HL7 message types
- **100 total test patients** with complete demographics
- **10 different HL7 trigger events** (ADT^A01-A40, SIU^S12, ORU^R01)
- **Natural language commands** for each scenario
- **Use case descriptions** for clinical context
- **Required HL7 segments** documented
- **Geographic diversity** across 10 US states
- **Realistic allergy profiles** and medical data
- **Complete testing workflow** from upload to verification

Use these comprehensive test scenarios to thoroughly validate the Interface Wizard CSV upload feature and HL7 integration with OpenEMR!
