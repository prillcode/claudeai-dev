# AWS Infrastructure Skills - Use Cases & Examples

This guide shows you how to use the AWS Infrastructure Skills suite through natural language conversations with Claude Code. No need to remember command-line syntax or script paths - just describe what you want to accomplish!

## 📖 Table of Contents

1. [How It Works](#how-it-works)
2. [Orchestrator Use Cases](#orchestrator-use-cases-recommended)
3. [Individual Skill Use Cases](#individual-skill-use-cases)
4. [Common Scenarios](#common-scenarios)
5. [Filtering & Customization](#filtering--customization)
6. [After Import Workflows](#after-import-workflows)
7. [Troubleshooting & Help](#troubleshooting--help)

---

## How It Works

With Claude Code skills, you interact naturally instead of running scripts manually:

**❌ Old Way (Manual Scripts):**
```bash
python aws-resource-discovery/scripts/discover.py \
  --profile prod --region us-east-1 \
  --resource-types lambda,dynamodb \
  --output ./discovery/
```

**✅ New Way (Natural Language with Claude):**
```
"Discover Lambda functions and DynamoDB tables in my prod account
in us-east-1"
```

Claude will:
- Load the appropriate skill
- Execute the workflow
- Show you progress in real-time
- Report results and next steps

---

## Orchestrator Use Cases (Recommended)

The **aws-to-cdk-importer** orchestrator coordinates all skills in a single workflow. Use this for most scenarios.

### Use Case 1: Import Serverless Application Resources

**Your Goal:** Import Lambda functions, DynamoDB tables, and EventBridge rules from production into CDK for version control and IaC management.

**What You Say:**
```
"Use aws-to-cdk-importer to import my Lambda functions, DynamoDB tables,
and EventBridge rules from the prod profile in us-east-1. Organize them
by architectural layer and save to ./my-serverless-app-cdk"
```

**What Happens:**
```
[1/5] Discovering AWS resources...
      Profile: prod | Region: us-east-1
      ✓ Found 12 Lambda functions
      ✓ Found 5 DynamoDB tables
      ✓ Found 3 EventBridge rules

[2/5] Generating CDK constructs...
      Mode: reference
      ✓ Generated 20 construct files

[3/5] Organizing into CDK stacks...
      Strategy: layer
      ✓ Created 2 stack files (compute, data)

[4/5] Generating import configurations...
      ✓ Created import mappings for 20 resources
      ✓ Generated 3 import scripts

[5/5] Creating summary report...
      ✓ Report saved to IMPORT_SUMMARY.md

✅ Workflow completed successfully!
   Output location: ./my-serverless-app-cdk
   Next steps: See IMPORT_SUMMARY.md
```

**Follow-Up You Might Say:**
```
"Show me the generated compute-stack.ts file"

"Help me install the dependencies and run cdk synth"

"Execute the import scripts for me"
```

---

### Use Case 2: Import with Tag Filters

**Your Goal:** Only import resources tagged with a specific project or environment.

**What You Say:**
```
"Import AWS resources tagged with 'Project=CustomerPortal' from my
dev account in us-west-2. Use the tag-based organization strategy
grouped by Environment tag."
```

**What Happens:**
- Discovers only resources with `Project=CustomerPortal` tag
- Organizes stacks by `Environment` tag value (dev, staging, prod)
- Creates one stack per environment

**Result:**
```
cdk-organized/lib/stacks/
├── environment-dev-stack.ts
├── environment-staging-stack.ts
└── environment-prod-stack.ts
```

---

### Use Case 3: Full Management Mode Import

**Your Goal:** Import resources with full CDK management capability (not just references).

**What You Say:**
```
"Import my Lambda functions and DynamoDB tables from staging
in eu-west-1 using full management mode. I want to be able to
modify their configuration through CDK."
```

**What Happens:**
- Uses `--mode full` instead of default `--mode reference`
- Generates complete construct definitions with all properties
- Allows full lifecycle management through CDK

**Note:** Full mode requires exact property matching between AWS and CDK.

---

### Use Case 4: Preview Before Importing (Dry Run)

**Your Goal:** See what would be imported without actually creating files.

**What You Say:**
```
"Do a dry run of importing Lambda and DynamoDB resources from
production to see what would be discovered"
```

**What Happens:**
- Simulates the entire workflow
- Shows what would be discovered and generated
- Doesn't create any files
- Useful for testing filters and estimating scope

---

## Individual Skill Use Cases

Sometimes you want to use just one skill independently. Here are examples for each.

### Skill 1: aws-resource-discovery

**Purpose:** Only discover and inventory resources, no code generation.

**Use Case: Audit Resources**

**What You Say:**
```
"Use aws-resource-discovery to scan all Lambda functions and
DynamoDB tables in my prod account and save the inventory to
./resource-audit/"
```

**Result:** Creates `resource-audit/resources.json` with complete resource inventory.

**Use Case: Multi-Region Discovery**

**What You Say:**
```
"Discover all S3 buckets in us-east-1 and eu-west-1 from my prod account"
```

**Note:** Currently single-region per run; run twice for different regions.

**Use Case: Export for Analysis**

**What You Say:**
```
"Discover all IAM roles and export them to JSON so I can analyze
our permissions structure"
```

**Result:** JSON inventory you can load into analysis tools.

---

### Skill 2: cdk-code-generator

**Purpose:** Generate CDK code from an existing resource inventory.

**Use Case: Generate from Existing Inventory**

**What You Say:**
```
"Use cdk-code-generator to create CDK constructs from the resource
inventory at ./resource-audit/resources.json in reference mode"
```

**Result:** TypeScript constructs in `./cdk-generated/constructs/`

**Use Case: Regenerate with Different Mode**

**What You Say:**
```
"Regenerate the CDK code from ./discovery/resources.json but this
time use full management mode instead of reference mode"
```

**Result:** New constructs with complete definitions instead of `.from*()` methods.

---

### Skill 3: cdk-stack-organizer

**Purpose:** Organize existing CDK constructs into logical stacks.

**Use Case: Reorganize Existing Project**

**What You Say:**
```
"Use cdk-stack-organizer to reorganize the constructs in
./cdk-generated/ by service instead of by layer"
```

**Result:** New stack organization with service-based grouping.

**Use Case: Custom Organization Rules**

**What You Say:**
```
"Organize the CDK constructs using custom rules. I want all API-related
resources (Lambda functions with 'api' in the name and API Gateway) in
one stack, and all data resources in another."
```

Then provide a custom rules JSON when Claude asks.

---

### Skill 4: cdk-import-config-generator

**Purpose:** Generate import configurations for an existing CDK project.

**Use Case: Generate Import Configs for Hand-Written CDK**

**What You Say:**
```
"Use cdk-import-config-generator to create import configurations
for my existing CDK project at ./my-cdk-app/. Use the resource
inventory from ./discovery/resources.json"
```

**Result:** Import mappings and scripts for your hand-written CDK project.

---

## Common Scenarios

### Scenario 1: Migrating Serverless App to CDK

**Situation:** You have a serverless application built manually through the AWS console. You want to bring it under CDK management.

**Conversation:**
```
You: "I need to import my serverless app to CDK. It has about 10 Lambda
      functions, 3 DynamoDB tables, and 2 EventBridge rules in us-east-1
      under the prod profile."

Claude: "I'll help you import that serverless app. I'll use the
         aws-to-cdk-importer orchestrator to discover and import those
         resources. What would you like to name the output directory?"

You: "Call it serverless-app-cdk"

Claude: *Executes orchestrator*
        [Shows progress through all 5 phases]
        "✅ Import complete! I've created a CDK project at
        ./serverless-app-cdk. Would you like me to help you review
        the generated code?"

You: "Yes, show me the compute stack"

Claude: *Shows compute-stack.ts contents*
        "This stack contains all your Lambda functions and EventBridge
        rules. The functions are imported in reference mode, so they're
        tracked by CDK but their configuration won't be modified."

You: "Help me run the import scripts"

Claude: *Runs npm install, cdk synth, and import scripts*
        "✅ All resources have been imported successfully! Your infrastructure
        is now managed by CDK."
```

---

### Scenario 2: Documenting Existing Infrastructure

**Situation:** You want to document what's running in production without making changes.

**Conversation:**
```
You: "I need to document all the Lambda functions and DynamoDB tables
      running in our production account but I don't want to change anything"

Claude: "I'll use aws-resource-discovery to create an inventory of those
         resources. This is read-only and won't modify anything. What's
         your AWS profile name?"

You: "prod-readonly"

Claude: *Runs discovery*
        "✓ Found 47 Lambda functions and 12 DynamoDB tables.
        I've saved the complete inventory to ./resource-inventory/resources.json

        Would you like me to generate a summary report or CDK reference code
        for documentation?"

You: "Generate reference code so our team can see how to reference these
      resources in new CDK projects"

Claude: *Generates reference-mode CDK code*
        "I've created reference constructs for all 59 resources. Your team
        can now import these files to reference existing production resources
        in new CDK stacks."
```

---

### Scenario 3: Multi-Account Migration

**Situation:** You're consolidating multiple AWS accounts and need to import resources from each.

**Conversation:**
```
You: "I need to import Lambda functions from three different accounts:
      dev, staging, and prod. How should I approach this?"

Claude: "I recommend running the orchestrator separately for each account,
         using descriptive output directories. Let's start with dev."

You: "Import Lambda and DynamoDB from dev account in us-east-1 to
      ./cdk-projects/dev-resources"

Claude: *Runs orchestrator for dev*
        "✅ Dev resources imported. Ready for staging?"

You: "Yes, import from staging account to ./cdk-projects/staging-resources"

Claude: *Runs orchestrator for staging*
        "✅ Staging complete. Now for prod?"

You: "Yes, prod account to ./cdk-projects/prod-resources"

Claude: *Runs orchestrator for prod*
        "✅ All three accounts imported! You now have:
        - ./cdk-projects/dev-resources/
        - ./cdk-projects/staging-resources/
        - ./cdk-projects/prod-resources/

        Would you like me to help you merge these into a single
        multi-environment CDK project?"
```

---

## Filtering & Customization

### Filter by Resource Type

**What You Say:**
```
"Only import Lambda functions, ignore everything else"

"Import Lambda and DynamoDB, but exclude S3 and IAM"
```

### Filter by Tags

**What You Say:**
```
"Only import resources tagged with Environment=Production"

"Import resources where Team=Platform"

"Only resources with the tag ManagedBy=Terraform (to migrate from TF to CDK)"
```

### Filter by Name Pattern

**What You Say:**
```
"Only import Lambda functions whose names start with 'api-'"

"Import DynamoDB tables matching the pattern '*-prod-*'"
```

### Custom Stack Organization

**What You Say:**
```
"Organize the stacks by application. I want all resources with 'checkout'
in the name in one stack, all 'inventory' resources in another."

"Create one stack per microservice based on the Service tag"

"Group resources by cost center using the CostCenter tag"
```

---

## After Import Workflows

### Review Generated Code

**What You Say:**
```
"Show me the compute-stack.ts file"

"What constructs were generated for DynamoDB?"

"Show me the import configuration mappings"
```

### Build and Validate

**What You Say:**
```
"Install the NPM dependencies"

"Run npm run build and fix any TypeScript errors"

"Run cdk synth to validate the generated code"
```

### Execute Imports

**What You Say:**
```
"Run the import script for the compute stack"

"Import all stacks one at a time, starting with data stack"

"Execute all import scripts and verify they succeeded"
```

### Verify and Commit

**What You Say:**
```
"Run cdk diff to verify the imports were successful"

"Initialize a git repository and make the initial commit"

"Create a PR with this CDK project"
```

---

## Troubleshooting & Help

### Get Help with Errors

**What You Say:**
```
"The discovery phase failed with a permissions error. What permissions
do I need?"

"Import failed at phase 3. Show me the error log and help me fix it"

"The generated TypeScript code has compilation errors. Help me fix them"
```

### Understand What Happened

**What You Say:**
```
"Explain what the aws-to-cdk-importer orchestrator does"

"What's the difference between reference mode and full mode?"

"Why did it organize my resources into these specific stacks?"
```

### Dry Run / Preview

**What You Say:**
```
"Show me what would be discovered without actually importing anything"

"Estimate how long this import will take"

"What resources would be included with my current filters?"
```

### Check Documentation

**What You Say:**
```
"Show me the troubleshooting guide"

"What organization strategies are available?"

"How do I configure custom organization rules?"
```

---

## Tips for Effective Use

### ✅ DO:

1. **Start with the orchestrator** for most use cases
   - "Import my Lambda and DynamoDB resources using aws-to-cdk-importer"

2. **Use descriptive output directories**
   - "Save to ./my-project-cdk" (not just "./output")

3. **Start with reference mode** for safety
   - It's the default, but you can specify: "use reference mode"

4. **Filter appropriately** for large accounts
   - "Only resources tagged with Project=MyApp"

5. **Use dry-run** when uncertain
   - "Do a dry run first"

6. **Ask for help** interpreting results
   - "Explain what was generated"

### ❌ DON'T:

1. **Don't try to run Python scripts manually**
   - Just describe what you want in natural language

2. **Don't use full mode** without understanding implications
   - Ask: "What's the difference between reference and full mode?"

3. **Don't import everything** from large accounts without filters
   - Filter by tags, resource types, or name patterns

4. **Don't skip reviewing generated code**
   - Ask: "Show me the generated stacks before I import"

5. **Don't forget to test in dev/staging first**
   - "Let's test this on dev account before prod"

---

## Example Conversation Templates

### Template 1: Quick Import
```
"Import Lambda and DynamoDB from {profile} in {region} to {output-dir}"
```

### Template 2: Filtered Import
```
"Import resources tagged '{Key}={Value}' from {profile} in {region},
organized by {strategy}"
```

### Template 3: Full Workflow with Review
```
1. "Import {resources} from {profile} to {output-dir}"
2. [Claude imports]
3. "Show me the generated {stack-name} stack"
4. [Claude shows code]
5. "Help me install dependencies and run cdk synth"
6. [Claude runs commands]
7. "Execute the import scripts"
8. [Claude imports to CloudFormation]
9. "Verify imports and create a git commit"
```

### Template 4: Custom Organization
```
"Import {resources} from {profile} and organize them by {custom-strategy}.
I want {description of grouping logic}"
```

---

## Getting Started

Ready to import your first resources? Try this:

```
"Use aws-to-cdk-importer to import Lambda functions from my {profile}
account in {region} to ./my-first-import"
```

Replace `{profile}` and `{region}` with your AWS profile and region, and Claude will guide you through the entire process!

---

## Need More Help?

- **Ask Claude:** "Show me the aws-to-cdk-importer documentation"
- **Check troubleshooting:** "Show me the troubleshooting guide"
- **Review examples:** "Show me more examples of importing resources"
- **Get clarification:** "Explain {topic} in more detail"

---

**Last Updated:** 2025-11-08
**Maintained by:** Aaron Prill
**Part of:** AWS Infrastructure Skills Suite
