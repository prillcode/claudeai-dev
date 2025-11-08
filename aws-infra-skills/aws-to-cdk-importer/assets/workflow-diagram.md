# AWS to CDK Importer - Workflow Diagram

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         AWS to CDK Importer                             │
│                         Orchestrator Workflow                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                                    │
                                    ▼

                        User Provides Configuration
                    ┌───────────────────────────────┐
                    │ • AWS Profile & Region        │
                    │ • Resource Type Filters       │
                    │ • Organization Strategy       │
                    │ • Output Directory            │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃          5-Phase Sequential Workflow                   ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
           Phase 1              Phase 2              Phase 3
         Discovery          Code Generation       Organization
                │                   │                   │
                │                   │                   │
                └───────────────────┼───────────────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                        ▼                       ▼
                   Phase 4                  Phase 5
              Import Configs             Summary Report
                        │                       │
                        │                       │
                        └───────────┬───────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Complete CDK Project         │
                    │  Ready for cdk import         │
                    └───────────────────────────────┘
```

## Detailed Phase Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Phase 1: Resource Discovery                                           │
│  Skill: aws-resource-discovery                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

    Input: AWS Profile, Region, Filters
      │
      ├──> Connect to AWS (boto3)
      │
      ├──> Enumerate Resources
      │    • Lambda Functions
      │    • DynamoDB Tables
      │    • S3 Buckets
      │    • IAM Roles
      │    • And more...
      │
      ├──> Apply Filters
      │    • Resource Type Filter
      │    • Tag Filter
      │    • Name Pattern Filter
      │
      └──> Serialize to JSON

    Output: discovery/resources.json
            {
              "lambda": [...],
              "dynamodb": [...],
              "s3": [...]
            }

                        │
                        ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Phase 2: CDK Code Generation                                          │
│  Skill: cdk-code-generator                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

    Input: resources.json, Generation Mode
      │
      ├──> Parse Resource Inventory
      │
      ├──> For Each Resource:
      │    │
      │    ├──> Generate TypeScript Construct
      │    │    • Reference Mode: from* methods
      │    │    • Full Mode: Constructors
      │    │
      │    ├──> Map AWS Properties → CDK Properties
      │    │
      │    └──> Resolve Cross-Resource References
      │
      ├──> Generate Dependencies Manifest
      │
      └──> Generate Metadata

    Output: cdk-generated/
            ├── constructs/
            │   ├── lambdas/*.ts
            │   ├── dynamodb/*.ts
            │   └── s3/*.ts
            ├── dependencies.json
            └── metadata.json

                        │
                        ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Phase 3: Stack Organization                                           │
│  Skill: cdk-stack-organizer                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

    Input: Generated Constructs, Organization Strategy
      │
      ├──> Analyze Constructs
      │
      ├──> Apply Organization Strategy
      │    │
      │    ├──> Layer Strategy
      │    │    • compute-stack
      │    │    • data-stack
      │    │    • storage-stack
      │    │
      │    ├──> Service Strategy
      │    │    • lambda-stack
      │    │    • dynamodb-stack
      │    │    • s3-stack
      │    │
      │    ├──> Tag Strategy
      │    │    • Group by tag value
      │    │
      │    └──> Custom Strategy
      │         • User-defined rules
      │
      ├──> Create Stack Files
      │
      ├──> Generate CDK App Entry Point
      │
      └──> Create Project Configuration
           • cdk.json
           • package.json
           • tsconfig.json

    Output: cdk-organized/
            ├── bin/
            │   └── app.ts
            ├── lib/
            │   ├── stacks/
            │   │   ├── compute-stack.ts
            │   │   ├── data-stack.ts
            │   │   └── storage-stack.ts
            │   └── constructs/
            ├── cdk.json
            ├── package.json
            └── tsconfig.json

                        │
                        ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Phase 4: Import Configuration Generation                              │
│  Skill: cdk-import-config-generator                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

    Input: resources.json, Stack Files, AWS Credentials
      │
      ├──> Parse Stack Definitions
      │
      ├──> Extract Logical IDs
      │
      ├──> Map Logical ID → Physical Resource ID
      │    MyFunction → arn:aws:lambda:...:function:my-function
      │
      ├──> Generate Import Mapping JSON
      │
      ├──> Create Import Scripts
      │    • import-<stack>.sh for each stack
      │    • import-all.sh for all stacks
      │
      └──> Create Verification Scripts
           • verify-imports.sh

    Output: import-configs/
            ├── mappings/
            │   ├── compute-stack-import.json
            │   ├── data-stack-import.json
            │   └── storage-stack-import.json
            └── scripts/
                ├── import-all.sh
                ├── import-compute.sh
                ├── import-data.sh
                ├── import-storage.sh
                └── verify-imports.sh

                        │
                        ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Phase 5: Summary Report Generation                                    │
│  Orchestrator Internal                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

    Input: All Phase Results, Report Template
      │
      ├──> Aggregate Statistics
      │    • Resource counts
      │    • Construct counts
      │    • Stack counts
      │    • File locations
      │
      ├──> Load Report Template
      │
      ├──> Populate Template
      │    • Replace placeholders
      │    • Add statistics
      │    • Include next steps
      │
      └──> Write Report

    Output: IMPORT_SUMMARY.md
            • Configuration summary
            • Phase results
            • Next steps
            • File locations
            • Checklist

                        │
                        ▼

        ┌───────────────────────────────────────┐
        │  Workflow Complete                    │
        │                                       │
        │  User can now:                        │
        │  1. Review generated code             │
        │  2. Run npm install                   │
        │  3. Run cdk synth                     │
        │  4. Execute import scripts            │
        │  5. Commit to version control         │
        └───────────────────────────────────────┘
```

