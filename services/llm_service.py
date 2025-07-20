from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.config import config

class LLMService:
    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in config")
        self.llm = ChatAnthropic(
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
        )

    def invoke(self, messages): #Stateful
        """
        Directly invoke the LLM with a list of message objects.
        """
        return self.llm.invoke(messages)

    def invoke_prompt(self, prompt: str): #Stateless
        """
        Directly invoke the LLM with a single prompt string.
        """
        return self.llm.invoke([HumanMessage(content=prompt)])