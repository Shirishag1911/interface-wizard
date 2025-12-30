# Quick Start Guide - Interface Wizard

## 🚀 Installation (5 minutes)

### 1. Install Dependencies

```bash
cd actual-code
pip install -r requirements.txt
```

**What gets installed:**
- `openai==1.10.0` - Works with BOTH Ollama Cloud (FREE) and OpenAI (Paid)
- `fastapi`, `uvicorn` - REST API framework
- `pandas`, `openpyxl` - Excel/CSV processing
- `hl7` - HL7 message validation

**No separate Ollama library needed!** The `openai` library supports Ollama Cloud via the `base_url` parameter.

---

### 2. Start the Server

```bash
cd actual-code
python main_with_fastapi.py --api
```

Server will start on **http://localhost:8000**

---

### 3. Test with Patient_Records.xlsx

```bash
python test_end_to_end.py
```

This automated test will:
1. Upload Patient_Records.xlsx
2. Use Ollama Cloud for column mapping (FREE)
3. Generate HL7 messages programmatically (10x faster)
4. Send to Mirth Connect
5. Display results

---

## 📊 Verify Results

### Check Mirth Connect
- Open Mirth Administrator UI
- Check channel message count
- View received HL7 messages

### Check OpenEMR Database
```sql
SELECT pid, fname, lname, pubpid, DOB, sex, regdate
FROM openemr.patient_data
ORDER BY pid DESC LIMIT 10;
```

### Check Logs
```bash
tail -f interface_wizard.log
```

---

## 📖 Full Documentation

- **[OLLAMA_SETUP_GUIDE.md](OLLAMA_SETUP_GUIDE.md)** - Complete Ollama Cloud setup
- **[IW-Backend-API-Documentation-v3.0.md](actual-code/IW-Backend-API-Documentation-v3.0.md)** - Full API reference
