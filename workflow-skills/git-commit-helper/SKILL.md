---
name: git-commit-helper
description: Generates commits with clear commit messages from git diffs. Use when creating commits and writing commit messages.
---

# Create Git Commits

## Instructions

1. I will run `git diff HEAD` to determine if there are existing changes - either staged or unstaged.
2. If changed files are found, I will create a commit and message as outlined next.
3. Whenever creating any commit message, I'll suggest a commit message with:
   - A Summary under 50 characters with one of the following valid prefixes.
	- valid prefixes: "fix:", "feat:", "chore:"
	- use "fix:" if changed file(s) is fixing some existing component/file
	- use "feat:" if any changed file includes a new component, feature, or enhancement
	- use "chore:" if only adding documentation or managing packaging versions, or similar.
   - Also include a Detailed description as bulleted list including affected components/files as applicable
   - Do NOT include "Generated with [Claude Code](https://claude.com/claude-code)" in the message

## Best practices

- Use present tense
- Explain what and why, not how

