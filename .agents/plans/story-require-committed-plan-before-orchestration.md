# Story: Require Committed Plan Before Orchestration

## Goal

Prevent ambiguous orchestration starts by requiring the orchestrator to escalate when asked to execute a plan document that is not committed, and require planning guidance to include an explicit plan-commit step after plan approval.

## User Model

### User Gamut
- Solo maintainers iterating quickly who need deterministic plan-to-execution handoffs.
- Teams coordinating multi-agent work where plan provenance must be auditable.
- Review-focused leads who need confidence that the executed plan is the approved snapshot.
- Contributors working in dirty branches where uncommitted plan edits can drift from approved intent.

### User-Needs Gamut
- A hard safety gate that blocks orchestration from uncommitted plan documents.
- Clear escalation behavior when the requested plan path is untracked or modified.
- Planning workflow that explicitly commits approved plan artifacts before implementation orchestration.
- Evidence in docs and templates that the approval/commit handoff was completed.

### Ambiguities From User Model
- Whether the gate should allow uncommitted plans with warning-only behavior.
- Resolved default: escalate and hard-stop orchestration for that plan path until the plan is committed.
- Override policy: only explicit user override may bypass this gate for a one-time run; default remains block.

## Plan Path Resolution Rules

- Single-path request: use the exact normalized path provided in the orchestration request.
- Multi-path request: check each requested plan path independently; block orchestration for any uncommitted path.
- Implicit plan request (no path): orchestrator must escalate for missing plan-path specificity before running committed-state checks.
- Normalization requirement: resolve to repository-relative canonical path before git-state checks.

## Committed-State Definition

- `Committed` for a plan path means all are true:
  - file is tracked by git,
  - file has no staged or unstaged diffs,
  - file content is present in `HEAD`.
- Non-committed states that trigger escalation:
  - `untracked`,
  - tracked but `modified` (staged or unstaged),
  - path missing from working tree.

## Context References

- `ORCHESTRATOR_AGENT.md:37` - mission section where orchestration prerequisites can be clarified.
- `ORCHESTRATOR_AGENT.md:168` - development-loop area where execution preflight gates belong.
- `ORCHESTRATOR_AGENT.md:604` - recovery instructions already rely on git state checks.
- `planning_guidance.md:144` - planning process where post-approval actions should be defined.
- `planning_guidance.md:212` - mandatory validation loop where plan-state checks can be enforced.
- `planning_guidance.md:388` - single-story template to record plan approval/commit handoff metadata.

## Acceptance Criteria

- [ ] `ORCHESTRATOR_AGENT.md` defines a pre-orchestration plan-state gate: if the requested plan file is untracked or has uncommitted changes, orchestrator must escalate and pause execution.
- [ ] Escalation prompt requirements are explicit: include plan path, detected git state (`untracked` or `modified`), and recommended default action.
- [ ] Orchestrator guidance defines what counts as "plan committed" (tracked and clean relative to `HEAD`).
- [ ] Orchestrator guidance defines plan-path resolution behavior for single-path, multi-path, and implicit (missing path) orchestration requests.
- [ ] Gate semantics are explicit: default hard-stop until commit; one-time bypass only with explicit user override citation.
- [ ] `planning_guidance.md` includes an explicit step: after user approves a plan, commit the plan artifact(s) before orchestration begins.
- [ ] `planning_guidance.md` templates include a section to record plan approval and plan-commit evidence.
- [ ] Validation-loop guidance includes checking that unresolved plan-commit status blocks orchestration start.

## Implementation Tasks

1. Update `ORCHESTRATOR_AGENT.md` with a new pre-orchestration plan-state gate section:
   - determine plan path being requested,
   - check if plan file is tracked and clean,
   - escalate and stop if not committed.
   - if plan path is missing/ambiguous, escalate for specificity and do not start orchestration.
2. Define deterministic git-state rules in orchestrator guidance:
   - `untracked` plan file => escalate,
   - tracked but modified/staged-uncommitted => escalate,
   - tracked and clean => eligible for orchestration.
   - missing file path => escalate.
3. Add escalation payload requirements in orchestrator guidance:
   - plan path,
   - detected state,
   - recommended default (`commit plan first`).
   - allowed outcomes: `commit then continue` (default), `cancel orchestration`, `explicit one-time override`.
4. Update `planning_guidance.md` planning workflow with a mandatory post-approval step:
   - commit approved plan doc(s) before implementation orchestration.
5. Update plan templates in `planning_guidance.md` with `Plan Approval and Commit Status` fields:
   - approval status,
   - approval citation,
   - plan commit hash,
   - ready-for-orchestration status.
6. Update validation-loop guidance in `planning_guidance.md` to require plan-commit status closure before orchestration.

## Testing Strategy

- Documentation grep checks for committed-plan gate language in orchestrator instructions.
- Documentation grep checks for post-approval plan commit step in planning guidance.
- Template audit to verify `Plan Approval and Commit Status` exists in planning templates.

## Validation Commands

- `rg "plan-state gate|pre-orchestration|untracked|modified|tracked and clean|commit plan first" ORCHESTRATOR_AGENT.md`
- `rg "after user approves|commit the plan|before orchestration begins|plan artifact" planning_guidance.md`
- `rg "Plan Approval and Commit Status|approval citation|plan commit hash|ready-for-orchestration" planning_guidance.md`
- `rg "Validation Loop|blocks orchestration|plan-commit status" planning_guidance.md`

## Validation Evidence Record

| Command | Baseline Result | Post-Change Result | Delta | Evidence |
|---------|------------------|--------------------|-------|----------|
| `rg "plan-state gate|pre-orchestration|untracked|modified|tracked and clean|commit plan first" ORCHESTRATOR_AGENT.md` | `fail (no explicit committed-plan gate)` | `pass (committed-plan gate + escalation defaults present)` | `improvement (fail->pass)` | `Post-change includes deterministic state rules and escalation payload requirements.` |
| `rg "after user approves|commit the plan|before orchestration begins|plan artifact" planning_guidance.md` | `fail (no explicit post-approval plan-commit step)` | `pass (explicit post-approval plan commit requirement present)` | `improvement (fail->pass)` | `Planning process now requires commit of approved plan docs before orchestration.` |
| `rg "Plan Approval and Commit Status|approval citation|plan commit hash|ready-for-orchestration" planning_guidance.md` | `fail (template fields missing)` | `pass (template section and fields present)` | `improvement (fail->pass)` | `Templates include auditable approval/commit handoff metadata.` |
| `rg "Validation Loop|blocks orchestration|plan-commit status" planning_guidance.md` | `pass (validation loop exists)` | `pass (loop includes plan-commit closure gate)` | `pass->pass` | `Validation loop preserved and extended with orchestration block condition.` |

## Validation Exception Ledger

| Story | Iteration Scope | Command Set | Reason | Requesting User | Approval Citation | Timestamp | Expiry/Validity |
|-------|------------------|-------------|--------|-----------------|-------------------|-----------|-----------------|
| `Require Committed Plan Before Orchestration` | `Iteration 1` | `none` | `none` | `none` | `none` | `2026-04-15` | `none` |

## Validation Loop Results

- Iteration 1:
  - Missing details check: FAIL; path resolution and outcome handling were underspecified.
  - Ambiguity check: FAIL; override policy and commit scope were insufficiently explicit.
- Iteration 2:
  - Added explicit plan-path resolution rules and committed-state definition.
  - Added hard-stop default with explicit one-time user override policy.
  - Added deterministic escalation outcomes and missing-path handling.
  - Missing details check: PASS.
  - Ambiguity check: PASS.
- Iterations run: 2
