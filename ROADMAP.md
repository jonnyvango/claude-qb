# Roadmap

Quarterback runs on macOS with Ghostty and zsh today. The goal is a hub that installs in one step and works in any terminal.

The order is deliberate: make it reliable, keep terminal-specific code in one place, then build features and add terminals side by side. Phases 3 and 4 can run at the same time.

## Phase 1: Make it solid

Someone new should be able to install Quarterback in one step, and it should keep working when Claude Code updates.

- [ ] One-step install: `/qb` starts the hub from the plugin's own folder, with no clone or symlink
- [ ] Remove the Node.js 23.6+ requirement by shipping a prebuilt binary or plain JavaScript
- [ ] Fall back cleanly when Claude Code's session or transcript files change format
- [ ] State the minimum supported Claude Code version
- [ ] Run tests in GitHub Actions, including coverage of `bin/qb.ts` and `hooks/register.tsx`
- [ ] Reuse an open hub window instead of opening another on each `/qb`
- [ ] Scroll boards taller than the window
- [ ] Add a setting to turn off the background tint
- [ ] Make session status files readable only by their owner

## Phase 2: Separate the terminal code

Adding a terminal should mean adding one small implementation, not changing the hub.

- [ ] Put opening a window and jumping to a tab behind one interface, with Ghostty as the first implementation
- [ ] Remove the assumptions about zsh and macOS `ttys` device names
- [ ] Keep the hub working on unsupported terminals, without the jump keys

## Phase 3: Build features

Features should work without terminal-specific code wherever possible.

- [ ] Show when a session is waiting on you, such as for a permission prompt

## Phase 4: Widen the audience

A terminal counts as supported once it has been tested on a real setup. Each one gets listed in a support table in the README.

1. [ ] iTerm2
2. [ ] tmux
3. [ ] Terminal.app
4. [ ] WezTerm and Kitty
5. [ ] Linux
6. [ ] Windows, if there's demand

## Wider launch

Announce Quarterback widely once the install takes one step and at least one terminal besides Ghostty works.
