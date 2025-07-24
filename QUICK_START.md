# Claude Memory API - Complete Setup Guide

## 📋 **Prerequisites**

- **Python 3.9+** (recommended: Python 3.11+)
- **Git** (for cloning repository)
- **2GB free disk space** (for embedding models)
- **Internet connection** (initial setup only)

## 🚀 **Installation from GitHub**

### **1. Clone Repository**
```bash
# Clone to your preferred location
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

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### **3. First-Time Initialization**
```bash
# The system will auto-create the database on first run
# Start the API server
python memory_api_server.py
```

### **4. Verify Installation**
```bash
# In another terminal, test the API
curl http://localhost:8080/api/health

# Should return: {"success": true, "data": {"status": "healthy"}}
```

## 📁 **Directory Structure**
After cloning, you'll have:
```
your-chosen-directory/
└── claude-code-vector-memory/
    ├── memory_api_server.py
    ├── ClaudeMemory.psm1
    ├── requirements.txt
    ├── scripts/
    ├── chroma_db/ (auto-created)
    └── ...
```

## 🖥️ **Windows PowerShell Integration**

### **Setup Automatic Startup (Recommended)**
```powershell
# Navigate to your installation directory
cd "C:\your\path\to\claude-code-vector-memory"

# Import PowerShell module
Import-Module .\ClaudeMemory.psm1

# Install Windows startup - server will auto-start with Windows
Install-ClaudeMemoryStartup
```

**Note**: After running `Install-ClaudeMemoryStartup`, the Memory API server will automatically start every time Windows boots, ensuring it's always available for Claude Code CLI and Claude Desktop.

### **Manual Server Control**
```powershell
# Start server
Start-ClaudeMemoryAPI

# Check status
Get-ClaudeMemoryStatus

# Search memories
Search-ClaudeMemory "your search terms"
```

## 🖥️ **Claude Desktop Integration (MCP Server)**

### **Overview**
Claude Desktop can access the memory system directly through the Model Context Protocol (MCP) server. This provides native integration without needing the HTTP API.

### **Windows Installation**

1. **Install Python dependencies:**
   ```powershell
   # Install uv package manager (if not already installed)
   pip install uv
   
   # Install chroma-mcp
   pip install chroma-mcp
   ```

2. **Configure Claude Desktop:**
   
   Edit your Claude Desktop config file at:
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```
   
   Add the following to your `mcpServers` section:
   ```json
   {
     "mcpServers": {
       "chroma": {
         "command": "C:\\Users\\[YOUR_USERNAME]\\AppData\\Roaming\\Python\\Python313\\Scripts\\chroma-mcp.exe",
         "args": [
           "--client-type", "persistent",
           "--data-dir", "C:\\your\\path\\to\\claude-code-vector-memory\\chroma_db"
         ]
       }
     }
   }
   ```
   
   **Note**: Replace `[YOUR_USERNAME]` with your Windows username, adjust the Python version (Python313) if needed, and update the path to your installation directory.

3. **Alternative configuration** (if chroma-mcp.exe path differs):
   ```json
   {
     "mcpServers": {
       "chroma": {
         "command": "cmd",
         "args": [
           "/c",
           "python", "-m", "chroma_mcp",
           "--client-type", "persistent",
           "--data-dir", "C:\\your\\path\\to\\claude-code-vector-memory\\chroma_db"
         ]
       }
     }
   }
   ```

### **macOS Installation**

1. **Install Python dependencies:**
   ```bash
   # Install uv package manager (if not already installed)
   pip install uv
   
   # Install chroma-mcp
   pip install chroma-mcp
   ```

2. **Configure Claude Desktop:**
   
   Edit your Claude Desktop config file at:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```
   
   Add the following to your `mcpServers` section:
   ```json
   {
     "mcpServers": {
       "chroma": {
         "command": "uvx",
         "args": [
           "chroma-mcp",
           "--client-type", "persistent",
           "--data-dir", "/your/path/to/claude-code-vector-memory/chroma_db"
         ]
       }
     }
   }
   ```
   
   **Note**: Replace `/your/path/to/claude-code-vector-memory` with your actual installation path.

### **Verify MCP Integration**

After restarting Claude Desktop, Claude should have access to these ChromaDB tools:
- `chroma_list_collections` - View available collections
- `chroma_query_documents` - Search for relevant memories
- `chroma_add_documents` - Add new memories
- `chroma_get_documents` - Retrieve specific memories
- `chroma_get_collection_count` - Check total memories stored

Claude will automatically search the `claude_summaries` collection before starting new tasks.

## 📊 **API Endpoints**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Check system status |
| `/api/search` | POST | Search for memories |
| `/api/add_memory` | POST | Save new memory |
| `/api/memories` | GET | List all memories |
| `/api/memory/{id}` | DELETE | Delete specific memory |
| `/api/reindex` | POST | Rebuild search index |

## 🧪 **Quick Test**

```bash
# Health check
curl http://localhost:8080/api/health

# Search test
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python development", "max_results": 3}'

# Add memory test
curl -X POST http://localhost:8080/api/add_memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test memory from quick start guide",
    "title": "Quick Start Test",
    "source": "claude_code",
    "technologies": ["api", "testing"]
  }'
```

## 📝 **Project Integration - CLAUDE.md / GEMINI.md / AI Assistant Files**

### **For Any AI Assistant Project**
Add this section to your project's instruction file (CLAUDE.md, GEMINI.md, etc.) to enable memory integration:

```markdown
## Memory Integration (MANDATORY) - HTTP API

