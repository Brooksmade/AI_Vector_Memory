# Claude Memory API - Global Setup Guide

This guide shows you how to make the Claude Memory API available from **any project** without manually starting the server each time.

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

# Stop the server
claude-memory-stop
```

### **Features:**
- ✅ Global command-line utilities
- ✅ Desktop shortcuts
- ✅ Environment variables
- ✅ Windows startup integration

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

## 🔧 **After Setup - Usage from Any Project**

Once you've chosen and completed a setup method, the Memory API will be available from **any project directory**:

### **From Claude Code CLI:**
The updated CLAUDE.md will automatically use the API:
```bash
# API calls are made automatically
curl http://localhost:8080/api/search -H "Content-Type: application/json" -d '{"query": "react components"}'
```

### **From Any Terminal:**
```bash
# Health check
curl http://localhost:8080/api/health

# Search
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "python development", "max_results": 3}'
```

### **From Scripts:**
```python
import requests

# The API is always available at localhost:8080
response = requests.get("http://localhost:8080/api/health")
print(response.json())
```

### **From Claude Desktop:**
```javascript
// Use the JavaScript client from any web page
const client = new ClaudeMemoryClient('http://localhost:8080');
const results = await client.search('machine learning');
```

---

## 🧪 **Verify Your Setup**

### **Test 1: Health Check**
```bash
curl http://localhost:8080/api/health
```
**Expected:** `{"success": true, "data": {"status": "healthy"}}`

### **Test 2: Search Test**
```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_results": 1}'
```
**Expected:** `{"success": true, "data": {"results": [...]}}`

### **Test 3: From Different Directory**
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
```

### **Remote Access:**
Update `config.json`:
```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8080
  }
}
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
✅ **Claude Code CLI works seamlessly**  
✅ **Claude Desktop can use the JavaScript client**  
✅ **Shared memory across all interfaces**

**No more manual `python memory_api_server.py` commands needed!**

Choose the method that best fits your workflow and enjoy seamless memory integration across all your Claude interactions! 🚀