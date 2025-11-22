---
name: feature-story-creator
description: Transform features into user stories ready for dev-spec. Analyzes feature technical components and creates numbered stories with acceptance criteria, dependencies, and technical notes. Outputs feed into dev-spec skill. Use when decomposing features into implementable stories.
---

<objective>
Transform feature files into structured user stories ready for dev-spec execution. Each story represents a vertical slice of functionality with clear acceptance criteria, technical notes, affected components, and dependencies. Supports flexible story sizing and hybrid decomposition strategies.
</objective>

<quick_start>
<workflow>
1. **Select feature input method**:
   - By feature ID (F001, F002, etc.)
   - Interactive selection from available features
   - Batch process all features from an epic
   - Batch process all unprocessed features

2. **Read and analyze feature(s)**:
   - Parse feature file(s) from `{agile_docs_directory}/features/`
   - Identify technical components and acceptance criteria
   - Understand dependencies and complexity

3. **Decompose into stories**:
   - Apply hybrid strategy (user journeys + technical vertical slices)
   - Target flexible story sizes (adapt to complexity)
   - Each story = actionable work unit for dev-spec
   - Aim for 3-8 stories per feature

4. **Generate story artifacts**:
   - Create stories with sequential numbering (S001, S002, S003...)
   - Each story includes: title, description, technical notes, acceptance criteria, dependencies
   - Link story back to feature and epic for traceability

5. **Create story index**:
   - Generate index file for feature showing all stories
   - Show story dependencies and implementation order
   - Provide next steps for dev-spec execution

6. **Save and review**:
   - Present story breakdown to user
   - Allow iteration before saving
   - Save all artifacts after approval
</workflow>
</quick_start>

<configuration>
<storage_location>
Uses same configuration as epic-feature-creator:
- Reads `agile_docs_directory` from root CLAUDE.md
- If not configured, inherits default `./.agile-docs/`

**Directory structure:**
```
{agile_docs_directory}/
├── epics/
│   └── EPIC-{number}-source.md
├── features/
│   ├── EPIC-{number}-index.md
│   ├── F001-{slug}.md
│   └── ...
└── stories/
    ├── F001-story-index.md          # Story index for feature F001
    ├── S001-{slug}.md                # Individual story files
    ├── S002-{slug}.md
    └── ...
```
</storage_location>

<sequential_numbering>
**Story numbering:**
- Stories numbered globally and sequentially: S001, S002, S003...
- Check existing stories directory for highest number
- Increment from last used number across all features
- Format: `S{number:03d}-{slug}.md`
- Example: `S001-user-registration-form.md`

**Traceability:**
- Each story references its parent feature_id
- Each story references original epic_id
- Maintains complete chain: Epic → Feature → Story → Spec → Implementation
</sequential_numbering>
</configuration>

<feature_selection>
<input_methods>
Support multiple ways to select features for decomposition:

**1. By Feature ID:**
```
User: /feature-to-stories F001
User: /feature-to-stories F001 F003 F005
```

**2. Interactive Selection:**
```
User: /feature-to-stories
Skill: Lists available features, prompts for selection
```

**3. Batch by Epic:**
```
User: /feature-to-stories EPIC-PROJ-123
Skill: Processes all features from that epic
```

**4. Batch All Unprocessed:**
```
User: /feature-to-stories --all-unprocessed
Skill: Finds features without stories, processes them
```
</input_methods>

<feature_discovery>
When no specific feature provided:
1. Scan `{agile_docs_directory}/features/` for feature files
2. Check each feature's status in frontmatter
3. Identify features with `status: ready_for_stories`
4. Present numbered list to user:
   ```
   Available features ready for stories:
   1. F001 - User Registration [M] (EPIC-PROJ-123)
   2. F002 - Email/Password Login [M] (EPIC-PROJ-123)
   3. F003 - Social Authentication [L] (EPIC-PROJ-123)

   Select feature(s) to decompose (comma-separated numbers or 'all'):
   ```
5. Process selected features
</feature_discovery>
</feature_selection>

<story_decomposition>
<hybrid_strategy>
Apply hybrid decomposition based on feature characteristics:

**User Journey Stories** (for user-facing features):
- Registration flow: form display → validation → submission → confirmation
- Login flow: form display → authentication → session creation → redirect
- Profile management: view profile → edit fields → save changes

**Technical Vertical Slices** (for infrastructure features):
- Database layer: schema design → migration → model creation
- API layer: endpoint definition → business logic → error handling
- Integration: service setup → API client → error handling

**Mixed Approach** (for complex features):
- Combine user journey and technical perspectives
- Example: "User registration form" includes frontend form + validation logic + API integration
- Each story is independently testable and deliverable

**Decomposition principles:**
- Each story delivers value (can be tested and demoed)
- Stories are thin vertical slices through the stack
- Dependencies between stories are explicit
- Stories can be implemented in logical order
</hybrid_strategy>

