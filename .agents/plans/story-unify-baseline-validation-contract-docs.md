# Story: Unify Baseline Validation Contract Across Planning and Subagent Docs

## Goal

Update planning and orchestration instruction documents so every story uses a single standard validation command set with baseline evidence captured before implementation, post-change evidence captured after implementation, and explicit delta analysis preventing unsupported "pre-existing failure" claims.

## Validation Contract Specification

- Source of truth artifact: the canonical source of truth is the story context file section `## Validation Evidence Record` for each story iteration.
- Developer report role: developer completion/revision reports must include the same table for transmission, but story-context records are authoritative for reviewer/judge decisions.
- Persistence rule: on every iteration, orchestrator must ensure the latest developer evidence table is written to the story context file section `## Validation Evidence Record` so evidence is versioned with repository state (chat-only evidence is insufficient).
- Required table schema (exact columns): `Command | Baseline Result | Post-Change Result | Delta | Evidence`.
- Command-set selection precedence (fixed across all role docs):
  1. Story-defined `Validation Commands` when present and executable.
  2. Project-standard full-suite command bundle.
  3. Repository-appropriate generic full-suite fallback (lint, tests, and any required project health checks).
- Command-set freeze rule: the selected command set is frozen at story iteration 1 baseline and reused for the story unless exception-approved.
- Fallback granularity rule: fallback evaluation is per-command (not all-or-nothing). Any substituted command must be logged in `Evidence` with substitution reason.
- Command-set change policy: if a command must change mid-story, orchestrator must escalate and obtain explicit requesting-user approval, then start a new baseline epoch and document reason/scope.
- Epoch completion gate: story completion uses the active epoch baseline and additionally requires an approved exception ledger entry for each removed/replaced command from prior epochs to prevent silent gate-softening.
- Delta algorithm (deterministic):
  - Pass -> Fail: regression (disallowed unless exception-approved).
  - Fail -> Pass: improvement.
  - Fail -> Fail: allowed only when no new failing test/rule identifiers are introduced.
- If identifiers are unavailable, evidence must include a manual failure-signature comparison and be treated as `Needs Judge Attention` until judge confirms no net regression.
- Failure-signature normalization minimums: include normalized failing unit identifiers where available (test name, lint rule id, or error code), plus command exit code and stable error excerpt hash/summary; if normalization is impossible, auto-escalate to `Needs Judge Attention`.
- Exception record schema (required fields): `Story | Iteration Scope | Command Set | Reason | Requesting User | Approval Citation | Timestamp | Expiry/Validity`.
- Exception ledger location: exception entries must be stored in the same story context file under `## Validation Exception Ledger`; reviewer and judge must verify entries from this section only.
- Failure-signature hash rule: when hash evidence is required, use SHA-256 over normalized signature text (`command + normalized identifiers + normalized message excerpt`) and record the hex digest in `Evidence`.

## Canonical Paths

- Canonical documentation files for this story are repository-root paths:
  - `planning_guidance.md`
  - `ORCHESTRATOR_AGENT.md`
  - `DEVELOPER_SUBAGENTS.md`
  - `REVIEWER_SUBAGENTS.md`
  - `REVIEW_JUDGE_SUBAGENTS.md`
- `.llm-conductor/*` is a path alias in this repository and must not be treated as a separate source tree.

## User Model

### User Gamut
- Solo maintainers running rapid agent-driven implementation loops on local repositories.
- Teams relying on orchestrator/subagent workflows for multi-story delivery with review gates.
- CI-focused contributors who need deterministic pass/fail evidence and regression attribution.
- Technical leads auditing process quality and preventing reward-hacking in automated workflows.

### User-Needs Gamut
- Reliable distinction between pre-existing failures and new regressions.
- One clear validation contract shared across planner, implementer, reviewer, and judge roles.
- Minimal ambiguity in final story outcomes and completion criteria.
- Practical workflow that defaults to full-suite quality checks without brittle ad-hoc command selection.

### Ambiguities From User Model
- Whether plans should maintain separate pre/post command lists or one command list run twice.
- Resolved default: one standard validation command set, with separate baseline/post result recording and delta analysis.

## Context References

