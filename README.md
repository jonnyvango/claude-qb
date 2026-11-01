# Quarterback

A live hub of every Claude Code session on your machine. Run `qb` and a whole terminal window shows what each session is doing, grouped by project, with none of Claude Code's own UI around it.

```
Quarterback  2 working, 4 open

claude-qb
  1  WORKING  Standalone hub window
      Bash: npm test
      RUNNING  Find bug: Read: /x.ts (3 tool calls)

shop
  2  COMPLETE  Fix checkout rounding
      Finished its turn

1-9 go to session · q quit
```

## Requirements

- macOS and [Ghostty](https://ghostty.org). The hub itself draws in any terminal, but opening its window and jumping to a tab use Ghostty's AppleScript support.
- Node.js 23.6 or later, which runs the hub's TypeScript directly. There is nothing to build and there are no dependencies.
- zsh, with `PATH` set up in `.zshrc` or earlier, for `/qb` to find the `qb` command.
- Claude Code.

## Install

Two parts: the plugin makes each session report what it's doing, and the `qb` command shows the hub.

Install the plugin at the prompt of a Claude Code session in a terminal:

```
/plugin install quarterback --marketplace jonnyvango/claude-qb
```

Answer `y` to add the marketplace, then choose a scope. Or from a shell:

```sh
claude plugin marketplace add jonnyvango/claude-qb
claude plugin install quarterback@claude-qb
```

Then clone the repository and put `qb` on your `PATH`:

```sh
git clone https://github.com/jonnyvango/claude-qb.git
ln -s "$PWD/claude-qb/bin/qb.ts" ~/.local/bin/qb
```

Restart any open Claude Code sessions so they pick up the plugin.

## Usage

| Run | What happens |
| --- | --- |
| `qb` in a terminal | Turns that terminal into the hub |
| `/qb` in a Claude Code session | Opens the hub in a new Ghostty window |

In the hub:

| Key | Action |
| --- | --- |
| `1`-`9` | Jump to that session's Ghostty tab |
| `q` or `Ctrl-C` | Quit |

## What the hub shows

Sessions are grouped under their project, which is the name of the folder the session runs in. Each session has:

- **A number**, if it runs in a terminal tab you can jump to.
- **Its status**: `WORKING`, `COMPLETE`, `IDLE`, or `OFFLINE` once a session stops reporting. An offline session leaves the board after a minute.
- **A short description**: your `/rename` title if you set one, otherwise Claude Code's automatic title, otherwise the first line of the prompt.
- **Its current activity**, such as the tool call in progress.
- **Its agents**, each with a status, what it's doing and its tool call count.

The board refreshes every 2 seconds. If it's taller than the window, the bottom is cut off with a note saying how many lines are hidden.

A session without the plugin still appears, because Claude Code lists every open session itself. It shows its status and description but no live activity or agents.

## Inside a session

Besides reporting to the hub, the plugin does two things in each session:

- Adds a summary to the status line, such as `QB: 2 working, 4 open`.
- Tints the terminal background by status: dark yellow while working, dark green when complete. It restores your background when the session ends.

## Privacy

Everything stays on your machine. Each session writes its status, latest prompt and current activity to `~/.claude/quarterback/<session id>.json`, and the file is deleted when the session ends. The hub reads those files plus Claude Code's own `~/.claude/sessions/` and `~/.claude/projects/` to find open sessions and their titles. It never reads the `.key` files in `~/.claude/sessions/`.

## Development

- `hooks/board.ts`: logic and drawing shared by the plugin and the hub. It has no I/O.
- `hooks/register.tsx`: the Claude Code plugin, which publishes each session's status.
- `bin/qb.ts`: the standalone hub.

```sh
claude --plugin-dir .          # run a session with your working copy
claude plugin test .           # run the tests
claude plugin validate .       # check the plugin
```

Issues are tracked in [GitHub Issues](https://github.com/jonnyvango/claude-qb/issues). See the [roadmap](ROADMAP.md) for what's planned.

## License

[MIT](LICENSE)
