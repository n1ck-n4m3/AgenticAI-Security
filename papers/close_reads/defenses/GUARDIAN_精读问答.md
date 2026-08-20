# GUARDIAN 精读问答笔记

> **论文**：GUARDIAN: Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling  
> **发表**：NeurIPS 2025  
> **定位**：无监督、跨轮时序图异常检测；覆盖幻觉放大、Agent 定向攻击和通信定向攻击。  
> **进度**：2026-08-10 已完成第一轮速通精读。  
> **五篇总览**：见 `五篇MAS防御论文_最终速通总览.md`。

## 30 秒速记

- **问题**：前面的图防御多把某一轮当作静态图，难以看到错误怎样跨轮传播。
- **图表示**：每个“Agent 在某一轮的状态”是节点，response 的 BERT embedding 是节点特征，跨轮通信是有向边。
- **方法**：两层 GCN 编码每轮图，Transformer 聚合历史轮次；两个 decoder 分别重建节点文本特征和通信结构。
- **检测直觉**：正常交互容易重建；重建误差大的节点或连接不符合正常规律，因此可疑。
- **训练**：不需要攻击标签，但需要按轮持续训练 GCN、Transformer 和双 decoder；它不是 training-free。
- **干预**：每轮把最可疑 Agent 及其关联边删除，再让剩余 Agent 继续协作。
- **结果**：最终任务准确率多数超过基线，异常检测率平均超过 80%；但每个数据集单独训练、只测同分布，误报率最高约 30.67%。
- **局限**：检测后仍主要是隔离；异常分组合与阈值实现说明不够清楚，在线训练还可能把漏检攻击逐渐学成“正常”。

## 一、这篇到底解决什么？

它把三类风险统一成一个问题：

| 风险 | 是否必须有人攻击 | 例子 |
|---|---:|---|
| 幻觉放大 | 否 | 一个 Agent 自己答错，其他 Agent 在后续轮次跟着相信 |
| Agent-targeted attack | 是 | 攻击者修改某个 Agent 的 system prompt，使它持续输出错误 |
| Communication-targeted attack | 是 | Agent 本身正常，但传输中的消息被篡改 |

共同规律是：**异常不会只停留在一条 response，而会沿通信关系跨轮传播。**因此 GUARDIAN 不只看“这句话像不像攻击”，而是看“这个节点及其通信历史是否符合正常的时空演化规律”。

## 二、时序图怎样构造？

Agent 的 response 写成：

$$
r_{t,i}=\phi_{t,i}(p_i,q,R_{t-1}).
$$

- $t$：第几轮；
- $i$：第几个 Agent；
- $p_i$：该 Agent 的角色 prompt；
- $q$：用户问题；
- $R_{t-1}$：上一轮它能收到的其他 Agent responses；
- $\phi_{t,i}$：Agent/LLM 的生成过程；
- $r_{t,i}$：Agent $i$ 在第 $t$ 轮生成的 response。

直译：**Agent 根据自己的角色、用户问题和上一轮收到的消息，生成这一轮回答。**

随后建立图序列：

$$
\{G_t\}_{t=1}^{T},\qquad G_t=(V_t,E_t,X_t).
$$

- $V_t$：第 $t$ 轮的 Agent 节点；
- $X_t$：把本轮 response 用 BERT 编成的节点向量；
- 边 $(v_{t-1,i},v_{t,j})$：第 $t$ 轮的 Agent $j$ 读取了上一轮 Agent $i$ 的消息。

### 和 G-Safeguard 的差别

```text
G-Safeguard：重点编码当前图中的节点历史和边消息历史，再做监督节点分类
GUARDIAN：显式保留 G1, G2, ..., GT 的轮次序列，再学习跨轮演化和重建
```

因此 GUARDIAN 的核心增量是 **temporal modeling**，不只是“又用了一个 GNN”。

## 三、整个网络架构

```text
每轮 responses
  ↓ BERT
节点特征 Xt + 通信结构 Et
  ↓ 两层 GCN
每轮节点表示 Zt
  ↓ Transformer 处理 Z1,...,ZT
包含历史信息的最终表示 ZT
  ├─ Attribute Decoder → 重建节点特征 X̂T
  └─ Structure Decoder → 重建通信结构 ÊT
  ↓
节点/边重建误差 → 异常分 → 删除最可疑 Agent
```

### 1. GCN：看当前图中的邻居

$$
H^{(l+1)}=\operatorname{ReLU}(\tilde D^{-1/2}\tilde A\tilde D^{-1/2}H^{(l)}W^{(l)}),
\qquad H^{(0)}=X_t.
$$

不需要背矩阵细节，只要理解：

- $H^{(l)}$：第 $l$ 层时每个节点的表示；
- $\tilde A$：哪些节点相连；
- $\tilde D$：防止邻居多的节点数值过大，做归一化；
- $W^{(l)}$：真正被训练的权重；
- 两层 GCN：一个节点可以融合两跳范围的信息。

一句话：**每个 Agent 不只保留自己的 response，还吸收相邻 Agent 的信息。**

### 2. Transformer：看跨轮历史

$$
\operatorname{Attn}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
$$

- $Q$：当前需要寻找什么历史信息；
- $K$：每段历史信息的“索引”；
- $V$：历史信息的实际内容；
- softmax：把相关性变成总和为 1 的注意力权重。

直觉：**当前轮不是平均参考所有过去轮次，而是自动挑更相关的历史交互。**

### 3. 双 Decoder：分别重建语义和结构

节点属性重建误差：

$$
R_X=X_T-\hat X_T,
\qquad
L_{att}=\frac{1}{|V_T|}\sum_i\lVert x_{T,i}-\hat x_{T,i}\rVert_2^2.
$$

意思是比较真实 response embedding 与模型重建的 embedding。差得越远，该 Agent 的文本行为越异常。

结构重建误差：

$$
R_E=E_T-\hat E_T.
$$

结构 decoder 用 binary cross-entropy 判断每对节点之间是否应该存在通信边。实际有边但模型认为不该有，或实际无边但模型认为应该有，都产生较大结构误差。

为什么需要两个 decoder：**文本异常和通信异常不是同一种信号，硬塞进一个重建目标容易相互干扰。**

## 四、Information Bottleneck 到底是什么？

公式为：

$$
L_{GIB}=I(X_t;Z_t)-\beta I(Z_t;Y_t).
$$

### 先解释 $I(A;B)$

$I(A;B)$ 叫 mutual information，可直观理解为：**知道 $A$ 以后，能帮我知道多少关于 $B$ 的信息。**

- $I(X_t;Z_t)$：压缩表示 $Z_t$ 保留了多少原始 response 信息；最小化它，要求不要什么细节都记住。
- $I(Z_t;Y_t)$：$Z_t$ 保留了多少与最终任务结果 $Y_t$ 有关的信息；前面有负号，最小化整体时反而希望它越大越好。
- $\beta$：控制“压缩无关细节”和“保留任务信息”的平衡。

直觉类比：把一整场 meeting 压成会议纪要。好的纪要应该删掉口头禅和重复内容，但保留决定最终结论的证据。

### 总损失

$$
L_{rec}=\alpha L_{att}+(1-\alpha)L_{stru},
$$

$$
L_{total}=L_{rec}+\lambda L_{GIB}.
$$

- $\alpha$：文本重建和结构重建谁更重要；
- $\lambda$：重建任务与信息压缩谁更重要。

论文实验认为 $\alpha\in[0.3,0.5]$、压缩相关参数 $\gamma\in[0.001,0.01]$ 较好。

### 对论文理论声明的正确理解

论文证明的是“互信息受到上界约束”，不是数学上证明“一定不会传播错误”。信息受限可能减少冗余和噪声，但**从互信息上界直接跳到阻止错误级联，仍需要实验和额外假设。**

## 五、异常检测和删除公式

$$
f:G_t\rightarrow\mathbb{R}^{|V_t|+|E_t|},
\qquad
V_t^*=\{v\in V_t\mid s_v>\tau\}.
$$

