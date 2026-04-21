# Story: Clarify Orchestrator Scope and Commit Reuse Update

## Goal

Clarify orchestrator authority boundaries so it coordinates planning and delegation without implementing code directly, while also committing the already-applied sub-agent reuse update through the proper developer-subagent workflow.

## User Model

### User Gamut
- Maintainers running long orchestrated loops where role boundaries prevent context and process drift.
- Contributors who depend on clear coordinator-vs-implementer separation for auditability.
- Teams operating in dirty worktrees where orchestration discipline must remain predictable.
- Review owners who need deterministic subagent responsibilities and commit ownership.

### User-Needs Gamut
- Orchestrator behavior that cannot be misread as direct implementation authority.
- Clear allowance for planning research reads without opening implementation-inspection scope.
- Explicit policy for when orchestrator may write files (plan docs only, under planning guidance).
- A concrete path to commit the existing sub-agent reuse documentation change safely.

### Ambiguities From User Model
- Whether "file reads" for orchestrator should include implementation validation.
- Resolved default: orchestrator may read files for planning/research and state reconstruction only, not for implementation-level code review that belongs to reviewer/judge/developer roles.

## Context References

- `ORCHESTRATOR_AGENT.md:17` - current MUST NOT section includes no-write/no-implementation rules.
- `ORCHESTRATOR_AGENT.md:19` - blanket file-read prohibition conflicts with planning research needs.
- `ORCHESTRATOR_AGENT.md:29` - trust/verify language can be overread as orchestration-level implementation inspection.
- `ORCHESTRATOR_AGENT.md:179` - session-reuse policy section already modified and currently uncommitted.
- `DEVELOPER_SUBAGENTS.md:11` - developer role includes required implementation commits.
- `DEVELOPER_SUBAGENTS.md:252` - commit requirement and exception clause that can be misused.
- `planning_guidance.md:160` - planning requires codebase intelligence gathering.
- `planning_guidance.md:204` - planning process requires constructing plan artifacts.

## Acceptance Criteria

- [ ] `ORCHESTRATOR_AGENT.md` explicitly defines that orchestrator never implements code or directly edits implementation files.
- [ ] `ORCHESTRATOR_AGENT.md` explicitly permits file reads for planning/research and recovery only, with implementation inspection delegated to subagents.
- [ ] `ORCHESTRATOR_AGENT.md` explicitly permits writing only plan documents, and only when following `planning_guidance.md`.
- [ ] `ORCHESTRATOR_AGENT.md` distinguishes subagent execution failure from normal judge outcome `NEEDS REVISION`.
- [ ] The existing sub-agent reuse changes in `ORCHESTRATOR_AGENT.md` are committed via the normal developer-subagent workflow (not direct orchestrator implementation).
- [ ] Resulting language no longer conflicts with planning responsibilities defined in `planning_guidance.md`.
- [ ] Scope is explicit: this story modifies `ORCHESTRATOR_AGENT.md` only; `DEVELOPER_SUBAGENTS.md` and `planning_guidance.md` are read-only references for consistency checks.
- [ ] Subagent failure taxonomy includes objective triggers for "unusable output" (missing required report sections, schema violations, or tool/runtime error output).

## Commit Protocol

- Commit ownership: developer subagent performs staging and commit for story-file changes.
- Commit subject format: `[Story X.Y] Clarify orchestrator scope boundaries and failure taxonomy`.
- Commit body: optional, but must mention that prior sub-agent session-reuse edits are included if they were already present.
- Provenance evidence required in report:
  - commit hash,
  - commit subject,
  - confirmation that developer subagent executed the commit step.

## Implementation Tasks

1. Update `ORCHESTRATOR_AGENT.md` role-boundary section to separate:
   - prohibited implementation actions,
   - allowed planning/research reads,
   - allowed plan-doc writes under `planning_guidance.md` only.
2. Add explicit failure taxonomy text in `ORCHESTRATOR_AGENT.md`:
   - `subagent failure` (crash/timeout/tool error/rate-limit unusable output) -> launch NEW subagent,
   - `NEEDS REVISION` judge outcome -> normal revision loop (not failure).
