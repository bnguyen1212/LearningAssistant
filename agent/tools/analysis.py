from utils.prompt_templates import SESSION_SUMMARY_TEMPLATE
from core.conversation import conversation_manager
def summarize_session(llm_service) -> dict:
    """
    Generate a subject line, markdown summary, and topic list from the conversation text using the LLM.
    Returns a dict with keys: 'subject', 'summary', 'topics'
    """
    conversation_text = conversation_manager.get_conversation_for_summary() 
    print(conversation_text)
    prompt = SESSION_SUMMARY_TEMPLATE.format(conversation_text=conversation_text)
    try:
        response = llm_service.invoke_prompt(prompt)
        content = response.content if hasattr(response, "content") else str(response)

        # Parse output
        subject = ""
        summary = ""
        topics = []

        # Split by section headers
        lines = content.splitlines()
        section = None
        summary_lines = []
        for line in lines:
            if line.strip().lower().startswith("subject line:"):
                section = "subject"
            elif line.strip().lower().startswith("session summary:"):
                section = "summary"
            elif line.strip().lower().startswith("topics:"):
                section = "topics"
            elif section == "subject" and line.strip():
                subject = line.strip();
            elif section == "summary" and line.strip():
                summary_lines.append(line)
            elif section == "topics" and line.strip():
                topics = [topic.strip() for topic in line.split(",") if topic.strip()]
        
        summary = "\n".join(summary_lines).strip()
        return {
            "subject": subject,
            "summary": summary,
            "topics": topics
        }
    except Exception as e:
        print(f"Session summarization failed: {e}")
        return {"subject": "", "summary": "", "topics": []}