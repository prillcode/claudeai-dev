---
name: feature-creator
description: Orchestrates the feature development workflow for complex, multi-file software features. This skill should be used when the user requests to implement, build, or develop complex features requiring architectural decisions, multi-file changes, or comprehensive planning. Triggers on complexity signals (multi-file, new features, architectural changes) combined with feature-related language ("implement", "build", "feature", "add functionality").
---

# Feature Creator

## Overview

Feature Creator orchestrates a systematic workflow for developing complex software features by separating specification from implementation. Use this skill when building features that involve multiple files, architectural decisions, or require comprehensive planning.

## When to Use Feature Creator

Use this skill when:
- User requests to "implement", "build", or "develop" a new feature
- Task involves multiple files or components
- Architectural decisions are needed
- Feature requires careful planning and verification
- Task has 3+ distinct steps or touches multiple parts of the codebase

**Do not use** for simple bug fixes, single-file tweaks, or straightforward maintenance tasks (use task-creator instead).

## Workflow

Feature Creator follows a two-phase workflow that separates analysis from execution:

### Phase 1: Specification (Analysis)
**Tool: spec-feature skill**

In this phase, work with the user to create a rigorous, specification-grade prompt:

1. **Clarify Requirements**: Ask targeted questions about:
   - Architecture and design patterns to use
   - Data sources and integrations needed
   - Framework preferences and constraints
   - Success criteria and verification methods

2. **Generate Feature Spec**: Create a structured prompt with:
   - XML-formatted semantic organization
   - Complete context about the feature's purpose
   - Explicit requirements and implementation guidance
   - Clear success criteria and verification steps
   - "What to avoid and why" sections
   - Extended thinking triggers for complex reasoning

3. **Save Specification**: Store the generated prompt in `./features/` directory
   - Format: `001-feature-name.md`, `002-another-feature.md`, etc.
   - Numbered sequentially for easy tracking
   - May generate multiple prompts for complex features

### Phase 2: Implementation (Execution)
**Tool: dev-feature skill**

Execute the generated specification in a fresh context:

1. **Load Feature Spec**: Read the prompt(s) from `./features/`
2. **Execute in Clean Context**: Delegate to sub-agent with pristine specification
3. **Support Execution Strategies**:
   - **Single prompt**: For focused features
   - **Parallel execution**: For independent components
   - **Sequential execution**: For dependent tasks
4. **Archive on Completion**: Move completed prompts to `./features/completed/`

## Benefits of This Approach

**Separation of Concerns:**
- Main context stays clean with requirements gathering and planning
- Implementation happens in fresh context with only the specification
- No pollution from exploration mixed with execution

**Higher Quality:**
- Systematic thinking produces comprehensive specifications
- Extended thinking triggers handle complex reasoning
- Success criteria ensure clear completion signals
- Verification protocols built into every feature

**Reusability:**
- Specifications saved as markdown files
- Can review, edit, or rerun prompts
- Archive completed work for reference
- Parallel execution when possible (no token concerns with Claude Max)

## Related Skills

- **spec-feature**: Creates the feature specification prompt
- **dev-feature**: Executes the feature specification
- **task-creator**: For simpler bug fixes and maintenance (not complex features)

## Example Usage Pattern

```
User: "I want to build a user authentication system with OAuth support"

1. feature-creator provides workflow guidance
2. Claude invokes spec-feature to:
   - Ask about OAuth providers, token storage, session management
   - Generate comprehensive feature spec with XML structure
   - Save to ./features/001-user-authentication.md
3. Claude invokes dev-feature to:
   - Load the specification
   - Execute in clean sub-agent context
   - Implement with clear success criteria
   - Archive to ./features/completed/
```

## Notes

- This skill provides **guidance and structure**, not full automation
- Claude will invoke spec-feature and dev-feature directly when appropriate
- Flexible approach allows adaptation to specific feature needs
- User maintains control while benefiting from systematic workflow