## Data Flow Between Phases

```
┌──────────────────┐
│   User Input     │
│  • Profile       │
│  • Region        │
│  • Filters       │
│  • Strategy      │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────┐
│  Phase 1: Discovery            │
│  Skill: aws-resource-discovery │
└────────┬───────────────────────┘
         │
         │ resources.json
         │ {
         │   "lambda": [...],
         │   "dynamodb": [...]
         │ }
         │
         ▼
┌────────────────────────────────┐
│  Phase 2: Code Generation      │
│  Skill: cdk-code-generator     │
└────────┬───────────────────────┘
         │
         │ constructs/**/*.ts
         │ export class MyFunctionConstruct
         │   extends Construct { ... }
         │
         ▼
┌────────────────────────────────┐
│  Phase 3: Organization         │
│  Skill: cdk-stack-organizer    │
└────────┬───────────────────────┘
         │
         │ stacks/**/*.ts
         │ export class ComputeStack
         │   extends Stack {
         │     new MyFunctionConstruct(...)
         │   }
         │
         ├────────────────────────┐
         │                        │
         │ resources.json         │
         │ (from Phase 1)         │
         │                        │
         ▼                        ▼
┌────────────────────────────────┐
│  Phase 4: Import Configs       │
│  Skill: cdk-import-config-gen  │
└────────┬───────────────────────┘
         │
         │ import mappings + scripts
         │ {
         │   "MyFunction": "arn:..."
         │ }
         │ ./import-compute.sh
         │
         ▼
┌────────────────────────────────┐
│  Phase 5: Report               │
│  Orchestrator                  │
└────────┬───────────────────────┘
         │
         │ IMPORT_SUMMARY.md
         │ Complete report with
         │ statistics and next steps
         │
         ▼
┌────────────────────────────────┐
│  Complete CDK Project          │
│  Ready for cdk import          │
└────────────────────────────────┘
```

## Error Handling Flow

