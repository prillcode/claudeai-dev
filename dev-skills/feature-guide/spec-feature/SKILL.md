---
name: spec-feature
description: Expert prompt engineer that creates optimized, XML-structured feature specifications for complex software development. This skill should be used when creating specifications for features that require comprehensive planning, multiple files, or architectural decisions. Generates rigorous, specification-grade prompts with intelligent depth selection, extended thinking triggers, and clear success criteria. Always saves specifications to ./features/ directory.
---

# Feature Specification Creator

## Overview

Creates rigorous, XML-structured specifications for complex software features. Transforms vague feature requests into comprehensive, executable specifications through systematic analysis and clarification.

## When to Use

Use this skill when:
- Creating specifications for multi-file features
- Features require architectural decisions
- Need comprehensive planning before implementation
- User requests feature development with incomplete details
- Working with complex requirements needing clarification

## Core Specification Process

### Step 1: Analyze the Request

Before generating anything, analyze the feature request:

**Clarity Check (Golden Rule)**: Would a colleague with minimal context understand what's being asked?
- Are there ambiguous terms that could mean multiple things?
- Would examples help clarify the desired outcome?
- Are there missing details about constraints or requirements?
- Is the context clear (what it's for, who it's for, why it matters)?

**Task Complexity**: Is this simple (single file, clear goal) or complex (multi-file, research needed, multiple steps)?

**Single vs Multiple Specifications**:
- **Single spec**: Task has clear dependencies, single cohesive goal, sequential steps
- **Multiple specs**: Task has independent sub-tasks that could be parallelized or done separately
- Consider: Can parts be done simultaneously? Are there natural boundaries between sub-tasks?

**Execution Strategy** (if multiple specs):
- **Parallel**: Sub-tasks are independent, no shared file modifications, can run simultaneously
- **Sequential**: Sub-tasks have dependencies, one must finish before next starts
- Look for: Shared files (sequential), independent modules (parallel), data flow between tasks (sequential)

**Reasoning Depth Needed**:
- Simple/straightforward → Standard specification
- Complex reasoning, multiple constraints, or optimization → Include extended thinking triggers

**Project Context**: Do you need to examine the codebase structure, dependencies, or existing patterns?

**Required Tools**: What file references, bash commands, or MCP servers might be needed?

**Verification Needs**: Does this feature warrant built-in error checking or validation steps?

### Step 2: Clarify Requirements

If the request is ambiguous or could benefit from more detail, ask targeted questions:

"I'll create an optimized feature specification. First, let me clarify a few things:

1. [Specific question about ambiguous aspect]
2. [Question about architectural decisions - frameworks, patterns, libraries]
3. [Question about data sources and integrations]
4. What is this feature for? How will users interact with it?
5. Who is the intended audience/user?
6. Can you provide an example of [specific aspect]?

Please answer any that apply, or just say 'continue' if I have enough information."

**Key areas to clarify**:
- Architecture and design patterns to use
- Data sources and integrations needed
- Framework preferences and constraints
- Security and performance requirements
- Success criteria and verification methods

### Step 3: Confirm Understanding

Once you have enough information, confirm your understanding:

"I'll create a feature specification for: [brief summary of feature]

This will be a [simple/moderate/complex] specification that [key approach].

[If multiple specs]: I'll create [N] specifications that can run [in parallel/sequentially].

Should I proceed, or would you like to adjust anything?"

### Step 4: Generate and Save Specification(s)

Create the specification(s) and save to the ./features/ folder.

**For single specifications:**
- Generate one specification file following the XML patterns below
- Save as `./features/[number]-[name].md`

**For multiple specifications:**
- Determine how many specifications are needed (typically 2-4)
- Generate each spec with clear, focused objectives
- Save sequentially: `./features/[N]-[name].md`, `./features/[N+1]-[name].md`, etc.
- Each specification should be self-contained and executable independently

**File naming:**
- Check existing files in ./features/ to determine next number
- Number format: 001, 002, 003, etc.
- Name format: lowercase, hyphen-separated, max 5 words describing the feature
- Example: `./features/001-implement-user-authentication.md`

**File contents:**
- ONLY the specification content, no explanations or metadata
- Full XML structure with semantic tags
- Ready to be executed by dev-feature skill

## XML Specification Patterns

### For Feature Implementation

```xml
<objective>
[Clear statement of what feature needs to be built]
Explain the end goal and why this feature matters.
</objective>

<context>
[Project type, tech stack, relevant constraints]
[Who will use this feature, what it's for]
@[relevant files to examine]
Read CLAUDE.md for project conventions if it exists.
</context>

<requirements>
[Specific functional requirements]
[Performance or quality requirements]
[User experience requirements]
Be explicit about what should be implemented.
</requirements>

<implementation>
[Specific approaches or patterns to follow]
[Architecture decisions and rationale]
[What to avoid and WHY - explain the reasoning behind constraints]
[For ambitious features]: Include as many relevant features as possible. Go beyond the basics to create a fully-featured implementation.
</implementation>

<output>
Create/modify files with relative paths:
- `./path/to/file.ext` - [what this file should contain]
- `./path/to/another.ext` - [purpose of this file]
</output>

<verification>
Before declaring complete, verify your work:
- [Specific test or check to perform]
- [How to confirm the solution works]
- [Integration testing requirements]
</verification>

<success_criteria>
[Clear, measurable criteria for completion]
[User acceptance criteria]
[Performance benchmarks if applicable]
</success_criteria>
```

### For Analysis-Heavy Features

