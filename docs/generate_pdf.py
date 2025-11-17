"""
PDF Generator for Interface Wizard Documentation
Combines all markdown documentation into a single PDF
"""

import os
from pathlib import Path

# Check if required libraries are available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
    from reportlab.platypus import Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    print("[OK] reportlab is installed")
except ImportError:
    print("[ERROR] reportlab not installed")
    print("\nInstalling reportlab...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'reportlab'])
    print("[OK] reportlab installed successfully")
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

def create_pdf():
    """Generate comprehensive PDF documentation"""

    # File paths
    docs_dir = Path(__file__).parent
    output_file = docs_dir / "Interface_Wizard_Complete_Documentation.pdf"

    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )

    # Container for PDF elements
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#4a7ba7'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        spaceBefore=10,
        backColor=colors.HexColor('#f5f5f5')
    )

    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Interface Wizard", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Complete Technical Documentation", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Backend - Mirth Connect Integration Guide", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Version 1.0", styles['Normal']))
    story.append(Paragraph("November 2025", styles['Normal']))
    story.append(PageBreak())

    # Table of Contents
    story.append(Paragraph("Table of Contents", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    toc_items = [
        "1. System Overview",
        "2. Architecture Diagram",
        "3. Required Libraries and Dependencies",
        "4. Configuration Files (.env)",
        "5. Backend Code Structure",
        "6. HL7 Service Implementation",
        "7. MLLP Client Implementation",
        "8. Complete Code Flow",
        "9. Mirth Connect Channel Setup",
        "10. Testing and Troubleshooting",
        "11. Quick Reference Guide"
    ]

    for item in toc_items:
        story.append(Paragraph(item, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    story.append(PageBreak())

    # Section 1: System Overview
    story.append(Paragraph("1. System Overview", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    overview_text = """
    <b>Interface Wizard</b> is a healthcare integration system that enables natural language
    interaction with Electronic Health Record (EHR) systems. The system uses AI to interpret
    user commands and automatically generates HL7 messages for patient registration, updates,
    and queries.
    """
    story.append(Paragraph(overview_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Components table
    components_data = [
        ['Component', 'Technology', 'Purpose'],
        ['Frontend', 'Angular/React', 'User interface'],
        ['Backend', 'FastAPI (Python)', 'API server, HL7 generation'],
        ['Integration Engine', 'Mirth Connect', 'HL7 message routing'],
        ['Database', 'MySQL (OpenEMR)', 'Patient data storage'],
        ['AI Processing', 'OpenAI GPT-4', 'Natural language understanding']
    ]

    components_table = Table(components_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    components_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(components_table)
    story.append(PageBreak())

    # Section 2: Architecture
    story.append(Paragraph("2. System Architecture", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    arch_code = """
User Interface (Angular/React)
        ↓
    HTTP POST
        ↓
Backend API (FastAPI)
    ├─→ AI Service (OpenAI GPT-4)
    ├─→ HL7 Service (hl7apy)
    └─→ MLLP Client (socket)
        ↓
    TCP Port 6661
        ↓
Mirth Connect Channel
    ├─→ MLLP Listener
    ├─→ Source Transformer (JavaScript)
    └─→ Database Writer
        ↓
OpenEMR Database (MySQL)
    """

    story.append(Preformatted(arch_code, code_style))
    story.append(PageBreak())

    # Section 3: Required Libraries
    story.append(Paragraph("3. Required Libraries and Dependencies", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Python Dependencies (requirements.txt)", heading2_style))

    requirements_text = """
<b>Core Libraries:</b><br/>
• <b>hl7apy==1.3.4</b> - Creates and parses HL7 v2.x messages<br/>
• <b>fastapi==0.104.1</b> - Modern web framework for building APIs<br/>
• <b>uvicorn==0.24.0</b> - ASGI server to run FastAPI<br/>
• <b>openai==1.3.5</b> - OpenAI API client for GPT-4<br/>
• <b>pymysql==1.1.0</b> - MySQL database driver<br/>
• <b>pydantic==2.5.0</b> - Data validation and settings management<br/>
• <b>python-dotenv==1.0.0</b> - Load environment variables from .env file<br/>
<br/>
<b>Network Communication:</b><br/>
• <b>socket</b> (built-in) - TCP/IP communication with Mirth Connect
    """

    story.append(Paragraph(requirements_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Library purposes table
    lib_data = [
        ['Library', 'File Used In', 'Purpose'],
        ['hl7apy', 'hl7_service.py', 'Create HL7 ADT^A04 messages'],
        ['socket', 'mllp_client.py', 'Send messages via MLLP protocol'],
        ['fastapi', 'main.py, command.py', 'REST API endpoints'],
        ['openai', 'ai_service.py', 'Extract patient data from text'],
        ['pydantic', 'config.py, models/', 'Configuration and validation']
    ]

    lib_table = Table(lib_data, colWidths=[1.3*inch, 1.8*inch, 2.9*inch])
    lib_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(lib_table)
    story.append(PageBreak())

    # Section 4: Configuration Files
    story.append(Paragraph("4. Configuration Files", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("4.1 Environment Variables (.env)", heading2_style))

    env_intro = """
    The <b>backend/.env</b> file contains all configuration needed for the system to operate.
    This is the ONLY configuration file you need to modify.
    """
    story.append(Paragraph(env_intro, styles['BodyText']))
    story.append(Spacer(1, 0.1*inch))

    # Critical config table
    config_data = [
        ['Variable', 'Value', 'Description'],
        ['MLLP_HOST', 'localhost', 'Mirth Connect server location'],
        ['MLLP_PORT', '6661', 'Mirth MLLP listener port (CRITICAL!)'],
        ['OPENAI_API_KEY', 'sk-proj-...', 'OpenAI API key for GPT-4'],
        ['DB_HOST', 'localhost', 'MySQL database server'],
        ['DB_NAME', 'openemr', 'OpenEMR database name'],
        ['DB_USER', 'openemr', 'Database username'],
        ['DB_PASSWORD', 'openemr', 'Database password']
    ]

    config_table = Table(config_data, colWidths=[1.8*inch, 1.5*inch, 2.7*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(config_table)
    story.append(Spacer(1, 0.2*inch))

    critical_note = """
    <b>⚠ CRITICAL:</b> The MLLP_PORT value (6661) MUST match the port configured
    in your Mirth Connect channel's MLLP Listener. If these don't match, messages
    will fail to send.
    """
    story.append(Paragraph(critical_note, styles['BodyText']))
    story.append(PageBreak())

    # Section 5: Backend Code Structure
    story.append(Paragraph("5. Backend Code Structure", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    structure_code = """
backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Loads .env configuration
│   │
│   ├── api/v1/endpoints/
│   │   └── command.py             # POST /api/v1/command
│   │
│   ├── services/
│   │   ├── ai_service.py          # OpenAI integration
│   │   ├── hl7_service.py         # ⭐ Creates HL7 messages
│   │   ├── mllp_client.py         # ⭐ Sends to Mirth
│   │   └── database_service.py    # Database operations
│   │
│   ├── models/
│   │   ├── command.py             # Request/Response models
│   │   └── patient.py             # Patient data models
│   │
│   └── utils/
│       └── logger.py              # Logging configuration
│
├── .env                           # ⭐ Configuration file
├── requirements.txt               # Python dependencies
└── run.py                         # Application entry point
    """

    story.append(Preformatted(structure_code, code_style))
    story.append(Spacer(1, 0.2*inch))

    # Key files table
    key_files_data = [
        ['File', 'Lines', 'Purpose', 'Key Libraries'],
        ['hl7_service.py', '150', 'Create HL7 messages', 'hl7apy'],
        ['mllp_client.py', '180', 'Send to Mirth via MLLP', 'socket'],
        ['ai_service.py', '120', 'Process user commands', 'openai'],
        ['config.py', '80', 'Load configuration', 'pydantic'],
        ['command.py', '50', 'API endpoint', 'fastapi'],
        ['.env', '56', 'All configuration', '-']
    ]

    key_files_table = Table(key_files_data, colWidths=[1.5*inch, 0.7*inch, 2.3*inch, 1.5*inch])
    key_files_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(key_files_table)
    story.append(PageBreak())

    # Section 6: HL7 Service
    story.append(Paragraph("6. HL7 Service Implementation", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    hl7_intro = """
    The <b>hl7_service.py</b> file is responsible for creating HL7 v2.x messages
    that Mirth Connect can understand and process. It uses the <b>hl7apy</b> library
    to construct properly formatted HL7 messages.
    """
    story.append(Paragraph(hl7_intro, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Key Code Snippet:", heading2_style))

    hl7_code = """
from hl7apy.core import Message, Segment
from datetime import datetime

class HL7Service:
    def create_adt_a04_message(self, patient_data):
        # Create HL7 ADT^A04 (Register Patient) message
        msg = Message("ADT_A04", version="2.5")

        # Message Header
        msg.msh.msh_3 = "InterfaceWizard"
        msg.msh.msh_9 = "ADT^A04"
        msg.msh.msh_10 = f"MSG{datetime.now()}"

        # Patient Identification
        msg.pid.pid_3 = f"{patient_data['mrn']}^^^MRN"
        msg.pid.pid_5 = f"{patient_data['last_name']}^"
                        f"{patient_data['first_name']}"
        msg.pid.pid_7 = patient_data['dob']
        msg.pid.pid_8 = patient_data['gender']

        # Convert to ER7 format (pipe-delimited)
        return msg.to_er7()
    """

    story.append(Preformatted(hl7_code, code_style))
    story.append(Spacer(1, 0.2*inch))

    hl7_output = """
    <b>Output Example:</b><br/>
    <font face="Courier" size="8">
    MSH|^~\\&|InterfaceWizard|Facility|||20251117101530||ADT^A04|MSG001|P|2.5<br/>
    PID|1||12345^^^MRN||Doe^John||19800101|M
    </font>
    """
    story.append(Paragraph(hl7_output, styles['BodyText']))
    story.append(PageBreak())

    # Section 7: MLLP Client
    story.append(Paragraph("7. MLLP Client Implementation", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    mllp_intro = """
    The <b>mllp_client.py</b> file handles TCP/IP communication with Mirth Connect
    using the MLLP (Minimal Lower Layer Protocol) standard. MLLP wraps HL7 messages
    with special control characters for transmission.
    """
    story.append(Paragraph(mllp_intro, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("MLLP Protocol Format:", heading2_style))

    mllp_format = """
    <font face="Courier" size="9">
    &lt;VT&gt; + HL7_MESSAGE + &lt;FS&gt; + &lt;CR&gt;

    Where:
    • &lt;VT&gt; = Vertical Tab (0x0B) - Start of message
    • HL7_MESSAGE = The actual HL7 content
    • &lt;FS&gt; = File Separator (0x1C) - End of message
    • &lt;CR&gt; = Carriage Return (0x0D) - Message terminator
    </font>
    """
    story.append(Paragraph(mllp_format, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Key Code Snippet:", heading2_style))

    mllp_code = """
import socket
from app.config import settings

class MLLPClient:
    VT = b'\\x0b'  # Start Block
    FS = b'\\x1c'  # End Block
    CR = b'\\x0d'  # Carriage Return

    def send_message(self, hl7_message):
        # Wrap with MLLP envelope
        mllp_msg = self.VT + hl7_message.encode() +
                   self.FS + self.CR

        # Connect to Mirth
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        sock.connect((settings.MLLP_HOST,
                      settings.MLLP_PORT))

        # Send message
        sock.sendall(mllp_msg)

        # Receive ACK
        response = sock.recv(4096)
        sock.close()

        return {"success": True, "ack": response}
    """

    story.append(Preformatted(mllp_code, code_style))
    story.append(PageBreak())

    # Section 8: Complete Flow
    story.append(Paragraph("8. Complete Message Flow", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    flow_steps = [
        ['Step', 'Component', 'Action'],
        ['1', 'User', 'Types: "Create patient John Doe"'],
        ['2', 'Frontend', 'POST /api/v1/command'],
        ['3', 'API Endpoint', 'Receives request, calls AI Service'],
        ['4', 'AI Service', 'Extracts patient data using OpenAI'],
        ['5', 'HL7 Service', 'Creates HL7 ADT^A04 message'],
        ['6', 'MLLP Client', 'Wraps with MLLP, sends via TCP'],
        ['7', 'Mirth Connect', 'Receives on port 6661'],
        ['8', 'Source Transformer', 'Extracts data, inserts to DB'],
        ['9', 'Database', 'Patient record created'],
        ['10', 'ACK Response', 'Success message returned to user']
    ]

    flow_table = Table(flow_steps, colWidths=[0.6*inch, 1.5*inch, 3.9*inch])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(flow_table)
    story.append(PageBreak())

    # Section 9: Mirth Setup
    story.append(Paragraph("9. Mirth Connect Channel Setup", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    mirth_intro = """
    Mirth Connect must be configured with a channel that listens for incoming
    HL7 messages on port 6661 and processes them into the OpenEMR database.
    """
    story.append(Paragraph(mirth_intro, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Mirth configuration table
    mirth_config_data = [
        ['Component', 'Setting', 'Value'],
        ['Channel Name', 'Name', 'Interface Wizard HL7 Listener'],
        ['Source Connector', 'Type', 'MLLP Listener'],
        ['Source Connector', 'Host', '0.0.0.0'],
        ['Source Connector', 'Port', '6661 (CRITICAL!)'],
        ['Source Transformer', 'Language', 'JavaScript'],
        ['Source Transformer', 'Action', 'Extract data, insert to DB'],
        ['Destination', 'Type', 'File Writer (for archival)'],
        ['Destination', 'Directory', 'C:/mirth/hl7_messages/']
    ]

    mirth_config_table = Table(mirth_config_data, colWidths=[1.8*inch, 1.5*inch, 2.7*inch])
    mirth_config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(mirth_config_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("Why Use Source Transformer for Database?", heading2_style))

    transformer_reasons = """
    We use the <b>Source Transformer</b> (instead of Database Destination) because:<br/>
    <br/>
    ✓ <b>Faster</b> - Database insert happens immediately<br/>
    ✓ <b>Guaranteed</b> - Executes even if destinations fail<br/>
    ✓ <b>Flexible</b> - Full control with JavaScript<br/>
    ✓ <b>Validation</b> - Can check for duplicates before inserting<br/>
    ✓ <b>Custom Logic</b> - Calculate next PID, handle special cases
    """
    story.append(Paragraph(transformer_reasons, styles['BodyText']))
    story.append(PageBreak())

    # Section 10: Testing
    story.append(Paragraph("10. Testing and Troubleshooting", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("10.1 Testing Checklist", heading2_style))

    testing_data = [
        ['Test', 'Command/Check', 'Expected Result'],
        ['Backend Running', 'Check http://localhost:8000/health', 'Status: OK'],
        ['Mirth Running', 'Check http://localhost:8443', 'Login page appears'],
        ['Channel Deployed', 'Mirth Dashboard', 'Green status indicator'],
        ['Port Available', 'netstat -ano | findstr :6661', 'Shows listening port'],
        ['Test Message', 'Send via frontend', 'Success response'],
        ['Database Check', 'SELECT * FROM patient_data', 'New patient record']
    ]

    testing_table = Table(testing_data, colWidths=[1.5*inch, 2.2*inch, 2.3*inch])
    testing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(testing_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("10.2 Common Issues", heading2_style))

    issues_data = [
        ['Problem', 'Solution'],
        ['Connection Refused (6661)', 'Start and deploy Mirth channel'],
        ['CORS Error', 'Add frontend port to backend/.env CORS_ORIGINS'],
        ['Duplicate PID Error', 'Use SELECT MAX(pid)+1 in transformer'],
        ['OpenAI API Error', 'Check OPENAI_API_KEY in .env'],
        ['Database Connection Failed', 'Verify MySQL is running, check credentials']
    ]

    issues_table = Table(issues_data, colWidths=[2.5*inch, 3.5*inch])
    issues_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c45650')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe0e0')])
    ]))

    story.append(issues_table)
    story.append(PageBreak())

    # Section 11: Quick Reference
    story.append(Paragraph("11. Quick Reference Guide", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("11.1 Start Commands", heading2_style))

    start_commands = """
    <font face="Courier" size="9">
    <b># Start Backend</b>
    cd backend
    .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

    <b># Start Angular Frontend</b>
    cd frontend-angular
    npm start

    <b># Start React Frontend</b>
    cd frontend-react
    npm start
    </font>
    """
    story.append(Paragraph(start_commands, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("11.2 Key Ports", heading2_style))

    ports_data = [
        ['Service', 'Port', 'URL'],
        ['Backend API', '8000', 'http://localhost:8000'],
        ['Angular Frontend', '4200', 'http://localhost:4200'],
        ['React Frontend', '3000', 'http://localhost:3000'],
        ['Mirth Connect', '8443', 'https://localhost:8443'],
        ['Mirth MLLP Listener', '6661', 'TCP localhost:6661'],
        ['MySQL Database', '3306', 'localhost:3306'],
        ['OpenEMR', '80', 'http://localhost/openemr']
    ]

    ports_table = Table(ports_data, colWidths=[2*inch, 1*inch, 3*inch])
    ports_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(ports_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("11.3 Default Credentials", heading2_style))

    creds_data = [
        ['System', 'Username', 'Password'],
        ['Mirth Connect', 'admin', 'admin'],
        ['OpenEMR', 'administrator', 'Admin@123456'],
        ['MySQL', 'openemr', 'openemr']
    ]

    creds_table = Table(creds_data, colWidths=[2*inch, 2*inch, 2*inch])
    creds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a7ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))

    story.append(creds_table)
    story.append(PageBreak())

    # Final page - Summary
    story.append(Paragraph("Summary", heading1_style))
    story.append(Spacer(1, 0.2*inch))

    summary_text = """
    <b>Interface Wizard</b> successfully integrates natural language processing with
    healthcare systems using industry-standard HL7 messaging protocol.<br/>
    <br/>
    <b>Key Components:</b><br/>
    • <b>hl7apy</b> library creates properly formatted HL7 messages<br/>
    • <b>socket</b> module sends messages via MLLP protocol<br/>
    • <b>Mirth Connect</b> receives and processes messages<br/>
    • <b>OpenEMR database</b> stores patient records<br/>
    <br/>
    <b>Critical Configuration:</b><br/>
    • MLLP_PORT in .env MUST match Mirth channel listener port<br/>
    • All configuration in single .env file<br/>
    • Source Transformer handles database operations<br/>
    <br/>
    <b>Benefits:</b><br/>
    • Standards-based healthcare integration<br/>
    • Scalable and maintainable architecture<br/>
    • Comprehensive error handling and logging<br/>
    • Easy to test and troubleshoot<br/>
    <br/>
    <br/>
    <b>Document Version:</b> 1.0<br/>
    <b>Last Updated:</b> November 2025<br/>
    <b>Author:</b> Interface Wizard Development Team
    """

    story.append(Paragraph(summary_text, styles['BodyText']))

    # Build PDF
    doc.build(story)

    print(f"\n[SUCCESS] PDF generated successfully!")
    print(f"[LOCATION] {output_file}")
    print(f"[SIZE] {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file)

if __name__ == "__main__":
    print("=" * 60)
    print("Interface Wizard PDF Documentation Generator")
    print("=" * 60)
    print()

    try:
        pdf_path = create_pdf()
        print()
        print("=" * 60)
        print("[SUCCESS] You can now open the PDF file.")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
