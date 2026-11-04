# Cloud spike (phase 2)

Notes from running `/quarterback:drive` on [qb-toy](https://github.com/jonnyvango/qb-toy) in a cloud session. Phase 2 is done when the loop has run there and these questions have answers.

| Question | Answer so far |
| --- | --- |
| Does the plugin load from qb-toy's `.claude/settings.json`? | Not yet: run 1 had no GitHub access to claude-qb |
| Does the git hook block a push to master? | Not tested: the hook never loaded |
| Is python3 there for the hook? | Yes: 3.13 at `/usr/local/bin/python3` |
| How does grill ask its questions? | Not tested. `AskUserQuestion` is available |
| Can it push and open a PR? | Not yet: no `origin` remote, and `gh` saw an invalid `GH_TOKEN` |
| What do commits look like without the personal atomic-commits skill? | Not tested: that skill isn't there, and no commits were made |

## Run 1: 2026-11-04

Launched with `claude --cloud "<prompt>"` from a local clone of qb-toy. `--cloud` won't start without an interactive terminal, so an agent can't launch it on its own. The user had to run it.

What happened:

- **The plugin didn't load.** The session read qb-toy's settings, but nothing was installed (`installed_plugins.json` was empty). `gh api repos/jonnyvango/claude-qb` returned 403 because the session had no GitHub access to that repo. claude-qb is private, so the marketplace couldn't be fetched.
- **There was no `origin` remote.** The clone had no remote at all, so `git push origin master` failed with exit 128 before any hook could matter. Launching from a local directory doesn't seem to give the session a GitHub remote.
- **`gh` was installed but not signed in.** `GH_TOKEN` was set, but `gh auth status` called it invalid.
- **There was nothing to drive.** qb-toy's only milestone, Shout, was already done, so even a working plugin would have stopped.

For run 2:

1. Give the session GitHub access to both repos: read access to claude-qb, and push access to qb-toy.
2. Start the session on the qb-toy GitHub repo (from claude.ai/code, or check that `--cloud` attaches a remote), so that `origin` exists.
3. Find where the invalid `GH_TOKEN` comes from in the cloud environment, and fix or remove it.
4. Give qb-toy an open milestone.
