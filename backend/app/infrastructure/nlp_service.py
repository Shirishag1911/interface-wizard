"""NLP Service implementation using OpenAI."""
import json
from typing import Optional
from openai import AsyncOpenAI
from loguru import logger

from app.config import settings
from app.domain.entities import UserCommand, CommandType, OperationResult, ConversationContext
from app.domain.interfaces import INLPService


class OpenAINLPService(INLPService):
    """NLP service implementation using OpenAI GPT-4."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def interpret_command(
        self, raw_text: str, context: Optional[ConversationContext] = None
    ) -> UserCommand:
        """Interpret natural language command using OpenAI."""
        try:
            system_prompt = self._get_interpretation_system_prompt()
            user_prompt = self._build_interpretation_user_prompt(raw_text, context)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"NLP interpretation result: {result}")

            return UserCommand(
                raw_text=raw_text,
                command_type=CommandType(result.get("command_type", "unknown")),
                parameters=result.get("parameters", {}),
            )

        except Exception as e:
            logger.error(f"Error interpreting command: {str(e)}", exc_info=True)
            return UserCommand(
                raw_text=raw_text,
                command_type=CommandType.UNKNOWN,
                parameters={},
            )

    async def generate_response(
        self, operation_result: OperationResult, context: Optional[ConversationContext] = None
    ) -> str:
        """Generate human-friendly response using OpenAI."""
        try:
            system_prompt = self._get_response_generation_system_prompt()
            user_prompt = self._build_response_generation_user_prompt(operation_result, context)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return operation_result.message  # Fallback to default message

    def _get_interpretation_system_prompt(self) -> str:
        """Get system prompt for command interpretation."""
        return """You are an AI assistant for Interface Wizard, a healthcare data integration tool.
Your task is to interpret natural language commands related to EHR data operations and convert them into structured format.

Available command types:
- create_patient: Create a single patient record
- create_bulk: Create multiple patient records at once
- update_patient: Update an existing patient record
- retrieve_patient: Retrieve patient information
- retrieve_lab_result: Retrieve lab results for a patient
- admit_patient: Admit a patient to the hospital
- discharge_patient: Discharge a patient from the hospital
- transfer_patient: Transfer a patient to another location
- query: General query about data
- unknown: Command cannot be understood

Extract parameters from the command such as:
- count: number of records (for bulk operations)
- patient_id, mrn: patient identifiers
- first_name, last_name, date_of_birth, gender: patient demographics
- test_type: type of lab test
- location: hospital location
- Any other relevant parameters mentioned

Respond ONLY with a JSON object in this format:
{
    "command_type": "create_patient",
    "parameters": {
        "first_name": "John",
        "last_name": "Doe",
        ...
    },
    "confidence": 0.95
}"""

    def _build_interpretation_user_prompt(self, raw_text: str, context: Optional[ConversationContext]) -> str:
        """Build user prompt for command interpretation."""
        prompt = f"Interpret this command: {raw_text}\n\n"

        if context and context.command_history:
            recent_commands = context.command_history[-3:]
            prompt += "Recent conversation context:\n"
            for cmd in recent_commands:
                prompt += f"- User said: {cmd.raw_text}\n"

        return prompt

    def _get_response_generation_system_prompt(self) -> str:
        """Get system prompt for response generation."""
        return """You are a friendly AI assistant for Interface Wizard.
Generate clear, concise, and helpful responses to users about their EHR data operations.

Guidelines:
- Be professional but conversational
- Explain what was done clearly
- If there were errors, explain them in simple terms and suggest solutions
- Use medical terminology appropriately but keep language accessible
- Keep responses concise (2-4 sentences typically)
- If data was retrieved, present it in a readable format"""

    def _build_response_generation_user_prompt(
        self, operation_result: OperationResult, context: Optional[ConversationContext]
    ) -> str:
        """Build user prompt for response generation."""
        prompt = f"""Generate a user-friendly response for this operation:

Status: {operation_result.status.value}
Default Message: {operation_result.message}
Records Affected: {operation_result.records_affected}
Records Succeeded: {operation_result.records_succeeded}
Records Failed: {operation_result.records_failed}
Protocol Used: {operation_result.protocol_used.value if operation_result.protocol_used else 'N/A'}

"""

        if operation_result.data:
            prompt += f"Data: {json.dumps(operation_result.data, indent=2)[:500]}\n\n"

        if operation_result.errors:
            prompt += f"Errors: {', '.join(operation_result.errors[:3])}\n\n"

        if operation_result.warnings:
            prompt += f"Warnings: {', '.join(operation_result.warnings[:3])}\n\n"

        prompt += "Generate a clear, helpful response for the user."

        return prompt
