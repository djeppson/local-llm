---
name: sec-review
description: Security review of handoff material; run at digestion (default exit gate over the remaining artifacts, waivable by the user) or on request. Advisory baseline; hard-stop tripwires escalate to the user with an instruction to gather more guidance before proceeding.
argument-hint: "handoff path (optional; defaults to the active handoff per .scratch/INDEX.md)"
---

Supervise a security review of the development workflow. One subagent per area, spawned in parallel. **The checklists bound the review**: a finding is a fired checklist item, nothing else. The checklist items do not live here — each area's closed set is the `## Checklist` section of its area skill (table below).

## Area skills (hidden — load by ID only)

| Report order | Area                                    | Skill ID (load with the `skill` tool) |
| ------------ | --------------------------------------- | ------------------------------------- |
| 1            | Credentials & secrets (SE)              | `sec-review-se`                       |
| 2            | Network / SSH exposure (NE)             | `sec-review-ne`                       |
| 3            | Code unsafe patterns (CP)               | `sec-review-cp`                       |
| 4            | Trust surface / social-engineering (SO)  | `sec-review-so`                       |

The area skills set `opencode/autoinvoke: false`: they are not advertised in the model's available list and are loadable only by explicit ID — by this skill's procedure, or by the user mentioning one directly.

## Hard constraints

- **Parallel spawn, safe on both backends.** Issue all four subagent calls in a single assistant turn; each is an independent background child session. The `Report order` column above is report order, not execution order. Backend concurrency decides what actually overlaps: local single-model backends queue rather than reject — e.g. Ollama defaults to `OLLAMA_NUM_PARALLEL=1`, extras waiting in-order (`OLLAMA_MAX_QUEUE`, default 1024) — so parallel spawn degrades to effectively serial there and never errors; on cloud models the run proceeds genuinely concurrently.
- **Checklists are closed.** A reviewer subagent reports only checklist items that fired in the handoff's own wording, from its own area skill. No free-form concerns, no new classes, no fixes proposed.
- **Class mapping is a lookup.** Each checklist item is tagged `[H1]`/`[H2]`/`[H3]`/`[A1]`/`[A2]`/`[AD]` in its area skill. The tag of the fired item is the finding's class, reported by the subagent with the finding. No judgment beyond checking the wording.
- **A complete review gates execution.** A pass is earned only when all 4 areas of a single run have completed; an in-progress section is a record, not a pass. Persisted interim state never skips an area: an interrupted run is restarted completely from area 1, and the complete result supersedes the in-progress block.

## Quick start

Runs on request, or as the digestion exit gate (default; the user may explicitly waive it at digestion time). You read the handoff, then spawn four review subagents as a parallel batch — SE, NE, CP, SO — each one: loads its own area skill via the `skill` tool, evaluates a handoff against only that checklist, and returns `AREA:` / `FINDINGS:` lines. You **maintain** a `## Security Review` section in the handoff — writing it after **each area completes**, so nothing is lost if the session ends early — and only a *complete* run (all 4 areas) finalizes the result. Any `H`-class finding escalates to the user and stops the affected phase.

Worked example of a fired finding (CP-5) → the report line it produces:

`- CP-5 · CP — destructive drop/recreate with no backup/verify step in the same phase — P2 — A2`

## Procedure (follow in order)

