# MAS-Security

Reading notes, paper catalog, and working copies for **LLM multi-agent system (MAS) security** — attacks, graph/topology defenses, benchmarks, and self-healing.

This is a research library, not a frozen SoK corpus. Classification follows the MAS scope used by [BrookeYangRui/multiagent_security_corpus](https://github.com/BrookeYangRui/multiagent_security_corpus) (LLM agents + a concrete security property + a material interaction path), then files papers as **attack / defense / benchmark / survey**.

Paper PDFs are **not** in this repository (copyright). Use the catalog links.

## Start here

| File | What it is |
|---|---|
| [papers/CATALOG.md](papers/CATALOG.md) | All papers: venue, one-line summary, official link |
| [papers/GAP_2025_2026.md](papers/GAP_2025_2026.md) | 2025–2026 top-venue papers added after the original 62-paper list |
| [papers/README.md](papers/README.md) | Taxonomy rules |
| [papers/guides/Agentic_AI_Security_Reading_Guide_2024-2026.md](papers/guides/Agentic_AI_Security_Reading_Guide_2024-2026.md) | Longer notes on the original 62 papers |

## Taxonomy

```text
01  MAS security
      attacks / defenses / benchmarks / surveys
02  Adjacent agent security (single-agent PI, tools, jailbreak, backdoor)
03  AI for security (LLM as a security tool)
04  Trustworthy-ML foundations for self-healing (calibration, OOD, BFT, …)
```

A paper goes in **one** primary folder by dominant contribution.

## Code

`code/` keeps **source only** (no checkpoints, no dialogue dumps).

| Tree | Paper | License | Notes |
|---|---|---|---|
| `code/blindguard/` | BlindGuard (ACL 2026) | Apache-2.0 | Official implementation, weights omitted |
| `code/xg-guard/` | XG-Guard (ACL 2026) | See `NOTICE.md` | Third-party snapshot; datasets omitted |

Upstream papers: [BlindGuard](https://aclanthology.org/2026.acl-long.1819/), [XG-Guard](https://aclanthology.org/2026.acl-long.1407/).

## What this repo is not

- Not meeting notes, advisor correspondence, or unpublished research proposals.
- Not a copy of the USENIX 2027 SoK evidence ledger.
- Not a dump of copyrighted PDFs.

## Acknowledgements

Literature coverage for 2025–2026 MAS papers was checked against [multiagent_security_corpus](https://github.com/BrookeYangRui/multiagent_security_corpus) (cutoff 2026-07-01).
