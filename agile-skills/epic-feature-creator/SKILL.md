---
name: epic-feature-creator
description: Transform JIRA epics into technical feature breakdowns organized by system components. Analyzes epic scope and creates numbered features with technical components, dependencies, and acceptance criteria. Outputs feed into feature-story-creator skill. Use when decomposing epics into deliverable features.
---

<objective>
Transform JIRA epics into structured feature sets organized by technical components. Each feature includes description, technical components, dependencies, acceptance criteria, and effort estimates. Supports future JIRA API integration while currently accepting pasted JIRA export format.
</objective>

<quick_start>
<workflow>
1. **Configure storage** (first use only):
   - Check for `agile_docs_directory` in root CLAUDE.md
   - If not found, prompt: "Where should agile artifacts be stored? (default: ./.agile-docs)"
   - Save choice to root CLAUDE.md under `## Agile Workflow` section

2. **Accept epic input**:
   - Prompt: "Paste JIRA epic content (title, description, acceptance criteria, scope)"
   - Parse epic details from pasted content

3. **Analyze and decompose**:
   - Identify technical components (frontend, backend, API, database, infrastructure)
   - Group related functionality by technical boundaries
   - Consider epic scope for functional groupings if needed

4. **Generate features**:
   - Create feature breakdown with sequential numbering (F001, F002, F003...)
   - Each feature includes: title, description, technical components, dependencies, acceptance criteria
   - Estimate relative complexity (S/M/L/XL)

5. **Save artifacts**:
   - Save original epic: `{agile_docs_directory}/epics/EPIC-{number}-source.md`
   - Save features: `{agile_docs_directory}/features/F{number}-{slug}.md`
   - Create index: `{agile_docs_directory}/features/EPIC-{number}-index.md`
</workflow>
</quick_start>

<configuration>
<storage_setup>
**First-time configuration:**

1. Read root `CLAUDE.md` to check for existing configuration
2. Look for section: `## Agile Workflow`
3. Look for field: `agile_docs_directory: {path}`

If not found:
- Prompt user: "Where should agile artifacts be stored? (press Enter for default: ./.agile-docs)"
- Create section in root CLAUDE.md:
  ```markdown
  ## Agile Workflow

  agile_docs_directory: {user_choice_or_default}
  ```

**Directory structure created:**
```
{agile_docs_directory}/
├── epics/                    # Original epic sources
│   └── EPIC-{number}-source.md
├── features/                 # Generated features
│   ├── EPIC-{number}-index.md
│   ├── F001-{slug}.md
│   ├── F002-{slug}.md
│   └── ...
└── stories/                  # Created by feature-story-creator
    └── ...
```
</storage_setup>

<sequential_numbering>
**Feature numbering:**
- Features numbered sequentially: F001, F002, F003...
- Check existing features directory for highest number
- Increment from last used number
- Format: `F{number:03d}-{slug}.md`
- Example: `F001-user-authentication.md`

**Epic numbering:**
- Parse JIRA epic number from input (e.g., "PROJ-123")
- Save as: `EPIC-PROJ-123-source.md`
- Reference in feature files for traceability
</sequential_numbering>
</configuration>

<epic_input_format>
<jira_export>
Accept pasted JIRA epic content with these fields:

**Required fields:**
- Epic title/summary
- Description
- Acceptance criteria

**Optional fields:**
- Scope/business value
- Constraints
- Related epics/dependencies
- Labels/components

**Example input:**
```
Epic: PROJ-123 - User Authentication System

Description:
Implement complete user authentication system with email/password login,
social auth (Google, GitHub), and session management.

Acceptance Criteria:
- Users can register with email/password
- Users can login with email/password
- Users can login with Google OAuth
- Users can login with GitHub OAuth
- Sessions persist across page refreshes
- Logout functionality works correctly

Scope:
Frontend, backend API, database schema, third-party integrations
```
</jira_export>

<future_jira_integration>
Skill designed for future JIRA API integration:
- Current: Accept pasted content
- Future: Direct JIRA API fetch by epic key
- Structure preserved to support both input methods
- Epic source storage enables traceability
</future_jira_integration>
</epic_input_format>

<feature_decomposition>
<analysis_process>
1. **Identify technical domains:**
   - Frontend components (UI, pages, forms)
   - Backend services (APIs, business logic)
   - Data layer (database, schema, migrations)
   - Infrastructure (auth providers, sessions, security)
   - Integration points (third-party services)

2. **Group by technical boundaries:**
   - Primarily organize by system components
   - Consider functional groupings if epic demands it
   - Epic content guides grouping strategy

3. **Define feature scope:**
   - Each feature should be independently deliverable
   - Features can have dependencies on other features
   - Size features appropriately (not too large, not too granular)
   - Target: Each feature → 3-8 stories

4. **Extract acceptance criteria:**
   - Map epic-level criteria to specific features
   - Add technical acceptance criteria
   - Ensure completeness and testability
</analysis_process>

<feature_template>
Each generated feature file contains:

