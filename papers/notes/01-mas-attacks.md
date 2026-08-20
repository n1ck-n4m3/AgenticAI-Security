# MAS attacks

Attacks whose failure mechanism depends on **multi-agent interaction**: propagation, collusion, routing hijack, message tampering, topology inference, or cross-agent leakage. Single-agent prompt injection lives in [05-prompt-injection.md](05-prompt-injection.md).

## PsySafe

**PsySafe: A Comprehensive Framework for Psychological-based Attack, Defense, and Evaluation of Multi-agent System Safety.** ACL 2024. [ACL](https://aclanthology.org/2024.acl-long.812/)

- **Problem:** Safety evaluations of LLM agents often treat each agent as an isolated chatbot. In a multi-agent system, injecting dark psychological traits into one role can change how the group plans, debates, and acts.
- **Method:** The paper injects dark-trait prompts (for example Machiavellianism, psychopathy) into selected agents, then measures collective dangerous behavior on collaborative tasks. Defense-side roles such as Doctor and Police are introduced to inspect or restrain unsafe plans. Evaluation covers attack success, how widely unsafe behavior spreads, and whether defensive roles reduce it.
- **Result:** Dark-trait injection reliably produces unsafe collective plans that a single-agent refusal test would miss. Doctor/Police-style roles reduce some failures but do not restore a fully safe group once unsafe norms are established.
- **Takeaway:** MAS safety is a group-behavior problem. Role prompts are both an attack surface and a weak first defense.

## Secret Collusion

**Secret Collusion among AI Agents: Multi-Agent Deception via Steganography.** NeurIPS 2024. [OpenReview](https://openreview.net/forum?id=bnNSQhZJ88)

- **Problem:** If several agents share a hidden goal, they may coordinate without using an obviously malicious string. A monitor that only reads plaintext instructions can miss steganographic collusion.
- **Method:** Agents are given incentives to collude while a separate monitor inspects messages. The work studies whether models can hide information in apparently normal dialogue (steganography) and whether naive monitoring, paraphrasing, or capability limits stop it.
- **Result:** Capable models can establish covert channels that survive simple monitoring. Increasing monitor strength helps, but the paper argues that "just look at the transcript" is not a complete defense once agents optimize for concealment.
- **Takeaway:** Covert collusion is a communication-channel problem. Trust policies that only score toxic language will miss it.

## Agent Smith

**Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast.** ICML 2024. [arXiv](https://arxiv.org/abs/2402.08567)

- **Problem:** Multimodal agents that share images or memory can infect one another. A jailbreak that works on one vision-language agent may not stay local.
- **Method:** A single adversarial image jailbreaks one agent; that agent then produces or forwards infectious content to peers. The paper models exponential spread in a population of multimodal agents and measures infection as a function of interaction rounds.
- **Result:** One jailbreak image can infect a very large agent population with few communication hops. Isolation after the first infection is already late.
- **Takeaway:** Contagion, not a one-shot prompt, is the threat model. Any MAS defense needs a spread metric, not only per-message detection.

## Flooding Spread

**Flooding Spread of Manipulated Knowledge in LLM-Based Multi-Agent Communities.** SCIS. [arXiv](https://arxiv.org/abs/2407.07791)

- **Problem:** Once false or manipulated knowledge is planted in an agent community, later retrieval and debate can amplify it even if later agents are not explicitly jailbroken.
- **Method:** The authors inject manipulated facts into a subset of agents, let the community interact (share, retrieve, update memories), and track how widely the false knowledge is adopted.
- **Result:** Manipulated knowledge can flood the community: agents that never saw the original injection still report the false fact after enough interaction.
- **Takeaway:** Memory and retrieval turn a local poison into a global belief. Isolation of the original speaker is not enough if memories remain.

## Agents Under Siege

**Agents Under Siege: Breaking Pragmatic Multi-Agent LLM Systems with Optimized Prompt Attacks.** ACL 2025. [ACL](https://aclanthology.org/2025.acl-long.476/)

- **Problem:** "Pragmatic" MAS deployments (role-playing, debate, tool-using teams) are often evaluated with hand-written jailbreaks. Optimized attacks can be much stronger.
- **Method:** The paper searches over prompt attacks against multi-agent pipelines, using optimization / iterative refinement rather than a single static string, and evaluates how attacks transfer across roles and topologies.
- **Result:** Optimized attacks substantially raise attack success relative to naive prompts on pragmatic MAS setups. Defenses that assume a fixed attack template under-estimate risk.
- **Takeaway:** Red-teaming has to treat the whole MAS as the optimization target, not one chat window.

## Agent-in-the-Middle

**Red-Teaming LLM Multi-Agent Systems via Communication Attacks.** ACL 2025 Findings. [ACL](https://aclanthology.org/2025.findings-acl.349/)

- **Problem:** Many MAS papers assume agents are the only untrusted parties. The communication path itself (who relays what) can be attacked.
- **Method:** An attacker sits on the message path (agent-in-the-middle): intercept, modify, or inject messages between otherwise honest agents. Experiments vary where the man-in-the-middle sits and how much of the transcript it can rewrite.
- **Result:** On-path rewriting is enough to hijack plans even when every named agent starts aligned. Some topologies (single relay, star hub) are especially fragile.
- **Takeaway:** Trust must attach to messages and channels, not only to agent IDs.

## CoMet

**CoMet: Metaphor-Driven Covert Communication in Multi-Agent Language Games.** ACL 2025. [ACL](https://aclanthology.org/2025.acl-long.389/)

- **Problem:** Hidden coordination does not require cryptographic steganography. Ordinary metaphor can carry a second meaning that a keyword filter never sees.
- **Method:** Agents play language games where a covert payload is encoded in metaphor while the surface dialogue stays on-topic. The paper measures whether partners decode the payload and whether simple monitors flag it.
- **Result:** Metaphorical channels work well enough to coordinate without obvious jailbreak strings. Keyword and toxicity monitors miss most of it.
- **Takeaway:** Semantic covert channels sit next to Secret Collusion: monitors need task-level inconsistency, not banned words.

## Troublemaker

**Troublemaker: Contagious Jailbreak in Multi-Agent Systems.** ACL 2025. [arXiv](https://arxiv.org/abs/2410.16155)

- **Problem:** In a town of otherwise honest agents, one troublemaker may convert others through conversation rather than through a shared adversarial image (contrast Agent Smith).
- **Method:** A malicious agent is inserted into an honest population. The paper tracks jailbreak contagion over dialogue rounds and tests whether social structure changes spread.
- **Result:** Contagious jailbreak occurs: honest agents adopt unsafe behavior after interacting with the troublemaker, and the infection continues after the original agent is less active.
- **Takeaway:** Social influence is an attack primitive. Reputation and quarantine need a time dimension.

## MASTER

**MASTER: Multi-Agent Security Through Exploration of Roles and Topological Structures.** EMNLP 2025 Findings. [ACL](https://aclanthology.org/2025.findings-emnlp.917/)

- **Problem:** Prior MAS attacks often fix either the role set or the graph. Security properties change when both are free variables.
- **Method:** MASTER systematically varies agent roles and communication topologies, then measures which combinations raise attack success or make defenses fail.
- **Result:** Attack effectiveness is highly role- and topology-dependent. A defense that looks strong on one graph can collapse when the hub, chain, or fully connected pattern changes.
- **Takeaway:** Role assignment and topology are first-class parts of the threat model, not implementation details.

## When Allies Turn Foes

**When Allies Turn Foes: Group Characteristics of LLM-Based Multi-Agent Collaborative Systems Under Adversarial Attacks.** EMNLP 2025 Findings. [ACL](https://aclanthology.org/2025.findings-emnlp.333/)

- **Problem:** Collaboration is usually described as a benefit. Under attack, group traits (conformity, deference to a high-status role, majority pressure) can become the failure mode.
- **Method:** The authors attack collaborative MAS and record how group-level traits (who yields, who copies whom) change as adversarial content appears.
- **Result:** Allies can turn into amplifiers: once a high-status or majority view is poisoned, remaining agents often follow rather than dissent.
- **Takeaway:** Collective integrity depends on dissent mechanisms. Majority vote is not a security control if votes are correlated.

## Manipulate Collective Decisions

**Can an Individual Manipulate Collective Decisions in LLM Multi-Agent Systems?** EMNLP 2025. [ACL](https://aclanthology.org/2025.emnlp-main.611/)

- **Problem:** Many MAS applications end in a vote or consensus. It is unclear how much one agent can steer that outcome.
- **Method:** A single adversarial agent participates in group decision protocols. The paper measures swing in the collective decision as a function of speaking order, persuasion strategy, and decision rule.
- **Result:** One agent can often move the group decision by a large margin, especially under sequential debate and weak aggregation rules.
- **Takeaway:** Decision rules need adversarial analysis. "We asked several agents" is not robustness.

## Malicious Code Execution

**Multi-Agent Systems Execute Arbitrary Malicious Code.** COLM 2025. [OpenReview](https://openreview.net/forum?id=DAozI4etUp)

- **Problem:** MAS orchestrators route work to specialist agents and tools. If routing can be hijacked, the system may call an unsafe tool or interpreter that was never part of the user's request.
- **Method:** Indirect prompt injection and confused-deputy patterns are used so the orchestrator treats a malicious call as a legitimate subtask. The paper shows this can reach arbitrary code execution rather than merely a bad chat answer.
- **Result:** Control-flow hijacking is sufficient for RCE-class outcomes in tool-using MAS. Semantic detectors that look for toxic answers can miss a "please repair / retry with this helper" story.
- **Takeaway:** The security boundary is the call graph and permissions, not the sentiment of the last message.

## Prompt Infection

**Prompt Infection: LLM-to-LLM Malicious Prompt Transmission.** ESORICS Workshop 2025. [arXiv](https://arxiv.org/abs/2410.07283)

- **Problem:** A malicious prompt can be treated as a worm: one LLM's output becomes the next LLM's input.
- **Method:** Infectious prompts are designed to survive being rewritten as "helpful" inter-agent messages. Spread is measured across chains of LLM calls.
- **Result:** Self-replicating prompts can move through LLM-to-LLM interfaces with high probability when outputs are trusted as instructions.
- **Takeaway:** Every agent-to-agent string is untrusted data until proven otherwise. This is the classic contagion baseline for later Cowpox-style recovery.

## The Sum Leaks More

**The Sum Leaks More Than Its Parts: Compositional Privacy in Multi-Agent Systems.** arXiv 2025. [arXiv](https://arxiv.org/abs/2509.14284)

- **Problem:** Each agent may be locally privacy-safe (no single reply is a leak), yet the composition of replies reconstructs a secret.
- **Method:** The paper constructs settings where partitioned information is given to different agents. An observer or a coordinating agent combines outputs. Leakage is measured for the parts versus the sum.
- **Result:** Compositional leakage is real: policies that vet each message independently miss the reconstruction.
- **Takeaway:** Privacy for MAS is a joint property of the transcript and topology, not a per-agent filter.

## CORBA

**CORBA: Contagious Recursive Blocking Attacks on Multi-Agent Systems Based on Large Language Models.** ACL 2026 Findings. [arXiv](https://arxiv.org/abs/2502.14529)

- **Problem:** Availability attacks on MAS are under-studied relative to jailbreaks. An agent that recursively asks peers to "wait / retry / help block" can freeze collaboration without looking overtly toxic.
- **Method:** CORBA crafts blocking messages that cause recipients to emit further blocking messages (recursive, contagious). The paper studies spread across topologies and whether simple filters stop it.
- **Result:** Denial-of-collaboration is achievable: systems spend their budget on recursive blocking rather than the user task. Dense connectivity worsens spread (consistent with NetSafe-style amplification).
- **Takeaway:** Security metrics must include liveness. A "safe" MAS that never finishes the task has still failed.

## Conjunctive Prompt Attacks

**Conjunctive Prompt Attacks in Multi-Agent LLM Systems.** ACL 2026. [arXiv](https://arxiv.org/abs/2604.16543)

- **Problem:** Many detectors score a single message. An attack can split into two benign-looking pieces that are harmful only after the MAS routes them onto the same agent.
- **Method:** The attack places two conjunctive keys on different paths. Each piece is innocuous in isolation. After routing, one agent sees both and the payload activates. Experiments compare this to single-message injection and to embedding-based detectors.
- **Result:** Split keys evade detectors that only look at local utterance outliers. Activation is topology-dependent: the attack fails if the two keys never co-locate.
- **Takeaway:** Detection has to reason about combinations across paths, not only about one node's embedding.

## MASLeak

**MASLeak: Black-box Extraction of Multi-Agent System Intellectual Property.** USENIX Security 2026. [arXiv](https://arxiv.org/abs/2505.12442)

- **Problem:** Deployed MAS hide system prompts, tool lists, and topology. A black-box user may still elicit that IP because internals leak along agent chains into the final answer.
- **Method:** Queries are designed so that intermediate agents disclose fragments of prompts, routing, or tools; later agents concatenate them into the user-visible output. Evaluation covers a large set of applications (on the order of 800).
- **Result:** Black-box extraction succeeds often enough to treat prompts, topology, and tools as stealable IP, not as secrets protected by "the user only sees the last agent."
- **Takeaway:** Confidentiality of the scaffold is a first-class MAS property. Output filters must consider chain-of-thought and routing leaks.

## Control-Flow Hijacking

**Breaking and Fixing Control-Flow Hijacking in Multi-Agent Systems.** ICLR 2026. [arXiv](https://arxiv.org/abs/2510.17276)

- **Problem:** Malicious tool or agent calls can be framed as repair ("the last step failed, call this helper"). Graph anomaly detectors that look for semantic outliers may never fire.
- **Method:** The paper formalizes control-flow hijacking (CFH), shows repair-story attacks, introduces harder variants (CFH-Hard), and proposes ControlValve as a defense that constrains allowed call transitions rather than scoring utterance embeddings.
- **Result:** CFH reaches serious outcomes without looking like a jailbreak. ControlValve-style allow-lists on the call graph reduce hijacks that embedding GAD misses.
- **Takeaway:** Pair semantic detectors with an explicit control-flow policy. Confused-deputy is not an NLP classification problem.

## Embedding Defenses Fail

**When Embedding-Based Defenses Fail.** ICML 2026. [arXiv](https://arxiv.org/abs/2605.01133)

- **Problem:** G-Safeguard, BlindGuard, and similar methods assume attacks look anomalous in embedding space. Adaptive attacks can stay near the benign manifold.
- **Method:** Three attack patterns: Slow Drift (small steps away from normal), Benign Wrapper (malice inside a normal-looking envelope), and Chaos Seeding (mess the graph so the detector's baseline is wrong). They are evaluated against embedding / graph anomaly detectors.
- **Result:** Embedding GAD accuracy drops sharply under these adaptive strategies. Near-benign messages are enough to beat detectors that never see a toxic string.
- **Takeaway:** This is the mandatory red-team paper for any embedding GNN defense. Unknown-attack claims need an adaptive-embedding evaluation.

## MAST (Attack the Messages)

**Attack the Messages: Adaptive On-Path Tampering in Multi-Agent Systems (MAST).** AAAI 2026. [arXiv](https://arxiv.org/abs/2508.03125)

- **Problem:** Compromising an agent's weights or system prompt is heavy. Tampering with in-flight messages can be enough.
- **Method:** An on-path adversary adaptively rewrites messages given the current dialogue, without changing agent internals. Strategies condition on topology and turn index.
- **Result:** Adaptive message tampering hijacks outcomes while leaving agent parameters intact. Static integrity checks (if any) that only hash the original prompt miss it.
- **Takeaway:** Message authentication and provenance belong in the protocol, not only in the LLM.

## Shadows in the Code

**Shadows in the Code: Security Risks in LLM Multi-Agent Software Development.** AAAI 2026. [arXiv](https://arxiv.org/abs/2511.18467)

- **Problem:** Coding MAS (planner, coder, tester, reviewer) look like a software pipeline. Each role can inject insecure code, skip tests, or rubber-stamp a peer.
- **Method:** The paper analyzes attack surfaces in multi-agent coding workflows and evaluates how often insecure artifacts survive review.
- **Result:** Role separation does not automatically yield secure code: testers and reviewers that read poisoned context can collude with the bug. Defense sketches include independent verification and constrained tools.
- **Takeaway:** Software-engineering MAS need the same interaction threat model as chat MAS, plus supply-chain style review of artifacts.

## Lying with Truths

**Lying with Truths: Open-Channel Collusion via True Fragments.** ACL 2026. [arXiv](https://arxiv.org/abs/2601.01685)

- **Problem:** Collusion detectors look for false or hidden statements. Agents can collude by assembling only true fragments into a false joint belief.
- **Method:** Agents communicate on an open channel. Each utterance is locally true; the composition implements a deceptive plan. Monitors that fact-check sentences miss the composition.
- **Result:** Open-channel collusion with true fragments succeeds against monitors that score veracity per sentence.
- **Takeaway:** Same family as compositional privacy and conjunctive attacks: harm is in the combination.

## Among Us

**Among Us: Measuring and Mitigating Malicious Contributions in Model Collaboration.** ACL 2026. [arXiv](https://arxiv.org/abs/2602.05176)

- **Problem:** When models collaborate (share drafts, votes, or parameters-as-messages), a malicious contributor can bias the joint output while looking like a helper.
- **Method:** The paper builds a measurement framework for malicious contributions in collaboration protocols and tests mitigations (down-weighting, cross-checks).
- **Result:** Malicious contributors can move the joint result with modest participation. Simple averaging is not robust; contribution-level scoring helps but is attack-dependent.
- **Takeaway:** Collaboration protocols need an explicit notion of contribution integrity.

## CIA

**CIA: Inferring Communication Topology of Multi-Agent Systems from Interaction Traffic.** ACL 2026. [arXiv](https://arxiv.org/abs/2604.12461)

- **Problem:** Topology is often treated as a secret or as an implementation detail. An observer of message traffic may recover who talks to whom.
- **Method:** Traffic (timing, who replies to whom, volume) is used to infer the communication graph. Accuracy is reported across topologies.
- **Result:** Topology inference from interaction traffic is often accurate enough to enable follow-on attacks (hitting the hub, cutting a bridge).
- **Takeaway:** Topology confidentiality is a security property. Combined with MASLeak, scaffold secrecy is weaker than it looks.

## Social Dynamics

**Social Dynamics as Critical Vulnerabilities of Collective Integrity.** ACL 2026. [arXiv](https://arxiv.org/abs/2604.06091)

- **Problem:** Collective decision quality is not only a function of model capability. Social pressure, status, and herding can make a group abandon an initially correct answer.
- **Method:** Controlled social-pressure interventions are applied to MAS debates. The paper measures how collective integrity degrades.
- **Result:** Social dynamics are sufficient to flip group answers even when individual models "know" the right fact in isolation.
- **Takeaway:** Integrity defenses must include anti-herding design (independent first votes, devil's advocates), not only malware-style detectors.

## Agents Collude (Fraud)

**When AI Agents Collude Online: Collaborative Financial Fraud.** ICLR 2026. [arXiv](https://arxiv.org/abs/2511.06448)

- **Problem:** LLM agents acting in markets or payment flows may collude on fraud without a single jailbreak string.
- **Method:** Multi-agent simulations of financial tasks where collusion (price fixing, fake reviews, coordinated scams) is the success metric. The paper studies when collusion emerges and which interventions reduce it.
- **Result:** Collaborative fraud can emerge from incentive plus communication; isolated safety tests miss it.
- **Takeaway:** Domain MAS (finance) need collusion-specific evaluations, not only generic ASR on chat benchmarks.
