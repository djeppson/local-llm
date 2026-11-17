# User Only

This is a ad-hoc scribble pad for me, the user, to use. No need to read further.

## Should this kind of usage convo be avoided?

Keep the edits surgical. Multiple edit calls on the same file — must they be sequential? They’re independent text regions; can I batch them in one message (multiple edits to the same file — order of application? They’re independent, non-overlapping regions; parallel edits to the same file risk conflicts. Safer: sequential, or one big edit? Multiple distinct small edits; do them one per message? That’s too many round trips. The edit tool applies immediately; parallel calls to the same file — the tool probably serializes, but each edit matches oldString independently; regions don’t overlap so order doesn’t matter. Batch 4 edits in one block.


## Agent confusion
Now the layout is fully visible, and it's cleaner than I assumed:
- Your OpenCode global AGENTS.md is a 201-byte pointer — its actual content is literally "always check for AGENTS.md in the repo you're working in." So the layering (global says "go look", repo says "what") is intentional on your part.
- The shared framework file you have now lives in frob/ and is symlinked into local-llm and valheim — and fin has its own, different AGENTS.md (a real file — so the "repo-specific layer" already exists in your setup too).
- Your opencode.json is already a symlink into the notes repo (notes/config/.config/opencode/opencode.json) — you already have a repo that owns your user-wide OpenCode config.
- One concrete bug in the current setup: because local-llm/AGENTS.md is a symlink to frob/AGENTS.md, the harness injects that 8KB document under both paths, on every turn — the same text twice, in every prompt. The "jank" you're feeling has a measurable cost.
So your instinct is right, and the target shape follows almost directly from what you've already built:
1. Framework file moves into the notes config repo — config/.config/opencode/AGENTS.md, a real file (git-versioned, replacing the need for frob as the "dedicated repo" — the experiment you're playing with already exists and works, you just weren't using it for this).
2. ~/.config/opencode/AGENTS.md becomes a symlink to it (exactly mirroring how opencode.json is wired) — replacing the pointer text.
3. Symlinks removed in local-llm and valheim — ends the double-injection; the framework is now global by construction.
4. fin/AGENTS.md stays if it's genuinely repo-specific (I'd read it to confirm it's not a stale copy of the shared one).
5. frob/ retires (move the file, delete the dir — or tell me to keep it).
6. The header line updates to match reality: "owned by the notes config repo, loaded as OpenCode's user-wide AGENTS.md; repo-specific instructions live in each repository's own AGENTS.md."
That gives you: one source of truth, version control where your other config already lives, idiomatic loading (global once, repo layer thin/optional), no symlinks in projects, no duplicate injection.
Want me to go through that (starting by reading fin/AGENTS.md so we know what "repo-specific" content actually needs to survive)?
