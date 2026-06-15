---
name: commit
description: Split current changes into small atomic conventional commits and execute them. No AI attribution footer. Use when user says "/commit" or asks to commit changes.
license: MIT
allowed-tools: Bash
---

# Commit (Atomic, No AI Attribution)

## Overview

Create standardized, semantic git commits using Conventional Commits. Analyze the actual diff to determine type and description. **Split changes into small, atomic, topic-based commits** — one logical change per commit. **No AI attribution** in messages.

## Conventional Commit Format

```
<type>: <description>

[optional body]

[optional footer(s)]
```

No scope. Keep messages short.

## Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

## Breaking Changes

```
# Exclamation mark after type
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## Workflow

### 1. Analyze Diff

```bash
git status --porcelain
git diff
git diff --staged
```

Cross-reference with the conversation — **stage only files touched in this session**. Skip pre-existing modifications unless the user explicitly includes them.

### 2. Group Into Atomic Commits

One logical change per commit. If a file mixes session edits with unrelated changes, use `git add -p` to stage only the right hunks, then verify with `git diff --cached` before committing.

```bash
# Stage specific files
git add path/to/file1 path/to/file2

# Interactive when one file has mixed work
git add -p path/to/mixed
git diff --cached    # verify
```

Never `git add -A` or `git add .`. **Never commit secrets** (`.env`, credentials, keys).

### 3. Generate Commit Message

Analyze each staged group:

- **Type**: kind of change (see table)
- **Description**: one-line summary, present tense, imperative mood, **< 72 chars**

Body only when the *why* is non-obvious from the diff. Most commits should be subject-only.

### 4. Execute Commit

```bash
# Single line — preferred
git commit -m "<type>: <description>"

# Multi-line only when body is needed
git commit -m "$(cat <<'EOF'
<type>: <description>

<body explaining why>
EOF
)"
```

Repeat steps 2–4 for each remaining group.

## Best Practices

- One logical change per commit
- Present tense, imperative mood: "add" not "added", "fix" not "fixes"
- Keep description under 72 characters
- Reference issues when relevant: `Closes #123`, `Refs #456`
- Most commits don't need a body

## Git Safety Protocol

- **No AI attribution** — no `Co-Authored-By: Claude`, no `🤖 Generated with…`, no mention of AI in any message
- NEVER update git config
- NEVER run destructive commands (`--force`, hard reset) without explicit request
- NEVER skip hooks (`--no-verify`) unless user asks
- NEVER force push to main/master
- If commit fails due to hooks, fix and create a **NEW** commit (don't amend)
