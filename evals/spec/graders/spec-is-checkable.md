---
type: llm
focus: { source: file, path: docs/milestones/1-shout.md }
---

PASS if the `## Spec` section has a goal, the behaviour (including what `--shout` does with no name), a numbered list of acceptance checks and what's out of scope. Each acceptance check must be a command or observation with an exact expected result, and one must show that `./greet --shout Bob` prints `HELLO, BOB!`. It must have one `Check: `<command>`` line whose command runs the automated checks, and that command must exercise `--shout`, so it can't pass before the flag exists. FAIL if the spec is missing, the check line is missing or wouldn't test `--shout`, any check is vague, such as "works correctly", or it adds scope that the milestone and its notes don't call for.