- $f$：整个异常检测器，不是单独指 GCN；它包含编码、时间聚合、重建和打分。
- $s_v$：节点 $v$ 的异常分。
- $\tau$：人为设定的风险阈值。
- 竖线 $\mid$：读作“满足……条件的”；这里表示所有满足 $s_v>\tau$ 的节点。
- $V_t^*$：被判定异常的节点集合。

删除后：

$$
G_t'=(V_t\setminus V_t^*,\ E_t\setminus E_{V_t^*}).
$$

即删除异常节点以及与其相连的边。

### 一个必须注意的实现问题

主文公式写的是“所有超过阈值 $\tau$ 的节点”，案例与实验描述却强调**每轮只删除异常分最高的一个 Agent**。而且主文没有给出一个非常明确的单式，说明属性误差和结构误差最终怎样合成 $s_v$。因此我们能确定总体机制，但阈值与最终打分细节的可复现性不够理想。

## 六、它到底训练什么？是实时的吗？

训练的是：

```text
两层 GCN
+ 跨轮 Transformer
+ Attribute Decoder
+ Structure Decoder
+ Information Bottleneck 相关参数
```

不重新训练底层 GPT、Claude、Llama。BERT 负责把 response 转成节点向量；论文没有把“微调 BERT”作为主要训练部分。

它是 **runtime 中逐轮运行、同时增量更新检测网络**：用较早轮次训练/适应，在后续轮次检测；新一轮又把历史与当前图合并，移除已检测异常节点后继续微调。

### 问：论文所说的“增量训练范式”到底是什么意思？

先用一句话概括：

> GUARDIAN 不把全部交互随机打散后一次性训练完，而是按照真实讨论轮次依次学习；第 1 轮学到的检测器继续用于第 2 轮，第 2 轮更新后的检测器继续用于第 3 轮，并在进入下一轮学习前剔除上一轮已经判定异常的节点。

可以把它写成下面的流程：

```text
第 1 轮图 G1
  → 用无监督重建损失训练检测器 θ1
  → 计算异常分
  → 删除/隔离检测出的异常节点，得到清理图 G1'

第 2 轮图 G2 + 清理后的历史图 G1'
  → 从 θ1 接着微调，而不是重新初始化
  → 得到 θ2
  → 检测并清理本轮异常，得到 G2'

第 3 轮图 G3 + G1' + G2'
  → 从 θ2 接着微调
  → 得到 θ3
  → ……
```

其中 \(\theta_t\) 表示第 \(t\) 轮时 GUARDIAN 检测网络的参数。直观上近似于：

