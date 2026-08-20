# Jailbreak, backdoor, and privacy

Model-level attacks and defenses that MAS papers cite but that are not MAS-primary. IEEE S&P 2025 items without a public full text here are marked as program/abstract summaries.

## DDFed

**Dual Defense: Enhancing Privacy and Mitigating Poisoning Attacks in Federated Learning.** NeurIPS 2024. [NeurIPS](https://neurips.cc/virtual/2024/poster/96030)

- **Problem:** FL wants both private aggregation and poisoning resistance. Those goals often fight: detectors want plaintext updates, privacy wants ciphertext.
- **Method:** Fully homomorphic encryption for aggregation plus a two-stage anomaly detector that runs on ciphertexts, without changing the FL topology.
- **Result:** Privacy and poisoning resistance improve together at acceptable accuracy cost.
- **Takeaway:** Joint optimization of privacy and robustness; MAS reputation aggregation has the same multi-objective shape.

## RFLPA

**RFLPA: A Robust Federated Learning Framework against Poisoning Attacks with Secure Aggregation.** NeurIPS 2024. [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2024/hash/bcbdc25dc4f0be5ae8ac07232df6e33a-Abstract-Conference.html)

- **Problem:** Secure aggregation hides updates, which also hides the statistics used by robust aggregators.
- **Method:** Verifiable Shamir secret sharing so cosine similarity (and related stats) can be computed without opening individual updates; down-weight or filter outliers, then aggregate.
- **Result:** Accuracy under poisoning is preserved without exposing client updates.
- **Takeaway:** Cryptography plus robust statistics can coexist. "Compare contributions without reading plaintext" transfers to multi-agent reputation.

## SPMC

**SPMC: Self-Purifying Federated Backdoor Defense via Margin Contribution.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/he25f.html)

- **Problem:** Adaptive federated backdoors dodge static robust aggregators. Clean accuracy often drops when defenses are aggressive.
- **Method:** Estimate each client's margin contribution, down-weight clients that disagree with the majority margin, and self-purify suspicious local gradients.
- **Result:** Holds up under adaptive backdoors while keeping clean accuracy.
- **Takeaway:** Contribution consistency is a distributed trust signal.

## Scaling Trends in Robustness

**Scaling Trends in Language Model Robustness.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/howe25a.html)

- **Problem:** Folk wisdom says larger models are safer. Attack and defense compute also scale.
- **Method:** Measure attack success and defense sample-efficiency across model scales, with and without adversarial / safety training.
- **Result:** Without safety training, larger is not more robust. Adversarial training helps sample efficiency, but attack-side scaling is often faster.
- **Takeaway:** Do not equate scale with security. Adding more MAS agents can also add fragility (see NetSafe).

## Jailbreak Tax

**The Jailbreak Tax: How Useful are Your Jailbreak Outputs?** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/nikolic25a.html)

- **Problem:** Jailbreak papers score whether the refusal was bypassed. The bypassed output may be useless for the harmful task.
- **Method:** After a successful jailbreak, measure task accuracy / usefulness of the output. Define a "tax" as the capability drop.
- **Result:** Usefulness can collapse (the paper reports cases on the order of a 92-point drop). "Jailbroken" is not "harmfully competent."
- **Takeaway:** Threat evaluation must separate trigger success from effective harm. Same split for collusion ASR.

## Weak-to-Strong Jailbreaking

**Weak-to-Strong Jailbreaking on Large Language Models.** ICML 2025. [PMLR](https://proceedings.mlr.press/v267/zhao25aa.html)

- **Problem:** Strong models are expensive to jailbreak with search. Alignment differences between a small and a large model can be a cheap signal.
- **Method:** Use the alignment gap between two weaker/stronger models, in a single forward pass, to amplify misaligned behavior on the large model. Discusses preliminary defenses.
- **Result:** Reported ASR above 99% in the paper's highlighted setting, at very low attack cost.
- **Takeaway:** Heterogeneous ensembles are a double-edged sword: diversity helps auditing and also supplies jailbreak signals.

## Task-Level Jailbreak

**Exploiting Task-Level Vulnerabilities: An Automatic Jailbreak Attack and Defense Benchmarking for LLMs.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/zhang-lan)

