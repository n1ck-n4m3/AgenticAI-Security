# MAS 攻击与基准精读（P1）

2026-08-10 组会 P1：精读攻击/基准论文（含教授点名的 **TAMAS**、**Conjunctive Prompt Attacks**），并对照防御侧做局限与信任笔记。

本目录同时放 **英文原文 PDF** 与 **中文编译版 PDF**。中间源码在 `_arxiv_src/`、`_cn_build/`（可忽略）。

五篇论文的方法、公式、实验结论、局限与自愈启示已整理为：[`五篇攻击与基准论文_精读总结.md`](./五篇攻击与基准论文_精读总结.md)。

## 五篇为什么选这几篇

| 论文 | 角色 | 与组会/proposal 的关系 |
|------|------|------------------------|
| **TAMAS** | 教授点名；MAS 对抗基准 | Autogen/CrewAI、六类攻击、ERS（安全 vs 还能干活） |
| **Conjunctive Prompt Attacks** | 教授点名 | 触发键 + 隐藏模板单独都良性，路由会合才激活；现有句级 GAD 可能看不见 |
| **NetSafe** | 拓扑安全现象 | 密图更脆、幻觉放大；信任沿边传播 |
| **ASB** | 单智能体攻防基准 | G-Safeguard 族 PI/TA/MA 的形式化源头 |
| **CORBA** | 协作拒绝服务 | 语义良性的递归阻塞；「看起来正常」的可用性攻击 |

## 文件对照

| 英文原文 | 中文版 |
|----------|--------|
| `TAMAS_Benchmarking_Adversarial_Risks_in_Multi-Agent_LLM_Systems.pdf` | `TAMAS_中文版.pdf` |
| `Conjunctive_Prompt_Attacks_in_Multi-Agent_LLM_Systems.pdf` | `Conjunctive_中文版.pdf` |
| `NetSafe_Exploring_the_Topological_Safety_of_Multi-agent_System.pdf` | `NetSafe_中文版.pdf` |
| `ASB_Formalizing_and_Benchmarking_Attacks_and_Defenses.pdf` | `ASB_中文版.pdf` |
| `CORBA_Contagious_Recursive_Blocking_Attacks.pdf` | `CORBA_中文版.pdf` |

中文版由 arXiv LaTeX 源译后 XeLaTeX 编译。公式、引用、评测提示词/对话日志保持英文；专有名词（TAMAS、ASR、ARIA 等）保留原文。

## 同组会另外两份 P1 笔记

- 局限与可改进（防御五篇 + 本目录五篇）：[`../defenses/已读论文_局限与可改进.md`](../defenses/已读论文_局限与可改进.md)
- 信任：定义 / 涌现 / 传播 / 恶化 / 恢复：[`../../../ideas/trust_define_emerge_recover.md`](../../../ideas/trust_define_emerge_recover.md)
- 英文 canonical PDF 已迁到 [`../../01_mas_security/`](../../01_mas_security/)；本目录保留精读笔记与中文编译版。
