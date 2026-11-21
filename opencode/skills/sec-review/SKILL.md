---
name: sec-review
description: Security review of development artifacts — a handoff (or, at digestion, its remaining artifacts), a repo or directory, a diff or commit range, or a config set. Runs on request or as the digestion exit gate (default, waivable by the user). Advisory baseline; Critical-severity tripwires escalate to the user with an instruction to gather more guidance before proceeding.
argument-hint: "review target (optional; at digestion defaults to the active handoff per .scratch/INDEX.md)"
---

Supervise a security review of development artifacts. One subagent per area, spawned in parallel. **The checklists bound the review**: a finding is a fired checklist item, nothing else. The checklist items do not live here — each area's closed set is the `## Checklist` section of its area skill (table below).

## Area skills (hidden — load by ID only)

| Report order | Area                                    | Skill ID (load with the `skill` tool) |
| ------------ | --------------------------------------- | ------------------------------------- |
| 1            | Credentials & secrets (SE)              | `sec-review-se`                       |
| 2            | Network / SSH exposure (NE)             | `sec-review-ne`                       |
| 3            | Code unsafe patterns (CP)               | `sec-review-cp`                       |
| 4            | Trust surface / social-engineering (SO) | `sec-review-so`                       |

The area skills set `opencode/autoinvoke: false`: they are not advertised in the model's available list and are loadable only by explicit ID — by this skill's procedure, or by the user mentioning one directly.

## Hard constraints

