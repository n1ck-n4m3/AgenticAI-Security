# Surveys and SoKs

Maps of the area rather than a new attack or defense. MAS-primary notes in this library follow the interaction-security scope used by [multiagent_security_corpus](https://github.com/BrookeYangRui/multiagent_security_corpus) (literature cutoff 2026-07-01): LLM agents, a concrete security property, and a material interaction path. These surveys are broader comparators.

## Agents Under Threat

**AI Agents Under Threat: A Survey of the Safety and Security Landscape.** ACM Computing Surveys. [arXiv](https://arxiv.org/abs/2406.02630)

- **Problem:** "Agent security" exploded across jailbreaks, tools, memory, and multi-agent papers with no shared map. New work needed a vocabulary for threats versus the chatbot literature.
- **Method:** A survey of challenges for LLM agents: prompt injection, tool misuse, memory, multi-agent interaction, and defenses then available. Coverage is **single-agent-heavy**; MAS is one chapter rather than the denominator.
- **Result:** The value is the taxonomy and the bibliography, not a new detector. It is the CSUR-level snapshot of agent risk as the field professionalized.
- **Takeaway:** Use it as a comparator map. Do not treat its single-agent emphasis as a MAS-primary evidence set.

## TRiSM

**TRiSM for Agentic AI: Trust, Risk, and Security Management in Multi-Agent Systems.** AI Open 2026. [arXiv](https://arxiv.org/abs/2506.04133)

- **Problem:** Security papers optimize ASR. Operators need a management frame: trust, risk, and security as ongoing processes over agentic MAS.
- **Method:** Survey organized around TRiSM (trust / risk / security management): how to identify assets, threats, controls, and governance for agentic systems, with MAS in scope.
- **Result:** A management-oriented synthesis rather than a leaderboard. Useful for positioning runtime monitors, identity, and audit.
- **Takeaway:** Complements GAD papers: they are controls inside a TRiSM program, not the program itself.

## Agentic AI SoK

**SoK: Attack and Defense Landscape of Agentic AI.** USENIX Security 2026. [USENIX](https://www.usenix.org/conference/usenixsecurity26/presentation/kim-juhee-agentic)

- **Problem:** Agentic systems compose models, tools, memory, planners, and other agents. Attacks and defenses attach to **components**, but papers often claim system-level security from one component.
- **Method:** A systemization of knowledge: component-centric attack and defense landscape for agentic AI. MAS interaction is one slice next to tools, memory, and planners.
- **Result:** The SoK's contribution is the landscape and the gaps (what is evaluated versus what is deployed), not a new GNN.
- **Takeaway:** Best security-venue map for "agentic" as an architecture. Pair with the MAS-interaction corpus for the multi-agent slice, rather than treating the SoK as MAS-only.
