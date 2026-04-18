# Story: Simplify Validation Contract to Starting-State Check

## Goal

Replace the ~445-line "Unified Validation Contract" introduced by commit `ba024bb9` with a minimal starting-state validation check. Catch the real reward-hacking attack ("these tests were already failing") without duplicating contract prose across five docs, contradicting the orchestrator's "never implement" rule, or inventing unimplementable machinery (SHA-256 of normalized failure signatures, baseline epochs, exception ledgers).

## Background

Commit `ba024bb9` ("Unify baseline validation contract across guidance docs") copied the same ~15-line "Unified Validation Contract" block verbatim into `ORCHESTRATOR_AGENT.md`, `DEVELOPER_SUBAGENTS.md`, `REVIEWER_SUBAGENTS.md`, `REVIEW_JUDGE_SUBAGENTS.md`, and `planning_guidance.md`, plus added heavy scaffolding: Phase 0, a Validation Epoch Status tracker, evidence mirror tables in every role, an exception ledger with 8 fields, command-set precedence/freeze/epoch vocabulary, SHA-256 failure-signature hashing, and a `Needs Judge Attention` side-channel.

The attack it targeted is real — developers explaining away current failures as "pre-existing" when they weren't, seen ~100 times. The fix is over-engineered:

- **DRY violation:** five identical copies of the contract, no cross-references.
- **Orchestrator role contradiction:** Phase 0 implies the orchestrator runs validation commands; the persistence rule implies it writes into story context files each iteration. Both violate `ORCHESTRATOR_AGENT.md:7-35` ("NEVER IMPLEMENT DIRECTLY").
- **Spec/log conflation:** story context file (plan/spec) declared authoritative for mutable per-iteration evidence tables.
- **Unimplementable machinery:** SHA-256 over "normalized failure signatures" isn't reliably computable across tools, versions, and line shifts; the hash adds no information over the identifier it's computed from.
- **Useless jargon:** "command set," "freeze," "epoch," "precedence," "exception ledger" add nothing over a commit hash + the commands already listed in the story plan.

Per conversation with the requesting user: per-iteration repo-state drift does not occur in this orchestration system (if it does, the story is restarted); the "stale baseline" concern and "epoch" concept do not apply. The developer's starting commit hash is the only anchor needed.

## User Model

### User Gamut

- LLM agents under each role (orchestrator, developer-subagent, reviewer-subagent, judge-subagent) — primary readers; each reads a single role doc.
- Human operators tasking the orchestrator with epic/story completion, and also tasking the orchestrator to generate plans.
- Operators auditing why a story was approved with broken tests.

### User-Needs Gamut

- Reliable catch of the "already failing" reward-hack.
- Reliable catch of leftover uncommitted/untracked files at story start — either a lie or inherited broken state.
- Role docs each readable and actionable in isolation.
- Orchestrator instructions that remain unambiguous about NOT running test suites and NOT rewriting plan/context files.
- A contract that treats the developer's actual starting commit as the baseline, not a frozen iteration-1 snapshot.
- Plans where validation commands are spelled out up-front, no runtime command selection.

### Ambiguities From User Model

