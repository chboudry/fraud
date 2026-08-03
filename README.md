# fraud — graph fraud detection: methods & examples

- [`patterns`](patterns/README.md) — fraud typology taxonomy (Industry → Domain → Use Case → Variant).
- [`05-sources`](pipeline/05-sources/README.md) — data sources: synthetic / public / private.
- [`20-grouping`](pipeline/20-grouping/README.md) — WCC vs window-CC, and when to use each.
  - [`weakly-connected-component`](pipeline/20-grouping/weakly-connected-component/README.md) — the graph as it is now.
  - [`windows-connected-component`](pipeline/20-grouping/windows-connected-component/README.md) — time-bounded community.
    - [`upper`](pipeline/20-grouping/windows-connected-component/upper/README.md) — leak-safe upper bound (two methods).
    - [`upper+lower`](pipeline/20-grouping/windows-connected-component/upper+lower/README.md) — adding the bridge-cut lower bound.