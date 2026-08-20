# Prompt injection and tool use

Single-agent and application-layer injection, tool selection, and MCP. MAS interaction attacks are in [01-mas-attacks.md](01-mas-attacks.md). Paywalled IEEE S&P 2025 items are summarized from public program and abstract information only.

## InjecAgent

**InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents.** ACL 2024 Findings. [ACL](https://aclanthology.org/2024.findings-acl.624/)

- **Problem:** Tool-using agents read web pages, mail, and API payloads. Attackers hide instructions in those returns (indirect prompt injection, IPI). There was no systematic IPI benchmark for tool agents.
- **Method:** InjecAgent formalizes success as whether the agent carries out the attacker's intent. About 1,054 cases cover harm types such as direct damage and data exfiltration, across diverse tools and models.
- **Result:** Models are substantially vulnerable to IPI; success varies by harm type. The bench became a shared target for later defenses (including MELON).
- **Takeaway:** External content is an instruction channel. In MAS, peer messages are the same kind of untrusted return.

## LLMSmith

**Demystifying RCE Vulnerabilities in LLM-Integrated Apps.** CCS 2024. [ACM](https://dl.acm.org/doi/10.1145/3658644.3690338)

- **Problem:** Apps often execute model output as code or shell. Alignment of the LLM does not fix unsafe execution glue.
- **Method:** LLMSmith audits LLM-integrated frameworks for dangerous sinks and execution paths (about 11 frameworks, 20 vulnerabilities, on the order of 13 CVEs).
- **Result:** RCE-class bugs are common once generated text is treated as a command.
- **Takeaway:** The trust boundary is the tool runtime, not the chat policy.

## AgentDojo

**AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.** NeurIPS 2024 (Datasets and Benchmarks). [OpenReview](https://openreview.net/forum?id=m1YYAQjO3w)

- **Problem:** Static prompt suites miss dynamic tool loops. Attacks and defenses need to iterate inside an environment.
- **Method:** A simulated tool-using agent completes user tasks while attackers contaminate tool returns. About 97 tasks and 629 security cases. Metrics: task success and attack success together.
- **Result:** Became the community's default dynamic PI environment; later defenses (MELON, DRIFT) report on it.
- **Takeaway:** External validity for agent security comes from multi-step tool environments.

## GuardAgent

**GuardAgent: Safeguard LLM Agents via Knowledge-Enabled Reasoning.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/xiang25a.html)

- **Problem:** Natural-language refusals are not a deterministic check of "does this action violate the policy?"
- **Method:** A guard agent compiles safety requirements into executable checking code (access control, web constraints) and allows or blocks the target agent's action.
- **Result:** Effective blocking on access-control and web-safety tasks relative to prompt-only guards.
- **Takeaway:** Guards can be agents that run code. In MAS, a police agent is the analogue, and it must itself be in the threat model.

## MELON

**MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/zhu25z.html)

- **Problem:** Successful IPI makes the agent's next action depend on the malicious task rather than the user's task. String matching does not capture that.
- **Method:** Mask suspicious context, re-run, and compare actions. Large disagreement flags injection. The paper includes analysis of when this detection is valid, and evaluates on AgentDojo.
- **Result:** Beats prior defenses on AgentDojo while keeping task utility relatively high.
- **Takeaway:** Behavioral consistency is the signal. The MAS analogue is: drop one peer's messages and see whether the collective decision jumps.

## ShieldAgent

**ShieldAgent: Shielding Agents via Verifiable Safety Policy Reasoning.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/chen25ae.html)

- **Problem:** Policy documents are prose. Runtime needs checkable rules over action traces.
- **Method:** Extract verifiable rules from policy text, build action-level probabilistic rule circuits, and verify traces; violations are blocked with an explanation.
- **Result:** Trace-checking tasks show effective blocking plus attributable violation reasons.
- **Takeaway:** Natural-language policy should compile to executable checks (same spirit as shielding in the foundations notes).

## DRIFT

**DRIFT: Dynamic Rule-Based Defense with Injection Isolation for Securing LLM Agents.** NeurIPS 2025. [NeurIPS](https://neurips.cc/virtual/2025/poster/116028)

- **Problem:** System defenses are often static. Rules go stale, and memory streams can be poisoned after the first check.
- **Method:** Three pieces: Secure Planner, Dynamic Validator, Injection Isolator. Plans are constrained; validators update rules; isolators cut contaminated memory or context before continuing.
- **Result:** Tracks changing attacks better than static policies while keeping task completion usable.
- **Takeaway:** Isolation has to be dynamic. MAS topology policy should also be updatable, not prune-once.

## StruQ

**StruQ: Defending Against Prompt Injection with Structured Queries.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe)

