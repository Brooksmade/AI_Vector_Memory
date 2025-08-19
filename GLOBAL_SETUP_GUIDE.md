# Claude Memory API - Global Setup Guide

This guide shows you how to make the Claude Memory API available from **any project** without manually starting the server each time, now with enhanced features including automatic memory engagement, curation tools, and Claude Code hooks integration.

## 🎯 **Choose Your Setup Method**

| Method | Best For | Auto-Start | Complexity | Recommended |
|--------|----------|------------|------------|-------------|
| **PowerShell Module** | Windows users, quick setup | ✅ | Low | ⭐⭐⭐⭐⭐ |
| **Windows Service** | Always-on background service | ✅ | Medium | ⭐⭐⭐⭐ |
| **Global Commands** | Command-line users | ✅ | Low | ⭐⭐⭐⭐ |
| **Docker Container** | Cross-platform, isolated | ✅ | Medium | ⭐⭐⭐ |

---

## 🚀 **Method 1: PowerShell Module (Recommended)**

### **Setup (5 minutes)**

1. **Import the PowerShell module:**
   ```powershell
   Import-Module E:\tools\claude-code-vector-memory\ClaudeMemory.psm1
   ```

2. **Set up auto-startup:**
   ```powershell
   Install-ClaudeMemoryStartup
   ```

3. **Install enhanced features (optional):**
   ```powershell
   # Install curation dependencies
   pip install scikit-learn rich click
   
   # Install active monitoring (optional)
   pip install watchdog
   ```

### **Usage from ANY project:**

```powershell
# Check if running
Get-ClaudeMemoryStatus

# Start if needed  
Start-ClaudeMemoryAPI

# Search from any directory
Search-ClaudeMemory "react components"

# Add memories
Add-ClaudeMemory -Content "Built a new component..." -Title "Component Work"

# Memory curation
Get-ClaudeMemoryHealth
Remove-ClaudeMemoryDuplicates
Archive-ClaudeOldMemories

# Stop when needed
Stop-ClaudeMemoryAPI
```

### **Make it permanent:**
Add to your PowerShell profile:
```powershell
# Add this line to $PROFILE
Import-Module E:\tools\claude-code-vector-memory\ClaudeMemory.psm1
```

---

## 🏗️ **Method 2: Windows Service**

### **Setup (10 minutes)**

1. **Run the service installer:**
   ```bash
   cd E:\tools\claude-code-vector-memory
   python install_service.py
   ```

2. **Set up Task Scheduler:**
   - Open Task Scheduler (`Windows + R`, type `taskschd.msc`)
   - Click "Import Task..."
   - Select: `E:\tools\claude-code-vector-memory\claude_memory_api_task.xml`
   - Click OK

### **Result:**
- ✅ Starts automatically with Windows
- ✅ Runs in background (no visible window)
- ✅ Available from any project
- ✅ Restarts automatically if it crashes
- ✅ Includes all curation and active features

---

## 🌐 **Method 3: Global Commands**

### **Setup (5 minutes)**

1. **Run the global setup script:**
   ```bash
   cd E:\tools\claude-code-vector-memory
   python setup_global_access.py
   ```

2. **Restart your computer** (for PATH changes to take effect)

### **Usage from ANY directory:**

```bash
# Start the server
claude-memory-start

# Check status
claude-memory-status

# Search memories
claude-memory-search "your query here"

# Memory management
python E:\tools\claude-code-vector-memory\memory_manager.py health
python E:\tools\claude-code-vector-memory\memory_manager.py deduplicate --execute
python E:\tools\claude-code-vector-memory\memory_manager.py auto-curate

# Interactive management
python E:\tools\claude-code-vector-memory\memory_manager.py interactive

# Stop the server
claude-memory-stop
```

### **Features:**
- ✅ Global command-line utilities
- ✅ Desktop shortcuts
- ✅ Environment variables
- ✅ Windows startup integration
- ✅ Memory curation tools

---

## 🐳 **Method 4: Docker Container**

### **Setup (Docker required)**

1. **Build and start the container:**
   ```bash
   cd E:\tools\claude-code-vector-memory
   docker-compose up -d
   ```

