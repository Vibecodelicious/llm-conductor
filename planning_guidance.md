# Planning Guidance

## Purpose

Transform feature requests into implementation-ready plans that maximize first-pass execution success.

Planning is analysis and design work. Do not write implementation code in this phase.

## Core Principle: Analysis First

When planning implementation approaches, do the analytical work before presenting options or asking for help.

### Decision Process

1. Analyze thoroughly.
- Think through plausible approaches and tradeoffs.
- Do not present options that have no meaningful upside.

2. Validate with a sub-agent.
- Before committing to an approach, launch a sub-agent to review your analysis.
- Ask it to identify:
  - Assumptions you made
  - High-value options you may have missed
  - What could be wrong with your approach (adversarial: try to prove it wrong)
  - Contradicting evidence from the repository
- Require evidence-backed validation, not reasoning-only agreement.

3. Evaluate tradeoffs in this priority order.
- Long-term project goals
- Ongoing maintenance burden
- Implementation complexity

4. Escalate only genuine ambiguity.
- Escalate to the user only after analysis and sub-agent validation.
- Escalation should be rare.
- Escalate when multiple defensible options remain and the choice depends on user/business preferences.

### When To Present Options To The User

Present multiple options only when all of the following are true:
- Each option has real advantages the others do not.
- Technical analysis cannot resolve the choice alone.
- The decision depends on business context, risk tolerance, or team preference.

## Core Principle: User-Need First

All planning starts from the user outcome and correctness bar.
Efficiency matters only when quality and correctness are preserved.

If a decision is ambiguous, resolve it by prioritizing what best protects user outcomes and review quality.

## Core Principle: Prioritize Demoable Progress

When planning milestones, prioritize demoable progress.

This means that once a milestone is completed in the project, it should produce visible, demonstrable value whenever practical.
Avoid long runs of infrastructure-only milestones unless they are strictly necessary.

## Core Principle: Manage Duplication Explicitly

If you choose a non-DRY approach, manage the risk intentionally.

When duplicated logic must exist in multiple places:
- Add short comments at each location pointing to the other linked locations.
- Make update coupling explicit so future changes do not silently diverge.
- Treat this coupling cost as part of the design tradeoff.

## Triage: Single Story vs Epic

Use this simple rule:
- If the work is exactly one story, create a single-story plan.
- If the work is more than one story, create an epic containing those stories.

Multi-story epics can include broad cleanup work (for example, fixing unrelated small issues) when that is the most practical structure.

## Plan Types and Paths

### Path A: Single-Story Plan

Use for one-story scope.

- Plan file: `.agents/plans/story-{kebab-case-title}.md`
- Include full context, implementation steps, testing strategy, and validation commands.

### Path B: Epic Plan

Use for multi-story scope.

- Epic directory: `.agents/plans/epic-{epic-title}/`
- Epic file: `.agents/plans/epic-{epic-title}/epic-{epic-title}.md`
- Story files: `.agents/plans/epic-{epic-title}/story-{epic-title}.{X}-{kebab-case-story-title}.md`

`{epic-title}` should be kebab-case and descriptive.

## Parallelization Guidance (Generic)

Look for independent workstreams that can proceed in parallel:
- UI and frontend work with mocks
- Backend/service work with API contracts
- Data schema/migration prep
- Test harness and validation automation
- Documentation updates tied to completed stories

### Parallelization Risk Controls

- Define interfaces/contracts early.
- Identify critical dependencies and integration order.
- Use stubs/mocks for blocked dependencies.
- Re-integrate at milestone boundaries.
- Keep ownership boundaries explicit.

## Lightweight User Model Guidance (Mandatory)

Every plan must include a `User Model` section.

The plan must explicitly construct and use:
- `user gamut`
- `user-needs gamut`

### Required Concepts

- `user gamut`: the range of distinct user segments affected.
- `user-needs gamut`: the range of distinct needs, constraints, and desired outcomes across those segments.

These are called gamuts because they represent broad, multi-dimensional spaces, not narrow one-axis lists.

### List Rules (Mandatory)

Any list in `user gamut` or `user-needs gamut` sections must follow all rules:
- Treat lists as `examples only`, never exhaustive categories.
- Span broad dimensionalities (role, domain, context, risk profile, scale, workflow, expertise, etc.).
- Avoid single-axis framing unless explicitly labeled as one slice.
- Prefer mind-expanding examples over mind-narrowing taxonomies.

### Practical Use In Planning

Use the user model to:
- Evaluate who benefits or is harmed by each design decision.
- Identify ambiguities where different user regions may prefer different outcomes.
- Shape acceptance criteria so they cover materially different user regions.

If the user model is vague, add explicit discovery tasks/questions in the plan rather than assuming certainty.

## Planning Process

### Phase 1: Feature Understanding

- Extract the core problem.
- Identify user value and expected impact.
- Classify work type (new capability, enhancement, refactor, bug fix).
- Assess complexity and likely surface area.
- Draft or refine the user story:

