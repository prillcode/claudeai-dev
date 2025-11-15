---
name: spec-task
description: Creates lightweight task specifications for simple bug fixes and maintenance work. This skill should be used when creating specifications for straightforward tasks that don't require extensive planning. Generates simplified XML-structured specifications with only essential elements (objective, requirements, verification). Always saves specifications to ./.dev-docs/tasks/ directory. Designed for speed and simplicity.
---

# Task Specification Creator

## Overview

Creates lightweight, focused specifications for simple tasks like bug fixes and maintenance work. Optimized for speed with minimal overhead while maintaining clear documentation.

## When to Use

Use this skill when:
- Creating specifications for bug fixes
- Simple maintenance tasks or small updates
- Single-file or straightforward multi-file changes
- Requirements are already clear
- No architectural decisions needed

**Do not use** for complex features, multi-component work, or tasks requiring extensive planning (use spec-feature instead).

## Core Specification Process

### Step 1: Analyze the Task

Quickly assess the task:
- Is the task description clear enough to proceed?
- What files need to be modified?
- What's the expected outcome?
- How will we verify it's fixed?

**Note**: For simple tasks, assume clarity. Only ask questions if truly ambiguous.

### Step 2: Generate Specification

Create a lightweight specification with simplified XML structure:

**Required tags only:**
- `<objective>` - What needs to be done and why
- `<requirements>` - Specific things to implement or fix
- `<verification>` - How to test it works

**Skip these (used in feature specs but not needed for tasks):**
- Extended thinking triggers
- Comprehensive context sections
- Implementation details
- "Go beyond basics" language
- Complex architectural guidance

### Step 3: Save Specification

Save to `./.dev-docs/tasks/` directory:
- Format: `001-task-name.md`, `002-another-task.md`, etc.
- Check existing files to determine next number
- Lowercase, hyphen-separated naming
- Always single task (no multiple/parallel/sequential logic)

## Simplified XML Structure

```xml
<objective>
[Clear statement of what needs to be fixed or updated]
[Brief explanation of why - one sentence]
</objective>

<requirements>
[Specific steps to complete the task]
- Fix [specific issue]
- Update [specific element]
- Test [specific scenario]
</requirements>

<verification>
Before completing, verify:
- [How to test the fix works]
- [Expected behavior after fix]
</verification>
```

## Example Task Specification

```xml
<objective>
Fix the broken login button on mobile devices. The button is not clickable due to a CSS z-index issue causing it to be covered by the navigation overlay.
</objective>

<requirements>
- Locate the login button CSS in @src/styles/auth.css
- Increase z-index to be higher than navigation overlay (currently 100)
- Ensure button remains clickable on all mobile viewport sizes
- Verify no visual regression on desktop
</requirements>

<verification>
Before completing, verify:
- Login button is clickable on mobile (test on viewport widths 320px, 375px, 414px)
- Button still functions correctly on desktop
- No overlap with navigation overlay
- Button click triggers login modal as expected
</verification>
```

## Specification Construction Guidelines

### Always Include

- Clear objective stating what and why (brief)
- Specific, actionable requirements
- Simple verification steps
- File references with @ notation when known
- Relative paths for any file operations

### Never Include for Tasks

- Extended thinking triggers ("thoroughly analyze", etc.)
- "Go beyond basics" language
- Parallel tool calling guidance
- Complex implementation strategies
- Multiple execution scenarios
- Comprehensive architectural context

### Keep It Simple

1. **Brevity**: Tasks specs should be concise, typically 10-20 lines
2. **Clarity**: Direct, unambiguous instructions
3. **Focus**: Only what's needed to complete the specific task
4. **Verification**: Simple, concrete steps to confirm success

## After Generating Specification

Present simple options to the user:

```
✓ Saved task specification to ./.dev-docs/tasks/005-fix-mobile-login-button.md

What's next?

1. Execute task now (using dev-task)
2. Review/edit specification first
3. Save for later

Choose (1-3):
```

When user chooses to execute, invoke the **dev-task** skill.

## Setup Requirements

Before saving any specifications:
1. Check if `./.dev-docs/tasks/` directory exists
2. If not, create it: `!mkdir -p ./.dev-docs/tasks/`
3. Read `!ls ./.dev-docs/tasks/ 2>/dev/null | sort -V | tail -1` to determine next number
4. If no files exist, start with 001

## Task Specification Examples

**Bug Fix:**
```xml
<objective>
Fix TypeError in user profile page when avatar is null.
</objective>

<requirements>
- Add null check in @src/components/UserProfile.tsx before accessing avatar.url
- Provide default placeholder avatar when avatar is null
- Maintain existing styling and functionality
</requirements>

<verification>
- Profile page loads without errors when avatar is null
- Default placeholder displays correctly
- Existing functionality unchanged when avatar exists
</verification>
```

**Simple Update:**
```xml
<objective>
Update copyright year from 2024 to 2025 in footer.
</objective>

<requirements>
- Update year in @src/components/Footer.tsx
- Ensure change is reflected on all pages
</requirements>

<verification>
- Footer displays "© 2025" on all pages
- No other content affected
</verification>
```

**Dependency Update:**
```xml
<objective>
Update lodash to version 4.17.21 to fix security vulnerability.
</objective>

<requirements>
- Update lodash version in @package.json
- Run npm install to update lock file
- Verify no breaking changes in existing code
</requirements>

<verification>
- Package.json shows lodash@4.17.21
- npm audit shows no high-severity vulnerabilities
- Existing tests pass
- Application builds without errors
</verification>
```

## When to Ask Questions

**Only ask questions if:**
- The bug description is completely vague ("something is broken")
- Multiple interpretation of the task exist
- Can't identify which files need modification
- Security or data implications are unclear

**Don't ask questions when:**
- Task is straightforward ("fix typo", "update color")
- Files to modify are obvious from description
- Expected outcome is clear
- Standard fix with known approach

## Related Skills

- **task-creator**: Orchestrator that guides the overall task workflow
- **dev-task**: Executes the generated task specifications
- **spec-feature**: For complex features (not simple tasks)
