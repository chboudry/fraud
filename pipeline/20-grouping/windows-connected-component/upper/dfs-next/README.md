# DFS_NEXT — runnable demo (point-in-time WCC)

> End-to-end demo of the **upper-bound** (leak-safe) community via the pre-materialized temporal
> structure `COMPONENT_PARENT` / `DFS_NEXT` / `LAST_DFS_NODE_IN_COMP`.
>
> Method source: [halftermeyer/point-in-time-wcc-neo4j-model](https://github.com/halftermeyer/point-in-time-wcc-neo4j-model).

## The idea in one paragraph

Two `Dossier` nodes that share an identifier are linked by `SIMILARITE`. On top of that graph we
materialize three relationships so time-travel queries are cheap:

1. **`COMPONENT_PARENT`** (old → new) — a time-oriented union-find forest; the head (no outgoing
   edge) is the newest member.
2. **`DFS_NEXT`** (head → all members) — a pre-materialized linked list of a component's members,
   so *enumerate the community* is a single linear scan instead of a repeated graph search.
3. **`LAST_DFS_NODE_IN_COMP`** — the tail marker that **bounds** the walk: starting at dossier `d`
   and following `DFS_NEXT` up to `LAST(d)` reconstructs the community exactly as it stood on
   `d`'s date — no future members leak in.

This yields component retrieval **as of any date** (or as of now) in single-digit milliseconds,
with no WCC recomputation.

## Demo contents

| File | Role |
|------|------|
| `01_setup_ingestion.ipynb` | Generate & ingest synthetic `Dossier` + identifiers (demo data only). |
| `02_build_relations.ipynb` | Build `SIMILARITE`, then `COMPONENT_PARENT` / `DFS_NEXT` / `LAST_DFS_NODE_IN_COMP`. |
| `03_training_walkforward.ipynb` | Point-in-time features + walk-forward training / learning curves. |
| `04_streamlit.ipynb` | Notebook wrapper to launch the app. |
| `credit_fraud_app.py` | Streamlit app: pick a dossier, see its community **before / at / after** its date. |
| `demopit_verification.ipynb` | Verifies the point-in-time reconstruction on the A–F example. |

## Prerequisites

- A running **Neo4j** instance with the **GDS** (Graph Data Science) library.
- A database (the notebooks default to `fraudwcctemporal`); update the
  `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` constants at the top of each file.
- Python 3.10+.

## Run

Notebooks in order: `01_setup_ingestion` → `02_build_relations` → `03_training_walkforward`.
Then the app:

```bash
pip install streamlit streamlit-agraph
streamlit run credit_fraud_app.py
```

## Scope

This demo covers the **upper bound only** (leak-safe, all-past point-in-time). Adding the
**lower** bound (bridge-cut, sliding window) is covered in
[`../../upper+lower/`](../../upper+lower/) — where `DFS_NEXT` alone is shown to be insufficient
under branching.
