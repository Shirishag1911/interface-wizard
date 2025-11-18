"""Test script to verify CSV upload functionality."""
import requests

# Test 1: Simple command without file
print("Test 1: Simple command without file")
response1 = requests.post(
    "http://localhost:8000/api/v1/command",
    data={
        "command": "Test command",
        "session_id": "test-session"
    }
)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text[:200]}\n")

# Test 2: CSV file upload
print("Test 2: CSV file upload")
with open("docs/test_data/01_new_patient_registration.csv", "rb") as f:
    files = {"file": ("01_new_patient_registration.csv", f, "text/csv")}
    data = {
        "command": "Process uploaded file",
        "session_id": "test-session"
    }
    response2 = requests.post(
        "http://localhost:8000/api/v1/command",
        data=data,
        files=files
    )
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text[:500]}")
