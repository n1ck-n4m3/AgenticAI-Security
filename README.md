# Agentic AI Security

A public reading library for **agentic AI security**: multi-agent LLM systems, prompt injection and tool use, jailbreaks and backdoors, and using LLMs for security work.

Paper PDFs are not stored here. Each paper has an English note with venue, link, problem, method, and result.

## Layout

| Path | Contents |
|---|---|
| [papers/CATALOG.md](papers/CATALOG.md) | Full index |
| [papers/notes/](papers/notes/) | One markdown file per topic; every paper summarized |
| [code/](code/) | Source-only snapshots of BlindGuard and XG-Guard (no weights, no datasets) |

## Topics

1. [MAS attacks](papers/notes/01-mas-attacks.md)
2. [MAS defenses](papers/notes/02-mas-defenses.md)
3. [MAS benchmarks](papers/notes/03-mas-benchmarks.md)
4. [Surveys and SoKs](papers/notes/04-surveys.md)
5. [Prompt injection and tools](papers/notes/05-prompt-injection.md)
6. [Jailbreak, backdoor, privacy](papers/notes/06-jailbreak-backdoor-privacy.md)
7. [AI for security](papers/notes/07-ai-for-security.md)
8. [Trustworthy-ML foundations](papers/notes/08-foundations.md)

MAS notes follow the interaction-security scope used by [multiagent_security_corpus](https://github.com/BrookeYangRui/multiagent_security_corpus): LLM agents, a concrete security property, and a material interaction path. Adjacent agent-security and AI-for-security papers are kept as context, not mixed into that denominator.

## What is not in this repo

- Personal study notes or unpublished proposals
- Copyrighted PDFs
- Training checkpoints and generated dialogue dumps
