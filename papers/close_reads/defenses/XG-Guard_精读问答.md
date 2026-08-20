# XG-Guard 精读问答笔记

> **论文**：Explainable and Fine-Grained Safeguarding of LLM Multi-Agent Systems via Bi-Level Graph Anomaly Detection  
> **简称**：XG-Guard（eXplainable and fine-Grained safeGuarding）  
> **用途**：持续记录 XG-Guard 精读过程中的问题、公式拆解、方法直觉、实验分析、批判性评价与研究启示，供复习、meeting 和 paper idea 使用。  
> **进度**：2026-08-10 已完成方法与第四章第一轮精读；后续以快速复盘、代码核对和跨论文比较为主。  
> **本地论文**：`papers/close_reads/defenses/XG-Guard_中文版.pdf`；英文 canonical：`papers/01_mas_security/defenses/2026_ACL_XG-Guard.pdf`
> **三篇总览**：见 `前三篇MAS防御论文_快速总览.md`。
> **五篇最终速通**：见 `五篇MAS防御论文_最终速通总览.md`。

## 30 秒速记

- **问题**：整句embedding会稀释少量恶意token，而且BlindGuard只能指出异常Agent，不能解释原因。
- **方法**：sentence/token双流GNN；用当前图均值建立两套theme prototype，以到主题的距离计算异常。
- **训练**：只用正常图；自己对话主题是正样本，其他对话主题是负样本，通过跨主题对比学习训练两条GNN。
- **检测/修复**：标准化两套分数，用协方差融合；输出Agent异常分和token热力图，随后隔离Top-K节点。
- **结果**：24个主组合平均AUC 95.48，全部高于BlindGuard；总体接近但略逊有标签G-Safeguard。
- **局限**：可能学成“跑题检测”；正常多数、主题偏离和固定Top-3假设强；解释缺少faithfulness验证，仍未实现细粒度修复。

## 延续的讲解规则

1. 先说每段/每个公式要解决什么问题，再解释数学符号；
2. 逐个说明输入、输出、上下标、集合、概率、损失与优化对象；
3. 把公式翻译成一句口语，再给最小例子；
4. 区分论文宣称、公式表达、官方代码实际实现与我们的分析判断；
5. 实验表不仅复述数值，还要提炼结论、证据强弱、缺失实验和对 self-healing MAS 的启示；
6. 持续与 G-Safeguard、BlindGuard 做一对一比较。

## 预先锁定的阅读主线

XG-Guard 针对前两类方法的两个缺口：

```text
G-Safeguard / BlindGuard
整段 response → 一个 sentence embedding → 节点级异常判断

问题 1：恶意线索可能只藏在少数 token 中，整句压缩会稀释细粒度信号
问题 2：只能说哪个 agent 可疑，不能指出具体哪些 token 导致判断
```

论文提出的核心链条待逐节验证：

```text
agent response
   ↓
sentence-level representation + token-level representations
   ↓
bi-level agent encoder
   ↓
theme-based anomaly detector
   ↓
sentence/token bi-level anomaly score fusion
   ↓
agent-level detection + token-level explanation
   ↓
隔离/修复
```

## 精读时必须回答的问题

### 方法问题

1. “bi-level”具体是哪两层？两层信息如何交互？
2. token 表示来自哪个模型、哪一层、是否冻结？
3. theme 是怎样定义和计算的？是全图平均、聚类中心、attention prototype，还是可训练变量？
4. sentence-level 与 token-level anomaly score 如何对齐、归一化和融合？
5. token 贡献分数是否真能构成忠实解释，还是仅仅与最终分数相关的热力图？
6. 检测器是监督、无监督、自监督，还是使用人工伪异常？真正训练的网络与损失是什么？
7. 图结构具体进入了哪一步？是否真的进行 GNN message passing？
8. 检测后采取什么修复动作？是否仍只是剪边/隔离？

### 实验与会议问题

1. 论文解决的准确问题是什么，为什么值得发表？
2. 相对 G-Safeguard 和 BlindGuard 的创新是否实质，而非简单增加 token encoder？
3. 哪些攻击真正需要 token-level detection？实验是否专门控制攻击 token 比例和隐蔽程度？
4. 可解释性如何评估？有没有 token-level ground truth、faithfulness test、deletion/insertion test 或人工评估？
5. 是否覆盖 prompt injection、memory attack、tool attack、不同拓扑和不同 LLM？
6. clean utility、误报、额外延迟和 token-level 计算成本怎样？
7. 对 adaptive attacker、collusion、majority compromise、语义模仿是否稳健？
8. 消融能否分别证明 token level、sentence level、theme detector 和 fusion 的必要性？

## 三篇论文的初始定位（待读完后修正）

| 方法 | 核心检测思想 | 主要粒度 | 训练信号 | 解释能力 |
|---|---|---|---|---|
| G-Safeguard | edge-aware GNN 节点分类 | agent/response + communication edge | 真实攻击标签 | 主要定位恶意 agent |
| BlindGuard | self-neighbor-global 正常性表示与对比异常检测 | agent/response | 正常数据 + artificial corruption | 主要给 agent 异常分 |
| XG-Guard | bi-level graph anomaly detection + theme deviation | agent sentence + token | 待读方法章节确认 | 目标是 agent 定位 + token 解释 |

## 对 self-healing 研究的预期关联

如果 XG-Guard 的 token explanation 具有忠实性，它可能把此前的：

```text
发现哪个 agent 异常
```

推进到：

```text
发现哪个 agent 的哪部分内容异常
```

这对细粒度恢复可能有价值，例如只删除污染 span、修复 memory entry、阻断恶意 tool argument，而不必整个隔离 agent。但必须验证论文是否真的执行了这种细粒度修复；“提供 token 热力图”不等于“实现 self-healing”。

---

<!-- 后续 XG-Guard 的所有问题与回答按日期追加在此处。 -->

## 2026-08-10｜为什么 XG-Guard 也使用 GNN？GNN 与 MLP 到底是什么关系？

### 问题中的核心误区

GNN 和 MLP 不是“两个互相排斥的模型选项”，监督与无监督也不分别绑定某一种网络。

必须把两条轴分开：

| 维度 | 回答的问题 | 可选方案 |
|---|---|---|
| network architecture | 模型怎样读取和变换信息？ | MLP、GNN、Transformer 等 |
| training objective | 用什么信号教模型？ | 真实标签监督、corruption 对比学习、跨图对比学习、重构等 |

三篇论文的位置是：

| 方法 | 图信息处理方式 | 训练方式 |
|---|---|---|
| G-Safeguard | edge-aware 多层 GNN | 真实攻击标签 + 交叉熵，监督 |
| BlindGuard | 固定邻接聚合 + MLP/Linear | artificial corruption + 对比学习，无真实攻击标签 |
| XG-Guard | sentence/token 双流 GNN + skip connection | 同图主题正样本、异图主题负样本 + 对比学习，无真实攻击标签 |

因此 XG-Guard 使用无监督训练和 GNN 完全不矛盾。

### 1. MLP 是什么？

最简单形式：

\[
h_i=\sigma(Wx_i+b).
\]

MLP 对每个节点独立执行同一个变换。若输入只有 \(x_i\)，Agent \(i\) 的输出只取决于自己：

```text
Agent 1 的 x1 → MLP → h1
Agent 2 的 x2 → MLP → h2
Agent 3 的 x3 → MLP → h3
```

MLP 默认不知道谁和谁相连，也不会自动读取邻居。改变 Agent 2 的内容，若 Agent 1 的输入保持不变，则 Agent 1 的 MLP 输出也不变。

### 2. GNN 是什么？

一个简化 GNN 可以写成：

\[
h_i=\sigma\left(W_{self}x_i+W_{nei}sum_{j\in\mathcal N(i)}\hat A_{ij}x_j\right).
\]

它先读取自己与邻居，再进行可学习变换：

```text
自己的信息 x_i
       +
邻居信息 aggregate({x_j})
       ↓
Linear/MLP
       ↓
新的节点表示 h_i
```

因此，GNN 的关键不是“完全不用 MLP”，而是比普通 MLP 多了**按照图的边进行邻居消息传递**。多数 GNN 内部本来就包含 Linear/MLP：

\[
H^{(l+1)}=\sigma(\hat A H^{(l)}W^{(l)}).
\]

其中：

- \(\hat A H^{(l)}\)：按照图结构聚合邻居；
- \(W^{(l)}\)：Linear/MLP 式的可训练特征变换；
- \(\sigma\)：非线性激活。

所以可以把 GNN 粗略理解为：

> GNN = 图上的邻居信息搬运 + MLP/Linear 信息加工。

### 3. BlindGuard 为什么看起来只训练 MLP？