```text
As a <type of user>
I want to <action/goal>
So that <benefit/value>
```

### Phase 2: Codebase Intelligence Gathering

Use repository evidence and sub-agents where useful.

1. Project structure and architecture
- Primary language/framework/runtime
- Directory boundaries and integration points
- Build and environment setup

2. Pattern recognition
- Similar implementations
- Naming and module conventions
- Error handling and logging patterns
- Existing anti-patterns to avoid

3. Dependency analysis
- Relevant libraries and versions
- Integration approach already used in repo
- Internal docs and references in repo

4. Testing patterns
- Framework and test layout
- Similar test examples
- Unit/integration expectations

5. Integration points
- Files to modify
- New files to add
- Routing/API/data/auth patterns if applicable

6. Planned-target inventory (mandatory)
- Build a deterministic list of planned target files before implementation starts.
- Primary source: story-plan sections that enumerate target paths (for example, `New Files to Create`, `Files Modified`, or explicit file-path bullets in `Implementation Tasks`).
- Secondary fallback: `Context References` entries that explicitly identify modification targets.
- This inventory is the required input for worktree artifact checks.

### Phase 3: External Research

Use external research when needed for unfamiliar or changing dependencies.
Capture references directly in story plans when they materially affect implementation.

### Phase 4: Strategic Design

- Evaluate architecture fit.
- Identify critical dependencies and order of operations.
- Anticipate failure modes and edge cases.
- Define testing and validation approach.
- Consider performance, security, maintainability, and extensibility.
- Select approach with clear rationale.

### Phase 5: Plan Construction

Create either:
- Single-story plan (Path A), or
- Epic plus story plans (Path B)

Make tasks executable, ordered by dependency, and independently verifiable.

### Phase 6: Plan Approval and Commit Handoff (Mandatory)

After user approves the plan, commit the plan artifact(s) before orchestration begins.

- Scope: every approved plan document that defines execution scope for the run.
- Required evidence to record in the plan: approval status, approval citation, plan commit hash, ready-for-orchestration status.
- Blocking rule: if plan-commit status is unresolved, orchestration start is blocked.

### Phase 7: Worktree Artifact Check and Escalation (Mandatory)

Before implementation begins, run a mandatory overlap check for every planned target file.

- Artifact classes (must use these exact labels):
  - `tracked-dirty`: tracked file with staged or unstaged uncommitted modifications.
  - `existing-untracked`: file exists on disk and is untracked by git.
- Scope rule: ignored files are out of scope unless they are explicitly listed as planned target files.
- Escalation trigger: if any planned target file overlaps either artifact class, escalation is mandatory before implementation for that path.
- Escalation unit: batch by story, with one escalation row per overlapping path.
- Required escalation payload fields:
  - `target file`
  - `artifact class`
  - `risk summary` (why editing now is unsafe or ambiguous)
  - `recommended default`
  - `user decision needed`
- Blocking rule: unresolved pending escalation blocks implementation for overlapping paths.
- Timing and ownership:
  - The planner performs the artifact check during plan validation and records results in the plan.
  - The implementer re-checks immediately before edits.
  - If re-check finds overlap without approved direction (or explicit deferral), implementation must stop and escalate.

## Plan Validation (Mandatory, Non-Optional)

After creating any plan (single-story or epic), run this validation loop.

### Validation Step 1: Missing Details Check

Launch a sub-agent to review the plan documents and identify missing details that would block implementation.
Instruct it to explore the repository before concluding details are missing.

### Validation Step 2: Ambiguity Check

Launch a sub-agent to identify multiple valid implementation paths that could materially change outputs or maintainability.

Resolve ambiguities by:
- Updating plan docs with clarifying guidance, or
- Escalating to the user only when the choice depends on user/business preference.

### Validation Step 3: Worktree Artifact Risk Check

Launch a sub-agent (or perform directly with repository evidence) to validate overlap status for all planned target files.

- Verify each planned target path against worktree artifact classes: `tracked-dirty` and `existing-untracked`.
- Confirm the plan includes a `Worktree Artifact Check` section with overlap outcomes and escalation status.
- Ensure unresolved overlap escalations are not left pending before implementation starts.

### Validation Step 4: Plan Approval/Commit Closure Check

Validate that plan-commit status is closed before implementation orchestration starts.

- Confirm each active story plan has a completed `Plan Approval and Commit Status` section.
- Verify `ready-for-orchestration` is affirmative and backed by approval citation plus plan commit hash.
- Any missing approval/commit evidence blocks orchestration until resolved or explicitly overridden by the user.

### Iteration Rule

Repeat the validation loop up to 3 iterations, or stop earlier only when the sub-agent confirms no blocking gaps and no unresolved high-impact ambiguity.

The validation loop is not complete while any required worktree artifact escalation remains unresolved.
The validation loop also blocks orchestration when plan-commit status is unresolved.

