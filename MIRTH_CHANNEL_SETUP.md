# Mirth Connect Channel Setup Guide

## 🎯 What is a Mirth Channel?

A **Mirth Channel** is a message processing pipeline that:

1. **Listens** for HL7 messages (MLLP Listener)
2. **Receives** messages from Interface Wizard
3. **Transforms** them if needed (optional)
4. **Sends** them to OpenEMR or stores them

**Why do we need it?**
- Interface Wizard generates HL7 messages
- These messages need to be sent somewhere
- Mirth acts as the "receiver" and "router"
- Without it, messages have nowhere to go = timeout errors

---

## 📋 Step-by-Step Channel Creation

### Step 1: Open Mirth Administrator

1. Open Mirth Connect Administrator (should be running)
2. Connect to: `localhost:8080` or `localhost:4443`
3. Login with: `admin` / `Admin@123`

### Step 2: Create New Channel

1. Click **"Channels"** in the left menu
2. Click **"New Channel"** button (or right-click → New Channel)

### Step 3: Configure Channel Settings

**General Tab:**
```
Channel Name: Interface Wizard HL7 Listener
Description: Receives HL7 messages from Interface Wizard application
Data Type: HL7 v2.x
```

Click **"Set Data Types"** and select: **HL7 v2.x** for both

### Step 4: Configure Source (Listener)

Click on **"Source"** tab:

**Connector Type:**
- Select: **MLLP Listener**

**Listener Settings:**
```
Local Address: 0.0.0.0
Local Port: 6661

⚠️ IMPORTANT: This port MUST be 6661 (matches backend/.env MLLP_PORT)
```

**Other Settings:**
```
Server Mode: Yes (default)
Receive Timeout: 0 (no timeout)
Buffer Size: 65536
Max Connections: 10
```

**Response Settings:**
```
Response:
  - Select "Auto-generate (After source transformer)"
  - This will send ACK messages back to Interface Wizard
```

### Step 5: Configure Destination

Click on **"Destinations"** tab, then **"Add New Destination"**:

**Option A: Database Writer (Recommended for Testing)**

**Connector Type:** Database Writer

**Database Settings:**
```
Driver: MySQL
URL: jdbc:mysql://localhost:3306/openemr
Username: openemr
Password: openemr
```

**SQL Statement:**
```sql
INSERT INTO interface_wizard_messages
(message_id, message_type, message_content, received_at)
VALUES
(${message.messageId}, ${message.messageType}, ${message}, NOW())
```

**Note:** You may need to create this table first (see below)

---

**Option B: Channel Writer (Forward to existing OpenEMR channel)**

**Connector Type:** Channel Writer

**Settings:**
```
Channel: [Select your existing OpenEMR HL7 channel]
```

---

**Option C: File Writer (Simple Testing)**

**Connector Type:** File Writer

**Settings:**
```
Directory: C:\mirth_messages\
File Name: ${DATE_TIME}_${message.messageId}.hl7
```

This saves each message as a file for easy inspection.

### Step 6: Deploy Channel

1. Click **"Save Changes"** (disk icon)
2. Click **"Deploy Channel"** (play icon in toolbar)
3. Right-click on channel → **"Start"**
4. Status should change to: **Started** (green)

---

## 🧪 Test the Channel

### Test 1: Send Test Message from Mirth

1. Right-click on your channel
2. Select **"Send Message"**
3. Paste this test HL7 message:

```
MSH|^~\&|INTERFACE_WIZARD|IW|OpenEMR|OpenEMR|20241114120000||ADT^A28^ADT_A05|TEST123|P|2.5
EVN|A28|20241114120000
PID|1|MRN12345|MRN12345||Doe^John^||19900115|M
```

4. Click **"Send"**
5. Check **"Dashboard"** for message count
6. Should see: Received: 1, Sent: 1

### Test 2: Check Channel Logs

1. Click on channel
2. Click **"Messages"** tab at bottom
3. You should see:
   - Message ID
   - Status: SENT
   - Raw message content

---

## 🔧 Create Database Table (If Using Database Writer)

If you chose **Database Writer**, create this table in OpenEMR database:

