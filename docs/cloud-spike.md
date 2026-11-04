# Cloud spike (phase 2)

Notes from running `/quarterback:drive` on [qb-toy](https://github.com/jonnyvango/qb-toy) in a cloud session. Phase 2 is done: the loop ran there, and on 2026-11-04 the user chose cloud as the default. The fixes it needs are roadmap item 2b.

| Question | Answer |
| --- | --- |
| Does the plugin load? | Yes, once the cloud environment's setup script installs it (run 3). By design, a cloud session never installs plugins from a repo's `.claude/settings.json` |
| Does a user have to give the session access to claude-qb? | No. Run 2 reached it with only qb-toy enabled |
| Does the git hook block a push to master? | Yes. It denied `git push origin master` before the command ran (run 3) |
| Is python3 there for the hook? | Yes: 3.13 at `/usr/local/bin/python3` |
| How does grill ask its questions? | It asked one batch of three multiple-choice questions through `AskUserQuestion`, each with its recommended answer first, and waited for answers in the web UI |
| Can it push and open a PR? | Push: yes, but only to the session's own `claude/<name>` branch, not `spec/<n>-<slug>`. PR: `gh pr create` gets a 403 because GraphQL is blocked, but `gh api -X POST repos/<owner>/<repo>/pulls` (REST) opened it. The session's GitHub connector (`create_pull_request`) works too (run 4) |
| Does a cloud environment pick up plugin updates? | Not by itself. Run 4 still had 0.7.0 (`511062b`, the run 3 install) after master moved to 0.8.0, because the environment's cached setup was reused. Adding `claude plugin marketplace update` and `claude plugin update` to the setup script fixed it (run 5) |
| Does anyone need to fix `GH_TOKEN`? | No. It reads as the placeholder `proxy-injected`, and the proxy swaps in real credentials |
| What do commits look like without the personal atomic-commits skill? | Small and focused: 7 commits, each one step (notes, spec, tests, feature, README, decision log, a fix-up) |

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

## What the docs say

From [cloud environments](https://code.claude.com/docs/en/cloud-environments.md) and [plugin loading](https://code.claude.com/docs/en/plugins/loading.md):

- **Plugins:** a cloud session doesn't install the plugins a repo turns on in `enabledPlugins`. It doesn't add the marketplaces in `extraKnownMarketplaces` either, because that needs the workspace trust dialog, and a cloud session never shows it. The supported route is the environment's setup script, which runs before Claude Code starts: `claude plugin marketplace add jonnyvango/claude-qb` and then `claude plugin install quarterback@claude-qb`. A SessionStart hook would install the plugin too late, because plugins load at session start.
- **GitHub:** `GH_TOKEN` is the placeholder `proxy-injected`, and the GitHub proxy fills in real credentials. That explains run 1's "invalid token". The proxy blocks GraphQL, so `gh pr` and `gh issue` get a 403. REST calls through `gh api` work, and the web UI has a Create PR button.

So every cloud user would need a one-time setup script, and drive can't rely on `gh pr create` there.

## Run 3: 2026-11-04

The cloud environment's setup script ran `claude plugin marketplace add jonnyvango/claude-qb` and `claude plugin install quarterback@claude-qb`, and the session was started on qb-toy from claude.ai/code. Result: [qb-toy #4](https://github.com/jonnyvango/qb-toy/pull/4), milestone 2 (Languages), opened, with nothing merged and nothing pushed to master.

- **The plugin loaded** (v0.7.0), with all its skills and agents.
- **The hook blocked** `git push origin master`, with Quarterback's deny message.
- **Grill** asked three questions in one batch, and the run waited until they were answered.
- **The branch:** the session can only push to the branch it was given (`claude/tender-galileo-dqfcuf`), so drive used that branch instead of `spec/2-languages` and logged the decision in the PR.
- **The PR:** `gh pr create` failed with "GitHub GraphQL is not available from Claude Code sessions; use the REST API". Opening it through `gh api` worked, but only because the prompt said to try that.
- **The review** passed on the first pass, with the PR sections the playbook asks for. bash 3.2 couldn't be tested, because the container only has 5.2.

## What cloud needs from Quarterback

1. **Install docs:** each user adds the two install commands to their cloud environment's setup script.
2. **Opening a PR:** drive should fall back to the REST API when `gh pr create` fails, without being told to.
3. **Branch names:** in a cloud session, use the branch the session was given rather than `spec/<n>-<slug>`.

## Run 4: 2026-11-04

This run was meant to test roadmap item 2b (0.8.0) with a plain prompt. Result: [qb-toy #6](https://github.com/jonnyvango/qb-toy/pull/6), milestone 3 (Help), opened, but on the old plugin. So it doesn't count as 2b's check.

- **The plugin was stale.** The session had 0.7.0 at `511062b`, the same install as run 3, so the environment's cached setup was reused, and that cache doesn't pick up plugin updates. The prompt said to stop unless the version was 0.8.0, but the session ran drive anyway.
- **The PR was opened through the GitHub connector.** Without being told how, the old drive pushed and then called the connector's `create_pull_request` tool, not `gh`. The guard's matcher covers `mcp__<any server>__merge_pull_request`, so the connector can't merge.
- **The branch** was the session's own `claude/<name>`, recorded as a decision, as the old rules required.

## Run 5: 2026-11-04

This was roadmap item 2b's done check: the setup script had the two update lines added, and the prompt didn't say how to open the PR or which branch to use. Result: [qb-toy #8](https://github.com/jonnyvango/qb-toy/pull/8), milestone 4 (Version), opened on 0.8.0 (`40f0bd5`). 2b is done.

- **The plugin was current.** Changing the setup script made the environment reinstall it.
- **The branch** was the session's own `claude/<name>`, found without being told. Drive also checked for earlier work on the milestone and found none. The branch still appeared in the decision log, which it no longer needs to.
- **The PR** was opened through the GitHub connector's `create_pull_request`. In this session `gh` was allowed only for search, so drive skipped `gh api` and picked the connector on its own.
- **Grill** asked nothing, because the roadmap line settled what users see.
- **The decision log** had 6 entries, each about behaviour users see or a changed test, against 12 for milestone 2 before the playbook was trimmed.