<story_sizing>
**Flexible sizing based on complexity:**

**Small stories** (2-4 hours):
- Single component change
- Simple API endpoint
- Basic UI form
- Simple validation logic

**Medium stories** (4-8 hours):
- Multiple related components
- API endpoint with business logic
- UI component with state management
- Integration with external service

**Factors affecting size:**
- Technical complexity
- Number of components affected
- Integration requirements
- Risk and unknowns

**Size targets:**
- Prefer smaller stories when possible
- Medium stories acceptable for cohesive functionality
- Large stories (>8 hours) should be split further
- Each story should fit in dev-spec workflow
</story_sizing>

<analysis_process>
For each feature:

1. **Review feature components:**
   - Frontend components listed
   - Backend services and APIs
   - Database changes
   - Infrastructure needs
   - External integrations

2. **Review acceptance criteria:**
   - Map criteria to potential stories
   - Each criterion may spawn 1+ stories
   - Add technical criteria not in original feature

3. **Identify story candidates:**
   - Look for natural boundaries
   - Consider implementation order
   - Identify dependencies

4. **Define story scope:**
   - What frontend work is needed?
   - What backend work is needed?
   - What database changes?
   - What can be tested independently?

5. **Order stories logically:**
   - Foundation before features
   - Dependencies before dependents
   - Infrastructure before UI
   - Backend before frontend (usually)
</analysis_process>
</story_decomposition>

<story_template>
Each generated story file contains:

```markdown
---
story_id: S{number}
feature_id: F{feature_number}
epic_id: {epic_number}
title: {Story Title}
status: ready_for_spec
estimated_hours: {2-4|4-8|8+}
---

# {Story Title}

## Description
{What this story delivers, why it matters, and how it fits in the larger feature}

## User Story
As a {user type}
I want {capability}
So that {benefit}

## Technical Notes
**Affected Components:**
- **Frontend**: {Specific components, pages, files to modify}
- **Backend**: {APIs, services, functions to implement}
- **Database**: {Models, migrations, schema changes}
- **Infrastructure**: {Config, environment, third-party setup}

**Implementation Approach:**
{High-level approach or technical considerations}

## Acceptance Criteria
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}

## Dependencies
- **Depends on**: {List of story IDs that must be completed first}
- **Blocks**: {List of story IDs that depend on this}
- **External**: {Third-party services, libraries, external factors}

## Testing Considerations
{How to test this story, what scenarios to cover}

## Next Step
Ready for dev-spec skill to create detailed specification.
```
</story_template>

<output_artifacts>
<story_files>
**Files**: `{agile_docs_directory}/stories/S{number}-{slug}.md`

One file per story using template above.

**Frontmatter fields:**
- `story_id`: S001, S002, etc.
- `feature_id`: Parent feature (F001)
- `epic_id`: Original epic (EPIC-PROJ-123)
- `title`: Story title
- `status`: ready_for_spec, in_progress, completed
- `estimated_hours`: Rough effort estimate
</story_files>

<story_index>
**File**: `{agile_docs_directory}/stories/F{number}-story-index.md`

Overview of all stories for a feature:

```markdown
---
feature_id: F{number}
feature_title: {Title}
epic_id: {epic_number}
total_stories: {count}
created_date: {ISO date}
---

# Stories for Feature: {Feature Title}

## Feature Summary
{Brief feature description from original feature file}

## Stories
1. **S001** - {Title} [{Hours}] - {Brief description}
2. **S002** - {Title} [{Hours}] - {Brief description}
3. **S003** - {Title} [{Hours}] - {Brief description}

## Story Dependencies
```
S001 (no dependencies)
S002 (depends on S001)
S003 (depends on S001)
S004 (depends on S002, S003)
```

## Recommended Implementation Order
1. S001 - {Why first}
2. S002 - {Why second}
3. S003 - {Can be parallel with S002}
4. S004 - {Why last}

## Total Effort Estimate
{Sum of estimated hours}

## Next Steps
Use dev-spec skill on each story to create implementation specifications.

Example:
```
/dev-spec S001
```

Or use dev-orchestrator for complete workflow:
```
/dev-orchestrator S001
```
```
</story_index>

<feature_update>
After creating stories, update the parent feature file:

**Update feature status:**
```yaml
status: stories_created
stories_count: {count}
stories_created_date: {ISO date}
```

This tracks which features have been decomposed.
</feature_update>
</output_artifacts>

<validation>
<completeness_check>
Before finalizing, verify:
- [ ] All feature acceptance criteria mapped to stories
- [ ] Each story has clear, testable acceptance criteria
- [ ] Technical components identified for each story
- [ ] Story dependencies are explicit and correct
- [ ] No story is too large (>8 hours should be split)
- [ ] Stories are independently deliverable (thin vertical slices)
- [ ] User story format complete (As a... I want... So that...)
- [ ] Implementation order makes sense
- [ ] Traceability maintained (story → feature → epic)
</completeness_check>

