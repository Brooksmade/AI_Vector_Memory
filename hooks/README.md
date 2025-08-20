# Claude Memory System - Hooks Documentation

This directory contains hook scripts that integrate the memory system with Claude Code CLI. Hooks automatically engage memory features during your Claude interactions.

## 📁 Hook Types Available

### Python Hooks (Recommended for Windows)
**Location:** `python-windows/`
- **Best for:** Windows users
- **Requirements:** Python 3.8+
- **Advantages:** 
  - Better error handling
  - Cross-platform compatible
  - No JSON escaping issues
  - Rich output formatting

### Shell Hooks (For Mac/Linux)
**Location:** `shell-unix/` (Currently missing - needs to be added)
- **Best for:** Mac/Linux users
- **Requirements:** Bash, curl
- **Advantages:**
  - Native to Unix systems
  - Lightweight
  - No Python required

## 🎯 Which Hooks Should You Use?

| Your OS | Recommended | Alternative | Why |
|---------|-------------|-------------|-----|
| **Windows 10/11** | Python hooks (`.py`) | PowerShell (`.ps1`) | Python handles Windows paths and encoding better |
| **macOS** | Shell hooks (`.sh`) | Python hooks (`.py`) | Shell is native, but Python works too |
| **Linux** | Shell hooks (`.sh`) | Python hooks (`.py`) | Shell is native, but Python works too |

## 📋 Hook Files Explained

### Core Hooks (Run Automatically)

| Hook | Purpose | When It Runs |
|------|---------|--------------|
| `session-start` | Checks memory health, shows recent work | When Claude Code starts |
| `memory-check` | Searches for past issues with files | Before Edit/Write/MultiEdit operations |
| `memory-store` | Stores errors for future learning | After any tool operation with errors |
| `error-recovery` | Analyzes errors and suggests fixes | After errors occur |
| `session-end` | Saves session summary | When Claude Code stops |

### Specialized Hooks

| Hook | Purpose | When It Runs |
|------|---------|--------------|
| `git-check` | Warns about past merge conflicts | Before git operations |
| `dependency-check` | Checks for past package issues | Before npm/pip install |
| `test-check` | Identifies past test failures | Before running tests |

## 🔧 Installation Instructions

### For Windows Users

1. **Copy Python hooks to your project:**
```batch
REM In your project directory:
mkdir .claude\hooks
copy [MEMORY_PATH]\hooks\python-windows\*.py .claude\hooks\
copy [MEMORY_PATH]\hooks\python-windows\*.cmd .claude\hooks\
copy [MEMORY_PATH]\hooks\python-windows\*.ps1 .claude\hooks\
```

2. **Configure `.claude/settings.local.json`:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/session-start.py",
        "timeout": 5000
      }]
    }],
    "PreToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/memory-check.py",
        "timeout": 5000
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python .claude/hooks/memory-store.py",
        "timeout": 3000
      }]
    }]
  }
}
```

### For Mac/Linux Users

1. **Copy shell hooks to your project:**
```bash
# In your project directory:
mkdir -p .claude/hooks
cp [MEMORY_PATH]/hooks/shell-unix/*.sh .claude/hooks/
chmod +x .claude/hooks/*.sh
```

2. **Configure `.claude/settings.local.json`:**
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/session-start.sh",
        "timeout": 5000
      }]
    }],
    "PreToolUse": [{
      "matcher": "Edit|Write|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/memory-check.sh",
        "timeout": 5000
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/memory-store.sh",
        "timeout": 3000
      }]
    }]
  }
}
```

## ⚠️ Common Issues & Solutions

### Windows Issues

**Problem:** "python: command not found"
- **Solution:** Use full path: `"command": "C:\\Python311\\python.exe .claude/hooks/session-start.py"`

**Problem:** Hooks not triggering
- **Solution:** Check Windows Defender/antivirus isn't blocking scripts

**Problem:** JSON parsing errors
- **Solution:** Use Python hooks instead of shell scripts - they handle JSON better

### Mac/Linux Issues

**Problem:** "Permission denied"
- **Solution:** Make scripts executable: `chmod +x .claude/hooks/*.sh`

**Problem:** "curl: command not found"
- **Solution:** Install curl: `sudo apt-get install curl` (Linux) or `brew install curl` (Mac)

## 🧪 Testing Your Hooks

### Test Individual Hooks

**Windows (Python):**
```batch
REM Test session start
python .claude\hooks\session-start.py

REM Test with mock data
echo {"tool_name": "Edit", "tool_input": {"file_path": "test.py"}} | python .claude\hooks\memory-check.py
```

**Mac/Linux (Shell):**
```bash
# Test session start
bash .claude/hooks/session-start.sh

# Test with mock data
echo '{"tool_name": "Edit", "tool_input": {"file_path": "test.py"}}' | bash .claude/hooks/memory-check.sh
```

### Verify Memory Server Connection

All platforms:
```bash
curl http://localhost:8080/api/health
```

## 📊 Hook Data Flow

```
Claude Code Action
        ↓
    Hook Triggered
        ↓
    Read Tool Input (JSON)
        ↓
    Query Memory API
        ↓
    Process Response
        ↓
    Display Warnings/Info
        ↓
    Continue Operation
```

## 🔍 Debugging Hooks

### Enable Verbose Output

Add debug prints to see what's happening:

**Python hooks:**
```python
import json
import sys

# Add at start of script
DEBUG = True

if DEBUG:
    print(f"[DEBUG] Script: {__file__}", file=sys.stderr)
    print(f"[DEBUG] Input: {sys.stdin.read()}", file=sys.stderr)
```

**Shell hooks:**
```bash
# Add at start of script
set -x  # Enable debug mode
```

### Check Logs

- **Memory API logs:** `[MEMORY_PATH]/memory_api.log`
- **Claude Code logs:** Check Claude's output
- **Test manually:** Run hooks directly from terminal

## 💡 Best Practices

1. **Always test hooks** after installation
2. **Keep memory server running** - hooks won't work without it
3. **Use appropriate hooks** for your OS
4. **Monitor memory growth** - run curation periodically
5. **Back up memories** - the `chroma_db/` folder contains your data

## 🚀 Advanced Configuration

### Custom Timeout Values

Adjust timeout based on your system speed:
```json
{
  "timeout": 10000  // 10 seconds for slower systems
}
```

### Conditional Hooks

Only run on specific file types:
```json
{
  "matcher": "Edit",
  "filter": "*.py",  // Only Python files
  "hooks": [...]
}
```

### Environment Variables

Set project-specific memory settings:
```bash
export CLAUDE_PROJECT_ROOT=/path/to/project
export MEMORY_API_URL=http://localhost:8080
```

## 📚 Additional Resources

- Main documentation: `../README.md`
- API documentation: `../docs/API.md`
- Troubleshooting: `../docs/TROUBLESHOOTING.md`
- Memory server setup: `../CLAUDE.md`

---

**Remember:** Hooks are the bridge between Claude Code and your memory system. They work silently in the background to make Claude remember your past work and learn from your errors.