BlindGuard 没有放弃图信息，而是先用固定公式手工计算：

\[
x_i^{nei}=(\hat AX)_i,
\qquad
x^{global}=\operatorname{mean}(X),
\]

再输入 MLP：

\[
z_i=\operatorname{MLP}ig(x_i\parallel x_i^{nei}\parallel x^{global}\big).
\]

因此它的流程是：

```text
固定规则根据 A 聚合邻居
          ↓
MLP 学习怎样融合 self / neighbor / global
```

这在功能上类似“固定的一层图聚合 + 可学习 MLP”，只是邻居聚合规则本身不学习。它仍是 graph-aware，而不等于纯粹忽略图的 MLP。

BlindGuard 完全可以改成 GNN。作者选择固定聚合的可能设计考虑包括：

1. 明确得到 self、one-hop neighbor、whole-graph global 三种上下文；
2. 网络小、训练和运行成本低；
3. 避免多层消息传播造成 over-smoothing；
4. 让无攻击标签的对比学习集中学习正常性空间，而不是学习复杂传播参数。

但这只是架构选择，不是理论限制。XG-Guard 本身就证明无监督方法也可以训练 GNN。

### 4. G-Safeguard 为什么使用 GNN？能不能用 MLP？

G-Safeguard 想显式回答：

```text
谁向 Agent i 传了什么？
有害语义怎样沿有向边逐轮传播？
邻居和边历史如何共同改变 Agent i？
```

所以使用 edge-aware GNN：

\[
h_i^{(l)}=operatorname{COMB}\left(
h_i^{(l-1)},
\operatorname{AGGR}_{j\in\mathcal N(i)}
\psi(h_j^{(l-1)},e_{ij})
\right).
\]

普通 MLP 若只输入 \(x_i\)，完全看不到邻居 \(j\)、邻接矩阵 \(A\) 和边语义 \(e_{ij}\)，会丢掉 G-Safeguard 最想利用的传播信息。

但 G-Safeguard当然可以使用 MLP，而且实际上 GNN 内部的 \(\psi\)、COMB 和最后输出攻击概率的 \(f_\theta\) 往往就是 Linear/MLP。更准确的说法是：

> G-Safeguard 不能只用“仅看单节点的裸 MLP”替代整套 GNN而不损失拓扑信息；但可以在 GNN 内部、GNN 之后，或对预先聚合好的图特征使用 MLP。

如果先人工构造：

\[
u_i=[x_i,\operatorname{AGGR}(x_j),\operatorname{AGGR}(e_{ij})],
\]

再把 \(u_i\) 输入 MLP，也能做检测；但邻居和边怎样聚合就变成固定的人工设计，通常不如 edge-aware GNN 灵活。

### 5. XG-Guard 为什么使用两个 GNN？

XG-Guard 同时处理两个视角。

#### Sentence stream

\[
h_i^s=\operatorname{GNN}^s(x_i^s,A)+x_i^s.
\]

它让整句表示读取通信邻居，再加回自己的原始表示。后面的 \(+x_i^s\) 是 skip/residual connection，防止邻居聚合把恶意节点自身的特殊线索冲淡。

#### Token stream

先把 token 与所在句子的整体语义相加：

