---
name: writing-guidance
description: Write and revise documentation through a delegated review loop — README, DEVELOPMENT.md, tutorials, API and CLI reference, runbooks, architecture notes, migration guides, release notes, and customer guides. The agent drafts, then launches fresh reviewer subagents that hunt for reader failure, then revises against their findings. Use this whenever the user asks to write, draft, rewrite, revise, tighten, review, or de-slop a document, or mentions writing guidance, documentation review, adversarial doc review, LLM writing tells, or making a doc readable by someone without the project context. Use it for edits to existing docs too, not just new ones.
---

# Writing Guidance

Documentation that real readers can use without shared chat history, hidden project
context, or LLM filler.

The mechanism is context isolation. You wrote the draft, so you cannot see what it
assumes — every term you defined in your own head reads as obvious to you. Reviewers
run as fresh subagents that have never seen your reasoning, only the document and its
sources. What they cannot follow, the reader cannot follow.

This is documentation work, not implementation planning. Do not import gates from
project planning workflows unless the user asks for a plan document.

## Roles

**You are the writer.** You gather sources, model the reader, draft, and revise. You
own every edit to the target document.

**Reviewers are subagents.** They read, they report, they never edit. Each one gets a
narrow job and its own instruction file. A reviewer that helped write the document is
worthless, so reviewers are always fresh sessions — never reuse a reviewer session
across iterations, and never let a reviewer see your working notes beyond the review
packet.

## Core Principles

### Reader success

The document should help its reader do or understand the intended thing. Model the
reader internally; do not put that model in the document. Project documentation speaks
directly to the task. It does not announce its audience with an `Audience`,
`User Model`, or `User Gamut` section unless the genre calls for one — a book preface,
a formal training course, an explicitly segmented product page.

### Use source context before asking

Do not make the user act as document strategist. Inspect available source material and
make well-supported editorial decisions before asking anything.

Look first for existing plans, requirements, and roadmap notes; documentation near the
target; and the code, command output, configuration, examples, API definitions,
schemas, and tests the document describes. The target path, filename, and document type
are themselves evidence.

Use plan user models as source context for the *product's* users. Then infer the reader
of *this* document from its genre and location. A `DEVELOPMENT.md` reader is a
contributor building software for the users described in the product plan; it is not
the product end user.

Ask the user only for what source material cannot supply: private product positioning,
unpublished customer commitments, release timing, legal or security policy, intended
distribution channel.

### Source truth

Do not invent commands, APIs, paths, options, versions, numbers, behavior, performance
claims, product promises, or support policy. When source truth is unavailable, write
around the gap honestly or ask for the missing source. Plausible specifics are the
worst possible filler — they survive review by looking right.

### Target document, private working notes

Reader models, source inventories, and review findings stay in your working notes. The
final document should read like intentional documentation, not like a transcript of how
it was produced.

## The Writing Loop

Setup runs once. The iteration body repeats up to 3 times.

```
SETUP (once)
  Step 1  Scope        -> target path, document type, acceptance criteria
  Step 2  Sources      -> read enough to write accurately
  Step 3  Reader model -> private; never pasted into the document
  Step 4  Draft        -> first full version of the target document
  Step 5  Select       -> choose the reviewer set (see Reviewer Selection)
  iteration := 1
  review_set := selected reviewers

ITERATION BODY
  Step 6  Review       -> launch every reviewer in review_set as fresh
                          parallel subagents with the review packet
  Step 7  Triage       -> for each finding: accept, or decline with a reason
                          if nothing accepted            -> exit CLEAN
                          if blocked on missing source   -> exit BLOCKED
  Step 8  Revise       -> apply the accepted findings to the document
  Step 9  Narrow       -> review_set := reviewers whose finding areas the
                          revision materially changed
                          if review_set is empty         -> exit NARROWED
  Step 10 Cap          -> if iteration = 3                -> exit CAPPED
                          iteration := iteration + 1
                          go to Step 6

CLOSURE
  Report per Closure Report
```

### Setup

**Step 1 — Scope.** Identify the target document path and document type. Note any
acceptance criteria or scope constraints the user gave. If the intended deliverable
itself is unclear, ask now; this is the one question worth blocking on.

**Step 2 — Sources.** Read enough to write accurately: nearby or related docs for
voice, structure, and terminology; plans or requirements for product user context; the
code, schemas, commands, tests, or examples that keep you from inventing specifics.
Record which files you used — they go in the review packet, not necessarily in the
document.

**Step 3 — Reader model.** Build this privately. Deliberately spread it wider than
"someone like me": who reads this, what they are trying to accomplish, what they know
before opening it, what terms and setup steps and verification they need, and how the
product's user model shapes the decisions this reader has to make. A model that
collapses to one reader type will produce a document that serves one reader type.

**Step 4 — Draft.** Write for the inferred reader and genre. Introduce project-local
terms before relying on them. Give concrete steps where the reader must act, with
expected results or verification where useful. Prefer accurate, direct language over
persuasion. Match the document type. Stay in scope.

**Step 5 — Select reviewers.** See Reviewer Selection below.

### Iteration body

**Step 6 — Review.** Launch every reviewer in `review_set` as a fresh subagent, in
parallel, using the launch prompt below. Reviewers do not talk to each other and do not
edit the document.

**Step 7 — Triage.** For each finding, decide: accept, or decline with a reason.
Accept what harms reader success, factual accuracy, or genre fit. Decline subjective
preference and tells that do not hurt the reader — a flagged word that is correct in
context stays. When two reviewers conflict, choose what serves the real reader and
source truth. Record declines; they go in the closure report. Then check the CLEAN and
BLOCKED exits.

