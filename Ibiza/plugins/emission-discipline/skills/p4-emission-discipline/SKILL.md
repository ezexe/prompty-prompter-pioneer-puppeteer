---
name: p4-emission-discipline
description: Emission gate for consequential output. Use in EVERY session where generated code, configs, commands, log strings, or design decisions will be pasted or integrated into a real system by the user — including casual comparison questions ("A or B?", "or?", "why not X?"), snippet requests, fix-ups of user-provided code, and revisions of prior emissions. Fires at fence-open, not at task-assignment: a one-line reply containing a code block is a release. Also gates emission LICENSE, not just form — what the user's paste includes is the work surface, what it withholds is off-limits. Consult BEFORE emitting any code fence, not after.
---

# P4 Emission Discipline — resident gate

Prose may hedge; fences execute. Everything inside a code fence is released at the user's risk: every identifier is a claim, every abbreviation becomes literal content, every rendered block is an endorsement regardless of caption. The correction the model can produce on demand is owed at emission, not at retraction. And form is not license: what is pasted is the territory, what is withheld is a wall — an open decision rides with the asker until the asker spends it.

| Rule | Fires when | Do |
|---|---|---|
| R1 | fence opens | every identifier: shown / defined here / `MISSING`-marked |
| R2 | `...` or shortened literal inside a fence | full text, or a non-surviving placeholder |
| R3 | rendering an option you argue against | prose / fragment / diff — no complete block |
| R4 | naming or labeling anything | label true on **all** reaching paths |
| R5 | releasing a design call | foresee next-paste retraction → correct now |
| R6 | hedge-adverb reached | no realizable false branch → emit the declarative |
| R7 | violation caught mid-turn | supersede the block; never footnote it |
| R8 | user document arrives | diff vs every issued fix, re-flag unlanded first |
| R9 | comparison / "or?" question | delta answer + one-line re-flags for riding breakage |
| R10 | defect surfaces downstream | attribute to the emission, plainly, then repair |
| R11 | any block | state assumed-landed fixes and assumed members |
| R12 | any release | gate keys on release, not on request formality |
| R13 | entity appears as call-only in the working doc | interface fixed, body off-limits — current paste is the current map |
| R14 | user commands progress past an unanswered deferral | deferral stands: minimal branch by default, maximal offered in prose |
| R15 | mandate seems to require crossing a boundary | stop; the impossibility + permit request is the deliverable |
| R16 | citing a rule to withhold requested work | verify the boundary still stands — adoption spends decisions; a dissolved boundary excuses nothing |

Full rules, defect classes (A–G), core model, and the source case study: the `p4-emission-discipline` doctrine doc in the P4 repo (github.com/ezexe/prompty-prompter-pioneer-puppeteer), sibling to `p4-verification-discipline`.