```sql
-- Connect to MySQL
-- Database: openemr

CREATE TABLE IF NOT EXISTS interface_wizard_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(50),
    message_content TEXT,
    received_at DATETIME,
    processed BOOLEAN DEFAULT FALSE,
    INDEX idx_message_id (message_id),
    INDEX idx_received_at (received_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**To create this table:**

1. Open phpMyAdmin (XAMPP)
2. Select `openemr` database
3. Click **SQL** tab
4. Paste the above SQL
5. Click **"Go"**

---

## ✅ Verify Channel is Working

### Checklist:
- [ ] Channel created successfully
- [ ] Listener port is **6661**
- [ ] Channel is deployed (not paused)
- [ ] Channel status is **Started** (green)
- [ ] Test message sent successfully
- [ ] ACK response generated
- [ ] Message appears in destination (database/file)

---

## 🔍 Troubleshooting

### Issue: "Port 6661 already in use"

**Solution:**
```
1. Check what's using the port:
   netstat -ano | findstr :6661

2. Either:
   a) Kill that process, OR
   b) Change port in both:
      - Mirth channel listener
      - backend/.env (MLLP_PORT)
```

### Issue: "Channel won't start"

**Check:**
1. Is MySQL running?
2. Are database credentials correct?
3. Check Mirth logs: `[Mirth Install]\logs\mirth.log`

### Issue: "No ACK response"

**Solution:**
```
In Source settings:
- Enable "Response"
- Select "Auto-generate (After source transformer)"
```

### Issue: Messages not reaching destination

**Check:**
1. Destination connector is configured
2. Database connection is valid
3. SQL statement is correct
4. Check channel logs for errors

---

## 🎬 What Happens When Interface Wizard Sends a Message

```
┌─────────────────────┐
│ Interface Wizard    │
│ (Port 8000)         │
└──────────┬──────────┘
           │
           │ 1. Generates HL7 message
           │    (ADT^A28 for new patient)
           ▼
┌─────────────────────┐
│ MLLP Client         │
│ (in Python backend) │
└──────────┬──────────┘
           │
           │ 2. Sends via TCP
           │    to localhost:6661
           ▼
┌─────────────────────┐
│ Mirth Channel       │
│ MLLP Listener:6661  │
└──────────┬──────────┘
           │
           │ 3. Receives message
           │    Parses HL7
           ▼
┌─────────────────────┐
│ Destination         │
│ (Database/File)     │
└──────────┬──────────┘
           │
           │ 4. Stores message
           │
           ▼
┌─────────────────────┐
│ ACK Response        │
│ AA = Success        │
└──────────┬──────────┘
           │
           │ 5. Sends ACK back
           │    to Interface Wizard
           ▼
┌─────────────────────┐
│ Interface Wizard    │
│ Shows: Success!     │
└─────────────────────┘
```

---

## 📝 Quick Configuration Summary

**For quick setup, use these exact values:**

| Setting | Value |
|---------|-------|
| Channel Name | Interface Wizard HL7 Listener |
| Source Type | MLLP Listener |
| Listen Address | 0.0.0.0 |
| Listen Port | **6661** |
| Response | Auto-generate ACK |
| Destination | File Writer (easiest) or Database Writer |
| File Directory | C:\mirth_messages\ |

---

## 🎯 Simplest Setup (Recommended for Testing)

**Use File Writer destination:**

1. Create folder: `C:\mirth_messages\`
2. In destination, choose **File Writer**
3. Directory: `C:\mirth_messages\`
4. Filename: `${DATE_TIME}_${message.messageId}.hl7`

**Benefits:**
- No database needed
- Easy to verify (just open the files)
- See exactly what messages are being sent
- Simple troubleshooting

**After sending a test command from Interface Wizard:**
- Check `C:\mirth_messages\`
- You'll see `.hl7` files
- Open with Notepad to see HL7 content

---

## 🚀 Ready to Test!

Once your channel is set up:

1. Start your Mirth channel
2. Run Interface Wizard backend: `run-backend.bat`
3. Run Interface Wizard frontend: `run-frontend.bat`
4. Send test command: **"Create a test patient"**
5. Check:
   - Mirth dashboard shows message received
   - File appears in `C:\mirth_messages\` (if using File Writer)
   - Interface Wizard shows success

---

**Questions? Issues?**

Check Mirth logs: `[Mirth Install Directory]\logs\mirth.log`
Check Interface Wizard logs: `backend\logs\interface-wizard.log`
