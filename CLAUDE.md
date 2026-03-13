# CLAUDE.md - Developer Workflow & Guidelines

## 🚨 Core Rules & Safety

- **Database Authorization:** Always request explicit user approval before executing `psql` commands that involve `CREATE`, `UPDATE`, or `DELETE`.
- **Progress Tracking:** Update `PROGRESS.md` (Completed, In Progress, Next Steps) **after validation** and before finishing a task.

---

## 🤖 Agent Roles & Parallel Spawning

- **🐼 panda_dev:** Standard features, bug fixes, refactor, and tests.
- **🦁 lion_dev:** Complex architecture, system design, and strategic decisions.
- **🐔 chicken_tester:** API-first validation and smoke testing.
- **Parallel Rules:** You may spawn multiple agents (2+ 🐼, 2+ 🦁, 2+ 🐔, or mixed) if tasks are independent.
  - **e.g.,** Spawn 🐼 for Frontend and 🦁 for Backend API concurrently.
  - **e.g.,** Spawn multiple 🐔 testers to validate different UI platforms.

---

## ⚡ Error Recovery & Communication

- **Error Recovery:** If an agent hits the same error >3 times or fails a fix >2 times, **stop immediately** and report to the user.
- **Language:** The user speaks Thai, but all **agent-to-agent communication and technical outputs must be in English** for token efficiency and precision.
- **Style:** Be direct and concise. Avoid unnecessary conversational filler.

---

## 🛠 Standard Workflow

1. **Plan:** `@lion_dev` designs the plan (for complex tasks).
2. **Execute:** Assign subtasks to `@panda_dev`/`@lion_dev` (Parallel allowed) using **English instructions**.
3. **Validate:** Invoke `@tester` (or multiple testers) to verify logic and User Journeys.
4. **Document:** Update `PROGRESS.md` once tests pass.
5. **Finish:** Provide a brief summary of work to the user.

---

## 📝 Technical Standards

- **Format:** Always use full file paths and Markdown code blocks.
- **Commits:** Follow Conventional Commits (feat, fix, refactor, docs).
