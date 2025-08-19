# Claude Memory API - Advanced AI Memory System with Automatic Engagement

A comprehensive HTTP API-based memory system that provides persistent, searchable memory for AI assistants like Claude Code CLI and Claude Desktop. Features automatic memory engagement through hooks, intelligent curation, and semantic search with ChromaDB.

## 🚀 **Key Features**

### Core Capabilities
- **REST API Server**: Flask-based HTTP API with comprehensive endpoints
- **Semantic Search**: ChromaDB with sentence transformers for conceptual similarity (TF-IDF for near-duplicates)
- **Cross-Platform**: Works with Claude Code CLI, Claude Desktop (via MCP), and any HTTP client
- **Persistent Storage**: Memories survive restarts and are shared across all projects
- **Windows Integration**: PowerShell module with automatic startup capabilities

### Advanced Features (NEW)
- **🪝 Claude Code Hooks**: Automatic memory engagement without manual API calls
- **🧹 Memory Curation**: Deduplication, consolidation, archiving, and quality enhancement
- **📊 Analytics & Insights**: Pattern recognition, error tracking, technology trends
- **🔍 Active Memory**: File watching, error learning, and context tracking (optional)
- **🛠 Management CLI**: Interactive tool for memory maintenance and analysis

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

# Install core dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt

# Install advanced features (optional but recommended)
pip install scikit-learn rich click  # For curation features
pip install watchdog                 # For active memory features
```

### **3. Start the System**
```bash
# Start the API server with all features
python memory_api_server.py

# Verify it's running (in another terminal)
curl http://localhost:8080/api/health
```

## 🎯 **Quick Start**

### Basic Usage
1. **Clone and setup** (see Installation above)
2. **Start the server**: `python memory_api_server.py`
3. **Test the API**: `curl http://localhost:8080/api/health`
4. **Search memories**: `curl -X POST http://localhost:8080/api/search -H "Content-Type: application/json" -d '{"query": "python development"}'`

### Advanced Usage with Claude Code Hooks
1. **Copy hook scripts to your project**:
   ```bash
   mkdir -p .claude/hooks
   cp E:\tools\claude-code-vector-memory\hooks\*.sh .claude/hooks/
   ```

2. **Configure hooks in `.claude/settings.local.json`**:
   ```json
   {
     "hooks": {
       "SessionStart": [{"hooks": [{"type": "command", "command": "bash .claude/hooks/session-start.sh"}]}],
       "PreToolUse": [
         {"matcher": "Edit|Write|MultiEdit", "hooks": [{"type": "command", "command": "bash .claude/hooks/memory-check.sh"}]}
       ],
       "PostToolUse": [
         {"matcher": "*", "hooks": [{"type": "command", "command": "bash .claude/hooks/error-recovery.sh"}]}
       ]
     }
   }
   ```

3. **Memory engages automatically** - no manual API calls needed!

## 📖 **Integration Guides**

- **Complete Setup**: See [`GLOBAL_SETUP_GUIDE.md`](GLOBAL_SETUP_GUIDE.md) for all setup methods
- **Claude Code Hooks**: Automatic memory engagement through event hooks
- **Memory Manager CLI**: Interactive management tool
- **Windows Startup**: PowerShell module for automatic server startup

## 🔧 **API Endpoints**

### Core Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | System health and status |
| `/api/search` | POST | Semantic search for memories |
| `/api/add_memory` | POST | Save new memory |
| `/api/memories` | GET | List all memories (paginated) |
| `/api/memory/{id}` | DELETE | Delete specific memory |
| `/api/reindex` | POST | Rebuild search index |

### Curation Endpoints (NEW)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/curator/health` | GET | Analyze memory health |
| `/api/curator/deduplicate` | POST | Remove duplicate memories |
| `/api/curator/consolidate` | POST | Merge related memories |
| `/api/curator/archive` | POST | Archive old memories |
| `/api/curator/enhance/{id}` | POST | Improve memory quality |
| `/api/curator/analyze` | GET | Pattern analysis & insights |
| `/api/curator/auto-curate` | POST | Automatic maintenance |

### Active Memory Endpoints (NEW)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/active/status` | GET | Current context status |
| `/api/active/decisions` | GET | Pending warnings/decisions |
| `/api/active/context` | POST | Update current context |
| `/api/active/check_before_action` | POST | Pre-action memory check |

## 🛠 **Memory Manager CLI**

Interactive command-line tool for memory management:

```bash
# Interactive mode
python memory_manager.py interactive

# Check memory health
python memory_manager.py health

# Remove duplicates
python memory_manager.py deduplicate --execute

# Archive old memories
python memory_manager.py archive --days 90 --execute

# Auto-curate (dry run first, then execute)
python memory_manager.py auto-curate
python memory_manager.py auto-curate --execute

# Search with rich output
python memory_manager.py search

# View statistics
python memory_manager.py stats
```

## 🪝 **Claude Code Hooks System**

### Available Hooks
1. **session-start.sh** - Initialize context, find relevant past work
2. **session-end.sh** - Save session summary
3. **memory-check.sh** - Check before file edits
4. **memory-store.sh** - Store errors and outcomes
5. **test-check.sh** - Warn about past test failures
6. **git-check.sh** - Git operation guidance
7. **dependency-check.sh** - Package installation warnings
8. **error-recovery.sh** - Analyze errors, suggest solutions

