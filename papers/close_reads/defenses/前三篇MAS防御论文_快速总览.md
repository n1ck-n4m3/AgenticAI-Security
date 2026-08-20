# 前三篇 MAS 防御论文快速总览

> 用途：赶进度、meeting前快速复习。详细公式和问答分别见三篇精读笔记。

## 一页结论

```text
G-Safeguard：有攻击标签 → 学习识别已知攻击者
BlindGuard：无攻击标签 → 学习正常群体，离群者可疑
XG-Guard：无攻击标签 → 在sentence和token两层寻找主题偏离，并解释可疑token
```

## 核心对比

| 项目 | G-Safeguard | BlindGuard | XG-Guard |
|---|---|---|---|
| 核心问题 | 已知攻击检测与传播阻断 | 未知攻击检测 | 未知攻击检测+token解释 |
| 训练数据 | 正常+真实攻击标签 | 仅正常图 | 仅正常图 |
| 原始文本粒度 | response历史+边消息历史 | sentence response | sentence+token |
| 图处理 | edge-aware多层GNN | 固定neighbor/global聚合+MLP | sentence/token双流GNN |
| 训练信号 | 真实0/1标签 | 人工方向性噪声 | 自己主题正配对、异图主题负配对 |
| 损失 | binary cross-entropy | 对比学习 | 跨主题对比学习 |
| 推理输出 | 攻击概率 | Agent异常分 | Agent异常分+token解释分 |
| 修复 | 隔离/剪传播边 | 隔离/剪边 | 剪入边和出边 |
| 最强点 | 监督条件下检测强、边语义细 | unknown-attack泛化 | 细粒度检测与解释 |
| 最弱点 | 依赖攻击标签 | 粗粒度、离群假设 | 主题偏离假设、解释未严格验证 |

## 每篇只记五句话

### G-Safeguard

1. 把MAS每轮交互建成动态话语图，Agent是节点，通信是有向边。
2. 节点与边都编码历史话语，edge-aware GNN聚合传播信息。
3. 用真实攻击标签和交叉熵训练节点分类器。
4. 检出高风险Agent后剪边，阻止有害消息继续扩散。
5. 强项是已知攻击检测；弱项是标签依赖、未知攻击泛化和修复深度。

### BlindGuard

1. 针对G-Safeguard需要真实攻击标签的问题，只用正常MAS图训练。
2. 用SentenceBERT编码response，再构造self、neighbor、global三种上下文。
3. 给正常节点向量加方向性噪声制造伪异常，通过对比学习塑造正常表示空间。
4. 推理时与当前群体越不相似越异常，再隔离Top-K节点。
5. 强项是unknown attack；弱项是正常多数和语义离群假设，且公开实现主要是固定聚合+小型MLP。

### XG-Guard

1. 针对整句embedding遗漏少量恶意token和黑盒检测问题，引入sentence/token双流。
2. 两条GNN分别编码整句和token视角，并用当前图均值构造两套theme prototype。
3. 自己图的主题是正样本，其他图的主题是负样本，只用正常图做对比学习。
4. 以到主题的距离计算两套异常分，再用协方差融合，并输出token解释热力图。
5. 强项是显著超过BlindGuard并提供细粒度证据；弱项是可能只会识别跑题、解释faithfulness不足、修复仍是隔离。

## 到底训练什么？

```text
G-Safeguard：训练edge-aware GNN + 攻击分类头
BlindGuard：训练融合Linear/MLP + contrastive projection head；SentenceBERT冻结
XG-Guard：训练sentence GNN + token GNN；SentenceBERT、prototype和covariance公式不训练
```

三篇都不需要重新训练backbone LLM。

## 实验结论

### G-Safeguard

- 在与训练攻击匹配时，监督检测非常强；
- 不同拓扑与backbone下多数有效；
- 工具攻击曾暴露语义/标签或观测面错配问题；
- 不能据此证明未知攻击和不可逆副作用修复。

### BlindGuard

- 明显超过通用无监督GAD；
- 未见攻击迁移时通常比攻击特定G-Safeguard更稳；
- 多数场景接近监督方法，但Top-3与3/8 corruption等设定偏理想化；
- 只实现observe-detect-isolate。

### XG-Guard

- 24个主组合平均AUC为95.48，BlindGuard为78.18；24/24全部更高；
- 平均ASR@3为11.15，BlindGuard为16.51；
- 监督G-Safeguard平均AUC为98.63、ASR为10.33，整体仍略强；
- 去token后平均AUC降至86.51；保留token但去fusion仅72.72，说明fusion是性能核心；
- 解释实验主要是两个热力图案例，缺少定量faithfulness评估。

## 三篇共同缺口：proposal空间

它们主要实现：

```text
Observe → Detect → Isolate
```

尚未完整实现：

```text
Diagnose攻击面
→ 定位污染源
→ 选择span/memory/tool/graph级恢复动作
→ 回滚不可逆副作用
→ 独立验证恢复
→ 安全重新接入
```

因此self-healing proposal最自然的增量不是再做一个更高AUC的检测器，而是把检测证据转成可验证的诊断与恢复闭环。

## 截至 2026-08-10 的后续工作判断

- **XG-Guard**：2025-12-21 首次上传 [arXiv](https://arxiv.org/abs/2512.18733)，随后正式发表于 [ACL 2026 Long Papers](https://aclanthology.org/2026.acl-long.1407/)；不是仍在投稿的预印本。
- **同基准是否已有论文全面超过 XG-Guard？**目前没有查到后来论文在 XG-Guard 的完整数据集、攻击、拓扑和指标上直接复现并全面超过它，因此不能宣布已有统一新 SOTA。
- **GroupGuard**（[arXiv:2603.13940](https://arxiv.org/abs/2603.13940)，2026-03-14）：面向多个恶意 Agent 的合谋攻击，training-free，采用持续图监测、蜜罐诱导和结构剪枝；威胁模型比 XG-Guard 更强，但论文只直接比较 G-Safeguard 等基线，没有与 XG-Guard 做同条件比较。
- **STAR**（[arXiv:2605.28104](https://arxiv.org/abs/2605.28104)，2026-05-27）：面向自适应协同攻击，training-free，并能在 sentence 级检测和改写误导信息；修复动作比 XG-Guard 的隔离更深，但实验设置不同且未直接比较 XG-Guard。

所以要分维度判断：**普通独立攻击的细粒度检测与解释看 XG-Guard；合谋攻击看 GroupGuard；真正纠正消息内容看 STAR。**三者都还不是完整的 self-healing 闭环。

## Meeting最短回答模板

对每篇只回答：

1. **问题**：上一代方法缺什么？
2. **方法**：输入、编码器、训练信号、异常分、修复各是什么？
3. **为什么有效**：哪个结构与攻击机制匹配？
4. **证据**：主表最关键的两组数是什么？
5. **局限/idea**：哪些威胁假设没覆盖，如何连接self-healing？
