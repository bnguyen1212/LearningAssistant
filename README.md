# 🎓 Learning Assistant

An intelligent conversational learning companion that integrates with your Obsidian knowledge base to provide contextual responses and automatically generate session summaries.

---

### Tool-Based Workflow

The assistant now uses a tool-based workflow, where the LLM suggests tool calls and the Python backend executes them. This enables:

- Modular tool functions for context search, session saving, and more
- Clear separation between LLM reasoning and backend actions
- Easier extensibility for new tools and features

**How it works:**

- The LLM returns a tool call (e.g., `chat_with_context_tool` or `save_session_tool`)
- The backend inspects the tool call, executes the corresponding Python function, and returns results
- The LLM then uses the tool results to generate a final conversational response

### Configuration Options

You can configure the assistant using the `.env` file and Python settings:

- `ANTHROPIC_API_KEY`: Claude API key
- `VOYAGE_API_KEY`: Voyage AI embeddings key
- `OBSIDIAN_VAULT_PATH`: Path to your Obsidian vault
- `LLM_MODEL`: Claude model (e.g., `claude-3-haiku-20240307`)
- `LLM_TEMPERATURE`: LLM response creativity (float, e.g., `0.2`)
- `EMBEDDING_MODEL`: Voyage model (e.g., `voyage-3-lite`)
- `TOP_K`: Number of relevant documents to retrieve (default: 3)
- `CHUNK_SIZE`: Document chunk size for indexing (default: 512)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)

These can be set in `.env` or in the relevant Python config files.

### Updated Project Structure

The project is organized for clarity and modularity:

```
LearningAssistant/
├── main.py                     # Application entry point & tool orchestration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── services/
│   ├── llm_service.py          # LLM integration & prompt management
│   ├── vector_store.py         # ChromaDB & Voyage AI embeddings
│   ├── obsidian_service.py     # Obsidian vault operations
├── agent/
│   ├── learning_agent.py       # Agent logic
│   └── tools/
│       ├── chat.py             # Context search tool
│       ├── storage.py          # Session save tool
│       └── analysis.py         # Analysis tool helper
├── core/
│   ├── config.py               # Configuration management
│   ├── conversation.py         # Conversation state/history
├── utils/
│   └── prompt_templates.py     # LLM prompt templates
├── tests/
│   ├── test_integration_basic.py
│   └── test_integration_complete.py
└── chroma_db/                  # Vector database storage
```

### Session Summary Format

Session summaries are automatically saved to your Obsidian vault in a daily folder structure, with unique filenames and backlinks to referenced files.

**File Structure:**

```
<OBSIDIAN_DAILY_NOTES_FOLDER>/
    July 25, 2025/
        What_is_machine_143022.md
```

**Session Summary Example:**

```markdown
---
created: 2025-07-11T14:30:22
type: learning_session_summary
daily_folder: July 11, 2025
tags: [learning, session, summary]
---

# Learning Session Summary

<session summary content>

## Referenced Files

- [[Some_Note]]
- [[Another_Note]]
```

**Backlinks:**

- For every referenced file, a backlink is automatically added to the original note under a `## References` section:
  ```markdown
  ## References

  - [[Daily Notes/July 11, 2025/What_is_machine_143022]]
  ```

**File Naming:**

- Session summaries are named as `<SessionName>_<HHMMSS>.md` for uniqueness and clarity.

This structure ensures easy navigation, traceability, and rich interlinking between your learning sessions and your existing notes.

---

## ✨ Features

- **🤖 Intelligent Conversations**: Chat naturally about any topic with Claude AI
- **🔍 Knowledge Base Integration**: Searches your Obsidian vault for relevant context
- **📝 Automatic Note Generation**: Creates comprehensive session summaries
- **🔄 Seamless Integration**: Saves learning sessions back to your Obsidian vault
- **💡 Context-Aware Responses**: Maintains conversation flow and references your existing knowledge
- **⚡ Real-time Search**: Vector-based search through your personal knowledge base

### Core Components

- **Vector Store**: ChromaDB with Voyage AI embeddings for semantic search
- **LLM Service**: Claude Haiku for cost-effective, intelligent responses
- **Obsidian Integration**: Direct file system integration with markdown generation

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Obsidian vault with markdown files
- API keys for Anthropic (Claude) and Voyage AI

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd LearningAssistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
VOYAGE_API_KEY=your_voyage_key_here
OBSIDIAN_VAULT_PATH=C:\path\to\your\obsidian\vault
```

### 4. Build Vector Index

```bash
python services/build_index.py
```

### 5. Start the Assistant

```bash
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Ready to enhance your learning journey? Start exploring with the Learning Assistant today!** 🚀
