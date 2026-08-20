# MAS Security（核心集）

本目录只收 **LLM 多智能体 + 具体安全性质 + 交互路径是机制一部分** 的论文。

| 子目录 | 主贡献 | 本地 PDF |
|---|---|---:|
| [`attacks/`](attacks/) | 攻击 / 威胁机制 | 26 |
| [`defenses/`](defenses/) | 防御 / 韧性 / 协议 | 18 |
| [`benchmarks/`](benchmarks/) | 基准 / 测量 / 评测框架 | 11 |
| [`surveys/`](surveys/) | Survey / SoK | 3 |

完整条目（含链接与一句话）见 [`../CATALOG.md`](../CATALOG.md)。2025–2026 新补篇目标了 ★，见 [`../GAP_2025_2026.md`](../GAP_2025_2026.md)。

## 和 G-Safeguard 族怎么连

```text
监督图检测          G-Safeguard
未知攻击离群        BlindGuard
token 可解释        XG-Guard
跨轮重建            GUARDIAN
结构+纠错           Resilience / ResMAS / Byzantine Reliability
embedding 失效      Embedding-Based Defenses Fail     ★ 必读
去中心信誉          SentinelNet / Credibility Scoring
传染与自愈          Prompt Infection / Cowpox
控制流而非语义      Malicious Code / ControlValve
黑盒泄漏            MASLeak / Topology Matters
协议层              A2ASecBench / BlockA2A / SAFEFLOW
合取/隐蔽信道       Conjunctive / CoMet / Secret Collusion
```
