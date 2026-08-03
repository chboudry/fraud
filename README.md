# fraud — graph fraud detection: methods & examples

- [`20-grouping`](pipeline/20-grouping/README.md) — WCC vs window-CC, and when to use each.
  - [`weakly-connected-component`](pipeline/20-grouping/weakly-connected-component/README.md) — the graph as it is now.
  - [`windows-connected-component`](pipeline/20-grouping/windows-connected-component/README.md) — time-bounded community.
    - [`upper`](pipeline/20-grouping/windows-connected-component/upper/README.md) — leak-safe upper bound (two methods).
    - [`upper+lower`](pipeline/20-grouping/windows-connected-component/upper+lower/README.md) — adding the bridge-cut lower bound.