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

# Prompt for analyzing conversation topics
TOPIC_ANALYSIS_PROMPT = """Analyze this conversation and identify distinct learning topics that should have separate notes created.

Conversation:
{conversation_text}

Return a simple list of topic names, one per line. Each topic should be specific enough to create a focused note. For example:
- Neural Network Architectures
- Python Performance Optimization  
- Machine Learning Data Preprocessing

Topics (one per line):"""

# Prompt for generating notes for a specific topic
NOTE_GENERATION_PROMPT = """Based on our conversation, create a comprehensive learning note about: {topic}

Full conversation:
{conversation_text}

Create a well-structured markdown note that:
1. Captures key concepts and insights about {topic}
2. Includes important details, examples, and explanations
3. Highlights connections to related topics
4. Notes any questions or areas for further exploration
5. Organizes information clearly with headers and bullet points

Focus only on content related to {topic}. Make it a valuable reference for future learning.

Note content:"""

# Template for formatting context in chat messages
CONTEXT_MESSAGE_TEMPLATE = """Context from your knowledge base:
{context_text}

---

{user_message}"""

# Prompt for generating category paths for note organization
CATEGORY_GENERATION_PROMPT = """Given the topic "{topic}", suggest an appropriate folder hierarchy for organizing this note in a knowledge base.

Return only the folder path using forward slashes, like:
- AI_and_Machine_Learning/Deep_Learning
- Programming/Python/Performance
- Data_Science/Statistics
- Web_Development/Frontend
- Mathematics/Linear_Algebra

Keep it 1-3 levels deep maximum. Use underscores instead of spaces.

Topic: {topic}
Folder path:"""