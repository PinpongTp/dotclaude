---
description: Split staged/unstaged changes into multiple topic-based commits
---

Analyze the current repository changes and create **multiple commits**, each scoped to a single logical topic. Do NOT bundle unrelated changes into one commit.

## Scope rule (IMPORTANT)

- **Commit ONLY changes related to the work done in the current session.** Do not commit unrelated pre-existing modifications, even if they appear in `git status`.
- Identify session-related changes by cross-referencing with the conversation history (files Claude edited/created this session).
- For changes NOT touched in this session:
  - If they look **unrelated and safe to leave**, skip them silently.
  - If they look **related or could break the build/tests if left out** (e.g., a file imports a symbol that was renamed in a session-edited file), STOP and ask the user:
    > "พบไฟล์ `<path>` ที่ไม่ได้แก้ใน session นี้ แต่อาจเกี่ยวข้องกับการเปลี่ยนแปลง — ต้องการ commit ไฟล์นี้ด้วย, commit ทั้งหมด, หรือข้าม?"
- Only commit "everything" if the user explicitly says so (e.g., `/commit all`, "commit ทั้งหมด").

## Steps

1. Run in parallel:
   - `git status` (no `-uall`)
   - `git diff` (unstaged)
   - `git diff --cached` (staged)
   - `git log -n 10 --oneline` (match commit style)

2. Filter to **session-scoped files only** (per the Scope rule above), then group them by topic. Examples of separate topics:
   - feature additions (separate per feature)
   - bug fixes (separate per bug)
   - refactor / cleanup
   - docs
   - config / tooling / settings
   - tests
   - dependencies

   If a single file contains changes for multiple topics, use `git add -p` to stage hunks selectively.

3. For each topic group, sequentially:
   - Stage ONLY the files/hunks for that topic (use explicit file paths, never `git add -A` or `git add .`).
   - Verify with `git diff --cached --stat` that only the intended changes are staged.
   - Commit using Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `test:`, etc.). Use a single `-m` flag (do NOT add Co-Authored-By or any AI attribution):

     ```
     git commit -m "<type>: <concise why-focused subject>"
     ```

   - For multi-line messages, use multiple `-m` flags (avoid HEREDOC — `cat` may be rewritten by shell hooks like rtk):

     ```
     git commit -m "<subject>" -m "<body paragraph>"
     ```

4. After all commits, run `git status` and `git log --oneline -n <N>` to confirm.

## Rules

- **Never** add AI attribution to commits — no `Co-Authored-By: Claude`, no `🤖 Generated with Claude Code`, no mention of AI/Claude/assistant in subject or body. Commit messages must look like they were written by the user.
- **Never** mix unrelated topics in one commit.
- **Never** commit secrets or `.env` / credential files — warn the user instead.
- **Never** use `--no-verify`, `--amend`, or destructive git ops.
- If a pre-commit hook fails: fix the issue, re-stage, create a NEW commit (do not amend).
- Commit message focuses on **why**, not what. Subject ≤72 chars.
- If there are no changes, report that and stop.
- If grouping is ambiguous, list the proposed groups to the user and ask before committing.

$ARGUMENTS
