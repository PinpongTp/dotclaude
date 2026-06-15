---
name: commit-ai
description: Split current changes into small atomic conventional commits with an AI attribution footer (Co-Authored-By Claude). Use when user says "/commit-ai" or wants commits marked as AI-assisted.
license: MIT
allowed-tools: Bash
---

# Commit (Atomic, AI-attributed)

## Overview

Same as `/commit` — atomic conventional commits — **but every message ends with a `Co-Authored-By` footer marking it as AI-assisted**.

## Conventional Commit Format

```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

No scope. Footer always present.

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
feat!: remove deprecated endpoint

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

or with body:

```
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## Workflow

### 1. Analyze Diff

```bash
git status --porcelain
git diff
git diff --staged
```

Stage only files touched in this session.

### 2. Group Into Atomic Commits

One logical change per commit. Use `git add -p` for files with mixed work; verify with `git diff --cached`.

```bash
git add path/to/file1 path/to/file2
```

Never `git add -A` or `git add .`. **Never commit secrets.**

### 3. Generate Commit Message

- **Type**: see table
- **Description**: present tense, imperative, **< 72 chars**
- Body only when *why* is non-obvious
- **Footer always present** with current model name

### 4. Execute Commit (HEREDOC for footer)

```bash
git commit -m "$(cat <<'EOF'
<type>: <description>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

With body:

```bash
git commit -m "$(cat <<'EOF'
<type>: <description>

<body explaining why>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Update the model name on the footer if a newer one is in use.

Repeat steps 2–4 per group.

## Best Practices

- One logical change per commit
- Present tense, imperative mood
- Subject under 72 characters
- Reference issues when relevant: `Closes #123`
- Most commits are subject + footer only (no body)

## Git Safety Protocol

- NEVER update git config
- NEVER run destructive commands (`--force`, hard reset) without explicit request
- NEVER skip hooks (`--no-verify`) unless user asks
- NEVER force push to main/master
- If commit fails due to hooks, fix and create a **NEW** commit (don't amend)
