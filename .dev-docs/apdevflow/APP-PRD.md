# Product Requirements Document: APDevFlow

## Executive Summary

### Product Vision
APDevFlow (AI-Powered DevFlow) is a developer-first workflow automation platform that bridges JIRA Cloud with Claude AI skills, enabling teams to leverage AI-powered development workflows for agile planning and implementation. The system empowers developers to export JIRA tickets to their local workspace and invoke specialized Claude skills for specification generation, implementation, and code quality—dramatically reducing cognitive load and accelerating delivery.

**Created by:** Aaron Prill, AP Dev Solutions  
**Brand Identity:** APDevFlow - Where "AP" represents both "Agile Programming" and "Aaron Prill"  
**CLI Command:** `devflow` (primary) + `apdev` (alias)

### Business Objectives
- **Developer Productivity**: Reduce spec writing time by 70%
- **Planning Efficiency**: Decrease epic breakdown time from hours to minutes
- **Code Quality**: Standardize implementation patterns across teams
- **Skill Reusability**: Make Claude skills accessible to entire development organization
- **Multi-Tenant Ready**: Design for SaaS deployment to multiple organizations

### Success Metrics
- 50+ developers actively using across 5+ teams
- Average spec generation time: < 2 minutes per story
- Epic breakdown time: 3 hours → 20 minutes
- Developer satisfaction: 4.5/5 or higher
- Skill invocation success rate: 95%+
- Cost per developer per month: < $30

---

## Product Overview

### Problem Statement

**For Product/Planning Teams:**
- Epic and feature breakdown is time-consuming and inconsistent
- Creating detailed user stories requires deep technical understanding
- No standardized process for decomposing work items

**For Developers:**
- Writing implementation specs is repetitive and tedious
- Context switching between JIRA and development environment
- Inconsistent approaches to similar problems across team members
- Manual effort translating requirements into technical specifications

**For Organizations:**
- Knowledge silos prevent best practices from spreading
- New team members lack templates and patterns
- No way to codify and distribute development workflows
- Difficult to measure AI/automation ROI

### Solution

A **two-mode workflow automation platform**:

1. **Planning Mode**: Product Owners and Scrum Masters use the dashboard to break down epics → features → stories using Claude skills, with approval workflows before pushing to JIRA.

2. **Developer Mode**: Individual developers export their assigned JIRA tickets to local workspaces and invoke Claude skills (dev-spec, dev-execute, git-commit-helper) to accelerate implementation.

The platform is **organization-agnostic**, deployable to any company's AWS account, with developer-by-developer JIRA OAuth ensuring proper attribution and security.

### Target Users

**Primary: Software Developers**
- Pain points: Spec writing, repetitive tasks, context switching
- Needs: Fast ticket → code workflows, standardized patterns, AI assistance
- Tech level: Comfortable with CLI, git, Claude Code

**Secondary: Product Owners / Scrum Masters**
- Pain points: Epic breakdown complexity, inconsistent story quality
- Needs: Batch processing epics, review/approval workflows
- Tech level: Moderate technical skills, JIRA power users

**Tertiary: Engineering Leadership**
- Pain points: Inconsistent processes, difficult to scale best practices
- Needs: Usage analytics, team standardization, ROI visibility
- Tech level: Strategic oversight, dashboard consumers

---

## Technical Architecture Overview

### System Architecture (Organization-Deployed)

```
┌─────────────────────────────────────────────────────────────┐
│                    Organization's AWS Account                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                Frontend (React SPA)                     │ │
│  │  - Hosted on CloudFront + S3                           │ │
│  │  - Developer dashboard & Planning dashboard            │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            API Gateway (REST API)                       │ │
│  └────────────────────────────────────────────────────────┘ │
│         │              │              │              │       │
│         ↓              ↓              ↓              ↓       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  JIRA    │  │  Skill   │  │ Artifact │  │  User    │   │
│  │  Sync    │  │  Invoke  │  │ Manager  │  │  Auth    │   │
│  │ Lambda   │  │  Lambda  │  │  Lambda  │  │  Lambda  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │              │       │
│         ↓              ↓              ↓              ↓       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    DynamoDB Tables                      │ │
│  │  - Users          - Tickets        - Artifacts         │ │
│  │  - SkillRuns      - Approvals      - Analytics         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │        S3 Buckets                                       │ │
│  │  - Skill outputs    - Exported tickets                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Secrets Manager                              │ │
│  │  - JIRA OAuth credentials (per developer)              │ │
│  │  - Claude API keys (optional, see strategy below)      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │   External Services    │
              ├────────────────────────┤
              │ - JIRA Cloud API       │
              │ - Claude API (optional)│
              └────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Developer's Local Environment                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Workspace: ~/jira-exports/PROJ-123/                   │ │
│  │    - ticket.md        (exported JIRA content)          │ │
│  │    - spec.md          (generated by dev-spec)          │ │
│  │    - implementation/  (generated by dev-execute)       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Claude Code + Skills                                   │ │
│  │    ~/.claude/skills/                                    │ │
│  │      - epic-feature-creator/                           │ │
│  │      - feature-story-creator/                          │ │
│  │      - dev-spec/                                        │ │
│  │      - dev-execute/                                     │ │
│  │      - git-commit-helper/                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Tenant Considerations

**Organization Isolation:**
- Each organization deploys to their own AWS account
- No shared infrastructure between organizations
- JIRA OAuth credentials scoped to organization's JIRA instance

**Future SaaS Evolution:**
- Current: Self-deployed per organization
- Future: Single AWS account with tenant isolation
- Migration path: Keep architecture tenant-aware from day 1

**Deployment Model:**
```typescript
interface OrganizationDeployment {
  organizationId: string;
  awsAccountId: string;
  jiraInstance: string; // e.g., "acme.atlassian.net"
  deployedAt: Date;
  
  // Future: billing, usage limits, etc.
}
```

---

## Claude Integration Strategy

### The Two Approaches

#### **Approach 1: Claude Code (Local Developer Execution)** ⭐ RECOMMENDED FOR MVP

**How It Works:**
1. Developer has Claude Code installed locally
2. Your custom skills installed in `~/.claude/skills/`
3. Dashboard exports JIRA ticket to local workspace as markdown
4. Developer invokes skill via Claude Code CLI or interactive prompt
5. Results saved locally, developer manually uploads to JIRA or dashboard

**Pros:**
- ✅ Zero Claude API costs (developers use their own Claude subscriptions)
- ✅ Skills already working in Claude Code environment
- ✅ Developer has full control over execution
- ✅ No credential management complexity
- ✅ Works offline (after initial export)
- ✅ Aligns with existing developer workflow

**Cons:**
- ❌ Requires each developer to have Claude subscription
- ❌ Manual step to invoke skills (not fully automated)
- ❌ Harder to track usage/analytics centrally
- ❌ Inconsistent execution environments across developers

**Cost Model:**
- Free for the organization (developers pay for their own Claude)
- Each developer needs Claude Pro ($20/month) or Team/Enterprise

**Implementation:**
```typescript
// Developer workflow
interface ClaudeCodeWorkflow {
  // 1. Dashboard exports ticket
  export(ticketId: string): Promise<LocalWorkspace> {
    const ticket = await jira.getTicket(ticketId);
    const workspace = createLocalWorkspace(ticketId);
    
    // Write ticket.md
    fs.writeFileSync(
      `${workspace}/ticket.md`,
      formatTicketAsMarkdown(ticket)
    );
    
    return workspace;
  }
  