$$
\theta_t\leftarrow\operatorname{FineTune}
\left(\theta_{t-1},\;G_{1:t-1}'\cup G_t\right).
$$

这不是论文单独给出的原公式，而是对其文字流程的直观改写：当前参数由上一轮参数继续更新，训练数据由清理后的历史交互图和当前图组成。

#### 1. 为什么叫“incremental”，而不是普通训练？

普通离线异常检测通常会：

```text
收集全部图 → 随机划分训练集/测试集 → 训练一次 → 固定模型测试
```

GUARDIAN则尊重时间顺序：

```text
较早轮次用于学习 → 检测较晚轮次 → 得到新数据后继续更新模型
```

所以“增量”有两层含义：

1. **数据逐轮增加**：每轮都有新的Agent response和通信边；
2. **参数连续更新**：第 \(t\) 轮不是从零训练，而是在第 \(t-1\) 轮参数基础上继续微调。

这里的“持续微调神经网络”指更新GUARDIAN自己的：

```text
GCN + 时序 Transformer + Attribute Decoder
+ Structure Decoder + Information Bottleneck相关参数
```

它**不是持续微调GPT、Claude、Llama等底层LLM**。

#### 2. “从交互历史中渐进学习”具体学到了什么？

它并不是把历史问答像记事本一样背下来，而是利用连续图学习正常协作的统计规律，例如：

- 某类任务中Agent回答向量通常怎样变化；
- 相邻Agent的信息通常怎样影响下一轮回答；
- 哪些通信边和角色组合经常出现；
- 正常讨论从分歧走向共识时，节点和边通常怎样演化。

这些规律被压进检测器参数和时序表示中。所谓“积累知识”，主要指参数 \(\theta_1\rightarrow\theta_2\rightarrow\theta_3\) 持续继承和更新，不代表底层LLM获得了新的永久知识。

#### 3. “动态适应新模式”是什么意思？

正常协作模式本来就会随轮次变化：

```text
第1轮：大家独立作答，分歧较大
第2轮：开始引用邻居理由
第3轮：逐渐收敛到共同答案
```

如果使用固定检测器，它可能把“后期大量共识”误认为异常，也可能无法识别攻击者后来改变的说法。增量微调允许检测器随着讨论阶段更新对“正常状态”的理解。

但论文实验是在**每个数据集单独训练、同分布测试**。因此这里证明的是对同一任务分布内的轮次变化具有适应性，还不能直接推出它能适应完全未知领域或任意新型攻击。

#### 4. “移除先前识别的异常”到底移除什么？

它不是删除底层LLM参数，也不是从世界上永久删除某个Agent程序，而是在后续协作和检测所使用的输入图中：

1. 移除被判异常的Agent节点；
2. 同时移除与该节点相连的通信边；
3. 后续训练尽量只使用清理后的图。

这样做有两个目的：

- **阻止传播**：异常Agent不能继续向邻居发送错误信息；
- **保护训练分布**：避免已知攻击内容被当作正常样本反复用于增量微调。

因此这里的“删除”更准确地说是**运行时隔离/图剪枝**，不是修复该Agent内部状态。

#### 5. 为什么无监督模型也可以一边训练一边检测？

因为训练不需要“正常/攻击”的真实标签。GUARDIAN学习重建当前图：

$$
L_{total}=L_{rec}+\lambda L_{GIB},
\qquad
L_{rec}=\alpha L_{att}+(1-\alpha)L_{stru}.
$$

- \(L_{att}\)：能否重建Agent response的节点特征；
- \(L_{stru}\)：能否重建通信结构；
- \(L_{GIB}\)：压缩无关信息、保留任务相关模式。

训练完成后，难以被当前模型重建的节点或边会得到较高异常分。因此它不是“先知道谁是攻击者再训练”，而是先学习多数交互呈现的规律，再把不符合规律的部分视为异常。

#### 6. “模型无关”是什么意思？

这里的model-agnostic不是说GUARDIAN本身没有模型，而是说它不依赖被保护LLM的内部结构。

GUARDIAN主要需要：

- 每个Agent生成的文本response；
- 哪个Agent向哪个Agent发送了消息；
- 消息属于哪一轮。

它不需要：

- GPT/Claude/Llama的模型权重；
- LLM内部隐藏层；
- LLM梯度；
- 修改或重新训练底层LLM。

因此不论Agent使用闭源API模型还是本地开源模型，只要能观察文本输出和通信关系，理论上都可以在外部接入GUARDIAN。

更准确的架构关系是：

```text
GPT / Claude / Llama：继续负责生成回答
                    ↓ 输出文本和通信日志
GUARDIAN：在外部把这些日志建成时序图，训练自己的异常检测网络
```

#### 7. 这种范式最危险的地方是什么？

它存在一个循环依赖：模型必须先正确识别异常，才能得到干净数据继续训练。

```text
正确检测攻击
  → 删除攻击节点
  → 后续训练数据更干净
  → 检测器可能越来越准确

漏检攻击
  → 攻击节点留在训练图中
  → 模型反复学习攻击行为
  → 攻击可能逐渐被当成“正常模式”

误报正常节点
  → 正常样本被删除
  → 学到的正常分布发生偏移
  → 后续可能产生更多误报
```

因此“移除异常后持续微调”既是GUARDIAN的适应机制，也是潜在的在线数据投毒和误差累积入口。论文没有充分解决如何利用可信缓冲区、人工确认、回滚或冻结参数来打断这一错误反馈闭环。

#### 最简单的生活化理解

把GUARDIAN想成一个每天参加公司会议的审计员：

- 第一天，它学习正常员工通常怎样发言和互相回应；
- 发现一个人持续制造异常后，先把他移出后续会议；
- 第二天，它带着第一天的经验继续观察，而不是失忆后重新学习；
- 随着会议推进，它逐渐理解这个团队自己的协作习惯。

好处是它越来越熟悉团队；风险是如果第一天把坏人当成正常员工，它也可能逐渐把坏人的行为学成“公司文化”。

这带来一个风险：

```text
漏检攻击 → 攻击数据留在增量训练集 → 模型逐渐把攻击当正常
误报正常节点 → 正常数据被删掉 → 学到的“正常”分布进一步偏移
```

所以“边训边防”有适应性，也有在线数据投毒和误差累积问题。

## 七、实验怎么设计，结论是什么？

### 设置

- 数据：MMLU、MATH、FEVER、Biographies；每个数据集随机抽 100 个问题，独立运行 3 次。
- backbone：GPT-3.5-turbo、GPT-4o、Claude-3.5-Sonnet，另测 Llama3.1-8B。
- Agent 数：主要为 4，扩展到 3-7。
- 每个数据集单独训练一个检测模型，属于 **in-distribution anomaly detection**。
- 三类场景：自然幻觉放大、首轮污染一个 Agent、轮间污染通信边。
- 指标：最终任务准确率、异常检测率、FDR、API calls、运行时间。

### 核心结果

1. 幻觉放大场景：平均比此前最佳基线高 4.2 个点；MATH 跨 backbone 高 7.1 个点，GPT-3.5 上最高高 15.4 个点。
2. Agent-targeted attack：MATH 比最佳基线高 4.3 个点。
3. Communication-targeted attack：MMLU 和 MATH 比最佳基线平均高约 3.6 个点。
4. 异常检测率平均超过 80%，峰值 94.74%。
5. FDR 最好是 8.32%，但 communication-targeted/MMLU 达 30.67%，说明某些场景每约 3 次干预就可能有 1 次误删。
6. 稀疏拓扑下仍有效：MATH/GPT-3.5 在 25%、50%、75% 连接率下分别为 52.2、56.1、57.3，均高于 DyLAN。
7. 时序版不保证每格都胜静态版：例如幻觉场景 GPT-4o/MMLU 是 GUARDIAN.s 86.4、GUARDIAN 84.9；MATH 在 5-7 Agents 时静态版也可能更高。
8. API calls 较少，因为每轮删节点后，需要继续调用的 Agent 也变少。

### 能不能说它比 G-Safeguard、BlindGuard、XG-Guard 好？

不能直接说。GUARDIAN 的主要表格比较 LLM Debate、DyLAN、SelfCheckGPT、Challenger 和 Inspector，没有在同一设置下对比前三个图防御。它证明的是**时序重建方案在自己的任务准确率实验里有效**，不是统一 benchmark 上的新冠军。

## 八、最重要的批判与 proposal 启示

### 方法局限

1. **不是完全未知分布泛化**：每个数据集单独训练，并明确聚焦同分布检测。
2. **在线自污染风险**：漏检样本可能进入后续训练，逐渐被正常化。
3. **异常分实现不够透明**：主文没有完整说明双重建误差如何变成最终 $s_v$。
4. **删除不是修复**：定位到通信异常后仍主要删 Agent，而不是只修复被污染的边或消息。
5. **误报并不低到可以忽略**：部分 FDR 接近 30%。
6. **规模证据有限**：只扩展到 7 个 Agent；在 MATH 中 Agent 变多后时序版还出现下降。
7. **IB 的理论边界不等于安全保证**：压缩信息并不能区分“冗余”和“关键但少见的正确证据”。

### 对 self-healing 的启示

GUARDIAN 比前三篇多了“跨轮追踪”和“通信边异常”两个重要信号，但恢复仍停在：

```text
Detect → Delete node → Continue
```

真正自愈可以继续做：

```text
检测异常 trajectory
→ 区分源头 Agent、被污染 Agent 与被篡改边
→ 只回滚受污染 memory/message/tool state
→ 从可信 checkpoint 重放
→ 独立 verifier 验证
→ 安全重新接入 Agent
```

## 九、Meeting 最短回答

> GUARDIAN 将多 Agent 的多轮交互建成时序属性图，用 GCN 编码每轮空间依赖、Transformer 编码跨轮历史，再通过节点属性和通信结构的双重建误差做无监督异常检测。它不需要攻击标签，但需要在线增量训练。检测后每轮删除最可疑节点，因此能同时缓解幻觉放大、Agent 攻击和通信攻击。实验显示最终准确率和异常检测率较强，但只做同分布、按数据集训练，误报最高约 30%，真正的修复仍是隔离而非状态恢复。

## 十、实验前全部内容：从问题到训练闭环完整串讲

### 1. 先把论文的出发点说成人话

多人讨论的危险不只是“某个Agent说错一句话”，而是：

```text
一个Agent说错
  → 下游Agent把错误当作上下文
  → 下游Agent重新组织、强化错误
  → 错误逐轮扩散，最后看起来像集体共识
```

GUARDIAN统一处理三类风险：

1. **幻觉放大**：没人攻击，某个Agent自然产生幻觉，其他Agent跟着相信；
2. **Agent-targeted attack**：攻击者修改某个Agent的prompt，使这个Agent主动输出错误；
3. **Communication-targeted attack**：Agent本身没坏，但Agent之间传输的消息被篡改。

前三类问题的共同点不是某个关键词，而是**异常内容沿着“谁听了谁”的路径跨轮传播**。因此只检查一条response、做多数投票或把各Agent当成独立个体，都可能漏掉最关键的传播信息。

论文用二元变量描述传播：

$$
h_{t,i}\in\{0,1\},\qquad \operatorname{err}_{t,i}\in\{0,1\}.
$$

- $h_{t,i}=1$：第$t$轮Agent $i$的回答存在幻觉；
- $\operatorname{err}_{t,i}=1$：第$t$轮Agent $i$的回答存在注入错误。

论文用

$$
\sum_{i=1}^{n}h_{t,i}\geq\sum_{i=1}^{n}h_{t-1,i}
$$

表达“被幻觉影响的Agent数可能逐轮增加”。这更像论文要研究的**级联传播模式**，不是任何MAS都必然满足的数学定律：如果后续Agent能够纠错，右边的错误数量也可能下降。

### 2. 一条Agent回答公式到底在说什么？

$$
r_{t,i}=\phi_{t,i}(p_i,q,\mathbb{R}_{t-1}).
$$

- $r_{t,i}$：Agent $i$在第$t$轮生成的文本response；
- $\phi_{t,i}$：该Agent的生成过程，可理解为“LLM + system prompt + 调用逻辑”；
- $p_i$：Agent自己的角色或系统prompt；
- $q$：用户原始问题；
- $\mathbb{R}_{t-1}$：它在上一轮能收到的其他Agent回答集合。

直译：**当前回答由自己的身份、原问题和上一轮收到的消息共同决定。**这也说明为什么错误能传播：错误一旦进入$\mathbb{R}_{t-1}$，就成为下一轮生成的输入。

### 3. 为什么要把讨论建成“离散时序属性图”？

每轮建立一个图：

$$
\mathcal G_t=(\mathcal V_t,\mathcal E_t,\mathbf X_t),
\qquad \{\mathcal G_t\}_{t=1}^{T}.
$$

- $\mathcal V_t$：第$t$轮的节点集合；
- $\mathcal E_t$：通信边集合；
- $\mathbf X_t$：所有节点的文本特征矩阵；
- $T$：当前观察到的最后一轮。

这里一个节点不是抽象的“永久Agent”，而是**Agent在某一轮的状态**：

$$
v_{t,i}=\text{Agent }i\text{在第}t\text{轮的状态}.
$$

所以同一个Agent在$t=1$和$t=2$对应两个时间状态$v_{1,i}$与$v_{2,i}$。这样才看得出它的答案怎样变化。

#### 节点属性：回答文本变成向量

$$
\mathbf x_{t,i}=\operatorname{BERT}(r_{t,i}).
$$

BERT在这里不是直接判断攻击，而是一个“文字转坐标”的编码器：把任意长度的response压成固定长度向量。语义相近的回答通常在向量空间更接近。把所有Agent的向量叠在一起，就是$\mathbf X_t$。

这一步只保留文本语义表示，并不会自动知道事实真伪。后面的图网络才根据邻居和历史判断这个向量是否符合协作规律。

#### 边：谁把谁的回答当成了上下文

$$
(v_{t-1,i},v_{t,j})\in\mathcal E
$$

表示第$t$轮的Agent $j$读取了第$t-1$轮Agent $i$的回答。这是有方向的：信息从$i$流向$j$。

直观上可以把整张时序图摊开：

```text
第1轮： A1   B1   C1
          \  ↓  /
第2轮： A2   B2   C2
          \  ↓  /
第3轮： A3   B3   C3
```

每个圆点是一轮中的Agent状态，每条箭头表示消息怎样进入下一轮。这样既能看到“谁说了异常内容”，也能看到“异常沿哪条路传下去”。

### 4. 全部网络一张图

```text
文本response + 通信日志
        ↓
BERT得到节点向量Xt；通信关系得到邻接矩阵Ae
        ↓
两层GCN：融合图邻居，得到每轮表示Zt
        ↓
Transformer：聚合Z1,…,ZT的跨轮历史，得到最终表示ZT
        ↓
 ┌─────────────────┴──────────────────┐
属性Decoder                         结构Decoder
重建X̂T                              重建ÊT
连续语义用MSE                       二值边用BCE
 └─────────────────┬──────────────────┘
      原图与重建图的差异 → 异常分
        ↓
隔离最高风险Agent及关联边
        ↓
用清理后的历史进入下一轮并继续微调检测器
```

它不是一个单独的GNN分类器，而是：

```text
BERT特征化 + GCN空间编码 + Transformer时间编码
+ 双重建Decoder + 信息瓶颈 + 增量训练/剪枝闭环
```

### 5. GCN到底在这里做什么？

论文使用两层GCN：

$$
\mathbf H^{(l+1)}=operatorname{ReLU}
\left(
\mathbf D_e^{-\frac12}\mathbf A_e\mathbf D_e^{-\frac12}
\mathbf H^{(l)}\mathbf W^{(l)}
\right),
\qquad \mathbf H^{(0)}=\mathbf X_t.
$$

逐块翻译：

- $l$：第几层网络，不是第几轮；
- $\mathbf H^{(0)}=\mathbf X_t$：进入第一层前，每个节点只有自己的BERT向量；
- $\mathbf W^{(l)}$：需要训练的权重，把旧特征变成网络需要的新特征；
- $\mathbf A_e$：邻接矩阵，告诉模型哪些节点相连；
- 左右两个$\mathbf D_e^{-1/2}$：按节点度数归一化，避免连接多的节点仅因邻居多就数值特别大；
- $\operatorname{ReLU}$：把负数截成0，增加非线性表达能力；
- $\mathbf H^{(l+1)}$：融合邻居后的新节点表示。

可以把一层GCN理解为每个Agent做一次：

```text
我的新笔记 = 我的旧笔记经过变换
           + 与我相连的邻居笔记经过变换和归一化汇总
```

一层看到一跳邻居，两层大致看到两跳传播路径。作者选两层，是在“看到传播关系”和“计算量/过度平滑”之间折中。

为什么不能只用MLP？MLP逐行处理每个Agent的向量，天然不知道谁听了谁。GCN把邻接关系直接写进计算，因此更适合识别“某个Agent的异常怎样影响邻居”。

需要注意：论文把通信描述成有向边，但公式采用标准对称归一化GCN，没有详细说明有向边如何处理、是否转成无向图，这是实现说明中的一个缺口。

### 6. Transformer为什么还需要？GCN不是已经看图了吗？

GCN擅长回答：**这一轮/局部图里，当前节点和邻居有什么关系？**

Transformer擅长回答：**前面多轮中，哪些历史状态对当前最重要？**

输入是GCN产生的序列：

$$
\{\mathbf Z_1,\mathbf Z_2,\ldots,\mathbf Z_T\}.
$$

注意力公式：

$$
\operatorname{Attn}(Q,K,V)
=\operatorname{softmax}
\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
$$

- $Q$（Query）：当前状态在寻找什么历史信息；
- $K$（Key）：每个历史状态的“检索标签”；
- $QK^\top$：当前状态与各段历史有多匹配；
- $\sqrt{d_k}$：缩放，避免数值过大让softmax过于极端；
- softmax：把匹配分变成总和为1的权重；
- $V$（Value）：被真正加权汇总的历史内容。

比如一个Agent本轮突然给出错误答案，Transformer可以回看：它前两轮是否一直正确、异常是否恰好发生在接收某条消息之后。单看当前response可能觉得合理，放到历史轨迹中就显得突变。

### 7. 为什么要两个Decoder？

GUARDIAN不直接输出“攻击/正常”标签，而是让网络回答两个问题：

1. 根据学到的正常规律，当前Agent的文本向量**本来应该长什么样**？
2. 根据学到的正常规律，当前通信拓扑**本来应该长什么样**？

#### 属性Decoder：重建回答语义

它用带ReLU的神经网络把$\mathbf Z_T$映射回：

$$
\hat{\mathbf X}_T=\operatorname{Dec}_{att}(\mathbf Z_T).
$$

残差是：

$$
\mathbf R_X=\mathbf X_T-\hat{\mathbf X}_T.
$$

训练损失为均方误差：

$$
\mathcal L_{att}=
\frac{1}{|\mathcal V_T|}
\sum_{i=1}^{|\mathcal V_T|}
\lVert\mathbf x_{T,i}-\hat{\mathbf x}_{T,i}\rVert_2^2.
$$

$\lVert\cdot\rVert_2^2$就是把每一维的差平方后相加。某节点的真实向量和重建向量差得越大，说明它的语义行为越不符合模型学到的常见模式。

#### 结构Decoder：重建通信关系

框架图给出的核心形式是：

$$
\hat{\mathcal E}_T\approx
\operatorname{sigmoid}(\mathbf Z_T\mathbf Z_T^\top).
$$

两个节点表示的点积越大，decoder越认为二者应当相连；sigmoid把任意实数压到$0$到$1$，解释为存在边的概率$p_{ij}$。

训练用二元交叉熵：

$$
\mathcal L_{stru}
=-\frac{1}{|\mathcal V_T|^2}
\sum_{i,j}
\left[
I_{(i,j)\in\mathcal E_T}\log p_{ij}
+I_{(i,j)\notin\mathcal E_T}\log(1-p_{ij})
\right].
$$

$I_{条件}$是指示函数：条件成立取1，否则取0。实际有边时惩罚“预测边概率太低”，实际无边时惩罚“预测边概率太高”。

结构残差为：

$$
\mathbf R_{\mathcal E}=\mathcal E_T-\hat{\mathcal E}_T.
$$

第$i$行残差的范数越大，说明与节点$i$相关的通信模式越反常。

为什么不共用一个decoder？因为文本向量是连续数，适合MSE；边是0/1离散关系，适合sigmoid+BCE。分开重建可以避免两类信号互相干扰，并能用$\alpha$调整二者的重要性。

严格地说，$\mathbf Z_T\mathbf Z_T^\top$天然是对称矩阵，而论文的通信边是有向的。若没有额外的源/目标投影，这个简单decoder无法完整区分$i\to j$与$j\to i$；论文没有充分解释这一点。

### 8. 无监督异常检测为什么能成立？

核心假设是：

> 正常协作模式占多数、反复出现；异常比较少且偏离常态。受容量约束的autoencoder容易学会重建多数正常模式，却较难精确重建少见异常。

所以检测不是：

```text
看过“攻击”标签 → 学会攻击类别边界
```

而是：

```text
学习正常图怎样演化 → 重建不像的节点/边得到大残差 → 判为可疑
```

这也是它可以检测未知攻击的理论来源，但不是无条件保证。如果攻击在训练图中很多、持续时间很长，或模型容量大到能把异常也记住，异常同样可能被低误差重建。

### 9. 形式化检测和删除公式

$$
\min_f\mathcal L(f),
\qquad
f:\mathcal G_t\rightarrow
\mathbb R^{|\mathcal V_t|+|\mathcal E_t|}.
$$

- $f$：完整GUARDIAN检测器，而不是只指GCN；
- $\mathcal L(f)$：训练整个检测器的损失；
- $\mathbb R^{|V|+|E|}$：输出一个实数向量，给图中的节点和边提供异常分。

异常节点集合：

$$
\mathcal V_t^*=\{v\in\mathcal V_t\mid s_v>\tau\}.
$$

- $s_v$：节点$v$的异常分；
- $\tau$：阈值；
- $\mid$：读作“满足”；
- 整个式子：从所有节点中挑出异常分超过阈值的节点。

清理图：

$$
\mathcal G_t'=
(\mathcal V_t\setminus\mathcal V_t^*,
\mathcal E_t\setminus\mathcal E_{\mathcal V_t^*}).
$$

$A\setminus B$表示从集合$A$里去掉$B$。也就是移除异常Agent状态，并移除与它关联的通信边。

论文可以确定属性残差和结构残差都会参与异常判断，但没有在主文给出一个完整、可复现的$s_v$融合公式。概念上可理解为：

$$
s_i\ \text{随}\ 
\lVert\mathbf R_X(i,:)\rVert
\ \text{和}\ 
\lVert\mathbf R_{\mathcal E}(i,:)\rVert
\ \text{增大而增大},
$$

但这只是机制说明，不应冒充论文给出的精确公式。另外，形式化定义选出所有$s_v>\tau$的节点，框架图和案例却采用“每轮删除最高分的一个节点”。后者更保守，可减少一次误删太多正常Agent的风险。

### 10. Information Bottleneck不是简单的“降维”

$$
\mathcal L_{GIB}
=I(\mathbf X_t;\mathbf Z_t)
-\beta I(\mathbf Z_t;\mathbf Y_t),
\qquad k<d.
$$

$I(A;B)$叫互信息。概率论直觉上，它衡量“A和B绑定得多紧”：知道A后，能减少多少对B的不确定性。

- $\mathbf X_t$：原始BERT节点特征；
- $\mathbf Z_t$：压缩后的图表示；
- $\mathbf Y_t$：协作任务的结果；
- $I(X;Z)$：$Z$记住了多少原始细节；最小化它，要求少背噪声、重复句和无关细节；
- $I(Z;Y)$：$Z$保留了多少与任务结果有关的信息；因为前面是负号，最小化总式时会尽量让它变大；
- $\beta$：两种目标的平衡权重。

最好的直觉是“会议纪要”：原始会议$X$很长，纪要$Z$更短，但仍应保留决定最终结论$Y$的证据。

$k<d$确实包含维度压缩，但信息瓶颈比普通降维更强：普通降维只要求向量变短，IB要求**有选择地忘掉与任务无关的信息**。

论文总损失是：

$$
\mathcal L_{rec}
=\alpha\mathcal L_{att}
+(1-\alpha)\mathcal L_{stru},
$$

$$
\mathcal L_{total}
=\mathcal L_{rec}+\lambda\mathcal L_{GIB}.
$$

- $\alpha$大：更重视文本语义重建；
- $\alpha$小：更重视通信结构重建；
- $\lambda$大：信息压缩约束在总训练中影响更大。

附录用$\mathcal L_{rec}\approx-I(Z;Y)$把目标近似改写为“重建损失 + $\gamma I(X;Z)$”。这说明$Y$不是恶意Agent标签，监督信号仍主要来自自重建。不过论文没有充分给出互信息项的具体估计器和训练实现，因此IB的落地可复现性弱于GCN、Transformer和双重建损失。

### 11. 两条“信息上界定理”应该怎样读？

论文声称：

$$
I(\mathbf x_{t,i};\mathbf x_{t,j})
\leq \eta I(\mathbf x_{t,i};\mathbf Y_t),
$$

并将其解释为Agent之间的信息流被压缩率$\eta$约束，从而减少错误级联。它还给出：

$$
I(\mathbf Z_{1:t-1};\mathbf Z_t)
\leq
\mathbb E\left[
\log\frac{P(\mathbf Z_t\mid\mathbf Z_{1:t-1})}{Q(\mathbf Z_t)}
\right],
$$

意思是历史表示与当前表示的互信息可以被一个带先验$Q(Z_t)$的变分表达式上界约束。

正确理解是：这些式子给出了**信息量约束的理论视角**，不等于证明系统一定不会传播错误。尤其附录第一条证明把数据处理不等式写成

$$
I(x_i;x_j)\le I(x_i;z_j),
$$

但如果$z_j$确实是$x_j$的压缩表示，标准数据处理不等式通常应给出相反方向

$$
I(x_i;z_j)\le I(x_i;x_j).
$$

因此该证明至少缺少额外假设或存在不等号方向问题，不能把它当作严格的防级联安全保证。

### 12. 到底训练哪些网络？一步训练发生了什么？

主要训练的是GUARDIAN自己的：

```text
GCN权重W
+ Transformer的Q/K/V投影、前馈层等参数
+ 属性Decoder参数
+ 结构Decoder相关参数
+ 信息瓶颈相关参数
```

不是重新训练GPT、Claude、Llama。论文只说用BERT生成节点特征，没有清楚说明是否联合微调BERT；主方法的学习重点是其后的检测网络。

一次训练迭代可直观写成：

```text
1. 输入当前及历史时序图
2. GCN + Transformer编码成ZT
3. 两个Decoder生成X̂T和ÊT
4. 计算Latt、Lstru和GIB项
5. 合成Ltotal
6. 反向传播：调整GUARDIAN参数，使总损失下降
7. 用重建残差算异常分并隔离最高风险节点
```

因为没有$y_i=0/1$攻击标签，所以它训练的不是攻击分类边界，而是“能压缩并重建常见时空图规律的函数”。

### 13. 增量训练怎样形成运行时闭环？

```text
G1 → 训练θ1 → 检测/清理得到G1'
G1' + G2 → 从θ1继续训练得到θ2 → 检测/清理G2'
G1' + G2' + G3 → 从θ2继续训练得到θ3 → ……
```

近似写成：

$$
\theta_t\leftarrow
\operatorname{FineTune}
(\theta_{t-1},\mathcal G_{1:t-1}'\cup\mathcal G_t).
$$

这是对论文流程的直观改写，不是论文原式。

为什么这么设计：

1. 真实MAS数据按轮到达，按时间学习比随机打散更符合部署；
2. 正常讨论模式也会从“独立作答”逐渐变成“互相引用并达成共识”，模型需要适应阶段变化；
3. 把已识别异常从历史训练图移除，既阻断传播，也避免模型把已知攻击反复学成正常。

它属于**轮级在线/近实时防御**：必须先拿到本轮response和通信关系，才能检测并影响下一轮；它不是token尚未生成时的即时拦截。

最大风险是反馈闭环：漏检攻击会让污染数据继续进入增量训练，误报则会从正常分布中删掉正确样本。因此边训边防既是适应机制，也是潜在的在线投毒和错误累积入口。

### 14. “model-agnostic”到底指什么？

GUARDIAN只需要外部可观测信息：

- Agent输出的response；
- 哪个Agent把消息发给了谁；
- 消息属于哪一轮。

它不需要LLM权重、隐藏层或梯度，也不要求修改底层LLM：

```text
GPT / Claude / Llama负责回答
              ↓ 文本和通信日志
GUARDIAN在外部建图、训练自己的检测器、隔离异常节点
```

所以“模型无关”不是GUARDIAN本身没有神经网络，而是它可以作为外部runtime wrapper保护不同开源或闭源LLM。

### 15. 为什么整套设计看起来合理？

| 设计 | 针对的问题 | 直观作用 |
|---|---|---|
| 时序属性图 | 错误沿通信关系跨轮传播 | 同时保存谁说了什么、谁听了谁、发生在哪轮 |
| BERT | 原始文本不能直接进入图网络 | 把response变成固定长度语义向量 |
| GCN | 单看Agent自身会忽略邻居依赖 | 汇总局部传播路径 |
| Transformer | 静态图看不到跨轮突变和长期影响 | 选择性回看历史 |
| 双Decoder | 文本异常与通信异常数据类型不同 | 分别重建连续语义和二值拓扑 |
| 无监督重建 | 真实攻击标签稀缺且攻击会变化 | 学常态，再找偏离常态的对象 |
| Information Bottleneck | 图密集、消息重复、模型可能死记噪声 | 强迫表示保留少而有用的信息 |
| 增量训练 | 协作模式随轮次变化 | 带着历史经验逐轮适应 |
| 每轮删一个节点 | 阻止异常继续传播 | 保守隔离，同时减少API调用 |

### 16. 最后用一个故事把全流程钉死

四个Agent讨论一道题。第一轮，A因为幻觉给出错误答案，B、C、D正确。

1. GUARDIAN把四段回答用BERT变成四个向量，并记录消息箭头；
2. 第二轮C引用了A，于是C也答错；图上出现A第一轮到C第二轮的传播路径；
3. GCN让C的表示包含邻居A的影响；Transformer又看到C是接收A消息后才突然偏离历史；
4. 属性Decoder难以重建A/C的异常语义轨迹，结构Decoder检查通信关系是否异常；
5. A或C得到较高异常分，其中最高的一个被先隔离，关联边被切断；
6. 剩余Agent继续下一轮，GUARDIAN带着清理后的历史继续微调；
7. 若剩余图还有高风险节点，再隔离一个，直到正常Agent达成正确共识。

一句话收束：

> GUARDIAN不是靠攻击标签认坏人，而是把多Agent讨论当成一部带人物关系的连续剧：GCN看人物关系，Transformer看前情提要，双Decoder尝试复原正常剧情；哪位角色或哪条关系最复原不像，谁就最可疑，然后先把最可疑者隔离，再让剩余团队继续讨论。

## 十一、GCN、双重建、无监督与增量训练易混概念

### 1. GCN和GNN是什么关系？

GNN（Graph Neural Network）是总称，GCN（Graph Convolutional Network）是其中一种具体网络：

```text
GNN
├── GCN：归一化后求和/平均邻居信息
├── GAT：用注意力决定不同邻居的重要性
├── GraphSAGE：采样并聚合邻居
└── 其他图网络
```

因此“为什么不用GNN”这个问题的答案是：**论文已经用了GNN，只是具体选择了GCN这一分支。**

一层GCN可以简化理解为：

$$
h_i^{(l+1)}=operatorname{ReLU}
\left(\sum_{j\in N(i)}c_{ij}W^{(l)}h_j^{(l)}\right).
$$

- $h_i^{(l)}$：节点$i$在第$l$层的表示；
- $N(i)$：节点$i$的邻居；
- $W^{(l)}$：这一层需要训练的权重；
- $c_{ij}$：按节点度数得到的归一化系数；
- 求和：收集邻居消息；
- ReLU：增加非线性。

GCN类似图上的卷积：图片卷积汇总固定网格中的相邻像素，GCN汇总图中通过边连接的邻居。

### 2. 为什么用两层GCN？

一层GCN传播一跳信息，两层传播两跳信息：

```text
A → B → C

一层后：B知道A，C知道B
两层后：C还能间接知道A
```

这适合错误传播场景：即使C没有直接读取A，也可能通过B受到A影响。

两层不是数学上唯一正确的数字，而是经验折中：

- 一层可能只能看到直接邻居；
- 两层能看到短级联路径；
- 太深会增加计算量，并可能发生oversmoothing，即不同节点反复平均后越来越相似，反而难以区分异常。

MAS实验中的图通常较小、讨论轮次有限，因此作者选择两层兼顾范围与效率。换成GAT、GraphSAGE或更多层理论上都可以，但需要重新实验验证。

### 3. 为什么连续文本向量用MSE？

假设真实BERT向量和重建向量为：

$$
x=[0.2,-0.7],\qquad \hat x=[0.1,-0.3].
$$

MSE计算：

$$
(0.2-0.1)^2+[-0.7-(-0.3)]^2=0.17.
$$

每个维度都有“距离多远”的概念，所以直接测坐标差距很自然。平方还有两个作用：

1. 正负误差不会相互抵消；
2. 大误差会受到更重惩罚。

从概率角度看，如果假设连续向量的重建误差近似高斯噪声，那么最小化MSE等价于最大化观测向量的似然。

MSE并非唯一选择，也可使用cosine distance等；论文选择MSE主要因为节点属性是连续向量且实现简单稳定。

### 4. 为什么0/1通信边用sigmoid+BCE？

一条边的真实标签只有两种：

$$
y_{ij}=1\quad\text{有边},\qquad y_{ij}=0\quad\text{无边}.
$$

网络先产生任意实数logit $a_{ij}$，sigmoid将其转换成概率：

$$
p_{ij}=\sigma(a_{ij})=\frac{1}{1+e^{-a_{ij}}}\in(0,1).
$$

BCE为：

$$
L_{ij}=-[y_{ij}\log p_{ij}+(1-y_{ij})\log(1-p_{ij})].
$$

- 若实际有边，$y=1$，只剩$-\log p$，训练会推动$p\rightarrow1$；
- 若实际无边，$y=0$，只剩$-\log(1-p)$，训练会推动$p\rightarrow0$。

从概率角度，边是Bernoulli二项变量，最小化BCE等价于最大化正确0/1边出现的似然。因此：

```text
连续数值“差多少” → MSE
二元事件“有还是没有” → sigmoid产生概率 + BCE判断概率是否正确
```

### 5. 为什么叫无监督训练？

因为训练时不需要人工给出：

$$
y_i=0\text{（正常）或}1\text{（攻击）}.
$$

它的训练目标直接来自输入本身：

```text
输入真实节点属性X → 要求重建X̂接近X
输入真实邻接矩阵E → 要求重建Ê接近E
```

所以严格说它具有self-supervised reconstruction的味道；图异常检测论文通常仍把“没有异常标签”的这种训练称为无监督。

模型先学习多数数据的常见规律，检测时再把高重建误差视为异常。它隐含假设异常较少；如果攻击大量进入训练数据，模型也可能学会重建攻击。

### 6. 增量训练是不是每个$t$交给Transformer学习？

不是。这里有两条不同的“时间线”：

#### 时间建模

在一次forward中：

$$
G_1\xrightarrow{GCN}Z_1,\ldots,
G_t\xrightarrow{GCN}Z_t,
$$

然后Transformer读取：

$$
[Z_1,Z_2,\ldots,Z_t]
$$

来学习跨轮依赖。这叫temporal modeling。

#### 增量训练

新一轮$G_t$到达后，从上一轮参数$\theta_{t-1}$继续反向传播：

$$
\theta_t\leftarrow
\operatorname{Optimize}(\theta_{t-1},G_{1:t-1}'\cup G_t).
$$

更新的不是只有Transformer，而是整套可训练GUARDIAN网络。区别可记成：

```text
Transformer看多个t：数据在时间维度怎样关联
增量训练跨多个t更新θ：网络参数怎样持续学习
```

### 7. 哪些权重需要训练？

可训练参数主要包括：

1. **GCN**：每层$W^{(0)},W^{(1)}$及bias；
2. **Transformer**：$W_Q,W_K,W_V,W_O$、前馈网络、LayerNorm参数等；
3. **属性Decoder**：MLP各层的weight和bias；
4. **信息瓶颈/压缩投影**：如果实现为显式投影或变分层，对应的网络参数也需训练。

结构Decoder若严格采用图中的

$$
\hat E=\sigma(ZZ^\top)
$$

则内积和sigmoid本身没有额外权重，但$Z$由前面的可训练网络产生，所以结构损失仍会反向更新GCN和Transformer。

$\alpha,\lambda,\beta$是人为选择的超参数，不是普通反向传播学习的weight。论文也没有清楚说明BERT是否联合微调，因此不能确定地把BERT参数计入GUARDIAN主要训练权重。

### 8. 网络如何“收敛”？

每次forward后计算：

$$
L_{total}
=\alpha L_{att}+(1-\alpha)L_{stru}+\lambda L_{GIB}.
$$

反向传播计算每个参数对损失的影响，然后优化器执行：

$$
\theta\leftarrow\theta-\eta\frac{\partial L}{\partial\theta},
$$

其中$\eta$是学习率。重复训练后，如果重建损失不再明显下降、验证指标稳定，或达到预设epoch数，就认为本阶段训练收敛。

神经网络损失是非凸的，因此只能说优化到了一个较稳定的局部解，不能保证全局最优。增量场景的数据还会不断变化，所以它更像持续追踪当前分布，而不是永久收敛一次后永远不动。论文没有充分交代每个时间步的具体epoch数和停止准则。

### 9. 前半部分整体是不是Encoder？

可以近似这么说，但严格划分为：

```text
BERT + 建图                    → Graph Preprocessing
GCN                           → Attributed Graph Encoder
Transformer                   → Time Information Encoder
GCN + Transformer             → 整体时空Encoder
Attribute/Structure Decoder   → 双Decoder
重建误差和节点删除             → Detection/Mitigation
Information Bottleneck        → 作用在潜表示Z上的训练约束
```

因此从输入图到潜在表示$Z_T$之前可统称encoder side，但BERT/建图更准确地叫预处理；论文正式命名的两个encoder是GCN和Transformer。

## 十二、总损失、数据流与训练/测试设计

### 1. 总损失中的三项分别约束什么？

$$
L_{total}=\alpha L_{att}+(1-\alpha)L_{stru}+\lambda L_{GIB}.
$$

它不是三种互不相关的检测器，而是三个训练要求共同拉动同一套网络参数：

| 损失 | 比较/约束的数据 | 要网络学会什么 |
|---|---|---|
| $L_{att}$ | 真实文本矩阵$X_T$与重建矩阵$\hat X_T$ | 保留并重建Agent回答的语义规律 |
| $L_{stru}$ | 真实邻接矩阵$E_T$与预测边概率$\hat E_T$ | 重建正常通信拓扑 |
| $L_{GIB}$ | 原始表示$X$、压缩表示$Z$和任务结果$Y$的互信息 | 不要死记全部输入，只保留较有用的信息 |

$\alpha$平衡语义和结构重建，$\lambda$平衡重建能力与信息压缩。它们通常是人工设置的超参数，不是神经网络自动学习的weight。

三项目标存在张力：$L_{att}$和$L_{stru}$要求$Z$保留足够信息来重建输入，$L_{GIB}$又要求$Z$不要把输入完整照抄。好的$Z$应该处在“能重建常态，但不能无脑记忆所有细节”的中间状态。

### 2. 一个训练样本在网络中的表示

一个问题$q$会触发一次多Agent协作episode。第$t$轮的数据可表示为：

$$
G_t=(V_t,E_t,X_t).
$$

假设有$N$个Agent，BERT维度是$k$，GCN潜表示维度是$d$：

| 数据 | 典型形状 | 内容 |
|---|---:|---|
| $X_t$ | $N\times k$ | 第$t$轮N个Agent的BERT response向量 |
| $A_t/E_t$ | $N\times N$或边集合 | 谁向谁发送了消息 |
| $H_t^{(1)}$ | $N\times d_1$ | 一层GCN后的节点表示 |
| $Z_t$ | $N\times d$ | 两层GCN后的本轮图表示 |
| $[Z_1,\ldots,Z_T]$ | 带时间轴的张量 | Transformer的跨轮输入 |
| $Z_T^{time}$ | $N\times d$ | 融合历史后的当前节点表示 |
| $\hat X_T$ | $N\times k$ | 属性Decoder重建的文本特征 |
| $\hat E_T$ | $N\times N$ | 结构Decoder预测的边概率 |

论文在GCN输出和Transformer输出处都使用$Z_T$记号，容易混淆；理解时可把后者临时记成$Z_T^{time}$。

### 3. 数据从输入到反向传播怎样流动？

```text
用户问题q
  ↓
N个Agent在第t轮产生response r(t,i)
  ↓
BERT编码 → Xt；通信日志 → Et/At
  ↓
两层GCN逐轮编码 → Z1,…,ZT
  ↓
Transformer沿时间轴聚合 → ZT(time)
  ↓                         ↓
属性Decoder                  结构Decoder
得到X̂T                      得到ÊT
  ↓                         ↓
MSE得到Latt                  BCE得到Lstru
  └────────────┬────────────┘
             加入LGIB
                 ↓
              Ltotal
                 ↓
反向传播更新GCN、Transformer、属性Decoder及IB相关参数
                 ↓
用节点/边重建残差计算异常分，隔离最高风险节点
                 ↓
清理图进入下一轮增量训练
```

结构Decoder若采用$\sigma(ZZ^\top)$，本身可以没有weight，但$L_{stru}$的梯度仍通过$Z$反向更新Transformer和GCN。

### 4. 训练数据和评价数据从哪里来？

论文使用四个数据集：

- MMLU：57个学科的多选知识题；
- MATH：完整数据集含12,500道竞赛数学题；
- FEVER：完整数据集含185,445条事实核验claim；
- Biographies：524位计算机科学家的真实传记信息。

实验并未使用每个完整数据集，而是从每个数据集中随机抽取100个问题，并进行3次独立测试运行。一个问题会形成一次多Agent讨论episode及其时序图序列。

### 5. 它是不是常规train/test split？

不是。论文明确说不采用传统无监督异常检测中的随机数据划分，而是：

```text
同一个协作episode中
较早时间步 → 训练/适应检测器
较晚时间步 → 进行异常检测
新时间步到达 → 用清理后的历史继续微调整套网络
```

而且每个数据集单独训练一个检测模型：MMLU模型不直接拿去零样本检测MATH，MATH模型也不直接测试FEVER。因此实验属于in-distribution anomaly detection。

实验中的“无监督”只表示训练时不用正常/恶意节点标签，不表示评价阶段没有ground truth：数据集正确答案用于计算最终准确率；模拟攻击时攻击Agent/边的身份是已知的，用来计算异常检测率与FDR，但这些攻击标签不应进入重建损失训练。

### 6. 三种安全场景怎样生成？

1. 幻觉放大：不人工指定攻击者，观察LLM自然错误如何传播；
2. Agent-targeted：第一轮随机选择1个Agent进行攻击；
3. Communication-targeted：在中间轮次随机干扰多条通信边。

主实验通常使用4个无角色差异的Agent，另测3-7个Agent；主要采用完全连接图，并额外测试25%、50%、75%连接率的稀疏图。backbone包括GPT-3.5-turbo、GPT-4o、Claude-3.5-sonnet和Llama3.1-8B，使用zero-shot CoT。

### 7. 训练/测试设计中没有交代清楚的地方

论文没有报告标准的80/20或train/validation/test比例，也没有充分说明：

- 100个问题的先后顺序怎样确定；
- 检测器参数是否跨问题episode持续继承，还是每个问题重置；
- 每个时间步微调多少epoch、停止条件是什么；
- 是否存在独立validation set来选择$\alpha,\lambda,\beta$；
- 当前图是先参与微调再打分，还是先用上一轮参数打分再训练。

因此最准确的评价是：这是一种按时间展开的在线/增量、同分布重建检测实验，而不是严格独立held-out测试集上的泛化实验。不能据此直接声称模型能零样本泛化到新领域或全新协作分布。

## 十三、幻觉为何传播、实验最终结论与GIB意义

### 1. 幻觉为什么会在MAS中传播？

每个Agent的当前回答把上一轮其他Agent的输出作为上下文：

$$
r_{t,j}=\phi_{t,j}(p_j,q,R_{t-1}).
$$

一旦错误回答进入$R_{t-1}$，它就不再只是“别人的观点”，而成为下游LLM下一次生成的输入证据。传播通常经过：

```text
Agent A首次幻觉
→ B/C把A的回答放入context
→ B/C将错误重新表述，并补充看似合理的推理
→ 同一错误在上下文中出现多次
→ 后续Agent把重复和共识误当成可信度
→ 错误逐轮放大
```

关键机制包括：LLM没有天然事实验证器；错误可能语义流畅；Agent之间不是统计独立的；多数投票在大家共享同一污染源时也会失效；全连接拓扑会让一个错误迅速暴露给所有Agent。

论文用受幻觉影响节点数非递减来描述所研究的级联模式，但这不是普适定律；如果下游Agent具备有效验证能力，幻觉也可能被纠正。

### 2. 最终实验怎样总结？

- 幻觉放大：相对已有最佳基线平均提升4.2个百分点；MATH跨backbone提升7.1点，GPT-3.5上最高提升15.4点。
- Agent-targeted：MATH上比最佳基线提升4.3点。
- Communication-targeted：MMLU和MATH上比最佳基线平均提升约3.6点。
- 异常检测率：平均超过80%，最高94.74%。
- 误报：FDR最好8.32%，但communication-targeted/MMLU达到30.67%，即该场景约每3次干预可能有1次误删。
- 拓扑：25%、50%、75%稀疏连接下仍优于表中基线。
- 成本：删除节点减少后续Agent调用，API calls较低；MMLU和FEVER运行时间最低，MATH比无防御LLM Debate平均多不到5秒。

需要反向看：GUARDIAN时序版不是每格都赢静态版GUARDIAN.s；例如幻觉/GPT-4o/MMLU静态版86.4、时序版84.9，MATH中5-7个Agent时静态版也更高。此外实验是每个数据集单独训练的同分布检测，不能证明跨领域零样本泛化，也没有在统一benchmark上直接证明胜过G-Safeguard、BlindGuard或XG-Guard。

### 3. $L_{GIB}$到底训练什么？

$$
L_{GIB}=I(X;Z)-\beta I(Z;Y).
$$

它不是单独训练一个“GIB分类器”，而是对产生$Z$的Encoder施加梯度：

```text
X → GCN/压缩层 → 每轮Z
                 ↓
       Transformer融合历史
```

直接受到影响的主要是GCN、Transformer以及可能存在的信息瓶颈投影层。$\beta$和外层的$\lambda$是人工超参数，不是普通网络weight。

- 最小化$I(X;Z)$：让$Z$少记原始回答中的重复、措辞和噪声；
- 因为第二项有负号，最小化整体会尽量增大$I(Z;Y)$：保留与协作结果相关的信息。

它解决Autoencoder的核心危险：如果Encoder容量过大，可以把输入原样记住，连攻击和幻觉也重建得很好，异常重建误差就不会高。信息瓶颈限制记忆容量，迫使网络学习占多数的稳定模式，使少见异常更难重建。

### 4. $L_{GIB}$的代价和论文实现问题

压缩太弱会保留噪声，压缩太强又可能丢掉少见但正确的关键证据。因此消融实验中中等压缩最好：$\alpha\in[0.3,0.5]$，压缩权重$\gamma\in[0.001,0.01]$。

论文附录使用$L_{rec}\approx-I(Z;Y)$，把目标近似改写为：

$$
L_{rec}+\gamma I(X;Z),
\qquad
\gamma=\frac{\lambda}{1+\lambda\beta}.
$$

因此实际直觉是“重建图，同时惩罚$Z$携带过多原始信息”。但论文没有充分说明互信息$I(X;Z)$的具体估计器和实现，所以GIB部分的可复现性弱于GCN、Transformer和双重建损失；理论信息上界也不等于严格保证幻觉不会传播。

## 十四、GUARDIAN实验中的Baseline论文速览

GUARDIAN比较的五个baseline不是同一种方法：

| 类别 | 方法 | 核心思想 |
|---|---|---|
| 普通MAS协作框架 | LLM Multi-agent Debate | 多个LLM反复阅读、批评并修改彼此答案，最终形成共识 |
| 动态MAS协作框架 | DyLAN | 先按贡献选择Agent团队，再用动态通信和早停完成任务 |
| 单LLM幻觉检测 | SelfCheckGPT | 对同一问题多次随机采样，利用回答不一致性判断幻觉 |
| 分布式防御 | Challenger | 给每个Agent增加质疑他人消息的安全检查prompt |
| 中央审计防御 | Inspector | 增加一个独立审计Agent，拦截、检查和纠正通信消息 |

### 1. LLM Multi-agent Debate

论文：*Improving Factuality and Reasoning in Language Models through Multiagent Debate*（Du et al., 2023）。

```text
多个Agent先独立回答
→ 每个Agent读取其他人的答案和理由
→ 批评并更新自己的答案
→ 重复多轮
→ 达成共识/多数结果
```

它只需要黑盒LLM，不训练额外检测器。优点是不同Agent可以互相纠错；缺点是没有显式恶意检测，如果错误先说得很有说服力，所有Agent也可能收敛到同一个错误。GUARDIAN将它作为“无专门防御时，普通讨论本身有多抗错”的基础线。

### 2. DyLAN

论文：*A Dynamic LLM-Powered Agent Network for Task-Oriented Agent Collaboration*（Liu et al., COLM 2024）。

它有两阶段：

```text
Team Optimization
→ 先试运行，用无监督Agent Importance Score估计贡献
→ 选择适合当前任务的Agent团队

Task Solving
→ 选中的Agent按动态前馈通信图协作
→ 达成共识后提前停止
```

它删除低贡献Agent的目的主要是提高任务准确率和效率，不是识别攻击者。低贡献不一定恶意，恶意Agent也可能表现得很“积极”。它与GUARDIAN的相似点是动态删节点；差别是DyLAN按任务贡献优化团队，GUARDIAN按时序重建异常分隔离风险。

### 3. SelfCheckGPT

论文：*SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models*（Manakul et al., EMNLP 2023）。

原方法直觉：如果模型真的知道一个事实，多次随机生成通常较一致；如果是在幻觉，不同采样更容易互相矛盾。

```text
主回答
+ 同一问题的多次随机采样
→ 比较主回答中的句子是否被采样结果支持
→ 得到句子/段落幻觉分
```

zero-resource表示不需要外部知识库，black-box表示不需要模型概率或内部权重。

GUARDIAN实验把它改造成MAS baseline：给每个Agent回答算幻觉分，排除最高风险回答，让其他Agent参考剩余回答重新思考，最后对通过阈值的答案多数投票。它擅长检测不一致幻觉，但若模型多次稳定地产生同一个错误，或通信边被篡改却语义仍一致，就容易漏检；调用多次采样的成本也高。

### 4. Challenger

Challenger和Inspector来自同一篇论文：*On the Resilience of LLM-Based Multi-Agent Collaboration with Faulty Agents*（Huang et al., 2024）。

Challenger把检查能力分散到每个已有Agent：通过修改配置/prompt，要求Agent在执行自身任务前质疑收到的消息，并判断safe或unsafe。

```text
收到其他Agent消息
→ 我先挑战和验证它
→ 判断safe/unsafe
→ 再决定是否用于自己的任务
```

优点是不需要中央审计员；缺点是每个普通Agent都要额外检查，增加token/API成本，而且判断仍由LLM完成，可能被有说服力的恶意内容骗过。

### 5. Inspector

Inspector采用中央审计思路：额外部署一个专门监督Agent，拦截Agent之间的消息，检查错误或不一致，必要时纠正后再放行。

```text
Agent A的消息
→ Inspector检查/纠正
→ 再传给Agent B
```

优点是安全职责集中、普通Agent不用全部改prompt；缺点是所有通信依赖Inspector，增加调用和延迟，并形成单点故障。Inspector本身如果判断错误或被攻击，整个系统都会受影响。

### 6. 一句话对比GUARDIAN

```text
LLM Debate：让大家多讨论，希望自然纠错
DyLAN：按贡献选团队，提高效率
SelfCheckGPT：看同一模型多次回答是否一致
Challenger：每个Agent自己检查收到的消息
Inspector：增加一个中央审计Agent检查所有消息
GUARDIAN：将多轮交互建成时序图，用重建异常分定位并隔离节点
```

GUARDIAN的主要区别是“学习时空传播规律”，而不是直接让LLM阅读文本后说safe/unsafe；但其主要实验没有在同一设置下对比G-Safeguard、BlindGuard、XG-Guard等专门图异常防御，不能据此宣布在所有MAS防御中最好。
