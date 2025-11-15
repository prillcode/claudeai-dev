---
name: bmm-archive-branch-docs
description: Archive completed BMAD feature documentation to prepare workflow for next major feature. Use when completing a feature branch and ready to restart the BMAD workflow for a new feature. Typically used before merging a feature branch to upstream.
---

# BMAD Feature Docs Archiver

## Overview

Archive completed BMAD Method feature documentation when finishing a feature branch to prepare the workflow for the next major, and keep upstream branch clean of feature/branch-specific workflow documentation (stories/epics). This skill moves Epic and Story documentation files from the root BMAD Docs directory into an archive subdirectory, allowing the documentation workflow to restart cleanly for each new major feature.

## When to Use This Skill

Use this skill when:
- Completing work on a major feature that has its own feature branch
- Ready to merge a feature branch back to the upstream branch (dev, main, etc.)
- Want to restart the BMAD documentation workflow for a new feature
- Need to preserve completed feature documentation while clearing the workspace

**Recommended starting point:** On a feature branch that is ready to be merged back to the upstream branch.

## Workflow

### Step 0: Explain Purpose and Verify Context

Start by explaining to the user:
- This skill archives completed BMAD feature documentation
- The recommended starting point is being on a feature branch ready to merge
- The process will move completed docs to an archive subdirectory
- This prepares the BMAD workflow to restart for the next major feature

### Step 1: Confirm BMAD Docs Directory

Ask the user to confirm the location of their BMAD Docs directory. This is the directory where BMAD creates Epic and Story markdown files.

**Common directory names:**
- `.bmm-docs`
- `.bmad-docs`
- `docs/bmad`
- Custom names configured by the user

**Important:** Do NOT target the `bmad/` directory that contains the BMAD agent workflow files. The target is the separate documentation output directory.

### Step 2: Create Archive Directory

Create an `archive/` directory in the BMAD Docs directory if it doesn't already exist:

```bash
mkdir -p <bmad-docs-dir>/archive
```

### Step 3: Get Archive Name from User

Prompt the user for the name of the feature/branch being archived.

**Default:** Use the current git branch name (obtain via `git branch --show-current`)

Example interaction:
- "What would you like to name this archive? (default: [current-branch-name])"

### Step 4: Execute Archiving

Use the `scripts/archive_bmad_docs.py` script to move files to the archive subdirectory:

```bash
python scripts/archive_bmad_docs.py <bmad-docs-dir> <archive-name>
```

The script will:
- Create `<bmad-docs-dir>/archive/<archive-name>/` directory
- Move these files from the root BMAD Docs directory to the archive:
  - `PRD.md`
  - `epics.md`
  - `sprint-status.yaml`
  - `tech-spec.md`
  - `stories/` (directory including all files and subdirectories)
- Report what was archived and what was skipped (if files don't exist)

**Alternative manual approach:** If the script encounters issues, manually move files:

```bash
mkdir -p <bmad-docs-dir>/archive/<archive-name>
mv <bmad-docs-dir>/PRD.md <bmad-docs-dir>/archive/<archive-name>/
mv <bmad-docs-dir>/epics.md <bmad-docs-dir>/archive/<archive-name>/
mv <bmad-docs-dir>/sprint-status.yaml <bmad-docs-dir>/archive/<archive-name>/
mv <bmad-docs-dir>/tech-spec.yaml <bmad-docs-dir>/archive/<archive-name>/
mv <bmad-docs-dir>/stories/ <bmad-docs-dir>/archive/<archive-name>/
```

### Step 5: Confirm Directory State

After archiving, inform the user that the feature docs have been archived and ask them to confirm the root BMAD Docs directory is in the desired state.

**Important files to keep in root:**
- `bmm-workflow-status.yml` - Important context for future features
- `index.md` - Important context for future features
- `project-overview.md` - Overview of entire tech stack. Important context for future features.
- `project-scan-reports.json` - Tracks all recent documentation scans. Important to keep as projects can be scanned multiple times.

Ask if there are any other docs they want archived that weren't automatically moved.

### Step 6: Provide Next Steps

Once the user confirms the directory state is correct, recommend these next steps:

1. **Create a commit** of the archiving changes:
   ```bash
   git add <bmad-docs-dir>
   git commit -m "chore: archived BMAD feature docs to prepare workflow for next major feature"
   ```

2. **Merge the feature branch** to the appropriate upstream branch:
   ```bash
   git checkout main  # or dev, depending on workflow
   git merge <feature-branch>
   git push
   ```

3. **Create a new feature branch** to start the next feature:
   ```bash
   git checkout -b <new-feature-branch>
   ```

4. **Start the BMAD workflow** over again for the new feature!

## Resources

### scripts/archive_bmad_docs.py

Python script that automates the archiving process. Can be executed directly to move files from the root BMAD Docs directory to an archive subdirectory.

**Usage:**
```bash
python scripts/archive_bmad_docs.py <bmad-docs-dir> <archive-name>
```

**Example:**
```bash
python scripts/archive_bmad_docs.py .bmm-docs feature-auth-system
```

The script handles:
- Directory creation (archive and subdirectory)
- Moving files and directories
- Error handling for missing files
- Reporting archived and skipped items
