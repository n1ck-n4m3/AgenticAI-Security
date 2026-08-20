# MAS benchmarks and measurement

Main contribution is a **benchmark, protocol, or measurement framework**, even when the paper also ships an attack suite.

## ASB

**Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents.** ICLR 2025. [OpenReview](https://openreview.net/forum?id=V4y0CpX4hK)

- **Problem:** Tool-using agents have several distinct injection points (user text, tool output, memory, planning templates). Prior work mixed them without a shared formalization or a utility-aware metric.
- **Method:** ASB is primarily a **single-agent** execution-chain benchmark, not a full MAS. It formalizes attack success as inducing a malicious action `a_m` under a contaminated context. Ten application scenarios, ten agents, thirteen LLMs; 50 clean tasks, 20 clean tools, 400 attack task/tool pairs. Five attacks: Direct PI, Indirect PI, Memory Poisoning, Plan-of-Thought backdoor, Mixed. Defenses include delimiters, rewriting, safety reminders, sandwich, perplexity, and LLM detectors. Metrics: ASR, performance with no attack (PNA), and net resilience (NRP) so "an agent that never uses tools" is not rewarded.
- **Result:** Mixed ~84% ASR, DPI ~73%, PoT backdoor ~42%, IPI ~28%, memory poisoning ~8% (often a retrieval miss, not recognition). Stronger models are not automatically safer: they may complete the malicious tool use more competently. Existing prompt-level defenses are limited and hurt PNA.
- **Takeaway:** Canonical map of agent attack surfaces. G-Safeguard-family PI/TA/MA settings draw from this taxonomy. ASB does not measure cross-agent spread.

## NetSafe

**NetSafe: Exploring the Topological Safety of Multi-agent Systems.** ACL 2025 Findings. [ACL](https://aclanthology.org/2025.findings-acl.150/)

- **Problem:** The same malicious agent can be harmless in one wiring and catastrophic in another. Topology was rarely the independent variable.
- **Method:** Fix the attack and vary the communication graph (density, degree, hierarchy). Measure how errors and malice propagate. The headline qualitative result is that denser graphs amplify faults.
- **Result:** Topological safety is real: connectivity that looks good for collaboration is often bad for containment. Hub and dense patterns spread errors farther than sparse hierarchies (aligns with Resilience's later structural findings).
- **Takeaway:** Always report worst-topology, not only average ASR. Defense papers that freeze one graph over-claim.

## Agentic Robustness

**On the Robustness of Agentic Systems to Adversarially Induced Harm.** COLM 2025. [arXiv](https://arxiv.org/abs/2508.16481)

- **Problem:** Chat jailbreak rates do not equal harm in an agent that can act. The paper measures robustness of agentic systems to adversarially induced harm, not just toxic text.
- **Method:** Agents are placed in settings where success is a harmful action (or a blocked harmful action). Attacks try to induce that harm; defenses and system structure are compared on harm versus task utility.
- **Result:** Systems that look aligned in chat still take harmful actions under adversarial tasks. Robustness depends on tool policy and organization, not only the base model.
- **Takeaway:** Evaluation target is induced harm, which is the right MAS-adjacent metric for action-taking systems.

## MAGPIE

**MAGPIE: Multi-Agent Contextual Privacy Evaluation.** NeurIPS 2025 Workshop. [arXiv](https://arxiv.org/abs/2506.20737)

- **Problem:** Privacy tests that look at one agent's reply miss leaks that appear only when several agents share context.
- **Method:** MAGPIE is a contextual privacy benchmark for multi-agent settings: secrets are distributed, and the question is whether the system reveals them through collaboration.
- **Result:** Contextual, compositional leaks occur in collaborative agents even when single-turn privacy looks acceptable (same theme as The Sum Leaks More).
- **Takeaway:** Privacy measurement for MAS must be multi-party. Workshop-scale, but it fills a hole in ASB/TAMAS which are more attack-success oriented.

## Who's the Mole

**Who's the Mole: Detecting Intention-Hiding Malicious Agents.** arXiv 2025. [arXiv](https://arxiv.org/abs/2507.04724)

- **Problem:** Malicious agents that hide intent (play along, then defect) are harder than agents that jailbreak on turn one. Benchmarks that only use loud attacks overstate detector performance.
- **Method:** The paper constructs intention-hiding moles and measures detection: how long the mole can blend in, and which signals (inconsistency over time, vote patterns) expose it.
- **Result:** Intention-hiding agents evade detectors tuned on explicit PI. Time and cross-agent inconsistency matter more than a single toxic sentence.
- **Takeaway:** Mole-style evaluation is a necessary complement to ASB-style explicit attacks.

## Free-MAD

**Free-MAD: Consensus-Free Multi-Agent Debate.** ACL Findings. [arXiv](https://arxiv.org/abs/2509.11035)

- **Problem:** Multi-agent debate often forces consensus, which can amplify a confident wrong (or attacked) position. Security-relevant reading: consensus rules are an integrity mechanism.
- **Method:** Free-MAD studies debate **without** forcing consensus: agents may retain dissent. The paper measures accuracy and, implicitly, resistance to steamrolling.
- **Result:** Consensus-free debate changes how errors propagate compared with must-agree protocols; it is a measurement of aggregation rules, not a GAD bench.
- **Takeaway:** Decision protocol is part of the security evaluation, alongside topology (NetSafe) and planner-executor split (PEAR).

## TAMAS

**TAMAS: Benchmarking Adversarial Risks in Multi-Agent LLM Systems.** ACL 2026. [ACL](https://aclanthology.org/2026.acl-long.1442/)

- **Problem:** ASB is single-agent. Deployed MAS use frameworks such as AutoGen and CrewAI, with different attack surfaces (peer messages, shared memory, role templates). There was no unified adversarial-risk exam for those stacks.
- **Method:** TAMAS attacks multiple surfaces on multi-agent frameworks and reports an **ERS**-style (empirical risk) aggregate so papers can compare systems, models, and defenses on one leaderboard-like protocol.
- **Result:** Risk varies sharply by framework, model, and attack surface. A defense that helps on one framework does not automatically transfer. This is the MAS-native counterpart to ASB.
- **Takeaway:** Use TAMAS (MAS) and ASB (single-agent chain) together. Do not quote G-Safeguard numbers as a TAMAS result.

## A2ASecBench

**A2ASecBench: Protocol-Aware Security Benchmarking for Agent-to-Agent Communication.** ICLR 2026. [OpenReview](https://openreview.net/pdf?id=LfdFnakqGJ)

- **Problem:** Dialogue-graph GAD benches do not capture **protocol** attacks (identity, routing, capability tokens) in Agent-to-Agent stacks.
- **Method:** Six protocol-aware A2A attacks, jointly scored with utility so a system that refuses all calls does not win. Emphasis is the A2A layer, not utterance embeddings.
- **Result:** Protocol attacks succeed against stacks that look fine on ASB-style PI. Utility-aware scoring is part of the protocol.
- **Takeaway:** If the system speaks A2A / MCP-like protocols, this bench is the relevant one; BlockA2A and SAFEFLOW are the matching defenses.

## PEAR

**PEAR: Planner-Executor Adversarial Robustness.** EACL 2026 Findings. [arXiv](https://arxiv.org/abs/2510.07505)

- **Problem:** Many agents split planner and executor. Attacks can target the plan, the execution, or the interface between them. End-to-end ASR hides where it broke.
- **Method:** PEAR is a robustness benchmark for planner-executor architectures: attacks and metrics are factored across the two roles.
- **Result:** Planner poisoning and executor hijack are not the same failure. Some defenses protect one role and leave the other open.
- **Takeaway:** Factor evaluation by architecture. Related to Control-Flow Hijacking (who is allowed to call whom).

## Topology Matters

**Topology Matters: How Communication Structure Changes Memory Leakage in MAS.** ACL 2026 Findings. [arXiv](https://arxiv.org/abs/2512.04668)

- **Problem:** Memory leakage (MASLeak-adjacent) is usually reported as a model or prompt issue. Topology may dominate.
- **Method:** The paper holds the leakage task fixed and varies communication topology, measuring how much private memory reaches the user-visible output.
- **Result:** Leakage rates change with topology: hubs and dense graphs leak more because more agents see the secret. Sparse or need-to-know graphs leak less.
- **Takeaway:** Confidentiality controls include graph cut, not only output filters. Cite next to MASLeak and NetSafe.

## LieCraft

**LieCraft: Evaluating Deceptive Capability of Language Models in Agent Settings.** AAAI 2026. [arXiv](https://arxiv.org/abs/2603.06874)

- **Problem:** Jailbreak ASR does not measure whether a model can **strategically deceive** peers or monitors (hold a cover story, lie only when needed).
- **Method:** LieCraft is an evaluation of deceptive capability: tasks where success requires lying or concealing intent in an agent/multi-agent setting.
- **Result:** Deceptive capability is measurable and is not identical to generic helpfulness or generic jailbreak success.
- **Takeaway:** Needed context for Secret Collusion, Lying with Truths, and Who's the Mole: those attacks assume some deceptive skill.
