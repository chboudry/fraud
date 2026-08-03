# Fraud typologies (taxonomy)

Case studies that *compose* several [`pipeline/`](../pipeline/) blocks to catch a **specific**
fraud. Before listing them, this README fixes the **taxonomy** we use to name them — because
"fraud detection" alone is too coarse to be actionable.

## Why a taxonomy

> For example, in banking, "fraud detection" is too coarse to mean anything actionable on its
> own. What matters is a granular, multi-layer view of the actual problem being addressed:
>
> **Industry = Bank → Domain = Risk & Fraud → Use Case = Customer Fraud → Variant = Identity Fraud**
>
> A thorough taxonomy gives a shared vocabulary, keeps everyone aligned on real needs, and avoids
> treating broad categories as if they were actionable use cases.

## Four levels

| Level | Question it answers | Example |
|-------|---------------------|---------|
| **Industry** | *Who* is the customer? | Bank |
| **Domain** | *Which* business function? | Risk & Fraud |
| **Use Case** | *What* broad problem? | Customer Fraud |
| **Variant** | *Which actionable* pattern? | Identity Fraud |

A **Variant** is the actionable unit: it is what a `patterns/` folder documents, and what a
detection engagement actually delivers. Everything above it is context for alignment.

## Taxonomy for graph fraud (banking-centred)

Banking is the primary industry here, with two fraud-relevant domains. Variants that already have
a folder are linked; the others are natural extensions of the same taxonomy.

### Industry: Banking — Domain: Risk & Fraud

| Use Case | Variant | Folder |
|----------|---------|--------|
| **Customer Fraud** — abuse of a customer's identity or account | Identity Fraud (synthetic / stolen identity) | [`synthetic-identity`](synthetic-identity/) |
| | Account Takeover (ATO) | [`account-takeover`](account-takeover/) |
| | Application Fraud (fabricated data at onboarding) | *planned* |
| **First-Party Fraud** — the customer *is* the fraudster | Bust-out (build trust, then default) | [`bust-out`](bust-out/) |
| | First-payment default / never-pay | *planned* |
| **Payment & Transaction Fraud** — abuse of payment rails | Money mule networks | [`mule-networks`](mule-networks/) |
| | Authorized Push Payment (APP) scams | *planned* |
| | Card-not-present / card fraud | *planned* |
| **Organized Fraud** — collusion structures (cross-cutting) | Fraud rings | [`fraud-rings`](fraud-rings/) |
| **Internal Fraud** — an employee abuses legitimate access | Employee-facilitated dormant-account cash-out | [`internal-fraud`](internal-fraud/) |

### Industry: Banking — Domain: Financial Crime / AML

| Use Case | Variant | Folder |
|----------|---------|--------|
| **Money Laundering** | Layering / smurfing / circular flows | [`money-laundering`](money-laundering/) |
| **Sanctions & Watchlist evasion** | Ownership obfuscation, shell chains | *planned* |
| **Terrorist financing** | Structuring to/from high-risk jurisdictions | *planned* |

## The same taxonomy in other industries

The graph techniques in `pipeline/` are industry-agnostic; only the taxonomy labels change:

| Industry | Domain | Example Use Case → Variant |
|----------|--------|----------------------------|
| Insurance | Risk & Fraud | Claims Fraud → staged-accident / collusion rings |
| E-commerce / Marketplace | Trust & Safety | Account Fraud → fake accounts / seller collusion |
| Telecom | Risk & Fraud | Subscription Fraud → identity fraud / SIM-box rings |
| Public sector | Benefits Integrity | Benefit Fraud → identity fraud / organized rings |
| Crypto / Fintech | Financial Crime | Money Laundering → mixer / layering patterns |

## How this maps to the repo

- Each **Variant** = one folder here, documenting the graph fingerprint, the `pipeline/` blocks it
  composes, and a reproducible synthetic example.
- New variants drop in as sibling folders — no renumbering. Add a row to the tables above and a
  folder below.
- A variant is always **client-agnostic** and demonstrated on synthetic or public data
  ([`../pipeline/05-sources/`](../pipeline/05-sources/)); never on named client data.
