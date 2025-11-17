"""Repository implementations for data persistence."""
from typing import Optional, List, Dict
from datetime import datetime

from app.domain.entities import HL7Message, OperationResult, ConversationContext
from app.domain.interfaces import IMessageRepository, IOperationRepository, IContextRepository


class InMemoryMessageRepository(IMessageRepository):
    """In-memory implementation of message repository."""

    def __init__(self):
        self.messages: Dict[str, HL7Message] = {}
        self.sessions: Dict[str, List[str]] = {}

    async def save_message(self, message: HL7Message) -> None:
        """Save an HL7 message."""
        self.messages[message.message_id] = message

        # Track by session if metadata contains session_id
        session_id = message.metadata.get("session_id")
        if session_id:
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            self.sessions[session_id].append(message.message_id)

    async def get_message(self, message_id: str) -> Optional[HL7Message]:
        """Retrieve a message by ID."""
        return self.messages.get(message_id)

    async def get_messages_by_session(self, session_id: str) -> List[HL7Message]:
        """Retrieve all messages for a session."""
        message_ids = self.sessions.get(session_id, [])
        return [self.messages[mid] for mid in message_ids if mid in self.messages]


class InMemoryOperationRepository(IOperationRepository):
    """In-memory implementation of operation repository."""

    def __init__(self):
        self.operations: Dict[str, OperationResult] = {}
        self.sessions: Dict[str, List[str]] = {}

    async def save_operation(self, operation: OperationResult) -> None:
        """Save an operation result."""
        self.operations[operation.operation_id] = operation

    async def get_operation(self, operation_id: str) -> Optional[OperationResult]:
        """Retrieve an operation by ID."""
        return self.operations.get(operation_id)

    async def get_operations_by_session(self, session_id: str) -> List[OperationResult]:
        """Retrieve all operations for a session."""
        return [
            op for op in self.operations.values()
            if op.command_id.startswith(session_id)
        ]


class InMemoryContextRepository(IContextRepository):
    """In-memory implementation of context repository."""

    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}

    async def save_context(self, context: ConversationContext) -> None:
        """Save conversation context."""
        self.contexts[context.session_id] = context

    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context by session ID."""
        return self.contexts.get(session_id)

    async def update_context(self, context: ConversationContext) -> None:
        """Update existing conversation context."""
        context.last_activity = datetime.utcnow()
        self.contexts[context.session_id] = context
