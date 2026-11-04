---
name: drive
description: Take the project's current milestone to an open pull request, stopping only when the user is needed. Use when the user runs /quarterback:drive or asks Quarterback to carry on.
---

# Drive

Take the current milestone to an open pull request, stopping only for the calls that need the user. Follow the playbook throughout.

The current milestone is the first unchecked one in `ROADMAP.md`. Work out how far it has got from its branch, its milestone file and any pull request (playbook), then carry on from there through these steps:

1. **Grill:** if the milestone file has no notes, use the `grill` skill. If it asked anything, stop until the user answers.
2. **Spec:** if there's no spec, run the `quarterback:spec-writer` agent.
3. **Build:** run the `quarterback:implementer` agent.
4. **Check:** run the `quarterback:reviewer` agent. If it fails, pass its findings to the implementer and check again. If it fails a second time, escalate.
5. **Pull request:** tick the milestone in `ROADMAP.md`, commit, push the branch and open a pull request against the default branch. Its body follows the playbook, using the decisions from the milestone file and the evidence from the reviewer's report.

Run the agents one at a time, on the milestone's branch. Give each one what it needs, such as the milestone, the file path and any findings, rather than the whole history.

When a report ends in `NEEDS_USER`, ask the user that question (with AskUserQuestion if you have it), pass the answer back and carry on.

Stop when:

- the pull request is open, and give the user its link
- you need the user and can't go further without them
- the milestone's pull request is already open, and say that it's waiting for their merge
- there's no `ROADMAP.md`, or every milestone is ticked, and say so
