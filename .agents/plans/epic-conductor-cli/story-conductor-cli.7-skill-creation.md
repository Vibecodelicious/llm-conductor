# Story: Skill Creation

**Epic:** Conductor CLI Tool
**Size:** Medium
**Dependencies:** None. The skill works today via Claude Code's Agent tool against the existing framework docs. When Stories 5–6 land, it detects the `conductor` CLI and delegates to it automatically. (Note: the epic file currently lists Stories 5 and 6 as dependencies for Story 7; update the epic accordingly if this story is sequenced first.)

## Story Description

Make llm-conductor a native agent skill. The repo itself becomes the skill — `SKILL.md` lives at the repo root, and the existing framework docs (`planning_guidance.md`, `ORCHESTRATOR_AGENT.md`, `DEVELOPER_SUBAGENTS.md`, `REVIEWER_SUBAGENTS.md`, `REVIEW_JUDGE_SUBAGENTS.md`) stay where they are and serve as references in place. No copies, no symlinks.

The skill activates when a user asks an LLM agent to plan or orchestrate software work. Its job is to drive the pipeline end-to-end: a readiness check first, then (if appropriate) plan authoring per `planning_guidance.md` to approval+commit closure, then (if the user wants it) orchestration per `ORCHESTRATOR_AGENT.md` until stories are complete or escalated.

## User Model

### User Gamut
- Developers who want an LLM agent to plan AND build a feature/project autonomously.
- Developers who want to use llm-conductor only for disciplined planning, then implement another way.
- Developers resuming a mid-run orchestration (status, diagnosis, resume).
- LLM agents discovering the framework via skill activation — the consumer of SKILL.md.

### User-Needs Gamut
- Reliable autonomous execution from "plan and orchestrate this" through to completion, with escalation only on real blockers.
- Readiness-check rigor: the agent should refuse to plan on vague input (e.g., "we'll need a system for user preferences") and return to discovery first.
- Conformant plans without hand-holding: plans authored via the skill should pass `planning_guidance.md` validation, including the sub-agent validation loop.
- Works whether or not the `conductor` CLI is installed.

### Design Implications
- SKILL.md is instructional prose aimed at the invoking LLM, not a compliance framework or state machine.
- The skill drives the planning validation sub-agent loop — it does not merely link to `planning_guidance.md`. SKILL.md references the validation steps in `planning_guidance.md` rather than re-enumerating them.
- Planning closure (Approval Status + Plan Commit Hash) is owned by the skill, because planning may be used standalone without any downstream orchestration gate to catch it. SKILL.md references `planning_guidance.md`'s closure protocol; it does not restate Phase -1.
- CLI detection requires both `command -v conductor` to succeed AND `.conductor/config.json` to exist; on a half-match, fall back to manual Agent tool invocations. Delegation scope is the orchestration loop only (`conductor run --story X.Y`); planning is always driven manually because the CLI does not run planning.
- The existing framework docs are canonical. References in SKILL.md are paths, not content — eliminating drift by construction.

## Acceptance Criteria

- [ ] `SKILL.md` exists at the repo root with YAML frontmatter (`name`, `description`).
- [ ] `SKILL.md` is under 500 lines.
- [ ] `SKILL.md` references the existing framework docs by path; no copies, no symlinks, no duplicated prose.
- [ ] `SKILL.md` instructs the invoking LLM to perform a readiness check at planning entry (not during orchestration resume): assess whether the user's input is concrete enough to plan on; if vague (example: "we'll need a system for user preferences"), pause and ask clarifying questions before proceeding.
- [ ] `SKILL.md` instructs the LLM to run the planning process per `planning_guidance.md`, including launching sub-agents for the validation loop as enumerated there (SKILL.md references those steps, does not restate them), to reach `Approval Status: approved` + `Plan Commit Hash: <hash>` before proposing orchestration.
- [ ] `SKILL.md` supports planning-only sessions — reaching plan closure is a valid terminal state; orchestration is never forced.
- [ ] `SKILL.md` instructs the LLM to run orchestration per `ORCHESTRATOR_AGENT.md` when the user wants execution, passing the committed plan path and its commit hash so the orchestrator's Phase -1 gate can verify closure.
- [ ] `SKILL.md` detects the `conductor` CLI by requiring both `command -v conductor` to succeed AND `.conductor/config.json` to be present; when both hold, delegates `conductor run --story X.Y` for the orchestration loop only. Otherwise falls back to Agent tool invocations. Planning is never delegated to the CLI.
- [ ] `SKILL.md` routes mid-run questions (status, resume, diagnosis of a failed story) to the relevant section of the framework docs.
- [ ] `evals/evals.json` exists with a small set of should-trigger and should-not-trigger prompts covering the main intent buckets (plan-and-orchestrate, plan-only, mid-run status, negative examples like "review my PR" or "write me a script").
- [ ] Description string tuned against the eval prompts so the skill fires on framework-relevant intents and does not fire on unrelated coding or review requests.