  // 2. Developer runs manually
  // $ cd ~/jira-exports/PROJ-123
  // $ claude-code
  // > I have a story in ticket.md, use dev-spec to create spec
  
  // 3. Upload result back
  upload(workspace: LocalWorkspace): Promise<void> {
    // Developer manually or via CLI helper
    // Uploads spec.md back to dashboard/JIRA
  }
}
```

**Prerequisites for Developers:**
- Claude Code installed
- Skills repository cloned and installed
- APDevFlow CLI tool (lightweight Python/Node script)

---

#### **Approach 2: Claude API (Centralized Execution)**

**How It Works:**
1. Organization obtains Claude API key
2. Dashboard invokes skills via Claude Messages API
3. Skills loaded as system prompts or uploaded artifacts
4. Results returned to dashboard automatically
5. Auto-saved to S3 and optionally pushed to JIRA

**Pros:**
- ✅ Fully automated (one-click skill execution)
- ✅ No developer prerequisites (works from browser)
- ✅ Centralized usage tracking and analytics
- ✅ Consistent execution environment
- ✅ Batch processing capabilities

**Cons:**
- ❌ Organization pays Claude API costs
- ❌ Need to adapt skills to work via API
- ❌ Requires credential management
- ❌ Skills not identical to Claude Code environment

**Cost Model:**
```typescript
// Claude Sonnet 4.5 pricing (as of Nov 2025)
const CLAUDE_PRICING = {
  input: 0.003,  // $3 per 1M tokens
  output: 0.015, // $15 per 1M tokens
};

// Example: dev-spec skill
interface SkillCostEstimate {
  skill: 'dev-spec';
  avgInputTokens: 2000;   // Story + context
  avgOutputTokens: 4000;  // Generated spec
  costPerRun: 0.066;      // $0.066 per spec
}

// Monthly estimate for 10 developers
const monthlyEstimate = {
  developersCount: 10,
  avgStoriesPerDevPerSprint: 5,
  sprintsPerMonth: 2,
  totalSpecsPerMonth: 100,
  totalCost: 6.60, // $6.60/month for specs alone
};

// Full workflow estimate (epic → features → stories → specs)
const fullWorkflowCost = {
  epics: 2,           // 2 epics/month @ $0.20 each = $0.40
  features: 20,       // 20 features @ $0.10 each = $2.00
  stories: 100,       // 100 stories @ $0.08 each = $8.00
  specs: 100,         // 100 specs @ $0.066 each = $6.60
  totalPerMonth: 17,  // ~$17/month total
  costPerDeveloper: 1.70, // $1.70 per developer per month
};
```

**Implementation:**
```typescript
interface ClaudeAPIWorkflow {
  // Invoke skill via Messages API
  async invokeSkill(params: {
    skillName: string;
    ticketContent: JiraTicket;
    context?: any;
  }): Promise<SkillResult> {
    
    // Load skill instructions
    const skillPrompt = await loadSkillPrompt(params.skillName);
    
    // Prepare context
    const systemPrompt = `
      ${skillPrompt}
      
      You are helping a developer work on a JIRA ticket.
      Use the skill instructions above to process the ticket.
    `;
    
    const userMessage = formatTicketForSkill(
      params.ticketContent,
      params.context
    );
    
    // Call Claude API
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 8000,
      system: systemPrompt,
      messages: [
        { role: 'user', content: userMessage }
      ]
    });
    
    return {
      success: true,
      output: response.content[0].text,
      tokensUsed: {
        input: response.usage.input_tokens,
        output: response.usage.output_tokens,
      },
      cost: calculateCost(response.usage),
    };
  }
}
```

**Skill Adaptation:**
Since your skills are designed for Claude Code (with file system access), we'd need to:
1. Extract the core prompt logic from SKILL.md
2. Pass ticket content as message content (not file reads)
3. Return results as text (not file writes)

```typescript
// Example: Adapting dev-spec skill
interface SkillAdapter {
  // Original skill expects files
  // ~/workspace/ticket.md → read and process
  
  // API version gets content directly
  adaptDevSpec(ticket: JiraTicket): ClaudeMessage {
    return {
      role: 'user',
      content: `
        # Task
        Generate an implementation specification for this user story.
        
        # Story Details
        ${ticket.summary}
        
        ${ticket.description}
        
        # Acceptance Criteria
        ${ticket.acceptanceCriteria}
        
        # Instructions
        [Content from your dev-spec/SKILL.md here]
      `
    };
  }
}
```

---

### **Recommended Hybrid Approach**

**MVP: Claude Code (Local)**
- Developers use their own Claude subscriptions
- Dashboard only does export/import of ticket content
- Zero API costs for organization
- Faster to build (no skill adaptation needed)

**Phase 2: Optional Claude API**
- Add "Auto-process" button for POs/planning teams
- Organization pays API costs for automated epic breakdowns
- Developers still use local Claude Code for dev-spec/dev-execute
- Best of both worlds

```typescript
interface HybridConfiguration {
  // Per organization setting
  planningMode: 'claude-api'; // POs use API for epic breakdowns
  developerMode: 'claude-code'; // Devs use local Claude Code
  
  // API key only needed for planning
  claudeApiKey?: string;
  