### **Usage:**
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

### **Features:**
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Isolated environment
- ✅ Auto-restart on failure
- ✅ Easy backup/restore

---

## 🪝 **Claude Code Hooks Integration (NEW)**

### **Automatic Memory Engagement**

Once the server is running, configure Claude Code to automatically use memory:

1. **Add hooks to your project's `.claude/settings.local.json`:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/memory-check.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/memory-store.sh",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
```

2. **Copy hook scripts to your project:**
```bash
# Create hooks directory
mkdir -p .claude/hooks

# Copy hook scripts
cp E:\tools\claude-code-vector-memory\hooks\*.sh .claude/hooks/
```

### **Result:**
- ✅ Automatic memory checks before file edits
- ✅ Automatic error storage for learning
- ✅ Only triggers on Claude's actions, not user edits
- ✅ No manual memory API calls needed

---

## 🧹 **Memory Curation Features (NEW)**

### **API Endpoints for Curation:**

Once the server is running with curation features:

```bash
# Analyze memory health
curl http://localhost:8080/api/curator/health

# Remove duplicates (dry run)
curl -X POST http://localhost:8080/api/curator/deduplicate \
  -H "Content-Type: application/json" \
  -d '{"dry_run": true}'

# Auto-curate memories
curl -X POST http://localhost:8080/api/curator/auto-curate \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'

# Analyze patterns
curl http://localhost:8080/api/curator/analyze
```

### **Memory Manager CLI:**

```bash
# Interactive memory management
python E:\tools\claude-code-vector-memory\memory_manager.py interactive

# Check memory health
python memory_manager.py health

# Remove duplicates
python memory_manager.py deduplicate --execute

# Archive old memories
python memory_manager.py archive --days 90 --execute

# Consolidate memories
python memory_manager.py consolidate <id1> <id2> <id3> --title "Consolidated Memory"

# Auto-curate everything
python memory_manager.py auto-curate --execute

# Search with rich output
python memory_manager.py search

# View statistics
python memory_manager.py stats
```

---

## 📊 **Active Memory Features (NEW)**

If watchdog is installed, the server provides:

### **File Monitoring:**
```bash
# Check active memory status
curl http://localhost:8080/api/active/status

# Get pending decisions/warnings
curl http://localhost:8080/api/active/decisions

# Update context
curl -X POST http://localhost:8080/api/active/context \
  -H "Content-Type: application/json" \
  -d '{"current_task": "Working on React components"}'
```

### **Pre-Action Checks:**
```bash
# Check before action
curl -X POST http://localhost:8080/api/active/check_before_action \
  -H "Content-Type: application/json" \
  -d '{"action": "Edit", "params": {"file_path": "src/App.tsx"}}'
```

---

## 🔧 **After Setup - Usage from Any Project**

Once you've chosen and completed a setup method, the Memory API will be available from **any project directory**:

### **From Claude Code CLI:**
The updated CLAUDE.md will automatically use the API:
```bash
# API calls are made automatically via hooks
# No manual calls needed!
```

### **From Any Terminal:**
```bash
# Health check with curation info
curl http://localhost:8080/api/health

# Enhanced search with similarity scores
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python development", "max_results": 3, "similarity_threshold": 0.5}'

# Memory curation
curl http://localhost:8080/api/curator/health
```

### **From Scripts:**
```python
import requests

# The API is always available at localhost:8080
response = requests.get("http://localhost:8080/api/health")
print(response.json())

# Curator features
health = requests.get("http://localhost:8080/api/curator/health")
print(health.json())
```

### **From Claude Desktop:**
```javascript
// Use the JavaScript client from any web page
const client = new ClaudeMemoryClient('http://localhost:8080');
const results = await client.search('machine learning');