- **Problem:** Template and token jailbreaks are brittle under realignment. Harmful goals can be decomposed into benign-looking subtasks.
- **Method:** Decompose a harmful task into knowledge steps, compose them to bypass guards, and turn the procedure into a defense benchmark.
- **Result:** More stubborn than template jailbreaks; remains effective after realignment in the authors' tests.
- **Takeaway:** Attack granularity is the task graph. MAS papers such as MASTER make the same move at the role/topology level.

## PETAL

**Towards Label-Only Membership Inference Attack against Pre-trained Large Language Models.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/he-yu)

- **Problem:** Realistic APIs do not return full logits. Classic MIA that needs probabilities is too strong a threat model.
- **Method:** PETAL uses only generated text. Per-token semantic similarity approximates perplexity / membership scores.
- **Result:** Competitive with logit-based MIA under label-only access.
- **Takeaway:** Privacy threat models should match the API the victim actually ships.

## BackdoorLLM

**BackdoorLLM: A Comprehensive Benchmark for Backdoor Attacks and Defenses on Large Language Models.** NeurIPS 2025 (Datasets and Benchmarks). [OpenReview](https://openreview.net/forum?id=b0pt0OP2vT)

- **Problem:** LLM backdoor papers used incompatible attacks (data poison, weight poison, hidden-state, chain-of-thought hijack) and incomparable defenses.
- **Method:** About eight attack classes and seven defenses under one protocol; report ASR and clean accuracy.
- **Result:** Existing defenses are largely ineffective against jailbreak-style backdoors.
- **Takeaway:** The field still lacks a working LLM-backdoor defense paradigm. Agent/MAS backdoors (for example ASB's PoT) need their own bench, not a vision-backdoor transplant.

## Lie Detector

**Lie Detector: Unified Backdoor Detection via Cross-Examination Framework.** NeurIPS 2025. [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dce7d0eb0233aea3df9b19f71f3a69fb-Abstract-Conference.html)

- **Problem:** Outsourced training is untrusted. A single model's outputs do not reveal a trigger.
- **Method:** Give the same task to two independently trained models and treat output inconsistency as backdoor evidence. Unified framework across backdoor types.
- **Result:** Detects a range of backdoors without knowing the trigger.
- **Takeaway:** Redundancy plus disagreement is a trust signal (same family as Resilience's Challenger and PeerGuard).

## RepGuard

**RepGuard: Adaptive Feature Decoupling for Robust Backdoor Defense in Large Language Models.** NeurIPS 2025. [OpenReview](https://openreview.net/forum?id=jv7OHhQ0YP)

- **Problem:** Defenses that need known triggers only paper over the behavior. The backdoor lives in a feature subspace.
- **Method:** Decouple anomalous features from semantic features, trigger-agnostically, and suppress the backdoor pathway.
- **Result:** Mean ASR drop on the order of 80% in the paper's suite, with usable clean accuracy.
- **Takeaway:** Decoupling representations is more fundamental than erasing a trigger string.

## Unlearned but Not Forgotten

**Unlearned but Not Forgotten: Data Extraction after Exact Unlearning in LLM.** NeurIPS 2025. [OpenReview](https://openreview.net/forum?id=BpAx3OuNOr)

- **Problem:** "Exact unlearning" is assumed to remove a point. If the attacker also has a pre-unlearning checkpoint, extraction can get easier, not harder.
- **Method:** Compare extraction with and without the old checkpoint; analyze how unlearning plus version history leaks.
- **Result:** Access to historical checkpoints raises extraction risk after unlearning.
- **Takeaway:** Threat models must include old model versions. MAS old memories and old policies are the same class of leak.

## T2I Jailbreak Fuzzing

**Fuzz-Testing Meets LLM-Based Agents: An Automated and Efficient Framework for Jailbreaking Text-To-Image Generation Models.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Manual prompts are a slow way to jailbreak image generators. LLM agents can fuzz the T2I policy. Public-program summary.
- **Method:** An agent mutates prompts, queries the T2I model, and searches using moderation feedback.
- **Result:** Efficient discovery of T2I jailbreaks; agents as attack tools.
- **Takeaway:** Dual use: CHeaT is the defensive mirror (use agent weaknesses against attacking agents).

## BAIT

**BAIT: Large Language Model Backdoor Scanning by Inverting Attack Target.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Trigger-unknown scanning is the realistic case for LLM backdoors. Public-program summary.
- **Method:** Invert the attack target (what the model is being pushed to do) rather than search for a trigger string.
- **Result:** Feasible scanning across several backdoor settings in the paper.
- **Takeaway:** Detect abnormal goals, not only abnormal prefixes.

## PEFTGuard

**PEFTGuard: Detecting Backdoor Attacks Against Parameter-Efficient Fine-Tuning.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** LoRA / adapter supply chains can ship a backdoor without replacing the base model. Public-program summary.
- **Method:** Adapter-level detection, distinct from full-model backdoor tests.
- **Result:** Shows that PEFT components need their own inspection.
- **Takeaway:** Trust sinks to adapters in the componentized-model era.

## Architectural Neural Backdoors

**Architectural Neural Backdoors from First Principles.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Backdoors are usually discussed as data or weights. Structure itself can implement a backdoor. Public-program summary.
- **Method:** Construct architecture-level backdoors and analyze stealth and triggering.
- **Result:** Structural threats are real, not only a thought experiment.
- **Takeaway:** Supply-chain review must include architecture graphs, not only checkpoints.

## Secure Transfer Learning

**Secure Transfer Learning: Training Clean Model Against Backdoor in Pre-Trained Encoder and Downstream Dataset.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Transfer learning can inherit a poisoned encoder and a poisoned downstream set at once. Public-program summary.
- **Method:** Training / filtering algorithms under a two-sided threat model.
- **Result:** Usable clean downstream models even when both sides are contaminated, in the paper's protocol.
- **Takeaway:** Audit both the encoder and the fine-tune data.

## Rigging the Foundation

**Rigging the Foundation: Manipulating Pre-training toward Advanced Membership Inference Attacks.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** MIA is usually a post-hoc attack on a finished model. An adversary who influences pre-training can make membership easier later. Public-program summary.
- **Method:** Plant structure or signals during pre-training that amplify later MIA.
- **Result:** Membership inference becomes substantially stronger than post-hoc MIA on an honest pre-train.
- **Takeaway:** Privacy attacks can start in the foundation, not only at inference.

## Comet

**Comet: Accelerating Private Inference for Large Language Model by Predicting Activation Sparsity.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Cryptographic private inference for LLMs is too slow. Activation sparsity is a lever. Public-program summary.
- **Method:** Predict sparsity to cut encrypted compute; keep accuracy in a usable range.
- **Result:** Large speedups for private LLM inference in the authors' system.
- **Takeaway:** "Secure and usable" includes latency, not only epsilon.

## Tokenizer MIA

**Membership Inference Attacks on Tokenizers of Large Language Models.** USENIX Security 2026. [USENIX](https://www.usenix.org/conference/usenixsecurity26/cycle1-accepted-papers)

- **Problem:** Classic MIA on LLM training data fights mislabeling, drift, and scale. The tokenizer is an earlier, cleaner target. Public-program summary.
- **Method:** Membership inference against tokenizer training data, plus an adaptive defense discussion.
- **Result:** Opens a tokenizer-level privacy surface that sidesteps several classic MIA confounders.
- **Takeaway:** The earlier the supply-chain stage, the more foundational the privacy question.