3. Add a brief guardrail that implementation inspection belongs to reviewer/judge/developer prompts, not orchestrator direct file inspection.
4. Commit the existing session-reuse update in `ORCHESTRATOR_AGENT.md` using a developer-subagent commit flow with a story-formatted commit message.
5. Run read-only consistency pass against `DEVELOPER_SUBAGENTS.md` and `planning_guidance.md` to verify no contradictory interpretation remains.
6. Record commit provenance evidence in the completion report.

## Testing Strategy

- Diff and keyword audit of `ORCHESTRATOR_AGENT.md` for role-boundary clarity and failure taxonomy.
- Cross-document wording check against `DEVELOPER_SUBAGENTS.md` and `planning_guidance.md`.
- Git verification that the prior sub-agent reuse modifications are committed.

## Validation Commands

- `rg "NEVER IMPLEMENT DIRECTLY|MUST NOT Do|planning_guidance\.md|research|recovery|NEEDS REVISION|subagent failure" ORCHESTRATOR_AGENT.md`
- `rg "Commit Frequently|Creating commits for the assigned story plan is required" DEVELOPER_SUBAGENTS.md`
- `git status --short`
- `git log --oneline -n 5`
- `rg "Scope is explicit|modifies `ORCHESTRATOR_AGENT\.md` only|unusable output|missing required report sections|schema violations" .agents/plans/story-orchestrator-scope-clarifications.md ORCHESTRATOR_AGENT.md`

## Validation Evidence Record

| Command | Baseline Result | Post-Change Result | Delta | Evidence |
|---------|------------------|--------------------|-------|----------|
| `rg "NEVER IMPLEMENT DIRECTLY|MUST NOT Do|planning_guidance\.md|research|recovery|NEEDS REVISION|subagent failure" ORCHESTRATOR_AGENT.md` | `pass (existing boundary + revision terms partially present)` | `pass (explicit clarified policy and failure taxonomy present)` | `pass->pass` | `Post-change matches include explicit planning-read/write carveout and failure-vs-revision distinction.` |
| `rg "Commit Frequently|Creating commits for the assigned story plan is required" DEVELOPER_SUBAGENTS.md` | `pass` | `pass` | `pass->pass` | `Developer commit ownership language remains present; used for orchestration commit pathway.` |
| `git status --short` | `fail (uncommitted ORCHESTRATOR_AGENT.md changes present)` | `pass (working tree clean for targeted story changes)` | `improvement (fail->pass)` | `Post-change verifies prior reuse edits were committed through developer-subagent workflow.` |
| `git log --oneline -n 5` | `pass (no story commit for reuse clarification yet)` | `pass (contains story commit for reuse clarification + scope clarification)` | `pass->pass` | `Recent log shows commit subject in story format documenting the committed update.` |
| `rg "Scope is explicit|modifies `ORCHESTRATOR\.md` only|unusable output|missing required report sections|schema violations" .agents/plans/story-orchestrator-scope-clarifications.md ORCHESTRATOR_AGENT.md` | `fail (objective scope/taxonomy language not yet explicit)` | `pass (scope boundary and objective unusable-output triggers present)` | `improvement (fail->pass)` | `Plan and orchestrator text contain deterministic scope rule and failure-trigger criteria.` |

## Validation Exception Ledger

| Story | Iteration Scope | Command Set | Reason | Requesting User | Approval Citation | Timestamp | Expiry/Validity |
|-------|------------------|-------------|--------|-----------------|-------------------|-----------|-----------------|
| `Clarify Orchestrator Scope and Commit Reuse Update` | `Iteration 1` | `none` | `none` | `none` | `none` | `2026-04-15` | `none` |

## Validation Loop Results

- Iteration 1:
  - Missing details check: FAIL; commit workflow proof and subject format were under-specified.
  - Ambiguity check: FAIL; scope boundary and "unusable output" criteria were not objective.
- Iteration 2:
  - Added `Commit Protocol` with deterministic commit format and required provenance evidence.
  - Added explicit scope boundary (modify `ORCHESTRATOR_AGENT.md` only) and objective unusable-output triggers.
  - Missing details check: PASS.
  - Ambiguity check: PASS.
- Iterations run: 2