- `planning_guidance.md:212` - mandatory validation loop section that will be extended to include baseline result capture.
- `ORCHESTRATOR_AGENT.md:138` - development loop where baseline gate and regression delta checks must be inserted.
- `DEVELOPER_SUBAGENTS.md:237` - acceptance verification/completion report sections to extend with baseline/post/delta evidence.
- `REVIEWER_SUBAGENTS.md:134` - adversarial review workflow where baseline claim verification should be required.
- `REVIEW_JUDGE_SUBAGENTS.md:170` - judgment report/decision framework where baseline evidence adequacy and regression decisions must be enforced.

## Acceptance Criteria

- [ ] `planning_guidance.md` defines a required Validation Baseline concept using one command set run before and after implementation, with mandatory delta analysis.
- [ ] Story and single-story templates include sections to record baseline results, post-change results, and regression delta.
- [ ] `ORCHESTRATOR_AGENT.md` requires baseline capture once at story iteration 1 before implementation, reuse that baseline through later iterations, and enforces a no-new-failures-vs-baseline completion gate (exceptions require explicit approval from the requesting user after orchestrator escalation).
- [ ] `DEVELOPER_SUBAGENTS.md` requires Step 0 baseline run only at story iteration 1, requires post-change validation on every iteration, and requires completion report evidence for baseline/post/delta.
- [ ] `REVIEWER_SUBAGENTS.md` requires verification of baseline evidence and flags unsupported "pre-existing" claims as findings.
- [ ] `REVIEW_JUDGE_SUBAGENTS.md` requires explicit baseline evidence adequacy judgment and regression decisioning before approval.
- [ ] Guidance language remains generic and defaults to full-suite checks (e.g., `bun test`, `bun run lint`) rather than file-scoped success criteria.
- [ ] A shared evidence schema is defined and used consistently across role documents: `Command | Baseline Result | Post-Change Result | Delta | Evidence`.
- [ ] Regression delta semantics are explicit: command-level pass/fail regression is disallowed, and fail-to-fail outcomes require evidence of no new failing test/rule identifiers unless exception-approved.
- [ ] Exception workflow is explicit: only the requesting user can approve an exception after orchestrator escalation, and approval scope must be logged per story and command set.
- [ ] All five role documents define the same source-of-truth artifact, command-selection precedence, command-set freeze/change policy, and deterministic delta algorithm.

## Implementation Tasks

1. Update `planning_guidance.md`:
   - Add baseline-first validation policy and anti-reward-hacking language.
   - Update templates to include baseline/post/delta reporting blocks.
   - Clarify one command-set principle and generic full-suite default guidance.
2. Update `ORCHESTRATOR_AGENT.md`:
   - Add baseline checkpoint in orchestration loop and state tracking fields for baseline/post/delta.
   - Lock timing: baseline is captured once per story at iteration 1 and reused for all revision iterations.
   - Add completion decision gate for regression deltas.
3. Update `DEVELOPER_SUBAGENTS.md`:
   - Add mandatory Step 0 baseline run only when story iteration equals 1.
   - For revision iterations, require reuse of recorded baseline plus fresh post-change run and delta comparison.
   - Extend completion report template with baseline/post/delta sections.
4. Update `REVIEWER_SUBAGENTS.md`:
   - Add baseline verification responsibilities and severity guidance for unsupported pre-existing claims.
5. Update `REVIEW_JUDGE_SUBAGENTS.md`:
   - Add required baseline adequacy and regression evaluation fields in judgment report.
6. Cross-document consistency pass:
   - Ensure terminology and required evidence fields match exactly across all updated instruction documents.
7. Define and propagate deterministic regression decision rules:
   - Add a single delta-comparison algorithm all roles reference.
   - Require role-specific report sections to include the same evidence columns.
8. Define and propagate exception protocol:
   - Require orchestrator escalation entry, explicit requesting-user approval citation, and scope boundaries (story + command set + iteration applicability).

## Testing Strategy

- Documentation consistency validation by searching for required terms/sections across all modified files.
- Manual review that each role document references baseline, post-change, and delta in a non-conflicting way.
- Run lightweight markdown lint/format checks if available in repo standards.

## Validation Commands

- `rg "Validation Baseline|baseline|post-change|delta|pre-existing" planning_guidance.md ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md`
- `rg "Command \| Baseline Result \| Post-Change Result \| Delta \| Evidence" planning_guidance.md ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md`
- `rg "requesting user|exception|escalation" ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md`

## Validation Evidence Record

