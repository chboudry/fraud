# Weakly Connected Component (WCC)

> The community in the graph's **current state** — time-blind connectivity. Best when you use
> the graph *as it is now*.

## Definition

On the undirected `SIMILARITE` graph, a WCC is a **maximal set of dossiers mutually reachable**
ignoring edge direction. Two dossiers are in the same WCC if a chain of shared identifiers
connects them — regardless of *when* those links appeared.

## When to use it

- **Investigation / exploration**: given a dossier, show everyone connected to it right now.
- **Deduplication & entity clustering**: the raw grouping that entity resolution (`10`) feeds.
- **Over-merge diagnosis**: WCC sizes reveal suspicious giant components (a single garbage
  identifier — a default phone/IP/device — can glue thousands of dossiers together).
- **Real-time snapshot**: the current shape of a ring for an analyst.

It is the wrong tool for **training**: because it uses every edge ever seen, a past event
inherits structure created by **future** events → future leakage. For that, use
[`../windows-connected-component/`](../windows-connected-component/).

## Computation & speed

- **With GDS (recommended)**: `gds.wcc` projects the `SIMILARITE` graph in memory and labels
  every node in one parallel pass. Fast and one-shot for the whole graph.
- **Without GDS**: a Cypher/APOC connectivity pass (iterative label propagation or repeated
  path expansion) works but is markedly slower at scale.

## Pros / cons

**Pros**

- Simple, single-pass, labels the whole graph at once.
- GDS-accelerated; trivial at this scale.
- Ideal for a current-state, human-facing view.

**Cons**

- **Time-blind** → future leakage if used for model training.
- Prone to **over-merge**: one hub / garbage identifier merges unrelated dossiers (see the 5802
  community note in `../old/window_cc_and_bridge_cutting.md`). Fix by blacklisting the identifier
  (`10-entity-resolution`) or by windowing (window-CC).
- No windowed features (velocity, acceleration, burstiness) — there is no window.
