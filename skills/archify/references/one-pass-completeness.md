# One-pass completeness (local extension, 2026-10-12)

> Local addition to the upstream skill package. It exists because a whole-system request
> was answered with a single shallow `architecture` overview and then needed three follow-up
> conversations (deeper architecture, then sequence/dataflow/lifecycle) before it was useful.
> Read this before choosing scope for any repository or system-level request.

## 1. Scope trigger

A repository or system-level request — "draw this project's architecture", "explain how this
system works end to end", "map the runtime" — with no explicit narrowing means **the system's
full runtime surface delivered as a view set**, not one overview diagram.

Only when the user names a narrow target ("just the retry path", "only the deployment
topology", "one sequence diagram for login") do you author exactly that.

## 2. Default view set

Include every view that the source actually supports. Do not invent a view the code does not
have; do not omit one it does.

| View | Author it when | Coverage expectation |
|---|---|---|
| `architecture` ×1 | always | Full runtime surface (see §3), not only the main journey |
| `sequence` | there is an HTTP/RPC/CLI request chain or an async trace | Split by the sync/async boundary when the limits in §4 are exceeded |
| `dataflow` | there is a real pipeline: ingestion, indexing, ETL, event fan-out, retrieval | One dataflow per pipeline; do not compress two pipelines into one canvas |
| `lifecycle` | the domain has status enums, gates, retries, TTLs, or terminal states | The real enum values and every transition that code writes |
| `workflow` | there is an approval gate, runbook, or CI/CD process the reader asked about | Optional; skip when the repo has none |

A view set is several diagrams in **several folders**, each finalized on its own. That is
expected output for one request, not a follow-up request.

## 3. Coverage checklist (must all be answerable "yes" before writing)

1. **Processes and entry points** — every server, worker, CLI, scheduler, and migration entry.
2. **Background and async work** — queues/streams, outbox relays, consumers, retention and
   timeout sweeps, startup recovery. These are runtime components; they belong on the canvas.
3. **Every durable store** — owned by the code that actually reads or writes it, with the
   read path and the write path distinguished.
4. **Every external system** — model providers, search providers, vector stores, object
   stores, tracing backends, with the protocol/endpoint the code uses.
5. **Cross-cutting layers that change behavior** — middleware chain, auth/token model,
   rate limiting, idempotency, dynamic configuration, observability and cost accounting.
6. **Failure paths** — degrade, fallback, retry, dead-letter, cancel, timeout/TTL.
7. **State and control gates** — where status is written, who may write it, what blocks it.
8. **Configuration source** — where defaults live and whether they reload at runtime.

Anything deliberately left out must be named as out of scope in a card **and** in the reply.
Never demote a real runtime component or relationship into a card to save space: cards answer
extra reader questions, they do not carry required topology. Detail that does not fit one
canvas is a signal to author another view, not to delete the fact.

## 4. Capacity limits (measured; plan the split before authoring)

| Mode | Hard limit | Consequence |
|---|---|---|
| `sequence` | Adjacent messages sharing horizontal space need **≥28px** of `y`. The desktop readability budget is **930px** of diagram width at 1440×900, and 10 participants require a viewBox ≥1117 (projected text 5.81px < 6px floor). | Plan **≤8 participants** and **≤22 messages** per canvas. Split on the sync/async boundary; move mode variants (resume modes, cancel paths) into cards. |
| `dataflow` | `stages` 2..5 but the automatic canvas is **940px** wide while 5 stages demand ≥1068; `row` is limited to **0..4**. | With no explicit viewBox use **≤4 stages**. Declaring a wide `viewBox` drops you to the legacy 930px budget and fails readability — compress columns instead. |
| `lifecycle` | Schema v2; lanes 1..4 (`main` first, `terminal` last); `col` **0..4**. | Place an exit or interruption in the column of the state it leaves. Do not invent an intermediate state for "resumed": a resume returns to the existing state and the back-transition runs vertically. |
| `architecture` | The canvas is measured from authored coordinates; an explicit `meta.viewBox` re-applies the legacy 930px budget. | Author within ~1070px (6 columns of ~105px with ~85–100px labeled gaps). Main-path labeled edges need `6.5px × ASCII units + 21px` clear gap; CJK counts two units. |
| all modes | Hub nodes (one database, one broker) with many owners produce crossings. | Prefer fewer, stronger edges plus a card for secondary reads/writes; each additional hub edge costs a corridor. |

Routing repair rules that were actually needed: align same-row nodes with `yOffset` when a 7px
jog appears (`composition/micro-segment`), give two same-source fan-outs different corridors or
`labelDy` (`composition/ambiguous-corridor`), and move a label off its own source node with
`labelDy` (`layout/constraint: label overlaps node`).

## 5. Evidence first, then one write

- Verify every cited `path:line` **exists at the pinned revision before writing the candidate**.
  The validator rejects out-of-range citations (`repository-evidence/line-out-of-range`) and
  reports the file's real length; a candidate with one bad citation never reaches the gates.
- Never trust line numbers that came from a summary, a plan, or another agent. Re-read the
  exact range you cite; sub-agent line numbers were wrong in practice (a repository file was
  cited at line 206 while the file had 83 lines, and the real code lived in a different module).
- Cite the narrowed claim, not the file: protocol, retry, and persistence facts each need the
  line that shows them.

## 6. Environment and evidence hygiene

- **Injected Node loaders**: if `finalize` fails with a `…hardlinked` / link-count error while
  the diagram is untouched, an injected loader (`NODE_OPTIONS`, e.g. an IDE-provided
  `node-language-shim.cjs`) is breaking the atomic-write check. Clear it for the command's
  process (PowerShell: `$env:NODE_OPTIONS=''`) and rerun.
- **Evidence ownership**: after a repair or a re-publish, `browser-check` refuses to overwrite
  a receipt it cannot attribute to the current artifact. Move the previous `<stem>.*.json`
  receipts into `published-r1/` or `review-N/` inside the diagram folder before running at the
  canonical `meta.output` path. Keep them; they are the audit trail.
- **Report per view**: artifact path, gate summary, browser-evidence status, and any residual
  `visualReviewRecommendation` signals, per diagram.
