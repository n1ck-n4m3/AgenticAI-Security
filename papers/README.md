# 论文库目录

按**贡献类型**而不是「年份 / 会议」组织。顶会录用仍是筛选标准；文件夹回答的是「这篇在 MAS 安全里干什么」。

分类对齐 [BrookeYangRui/multiagent_security_corpus](https://github.com/BrookeYangRui/multiagent_security_corpus) 的 MAS 范围门槛（LLM 多智能体 + 明确安全性质 + 实质性交互路径），但本库是**研究阅读库**，不是他们的 SoK 证据集：我们额外保留单智能体 agent 安全、AI-for-Security、以及可迁移的 Trustworthy ML 经典。

文献 cutoff 参考 corpus：`2026-07-01`。2025–2026 补漏见 [`GAP_2025_2026.md`](GAP_2025_2026.md)。

## 怎么用

| 你想做的事 | 打开 |
|---|---|
| 看全库标题、链接、一句话定位 | [`CATALOG.md`](CATALOG.md) |
| 看 2025–2026 新补的顶会/优质会 | [`GAP_2025_2026.md`](GAP_2025_2026.md) |
| 走 G-Safeguard 族精读 | [`close_reads/`](close_reads/) |
| 62 篇旧导读（按原方向一/二/三） | [`guides/Agentic_AI_Security_Reading_Guide_2024-2026.md`](guides/Agentic_AI_Security_Reading_Guide_2024-2026.md) |

Public GitHub has markdown only. Local research checkout also stores `YYYY_VENUE_ShortName.pdf`.

## 目录树

```text
papers/
├── CATALOG.md
├── GAP_2025_2026.md
├── 01_mas_security/                 # 核心：LLM 多智能体安全
│   ├── attacks/
│   ├── defenses/
│   ├── benchmarks/
│   └── surveys/
├── 02_agent_security/               # 相邻：单智能体 / 工具 / 模型安全
│   ├── prompt_injection_tool_use/
│   └── jailbreak_backdoor_privacy/
├── 03_ai_for_security/              # 用 LLM 做安全（优先级靠后）
├── 04_foundations_trustworthy_ml/   # 可迁移的可信 ML 经典
├── close_reads/                     # 精读笔记与中文编译版
└── guides/                          # 深度导读与旧清单
```

## 分类规则（本库）

一篇论文只放一个主目录：

1. **MAS attacks**：失败机制主要依赖多 agent 交互（传播、串谋、路由劫持、消息篡改、拓扑推断、跨 agent 泄漏）。
2. **MAS defenses**：干预点在交互图、信誉、剪边、协议、共识或系统结构。
3. **MAS benchmarks**：主贡献是基准 / 评测协议 / 测量框架（即使也带攻击套件）。
4. **MAS surveys**：SoK / survey，主贡献是地图而不是新攻击或新防御。
5. **Agent security**：单 agent 提示注入、工具劫持、越狱、后门、隐私。MAS 论文会引用它们，但它们本身不是 MAS-primary。
6. **AI for security**：用 LLM 做漏洞检测 / fuzzing / SOC。
7. **Foundations**：对抗鲁棒、校准、OOD、验证、BFT 等，用来形成 self-healing 语言，而不是 MAS 证据。

混合论文按**主贡献**归档（与 corpus 的 `dominant_contribution` 一致）。例如 TAMAS、ASB 进 benchmarks；G-Safeguard 进 defenses，即使它也分析攻击。

## 当前研究主线（先读这些）

G-Safeguard → BlindGuard → XG-Guard 是图异常检测族。补漏之后，最该立刻对照的新文：

1. **When Embedding-Based Defenses Fail**（ICML 2026）— 直接打 embedding/图检测器。
2. **SentinelAgent / SentinelNet** — 同类图/信誉检测，但是不同监控位置。
3. **Control-Flow Hijacking**（ICLR 2026）+ **Malicious Code Execution**（COLM 2025）— 路由/权限，不是语义离群。
4. **Cowpox**（ICML 2025）+ **ResMAS / Byzantine Reliability**（AAAI 2026）— 更接近「恢复 / 结构韧性」，而不只是隔离。
5. **MASLeak**（USENIX Security 2026）+ **A2ASecBench**（ICLR 2026）— 黑盒 IP 泄漏与协议层基准。

精读笔记仍在 `close_reads/`，不随 PDF 搬家而重写。
