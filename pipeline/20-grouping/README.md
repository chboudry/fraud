# 20 · Grouping

> Pipeline step 20 — group resolved entities into communities. Two regimes, chosen by **what
> you do with the community**.

## Start from the usage

The right grouping depends on your goal, not on the algorithm:

| You want to… | Use | Why |
|--------------|-----|-----|
| Explore / investigate the graph **as it is now** (who is connected to whom, deduplication, over-merge diagnosis, a real-time snapshot) | **Weakly Connected Component (WCC)** | You need the *current* connectivity, time is irrelevant, and you want it computed in one fast pass. |
| **Train a model** (or serve it leak-safely) | **Window Connected Component (window-CC)** | Each dossier must only see its **past** (point-in-time), and windowed features — velocity, acceleration, burstiness — require a **time-bounded** community. |

In one line: **WCC = the graph in its current state; window-CC = the community as it stood at a
past instant, bounded in time.**

- [`weakly-connected-component/`](weakly-connected-component/) — the time-blind community.
- [`windows-connected-component/`](windows-connected-component/) — the time-bounded community
  (upper / lower boundaries).

## WCC vs window-CC

| | Weakly CC | Window-CC |
|---|-----------|-----------|
| Time awareness | none — uses every edge ever seen | bounded to `[T − Δ, T]` for a source scored at `T` |
| Primary use | investigation, dedup, snapshot | model training & leak-safe inference |
| Future leakage | **yes** if used for training (an event inherits structure created by later events) | **no** — the upper bound enforces `date ≤ T` |
| Over-merge behavior | keeps everything glued (one garbage identifier merges thousands) | the lower bound (bridge-cut) can shatter over-merges inside the window |
| Windowed features (velocity, acceleration) | impossible (no window) | native |
| Cost | one cheap pass over the whole graph | per-event / per-cutoff recompute |

## Speed: with vs without GDS

- **WCC → use GDS.** `gds.wcc` runs in-memory, in parallel, in a single pass and labels the
  **whole** graph at once — the natural fit for a static, current-state component. Without GDS,
  a pure Cypher/APOC connectivity pass (iterative label propagation or path expansion) is far
  slower on a large graph.
- **Window-CC → GDS helps little.** GDS has **no dynamic connectivity** (no incremental
  add/remove of edges), so a time-bounded component must be recomputed. Two options:
  1. re-project a subgraph per cutoff and run `gds.wcc` — a projection overhead **per event**;
  2. a **pure Cypher bounded traversal** from the source with date predicates — no projection,
     computes only the source's piece.
  At this scale (largest communities ≈ 5802 / 678 / 416 dossiers) the Cypher traversal runs in
  **milliseconds**, and the pre-materialized `DFS_NEXT` linked list answers the upper bound with
  a **linear scan** — so window-CC does **not** need GDS here.

## Prior work

The `old/` folder holds the point-in-time WCC model (`COMPONENT_PARENT` / `DFS_NEXT` /
`LAST_DFS_NODE_IN_COMP`) and two write-ups referenced throughout the sub-folders:
`old/window_cc_and_bridge_cutting.md` (the concept + solutions) and `old/mode_etude_dfs.md`
(the A–F worked example).
