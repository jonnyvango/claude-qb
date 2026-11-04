# Cloud spike (phase 2)

Notes from running `/quarterback:drive` on [qb-toy](https://github.com/jonnyvango/qb-toy) in a cloud session. Phase 2 is done when the loop has run there and these questions have answers.

| Question | Answer so far |
| --- | --- |
| Does the plugin load from qb-toy's `.claude/settings.json`? | No: in run 2 the session could reach claude-qb, but the project settings never triggered an install |
| Does a user have to give the session access to claude-qb? | No: run 2 reached it with only qb-toy enabled |
| Does the git hook block a push to master? | Not tested: the hook never loaded |
| Is python3 there for the hook? | Yes: 3.13 at `/usr/local/bin/python3` |
| How does grill ask its questions? | Not tested. `AskUserQuestion` is available |
| Can it push and open a PR? | Not yet: no `origin` remote, and `gh` saw an invalid `GH_TOKEN` |
| What do commits look like without the personal atomic-commits skill? | Not tested: that skill isn't there, and no commits were made |

## Run 1: 2026-11-04

Launched with `claude --cloud "<prompt>"` from a local clone of qb-toy. `--cloud` won't start without an interactive terminal, so an agent can't launch it on its own. The user had to run it.

What happened:

- **The plugin didn't load.** The session read qb-toy's settings, but nothing was installed (`installed_plugins.json` was empty). `gh api repos/jonnyvango/claude-qb` returned 403, saying GitHub access to that repo wasn't enabled for the session. claude-qb is public, so GitHub wasn't refusing a private repo: the session can only reach repos enabled for it, and that probably also blocked fetching the marketplace.
- **There was no `origin` remote.** The clone had no remote at all, so `git push origin master` failed with exit 128 before any hook could matter. Launching from a local directory doesn't seem to give the session a GitHub remote.
- **`gh` was installed but not signed in.** `GH_TOKEN` was set, but `gh auth status` called it invalid.
- **There was nothing to drive.** qb-toy's only milestone, Shout, was already done, so even a working plugin would have stopped.

For run 2:

1. Enable both repos for the session: claude-qb so the marketplace can be fetched, and qb-toy (private) with push access. If the plugin still doesn't install with claude-qb enabled, that's a finding: a public marketplace isn't enough on its own.
2. Start the session on the qb-toy GitHub repo (from claude.ai/code, or check that `--cloud` attaches a remote), so that `origin` exists.
3. Find where the invalid `GH_TOKEN` comes from in the cloud environment, and fix or remove it.
4. Give qb-toy an open milestone.

## Run 2: 2026-11-04

Started from claude.ai/code on the qb-toy GitHub repo, with only qb-toy enabled for the session. The prompt said to stop if the plugin hadn't loaded, and it hadn't.

- **The plugin still didn't load, and access wasn't the reason.** qb-toy's settings were correct, but `installed_plugins.json` was empty, and the session had no marketplace copy or plugin cache. `git ls-remote` on claude-qb worked, and `claude plugin marketplace add jonnyvango/claude-qb` cloned and validated it. So claude-qb is reachable with only qb-toy enabled. Run 1's 403 was most likely caused by launching from a local folder with `--cloud`.
- **Declaring the plugin in project settings wasn't enough.** `extraKnownMarketplaces` plus `enabledPlugins` didn't trigger an install before the session started.
- python3 is there again. `AskUserQuestion` is available, and `GH_TOKEN` is set in the container. Nothing else was tested.
