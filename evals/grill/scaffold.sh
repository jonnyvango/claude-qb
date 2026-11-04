#!/usr/bin/env bash
# A toy repo whose next milestone is too vague to spec without the user.
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

- [x] **1. Greet:** `./greet <name>` prints `Hello, <name>!`.
- [ ] **2. Languages:** greet people in their own language. Done when the greeting can be in more than one language.
MD
git add -A
git commit -qm "Start the greeting CLI"
