#!/bin/bash
# Claude Code Hook - Check memory before running tests

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract tool name and command
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
COMMAND=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); inputs=data.get('tool_input', {}); print(inputs.get('command', ''))")

# Check if this is a test command
if [[ "$TOOL_NAME" == "Bash" ]] && ([[ "$COMMAND" == *"npm test"* ]] || [[ "$COMMAND" == *"npm run test"* ]] || [[ "$COMMAND" == *"jest"* ]] || [[ "$COMMAND" == *"pytest"* ]]); then
    
    echo "🧪 Checking memory for past test failures..."
    
    # Search for test-related issues
    MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"test failed error jest pytest npm\", \"max_results\": 3, \"similarity_threshold\": 0.5}")
    
    # Check for past test failures
    WARNINGS=$(echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        test_issues = [r for r in results if 'test' in r.get('preview', '').lower() and 'fail' in r.get('preview', '').lower()]
        if test_issues:
            print('⚠️ Found past test issues:')
            for issue in test_issues[:2]:
                print(f'  • {issue.get(\"title\", \"Unknown\")} ({issue.get(\"date\", \"Unknown\")})')
                # Extract specific test that failed if possible
                preview = issue.get('preview', '')
                if 'FAIL' in preview or 'failed' in preview:
                    print(f'    Issue: {preview[:150]}...')
            print('')
            print('💡 Consider checking these specific test areas before running.')
except:
    pass
")
    
    if [[ -n "$WARNINGS" ]]; then
        echo "$WARNINGS"
    fi
fi

exit 0