- **Problem:** LLM apps mix instructions and untrusted data in one text channel. That confusion is the root of prompt injection (OWASP's top LLM risk).
- **Method:** Split prompt and data into two structured channels. Fine-tune so the model obeys only the prompt channel and treats the data channel as non-instructional.
- **Result:** Attack success drops sharply across injection types with little utility loss. Becomes the architectural baseline for SecAlign and ToolHijacker comparisons.
- **Takeaway:** Interface design beats post-hoc filters. MAS should not flatten system, user, peer, and tool text onto one plane.

## SecAlign

**SecAlign: Defending Against Prompt Injection with Preference Optimization.** CCS 2025. [site](https://sizhe-chen.github.io/SecAlign-Website/)

- **Problem:** Structured queries help, but the model can still prefer to follow malicious instructions inside data. Preference optimization can teach the opposite.
- **Method:** Build preference pairs (safe compliance versus injected hijack) and train with DPO-style objectives. Evaluate generalization to unseen attacks. (Details from public abstracts and the author site when a local PDF is unavailable.)
- **Result:** Multi-class injection success is reported below 10%, several times lower than structured-query-only baselines, with better unseen-attack generalization.
- **Takeaway:** Alignment training is a first-class PI defense, not only a product-safety extra.

## DataSentinel

**DataSentinel: A Game-Theoretic Detection of Prompt Injection Attacks.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Passive classifiers lag adaptive injections. Detection can be set up as a game with a probe that is designed to "go off" under injection. Summarized from public program information.
- **Method:** A probe model is trained to be extremely sensitive to injected instructions; its reaction is the detection signal in a game between attacker and detector.
- **Result:** Strong detection across multiple injection styles in the authors' evaluation.
- **Takeaway:** Active canaries / honey tokens are a detection primitive (see also CHeaT in AI-for-security).

## Fun-tuning

**Fun-tuning: Characterizing the Vulnerability of Proprietary LLMs to Optimization-Based Prompt Injection via the Fine-Tuning Interface.** IEEE S&P 2025. [DOI](https://doi.org/10.1109/sp61157.2025.00121)

- **Problem:** Vendor fine-tuning APIs return losses and other signals. Those signals can drive optimization-based prompt injection against proprietary models.
- **Method:** Use fine-tuning-interface feedback to optimize injections (reported on Gemini-class APIs). Summarized from public information.
- **Result:** About 65-82% ASR on the paper's proprietary-model settings, exposing a utility-security tension in feedback-rich APIs.
- **Takeaway:** Any scoring or debug interface is an attack optimizer. MAS "eval loops" have the same shape.

## Prompt Inversion

**Prompt Inversion Attack against Collaborative Inference of Large Language Models.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Split / collaborative inference sends intermediate activations to another party. Those activations may invert to the user prompt. Public-program summary.
- **Method:** Invert intermediate representations to reconstruct the input prompt.
- **Result:** High-quality reconstructions; split inference is not privacy-safe by default.
- **Takeaway:** Multi-party inference needs a privacy mechanism, not only access control on the final text.

## ACE

**ACE: A Security Architecture for LLM-Integrated App Systems.** NDSS 2026. [NDSS](https://www.ndss-symposium.org/ndss-paper/ace-a-security-architecture-for-llm-integrated-app-systems/)

- **Problem:** Multi-app LLM systems break planning integrity, execution integrity, and privacy when plans are concrete and over-privileged from the start.
- **Method:** Plan first in an abstract, trusted vocabulary; map onto installed apps later. Static information-flow checks plus runtime data/capability barriers.
- **Result:** Systematic evaluation against plan/execution integrity and privacy attacks shows an advantage over prompt-only defenses.
- **Takeaway:** By-design architecture (plan/execute split plus IFC) dominates bolting on a detector.

## ObliInjection

**ObliInjection: Order-Oblivious Prompt Injection Attack to LLM Agents with Multi-source Data.** NDSS 2026. [NDSS](https://www.ndss-symposium.org/ndss-paper/obliinjection-order-oblivious-prompt-injection-attack-to-llm-agents-with-multi-source-data/)

- **Problem:** Agents concatenate many untrusted sources. The attacker may not know the concatenation order, so ordinary optimized injections are brittle.
- **Method:** An order-oblivious loss and orderGCG-style optimization make the payload work regardless of permutation. Contaminating about 1/6 to 1/100 of segments can be enough.
- **Result:** High success with partial control and unknown order.
- **Takeaway:** Composition under unknown routing is the realistic PI setting. Related to conjunctive MAS attacks.

## ToolHijacker

**Prompt Injection Attack to Tool Selection in LLM Agents.** NDSS 2026. [NDSS](https://www.ndss-symposium.org/ndss-paper/prompt-injection-attack-to-tool-selection-in-llm-agents/)

- **Problem:** Tool choice is retrieve-then-select. An attacker who can plant one malicious tool document may force that tool to be chosen without touching model weights (no-box).
- **Method:** Optimize the malicious tool description to fool both retrieval ranking and LLM selection. Test against StruQ, SecAlign, and DataSentinel.
- **Result:** High hijack rates; conversation-level PI defenses fail because the attack lives in the tool catalog.
- **Takeaway:** Trust the tool registry and retriever. MAS skill markets and peer directories have the same bug.

## Parasites in the Toolchain

**Parasites in the Toolchain: Large-Scale Attacks on the MCP Ecosystem.** IEEE S&P 2026. [arXiv](https://arxiv.org/abs/2509.06572)

- **Problem:** Model Context Protocol (MCP) makes tool servers easy to publish and consume. Scale plus weak identity turns the toolchain into a malware distribution channel.
- **Method:** Large-scale measurement and attack analysis of MCP servers and clients: malicious tools, name confusion, supply-chain style parasites.
- **Result:** Practical attacks on a real emerging ecosystem, not a toy tool API.
- **Takeaway:** Adjacent to MAS A2A/BlockA2A: interoperability without provenance is an open attack surface.
