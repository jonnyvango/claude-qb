#!/usr/bin/env bash
# A toy repo partway through a milestone: the notes are in, the spec isn't.
set -euo pipefail
git init -q -b master
git config user.name "Eval"
git config user.email "eval@example.com"
cat > greet <<'SH'
#!/usr/bin/env bash
echo "Hello, ${1:-world}!"
SH
chmod +x greet
cat > ROADMAP.md <<'MD'
# Roadmap

A tiny greeting CLI.

- [ ] **1. Shout:** a `--shout` flag that prints the greeting in capitals. Done when `./greet --shout Bob` prints `HELLO, BOB!`.
MD
git add -A
git commit -qm "Start the greeting CLI"
git switch -q -c spec/1-shout
mkdir -p docs/milestones
cat > docs/milestones/1-shout.md <<'MD'
# 1. Shout

## Notes

No questions needed.

## Spec

## Decisions
MD
git add -A
git commit -qm "Add notes for milestone 1"