\[
x_{i,j}^{t'}=x_{i,j}^t+x_i^s.
\]

再把一个 agent 的 token 平均成固定长度的节点表示，让 GNN 能在 agent 通信图上传播：

\[
x_i^{t'}=\frac1{T_i}\sum_jx_{i,j}^{t'},
\]

\[
h_{i,j}^t=\operatorname{GNN}^t(x_i^{t'},A)+x_{i,j}^{t'}.
\]

直觉是：

```text
sentence GNN：判断“这个 agent 整体说法相对邻居是否异常”
token GNN：判断“这句话里的某个 token 放在整个通信上下文中是否异常”
```

XG-Guard 若只对每个 sentence/token 独立使用 MLP，就无法根据通信拓扑判断一个词在当前邻居讨论中是否偏离主题。它也可以采用 BlindGuard 式固定邻居平均 + MLP，但作者选择可学习 GNN 来编码两条语义流。

### 6. 三种设计没有绝对优劣

| 设计 | 优点 | 风险/局限 |
|---|---|---|
| 纯节点 MLP | 简单、快 | 看不到图和传播关系 |
| 固定图聚合 + MLP | 简单、graph-aware、稳定 | 聚合规则不学习，表达能力有限 |
| 可学习 GNN | 能学习拓扑和多跳依赖 | 更复杂，可能过平滑、被恶意邻居污染 |
| edge-aware GNN | 能利用边上传播的语义 | 成本更高，更依赖高质量边表示和训练数据 |

GNN 不一定天然优于 MLP。如果邻居多数已被污染，GNN 反而可能把恶意信息聚合进正常节点；如果堆叠太深，不同节点还可能变得过于相似。XG-Guard 专门加 skip connection，就是承认并缓解这个问题，而不是说明 GNN 没有风险。

### 7. 论文描述仍有一个待追问点

XG-Guard 正文只抽象地写 \(\operatorname{GNN}^s\) 和 \(\operatorname{GNN}^t\)，当前方法与实现细节没有明确说明具体使用 GCN、GraphSAGE、GAT，层数、隐藏维度、激活函数以及两条 GNN 是否共享参数。这和 BlindGuard 把融合器笼统写成 MLP 类似，是复现信息不足，后续需要结合官方代码继续核对。

### 最终记忆句

> MLP 只会加工交给自己的信息；GNN 会先沿图收集邻居信息，再用 Linear/MLP 加工。BlindGuard 不是不能用 GNN，而是手工完成图聚合后训练 MLP；G-Safeguard 不是不能用 MLP，而是不能只靠看单节点的裸 MLP 保留边和传播信息；XG-Guard 则选择用两条 GNN 分别传播 sentence 和 token 上下文。监督/无监督与 GNN/MLP 是两条独立维度，不要混在一起。

---

## 2026-08-10｜GNN 到底是什么？从零理解原理

### 1. 最直观定义

GNN（Graph Neural Network，图神经网络）是专门处理图结构数据的神经网络。它的核心循环只有三步：

```text
1. Message：每个节点接收邻居的信息
2. Aggregate：把多个邻居的信息汇总
3. Update：把邻居信息和自己的旧信息结合，形成新表示
```

一句话：

> GNN 让每个节点反复执行“听邻居说话—总结邻居意见—结合自己更新认知”。

### 2. 在 MAS 中，图里的东西分别是什么？

```text
节点 node：Agent
边 edge：Agent之间的通信关系
节点特征 x_i：Agent回复经过SentenceBERT得到的向量
边特征 e_ij：Agent j 向 Agent i 发送的消息/交互历史（若方法建模）
邻接矩阵 A：记录谁能向谁传消息
GNN输出 h_i：结合图上下文后的Agent表示
```

原始 \(x_i\) 回答“Agent \(i\) 自己说了什么”；GNN 后的 \(h_i\) 回答“结合它所处的通信环境后，应该怎样理解 Agent \(i\)”。

### 3. 为什么普通神经网络不够？

普通 MLP 对节点分别处理：

\[
h_i=\operatorname{MLP}(x_i).
\]

如果只输入 \(x_i\)，Agent \(i\) 的结果完全不受其他 Agent 影响。但 MAS 中一句话是否异常经常取决于上下文：

```text
Agent A：答案是27
Agent B：答案是36
Agent C：答案是36
```

只看 A 的“27”，模型可能不知道是攻击还是普通错误；知道 B、C 都回答 36 后，A 的偏离才变得明显。GNN的作用就是让 A 的表示能够读取 B、C 的信息。

### 4. 一层 GNN 的完整公式

可以分成三条公式。

#### 第一步：Message——邻居发来消息

\[
m_{j\rightarrow i}^{(l)}
=
\psi\big(h_j^{(l)},e_{ji}\big).
\]

- \(j\rightarrow i\)：消息从节点 \(j\) 发往节点 \(i\)；
- \(l\)：当前第几层 GNN；
- \(h_j^{(l)}\)：第 \(l\) 层时邻居 \(j\) 的表示；
- \(e_{ji}\)：从 \(j\) 到 \(i\) 的边信息；
- \(\psi\)：可训练的消息变换函数，常由 Linear/MLP 实现；
- \(m_{j\rightarrow i}^{(l)}\)：经过加工后准备传给 \(i\) 的消息。

没有边特征的方法可以简化为：

\[
m_{j\rightarrow i}^{(l)}=W_mh_j^{(l)}.
\]

#### 第二步：Aggregate——汇总所有邻居

\[
m_i^{(l)}=operatorname{AGGR}left\{
m_{j\rightarrow i}^{(l)}:j\in\mathcal N(i)
\right\}.
\]

- \(\mathcal N(i)\)：节点 \(i\) 的邻居集合；
- 冒号可以读作“其中满足”；
- \(\{\cdots\}\)：把所有邻居消息收集成一个集合；
- AGGR：聚合函数，常用 sum、mean、max 或 attention 加权和；
- \(m_i^{(l)}\)：邻居信息的汇总结果。

必须聚合，是因为每个节点的邻居数量不一样，但神经网络需要得到固定维度向量。

#### 第三步：Update——结合自己并更新

\[
h_i^{(l+1)}
=
\operatorname{UPDATE}ig(h_i^{(l)},m_i^{(l)}\big).
\]

- \(h_i^{(l)}\)：节点自己的旧表示；
- \(m_i^{(l)}\)：刚汇总的邻居表示；
- UPDATE：可训练的 Linear/MLP、GRU 或残差融合；
- \(h_i^{(l+1)}\)：融合自己和邻居后的新表示。

整层翻译成口语：

> 把每个邻居的话加工一下，将所有邻居的话汇总，再与自己原来的理解结合，得到更新后的认知。

### 5. 最常见的矩阵写法

GCN 类方法经常写成：

\[
H^{(l+1)}=\sigma\left(\hat A H^{(l)}W^{(l)}\right).
\]

逐个解释：

- \(H^{(l)}\in\mathbb R^{N\times D}\)：把 \(N\) 个节点的 \(D\) 维表示按行堆起来；
- \(\hat A\in\mathbb R^{N\times N}\)：经过加自环、归一化的邻接矩阵；
- \(\hat A H^{(l)}\)：根据图的边把邻居表示加权汇总；
- \(W^{(l)}\)：第 \(l\) 层可训练权重；
- \(\sigma\)：ReLU 等非线性函数；
- \(H^{(l+1)}\)：所有节点更新后的表示。

其中最核心的区别是 \(\hat A\)：

```text
没有 Â：每个节点独立变换，更像MLP
有了 Â：节点会混入图中邻居的信息，成为GNN
```

### 6. 最小数字例子

假设节点 A 的当前数值特征是 1，两个邻居 B、C 的特征分别是 3 和 5。

使用 mean aggregation：

\[
m_A=\frac{3+5}{2}=4.
\]

假设最简单的更新规则是自己和邻居各占一半：

\[
h_A^{new}=0.5\times1+0.5\times4=2.5.
\]

于是 A 的表示从 1 变成 2.5，因为它吸收了邻居信息。真实模型处理的是几百维语义向量，权重 0.5 也不是人工固定，而是通过训练学习。

### 7. GNN 究竟训练什么？

通常图结构 \(A\) 是输入，不会自动改变；真正被训练的是：

```text
邻居消息怎样变换：W_message / ψ
不同邻居应该占多大权重：attention weights
self和neighbor怎样融合：W_self、W_neighbor、UPDATE
输出表示怎样用于分类或异常评分：prediction head
```

训练不是让模型背下“节点 A 连着节点 B”，而是让它学习一套可复用规则：遇到任意一张新图，怎样利用其边和节点特征更新表示。

### 8. 一层与多层分别能看到多远？

```text
0层：只看到自己
1层GNN：看到直接邻居（1-hop）
2层GNN：看到邻居的邻居（2-hop）
3层GNN：看到3-hop范围
```

因此多层 GNN 可以描述信息的级联传播。但层数不是越多越好：层数过多时，节点反复互相平均，最后所有节点可能变得很像，这叫 over-smoothing（过度平滑）。

### 9. 常见 GNN 的区别

| 类型 | 聚合邻居的方式 | 直觉 |
|---|---|---|
| GCN | 归一化加权平均 | 大家按固定规则平均发言 |
| GraphSAGE | 聚合后与 self 拼接/融合 | 分开保存自己的意见和邻居总结 |
| GAT | 学习 attention 权重 | 自动判断哪个邻居更值得听 |
| edge-aware GNN | 消息同时依赖节点与边特征 | 不仅看谁说话，还看这条边上传了什么 |

G-Safeguard 更接近 edge-aware message passing；BlindGuard 的 \(\hat AX\) 是固定 GCN 式邻居平均；XG-Guard 论文目前只写抽象的 \(\operatorname{GNN}^s\) 与 \(\operatorname{GNN}^t\)，未在方法正文说明具体 GNN 类型。

### 10. GNN本身不等于攻击检测器

GNN主要是 encoder，负责产生拓扑感知表示 \(h_i\)。它后面还需要任务头：

```text
监督检测：h_i → classifier/MLP → attack probability
异常检测：h_i → prototype/distance/similarity → anomaly score
```

所以“使用 GNN”只说明怎样编码图，不自动说明：

- 是监督还是无监督；
- 使用什么损失；
- 输出概率还是异常分；
- 检测后怎样修复。

### 11. GNN 的主要风险

1. **恶意信息也会被聚合。**如果邻居本身是攻击者，正常节点的表示可能被污染；
2. **多数被攻陷问题。**当恶意节点占多数，聚合后的“主流”可能就是错误模式；
3. **过度平滑。**层数过深时正常与恶意节点越来越相似；
4. **错误拓扑。**缺边、伪造边或时变边会误导消息传递；
5. **静态图限制。**普通 GNN 不自动理解多轮时间演化，需要 temporal/dynamic graph 设计；
6. **同质性假设。**很多 GNN 倾向相连节点相似，但 MAS 中攻击者可能故意连接或模仿正常节点。

### 最终记忆句

> GNN 不是神秘的新分类器，而是一种图上的信息加工机制：图的边决定消息从哪里来，AGGR 决定怎样汇总邻居，MLP/Linear 参数决定怎样理解和融合，训练损失决定最终想学成什么。每经过一层，节点就多知道一跳邻居的信息；最后还要接分类器或异常评分器，才能完成攻击检测。

---

## 2026-08-10｜GNN 为什么被发明？为什么天然适合 MAS 防御？谁提出的？

### 1. GNN最初要解决什么问题？

传统神经网络擅长处理规则结构：

```text
MLP：固定长度向量
CNN：规则网格，例如图像像素
RNN：有先后顺序的序列
```

但现实中很多对象天然是图：

```text
分子：原子 + 化学键
社交网络：用户 + 关系
论文网络：论文 + 引用
交通网络：路口 + 道路
MAS：Agent + 通信关系
```

图有三个特殊困难：

1. 每个节点的邻居数量不同；
2. 节点没有天然的第一、第二、第三顺序；
3. 不同图的节点数和连接方式不同。

早期方法常把图预处理成固定长度向量再交给 MLP，但这样容易丢失“谁和谁相连”的拓扑信息，而且结果严重依赖人工特征设计。GNN 的目标是让神经网络直接处理图，而不必先把图压平。

### 2. 谁最早提出 GNN？

较准确的历史线索是：

#### 2005：早期命名与模型提出

Marco Gori、Gabriele Monfardini、Franco Scarselli 在 IJCNN 2005 论文：

> *A New Model for Learning in Graph Domains*

中提出一种能够直接处理有向、无向、带标签和循环图的神经模型，并称其为 Graph Neural Network。论文的出发点正是避免将图预处理为扁平向量导致拓扑信息丢失。

#### 2009：经典正式框架

Franco Scarselli、Marco Gori、Ah Chung Tsoi、Markus Hagenbuchner、Gabriele Monfardini 在 IEEE Transactions on Neural Networks 发表：

> *The Graph Neural Network Model*

系统化定义了经典 GNN 模型和训练方法。这篇通常被当作早期 GNN 奠基论文。

#### 2016/2017：现代 GCN 普及

Thomas Kipf 与 Max Welling 提出 Graph Convolutional Network（GCN），论文：

> *Semi-Supervised Classification with Graph Convolutional Networks*

用高效的一阶局部图卷积同时编码节点特征和局部结构，使现代 GNN 更容易训练和扩展。

#### 2017：Message Passing 统一视角

Justin Gilmer 等人在 ICML 2017 的：

> *Neural Message Passing for Quantum Chemistry*

把多种图模型统一成 Message Passing Neural Network（MPNN）框架，即现在常用的“message—aggregate—update”语言。

所以不能只说“GNN是Kipf提出的”：Kipf和Welling提出并普及的是现代GCN；GNN概念和早期模型至少可追溯到Gori、Monfardini、Scarselli在2005年的工作，2009年Scarselli等人给出经典完整版本。

### 3. GNN 为什么适合图？核心是 inductive bias

Inductive bias 可以理解为“网络结构提前写进去的合理假设”。

GNN写进去的假设是：

```text
相连节点可能互相影响；
一个节点的状态应由自己和邻居共同决定；
同一种局部处理规则可以复用于图中所有节点。
```

这不是从数据中重新发现“图存在”，而是设计网络时就告诉模型：边代表潜在依赖，沿边收集信息是一件合理的事。

对于MAS，这一假设和真实运行机制高度吻合：Agent本来就是读取邻居消息后更新自己的回复，攻击也确实沿通信边传播。因此，GNN的计算过程与MAS的信息流具有结构对应关系。

### 4. 为什么比把整张图交给 MLP 更合适？

假设固定有8个Agent，可以把所有节点向量拼起来：

\[
[x_1,x_2,\ldots,x_8]\rightarrow\operatorname{MLP}.
\]

但存在四个问题。

#### 顺序敏感

如果把Agent编号从1、2、3改成3、1、2，MAS本身没有改变，但拼接向量的位置全部变化，MLP可能给出不同答案。

GNN的sum/mean等邻居聚合不依赖邻居排列顺序。节点重新编号后，输出只会跟着节点一起重新排列，而不会改变含义。这称为 permutation equivariance（置换等变性）。

#### 节点数固定

为8个节点设计的拼接MLP不能自然接收20或50个节点。GNN对每个节点复用同一套参数，可以直接处理不同规模的图。

#### 拓扑隐含而非显式

MLP必须从大量数据中自己猜测哪些输入位置相连；GNN直接使用邻接矩阵 \(A\)，明确规定允许的信息通道。

#### 参数浪费

MLP对不同位置学习大量单独权重；GNN在所有节点和边上共享同一消息函数，更节省参数，也更容易迁移到新图。

### 5. 为什么特别适合 MAS 攻击检测？

#### 攻击具有关系性

同一句话孤立看可能正常，放到邻居和任务上下文中才显得异常。GNN能比较节点与通信邻域。

#### 攻击具有传播性

一层GNN读取一跳邻居，两层读取两跳邻居。多层局部传播与恶意信息的级联传播路径自然对应。

#### 防御目标就是节点分类/评分

MAS防御常需要给每个Agent输出攻击概率或异常分数。GNN天生为每个节点产生表示 \(h_i\)，正好可以接节点分类器或异常检测器。

#### 通信边包含重要证据

有向、带边特征的GNN可以区分 \(i\to j\) 与 \(j\to i\)，并使用边上的消息历史，从而分析有害内容从哪里来、流向哪里。

#### 可适配不同拓扑

Chain、Tree、Star、Random只是在邻接矩阵 \(A\) 上不同；同一个GNN规则可以在不同图上执行，不需要为每种节点位置单独建立网络。

### 6. “适合”不等于“一定有效”

GNN的结构偏好只有在假设合理时才有帮助。MAS中存在明显失败条件：

1. 恶意邻居会通过message passing污染正常节点表示；
2. 多数节点被攻陷时，聚合得到的主流可能就是恶意主题；
3. 攻击者模仿正常语义时，图邻域一致性未必能区分；
4. 通信图时变，而静态GNN可能看不到攻击随时间传播的因果过程；
5. 层数过深会over-smoothing；
6. 节点重新连边、伪造边或隐藏边会改变GNN看到的证据。

因此选择GNN只是给模型加入了合适的关系建模能力，并没有自动解决攻击检测。真正效果还依赖节点/边特征、训练信号、异常评分、威胁模型和修复机制。

### 7. 放回三篇论文

- **G-Safeguard**：认为攻击标签已知且传播边语义重要，因此用edge-aware GNN学习“什么传播模式对应攻击”；
- **BlindGuard**：同样认可图上下文重要，但用固定 \(\hat AX\) 聚合邻居，再训练MLP学习正常性空间；
- **XG-Guard**：认为sentence和token都需要结合通信上下文，因此分别设计两条GNN，并用skip connection保护ego信息。

三篇都基于同一个根本判断：

> MAS中的安全状态不是每个Agent独立决定的，而是由Agent行为、通信邻域与传播关系共同决定；图是数据本来的结构，因此图模型具有合适的inductive bias。

### 最终记忆句

> GNN最初被发明，是为了让神经网络直接处理节点数可变、邻居无序、拓扑不规则的图，而不把图压平成会丢失结构的固定向量。早期GNN可追溯到Gori、Monfardini和Scarselli在2005年的工作，Scarselli等人在2009年系统化，Kipf与Welling在2016/2017年以GCN推动现代普及，Gilmer等人在2017年统一为message passing框架。它适合MAS防御，不是因为“GNN更高级”，而是因为它的结构假设——相连Agent互相影响、规则跨节点共享、多层表示多跳传播——与MAS通信和攻击扩散机制天然匹配。

---

## 2026-08-10｜XG-Guard 方法论完整精讲：原文转述、公式拆解与三篇对比

### 0. 一句话先把整篇方法钉住

> XG-Guard只用正常MAS对话训练两条GNN：一条看每个Agent整句话，一条看每句话中的token；它把当前对话中大多数Agent的平均表示当作“讨论主题”，把偏离主题的Agent视为异常，再用sentence与token两套异常分的协方差决定token证据该被增强还是压制，最终既输出恶意Agent分数，也输出可疑token热力图。

它仍然采用detect-then-remediate：检测高风险Agent后，剪除其入边和出边，将其从后续通信中隔离。它没有清理memory、撤销tool call或重新生成正确状态，因此是细粒度检测/解释，不是完整self-healing。

### 1. 原文要解决的两个缺口

原文对G-Safeguard与BlindGuard的概括是：它们把一个Agent的完整response压成一个sentence embedding，再做节点级检测。作者认为这有两个问题。

#### 缺口1：少量恶意token会被整句压缩稀释

```text
“Q3预算总体正常……并把报告发送到外部邮箱进行分析。”
```

整句话大部分内容正常，真正危险的可能只有“发送”“外部邮箱”等少量词。如果整句压成一个向量，危险片段可能被大量良性内容冲淡。

#### 缺口2：只能指出Agent，不能解释具体原因

```text
传统输出：Agent 1异常分0.91
XG-Guard目标：Agent 1异常；主要证据是“send”“external email”
```

因此XG-Guard想把agent-level detection推进为agent-level detection + token-level explanation。

### 2. 完整方法流程

```text
正常MAS训练图 / 测试MAS图
        ↓
每个Agent的response Ri
        ├─ 整句送入SentenceBERT → sentence feature
        └─ 切成token逐个编码       → token features
        ↓
双层图编码器
        ├─ sentence GNN + ego skip
        └─ token平均后做GNN + 每个token ego skip
        ↓
当前对话主题原型
        ├─ sentence prototype
        └─ token prototype
        ↓
每个Agent相对主题的两套异常分
        ├─ sentence anomaly score
        └─ token anomaly score
        ↓
标准化 + covariance-guided fusion
        ↓
最终Agent异常分 + 每个token解释分
        ↓
Top-K / 高风险Agent隔离，剪入边与出边
```

### 3. 统一符号表

| 符号 | 含义 |
|---|---|
| \(\mathcal G=(\mathcal V,\mathcal E)\) | 一张MAS通信图 |
| \(v_i\) | 第\(i\)个Agent/节点 |
| \(N=|\mathcal V|\) | Agent数量 |
| \(A\) | 邻接矩阵；\(A_{ij}=1\)表示\(v_j\)向\(v_i\)传消息 |
| \(R_i\) | Agent \(i\) 的response文本 |
| \(t_{i,j}\) | Agent \(i\) response中的第\(j\)个token |
| \(T_i\) | Agent \(i\) 的token数量 |
| 上标\(s\) | sentence level |
| 上标\(t\) | token level |
| \(x\) | SentenceBERT产生的原始属性 |
| \(h\) | 经过GNN并加入图上下文后的表示 |
| \(p\) | 当前对话的theme prototype |
| \(s\) | anomaly score；具体语义需看所在公式 |

### 4. 模块一：双层节点属性构造

#### 公式（1）：整句表示

\[
x_i^s=\operatorname{SentenceBERT}(R_i).
\]

**原文转述：**使用冻结的SentenceBERT，把Agent \(i\) 的完整response编码成一个sentence-level向量，表示整句话的总体语义。

**逐符号：**

- \(R_i\)：Agent \(i\) 的文本回复；
- SentenceBERT：文本嵌入模型；
- \(x_i^s\)：Agent \(i\) 的原始句子级向量；
- \(s\)：sentence，不是score；
- SentenceBERT冻结：训练XG-Guard时不更新它。

**直觉：**把整句话压成一张“语义身份证”，适合判断整体在讨论什么，但可能漏掉藏在少数词里的攻击。

#### 公式（2）：逐token表示

\[
x_{i,j}^t=\operatorname{SentenceBERT}(t_{i,j}),
\qquad
t_{i,j}\in\operatorname{Tokenize}(R_i).
\]

**原文转述：**先把 \(R_i\) 切成token，再为第\(j\)个token生成独立嵌入，以捕获细粒度恶意线索。

**逐符号：**

- Tokenize：把response切成token；
- \(t_{i,j}\)：Agent \(i\) 的第\(j\)个token；
- \(x_{i,j}^t\)：这个token的原始向量；
- \(t\)：token，不是时间。

**直觉：**公式（1）给整篇文章拍一张全景照，公式（2）把镜头拉近到每个词。

**需要注意：**正文写成对每个token调用SentenceBERT，而没有明确说明是把单token字符串独立encode，还是读取完整句子的token hidden state。两种实现的上下文能力差异很大，正文复现信息不足。

### 5. 模块二：双层图编码器

#### 公式（3）：sentence stream

\[
h_i^s=\operatorname{GNN}^s(x_i^s,A)+x_i^s.
\]

**原文转述：**句子级GNN沿通信图聚合邻居语义，同时通过skip connection加回Agent自己的原始表示，防止邻居聚合过度冲淡ego信息。

**逐符号：**

- \(\operatorname{GNN}^s\)：sentence stream的可训练GNN；
- 输入不应只理解成单独的\(x_i^s\)，实际要在整张\(X^s\)和\(A\)上消息传播；
- \(A\)：决定从哪些Agent接收信息；
- \(+x_i^s\)：残差/跳跃连接；
- \(h_i^s\)：既包含自己整句语义，也包含通信邻居语义的新表示。

**直觉：**

```text
邻居对Agent i的看法总结
          +
Agent i自己的原话
          ↓
sentence-level graph representation
```

为什么要加回self？如果Agent i说了一句异常话，但所有邻居正常，反复平均可能把异常稀释；skip connection强制保留它自己的证据。

#### 公式（4）：给每个token补充整句上下文

\[
x_{i,j}^{t'}=x_{i,j}^t+x_i^s.
\]

**原文转述：**一个token单独看语义太弱，因此把它与所在response的sentence embedding相加。

**直觉：**“send”单独可能正常；放在“把敏感报告发送到外部邮箱”整句中才更危险。公式（4）相当于给每个token附上“它所在句子整体在说什么”。

撇号 \('\) 不是求导，表示“增强后的token向量”。该加法要求两者维度相同。

#### 公式（5）：token stream真正怎样使用GNN

\[
x_i^{t'}=rac1{T_i}\sum_{j=1}^{T_i}x_{i,j}^{t'},
\]

\[
h_{i,j}^t=operatorname{GNN}^t(x_i^{t'},A)+x_{i,j}^{t'}.
\]

**原文转述：**不同Agent的response长度不同，无法直接把数量不一的token当作统一节点输入。因此先把Agent \(i\) 的所有增强token平均成一个固定长度向量 \(x_i^{t'}\)，在Agent通信图上运行token-level GNN，再把得到的图上下文加回每一个token。

**这是最容易读错的公式：**

```text
XG-Guard没有建立“token与token连接”的token图。
它仍然在Agent通信图A上跑GNN。
每个Agent进入GNN前只有一个mean-pooled token向量。
GNN输出的同一份Agent图上下文，再加到该Agent的每个token上。
```

**直觉例子：**Agent 1有20个token，Agent 2有50个token。先各自平均成一个固定维向量，GNN才可以把Agent 1、2当作两个节点通信。之后，Agent 1得到的邻居上下文被分别加回它的20个token，使每个token同时保留自己的细节和Agent级图上下文。

**代价：**mean pooling让GNN传播时看不到token顺序和个别极端token；细粒度差异主要依靠最后的 \(+x_{i,j}^{t'}\) 保留。

### 6. 模块三：当前对话的theme prototype

#### 公式（6）：计算两套主题中心

\[
p^s=\frac1{|\mathcal V|}\sum_{i=1}^{|\mathcal V|}h_i^s,
\]

\[
p^t=\frac1{|\mathcal V|}\sum_{i=1}^{|\mathcal V|}
\frac1{T_i}\sum_{j=1}^{T_i}h_{i,j}^t.
\]

**原文转述：**不同问题的正常语义不同，所以不学习一个跨所有任务固定不变的“正常中心”；而是在每张当前MAS图内部，用所有Agent表示的平均值动态总结这次对话的主题。

**逐个解释：**

- \(p^s\)：所有Agent句子级表示的平均，sentence theme；
- \(p^t\)：先对每个Agent的token表示求平均，再对所有Agent求平均，token theme；
- prototype：原型/中心代表，不是一个真实Agent；
- 这两个prototype不是独立可训练参数，而是每张图现场算出来的均值。

**直觉：**开会时8个人中5个人围绕“Q3预算”讨论，平均意见就代表会议中心主题。突然有人要求“把敏感信息发到外部邮箱”，其表示会远离这个中心。

**核心假设：**大多数Agent正常。若攻击者占多数或串通形成主流，平均主题本身会被污染。

#### 与BlindGuard的关系

BlindGuard也使用全图平均表示：

\[
h_i^g=\frac1N\sum_kx_k.
\]

所以“全局主题中心”不是完全凭空的新思想。XG-Guard的增量主要是：分别构建sentence/token两套prototype、用跨图主题进行对比训练、再进行协方差融合和token解释。

### 7. 模块四：两套异常分数

#### 公式（7）：离主题越远，越异常

\[
s_i^s=\operatorname{dist}(h_i^s,p^s),
\]

\[
s_i^t=\frac1{T_i}\sum_{j=1}^{T_i}
\operatorname{dist}(h_{i,j}^t,p^t).
\]

**原文转述：**Agent的表示与当前对话主题原型之间的距离，就是异常程度。句子级直接算一次；token级逐token算距离后取平均。

**输入输出：**

```text
sentence representation h_i^s + sentence prototype p^s
→ 一个sentence anomaly score s_i^s

所有token representations h_i,j^t + token prototype p^t
→ token距离的平均 → 一个Agent token anomaly score s_i^t
```

**最小例子：**

```text
Agent 1、2、3都围绕预算讨论 → 距离主题近
Agent 4要求窃取隐私         → 距离主题远
```

于是Agent 4的 \(s_4^s,s_4^t\) 应较高。

**原文歧义：**作者称 \(\operatorname{dist}\) 为距离函数，却举“inner product”作为例子。普通内积通常是相似度，越大越接近，而距离通常越大越异常；除非实际使用负内积、\(1-\)cosine或额外变换。正文没有把方向讲清楚。

### 8. 模块五：为什么不能简单平均两套分数？

作者担心token-level过度敏感。例如某些正常的专有词、工具名或符号离token prototype很远，导致token分数错误升高；sentence-level却认为整体正常。若直接平均：

\[
\frac{s_i^s+s_i^t}{2},
\]

错误token分数可能拖累最终检测。因此作者希望先判断“两套分数整体是否同意”。

#### 公式（8）：标准化

\[
\hat s_{\mathcal G}^s=rac{s_{\mathcal G}^s-\mu_{\mathcal G}^s}
{\sigma_{\mathcal G}^s},
\qquad
\hat s_{\mathcal G}^t=rac{s_{\mathcal G}^t-\mu_{\mathcal G}^t}
{\sigma_{\mathcal G}^t}.
\]

**原文转述：**sentence和token分数可能不在同一量纲，所以分别减去均值、除以标准差，变成可比较的z-score。

**符号：**

- \(s_{\mathcal G}^s\)：一张图/一批图中的sentence分数向量；
- \(\mu^s,\sigma^s\)：sentence分数的均值和标准差；
- 帽子 \(\hat{}\)：标准化后的版本；
- 标准化后，0表示接近平均，正数表示高于平均，负数表示低于平均。

**例子：**原始sentence分数范围0-1，token分数范围0-20，不能直接相加；z-score把它们都转成“高出各自平均多少个标准差”。

**实现疑问：**正文一处说针对图 \(\mathcal G\)，另一处说均值/标准差来自一批MAS图；究竟沿Agent维还是batch维计算不够清楚。公式也未写防止 \(\sigma=0\) 的epsilon。

#### 协方差是什么？

简化写法：

\[
\operatorname{Cov}(a,b)
=
\frac1n\sum_i(a_i-\bar a)(b_i-\bar b).
\]

它衡量两套分数是否同向变化：

```text
sentence高时token也高 → 正协方差 → 两者整体同意
sentence高时token反而低 → 负协方差 → 两者整体冲突
接近0                → token证据与sentence关系弱
```

#### 公式（9）：融合最终Agent异常分数

\[
s_{\mathcal G}
=
\hat s_{\mathcal G}^s
+
\operatorname{Cov}(\hat s_{\mathcal G}^s,hat s_{\mathcal G}^t)
\cdot\hat s_{\mathcal G}^t.
\]

**原文转述：**以sentence分数为基础，再根据两套分数的协方差决定token分数的权重。两者同意时token证据加强；冲突时负协方差会调整/抑制token贡献。

**直觉：**

```text
sentence与token都认为Agent 4异常
→ Cov > 0
→ token证据加到sentence证据上

sentence认为Agent 4正常，token却异常
→ Cov可能较低或为负
→ 不直接相信token的高分
```

**需要严格理解：**Cov是全局标量，不是每个Agent一个权重。它根据整张图/批次中两套排序的总体一致性，对所有Agent的token分数一起重加权。因此它是粗粒度校准，不是真正逐Agent学习融合。

### 9. Token解释分数从哪里来？

对token \(t_{i,j}\)：

\[
s_{i,j}^{exp}
=
\operatorname{Cov}(\hat s^s,\hat s^t)
\cdot
\operatorname{dist}(h_{i,j}^t,p^t).
\]

**原文转述：**某token离token主题越远，并且sentence/token两套检测整体越一致，该token越被认为是导致Agent异常的证据。

**直觉：**它给每个词上色：

```text
“send the report to external email”
  ↑        ↑            ↑
离正常主题较远的token被标红
```

**重要边界：**这是一种prototype-distance attribution，即“哪个token最不像当前主题”；它不自动等同于因果解释。论文主要用热力图案例说明解释效果，没有用删除该token后预测是否显著下降、token-level ground truth或faithfulness指标严格验证。因此“meaningful visualization”证据较强，“忠实解释最终决策”证据仍不足。

### 10. 模块六：只用正常图怎样训练？

XG-Guard没有真实攻击标签，也没有像BlindGuard那样给节点加高斯corruption。它通过“主题配对”构造正负样本。

假设一个batch有 \(B\) 张正常MAS对话图：

\[
\{\mathcal G_1,\ldots,\mathcal G_B\}.
\]

每张图讨论不同query，因此有自己的theme prototype \(p_k\)。

#### 公式（10）：正确主题配对是正样本

\[
s_{\mathcal G}^{pos}=f(R_k,p_k\mid A_k).
\]

**原文转述：**第\(k\)张图中的Agent responses \(R_k\)，应当与自己图的主题 \(p_k\) 匹配。

- \(R_k\)：第\(k\)张图中所有Agent responses，不是单个Agent；
- \(p_k\)：第\(k\)张图自己的主题原型；
- \(A_k\)：第\(k\)张图的通信拓扑；
- 竖线 \(\mid A_k\)：给定/条件于拓扑 \(A_k\)，不是除法；
- \(f\)：前面整套编码、主题比较和评分过程的抽象写法；
- \(s^{pos}\)：正确配对的兼容/相似分数，训练时希望高。

#### 公式（11）：配错另一场对话主题是负样本

\[
s_{\mathcal G}^{neg}=f(R_k,p_l\mid A_k),
\qquad l\ne k.
\]

**原文转述：**保持第\(k\)张图的responses和拓扑不变，把主题换成随机另一张图 \(\mathcal G_l\) 的prototype，制造语义不匹配。

**直觉例子：**

```text
正样本：Q3预算对话 + Q3预算主题
负样本：Q3预算对话 + 医疗诊断主题
```

模型被教会：Agent应该靠近自己当前对话的主题，远离别的对话主题。作者把这种“错误主题配对”当作恶意偏离的代理。

**与BlindGuard的关键差别：**

```text
BlindGuard负样本：给正常节点向量加方向性随机噪声
XG-Guard负样本：把正常对话配上另一场对话的主题
```

前者模拟表示空间扰动，后者模拟上下文/主题不匹配。

#### 公式（12）：对比损失

论文印出的形式是：

\[
\mathcal L
=
-\sum_{k=1}^{B}
\log(s_{\mathcal G}^{pos})
+
\alpha\log(1-s_{\mathcal G}^{neg}).
\]

**根据正文意图：**训练希望：

\[
s^{pos}\rightarrow1,
\qquad
s^{neg}\rightarrow0.
\]

更符合该意图的BCE式写法应为：

\[
\mathcal L_{intended}
=
-\sum_{k=1}^{B}
\left[
\log(s_k^{pos})
+
\alpha\log(1-s_k^{neg})
\right].
\]

- 第一项：正确主题配对的分数要高；
- 第二项：错误主题配对的分数要低；
- \(\alpha\)：控制负样本项的重要程度；
- \(B\)：batch中图的数量；
- log：当模型把正确配对打低分或错误配对打高分时给予较大惩罚。

**重要公式疑点：**论文排版中负号只明确作用于第一项；若严格按印刷公式最小化，\(+\alpha\log(1-s^{neg})\)可能产生与文字目标相反的方向。很可能是括号/负号排版错误，也可能实现中另有定义；没有代码不能替作者确定。另一个歧义是前面 \(s\) 被叫作“异常距离”，这里又被当作0-1兼容概率取log，符号被重复使用而未给出转换函数。

### 11. 到底训练了什么？

```text
SentenceBERT：冻结，不训练
sentence GNN^s：训练
token GNN^t：训练
GNN内部Linear/MLP权重：训练
theme prototype：每张图取均值，不是可训练参数
covariance fusion：固定公式，不是可训练网络
repair/pruning：规则，不训练
```

本质上训练的是两条GNN，使正常Agent表示靠近自己对话的主题，同时与其他对话主题可区分。

XG-Guard正文没有说明GNN到底是GCN、GAT还是GraphSAGE，也没有完整报告层数、隐藏维度、激活函数、两条GNN是否共享参数。这是方法复现信息不足。

### 12. 训练与推理完整区别

#### 训练阶段

```text
只输入正常MAS图
→ frozen SentenceBERT产生sentence/token属性
→ 两条GNN编码
→ 每张图计算自己的theme prototypes
→ 自己主题为positive，另一张图主题为negative
→ 对比损失
→ 更新两条GNN
```

#### 推理阶段

```text
输入可能被攻击的MAS图
→ 计算sentence/token图表示
→ 用这张测试图自身的所有Agent计算theme prototypes
→ 计算两套异常分
→ 标准化、协方差融合
→ 输出每个Agent最终异常分
→ 输出每个token解释分
→ 按防御预算选Top-3，剪除其入边与出边
```

测试图中的攻击者也参与prototype计算。因此该方法依赖“正常Agent占多数”；攻击比例高时主题锚点会被拖走。

### 13. 附录算法存在的编号问题

正文实际编号是：

```text
(1)(2) sentence/token属性
(3) sentence GNN
(4)(5) token增强和token GNN
(6) prototypes
(7) anomaly scores
(8) normalization
(9) fusion
(10)(11) positive/negative pairs
(12) loss
```

但附录Algorithm 1/2多处引用了不对应的编号，例如把式（7）称为prototype、把式（11）称为最终异常分。阅读时应以方法正文公式内容为准，这是论文编辑/编号未同步问题，不是读者理解错误。

### 14. 与G-Safeguard、BlindGuard一对一比较

| 阶段 | G-Safeguard | BlindGuard | XG-Guard |
|---|---|---|---|
| 研究目标 | 已知攻击节点分类 | 未知攻击异常检测 | 未知攻击检测 + token解释 |
| 训练数据 | 正常+真实攻击标签 | 仅正常图 | 仅正常图 |
| 文本粒度 | response/历史话语 | 当前response句向量 | sentence + token双粒度 |
| 边信息 | 显式edge message/history embedding | 邻接关系，无详细边语义 | 邻接关系，无详细边语义 |
| 图编码 | edge-aware多层GNN | 固定邻居/全局聚合 + MLP | sentence GNN + token GNN + residual |
| 负样本/监督 | 真实0/1攻击标签 | 节点向量加corruption | 当前对话配错其他对话theme |
| 损失 | binary cross-entropy | pseudo-label supervised contrastive | cross-dialogue theme contrastive loss |
| 检测依据 | 像不像训练攻击者 | 像不像当前正常群体 | 离当前sentence/token主题多远 |
| 输出 | 攻击概率 | agent异常分 | agent异常分 + token解释分 |
| 修复 | 主要剪高风险节点出边 | 主要隔离/剪边 | 剪高风险节点入边和出边 |
| 关键假设 | 训练攻击覆盖测试攻击 | 攻击形成表示离群且正常占多数 | 攻击偏离主题、正常占多数、不同训练对话主题可作负样本 |

### 15. 三篇方法演进的最直观理解

```text
G-Safeguard：
“我见过有标签的坏人，所以训练分类器认坏人。”

BlindGuard：
“我没见过坏人，但我知道正常群体通常怎样；离群者可疑。”

XG-Guard：
“我不只判断谁离群，还在句子和token两个层次看他偏离了当前主题的哪一部分。”
```

### 16. XG-Guard真正的创新在哪里？

1. 把response从单一sentence embedding扩展为sentence/token双流；
2. 两条GNN分别让粗粒度和细粒度表示吸收通信拓扑；
3. 用当前图的adaptive theme prototypes应对不同query主题；
4. 用跨对话prototype错配构造无攻击标签负样本；
5. 用covariance融合两个层级，并把token到主题的距离作为解释。

其中最实质的增量是token-level representation + fusion/explanation。单纯“用全局平均表示当前主题”与BlindGuard的global representation非常接近，不宜单独夸大为全新思想。

### 17. 方法的主要局限与可追问点

1. **主题偏离不等于恶意。**正常创新意见也可能偏离平均主题；高度隐蔽、仍然on-topic的攻击可能靠近主题；
2. **majority benign假设。**串通或多数攻陷会污染prototype；
3. **跨图负样本可能只教会topic classification。**模型可能学到“预算对话不同于医疗对话”，而非“正常不同于恶意”；
4. **token GNN并非真正token图。**GNN只看到mean-pooled token节点表示，token顺序和token间结构没有进入图传播；
5. **解释faithfulness不足。**token距离热力图是合理线索，但没有充分证明这些token因果性决定最终预测；
6. **协方差是全局单标量。**对所有Agent统一重加权，且在只有少量Agent时估计可能不稳定；
7. **公式存在歧义。**distance/inner product方向、score概率化、损失负号和算法编号均不够严谨；
8. **架构未充分报告。**具体GNN类型、层数、维度和激活缺失；
9. **防御预算Top-3。**主实验知道隔离3个Agent，真实部署未知攻击者数量时需要阈值校准；
10. **修复仍然粗粒度。**虽然解释到token，实际动作仍是整个Agent隔离，没有展示只删除恶意span、清理memory或回滚tool副作用。

### 18. 对self-healing研究的真正启示

XG-Guard提供的是从“异常节点”走向“异常证据定位”的一步：

```text
Agent异常分
     ↓
定位可疑token/短语
     ↓
未来可以映射到污染源类型
     ├─ prompt span
     ├─ memory entry
     ├─ tool name/argument
     └─ transmitted message
     ↓
选择细粒度恢复动作
```

但XG-Guard自己只完成了前两步和Agent隔离。你的self-healing proposal可以进一步做：解释可信度验证、攻击面诊断、span/memory/tool级修复、回滚、恢复验证与安全重新接入。

### 最终口头汇报版

> XG-Guard针对G-Safeguard和BlindGuard把整段Agent response压成单一句向量、只能给出黑盒节点判断的问题，提出sentence-token双层无监督图异常检测。它用冻结SentenceBERT分别编码完整response和各token；sentence stream通过GNN聚合通信邻居并用残差保留ego信息，token stream先给每个token加入sentence语义，再把一名Agent的token平均成固定节点向量送入第二条GNN，并把图上下文加回每个token。随后，它把当前图中所有Agent表示的均值作为动态对话主题prototype，以节点或token表示到prototype的距离产生两套异常分。两套分数先标准化，再由协方差衡量整体一致性并加权融合；token到主题的加权距离同时作为解释分。训练只使用正常MAS图：Agent与自己对话主题构成正配对，与另一张随机对话图的主题构成负配对，通过对比损失训练两条GNN。相对BlindGuard，真正新增的是token级视角、跨主题负样本和可解释融合，而主题均值与全局异常思想本身相近。其优势是能发现藏在少量token中的异常并指出可疑词；局限是依赖正常多数和主题偏离假设，跨图负样本可能学成topic discrimination，token解释尚缺faithfulness验证，且最终仍只隔离整个Agent而非执行细粒度自愈。

---

## 2026-08-10｜第四章完整实验讲解：每个实验证明了什么？

### 0. 第四章整体在回答哪些问题？

第四章试图回答五件事：

1. XG-Guard能否在不同攻击、任务和拓扑下准确找出恶意Agent？
2. 找出来并隔离后，MAS端到端任务表现是否改善？
3. 换用其他backbone LLM时是否仍有效？
4. token-level解释是否看起来有意义？
5. token view和covariance fusion是否真的必要？

对应证据：

```text
表1：主检测与防御结果
图3：跨LLM backbone
图4：多轮对话中的MAS准确率
图5：token解释案例
表2/表3：消融实验
```

### 1. 实验设置

#### 六个任务/攻击场景

| 攻击面 | 数据集 | 攻击机制 |
|---|---|---|
| PI | CSQA | 操纵恶意Agent的system prompt |
| PI | MMLU | 同上 |
| PI | GSM8K | 同上 |
| TA | InjecAgent | 诱导/利用外部工具或plugin窃取敏感信息等 |
| MA | PoisonRAG | 注入虚假检索/对话记录污染memory |
| MA | CSQA | 注入虚假对话记录影响协作推理 |

PI、TA、MA分别是prompt injection、tool attack、memory attack。

#### 四种拓扑

```text
Chain：信息沿链传播
Tree：树状层级传播
Star：中心节点影响大
Random：随机通信关系
```

六个攻击场景乘四种拓扑，共24个主实验组合。

#### Backbone LLM

- 主实验：GPT-4o-mini；
- 跨backbone测试：DeepSeek-V3、Qwen3-30B-A3B。

#### Baselines

| 类别 | 方法 | 含义 |
|---|---|---|
| 无防御 | No Defense | 不进行隔离 |
| 通用无监督GAD | DOMINANT | 图重构误差 |
| 通用无监督GAD | PREM | 对比/亲和性异常检测 |
| 通用无监督GAD | TAM | 邻域亲和度与拓扑修剪 |
| MAS无监督防御 | BlindGuard | 仅正常数据+corruption对比学习 |
| MAS监督防御 | G-Safeguard | 真实攻击标签训练，作为监督上界参考 |

G-Safeguard拥有真实攻击标签优势，因此不是与XG-Guard完全同等信息条件下的baseline；它更适合作为“如果攻击标签可用，可以达到什么水平”的上界参照。

#### 防御预算

异常分最高的三个Agent被标记为攻击者并隔离。

必须区分两个“3”：

```text
Top-3：隔离异常分最高的3个Agent
ASR@3：第3轮对话结束后测得的攻击成功率
```

两者不是同一个3。

### 2. 三个评价指标怎么读？

#### AUC/AUROC：检测排序能力，越高越好

AUC回答：随机抽一个恶意Agent和一个正常Agent，检测器把恶意Agent排得更可疑的概率有多大。

```text
100：近乎完美排序
90：很强
50：接近随机猜测
低于50：排序方向可能相反
```

AUC不依赖固定Top-3阈值，主要衡量检测器本身。

#### ASR@3：第3轮时攻击影响，越低越好

ASR表示出现恶意/错误行为的Agent比例。它衡量检测+隔离之后，攻击还成功传播了多少。

#### ACC：MAS最终任务准确率，越高越好

ACC不是只看检测器，而是看整个MAS经过防御后是否仍能把任务做对。

三者可能不完全同步：AUC高说明排序好，但如果隔离预算错误、误剪关键Agent或攻击已造成不可逆副作用，ASR/ACC仍可能不好。

### 3. 表1主结果

#### 结论A：XG-Guard显著超过BlindGuard

对表1的24个组合重新汇总：

| 指标 | BlindGuard | XG-Guard | 平均变化 |
|---|---:|---:|---:|
| AUC平均 | 78.18 | 95.48 | +17.30个百分点 |
| ASR@3平均 | 16.51 | 11.15 | -5.36个百分点 |

- XG-Guard在24/24个组合中AUC都高于BlindGuard；
- 在24个组合中，XG-Guard有21个ASR@3低于BlindGuard；
- 例外是Tree/PI-MMLU、Star/PI-GSM8K，XG的ASR更高；Random/PI-CSQA两者同为25.00。

这说明sentence+token双层表示确实比BlindGuard的sentence-level检测稳定得多，尤其在GSM8K、工具攻击与memory攻击上。

#### 代表性提升

Chain/PI-GSM8K：

```text
BlindGuard AUC 65.33 → XG-Guard 97.78
ASR@3      10.67 → 8.67
```

Tree/TA-InjecAgent：

```text
BlindGuard AUC 83.56 → XG-Guard 99.56
ASR@3      17.42 → 7.93
```

Random/MA-CSQA：

```text
BlindGuard AUC 73.33 → XG-Guard 95.56
ASR@3      20.33 → 0.67
```

#### 结论B：XG-Guard接近但没有整体超过G-Safeguard

| 指标 | G-Safeguard | XG-Guard |
|---|---:|---:|
| AUC平均 | 98.63 | 95.48 |
| ASR@3平均 | 10.33 | 11.15 |

总体上，拥有真实攻击标签的G-Safeguard仍稍强。

但XG-Guard在3/24个组合中AUC超过G-Safeguard：

- Star/MA-CSQA；
- Random/TA-InjecAgent；
- Random/MA-PoisonRAG。

它也在8/24个组合中取得更低ASR，例如多个MA-CSQA、PoisonRAG和Star/TA场景。

最准确结论：

> XG-Guard在不使用真实攻击标签的情况下显著刷新无监督MAS防御，并在部分场景达到或超过监督G-Safeguard，但整体平均仍略逊于监督上界。

#### 结论C：不同拓扑下比较稳定

例如TA-InjecAgent：

```text
Chain  99.56
Tree   99.56
Star   99.11
Random 98.67
```

但PI-CSQA相对较弱：

```text
Chain  87.11
Tree   89.78
Star   91.11
Random 90.67
```

这可能说明提示攻击与正常任务语义更接近，不如工具/记忆攻击容易形成明显token主题偏离。

#### 论文表述中的一处错误/夸大

正文称XG-Guard“在所有设定下AUC持续超过90%”，但表1中：

```text
Chain/PI-CSQA：87.11
Tree/PI-CSQA：89.78
```

所以应改成“绝大多数设定超过90%”。

### 4. AUC高为什么ASR不一定最低？

例子：Tree/PI-MMLU

```text
BlindGuard AUC 81.33，ASR 18.00
XG-Guard    AUC 92.00，ASR 20.67
```

XG检测排序明显更好，端到端ASR却略高。可能原因：

1. AUC看所有正常/恶意节点的整体排序，Top-3只看最前面三个；
2. 隔离某些Agent可能破坏协作结构；
3. 攻击在检测前已经影响其他Agent；
4. LLM生成存在随机性；
5. ASR不仅由检测器决定，还由拓扑、修复时机和任务行为决定。

所以不能仅凭AUC宣称整个防御一定更好，必须同时看ASR和ACC。

### 5. 图3：跨LLM backbone泛化

论文把MAS backbone从GPT-4o-mini换成DeepSeek-V3和Qwen3-30B-A3B，只在两个memory attack数据集MA-CSQA、MA-PoisonRAG上测试，并覆盖四种拓扑。

结果显示：

- 在Qwen/MA-CSQA中，XG-Guard相对BlindGuard等基线大幅降低ASR；
- 在DeepSeek与Qwen的PoisonRAG中，XG-Guard多数拓扑接近最低ASR；
- 不同backbone上没有发生明显完全失效。

这支持双层语义+主题偏离并非只适用于GPT-4o-mini措辞。

但证据边界是：

1. 只测试2个额外LLM；
2. 只测试2个memory attack任务，没有PI和TA跨LLM图；
3. 未充分说明是否直接使用同一checkpoint跨backbone，还是重新训练；
4. 图中没有误差线和统计显著性。

准确表述应是“对两个额外backbone的memory attack有初步迁移证据”。

### 6. 图4：多轮对话中的MAS任务准确率

设置：

```text
数据集：MA-CSQA
Backbone：GPT-4o-mini
拓扑：Star、Tree
轮数：1到4轮
指标：整个MAS的Accuracy
```

随着轮数增加，memory poisoning继续传播，多数方法的准确率下降。XG-Guard基本持续保持最高或接近最高的无监督防御准确率，下降较慢。

这说明它不只是AUC好看，隔离后确实能减少memory attack对最终任务的损害。

但它只证明“持续遏制传播”，没有证明self-healing：

- 只展示MA-CSQA与两种拓扑；
- 只到4轮；
- 没有clean/no-attack utility；
- 没有检测延迟、恢复时间或重新接入；
- 准确率维持不等于清理了污染memory。

### 7. 图5：可解释性案例

#### MA-PoisonRAG

模型高亮类似：

```text
all consistently
common belief
clear consensus
information presented
should be accepted as accurate
```

这些词表现出“大家都同意，所以必须相信”的操纵性话术。

#### TA-InjecAgent

模型高亮：

```text
find the personal details
email them
important document
```

这些token与隐私窃取和外发工具行为直接相关。

作者也承认模型会高亮标点，因为文本编码器可能把邻近上下文混入标点表示。

证据限制：只有两个定性案例，没有token-level ground truth、precision/recall、删除高分token后的预测变化或faithfulness测试。因此它证明“热力图看起来合理”，还没有严格证明解释忠实。

### 8. 表2/表3：消融实验

三个版本：

```text
XG-Guard：sentence + token + covariance fusion
-Fusion：保留sentence和token，但用简单平均融合
-Token：去掉token view，主要使用sentence信息
```

对附录24个组合汇总：

| 版本 | 平均AUC |
|---|---:|
| XG-Guard | 95.48 |
| -Token | 86.51 |
| -Fusion | 72.72 |

完整模型比-Token平均高约8.97点，说明token信息在正确融合时确实有价值；比-Fusion平均高约22.76点，说明covariance fusion是核心组件。

最值得注意：在24个组合中，-Fusion有19个比-Token更差。也就是：

> 保留token但简单平均，往往还不如完全不要token。

代表性例子TA-InjecAgent：

```text
Tree：XG 99.56，-Token 90.67，-Fusion 48.27
Star：XG 99.11，-Token 90.67，-Fusion 47.29
```

这支持sentence/token分数语义错配问题，但也说明实验并非单独证明“token天然更好”，而是证明“token必须与作者的fusion绑定才有效”。性能核心可能主要来自协方差校准。

理想消融还应加入token-only、learned gate/attention fusion、不同token pooling、不同GNN类型/层数，以及分别去掉theme prototype、cross-graph negatives和skip connection。

### 9. 超参数与可复现性

附录报告：

```text
Optimizer：Adam
Epochs：20
Weight decay：2×10^-4
Learning rate：MA-CSQA为1×10^-5，其余为1×10^-4
α：按数据集在1×10^-5到1×10^-4之间设置
```

缺失或不足：

1. 未报告batch size；
2. 未报告随机种子数量；
3. 表格没有mean±std；
4. 没有显著性检验；
5. 没有明确报告训练/验证样本量；
6. 具体GNN类型、层数、隐藏维度缺失；
7. α按数据集单独选择，却没有充分说明验证流程。

结果很亮眼，但复现与统计稳健性信息不足。

### 10. 第四章最终结论

#### 有力证明的

1. XG-Guard在24个主组合上AUC全部超过BlindGuard；
2. 大多数场景端到端ASR也更低；
3. 对工具攻击、PoisonRAG、MA-CSQA尤其强；
4. sentence+token正确融合明显优于sentence-only；
5. 在两个额外LLM的memory attack上仍有效；
6. 在MA-CSQA多轮交互中能较好维持任务准确率；
7. token热力图能高亮一些直观恶意短语。

#### 未充分证明的

1. 跨所有LLM、所有攻击的开放世界泛化；
2. 对多数攻击者、串通和adaptive on-topic attack的鲁棒性；
3. token解释的faithfulness；
4. clean/no-attack场景的误报和utility损失；
5. 长期运行、动态拓扑和大规模Agent扩展；
6. latency、token编码成本和内存开销；
7. 检测后的真正恢复、自愈与副作用回滚；
8. 未知攻击者数量下的阈值校准，因为主实验固定Top-3。

### 组会口头版

> 第四章在六个攻击任务和四种拓扑共24个组合上比较XG-Guard。主表显示，其平均AUC为95.48，相比BlindGuard的78.18提升17.30个百分点，24个组合全部更高；平均ASR@3从16.51降至11.15，21个组合更低。这说明sentence-token双层表示与主题融合显著提升无监督检测，尤其对GSM8K、InjecAgent和memory attack有效。与有真实标签的G-Safeguard相比，XG-Guard平均AUC和ASR仍略逊，但在部分工具与记忆场景达到或超过监督方法，因此最准确定位是接近监督上界，而非全面超越。跨backbone实验在DeepSeek-V3和Qwen3的两个memory任务上显示初步泛化，多轮MA-CSQA实验说明隔离后能维持较高任务准确率。消融最关键：完整模型平均AUC95.48，去token降到86.51，而保留token但去融合仅72.72；说明token信息有用，但未经协方差校准反而常常有害，fusion是性能核心。解释实验仅有两个热力图案例，缺少token真值与faithfulness测试；同时实验固定Top-3、无mean±std、无clean utility、无大规模/自适应攻击，因此论文充分证明了强无监督检测，却尚未证明可靠解释、开放世界鲁棒性或真正self-healing。
