---
name: tdd
description: Test-driven development with vertical-slice red-green-refactor loop. Use when user wants TDD, mentions "red-green-refactor", asks for integration-style tests, or wants test-first development.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion, Agent, LSP
---

# Test-Driven Development

## Philosophy

**Core principle**: tests verify behaviour through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style — exercise real code paths through public APIs, read like a specification, survive refactors.

**Bad tests** are coupled to implementation — mock internal collaborators, test private methods, break when you rename an internal function even though behaviour hasn't changed.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking discipline.

## Anti-pattern: horizontal slices

**Do not write all tests first, then all implementation.** That produces tests for *imagined* behaviour, locked to the *shape* of data and signatures, insensitive to real changes.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

Tracer-bullet vertical slices: one test → one implementation → repeat. Each cycle is informed by what the previous one taught you.

## Workflow

### 1. Planning

Before writing code:

- Use `AskUserQuestion` to confirm:
  - The public interface shape (signatures, error modes, async/sync)
  - Which behaviours matter most (you can't test everything — prioritise)
- For unfamiliar codebases, spawn `🐶dog_explore` (`model: haiku`, `mode: auto`) to map the area and surface the domain glossary / ADRs first.
- Identify [deep modules](deep-modules.md) opportunities and design for [testability](interface-design.md).
- List behaviours, not implementation steps.
- Get user approval before any test is written.

### 2. Tracer bullet

ONE test confirming ONE behaviour, end-to-end:

```
RED:   write test → fails
GREEN: minimal code → passes
```

### 3. Incremental loop

For each remaining behaviour, the same RED → GREEN cycle. Rules:

- One test at a time.
- Only enough code to pass the current test.
- Don't anticipate future tests.
- Tests stay on observable behaviour.

### 4. Refactor

After GREEN, look for [refactor candidates](refactoring.md):

- Extract duplication.
- Deepen modules (move complexity behind small interfaces).
- Apply SOLID where natural — not as ceremony.
- Re-run tests after each refactor step.

**Never refactor while RED.** Get to GREEN first.

### 5. Validate

After the feature is done, in parallel:

- `🐔chicken_tester` (`model: sonnet`, `mode: auto`) for end-to-end / integration sweep.
- `👨🏼‍🦳zoo_keeper` (`model: sonnet`, `mode: auto`) for security + cleanup pass if the change is non-trivial.

## Per-cycle checklist

```
[ ] Test describes behaviour, not implementation
[ ] Test uses public interface only
[ ] Test would survive an internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```

## Output to user

Compressed Thai updates per cycle (e.g. `RED test_checkout_empty → GREEN`). Full plan + cycle plan in English when needed for clarity.
