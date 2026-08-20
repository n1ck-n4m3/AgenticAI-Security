# MAS defenses

Defenses whose intervention sits on the **interaction graph, reputation, pruning, protocol, consensus, or system structure**. Single-agent injection guards are in [05-prompt-injection.md](05-prompt-injection.md).

## G-Safeguard

**G-Safeguard: A Topology-Guided Security Lens and Treatment on LLM-based Multi-agent Systems.** ACL 2025. [ACL](https://aclanthology.org/2025.acl-long.359/)

- **Problem:** Attacks on MAS travel along communication edges. Per-utterance filters ignore who influences whom. The paper asks how to detect compromised agents using the dialogue graph and then cut the edges that carry the attack.
- **Method:** Multi-agent dialogue is built as a directed graph: nodes are agents, edges carry utterance histories. An edge-aware GNN is trained with **labeled attacks** (prompt injection, tool attack, memory attack in the ASB family). The model outputs an attack probability per agent. Treatment is isolation / edge pruning so the detected attacker cannot keep broadcasting.
- **Result:** Supervised graph detection is strong when the test attack matches the training labels. The method is the backbone later papers (BlindGuard, XG-Guard) compare against. It does not claim unknown-attack detection.
- **Takeaway:** Topology-aware GNN plus prune is the canonical supervised MAS defense. The gap is label dependence and the assumption that attacks look like the training families.

## Credibility Scoring

**An Adversary-Resistant Multi-Agent LLM System via Credibility Scoring.** AACL / IJCNLP 2025. [ACL](https://aclanthology.org/2025.ijcnlp-long.90/)

- **Problem:** Hard isolation of a suspected agent throws away utility if the detector is wrong. Soft down-weighting may be enough.
- **Method:** Each agent receives a credibility score from its behavior. Downstream aggregation (votes, merged answers) weights high-credibility agents more and low-credibility ones less, without necessarily deleting them from the graph.
- **Result:** Credibility-weighted aggregation reduces the impact of adversarial agents relative to unweighted debate, with less utility damage than always dropping a node.
- **Takeaway:** Reputation is a continuous intervention. It is a cousin of Byzantine weighted aggregation (see Byzantine Reliability).

## AgentPrune

**Cut the Crap: An Economical Communication Pipeline for LLM-based Multi-Agent Systems.** ICLR 2025. [OpenReview](https://openreview.net/forum?id=LkzuPorQ5L)

- **Problem:** MAS pay for every message. Dense graphs are expensive and, as NetSafe later emphasizes, can also amplify errors.
- **Method:** AgentPrune learns or selects a sparser communication pipeline so that task performance stays high while message count drops. It is primarily an efficiency paper; the security reading is that pruning changes the attack surface.
- **Result:** Substantial communication reduction with small task-performance loss on the authors' collaboration benchmarks.
- **Takeaway:** Topology surgery is dual-use: it can cut cost and cut attack edges, but the pruning objective here is not an adversarial loss. Pair it with a security-aware pruner (G-Safeguard, SafeSieve, TopoSHIELD).

## Resilience

**On the Resilience of LLM-Based Multi-Agent Collaboration with Faulty Agents.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/huang25ay.html)

- **Problem:** What organizational structure still works when some agents are faulty, and can other agents correct bad messages without a trained detector?
- **Method:** No GNN is trained. The paper compares topologies (hierarchical, flat, linear) under injected faulty agents. Two prompt-level mechanisms: **Challenger** (peers question suspicious messages) and **Inspector** (a dedicated agent rewrites or checks content). Faults include wrong answers and, in code settings, damaging edits.
- **Result:** Hierarchical organization degrades less under a single fault (on the order of 5.5 points) than flat (~10.5) or linear (~23.7). Code tasks are hit hardest (~22.6). Challenger plus Inspector can recover a large fraction of the loss in some self-collaboration settings (the paper reports recovering most of a 96% loss slice in one setting). Experiments are mostly single-fault and synthetic.
- **Takeaway:** Structure is a defense. This line continues in ResMAS (search topology) and is orthogonal to embedding GAD. Recovery here is rewrite, not checkpoint rollback.

## Cowpox

**Cowpox: Spreading Cure Samples to Recover Infected LLM Agents.** ICML 2025. [arXiv](https://arxiv.org/abs/2508.09230)

- **Problem:** Most MAS defenses isolate. They do not undo infection in memory or RAG. Prompt Infection showed that malice spreads; a corresponding recovery mechanism was missing.
- **Method:** Cowpox constructs **cure samples** designed to outcompete viral samples in retrieval-augmented memories. The paper analyzes how cures propagate through the same interaction channels the virus used.
- **Result:** Cure samples can spread and restore infected agents more effectively than isolation-only baselines in the authors' RAG/community settings, with an explicit spread model.
- **Takeaway:** This is one of the few papers whose main contribution is recovery, not detection. It is the closest published analogue to a "self-healing" step, still limited to memory/RAG rather than tool side effects.

## GUARDIAN

**GUARDIAN: Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling.** NeurIPS 2025. [arXiv](https://arxiv.org/abs/2505.19234)

- **Problem:** One-shot graph snapshots miss attacks that look normal at turn t and only become visible in the trajectory. Supervised labels per attack family are also expensive.
- **Method:** Interactions are a **temporal graph**. BERT-style node attributes plus GCN capture space; a temporal Transformer captures turn-to-turn evolution. Dual decoders reconstruct attributes and structure; high reconstruction error is an anomaly. An information-bottleneck term limits what the latent keeps. Each round, the most suspicious agent can be removed. Training is unlabeled reconstruction, typically **per dataset / in-distribution**.
- **Result:** Anomaly detection rates average above 80% and peak around 95% in the paper's splits. False-discovery rate can reach about 30%. The method is not a cross-dataset unknown-attack claim in the BlindGuard sense.
- **Takeaway:** Time is a first-class signal. The intervention is still delete-the-node; FDR and in-distribution training are the practical limits.

## AgentBreeder

**AgentBreeder: Evolutionary Search for Capable and Safe Multi-Agent Scaffolds.** NeurIPS 2025. [arXiv](https://arxiv.org/abs/2502.00757)

- **Problem:** MAS scaffolds (roles, prompts, wiring) are usually hand-designed. Capability search can accidentally produce unsafe organizations.
- **Method:** Evolutionary search over scaffolds with a fitness that includes **both** task performance and safety metrics. Generations keep structures that do not win on capability alone.
- **Result:** Evolved scaffolds can improve the joint capability-safety objective relative to hand-written baselines on the authors' tasks.
- **Takeaway:** Organization is searchable. Unlike G-Safeguard, the defense is design-time, not runtime detection.

## PeerGuard

**PeerGuard: Detecting Backdoored Peers via Mutual Reasoning.** IEEE IRI 2025. [arXiv](https://arxiv.org/abs/2505.11642)

- **Problem:** A backdoored agent may behave well until a trigger. Central monitors that only see final answers miss inconsistent reasoning.
- **Method:** Agents inspect each other's reasoning chains. Inconsistencies between claimed reasoning and actions, or between peers on the same input, are treated as evidence of a backdoor.
- **Result:** Mutual reasoning catches backdoored peers better than outcome-only voting in the paper's settings, at extra communication cost.
- **Takeaway:** Cross-examination is a defense primitive (see also Lie Detector in the model-backdoor notes). It assumes some agents remain honest enough to audit.

## SentinelAgent

**SentinelAgent: Graph Anomaly Detection for LLM Multi-Agent Systems.** arXiv 2025. [arXiv](https://arxiv.org/abs/2505.24201)

- **Problem:** Same family as G-Safeguard: detect malicious agents from the communication graph. Placement of the monitor (who sees which edges) differs from the G-Safeguard papers.
- **Method:** A graph anomaly detector sits on agent interaction graphs and flags abnormal nodes. The preprint emphasizes a sentinel agent as the monitoring role.
- **Result:** Competitive detection on interaction-graph tasks; high citation count relative to contemporaneous preprints is why it is kept next to the G-Safeguard line.
- **Takeaway:** Monitor **placement** is part of the design. Compare with SentinelNet (decentralized, no single sentinel).

## SAFEFLOW

**SAFEFLOW: A Transactional Protocol for Principled Multi-Agent Execution.** arXiv 2025. [arXiv](https://arxiv.org/abs/2506.07564)

- **Problem:** Agent runs are typically best-effort chat. Failures, injections, and partial tool calls have no abort/commit semantics.
- **Method:** SAFEFLOW treats agent work as **transactions**: principled begin/commit/rollback around tool and message effects, so a detected fault can unwind a unit of work rather than only mute a speaker.
- **Result:** The protocol framing is the contribution; empirical claims focus on containing unsafe or failed runs with rollback compared with unconstrained loops.
- **Takeaway:** Protocol-level recovery is different from GNN isolation. This is the systems analogue of shielding plus checkpoints.

## BlockA2A

**BlockA2A: Verifiable Agent-to-Agent Interoperability.** arXiv 2025. [arXiv](https://arxiv.org/abs/2508.01332)

- **Problem:** Open A2A interoperability without identity, signatures, or provenance lets any peer impersonate a tool or agent.
- **Method:** BlockA2A adds identity, signed messages, and ledger-style provenance so agent-to-agent calls are attributable and auditable.
- **Result:** The paper shows a verifiable interoperability layer rather than a higher AUC on ASB-style semantic attacks.
- **Takeaway:** Authentication is complementary to GAD. Forged peers are a different threat from poisoned embeddings.

## BlindGuard

**BlindGuard: Safeguarding LLM-based Multi-Agent Systems under Unknown Attacks.** ACL 2026. [ACL](https://aclanthology.org/2026.acl-long.1819/)

- **Problem:** G-Safeguard needs attack labels. At test time the attack family may be new. The paper asks whether a detector trained only on **normal** collaboration graphs can flag unknown attacks.
- **Method:** Dialogue is embedded with a frozen sentence encoder. Each node is described by self / neighbor / global features. An MLP plus projection head is trained with **contrastive learning** on normal graphs plus synthetic noise, not real attack labels. At test time, anomaly scores drive isolation. Code snapshots in this repo implement PI, TA, MA, and MA_CSQA settings, with Dominant / TAM / PREM as unsupervised baselines.
- **Result:** Unknown-attack generalization is the headline relative to G-Safeguard. XG-Guard later reports that on 24 main combinations, BlindGuard averages AUC about 78 versus G-Safeguard's supervised ~99. The method assumes attacks form a **semantic outlier** in embedding space.
- **Takeaway:** Unsupervised GAD is the unknown-attack story. It is exactly what [When Embedding-Based Defenses Fail](01-mas-attacks.md#embedding-defenses-fail) targets.

## XG-Guard

**Explainable and Fine-Grained Safeguarding of LLM Multi-Agent Systems via Bi-Level Graph Anomaly Detection.** ACL 2026. [ACL](https://aclanthology.org/2026.acl-long.1407/)

- **Problem:** BlindGuard scores whole utterances. Operators need to know **which tokens** drove the anomaly, and unknown-attack AUC still has headroom.
- **Method:** Bi-level GNN: a sentence-level graph plus a token-level graph, with a theme / topic signal so off-topic tokens can be highlighted. Training is contrastive on normal graphs across themes (no attack labels). Outputs are an agent-level score and a token heatmap. Intervention remains isolation. The public snapshot in `code/xg-guard/` has no LICENSE file; see `NOTICE.md`.
- **Result:** On 24 main combinations the paper reports mean AUC about 95.5, above BlindGuard (~78) and still slightly below supervised G-Safeguard (~98.6). Explanation quality is less rigorously validated than detection AUC; a failure mode is flagging mere topic drift.
- **Takeaway:** Fine-grained GAD plus explanation is the current peak of the embedding-GNN line, with the same embedding-adaptive risk as BlindGuard.

## TopoSHIELD

**TopoSHIELD: Reshaping the Flow of Malice via Spatio-Temporal Risk-Aware Topological Evolution.** ACL 2026 Findings. [ACL](https://aclanthology.org/2026.findings-acl.426/)

- **Problem:** Static prune-once graphs cannot track risk that moves over turns. Malice flow depends on both space (who is connected) and time (when an edge is hot).
- **Method:** TopoSHIELD evolves the communication topology using spatio-temporal risk estimates: risky edges are down-weighted or rewired over time so malice is steered away from high-value agents.
- **Result:** Risk-aware topology evolution reduces spread relative to static graphs and to one-shot pruning on the authors' MAS attack settings.
- **Takeaway:** Topology is a **control trajectory**, not a fixed hyperparameter. Compare AgentPrune (efficiency), G-Safeguard (one-shot prune), SafeSieve (progressive prune), ResMAS (search).

## SafeSieve

**SafeSieve: Progressive Pruning of Unsafe Communication in Multi-Agent Systems.** AAAI 2026. [arXiv](https://arxiv.org/abs/2508.11733)

- **Problem:** One-shot isolation is brittle: too aggressive and utility dies; too timid and the attack remains. Progressive removal of unsafe or unreliable edges may trace a better safety-utility curve.
- **Method:** Communication is sieved in stages. Edges or agents that look unsafe or unreliable are pruned progressively while the remaining graph continues the task.
- **Result:** Progressive pruning improves the safety-utility trade-off versus all-or-nothing isolation on the paper's collaboration attacks.
- **Takeaway:** Intervention scheduling matters. This is operationally close to G-Safeguard's prune, with a curriculum.

## Byzantine Reliability

**Byzantine Reliability for LLM Multi-Agent Systems via Confidence-Probed Weighted Aggregation (CP-WBFT).** AAAI 2026. [arXiv](https://arxiv.org/abs/2511.10400)

- **Problem:** Classic BFT wants an identity of the faulty replica. LLM agents are not deterministic replicas, and the system may need to keep working **without** naming the adversary.
- **Method:** Agents are probed for confidence. Aggregation is a weighted Byzantine-style rule: low-confidence or inconsistent votes count less. The goal is reliability of the joint output under Byzantine-like agents.
- **Result:** Confidence-probed weighted aggregation withstands a fraction of adversarial agents better than naive majority, without a separate GNN detector.
- **Takeaway:** "Do not find the bad guy; bound their influence." This is the PBFT idea translated to semantic votes. Pair with [foundations: PBFT](08-foundations.md#pbft).

## ResMAS

**ResMAS: Optimizing Topology and Prompts for Resilient Multi-Agent Systems.** AAAI 2026. [arXiv](https://arxiv.org/abs/2601.04694)

- **Problem:** Resilience (ICML 2025) showed hierarchical graphs are tougher, but the organization was hand-chosen. Can topology and prompts be **jointly optimized** for resilience?
- **Method:** Search over communication graphs and topology-aware prompts with a resilience objective (performance under perturbed / faulty agents), not only clean-task accuracy.
- **Result:** Optimized topology-plus-prompt configurations outperform the paper's hand-designed resilient baselines under agent faults.
- **Takeaway:** Resilience is an optimization problem. Design-time search (ResMAS, AgentBreeder) complements runtime GAD.

## SentinelNet

**SentinelNet: Decentralized Credit and Neighbor Elimination for Multi-Agent Security.** WWW 2026. [arXiv](https://arxiv.org/abs/2510.16219)

- **Problem:** G-Safeguard-style monitors are centralized: one model sees the whole graph. That is a single point of failure and a privacy issue.
- **Method:** Each agent keeps a local **credit** for neighbors and eliminates bottom-k neighbors (local quarantine) without a global GNN. The network of local sentinels is the defense.
- **Result:** Decentralized credit plus neighbor elimination reduces the impact of malicious peers on WWW-scale / social-style agent graphs in the paper's evaluation, without a central detector.
- **Takeaway:** Defense can be fully distributed. Compare Credibility Scoring (soft weights, possibly central) and G-Safeguard (central GNN).
