# Bare-bones LangGraph Learning Assistant

A minimal personal learning assistant built with LangGraph that integrates with your Obsidian vault and personal code.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:

   ```bash
   # Edit .env file with your paths and API key
   ANTHROPIC_API_KEY=your_key_here
   OBSIDIAN_VAULT_PATH=C:\path\to\obsidian\vault
   CODE_PATH=C:\path\to\your\code
   ```

3. Run:
   ```bash
   python main.py
   ```

## Features

- ✅ Searches Obsidian vault for relevant notes
- ✅ Analyzes personal code repositories
- ✅ Falls back to external web search
- ✅ Generates comprehensive learning notes
- ✅ Updates Obsidian vault with new notes

## Workflow

1. **Search Obsidian** - Finds relevant existing notes
2. **Search Code** - Looks through personal code files
3. **External Search** - Gets info from DuckDuckGo API
4. **Generate Notes** - Creates structured learning content
5. **Update Vault** - Saves new notes to Obsidian

The workflow runs sequentially using LangGraph state management.
