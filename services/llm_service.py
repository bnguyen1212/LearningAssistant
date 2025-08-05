from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.config import config
from utils.prompt_templates import CHAT_SYSTEM_PROMPT
from core.conversation import conversation_manager

class LLMService:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in config")
        self.llm = ChatAnthropic(
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )
        # Set system prompt (default or provided)
        self.system_prompt = CHAT_SYSTEM_PROMPT

    def invoke(self, messages): #Stateful
        """
        Directly invoke the LLM with a list of message objects.
        """
        return self.llm.invoke(messages)

    def invoke_context(self, prompt: str): #Stateless
        """
        Directly invoke the LLM with a single prompt string, always with system prompt and recent context.
        """
        messages = [SystemMessage(content=self.system_prompt)]
        recent_messages = conversation_manager.get_history()
        if recent_messages:
            messages.extend(recent_messages)
            print(f"Recent messages: {recent_messages}")
        messages.append((HumanMessage(content=prompt)))
        print(f"LLM Invoked: {messages}")
        response = self.llm.invoke(
            messages
        )
        print("\nLLM Response: ", response)
        return response
    def invoke_prompt(self, prompt: str):
        """
        Directly invoke the llm with just a single prompt string.
        """
        return self.llm.invoke([HumanMessage(content=prompt)])
llm_service = LLMService()