# 05 · Sources

> Where a chapter's example data comes from. Every example draws on **one of three source
> types**, chosen deliberately per topic.

## Three kinds of source

- **Synthetic** — generated on the fly (fake identifiers, injected fraud). No confidentiality, fully reproducible, no real person involved. Most
  `queries/` examples build their own tiny synthetic graph.
- **Public** — authoritative open reference and watchlist data (identifiers, sanctions, PEPs,
  country/currency codes). Safe to use publicly; see the catalog below.
- **Private** — client data.

## Public reference data

| Dataset | What it is | Official source |
|---------|------------|-----------------|
| `banks-swift` | BIC / SWIFT bank identifier codes (ISO 9362) | [SWIFT — BIC](https://www.swift.com/standards/data-standards/bic-business-identifier-code) |
| `countries-iso2` | ISO 3166‑1 alpha‑2 country codes | [ISO 3166](https://www.iso.org/iso-3166-country-codes.html) |
| `countries-eu-high-risk` | EU list of high‑risk third countries (AML/CFT) | [European Commission](https://finance.ec.europa.eu/financial-crime/anti-money-laundering-and-countering-financing-terrorism-international-level_en) |
| `currencies-iso4217` | ISO 4217 currency codes | [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) |
| `organizations-lei` | Legal Entity Identifiers (LEI) | [GLEIF](https://www.gleif.org/) |
| `persons-pep` | Politically Exposed Persons | [OpenSanctions — PEPs](https://www.opensanctions.org/datasets/peps/) |
| `sanctions-ofac` | OFAC SDN & consolidated sanctions | [OFAC — Sanctions List Service](https://ofac.treasury.gov/sanctions-list-service) |
| `opensanctions` | Consolidated sanctions / PEPs / crime data | [OpenSanctions](https://www.opensanctions.org/) |

## A note on OpenSanctions

[OpenSanctions](https://www.opensanctions.org/) is an excellent hub: it **aggregates and cleans**
many of the sources above (sanctions lists, PEPs, watchlists, company registries) into a single,
well-modeled dataset (FollowTheMoney entities), with strong sourcing and provenance. For public
examples it is often the fastest way to get realistic, high-quality reference entities.

Two things to keep in mind:

- **Licensing**: the bulk data is free for **non-commercial** use (CC BY‑NC); **commercial** use
  requires a paid license.
- **Entity resolution is the paid part**: the raw lists are open, but the **matching /
  entity-resolution service** (the hosted API that reconciles your records against the data — the
  capability most relevant to [`../10-entity-resolution/`](../10-entity-resolution/)) is a
  commercial offering. The self-hostable matcher (`yente`) is open source, but production-grade
  resolution at scale is where the paid tier applies.

So: use OpenSanctions freely to **populate** public examples; treat its **resolution** layer as a
paid capability when comparing entity-resolution approaches.