### Hook Events
- **SessionStart**: When Claude Code session begins
- **PreToolUse**: Before tool execution (Edit, Write, Bash, etc.)
- **PostToolUse**: After tool execution
- **Stop**: When session ends

## 🏗 **Architecture**

```
claude-code-vector-memory/
├── memory_api_server.py          # Main Flask API server
├── memory_curator.py             # Curation system (NEW)
├── memory_curation_api.py        # Curation endpoints (NEW)
├── memory_active_features.py     # Active memory features (NEW)
├── memory_manager.py             # CLI management tool (NEW)
├── ClaudeMemory.psm1            # PowerShell module
├── models.py                    # Pydantic validation models
├── memory_client.js             # JavaScript client library
├── hooks/                       # Claude Code hook scripts (NEW)
│   ├── session-start.sh
│   ├── session-end.sh
│   ├── memory-check.sh
│   ├── memory-store.sh
│   ├── test-check.sh
│   ├── git-check.sh
│   ├── dependency-check.sh
│   └── error-recovery.sh
├── scripts/                     # Core memory scripts
│   ├── memory_search.py        # Search functionality
│   ├── index_summaries.py      # Indexing system
│   └── health_check.py         # System diagnostics
├── chroma_db/                   # Vector database (auto-created)
├── config.json                  # Server configuration
├── requirements.txt             # Core dependencies
├── requirements_api.txt         # API dependencies
├── GLOBAL_SETUP_GUIDE.md        # Complete setup guide (UPDATED)
├── QUICK_START.md               # Quick setup guide
├── UNINSTALL.md                 # Removal guide
└── README.md                    # This file
```

## 💡 **Use Cases**

### Basic
- **Project Continuity**: Remember past work across AI sessions
- **Cross-Project Learning**: Share knowledge between different projects
- **Development History**: Searchable archive of coding sessions
- **Team Memory**: Shared knowledge base for AI-assisted development

### Advanced
- **Error Prevention**: Learn from past mistakes automatically
- **Pattern Recognition**: Identify recurring issues and solutions
- **Quality Improvement**: Automatic memory curation and enhancement
- **Context Awareness**: Maintain working context throughout sessions
- **Proactive Assistance**: Warn about issues before they occur

## 📊 **Memory Quality & Curation**

The system automatically maintains memory quality through:

### Quality Scoring
- Content length and structure
- Metadata completeness (title, date, technologies)
- Code block presence
- Complexity rating

### Automatic Curation
- **Deduplication**: Remove exact and near-duplicate memories
- **Consolidation**: Merge related memories into comprehensive ones
- **Archiving**: Move old memories to archive files
- **Enhancement**: Improve metadata and structure

### Maintenance Schedule
```bash
# Recommended maintenance
python memory_manager.py auto-curate --execute  # Daily
python memory_manager.py health                 # Weekly
python memory_manager.py archive --days 90      # Monthly
```

## 🔒 **Security**

- **Input Validation**: All requests validated with Pydantic
- **Rate Limiting**: Prevents API abuse (configurable limits)
- **Local Only**: Runs on localhost by default
- **No External Dependencies**: All data stored locally
- **Hook Safety**: Hooks only trigger on AI actions, not user edits

## 🛠 **Requirements**

- Python 3.9+ (recommended: 3.11+)
- 2GB free disk space (for embedding models)
- Windows 10/11 (for PowerShell features)
- Internet connection (initial model download only)

### Optional Dependencies
- **scikit-learn**: For curation features (deduplication, quality scoring)
- **rich & click**: For CLI management tool
- **watchdog**: For active file monitoring

## 📚 **Documentation**

- **[GLOBAL_SETUP_GUIDE.md](GLOBAL_SETUP_GUIDE.md)** - Complete setup with all features
- **[QUICK_START.md](QUICK_START.md)** - Basic installation guide
- **[UNINSTALL.md](UNINSTALL.md)** - Full system removal instructions
- **[hooks/README.md](hooks/README.md)** - Hook system documentation

## 🚦 **Status Indicators**

When running with all features:
- ✅ **Core API**: Basic memory storage and search
- ✅ **Curation API**: Memory maintenance features
- ✅ **Active Memory**: File watching and context tracking
- ✅ **Hooks Integration**: Automatic engagement with Claude Code

## 👥 **Credits**

**Original Author**: [Christian Byrne](https://github.com/christian-byrne)  
**Original Repository**: https://github.com/christian-byrne/claude-code-vector-memory

This project builds upon Christian Byrne's original semantic memory system and extends it with:
- Comprehensive HTTP API architecture
- Claude Code hooks for automatic engagement
- Memory curation and quality management system
- Active memory features with file watching
- Interactive CLI management tool
- Pattern recognition and error learning
- PowerShell integration and Windows startup capabilities

The foundational ChromaDB integration, semantic search functionality, and core memory indexing system were developed by the original author.

---

**Ready to get started?** 
- Basic setup: See [QUICK_START.md](QUICK_START.md)
- Full features: See [GLOBAL_SETUP_GUIDE.md](GLOBAL_SETUP_GUIDE.md)
- Just want hooks? Copy the `hooks/` directory to your project!