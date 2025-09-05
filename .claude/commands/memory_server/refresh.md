# /refresh Command

When this command is used, execute the following task:

## Purpose
Manually trigger the session-start hook to refresh memory context

## Task
Run the session-start hook to:
- Check memory server health
- Display memory statistics
- Search for relevant past work
- Show found memories with relevance scores

## Implementation
Execute: `python .claude\hooks\session-start.py`

The hook expects empty JSON input: `{}`