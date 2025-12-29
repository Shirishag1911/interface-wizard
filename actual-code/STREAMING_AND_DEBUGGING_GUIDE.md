# Streaming Workflow & Debugging Guide

## Quick Reference: Upload ID and Streaming

### How the Workflow Works

```
1. POST /api/upload
   ↓ Returns: session_id

2. POST /api/upload/confirm
   ↓ Returns: upload_id + stream_url

3. GET /api/upload/{upload_id}/stream
   ↓ Real-time progress via SSE

4. GET /api/upload/{upload_id}/results
   ↓ Final results
```

---

## Understanding Upload ID vs Session ID

### Session ID (from Step 1)
- **Obtained from**: `POST /api/upload` response
- **Purpose**: Temporary storage of parsed patient data
- **Lifetime**: 1 hour
- **Used for**: Confirming which patients to process

**Example**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patients": [...]
}
```

### Upload ID (from Step 2)
- **Obtained from**: `POST /api/upload/confirm` response
- **Purpose**: Track the processing job
- **Used for**: Monitoring progress and getting results
- **Where to find it**: In the `ConfirmUploadResponse`

**Example**:
```json
{
  "upload_id": "upload_1735470600_abc123",
  "status": "processing",
  "stream_url": "/api/upload/upload_1735470600_abc123/stream"
}
```

---

## Complete Workflow Example

### Step 1: Upload File

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@patients.csv" \
  > upload_response.json

# Extract session_id
SESSION_ID=$(cat upload_response.json | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
```

### Step 2: Confirm and Get Upload ID

```bash
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"selected_indices\": [],
    \"send_to_mirth\": true
  }" \
  > confirm_response.json

# Extract upload_id
UPLOAD_ID=$(cat confirm_response.json | jq -r '.upload_id')
STREAM_URL=$(cat confirm_response.json | jq -r '.stream_url')

echo "Upload ID: $UPLOAD_ID"
echo "Stream URL: http://localhost:8000$STREAM_URL"
```

### Step 3: Monitor Progress (SSE Stream)

**Option A: Using JavaScript/Frontend**:
```javascript
// After getting the confirm response
const confirmResponse = await fetch('http://localhost:8000/api/upload/confirm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    selected_indices: [],
    send_to_mirth: true
  })
});

const data = await confirmResponse.json();
console.log('Upload ID:', data.upload_id);
console.log('Stream URL:', data.stream_url);

// NOW connect to the stream using the upload_id
const eventSource = new EventSource(
  `http://localhost:8000${data.stream_url}`
);

eventSource.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Step ${progress.step}: ${progress.message} (${progress.progress}%)`);

  if (progress.status === 'completed' || progress.status === 'failed') {
    eventSource.close();
    console.log('Processing finished!');
  }
};

eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};
```

**Option B: Using curl (for testing)**:
```bash
# Stream progress (this will stay open until processing completes)
curl -N http://localhost:8000/api/upload/$UPLOAD_ID/stream
```

### Step 4: Get Final Results

```bash
# After streaming completes
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | jq .
```

---

## Debug Logging Features

### What's Being Logged

The backend now logs **comprehensive details** for every Mirth transmission:

#### 1. Connection Attempts
```
🚀 STARTING MIRTH TRANSMISSION
📍 Target: localhost:6661
📏 HL7 Message Length: 450 characters
```

#### 2. Message Details
```
📋 MSH Segment: MSH|^~\&|InterfaceWizard|IW|Mirth|Mirth|20251229...
👤 PID Segment: PID|1||MRN001^^^MRN||Doe^John||19800515|M...
🆔 ZPI Segment (UUID): ZPI|a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

#### 3. MLLP Protocol
```
📦 MLLP Message Size: 520 bytes
🔧 MLLP Envelope: START_BLOCK(0x0b) + HL7 + END_BLOCK(0x1c 0x0d)
⏰ Socket timeout set to 15 seconds
```

#### 4. Connection Status
```
🔌 Attempting to connect to localhost:6661...
✅ CONNECTION ESTABLISHED to localhost:6661
```

#### 5. Transmission
```
📤 Sending MLLP message (520 bytes)...
✅ MESSAGE SENT SUCCESSFULLY
```

#### 6. ACK Response
```
⏳ Waiting for ACK response from Mirth...
📨 Received response (150 bytes)
📬 ACK Message: MSH|^~\&|Mirth|Mirth|...
✅ ACK STATUS: POSITIVE (AA/CA found)
```

#### 7. Error Details (if any)
```
❌ CONNECTION REFUSED ERROR
   - Mirth Host: localhost
   - Mirth Port: 6661
   - Possible causes:
     1. Mirth Connect is not running
     2. Channel is not deployed/started
     3. Wrong port number (check Mirth channel settings)
     4. Firewall blocking connection