## Templates

## Template: Epic

```markdown
# Epic: {Epic Title}

**Goal:** {Brief purpose}
**Depends on:** {Prerequisites or "None"}
**Parallel with:** {Parallel epics/stories or "None"}
**Complexity:** {Low/Medium/High}

## User Model

### User Gamut
- {examples only; broad dimensions}

### User-Needs Gamut
- {examples only; broad dimensions}

### Ambiguities From User Model
- {decision point where user regions may prefer different outcomes}

## Stories

### Story 1: {Story Name}
**Size:** {Small/Medium/Large}
**Description:** {What this story delivers}
**Implementation Plan:** `.agents/plans/epic-{epic-title}/story-{epic-title}.1-{kebab-case-story-title}.md`

### Story 2: {Story Name}
**Size:** {Small/Medium/Large}
**Description:** {What this story delivers}
**Implementation Plan:** `.agents/plans/epic-{epic-title}/story-{epic-title}.2-{kebab-case-story-title}.md`

## Dependencies and Integration

- Prerequisites:
- Enables:
- Integration points:
```

## Template: Story (Epic Story File)

```markdown
# Story: {Story Name}

**Epic:** {Epic Title}
**Size:** {Small/Medium/Large}
**Dependencies:** {Story dependencies or "None"}

## Story Description

{Expanded implementation context}

## User Model

### User Gamut
- {examples only; broad dimensions}

### User-Needs Gamut
- {examples only; broad dimensions}

### Design Implications
- {how this affects implementation choices}

## Acceptance Criteria

- [ ] {Specific, testable criterion}
- [ ] {Specific, testable criterion}

## Context References

### Relevant Codebase Files (must read)
- `{path}:line` - {why relevant}

### New Files to Create
- `{path}` - {purpose}

### Relevant Documentation
- {doc/link and why it matters}

## Implementation Plan

### Phase 1: Foundation
- {tasks}

### Phase 2: Core Implementation
- {tasks}

### Phase 3: Integration
- {tasks}

### Phase 4: Testing and Validation
- {tasks}

## Step-by-Step Tasks

1. {atomic task}
2. {atomic task}
3. {atomic task}

## Testing Strategy

- {unit/integration/e2e approach}

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `{non-interactive command}`
- `{non-interactive command}`

## Worktree Artifact Check

- Checked At: `{ISO-8601}`
- Planned Target Files: `{path list derived from plan sections}`
- Overlaps Found (path + class): `{none | path -> tracked-dirty | path -> existing-untracked}`
- Escalation Status: `{none|pending|approved|deferred}`
- Decision Citation: `{user approval/deferral reference or none}`

## Plan Approval and Commit Status

- Approval Status: `{pending|approved|rejected}`
- Approval Citation: `{link/quote or none}`
- Plan Commit Hash: `{commit hash or none}`
- Ready-for-Orchestration: `{yes|no}`

## Completion Checklist

- [ ] All acceptance criteria met
- [ ] Validation commands pass
- [ ] Plan approved and committed before orchestration begins
- [ ] User-model ambiguities resolved or escalated
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
```

## Template: Single-Story Plan

```markdown
# Story: {Story Title}

## Goal

{Single-story objective}

## User Model

### User Gamut
- {examples only; broad dimensions}

### User-Needs Gamut
- {examples only; broad dimensions}

### Ambiguities From User Model
- {decision points and how resolved/escalated}

## Context References

- `{path}:line` - {relevance}

## Acceptance Criteria

- [ ] {criterion}
- [ ] {criterion}

## Implementation Tasks

1. {task}
2. {task}
3. {task}

## Testing Strategy

- {tests to add/run}

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `{non-interactive command}`

## Worktree Artifact Check

- Checked At: `{ISO-8601}`
- Planned Target Files: `{path list derived from plan sections}`
- Overlaps Found (path + class): `{none | path -> tracked-dirty | path -> existing-untracked}`
- Escalation Status: `{none|pending|approved|deferred}`
- Decision Citation: `{user approval/deferral reference or none}`

## Plan Approval and Commit Status

- Approval Status: `{pending|approved|rejected}`
- Approval Citation: `{link/quote or none}`
- Plan Commit Hash: `{commit hash or none}`
- Ready-for-Orchestration: `{yes|no}`

## Validation Loop Results

- Missing details check: {result}
- Ambiguity check: {result}
- Plan-commit status check: {result}
- Iterations run: {1-3}
```

## Quality Checks

A complete plan should be:
- Context-rich and implementation-ready
- Specific to repository patterns
- Testable with concrete commands
- Clear enough for an agent without prior project context
- Explicit about unresolved ambiguity and user impact

## Reporting

After generating plans, report:
- Plan type chosen (single-story or epic)
- Paths to created files
- Story count
- Key dependencies
- Major risks and ambiguity decisions
- Validation loop outcome
