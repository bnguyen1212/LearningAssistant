from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.config import config
from utils.prompt_templates import CHAT_SYSTEM_PROMPT

class LLMService:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in config")
        self.llm = ChatAnthropic(
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
        )
        # Set system prompt (default or provided)
        self.system_prompt = CHAT_SYSTEM_PROMPT

    def invoke(self, messages): #Stateful
        """
        Directly invoke the LLM with a list of message objects. Prepends system prompt if not already present.
        """
        # Only add system prompt if not already present
        if not messages or not (isinstance(messages[0], SystemMessage) and messages[0].content == self.system_prompt):
            messages = [SystemMessage(content=self.system_prompt)] + messages
        return self.llm.invoke(messages)

    def invoke_prompt(self, prompt: str): #Stateless
        """
        Directly invoke the LLM with a single prompt string, always with system prompt.
        """
        return self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ])