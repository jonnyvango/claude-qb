# Quarterback

You quarterback, Claude plays. Quarterback is a Claude Code plugin that takes a project from an idea to merged pull requests. It stops only for the calls that need you: product decisions, decisions that can't be undone, and merges.

**Status: early development.** Nothing is usable yet. The commands below are planned and arrive milestone by milestone. See the [roadmap](ROADMAP.md) for where it's up to.

## How it will work

1. **`/quarterback:roadmap`** asks you about your idea and writes `ROADMAP.md`: the vision, then milestones, each with a definition of done. Only the next one or two milestones are written in detail. Each later one is detailed when it comes up, using what the earlier ones taught.
2. **`/quarterback:drive`** moves the current milestone forward one step each time it runs. The steps are:
   1. ask you about the milestone, if it needs your input
   2. write the spec
   3. build it
   4. check it
   5. open a pull request
3. When it needs you, for a question or a pull request to merge, it notifies you on your computer or phone and stops. You answer, and it carries on.

It is designed to run in the cloud, so your machine doesn't need to stay on, or locally.

## What needs you

Quarterback's agents make anything that can be undone themselves, such as naming, structure and small behaviour details, and record each decision in the pull request. They ask you about anything that changes the product's scope or what users see, data changes that are hard to undo, new external services, money, and security trade-offs. Questions come in batches, as multiple choice, each with a recommended answer.

Every pull request is built to be reviewed in minutes. It contains:

- a summary
- the decisions made, with how to override each one
- evidence that it works, such as check output and screenshots
- anything left over

Quarterback never merges, never pushes to your default branch, and never force-pushes.

## Requirements

- Claude Code

## Install

```sh
claude plugin marketplace add jonnyvango/claude-qb
claude plugin install quarterback@claude-qb
```

## Development

How to write skills and agents for this plugin is in [`CLAUDE.md`](CLAUDE.md).

```sh
claude --plugin-dir .          # run a session with your working copy
claude plugin validate .       # check the plugin
```

Issues are tracked in [GitHub Issues](https://github.com/jonnyvango/claude-qb/issues).

## History

Quarterback started as a live hub showing every Claude Code session on your machine. That version is retired, and its code is in this repository's git history. A new UI is planned as a milestone, and the workflow will build it.

## License

[MIT](LICENSE)
