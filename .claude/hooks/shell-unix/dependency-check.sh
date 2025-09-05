#!/bin/bash
# Claude Code Hook - Check memory before installing dependencies

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract command
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
COMMAND=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); inputs=data.get('tool_input', {}); print(inputs.get('command', ''))")

# Check if this is a dependency installation command
if [[ "$TOOL_NAME" == "Bash" ]] && ([[ "$COMMAND" == *"npm install"* ]] || [[ "$COMMAND" == *"pip install"* ]] || [[ "$COMMAND" == *"yarn add"* ]]); then
    
    echo "📦 Checking memory for dependency issues..."
    
    # Extract package name if possible
    PACKAGE=$(echo "$COMMAND" | python -c "
import sys
import re
command = sys.stdin.read()
# Try to extract package name
match = re.search(r'install\s+([a-z0-9\-_@/]+)', command, re.IGNORECASE)
if match:
    print(match.group(1))
")
    
    # Search for past issues with this package or dependencies in general
    SEARCH_QUERY="dependency install error"
    if [[ -n "$PACKAGE" ]]; then
        SEARCH_QUERY="$PACKAGE dependency install error version conflict"
    fi
    
    MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$SEARCH_QUERY\", \"max_results\": 3, \"similarity_threshold\": 0.4}")
    
    # Check for warnings
    WARNINGS=$(echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        dep_issues = []
        for r in results:
            preview = r.get('preview', '').lower()
            if 'version' in preview or 'conflict' in preview or 'peer' in preview:
                dep_issues.append(r)
        
        if dep_issues:
            print('⚠️ Found past dependency issues:')
            for issue in dep_issues[:2]:
                print(f'  • {issue.get(\"title\", \"Unknown\")}')
                # Check for specific version issues
                preview = issue.get('preview', '')
                if 'version' in preview.lower():
                    print('    💡 Check package.json for version conflicts')
                if 'peer' in preview.lower():
                    print('    💡 Check peer dependency requirements')
except:
    pass
")
    
    if [[ -n "$WARNINGS" ]]; then
        echo "$WARNINGS"
        echo ""
        echo "💡 Consider checking package versions before installing"
    fi
fi

exit 0