# Interface Wizard 🏥

A healthcare integration platform featuring natural language processing, HL7/FHIR support, and comprehensive EHR integration capabilities. Built with modern web technologies and designed for seamless healthcare data exchange.

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Angular 17](https://img.shields.io/badge/Angular-17-red.svg)](https://angular.io/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)

---

## 🎯 What is Interface Wizard?

Interface Wizard is an AI-powered healthcare integration tool that allows healthcare professionals to:
- **Use natural language** to create and query patient records
- **Generate HL7 v2.x messages** (ADT, ORU, QRY) via MLLP protocol
- **Integrate with OpenEMR** through Mirth Connect
- **Process FHIR R4 resources** for modern interoperability
- **Choose your frontend** - React or Angular with ChatGPT-style UI

---

## ✨ Key Features

### 🤖 AI-Powered Natural Language Interface
- Type commands like "Create a test patient named John Doe"
- AI extracts patient data and generates proper HL7 messages
- Powered by OpenAI GPT-4

### 🏥 Healthcare Standards Support
- **HL7 v2.x** - ADT (Admission/Discharge/Transfer), ORU (Observation Results), QRY (Query)
- **FHIR R4** - Patient, Observation, and other resources
- **MLLP Protocol** - Industry-standard HL7 transmission

### 🔌 Integration Ready
- **Mirth Connect** - Healthcare integration engine
- **OpenEMR** - Open-source EHR system
- **Direct database access** - MySQL integration
- **RESTful API** - Easy to integrate with other systems

### 🎨 Modern User Interface
- Dual frontend options (React 18 or Angular 17)
- ChatGPT-style conversational interface
- Dark/Light theme support
- Material Design components
- Responsive and mobile-friendly

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.9+ | Backend runtime |
| **Node.js** | 20.10+ | Frontend build tools |
| **MySQL** | 8.0+ | Database (via XAMPP or standalone) |
| **OpenEMR** | Latest | EHR system |
| **Mirth Connect** | 4.x | HL7 integration engine |
| **OpenAI API Key** | - | AI processing |

### Quick Install Guide

**Windows (XAMPP):**
```bash
# Install XAMPP (includes MySQL, Apache, PHP)
# Download from: https://www.apachefriends.org/

# Install Mirth Connect
# Download from: https://www.nextgen.com/products-and-services/mirth-connect-downloads

# Install OpenEMR
# Use XAMPP and follow: https://www.open-emr.org/wiki/index.php/OpenEMR_Installation_Guides
```

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/Shirishag1911/interface-wizard.git
cd interface-wizard
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
```

**Edit `.env` file with your credentials:**

```env
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=openemr
DB_USER=openemr
DB_PASSWORD=openemr

# Mirth MLLP Configuration (MUST match Mirth channel port!)
MLLP_HOST=localhost
MLLP_PORT=6661

# Application Settings
DEBUG=true
CORS_ORIGINS=["http://localhost:3000", "http://localhost:4200"]
```

### Step 3: Frontend Setup (Choose One)

#### Option A: React Frontend (Recommended for beginners)

```bash
cd frontend-react
npm install
```

#### Option B: Angular Frontend (Recommended for enterprise)

```bash
cd frontend-angular
npm install
```

### Step 4: Mirth Connect Setup

**Important:** Mirth Connect is required for HL7 message processing!

1. **Start Mirth Connect Administrator:**
   - Open browser: `https://localhost:8443` (or `http://localhost:8080`)
   - Login: `admin` / `admin` (default)

2. **Create Channel:**
   - Click **Channels** → **New Channel**
   - **Name:** `Interface Wizard HL7 Listener`
   - **Data Type:** `HL7 v2.x`

3. **Configure Source:**
   - **Connector Type:** MLLP Listener
   - **Host:** `0.0.0.0`
   - **Port:** `6661` ⚠️ MUST MATCH backend `.env` MLLP_PORT!

4. **Configure Source Transformer:**
   - Use the JavaScript code from `docs/MIRTH_CONNECT_SETUP_GUIDE.md`
   - This extracts patient data and inserts into OpenEMR database

5. **Configure Destination:**
   - **Connector Type:** File Writer
   - **Directory:** `C:/mirth/hl7_messages/`
   - **File Name:** `MSG_${DATE('yyyyMMdd')}_${UUID()}.hl7`

6. **Deploy and Start Channel**

📖 **Detailed Instructions:** See [docs/MIRTH_CONNECT_SETUP_GUIDE.md](docs/MIRTH_CONNECT_SETUP_GUIDE.md)

---

## 🎮 Running the Application

### Option 1: Using Batch Scripts (Windows - Easiest!)

**Start Backend:**
```bash
run-backend.bat
```

**Start Angular Frontend:**
```bash
run-frontend-angular.bat
```

**Start React Frontend:**
```bash
run-frontend-react.bat
```

### Option 2: Manual Commands

**Backend:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**React Frontend:**
```bash
cd frontend-react
npm start
```

**Angular Frontend:**
```bash
cd frontend-angular
npm start
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **React Frontend** | http://localhost:3000 | React chat interface |
| **Angular Frontend** | http://localhost:4200 | Angular chat interface |
| **Mirth Connect** | https://localhost:8443 | Integration engine admin |
| **OpenEMR** | http://localhost/openemr | EHR system |

---

## 💬 Usage Examples

### Creating Patients

**Natural Language Commands:**

```
"Create a test patient named John Doe"

"Create a patient named Jane Smith with diabetes diagnosis"

"Create 10 patients with random data"

"Create a patient with brain cancer named Nagaraj Mantha"
```

### What Happens Behind the Scenes:

1. **AI Processing** - OpenAI GPT-4 extracts patient data
2. **HL7 Generation** - Backend creates HL7 ADT^A04 message
3. **MLLP Transmission** - Message sent to Mirth Connect on port 6661
4. **Mirth Processing** - JavaScript transformer extracts data
5. **Database Insert** - Patient record created in OpenEMR
6. **Response** - Success message displayed in UI

---

## 📁 Project Structure

```
interface-wizard/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── domain/                   # Business entities
│   │   │   ├── entities.py           # Patient, Message models
│   │   │   └── interfaces.py         # Repository interfaces
│   │   ├── application/              # Use cases
│   │   │   └── use_cases.py          # Business logic
│   │   ├── infrastructure/           # External integrations
│   │   │   ├── hl7_service.py        # ⭐ HL7 message creation (hl7apy)
│   │   │   ├── nlp_service.py        # OpenAI GPT-4 integration
│   │   │   ├── fhir_service.py       # FHIR resource handling
│   │   │   └── repositories.py       # Database access
│   │   ├── presentation/             # API layer
│   │   │   ├── routes.py             # FastAPI endpoints
│   │   │   └── schemas.py            # Request/Response models
│   │   ├── config.py                 # Configuration management
│   │   └── main.py                   # Application entry point
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment template
│
├── frontend-react/                   # React 18 Frontend
│   ├── src/
│   │   ├── pages/                    # Main pages
│   │   │   ├── Chat.tsx              # ChatGPT-style interface
│   │   │   ├── Login.tsx             # Authentication (removed)
│   │   │   └── Register.tsx          # Registration (removed)
│   │   ├── components/               # Reusable components
│   │   │   ├── MessageBubble.tsx     # Chat message display
│   │   │   ├── ChatInput.tsx         # Input with suggestions
│   │   │   └── Sidebar.tsx           # Navigation sidebar
│   │   ├── services/
│   │   │   └── api.ts                # Backend API client
│   │   ├── context/                  # State management
│   │   │   └── ThemeContext.tsx      # Dark/Light mode
│   │   └── App.tsx                   # Main app component
│   └── package.json
│
├── frontend-angular/                 # Angular 17 Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── chat/                 # Chat module
│   │   │   │   ├── chat.component.ts # Main chat interface
│   │   │   │   ├── chat.service.ts   # API service
│   │   │   │   └── message.component.ts # Message display
│   │   │   ├── shared/               # Shared services
│   │   │   │   ├── api.service.ts    # HTTP client
│   │   │   │   └── theme.service.ts  # Theme management
│   │   │   ├── app.routes.ts         # Routing (simplified)
│   │   │   └── app.config.ts         # App configuration
│   │   ├── environments/             # Environment configs
│   │   └── styles.scss               # Global styles
│   └── package.json
│
├── docs/                             # 📚 Documentation
│   ├── BACKEND_MIRTH_INTEGRATION.md  # Complete backend guide
│   ├── CODE_FLOW_DIAGRAM.md          # Visual code flow
│   ├── MIRTH_CONNECT_SETUP_GUIDE.md  # Mirth setup instructions
│   ├── QUICK_REFERENCE.md            # Cheat sheet
│   ├── Interface_Wizard_Complete_Documentation.pdf  # PDF guide
│   └── generate_pdf.py               # PDF generator script
│
├── run-backend.bat                   # Windows: Start backend
├── run-frontend-angular.bat          # Windows: Start Angular
├── run-frontend-react.bat            # Windows: Start React
├── setup-backend.bat                 # Windows: Setup backend
├── setup-frontend.bat                # Windows: Setup frontend
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

---

## 🔧 Configuration Details

### Backend Environment Variables

All configuration in `backend/.env`:

```env
# Application Settings
APP_NAME=Interface Wizard
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database (OpenEMR MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=openemr
DB_USER=openemr
DB_PASSWORD=openemr

# OpenEMR Settings
OPENEMR_USERNAME=administrator
OPENEMR_PASSWORD=Admin@123456
OPENEMR_BASE_URL=http://localhost/openemr

# Mirth Connect Admin API (optional)
MIRTH_HOST=localhost
MIRTH_PORT=8443
MIRTH_USERNAME=admin
MIRTH_PASSWORD=Admin@123

# HL7 MLLP - CRITICAL!
MLLP_HOST=localhost
MLLP_PORT=6661                        # ⚠️ MUST match Mirth channel port!
MLLP_TIMEOUT=30

# OpenAI - REQUIRED!
OPENAI_API_KEY=your-api-key-here      # Get from https://platform.openai.com/api-keys
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# FHIR (optional)
FHIR_BASE_URL=http://localhost/openemr/apis/default/fhir
FHIR_VERSION=R4

# Security
SECRET_KEY=interface-wizard-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/interface-wizard.log

# CORS - Add frontend ports
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://localhost:4200", "http://localhost:4201"]
```

### Frontend Environment Variables

**React** (`frontend-react/.env`):
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

**Angular** (`frontend-angular/src/environments/environment.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1'
};
```

---

## 🧪 Testing

### Test the Full Workflow

1. **Start all services:**
   - MySQL (XAMPP)
   - Mirth Connect (with channel deployed)
   - Backend (port 8000)
   - Frontend (port 3000 or 4200)

2. **Open frontend in browser**

3. **Type test command:**
   ```
   Create a test patient named John Doe
   ```

4. **Expected results:**
   - ✅ Success message in UI
   - ✅ HL7 message sent to Mirth (check Mirth dashboard)
   - ✅ Patient record in OpenEMR database
   - ✅ Message file saved in `C:/mirth/hl7_messages/`

### Verify Database

```sql
-- Run in phpMyAdmin or MySQL client
SELECT * FROM openemr.patient_data ORDER BY pid DESC LIMIT 10;
```

### Check Mirth Logs

1. Open Mirth Connect Administrator
2. Click on channel → **Messages** tab
3. Look for SUCCESS messages

---

## 🐛 Troubleshooting

### "Connection refused to localhost:6661"

**Problem:** Backend can't connect to Mirth Connect

**Solution:**
1. Check if Mirth Connect is running
2. Verify channel is deployed (green status)
3. Confirm port 6661 in both:
   - Mirth channel listener settings
   - Backend `.env` MLLP_PORT

```bash
# Check if port is listening
netstat -ano | findstr :6661
```

### "CORS Error" in Frontend

**Problem:** Frontend can't access backend API

**Solution:**
1. Check backend is running on port 8000
2. Verify `CORS_ORIGINS` in backend `.env` includes frontend port:
   ```env
   CORS_ORIGINS=["http://localhost:3000", "http://localhost:4200"]
   ```
3. Restart backend after changing `.env`

### "OpenAI API Error"

**Problem:** AI processing fails

**Solution:**
1. Verify `OPENAI_API_KEY` in backend `.env`
2. Check API key is valid at https://platform.openai.com/api-keys
3. Ensure you have API credits/quota

### "Duplicate entry '0' for key 'pid'"

**Problem:** Mirth can't insert patient into database

**Solution:**
- OpenEMR's `pid` field is NOT auto-increment
- Use the Source Transformer code from `docs/MIRTH_CONNECT_SETUP_GUIDE.md`
- It calculates next PID using `SELECT MAX(pid) + 1`

### Backend Won't Start

**Common issues:**

```bash
# Check Python version (needs 3.9+)
python --version

# Check virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt --no-cache-dir

# Check for port conflicts
netstat -ano | findstr :8000
```

### Frontend Won't Start

```bash
# Check Node version (needs 20.10+)
node --version
npm --version

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentation

| Document | Description | Location |
|----------|-------------|----------|
| **Backend-Mirth Integration** | Complete guide to backend code, libraries, and Mirth integration | [docs/BACKEND_MIRTH_INTEGRATION.md](docs/BACKEND_MIRTH_INTEGRATION.md) |
| **Code Flow Diagram** | Visual representation of complete message flow | [docs/CODE_FLOW_DIAGRAM.md](docs/CODE_FLOW_DIAGRAM.md) |
| **Mirth Connect Setup** | Step-by-step Mirth channel configuration | [docs/MIRTH_CONNECT_SETUP_GUIDE.md](docs/MIRTH_CONNECT_SETUP_GUIDE.md) |
| **Quick Reference** | Cheat sheet with commands, ports, credentials | [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) |
| **PDF Documentation** | Complete documentation in PDF format | [docs/Interface_Wizard_Complete_Documentation.pdf](docs/Interface_Wizard_Complete_Documentation.pdf) |
| **API Documentation** | Interactive Swagger UI | http://localhost:8000/docs (when running) |

---

## 🔒 Security Considerations

### ⚠️ IMPORTANT: Development Use Only

This application is configured for **DEVELOPMENT and TESTING ONLY**. Do NOT use in production without proper security hardening.

### What's Protected

✅ **Git Repository:**
- `.env` files (API keys, passwords)
- `venv/` and `node_modules/`
- Log files
- HL7 message archives
- Database dumps
- Private keys and certificates

### Production Checklist

Before deploying to production:

- [ ] Enable HTTPS/TLS for all connections
- [ ] Implement proper authentication (JWT with refresh tokens)
- [ ] Enable rate limiting on API endpoints
- [ ] Add comprehensive audit logging
- [ ] Use production database with encryption at rest
- [ ] Rotate all API keys and credentials
- [ ] Enable HIPAA-compliant logging (if applicable)
- [ ] Implement role-based access control (RBAC)
- [ ] Add input validation and sanitization
- [ ] Enable SQL injection protection
- [ ] Add XSS protection headers
- [ ] Implement CSRF tokens
- [ ] Use environment-specific configuration
- [ ] Add monitoring and alerting
- [ ] Perform security audit and penetration testing

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI 0.104+ (Python async web framework)
- **HL7 Library:** hl7apy 1.3.4 (creates HL7 v2.x messages)
- **Network:** Built-in socket module (MLLP protocol)
- **AI:** OpenAI API (GPT-4 for NLP)
- **Database:** PyMySQL + SQLAlchemy
- **Validation:** Pydantic

**Frontend (React):**
- React 18 with hooks
- Material-UI components
- Axios for HTTP
- Context API for state management

**Frontend (Angular):**
- Angular 17 (standalone components)
- Angular Material
- RxJS for reactive programming
- HttpClient for API calls

**Integration:**
- Mirth Connect 4.x (HL7 routing)
- OpenEMR (EHR system)
- MySQL 8.0+ (database)

### Message Flow

```
User Input → AI Processing → HL7 Generation → MLLP Send → Mirth → Database → Response
```

See [docs/CODE_FLOW_DIAGRAM.md](docs/CODE_FLOW_DIAGRAM.md) for detailed flow.

---

## 🤝 Contributing

This is a project. For contribution guidelines, please contact the repository owner.

---

## 📄 License

Proprietary - All rights reserved

---

## 👤 Author

**Shirisha G**
- GitHub: [@Shirishag1911](https://github.com/Shirishag1911)
- Email: shirisha.g1911@gmail.com

---

## 🙏 Acknowledgments

- **FastAPI** - For the excellent Python web framework
- **React & Angular** - For modern frontend frameworks
- **OpenAI** - For GPT-4 API
- **Mirth Connect** - For healthcare integration capabilities
- **OpenEMR** - For the open-source EHR system
- **hl7apy** - For HL7 message generation
- **Claude Code** - For development assistance

---

## 📊 Project Stats

- **Lines of Code:** 50,000+
- **Files:** 118
- **Languages:** Python, TypeScript, JavaScript
- **Documentation:** 6 comprehensive guides + PDF
- **Setup Time:** ~30 minutes (with prerequisites installed)

---

## 🔗 Quick Links

- **Repository:** https://github.com/Shirishag1911/interface-wizard
- **Issues:** https://github.com/Shirishag1911/interface-wizard/issues
- **OpenEMR Docs:** https://www.open-emr.org/wiki/
- **Mirth Connect Docs:** https://www.nextgen.com/mirth-connect
- **HL7 Standard:** http://www.hl7.org/
- **FHIR Docs:** https://www.hl7.org/fhir/

---

**Version:** 1.0.0
**Last Updated:** November 17, 2025
**Status:** Active Development

---

*Generated with [Claude Code](https://claude.com/claude-code)*