// Check memory health
const health = await client.getCuratorHealth();
```

---

## 🧪 **Verify Your Setup**

### **Test 1: Health Check**
```bash
curl http://localhost:8080/api/health
```
**Expected:** `{"success": true, "data": {"status": "healthy", "database": {...}}}`

### **Test 2: Search Test**
```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_results": 1}'
```
**Expected:** `{"success": true, "data": {"results": [...]}}`

### **Test 3: Curation Health Check**
```bash
curl http://localhost:8080/api/curator/health
```
**Expected:** `{"success": true, "data": {"total_memories": ..., "quality_distribution": {...}}}`

### **Test 4: From Different Directory**
```bash
cd C:\
curl http://localhost:8080/api/health
```
**Expected:** Same healthy response

---

## 🔄 **Managing the Service**

### **Check Status:**
```bash
# PowerShell
Get-ClaudeMemoryStatus

# Command Line
claude-memory-status

# Browser
http://localhost:8080/api/health

# Memory Manager CLI
python memory_manager.py stats
```

### **Start/Stop:**
```bash
# PowerShell
Start-ClaudeMemoryAPI
Stop-ClaudeMemoryAPI

# Command Line
claude-memory-start
claude-memory-stop

# Docker
docker-compose up -d
docker-compose down
```

### **View Logs:**
```bash
# File-based logs
type E:\tools\claude-code-vector-memory\memory_api.log

# Docker logs
docker-compose logs -f

# Memory-specific logs
python memory_manager.py analyze
```

### **Maintenance:**
```bash
# Daily maintenance (recommended)
python memory_manager.py auto-curate --execute

# Weekly health check
python memory_manager.py health

# Monthly archive
python memory_manager.py archive --days 90 --execute
```

---

## 🚨 **Troubleshooting**

### **Port 8080 Already in Use:**
```bash
# Find what's using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### **API Not Responding:**
1. Check if the process is running
2. Verify port 8080 is not blocked by firewall
3. Check logs for error messages
4. Restart the service

### **Curation Features Not Available:**
```bash
# Install required dependencies
pip install scikit-learn rich click

# Verify installation
python -c "import sklearn, rich, click; print('Dependencies OK')"
```

### **Hooks Not Working:**
1. Ensure hooks are in `.claude/hooks/` directory
2. Check hook scripts have execute permissions
3. Verify memory server is running
4. Check Claude Code settings for hook configuration

### **Permission Issues:**
- Run setup scripts as Administrator
- Ensure write permissions to the memory directory
- Check Windows Defender/antivirus exclusions

---

## 💡 **Pro Tips**

### **Multiple Environments:**
```bash
# Development
http://localhost:8080

# Different port for testing
python memory_api_server.py --port 8081

# Production with curation
python memory_api_server.py --enable-curation
```

### **Remote Access:**
Update `config.json`:
```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8080
  },
  "curation": {
    "auto_dedupe_interval": 86400,
    "archive_days": 90
  }
}
```

### **Scheduled Maintenance:**
Set up Task Scheduler for automatic curation:
```xml
<Task>
  <Triggers>
    <CalendarTrigger>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
      <StartBoundary>2025-01-01T03:00:00</StartBoundary>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>E:\tools\claude-code-vector-memory\memory_manager.py auto-curate --execute</Arguments>
    </Exec>
  </Actions>
</Task>
```

### **HTTPS Setup:**
Use the nginx proxy in docker-compose:
```bash
docker-compose --profile with-proxy up -d
```

---

## 🎉 **You're All Set!**

After completing any of these setup methods:

✅ **The Memory API runs automatically**  
✅ **Available from any project directory**  
✅ **Claude Code hooks engage memory automatically**  
✅ **Memory curation keeps database clean**  
✅ **Error patterns are learned and prevented**  
✅ **Rich CLI tools for management**  
✅ **Shared memory across all interfaces**

**No more manual `python memory_api_server.py` commands needed!**

### **Key Features Now Available:**

- 🧠 **Automatic Memory**: Hooks check memory before edits, store errors after
- 🧹 **Auto-Curation**: Removes duplicates, archives old memories, enhances quality
- 📊 **Analytics**: Pattern recognition, error tracking, technology trends
- 🔍 **Smart Search**: Semantic similarity, relevance scoring, context awareness
- 📈 **Health Monitoring**: Quality metrics, recommendations, insights
- 🛠️ **Management Tools**: Interactive CLI, batch operations, visualizations

Choose the method that best fits your workflow and enjoy seamless memory integration across all your Claude interactions! 🚀