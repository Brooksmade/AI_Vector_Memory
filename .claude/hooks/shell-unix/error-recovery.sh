#!/bin/bash
# Claude Code Hook - Learn from errors and suggest recovery

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract tool response to check for errors
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
TOOL_RESPONSE=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(str(data.get('tool_response', {}))[:1000])")

# Check if there was an error
if [[ "$TOOL_RESPONSE" == *"error"* ]] || [[ "$TOOL_RESPONSE" == *"Error"* ]] || [[ "$TOOL_RESPONSE" == *"failed"* ]]; then
    
    echo "🔍 Analyzing error and searching for solutions..."
    
    # Extract error type
    ERROR_TYPE=$(echo "$TOOL_RESPONSE" | python -c "
import sys
import re

response = sys.stdin.read()

# Common error patterns
if 'TypeError' in response:
    print('TypeError')
elif 'SyntaxError' in response:
    print('SyntaxError')
elif 'Cannot find module' in response or 'Module not found' in response:
    print('ModuleNotFound')
elif 'ENOENT' in response or 'no such file' in response.lower():
    print('FileNotFound')
elif 'Permission denied' in response:
    print('PermissionError')
elif 'null' in response.lower() or 'undefined' in response.lower():
    print('NullReference')
else:
    print('GenericError')
")
    
    # Search for similar errors and their solutions
    MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$ERROR_TYPE error fixed solution resolved\", \"max_results\": 3, \"similarity_threshold\": 0.5}")
    
    # Extract solutions
    SOLUTIONS=$(echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        solutions = []
        for r in results:
            preview = r.get('preview', '').lower()
            if 'fixed' in preview or 'resolved' in preview or 'solution' in preview:
                # Try to extract the fix
                import re
                fix_match = re.search(r'fixed by (.+?)[\.\n]', preview, re.IGNORECASE)
                if fix_match:
                    solutions.append(fix_match.group(1))
                elif 'add' in preview:
                    solutions.append('Check if dependencies or imports are missing')
                elif 'null' in preview or 'undefined' in preview:
                    solutions.append('Add null checks or optional chaining')
        
        if solutions:
            print('💡 Potential solutions from memory:')
            for i, sol in enumerate(solutions[:3], 1):
                print(f'  {i}. {sol}')
            print('')
            print('🔧 Try these solutions or search memory for more details.')
except:
    pass
")
    
    if [[ -n "$SOLUTIONS" ]]; then
        echo "$SOLUTIONS"
    else
        # Store this new error for future learning
        curl -s -X POST http://localhost:8080/api/add_memory \
            -H "Content-Type: application/json" \
            -d "{
                \"title\": \"Error: $ERROR_TYPE in $TOOL_NAME\",
                \"content\": \"Error Type: $ERROR_TYPE\\nTool: $TOOL_NAME\\nResponse: $TOOL_RESPONSE\\nDate: $(date -Iseconds)\\nStatus: Unresolved - needs solution\",
                \"source\": \"claude_code\",
                \"technologies\": [\"error-tracking\"],
                \"complexity\": \"high\",
                \"project\": \"warehouse-inventory-management\"
            }" > /dev/null 2>&1
        
        echo "📝 New error pattern stored for future learning"
    fi
fi

exit 0