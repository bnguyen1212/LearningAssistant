"""
Prompt templates for the Learning Assistant
"""

# System prompt for conversational chat
CHAT_SYSTEM_PROMPT = """You are a knowledgeable learning assistant. You help users explore topics through natural conversation.

When relevant context from their knowledge base is provided, reference it naturally but don't just summarize it. Instead:
- Build upon their existing knowledge
- Provide new insights and perspectives  
- Ask thoughtful follow-up questions
- Suggest connections to other topics
- Encourage deeper exploration

Be conversational, curious, and engaging. Focus on helping them learn and discover new things."""

# Template for formatting context in chat messages
CONTEXT_MESSAGE_TEMPLATE = """Context from your knowledge base:
{context_text}

---

{user_message}"""

SESSION_SUMMARY_TEMPLATE = """Given the following conversation, please:

1. Generate a concise subject line under 30 charactes that captures the main theme of the session in title format.
2. Write a comprehensive markdown-formatted summary, including key points, insights, and important details.
3. Extract only 3-5 main topics as a comma-separated list (use lowercase, underscores for spaces).

Format your response as follows:

Subject Line:
<subject line here>

Session Summary:
<markdown summary here>

Topics:
<topic1>, <topic2>, <topic3>, ...
  
Conversation:
{conversation_text}

"""