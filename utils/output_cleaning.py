import re
from core.config import config

def detect_model_type():
    """
    Detect the model type from config. Returns a string like 'openai', 'anthropic', etc.
    """
    # Example: config.llm_service.model_name or config.MODEL_TYPE
    # Adjust this logic to match your config structure
    model_name = config.LLM_MODEL
    if model_name:
        name = str(model_name).lower()
        if 'openai' in name:
            return 'openai'
        if 'anthropic' in name or 'claude' in name:
            return 'anthropic'
        # Add more model type checks as needed
    return 'generic'


def clean_llm_output(text):
    """
    Clean LLM output by removing tool/function blocks, auto-detecting model type from config.
    """
    model_type = detect_model_type()
    patterns = [
        r"<function_calls>.*?</function_calls>",
        r"<invoke.*?>.*?</invoke>",
        r"<result>.*?</result>",
        r"<tool_calls>.*?</tool_calls>",
        r"<tool_use>.*?</tool_use>",
        r"<function_call>.*?</function_call>",
        r"<functions>.*?</functions>",
        r"<response>.*?</response>",
    ]
    if model_type == "openai":
        patterns += [r'"tool_calls":.*?\}\]']
    elif model_type == "anthropic":
        patterns += [r"\[tool_use\].*?\[\/tool_use\]"]
    # Add more model-specific patterns as needed
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.DOTALL)
    return text.strip()
