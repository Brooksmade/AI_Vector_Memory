# Claude Memory API - Persistent Memory System

A comprehensive HTTP API-based memory system that provides persistent, searchable memory for AI assistants like Claude Code CLI and Claude Desktop. Uses ChromaDB for semantic search with sentence transformers.

## 🚀 **Features**

- **REST API Server**: Flask-based HTTP API with comprehensive endpoints
- **Semantic Search**: ChromaDB with sentence transformers for conceptual similarity
- **Cross-Platform**: Works with Claude Code CLI, Claude Desktop (via MCP), and any HTTP client
- **Persistent Storage**: Memories survive restarts and are shared across all projects
- **Windows Integration**: PowerShell module with automatic startup capabilities
- **Universal Compatibility**: Works with any AI assistant that can make HTTP requests

## 📦 **Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/christian-byrne/claude-code-vector-memory.git
cd claude-code-vector-memory
```

### **2. Python Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### **3. Start the System**
```bash
# Start the API server
python memory_api_server.py

# Verify it's running (in another terminal)
curl http://localhost:8080/api/health
```

## 🎯 **Quick Start**

1. **Clone and setup** (see Installation above)
2. **Start the server**: `python memory_api_server.py`
3. **Test the API**: `curl http://localhost:8080/api/health`
4. **Search memories**: `curl -X POST http://localhost:8080/api/search -H "Content-Type: application/json" -d '{"query": "python development"}'`

## 📖 **Integration Guides**

- **Complete Setup**: See [`QUICK_START.md`](QUICK_START.md) for detailed installation and configuration
- **Claude Code CLI**: Copy memory integration template from QUICK_START.md to your project's CLAUDE.md
- **Claude Desktop**: Follow MCP server setup instructions in QUICK_START.md
- **Windows Startup**: Use PowerShell module for automatic server startup

## 🔧 **API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | System health and status |
| `/api/search` | POST | Search for memories |
| `/api/add_memory` | POST | Save new memory |
| `/api/memories` | GET | List all memories (paginated) |
| `/api/memory/{id}` | DELETE | Delete specific memory |
| `/api/reindex` | POST | Rebuild search index |

## 🏗 **Architecture**

- **HTTP API Server**: Flask with CORS, rate limiting, logging
- **Vector Database**: ChromaDB with persistent storage
- **Embedding Model**: Sentence transformers for semantic search
- **PowerShell Module**: Windows integration and automation
- **Validation**: Pydantic models for request/response validation

## 🧪 **Testing**

```bash
# Run comprehensive test suite
python test_api.py

# Test with PowerShell module (Windows)
Import-Module .\ClaudeMemory.psm1
Test-ClaudeMemoryAPI
Search-ClaudeMemory "your query"
```

## 📁 **Project Structure**

```
claude-code-vector-memory/
├── memory_api_server.py          # Main Flask API server
├── ClaudeMemory.psm1            # PowerShell module
├── models.py                    # Pydantic validation models
├── memory_client.js             # JavaScript client library
├── test_api.py                  # API test suite
├── config.json                  # Server configuration
├── requirements.txt             # Core dependencies
├── requirements_api.txt         # API dependencies
├── scripts/                     # Core memory scripts
│   ├── memory_search.py         # Search functionality
│   ├── index_summaries.py       # Indexing system
│   └── health_check.py          # System diagnostics
├── chroma_db/                   # Vector database (auto-created)
├── QUICK_START.md               # Detailed setup guide
├── UNINSTALL.md                 # Complete removal guide
└── README.md                    # This file
```

## 💡 **Use Cases**

- **Project Continuity**: Remember past work across AI sessions
- **Cross-Project Learning**: Share knowledge between different projects
- **Development History**: Searchable archive of coding sessions
- **Team Memory**: Shared knowledge base for AI-assisted development

## 🛠 **Requirements**

- Python 3.9+ (recommended: 3.11+)
- 2GB free disk space (for embedding models)
- Windows 10/11 (for PowerShell features)
- Internet connection (initial model download)

## 📚 **Documentation**

- **[QUICK_START.md](QUICK_START.md)** - Complete installation and setup guide
- **[UNINSTALL.md](UNINSTALL.md)** - Full system removal instructions
- **Memory Integration Template** - Copy from QUICK_START.md for any project

## 🔒 **Security**

- **Input Validation**: All requests validated with Pydantic
- **Rate Limiting**: Prevents API abuse
- **Local Only**: Runs on localhost by default
- **No External Dependencies**: All data stored locally

## 👥 **Credits**

**Original Author**: [Christian Byrne](https://github.com/christian-byrne)  
**Original Repository**: https://github.com/christian-byrne/claude-code-vector-memory

This project builds upon Christian Byrne's original semantic memory system and extends it with a comprehensive HTTP API architecture, PowerShell integration, Windows startup capabilities, and cross-platform support. The foundational ChromaDB integration, semantic search functionality, and core memory indexing system were developed by the original author.

---

**Ready to get started?** See [QUICK_START.md](QUICK_START.md) for detailed setup instructions.