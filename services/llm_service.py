import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from utils.prompt_templates import (
    CHAT_SYSTEM_PROMPT,
    TOPIC_ANALYSIS_PROMPT,
    NOTE_GENERATION_PROMPT,
    CONTEXT_MESSAGE_TEMPLATE
)

load_dotenv()

class LLMService:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7
        )
    
    def chat_with_context(self, user_message: str, recent_messages: List[Dict], 
                         relevant_context: List[str] = None) -> str:
        """
        Chat with Claude using only recent messages + context for token efficiency
        
        Args:
            user_message: Current user message
            recent_messages: Last 3 messages for context (List of {"role": str, "content": str})
            relevant_context: Relevant notes from vector search
        """
        messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]
        
        # Add recent conversation history (last 3 messages)
        for msg in recent_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        # Build current message with context
        if relevant_context:
            context_text = "\n\n".join(relevant_context)
            current_message = CONTEXT_MESSAGE_TEMPLATE.format(
                context_text=context_text,
                user_message=user_message
            )
        else:
            current_message = user_message
        
        messages.append(HumanMessage(content=current_message))
        
        # Get response from Claude
        response = self.llm.invoke(messages)
        return response.content
    
    def detect_note_request(self, message: str) -> bool:
        """
        Detect if user is requesting note generation
        """
        note_triggers = [
            "save this", "create notes", "write this down", "save notes",
            "capture this", "remember this", "save what we learned",
            "make notes", "document this", "save our discussion"
        ]
        
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in note_triggers)
    
    def analyze_conversation_topics(self, full_conversation: List[Dict]) -> List[str]:
        """
        Analyze the full conversation to identify distinct topics for note generation
        """
        # Convert conversation to text
        conversation_text = "\n\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in full_conversation
        ])
        
        analysis_prompt = TOPIC_ANALYSIS_PROMPT.format(
            conversation_text=conversation_text
        )

        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Parse topics from response
        topics = []
        for line in response.content.strip().split('\n'):
            topic = line.strip().strip('- ').strip()
            if topic:
                topics.append(topic)
        
        return topics
    
    def generate_note_for_topic(self, topic: str, full_conversation: List[Dict]) -> str:
        """
        Generate a structured note for a specific topic from the conversation
        """
        # Convert conversation to text
        conversation_text = "\n\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in full_conversation
        ])
        
        note_prompt = NOTE_GENERATION_PROMPT.format(
            topic=topic,
            conversation_text=conversation_text
        )

        response = self.llm.invoke([HumanMessage(content=note_prompt)])
        return response.content