# 五篇 MAS 防御论文最终速通总览

> 用途：通宵后不用再翻原文。meeting 前按“总表 → 每篇一句话 → 90 秒回答”复习即可。

## 一张表记完

| 论文 | 它真正解决什么 | 输入/核心模型 | 训练信号 | 检测结果 | 干预 | 最大缺口 |
|---|---|---|---|---|---|---|
| G-Safeguard | 已知攻击检测 | 节点/边话语历史 + edge-aware GNN | 真实攻击标签 | Agent 攻击概率 | 隔离/剪边 | 依赖攻击标签 |
| BlindGuard | 未知攻击检测 | sentence embedding + self/neighbor/global + MLP | 正常图 + 人工噪声对比学习 | Agent 异常分 | 隔离 | 假设攻击形成语义离群 |
| XG-Guard | 未知攻击检测 + token 解释 | sentence/token 双流 GNN + theme | 正常图跨主题对比学习 | Agent 分 + token 热力图 | 隔离 | 可能只是跑题检测；解释验证弱 |
| GUARDIAN | 跨轮异常传播检测 | BERT + GCN + temporal Transformer + 双 decoder | 无标签重建 + information bottleneck | 节点/边重建异常 | 每轮删除最可疑 Agent | 同分布增量训练；误报/自污染 |
| Resilience | 系统结构抗故障规律 + 消息纠错 | 无训练网络；Challenger prompt + Inspector Agent | 无 | 没有统一风险分 | 质疑、检查、重写消息 | 单故障/合成攻击；无状态回滚 |

## 五篇各记一句话

1. **G-Safeguard**：我见过这种攻击，所以训练 GNN 把攻击者分出来，再剪掉传播边。
2. **BlindGuard**：我没见过攻击，但我只学正常群体；谁明显不像正常群体，谁可疑。
3. **XG-Guard**：不仅看整句，还看 token；谁偏离当前讨论主题、具体哪些词导致偏离，都给出来。
4. **GUARDIAN**：不只看这一轮，还看跨轮演化；正常节点和通信应该容易重建，重建失败就是异常。
5. **Resilience**：不先训练检测器，而是找出更抗故障的组织结构，并让 Agent 互相质疑、让 Inspector 修正消息。

## 方法演进主线

```text
已知攻击标签
G-Safeguard：监督分类
        ↓ 去掉攻击标签
BlindGuard：正常性/离群检测
        ↓ 增加细粒度和解释
XG-Guard：sentence + token + theme
        ↓ 增加跨轮传播建模
GUARDIAN：temporal graph reconstruction

另一条系统设计路线：
Resilience：拓扑韧性 + Challenger/Inspector 内容纠错
```

## 到底训练了什么？

```text
G-Safeguard：edge-aware GNN + 分类头
BlindGuard：融合 MLP/Linear + projection head；SentenceBERT 冻结
XG-Guard：sentence GNN + token GNN；文本 encoder 冻结
GUARDIAN：GCN + temporal Transformer + attribute/structure decoders
Resilience：不训练网络，只改 prompt 或增加 Inspector LLM
```

五篇都不重新训练 backbone LLM。

## 实验上最值得记的数字

- **XG-Guard**：24 个主组合平均 AUC 95.48，BlindGuard 为 78.18；监督 G-Safeguard 平均 AUC 98.63，仍略高。
- **GUARDIAN**：异常检测率平均超过 80%，峰值 94.74%；但 FDR 最高 30.67%，且每个数据集单独训练、只做同分布检测。
- **Resilience**：Hierarchical 平均下降约 5.51 点，Flat 10.54，Linear 23.72；代码受影响最大约 -22.56；C+I 在一个 Self-collab 设置中恢复 96.4% 的性能损失。

这些数字来自不同 benchmark，**不能横向宣布谁统一最好。**

## 老师最可能问的五个问题

### 1. 为什么都喜欢用图？

MAS 的风险不只在单条文本，而在“谁影响谁、错误沿哪条通信路径传播”。图把 Agent 变成节点、通信变成边，GNN 可以让节点吸收邻居信息。

### 2. 为什么有 GNN 还要 Transformer？

GNN 主要回答“当前图里邻居怎样影响我”；GUARDIAN 的 Transformer 回答“前几轮怎样一步步影响当前轮”。一个偏空间，一个偏时间。

### 3. 无监督是不是不用训练？

不是。BlindGuard、XG-Guard、GUARDIAN 都要训练检测网络，只是不使用真实攻击标签。只有 Resilience 的 Challenger/Inspector 基本是 training-free prompt/agent 机制。

### 4. 五篇真的修复系统了吗？

前三篇和 GUARDIAN 基本是隔离/删节点。Resilience 会改写消息，修复更深入一点，但都没有完整处理 memory poisoning、已执行 tool action、外部数据库和不可逆副作用。

### 5. 你的 self-healing idea 在哪里？

不是再做一个更高 AUC 的检测器，而是补上：

```text
多粒度检测证据
→ 根因诊断（Agent/message/memory/tool/edge）
→ 选择最小恢复动作
→ 从可信 checkpoint 回滚或重放
→ 独立 verifier 检查
→ 安全重新接入
```

## 五篇共同没有完成的闭环

```text
现有论文：Observe → Detect → Isolate / Rewrite

真正自愈：Observe
        → Detect
        → Diagnose root cause
        → Contain blast radius
        → Recover state/content/topology
        → Verify recovery
        → Reintegrate safely
```

你的 proposal 可以把五篇分别提供的东西拼起来：

- G-Safeguard：有监督结构传播信号；
- BlindGuard：未知攻击泛化；
- XG-Guard：token 级证据与解释；
- GUARDIAN：跨轮 trajectory 与边异常；
- Resilience：组织拓扑和主动内容纠错。

真正缺少的是**把这些检测证据转换成可验证恢复动作的控制器**。

## Meeting 90 秒完整回答

> 这五篇展示了 MAS 防御从检测到初步修复的演进。G-Safeguard 使用攻击标签训练 edge-aware GNN，检测强但依赖已知攻击；BlindGuard 只用正常数据和人工扰动进行对比学习，提高未知攻击泛化；XG-Guard 进一步联合 sentence 和 token 级 GNN，用主题偏离做细粒度异常检测和解释；GUARDIAN 把交互扩展成时序图，用 GCN、Transformer 和双重建 decoder 捕捉错误跨轮传播；Resilience 则不训练检测网络，而是研究拓扑，发现 hierarchical 对单故障更稳，并通过 Challenger 和 Inspector 质疑及改写消息。它们的共同局限是大多只隔离节点，少数只修正文本文本，没有诊断并恢复 memory、tool state 和外部副作用。因此下一步真正有价值的是建立 detect-diagnose-recover-verify-reintegrate 的 self-healing 闭环。

