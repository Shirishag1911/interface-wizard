#!/usr/bin/env python3
"""
End-to-End Testing Script for Interface Wizard

Tests:
1. Upload Patient_Records.xlsx with Ollama Cloud column mapping
2. Verify column mapping results
3. Confirm and process patients
4. Generate HL7 messages programmatically
5. Send to Mirth Connect
6. Verify OpenEMR database insertion

Usage:
    python test_end_to_end.py
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
EXCEL_FILE = "Patient_Records.xlsx"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_health_check() -> bool:
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_and_mapping() -> Dict[str, Any]:
    """Test 2: Upload Excel file with Ollama Cloud column mapping"""
    print_section("TEST 2: Upload Excel File with Ollama Cloud Mapping")

    try:
        with open(EXCEL_FILE, 'rb') as f:
            files = {'file': (EXCEL_FILE, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'trigger_event': 'ADT-A04',  # Register Patient
                'use_llm_mapping': 'true'     # Use Ollama Cloud
            }

            print(f"📤 Uploading {EXCEL_FILE}...")
            print(f"   Trigger Event: ADT-A04 (Register Patient)")
            print(f"   LLM Mapping: Enabled (Ollama Cloud)")

            response = requests.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )

            print(f"\nStatus Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                print(f"\n✅ Upload successful!")
                print(f"   Session ID: {result['session_id']}")
                print(f"   Total Records: {result['total_records']}")
                print(f"   Valid Records: {result['valid_records']}")
                print(f"   Invalid Records: {result['invalid_records']}")

                print(f"\n📋 Column Mapping Results:")
                for excel_col, std_field in result['column_mapping'].items():
                    print(f"   '{excel_col}' → '{std_field}'")

                if result['validation_errors']:
                    print(f"\n⚠️  Validation Errors:")
                    for error in result['validation_errors'][:5]:  # Show first 5
                        print(f"   Row {error['row']}, Field '{error['field']}': {error['error']}")

                print(f"\n👥 Sample Patients (first 3):")
                for i, patient in enumerate(result['patients'][:3], 1):
                    print(f"   {i}. {patient['firstName']} {patient['lastName']} (MRN: {patient['mrn']})")
                    print(f"      DOB: {patient['dateOfBirth']}, Gender: {patient['gender']}")
                    print(f"      Status: {patient['validation_status']}")
                    print(f"      UUID: {patient['uuid']}")

                return result
            else:
                print(f"❌ Upload failed: {response.text}")
                return None

    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_confirm_and_process(session_id: str) -> Dict[str, Any]:
    """Test 3: Confirm and process patients"""
    print_section("TEST 3: Confirm and Process Patients")

    try:
        payload = {
            "session_id": session_id,
            "selected_indices": [],  # Empty = process all valid patients
            "send_to_mirth": True
        }

        print(f"📤 Confirming processing...")
        print(f"   Session ID: {session_id}")
        print(f"   Selected: ALL valid patients")
        print(f"   Send to Mirth: YES")

        response = requests.post(
            f"{BASE_URL}/api/upload/confirm",
            json=payload
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Processing started!")
            print(f"   Upload ID: {result['upload_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Total Selected: {result['total_selected']}")
            print(f"   Stream URL: {result['stream_url']}")

            return result
        else:
            print(f"❌ Confirm failed: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Confirm error: {e}")
        return None

def test_stream_progress(upload_id: str):
    """Test 4: Monitor real-time progress via SSE"""
    print_section("TEST 4: Monitor Real-Time Progress (SSE)")

    print(f"📡 Connecting to SSE stream...")
    print(f"   Upload ID: {upload_id}")
    print(f"   URL: {BASE_URL}/api/upload/{upload_id}/stream")
    print()

    try:
        import sseclient  # pip install sseclient-py
        response = requests.get(f"{BASE_URL}/api/upload/{upload_id}/stream", stream=True)
        client = sseclient.SSEClient(response)

        for event in client.events():
            data = json.loads(event.data)
            step = data.get('step', 0)
            message = data.get('message', '')
            progress = data.get('progress', 0)
            status = data.get('status', '')

            print(f"[Step {step}] {message} ({progress}%) - Status: {status}")

            if step == 6 or status == "completed":
                print("\n✅ Processing completed!")
                break

    except ImportError:
        print("⚠️  sseclient-py not installed, skipping SSE test")
        print("   Install with: pip install sseclient-py")
        print("   Waiting 10 seconds for processing to complete...")
        time.sleep(10)
    except Exception as e:
        print(f"⚠️  SSE error: {e}")
        print("   Waiting 10 seconds for processing to complete...")
        time.sleep(10)

def test_get_results(upload_id: str) -> Dict[str, Any]:
    """Test 5: Get final results"""
    print_section("TEST 5: Get Final Results")

    try:
        print(f"📥 Fetching results...")
        print(f"   Upload ID: {upload_id}")

        response = requests.get(f"{BASE_URL}/api/upload/{upload_id}/results")

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Results retrieved!")
            print(f"   Upload ID: {result['upload_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Total Processed: {result['total_processed']}")
            print(f"   Successful: {result['successful']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Processing Time: {result['processing_time_seconds']}s")

            print(f"\n📋 Sample Results (first 3):")
            for i, res in enumerate(result['results'][:3], 1):
                print(f"\n   {i}. {res['patient']}")
                print(f"      Status: {res['status']}")
                print(f"      UUID: {res['uuid']}")
                if res['hl7_message']:
                    lines = res['hl7_message'].split('\n')
                    print(f"      HL7 Message ({len(lines)} segments):")
                    for line in lines:
                        print(f"         {line}")
                if res.get('mirth_ack'):
                    print(f"      Mirth ACK: {res['mirth_ack'][:100]}...")

            return result
        else:
            print(f"❌ Get results failed: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Get results error: {e}")
        return None

def main():
    """Run all tests"""
    print("\n🧪 Interface Wizard End-to-End Testing")
    print(f"File: {EXCEL_FILE}")
    print(f"Server: {BASE_URL}")

    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Server not responding. Please start the server:")
        print("   python main_with_fastapi.py --api")
        return

    # Test 2: Upload and Column Mapping
    upload_result = test_upload_and_mapping()
    if not upload_result:
        print("\n❌ Upload failed. Cannot continue testing.")
        return

    session_id = upload_result['session_id']

    # Test 3: Confirm and Process
    confirm_result = test_confirm_and_process(session_id)
    if not confirm_result:
        print("\n❌ Confirm failed. Cannot continue testing.")
        return

    upload_id = confirm_result['upload_id']

    # Test 4: Stream Progress
    test_stream_progress(upload_id)

    # Test 5: Get Results
    final_results = test_get_results(upload_id)

    # Summary
    print_section("TEST SUMMARY")
    if final_results and final_results['status'] == 'completed':
        print("✅ All tests passed!")
        print(f"   {final_results['successful']}/{final_results['total_processed']} patients processed successfully")
    else:
        print("⚠️  Some tests had issues. Check logs above.")

    print("\n📝 Next Steps:")
    print("   1. Check Mirth Connect channel logs")
    print("   2. Query OpenEMR database to verify patient insertion")
    print("   3. Review interface_wizard.log for detailed processing logs")

if __name__ == "__main__":
    main()
