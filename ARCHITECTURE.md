# Interface Wizard - Architecture Documentation

## Overview

Interface Wizard follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns, ensuring high maintainability, testability, and scalability.

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│              Presentation Layer (FastAPI)            │
│  - REST API Endpoints                                │
│  - Request/Response Models (Pydantic)                │
│  - Dependency Injection                              │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│            Application Layer (Use Cases)             │
│  - ProcessCommandUseCase                             │
│  - Business Logic Orchestration                      │
│  - Transaction Management                            │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│              Domain Layer (Core Business)            │
│  - Entities (Patient, HL7Message, etc.)              │
│  - Interfaces (Ports)                                │
│  - Business Rules                                    │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│        Infrastructure Layer (Adapters)               │
│  - NLP Service (OpenAI)                              │
│  - HL7 Service (MLLP)                                │
│  - FHIR Service (HTTP)                               │
│  - Data Generator (Faker)                            │
│  - Repositories (In-Memory)                          │
└─────────────────────────────────────────────────────┘
```

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── domain/              # Core business logic
│   │   ├── entities.py      # Business entities
│   │   └── interfaces.py    # Abstract interfaces (ports)
│   │
│   ├── application/         # Use cases
│   │   └── use_cases.py     # Business workflows
│   │
│   ├── infrastructure/      # External services
│   │   ├── nlp_service.py   # OpenAI integration
│   │   ├── hl7_service.py   # HL7 messaging
│   │   ├── fhir_service.py  # FHIR API client
│   │   ├── data_generator.py # Test data generation
│   │   └── repositories.py  # Data persistence
│   │
│   ├── presentation/        # API layer
│   │   ├── routes.py        # API endpoints
│   │   ├── schemas.py       # Request/response models
│   │   └── dependencies.py  # DI container
│   │
│   ├── config.py            # Configuration management
│   └── main.py              # Application entry point
│
├── tests/                   # Test suite
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

### Key Design Patterns

#### 1. Dependency Inversion Principle (DIP)
- All dependencies point inward toward the domain
- Domain defines interfaces (ports)
- Infrastructure implements interfaces (adapters)

```python
# Domain defines the contract
class INLPService(ABC):
    @abstractmethod
    async def interpret_command(self, text: str) -> UserCommand:
        pass

# Infrastructure implements it
class OpenAINLPService(INLPService):
    async def interpret_command(self, text: str) -> UserCommand:
        # Implementation using OpenAI
        ...
```

#### 2. Repository Pattern
- Abstracts data persistence
- Easy to swap in-memory for database

```python
class IOperationRepository(ABC):
    async def save_operation(self, operation: OperationResult) -> None:
        pass
```

#### 3. Use Case Pattern
- Each use case represents one business workflow
- Orchestrates domain entities and services

```python
class ProcessCommandUseCase:
    def __init__(self, nlp_service, hl7_service, ...):
        self.nlp_service = nlp_service
        # Dependencies injected
```

#### 4. Service Layer
- External service integrations are abstracted
- Easy to mock for testing

### Data Flow

```
User Input → API → Use Case → Domain → Services → External Systems
                                ↓
                           Repositories
                                ↓
                           Persistence
```

1. **User submits command** via REST API
2. **Use Case** receives request
3. **NLP Service** interprets natural language
4. **Use Case** determines action
5. **HL7/FHIR Service** executes operation
6. **Repository** persists result
7. **Response** returned to user

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   │
│   ├── pages/               # Page components
│   │   └── App.tsx
│   │
│   ├── services/            # API services
│   │   └── api.ts
│   │
│   ├── store/               # State management
│   │   └── chatStore.ts
│   │
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   │
│   ├── styles/              # CSS/styling
│   │
│   └── index.tsx            # Entry point
│
├── public/                  # Static files
├── package.json
└── tsconfig.json
```

### State Management

Using **Zustand** for simple, efficient state management:

```typescript
interface ChatState {
  messages: Message[];
  sessionId: string;
  isProcessing: boolean;
  addUserMessage: (content: string) => void;
  addSystemMessage: (content: string, operation?: any) => void;
}
```

### Component Hierarchy

```
App
├── AppBar (Header)
│   ├── Status Indicator
│   └── Controls
├── ChatContainer
│   └── ChatMessage[] (List)
└── ChatInput
```

## Communication Flow

### Request Flow

```
┌──────────┐      HTTP      ┌──────────┐    Use Case    ┌──────────┐
│ Frontend │ ────────────→   │ FastAPI  │ ──────────→    │ Business │
│  (React) │                 │   API    │                │  Logic   │
└──────────┘                 └──────────┘                └──────────┘
                                                               │
                                                               ▼
                                                         ┌──────────┐
                                                         │   NLP    │
                                                         │ (OpenAI) │
                                                         └──────────┘
                                                               │
                                                               ▼
                                                   ┌────────────────────┐
                                                   │  HL7/FHIR Services │
                                                   └────────────────────┘
                                                               │
                                                               ▼
                                                   ┌────────────────────┐
                                                   │    OpenEMR/Mirth   │
                                                   └────────────────────┘
```

### HL7 Message Flow