```

---

## Where to Find Logs

### Console Output
When you run the server, you'll see real-time logs in the terminal:

```bash
python main_with_fastapi.py --api

# You'll see logs like:
2025-12-29 11:30:00 - __main__ - INFO - 🚀 STARTING MIRTH TRANSMISSION
2025-12-29 11:30:00 - __main__ - INFO - 📍 Target: localhost:6661
...
```

### Log File
All logs are also saved to `interface_wizard.log` in the same directory:

```bash
# View live logs
tail -f interface_wizard.log

# Search for specific upload
grep "Upload ID: upload_1735470600_abc123" interface_wizard.log

# Search for errors
grep "ERROR" interface_wizard.log

# Search for Mirth transmissions
grep "MIRTH TRANSMISSION" interface_wizard.log
```

---

## Debugging Mirth Connection Issues

### Issue: "Connection Refused"

**Log Output**:
```
❌ CONNECTION REFUSED ERROR
   - Mirth Host: localhost
   - Mirth Port: 6661
```

**Troubleshooting Steps**:

1. **Check Mirth is Running**:
   ```bash
   # Linux/Mac
   ps aux | grep mirth

   # Windows
   tasklist | findstr mirth
   ```

2. **Check Port is Listening**:
   ```bash
   # Linux/Mac
   netstat -an | grep 6661
   lsof -i :6661

   # Windows
   netstat -an | findstr 6661
   ```

3. **Test Connection**:
   ```bash
   telnet localhost 6661
   # Should connect without error
   ```

4. **Check Mirth Administrator**:
   - Open Mirth Connect Administrator
   - Check channel status (should be green/started)
   - Verify channel listener port is 6661
   - Check channel logs for any errors

5. **Verify MLLP Listener Settings**:
   - In Mirth Administrator, open your channel
   - Source Connector → MLLP Listener
   - Verify "Listener Port" = 6661

---

### Issue: "Message Sent but Not in Mirth"

**Symptom**: Logs show "✅ MESSAGE SENT SUCCESSFULLY" but Mirth has no record.

**Possible Causes**:

1. **Wrong Channel**: Message sent to different port
   - Check `MIRTH_PORT` in main_with_fastapi.py matches channel port
   - Check logs for: `📍 Target: localhost:XXXX`

2. **Channel Filtering**: Mirth filtering/rejecting the message
   - Check Mirth channel "Filter" tab
   - Check Mirth channel logs in Administrator UI

3. **Destination Issue**: Message received but not processed
   - Check Mirth channel "Destination" tab
   - Check database connection settings
   - Check channel transformers

4. **ACK Not Checked**: Message received but no confirmation
   - Look for: `📬 ACK Message: ...` in logs
   - Verify ACK contains "AA" or "CA" for success

**Debug Steps**:

```bash
# 1. Check exactly what's being sent
grep "MSH Segment:" interface_wizard.log | tail -5

# 2. Check connection details
grep "Target:" interface_wizard.log | tail -5

# 3. Check ACK responses
grep "ACK Message:" interface_wizard.log | tail -5

# 4. Look for full transmission log
grep -A 20 "STARTING MIRTH TRANSMISSION" interface_wizard.log | tail -25
```

---

### Issue: "Timeout Waiting for ACK"

**Log Output**:
```
❌ TIMEOUT ERROR: Connection timeout!
   - Checked host: localhost
   - Checked port: 6661
   - Timeout: 15 seconds
```

**Possible Causes**:

1. **Mirth Not Responding**: Channel stuck or overloaded
2. **Network Issues**: Slow connection
3. **Transformer Error**: Mirth channel transformer failing

**Solutions**:

1. Check Mirth channel logs for errors
2. Restart Mirth channel
3. Check transformer JavaScript for errors
4. Reduce message rate (already has 1-second delay)

---

## Testing Without Mirth

If you want to test the workflow without sending to Mirth:

```bash
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id-here",
    "selected_indices": [],
    "send_to_mirth": false
  }'
```

Logs will show:
```
⏭️  STEP 3: Skipped - send_to_mirth is disabled
```

---

## Complete Example Session

```bash
# 1. Start backend with visible logs
python main_with_fastapi.py --api

# In another terminal:

# 2. Upload file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test_patients.csv" > upload.json

SESSION_ID=$(cat upload.json | jq -r '.session_id')
echo "Session: $SESSION_ID"

# 3. Confirm processing
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"selected_indices\": [], \"send_to_mirth\": true}" \
  > confirm.json

UPLOAD_ID=$(cat confirm.json | jq -r '.upload_id')
echo "Upload ID: $UPLOAD_ID"

# 4. Stream progress
curl -N http://localhost:8000/api/upload/$UPLOAD_ID/stream

