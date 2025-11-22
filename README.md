# PrillCode's Claude Skills

A mono-repository of [Claude Code](https://claude.com/claude-code) skills and related tooling for extending Claude's capabilities with specialized workflows, domain knowledge, and integrations.

## Overview

This repository contains custom skills organized by category. Each skill is a self-contained package that provides Claude with procedural knowledge, scripts, reference materials, and assets for specific tasks.

## Skill Categories

### [dev-skills/](dev-skills/)
Unified development workflow system for all software development tasks with adaptive complexity.

- **dev-orchestrator** - Orchestrates complete development workflow from specification to completion
- **dev-spec** - Creates specifications with adaptive complexity (lightweight for bugs, comprehensive for features)
- **dev-execute** - Executes specifications with two-phase testing workflow (implement → test → confirm → archive)
- **git-commit-helper** - Generate conventional commit messages from git diffs

### [infra-skills/](infra-skills/)
Suite of composable skills for AWS infrastructure discovery and CDK code generation.

- **aws-resource-discovery** - Scan AWS accounts and discover resources with dependency detection
- **cdk-code-generator** - Generate TypeScript CDK code from AWS resources
- **cdk-stack-organizer** - Organize CDK code into logical stacks
- **cdk-import-config-generator** - Generate CDK import configurations
- **aws-to-cdk-importer** - Orchestrate end-to-end AWS-to-CDK workflow

See [infra-skills/AWS_CDK_IMPORTER_ROADMAP.md](infra-skills/AWS_CDK_IMPORTER_ROADMAP.md) for complete roadmap.

### [agile-skills/](agile-skills/)
Skills for decomposing agile artifacts into actionable development work.

- **epic-feature-creator** - Transform JIRA epics into technical feature breakdowns
- **feature-story-creator** - Break features into user stories ready for dev-spec
- **story-task-creator** *(Planned)* - Split large stories into sub-tasks

See [agile-skills/README.md](agile-skills/README.md) for complete workflow.

## Skill Structure

Each skill follows the standard Claude Code skill format:

```
skill-name/
├── SKILL.md                    # Skill documentation (required)
├── scripts/                    # Executable code (Python/Bash/etc.)
├── references/                 # Documentation loaded as needed
└── assets/                     # Templates and files used in output
```

## Using These Skills

Skills can be installed for use with Claude Code by copying them to your Claude skills directory:

```bash
cp -r <skill-name> ~/.claude/skills/
```

Or use them directly by referencing them in your prompts when working in this repository.

## Future Plans

- Additional workflow automation skills
- MCP (Model Context Protocol) servers and integrations
- DevOps and infrastructure tooling
- Documentation and knowledge management skills

## Contributing

This is a personal repository of skills developed for my own workflows, but feel free to use them as inspiration for your own skills.

---

**Author:** Aaron Prill ([@prillcode](https://github.com/prillcode))
**Last Updated:** 2025-11-21
