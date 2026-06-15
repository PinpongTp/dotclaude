---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable. Triggered by "/improve-codebase-architecture".
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion, Agent
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. Aim: testability and AI-navigability.

## Glossary

Use these terms exactly. Consistent language is the point — don't drift into "component", "service", "API", or "boundary". Full definitions in [LANGUAGE.md](LANGUAGE.md).

- **Module** — anything with an interface and an implementation (function, class, package, slice).
- **Interface** — everything a caller must know: types, invariants, error modes, ordering, config. Not just the type signature.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface. **Deep** = a lot of behaviour behind a small interface. **Shallow** = interface nearly as complex as the implementation.
- **Seam** — where an interface lives; a place behaviour can be altered without editing in place. (Use this, not "boundary".)
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key principles:

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is *informed* by the project's domain model. CONTEXT.md gives names to good seams; ADRs record decisions the skill should not re-litigate.

## Process

### 1. Explore

Read the project's `CONTEXT.md` (or `CONTEXT-MAP.md`) and any ADRs in the area first.

Then spawn `🐶dog_explore` (`model: haiku`, `mode: auto`) — multiple in parallel if the codebase is large — to walk the code. Don't follow rigid heuristics; explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts are untested, or hard to test through their current interface?

Apply the **deletion test** to anything suspected shallow: would deleting concentrate complexity, or just move it? "Concentrates" is the signal.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve `${TMPDIR:-/tmp}` (or `%TEMP%` on Windows); filename `architecture-review-<YYYYMMDD-HHMMSS>.html`. Open it (`open` macOS, `xdg-open` Linux, `start` Windows) and tell the user the absolute path.

Use **Tailwind via CDN** for layout, **Mermaid via CDN** where graph-shaped relationships communicate best. Mix Mermaid (call graphs, dependencies, sequences) with hand-built CSS/SVG (editorial diagrams). Each candidate gets a **before/after visualisation**.

Each candidate as a card:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture causes friction
- **Solution** — plain-English description of the change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side-by-side, custom-drawn, illustrating shallowness and the deepening
- **Recommendation strength** — `Strong`, `Worth exploring`, or `Speculative`, rendered as a badge

End the report with a **Top recommendation**: which candidate to tackle first and why.

**Use `CONTEXT.md` vocabulary for the domain, and [LANGUAGE.md](LANGUAGE.md) vocabulary for the architecture.** If `CONTEXT.md` defines "Order", talk about "the Order intake module" — not "the FooBarHandler", not "the Order service".

**ADR conflicts**: only surface a candidate that contradicts an existing ADR when the friction is real enough to warrant reopening that ADR. Mark it clearly (warning callout: *"contradicts ADR-0007 — but worth reopening because…"*). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](HTML-REPORT.md) for the scaffold, [DEEPENING.md](DEEPENING.md) for patterns, and [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md) for interface options.

Do **not** propose interfaces yet. After the file is written, ask via `AskUserQuestion`: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation (same shape as `/grill-with-docs`). Walk the design tree — constraints, dependencies, the deepened module's shape, what sits behind the seam, what tests survive.

Side effects inline as decisions crystallise:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md` (see [../grill-with-docs/CONTEXT-FORMAT.md](../grill-with-docs/CONTEXT-FORMAT.md)). Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR: *"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"* Only offer when the reason would actually be needed by a future explorer. See [../grill-with-docs/ADR-FORMAT.md](../grill-with-docs/ADR-FORMAT.md).
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).

### 4. Implementation hand-off

When the user is ready to implement:

- Architectural rewrites → `🦁lion_dev` (`model: opus`, `mode: acceptEdits`).
- Mechanical refactors with a clear plan → `🐼panda_dev` (`model: sonnet`, `mode: acceptEdits`).
- Post-change validation in parallel → `🐔chicken_tester` + `👨🏼‍🦳zoo_keeper` (both `model: sonnet`, `mode: auto`).

## Output to user

Compressed Thai for status updates. The HTML report itself in English (it's a durable artifact and the project's working language).