# 5. Get results (after streaming completes)
curl http://localhost:8000/api/upload/$UPLOAD_ID/results | jq .

# 6. Check logs for any issues
grep -A 50 "Upload ID: $UPLOAD_ID" interface_wizard.log
```

---

## Log Analysis Commands

### Find All Uploads for a Session
```bash
SESSION_ID="your-session-id"
grep "$SESSION_ID" interface_wizard.log
```

### Find All Mirth Transmissions
```bash
grep "STARTING MIRTH TRANSMISSION" interface_wizard.log
```

### Count Successful vs Failed
```bash
# Successful
grep "ACK STATUS: POSITIVE" interface_wizard.log | wc -l

# Failed
grep "CONNECTION REFUSED\|TIMEOUT ERROR\|ACK STATUS: NEGATIVE" interface_wizard.log | wc -l
```

### View Last 5 Processing Jobs
```bash
grep "STARTING CONFIRMED PATIENT PROCESSING" interface_wizard.log | tail -5
```

### Find Errors Only
```bash
grep "ERROR\|❌" interface_wizard.log | tail -20
```

---

## Frontend Integration Example

### Complete React Component

```javascript
import React, { useState, useEffect } from 'react';

function PatientUploadWithLogging() {
  const [sessionId, setSessionId] = useState(null);
  const [uploadId, setUploadId] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  const addLog = (message) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const handleUpload = async (file) => {
    addLog('Uploading file...');

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/api/upload', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    setSessionId(data.session_id);
    setPreviewData(data);

    addLog(`✅ Upload complete. Session ID: ${data.session_id}`);
    addLog(`Total records: ${data.total_records}, Valid: ${data.valid_records}`);
  };

  const handleConfirm = async () => {
    addLog('Confirming patient selection...');

    const response = await fetch('http://localhost:8000/api/upload/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        selected_indices: [],
        send_to_mirth: true
      })
    });

    const data = await response.json();
    setUploadId(data.upload_id);

    addLog(`✅ Processing started. Upload ID: ${data.upload_id}`);
    addLog(`Stream URL: ${data.stream_url}`);

    // Start SSE stream
    const eventSource = new EventSource(
      `http://localhost:8000${data.stream_url}`
    );

    eventSource.onmessage = (event) => {
      const progressData = JSON.parse(event.data);
      setProgress(progressData.progress);

      addLog(`[${progressData.progress}%] ${progressData.message}`);

      if (progressData.status === 'completed') {
        eventSource.close();
        addLog('✅ Processing completed!');
      } else if (progressData.status === 'failed') {
        eventSource.close();
        addLog('❌ Processing failed!');
      }
    };

    eventSource.onerror = (error) => {
      eventSource.close();
      addLog('❌ Stream error occurred');
    };
  };

  return (
    <div>
      <h2>Patient Upload with Debug Logging</h2>

      <input
        type="file"
        onChange={(e) => handleUpload(e.target.files[0])}
      />

      {previewData && (
        <div>
          <h3>Preview</h3>
          <p>Total: {previewData.total_records}, Valid: {previewData.valid_records}</p>
          <button onClick={handleConfirm}>Confirm & Process</button>
        </div>
      )}

      <div style={{ marginTop: '20px' }}>
        <h3>Progress: {progress}%</h3>
        <div style={{
          width: '100%',
          height: '30px',
          backgroundColor: '#eee',
          borderRadius: '5px'
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            backgroundColor: '#4CAF50',
            borderRadius: '5px',
            transition: 'width 0.3s'
          }}></div>
        </div>
      </div>

      <div style={{ marginTop: '20px', fontFamily: 'monospace' }}>
        <h3>Logs</h3>
        <div style={{
          maxHeight: '300px',
          overflow: 'auto',
          backgroundColor: '#f5f5f5',
          padding: '10px',
          border: '1px solid #ccc'
        }}>
          {logs.map((log, idx) => (
            <div key={idx}>{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default PatientUploadWithLogging;
```

---

## Summary

### Key Points

1. **Session ID** = From upload, used for confirmation
2. **Upload ID** = From confirmation, used for streaming/results
3. **Logs** = Console + `interface_wizard.log` file
4. **Mirth Debugging** = Check connection, port, channel status
5. **Stream URL** = Returned in confirm response, contains upload_id

### Quick Troubleshooting Checklist

- [ ] Check `interface_wizard.log` for detailed logs
- [ ] Verify `upload_id` from confirm response
- [ ] Verify Mirth is running (ps/tasklist)
- [ ] Verify port 6661 is listening (netstat)
- [ ] Check Mirth channel is started (green status)
- [ ] Test connection (telnet localhost 6661)
- [ ] Review ACK messages in logs
- [ ] Check for error messages in logs

---

**Happy Debugging! 🐛🔍**
