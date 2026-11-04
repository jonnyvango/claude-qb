# Roadmap

This is the plan for building Quarterback itself. It's a placeholder: in phase 5, `/quarterback:roadmap` rewrites it in Quarterback's own format, and from then on the workflow drives it.

The order is deliberate. A rough version of the whole loop comes first, and then each part gets improved, starting with whichever part breaks.

- [x] **0. Scaffold:** retire the hub, set up the plugin and write the shared rules.
- [x] **1. Crude end to end:** minimal `grill`, `spec` and `drive` skills; `spec-writer`, `implementer` and `reviewer` agents; a hook that blocks merges and pushes to the default branch; one eval per skill. Done when `/drive` takes a toy milestone to an open pull request.
- [x] **2. Cloud spike:** run the rough loop in a cloud session and record what works there, which decides whether cloud or local is the default. Include a check that a push to the default branch really gets blocked there. If Python is missing or the hook crashes, Claude Code lets the command through. Result: cloud is the default. See [`docs/cloud-spike.md`](docs/cloud-spike.md).
- [ ] **2b. Cloud fixes:** when `gh pr create` is blocked, drive opens the PR through the REST API, and in a cloud session it uses the branch the session was given instead of `spec/<n>-<slug>`. Done when a cloud run gets to an open PR without being told how.
- [ ] **3. Verification:** acceptance checks in every spec, tests written first, a hook that stops an implementer while its check fails, and reviews that run the app.
- [ ] **4. Your attention:** a grill with a scope fence, a decision log, escalation, notifications and attempt budgets.
- [ ] **5. Roadmap:** the `roadmap` skill, tested by rewriting this file.
- [ ] **6. Parallel tasks and lessons:** independent tasks in parallel, and lessons written back to `CLAUDE.md`.
- [ ] **7. The new UI:** Quarterback builds its own UI, with you only quarterbacking.

## Later

- Working ahead on stacked branches while a pull request waits for you
- Closing the git hook's gaps: commands run from scripts an agent writes, remotes other than `origin`, `gh repo sync`, and merges through `gh api graphql`
- Evals that can check commits, since git can't run inside the eval sandbox on macOS
- Resuming a milestone in a new cloud session, which gets a different branch from the one the earlier work is on
- A full eval baseline: so far each case has run once, without the no-plugin arm