  // Usage tracking
  apiUsage: {
    enabled: boolean;
    monthlyBudget: number;
    alertThreshold: number;
  };
}
```

---

## Feature Requirements

### Feature 1: Developer Ticket Export

**User Story:**
As a developer, I want to export my JIRA tickets to my local workspace, so I can process them with Claude skills without manual copy/paste.

**Requirements:**

1. **"My Tickets" Dashboard**
   ```typescript
   interface MyTicketsView {
     filters: {
       assignedToMe: boolean;
       status: JiraStatus[];
       sprint: string;
     };
     tickets: JiraTicket[];
     actions: {
       exportTicket: (id: string) => LocalExport;
       exportBatch: (ids: string[]) => LocalExport[];
       openWorkspace: (id: string) => void;
     };
   }
   ```

2. **Export Formats**
   - Markdown (primary): ticket.md with structured content
   - JSON (optional): ticket.json with full JIRA data
   - Context file: context.md with related tickets/history

3. **Export Location**
   ```
   ~/jira-exports/
     PROJ-123/
       ticket.md          # Main ticket content
       context.md         # Related tickets, comments, history
       config.json        # Metadata (ticket ID, last sync, etc.)
       .generated/        # Skill outputs go here
         spec.md
         implementation/
   ```

4. **CLI Helper Tool**
   ```bash
   # Install
   npm install -g @apdevsolutions/devflow
   
   # Authenticate
   devflow auth
   
   # Export ticket
   devflow export PROJ-123
   # Creates ~/jira-exports/PROJ-123/
   
   # Sync (update with latest JIRA data)
   devflow sync PROJ-123
   
   # Upload results back
   devflow upload PROJ-123/spec.md --attach
   ```

**Acceptance Criteria:**
- Export creates well-formatted markdown with all necessary context
- CLI tool works on macOS, Linux, Windows (WSL)
- Export includes: summary, description, acceptance criteria, comments, linked issues
- Config file tracks last sync time
- Upload command attaches files to JIRA ticket

---

### Feature 2: Skill Recommendation Engine

**User Story:**
As a developer, I want the dashboard to suggest which Claude skills to use for each ticket, so I don't have to remember the skill catalog.

**Requirements:**

1. **Smart Recommendations**
   ```typescript
   interface SkillRecommendation {
     recommendSkills(ticket: JiraTicket): Suggestion[] {
       const suggestions: Suggestion[] = [];
       
       // Epic without features
       if (ticket.type === 'Epic' && !hasChildren(ticket)) {
         suggestions.push({
           skill: 'epic-feature-creator',
           confidence: 0.95,
           reason: 'Epic has no child features yet',
           estimatedTime: '2-3 minutes',
           costEstimate: '$0.20',
         });
       }
       
       // Story assigned to me, no spec
       if (ticket.assignee === currentUser && 
           ticket.type === 'Story' &&
           !hasAttachment(ticket, 'spec.md')) {
         suggestions.push({
           skill: 'dev-spec',
           confidence: 0.90,
           reason: 'Story needs implementation specification',
           estimatedTime: '1-2 minutes',
           costEstimate: 'Free (local Claude Code)',
         });
       }
       
       // Story with spec, ready to implement
       if (hasAttachment(ticket, 'spec.md') && 
           ticket.status === 'In Progress') {
         suggestions.push({
           skill: 'dev-execute',
           confidence: 0.85,
           reason: 'Spec ready for implementation',
           estimatedTime: '3-5 minutes',
           costEstimate: 'Free (local Claude Code)',
         });
       }
       
       return suggestions.sort((a, b) => b.confidence - a.confidence);
     }
   }
   ```

2. **Skill Metadata Registry**
   ```typescript
   const SKILL_REGISTRY = {
     'epic-feature-creator': {
       displayName: 'Epic → Features',
       description: 'Break down epic into technical features',
       inputType: 'Epic',
       outputType: 'Feature[]',
       estimatedTime: '2-3 min',
       requiredFields: ['summary', 'description'],
       optionalFields: ['businessGoals', 'constraints'],
       executionMode: 'claude-api', // or 'claude-code'
       skillPath: '/skills/agile-skills/epic-feature-creator',
       documentation: 'https://github.com/prillcode/claudeai-dev/...',
     },
     'dev-spec': {
       displayName: 'Generate Spec',
       description: 'Create implementation specification',
       inputType: 'Story',
       outputType: 'Specification',
       estimatedTime: '1-2 min',
       requiredFields: ['summary', 'acceptanceCriteria'],
       optionalFields: ['technicalContext', 'dependencies'],
       executionMode: 'claude-code',
       skillPath: '/skills/dev-skills/dev-spec',
     },
     // ... other skills
   };
   ```

3. **UI Display**
   ```
   ┌──────────────────────────────────────────────────┐
   │ PROJ-123: Add user authentication                │
   │ 📌 Story • Assigned to you • Updated 2h ago      │
   │                                                   │
   │ 💡 Suggested Skills:                             │
   │                                                   │
   │ ⭐ dev-spec (Generate Spec)                      │
   │    Confidence: 90%                               │
   │    Time: 1-2 min • Free (local Claude Code)     │
   │    [Export & Launch Claude Code]                │
   │                                                   │
   │ 📝 dev-execute (Implement)                       │
   │    Confidence: 60%                               │
   │    Available after spec is created              │
   │    [Not ready yet]                              │
   └──────────────────────────────────────────────────┘
   ```

**Acceptance Criteria:**
- Recommendations appear within 100ms
- Confidence scores are accurate (validated against user actions)
- Top recommendation is correct 80%+ of the time
- Can manually override and choose any skill
- Shows prerequisites (e.g., "needs spec.md first")

---

### Feature 3: Planning Dashboard (Epic Breakdown)

**User Story:**
As a Product Owner, I want to break down epics into features and stories using Claude skills, with approval workflow before pushing to JIRA.

**Requirements:**

1. **Planning View**
   ```typescript
   interface PlanningDashboard {
     // Current sprint/backlog
     epics: Epic[];
     features: Feature[];
     stories: Story[];
     
     // Batch actions
     actions: {
       selectEpics: (ids: string[]) => void;
       breakdownEpics: (epicIds: string[]) => Promise<BreakdownResult>;
       reviewResults: (results: BreakdownResult) => void;
       approveAndPush: (results: BreakdownResult) => Promise<void>;
     };
   }
   ```

2. **Batch Breakdown Workflow**
   ```
   1. Select Epics → 2. Process → 3. Review → 4. Approve → 5. Push to JIRA
   
   Step 1: Select
   ┌────────────────────────────────────────────┐
   │ ☑ EPIC-1: Mobile app redesign              │
   │ ☑ EPIC-2: API performance improvements     │
   │ ☐ EPIC-3: Security enhancements            │
   │                                             │
   │ [Process Selected (2 epics)]               │
   └────────────────────────────────────────────┘
   
   Step 2: Processing
   ┌────────────────────────────────────────────┐
   │ Breaking down epics...                     │
   │                                             │
   │ ✅ EPIC-1 → 5 features generated          │
   │ 🔄 EPIC-2 → Processing... 50%             │
   │                                             │
   │ Estimated time: 30 seconds remaining       │
   └────────────────────────────────────────────┘
   
   Step 3: Review
   ┌────────────────────────────────────────────┐
   │ EPIC-1: Mobile app redesign                │
   │   ✨ Feature 1.1: Login screen redesign    │
   │   ✨ Feature 1.2: Dashboard UX update      │
   │   ✨ Feature 1.3: Settings modernization   │
   │   ✨ Feature 1.4: Onboarding flow          │
   │   ✨ Feature 1.5: Performance optimization │
   │                                             │
   │ [Edit] [Regenerate] [Approve]              │
   └────────────────────────────────────────────┘
   ```

3. **Approval Workflow**
   ```typescript
   interface ApprovalWorkflow {
     // Who can approve
     approvers: {
       epicBreakdown: ['product-owner', 'tech-lead'];
       featureStories: ['product-owner'];
       devSpec: ['developer']; // Auto-approved by ticket owner
     };
     
     // Approval states
     states: {
       pending: 'Awaiting approval';
       approved: 'Ready to push to JIRA';
       rejected: 'Needs revision';
       pushed: 'Created in JIRA';
     };
     
     // Notifications
     notify(approvers: User[], item: GeneratedItem): void;
   }
   ```

4. **Diff View Before Push**
   ```
   ┌─────────────────────────────────────────────────┐
   │ Changes to be created in JIRA:                  │
   │                                                  │
   │ + Feature PROJ-234: Login screen redesign       │
   │   Parent: EPIC-1                                │
   │   Story points: 13                              │
   │   Sprint: Sprint 24                             │
   │                                                  │
   │ + Feature PROJ-235: Dashboard UX update         │
   │   Parent: EPIC-1                                │
   │   Story points: 8                               │
   │   Sprint: Sprint 24                             │
   │                                                  │
   │ Total: 2 features, estimated 21 story points    │
   │                                                  │
   │ [❌ Cancel] [✏️ Edit] [✅ Create in JIRA]      │
   └─────────────────────────────────────────────────┘
   ```

**Acceptance Criteria:**
- Can batch process up to 10 epics at once
- Review UI shows all generated features before JIRA creation
- Can edit generated content inline
- Can regenerate individual features
- Approval requires explicit action (not auto-push)
- JIRA creation is atomic (all or nothing)
- Links child features to parent epic correctly

---

### Feature 4: Artifact Management

**User Story:**
As a developer, I want to see all generated artifacts (specs, code) associated with a ticket, so I can track what's been created and access it easily.

**Requirements:**

1. **Artifact Storage Model**
   ```typescript
   interface Artifact {
     id: string;
     ticketId: string; // PROJ-123
     skillUsed: string; // dev-spec, dev-execute
     
     // Content
     content: string | Buffer;
     contentType: 'markdown' | 'code' | 'json';
     fileName: string; // spec.md, implementation.ts
     
     // Metadata
     generatedBy: string; // Developer email
     generatedAt: Date;
     version: number; // Support re-generation
     
     // Storage
     s3Location: string; // s3://bucket/artifacts/PROJ-123/spec-v2.md
     jiraAttachment?: {
       attachmentId: string;
       attachedAt: Date;
     };
     
     // Lifecycle
     status: 'draft' | 'approved' | 'attached';
     approvedBy?: string;
     approvedAt?: Date;
   }
   ```

2. **Artifact Viewer UI**
   ```
   ┌──────────────────────────────────────────────────┐
   │ PROJ-123: Add user authentication                │
   │                                                   │
   │ 📚 Generated Artifacts (3)                       │
   │                                                   │
   │ 📄 spec.md (v2)                                  │
   │    Generated by: aaron@company.com               │
   │    Skill: dev-spec                               │
   │    Created: Nov 21, 2025 10:30 AM               │
   │    Status: ✅ Attached to JIRA                  │
   │    [👁 View] [⬇️ Download] [🔗 JIRA Link]      │
   │                                                   │
   │ 📁 implementation.zip (v1)                       │
   │    Generated by: aaron@company.com               │
   │    Skill: dev-execute                            │
   │    Created: Nov 21, 2025 11:45 AM               │
   │    Status: 📝 Draft                             │
   │    [👁 View] [⬇️ Download] [📤 Attach to JIRA] │
   │                                                   │
   │ 📝 commit-message.txt (v1)                       │
   │    Generated by: aaron@company.com               │
   │    Skill: git-commit-helper                      │
   │    Created: Nov 21, 2025 2:15 PM                │
   │    Status: 📝 Draft                             │
   │    [👁 View] [📋 Copy]                          │
   └──────────────────────────────────────────────────┘
   ```

3. **Version Control**
   - Track multiple versions of same artifact (spec v1, v2, v3)
   - Can revert to previous version
   - Can compare versions (diff view)
   - Can see "why regenerated" (user notes)

4. **Attachment to JIRA**
   ```typescript
   interface JiraAttachmentService {
     async attachArtifact(params: {
       ticketId: string;
       artifactId: string;
       comment?: string;
     }): Promise<void> {
       const artifact = await getArtifact(params.artifactId);
       
       // Upload to JIRA
       const attachmentId = await jiraClient.addAttachment(
         params.ticketId,
         artifact.content,
         artifact.fileName
       );
       
       // Add comment
       if (params.comment) {
         await jiraClient.addComment(
           params.ticketId,
           `${params.comment}\n\nGenerated by: ${artifact.skillUsed}`
         );
       }
       
       // Update artifact record
       await updateArtifact(params.artifactId, {
         jiraAttachment: {
           attachmentId,
           attachedAt: new Date(),
         },
         status: 'attached',
       });
     }
   }
   ```

**Acceptance Criteria:**
- All generated artifacts are saved and retrievable
- Can view artifact history (all versions)
- Can download any artifact
- Can attach to JIRA with one click
- Can compare artifact versions
- S3 storage is organized by ticket ID
- Artifacts are soft-deleted (never hard-deleted)

---

### Feature 5: Usage Analytics

**User Story:**
As an Engineering Manager, I want to see analytics on skill usage and developer productivity, so I can measure ROI and identify adoption patterns.

**Requirements:**

1. **Metrics Tracked**
   ```typescript
   interface UsageMetrics {
     // Per developer
     developer: {
       email: string;
       ticketsProcessed: number;
       skillInvocations: {
         [skillName: string]: number;
       };
       timeSaved: number; // Estimated hours
       artifactsGenerated: number;
     };
     
     // Per skill
     skill: {
       name: string;
       totalInvocations: number;
       successRate: number;
       avgExecutionTime: number;
       avgTokens: {
         input: number;
         output: number;
       };
       costTotal: number; // If using Claude API
     };
     
     // Per team
     team: {
       name: string;
       members: number;
       activeUsers: number;
       epicsProcessed: number;
       storiesProcessed: number;
       timeSavedTotal: number;
     };
   }
   ```

2. **Analytics Dashboard**
   ```
   ┌──────────────────────────────────────────────────┐
   │ 📊 Analytics - Last 30 Days                      │
   │                                                   │
   │ 👥 Active Users: 23/28 developers (82%)         │
   │ 🎯 Tickets Processed: 156 stories, 12 epics     │
   │ ⏱️ Time Saved: ~87 hours (3.8 hrs/dev)          │
   │ 💰 Cost: $0 (all Claude Code)                   │
   │                                                   │
   │ Top Skills:                                      │
   │   1. dev-spec: 89 invocations (57%)             │
   │   2. epic-feature-creator: 34 invocations (22%) │
   │   3. feature-story-creator: 22 invocations (14%)│
   │                                                   │
   │ [View Detailed Reports]                          │
   └──────────────────────────────────────────────────┘
   ```

3. **Time Saved Estimation**
   ```typescript
   const TIME_SAVINGS_ESTIMATES = {
     'epic-feature-creator': {
       manualTime: 120, // 2 hours manually
       aiTime: 10,      // 10 minutes with AI + review
       savedPerRun: 110, // 110 minutes saved
     },
     'feature-story-creator': {
       manualTime: 60,  // 1 hour
       aiTime: 8,
       savedPerRun: 52,
     },
     'dev-spec': {
       manualTime: 45,  // 45 minutes
       aiTime: 5,
       savedPerRun: 40,
     },
     'dev-execute': {
       manualTime: 180, // 3 hours
       aiTime: 20,
       savedPerRun: 160,
     },
   };
   ```

4. **Export Reports**
   - CSV export of all metrics
   - Weekly email summary to managers
   - Monthly executive report (PDF)

**Acceptance Criteria:**
- Metrics update in near real-time (<5 min lag)
- Can filter by date range, team, developer
- Time saved calculations are conservative (underestimate)
- Charts are clear and actionable
- Can drill down into individual skill invocations

---

## Detailed Workflow Mappings

### Workflow 1: Developer Processes Story with dev-spec

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Developer views their dashboard                 │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Sees PROJ-123 assigned to them                  │
│         Status: To Do                                    │
│         Suggested Skill: dev-spec (90% confidence)       │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Clicks "Export & Launch Claude Code"            │
│                                                          │
│ Backend Actions:                                         │
│  1. Fetch full ticket from JIRA API                     │
│  2. Fetch related context (linked tickets, comments)    │
│  3. Generate markdown export                            │
│  4. Create local workspace: ~/jira-exports/PROJ-123/   │
│  5. Write files:                                         │
│     - ticket.md (main content)                          │
│     - context.md (additional context)                   │
│     - config.json (metadata)                            │
│  6. Open workspace in VS Code (optional)                │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Developer in local workspace                    │
│                                                          │
│ $ cd ~/jira-exports/PROJ-123                            │
│ $ code .  # Opens VS Code                               │
│ $ claude-code  # Starts Claude Code                     │
│                                                          │
│ > I have a story in ticket.md. Please use the dev-spec │
│   skill to create an implementation specification.      │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: Claude Code executes dev-spec skill             │
│                                                          │
│ Claude reads:                                            │
│  - ticket.md (story content)                            │
│  - context.md (additional context)                      │
│  - ~/.claude/skills/dev-spec/SKILL.md (instructions)   │
│                                                          │
│ Claude generates:                                        │
│  - spec.md (implementation specification)               │
│                                                          │
│ Duration: ~2 minutes                                     │
│ Cost: $0 (using developer's Claude subscription)        │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Developer reviews spec.md                       │
│                                                          │
│ Makes any needed edits                                   │
│ Validates against acceptance criteria                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 7: Upload spec back to dashboard                   │
│                                                          │
│ $ devflow upload spec.md --attach                       │
│                                                          │
│ Backend Actions:                                         │
│  1. Read spec.md from local workspace                   │
│  2. Upload to S3: s3://.../PROJ-123/spec-v1.md         │
│  3. Create artifact record in DynamoDB                  │
│  4. Attach to JIRA ticket (optional, based on --attach) │
│  5. Add JIRA comment: "Spec generated by dev-spec"     │
│  6. Update dashboard UI to show artifact                │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 8: Dashboard shows artifact                        │
│                                                          │
│ PROJ-123:                                                │
│   📄 spec.md (v1) - Attached to JIRA ✅                │
│   Next suggested skill: dev-execute (85%)               │
└─────────────────────────────────────────────────────────┘
```

