# Roadmap

This is the plan for building Quarterback itself. It's a placeholder: in phase 5, `/quarterback:roadmap` rewrites it in Quarterback's own format, and from then on the workflow drives it.

The order is deliberate. A rough version of the whole loop comes first, and then each part gets improved, starting with whichever part breaks.

- [x] **0. Scaffold:** retire the hub, set up the plugin and write the shared rules.
- [ ] **1. Crude end to end:** minimal `grill`, `spec` and `drive` skills; `spec-writer`, `implementer` and `reviewer` agents; a hook that blocks merges and pushes to the default branch; one eval per skill. Done when `/drive` takes a toy milestone to an open pull request.
- [ ] **2. Cloud spike:** run the rough loop in a cloud session and record what works there, which decides whether cloud or local is the default.
- [ ] **3. Verification:** acceptance checks in every spec, tests written first, a hook that stops an implementer while its check fails, and reviews that run the app.
- [ ] **4. Your attention:** a grill with a scope fence, a decision log, escalation, notifications and attempt budgets.
- [ ] **5. Roadmap:** the `roadmap` skill, tested by rewriting this file.
- [ ] **6. Parallel tasks and lessons:** independent tasks in parallel, and lessons written back to `CLAUDE.md`.
- [ ] **7. The new UI:** Quarterback builds its own UI, with you only quarterbacking.

## Later

- Working ahead on stacked branches while a pull request waits for you
