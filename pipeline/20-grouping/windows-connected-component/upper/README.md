# Upper bound — leak-safe, point-in-time

> Rebuild the community **as it existed at `date ≤ T`**. This half is proven and essential: it
> is what keeps training and inference free of future leakage.

Keep only information available at `T`. A plain WCC over the full graph would let an event
inherit structure created by **future** events — offline metrics inflate, then collapse in
production. Filtering to `≤ T` is what gives the well-documented lift on temporal fraud graphs.

There are **two ways** to materialize this upper bound. They return the **same** community for
the full-history view; they differ in cost and ergonomics.

## Method 1 — `SAME_CC_AS` / `COMPONENT_PARENT` (chronological union-find forest)

A time-oriented union-find forest: inside each `SIMILARITE` component, dossiers are processed by
ascending date and each new dossier attaches to the **current head** of its community. Every
merge points forward in time, so the head (no outgoing `COMPONENT_PARENT`) is the newest node.

**As-of query**: walk forward and stop at the latest head with `date ≤ D`.

- ➕ Compact; directly encodes the "as-of head"; walk is `O(depth)`.
- ➖ Out-degree ≤ 1, forward-merge only → answers **as-of** and nothing else; it **cannot drop an
  interior member** (removing one could split the component, which a forward forest cannot
  represent). It is a **tree traversal re-expanded on every query**.

**Source**: [halftermeyer/temporal-connected-components-with-neo4j](https://github.com/halftermeyer/temporal-connected-components-with-neo4j)
— the `SAME_CC_AS` relationship and the GDS-batched WCC construction for real-time temporal
WCC queries.

## Method 2 — `DFS_NEXT` linked list (+ `LAST_DFS_NODE_IN_COMP`)

A pre-materialized **linearization** of the component: a DFS from the head over the reversed
forest links consecutively visited nodes into a linked list, and `LAST_DFS_NODE_IN_COMP` marks
the tail of each node's sub-chain — the **bound** that stops a point-in-time walk.

**As-of query**: from dossier `d`, follow `DFS_NEXT` until `LAST(d)`; the visited set is `d`'s
leak-safe community. Optionally filter members by date.

- ➕ A single **linear scan** instead of a repeated tree traversal; pre-materialized → fast
  enumeration; **correct even under branching** for the full-history point-in-time view (the
  marker follows the sub-tree = connectivity, not time).
- ➖ The chain is **not date-monotone across merges** (the `A → B` "jump" in the worked example):
  a naïve date filter on the chain is therefore **wrong for a sliding window** — that problem
  belongs to the lower bound, see [`../upper+lower/`](../upper+lower/). Extra storage; three
  relationships to maintain.

**Source**: [halftermeyer/point-in-time-wcc-neo4j-model](https://github.com/halftermeyer/point-in-time-wcc-neo4j-model)
— `COMPONENT_PARENT` / `DFS_NEXT` / `LAST_DFS_NODE_IN_COMP` for constant-time-per-member
component retrieval. Our runnable demo of this method lives in [`dfs-next/`](dfs-next/).

## Most windowed features need only this bound

A key practical point: **many windowed features do not require the lower (bridge-cut) bound at
all.** Counting the *last X dossiers over time* — `n_7d`, `n_30d`, `n_1y`, and ratios such as
`accel = (n_7d/7) / (n_30d/30)` — is just the leak-safe community (this upper bound) **plus a
date filter in Cypher**. No component recompute, no GDS projection: it is the **most performant**
path and stays exact.

The lower bound is a **different concern** — it is about *shrinking* the community by severing
old connections assumed no longer relevant (a phone number that changed owner, an address left
after a move). That is under study and covered in [`../upper+lower/`](../upper+lower/). If all you
need is recent-activity counts, stop at the upper bound.

## Which to use

Use `DFS_NEXT` for the cumulative "all past" point-in-time community — it is the fast, correct
linear scan. Keep `COMPONENT_PARENT` / `SAME_CC_AS` as the underlying forest that makes the
as-of head resolvable and that the linked list is built from.

The full A–F reproduction (both methods returning the same 1-year table) is in
`../../old/mode_etude_dfs.md` (§3) and the concept in `../../old/window_cc_and_bridge_cutting.md`
(§1.A). A runnable end-to-end demo (ingestion → structure build → walk-forward training →
Streamlit app) is in [`dfs-next/`](dfs-next/).
