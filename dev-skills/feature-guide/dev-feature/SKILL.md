---
name: dev-feature
description: Execute feature specifications from ./.dev-docs/features/ directory in fresh sub-agent contexts. This skill should be used when implementing features after specifications have been created by spec-feature. Supports single feature execution, parallel execution of multiple independent features, and sequential execution of dependent features. Archives completed specifications to ./.dev-docs/features/completed/.
---

# Feature Development Executor

## Overview

Executes feature specifications from `./.dev-docs/features/` as delegated sub-tasks with fresh context. This keeps the main conversation clean while implementation happens in focused, isolated contexts.

## When to Use

Use this skill when:
- Feature specifications have been created and are ready to implement
- User wants to execute one or more saved feature specifications
- Need to run multiple features in parallel or sequential order
- Implementing features with clean, fresh context

## Execution Modes

### Single Feature
Execute one feature specification in a fresh sub-agent context.

### Parallel Execution
Execute multiple independent features simultaneously. Use when:
- Features modify different files (no shared files)
- Features are independent components or modules
- No dependencies between features
- Maximum efficiency is desired

### Sequential Execution
Execute features one at a time in order. Use when:
- Features have dependencies (one must complete before next starts)
- Features modify shared files
- Data flows from one feature to the next
- Order matters for correctness

## How to Invoke

**Single feature:**
- By number: "Execute feature 005" or "Run feature 5"
- By name: "Execute user-authentication" or "Run dashboard feature"
- Most recent: "Execute the latest feature" (finds newest in ./.dev-docs/features/)

**Multiple features:**
- Parallel: "Execute features 005, 006, and 007 in parallel"
- Sequential: "Execute features 005, 006, and 007 sequentially"
- Default: If execution strategy not specified, defaults to sequential for safety

## Execution Process

### Step 1: Resolve Feature Files

For each requested feature:

**By number:**
- Match zero-padded number (e.g., "5" matches "005-*.md", "42" matches "042-*.md")
- Search in ./.dev-docs/features/ directory

**By name:**
- Find files containing the name string in filename
- Example: "auth" matches "005-user-authentication.md"

**Most recent:**
- Use `ls -t ./.dev-docs/features/*.md | head -1` to find latest

**Matching rules:**
- Exactly one match → Use that file
- Multiple matches → List options and ask user to choose
- No matches → Report error and list available features

### Step 2: Execute Feature(s)

#### Single Feature Execution

1. Read the complete contents of the feature specification file
2. Delegate to sub-agent using Task tool:
   - Set `subagent_type="general-purpose"`
   - Set `description` to brief feature summary
   - Set `prompt` to the full specification content
3. Wait for sub-agent to complete implementation
4. Archive specification to `./.dev-docs/features/completed/` with metadata
5. Return results to user

**Archiving format:**
```
./.dev-docs/features/completed/[number]-[name].md

Add metadata at top of archived file:
---
executed: [timestamp]
status: completed
---
[original specification content]
```

#### Parallel Execution

**Critical: All Task tool calls MUST be in a SINGLE MESSAGE for parallel execution**

1. Read all requested feature specification files
2. Spawn ALL Task tools simultaneously in one message:
   ```
   Task tool for feature 005
   Task tool for feature 006
   Task tool for feature 007
   (All in one message with multiple tool calls)
   ```
3. Wait for ALL sub-agents to complete
4. Archive all specifications to ./.dev-docs/features/completed/
5. Return consolidated results showing what each feature accomplished

#### Sequential Execution

1. Read first feature specification file
2. Spawn Task tool for first feature
3. Wait for completion
4. Archive first feature specification
5. Read second feature specification file
6. Spawn Task tool for second feature
7. Wait for completion
8. Archive second feature specification
9. Repeat for remaining features in order
10. Return consolidated results showing progression through features

### Step 3: Report Results

Present clear summary of execution:

**Single feature:**
```
✓ Executed: ./.dev-docs/features/005-implement-dashboard.md
✓ Archived to: ./.dev-docs/features/completed/005-implement-dashboard.md

Results:
[Summary of what was implemented]
```

**Parallel execution:**
```
✓ Executed in PARALLEL:
  - ./.dev-docs/features/005-implement-auth.md
  - ./.dev-docs/features/006-implement-api.md
  - ./.dev-docs/features/007-implement-ui.md

✓ All archived to ./.dev-docs/features/completed/

Results:
Feature 005 (Auth): [summary]
Feature 006 (API): [summary]
Feature 007 (UI): [summary]
```

**Sequential execution:**
```
✓ Executed SEQUENTIALLY:
  1. ./.dev-docs/features/005-setup-database.md → Success
  2. ./.dev-docs/features/006-create-migrations.md → Success
  3. ./.dev-docs/features/007-seed-data.md → Success

✓ All archived to ./.dev-docs/features/completed/

Results:
Step 1 (Database): [summary]
Step 2 (Migrations): [summary]
Step 3 (Seed Data): [summary]
```

## Context Strategy

By delegating to sub-agents, the implementation work happens in fresh, focused context while the main conversation stays clean for:
- Requirements gathering
- Specification refinement
- Progress tracking
- Iteration and feedback

This separation improves implementation quality and maintains conversation clarity.

## Error Handling

**If a feature fails during execution:**
- Single feature: Report failure with error details, do not archive
- Parallel execution: Report which features succeeded/failed, archive only successful ones
- Sequential execution: Stop immediately, do not execute remaining features, report failure point

**If feature file not found:**
- List available features in ./.dev-docs/features/
- Ask user to clarify which feature to execute

**If multiple matches found:**
- List all matching feature files
- Ask user to specify which one (by full number or more specific name)

## Directory Setup

**Before execution:**
1. Verify ./.dev-docs/features/ directory exists
2. Verify requested feature files exist
3. Ensure ./.dev-docs/features/completed/ directory exists (create if needed)

**Archive location:**
- Create ./.dev-docs/features/completed/ if it doesn't exist: `mkdir -p ./.dev-docs/features/completed/`

## Critical Notes

- **Parallel execution**: ALL Task tool calls MUST be in a single message
- **Sequential execution**: Wait for each Task to complete before starting next
- **Archive timing**: Only archive after successful completion
- **Failure handling**: Stop sequential execution on first failure
- **Results clarity**: Provide consolidated results for multiple feature execution
- **Fresh context**: Each sub-agent gets clean context with only the specification

## Related Skills

- **feature-creator**: Orchestrator for the overall feature development workflow
- **spec-feature**: Creates the feature specifications that this skill executes
- **task-creator**: For simpler tasks (not complex features)