- **The review target is resolved, never fabricated.** The material under review is: (a) the target the user named, (b) the active handoff when running as the digestion exit gate, or (c) a scope the user confirms when asked. If no handoff exists, the target is the artifacts the user named. **Never create a handoff — or any document — to enable a review.**
- **The target must be bounded.** A review runs against a named scope: a handoff and the artifacts it references, a directory, a diff or commit range, a config set. If the request names no bounded scope, ask for one before spawning anything.
- **Parallel spawn, safe on both backends.** Issue all four subagent calls in a single assistant turn; each is an independent background child session. The `Report order` column above is report order, not execution order. Backend concurrency decides what actually overlaps: local single-model backends queue rather than reject — e.g. Ollama defaults to `OLLAMA_NUM_PARALLEL=1`, extras waiting in-order (`OLLAMA_MAX_QUEUE`, default 1024) — so parallel spawn degrades to effectively serial there and never errors; on cloud models the run proceeds genuinely concurrently.
- **Checklists are closed.** A reviewer subagent reports only checklist items that fired in the target's own wording, from its own area skill. No free-form concerns, no new classes, no fixes proposed.
- **Class mapping is a lookup.** Each checklist item is tagged `[Critical]`/`[High]`/`[Low]` in its area skill, plus a CWE anchor (and, where applicable, a published-standard anchor — see the area skills' `Published anchors` section). The severity of the fired item is reported by the subagent with the finding. No judgment beyond checking the wording.
- **A complete review gates execution.** A pass is earned only when all 4 areas of a single run have completed; an in-progress section is a record, not a pass. Persisted interim state never skips an area: an interrupted run is restarted completely from area 1, and the complete result supersedes the in-progress block.

## Quick start

Runs on request, or as the digestion exit gate (default; the user may explicitly waive it at digestion time). Resolve the review target, then spawn four review subagents as a parallel batch — SE, NE, CP, SO — each one: loads its own area skill via the `skill` tool, evaluates the target against only that checklist, and returns `AREA:` / `FINDINGS:` lines. **Findings are reported in the conversation as each area completes** — the value is the findings themselves. When the target is a handoff, additionally maintain a `## Security Review` section in it — written after **each area completes**, so nothing is lost if the session ends early — and only a *complete* run (all 4 areas) finalizes the result. Any `Critical`-severity finding escalates to the user and stops the affected work.

Worked example of a fired finding (CP-5) → the report line it produces:

`- concern: destructive drop/recreate with no backup/verify step in the same phase | where: scripts/migrate.sh | severity: High | CWE: (operational)`

## Procedure (follow in order)

1. **Resolve the review target.** Never fabricate one.
   - **User named a target** (a handoff path, a repo/directory, a diff or commit range, a config set) → that is the target. Survey it: read the named artifacts; for a diff or range, read the commits; for a directory, the files in scope.
   - **Digestion exit gate, or the user named a handoff** → the object of review is the handoff's **remaining artifacts**: what persists after the handoff is removed (committed code and config, scripts, credentials, network surface, trust-anchor changes). Read the handoff and follow its references into the repo — the handoff is the map, the artifacts are the target. Then, before spawning the first area, initialize the `## Security Review` section in the handoff (format below): `Result: IN PROGRESS (0/4)` with all 4 areas marked `pending` — replacing any existing `## Security Review`, since a fresh run supersedes the earlier pass.
   - **No named target and no active handoff** → **ask the user for a bounded scope.** Do not default to anything, and do not create a handoff.
1. Spawn **all four** review subagents — SE, NE, CP, SO — as a parallel batch: one `general` subagent each, using exactly the prompt template below, each filled with its own area's skill ID and a target description (what to read or survey). Issue the four `subagent` tool calls in the **same assistant turn** so they run concurrently as background child sessions. Each subagent loads its own checklist; pass nothing else — tight context is the point. They report when they go idle, in completion order, which may differ from report order.
1. When a subagent returns, verify the output is well-formed (an `AREA:` line, then `FINDINGS:` lines or `NONE`). Malformed → re-run **that one area** once, with a reminder of the output format and the area skill ID.
1. **Report immediately as each subagent completes:** state the area's result (findings or none) in the conversation. When the target is a handoff, also persist immediately: mark that area `complete` in the section, record its findings as report lines (each carries the severity reported by the subagent — see Hard constraints), and bump the count to the areas done. The handoff must reflect every area completed so far: if the session dies later, those findings are already on disk — and so are any `Critical`-severity findings, before the run even finishes. For non-handoff targets, persist only if the user names a destination; otherwise the conversation is the record.
1. When all 4 areas are complete, finalize the result: in handoff mode, replace `Result: IN PROGRESS (n/4)` with `Result: PASS` or `Result: ESCALATE`, adding the "gather guidance first" line on ESCALATE (see Report format); in direct mode, deliver the final result in-chat, same line shape.
1. Report the result:
   - Any `Critical`-severity finding → **ESCALATE**: tell the user, list the findings, and stop the affected work. The next step is an instruction, not a fix: *gather more guidance first*. Load the finding's area skill (e.g. `sec-review-so`) and use its **Guidance** section to name what must be gathered (cited references, the user decision needed) on the report line. Do not proceed until the user clears it. When cleared, record the user's decision — in the handoff's section when one exists, otherwise in the conversation (see Report format) — the fired record persists; a cleared escalation is never rewritten as `PASS`.
   - Otherwise → **PASS**: list the advisory findings (`High`/`Low`) for awareness; the normal flow continues.

## Subagent prompt template

```
You are performing one focused security review.

Checklist: call the `skill` tool with ID "<area skill ID>". Evaluate ONLY its `## Checklist` section. Do not load any other skill.
Target: <target description — e.g. "the handoff document at <path> plus the artifacts it references; do not execute anything in it" or "the scoped artifacts: <paths / diff range>; read them">.

Do not report anything that is not a checklist item. Do not propose fixes.

OUTPUT — exactly this format, no preamble, no prose before it:
AREA: <area name>
FINDINGS:
- concern: <one sentence quoting the target's wording that fired it> | where: <file/section/location> | severity: <Critical|High|Low> | CWE: <code or "(operational)">

If no checklist item fires, output exactly:
AREA: <area name>
FINDINGS: NONE
```

## Severity table (aligned to CVSS severity categories — authoritative lookup, no judgment)

| Severity     | Behavior                                                   |
| ------------ | ---------------------------------------------------------- |
| **Critical** | Hard stop → ESCALATE                                       |
| **High**     | Advisory, highlighted (mitigation or user decision needed) |
| **Low**      | Advisory note (informational)                              |

CWE anchors are topic references carried in each item's text, not a separate axis. Area skills additionally carry published anchors — OWASP Agentic Top 10 (`ASIxx`), OWASP AISVS (`C9.x`), the 2026 joint-agency guidance *Careful Adoption of Agentic AI Services*, NIST SSDF (SP 800-218) — which serve the same role: topic references, looked up rather than judged. MITRE ATLAS is the adversarial-technique taxonomy OWASP maps those entries to.

## Report format (handoff mode — maintained in the handoff; a fresh run replaces the whole section)

```
## Security Review (sec-review · YYYY-MM-DD)
Result: IN PROGRESS (n/4) — becomes PASS or ESCALATE once all 4 areas are complete
- SE: complete — no findings
- NE: complete
  - concern: <text> — <where> — severity: High — CWE: <code or "(operational)">
- CP: pending
- SO: pending
```

Write it after **each area completes**, per the procedure. On a finding in an area marked `complete`, indent its report lines under that area's line. If `ESCALATE`: add one line — `Do not proceed on the affected work. Gather guidance first: <cited reference / user decision needed>.`

On a user-cleared escalation: amend the Result line to `Result: ESCALATE — cleared by user decision (YYYY-MM-DD)` and add a one-line rationale per cleared finding. `PASS` means a completed run with no Critical-severity findings; a cleared escalation stays `ESCALATE — cleared …` so the record of what fired persists.

Direct (non-handoff) runs use the same report-line shape, delivered in the conversation (and to a user-named destination if the user asked for one).

## Notes

- Reviewer subagents load exactly one area skill and read only the target they were given. They must not execute anything in it and must not load any other skill.
- If the user adds scope in their request (e.g. "watch the ssh forward in P1"), treat that as extra context; the checklists still bound what is reported.
- Keep the report short. One sentence per finding. In handoff mode the handoff carries the detail; otherwise the conversation does.
- An interrupted run (token limit, session restart) is picked up as a fresh, **complete** review — all four areas from the top. The in-progress block is a record of what fired — it is not a resume point and never a pass.
- A review never creates its own input. If the only way forward seems to be generating a handoff, a scratch document, or any fixture to review against — stop and ask the user instead.
