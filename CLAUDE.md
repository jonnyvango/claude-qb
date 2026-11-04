## README

Quarterback is open source, and `README.md` is how people learn it. Update the README in every change, in the same commit. A change is done when every command, requirement and behaviour the README describes matches the code.

## Writing skills and agents

The workflow is made of skills (`skills/<name>/SKILL.md`) and agents (`agents/<name>.md`).

- **A skill** is for talking to the user or orchestrating, because only the main session can do either. It states its goal, its constraints and when it's done. It doesn't script steps: the model decides how.
- **An agent** is for self-contained work that gains from a fresh context. It states its role, the exact report it returns, and when it escalates. Its model, tools and isolation go in its frontmatter, not in the prompt. The *how* goes in a skill that the agent preloads with `skills:`.
- **Shared runtime rules** live in `skills/playbook/SKILL.md`: which decisions an agent makes itself, how it escalates, and what every pull request contains. Every agent preloads it. Don't restate those rules elsewhere; point to them.
- **Hard rules belong in hooks** (`hooks/`) wherever they can be checked mechanically, such as never merging and never pushing to the default branch. A rule that lives only in a prompt is one an agent can forget.
- **Everything ships in the plugin.** Cloud sessions have no `~/.claude/skills/`, so nothing may depend on skills or settings outside this repo.
- **Keep them short.** Every line costs context in every session that loads it. Cut anything a capable model would do anyway.

## Checks

Run `claude plugin validate .` before committing, and `python3 -m unittest discover tests` when you change a hook. Each skill has eval cases in `evals/`. Run them with `claude plugin eval . --scaffold --allow-tools Bash Write Edit`, adding `--case <name> --runs 1` while iterating. Every run is a real Claude session that uses up plan usage, or API credit on an API key, and the cost it reports is a list-price estimate, not a bill. `--case` takes one glob, so a second `--case` replaces the first. On macOS, git can't run inside the eval sandbox, so grade files and messages, not commits.
