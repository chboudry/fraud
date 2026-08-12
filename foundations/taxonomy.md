# Fraud taxonomy

> How we name fraud problems, because "fraud detection" alone is too coarse to be actionable. This page fixes the vocabulary; [`../patterns/`](../patterns/) documents each actionable variant as a case study.

## Why a taxonomy

> For example, in banking, "fraud detection" is too coarse to mean anything actionable on its own. What matters is a granular, multi-layer view of the actual problem being addressed:
>
> **Industry = Bank → Domain = Risk & Fraud → Use Case = Customer Fraud → Variant = Identity Fraud**
>
> A thorough taxonomy gives a shared vocabulary, keeps everyone aligned on real needs, and avoids treating broad categories as if they were actionable use cases.

## Four levels

| Level | Question it answers | Example |
|-------|---------------------|---------|
| **Industry** | *Who* is the customer? | Bank |
| **Domain** | *Which* business function? | Risk & Fraud |
| **Use Case** | *What* broad problem? | Customer Fraud |
| **Variant** | *Which actionable* pattern? | Identity Fraud |

A **Variant** is the actionable unit: it is what a [`../patterns/`](../patterns/) folder documents, and what a detection engagement actually delivers. Everything above it is context for alignment.

## Taxonomy for graph fraud (banking-centred)

Banking is the primary industry here, with two fraud-relevant domains. Variants that already have a folder are linked; the others are natural extensions of the same taxonomy.

### Industry: Banking — Domain: Risk & Fraud

| Use Case | Variant | Folder |
|----------|---------|--------|
| **Customer Fraud** — abuse of a customer's identity or account | Identity Fraud (synthetic / stolen identity) | [`synthetic-identity`](../patterns/synthetic-identity/) |
| | Account Takeover (ATO) | [`account-takeover`](../patterns/account-takeover/) |
| | Application Fraud (fabricated data at onboarding) | *planned* |
| **First-Party Fraud** — the customer *is* the fraudster | Bust-out (build trust, then default) | [`bust-out`](../patterns/bust-out/) |
| | First-payment default / never-pay | *planned* |
| **Payment & Transaction Fraud** — abuse of payment rails | Money mule networks | [`mule-networks`](../patterns/mule-networks/) |
| | Authorized Push Payment (APP) scams | *planned* |
| | Card-not-present / card fraud | *planned* |
| **Organized Fraud** — collusion structures (cross-cutting) | Fraud rings | [`fraud-rings`](../patterns/fraud-rings/) |
| **Internal Fraud** — an employee abuses legitimate access | Employee-facilitated dormant-account cash-out | [`internal-fraud`](../patterns/internal-fraud/) |

### Industry: Banking — Domain: Financial Crime / AML

| Use Case | Variant | Folder |
|----------|---------|--------|
| **Money Laundering** | Layering / smurfing / circular flows | [`money-laundering`](../patterns/money-laundering/) |
| **Sanctions & Watchlist evasion** | Ownership obfuscation, shell chains | *planned* |
| **Terrorist financing** | Structuring to/from high-risk jurisdictions | *planned* |

## The same taxonomy in other industries

The graph techniques in [`../pipeline/`](../pipeline/) are industry-agnostic; only the taxonomy labels change:

| Industry | Domain | Example Use Case → Variant |
|----------|--------|----------------------------|
| Insurance | Risk & Fraud | Claims Fraud → staged-accident / collusion rings |
| E-commerce / Marketplace | Trust & Safety | Account Fraud → fake accounts / seller collusion |
| Telecom | Risk & Fraud | Subscription Fraud → identity fraud / SIM-box rings |
| Public sector | Benefits Integrity | Benefit Fraud → identity fraud / organized rings |
| Crypto / Fintech | Financial Crime | Money Laundering → mixer / layering patterns |
