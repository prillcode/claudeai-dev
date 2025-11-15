# PrillCode's Claude Skills

A mono-repository of [Claude Code](https://claude.com/claude-code) skills and related tooling for extending Claude's capabilities with specialized workflows, domain knowledge, and integrations.

## Overview

This repository contains custom skills organized by category. Each skill is a self-contained package that provides Claude with procedural knowledge, scripts, reference materials, and assets for specific tasks.

## Skill Categories

### [workflow-skills/](workflow-skills/)
Skills for development workflow automation and productivity.

- **bmm-archive-branch-docs** - Archive completed BMAD feature documentation for workflow management
- **git-commit-helper** - Generate commits with clear messages from git diffs

### [dev-skills/](dev-skills/)
Skills for development workflow guidance and structured task management.

- **feature-guide/** - Multi-file feature development with spec-dev workflow (feature-creator, spec-feature, dev-feature)
- **task-guide/** - Lightweight bug fixes and maintenance tasks (task-creator, spec-task, dev-task)

### [aws-infra-skills/](aws-infra-skills/)
Suite of composable skills for AWS infrastructure discovery and CDK code generation.

- **aws-resource-discovery** *(In Development)* - Scan AWS accounts and discover resources with dependency detection
- **cdk-code-generator** *(Planned)* - Generate TypeScript CDK code from AWS resources
- **cdk-stack-organizer** *(Planned)* - Organize CDK code into logical stacks
- **cdk-import-config-generator** *(Planned)* - Generate CDK import configurations
- **aws-to-cdk-importer** *(Future)* - Orchestrate end-to-end AWS-to-CDK workflow

See [aws-infra-skills/AWS_CDK_IMPORTER_ROADMAP.md](aws-infra-skills/AWS_CDK_IMPORTER_ROADMAP.md) for complete roadmap.

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
**Last Updated:** 2025-11-07
