---
name: spec
description: How to write a Quarterback milestone spec, which covers the behaviour to build and the checks that prove it, within what the milestone's notes settled. Preloaded by the spec-writer agent.
user-invocable: false
---

# Writing a spec

A spec lets an implementer build the milestone without asking anything, and lets a reviewer check it without making judgement calls. Write it under `## Spec` in the milestone file (playbook), with these parts:

- **Goal:** what changes for the user, in a sentence or two.
- **Behaviour:** what to build, described as what a user can observe, not how it's coded. It includes the edge cases a user would hit.
- **Acceptance checks:** a numbered list. Each check is a command to run, or something to look at, with its exact expected result. Together they prove the milestone's definition of done. Prefer automated tests that the implementer adds, and say where they go.
- **Out of scope:** anything nearby that this milestone doesn't do.

Stay within the milestone and its notes. If a gap is on the playbook's decide list, decide it and log the decision. If it's on the ask list, escalate. Use the project's existing stack, conventions and checks.

The spec should take two minutes to read. If it needs more, the milestone is too big, so escalate with a proposed split.
