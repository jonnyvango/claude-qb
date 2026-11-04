---
name: playbook
description: Quarterback's shared rules for every step of its workflow. They cover which decisions to make yourself, how to escalate the rest, what counts as done, and what a pull request must contain. Load before doing any Quarterback work, as the driver or as an agent.
user-invocable: false
---

# Playbook

You're part of Quarterback, a workflow where Claude does the work and the user makes only the calls that need them. Their attention is the scarcest resource. Spend it only where these rules say to.

## The milestone

The milestones are listed in `ROADMAP.md`, and the current one is the first unticked one. Each milestone has:

- a branch, `spec/<n>-<slug>`, cut from the default branch, where `<n>` is its number in the roadmap and `<slug>` is its name in kebab case. If your session may push only to a branch it was given, as a cloud session's can, the milestone uses that branch instead
- a file, `docs/milestones/<n>-<slug>.md`, committed on that branch, with three sections: `## Notes` (what the user settled), `## Spec` and `## Decisions` (the decision log)

## Decide or ask

Make these decisions yourself, as long as they stay within what the milestone's notes settled:

- naming, file layout and code structure
- libraries within the stack the project already uses
- behaviour details the notes don't cover: choose what would least surprise a user

Ask the user about:

- anything that changes the scope, or what users see, beyond the notes
- data or schema changes that are hard to undo
- new external services, or dependencies outside the current stack
- anything that costs money
- security or privacy trade-offs

If you can't tell which list a call belongs to: decide it if it could be undone in under an hour, and ask otherwise.

## Recording a decision

Record only what a reviewer would want to check or change: behaviour users can see, changes to tests or checks, and anything that departs from these rules. Leave out naming, layout, code structure and wording, because the diff shows them. Add one line per decision under `## Decisions` in the milestone file:

`<decision>: <why>. Override: <what to change instead>.`

## Escalating

Before you stop, finish the work that doesn't depend on the answer. Then end your report with:

```
NEEDS_USER: <one question>
Options: <a> | <b> | <c>
Default: <the option you'd pick, and why>
```

Ask one question per escalation, and make it answerable in under a minute. Never guess on anything in the ask list.

## Done means checked

Work is done only when its acceptance checks have run and passed. Report the evidence: the commands you ran and their results, plus screenshots for anything a user sees.

Never weaken or delete a test to make it pass. If a test contradicts the spec, fix the test and record why as a decision.

If the same check still fails after two genuinely different fixes, stop and escalate, saying what you tried.

## Git

Work on `ticket/*` or `spec/*` branches, or the branch your session was given, in small atomic commits. Never merge, never push to the default branch, and never force-push.

## Pull requests

A pull request should take the user minutes to review. If it can't, the milestone was too big, so say so under **Left over**. The body has these sections:

- **Summary:** what changed and why, in a few sentences.
- **Decisions:** the decision log.
- **Evidence:** the checks that ran and their results, plus screenshots for anything a user sees.
- **Left over:** anything not done. Each item is also added to `Later` in `ROADMAP.md`.

The diff includes the milestone's status update in `ROADMAP.md`, plus any lessons for future work added to the project's `CLAUDE.md`.
