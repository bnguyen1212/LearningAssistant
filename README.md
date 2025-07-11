# 🎓 Learning Assistant

An intelligent conversational learning companion that integrates with your Obsidian knowledge base to provide contextual responses and automatically generate session summaries.

## ✨ Features

- **🤖 Intelligent Conversations**: Chat naturally about any topic with Claude AI
- **🔍 Knowledge Base Integration**: Searches your Obsidian vault for relevant context
- **📝 Automatic Note Generation**: Creates comprehensive session summaries
- **🔄 Seamless Integration**: Saves learning sessions back to your Obsidian vault
- **💡 Context-Aware Responses**: Maintains conversation flow and references your existing knowledge
- **⚡ Real-time Search**: Vector-based search through your personal knowledge base

## 🏗️ Architecture

The system uses a graph-based workflow architecture with specialized nodes:

```
User Input → Chat Node → Note Detection → Session Summary → Obsidian Integration
     ↑                                                              ↓
     └─────────────── Fresh Conversation ←─── Knowledge Re-indexing
```

### Core Components

- **Graph Workflow**: LangGraph-based conversation flow management
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

## 📁 Project Structure

```
LearningAssistant/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── generate_workflow_diagram.py # Workflow visualization
├── services/
│   ├── llm_service.py          # Claude Haiku integration
│   ├── vector_store.py         # ChromaDB & Voyage AI embeddings
│   ├── obsidian_service.py     # Obsidian vault operations
│   └── build_index.py          # Vector index builder
├── nodes/
│   ├── chat_nodes.py           # Conversation logic
│   ├── analysis_nodes.py       # Session summary generation
│   └── storage_nodes.py        # File operations & indexing
├── graph/
│   ├── state.py                # Conversation state management
│   └── workflow.py             # LangGraph workflow definition
├── utils/
│   └── prompt_templates.py     # LLM prompt templates
├── tests/
│   ├── test_integration_basic.py
│   └── test_integration_complete.py
└── chroma_db/                  # Vector database storage
```

## 🎯 Usage

### Starting a Conversation

```
💭 You: What is machine learning?

🤖 Assistant: Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed...

💭 You: How does it differ from traditional programming?

🤖 Assistant: Great follow-up! Based on our previous discussion about machine learning, the key differences are...
```

### Saving Learning Sessions

When you want to capture your learning session:

```
💭 You: save this conversation as notes

📝 Generating session summary...
✅ Session summary generated (1,247 characters)

💾 Saving session summary to Obsidian vault...
📁 Created session folder: 20250711_143022_What_is_machine
✅ Saved session summary: Learning_Session_Summary.md

🔄 Starting knowledge base re-indexing...
✅ Your knowledge base has been expanded!
```

### Available Commands

- **Note Generation**: `save this as notes`, `save`, `notes`, `summarize`
- **Fresh Start**: `new` - Start a new conversation
- **Exit**: `quit`, `exit`, `bye` - Close the application
- **Help**: `help`, `?` - Show available commands

## 📝 Generated Notes Format

Session summaries are automatically saved to your Obsidian vault:

```
Learning_Sessions/
└── 20250711_143022_What_is_machine/
    └── Learning_Session_Summary.md
```

**Example session summary:**

```markdown
---
created: 2025-07-11T14:30:22
type: learning_session_summary
session: 20250711_143022_What_is_machine
tags: [learning, session, summary]
---

# Learning Session Summary

**Session:** 20250711_143022_What_is_machine  
**Date:** 2025-07-11 14:30:22

## Main Topics Discussed

### Machine Learning Fundamentals
- Definition: Subset of AI that enables computers to learn from data
- Key characteristic: No explicit programming for every task
- Data-driven approach to problem solving

### Comparison with Traditional Programming
- Traditional: Explicit rules and logic programmed by developers
- ML: Patterns learned from data examples
- Use cases: When rules are complex or unknown

## Key Insights
- Machine learning excels at pattern recognition tasks
- Traditional programming better for well-defined logical processes
- Hybrid approaches often most effective in practice

## Questions Raised
- What are the main types of machine learning algorithms?
- How do you evaluate ML model performance?

## Next Steps
- Explore supervised vs unsupervised learning
- Learn about common algorithms (regression, classification, clustering)
```

## 🔧 Configuration

### Model Settings

**LLM Model** (in `services/llm_service.py`):
```python
model="claude-3-haiku-20240307"  # Fast and cost-effective
# Alternative: claude-3-5-sonnet-20241022 (more capable, higher cost)
```

**Embedding Model** (in `services/vector_store.py`):
```python
model_name="voyage-3-lite"  # Cost-effective
# Alternative: voyage-3 (higher accuracy, higher cost)
```

### Search Parameters

```python
# Number of relevant documents to retrieve
top_k=3

# Chunk size for document processing
chunk_size=512
chunk_overlap=50
```

## 🧪 Testing

### Run Integration Tests

```bash
# Complete integration test suite
python tests/test_integration_complete.py

# Basic functionality tests
python tests/test_integration_basic.py
```

### Manual Testing Checklist

1. **Conversation Flow**: Multi-turn conversations with context retention
2. **Knowledge Search**: Finding relevant content from your vault
3. **Note Generation**: Creating and saving session summaries
4. **File Integration**: Verifying notes appear in Obsidian
5. **Fresh Sessions**: Starting new conversations cleanly

## 🔍 Troubleshooting

### Common Issues

**"Index not built" error:**
```bash
python services/build_index.py
```

**API errors:**
- Verify API keys in `.env` file
- Check account credits/quotas
- Ensure network connectivity

**Obsidian integration issues:**
- Verify `OBSIDIAN_VAULT_PATH` points to correct directory
- Check file system permissions
- Ensure Obsidian vault exists

**Empty search results:**
- Run `python view_chromadb.py` to check database
- Rebuild index if necessary
- Verify vault contains markdown files

### Debug Tools

```bash
# View database contents
python view_chromadb.py

# Test minimal setup
python test_minimal.py

# Generate workflow diagram
python generate_workflow_diagram.py
```

## 📊 Cost Optimization

The system is designed for cost-effective operation:

- **Claude Haiku**: ~10x cheaper than Claude Sonnet
- **Voyage 3-lite**: Cost-effective embeddings
- **Smart Context**: Only sends recent messages to LLM
- **Early Detection**: Skips LLM calls for note requests

**Estimated costs** (per 1000 messages):
- Claude Haiku: $0.50-2.00
- Voyage embeddings: $0.10-0.50
- **Total**: ~$0.60-2.50 per 1000 interactions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Ready to enhance your learning journey? Start exploring with the Learning Assistant today!** 🚀
