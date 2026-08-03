# Window Connected Component (window-CC)

> The community **as it stood at a past instant**, bounded in time. The grouping used for
> **model training** and leak-safe inference.

When we score a dossier at instant `T`, its community should be bounded by **two** time
boundaries, not one:

```
                 back boundary                     front boundary
                 (lower bound)                     (upper bound)
   ────────────────┃──────────── window ────────────┃────────────▶ time
                 T − Δ                               T
                          (Δ = e.g. 6 months)
```

The set of dossiers connected to the source **using only nodes/edges inside `[T − Δ, T]`** is a
*window connected component*. The two boundaries play very different roles and are documented
separately:

| Boundary | Predicate | Status | Detailed in |
|----------|-----------|--------|-------------|
| **Upper** (front, leak-safe) | `date ≤ T` | proven, essential | [`upper/`](upper/) |
| **Lower** (back, bridge-cut) | `date ≥ T − Δ` | business-motivated, not independently proven | [`upper+lower/`](upper+lower/) |

## What each boundary is for

The two boundaries answer different questions:

- The **upper** bound is about **correctness**: never let a dossier see structure created after
  `T` (no future leakage). It is proven and always required.
- The **lower** bound is about **shrinking the community**. The hypothesis is that some **old
  connections are no longer relevant** and should not be counted — for example a **phone number
  that changed owner**, or an **address left behind after a move**. Cutting links that survive
  only through out-of-window nodes removes that stale glue.

The lower bound is **still under study**, and it is only *one* way to encode "keep the recent,
still-relevant community". Other approaches could serve the same intent, e.g. **quantifying the
graph** — tracking centrality / degree growth to flag a community that turns *tentacular* (a sign
of over-merge rather than a real ring) — or **temporal clustering** (re-clustering the community
over time, e.g. Leiden, and keeping the source's current cluster).

> **You often don't need the lower bound.** Counting the *last X dossiers over time* (`n_7d`,
> `n_30d`, `n_1y`, and ratios such as `accel = (n_7d/7) / (n_30d/30)`) needs only the **upper**
> bound **+ a date filter in Cypher** — which is **more performant** than recomputing a
> bridge-cut component. Reserve the lower bound for when you specifically want to **sever** stale
> connectivity, not merely to count recent activity.

## Why window-CC for training

- **Leak-safety**: the upper bound guarantees a dossier never sees structure created after `T`,
  so offline metrics don't inflate and then collapse in production.
- **Windowed features**: velocity, burstiness and acceleration
  (`accel = (n_7d / 7) / (n_30d / 30)`) only make sense on a **time-bounded** community — hence
  the tight coupling with `30-features`.

## How to read this folder

1. [`upper/`](upper/) — the leak-safe upper bound, and its **two implementations**
   (`SAME_CC_AS` / `COMPONENT_PARENT` walk vs the `DFS_NEXT` linked list) with trade-offs.
2. [`upper+lower/`](upper+lower/) — adding the **bridge-cut** lower bound, and why neither
   linked-list shortcut works under a merge (the windowed `SIMILARITE` traversal is required).

Full background and the A–F worked example live in `../old/window_cc_and_bridge_cutting.md` and
`../old/mode_etude_dfs.md`.

## References

The window-CC object and the leak-safety / bridge-cutting arguments draw on:

- Ma et al., **Efficient Algorithms for Temporal Connected Components** — [SIGMOD 2023](https://chenhao-ma.github.io/papers/SIGMOD23temporalCC.pdf): window-CC is defined and optimized for query efficiency.
- **Temporal connected components**, [VLDB Journal 2026](https://dl.acm.org/doi/10.1007/s00778-026-00977-5): maintainable indices for window-CC queries.
- ["No Peeking Ahead" — Time-aware graph fraud detection (Towards Data Science)](https://towardsdatascience.com/no-peeking-ahead-time-aware-graph-fraud-detection/): filtering to `≤ t` yields ~2–3× lift on top deciles; the leaky variant inflates scores.
- ["Leakage-Safe Graph Features…" (arXiv 2603.06632)](https://arxiv.org/pdf/2603.06632): structural features on the historical subgraph `G≤t`, ROC-AUC ≈ 0.85 on Elliptic under a strict temporal split.
- [ATLAS, Capital One (arXiv 2509.20339)](https://arxiv.org/pdf/2509.20339): serve-time non-anticipative connectivity in production (+6.38% AUC, −50% friction); its ablation shows **larger** windows are better — no support for aggressive cutting.
- [Neo4j — Mastering fraud detection with a temporal graph](https://neo4j.com/blog/developer/mastering-fraud-detection-temporal-graph/): the `SAME_CC_AS` forest this model builds on.
- [Credit-fraud temporal features study](https://scipublication.com/index.php/AIMLR/article/download/209/192): transaction **velocity** is the single most predictive temporal feature (~28.4% of temporal performance) — and computing it needs a well-defined windowed community.
