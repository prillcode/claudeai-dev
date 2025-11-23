# Product Requirements Document: APDevFlow (Revised)

## Executive Summary

### Product Vision
APDevFlow (AI-Powered DevFlow) is a **lightweight scrum dashboard and AI-powered development workflow accelerator** that helps Product Owners break down features into epics and stories, and helps developers generate implementation specs using AI skills. The platform works standalone or as a companion to existing project management tools like JIRA.

**Created by:** Aaron Prill, AP Dev Solutions
**Brand Identity:** APDevFlow - Where "AP" represents both "Agile Programming" and "Aaron Prill"
**CLI Command:** `devflow` (primary) + `apdev` (alias)

### Core Philosophy

**"Workflow First, Integration Optional"**

APDevFlow is NOT another JIRA plugin. It's a standalone workflow tool that:
- Helps POs plan features using AI-powered breakdown
- Helps developers generate specs and implement code faster
- Optionally syncs with JIRA (but doesn't require it)

### Business Objectives
- **Developer Productivity**: Reduce spec writing time by 70%
- **Planning Efficiency**: Decrease epic breakdown time from hours to minutes
- **Tool Agnostic**: Works with Claude Code, Cursor, or standalone
- **Simple Integration**: Manual JIRA export for MVP, automated later
- **Low Barrier**: No OAuth complexity, just paste a PAT and go

### Success Metrics
- 20+ developers actively using across 3+ teams
- Average spec generation time: < 2 minutes per story
- Epic breakdown time: 3 hours → 15 minutes
- Developer satisfaction: 4.5/5 or higher
- Skill invocation success rate: 95%+
- Cost per developer per month: < $5 (AWS only, no API costs for MVP)

---

## Product Overview

### Problem Statement

**For Product/Planning Teams:**
- Epic and feature breakdown is time-consuming and inconsistent
- Creating detailed user stories requires deep technical understanding
- No standardized process for decomposing work items
- **Existing tools (JIRA) are complex and slow for planning workflows**

**For Developers:**
- Writing implementation specs is repetitive and tedious
- Context switching between project management tools and development environment
- Inconsistent approaches to similar problems across team members
- Manual effort translating requirements into technical specifications
- **Don't want heavy integrations - just want AI assistance for specs**

**For Organizations:**
- Knowledge silos prevent best practices from spreading
- New team members lack templates and patterns
- No way to codify and distribute development workflows
- **Don't want vendor lock-in to specific tools**

### Solution

A **lightweight, UI-first scrum dashboard + CLI workflow tool**:

**1. Planning Dashboard (Web UI)**
- Product Owners create feature requests (paste PRD or summary)
- AI breaks down features → epics → stories using Claude API via Bedrock
- Review, edit, approve workflow
- Export to JIRA/CSV (manual for MVP, automated later)
- Assign stories to developers

**2. Developer CLI + Local Workflow**
- Developers see assigned stories in dashboard
- Export story to local workspace via `devflow start story-123`
- Use Claude Code (or Cursor) skills to generate specs and code
- Upload results back via `devflow finish story-123`

**3. Optional JIRA Integration**
- Personal Access Tokens (not OAuth) for simple setup
- Manual CSV export for MVP
- Automated API creation in Phase 4

### Key Differentiators

**vs. JIRA:**
- Simpler, faster UI focused on planning
- AI-powered breakdown (JIRA doesn't have this)
- Works without JIRA

**vs. Linear:**
- Open source / self-hosted option
- Deeper AI integration via custom skills
- Developer-first CLI workflow

**vs. GitHub Copilot Workspace:**
- Works with any project management tool
- Skills are customizable and shareable
- Not tied to GitHub

---

## Target Users

**Primary: Software Developers (Individual Contributors)**
- Pain points: Spec writing, repetitive tasks, unclear requirements
- Needs: Fast story → spec → code workflows, AI assistance
- Tech level: Comfortable with CLI, git, Claude Code or Cursor
- **Assumption:** Has Bedrock-backed Claude Code access (company-paid)

**Secondary: Product Owners / Scrum Masters**
- Pain points: Epic breakdown complexity, inconsistent story quality
- Needs: AI-powered planning, approval workflows, export to JIRA
- Tech level: Comfortable with web UIs, JIRA power users
- **Assumption:** Doesn't need Claude Code, uses web dashboard only

**Tertiary: Engineering Leadership**
- Pain points: Inconsistent processes, difficult to scale best practices
- Needs: Usage analytics, team standardization, ROI visibility
- Tech level: Strategic oversight, dashboard consumers

---

## Technical Architecture (Revised)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Organization's AWS Account                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Frontend (React SPA)                          │ │
│  │  - Planning Dashboard (PO view)                        │ │
│  │  - Developer Dashboard (Dev view)                      │ │
│  │  - Hosted on CloudFront + S3                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            API Gateway (REST API)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│         │              │              │              │       │
│         ↓              ↓              ↓              ↓       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Planning │  │  Story   │  │ Artifact │  │  User    │   │
│  │  Lambda  │  │  Export  │  │ Manager  │  │  Auth    │   │
│  │          │  │  Lambda  │  │  Lambda  │  │  Lambda  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │              │       │
│         ↓              ↓              ↓              ↓       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    DynamoDB Tables                      │ │
│  │  - Users          - Features       - Epics             │ │
│  │  - Stories        - Artifacts      - Analytics         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        S3 Buckets                                       │ │
│  │  - Story exports    - Artifacts    - PRD uploads       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Secrets Manager                              │ │
│  │  - JIRA PATs (optional, per developer)                 │ │
│  │  - Bedrock credentials for Claude API                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   External Services    │
              ├────────────────────────┤
              │ - JIRA API (optional)  │
              │ - Bedrock Claude API   │
              └────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Developer's Local Environment                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Workspace: ~/repos/myapp-story-123/                   │ │
│  │    .apdevflow/                                          │ │
│  │      - story.md       (exported story content)         │ │
│  │      - context.md     (additional context)             │ │
│  │      - spec.md        (generated by dev-spec)          │ │
│  │    src/               (implementation code)            │ │
│  │    .git/              (git worktree)                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Claude Code + Skills (or Cursor + .cursorrules)       │ │
│  │    ~/.claude/skills/                                    │ │
│  │      - dev-spec/                                        │ │
│  │      - dev-execute/                                     │ │
│  │      - git-commit-helper/                              │ │
│  │    OR                                                   │ │
│  │    ~/.cursor/rules/ (future)                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Architecture Changes from Original PRD

**What's Different:**

1. **No JIRA OAuth complexity** - Use PATs for optional JIRA sync
2. **Standalone data model** - Features/Epics/Stories stored in APDevFlow first
3. **Manual JIRA export** - CSV/bulk import for MVP (API automation later)
4. **Skill agnostic foundation** - Designed for Claude Code, extensible to Cursor
5. **Git worktree integration** - First-class support from day 1
6. **Bedrock for PO workflows** - Claude API via Bedrock for epic/story generation

---

## Data Models (Revised)

### DynamoDB Table Schemas

**FeaturesTable:**
```typescript
{
  TableName: 'apdevflow-features',
  PK: 'ORG#company-id',
  SK: 'FEATURE#feat-001',

  featureId: 'feat-001',
  title: 'Mobile App Redesign',
  description: 'Full feature description...',

  // Source
  prdDocument: 's3://bucket/features/feat-001/prd.md', // Optional uploaded PRD
  createdBy: 'po@company.com',
  createdAt: '2025-11-22T10:00:00Z',

  // Lifecycle
  status: 'draft', // draft, approved, in_progress, complete
  approvedBy: 'tech-lead@company.com',
  approvedAt: '2025-11-22T11:00:00Z',

  // JIRA integration (optional)
  jiraEpicKey: null, // Filled manually or via API (Phase 4)

  // Metadata
  tags: ['mobile', 'ux', 'q1-2025'],

  GSI1PK: 'STATUS#draft',
  GSI1SK: 'CREATED#2025-11-22T10:00:00Z',
}
```

**EpicsTable:**
```typescript
{
  TableName: 'apdevflow-epics',
  PK: 'FEATURE#feat-001',
  SK: 'EPIC#epic-001',

  epicId: 'epic-001',
  featureId: 'feat-001',

  title: 'Login & Authentication Redesign',
  description: 'Detailed epic description...',
  acceptanceCriteria: [
    'Users can log in with email/password',
    'Support OAuth providers',
    'Session management',
  ],

  // AI generation metadata
  generatedByAI: true,
  skillUsed: 'epic-feature-creator',
  modelUsed: 'claude-sonnet-4-5',
  tokensUsed: { input: 3000, output: 5000 },
  generatedAt: '2025-11-22T10:15:00Z',

  // Manual edits
  editedBy: 'po@company.com',
  editedAt: '2025-11-22T10:20:00Z',

  // Lifecycle
  status: 'approved',

  // JIRA integration (optional)
  jiraEpicKey: 'PROJ-100', // Filled by PO after manual creation

  GSI1PK: 'FEATURE#feat-001',
  GSI1SK: 'ORDER#001',
}
```

**StoriesTable:**
```typescript
{
  TableName: 'apdevflow-stories',
  PK: 'EPIC#epic-001',
  SK: 'STORY#story-001',

  storyId: 'story-001',
  epicId: 'epic-001',

  title: 'Implement JWT-based authentication',
  description: 'As a user, I want to log in securely...',
  acceptanceCriteria: [
    'Login endpoint accepts email/password',
    'Returns JWT token on success',
    'Token expires after 24 hours',
  ],

  storyPoints: 8,

  // Assignment
  assignee: 'aaron@company.com',
  assignedAt: '2025-11-22T11:00:00Z',

  // AI generation metadata
  generatedByAI: true,
  skillUsed: 'feature-story-creator',
  generatedAt: '2025-11-22T10:30:00Z',

  // Lifecycle
  status: 'in_progress', // ready, in_progress, blocked, review, done

  // JIRA integration (optional)
  jiraKey: 'PROJ-123', // Filled by PO after manual creation

  // Developer workflow
  exportedToWorkspace: true,
  workspacePath: '~/repos/myapp-story-001/',

  GSI1PK: 'ASSIGNEE#aaron@company.com',
  GSI1SK: 'STATUS#in_progress',
  GSI2PK: 'EPIC#epic-001',
  GSI2SK: 'ORDER#001',
}
```

**ArtifactsTable:**
```typescript
{
  TableName: 'apdevflow-artifacts',
  PK: 'STORY#story-001',
  SK: 'ARTIFACT#spec#v2',

  artifactId: 'artifact-uuid-123',
  storyId: 'story-001',

  // Artifact details
  fileName: 'spec.md',
  contentType: 'markdown',
  fileSize: 4567,
  s3Location: 's3://bucket/artifacts/story-001/spec-v2.md',

  // Skill metadata
  skillUsed: 'dev-spec',
  skillVersion: '1.0.0',

  // Generation metadata
  generatedBy: 'aaron@company.com',
  generatedAt: '2025-11-22T12:00:00Z',

  // Version tracking
  version: 2,
  previousVersionId: 'artifact-uuid-122',

  // Lifecycle
  status: 'draft', // draft, uploaded, attached_to_jira

  // JIRA attachment (optional)
  jiraAttachment: {
    attachmentId: 'jira-attach-123',
    attachedAt: '2025-11-22T13:00:00Z',
  },

  GSI1PK: 'USER#aaron@company.com',
  GSI1SK: 'TIMESTAMP#2025-11-22T12:00:00Z',
}
```

**UsersTable:**
```typescript
{
  TableName: 'apdevflow-users',
  PK: 'USER#aaron@company.com',
  SK: 'PROFILE',

  email: 'aaron@company.com',
  name: 'Aaron Prill',
  role: 'developer', // 'po', 'developer', 'manager'

  // JIRA integration (optional)
  jiraConfig: {
    instance: 'company.atlassian.net',
    patEncrypted: 'encrypted-pat-token', // Personal Access Token
    username: 'aaron@company.com',
  },

  // Preferences
  preferences: {
    workspaceBasePath: '~/repos',
    defaultTool: 'claude-code', // or 'cursor'
    autoOpenVSCode: true,
  },

  // Stats
  stats: {
    storiesCompleted: 15,
    skillInvocations: 45,
    timeSavedMinutes: 1200,
    lastActive: '2025-11-22T14:30:00Z',
  },

  createdAt: '2025-11-01T00:00:00Z',
  updatedAt: '2025-11-22T14:30:00Z',
}
```

---

## Core Workflows

### Workflow 1: PO Creates Feature and Breaks Down into Epics

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: PO opens Planning Dashboard                     │
│         Clicks "New Feature Request"                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Enter Feature Details                           │
│                                                          │
│  Title: Mobile App Redesign                             │
│  Description: [Paste PRD or write summary]              │
│                                                          │
│  Option 1: [Upload PRD.md file]                         │
│  Option 2: [Paste text]                                 │
│                                                          │
│  [✨ Generate Epics with AI]                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Backend Invokes epic-feature-creator Skill      │
│                                                          │
│  Lambda calls Bedrock Claude API:                       │
│  - System prompt: epic-feature-creator skill            │
│  - User message: feature PRD content                    │
│  - Returns: List of 3-5 epics with descriptions         │
│                                                          │
│  Duration: ~30 seconds                                   │
│  Cost: ~$0.15 (Bedrock pricing)                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Review Generated Epics                          │
│                                                          │
│  Feature: Mobile App Redesign                           │
│                                                          │
│  Generated Epics (3):                                   │
│    📦 Epic 1: Login & Authentication Redesign           │
│       Description: Modernize auth flow...               │
│       [Edit] [Delete]                                   │
│                                                          │
│    📦 Epic 2: Dashboard UX Improvements                 │
│       Description: Improve dashboard...                 │
│       [Edit] [Delete]                                   │
│                                                          │
│    📦 Epic 3: Performance Optimization                  │
│       Description: Reduce load times...                 │
│       [Edit] [Delete]                                   │
│                                                          │
│  [+ Add Epic Manually]                                  │
│  [Regenerate All] [Approve]                             │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: PO Approves, Saves to APDevFlow                │
│                                                          │
│  ✅ Feature and 3 Epics saved to DynamoDB               │
│  Status: Approved                                        │
│                                                          │
│  Next Steps:                                             │
│  [Break Down Epic 1 into Stories]                       │
│  [Export to JIRA]                                        │
│  [Continue Later]                                        │
└─────────────────────────────────────────────────────────┘
```

**Time Saved:** 2-3 hours of manual epic breakdown → 5 minutes

---

### Workflow 2: PO Breaks Down Epic into User Stories

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Select Epic from Planning Dashboard             │
│         Epic 1: Login & Authentication Redesign          │
│         [✨ Generate User Stories]                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Backend Invokes feature-story-creator Skill     │
│                                                          │
│  Lambda calls Bedrock Claude API:                       │
│  - System prompt: feature-story-creator skill           │
│  - User message: epic content                           │
│  - Returns: List of 4-8 user stories                    │
│                                                          │
│  Duration: ~45 seconds                                   │
│  Cost: ~$0.08                                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Review Generated Stories                        │
│                                                          │
│  Epic: Login & Authentication Redesign                  │
│                                                          │
│  Generated Stories (5):                                 │
│    ☐ Story 1: Implement JWT-based auth                  │
│       As a user, I want to log in securely...           │
│       Story Points: 8                                   │
│       Assignee: [Unassigned ▼]                          │
│       [Edit] [Delete]                                   │
│                                                          │
│    ☐ Story 2: Add OAuth providers (Google, GitHub)      │
│       As a user, I want to log in with...              │
│       Story Points: 5                                   │
│       Assignee: [Unassigned ▼]                          │
│       [Edit] [Delete]                                   │
│                                                          │
│  ... (3 more stories)                                   │
│                                                          │
│  [+ Add Story Manually]                                 │
│  [Regenerate All] [Approve & Assign]                    │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Assign Stories to Developers                    │
│                                                          │
│  Story 1: Implement JWT auth                            │
│    Assignee: Aaron Prill ✓                              │
│                                                          │
│  Story 2: OAuth providers                               │
│    Assignee: Jane Doe ✓                                 │
│                                                          │
│  Story 3: Password reset                                │
│    Assignee: [Unassigned]                               │
│                                                          │
│  [Save Assignments]                                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Export to JIRA (Manual for MVP)                │
│                                                          │
│  Option A: Export as CSV                                │
│    [📥 Download CSV for JIRA Bulk Import]               │
│    Then: Upload to JIRA manually                        │
│    Then: Copy JIRA ticket IDs back to APDevFlow         │
│                                                          │
│  Option B: Copy JIRA Format                             │
│    [📋 Copy JIRA Bulk Create Format]                    │
│    Paste into JIRA bulk create                          │
│                                                          │
│  Option C: Create Manually (Phase 4 - Auto via API)    │
│    [Create in JIRA] ← Future feature                   │
└─────────────────────────────────────────────────────────┘
```

**Time Saved:** 1-2 hours of manual story creation → 10 minutes

---

### Workflow 3: Developer Processes Assigned Story

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Developer opens APDevFlow Dashboard             │
│         Sees assigned stories                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: View Story Details                              │
│                                                          │
│  📋 Story: Implement JWT-based authentication           │
│     Epic: Login & Authentication Redesign               │
│     Status: Ready for Dev                               │
│     Story Points: 8                                     │
│     JIRA: PROJ-123 (optional)                           │
│                                                          │
│     Description:                                         │
│     As a user, I want to log in securely...            │
│                                                          │
│     Acceptance Criteria:                                │
│     - Login endpoint accepts email/password             │
│     - Returns JWT token on success                      │
│     - Token expires after 24 hours                      │
│                                                          │
│     [📥 Start Work on This Story]                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Developer Clicks "Start Work"                   │
│                                                          │
│  This runs: devflow start story-001                     │
│                                                          │
│  Backend Actions:                                        │
│  1. Create export package                               │
│  2. Write to local workspace                            │
│  3. Create git worktree (if enabled)                    │
│  4. Open in VS Code (if enabled)                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Local Workspace Created                         │
│                                                          │
│  $ devflow start story-001                              │
│                                                          │
│  ✓ Created worktree: ~/repos/myapp-story-001           │
│  ✓ Branch: feature/story-001 (based on main)           │
│  ✓ Exported story to .apdevflow/story.md                │
│  ✓ Opened in VS Code                                    │
│                                                          │
│  Workspace structure:                                    │
│  ~/repos/myapp-story-001/                               │
│    .apdevflow/                                           │
│      story.md          # Story content                  │
│      context.md        # Additional context             │
│      config.json       # Metadata                       │
│    src/                # Source code                    │
│    package.json                                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Developer Uses Claude Code to Generate Spec     │
│                                                          │
│  $ cd ~/repos/myapp-story-001                           │
│  $ code .  # Opens VS Code (already open)               │
│  $ claude-code  # Or use Claude Code in VS Code         │
│                                                          │
│  > I have a story in .apdevflow/story.md. Please use   │
│    the dev-spec skill to create an implementation       │
│    specification.                                        │
│                                                          │
│  Claude Code:                                            │
│  - Reads .apdevflow/story.md                            │
│  - Loads ~/.claude/skills/dev-spec/SKILL.md            │
│  - Generates .apdevflow/spec.md                         │
│                                                          │
│  Duration: ~2 minutes                                    │
│  Cost: $0 (using Bedrock-backed Claude Code)            │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Developer Reviews and Implements                │
│                                                          │
│  $ cat .apdevflow/spec.md                               │
│  # Reviews spec, makes edits                            │
│                                                          │
│  $ claude-code                                          │
│  > Use dev-execute to implement the spec in            │
│    .apdevflow/spec.md                                   │
│                                                          │
│  Claude Code:                                            │
│  - Reads .apdevflow/spec.md                             │
│  - Generates implementation in src/                     │
│                                                          │
│  $ npm test                                             │
│  ✓ All tests passing                                    │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 7: Developer Commits and Uploads                   │
│                                                          │
│  $ git add .                                            │
│  $ git commit -m "feat(auth): implement JWT auth"      │
│  $ git push origin feature/story-001                   │
│                                                          │
│  $ devflow finish story-001                             │
│                                                          │
│  Backend Actions:                                        │
│  1. Read .apdevflow/spec.md from workspace              │
│  2. Upload to S3: s3://.../story-001/spec-v1.md        │
│  3. Create artifact record in DynamoDB                  │
│  4. (Optional) Attach to JIRA ticket if PAT configured │
│  5. Update story status to "In Review"                  │
│  6. Prompt: Remove worktree? [Y/n]                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 8: Dashboard Shows Completion                      │
│                                                          │
│  Story: Implement JWT-based authentication              │
│    Status: In Review ✅                                 │
│    Artifacts:                                            │
│      📄 spec.md (v1) - Uploaded 2m ago                  │
│    Git:                                                  │
│      🌿 feature/story-001 (pushed)                      │
│    Next Steps:                                           │
│      - Create PR                                         │
│      - Request code review                               │
└─────────────────────────────────────────────────────────┘
```

**Time Saved:** 45 minutes of spec writing → 5 minutes

---

## Feature Requirements (Revised for MVP)

### Feature 1: Planning Dashboard (PO View)

**User Story:**
As a Product Owner, I want to create features and break them down into epics and stories using AI, so I can plan sprints faster.

**Requirements:**

1. **Feature Creation UI**
   - Text input for title and description
   - File upload for PRD.md (optional)
   - "Generate Epics" button triggers AI breakdown

2. **Epic Breakdown**
   - Backend invokes `epic-feature-creator` via Bedrock
   - Display 3-5 generated epics
   - Inline editing of epic details
   - Manual add/delete epics

3. **Story Breakdown**
   - Select epic → "Generate Stories"
   - Backend invokes `feature-story-creator` via Bedrock
   - Display 4-8 generated stories
   - Assign stories to developers (dropdown)
   - Inline editing of story details

4. **Export to JIRA (Manual for MVP)**
   - CSV export (JIRA bulk import format)
   - Copy to clipboard (JIRA bulk create format)
   - Instructions shown in UI

**Acceptance Criteria:**
- PO can create feature, generate epics in <1 minute
- Can edit AI-generated content inline
- Can assign stories to developers
- CSV export works with JIRA import
- All data saved to DynamoDB

---

### Feature 2: Developer Dashboard (Dev View)

**User Story:**
As a developer, I want to see my assigned stories and export them to my local workspace, so I can use AI skills to generate specs.

**Requirements:**

1. **My Stories View**
   - List of stories assigned to current user
   - Filter by status (ready, in_progress, blocked, review, done)
   - Sort by priority, story points, created date

2. **Story Detail View**
   - Full story content (title, description, acceptance criteria)
   - Epic context
   - JIRA link (if available)
   - "Start Work" button

3. **Story Actions**
   - Start Work → triggers `devflow start story-123`
   - View Artifacts (uploaded specs, code)
   - Update Status manually

**Acceptance Criteria:**
- Developer sees only their assigned stories
- Story detail view shows all necessary info
- "Start Work" triggers CLI command (or prompts to install CLI)
- Status updates reflect in dashboard

---

### Feature 3: CLI Tool (`devflow`)

**User Story:**
As a developer, I want a CLI tool to export stories to my workspace and upload results, so I can work locally with Claude Code.

**Requirements:**

1. **Installation**
   ```bash
   npm install -g @apdevsolutions/devflow
   # or
   brew install apdevsolutions/tap/devflow
   ```

2. **Authentication**
   ```bash
   devflow auth
   # Prompts for API key or opens browser for OAuth
   ```

3. **Core Commands**
   ```bash
   # Start work on story
   devflow start story-123
   # - Creates worktree ~/repos/myapp-story-123
   # - Exports story to .apdevflow/
   # - Opens VS Code

   # Finish work on story
   devflow finish story-123
   # - Uploads artifacts to S3
   # - Updates story status
   # - Prompts to remove worktree

   # List active stories
   devflow list

   # Sync story content from server
   devflow sync story-123

   # Install/update skills
   devflow skills install
   devflow skills update
   ```

4. **Configuration**
   ```json
   // ~/.apdevflow/config.json
   {
     "apiUrl": "https://api.apdevflow.com",
     "workspaceBasePath": "~/repos",
     "defaultTool": "claude-code",
     "autoOpenVSCode": true,
     "jira": {
       "instance": "company.atlassian.net",
       "pat": "encrypted-token"
     }
   }
   ```

**Acceptance Criteria:**
- CLI installs on macOS, Linux, Windows (WSL)
- `devflow start` creates workspace with correct structure
- `devflow finish` uploads artifacts successfully
- Skill installation works without manual steps

---

### Feature 4: Artifact Management

**User Story:**
As a developer, I want to see all artifacts I've generated for a story, so I can track versions and download them.

**Requirements:**

1. **Artifact Viewer UI** (in Dashboard)
   - List artifacts per story
   - Show version history
   - Download button
   - View diff between versions

2. **Artifact Upload** (from CLI)
   - `devflow finish` uploads .apdevflow/spec.md to S3
   - Creates artifact record in DynamoDB
   - Tracks version number

3. **Optional JIRA Attachment**
   - If JIRA PAT configured, attach to JIRA ticket
   - Add comment: "Spec generated by dev-spec skill"

**Acceptance Criteria:**
- Artifacts are versioned (v1, v2, v3...)
- Can view artifact history
- Can download any version
- JIRA attachment works if PAT configured

---

### Feature 5: Skill Management

**User Story:**
As a developer, I want to install and update APDevFlow skills easily, so I don't have to manually clone repos.

**Requirements:**

1. **Skill Installation**
   ```bash
   devflow skills install
   ```
   - Clones github.com/apdevsolutions/devflow-skills
   - Symlinks to ~/.claude/skills/
   - Tracks version in config

2. **Skill Updates**
   ```bash
   devflow skills update
   ```
   - Pulls latest from skills repo
   - Shows changelog
   - Updates version in config

3. **Skill Registry** (in Dashboard)
   - List available skills
   - Show descriptions
   - Links to documentation

**Acceptance Criteria:**
- Skill installation works without errors
- Skills are usable in Claude Code immediately
- Skill updates don't break existing workflows

---

## Technology Stack (Revised)

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (clean, modern, accessible)
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Hosting**: S3 + CloudFront

### Backend (AWS Serverless)
- **Compute**: Lambda (Node.js 20.x, TypeScript)
- **API**: API Gateway (REST API)
- **Storage**:
  - DynamoDB (6 tables: Features, Epics, Stories, Artifacts, Users, Analytics)
  - S3 (artifacts, PRD uploads, story exports)
- **Auth**: Cognito (user authentication)
- **AI**: Bedrock Claude API (for PO planning workflows)
- **Secrets**: Secrets Manager (JIRA PATs, Bedrock credentials)
- **Monitoring**: CloudWatch + X-Ray

### CLI Tool
- **Language**: TypeScript (compiled to Node.js)
- **Package**: npm package + Homebrew tap
- **Config**: JSON file in ~/.apdevflow/
- **Git**: Uses local git binary for worktree operations

### External Integrations
- **JIRA Cloud API**: Personal Access Tokens (optional)
- **Bedrock Claude API**: For epic/story generation (PO workflows)
- **Claude Code**: Developer tool (local, no API integration needed)

### Development Tools
- **IaC**: AWS CDK (TypeScript)
- **CI/CD**: GitHub Actions
- **Testing**: Vitest (fast, modern Jest alternative)
- **Linting**: ESLint, Prettier, TypeScript strict mode

---

## MVP Phasing (Revised)

### Phase 0: Prerequisites (1-2 days)
**Goal**: Setup development environment

**Tasks:**
- [ ] Create GitHub repos (frontend, backend, CLI)
- [ ] Setup AWS account & CDK project
- [ ] Setup Bedrock access
- [ ] Document setup instructions

**Time**: 4-8 hours

---

### Phase 1: Core Dashboard + AI Planning (Week 1-2)
**Goal**: PO can create features and generate epics/stories using AI

**Frontend:**
- [ ] React app with Tailwind + shadcn/ui
- [ ] Planning Dashboard UI
  - Feature creation form
  - Epic list view with AI generation
  - Story list view with AI generation
- [ ] Basic routing (home, planning, stories)
- [ ] Cognito auth integration

**Backend:**
- [ ] Lambda: Feature CRUD operations
- [ ] Lambda: Epic generation (Bedrock API)
- [ ] Lambda: Story generation (Bedrock API)
- [ ] DynamoDB: Features, Epics, Stories tables
- [ ] S3: PRD uploads

**AI Integration:**
- [ ] Bedrock Claude API setup
- [ ] Load skill prompts (epic-feature-creator, feature-story-creator)
- [ ] Parse AI responses into structured data

**Success Criteria:**
- PO can create feature, paste PRD
- Click "Generate Epics" → AI returns 3-5 epics
- Click "Generate Stories" → AI returns 4-8 stories
- Can edit AI-generated content inline
- Can assign stories to developers
- All data saved to DynamoDB

**Time**: 2 weeks (40-60 hours)

---

### Phase 2: Developer Dashboard + Story Export (Week 3-4)
**Goal**: Developers can see assigned stories and export them

**Frontend:**
- [ ] Developer Dashboard UI
  - My Stories list view
  - Story detail view
  - Filters (status, sprint)
- [ ] "Start Work" button (triggers CLI or shows instructions)

**Backend:**
- [ ] Lambda: Story export package creation
- [ ] Lambda: User management
- [ ] DynamoDB: Users table
- [ ] S3: Story exports

**CLI Tool (Basic):**
- [ ] CLI scaffolding (TypeScript + oclif or yargs)
- [ ] `devflow auth` command
- [ ] `devflow start <story-id>` command
  - Fetch story from API
  - Create workspace directory
  - Export story to .apdevflow/story.md
- [ ] `devflow list` command

**Success Criteria:**
- Developer logs in, sees assigned stories
- Clicks "Start Work" or runs `devflow start story-123`
- Story exported to local workspace
- Workspace has .apdevflow/story.md with correct content

**Time**: 2 weeks (40-50 hours)

---

### Phase 3: Artifact Upload + Git Worktree Integration (Week 5-6)
**Goal**: Developers can upload specs and use git worktrees

**CLI Tool (Enhanced):**
- [ ] `devflow finish <story-id>` command
  - Upload .apdevflow/spec.md to S3
  - Create artifact record via API
  - Update story status
- [ ] Git worktree integration
  - `devflow start` creates worktree
  - `devflow finish` prompts to remove worktree
- [ ] `devflow sync <story-id>` command

**Backend:**
- [ ] Lambda: Artifact upload handling
- [ ] DynamoDB: Artifacts table
- [ ] S3: Artifact storage with versioning

**Frontend:**
- [ ] Artifact viewer UI
  - List artifacts per story
  - Download button
  - Version history

**Success Criteria:**
- Developer runs `devflow finish story-123`
- Spec uploaded to S3
- Artifact visible in dashboard
- Can download artifact from dashboard
- Git worktrees created/removed correctly

**Time**: 2 weeks (35-45 hours)

---

### Phase 4: JIRA Integration (Manual Export) (Week 7)
**Goal**: PO can export stories to JIRA manually

**Frontend:**
- [ ] "Export to JIRA" button
- [ ] Generate CSV in JIRA bulk import format
- [ ] Show instructions for JIRA import
- [ ] Input for JIRA ticket IDs (after manual creation)

**Backend:**
- [ ] Lambda: CSV generation
- [ ] Store JIRA ticket IDs in Stories table

**Success Criteria:**
- PO clicks "Export to JIRA"
- CSV downloads with correct format
- Can upload to JIRA bulk import
- Can paste ticket IDs back into APDevFlow

**Time**: 1 week (15-20 hours)

---

### Phase 5: Skill Installation + Documentation (Week 8)
**Goal**: Easy skill installation and great docs

**CLI Tool:**
- [ ] `devflow skills install` command
  - Clone skills repo
  - Symlink to ~/.claude/skills/
  - Track version
- [ ] `devflow skills update` command

**Documentation:**
- [ ] User guide (PO workflows)
- [ ] Developer guide (using CLI + Claude Code)
- [ ] API documentation
- [ ] Video walkthrough (optional)

**Success Criteria:**
- Developer runs `devflow skills install`
- Skills available in Claude Code immediately
- Documentation covers all workflows
- New user can onboard in <30 minutes

**Time**: 1 week (20-25 hours)

---

### Phase 6: Analytics + Polish (Week 9-10)
**Goal**: Usage analytics and production-ready

**Frontend:**
- [ ] Analytics dashboard (manager view)
  - Active users
  - Stories/epics processed
  - Time saved estimates
  - Skill usage stats

**Backend:**
- [ ] DynamoDB: Analytics table
- [ ] Lambda: Analytics aggregation
- [ ] CloudWatch: Dashboards + alarms

**Polish:**
- [ ] Error handling improvements
- [ ] Loading states
- [ ] Better UX feedback
- [ ] Performance optimization

**Success Criteria:**
- Managers can see analytics
- Error handling is robust
- UI is polished and fast
- Ready for production use

**Time**: 2 weeks (30-40 hours)

---

## Post-MVP Roadmap

### Phase 7: JIRA API Auto-Creation (Week 11-12)
- JIRA Personal Access Token setup in UI
- Auto-create tickets via JIRA API
- Two-way sync (JIRA → APDevFlow status updates)

### Phase 8: Cursor Support (Week 13-14)
- Adapt skills for .cursorrules format
- `devflow skills install --tool cursor`
- Cursor-specific workflows

### Phase 9: Team Collaboration (Week 15-16)
- Shared artifact library
- Team templates
- Peer review workflows
- Comments and discussions

### Phase 10: Advanced Git Workflows (Week 17-18)
- PR creation helper
- CI/CD status tracking in dashboard
- Auto commit message generation

---

## Cost Estimation (Revised)

### AWS Infrastructure (Per Organization)

**Monthly Costs:**
```
Lambda Invocations:
  - Planning workflows: 10,000/month
  - Story exports: 5,000/month
  - Cost: ~$0.50

DynamoDB:
  - On-demand pricing
  - 6 tables, light-moderate traffic
  - Cost: ~$3-5

S3:
  - 10 GB storage (artifacts, exports)
  - 5k requests/month
  - Cost: ~$1

API Gateway:
  - 15k requests/month
  - Cost: ~$0.25

CloudFront:
  - 50 GB data transfer
  - Cost: ~$5

Bedrock Claude API (Sonnet):
  - 20 epic generations/month @ $0.15 = $3
  - 100 story generations/month @ $0.08 = $8
  - Cost: ~$11/month

Secrets Manager:
  - 5 secrets (JIRA PATs)
  - Cost: ~$2

CloudWatch:
  - Logs + metrics
  - Cost: ~$2

Total AWS + Bedrock: ~$25-30/month
```

### Per Developer Cost

**For team of 20 developers:**
- Total cost: $30/month
- Per developer: **$1.50/month**

**ROI:**
- Time saved per developer: ~8 hours/month
- Value of time: $50/hour (conservative)
- Monthly value: 20 devs × 8 hrs × $50 = **$8,000**
- Monthly cost: $30
- **ROI: 26,600%**

---

## Security & Compliance

### Authentication
- **Web Dashboard**: AWS Cognito user pools
- **CLI Tool**: API key or OAuth token
- **JIRA Integration**: Personal Access Tokens (user-specific)

### Data Protection
- **Encryption at Rest**: S3 SSE, DynamoDB encryption
- **Encryption in Transit**: TLS 1.2+
- **Secrets**: AWS Secrets Manager with KMS
- **API Security**: API Gateway with Cognito authorizer, rate limiting

### JIRA PAT Handling
- Never log PATs
- Encrypt before storing in Secrets Manager
- Rotate regularly (prompt user every 90 days)
- User can revoke at any time

### Data Retention
- Stories/Epics: Indefinite (or until user deletes)
- Artifacts: 2 years default (configurable)
- Logs: 30 days
- Soft delete (never hard delete user data)

---

## Success Metrics (Revised)

### Adoption Metrics (First 3 Months)
- 20+ active developers
- 50+ stories processed per week
- 10+ epics generated per month

### Efficiency Metrics
- Avg spec generation time: <2 min (vs. 45 min manual)
- Epic breakdown time: <5 min (vs. 2-3 hours manual)
- Story creation time: <10 min (vs. 1-2 hours manual)

### Quality Metrics
- AI-generated content acceptance rate: >80%
- Stories requiring major revision: <20%
- User satisfaction: 4.5/5+

### ROI Metrics
- Total time saved: >30 hrs/week (team of 20)
- Cost per hour saved: **<$0.01**
- Break-even: Week 1

---

## Risks & Mitigations (Revised)

### Risk 1: Developer Adoption (CLI Tool)
**Impact**: Low CLI usage, manual copy/paste instead
**Mitigation:**
- Make CLI installation dead simple (brew, npm)
- Clear documentation with examples
- Video walkthrough
- In-app prompts to install CLI

### Risk 2: AI Quality Variability
**Impact**: Poor epic/story breakdowns, low trust
**Mitigation:**
- Human-in-the-loop review (always)
- Inline editing capabilities
- "Regenerate" option
- Track acceptance rate, improve prompts

### Risk 3: JIRA Manual Export Friction
**Impact**: POs don't want manual CSV export
**Mitigation:**
- Make CSV export one-click
- Clear instructions in UI
- Phase 7: Auto-creation via API
- For MVP: Set expectation that it's manual

### Risk 4: Skill Installation Complexity
**Impact**: Developers struggle to install skills
**Mitigation:**
- Automated `devflow skills install`
- Symlink approach (no manual setup)
- Troubleshooting guide
- Support Slack channel

### Risk 5: Bedrock API Costs
**Impact**: Higher than expected AI costs
**Mitigation:**
- Set monthly budget alerts
- Rate limit per user (max 10 epic generations/day)
- Cost dashboard for visibility
- Optimize prompts to reduce tokens

---

## Open Questions (Revised)

1. **Multi-Org Support:**
   - Should MVP support multiple organizations in one deployment?
   - Or one deployment per organization?
   - **Decision:** One org per deployment for MVP

2. **Skill Versioning:**
   - How to handle breaking changes in skills?
   - Semantic versioning for skills?
   - **Decision:** Track skill version in artifacts, allow rollback

3. **Offline Mode:**
   - Can developers work offline after export?
   - **Decision:** Yes, export is standalone. No sync until online.

4. **Windows Support:**
   - Full Windows support or WSL only?
   - **Decision:** WSL for MVP, native Windows later

5. **Team Permissions:**
   - Role-based access control (PO vs. Dev vs. Manager)?
   - **Decision:** Basic roles for MVP (po, developer, manager)

---

## Appendix

### A. JIRA Personal Access Token Setup

**User Guide:**
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it: "APDevFlow"
4. Copy the token
5. In APDevFlow dashboard: Settings > JIRA Integration > Paste token
6. Save

**Token Storage:**
- Encrypted with AWS KMS
- Stored in Secrets Manager
- Per-user (not shared)

### B. Git Worktree Convention

**Directory Structure:**
```
~/repos/
  myapp/                  # Main repo (main branch)
  myapp-story-001/        # Worktree for story-001
    .apdevflow/
      story.md
      spec.md
    src/
    .git/                 # Git worktree metadata
  myapp-story-002/        # Worktree for story-002
```

**Cleanup:**
```bash
# After PR merged
devflow finish story-001
# Prompts: Remove worktree? [Y/n]
# If yes: removes ~/repos/myapp-story-001/

# Manual cleanup
devflow clean
# Finds merged worktrees, prompts to remove
```

### C. Skill Adaptation for Claude API

**epic-feature-creator skill (API version):**
```typescript
// Backend loads skill
const skillPrompt = await fs.readFile(
  './skills/agile-skills/epic-feature-creator/SKILL.md',
  'utf-8'
);

// Extract core instructions (remove file I/O sections)
const apiSkillPrompt = adaptSkillForAPI(skillPrompt);

// Invoke Bedrock
const response = await bedrockClient.invokeModel({
  modelId: 'anthropic.claude-sonnet-4-5-v2',
  contentType: 'application/json',
  body: JSON.stringify({
    anthropic_version: 'bedrock-2023-05-31',
    max_tokens: 4000,
    system: apiSkillPrompt,
    messages: [{
      role: 'user',
      content: `Feature Request:\n\n${featureDescription}`
    }]
  })
});
```

---

**Document Version**: 2.0 (Revised)
**Last Updated**: November 22, 2025
**Author**: Aaron Prill, AP Dev Solutions
**Product**: APDevFlow (AI-Powered DevFlow)
**Status**: Ready for MVP Implementation

**Major Changes from v1.0:**
- UI-first approach (standalone scrum dashboard)
- JIRA integration simplified (PATs, manual export for MVP)
- Git worktree integration as first-class feature
- Multi-tool vision (Claude Code primary, Cursor later)
- Revised data models (Features/Epics/Stories in APDevFlow)
- Simplified MVP scope (6 phases, 10 weeks)
- Cost reduction ($30/month vs. $50/month)
