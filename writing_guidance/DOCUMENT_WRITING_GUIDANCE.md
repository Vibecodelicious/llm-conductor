# Document Writing Guidance

## Purpose

Create customer-facing and developer-facing documentation that real readers can use without shared chat history, hidden project context, or LLM-style filler.

This guidance is for documentation work, not implementation planning. Do not import gates from project planning workflows unless the user explicitly asks for a plan document.

## Core Principle: Reader Success

The target document should help its reader do or understand the intended thing. The writer and reviewers should model the reader internally, but the document should not usually include an `Audience`, `User Model`, `User Gamut`, or similar meta section.

Project documentation normally speaks directly to the task. It does not announce its audience unless the genre calls for that, such as a book preface, formal training course, or explicitly segmented product page.

## Core Principle: Use Source Context Before Asking

Do not make the user act as document strategist. Before asking questions, inspect available source material and make well-supported editorial decisions.

Look first for:
- Existing plans, requirements, roadmap notes, and user-model material.
- Existing documentation near the target document.
- Code, command output, configuration, examples, API definitions, schemas, tests, and product behavior relevant to the document.
- The target path, filename, and document type.

Use existing plan user models as source context for the product's users and goals. Then separately infer the reader of the specific document from its genre and location. For example, a `DEVELOPMENT.md` reader is usually a contributor or maintainer building software for the users described by the product plan; it is not usually the product end user.

Ask the user only when the document requires information that is not available from source material, such as private product positioning, unpublished customer commitments, release timing, legal/security policy, or the intended distribution channel.

## Core Principle: Source Truth

Documentation must be grounded in source material. Do not invent commands, APIs, paths, options, versions, numbers, behavior, performance claims, product promises, or support policy.

When source truth is unavailable, write around the gap honestly or ask for the missing source. Do not fill the gap with plausible specifics.

## Core Principle: Target Document, Private Working Notes

The writer may use private notes for reader modeling, source inventory, and review findings. Keep those notes out of the target document unless they are part of the requested deliverable.

The final document should read like intentional documentation, not like a transcript of how the document was produced.

## Document Writing Loop

Repeat the loop up to 3 iterations. Stop earlier when focused reviewers find no reader-harming issues that require revision.

### Phase 1: Source Gathering

Read enough source material to write accurately.

Required activities:
- Identify the target document path and document type.
- Inspect nearby or related docs for voice, structure, and terminology.
- Inspect relevant plans or requirements for product user context.
- Inspect code, schemas, commands, tests, or examples needed to avoid invented specifics.
- Record source files used in the writer's completion report, not necessarily in the target document.

### Phase 2: Private Reader Modeling

Build a private model of:
- Who will read this document.
- What they are trying to accomplish.
- What they likely know before opening it.
- What terms, setup steps, examples, and verification they need.
- How the product's user model affects the choices developers or maintainers must make.

Do not paste this model into the document by default.

### Phase 3: Drafting

Write the document for the inferred reader and genre.

Good documentation should:
- Introduce project-local terms before relying on them.
- Give concrete steps when the reader needs to act.
- Include expected results or verification where useful.
- Prefer accurate, direct language over persuasion or filler.
- Match the document type: tutorial, reference, concept, README, runbook, API docs, release notes, or development guide.
- Stay within the requested scope.

### Phase 4: Focused Review

Run focused reviewers with separate instruction documents. Each reviewer should have a narrow job and should report evidence-backed findings, not rewrite the document. Focused review is adversarial in the sense that reviewers actively look for reader failure; it is not a quota for criticism.

Give each reviewer this review packet:
- Original user request and any acceptance criteria or scope constraints.
- Target document path and contents.
- Writer completion report, if one exists.
- Source paths or source excerpts used by the writer.
- Known source gaps, if any.

Default reviewers:
- Reader-State Reviewer (`writing_guidance/DOCUMENT_READER_STATE_REVIEWER.md`): checks whether cold readers can follow the document without hidden context.
- Task-Success Reviewer (`writing_guidance/DOCUMENT_TASK_SUCCESS_REVIEWER.md`): checks whether readers can complete the workflow or understand the concept.
- Source-Truth Reviewer (`writing_guidance/DOCUMENT_SOURCE_TRUTH_REVIEWER.md`): checks claims against source material.
- Genre-and-Voice Reviewer (`writing_guidance/DOCUMENT_GENRE_VOICE_REVIEWER.md`): checks whether the document fits its intended genre and distribution.
- LLM-Residue Reviewer (`writing_guidance/DOCUMENT_LLM_RESIDUE_REVIEWER.md`): checks for LLM writing tells and dialogue-encoded prose.

Not every document needs every reviewer. Use the smallest reviewer set that covers the document's risk.

Reviewer selection defaults:
- New top-level README, `DEVELOPMENT.md`, customer guide, tutorial, migration guide, or troubleshooting guide: run all default reviewers.
- API reference, CLI reference, config reference, schema docs, or command docs: run Source-Truth, Task-Success, Reader-State, and Genre-and-Voice. Add LLM-Residue if the draft is long or prose-heavy.
- Architecture note, design explanation, or maintainer guide: run Reader-State, Source-Truth, Task-Success, and Genre-and-Voice. Add LLM-Residue if the draft uses essay-like prose.
- Release note or changelog entry: run Source-Truth and Genre-and-Voice. Add Reader-State if the entry introduces new terms or migration action.
- Small edits to an existing doc: run the reviewers tied to the changed risk area.

If the document type is unclear, infer from path, title, and requested reader task. Do not ask the user to choose reviewers unless the intended deliverable itself is unclear.

### Phase 5: Revision

Revise concrete findings that harm reader success, factual accuracy, or genre fit.

Do not churn on subjective preferences. If reviewer feedback conflicts, choose the change that best serves the document's real reader and source truth. If a reviewer flags a tell that does not harm the reader, leave it alone.

After revision, rerun reviewers whose finding areas were materially changed. If revisions are broad, rerun the selected reviewer set. Do not rerun reviewers for untouched areas just to exhaust the iteration limit.

### Phase 6: Closure

When the loop ends, report:
- Document path.
- Source files used.
- Reviewers run and iteration count.
- Material changes made after review.
- Any source gaps that remain.

## Writer Completion Report

Use this report for handoff to reviewers and the user. It is not part of the target document unless requested.

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
- Product-user context used: <plan/user-model source or none>

### Review Loop
- Iterations run: <1-3>
- Reviewers run: <list>
- Findings addressed: <summary>
- Findings intentionally not addressed: <summary and rationale>

### Remaining Source Gaps
- <none, or specific missing source truth>
```

## What Not To Do

- Do not add audience-model sections to target docs by default.
- Do not ask the user broad discovery questions before inspecting source material.
- Do not present a menu of stylistic options unless the user requested one.
- Do not fabricate examples, command output, paths, APIs, or support claims.
- Do not preserve chat-history phrasing such as "as discussed" or "updated based on feedback."
- Do not expand a focused document into a general best-practices guide.
