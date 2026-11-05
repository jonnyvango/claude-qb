# Quarterback

You quarterback, Claude plays. Quarterback is a Claude Code plugin that takes a project from an idea to merged pull requests. It stops only for the calls that need you: product decisions, decisions that can't be undone, and merges.

**Status: early development.** A rough first version of `/quarterback:drive` works, given a `ROADMAP.md` you write yourself. Everything marked planned arrives milestone by milestone. See the [roadmap](ROADMAP.md) for where it's up to.

## How it works

1. **`/quarterback:roadmap`** *(planned)* asks you about your idea and writes `ROADMAP.md`: the vision, then milestones, each with a definition of done. Only the next one or two milestones are written in detail. Each later one is detailed when it comes up, using what the earlier ones taught. Until it arrives, write `ROADMAP.md` yourself as a checklist, one line per milestone: `- [ ] **1. Name:** what it does. Done when ...`
2. **`/quarterback:drive`** takes the first unticked milestone to an open pull request, and stops only when it needs you. Along the way it:
   1. asks you about the milestone, if it needs your input (`/quarterback:grill` runs this step on its own)
   2. writes the spec
   3. builds it
   4. checks it
   5. opens a pull request

   Each milestone gets a branch, `spec/<n>-<slug>` (in a cloud session, the branch the session was given), and a file, `docs/milestones/<n>-<slug>.md`, which holds your answers, the spec and the decision log. After you answer a question or merge a pull request, run `/quarterback:drive` again and it picks up where it stopped.
3. When it needs you, it stops and asks in the session. *(Planned: notifications on your computer or phone.)*

Cloud is the default, so your machine doesn't need to stay on, but it runs locally too. It has taken a milestone to an open pull request both locally and in a cloud session. [`docs/cloud-spike.md`](docs/cloud-spike.md) records what works in the cloud, and what still needs fixing.

## What needs you

Quarterback's agents make the decisions that can be undone themselves, and ask you about the rest, such as scope, money and security. Every pull request is built to be reviewed in minutes, and lists the decisions made with how to override each one. The full rules are in the [playbook](skills/playbook/SKILL.md).

Quarterback never merges, never pushes to your default branch, and never force-pushes. A hook enforces this in every Claude Code session where the plugin is enabled, not only during Quarterback's work. While it's on, Claude can't merge a pull request, merge into the default branch, push to it or force-push, in any repository. Do those yourself, or disable the plugin.

## Requirements

- Claude Code
- git, and the GitHub CLI (`gh`) signed in, to open pull requests
- Python 3, for the git hook. Without it, or if the hook crashes, the hook can't block anything and Claude Code lets the command through.

## Install

```sh
claude plugin marketplace add jonnyvango/claude-qb
claude plugin install quarterback@claude-qb
```

A cloud session (claude.ai/code) doesn't install plugins listed in a repo's `.claude/settings.json`, so put these in your cloud environment's setup script instead. Keep the update lines: a cloud environment reuses its cached setup, and without them it keeps an old copy of the plugin.

```sh
claude plugin marketplace add jonnyvango/claude-qb
claude plugin install quarterback@claude-qb
claude plugin marketplace update claude-qb
claude plugin update quarterback@claude-qb
```

In the cloud, `gh pr create` is blocked, so Quarterback opens the pull request another way, such as GitHub's REST API (`gh api`) or the session's GitHub connector.

## Development

The shared rules every step follows are in [`skills/playbook/SKILL.md`](skills/playbook/SKILL.md). How to write skills and agents for this plugin is in [`CLAUDE.md`](CLAUDE.md).

```sh
claude --plugin-dir .          # run a session with your working copy
claude plugin validate .       # check the plugin
python3 -m unittest discover tests   # test the git hook
claude plugin eval . --scaffold --allow-tools Bash Write Edit   # run the skills' evals
```

Every pull request to `master` runs [`checks.yml`](.github/workflows/checks.yml) in GitHub Actions. It validates the plugin, tests the git hook, and fails if the pull request changes `skills/`, `agents/` or `hooks/` without bumping the version in `.claude-plugin/plugin.json`. The bump makes installed copies, including cached cloud environments, pick up the change.

Each skill has eval cases in [`evals/`](evals). Every eval run is a real Claude session on your account, so add `--case <name> --runs 1` while iterating. On a Claude plan, runs count against your usage limits. The dollar cost the eval reports is an estimate at API list price, not a charge.

Issues are tracked in [GitHub Issues](https://github.com/jonnyvango/claude-qb/issues).

## History

Quarterback started as a live hub showing every Claude Code session on your machine. That version is retired, and its code is in this repository's git history. A new UI is planned as a milestone, and the workflow will build it.

## License

[MIT](LICENSE)