<user_review>
Present story breakdown to user:
1. Show story index with all stories for feature
2. Show dependency graph
3. Show recommended implementation order
4. Ask: "Does this story breakdown look correct?"
5. Allow iteration before saving to files
6. Only write files after user approval
7. Update parent feature status after saving
</user_review>
</validation>

<integration_points>
<input_from>
**epic-feature-creator:**
- Reads feature files from `{agile_docs_directory}/features/`
- Expects features with status `ready_for_stories`
- Uses feature components, dependencies, and acceptance criteria

**Direct input:**
- Feature IDs provided by user
- Epic ID for batch processing
- Interactive selection
</input_from>

<output_to>
**dev-spec (dev-skills):**
- Stories ready for specification creation
- Each story has sufficient detail for dev-spec
- Status: `ready_for_spec`

**story-task-creator (optional):**
- Large stories (>8 hours) can be further decomposed
- Reads stories with `status: needs_tasks`

**Direct to dev-orchestrator:**
- Stories can go directly to full workflow
- dev-orchestrator → dev-spec → dev-execute → testing → commit
</output_to>

<traceability_chain>
**Complete artifact chain:**

```
EPIC-PROJ-123-source.md
├── F001-user-registration.md
│   ├── S001-registration-form-ui.md
│   │   └── 001-registration-form-ui.md        (dev-spec)
│   ├── S002-registration-validation.md
│   │   └── 002-registration-validation.md     (dev-spec)
│   └── S003-registration-api.md
│       └── 003-registration-api.md            (dev-spec)
├── F002-user-login.md
│   ├── S004-login-form-ui.md
│   │   └── 004-login-form-ui.md               (dev-spec)
│   └── S005-login-auth-api.md
│       └── 005-login-auth-api.md              (dev-spec)
└── ...
```

Each level references its parents for complete traceability.
</traceability_chain>
</integration_points>

<example_decomposition>
<feature_input>
**Feature F001: User Registration** (Medium complexity)

Technical Components:
- Frontend: Registration form, validation UI, success/error states
- Backend: Registration API endpoint, user creation logic, email validation
- Database: User model, email uniqueness constraint
- Infrastructure: Email service integration for verification

Acceptance Criteria:
- Users can access registration form
- Form validates email format and password strength
- Registration creates user in database
- Duplicate emails are rejected
- Success confirmation displayed
</feature_input>

<story_output>
**Generated Stories:**

**S001: Registration Form UI** [4h]
- Create registration form component
- Input fields for email, password, confirm password
- Client-side validation feedback
- Submit button and loading states

**S002: Registration Form Validation** [3h]
- Email format validation
- Password strength requirements
- Confirm password matching
- Display validation errors

**S003: User Registration API Endpoint** [5h]
- POST /api/auth/register endpoint
- Request validation
- User creation logic
- Email uniqueness check
- Password hashing

**S004: Registration Database Schema** [2h]
- User model creation
- Database migration
- Email uniqueness constraint
- Timestamps and default values

**S005: Registration Integration** [4h]
- Connect form to API
- Handle success/error responses
- Display success confirmation
- Redirect after successful registration

**Dependencies:**
- S004 (database) must be first
- S003 (API) depends on S004
- S001, S002 (UI) can be parallel
- S005 (integration) depends on all others

**Total: 18 hours across 5 stories**
</story_output>
</example_decomposition>

<success_criteria>
Skill successfully executed when:
- Feature file(s) read and analyzed
- Stories generated with complete structure (description, user story, technical notes, criteria)
- Story index created with dependencies and implementation order
- Sequential numbering applied correctly
- Traceability maintained (story → feature → epic)
- User reviews and approves story breakdown
- All story files saved to configured directory
- Parent feature status updated to `stories_created`
- Clear next step provided (use dev-spec or dev-orchestrator on stories)
</success_criteria>

<example_session>
```
User: /feature-to-stories F001

Skill:
1. Reads agile_docs_directory from CLAUDE.md
2. Reads feature file: features/F001-user-registration.md
3. Analyzes feature components and acceptance criteria
4. Decomposes into 5 stories:
   - S001: Registration Form UI [4h]
   - S002: Registration Form Validation [3h]
   - S003: User Registration API Endpoint [5h]
   - S004: Registration Database Schema [2h]
   - S005: Registration Integration [4h]
5. Creates story files with complete details
6. Creates F001-story-index.md with dependency graph
7. Shows user the story breakdown for review
8. Saves all artifacts after approval
9. Updates F001 status to stories_created

Next: User runs dev-spec on S004 (database schema first based on dependencies)
```
</example_session>