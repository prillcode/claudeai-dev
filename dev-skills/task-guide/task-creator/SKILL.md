---
name: task-creator
description: Orchestrates the task development workflow for simple bug fixes and maintenance work. This skill should be used when the user requests to fix bugs, make small updates, or perform straightforward maintenance tasks. Triggers on simplicity signals (single-file changes, clear bugs, small enhancements) combined with task-related language ("fix", "bug", "tweak", "update", "patch").
---

# Task Creator

## Overview

Task Creator orchestrates a lightweight workflow for simple bug fixes and maintenance tasks. Use this skill for straightforward work that doesn't require extensive planning or architectural decisions.

## When to Use Task Creator

Use this skill when:
- User requests to "fix", "patch", or "resolve" a bug
- Task involves single-file or simple multi-file changes
- Requirements are clear and straightforward
- No architectural decisions needed
- Maintenance work or small enhancements

**Do not use** for complex features, multi-component systems, or work requiring extensive planning (use feature-creator instead).

## Workflow

Task Creator follows a streamlined two-phase workflow:

### Phase 1: Specification (Quick)
**Tool: spec-task skill**

Create a lightweight task specification:

1. **Assume Clarity**: For straightforward tasks, skip extensive clarification
2. **Generate Task Spec**: Create a simplified specification with:
   - Simplified XML structure (objective, requirements, verification only)
   - Clear, focused instructions
   - Basic verification steps
3. **Save Specification**: Store in `./tasks/` directory
   - Format: `001-task-name.md`, `002-another-task.md`, etc.
   - Numbered sequentially for tracking
   - Always single task (no parallel/sequential logic)

### Phase 2: Implementation (Direct)
**Tool: dev-task skill**

Execute the task specification in a fresh context:

1. **Load Task Spec**: Read the specification from `./tasks/`
2. **Execute Directly**: Delegate to sub-agent with the specification
3. **Single Execution**: Tasks are always executed individually (no parallel/sequential)
4. **Archive on Completion**: Move completed spec to `./tasks/completed/`

## Key Differences from Feature Creator

| Aspect | Task Creator | Feature Creator |
|--------|--------------|-----------------|
| **Use Case** | Bug fixes, small updates | New features, architecture |
| **Complexity** | Single-file, straightforward | Multi-file, complex |
| **XML Structure** | Simplified (3 tags) | Full (7+ tags) |
| **Clarification** | Minimal/skip | Interactive questions |
| **Execution** | Always single | Parallel/sequential support |
| **Planning Depth** | Light | Comprehensive |

## Benefits of This Approach

**Speed and Simplicity:**
- Minimal overhead for straightforward work
- Skip unnecessary planning for clear tasks
- Quick turnaround from request to implementation

**Separation of Concerns:**
- Main context stays clean
- Implementation in fresh context
- No clutter from simple fixes

**Tracking:**
- All tasks documented in `./tasks/`
- Completed work archived to `./tasks/completed/`
- Easy audit trail of maintenance work

## Related Skills

- **spec-task**: Creates the lightweight task specification
- **dev-task**: Executes the task specification
- **feature-creator**: For complex features (not simple tasks)

## Example Usage Pattern

```
User: "Fix the bug where the login button doesn't work on mobile"

1. task-creator provides workflow guidance
2. Claude invokes spec-task to:
   - Create simple specification with objective, requirements, verification
   - Save to ./tasks/001-fix-mobile-login-button.md
3. Claude invokes dev-task to:
   - Load the specification
   - Execute in clean sub-agent context
   - Implement the fix
   - Archive to ./tasks/completed/
```

## Task Examples

**Good for task-creator:**
- "Fix the broken link on the homepage"
- "Update the copyright year in the footer"
- "Remove deprecated API calls from auth service"
- "Fix typo in error message"
- "Change background color from blue to green"
- "Update dependency version for security patch"

**Not for task-creator (use feature-creator):**
- "Add user authentication with OAuth"
- "Implement real-time notifications system"
- "Refactor the entire data layer"
- "Build a new dashboard with charts"

## Notes

- This skill provides **guidance and structure**, not full automation
- Claude will invoke spec-task and dev-task directly when appropriate
- Lightweight approach optimized for speed and simplicity
- User maintains control while benefiting from organized workflow
