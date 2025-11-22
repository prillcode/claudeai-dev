# Agile Skills

A collection of Claude Code skills for decomposing agile artifacts into actionable development work. These skills bridge the gap between high-level planning (epics, features, stories) and the execution layer provided by [dev-skills](../dev-skills/).

## Overview

This directory contains skills for progressive work decomposition following the agile hierarchy:

**Epic → Features → Stories → Specs → Implementation**

- **epic-feature-creator** - Decomposes JIRA epics into technical features
- **feature-story-creator** - Breaks features into user stories (planned)
- **story-task-creator** - Splits large stories into sub-tasks (planned)

These skills integrate with dev-skills to create a complete workflow from epic to deployed code.

## Skills

### epic-feature-creator

Transforms JIRA epics into technical feature breakdowns organized by system components.

**Purpose:**
- Parse JIRA epic content (title, description, acceptance criteria, scope)
- Analyze technical domains (frontend, backend, database, infrastructure)
- Generate numbered features (F001, F002, F003...) with dependencies
- Create feature index with dependency graph
- Preserve epic source for traceability

**Features:**
- JIRA export format support (paste epic content)
- Future-proofed for direct JIRA API integration
- Technical component identification
- Dependency mapping between features
- Complexity estimation (S/M/L/XL)
- Sequential numbering with slug-based filenames
- Configurable storage directory (defaults to `./.agile-docs/`)

**Output Structure:**
```
{agile_docs_directory}/
├── epics/
│   └── EPIC-{number}-source.md           # Original epic content
├── features/
│   ├── EPIC-{number}-index.md            # Feature overview with dependency graph
│   ├── F001-{slug}.md                    # Individual feature files
│   ├── F002-{slug}.md
│   └── ...
└── stories/                              # Created by feature-story-creator
```

**Each feature includes:**
- Title and description
- Technical components (frontend, backend, database, infrastructure)
- Dependencies (on other features or external services)
- Acceptance criteria
- Complexity estimate with rationale
- Architecture notes and risks

**When to use:**
- Starting work on a new epic
- Need to break down epic scope into deliverable units
- Want technical decomposition before story creation
- Ready to plan feature implementation order

**Slash command:** `/epic-to-features [paste epic content]`

### feature-story-creator

*(Planned)* Breaks features into user stories ready for dev-spec.

**Purpose:**
- Read feature files from `{agile_docs_directory}/features/`
- Decompose each feature into 3-8 user stories
- Generate story files with acceptance criteria
- Create story-to-feature traceability
- Prepare stories for dev-spec input

**Integration:**
- Input: Feature files from epic-feature-creator
- Output: Story files ready for dev-spec or story-task-creator

### story-task-creator

*(Planned)* Optional layer to split large stories into sub-tasks.

**Purpose:**
- Break large stories (>2 days) into smaller tasks (<2 hours each)
- Useful when stories are too complex for single dev-spec
- Creates task breakdown with clear dependencies
- Outputs feed directly into dev-spec

**Integration:**
- Input: Story files from feature-story-creator
- Output: Task breakdowns ready for dev-spec

## Complete Workflow

### Full Integration Chain

```
1. JIRA Epic (paste)
   ↓
2. epic-feature-creator → Features (F001, F002, F003...)
   ↓
3. feature-story-creator → Stories (S001, S002, S003...)
   ↓
4. story-task-creator (optional) → Tasks (T001, T002...)
   ↓
5. dev-spec (dev-skills) → Specification
   ↓
6. dev-execute (dev-skills) → Implementation
   ↓
7. Testing → User confirms completion
   ↓
8. git-commit-helper (dev-skills) → Commit
```

### Example Flow

**Starting with an epic:**

```bash
# 1. Decompose epic into features
/epic-to-features
[Paste JIRA epic content]

# Result: 4 features created (F001-F004)

# 2. Break first feature into stories (planned)
/feature-to-stories F001

# Result: 5 stories created (S001-S005)

# 3. Implement first story using dev-skills
/dev-orchestrator S001

# Result: Spec created, implemented, tested, committed

# 4. Repeat for remaining stories...
```

## Configuration

The skills support configurable directory storage via root `CLAUDE.md`:

```markdown
## Agile Workflow

agile_docs_directory: ./.agile-docs
```

If not configured, prompts user on first use and saves choice to root `CLAUDE.md`. Default: `./.agile-docs`

## Directory Structure

```
agile-skills/
├── README.md                           # This document
├── epic-feature-creator/               # Epic → Features
│   └── SKILL.md
├── feature-story-creator/              # Features → Stories
│   └── SKILL.md
└── story-task-creator/                 # Stories → Tasks (planned)
    └── SKILL.md
```

## Integration with dev-skills

These skills are designed to work seamlessly with [dev-skills](../dev-skills/):

**agile-skills** handle decomposition:
- Epic → Features → Stories → Tasks

**dev-skills** handle execution:
- Task/Story → Spec → Implementation → Testing → Commit

Together they provide end-to-end workflow from epic to deployed code.

## Key Features

- **Progressive Decomposition** - Break large epics into manageable units
- **Technical Organization** - Group by system components (frontend, backend, etc.)
- **Dependency Tracking** - Map dependencies between features and stories
- **Traceability** - Maintain links from implementation back to epic
- **Configurable Storage** - Set directory per project via CLAUDE.md
- **Future-Proof** - Designed for eventual JIRA API integration
- **Clean Handoffs** - Each skill outputs artifacts for the next skill

## Artifact Hierarchy

All artifacts use frontmatter metadata for tooling and traceability:

**Epic Source** (`EPIC-{number}-source.md`):
```yaml
---
epic_id: PROJ-123
created_date: 2025-01-21
source: jira_export
---
```

**Feature** (`F{number}-{slug}.md`):
```yaml
---
feature_id: F001
epic_source: EPIC-PROJ-123
title: User Registration
complexity: M
status: ready_for_stories
---
```

**Story** (`S{number}-{slug}.md`):
```yaml
---
story_id: S001
feature_id: F001
epic_id: PROJ-123
status: ready_for_spec
---
```

**Spec** (from dev-spec):
```yaml
---
spec_id: 001
story_id: S001
feature_id: F001
epic_id: PROJ-123
---
```

This creates complete traceability from epic to implementation.

## Usage

These skills work proactively with Claude Code:

- Paste epic content → Claude may invoke epic-feature-creator
- Features ready → Use feature-story-creator on each feature
- Stories ready → Use dev-orchestrator (dev-skills) on each story
- Skills automatically maintain traceability throughout

## See Also

- [../dev-skills/](../dev-skills/) - Specification creation and execution
- [~/.claude/skills/](../../.claude/skills/) - User-level Claude Code skills