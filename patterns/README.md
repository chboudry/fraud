# Fraud typologies

## Variants

Each folder documents one **Variant**: its graph fingerprint, the `pipeline/` blocks it composes, and a reproducible synthetic example.

| Variant | Domain | Folder |
|---------|--------|--------|
| Identity Fraud (synthetic / stolen identity) | Risk & Fraud | [`synthetic-identity`](synthetic-identity/) |
| Account Takeover (ATO) | Risk & Fraud | [`account-takeover`](account-takeover/) |
| Bust-out (build trust, then default) | Risk & Fraud | [`bust-out`](bust-out/) |
| Money mule networks | Risk & Fraud | [`mule-networks`](mule-networks/) |
| Fraud rings | Risk & Fraud | [`fraud-rings`](fraud-rings/) |
| Employee-facilitated dormant-account cash-out | Risk & Fraud | [`internal-fraud`](internal-fraud/) |
| Layering / smurfing / circular flows | Financial Crime / AML | [`money-laundering`](money-laundering/) |

Planned variants and the full taxonomy tables (including other industries) are in [`../foundations/taxonomy.md`](../foundations/taxonomy.md).

## How this maps to the repo

- Each **Variant** = one folder here, documenting the graph fingerprint, the `pipeline/` blocks it composes, and a reproducible synthetic example.
- New variants drop in as sibling folders — no renumbering. Add a row to the table above and a row to the taxonomy tables.
- A variant is always **client-agnostic** and demonstrated on synthetic or public data ([`../pipeline/05-sources/`](../pipeline/05-sources/)); never on named client data.
