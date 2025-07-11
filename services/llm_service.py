import os
from typing import List, Dict
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from utils.prompt_templates import (
    CHAT_SYSTEM_PROMPT,
    CONTEXT_MESSAGE_TEMPLATE,
    SESSION_SUMMARY_PROMPT
)

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.llm = ChatAnthropic(
            anthropic_api_key=api_key,
            model="claude-3-haiku-20240307",
            temperature=0.7,
            max_tokens=4000
        )
    
    def detect_note_request(self, user_message: str) -> bool:
        """
        Detect if the user is requesting to save/generate notes
        """
        note_triggers = [
            "save", "notes", "remember", "capture", "record", "write down",
            "summarize", "summary", "take notes", "save this", "keep this"
        ]
        
        message_lower = user_message.lower()
        return any(trigger in message_lower for trigger in note_triggers)
    
    def chat_with_context(self, user_message: str, recent_messages: List[Dict], 
                         relevant_context: List[str] = None) -> str:
        """
        Generate a response using conversation context and knowledge base context
        """
        # Format the user message with context if available
        if relevant_context:
            context_text = "\n\n".join(relevant_context)
            formatted_message = CONTEXT_MESSAGE_TEMPLATE.format(
                context_text=context_text,
                user_message=user_message
            )
        else:
            formatted_message = user_message
        
        # Build message history
        messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]
        
        # Add recent conversation history
        for msg in recent_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=formatted_message))
        
        # Get response
        response = self.llm.invoke(messages)
        return response.content
    
    def generate_session_summary(self, full_conversation: List[Dict]) -> str:
        """
        Generate a comprehensive session summary from the entire conversation
        """
        # Convert conversation to text
        conversation_text = "\n\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in full_conversation
        ])
        
        summary_prompt = SESSION_SUMMARY_PROMPT.format(
            conversation_text=conversation_text
        )

        from langchain_core.messages import HumanMessage
        response = self.llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content