**Time Breakdown:**
- Manual spec writing: ~45 minutes
- With AI assistance: ~5 minutes (2 min generation + 3 min review)
- **Time saved: 40 minutes** per story

---

### Workflow 2: PO Breaks Down Epic (Claude API)

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: PO opens Planning Dashboard                     │
│         Sees 3 unprocessed epics                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 2: Selects EPIC-1 and EPIC-2                       │
│         Clicks "Break Down Epics"                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 3: Backend processes batch                         │
│                                                          │
│ For each epic:                                           │
│  1. Fetch epic from JIRA                                │
│  2. Fetch related context                               │
│  3. Load epic-feature-creator skill                     │
│  4. Invoke Claude API with skill + epic content         │
│  5. Parse response → list of features                   │
│  6. Save to DynamoDB (pending approval)                 │
│                                                          │
│ Duration: ~3 minutes for 2 epics                         │
│ Cost: ~$0.40 total                                       │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 4: Review screen shows results                     │
│                                                          │
│ EPIC-1: Mobile app redesign                             │
│   ✨ Feature: Login screen redesign (8 pts)            │
│   ✨ Feature: Dashboard UX update (5 pts)              │
│   ✨ Feature: Settings modernization (5 pts)           │
│   ✨ Feature: Onboarding flow (8 pts)                  │
│   ✨ Feature: Performance optimization (13 pts)        │
│                                                          │
│ Total: 5 features, 39 story points                      │
│                                                          │
│ [Edit] [Regenerate] [Approve & Create in JIRA]         │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 5: PO reviews and edits                            │
│                                                          │
│ - Adjusts story points on Feature 3                     │
│ - Adds sprint assignment                                │
│ - Adds custom field values                              │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 6: Clicks "Approve & Create in JIRA"               │
│                                                          │
│ Backend Actions:                                         │
│  1. Validate all features                               │
│  2. Create JIRA issues via API (batch)                  │
│  3. Link features to parent epic                        │
│  4. Add labels/components                               │
│  5. Add comment: "Generated by epic-feature-creator"    │
│  6. Update approval records                             │
│  7. Send notification to team                           │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Step 7: Confirmation & next steps                       │
│                                                          │
│ ✅ Created 5 features in JIRA                           │
│                                                          │
│ Next: Break down features into stories?                 │
│ [Yes, continue] [No, done for now]                      │
└─────────────────────────────────────────────────────────┘
```

**Time Breakdown:**
- Manual epic breakdown: ~2-3 hours
- With AI assistance: ~15 minutes (3 min generation + 12 min review/edit)
- **Time saved: ~2.5 hours** per epic

---

### Workflow 3: Developer Full Workflow (Epic → Code)

```
Scenario: Developer assigned to implement full epic

