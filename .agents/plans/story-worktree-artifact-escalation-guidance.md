# Story: Add Worktree Artifact Escalation Guidance to Planning

## Goal

Add explicit planning guidance that requires escalation before execution when a plan would modify a file that is already dirty in the worktree (tracked with uncommitted changes) or already exists as an untracked file.

## User Model

### User Gamut
- Engineers working in partially dirty branches while orchestrating multiple stories.
- Release-focused maintainers who need to avoid accidental edits to unrelated local work.
- Contributors collaborating with generated files and local artifacts that may be untracked.
- Reviewers who require traceable justification when changing already-dirty files.

### User-Needs Gamut
- Early detection of worktree collision risk before implementation begins.
- Mandatory escalation points that protect user intent and avoid silent overwrite behavior.
- Consistent planner behavior for both tracked-dirty and existing-untracked files.
- Template-level visibility so every plan records whether artifact risk exists.

### Ambiguities From User Model
- Whether escalation should be optional when overlap appears low-risk.
- Resolved default: escalation is mandatory whenever the planned target file is tracked-dirty or exists untracked at plan time.

## Worktree Artifact Model

- Source of planned target files (deterministic):
  - Primary: story-plan sections that enumerate target paths (for example, `New Files to Create`, `Files Modified`, or explicit file-path bullets in `Implementation Tasks`).
  - Secondary fallback: `Context References` entries that explicitly identify modification targets.
- Artifact classes:
  - `tracked-dirty`: tracked file with staged or unstaged uncommitted modifications.
  - `existing-untracked`: file exists on disk and is untracked by git.
- Scope rule:
  - ignored files are out of scope unless explicitly listed as planned target files.
- Escalation unit:
  - batch by story, with one row per overlapping path in escalation payload.

## Context References

- `planning_guidance.md:160` - intelligence-gathering phase where repository state checks can be inserted.
- `planning_guidance.md:204` - plan construction phase where risk gates should be captured in plan docs.
- `planning_guidance.md:212` - mandatory validation loop where this check can be validated.
- `planning_guidance.md:388` - single-story template section to extend with worktree artifact risk logging.
- `ORCHESTRATOR_AGENT.md:606` - recovery instructions already use `git status`, indicating git-state awareness exists.
- `ORCHESTRATOR_AGENT.md:410` - dependency skip pattern provides precedent for deferring unsafe work until conditions are resolved.

## Acceptance Criteria

- [ ] `planning_guidance.md` defines a mandatory pre-implementation worktree artifact check for each planned target file.
- [ ] Guidance explicitly covers both categories: tracked files with uncommitted changes and existing files that are untracked.
- [ ] Guidance requires escalation before implementation when either category overlaps planned modifications.
- [ ] Escalation payload requirements are defined: file path, artifact type, risk summary, and requested user decision.
- [ ] Story templates in `planning_guidance.md` include a section to record artifact-check outcome and escalation status.
- [ ] Validation-loop guidance in `planning_guidance.md` includes verification that no unresolved artifact-overlap escalation remains.
- [ ] `planning_guidance.md` defines who performs checks and when (planner during validation; implementer immediately before edits).
- [ ] `planning_guidance.md` states unresolved pending escalation blocks implementation for overlapping paths.

## Implementation Tasks

1. Update `planning_guidance.md` planning process to add a mandatory worktree artifact check before implementation execution.
2. Define explicit artifact classes:
   - `tracked-dirty` (tracked file with staged or unstaged modifications),
   - `existing-untracked` (file exists on disk and is untracked by git).
3. Add mandatory escalation rule when planned file modifications overlap either class.
4. Add escalation payload schema fields in guidance:
   - target file,
   - artifact class,
   - why unsafe/ambiguous,
   - recommended default,
   - user decision needed.
5. Add normative flow and timing:
   - planner performs artifact check during plan validation,
   - implementer re-checks immediately before modifications,
   - unresolved pending escalation blocks implementation for overlapping paths.
6. Update Single-Story and Epic Story templates in `planning_guidance.md` with a `Worktree Artifact Check` section.
7. Add `Worktree Artifact Check` required fields:
   - Checked At,
   - Planned Target Files,
   - Overlaps Found (path + class),
   - Escalation Status (none/pending/approved/deferred),
   - Decision Citation.
8. Add validation-loop checkpoint language ensuring artifact-overlap escalations are resolved (approved direction or explicit deferral) before implementation starts.

## Testing Strategy

- Documentation grep checks for new artifact terminology and escalation directives.
- Template audit to ensure `Worktree Artifact Check` is present where story plans are authored.
- Manual consistency review with existing orchestration safety language.

## Validation Commands

- `rg "worktree|tracked-dirty|existing-untracked|artifact|escalat" planning_guidance.md`
- `rg "Worktree Artifact Check" planning_guidance.md`
- `rg "Validation Loop|Missing details check|Ambiguity check" planning_guidance.md`
- `rg "before implementation|blocks implementation|planner|implementer|Escalation Status|Decision Citation" planning_guidance.md`

## Validation Evidence Record

| Command | Baseline Result | Post-Change Result | Delta | Evidence |
|---------|------------------|--------------------|-------|----------|
| `rg "worktree|tracked-dirty|existing-untracked|artifact|escalat" planning_guidance.md` | `fail (no explicit worktree-artifact escalation policy)` | `pass (policy terms and escalation requirements present)` | `improvement (fail->pass)` | `Post-change matches include mandatory artifact classes and escalation directive language.` |
| `rg "Worktree Artifact Check" planning_guidance.md` | `fail (template section missing)` | `pass (story templates include artifact-check section)` | `improvement (fail->pass)` | `Post-change confirms template-level capture of overlap and escalation status.` |
| `rg "Validation Loop|Missing details check|Ambiguity check" planning_guidance.md` | `pass` | `pass (includes artifact-overlap resolution checkpoint)` | `pass->pass` | `Validation loop remains present and includes new artifact-risk closure requirement.` |
| `rg "before implementation|blocks implementation|planner|implementer|Escalation Status|Decision Citation" planning_guidance.md` | `fail (timing/ownership/blocking semantics absent)` | `pass (timing ownership and block-on-pending semantics explicit)` | `improvement (fail->pass)` | `Post-change includes deterministic flow and required template fields for escalation closure.` |

## Validation Exception Ledger

| Story | Iteration Scope | Command Set | Reason | Requesting User | Approval Citation | Timestamp | Expiry/Validity |
|-------|------------------|-------------|--------|-----------------|-------------------|-----------|-----------------|
| `Add Worktree Artifact Escalation Guidance to Planning` | `Iteration 1` | `none` | `none` | `none` | `none` | `2026-04-15` | `none` |

## Validation Loop Results

- Iteration 1:
  - Missing details check: FAIL; planned-target source and template field schema were not deterministic.
  - Ambiguity check: FAIL; timing/ownership and escalation granularity were underspecified.
- Iteration 2:
  - Added deterministic planned-target source, artifact scope, and escalation-unit rules.
  - Added normative timing/ownership flow and block-on-pending implementation rule.
  - Added required `Worktree Artifact Check` fields for template updates.
  - Missing details check: PASS.
  - Ambiguity check: PASS.
- Iterations run: 2