```
Command → NLP → Intent → HL7 Builder → MLLP → Mirth → OpenEMR
                                          │
                                          ▼
                                        ACK ←─────────────────┘
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each class has one reason to change
- `NLPService`: Only handles NLP
- `HL7Service`: Only handles HL7 messaging

### Open/Closed Principle (OCP)
- Open for extension, closed for modification
- New command types can be added without changing existing code

### Liskov Substitution Principle (LSP)
- Interfaces can be swapped with implementations
- `INLPService` can be replaced with any implementation

### Interface Segregation Principle (ISP)
- Specific interfaces for each service
- `INLPService`, `IHL7Service`, `IFHIRService` are separate

### Dependency Inversion Principle (DIP)
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)

## Scalability Considerations

### Current Implementation
- In-memory repositories for quick development
- Single-process application

### Future Enhancements

#### 1. Database Integration
```python
class DatabaseOperationRepository(IOperationRepository):
    # Implement with SQLAlchemy
    async def save_operation(self, operation):
        # Save to MySQL/PostgreSQL
```

#### 2. Message Queue
```python
# For async processing
from celery import Celery

@celery.task
async def process_bulk_operation(commands):
    # Process in background
```

#### 3. Caching Layer
```python
from redis import asyncio as aioredis

class CachedNLPService(INLPService):
    # Cache NLP interpretations
```

#### 4. Microservices
- Split services into separate containers
- HL7 Service as separate microservice
- NLP Service as separate microservice

## Security Considerations

### Current Implementation
- Environment variables for secrets
- CORS configuration
- Input validation via Pydantic

### Production Considerations
1. **Authentication**: Add JWT or OAuth
2. **Authorization**: Role-based access control
3. **Encryption**: TLS for all communications
4. **Audit Logging**: Track all operations
5. **Rate Limiting**: Prevent abuse

## Testing Strategy

### Unit Tests
```python
# Test domain entities
def test_patient_entity():
    patient = Patient(first_name="John", last_name="Doe")
    assert patient.first_name == "John"

# Test use cases with mocks
@pytest.mark.asyncio
async def test_process_command_use_case():
    # Mock dependencies
    nlp_service = Mock(INLPService)
    # Test business logic
```

### Integration Tests
```python
# Test API endpoints
async def test_process_command_endpoint():
    response = await client.post("/api/v1/command",
        json={"command": "Create a patient"})
    assert response.status_code == 200
```

### End-to-End Tests
- Test full workflow with real services
- Verify HL7 messages reach Mirth
- Confirm data appears in OpenEMR

## Performance Optimization

### Backend
1. **Async/Await**: Non-blocking I/O operations
2. **Connection Pooling**: Reuse HTTP connections
3. **Batch Processing**: Group operations when possible

### Frontend
1. **React Query**: Caching and request deduplication
2. **Code Splitting**: Lazy load components
3. **Virtualization**: For large message lists

## Monitoring and Logging

### Logging Strategy
```python
from loguru import logger

# Structured logging
logger.info("Processing command",
    command_type=command.command_type,
    session_id=context.session_id)
```

### Metrics to Track
- Command processing time
- Success/failure rates
- HL7 ACK response times
- OpenAI API latency

## Extensibility

### Adding New Command Types

1. **Add to Domain**:
```python
class CommandType(Enum):
    CREATE_APPOINTMENT = "create_appointment"  # New
```

2. **Implement Handler**:
```python
async def _handle_create_appointment(self, command):
    # Implementation
```

3. **Register in Router**:
```python
handlers = {
    CommandType.CREATE_APPOINTMENT: self._handle_create_appointment,
}
```

### Adding New Protocols

1. **Define Interface**:
```python
class IX12Service(ABC):
    @abstractmethod
    async def send_claim(self, claim: Claim) -> Result:
        pass
```

2. **Implement Service**:
```python
class X12Service(IX12Service):
    async def send_claim(self, claim):
        # Implementation
```

3. **Inject Dependency**:
```python
def get_x12_service() -> IX12Service:
    return X12Service()
```

## Technology Stack Summary

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI/NLP**: OpenAI GPT-4
- **HL7**: hl7apy, python-hl7
- **FHIR**: httpx, fhir.resources
- **Data**: Faker, SQLAlchemy
- **Async**: asyncio, uvicorn

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **UI**: Material-UI
- **State**: Zustand
- **HTTP**: Axios
- **Styling**: Emotion

### Infrastructure
- **Web Server**: Uvicorn (ASGI)
- **Database**: MySQL (OpenEMR)
- **Integration**: Mirth Connect
- **Container** (Future): Docker

## Deployment Architecture

### Development
```
Localhost:3000 (React) → Localhost:8000 (FastAPI) → Localhost:3306 (MySQL)
                              ↓
                    Localhost:6661 (MLLP)
                              ↓
                    Localhost:8443 (Mirth)
```

### Production (Recommended)
```
NGINX → Frontend (React Build)
  ↓
  → Backend API (Gunicorn + Uvicorn)
        ↓
        → Database (MySQL/PostgreSQL)
        → Redis (Caching)
        → Mirth Connect
```

## Best Practices Implemented

1. **Clean Architecture**: Separation of concerns
2. **SOLID Principles**: Maintainable code
3. **Dependency Injection**: Testable components
4. **Type Safety**: Pydantic models, TypeScript
5. **Async Programming**: Efficient I/O operations
6. **Error Handling**: Graceful degradation
7. **Logging**: Structured, contextual logging
8. **Documentation**: Comprehensive docstrings
9. **Configuration**: Environment-based settings
10. **API Versioning**: /api/v1/ prefix

This architecture ensures the application is maintainable, testable, and ready for future enhancements while meeting all URS requirements.