┌─────────────────────────────────────────────────────────┐
│ Starting Point: EPIC-3 assigned to developer            │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Epic → Features                                │
│                                                          │
│ $ devflow export EPIC-3                                 │
│ $ cd ~/jira-exports/EPIC-3                              │
│ $ claude-code                                           │
│ > Use epic-feature-creator to break this down           │
│                                                          │
│ Result: 4 features defined in features.md               │
│                                                          │
│ $ devflow create-features features.md                   │
│ # Creates PROJ-201, PROJ-202, PROJ-203, PROJ-204       │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Feature → Stories                              │
│                                                          │
│ $ devflow export PROJ-201                               │
│ $ cd ~/jira-exports/PROJ-201                            │
│ $ claude-code                                           │
│ > Use feature-story-creator for this feature            │
│                                                          │
│ Result: 6 user stories in stories.md                    │
│                                                          │
│ $ devflow create-stories stories.md                     │
│ # Creates PROJ-211, PROJ-212, ... PROJ-216             │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Story → Spec → Code                            │
│                                                          │
│ For each story (PROJ-211, etc):                         │
│                                                          │
│ $ devflow export PROJ-211                               │
│ $ cd ~/jira-exports/PROJ-211                            │
│ $ claude-code                                           │
│ > Use dev-spec to create spec                           │
│                                                          │
│ Result: spec.md                                          │
│                                                          │
│ > Use dev-execute to implement this spec                │
│                                                          │
│ Result: implementation files created                     │
│                                                          │
│ $ devflow upload spec.md implementation/ --attach       │
│ $ git add .                                             │
│ $ git commit  # Uses git-commit-helper skill            │
└─────────────────────────────────────────────────────────┘
```

**Total Time:**
- Manual: ~20+ hours (epic → features → stories → specs → implementation)
- With AI: ~4-6 hours (mostly review, validation, testing)
- **Time saved: 14-16 hours** per epic

---

## Data Models

### DynamoDB Table Schemas

**UsersTable:**
```typescript
{
  TableName: 'apdevflow-users',
  PK: 'USER#aaron@company.com',
  SK: 'PROFILE',
  
  email: 'aaron@company.com',
  name: 'Aaron Prill',
  role: 'developer', // 'developer' | 'product-owner' | 'manager'
  
  jiraAccount: {
    accountId: 'jira-account-id',
    oauthTokenEncrypted: 'encrypted-token',
    refreshToken: 'encrypted-refresh',
    tokenExpiry: '2025-12-21T10:00:00Z',
  },
  
  preferences: {
    defaultExportPath: '~/jira-exports',
    autoAttachSpecs: true,
    notificationsEnabled: true,
  },
  
  stats: {
    ticketsProcessed: 45,
    skillInvocations: 67,
    timeSavedMinutes: 2400,
    lastActive: '2025-11-21T14:30:00Z',
  },
  
  createdAt: '2025-10-01T00:00:00Z',
  updatedAt: '2025-11-21T14:30:00Z',
}
```

**TicketsTable:**
```typescript
{
  TableName: 'apdevflow-tickets',
  PK: 'TICKET#PROJ-123',
  SK: 'METADATA',
  
  jiraId: 'PROJ-123',
  jiraKey: 'PROJ-123',
  type: 'Story', // 'Epic' | 'Feature' | 'Story' | 'Task' | 'Bug'
  
  summary: 'Add user authentication',
  description: 'Full description...',
  acceptanceCriteria: '- Criterion 1\n- Criterion 2',
  
  assignee: 'aaron@company.com',
  reporter: 'po@company.com',
  status: 'In Progress',
  storyPoints: 8,
  sprint: 'Sprint 24',
  
  // Related items
  parentId: 'PROJ-100', // Epic or Feature
  linkedIssues: ['PROJ-122', 'PROJ-124'],
  
  // Sync metadata
  lastSyncedAt: '2025-11-21T10:00:00Z',
  jiraUpdatedAt: '2025-11-21T09:45:00Z',
  
  // Full JIRA payload (cached)
  jiraData: { /* full JIRA JSON */ },
  
  GSI1PK: 'ASSIGNEE#aaron@company.com',
  GSI1SK: 'STATUS#In Progress',
}
```

**ArtifactsTable:**
```typescript
{
  TableName: 'apdevflow-artifacts',
  PK: 'TICKET#PROJ-123',
  SK: 'ARTIFACT#spec#v2',
  
  artifactId: 'uuid-123',
  ticketId: 'PROJ-123',
  
  // Artifact details
  fileName: 'spec.md',
  contentType: 'markdown',
  fileSize: 4567,
  s3Location: 's3://bucket/artifacts/PROJ-123/spec-v2.md',
  
  // Skill metadata
  skillUsed: 'dev-spec',
  skillVersion: '1.0.0',
  
  // Generation metadata
  generatedBy: 'aaron@company.com',
  generatedAt: '2025-11-21T10:30:00Z',
  executionTime: 45.2, // seconds
  tokensUsed: {
    input: 2000,
    output: 4000,
  },
  cost: 0.066, // dollars
  
  // Version tracking
  version: 2,
  previousVersionId: 'uuid-122',
  regenerationReason: 'Updated acceptance criteria',
  
  // Lifecycle
  status: 'attached', // 'draft' | 'approved' | 'attached'
  approvedBy: 'tech-lead@company.com',
  approvedAt: '2025-11-21T10:45:00Z',
  
  // JIRA integration
  jiraAttachment: {
    attachmentId: 'jira-attach-123',
    attachedAt: '2025-11-21T10:50:00Z',
    attachmentUrl: 'https://company.atlassian.net/...',
  },
  
  GSI1PK: 'USER#aaron@company.com',
  GSI1SK: 'TIMESTAMP#2025-11-21T10:30:00Z',
}
```

**SkillInvocationsTable:**
```typescript
{
  TableName: 'apdevflow-skill-invocations',
  PK: 'USER#aaron@company.com',
  SK: 'INVOCATION#2025-11-21T10:30:00Z',
  
  invocationId: 'uuid-456',
  
  // Skill details
  skillName: 'dev-spec',
  skillVersion: '1.0.0',
  executionMode: 'claude-code', // 'claude-code' | 'claude-api'
  
  // Context
  ticketId: 'PROJ-123',
  userId: 'aaron@company.com',
  
  // Execution
  status: 'success', // 'success' | 'failed' | 'timeout'
  startTime: '2025-11-21T10:28:00Z',
  endTime: '2025-11-21T10:30:15Z',
  durationSeconds: 135,
  
  // Usage (if Claude API)
  tokensUsed: {
    input: 2000,
    output: 4000,
  },
  cost: 0.066,
  
  // Result
  artifactId: 'uuid-123',
  errorMessage: null,
  
  // Analytics
  timeSavedMinutes: 40, // Estimated
  
  GSI1PK: 'SKILL#dev-spec',
  GSI1SK: 'TIMESTAMP#2025-11-21T10:30:00Z',
}
```

**ApprovalsTable:**
```typescript
{
  TableName: 'apdevflow-approvals',
  PK: 'APPROVAL#pending',
  SK: 'ARTIFACT#uuid-123',
  
  approvalId: 'uuid-789',
  artifactId: 'uuid-123',
  ticketId: 'PROJ-123',
  
  // Request
  requestedBy: 'aaron@company.com',
  requestedAt: '2025-11-21T11:00:00Z',
  
  // Approvers
  approvers: ['tech-lead@company.com', 'po@company.com'],
  approvalType: 'epic-breakdown', // 'epic-breakdown' | 'feature-stories' | 'dev-spec'
  
  // Status
  status: 'pending', // 'pending' | 'approved' | 'rejected'
  approvedBy: null,
  approvedAt: null,
  rejectionReason: null,
  
  // Content preview
  summary: 'Epic breakdown: 5 features generated',
  
  GSI1PK: 'APPROVER#tech-lead@company.com',
  GSI1SK: 'STATUS#pending',
}
```

---

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: Zustand or React Query
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Hosting**: S3 + CloudFront

### Backend (AWS Serverless)
- **Compute**: Lambda (Node.js 20.x, TypeScript)
- **API**: API Gateway (REST API)
- **Storage**: 
  - DynamoDB (5 tables)
  - S3 (artifacts, exports)
- **Auth**: Cognito (user authentication)
- **Secrets**: Secrets Manager (JIRA OAuth, Claude API)
- **Monitoring**: CloudWatch + X-Ray

### External Integrations
- **JIRA Cloud API**: OAuth 2.0
- **Claude API**: Anthropic Messages API (optional)
- **Claude Code**: Local developer tool (required for MVP)

### Development Tools
- **IaC**: AWS CDK (TypeScript)
- **CI/CD**: GitHub Actions
- **Testing**: Jest, React Testing Library
- **Linting**: ESLint, Prettier

---

## MVP Phasing

### Phase 0: Prerequisites (Week 0)
**Goal**: Setup development environment
- [ ] Create GitHub repository
- [ ] Setup AWS account & profile
- [ ] Install dependencies
- [ ] Document setup instructions

**Time**: 2-4 hours

---

### Phase 1: Core Infrastructure (Week 1)
**Goal**: Basic JIRA integration + ticket export

**Features:**
- [ ] JIRA OAuth setup (developer-by-developer)
- [ ] User authentication (Cognito)
- [ ] Basic React dashboard
- [ ] "My Tickets" view (read-only)
- [ ] Export single ticket to markdown
- [ ] CLI tool: `jira-bridge export PROJ-123`

**Backend:**
- [ ] Lambda: JIRA sync
- [ ] Lambda: Ticket export
- [ ] DynamoDB: Users, Tickets tables
- [ ] S3: Exports bucket

**Success Criteria:**
- Developer can log in with JIRA OAuth
- Can view their assigned tickets
- Can export ticket to `~/jira-exports/PROJ-123/ticket.md`
- Markdown export is well-formatted and complete

**Time**: 1 week (30-40 hours)

---

### Phase 2: Skill Recommendations (Week 2)
**Goal**: Smart skill suggestions

**Features:**
- [ ] Skill recommendation engine
- [ ] Display suggested skills per ticket
- [ ] Skill metadata registry
- [ ] "Launch Claude Code" button (opens workspace)
- [ ] Basic artifact tracking (manual upload)

**Backend:**
- [ ] Lambda: Skill recommendation logic
- [ ] DynamoDB: Artifacts table
- [ ] S3: Artifact storage

**Success Criteria:**
- Dashboard shows relevant skill suggestions (80%+ accuracy)
- Developer can launch Claude Code from dashboard
- Can manually upload generated spec.md via CLI

**Time**: 1 week (25-35 hours)

---

### Phase 3: Artifact Management (Week 3)
**Goal**: Track and display generated artifacts

**Features:**
- [ ] Artifact viewer UI
- [ ] Version tracking
- [ ] Attach to JIRA button
- [ ] Download artifacts
- [ ] CLI: `jira-bridge upload spec.md --attach`

**Backend:**
- [ ] Lambda: Artifact upload
- [ ] Lambda: JIRA attachment
- [ ] DynamoDB: Artifact versioning

**Success Criteria:**
- All generated artifacts are visible in dashboard
- Can attach artifact to JIRA with one click
- Can view artifact history/versions

**Time**: 1 week (20-30 hours)

---

### Phase 4: Planning Dashboard (Week 4)
**Goal**: Epic breakdown for POs

**Features:**
- [ ] Planning view (separate from developer view)
- [ ] Select epics for processing
- [ ] Claude API integration (epic-feature-creator)
- [ ] Review generated features
- [ ] Approve & push to JIRA

**Backend:**
- [ ] Lambda: Claude API skill invoker
- [ ] Lambda: Batch JIRA creation
- [ ] DynamoDB: Approvals table
- [ ] Secrets Manager: Claude API key

**Success Criteria:**
- PO can select epic and generate features
- Features are reviewable before JIRA creation
- Can batch create features in JIRA

**Time**: 1.5 weeks (35-45 hours)

---

### Phase 5: Analytics & Polish (Week 5-6)
**Goal**: Usage tracking and production readiness

**Features:**
- [ ] Analytics dashboard
- [ ] Usage metrics per developer/skill
- [ ] Time saved calculations
- [ ] Export reports (CSV)
- [ ] Error handling & logging
- [ ] User documentation

**Backend:**
- [ ] DynamoDB: SkillInvocations table
- [ ] Lambda: Analytics aggregation
- [ ] CloudWatch: Dashboards & alarms

**Success Criteria:**
- Managers can see usage analytics
- Error handling is robust
- Documentation is complete

**Time**: 2 weeks (40-50 hours)

---

## Post-MVP Enhancements

### Phase 6: Advanced Developer Workflow
- Git worktree integration
- Automated commit messages
- PR creation helper
- CI/CD status tracking

### Phase 7: Team Collaboration
- Shared artifact library
- Team templates
- Peer review workflows
- Skill sharing marketplace

### Phase 8: Multi-Tenant SaaS
- Organization isolation
- Billing integration
- Admin portal
- White-label deployment

---

## Security & Compliance

### Authentication & Authorization

**JIRA OAuth:**
- OAuth 2.0 flow (3-legged)
- Per-developer tokens (not shared)
- Encrypted at rest in Secrets Manager
- Auto-refresh token handling

**User Authentication:**
- AWS Cognito user pools
- MFA optional (recommended)
- Session management

**API Security:**
- API Gateway with Cognito authorizer
- Rate limiting per user
- Request validation

### Data Protection

**Encryption:**
- At rest: S3 SSE, DynamoDB encryption
- In transit: TLS 1.2+
- Secrets: AWS Secrets Manager with KMS

**Data Retention:**
- Tickets: Sync from JIRA (ephemeral cache)
- Artifacts: 2 years default
- Logs: 30 days

**PII Handling:**
- User emails stored (necessary for JIRA integration)
- No credit card data
- JIRA content treated as sensitive

### Compliance

**GDPR (if applicable):**
- Right to access: API endpoint for user data export
- Right to deletion: Delete user account + artifacts
- Data portability: Export artifacts as ZIP

**SOC 2 (future):**
- Audit logging
- Access controls
- Incident response plan

---

## Cost Estimation

### AWS Infrastructure (Per Organization)

**Monthly Costs:**
```
Lambda Invocations:
  - Avg: 50,000 requests/month
  - Cost: ~$1