```
                    Start Workflow
                         │
                         ▼
                   Phase 1 Execute
                         │
            ┌────────────┴────────────┐
            │ Success?               │
            │                        │
         Yes│                        │No
            │                        │
            ▼                        ▼
       Phase 2 Execute         Log Error
            │                  Stop Workflow
            │                  Preserve Outputs
            │                  Return Exit Code 1
            │
            ┌────────────┴────────────┐
            │ Success?               │
            │                        │
         Yes│                        │No
            │                        │
            ▼                        ▼
       Phase 3 Execute         Log Error
            │                  Stop Workflow
            │                  Preserve Outputs
            │                  Return Exit Code 2
            │
            ┌────────────┴────────────┐
            │ Success?               │
            │                        │
         Yes│                        │No
            │                        │
            ▼                        ▼
       Phase 4 Execute         Log Error
            │                  Stop Workflow
            │                  Preserve Outputs
            │                  Return Exit Code 3
            │
            ┌────────────┴────────────┐
            │ Success?               │
            │                        │
         Yes│                        │No
            │                        │
            ▼                        ▼
       Phase 5 Execute         Log Error
            │                  Stop Workflow
            │                  Preserve Outputs
            │                  Return Exit Code 4
            │
            ▼
    All Phases Complete
    Return Exit Code 0
    Display Success Message
```

## Component Skill Integration

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│               Orchestrator (Python)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  orchestrate.py                                     │   │
│  │    │                                                │   │
│  │    ├──> workflow_engine.py                         │   │
│  │    │       │                                        │   │
│  │    │       ├──> skill_invoker.py                   │   │
│  │    │       │     │                                  │   │
│  │    │       │     │  subprocess.run([               │   │
│  │    │       │     │    'python',                    │   │
│  │    │       │     │    '../aws-resource-discovery/  │   │
│  │    │       │     │        scripts/discover.py',    │   │
│  │    │       │     │    '--profile', profile,        │   │
│  │    │       │     │    '--region', region           │   │
│  │    │       │     │  ])                             │   │
│  │    │       │     │                                  │   │
│  │    │       │     └──> Component Skill ───┐         │   │
│  │    │       │                              │         │   │
│  │    │       ├──> data_passer.py            │         │   │
│  │    │       │     • Validates outputs      │         │   │
│  │    │       │     • Passes data forward    │         │   │
│  │    │       │                              │         │   │
│  │    │       └──> progress_tracker.py       │         │   │
│  │    │             • Displays progress      │         │   │
│  │    │                                      │         │   │
│  └────┼──────────────────────────────────────┼─────────┘   │
│       │                                      │             │
└───────┼──────────────────────────────────────┼─────────────┘
        │                                      │
        ▼                                      ▼
   User Output                      Component Skill Execution
   • Progress updates               ┌─────────────────────────┐
   • Resource counts                │ aws-resource-discovery  │
   • Success/Failure                │ cdk-code-generator      │
                                    │ cdk-stack-organizer     │
                                    │ cdk-import-config-gen   │
                                    └─────────────────────────┘
```

## Parallel Execution (Future v2.1+)

```
Current v2.0: Sequential Execution
───────────────────────────────────

Phase 1 ─────> Phase 2 ─────> Phase 3 ─────> Phase 4 ─────> Phase 5


Future v2.1: Optimized with Parallelization
────────────────────────────────────────────

                    Phase 1: Discovery
                    (Single Region)
                         │
                         ▼
                    Phase 2: Code Gen
                    (Per Resource Type)
          ┌───────────┬──┴──┬───────────┐
          │           │     │           │
          ▼           ▼     ▼           ▼
      Lambda      DynamoDB  S3        IAM
      Generate    Generate  Generate  Generate
          │           │     │           │
          └───────────┴──┬──┴───────────┘
                         │
                         ▼
                    Phase 3: Organization
                         │
                         ▼
                    Phase 4: Import Configs
                    (Per Stack)
          ┌───────────┬──┴──┬───────────┐
          │           │     │           │
          ▼           ▼     ▼           ▼
      Compute     Data    Storage    IAM
      Configs     Configs Configs    Configs
          │           │     │           │
          └───────────┴──┬──┴───────────┘
                         │
                         ▼
                    Phase 5: Report
```

## Legend

```
┌────────┐
│ Box    │  = Process / Component
└────────┘

   ─────    = Data Flow

   ═════    = Major Section Boundary

   ▼        = Flow Direction

   │        = Vertical Flow
   ├──      = Branch
   └──      = End Branch

   ?        = Decision Point

   ✓        = Success
   ✗        = Failure
```
