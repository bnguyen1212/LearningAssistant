from .analysis import summarize_session

def save_session(
    referenced_files: list,
    llm_service,
    obsidian_service
) -> str:
    """
    Summarizes the session and saves the note to Obsidian.
    Calls summarize_session to get summary, subject, and topics, then saves the note.
    Returns path of saved session note.
    """
    summary_data = summarize_session(llm_service)
    subject = summary_data.get("subject", "")
    session_summary = summary_data.get("summary", "")
    topics = summary_data.get("topics", [])
    path = obsidian_service.save_session_notes(session_summary, subject, topics, referenced_files)
    return path