DynamoDB:
  - On-demand pricing
  - 5 tables, moderate traffic
  - Cost: ~$5-10

S3:
  - 50 GB storage (artifacts)
  - 10k requests/month
  - Cost: ~$2

API Gateway:
  - 50k requests/month
  - Cost: ~$0.50

CloudFront:
  - 100 GB data transfer
  - Cost: ~$10

Secrets Manager:
  - 10 secrets (JIRA OAuth per dev)
  - Cost: ~$4

CloudWatch:
  - Logs + metrics
  - Cost: ~$5

Total AWS: $27.50 - $37.50/month
```

### Claude API (Optional, Planning Mode Only)

If using Claude API for epic breakdowns:
```
Monthly estimate:
  - 10 epics/month @ $0.20 each = $2
  - 50 features/month @ $0.10 each = $5
  - 100 stories/month @ $0.08 each = $8

Total Claude API: ~$15/month
```

### Total Cost Per Organization
- **MVP (Claude Code only)**: $27.50 - $37.50/month
- **With Claude API**: $42.50 - $52.50/month

**Per Developer:**
- MVP: $1-2/month (assuming 20 developers)
- With Claude API: $2-3/month

---

## Success Metrics

### Adoption Metrics
- Active users: 70%+ of dev team
- Tickets processed: 50+ per week
- Skill invocations: 100+ per week

### Efficiency Metrics
- Avg spec generation time: <2 min
- Epic breakdown time: <20 min
- Time saved per developer: >3 hrs/sprint

### Quality Metrics
- Skill success rate: >95%
- Generated specs requiring major revision: <20%
- User satisfaction: 4.5/5+

### ROI Metrics
- Total time saved: >50 hrs/week (team of 20)
- Cost per hour saved: <$1
- Break-even: <1 month

---

## Risks & Mitigations

### Risk 1: Developer Adoption
**Impact**: Low usage, wasted investment
**Mitigation:**
- Strong onboarding documentation
- Demo videos showing value
- Champion developers in each team
- Gradual rollout (start with 1 team)

### Risk 2: Claude Code Dependency
**Impact**: Developers without Claude subscriptions can't use
**Mitigation:**
- Organization can pay for Team licenses
- Phase 2: Add Claude API fallback
- Clear communication of prerequisites

### Risk 3: JIRA API Rate Limits
**Impact**: Sync failures, degraded UX
**Mitigation:**
- Aggressive caching (DynamoDB)
- Rate limit monitoring
- Backoff & retry logic
- Webhook-based sync (future)

### Risk 4: Skill Quality Variability
**Impact**: Poor AI outputs, low trust
**Mitigation:**
- Human-in-the-loop review (always)
- Confidence scoring
- Feedback loop for skill improvement
- Version control for skills

### Risk 5: Cost Overruns (Claude API)
**Impact**: Unexpected bills
**Mitigation:**
- Start with Claude Code (zero API cost)
- Set budgets & alerts
- Rate limiting per user
- Cost dashboard for visibility

---

## Open Questions

1. **Skill Distribution:**
   - How do developers install/update skills?
   - Git submodule? npm package? Manual clone?

2. **Workspace Conventions:**
   - Should we enforce `~/jira-exports/` or allow customization?
   - Support Windows paths?

3. **JIRA Permissions:**
   - What if developer can't create features/stories?
   - Handle permission errors gracefully?

4. **Offline Support:**
   - Can developers work offline after export?
   - Sync conflicts when back online?

5. **Team Conventions:**
   - Different teams use JIRA differently (workflows, fields)
   - How to make this flexible?

---

## Appendix

### A. Claude Integration Deep Dive

**Claude Code Approach:**
```typescript
// What happens when developer runs Claude Code