```xml
<objective>
[What feature needs to be built and why]
[Research or analysis required before implementation]
</objective>

<research>
[Codebase areas to explore]
[Patterns or conventions to discover]
@[files or directories to examine]
![commands to gather information]
Thoroughly analyze existing patterns before implementing.
</research>

<requirements>
[Functional requirements]
[How new feature should integrate with existing code]
</requirements>

<implementation>
[Approach that aligns with discovered patterns]
[How to maintain consistency with existing code]
Deeply consider multiple approaches before selecting optimal one.
</implementation>

<validation>
[How to verify the implementation matches existing patterns]
[Integration testing with existing features]
</validation>

<output>
[Files to create/modify with relative paths]
</output>

<success_criteria>
[Clear completion criteria]
</success_criteria>
```

## Specification Construction Rules

### Always Include

- XML tag structure with clear, semantic tags
- **Contextual information**: Why this feature matters, what it's for, who will use it
- **Explicit, specific instructions**: Exactly what to implement
- **Sequential steps**: Use numbered lists for clarity
- File output instructions using relative paths: `./filename` or `./subfolder/filename`
- Reference to reading CLAUDE.md for project conventions
- Explicit success criteria within `<success_criteria>` tags
- Verification steps within `<verification>` tags

### Conditionally Include (based on analysis)

**Extended thinking triggers** for complex reasoning:
- Phrases like: "thoroughly analyze", "consider multiple approaches", "deeply consider", "explore multiple solutions"
- Don't use for simple, straightforward features

**"Go beyond basics" language** for creative/ambitious features:
- Example: "Include as many relevant features as possible. Go beyond the basics to create a fully-featured implementation."

**WHY explanations** for constraints and requirements:
- Explain WHY constraints matter, not just what they are
- Example: Instead of "Never use ellipses", write "Your response will be read aloud, so never use ellipses since text-to-speech can't pronounce them"

**Parallel tool calling** for agentic/multi-step workflows:
- "For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially."

**Reflection after tool use** for complex agentic tasks:
- "After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding."

**Additional tags** as needed:
- `<research>` tags when codebase exploration is needed
- `<validation>` tags for tasks requiring verification
- `<examples>` tags for complex or ambiguous requirements
- `<constraints>` tags for specific limitations

### Intelligence Guidelines

1. **Clarity First**: If anything is unclear, ask before proceeding. Test: Would a colleague with minimal context understand this specification?

2. **Context is Critical**: Always include WHY the feature matters, WHO it's for, and WHAT it will be used for.

3. **Be Explicit**: Generate specifications with explicit, specific instructions. For ambitious features, include "go beyond the basics."

4. **Scope Assessment**: Simple features get concise specs. Complex features get comprehensive structure with extended thinking triggers.

5. **Context Loading**: Only request file reading when the feature explicitly requires understanding existing code:
   - "Examine @package.json for dependencies" (when adding new packages)
   - "Review @src/database/* for schema" (when modifying data layer)
   - Skip file reading for greenfield features

6. **Precision vs Brevity**: Default to precision. A longer, clear specification beats a short, ambiguous one.

7. **Tool Integration**:
   - Include MCP servers only when explicitly mentioned or obviously needed
   - Use bash commands for environment checking when state matters
   - File references should be specific, not broad wildcards
   - For multi-step agentic tasks, include parallel tool calling guidance

8. **Output Clarity**: Every specification must specify exactly where to save outputs using relative paths.

9. **Verification Always**: Every specification should include clear success criteria and verification steps.

## After Generating Specification(s)

After saving the specification(s), present options to the user:

### Single Specification Scenario

```
✓ Saved specification to ./features/005-implement-dashboard.md

What's next?

1. Execute feature now (using dev-feature)
2. Review/edit specification first
3. Save for later
4. Other

Choose (1-4):
```

### Multiple Parallel Specifications

```
✓ Saved specifications:
  - ./features/005-implement-auth.md
  - ./features/006-implement-api.md
  - ./features/007-implement-ui.md

Execution strategy: These can run in PARALLEL (independent components, no shared files)

What's next?

1. Execute all in parallel now (launches 3 sub-agents simultaneously)
2. Execute sequentially instead
3. Review/edit specifications first
4. Other

Choose (1-4):
```

### Multiple Sequential Specifications

```
✓ Saved specifications:
  - ./features/005-setup-database.md
  - ./features/006-create-migrations.md
  - ./features/007-seed-data.md

Execution strategy: These must run SEQUENTIALLY (dependencies: 005 → 006 → 007)

What's next?

1. Execute sequentially now (one completes before next starts)
2. Execute first specification only (005-setup-database.md)
3. Review/edit specifications first
4. Other

Choose (1-4):
```

When user chooses to execute, invoke the **dev-feature** skill with appropriate parameters.

## Setup Requirements

Before saving any specifications:
1. Check if `./features/` directory exists
2. If not, create it: `!mkdir -p ./features/`
3. Read `!ls ./features/ 2>/dev/null | sort -V | tail -1` to determine the next number in sequence
4. If no files exist, start with 001

## Examples of When to Ask for Clarification

- "Build a dashboard" → Ask: "What kind of dashboard? Admin, analytics, user-facing? What data should it display? Who will use it?"
- "Add authentication" → Ask: "What type? JWT, OAuth, session-based? Which providers? What's the security context?"
- "Implement real-time updates" → Ask: "What technology? WebSockets, SSE, polling? What data needs real-time updates?"
- "Optimize performance" → Ask: "What specific performance issues? Load time, memory, database queries? What are current metrics?"
- "Create API endpoints" → Ask: "What resources? What operations (CRUD)? REST or GraphQL? Authentication required?"

## Related Skills

- **feature-creator**: Orchestrator that guides the overall feature development workflow
- **dev-feature**: Executes the generated specifications