CRITICAL: Before starting ANY new task, you MUST search through your previous conversations with this user using the Memory API:

### **Memory API Usage**

1. **Extract key terms** from the user's request (technologies, components, concepts)
2. **Call Memory API** to search for relevant past work:
   ```bash
   curl -X POST http://localhost:8080/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "extracted key terms", "max_results": 5, "similarity_threshold": 0.3}'
   ```
3. **Review API response** and identify relevant past work from the `results` array
4. **Present memory recap** to user showing what related work you've done before
5. **Ask user** if they want to build on previous approaches or start fresh

### **Memory API Endpoints**

- **Search**: `POST http://localhost:8080/api/search` - Find relevant memories
- **Add Memory**: `POST http://localhost:8080/api/add_memory` - Save conversation summaries
- **Health Check**: `GET http://localhost:8080/api/health` - Verify API status
- **List All**: `GET http://localhost:8080/api/memories` - Browse all memories

### **Search Request Format**
```json
{
  "query": "react components inventory management",
  "max_results": 3,
  "similarity_threshold": 0.3,
  "source_filter": "claude_code"
}
```

### **Expected Response Format**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "memory_id",
        "title": "Memory Title",
        "similarity": 0.85,
        "relevance_score": 0.92,
        "preview": "Brief preview of the memory content...",
        "metadata": {
          "date": "2025-07-24",
          "complexity": "high",
          "technologies": ["react", "typescript"],
          "source": "claude_code"
        }
      }
    ],
    "total_results": 1,
    "search_time_ms": 45
  }
}
```

### **Memory Presentation**

When presenting found memories:
- Show a brief "memory recap" before beginning work:
  ```
  📚 I found relevant past work (via Memory API):
  1. [Title] - [Date] (Similarity: 85%): We worked on [brief description]
     - Relevant because: [specific connection to current task]
  2. [Title] - [Date] (Similarity: 78%): We implemented [solution]
     - Could apply here for: [specific aspect]
  ```
- Ask: "Would you like me to build on any of these previous approaches, or should we start fresh?"

### **After Task Completion**

After completing significant work, save the conversation summary:
```bash
curl -X POST http://localhost:8080/api/add_memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Summary of the work completed...",
    "title": "Descriptive title of the session",
    "source": "claude_code",
    "technologies": ["react", "typescript", "warehouse"],
    "complexity": "medium",
    "project": "your-project-name"
  }'
```

This is MANDATORY for all tasks, not optional. Users rely on this continuity.

### **Memory Validation**

When finding potentially related past sessions from conversation history:
- Read the full context of each memory match to verify genuine relevance
- Confirm tasks share actual similarity beyond surface-level keyword overlap
- Verify that past solutions/approaches actually apply to the current situation
- Only reference and build upon past work if it genuinely helps with the current task
- Present found memories with clear relevance indicators: "This is relevant because..."
- If uncertain about relevance, ask user: "I found this past work on [topic] - would it be helpful here?"
```

### **Integration Examples**

**To Add to Your Projects:**
1. Copy the Memory Integration section above
2. Paste into your project's CLAUDE.md, GEMINI.md, or AI instruction file
3. Update the `"project": "your-project-name"` field in the add_memory example
4. Ensure the Memory API server is running at localhost:8080

## 🔧 **Customization**

### **Change Server Port**
Edit `config.json`:
```json
{
  "api": {
    "host": "localhost",
    "port": 8080
  }
}
```

### **Custom Database Location**
Edit `config.json`:
```json
{
  "database": {
    "path": "./your-custom-chroma-db",
    "collection_name": "your_collection"
  }
}
```

## 🧪 **Testing Your Installation**

### **Basic API Test**
```bash
python test_api.py
```

### **PowerShell Module Test (Windows)**
```powershell
Import-Module .\ClaudeMemory.psm1
Test-ClaudeMemoryAPI
```

### **Add Your First Memory**
```bash
curl -X POST http://localhost:8080/api/add_memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "My first memory test",
    "title": "Getting Started",
    "source": "manual_test",
    "technologies": ["api", "testing"]
  }'
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Python not found:**
- Install Python 3.9+ from python.org
- Ensure Python is in your PATH

**Port 8080 already in use:**
- Change port in config.json
- Or stop other services using port 8080

**Dependencies fail to install:**
- Upgrade pip: `pip install --upgrade pip`
- Try: `pip install --no-cache-dir -r requirements.txt`

**ChromaDB database errors:**
- Delete `chroma_db/` folder and restart
- Database will be recreated automatically

### **Getting Help**
1. Check the logs in `memory_api.log`
2. Run `python test_api.py` for diagnostics
3. Verify all dependencies: `pip list`

## 🎯 **What's Next**

1. **Test the installation** with `python test_api.py`
2. **Set up automatic startup** (Windows): Run `Install-ClaudeMemoryStartup` - enables server auto-start on Windows boot
3. **Configure MCP** for Claude Desktop (optional)
4. **Add memory integration** to your AI assistant projects
5. **Start using persistent memory** across all your coding sessions!

## 👥 **Credits & Attribution**

**Original Author**: [Christian Byrne](https://github.com/christian-byrne)  
**Original Repository**: https://github.com/christian-byrne/claude-code-vector-memory

This project extends Christian Byrne's original semantic memory system with comprehensive HTTP API functionality, PowerShell integration, Windows startup capabilities, MCP server support, and cross-platform compatibility. The foundational ChromaDB integration, semantic search capabilities, and core memory indexing architecture were developed by the original author.

---

**System Ready!** Your Claude Memory API is now installed and configured for use with any AI assistant.