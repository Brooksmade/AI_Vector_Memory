#!/bin/bash
# Claude Code Hook - Check memory before git operations

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract command
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
COMMAND=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); inputs=data.get('tool_input', {}); print(inputs.get('command', ''))")

# Check if this is a git command
if [[ "$TOOL_NAME" == "Bash" ]] && [[ "$COMMAND" == *"git "* ]]; then
    
    # For git commits
    if [[ "$COMMAND" == *"git commit"* ]]; then
        echo "📝 Checking memory for commit best practices..."
        
        # Search for commit-related memories
        MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"git commit message convention style\", \"max_results\": 2, \"similarity_threshold\": 0.4}")
        
        # Check for conventions
        echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        for r in results:
            if 'commit' in r.get('preview', '').lower():
                print('💡 Remember: Include clear commit messages and co-author attribution')
                break
except:
    pass
"
    fi
    
    # For git merge
    if [[ "$COMMAND" == *"git merge"* ]] || [[ "$COMMAND" == *"git rebase"* ]]; then
        echo "⚠️ Checking memory for past merge conflicts..."
        
        # Search for merge issues
        MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"git merge conflict rebase error\", \"max_results\": 3, \"similarity_threshold\": 0.5}")
        
        CONFLICTS=$(echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        conflicts = [r for r in results if 'conflict' in r.get('preview', '').lower() or 'merge' in r.get('preview', '').lower()]
        if conflicts:
            print('⚠️ Past merge issues detected:')
            for c in conflicts[:2]:
                print(f'  • {c.get(\"title\", \"Unknown\")}')
            print('💡 Consider checking branch status before merging')
except:
    pass
")
        
        if [[ -n "$CONFLICTS" ]]; then
            echo "$CONFLICTS"
        fi
    fi
fi

exit 0