- **Reviewer always reproduces baseline, or only sometimes?** Resolved: reviewer always reruns at HEAD; reproduces the developer's reported starting commit only when HEAD shows any failures. No attack surface exists when nothing is being explained away.
- **Missing `Validation Commands` in a plan — fall back or stop?** Resolved: stop and report planning gap. Applies to initial and revision iterations identically.
- **Clean-tree precondition on revision iterations?** Resolved: yes; remains satisfiable because prior-iteration commits are committed (tree is clean). "Starting commit" for a revision is `HEAD` at the moment the revision iteration begins, which includes the developer's prior iteration's commits. The reviewer reproduces from that commit, not from the story's iteration-1 starting point.
- **User exception for a regression — via new artifact or existing escalation?** Resolved: via the existing NEEDS_DISCUSSION / Escalation Log mechanism in `ORCHESTRATOR_AGENT.md`. No new artifact. If a judge sees a regression and has no user-granted exception recorded in the orchestrator's Escalation Log, the judge returns NEEDS_DISCUSSION and the orchestrator handles escalation per its existing flow.
- **"Same identifier" for `fail→fail` classification?** Resolved: exact string match on the tool-emitted identifier (full test name, eslint rule ID, compiler error code, etc.). Partial matches and exit-code-only matches do not qualify. If a tool does not emit a stable identifier, any fail→fail row from that command must be treated as potentially `new identifier` (regression) and escalated for judge adjudication — erring toward catching the attack.
- **Handoff artifact for validation results?** Resolved: the developer's completion/revision report IS the authoritative handoff. The orchestrator passes that report verbatim into the reviewer and judge subagent prompts (per its existing mechanism — no new file writes). The reviewer echoes the reviewer-reproduced results into its own report; the judge records the final verified results in `.judgement.N.md`. No file in the repository is mutated to carry evidence between roles.
- **Format for the pre-existing failures list?** Resolved: one row per command that had any failure at starting state. Each row lists the command followed by a colon-separated list of tool-emitted failing identifiers, e.g., `bun test: test/foo.test.ts > suite > case A, test/bar.test.ts > suite > case B`. Commands with no failures are omitted from the list (or the entire list reads `none` when no command failed). This format is used identically in the developer report, the reviewer report, and the judge's `### Verified Validation Results` subsection.

## Context References

Use landmark strings (section headings or distinctive phrases) to locate targets; the file has grown since `ba024bb9` so exact line numbers drift. All line numbers below are current (verified post-draft); treat them as advisory — confirm via grep before editing.

**`ORCHESTRATOR_AGENT.md`:**

- Keep intact: section heading "⛔ CRITICAL: NEVER IMPLEMENT DIRECTLY" and the list of prohibitions below it.
- Remove: section `## Unified Validation Contract (Mandatory)` (currently starts at line 59).
- Remove: `### Validation Epoch Status` table inside State Tracking.
- Remove: `### Phase 0: Baseline and Command-Set Lock (Iteration 1 Only)`.
- Revert: the additions inside Phase 1 that require verifying a developer evidence table and persisting it to story context.
- Revert: the APPROVED-AS-IS gate additions that check for regressions and exception-ledger entries (restore to the pre-commit two-line "Mark story complete / Proceed to next story").
- Remove: "Validation requirements for this iteration:" blocks inside the Developer Initial, Developer Revision, Reviewer, and Judge subagent-prompt templates. No replacement — each subagent reads its own role doc.

**`planning_guidance.md`:**

- Remove: section `## Unified Validation Contract (Mandatory)` (currently starts at line 288).
- Remove: `## Validation Evidence Record` template block inside the epic-story template.
- Remove: `## Validation Exception Ledger` template block inside the epic-story template.
- Remove: `## Validation Evidence Record` and `## Validation Exception Ledger` template blocks inside the single-story template.
- Keep and strengthen: the existing `## Validation Commands` template sections in both templates. Add one sentence: "Every story plan MUST list the validation commands. These are the source of truth for the developer's starting-state check and completion rerun; no runtime substitution is permitted."

**`DEVELOPER_SUBAGENTS.md`:**