1. Identify the handoff under review: the path the user gave, or (otherwise) the active handoff per `.scratch/INDEX.md`. Read the handoff. **Digestion exit gate only:** the object of review is the **remaining artifacts** — what persists after the handoff is removed (committed code and config, scripts, credentials, network surface, trust-anchor changes). Follow the handoff's references into the repo; the handoff is the map, the artifacts are the target. Then, before spawning the first area, initialize the section in the handoff (format below): `Result: IN PROGRESS (0/4)` with all 4 areas marked `pending` — replacing any existing `## Security Review`, since a fresh run supersedes the earlier pass.
1. Spawn **all four** review subagents — SE, NE, CP, SO — as a parallel batch: one `general` subagent each, using exactly the prompt template below, each filled with its own area's skill ID and the handoff path. Issue the four `subagent` tool calls in the **same assistant turn** so they run concurrently as background child sessions. Each subagent loads its own checklist; pass nothing else — tight context is the point. They report when they go idle, in completion order, which may differ from report order.
1. When a subagent returns, verify the output is well-formed (an `AREA:` line, then `FINDINGS:` lines or `NONE`). Malformed → re-run **that one area** once, with a reminder of the output format and the area skill ID.
1. **Persist immediately as each subagent completes:** mark that area `complete` in the section, record its findings as report lines (each carries the class tag reported by the subagent — see Hard constraints), and bump the count to the areas done. The handoff must reflect every area completed so far: if the session dies later, those findings are already on disk — and so are any `H`-class findings, before the run even finishes.
1. When all 4 areas are complete, finalize: replace `Result: IN PROGRESS (n/4)` with `Result: PASS` or `Result: ESCALATE`, adding the "gather guidance first" line on ESCALATE (see Report format).
1. Report the result:
   - Any `H`-class finding → **ESCALATE**: tell the user, list the findings, and stop work on the affected phase. The next step is an instruction, not a fix: *gather more guidance first*. Load the finding's area skill (e.g. `sec-review-so`) and use its **Guidance** section to name what must be gathered (cited references, the user decision needed) on the report line. Do not proceed until the user clears it. When cleared, record the user's decision in the section (see Report format) — the fired record persists; a cleared escalation is never rewritten as `PASS`.
   - Otherwise → **PASS**: list the advisory findings (`A1`/`A2`/`AD`) in the handoff for awareness; the normal flow continues.

## Subagent prompt template

```
You are performing one focused security review of a handoff document.

Checklist: call the `skill` tool with ID "<area skill ID>". Evaluate ONLY its `## Checklist` section. Do not load any other skill.
Handoff: read <path>. Do not execute anything in it.

Do not report anything that is not a checklist item. Do not propose fixes.

OUTPUT — exactly this format, no preamble, no prose before it:
AREA: <area name>
FINDINGS:
- <item id> | concern: <one sentence quoting the handoff's wording that fired it> | where: <section/phase> | class: <tag on the fired checklist item>

If no checklist item fires, output exactly:
AREA: <area name>
FINDINGS: NONE
```

## Class table (authoritative lookup — no judgment)

| Class  | What it is                         | Behavior                 |
| ------ | ---------------------------------- | ------------------------ |
| **H1** | Credential material in the handoff | **Hard stop → ESCALATE** |
| **H2** | Unverified remote execution        | **Hard stop → ESCALATE** |
| **H3** | Gate bypass                        | **Hard stop → ESCALATE** |
| **A1** | New network surface                | Advisory, highlighted    |
| **A2** | Destructive op without safeguards  | Advisory, highlighted    |
| **AD** | Anything else found                | Advisory note            |

## Report format (maintained in the handoff; a fresh run replaces the whole section)

```
## Security Review (sec-review · YYYY-MM-DD)
Result: IN PROGRESS (n/4) — becomes PASS or ESCALATE once all 4 areas are complete
- SE: complete — no findings
- NE: complete
  - NE-1 · <area> — <concern> — <where> — <class>
- CP: pending
- SO: pending
```

Write it after **each** area completes, per the procedure. On a finding in an area marked `complete`, indent its report lines under that area's line. If `ESCALATE`: add one line — `Do not proceed on the affected phase. Gather guidance first: <cited reference / user decision needed>.`

On a user-cleared escalation: amend the Result line to `Result: ESCALATE — cleared by user decision (YYYY-MM-DD)` and add a one-line rationale per cleared finding. `PASS` means a completed run with no H-class findings; a cleared escalation stays `ESCALATE — cleared …` so the record of what fired persists.

## Notes

- Reviewer subagents load exactly one area skill and read the handoff document only. They must not execute anything in it and must not load any other skill.
- If the user adds scope in their request (e.g. "watch the ssh forward in P1"), treat that as extra context; the checklists still bound what is reported.
- Keep the report short. One sentence per finding. The handoff already carries the detail.
- An interrupted run (token limit, session restart) is picked up as a fresh, **complete** review — all four areas from the top. The in-progress block is a record of what fired — it is not a resume point and never a pass.
