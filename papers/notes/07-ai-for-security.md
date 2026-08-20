# AI for security

LLMs used as security tools (vulnerability detection, fuzzing, SOC), plus defenses against attacking agents. IEEE S&P 2025 items without a local full text are marked as program/abstract summaries.

## GPTScan

**GPTScan: Detecting Logic Vulnerabilities in Smart Contracts by Combining GPT with Program Analysis.** ICSE 2024. [ACM](https://dl.acm.org/doi/10.1145/3597503.3639117)

- **Problem:** Smart-contract logic bugs cause large losses. Pattern matchers miss them; raw GPT over-reports.
- **Method:** Split each logic-bug type into a scene plus a property. GPT proposes matches; static analysis confirms and drops hallucinations.
- **Result:** False positives drop by about two thirds on real contracts, making detection usable.
- **Takeaway:** LLM proposes, program analysis confirms. The same split (proposer / inspector) appears in MAS defenses.

## LLM Incident Response

**Integrating Large Language Models into Security Incident Response.** SOUPS 2025. [USENIX](https://www.usenix.org/conference/soups2025/presentation/kramer)

- **Problem:** Incident response is labor-heavy. It is unclear whether LLMs should summarize alone or only assist analysts.
- **Method:** User study: 18 analysts, 50 real incidents. Compare autonomous LLM summaries versus human-LLM collaboration. Measure omissions, fabrications, readability, and analyst feedback.
- **Result:** Autonomous summaries miss critical facts about 35% of the time and fabricate about 42%. Collaboration still improves readability.
- **Takeaway:** Copilot, not autopilot. Capability claims for SOC LLMs must include omission and hallucination rates.

## CHeaT

**Cloak, Honey, Trap: Proactive Defenses Against LLM Agents.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/ayzenshteyn)

- **Problem:** Offensive LLM agents automate intrusion. The same agent quirks (bias, memory, tokenization) can be turned against them.
- **Method:** CHeaT deploys cloak / honey / trap tactics: honey tokens, infinite loops, bait execution paths that waste or capture attacking agents. Evaluated on 11 CTF machines.
- **Result:** 100% of attacking agents in the experimental setting were stopped, at lower cost than conventional hardening.
- **Takeaway:** Offense-as-agent has failure modes that defenders can engineer. Honey topology is the dual of a trust topology.

## HLPFUZZ

**Hybrid Language Processor Fuzzing via LLM-Based Constraint Solving.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/yang-yupeng)

- **Problem:** Compilers and interpreters have deep states that random fuzzing never reaches.
- **Method:** Natural-language specifications are turned into constraints; an LLM solves them to produce reaching inputs for the language processor.
- **Result:** About 52 bugs from roughly six-line specs in the paper's campaign; high discovery efficiency.
- **Takeaway:** LLMs amplify classical fuzzing's reach, as constraint solvers rather than as oracles.

## LLMxCPG

**LLMxCPG: Context-Aware Vulnerability Detection Through Code Property Graph-Guided LLMs.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/lekssays)

- **Problem:** Pure deep-learning vulnerability detectors drop about 45 points on strict datasets and break after small rewrites.
- **Method:** Build a code property graph, slice the vulnerability-relevant context (compressing context about 67-91%), then ask the LLM. Structure is the prior.
- **Result:** More stable than fragile DL baselines, especially across functions and under rewriting.
- **Takeaway:** Structural priors are what make LLM security analysis reliable.

## G2FUZZ

**Low-Cost and Comprehensive Non-textual Input Fuzzing with LLM-Synthesized Input Generators.** USENIX Security 2025. [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/zhang-kunpeng)

- **Problem:** LLMs are bad at emitting valid non-text (binary, structured) fuzz inputs directly.
- **Method:** The LLM writes an input-generator script; AFL++-style mutation then takes over. Generators are cheap to reuse.
- **Result:** Better coverage and bug finding on several non-text formats.
- **Takeaway:** Have the LLM produce tools, not samples.

## SV-TrustEval-C

**SV-TrustEval-C: Evaluating Structure and Semantic Reasoning in LLMs for Source Code Vulnerability Analysis.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Leaderboard accuracy on vulnerability labels can be shortcut learning. Public-program summary.
- **Method:** Probe tasks that separate genuine structural/semantic reasoning from superficial cues.
- **Result:** Exposes the real reasoning boundary of LLM vulnerability analysis.
- **Takeaway:** Evaluate the capability before deploying the detector.

## Supporting Human Raters

**Supporting Human Raters with the Detection of Harmful Content using Large Language Models.** IEEE S&P 2025. [program](https://sp2025.ieee-security.org/accepted-papers.html)

- **Problem:** Human moderation does not scale; LLM assistance can add bias and over-reliance. Public-program summary.
- **Method:** Assistive workflows for harmful-content rating; measure efficiency, quality, bias, and dependence.
- **Result:** Quantifies both the gain and the new risks of LLM-assisted rating.
- **Takeaway:** Human-AI security work is itself a research object (same spirit as the SOUPS SOC study).