## Context References

- `planning_guidance.md` — the planning process the skill drives end-to-end.
- `ORCHESTRATOR_AGENT.md` — the orchestration process the skill drives end-to-end.
- `DEVELOPER_SUBAGENTS.md`, `REVIEWER_SUBAGENTS.md`, `REVIEW_JUDGE_SUBAGENTS.md` — subagent contracts the orchestration process invokes; read to understand what SKILL.md needs to hand off to.
- `~/.agents/skills/skill-creator/SKILL.md` — authoring conventions for writing a SKILL.md and the description-optimization technique.

### New Files to Create
- `SKILL.md` — skill entry point at repo root.
- `evals/evals.json` — should-trigger and should-not-trigger prompts.

## Implementation Plan

### Phase 1: Draft SKILL.md

Write the skill file with four instructional sections aimed at the invoking LLM:

1. **Readiness check.** How to decide if the user's request is concrete enough to plan on. Concrete examples of vague vs. ready input. Direction: pause and ask clarifying questions when vague.
2. **Planning.** How to drive `planning_guidance.md` end-to-end, launching sub-agents for the validation loop per the steps enumerated there (SKILL.md references those steps, does not restate them). How to recognize when planning closure is reached (`Approval Status: approved` + `Plan Commit Hash: <hash>`) — the closure marker is owned here for standalone use; defer to `planning_guidance.md` for the closure protocol itself. Explicit acknowledgement that planning-only is a valid terminal state.
3. **Orchestration.** How to drive `ORCHESTRATOR_AGENT.md` end-to-end. CLI detection: both `command -v conductor` AND `.conductor/config.json` must hold; when both do, delegate the per-story loop to `conductor run --story X.Y`. Otherwise run the loop manually via Agent tool invocations. In either case, pass the committed plan path and hash into the orchestration entry so Phase -1's closure gate can verify them.
4. **Mid-run routing.** Where to send status, resume, and diagnosis questions — pointers into the framework docs.

Reference the framework docs by path. Keep the file under 500 lines.

### Phase 2: Eval prompts

Create `evals/evals.json` with a handful of should-trigger and should-not-trigger prompts covering the main intent buckets. Representative positives: "plan this feature and orchestrate it", "walk me through planning an epic for X", "story 2.3 is stuck mid-review — what do I do?". Representative negatives: "review my PR", "write me a Python script to parse JSON", "how do I center a div".

### Phase 3: Description tuning

Use the skill-creator's description optimization technique against `evals/evals.json` to iterate on the description string until trigger behavior is accurate.

## Step-by-Step Tasks

1. Draft `SKILL.md` at the repo root with frontmatter and the four sections above.
2. Write `evals/evals.json` with a handful of positive and negative prompts.
3. Iterate on the description until it triggers accurately on the eval prompts.
4. Manually test: give the skill a vague request — verify it pauses for discovery. Give it a concrete request — verify it proceeds to planning.
5. Manually test: give the skill a concrete request to plan-and-orchestrate a small story — verify it produces a committed plan and drives orchestration to completion (or a legitimate escalation).

## Testing Strategy

- Trigger accuracy: run the eval prompts, verify expected trigger/no-trigger behavior.
- Readiness check: manual vague-vs-concrete comparison.
- End-to-end: manual plan-and-orchestrate flow on a small story, verifying autonomous execution to closure.

## Validation Commands

Every story plan MUST list the validation commands explicitly. These are the source of truth for the developer's Pre-Implementation Starting-State Check and Completion Rerun; no runtime substitution is permitted.

- `test -f SKILL.md`
- `grep -qE '^name:' SKILL.md && grep -qE '^description:' SKILL.md`
- `test "$(wc -l < SKILL.md)" -lt 500`
- `test -f evals/evals.json && jq empty evals/evals.json`
- `grep -q 'planning_guidance.md' SKILL.md && grep -q 'ORCHESTRATOR_AGENT.md' SKILL.md`

## Worktree Artifact Check

- Checked At: `2026-04-21`
- Planned Target Files: `SKILL.md`, `evals/evals.json`
- Overlaps Found (path + class): `none`
- Escalation Status: `none`
- Decision Citation: `none`

## Plan Approval and Commit Status

- Approval Status: `approved`
- Approval Citation: User message 2026-05-20 — "Approved. Proceed" (following pass verdicts from both missing-details and ambiguity validation sub-agents on iteration 2)
- Plan Commit Hash: `b6080b8`
- Ready-for-Orchestration: `yes`

## Completion Checklist

- [ ] All acceptance criteria met
- [ ] SKILL.md under 500 lines
- [ ] Description triggers accurately on eval prompts
- [ ] Readiness-check behavior verified manually
- [ ] End-to-end plan-and-orchestrate flow verified manually
- [ ] Plan approved and committed before orchestration begins
- [ ] Worktree artifact overlaps resolved (approved direction or explicit deferral)