| Command | Baseline Result | Post-Change Result | Delta | Evidence |
|---------|------------------|--------------------|-------|----------|
| `rg "Validation Baseline\|baseline\|post-change\|delta\|pre-existing" planning_guidance.md ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md` | `pass (matches present across target docs)` | `pass (matches present across target docs)` | `pass->pass` | `Baseline and post both exit 0; evidence includes matched lines showing baseline/post-change/delta terminology remains present.` |
| `rg "Command \| Baseline Result \| Post-Change Result \| Delta \| Evidence" planning_guidance.md ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md` | `pass (schema string found in all role docs and planning guidance)` | `pass (schema string found in all role docs and planning guidance)` | `pass->pass` | `Baseline and post both exit 0; exact schema string matches confirmed in planning and role documents.` |
| `rg "requesting user\|exception\|escalation" ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md` | `pass (exception/escalation language found)` | `pass (exception/escalation language found)` | `pass->pass` | `Baseline and post both exit 0; requesting-user approval and escalation terms remain present in all role docs.` |

## Validation Exception Ledger

| Story | Iteration Scope | Command Set | Reason | Requesting User | Approval Citation | Timestamp | Expiry/Validity |
|-------|------------------|-------------|--------|-----------------|-------------------|-----------|-----------------|
| `Unify Baseline Validation Contract Across Planning and Subagent Docs` | `Iteration 2 revision cycle` | `none` | `none (no exceptions requested or required)` | `none` | `none` | `2026-04-13` | `none` |

## Validation Loop Results

- Iteration 1:
  - Missing details check found blockers: unqualified canonical file target and invalid validation command (`check.py`).
  - Ambiguity check found unresolved decisions: canonical instruction tree ownership and baseline timing across iterations.
- Iteration 2:
  - Plan updated to require mirrored updates in both `.llm-conductor` and `llm-conductor` trees.
  - Baseline timing locked to one capture at story iteration 1, reused through revisions.
  - Validation command corrected to `bun run scripts/devlog/check.ts`.
  - Missing details check: pending rerun.
  - Ambiguity check: pending rerun.
- Iteration 2 rerun outcome:
  - Missing details check: no blocking gaps.
  - Ambiguity check still open on baseline timing semantics, exception authority, and mirrored AC coverage.
- Iteration 3:
  - Plan updated to lock baseline timing semantics across iterations and define exception authority as explicit approval from the requesting user after escalation.
  - Plan updated so AC coverage for developer requirements explicitly includes both `.llm-conductor` and `llm-conductor` trees.
  - Missing details check rerun found remaining mirror-scope gap for reviewer/judge AC entries.
- Iteration 4:
  - Plan updated so reviewer and judge AC entries explicitly include both `.llm-conductor` and `llm-conductor` trees.
  - Missing details check rerun: no blocking gaps.
  - Ambiguity check rerun still flagged closure-state bookkeeping and exception authority wording.
- Iteration 5:
  - Exception authority wording locked to explicit approval from the requesting user after orchestrator escalation.
  - Validation-loop bookkeeping updated to reflect final rerun closure.
  - Missing details check: no blocking gaps.
  - Ambiguity check: no unresolved high-impact ambiguity; no escalation needed.
- Iterations run: 5 (complete)

- Iteration 6 (path correction + revalidation after repository migration):
  - Canonical file targets corrected to repository-root instruction files.
  - Missing details check found blocking invalid validation commands for this repository.
  - Plan updated with executable documentation-validation commands.
  - Ambiguity check found unresolved evidence schema, delta semantics, exception protocol, and canonical-path policy.
  - Plan updated to define explicit requirements for all four areas.
  - Missing details check (rerun): PASS (no blocking gaps).
  - Ambiguity check (rerun): FAIL; additional ambiguities identified around artifact persistence, fallback granularity, epoch completion semantics, and normalization behavior.
- Iteration 7:
  - Plan updated with explicit artifact persistence, per-command fallback behavior, epoch completion gate, and failure-signature normalization minimums.
  - Ambiguity check (rerun): FAIL; residual ambiguity remained around canonical evidence ownership, exception ledger location, and hash method standardization.
- Iteration 8:
  - Plan updated to make story context the authoritative evidence source, define developer report as a transmission mirror, lock exception ledger location, and define SHA-256 signature hashing.
  - Ambiguity check (rerun): PASS (no unresolved high-impact ambiguity).
- Iterations run: 8 (path-correction revalidation complete)