// 1. Claude Code reads workspace
const workspace = {
  files: [
    '~/jira-exports/PROJ-123/ticket.md',
    '~/jira-exports/PROJ-123/context.md',
  ],
  skills: [
    '~/.claude/skills/dev-spec/',
    '~/.claude/skills/dev-execute/',
  ],
};

// 2. Developer prompt
"I have a story in ticket.md. Use dev-spec to create a specification."

// 3. Claude Code:
//    - Reads ticket.md
//    - Loads dev-spec/SKILL.md
//    - Generates spec.md
//    - Writes to workspace

// 4. Developer reviews and uploads
$ jira-bridge upload spec.md --attach
```

**Claude API Approach:**
```typescript
// What happens when PO clicks "Break Down Epic"

// 1. Backend fetches epic
const epic = await jira.getEpic('EPIC-1');

// 2. Load skill
const skillPrompt = await fs.readFile(
  './skills/epic-feature-creator/SKILL.md'
);

// 3. Invoke Claude API
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 8000,
  system: skillPrompt,
  messages: [{
    role: 'user',
    content: formatEpicForSkill(epic),
  }],
});

// 4. Parse response
const features = parseFeatures(response.content[0].text);

// 5. Save for review
await saveForApproval(features);
```

### B. JIRA OAuth Flow

```typescript
// 1. User clicks "Connect JIRA"
// 2. Redirect to JIRA OAuth
const authUrl = `https://auth.atlassian.com/authorize?` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `response_type=code&` +
  `scope=read:jira-work write:jira-work`;

