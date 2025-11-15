# Development Skills

A collection of Claude Code skills for structured software development workflows. These skills provide guidance for both complex feature development and lightweight task management.

## Overview

This directory contains two complementary skill systems:

- **feature-guide/** - For complex, multi-file feature development
- **task-guide/** - For lightweight bug fixes and maintenance tasks

Each system provides a complete workflow from specification to implementation, with the appropriate level of structure and automation for the task at hand.

## Skill Collections

### [feature-guide/](feature-guide/)

For complex development work requiring architectural decisions, multiple files, or significant refactoring.

**Skills included:**
- **feature-creator** - Orchestrator that provides workflow guidance for the spec→dev process
- **spec-feature** - Creates structured feature specifications with interactive clarification
- **dev-feature** - Executes feature specifications with support for parallel/sequential workflows

**Features:**
- Complete XML specification structure (objective, context, requirements, implementation, verification, success criteria, avoid)
- Interactive clarifying questions for complex requirements
- Support for single, multiple, parallel, or sequential prompt execution
- Saves specifications to `./features/` directory
- Archives completed features to `./features/completed/`

**When to use:**
- Building new features or capabilities
- Making architectural changes
- Multi-file refactoring
- Tasks requiring planning and coordination

### [task-guide/](task-guide/)

For straightforward development work like bug fixes, small updates, or maintenance tasks.

**Skills included:**
- **task-creator** - Orchestrator that provides workflow guidance for simple tasks
- **spec-task** - Creates lightweight task specifications
- **dev-task** - Executes task specifications with simplified verification

**Features:**
- Simplified XML structure (objective, requirements, verification only)
- No clarifying questions (assumes task clarity)
- Single-prompt execution model
- Saves specifications to `./tasks/` directory
- Archives completed tasks to `./tasks/completed/`

**When to use:**
- Fixing bugs
- Making small tweaks or updates
- Single-file modifications
- Straightforward maintenance tasks

## Key Differences

| Aspect | Feature-Guide | Task-Guide |
|--------|---------------|------------|
| **Complexity** | Multi-file, architectural changes | Single-file, straightforward fixes |
| **XML Structure** | Full (7+ tags) | Simplified (3 tags) |
| **Clarification** | Interactive questions | Skip questions |
| **Execution** | Parallel/Sequential support | Single-prompt only |
| **Storage** | `./features/` → `./features/completed/` | `./tasks/` → `./tasks/completed/` |
| **Triggers** | Complex tasks + "implement", "build", "feature" | Simple tasks + "fix", "bug", "tweak", "update" |

## Workflow Approach

Both skill systems follow a similar two-phase workflow:

1. **Specification Phase** - Define what needs to be done
   - `spec-feature` for complex features
   - `spec-task` for simple tasks

2. **Development Phase** - Execute the specification
   - `dev-feature` for features
   - `dev-task` for tasks

The orchestrator skills (feature-creator, task-creator) provide guidance on when and how to use each phase, but Claude can also invoke the spec/dev skills directly as needed.

## Usage

These skills are designed to work proactively with Claude Code:

- When you request complex feature work, Claude may use the feature-guide skills
- When you request bug fixes or simple updates, Claude may use the task-guide skills
- You can also explicitly reference the skills or workflows in your prompts

## Directory Structure

```
dev-skills/
├── README.md                    # This document
├── PLAN.md                      # Implementation plan and design notes
├── feature-guide/
│   ├── feature-creator/         # Workflow orchestrator
│   ├── spec-feature/            # Feature specification creator
│   └── dev-feature/             # Feature implementation executor
└── task-guide/
    ├── task-creator/            # Workflow orchestrator
    ├── spec-task/               # Task specification creator
    └── dev-task/                # Task implementation executor
```

## See Also

- [PLAN.md](PLAN.md) - Detailed implementation plan and design notes
- [../workflow-skills/](../workflow-skills/) - Related workflow automation skills
