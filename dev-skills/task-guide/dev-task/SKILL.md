---
name: dev-task
description: Execute task specifications from ./tasks/ directory in fresh sub-agent contexts. This skill should be used when implementing simple tasks after specifications have been created by spec-task. Always executes single tasks (no parallel/sequential logic). Archives completed specifications to ./tasks/completed/. Optimized for speed and simplicity.
---

# Task Development Executor

## Overview

Executes task specifications from `./tasks/` as delegated sub-tasks with fresh context. Designed for simple, single-task execution with minimal overhead.

## When to Use

Use this skill when:
- Task specifications have been created and are ready to implement
- User wants to execute a saved task specification
- Implementing simple bug fixes or maintenance tasks
- Need clean, fresh context for task execution

**Do not use** for complex features or parallel execution (use dev-feature instead).

## Execution Mode

### Single Task Only

This skill always executes one task at a time:
- No parallel execution
- No sequential execution of multiple tasks
- One specification → one sub-agent → one implementation

**Why single-task only?**
- Tasks are simple and quick by definition
- No need for complex orchestration
- Reduces overhead and complexity
- Aligns with the lightweight task philosophy

## How to Invoke

**By number:**
- "Execute task 005"
- "Run task 5"

**By name:**
- "Execute fix-mobile-login"
- "Run the login button fix"

**Most recent:**
- "Execute the latest task"
- "Run the most recent task spec"

## Execution Process

### Step 1: Resolve Task File

Locate the requested task specification:

**By number:**
- Match zero-padded number (e.g., "5" matches "005-*.md")
- Search in ./tasks/ directory

**By name:**
- Find files containing the name string
- Example: "login" matches "005-fix-mobile-login.md"

**Most recent:**
- Use `ls -t ./tasks/*.md | head -1` to find latest

**Matching rules:**
- Exactly one match → Use that file
- Multiple matches → List options, ask user to choose
- No matches → Report error, list available tasks

### Step 2: Execute Task

1. **Read specification**: Load complete contents of the task file
2. **Delegate to sub-agent**: Use Task tool with:
   - `subagent_type="general-purpose"`
   - `description`: Brief task summary (e.g., "Fix mobile login button")
   - `prompt`: Full specification content
3. **Wait for completion**: Sub-agent implements the task
4. **Archive specification**: Move to `./tasks/completed/` with metadata
5. **Report results**: Summarize what was accomplished

**Archiving format:**
```
./tasks/completed/[number]-[name].md

Add metadata at top:
---
executed: [timestamp]
status: completed
---
[original specification content]
```

### Step 3: Report Results

Present clear summary:

```
✓ Executed: ./tasks/005-fix-mobile-login.md
✓ Archived to: ./tasks/completed/005-fix-mobile-login.md

Results:
[Summary of what was fixed or implemented]
```

## Context Strategy

By delegating to a sub-agent, implementation happens in fresh, focused context while the main conversation stays clean for:
- Task planning
- Progress tracking
- Quick iteration
- Multiple task management

## Error Handling

**If task fails during execution:**
- Report failure with error details
- Do not archive the specification
- User can review spec and retry

**If task file not found:**
- List available tasks in ./tasks/
- Ask user to clarify which task to execute

**If multiple matches found:**
- List all matching task files
- Ask user to specify which one

**If ./tasks/ directory doesn't exist:**
- Report that no tasks have been created yet
- Suggest using spec-task to create a task specification first

## Directory Setup

**Before execution:**
1. Verify ./tasks/ directory exists
2. Verify requested task file exists
3. Ensure ./tasks/completed/ directory exists (create if needed)

**Archive location:**
- Create ./tasks/completed/ if needed: `mkdir -p ./tasks/completed/`

## Example Workflow

```
User: "Execute the login button fix"

1. Search ./tasks/ for files containing "login button"
2. Find: ./tasks/005-fix-mobile-login-button.md
3. Read specification contents
4. Spawn sub-agent with specification
5. Sub-agent implements fix in clean context
6. Archive to ./tasks/completed/005-fix-mobile-login-button.md
7. Report: "Fixed z-index issue causing button to be unclickable on mobile"
```

## Key Differences from dev-feature

| Aspect | dev-task | dev-feature |
|--------|----------|-------------|
| **Execution** | Single task only | Supports parallel/sequential |
| **Complexity** | Simple, lightweight | Full-featured |
| **Directory** | ./tasks/ | ./features/ |
| **Archive** | ./tasks/completed/ | ./features/completed/ |
| **Use Case** | Bug fixes, maintenance | Complex features |

## Critical Notes

- **Always single-task**: Never batch or parallelize task execution
- **Fresh context**: Each sub-agent gets clean context with only the specification
- **Archive on success**: Only move to completed/ after successful execution
- **Simple reporting**: Focus on what was fixed, keep it concise
- **Fast execution**: Minimal overhead, optimized for speed

## Related Skills

- **task-creator**: Orchestrator for the overall task workflow
- **spec-task**: Creates the task specifications that this skill executes
- **dev-feature**: For complex features (not simple tasks)