```markdown
---
feature_id: F{number}
epic_source: EPIC-{epic_number}
title: {Feature Title}
complexity: {S|M|L|XL}
status: ready_for_stories
---

# {Feature Title}

## Description
{What this feature delivers and why}

## Technical Components
- **Frontend**: {Components, pages, UI elements}
- **Backend**: {APIs, services, business logic}
- **Database**: {Schema changes, migrations, models}
- **Infrastructure**: {External services, integrations, config}

## Dependencies
- Depends on: {List of feature IDs this depends on}
- Blocks: {List of feature IDs that depend on this}
- External: {Third-party services, libraries required}

## Acceptance Criteria
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}

## Complexity Estimate
{S|M|L|XL} - {Brief rationale}

## Notes
{Architecture considerations, risks, implementation notes}

## Next Step
Ready for feature-story-creator skill to break into stories.
```
</feature_template>

<complexity_estimation>
**Relative sizing:**
- **S (Small)**: Single component, minimal integration, 1-2 day effort
- **M (Medium)**: Multiple components, some integration, 3-5 day effort
- **L (Large)**: Multiple systems, significant integration, 1-2 week effort
- **XL (Extra Large)**: Cross-cutting, complex integration, 2+ week effort (consider splitting)

Base estimates on:
- Number of technical components involved
- Integration complexity
- Dependencies on other features
- Risk and unknowns
</complexity_estimation>
</feature_decomposition>

<output_artifacts>
<epic_source>
**File**: `{agile_docs_directory}/epics/EPIC-{epic_number}-source.md`

Preserves original JIRA epic content for traceability:

```markdown
---
epic_id: {epic_number}
created_date: {ISO date}
source: jira_export
---

# Epic: {Title}

{Original pasted content preserved exactly as provided}
```
</epic_source>

<feature_index>
**File**: `{agile_docs_directory}/features/EPIC-{epic_number}-index.md`

Overview of all features for this epic:

```markdown
---
epic_id: {epic_number}
epic_title: {Title}
total_features: {count}
created_date: {ISO date}
---

# Features for Epic: {Title}

## Summary
{Brief epic summary}

## Features
1. **F001** - {Title} [{Complexity}] - {Brief description}
2. **F002** - {Title} [{Complexity}] - {Brief description}
3. **F003** - {Title} [{Complexity}] - {Brief description}

## Dependency Graph
```
F001 (no dependencies)
F002 (depends on F001)
F003 (depends on F001)
F004 (depends on F002, F003)
```

## Total Effort Estimate
{Sum of complexity estimates with rationale}

## Next Steps
Use feature-story-creator skill on each feature to generate stories.
```
</feature_index>

<individual_features>
**Files**: `{agile_docs_directory}/features/F{number}-{slug}.md`

One file per feature using template from <feature_template> above.
</individual_features>
</output_artifacts>

<validation>
<completeness_check>
Before finalizing, verify:
- [ ] All epic acceptance criteria mapped to features
- [ ] Technical components identified for each feature
- [ ] Dependencies clearly stated
- [ ] No feature is too large (XL should be rare)
- [ ] Features are independently deliverable (with dependencies noted)
- [ ] Acceptance criteria are specific and testable
- [ ] Complexity estimates are reasonable
</completeness_check>

<user_review>
Present feature breakdown to user:
1. Show feature index with all features
2. Ask: "Does this feature breakdown look correct?"
3. Allow iteration before saving to files
4. Only write files after user approval
</user_review>
</validation>

<integration_points>
<input_from>
- JIRA epic export (current)
- Future: JIRA API direct fetch
</input_from>

<output_to>
**feature-story-creator skill:**
- Reads feature files from `{agile_docs_directory}/features/`
- Breaks each feature into stories
- Stories reference feature_id for traceability
</output_to>

<traceability>
**Epic → Features → Stories → Specs → Implementation**

```
EPIC-PROJ-123-source.md
├── F001-user-registration.md
│   ├── S001-registration-form.md      (story)
│   ├── S002-validation-logic.md       (story)
│   └── S003-registration-api.md       (story)
├── F002-user-login.md
│   ├── S004-login-form.md             (story)
│   └── S005-auth-api.md               (story)
└── F003-session-management.md
    ├── S006-session-storage.md        (story)
    └── S007-logout-logic.md           (story)
```
</traceability>
</integration_points>

<success_criteria>
Skill successfully executed when:
- Storage configuration completed and saved to CLAUDE.md
- Epic source preserved in epics/ directory
- Features generated with complete structure (description, components, dependencies, criteria)
- Feature index created with dependency graph
- Sequential numbering applied correctly
- User reviews and approves feature breakdown
- All artifacts saved to configured directory
- Clear next step provided (use feature-story-creator on features)
</success_criteria>

<example_session>
```
User: [Pastes JIRA epic content for PROJ-123 User Authentication]

Skill:
1. Configures storage (if needed)
2. Saves epic source to epics/EPIC-PROJ-123-source.md
3. Analyzes epic, identifies 4 features:
   - F001: User Registration (M)
   - F002: Email/Password Login (M)
   - F003: Social Authentication (L)
   - F004: Session Management (M)
4. Creates feature files with components, dependencies, criteria
5. Creates EPIC-PROJ-123-index.md with dependency graph
6. Shows user the feature breakdown for review
7. Saves all artifacts after approval

Next: User runs feature-story-creator on F001 to generate stories
```
</example_session>