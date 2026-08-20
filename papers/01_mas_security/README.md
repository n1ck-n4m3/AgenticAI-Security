# MAS security (core set)

This folder is the index for **LLM multi-agent systems** where a concrete security property and an interaction path are part of the mechanism.

Full notes live under [`../notes/`](../notes/). One-line entries and links: [`../CATALOG.md`](../CATALOG.md). 2025-2026 additions are marked with a star in the catalog; rationale: [`../GAP_2025_2026.md`](../GAP_2025_2026.md).

| Sub-area | Dominant contribution | Notes |
|---|---|---|
| Attacks | Threat mechanism | [01-mas-attacks.md](../notes/01-mas-attacks.md) |
| Defenses | Defense, resilience, protocol | [02-mas-defenses.md](../notes/02-mas-defenses.md) |
| Benchmarks | Measurement / evaluation | [03-mas-benchmarks.md](../notes/03-mas-benchmarks.md) |
| Surveys | Map rather than a new attack or defense | [04-surveys.md](../notes/04-surveys.md) |

## How the G-Safeguard family connects

```text
Supervised graph detection     G-Safeguard
Unknown-attack outliers        BlindGuard
Token-level explanation        XG-Guard
Cross-turn reconstruction      GUARDIAN
Structure + correction         Resilience / ResMAS / Byzantine Reliability
Embedding failure              When Embedding-Based Defenses Fail
Decentralized reputation       SentinelNet / Credibility Scoring
Contagion and recovery         Prompt Infection / Cowpox
Control flow, not semantics    Malicious Code / ControlValve
Black-box leakage              MASLeak / Topology Matters
Protocol layer                 A2ASecBench / BlockA2A / SAFEFLOW
Conjunctive / covert channels  Conjunctive / CoMet / Secret Collusion
```
