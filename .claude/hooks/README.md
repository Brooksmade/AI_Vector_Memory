# Claude Code Memory Hooks

These hooks provide automatic memory integration for Claude Code, enabling intelligent assistance without manual API calls.

## 📋 Available Hooks

### Session Management
- **`session-start.sh`** - Initializes memory context when a Claude Code session begins
- **`session-end.sh`** - Saves session summary when the session ends

### Pre-Operation Checks
- **`memory-check.sh`** - Checks memory for past issues before file edits
- **`test-check.sh`** - Warns about past test failures before running tests
- **`git-check.sh`** - Provides git best practices and warns about past conflicts
- **`dependency-check.sh`** - Warns about dependency issues before installations

### Post-Operation Learning
- **`memory-store.sh`** - Stores errors and outcomes after operations
- **`error-recovery.sh`** - Analyzes errors and suggests solutions from memory

## 🚀 Quick Setup

### 1. Copy Hooks to Your Project
```bash
# Create hooks directory in your project
mkdir -p .claude/hooks

# Copy all hook scripts
cp E:\tools\claude-code-vector-memory\hooks\*.sh .claude/hooks/
```

### 2. Configure in `.claude/settings.local.json`
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/session-start.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/session-end.sh",
            "timeout": 5000
          }
        ]
      }
    ],
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
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/test-check.sh",
            "timeout": 3000
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/git-check.sh",
            "timeout": 3000
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/dependency-check.sh",
            "timeout": 3000
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
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/error-recovery.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

## 📝 Hook Details

### session-start.sh
**Trigger**: SessionStart event  
**Purpose**: Initialize memory context for the session  
**Actions**:
- Searches for relevant past work in the current project
- Displays found memories to provide context
- Updates memory API with session information

### session-end.sh
**Trigger**: Stop event (session end)  
**Purpose**: Preserve session knowledge  
**Actions**:
- Extracts key information from session transcript
- Identifies technologies used and errors encountered
- Saves comprehensive session summary to memory

### memory-check.sh
**Trigger**: Before Edit/Write/MultiEdit operations  
**Purpose**: Prevent known issues  
**Actions**:
- Searches memory for past issues with the target file
- Displays warnings if similar errors found (>60% similarity)
- Suggests solutions from past experiences

### test-check.sh
**Trigger**: Before test commands (npm test, jest, pytest)  
**Purpose**: Avoid known test failures  
**Actions**:
- Searches for past test failures
- Identifies problematic test areas
- Suggests checking specific test cases

### git-check.sh
**Trigger**: Before git commands  
**Purpose**: Git operation guidance  
**Actions**:
- For commits: Reminds about message conventions
- For merges: Warns about past conflicts
- Provides best practices from memory

### dependency-check.sh
**Trigger**: Before package installations  
**Purpose**: Prevent dependency issues  
**Actions**:
- Searches for past issues with packages
- Warns about version conflicts
- Suggests checking peer dependencies

### memory-store.sh
**Trigger**: After any operation  
**Purpose**: Store outcomes for learning  
**Actions**:
- Detects errors in tool responses
- Stores error patterns with context
- Builds knowledge base over time

### error-recovery.sh
**Trigger**: After operations with errors  
**Purpose**: Learn and suggest solutions  
**Actions**:
- Categorizes error types
- Searches memory for similar errors and solutions
- Stores new error patterns if unknown
- Suggests recovery strategies

## 🔧 Requirements

- **Memory API Server**: Must be running at `http://localhost:8080`
- **Python**: For JSON parsing in hook scripts
- **Bash**: For script execution (Git Bash on Windows)
- **Claude Code**: With hooks support

## 🎯 Benefits

✅ **Automatic**: No manual memory API calls needed  
✅ **Proactive**: Warns before issues occur  
✅ **Learning**: Stores and learns from errors  
✅ **Context-Aware**: Maintains session context  
✅ **Non-Intrusive**: Only triggers on Claude's actions  

## 🔍 Debugging

To test hooks manually:
```bash
# Test session start
echo '{"session_id": "test", "cwd": "/path/to/project"}' | bash .claude/hooks/session-start.sh

# Test memory check
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/App.tsx"}}' | bash .claude/hooks/memory-check.sh

# Test error recovery
echo '{"tool_name": "Bash", "tool_response": {"error": "TypeError: Cannot read property"}}' | bash .claude/hooks/error-recovery.sh
```

## 📊 Hook Performance

Hooks are configured with appropriate timeouts:
- Session hooks: 5000ms (5 seconds)
- Check hooks: 3000ms (3 seconds)
- Recovery hooks: 5000ms (5 seconds)

These timeouts ensure hooks don't slow down your workflow while providing valuable assistance.

## 🚫 Disabling Hooks

To temporarily disable hooks, add to `.claude/settings.local.json`:
```json
{
  "disableAllHooks": true
}
```

Or disable specific hooks by removing them from the configuration.

## 📈 Metrics

The hooks track:
- Files modified per session
- Errors encountered and resolved
- Technologies used
- Test failures and fixes
- Dependency issues
- Git operation patterns

This data helps Claude provide increasingly better assistance over time.

---

**Note**: These hooks require the Claude Memory API server to be running. See the main [README](../README.md) for setup instructions.