- Remove: section `## Unified Validation Contract (Mandatory)` (currently starts at line 26).
- Remove entirely (not reposition): `## Step 0: Validation Baseline and Command Set`.
- Insert new: `## Pre-Implementation: Starting-State Check` positioned **between the existing Step 2 (Understand Dependencies) and Step 3 (Implementation)**. Do not renumber existing steps; insert as an unnumbered section with that heading. (The old "Step 0" is gone; the new section's heading does not use a step number, to avoid cascading renumbering confusion.)
- Extend: the `### Blocked Report Template`'s **Type** enumeration. The current values are "Missing Dependency / Unclear Requirements / Technical Issue". Add "Abnormal Starting State" and "Planning Gap" as additional allowed values. The new Pre-Implementation: Starting-State Check emits reports using the last two.
- Add new: `## Completion: Rerun Validation` at the end of Step 3. Content below.
- Simplify: the evidence table inside "Verify Acceptance Criteria" — remove the mirror table; reference the Completion: Rerun Validation output.
- Rewrite: the `### Validation Evidence Record (Mirror)` and `### Baseline / Post-Change / Delta Notes` blocks inside the Completion Report template → replace with the single minimal block (starting commit hash, pre-existing failures list, post-change results with classification).
- Rewrite: the `### Validation Evidence Record (Mirror)` block inside the Revision Report template → same minimal block.

**`REVIEWER_SUBAGENTS.md`:**

- Remove: section `## Unified Validation Contract (Mandatory)` (currently starts at line 22).
- Replace: `### A0. Validation Evidence Verification (Run Before AC Review)` → rename to `### A0. Verify Starting-State Claims` with the content specified in Task 2 below.
- Simplify: the `### Validation Evidence Status` block inside the review-report template into a short block (see Task 2).

**`REVIEW_JUDGE_SUBAGENTS.md`:**

- Remove: section `## Unified Validation Contract (Mandatory)` (currently starts at line 31).
- Remove: the six-bullet "Before evaluating reviewer findings..." audit block inside Step 2.
- Remove: `### Validation Evidence Judgment` table inside the judgment report template.
- Remove: the "Regression gate decision:" block inside the Overall Verdict section.
- Add: one bullet in the Decision Framework section stating the regression rule (see Task 3).
- Add: one short paragraph in the judgment-report template instructing the judge to record the reviewer's verified pre/post results inside the existing `.judgement.N.md` file — specifically as a new subsection `### Verified Validation Results` placed immediately after the existing `### Summary` table. No new artifact type.

## Acceptance Criteria

- [ ] All five "Unified Validation Contract" duplicate blocks are deleted (grep returns zero matches for the heading string).
- [ ] The developer's completion/revision report is the authoritative handoff artifact for validation results. No role doc requires the orchestrator (or anyone) to write evidence into a tracked file between roles. The reviewer consumes the developer's report (passed through the orchestrator per existing mechanism), echoes the reviewer-reproduced results in its own report, and the judge's `### Verified Validation Results` subsection in `.judgement.N.md` is the final verdict location.
- [ ] The `### Verified Validation Results` subsection in the judge's `.judgement.N.md` is the **sole** location for the judge's validation verdict; no other regression-gate verdict appears elsewhere in the judgment report.
- [ ] Pre-existing failures lists use a single consistent format across developer, reviewer, and judge reports: one row per failing command, formatted as `<command>: <identifier1>, <identifier2>, ...`; commands with no failures are omitted; the entire list reads `none` when no command failed.
- [ ] `DEVELOPER_SUBAGENTS.md`'s Blocked Report Template enumerates these Type values: Missing Dependency, Unclear Requirements, Technical Issue, Abnormal Starting State, Planning Gap.
- [ ] `ORCHESTRATOR_AGENT.md` retains "NEVER IMPLEMENT DIRECTLY" intact. Phase 0, Validation Epoch Status table, evidence-persistence step, APPROVED-AS-IS regression gate, and per-subagent-prompt validation blocks are removed.
- [ ] The orchestrator is not required by any doc to run validation commands, check out commits for baselining, or write evidence into any file.
- [ ] `planning_guidance.md` loses the Unified Validation Contract section and both template evidence/exception tables; the `## Validation Commands` template sections remain and include the explicit "MUST list" sentence.
- [ ] `DEVELOPER_SUBAGENTS.md` contains a `## Pre-Implementation: Starting-State Check` section that specifies:
  - Clean-working-tree precondition (`git status --porcelain` empty); if not, stop and emit a "Blocked: abnormal starting state" report.
  - Record starting commit hash via `git rev-parse HEAD`.
  - Run the plan's `## Validation Commands`. For each command, record pass/fail plus failing-test/lint-rule identifiers where the tool emits them.
  - If the plan has no `## Validation Commands` section (or it is empty), stop and emit a "Blocked: planning gap" report. Applies to initial and revision iterations identically; inherited commands from prior iterations do not exempt the plan from having the section explicitly.
- [ ] `DEVELOPER_SUBAGENTS.md` contains a `## Completion: Rerun Validation` section that specifies:
  - Rerun the **same** commands that were run at starting-state.
  - Classify each outcome as exactly one of: `pass→pass`, `fail→pass`, `pass→fail`, `fail→fail (same identifier)`, `fail→fail (new identifier)`.
  - "Same identifier" = exact string match on the tool-emitted identifier (test name, lint rule ID, compiler error code). If a tool does not emit a stable identifier, any fail→fail row from that command must be treated as `fail→fail (new identifier)` for gating purposes.
  - Include in the completion and revision reports: starting commit hash, pre-existing failures list (from starting-state check), post-change results classified per the enum.
- [ ] `REVIEWER_SUBAGENTS.md` contains `### A0. Verify Starting-State Claims` specifying:
  - Always rerun the plan's validation commands at HEAD.
  - If any HEAD command fails, check out the developer's reported starting commit and rerun all validation commands there.
  - For each HEAD failure, classify: "pre-existing" (same identifier present at starting commit) or "new" (not present at starting commit).
  - Any new failure at HEAD = CRITICAL regression finding.
  - Mismatch severity rules: developer-reported pre-existing list **larger** than reviewer's reproduced list = CRITICAL (developer is padding the pre-existing set to excuse failures that were actually pass→fail regressions). Developer-reported list **smaller** than reviewer's reproduced list = HIGH (incomplete baseline, not dangerous but sloppy).
  - Reference `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check` for the definition of the starting-state contract rather than restating it.
- [ ] `REVIEW_JUDGE_SUBAGENTS.md` Decision Framework contains a bullet stating: "Regressions (`pass→fail` or `fail→fail (new identifier)`) are not approvable. If a regression exists and the developer cannot fix it, return NEEDS_DISCUSSION so the orchestrator can escalate to the requesting user per its existing escalation flow. Do not rerun commands yourself unless the reviewer's reproduced evidence is ambiguous."
- [ ] `REVIEW_JUDGE_SUBAGENTS.md` judgment-report template contains a `### Verified Validation Results` subsection (placed immediately after the `### Summary` table) with fields: starting commit hash, pre-existing failures (verified by reviewer), post-change results at HEAD, regression findings count, regression gate verdict (pass / blocked / escalated).
- [ ] These terms are absent from all five docs: `command set`, `command-set`, `baseline epoch`, `epoch` (in the validation sense), `exception ledger`, `Needs Judge Attention`, `normalized failure signature`, `SHA-256`, `frozen command`, `command-set freeze`, `Unified Validation Contract`, `precedence` (in the command-selection sense).
- [ ] Where any role doc references the contract concept, it points at `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check` rather than duplicating the prose. No contract block appears in more than one file.

## Implementation Tasks

1. **`DEVELOPER_SUBAGENTS.md` — primary edit (contract lives here):**
   - Delete `## Unified Validation Contract (Mandatory)` and all its bullets.
   - Delete `## Step 0: Validation Baseline and Command Set` and all its subsections.
   - Insert `## Pre-Implementation: Starting-State Check` between existing Step 2 and Step 3. Content outline:
     - Precondition: working tree must be clean (`git status --porcelain` empty). If not, stop and emit the existing Blocked Report with type "abnormal starting state"; do not clean up, do not work through it.
     - Record starting commit hash via `git rev-parse HEAD`. This is quoted verbatim in the completion/revision report.
     - Locate the plan's `## Validation Commands` section. If absent or empty, stop and emit Blocked Report with type "planning gap."
     - Run each command. Capture exit status + tool-emitted failing identifiers (test names / lint rule IDs / compiler error codes) where available. This is the "pre-existing failures list."
     - These steps apply identically on iteration 1 and every revision iteration.
   - Add `## Completion: Rerun Validation` at the end of Step 3 (before "Step 4: Verify Acceptance Criteria"). Content outline:
     - Rerun the exact same commands from the starting-state check.
     - For each command, compute one of: `pass→pass`, `fail→pass`, `pass→fail`, `fail→fail (same identifier)`, `fail→fail (new identifier)`.
     - "Same identifier" definition: exact string match on tool-emitted identifier. If a tool does not emit a stable identifier, any fail→fail row must be classified as `fail→fail (new identifier)`.
     - `pass→fail` and `fail→fail (new identifier)` are regressions; the developer should attempt to fix them before completion. If unfixable, include them in the report and expect judge escalation.
   - Simplify the "Acceptance Criteria Verification" section: remove the mirror evidence table; add a one-line reference to `## Completion: Rerun Validation`.
   - Rewrite the Completion Report template's validation section. Replace the `### Validation Evidence Record (Mirror)` table and the `### Baseline / Post-Change / Delta Notes` block with:
     ```markdown
     ### Starting-State and Validation Results
     - **Starting commit:** `<git rev-parse HEAD from Pre-Implementation check>`
     - **Pre-existing failures:** <standard format — one row per failing command, `<command>: <id1>, <id2>, ...`; omit commands with no failures; write `none` if nothing failed>
     - **Post-change results:**

     | Command | Classification | Failing identifiers (if applicable) |
     |---------|----------------|--------------------------------------|
     | `...` | pass→pass / fail→pass / pass→fail / fail→fail (same identifier) / fail→fail (new identifier) | `<id1>, <id2>, ...` |
     - **Regressions to escalate:** <list of pass→fail or fail→fail (new identifier) rows in the same `<command>: <id1>, ...` format, or `none`>

     This block is the authoritative handoff artifact. The orchestrator passes the whole report verbatim into the reviewer and judge prompts; no file in the repo is mutated to carry evidence between roles.
     ```
   - Apply the same replacement inside the Revision Report template.

2. **`REVIEWER_SUBAGENTS.md`:**
   - Delete `## Unified Validation Contract (Mandatory)` and its bullets.
   - Replace `### A0. Validation Evidence Verification (Run Before AC Review)` with `### A0. Verify Starting-State Claims`. Content outline:
     - Always rerun the plan's validation commands at HEAD. Record per-command pass/fail and failing identifiers.
     - If every HEAD command passes and the developer's report claims no pre-existing failures, starting-state verification is complete — skip reproduction.
     - If any HEAD command fails: check out the developer's reported starting commit (`git checkout <hash>`), rerun all validation commands there, and record the reproduced pre-existing failures list. Return to the working branch afterward.
     - Classify each HEAD failure: "pre-existing" (same identifier present at starting commit per reviewer's reproduction) or "new" (not present at starting commit). "Same identifier" definition: see `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check`.
     - Severity rules:
       - Any "new" HEAD failure = CRITICAL regression finding.
       - Developer-reported pre-existing list **larger** than reviewer's reproduced list = CRITICAL (suggests padding the baseline to hide regressions).
       - Developer-reported pre-existing list **smaller** than reviewer's reproduced list = HIGH (incomplete baseline; not dangerous but indicates sloppy reporting).
       - Exact match between developer-reported and reviewer-reproduced pre-existing lists = clean.
     - A one-line cross-reference: "See `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check` for the full contract definition."
   - Replace the review-report template's `### Validation Evidence Status` block with:
     ```markdown
     ### Starting-State Verification
     - **Starting commit verified:** yes / no (reviewer's reproduction matches developer's hash)
     - **Pre-existing failures match:** exact / developer-overclaimed / developer-underclaimed
     - **Pre-existing failures (reviewer-reproduced):** <list in the standard format; see `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check` — one row per failing command, `<command>: <id1>, <id2>, ...`, or `none`>
     - **HEAD results:** pass count / fail count
     - **Regression findings:** count (detailed in Findings section)
     ```

3. **`REVIEW_JUDGE_SUBAGENTS.md`:**
   - Delete `## Unified Validation Contract (Mandatory)` and its bullets.
   - Delete the "Before evaluating reviewer findings..." pre-AC audit block inside Step 2.
   - Add to the Decision Framework section (as a new bullet under "Reject the Fix If" or a new top-level category "Regression Gate"):
     ```markdown
     ### Regression Gate

     - Regressions (`pass→fail` or `fail→fail (new identifier)`) reported by the reviewer are **not approvable** without explicit user exception.
     - If a regression exists and the developer has not fixed it, return **NEEDS_DISCUSSION**. The orchestrator handles escalation to the requesting user via its existing Escalation Log mechanism.
     - Rely on the reviewer's reproduced pre/post evidence. Do not rerun commands yourself unless the reviewer's evidence is internally inconsistent.
     ```
   - Delete `### Validation Evidence Judgment` table inside the judgment-report template.
   - Delete "Regression gate decision:" bullets inside the Overall Verdict section.
   - Insert a new subsection in the judgment-report template immediately after the `### Summary` table. This is the **sole** location for the judge's validation verdict — no other regression-gate verdict block appears elsewhere in the report.
     ```markdown
     ### Verified Validation Results

     - **Starting commit:** `<hash>` (reviewer-verified)
     - **Pre-existing failures (reviewer-reproduced):** <list in the standard format; one row per failing command, `<command>: <id1>, <id2>, ...`, or `none`>
     - **HEAD results:** pass count / fail count
     - **Regressions:** <list of new failures in the same format, or `none`>
     - **Regression gate:** clear / blocked (reason) / escalated (NEEDS_DISCUSSION)
     ```

4. **`ORCHESTRATOR_AGENT.md`:**
   - Delete `## Unified Validation Contract (Mandatory)` and its bullets.
   - Delete `### Validation Epoch Status` tracker table and its header row examples.
   - Delete `### Phase 0: Baseline and Command-Set Lock (Iteration 1 Only)` in full.
   - Inside Phase 1: remove steps that say "Verify developer report includes mirrored evidence table..." and "Persist the latest developer evidence table into story context...". Restore Phase 1 to the pre-commit three-step list (select story, launch developer, collect report).
   - Inside Phase 4 Decision: revert the APPROVED-AS-IS expanded block to its pre-commit form — the two-line "Mark story complete / Proceed to next story" (no evidence verification, no exception-ledger check).
   - Inside the four subagent-prompt templates (Developer Initial, Developer Revision, Reviewer, Judge): remove each "Validation requirements for this iteration:" block. No replacement — each subagent reads its own role doc.

5. **`planning_guidance.md`:**
   - Delete `## Unified Validation Contract (Mandatory)` section and its bullets.
   - Inside the epic-story template (`## Template: Story (Epic Story File)`): delete the `## Validation Evidence Record` table block and the `## Validation Exception Ledger` table block.
   - Inside the single-story template (`## Template: Single-Story Plan`): delete the `## Validation Evidence Record` table block and the `## Validation Exception Ledger` table block.
   - Inside both templates' existing `## Validation Commands` section, append one sentence: "Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted."

6. **Cross-reference and terminology pass:**
   - Run `rg -n "Unified Validation Contract|command[- ]set|baseline epoch|exception ledger|Needs Judge Attention|normalized failure signature|SHA-256|frozen command" ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md planning_guidance.md`. Output must be empty.
   - Confirm every role doc's contract reference points at `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check` (or the full heading phrase) rather than duplicating content.
   - Spot-check that the phrase "validation commands" appears in lower case when referring to the concept, and in `## Validation Commands` (title case) only when referring to the plan section heading.

## Testing Strategy

Docs-only change; no automated test suite. Verification:

- Grep-based absence checks for the removed terminology (see Validation Commands).
- Grep-based presence checks for the new section headings and key phrases.
- Manual isolation check: open each of the five docs and read it end-to-end. Confirm it is self-contained (does not depend on concepts defined only in another doc) except where it explicitly cross-references `DEVELOPER_SUBAGENTS.md § Pre-Implementation: Starting-State Check`.
- Dry-run walkthrough of one hypothetical iteration: the developer doc produces a completion report whose shape the reviewer doc and judge doc explicitly consume. Confirm no field is named inconsistently across docs.

## Validation Commands

Canonical command set for this story's Pre-Implementation Starting-State Check and Completion Rerun:

- `rg -n "Unified Validation Contract" ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md planning_guidance.md` — after: must return zero matches.
- `rg -n "command[- ]set|baseline epoch|exception ledger|Needs Judge Attention|normalized failure signature|SHA-256|frozen command|command-set freeze" ORCHESTRATOR_AGENT.md DEVELOPER_SUBAGENTS.md REVIEWER_SUBAGENTS.md REVIEW_JUDGE_SUBAGENTS.md planning_guidance.md` — after: must return zero matches.
- `rg -n "NEVER IMPLEMENT DIRECTLY" ORCHESTRATOR_AGENT.md` — after: must still match.
- `rg -cn "## Validation Commands" planning_guidance.md` — after: must be ≥ 2 (epic-story and single-story templates).
- `rg -n "Pre-Implementation: Starting-State Check" DEVELOPER_SUBAGENTS.md` — after: must match exactly once (the section heading).
- `rg -n "Completion: Rerun Validation" DEVELOPER_SUBAGENTS.md` — after: must match exactly once.
- `rg -n "Verify Starting-State Claims" REVIEWER_SUBAGENTS.md` — after: must match.
- `rg -n "git rev-parse HEAD" DEVELOPER_SUBAGENTS.md` — after: must match.
- `rg -n "Verified Validation Results" REVIEW_JUDGE_SUBAGENTS.md` — after: must match.
- `rg -n "Regression Gate" REVIEW_JUDGE_SUBAGENTS.md` — after: must match.
- `rg -n "Phase 0|Validation Epoch Status" ORCHESTRATOR_AGENT.md` — after: must return zero matches.

## Validation Loop Results

- **Iteration 1:** Initial draft. Launched parallel missing-details and ambiguity sub-agents.
- **Missing-details feedback (iteration 1):**
  - Line numbers in Context References were drifted (~25 lines) from current file state.
  - Step 0 deletion + new section insertion ordering was ambiguous.
  - Reviewer subsection prose was under-specified.
  - Judge verdict placement within `.judgement.N.md` was not specified.
- **Ambiguity feedback (iteration 1):**
  - "Same identifier" operational definition missing.
  - Missing `Validation Commands` handling at revision time unclear.
  - Reviewer severity direction for mismatches under-specified (sub-agent's own direction was flipped; corrected in iteration 2).
  - Clean-tree meaning on revision iterations not clarified.
  - Path for obtaining user exception on a regression unclear (sub-agent proposed reintroducing exception ledger; rejected — use existing NEEDS_DISCUSSION escalation).
- **Iteration 2:** Plan rewritten to use landmark-string references instead of line numbers, with all valid gaps and ambiguities addressed inline. Sub-agent A5's proposal to reintroduce an exception ledger was rejected (conflicts with the story's core goal).
- **Iteration 2 re-validation (parallel sub-agents against the rewritten plan):**
  - Previous-pass items confirmed fixed.
  - New blocker surfaced: Blocked Report Template's Type enum lacks entries for the two new blocked-report types ("Abnormal Starting State," "Planning Gap") emitted by the Pre-Implementation Starting-State Check.
  - New ambiguities surfaced: (1) judge verdict section needs explicit "sole location" language; (2) pre-existing failures list lacks a consistent format across roles; (3) orchestrator-persistence contract needs explicit handoff-artifact clarification (sub-agent proposed reintroducing story-context persistence — rejected; instead, made the developer's report explicitly the handoff); (4) reviewer template missing explicit "pre-existing failures (reviewer-reproduced)" field.
- **Iteration 3:** All four iteration-2 items resolved inline. Blocked Report Type enum extension added to Task 1. Standard format for pre-existing failures lists defined in User Model and echoed in developer completion/revision report templates, reviewer template, and judge template. Handoff artifact clarified in AC. Judge verdict section marked as sole validation verdict in AC and Task 3.
- **Iteration 3 re-validation:**
  - Missing-details sub-agent: no blockers; plan ready for implementation.
  - Ambiguity sub-agent: all four prior ambiguities confirmed resolved. One new "ambiguity" raised about the plan document itself referencing the blocks it targets for deletion — this is a misreading of plan semantics (a plan is a prescription for a target state, not a description of current state); no real contradiction. Sub-agent's own conclusion: "no unresolved high-impact ambiguity remains."
- **Iterations run:** 3 of 3 allowed. Validation loop closed cleanly. Plan ready for implementation.
