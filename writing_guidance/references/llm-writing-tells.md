# LLM Writing Tells

A catalog of patterns that mark LLM-produced prose. It is a shared reference, not a
reviewer — the Reader-State and LLM-Residue reviewers cite it while doing their own
jobs. Nothing here is a reviewer role, an output format, or a process to run.

The underlying failure is almost always the same: **the writer did not model the
reader's mental state.** The writer treats their own working vocabulary, recent
context, and project knowledge as shared ground. The reader, walking in cold, gets text
that only makes sense to someone standing in the same spot. Most patterns below are
surface symptoms of that. Diagnose the reader failure first, then name the symptom.

Severity comes from **reader harm, not from category**. A single embedded correction in
a one-page README aimed at non-developers does more damage than a dozen instances of
"delve" in an internal engineering memo. Every finding should tie back to a specific
reader and a specific need that reader has. A pattern listed here that costs the reader
nothing in context is not a finding — do not report it to fill a quota.

## The Tells

### A. Reader-state failures (highest priority)

These directly violate the audience-first principle.

- **Embedded corrections.** Text shaped like "X is true. Not Y." encodes the prior dialogue, not the fact. A cold reader sees a sentence that only makes sense if they had the wrong belief first.
- **Self-coined or project-internal nicknames used as proper nouns.** Terms the writer uses fluently with no definition. Flag any noun phrase a reader from the gamut would not already know.
- **Definite article for unintroduced entities.** "the session JSONL," "the resolver," "the harness" — *which* one? Definite articles imply prior introduction.
- **Scar-tissue rules without the scar.** Constraints stated without the failure they came from ("UUID selectors are rejected"). The reader cannot tell whether the rule is fundamental, optional, or working around a specific bug.
- **Local project vocabulary treated as ambient.** Project names, tool names, file conventions, internal protocols used before being introduced. Flag every such term and check whether it is glossed on first use.
- **Silent meaning shifts.** A word that holds one meaning across the document except in a single section or sentence where it means something else. The author tracks the distinction effortlessly; the reader hits a wall.
- **Handoff briefs that reference shared history that does not exist.** A subagent prompt, a doc, or a section that says "continue with the refactor we discussed" assumes context the reader does not have.
- **Linking out for the broad concept while assuming the local terms.** A document that points to an upstream README for "what is this project" while assuming "what is this internal tool" is obvious.
- **File formats and conventions cited as if known.** Format names (JSONL, NDJSON, protobuf) used without indicating what the file looks like, where it lives, or why it matters.

### B. Sycophancy and meta-chatter

- "Great question!" / "Excellent point!" / "You're absolutely right."
- Restating the user's question before answering.
- Reflexive "Certainly!" / "Of course!" / "I'd be happy to..."
- Apologizing for things that do not need apology.
- "Let me know if this helps!" / "Happy to clarify!" closers.

### C. Hedge-and-balance reflexes

- Reflexive "however" or "on the other hand" when one side is clearly right.
- "Both approaches have merit" used to avoid taking a position.
- "It depends" without saying on what.
- Imaginary or trivially asymmetric tradeoffs.
- Stacked modals: "could potentially possibly."
- "Nuanced" used as cover for not committing.

### D. Inflated diction and stock vocabulary

- Verbs: delve, leverage, utilize, facilitate, empower, foster, navigate, unlock, harness, streamline, weave.
- Adjectives: robust, comprehensive, seamless, holistic, cutting-edge, vibrant, rich, game-changing.
- Nouns: tapestry, journey, ecosystem, landscape, realm, plethora, myriad, testament, synergy.
- Filler connectives: "Moreover," "Furthermore," "Indeed," "It's worth noting that," "It's important to note that."
- Closer reflexes: "In conclusion," "In summary," "Ultimately," "At the end of the day."
- Universalizing dodges: "In today's fast-paced world," "As technology evolves."

### E. Structural padding

- Topic sentences that announce the paragraph's topic ("In this section, we'll discuss X").
- Conclusions that restate the introduction.
- "Let me break this down" with no breakdown.
- "There are several factors to consider:" preambles before content that did not need them.
- Numbered steps for non-sequential content.
- Three-item lists obviously padded from two.
- Announcing what will be done instead of doing it.

### F. Formatting tics

- Headers for every short section regardless of length.
- Bullet lists for prose-shaped content.
- Bold on every second phrase.
- Tables for non-tabular data.
- Code blocks for non-code content.
- Reflexive emoji as bullet decorations or section markers.
- Boilerplate README scaffolding (`## Features`, `## Getting Started`, `## Contributing`) used regardless of fit.

### G. Rhetorical-pivot tics

- "Not X — Y" reversals used many times per document.
- Em-dash overuse as a substitute for varied syntax.
- "But here's the thing:" / "Here's the catch:" / "The kicker?"
- Forced three-part climaxes: "not only X, but also Y, and ultimately Z."
- Rule of three forced where two examples would do.

### H. Scope creep and over-completion

- Answering questions the document was not asked.
- Adding a "Best practices" section to a focused doc.
- Volunteering disclaimers and caveats unprompted.
- Expanding scope when narrow was requested.
- Closing with optional next steps that were not asked for.

### I. Hallucinated specifics

- Confidently precise numbers with no source ("a 47% improvement").
- "According to a 2023 study..." with no citation.
- "Industry standard is..." / "Best practices suggest..." as authority laundering.
- Plausible-sounding API names, file paths, or function signatures that do not appear in the codebase.
- Fabricated section, line, or document references.

### J. Genre and voice misfit

- Marketing tone in internal/technical docs.
- Tutorial framing for reference material.
- Pep-talk closers ("You've got this!").
- Reflexive "we" when the writer is not a team.
- Customer-support voice in a spec.
- Essay structure for a short reference entry.

### K. Code and doc-specific tells

- Comments that restate the line above.
- Multi-paragraph docstrings on trivial functions.
- Variable names like `data`, `result`, `helper`, `myVariable`.
- TODO/FIXME comments fabricated as filler.
- Defensive error handling for code that cannot fail.
- READMEs that are 80% identical to boilerplate templates.
- "This is a simple..." prefacing.

### L. Time-blind and context-blind phrasing

- "Recent advances" with no date.
- "Currently" / "today" with no anchor.
- "The latest version" with no version reference.
- "As of my last update..."

### M. Dialogue-encoded prose

- Documents that record the back-and-forth instead of the result ("It was previously thought that X, but actually Y" in a greenfield doc).
- "Updated:" markers inside the prose body.
- Negative definitions where positive ones would work ("This is not a replacement for X" before establishing what it is).

## Using This Catalog

Cite the letter and name (`D. Inflated diction`) so findings are traceable. Report the
location, the reader harmed, and the smallest change that fixes it. Apply the same
standards to your own report: do not commit the tells you are flagging.
