# Interface Wizard

A GenAI-powered healthcare interface tool for performing HL7/FHIR operations using natural language commands.

## 🚀 Features

- **Natural Language Processing** - Use plain English to create/query patient records
- **HL7 v2.x Integration** - Generate and send ADT, ORU, QRY messages via MLLP
- **FHIR R4 Support** - Query and create FHIR resources (Patient, Observation)
- **Mirth Connect Integration** - Process messages through Mirth channels
- **OpenEMR Integration** - Direct database integration with OpenEMR
- **Dual Frontend** - Choose between React or Angular modern UI
- **Professional UI** - ChatGPT-style interface with dark/light mode

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 20.10+** and npm
- **MySQL 8.0+** (via XAMPP or standalone)
- **OpenEMR** (installed and configured)
- **Mirth Connect 4.x** (installed and running)
- **OpenAI API Key**

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd interface-wizard
```

### 2. Backend Setup

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

# Configure environment variables
copy .env.example .env
# Edit .env with your actual credentials
```

**Required Environment Variables:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - MySQL connection string for OpenEMR
- `MLLP_HOST` and `MLLP_PORT` - Mirth Connect MLLP listener details

### 3. Frontend Setup (Choose React OR Angular)

#### Option A: React Frontend

```bash
cd frontend-react
npm install
```

#### Option B: Angular Frontend

```bash
cd frontend-angular
npm install
```

### 4. Mirth Connect Channel Setup

1. Open Mirth Administrator (http://localhost:8443)
2. Login with your credentials
3. Create a new channel:
   - **Source:** TCP Listener (MLLP mode)
   - **Port:** 6661
   - **Destination:** File Writer or Database Writer
4. Deploy and start the channel

See `docs/MIRTH_SETUP.md` for detailed instructions.

## 🚀 Running the Application

### Start Backend

```bash
cd backend
venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

### Start Frontend

#### React:
```bash
cd frontend-react
npm start
```
Access at: **http://localhost:3000**

#### Angular:
```bash
cd frontend-angular
npm start
```
Access at: **http://localhost:4200**

## 📖 Usage

1. **Open the frontend** (React on :3000 or Angular on :4200)
2. **Login** with your credentials (or register a new account)
3. **Type natural language commands:**
   - "Create a test patient named John Doe"
   - "Create 10 patients with random data"
   - "Retrieve patient with MRN 12345"

## 🏗️ Project Structure

```
interface-wizard/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── domain/         # Business entities
│   │   ├── application/    # Use cases
│   │   ├── infrastructure/ # External integrations
│   │   └── presentation/   # API endpoints
│   ├── requirements.txt
│   └── .env.example
├── frontend-react/         # React frontend
│   ├── src/
│   │   ├── pages/         # Login, Register, Chat
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API services
│   │   └── context/       # State management
│   └── package.json
├── frontend-angular/       # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── auth/      # Authentication module
│   │   │   ├── chat/      # Chat module
│   │   │   └── shared/    # Shared services
│   └── package.json
└── README.md
```

## 🔐 Security Notes

⚠️ **IMPORTANT:** This application is configured for **DEVELOPMENT/TESTING ONLY**

- **DO NOT** use with real patient data
- **DO NOT** expose to the internet
- **DO NOT** commit `.env` files to version control
- **DO NOT** use default credentials in production

For production deployment:
- Enable HTTPS/TLS
- Implement proper authentication (JWT with refresh tokens)
- Use environment-specific configuration
- Enable rate limiting
- Add comprehensive audit logging
- Use production database with encryption

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests (React)
```bash
cd frontend-react
npm test
```

### Frontend Tests (Angular)
```bash
cd frontend-angular
npm test
```

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (requires 3.9+)
- Verify virtual environment is activated
- Ensure all dependencies installed: `pip list`
- Check `.env` file exists with correct values

### Frontend won't start
- Check Node version: `node --version` (requires 20.10+)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### "Cannot connect to backend"
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in frontend environment config

### "Timeout waiting for ACK"
- Verify Mirth Connect is running
- Check Mirth channel is deployed and started
- Confirm MLLP listener is on port 6661
- Check Mirth channel logs for errors

## 📚 Documentation

- [Architecture](ARCHITECTURE.md) - System design and patterns
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when backend running)
- [User Guide](USER_GUIDE.md) - Detailed usage instructions
- [Mirth Setup](docs/MIRTH_SETUP.md) - Mirth Connect configuration

## 🤝 Contributing

This is a proprietary project. Please contact the project owner for contribution guidelines.

## 📄 License

Proprietary - All rights reserved

## 👤 Author

**Your Name**

## 🙏 Acknowledgments

- FastAPI for the excellent Python framework
- React and Angular teams for modern frontend frameworks
- OpenAI for GPT API
- Mirth Connect for healthcare integration
- OpenEMR for the EHR system

---

**Version:** 1.0.0  
**Last Updated:** November 2025
