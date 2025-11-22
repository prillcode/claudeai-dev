# Skills Intended Workflow

This document illustrates the high-level workflow showing how agile-skills and dev-skills work together to transform JIRA epics into deployed code.

## Complete Workflow: Epic to Deployment

```mermaid
graph TD
    A[JIRA Epic] -->|Paste epic content| B[epic-feature-creator]
    B -->|Generates| C[Features F001-F00N]
    C -->|Select feature| D[feature-story-creator]
    D -->|Generates| E[Stories S001-S00N]
    E -->|Optional for large stories| F[story-task-creator]
    F -->|Generates| G[Tasks T001-T00N]

    E -->|Ready for spec| H[dev-orchestrator]
    G -->|Ready for spec| H

    H -->|Phase 1: Specification| I[dev-spec]
    I -->|Creates| J[Specification Document]

    H -->|Phase 2: Implementation| K[dev-execute]
    J -->|Input to| K
    K -->|Implements in sub-agent| L[Code Implementation]

    L -->|Provides| M[Testing Steps]
    M -->|User performs| N[Manual Testing]
    N -->|User confirms| O[Archive Completed Work]

    O -->|Ready to commit| P[git-commit-helper]
    P -->|Creates| Q[Conventional Commit]
    Q -->|Result| R[Deployed Feature]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style D fill:#fff4e1
    style F fill:#fff4e1
    style H fill:#e8f5e9
    style I fill:#e8f5e9
    style K fill:#e8f5e9
    style P fill:#e8f5e9
    style R fill:#f3e5f5
```

## Workflow Phases

### Phase 1: Decomposition (agile-skills)
```mermaid
graph LR
    A[Epic] -->|epic-feature-creator| B[Features]
    B -->|feature-story-creator| C[Stories]
    C -->|story-task-creator<br/>optional| D[Tasks]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#fff4e1
```

**Skills involved:**
- **epic-feature-creator**: JIRA epics → Technical features
- **feature-story-creator**: Features → User stories
- **story-task-creator**: Large stories → Sub-tasks (optional)

### Phase 2: Specification (dev-skills)
```mermaid
graph LR
    A[Story/Task] -->|dev-spec| B[Specification]

    style A fill:#fff4e1
    style B fill:#e8f5e9
```

**Skills involved:**
- **dev-spec**: Creates adaptive specifications (lightweight for simple tasks, comprehensive for complex features)

### Phase 3: Implementation (dev-skills)
```mermaid
graph LR
    A[Specification] -->|dev-execute| B[Implementation]
    B --> C[Testing Steps]
    C --> D[User Testing]
    D -->|Confirms| E[Archive]

    style A fill:#e8f5e9
    style B fill:#e8f5e9
    style C fill:#e8f5e9
    style D fill:#e8f5e9
    style E fill:#e8f5e9
```

**Skills involved:**
- **dev-execute**: Implements specification in fresh sub-agent context
- Provides testing steps
- Archives after user confirmation

### Phase 4: Commit (dev-skills)
```mermaid
graph LR
    A[Completed Work] -->|git-commit-helper| B[Conventional Commit]

    style A fill:#e8f5e9
    style B fill:#e8f5e9
```

**Skills involved:**
- **git-commit-helper**: Generates conventional commit messages from git diffs

## Orchestration

### dev-orchestrator: End-to-End Workflow
```mermaid
graph TD
    A[User Request] --> B[dev-orchestrator]
    B --> C[Invokes dev-spec]
    C --> D[Invokes dev-execute]
    D --> E[User Testing]
    E --> F[Optionally invokes git-commit-helper]
    F --> G[Complete]

    style B fill:#e8f5e9
    style C fill:#e8f5e9
    style D fill:#e8f5e9
    style F fill:#e8f5e9
```

**dev-orchestrator** can handle the complete workflow from story/task to deployed code:
- Automatically invokes dev-spec for specification
- Automatically invokes dev-execute for implementation
- Manages testing and completion phases
- Can optionally create commits

## Typical Usage Patterns

### Pattern 1: Full Epic Decomposition
```bash
# Start with epic
/epic-to-features
[Paste JIRA epic]

# Break into stories
/feature-to-stories F001

# Implement each story
/dev-orchestrator S001
/dev-orchestrator S002
/dev-orchestrator S003
```

### Pattern 2: Direct Story Implementation
```bash
# Already have story defined, go straight to implementation
/dev-orchestrator "Implement user login form"
```

### Pattern 3: Manual Step-by-Step
```bash
# Create spec
/dev-spec S001

# Review spec, then implement
/dev-execute 001

# Test, confirm, then commit
/git-commit-helper
```

## Artifact Traceability

```mermaid
graph TD
    A[EPIC-PROJ-123] --> B[F001: Feature]
    A --> C[F002: Feature]
    B --> D[S001: Story]
    B --> E[S002: Story]
    C --> F[S003: Story]
    D --> G[001: Spec]
    E --> H[002: Spec]
    F --> I[003: Spec]
    G --> J[Implementation]
    H --> K[Implementation]
    I --> L[Implementation]
    J --> M[Commit]
    K --> N[Commit]
    L --> O[Commit]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#fff4e1
    style G fill:#e8f5e9
    style H fill:#e8f5e9
    style I fill:#e8f5e9
    style M fill:#f3e5f5
    style N fill:#f3e5f5
    style O fill:#f3e5f5
```

Each artifact maintains references to its parent, creating complete traceability from commit back to original epic.

## Legend

- 🔵 **Blue**: Input (JIRA, user requests)
- 🟡 **Yellow**: agile-skills (decomposition)
- 🟢 **Green**: dev-skills (execution)
- 🟣 **Purple**: Output (deployed code)

---

**Last Updated:** 2025-11-21