---
name: grill
description: Ask the user only what the current milestone needs from them, then record the answers as the milestone's notes. Use at the start of a milestone, or when the user wants to talk one through before it's specced.
---

# Grill

Settle the calls about the current milestone that only the user can make, so the rest of it can run without them. Follow the playbook.

Read the milestone in `ROADMAP.md` and enough of the project to know what already exists. List the calls the milestone leaves open and sort them with the playbook's decide-or-ask rules. Ask only about the ones on the ask list. Leave the rest to the agents. Don't decide them now.

When you ask:

- Ask in one batch of at most four questions. Each is multiple choice, with your recommended option first and labelled "(Recommended)". Use AskUserQuestion if you have it; otherwise list the questions in your reply and stop.
- Each question stands on its own: what it's about and why it matters, in a sentence.
- If an answer raises a new question that needs them, ask one more batch, but no more.
- If nothing needs them, ask nothing.

Write the outcome under `## Notes` in the milestone file, creating the file and branch if they don't exist yet (playbook). Write one line per settled call, plus anything the user said beyond the options. If you asked nothing, write "No questions needed". Commit it.

You're done when the notes are committed, or when you've asked and are waiting for answers.