// 3. User approves
// 4. JIRA redirects back with code
// 5. Exchange code for token
const tokenResponse = await fetch('https://auth.atlassian.com/oauth/token', {
  method: 'POST',
  body: JSON.stringify({
    grant_type: 'authorization_code',
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    code: authCode,
    redirect_uri: REDIRECT_URI,
  }),
});

// 6. Store encrypted token
await secretsManager.createSecret({
  Name: `jira-token-${userId}`,
  SecretString: JSON.stringify({
    accessToken: tokenData.access_token,
    refreshToken: tokenData.refresh_token,
    expiresAt: Date.now() + tokenData.expires_in * 1000,
  }),
});
```

### C. Skill Metadata Example

```yaml
# epic-feature-creator/SKILL.md metadata

name: epic-feature-creator
version: 1.0.0
author: Aaron Prill
description: Transform JIRA epics into technical feature breakdowns

inputs:
  - name: epic
    type: JiraEpic
    required: true
    fields:
      - summary
      - description
      - businessGoals (optional)

outputs:
  - name: features
    type: Feature[]
    format: markdown
    schema:
      - title (string)
      - description (string)
      - storyPoints (number)
      - acceptanceCriteria (string[])

execution:
  mode: claude-api | claude-code
  estimatedTime: 120s
  averageTokens:
    input: 3000
    output: 5000

examples:
  - input: examples/epic-input.md
    output: examples/epic-output.md
```

---

**Document Version**: 1.0  
**Last Updated**: November 21, 2025  
**Author**: Aaron Prill, AP Dev Solutions  
**Product**: APDevFlow (AI-Powered DevFlow)  
**Status**: Draft - Ready for Implementation
