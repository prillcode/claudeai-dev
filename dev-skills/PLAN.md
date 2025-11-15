# Workflow Skills Creation Plan

## Overview

This directory contains two workflow skill systems for Claude Code:
- **feature-guide**: For complex, multi-file feature development
- **task-guide**: For lightweight bug fixes and maintenance tasks

## Directory Structure

```
dev-skills/
├── PLAN.md                      # This document
├── feature-guide/
│   ├── feature-creator/         # Orchestrator skill
│   ├── spec-feature/            # Based on create-prompt.md
│   └── dev-feature/             # Based on run-prompt.md
└── task-guide/
    ├── task-creator/            # Orchestrator skill
    ├── spec-task/               # Lightweight spec (inspired by create-prompt.md)
    └── dev-task/                # Lightweight dev (inspired by run-prompt.md)
```

## Implementation Steps

### 1. Setup Root Structure
- ✅ Create `dev-skills/` directory in cc-prompts
- ✅ Save this plan as `dev-skills/PLAN.md`
- ✅ Create `feature-guide/` and `task-guide/` subdirectories

### 2. Initialize All 6 Skills
- Use skill-creator's `init_skill.py` to scaffold each skill
- This creates SKILL.md templates with proper frontmatter

### 3. Feature-Guide Skills

#### feature-creator (orchestrator)
- **Triggers**: Complex tasks + feature keywords ("implement", "build", "feature")
- **Purpose**: Provides workflow guidance for spec→dev process
- **References**: spec-feature and dev-feature skills
- **No bundled resources needed**

#### spec-feature
- **Based on**: create-prompt.md (full logic)
- **XML Structure**: Complete - objective, context, requirements, implementation, verification, success_criteria, avoid
- **Features**:
  - Interactive clarifying questions
  - Supports single/multiple/parallel/sequential prompts
  - Saves to `./features/` (format: 001-feature-name.md)

#### dev-feature
- **Based on**: run-prompt.md (full logic)
- **Features**:
  - Reads from `./features/` directory
  - Supports parallel/sequential execution flags
  - Archives to `./features/completed/`
  - Flexible prompt resolution (by number or name)

### 4. Task-Guide Skills

#### task-creator (orchestrator)
- **Triggers**: Simple tasks + task keywords ("fix", "bug", "tweak", "update")
- **Purpose**: Lightweight workflow guidance
- **References**: spec-task and dev-task skills

#### spec-task
- **Inspired by**: create-prompt.md (lightweight version)
- **XML Structure**: Simplified - objective, requirements, verification only
- **Features**:
  - No clarifying questions (assumes clarity)
  - Always single-prompt
  - Saves to `./tasks/` (format: 001-task-name.md)

#### dev-task
- **Inspired by**: run-prompt.md (lightweight version)
- **Features**:
  - Single-prompt execution only
  - Archives to `./tasks/completed/`
  - Simpler verification steps

## Key Differences: Feature vs Task

| Aspect | Feature-Guide | Task-Guide |
|--------|---------------|------------|
| **Complexity** | Multi-file, architectural changes | Single-file, straightforward fixes |
| **XML Structure** | Full (7+ tags) | Simplified (3 tags) |
| **Clarification** | Interactive questions | Skip questions |
| **Execution** | Parallel/Sequential support | Single-prompt only |
| **Storage** | `./features/` → `./features/completed/` | `./tasks/` → `./tasks/completed/` |
| **Triggers** | Complexity + "implement", "build", "feature" | Simplicity + "fix", "bug", "tweak", "update" |

## Orchestrator Behavior

Both orchestrators provide **guidance/structure** rather than automation:
- They describe the workflow framework
- They reference the appropriate spec/dev skills
- Claude calls spec-* and dev-* skills directly when needed
- More flexible, less automated approach

## Package & Migration

### 5. Package All Skills
```bash
scripts/package_skill.py dev-skills/feature-guide/feature-creator
scripts/package_skill.py dev-skills/feature-guide/spec-feature
scripts/package_skill.py dev-skills/feature-guide/dev-feature
scripts/package_skill.py dev-skills/task-guide/task-creator
scripts/package_skill.py dev-skills/task-guide/spec-task
scripts/package_skill.py dev-skills/task-guide/dev-task
```

### 6. Move to Final Location
```bash
mv dev-skills ~/dev/claude-skills/workflow-skills/
```

## Testing

### Test Feature-Guide
- Request a complex multi-file feature
- Verify feature-creator triggers appropriately
- Check `./features/` directory creation
- Confirm archiving to `./features/completed/`

### Test Task-Guide
- Request a simple bug fix
- Verify task-creator triggers appropriately
- Check `./tasks/` directory creation
- Confirm archiving to `./tasks/completed/`

## Notes

- The slash commands (create-prompt.md, run-prompt.md) remain available for explicit user control
- Skills provide proactive usage for users who don't know about meta-prompting
- Hybrid approach gives both automation and control