**Step 8 — Revise.** Apply the accepted findings. This runs on every iteration
including the last, so findings raised at the cap still get fixed.

**Step 9 — Narrow.** The next `review_set` is only the reviewers whose finding areas
the revision materially changed. If the revision was broad, that is the full selected
set. Do not rerun reviewers over untouched areas to burn through the iteration cap.
Check the NARROWED exit.

**Step 10 — Cap.** If this was iteration 3, exit CAPPED. Otherwise increment and return
to Step 6.

### Exit conditions

Four ways out. Each is checked at the step named above.

**CLEAN** (Step 7). You accepted no findings from the current `review_set`. The
document is done. Exiting here on iteration 1 is a success; treat it as one rather than
looking for something to change.

**BLOCKED** (Step 7). A Source-Truth finding needs source material you cannot obtain.
Stop and ask the user for it. Do not guess past it and do not spend the remaining
iterations writing around it.

**NARROWED** (Step 9). The revision touched no area any reviewer covers, so there is
nothing left to re-review. The document is done.

**CAPPED** (Step 10). Iteration 3 revised and stopped. Its revisions were never
re-reviewed, and declined findings are still declined. Neither gets dropped silently —
the closure report lists both as open, so the user decides whether to keep going.

### Reviewer launch prompt

Give every reviewer the same packet. Fill the bracketed values:

```
You are a documentation reviewer. Read [SKILL_DIR]/references/<reviewer>.md
for your instructions and follow them exactly.

SESSION REQUIREMENT: You are a fresh session. You did not write this document.
Do not resume or assume any prior review context.

REVIEW PACKET
- Original user request: <verbatim request>
- Acceptance criteria and scope constraints: <or "none given">
- Target document: <path>
- Target document contents: <full current text>
- Writer completion report: <the report below, or "none">
- Source paths used by the writer: <list>
- Known source gaps: <list, or "none">
- Iteration: <N of 3>
- Changes since last review: <or "first review">

Report findings in the output format your instruction file specifies.
Do not edit the document. Do not invent findings to fill a quota.
```

Replace `[SKILL_DIR]` with this skill's directory. If your harness cannot launch
subagents, run each reviewer as a separate clean-context pass — read only the packet
and the reviewer's instruction file, and produce the report before reading anything
else. A reviewer pass that inherits your drafting context is not a review.

## Reviewers

| Reviewer | Instruction file | Job |
|---|---|---|
| Reader-State | `references/reader-state-reviewer.md` | Can a cold reader follow this without hidden context? |
| Task-Success | `references/task-success-reviewer.md` | Can the reader complete the workflow or grasp the concept? |
| Source-Truth | `references/source-truth-reviewer.md` | Does every claim check out against source? |
| Genre-and-Voice | `references/genre-voice-reviewer.md` | Does this fit its genre and distribution? |
| LLM-Residue | `references/llm-residue-reviewer.md` | Are there writing tells and dialogue-encoded prose? |

`references/llm-writing-tells.md` is the shared catalog of LLM writing tells, cited by
the Reader-State and LLM-Residue reviewers. It is a reference, not a reviewer — do not
launch it as one.

### Reviewer selection

Use the smallest set that covers the document's risk. Not every document needs every
reviewer.

| Document | Reviewers |
|---|---|
| New top-level README, `DEVELOPMENT.md`, customer guide, tutorial, migration guide, troubleshooting guide | All five |
| API, CLI, config, schema, or command reference | Source-Truth, Task-Success, Reader-State, Genre-and-Voice. Add LLM-Residue if the draft is long or prose-heavy |
| Architecture note, design explanation, maintainer guide | Reader-State, Source-Truth, Task-Success, Genre-and-Voice. Add LLM-Residue if the prose is essay-like |
| Release note, changelog entry | Source-Truth, Genre-and-Voice. Add Reader-State if it introduces new terms or migration action |
| Small edit to an existing doc | Only the reviewers tied to the changed risk area |

If the document type is unclear, infer it from path, title, and the reader task. Do not
ask the user to pick reviewers unless the deliverable itself is unclear.

## Writer Completion Report

This goes in the review packet and to the user. It is not part of the target document
unless the user asked for it.

```markdown
## Document Writing Report

**Document**: `path/to/document.md`
**Document type**: README / tutorial / reference / DEVELOPMENT / API docs / release notes / other
**Status**: draft / reviewed / ready to publish

### Source Material Used
- `path` - why it mattered

### Private Reader Model Summary
- Document reader: <brief internal summary>
- Reader task: <what the reader needs to do or understand>
- Product-user context used: <plan/user-model source, or none>

### Remaining Source Gaps
- <none, or specific missing source truth>
```

## Closure Report

Report this when the loop ends:

- Document path.
- Source files used.
- How the loop ended: CLEAN / BLOCKED / NARROWED / CAPPED.
- Iterations run, and which reviewers ran in each.
- Material changes made after review.
- Findings declined, with the reason.
- Open findings, if the loop ended CAPPED: the unreviewed final revision and any
  still-declined findings.
- Source gaps that remain.

## What Not To Do

- Do not add audience-model sections to target docs by default.
- Do not ask broad discovery questions before inspecting source material.
- Do not present a menu of stylistic options unless the user asked for one.
- Do not fabricate examples, command output, paths, APIs, or support claims.
- Do not keep chat-history phrasing such as "as discussed" or "updated based on feedback."
- Do not expand a focused document into a general best-practices guide.
- Do not let a reviewer edit the document, and do not review your own draft in the
  context that produced it.
