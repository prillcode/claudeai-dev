# Development Skills

A unified collection of Claude Code skills for structured software development workflows. These skills handle all types of development work - from simple bug fixes to complex multi-file features - with adaptive specification depth and systematic testing guidance.

## Overview

This directory contains a unified development workflow system with three complementary skills:

- **dev-orchestrator** - Orchestrates the complete development workflow
- **dev-spec** - Creates specifications with adaptive complexity
- **dev-execute** - Executes specifications with two-phase testing workflow

The workflow automatically adapts to task complexity, providing lightweight specifications for simple bugs and comprehensive specifications for complex features.

## Skills

### dev-orchestrator

Orchestrates systematic development workflow for any software development task.

**Purpose:**
- Guides the complete workflow from requirements to completion
- Invokes dev-spec for specification creation
- Invokes dev-execute for implementation
- Manages testing and completion phases

**When to use:**
- Any development work (bugs, features, enhancements, refactoring)
- User requests to implement, build, develop, or fix code
- Need systematic approach with testing guidance

### dev-spec

Creates optimized, XML-structured specifications for all development tasks.

**Purpose:**
- Transforms vague requests into comprehensive specifications
- Adapts depth based on task complexity automatically
- Provides interactive clarification for ambiguous requirements
- Includes testing step generation guidance

**Adaptive Complexity:**
- **Simple tasks** (bug fixes, single-file changes) → Lightweight specification
- **Moderate tasks** (multiple files, some design decisions) → Standard specification
- **Complex tasks** (multi-file, architectural decisions) → Comprehensive specification

**Features:**
- XML-structured specifications for clarity
- Configurable storage directory (defaults to `./.dev-docs/features/`)
- Sequential numbering (001, 002, 003...)
- Support for single, parallel, or sequential execution strategies

### dev-execute

Executes specifications in fresh sub-agent contexts with two-phase testing workflow.

**Purpose:**
- Implements specifications in isolated contexts
- Provides suggested manual testing steps
- Manages completion workflow after user testing

**Two-Phase Workflow:**
1. **Implementation Phase** - Sub-agent implements and provides testing steps
2. **Completion Phase** - User tests, then explicitly confirms completion for archival

**Features:**
- Single, parallel, or sequential execution modes
- Clean sub-agent contexts for focused implementation
- Archives completed work to `[configured_path]/completed/`
- Never archives automatically - waits for user confirmation

## Unified Workflow

All development work follows the same systematic approach:

1. **Specification** → dev-spec creates appropriate specification
2. **Implementation** → dev-execute runs specification in sub-agent
3. **Testing** → User performs manual testing with provided steps
4. **Completion** → User confirms, feature is archived

The complexity adapts automatically based on the task:
- Simple bug fix → Lightweight spec, quick implementation
- Complex feature → Comprehensive spec, thorough implementation

## Configuration

The skills support configurable directory storage via `CLAUDE.md`:

```markdown
## Development Workflow

dev_docs_directory: ./docs/features
```

If not configured, prompts user on first use and saves choice to root `CLAUDE.md`. Default: `./.dev-docs`

## Usage

These skills work proactively with Claude Code:

- Request any development work → Claude may invoke dev-orchestrator
- dev-orchestrator guides through spec → implement → test → complete workflow
- Skills automatically adapt specification depth to task complexity
- Testing steps provided after implementation
- Explicit user confirmation required before archival

## Directory Structure

```
dev-skills/
├── README.md                    # This document
├── dev-orchestrator/            # Workflow orchestrator
│   └── SKILL.md
├── dev-spec/                    # Specification creator
│   └── SKILL.md
└── dev-execute/                 # Specification executor
    └── SKILL.md
```

## Key Features

- **Unified Workflow** - Single workflow for all development tasks
- **Adaptive Complexity** - Automatically adjusts to task complexity
- **Testing First** - Manual testing guidance built into every implementation
- **Two-Phase Completion** - Implement → Test → Confirm → Archive
- **Configurable Storage** - Set directory per project via CLAUDE.md
- **Clean Contexts** - Implementation happens in fresh sub-agent contexts
- **Flexible Execution** - Single, parallel, or sequential execution modes

## See Also

- [../workflow-skills/](../workflow-skills/) - Related workflow automation skills
- [../aws-infra-skills/](../aws-infra-skills/) - AWS infrastructure discovery and CDK generation
