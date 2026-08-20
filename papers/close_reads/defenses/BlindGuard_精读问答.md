# BlindGuard 精读问答笔记

> **论文**：BlindGuard: Safeguarding LLM-based Multi-Agent Systems under Unknown Attacks  
> **用途**：持续记录 BlindGuard 精读过程中的问题、直觉解释、公式拆解、实验分析与研究启示，便于复习和组会。  
> **进度**：2026-08-10 已基本完成第一轮精读；后续以快速复盘和跨论文比较为主。  
> **讲解原则**：先说明问题与直觉，再逐个解释数学符号、输入输出和算法步骤；明确区分论文原文、合理推断与批判性判断。
> **三篇总览**：见 `前三篇MAS防御论文_快速总览.md`。
> **五篇最终速通**：见 `五篇MAS防御论文_最终速通总览.md`。

---

## 30 秒速记

- **问题**：G-Safeguard依赖真实攻击标签，未知攻击到来时怎么办？
- **方法**：SentenceBERT编码response；构造self、neighbor、global三层表示，用小型融合网络建立正常行为空间。
- **训练**：只用正常图；给部分节点嵌入加方向性噪声制造伪异常，使用对比学习。
- **检测/修复**：与群体表示越不相似越异常；选Top-K节点隔离/剪边。
- **优势**：无需真实攻击标签，未知攻击泛化明显优于针对已知攻击训练的监督检测器。
- **局限**：依赖攻击形成语义离群、正常Agent占多数；公开有效路径主要是固定图聚合+MLP，且修复仍只是隔离。

---

## 阅读主线

后续随着精读逐步完善：

1. 论文为什么提出 unknown-attack defense？
2. BlindGuard 与 G-Safeguard 的核心差别是什么？
3. 无监督图异常检测如何建立？
4. 节点、邻居和全局系统信息如何编码？
5. 攻击分数怎样计算？
6. 检测结果如何用于剪枝修复？
7. 实验是否真正支持未知攻击泛化？
8. 方法的假设、失败场景与自愈研究接口是什么？

---

## 续问补充

<!-- 后续针对 BlindGuard 的问答追加在这里。建议格式：

### YYYY-MM-DD｜问题主题

**Q：** 用户的原始问题

**直觉回答：** 先用一两句话或例子讲清楚。

**符号与公式：** 逐个解释符号、上下标、集合、函数、条件和输入输出。

**技术回答：** 对应论文机制、算法、图表或实验。

**边界/判断：** 区分论文原文、合理推断和批判性分析。

-->

### 2026-08-10｜BlindGuard 之前的无监督图异常检测怎样用于 MAS 防御？

**Q：** 无监督 GAD 只用正常 MAS 交互数据，怎样检测攻击者并防御 MAS？Gap 1 和 Gap 2 具体是什么意思？

#### 一句话直觉

传统无监督 GAD 的思路是：

> 先用正常 MAS 学出“正常的节点和连接通常长什么样”，部署时再寻找最不像这种正常模式的 agent，把它当成异常节点隔离。

GAD 本身主要负责“给节点打异常分”，并不天然完成整个 MAS 防御。将它用于 MAS 时，还要在前面增加“把交互转成图”，在后面增加“根据分数剪边隔离”。

#### 一、完整实现流程

##### 1. 把 MAS 交互转成图

在某一轮结束后，构造图：

\[
\mathcal G=(\mathcal V,\mathcal E,\mathbf X).
\]

- \(\mathcal G\)：整张 MAS 交互图；
- \(\mathcal V\)：节点集合，每个节点 \(v_i\) 是一个 agent；
- \(\mathcal E\)：边集合，\(e_{ij}\) 表示 agent \(i\) 与 agent \(j\) 存在通信；
- \(\mathbf X\)：所有节点的特征矩阵；
- \(\mathbf x_i\)：其中第 \(i\) 个 agent 的特征，通常由 SentenceBERT 等模型把回复 \(R_i\) 转成文本向量。

```text
Agent A 的回复 ──文本编码──→ x_A
Agent B 的回复 ──文本编码──→ x_B
Agent C 的回复 ──文本编码──→ x_C

谁向谁传消息 ─────────────→ 邻接矩阵 A / 边集合 E
```

注意这里有两个不同的 \(A\)：普通文字中的 Agent A 是智能体名字；数学中的邻接矩阵通常也写作 \(\mathbf A\)，表示节点间是否连接，不是 agent。

##### 2. 只用正常图训练

训练集只包含未遭攻击的 MAS 交互图：

\[
\{\mathcal G_1,\mathcal G_2,\ldots,\mathcal G_N\}_{\text{clean}}.
\]

这里：

- \(N\) 是正常交互图的数量；
- 没有真实攻击者节点；
- 也不需要“这个是 PI、这个是 TA”之类的攻击类型标签。

模型通过重构、邻居一致性或对比学习等任务，学习正常节点在图中通常具有的模式。

##### 3. 部署时给每个节点计算异常分数

被攻击的图输入训练好的 GAD 后，模型输出：

\[
s(v_i)\in\mathbb R.
\]

- \(s\) 是 anomaly scoring function，即异常打分函数；
- \(v_i\) 是第 \(i\) 个 agent 节点；
- 分数越高，一般表示越不像正常训练数据，越可疑。

它不是直接输出“这一定是某种工具攻击”，而是输出：

```text
A：0.08  很正常
B：0.13  比较正常
C：0.91  很异常
D：0.19  比较正常
```

##### 4. 选出高风险节点

可以使用两种常见规则：

```text
阈值法：s(v_i) > 0.5 就报警

Top-K 法：不管绝对分数，选异常分最高的 K 个节点
```

BlindGuard 论文为了公平比较不同 GAD，主要采用固定修复预算，例如选异常分最高的 3 个 agent。原因是不同 GAD 的分数量纲与校准不同，直接使用同一个阈值可能不公平。

##### 5. 剪边隔离并继续运行 MAS

选出可疑节点后，移除它与其他节点之间的通信边，阻止它继续传播消息：

```text
检测前：A ←→ B ←→ C(可疑) ←→ D

检测后：A ←→ B     C(隔离)     D
```

剩余正常 agent 只根据未被剪除的邻居消息继续下一轮推理。因此，“旧无监督 GAD 用于 MAS 防御”的完整结构也是：

```text
文本交互 → MAS 图 → 无监督 GAD 异常分 → Top-K/阈值 → 剪边 → 继续协作
```

它与 G-Safeguard 的外层检测—修复流程相似，主要区别在于检测器的训练方式：

```text
G-Safeguard：正常节点 + 真实攻击节点标签 → 监督训练
传统无监督 GAD：只有正常/无标签图 → 学正常模式 → 偏离者算异常
```

#### 二、三类代表性旧 GAD 是怎样打异常分的？

BlindGuard 主要选择 DOMINANT、PREM 和 TAM 作为无监督基线。三者对应三种典型思想。

##### 1. DOMINANT：重构不出来的节点就是异常

DOMINANT 使用图自编码器同时学习重构：

- 节点属性 \(\mathbf X\)：这个节点的话语向量；
- 图结构 \(\mathbf A\)：这个节点通常与谁连接。

训练时模型只看正常图，学习把正常输入压缩后再还原。测试时，如果节点 \(v_i\) 的属性或连接很难还原，其重构误差较大：

\[
s_i \approx
\underbrace{\|\mathbf x_i-\hat{\mathbf x}_i\|}_{\text{话语属性重构误差}}
+
\underbrace{\|\mathbf a_i-\hat{\mathbf a}_i\|}_{\text{连接结构重构误差}}.
\]

- 带帽子的 \(\hat{\mathbf x}_i\) 是模型重构/猜出来的节点特征；
- \(\mathbf x_i\) 是真实节点特征；
- 两者相差越大，越异常；
- \(\mathbf a_i\) 是节点 \(i\) 在邻接矩阵中的那一行，表示它与谁连接。

直觉类比：模型学会临摹正常图；某个节点怎么都临摹不像，就把它判为异常。

**套到 MAS 的问题：**攻击者可能完全不改变系统规定的通信拓扑，而且恶意话语仍然流畅、在讨论同一任务。这时结构很好重构，语义向量也未必明显偏离；相反，正常 agent 的独特推理风格反而可能难以重构，造成误报。

##### 2. PREM：比较自己与邻居是否匹配

PREM 的核心可直观理解为 ego-neighbor matching：

```text
ego：节点自己说了什么
neighbor：它的邻居整体在说什么
```

正常图中，相连节点通常存在一定上下文关联，所以模型通过对比学习，让节点自己的表示与其邻域表示相匹配。部署时，如果一个节点与邻居非常不一致，就给予较高异常分。

简化理解：

\[
s_i \approx 1-\operatorname{sim}
(\text{self}_i,\text{neighbors}_i).
\]

- \(\operatorname{sim}\) 表示相似度；
- 自己与邻居越相似，相似度越接近 1，异常分越低；
- 越不相似，异常分越高。

**套到 MAS 的问题：**它主要看局部邻居。攻击者如果说得很像正常人，或者多个攻击者互相连接、彼此保持一致，局部上就不显得异常；但它们可能整体偏离整个 MAS 的真实任务。

##### 3. TAM：低亲和度、低同质性的节点就是异常

TAM 建立在 affinity/homophily 思路上：

- affinity：两个相连节点在特征上有多亲近；
- homophily：相似节点更容易相连，即“物以类聚”；
- low homophily：一个节点与相连邻居普遍不像。

TAM 会根据节点—邻居亲和度学习表示，并迭代截断可能带来噪声的低亲和连接。一个节点如果与邻居的相似性持续较低，就容易被视为异常。

**套到 MAS 的问题：**MAS 中不同 agent 本来就承担不同角色。例如数学家负责推导、批评者负责质疑、总结者只给结论，他们的正常语言可能天然不相似。因此“和邻居不像”不一定是攻击；反过来，攻击者也可以使用相同话题与语言风格伪装成高亲和节点。

#### 三、Gap 1：为什么只看局部邻居不够？

识别 MAS 中的攻击者可能需要三个观察尺度：

```text
个体层：这个 agent 自己说了什么？
邻居层：它与直接协作者是否一致？
全局层：它是否符合整个系统的任务方向和集体状态？
```

一个例子：

```text
全局任务正确答案：36

A、B、C：推导得到 36
D、E：互相连接并共同坚持 27
```

从 D 的局部邻域看，D 和 E 非常一致，所以基于局部 affinity 的模型可能认为它们正常。但从全局看，D、E 形成了一个偏离整个系统目标的小团体。没有全局视角，就难以发现这种局部一致、全局异常的串通。

这就是 Gap 1：传统 GAD 往往只回答“你像不像邻居”，没有充分回答“你和整个 MAS 当前要完成的任务是否一致”。

#### 四、Gap 2：为什么“结构异常”假设与 MAS 攻击错位？

传统 GAD 常用于社交网络、交易网络等场景。在这些场景里，异常账户可能具有：

- 很少见的连接对象；
- 突然出现的大量边；
- 与邻居完全不同的属性；
- 低同质性或稀有子图结构。

因此旧方法容易形成假设：

```text
攻击者 = 图结构长得奇怪的节点
```

但 MAS 的拓扑通常由系统预先规定。一个 agent 被提示注入或记忆投毒后：

- 它仍占据原来的节点；
- 仍与原来的邻居通信；
- 度数和连接模式可能完全不变；
- 变化的只是它所表达的意图、结论或引导方向。

因此 MAS 中更典型的是：

```text
结构正常 + 语言流畅 + 意图恶意
```

例如所有 agent 都讨论“6 块橡皮和 8 支铅笔多少钱”，攻击者也不跑题，只是用看似合理的推理诱导答案 27。它在连接结构上没有任何异常，在粗粒度语义上甚至与其他节点高度相似，但其真正异常是 deceptive intent（欺骗意图）。

这就是 Gap 2：旧 GAD 主要寻找“结构上不像正常节点”，而 MAS 防御真正需要寻找的是“语义和意图上正在破坏任务的节点”。

#### 五、一个最小例子串起整个过程

假设 5 个 agent 回答同一道题：

```text
A：答案是 36，因为 6×2+8×3=36。
B：我也得到 36。
C：重新核算后是 36。
D（攻击者）：应当考虑折扣，所以答案是 27。
E：赞同 D 的折扣解释，答案 27。
```

如果 D、E 彼此相连：

- DOMINANT：图边没有改变，所有回复都在同一数学话题中，未必产生足够大的重构误差；
- PREM/TAM：D 与 E 互相一致，局部相似度可能很高；
- 需要的 MAS 专用判断：D、E 虽然局部一致，但相对于 A/B/C 和整个系统推理轨迹存在全局语义偏离。

因此 BlindGuard 才提出：同时编码 self、neighbor、global 三层上下文，并用语义 corruption 模拟“偏离正常语义流形”的伪异常，而不是继续把异常主要理解为奇怪的边或低同质性。

#### 六、对论文论证的边界判断

1. **无监督不等于不训练。**它仍然要用正常 MAS 交互训练模型；“无监督”指没有真实攻击者标签和攻击类型先验。
2. **旧 GAD 可以被包装成 MAS 防御，但不是原生为 MAS 设计。**其异常分数接入 Top-K/阈值和剪边模块后，才能完成防御闭环。
3. **Gap 1 与 Gap 2 是相关但不同的问题。**Gap 1 讲“看多少范围”，Gap 2 讲“把什么现象当异常”。
4. **语义异常也不是万能假设。**如果攻击者保持话题、语言风格和局部/全局语义都高度一致，只在关键事实上做细微操纵，BlindGuard 也可能漏检；正常 agent 的创新推理风格也可能被误报。

#### 最终总结

> BlindGuard 之前的无监督 GAD 防御，是先把 agent 当节点、通信当边、回复嵌入当节点属性，只用正常 MAS 图学习正常模式；部署时通过重构误差、ego-neighbor 不一致或低亲和度给节点打异常分，再隔离高分节点。它们可以形成基本的“检测—剪边”防御，但大多只关注局部相似性或结构偏离，而 MAS 攻击往往保持拓扑正常、以欺骗性语义破坏任务，甚至通过多个攻击者制造局部一致。因此它们既缺少个体—邻居—全局的多层上下文，也存在“结构异常”与“语义恶意”之间的假设错位。

### 2026-08-10｜BlindGuard 是哪年发表的？

- 最早以 arXiv 预印本公开：2025 年 8 月 11 日，编号 arXiv:2508.08127。
- 正式会议发表：ACL 2026 Long Papers，论文集时间为 2026 年 7 月。

因此，介绍论文时通常写“BlindGuard（Miao et al., ACL 2026）”；如果讨论工作首次公开的时间，则是 2025 年。

### 2026-08-10｜按 Shagufta 教授的会议问题预先分析 BlindGuard

**Q：** 针对 BlindGuard，回答会议要求的：问题定义、创新点与中稿理由、威胁模型、多攻击面鲁棒性证据、修复后效用、自适应攻击，以及对 self-healing proposal 的启示。

#### 0. 先给总判断

> BlindGuard 的核心贡献不是发明“图异常检测”或“剪边”，而是把 G-Safeguard 的“依赖已知攻击标签”改造成“只用正常 MAS 数据学习、面向未知攻击的语义异常检测”：它用 self–neighbor–global 分层编码理解 agent 在系统中的相对行为，再对正常嵌入做方向性 corruption，借助对比学习建立正常行为边界，部署时隔离偏离这一边界的节点。

它的故事完整、问题及时、实验维度较广，达到 ACL 论文应有的论证强度。但“unknown attack”需要克制理解：它不使用真实攻击样本训练，却仍假设攻击会造成可观察的语义偏离；公开实现还针对不同任务/攻击场景分别训练正常数据 checkpoint，并不是一个 checkpoint 无条件覆盖所有任务、攻击和领域。

---

#### A. 摘要与引言怎样定义问题？

##### A1. 一句话 problem statement

> 如何在完全没有恶意 agent 标签、也不知道未来攻击类型的条件下，只利用正常 MAS 交互数据训练一个检测器，在运行期间发现并隔离遭攻击的 agent？

它关注的系统问题仍然是 propagation vulnerability：

```text
少数 agent 被攻陷
        ↓
产生误导、泄密或错误消息
        ↓
正常 agent 把这些消息当作可信上下文
        ↓
攻击沿通信图传播，集体决策被污染
```

##### A2. 为什么 G-Safeguard 还不够？

G-Safeguard 需要真实的节点攻击标签：

```text
正常 agent：y=0
恶意 agent：y=1
```

而且公开实现对 PI、MA、TA 分别构造数据并训练攻击场景特定的 GNN。BlindGuard 认为这产生两个现实问题：

1. **availability：**真实攻击稀少、隐蔽且不断变化，难以收集足量、准确标注的恶意节点；
2. **generalizability：**针对某种已知攻击学到的二分类边界，遇到新攻击方式可能失效。

##### A3. 为什么直接使用传统无监督 GAD 也不够？

论文提出两个 gap：

```text
Gap 1：观察尺度不够
传统 GAD 多关注节点自己或局部邻居，缺少整个 MAS 的系统级上下文。

Gap 2：异常假设错位
传统 GAD 常把稀有连接、低同质性等结构偏离当异常；
MAS 攻击往往拓扑完全正常，只是语义、意图和推理方向恶意。
```

##### A4. 问题的价值和紧迫性怎样论证？

论文的价值链条是：

```text
真实攻击无法穷举
→ 依赖攻击标签的检测器部署成本高、更新慢
→ MAS 又会放大单点攻击并传播
→ 因而需要只学“正常行为”、能发现未知偏离的 runtime 防线
```

这是一个很强的引言结构：problem、现有方法的现实障碍、技术 gap 和方案组件几乎一一对应。

---

#### B. 方法是什么？真正创新在哪里？

##### B1. 方法主链

```text
训练阶段：只收集正常 MAS 对话
        ↓
SentenceBERT：回复文本 → 节点向量 x_i
        ↓
随机选择正常节点，在嵌入空间添加方向性噪声
制造 synthetic corrupted nodes
        ↓
分层编码：self + neighbor + global
        ↓
监督对比学习：正常靠拢，正常与伪异常分开

部署阶段：真实 MAS 每轮回复
        ↓
计算每个节点相对于其他节点的异常分
        ↓
Top-K 或阈值选出可疑 agent
        ↓
剪除相关通信边，阻止下一轮传播
```

##### B2. 创新点 1：把监督的“识别已知攻击”改成单类的“学习正常边界”

BlindGuard 不要求 PI、TA、MA 的真实恶意节点作为训练答案。它学习正常行为所在区域，测试时把偏离正常区域的节点视为可疑。

这不是“完全没有任何训练信号”。它会自己制造 corrupted 节点并赋予伪标签，再使用监督对比损失训练；所谓无监督，准确含义是：

> 不使用真实攻击者标签或真实攻击样本，而不是模型完全不训练。

##### B3. 创新点 2：MAS 专用的 self–neighbor–global 分层表示

每个 agent 的最终表示同时包含：

1. self：自己当前说了什么；
2. neighbor：直接邻居整体说了什么；
3. global：整个 MAS 的平均语义状态。

它同时处理：

```text
孤立攻击者：自己与邻居不一致
串通攻击群：内部彼此一致，但与全局系统不一致
```

##### B4. 创新点 3：方向性 corruption + 对比学习

作者没有在原始文本上编写假攻击，而是在正常回复的嵌入向量上增加按原向量长度缩放的随机方向噪声：

\[
\widetilde{\mathbf x}_i
=\mathbf x_i+\alpha\|\mathbf x_i\|_2
\frac{\boldsymbol\epsilon_i}{\|\boldsymbol\epsilon_i\|_2}.
\]

直觉是把一个正常节点从正常语义区域向某个方向推开，得到不属于任何具体攻击类型的伪异常。然后对比学习建立“正常内部紧凑、异常与正常分离”的 margin，减少对某个具体攻击签名的过拟合。

##### B5. 创新点 4：形成 unknown-attack detect–contain 流程

外层“检测后剪边”主要继承 G-Safeguard，真正新增的是无攻击标签下的检测器和训练策略。因此最准确的创新定位是：

> BlindGuard 创新主要在 unknown-attack detector，而不是 remediation；remediation 仍然是拓扑隔离。

---

#### C. 顶会为什么可能收下？

不能仅用“用了无监督学习”解释。更完整的中稿理由是：

##### C1. 问题新且现实

它正面击中上一代 G-Safeguard 最明显的部署缺陷：实际系统不可能为未来每一种攻击都提前收集节点级标签并重训检测器。

##### C2. gap 与机制对应得非常整齐

```text
缺少多层上下文
→ self + neighbor + global encoder

结构异常假设不适合语义攻击
→ semantic corruption

真实攻击标签不可得
→ synthetic anomalies + contrastive learning

恶意影响会传播
→ runtime pruning
```

这种“每个组件都回答一个引言 gap”的论文结构，对审稿人很友好。

##### C3. 不是只报检测 AUC，也测了系统后果

论文同时报告：

- AUC：恶意节点排序/区分能力；
- ASR@3：三轮传播后的攻击成功率；
- ACC：剪边后 MAS 的任务准确率；
- clean accuracy：无攻击时是否破坏正常协作；
- latency/complexity：部署开销。

这比只证明“检测器能分类”更像完整防御论文。

##### C4. 实验维度较广

- 三类攻击面：PI、TA、MA；
- 六个任务配置：CSQA、MMLU、GSM8K、InjecAgent、PoisonRAG、MA-CSQA；
- 四种拓扑：chain、tree、star、random；
- 多种 backbone：GPT-4o-mini、DeepSeek-V3、Qwen3-30B-A3B，并补充 Qwen3-8B；
- 8-agent 主设置及 20/50-agent 扩展；
- 未见攻击迁移、消融、阈值、K=2、串通、自适应、clean utility 和失败案例。

##### C5. 性能与实用性故事成立

它整体显著优于 DOMINANT、PREM、TAM 等通用无监督 GAD，并在多数设置中接近有真实攻击标签优势的 G-Safeguard。端到端三轮平均时间由 0.53 分钟增至 0.56 分钟，论文据此主张额外延迟较小。

综合判断：

> ACL 接收它，核心不是算法每一块都全新，而是它找到了一个重要且及时的 MAS 防御设定，用清晰、专门化的机制和较完整实验把“只用正常数据防未知攻击”这个故事闭合了。

---

#### D. Threat model：攻击者与防御者分别能做什么？

##### D1. 攻击者能力

主实验中：

- 系统有一部分 agent 被 compromise；
- 默认恰好 3 个被攻击节点；
- 攻击面包括 system prompt、memory 和 tool/plugin；
- 恶意节点可生成错误、误导或有害回复；
- 消息通过正常通信图影响其他 agent；
- 附录额外考虑简单防御感知 PI 和 sacrificial-decoy 串通。

##### D2. 防御者能力

- 训练时拥有一组确定为干净的正常 MAS 对话；
- 运行时看到所有 agent 回复和完整通信拓扑；
- 能使用冻结的 SentenceBERT 编码回复；
- 能在第一轮生成后、下一轮传播前执行监控；
- 能修改通信图、隔离高风险节点；
- 主实验知道修复预算 \(K=3\)，且真实攻击者数也恰好是 3。

##### D3. 没有覆盖或覆盖较弱的攻击能力

- 攻击者不能直接篡改 BlindGuard 检测器、SentenceBERT 或拓扑控制器；
- 没有系统研究攻击者操纵异常分数、全局均值或检测阈值；
- 没有测试攻击者动态改变通信拓扑；
- 没有测试长期慢速投毒和跨多轮逐渐漂移；
- 工具调用参数、memory 内部状态与真实外部副作用没有被完整纳入检测表示；
- 多数攻击仍是作者预设的三个攻击家族，真正开放世界攻击覆盖有限。

因此它的 threat model 更准确地说是：

> 检测器不知道攻击类型或真实恶意标签，但攻击通过可观察的 agent 回复产生语义偏离，且监控与剪边基础设施本身可信。

---

#### E. 论文如何证明强攻击面下仍然有效？

##### E1. 多攻击类型

- Prompt injection：CSQA、MMLU、GSM8K；
- Tool attack：InjecAgent；
- Memory poisoning：PoisonRAG、CSQA。

这证明它至少没有只在一种 prompt attack 上刷表。

##### E2. 多拓扑

chain、tree、star、random 用来检验不同传播路径下检测与剪边是否仍有效。

##### E3. 多 backbone

GPT-4o-mini、DeepSeek-V3、Qwen3-30B-A3B，以及较弱的 Qwen3-8B，用来检验回复风格和模型易感性变化后是否仍能工作。

##### E4. 未见攻击迁移

论文让 G-Safeguard 在 PI 上训练，再到同一 CSQA 任务测试未见 MA；BlindGuard 不使用攻击样本训练。在四种拓扑上：

```text
G-Safeguard AUC：59.56 / 60.44 / 64.00 / 60.44
BlindGuard  AUC：73.33 / 78.67 / 75.56 / 78.22
```

BlindGuard 的 ASR 在三种拓扑更低，在 random 上持平。这是论文支持“未知攻击泛化”的最直接证据。

##### E5. 规模扩展

PoisonRAG 的 R3 ASR：

```text
20 agents：No Defense 29.51 → BlindGuard 5.57
50 agents：No Defense 20.92 → BlindGuard 3.76
```

##### E6. 消融

移除 neighbor 或 global 表示都会降低性能；两者同时移除下降更明显。它支持 Gap 1 并非只写在引言里，而是方法确实利用了多层上下文。

##### E7. 额外压力测试

- 固定预算之外的 0.5 阈值检测；
- \(K=2\) 的受限修复预算；
- sacrificial-decoy + stealthy clique 串通；
- 试图模仿正常推理过程的简单自适应 PI；
- 不同 corruption 强度 \(\alpha\)；
- failure case 分析。

这些使它的防御论证比 G-Safeguard 在 adaptive attack 方面更完整。

---

#### F. Remediation 后任务效用是否可接受？

论文给出了三类证据：

1. 攻击下，BlindGuard 在降低 ASR 的同时提高 MAS 最终 ACC；
2. clean CSQA 中，PI 设置多数拓扑保持 90% 左右，random 从无防御 90.0% 变为 88.3%；MA 设置各拓扑保持 100%；
3. 三轮平均延迟约从 0.53 分钟增至 0.56 分钟。

因此在论文测试范围内，可说：

> BlindGuard 的剪边通常带来正的安全—效用净收益，clean utility 损失较小，额外延迟也较低。

但不能扩大为“剪边无害”：主实验恰好隔离 Top-3，误报可能剪掉关键正常 agent；clean utility 只在有限 CSQA 配置中验证，而且真实工作流中的工具执行、长任务和角色依赖可能对误剪更敏感。

---

#### G. 有没有自适应攻击？

有，但强度有限。

作者构造了一个防御感知 PI：把正确答案放入攻击提示，并要求恶意 agent 模仿正确答案的推理过程，再把攻击者指定的答案包装成看似正常的推理，以减少语义偏离。

其 AUC 约为 76.00–83.56，R3 ASR 约为 20.67–27.67。另有 sacrificial-decoy 串通攻击：一个明显跑题的节点吸引检测器，其他攻击者保持细微偏置和局部一致。

这比完全不做 adaptive evaluation 更好，但仍不能证明对强自适应攻击 robust，因为：

- 仅测试 PI + CSQA + GPT-4o-mini；
- 攻击策略由作者手工设计，搜索空间很小；
- 没有直接优化 anomaly score 的白盒攻击；
- 没有攻击全局平均表示、SentenceBERT 或 Top-K 排名；
- 没有自适应工具攻击、memory attack 和长期慢速攻击。

准确结论是：

> 论文对两种初步防御感知策略展现韧性，但没有完成系统性的强自适应攻击评估。

---

#### H. “未知攻击”这个 claim 有多强？

##### H1. 成立的部分

- 训练不需要真实攻击节点；
- 不需要 PI/TA/MA 标签来训练二分类器；
- 相比针对 PI 训练的 G-Safeguard，对未见 MA 的迁移更好；
- synthetic corruption 不绑定具体恶意关键词。

##### H2. 需要克制的部分

1. **未知不等于无假设。**方法明确假设攻击会使节点偏离正常语义和上下文；on-topic mimicry 会破坏该假设。
2. **任务/领域并非完全未知。**公开实现为 PI 的 MMLU、CSQA、GSM8K，以及 MA、MA-CSQA、TA 分别生成正常训练数据并训练 checkpoint。它更像“场景内未知攻击”，不是一次训练后跨所有领域通用。
3. **主实验知道攻击数量。**所有测试恰好 3 个攻击者，主修复也选择 Top-3；这给了部署时通常不知道的先验。阈值和 \(K=2\) 实验有所缓解，但不是主结果。
4. **测试攻击家族仍由实验者预先选定。**PI、TA、MA 覆盖面不错，却不是开放世界所有未知行为。
5. **异常比例隐含多数正常假设。**全局平均表示在正常节点占多数时较可靠；若攻击者成为多数或成功拖动全局语义中心，异常分可能失效。

因此组会上应说：

> BlindGuard 实现的是 attack-label-free、attack-agnostic 的场景内语义异常检测，对未见攻击类型具有证据支持；“完全开放世界 universal defense”仍是偏强表述。

---

#### I. 最值得指出的实验与方法缺口

##### I1. Top-K 使用了真实攻击者数量先验

主设置恰好 3 个攻击者，防御也恰好剪 Top-3。这不等于标签泄漏，但属于较强的数量 oracle。现实系统不知道是 0、1、3 还是 10 个攻击者。

##### I2. 规模实验可能随规模变大而变容易

如果 20-agent 和 50-agent 系统仍只有 3 个攻击者，那么攻击者比例从 15% 降到 6%。正常节点越多，全局平均越稳定，Top-3 也更容易覆盖全部攻击者。因此该实验支持“代码能运行在大图上”，但不足以单独证明攻击比例固定时的 scaling robustness。

##### I3. synthetic corruption 与真实攻击之间仍有 gap

随机方向噪声制造的是 off-manifold 异常；真实攻击可能是语义自然、风格一致、只在关键事实或工具参数上恶意的 on-manifold 异常。

##### I4. 只看粗粒度句向量

SentenceBERT 把整段回复压成单个向量，可能丢失少量关键恶意 token、工具参数、memory 修改位置和角色约束。这也是 XG-Guard 后续用 token-level 解释和细粒度检测切入的空间。

##### I5. 相对群体异常不等于恶意

创新、少数派但正确的 agent 可能因与邻居和全局不一致而被误报；多个攻击者也可能把全局共识拖向错误方向。

##### I6. 跨拓扑与跨任务 claim 需核对 checkpoint

架构可以接受不同图，但“在四种拓扑上都测试”不自动等于“同一 checkpoint 从某一拓扑零样本迁移到其他拓扑”。公开训练流程还显示不同数据集/攻击目录分别训练模型，说明通用性更多体现在方法范式，而不一定是一个 universal checkpoint。

##### I7. 仍然是事后遏制

BlindGuard 必须先看到第一轮回复；已经发生的工具调用、数据泄露或 memory 写入不会因后续剪边自动撤销。

---

#### J. 它在 self-healing 闭环里停在哪一步？

BlindGuard 做到了：

\[
\text{observe}\rightarrow\text{detect}\rightarrow\text{isolate}.
\]

它没有系统做到：

\[
\text{diagnose}\rightarrow\text{repair}\rightarrow
\text{recover}\rightarrow\text{verify}\rightarrow\text{reintegrate}.
\]

它能阻止可疑 agent 继续发消息，但不能：

- 判断攻击来自 prompt、memory 还是 tool；
- 清理被投毒 memory；
- 回滚已经执行的工具动作或数据外传；
- 修复被污染的正常 agent 上下文；
- 重建/替换 compromised agent；
- 验证恢复后的系统已经安全；
- 在安全后把隔离节点重新接入系统。

所以它是 unknown-attack containment，而不是完整 self-healing。

---

#### K. 对 Trustworthy & Self-Healing MAS proposal 的启示

##### K1. 可以直接复用的骨架

1. 只用 clean data 学习正常行为基线，减少对攻击标签依赖；
2. self–neighbor–global 多尺度安全观测；
3. runtime 每轮安全 hook；
4. anomaly score 而非硬二分类，便于建立连续 trust score；
5. topology intervention 作为快速 containment；
6. unknown attack、cross-backbone、cross-topology、adaptive attack 的实验框架。

##### K2. 我们可以向前推进的地方

```text
单轮句向量
→ 多轮时序状态 + token/tool/memory provenance

语义异常分
→ 动态信任分 + 不确定性 + 因果诊断

固定 Top-K 硬剪边
→ 降权、限流、沙箱、角色替代、风险分级处置

不知道攻击来源
→ 定位 prompt / memory / tool / message channel

只阻止未来传播
→ memory 清理、工具回滚、上下文重建、任务重规划

隔离后结束
→ 恢复验证、安全重接入和持续监测
```

最有价值的 proposal 接口是：

> 把 BlindGuard 的 attack-agnostic anomaly score 当成触发器；检测到异常后，由诊断模块寻找污染源，再选择与攻击面匹配的恢复动作，最后通过独立 Inspector 验证并决定是否重新接入。

---

#### L. 组会口头汇报版本

> BlindGuard 针对的是 G-Safeguard 依赖已知攻击标签、难以覆盖未来新攻击的问题。它只用正常 MAS 对话训练：先把每个 agent 的回复编码成向量，再对部分正常向量施加方向性语义 corruption 来制造伪异常，通过 self、neighbor、global 三层编码和监督对比学习建立正常行为边界。运行时，它根据每个 agent 与整个系统表示的平均相似度计算异常分，选出高风险节点并剪边隔离。论文的中稿亮点是把无攻击标签的 unknown-attack detection 与 MAS 拓扑遏制结合，并通过 PI、TA、MA，四类拓扑、多种 LLM、未见攻击迁移、20/50-agent 扩展、消融、clean utility、串通和简单自适应攻击进行较完整论证。它确实比传统无监督 GAD 稳定，也在 PI 训练、MA 测试时优于监督 G-Safeguard。但“未知攻击”不是无限制的：方法假设攻击会造成语义偏离，主实验又恰好知道有 3 个攻击者并剪 Top-3，公开实现还按任务/攻击场景分别训练正常数据 checkpoint。它最终仍只做到 observe、detect、isolate，不能诊断攻击来源、清理 memory、回滚工具副作用或验证恢复。因此它为我们的 proposal 提供了 attack-agnostic 检测与隔离骨架，而真正的 self-healing 空间在时序诊断、分层恢复、验证和安全重接入。

### 2026-08-10｜公式（1）：为什么 BlindGuard 论文先介绍监督防御？

**Q：** 公式（1）是什么意思？为什么这里需要监督，BlindGuard 不是无监督方法吗？

#### 先澄清位置

公式（1）不是 BlindGuard 自己的训练目标，而是论文在预备知识中定义的“上一代监督防御范式”，代表 G-Safeguard 等方法。作者先写出监督方法需要什么，再引出 BlindGuard 要去掉真实攻击标签。

#### 原公式

\[
\mathcal L_{\mathrm{sup}}
=\sum_{v_i\in\mathcal V}
\ell_{\mathrm{CE}}
\left(y_i,f_\theta(\widetilde{\mathcal G},v_i)\right).
\]

其计算流程为：

```text
整张被攻击图 G~ + 当前节点 v_i
              ↓
       检测器 f_θ
              ↓
    预测恶意概率 p_i
              ↓
与真实标签 y_i 做交叉熵
              ↓
所有节点损失相加，更新 θ
```

#### 逐个符号

- \(\mathcal L_{\mathrm{sup}}\)：监督训练的总损失；越小表示预测越接近真实节点标签。
- 下标 \(\mathrm{sup}\)：supervised，表示监督式。
- \(\sum\)：求和，把每个节点的分类错误加起来。
- \(v_i\)：第 \(i\) 个 agent 节点；\(v\) 是 node，\(i\) 是节点编号。
- \(v_i\in\mathcal V\)：遍历节点集合 \(\mathcal V\) 中的每个 agent。
- \(\widetilde{\mathcal G}\)：一张已经受到攻击的 MAS 交互图；波浪号表示它不是干净图。
- \(y_i\in\{0,1\}\)：节点 \(v_i\) 的真实标签；0 是正常，1 是恶意。
- \(f_\theta\)：GAD 检测器；\(\theta\) 是模型中通过训练学习的参数。
- \(f_\theta(\widetilde{\mathcal G},v_i)=p_i\in[0,1]\)：检测器结合整张图与目标节点，输出该节点是恶意节点的预测概率。
- \(\ell_{\mathrm{CE}}\)：cross-entropy loss，交叉熵损失，用来比较真实答案 \(y_i\) 与预测概率 \(p_i\)。

论文写 \(f_\theta:\mathbb R^d\rightarrow[0,1]\)，是把输入简写成节点最终的 \(d\) 维表示。更完整地理解，图和节点先被 GNN 编码成向量 \(\mathbf z_i\in\mathbb R^d\)，再由分类头输出概率：

\[
(\widetilde{\mathcal G},v_i)
\longrightarrow \mathbf z_i
\longrightarrow f_\theta(\mathbf z_i)=p_i.
\]

#### 交叉熵内部是什么？

二分类交叉熵通常写为：

\[
\ell_{\mathrm{CE}}(y_i,p_i)
=-\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
\]

当真实节点是恶意节点，\(y_i=1\)：

\[
\ell=-\log p_i.
\]

模型只有把 \(p_i\) 预测得接近 1，损失才小。

当真实节点是正常节点，\(y_i=0\)：

\[
\ell=-\log(1-p_i).
\]

模型只有把 \(p_i\) 预测得接近 0，损失才小。

数值例子：

| 真实标签 | 预测恶意概率 | 损失约为 | 含义 |
|---|---:|---:|---|
| \(y=1\) | \(p=0.9\) | 0.105 | 恶意节点被正确识别，惩罚小 |
| \(y=1\) | \(p=0.1\) | 2.303 | 恶意节点被当成正常，惩罚大 |
| \(y=0\) | \(p=0.1\) | 0.105 | 正常节点被正确识别，惩罚小 |
| \(y=0\) | \(p=0.9\) | 2.303 | 正常节点被误报为恶意，惩罚大 |

#### 为什么这种方法需要监督？

因为训练时必须有人告诉模型每个节点的真实身份 \(y_i\)：

```text
v_1：正常 → y_1=0
v_2：恶意 → y_2=1
v_3：正常 → y_3=0
```

没有这些标签，交叉熵就不知道应该把哪个节点的预测推向 1、哪个推向 0，也就不能按照公式（1）训练二分类器。

#### BlindGuard 去掉了什么？

BlindGuard 训练数据只有正常图：

```text
所有真实节点都是正常行为
没有 V_mal
没有真实攻击标签 y_i
不知道未来是 PI、TA 还是 MA
```

它通过对正常节点的嵌入添加 corruption，自己制造伪异常：

```text
原始正常向量 → 伪标签 0
corrupted 向量 → 伪标签 1
```

随后用这些伪标签进行监督对比学习。因此 BlindGuard 更精确的技术表述是：

> 在数据需求上是无真实攻击标签的 unsupervised / self-supervised defense；在优化过程中会使用由 corruption 自动产生的伪标签，并采用 supervised contrastive loss。

这两句话不矛盾。论文所谓“无监督”是指不需要人工或真实攻击者标签，不是指训练算法内部永远不能出现 0/1 伪标签。

#### 最小例子

一张被攻击图中有四个节点：

```text
真实标签：A=0，B=0，C=1，D=0
预测概率：A=.10，B=.20，C=.80，D=.40
```

公式（1）会分别计算四个交叉熵，再相加：

\[
\mathcal L_{\mathrm{sup}}
=\ell(0,.10)+\ell(0,.20)+\ell(1,.80)+\ell(0,.40).
\]

训练不断调整 \(\theta\)，使正常节点概率向 0 靠近、恶意节点概率向 1 靠近。

而 BlindGuard 没有真实的 \(C=1\) 告诉它，所以不能直接使用这个真实标签训练逻辑；它改为从正常节点制造 corrupted counterpart，学习正常行为周围的表示边界。

#### 一句话总结

> 公式（1）描述的是 BlindGuard 要替代的监督基线：把整张攻击图和节点输入检测器，输出恶意概率，再用真实节点标签通过交叉熵训练。BlindGuard 本身不使用真实恶意节点标签，而是只用正常数据制造 corrupted 伪异常并做对比学习，所以论文仍把它称为无监督防御。

### 2026-08-10｜公式（2）：BlindGuard 的节点特征是否只编码当前 response？与 G-Safeguard 有何不同？

**Q：** BlindGuard 构造智能体节点是否只需要把 response 转换成向量？为什么不像 G-Safeguard 那样把其他节点的信息聚合进来？

#### 核心答案

公式（2）只描述“原始节点特征构造”这一步，因此每个 agent 暂时只把自己的文本回复独立转换成向量。BlindGuard 并非不聚合其他节点；它在紧接着的 hierarchical encoder 中，再将 self、neighbor 和 global 三个层次的信息聚合成最终 agent 表示。

完整流程是：

```text
阶段 1：原始节点特征
每个 agent 的 response R_i
        ↓ SentenceBERT
自己的原始节点向量 x_i

阶段 2：上下文聚合
x_i + 邻居节点向量 + 全图节点向量
        ↓ hierarchical encoder
包含个体/局部/全局上下文的最终表示 z_i

阶段 3：异常检测
z_i 与系统内其他 z_j 比较
        ↓
异常分数 s(v_i)
```

#### 公式（2）逐项解释

\[
\mathbf x_i=\operatorname{SentenceBERT}(R_i)\in\mathbb R^D.
\]

- \(v_i\)：第 \(i\) 个 agent 节点；
- \(R_i\)：agent \(v_i\) 当前的文本 response；此处的 \(R\) 是 response，不是 agent；
- \(\operatorname{SentenceBERT}\)：冻结的预训练文本编码器；
- \(\mathbf x_i\)：节点 \(v_i\) 的原始语义向量；
- \(D\)：向量的维度；例如具体 SentenceBERT 可能输出数百维向量；
- \(\mathbb R^D\)：由 \(D\) 个实数组成的向量空间。这里的黑板粗体 \(\mathbb R\) 表示 real numbers，不是 response \(R_i\)。

例如原始回复是：

```text
R_i = “6 erasers cost $12 and 8 pencils cost $24, so the answer is $36.”
```

SentenceBERT 会得到类似：

```text
x_i = [0.12, -0.31, 0.08, ..., 0.44]
```

真实向量有 \(D\) 个数，而不是只有示例中的几个。每个维度通常没有“价格”“答案”等可直接命名的单独含义；整体向量的位置编码句子的综合语义。

“稠密向量”表示大部分维度都有非零数值，与高维、绝大多数位置为零的 sparse vector 相对。这里的“紧凑”表示把可变长度文本转为固定长度语义表示，并不等于后文所有语义信息都不会损失。

#### 公式（2）完成后，图中有什么？

假设有四个 agent：

```text
A 的回复 → x_A
B 的回复 → x_B
C 的回复 → x_C
D 的回复 → x_D
```

把它们按行放在一起形成节点特征矩阵：

\[
\mathbf X=
\begin{bmatrix}
\mathbf x_A\\
\mathbf x_B\\
\mathbf x_C\\
\mathbf x_D
\end{bmatrix}
\in\mathbb R^{N\times D}.
\]

但此时 \(\mathbf x_A\) 仍只表示 A 自己说了什么，还不知道 B/C/D 的内容。图模型还同时需要邻接矩阵 \(\mathbf A\)，它告诉模型谁与谁通信。

所以完整输入至少包括：

```text
X：所有 agent 的 response 向量
A：agent 间的通信拓扑
```

仅仅有单个 \(x_i\) 还不足以完成 BlindGuard。

#### BlindGuard 在哪里聚合其他节点？

紧接公式（2），分层编码器为节点 \(i\) 计算：

\[
\mathbf h_i^{\mathrm s}=\mathbf x_i,
\]

\[
\mathbf h_i^{\mathrm n}
=\sum_{j\in\mathcal N(i)}\widehat A_{ij}\mathbf x_j,
\]

\[
\mathbf h_i^{\mathrm g}
=\frac1N\sum_{k=1}^{N}\mathbf x_k.
\]

分别表示：

- \(\mathbf h_i^{\mathrm s}\)：self/agent-level，节点自己的回复；
- \(\mathbf h_i^{\mathrm n}\)：neighbor-level，对节点 \(i\) 的邻居回复进行加权聚合；
- \(\mathbf h_i^{\mathrm g}\)：global/system-level，对整张图所有 agent 的回复取平均；
- \(\mathcal N(i)\)：节点 \(i\) 的邻居集合；
- \(\widehat A_{ij}\)：归一化后的邻接权重；
- \(N\)：agent 总数。

然后三者拼接：

\[
\mathbf z_i=g_\theta
\left(
\mathbf h_i^{\mathrm s}\parallel
\mathbf h_i^{\mathrm n}\parallel
\mathbf h_i^{\mathrm g}
\right).
\]

- \(\parallel\)：concatenation，把三个向量首尾连接；
- \(g_\theta\)：可训练的 MLP；
- \(\mathbf z_i\)：真正用于后续对比学习和异常打分的最终 agent 表示。

所以：

```text
x_i：只有自己的原始回复
z_i：自己的回复 + 邻居信息 + 全局系统信息
```

#### 与 G-Safeguard 到底有什么不同？

两者并不是“一个聚合、一个不聚合”，而是都先构造单节点表示，再加入图上下文；区别在于原始信息和聚合机制。

| 比较项 | G-Safeguard | BlindGuard |
|---|---|---|
| 原始节点输入 | agent 的历史回复记录/话语历史 | 公式中主要是当前 response \(R_i\) |
| 边信息 | 显式编码每条定向边上的交互历史，形成 edge embedding | 主要使用邻接矩阵表示谁与谁相连，没有同等详细的文本 edge history |
| 局部聚合 | 多层 edge-aware GNN message passing，逐层吸收邻居信息 | 对邻居节点向量做一次归一化加权求和 |
| 全局信息 | 主要通过多层局部传播间接获得，层数有限时不一定看到整图 | 直接对全体节点取平均，显式加入 global context |
| 最终目标 | 监督二分类攻击概率 | 无真实攻击标签的异常表示与相似度评分 |

G-Safeguard 的大致链条：

```text
节点历史文本 + 边上消息历史
          ↓
多层 edge-aware GNN
          ↓
节点攻击概率
```

BlindGuard 的链条：

```text
当前节点回复向量
          ↓
self + neighbor平均 + global平均
          ↓
MLP / 对比表示
          ↓
相对系统的异常分数
```

#### 为什么 BlindGuard 要这样设计？

1. **训练便宜。**SentenceBERT 冻结，只训练较小的分层编码器，无需微调 backbone LLM 或 SentenceBERT。
2. **显式解决 Gap 1。**self、neighbor、global 分别对应个体、局部和系统三个上下文尺度。
3. **适合无监督异常检测。**它不需要识别某种具体攻击签名，只需判断节点是否偏离邻居和整个系统的正常语义模式。
4. **拓扑适配简单。**邻居聚合由邻接矩阵决定，全局平均不依赖固定 agent 数量。

#### 这种简化丢失了什么？

公式（2）显示，BlindGuard 的核心节点特征主要来自 response 文本。因此角色、memory、tool call、工具参数和外部状态只有在它们影响最终回复时才被间接观察。

另外，相较于 G-Safeguard 的历史与 edge embeddings，BlindGuard 的表示更粗：

- 当前 response 的一个句向量可能丢失多轮演化；
- 整句压成一个向量可能稀释少量关键恶意 token；
- 邻居加权平均可能混合来自不同角色的差异；
- 全局平均可能被多个串通攻击者拖偏；
- 工具已执行的副作用不会仅靠 response 向量被完整捕捉。

这也是为什么它擅长检测明显的 context/semantic deviation，却可能漏掉 on-topic、风格一致的隐蔽操纵。

#### 最终结论

> 公式（2）确实只把每个 agent 当前的 response 独立转成原始节点向量 \(\mathbf x_i\)，但这不是 BlindGuard 的最终节点表示。随后 hierarchical encoder 会把节点自己的 \(\mathbf x_i\)、邻居聚合和全局平均拼接成 \(\mathbf z_i\)。G-Safeguard 也先构造单节点特征，再通过 edge-aware 多层 GNN 聚合；主要区别是 G-Safeguard 显式建模节点/边的交互历史，而 BlindGuard 使用更轻量的当前回复 + 邻居平均 + 全局平均，以支持只用正常数据进行无监督异常检测。

### 2026-08-10｜G-Safeguard 与 BlindGuard 方法论公式一对一比较

**Q：** 将两篇论文方法论部分的公式按执行阶段逐一对应，并解释相同点、不同点和各自输入输出。

#### 0. 全局对应关系

| 方法阶段 | G-Safeguard | BlindGuard |
|---|---|---|
| 图输入 | 每轮动态 utterance graph，含节点与文本边嵌入 | MAS 节点、邻接矩阵和当前回复嵌入 |
| 原始节点特征 | 当前回复 + 历史回复 | 当前 response |
| 边语义特征 | 有：每条有向边的消息历史 | 无同等公式：主要使用邻接关系/权重 |
| 上下文编码 | 多层、边感知 GNN message passing | self + one-hop neighbor + explicit global mean |
| 异常训练数据 | 真实恶意节点及真实 \(0/1\) 标签 | 正常节点 + corruption 生成的伪异常 |
| 训练目标 | 二元交叉熵，直接训练 attack classifier | 监督对比损失，训练表示空间 |
| 推理输出 | 节点属于攻击集合的概率 | 节点相对当前群体的异常分数 |
| 修复 | 删除高风险节点的 outgoing edges | 论文声称双向隔离，并只用保留消息生成下一轮回复 |

两条主链：

```text
G-Safeguard
历史节点文本 + 历史边文本
→ edge-aware L-layer GNN
→ sigmoid attack probability
→ threshold/high-risk set
→ prune outgoing edges

BlindGuard
当前 response
→ self + neighbor + global encoder
→ corruption-guided contrastive representation
→ negative mean similarity anomaly score
→ Top-K/threshold
→ isolate/prune and regenerate next round
```

---

#### Pair 1：图的总体表示

##### G-Safeguard

\[
\mathcal M^{(t)}=(\mathbf X^{(t)},\mathbf E^{(t)}),
\]

其中：

- \(t\)：第 \(t\) 轮；
- \(\mathcal M^{(t)}\)：该轮构造的 multi-agent utterance graph；
- \(\mathbf X^{(t)}\in\mathbb R^{N\times D}\)：\(N\) 个节点的文本嵌入；
- \(\mathbf E^{(t)}\in\mathbb R^{E^{(t)}\times D}\)：该轮每条通信边的文本嵌入；
- \(E^{(t)}\)：该轮边数。

G-Safeguard 的图显式保存两类语义：节点说过什么，以及每条有向边上传过什么。

##### BlindGuard

\[
\mathcal G=(\mathcal V,\mathcal E),\qquad
\mathbf A\in\{0,1\}^{N\times N}.
\]

- \(\mathcal V\)：agent 节点集合；
- \(\mathcal E\)：通信边集合；
- \(\mathbf A\)：邻接矩阵，表示谁向谁通信。

BlindGuard 后续为节点生成 \(\mathbf X\)，但没有像 G-Safeguard 一样为每条边的消息历史构造 \(D\) 维 edge embedding。

##### 核心区别

```text
G-Safeguard：语义化的节点 + 语义化的边
BlindGuard：语义化的节点 + 表示连接关系的邻接矩阵
```

---

#### Pair 2：单个 agent 的原始节点特征

##### G-Safeguard

\[
\mathbf h_i^{(t)}coloneqq\mathbf X_i^{(t)}
=\mathcal T\left(
\mathbf R_i^{(t)},
\bigcup_{k=1}^{t-1}\mathbf R_i^{(k)}
\right).
\]

- \(C_i\)：第 \(i\) 个 agent；
- \(\mathbf R_i^{(t)}\)：它第 \(t\) 轮的回复；
- \(\bigcup_{k=1}^{t-1}\mathbf R_i^{(k)}\)：此前各轮回复的历史集合；
- \(\mathcal T\)：MiniLM 等文本嵌入函数；
- \(\mathbf X_i^{(t)}\)：第 \(i\) 行节点特征；
- \(\mathbf h_i^{(t)}\)：agent 在第 \(t\) 轮的初始节点表示。

直觉：

```text
这个 agent 当前说了什么
+
它以前说过什么
→ 一个 D 维历史语义表示
```

##### BlindGuard

\[
\mathbf x_i=\operatorname{SentenceBERT}(R_i)
\in\mathbb R^D.
\]

- \(v_i\)：第 \(i\) 个 agent；
- \(R_i\)：当前用于检测的 response；
- \(\mathbf x_i\)：原始节点向量；
- SentenceBERT 在训练中冻结。

直觉：

```text
这个 agent 当前说了什么
→ 一个 D 维语义表示
```

##### 一对一结论

两者都先把 agent 文本变成向量，但：

```text
G-Safeguard 的 x/h：显式包含多轮历史
BlindGuard 的 x：公式层面主要是当前 response
```

---

#### Pair 3：通信边如何表示？

##### G-Safeguard 独有公式

\[
\mathbf e_{ij}^{(t)}
=\mathcal F\left(
[\mathcal T(\mathbf R_{i\to j}^{(1)}),\ldots,
\mathcal T(\mathbf R_{i\to j}^{(K)})]
\right).
\]

- \(\mathbf R_{i\to j}^{(k)}\)：第 \(k\) 次从 agent \(i\) 传给 agent \(j\) 的消息；
- \(K\le t\)：这条边截至当前实际发生通信的次数；
- \(\mathcal T\)：把每条消息转成向量；
- \(\mathcal F\)：可学习、置换不变的融合函数；
- \(\mathbf e_{ij}^{(t)}\)：边 \(i\to j\) 的固定维历史语义表示。

直觉：

```text
i→j 这条通道以前传过的所有消息
→ 压缩成一个 edge vector
```

##### BlindGuard 的对应物

BlindGuard 没有同等的文本边历史公式。它主要通过：

\[
\widehat A_{ij}
\]

表示节点 \(i\) 与 \(j\) 是否相连、聚合时邻居 \(j\) 占多少权重。

##### 一对一结论

```text
G-Safeguard：这条边存在吗 + 边上历史传了什么
BlindGuard：这条边存在吗/聚合权重是多少
```

因此 G-Safeguard 对传播路径的语义来源建模更细，BlindGuard 的边表示更轻量。

---

#### Pair 4：怎样把其他 agent 的信息聚合进节点？

##### G-Safeguard：L 层 edge-aware message passing

\[
\mathbf h_i^{(t,l)}
=\operatorname{COMB}\left(
\mathbf h_i^{(t,l-1)},
\operatorname{AGGR}
\left\{
\psi(\mathbf h_j^{(t,l-1)},\mathbf e_{ij}^{(t)})
:C_j\in\mathcal N_{\mathrm{in}}^{(t)}(C_i)
\right\}
\right).
\]

- \(l\)：GNN 层编号；
- \(\mathbf h_i^{(t,l-1)}\)：节点 \(i\) 上一层表示；
- \(\mathcal N_{\mathrm{in}}^{(t)}(C_i)\)：本轮向 \(i\) 传消息的入邻居；
- \(\psi(\mathbf h_j,\mathbf e_{ij})\)：结合邻居 \(j\) 的表示和边 \(i,j\) 的语义；
- \(\operatorname{AGGR}\)：把所有邻居消息聚合起来；
- \(\operatorname{COMB}\)：把自己的旧表示与邻居聚合结果融合；
- \(\mathbf h_i^{(t,L)}\)：经过 \(L\) 层后的最终节点表示。

直觉：

```text
第1层：吸收一跳邻居及边上的语义
第2层：继续吸收二跳范围
……
第L层：形成最终上下文表示
```

##### BlindGuard：显式三层 summarization

\[
\mathbf h_i^{\mathrm s}=\mathbf x_i,
\]

\[
\mathbf h_i^{\mathrm n}
=\sum_{j\in\mathcal N(i)}\widehat A_{ij}\mathbf x_j,
\]

\[
\mathbf h_i^{\mathrm g}
=\frac1N\sum_{k=1}^{N}\mathbf x_k,
\]

随后：

\[
\mathbf z_i=g_\theta\left(
\mathbf h_i^{\mathrm s}parallel
\mathbf h_i^{\mathrm n}parallel
\mathbf h_i^{\mathrm g}
\right).
\]

- \(\mathbf h_i^{\mathrm s}\)：自己的 response；
- \(\mathbf h_i^{\mathrm n}\)：一跳邻居加权平均；
- \(\mathbf h_i^{\mathrm g}\)：全图所有节点平均；
- \(\parallel\)：拼接；
- \(g_\theta\)：可训练 MLP；
- \(\mathbf z_i\)：最终分层 agent 表示。

##### 一对一结论

```text
G-Safeguard：逐层传播，显式使用 edge semantics；全局信息靠多跳间接到达

BlindGuard：一次得到 self、one-hop neighbor 和 whole-graph global；不使用详细 edge semantics
```

因此：

- G-Safeguard 更强调“恶意内容沿哪条边传播”；
- BlindGuard 更强调“节点相对局部与全局正常上下文是否偏离”。

---

#### Pair 5：训练时异常样本从哪里来？

##### G-Safeguard

没有“制造异常”的公式，因为训练数据中已经有真实攻击节点：

\[
y_i\in\{0,1\},
\]

其中 \(y_i=1\) 表示真实恶意节点，\(y_i=0\) 表示正常节点。

##### BlindGuard：corruption 公式

\[
\widetilde{\mathbf x}_i
=\mathbf x_i
+\alpha\|\mathbf x_i\|_2
\frac{\boldsymbol\epsilon_i}
{\|\boldsymbol\epsilon_i\|_2},
\qquad
\boldsymbol\epsilon_i\sim\mathcal N(0,\mathbf I).
\]

- \(\mathbf x_i\)：正常 response 向量；
- \(\widetilde{\mathbf x}_i\)：人工制造的 corrupted 向量；
- \(\boldsymbol\epsilon_i\)：从高斯分布采样的随机噪声；
- \(\boldsymbol\epsilon_i/\|\boldsymbol\epsilon_i\|_2\)：只保留噪声方向，将长度归一化为 1；
- \(\alpha\|\mathbf x_i\|_2\)：corruption 的实际移动距离；
- \(\alpha\)：控制扰动强度。

直觉：

```text
正常语义点 x_i
→ 随机选一个方向
→ 按适当距离把它推离正常区域
→ 得到伪异常 x~_i
```

##### 一对一结论

```text
G-Safeguard：真实攻击者教模型什么是恶意
BlindGuard：从正常数据自己制造伪异常，学习正常区域的边界
```

---

#### Pair 6：训练损失怎样优化模型？

##### G-Safeguard：真实标签二元交叉熵

令：

\[
p_i
=p(C_i\in\mathcal V_{\mathrm{atk}}^{(t)}mid
\mathbf h_i^{(t,L)}).
\]

训练损失：

\[
\mathcal L_{\mathrm{GS}}
=-\mathbb E_{C_i,t}
\left[
y_i\log p_i
+(1-y_i)\log(1-p_i)
\right].
\]

含义：

```text
真实恶意 y_i=1 → 把 p_i 推向 1
真实正常 y_i=0 → 把 p_i 推向 0
```

它直接训练一个二元 attack classifier。

##### BlindGuard：伪标签监督对比损失

先定义余弦相似度：

\[
s_{i,j}
=\frac{\mathbf z_i^\top\mathbf z_j}
{\|\mathbf z_i\|\,\|\mathbf z_j\|}.
\]

再定义同类正样本集合：

\[
P_i=\{j\mid y_j=y_i,\ j\ne i\},
\]

其中此处的 \(y\) 是正常/人工 corrupted 的伪标签，而不是真实攻击标签。

损失：

\[
\mathcal L_{\mathrm{BG}}
=-\frac1N\sum_{i=1}^{N}
\frac1{|P_i|}\sum_{j\in P_i}
\log
\left(
\frac{e^{s_{i,j}/\tau}}
{e^{s_{i,j}/\tau}+
\sum_{k\notin P_i}e^{s_{i,k}/\tau}}
\right).
\]

- \(i\)：当前作为 anchor 的节点；
- \(P_i\)：与 \(i\) 同伪类别的节点；
- \(j\in P_i\)：希望与 \(i\) 靠近的正样本；
- \(k\notin P_i\)：希望与 \(i\) 分开的不同类样本；
- \(s_{i,j}\)：表示相似度；
- \(\tau\)：temperature，控制模型多强调相似度差异；
- \(|P_i|\)：正样本数量。

直觉：

```text
正常 ↔ 正常：拉近
corrupted ↔ corrupted：拉近
正常 ↔ corrupted：推远
```

##### 一对一结论

```text
G-Safeguard 优化“预测概率是否等于真实攻击标签”

BlindGuard 优化“表示空间中正常与伪异常是否分开”
```

这也是 supervised classification 与 unsupervised/self-supervised representation learning 的核心区别。

---

#### Pair 7：测试时怎样给节点打风险分？

##### G-Safeguard：sigmoid 攻击概率

\[
p_i
=p(C_i\in\mathcal V_{\mathrm{atk}}^{(t)}mid
\mathbf h_i^{(t,L)})
=\sigma\left(f_\theta(\mathbf h_i^{(t,L)})\right).
\]

- \(f_\theta\)：输出任意实数风险 logit；
- \(\sigma\)：sigmoid，将实数压到 \([0,1]\)；
- \(p_i\)：模型认为节点 \(i\) 是攻击节点的概率。

例如：

```text
A：p=.05
B：p=.83  ← 高风险
C：p=.12
```

这是相对固定训练边界的“绝对概率式”输出，尽管其概率是否校准还需实验验证。

##### BlindGuard：与当前群体的负平均相似度

\[
s(v_i)
=-\frac1N\sum_{j=1}^{N}
\operatorname{sim}(\mathbf z_i,\mathbf z_j).
\]

- 先计算节点 \(i\) 与系统中每个节点 \(j\) 的相似度；
- 取平均；
- 前面加负号，使“越不像群体”的节点得到越高异常分。

例子：

```text
正常节点平均相似度 = 0.80 → 异常分 = -0.80
可疑节点平均相似度 = 0.10 → 异常分 = -0.10
```

因为 \(-0.10>-0.80\)，所以可疑节点的异常分更高。

##### 一对一结论

```text
G-Safeguard：这个节点像不像训练时见过的攻击者？
→ attack probability

BlindGuard：这个节点像不像当前系统中的正常群体？
→ relative anomaly score
```

因此 BlindGuard 的分数不是严格的攻击概率，也不必位于 \([0,1]\)。

---

#### Pair 8：怎样从分数得到攻击者集合？

##### G-Safeguard

论文将识别出的高风险集合记为：

\[
\widetilde{\mathcal V}_{\mathrm{atk}}^{(t)}.
\]

其正文没有在方法公式里明确写固定阈值/Top-K 的集合生成式，概念上是根据较高 \(p_i\) 选择高风险节点。

##### BlindGuard

算法中明确使用：

\[
\mathcal V_{\mathrm{atk}}
=\operatorname{TopK}_{v_i}\ s(v_i),
\]

即选异常分最高的 \(K\) 个节点；论文也补充测试了阈值版本。

主实验 \(K=3\)，而真实攻击节点数也恰好为 3。

##### 一对一结论

```text
G-Safeguard：基于分类概率选择高风险节点
BlindGuard：基于相对异常排序选择 Top-K/超过阈值节点
```

---

#### Pair 9：怎样剪边修复？

##### G-Safeguard：删除攻击节点出边

\[
\mathcal E^{(t+1)}
\leftarrow
\mathcal E^{(t+1)}setminus
\bigcup_{C_i\in\widetilde{\mathcal V}_{\mathrm{atk}}^{(t)}}
\{e_{ij}^{(t)}\mid C_j\in\mathcal V\}.
\]

含义：对每个被判高风险的 \(C_i\)，删除它发往任意 \(C_j\) 的 outgoing edge。

```text
别人仍可能把消息发给 i
但 i 不能再把内容传播出去
```

##### BlindGuard：隔离可疑节点并更新下一轮输入

论文给出：

\[
\mathcal E^{(+)}
=\{e_{ij}\in\mathcal E^{(t)}mid
v_i\notin\mathcal V_{\mathrm{atk}}^{(t)}\}.
\]

随后：

\[
R_j^{(t+1)}
=LLM\left(
Q\cup
\{R_i^{(t)}\mid e_{ij}\in\mathcal E^{(+)}\}
\right).
\]

第二个公式的意思是：agent \(j\) 下一轮只读取保留下来的、被认为可信的 agent 回复。

论文文字称这是 bidirectional edge pruning、删除异常节点 incident edges，以实现完全隔离；但展示的集合公式只检查了边的一个端点 \(v_i\)。此外该论文对 \(e_{ij}\) 的方向索引在不同段落并不完全清楚。因此应区分：

```text
论文意图/文字：双向隔离异常节点
展示公式：按一个端点过滤边，严格方向取决于 e_ij 的索引约定
```

##### 一对一结论

```text
G-Safeguard：明确只剪高风险节点的出边，目标是停止传播

BlindGuard：声称把异常节点双向隔离，并显式写出正常 agent 下一轮只读取保留消息
```

两者都属于 containment，不会自动清理 memory 或回滚工具副作用。

---

#### 10. 最重要的方法论差异

##### 差异 A：时序粒度

```text
G-Safeguard：显式带 t，编码节点历史和边历史
BlindGuard：主体编码公式更像当前图快照，时序历史建模较弱
```

##### 差异 B：图语义粒度

```text
G-Safeguard：node semantics + edge semantics
BlindGuard：node semantics + adjacency/context summaries
```

##### 差异 C：全局信息来源

```text
G-Safeguard：通过 L 层消息传递间接扩大感受野
BlindGuard：直接加入全图平均表示
```

##### 差异 D：学习目标

```text
G-Safeguard：学习真实攻击分类边界
BlindGuard：学习正常行为周围的表示几何/margin
```

##### 差异 E：推理依据

```text
G-Safeguard：与训练攻击模式比较
BlindGuard：与当前 MAS 群体模式比较
```

##### 差异 F：各自更容易失败的情况

```text
G-Safeguard：新攻击与训练攻击签名不同，跨攻击类型失效

BlindGuard：攻击者与正常群体保持语义一致，或恶意多数拖偏全局中心
```

---

#### 11. 一页式记忆版

```text
G-Safeguard

R_i 当前+历史 ─T→ node h_i
R_i→j 边历史 ─T,F→ edge e_ij
node + semantic edge ─L层GNN→ h_i^(L)
h_i^(L) ─fθ,sigmoid→ attack probability p_i
真实标签 y_i ─BCE→ 训练分类器
高风险节点 → 删除 outgoing edges


BlindGuard

R_i 当前回复 ─SBERT→ node x_i
x_i ─corruption→ synthetic anomaly x~_i
self x_i + neighbor mean + global mean ─MLP→ z_i
正常/伪异常 ─SupCon→ 学表示空间
z_i 与全体 z_j 的负平均相似度 → anomaly score
Top-K/threshold → 隔离节点、只保留可信消息
```

#### 12. 最终总结

> 两篇论文都遵循“文本变图表示 → 图上下文编码 → 节点风险打分 → 剪边修复”的外层流程。G-Safeguard 的核心是用节点/边的多轮历史和 edge-aware GNN，在真实攻击标签监督下直接预测攻击概率；BlindGuard 的核心是用当前回复构造 self、neighbor、global 表示，对正常向量做 corruption，并通过对比学习建立正常行为边界，测试时以节点相对群体的语义偏离作为异常分。前者信息流建模更细但依赖已知攻击标签，后者摆脱真实攻击标签并显式使用全局上下文，但依赖“攻击会造成群体语义偏离”的假设。

### 2026-08-10｜随机 corruption 的泛化性、实时检测与训练/剪图时序

**Q：** corruption 噪声是随机的，泛化性好吗？BlindGuard 是实时检测吗？能否一边训练一边优化通信图？

#### 1. 随机噪声为什么可能帮助泛化？

BlindGuard 的 corruption 为：

\[
\widetilde{\mathbf x}_i
=\mathbf x_i
+\alpha\|\mathbf x_i\|_2
\frac{\boldsymbol\epsilon_i}
{\|\boldsymbol\epsilon_i\|_2},
\qquad
\boldsymbol\epsilon_i\sim\mathcal N(0,\mathbf I).
\]

这里的随机不是在原始文本中随便加乱码，而是在 SentenceBERT 的连续语义空间中，从正常点 \(\mathbf x_i\) 向随机方向移动。

如果训练过程中对许多正常节点、许多随机方向重复 corruption，模型看到的不是某一种固定伪攻击，而是在正常行为周围形成的一圈 synthetic negatives：

```text
                    × 伪异常
               ×              ×

        ×       正常行为区域       ×
               ● ● ● ●

               ×              ×
                    × 伪异常
```

这会鼓励模型学习：

> 不要记住“工具攻击包含某个关键词”，而要学习正常行为区域及其周围的 margin。

因此它对不同攻击类型可能比监督分类器更泛化，尤其当新攻击导致 response 明显偏离正常语义流形时。

#### 2. 随机噪声为什么又不能保证泛化？

随机方向只是一种代理异常，不等于真实攻击分布。它隐含假设：

```text
真实攻击 ≈ 从正常语义区域向外偏离
```

但真实攻击可能是 on-manifold：

- 始终围绕正确话题；
- 使用与正常 agent 相同的语言风格；
- 只偷偷修改一个数字、事实或结论；
- 恶意只存在于 tool-call 参数或 memory 写入中；
- 多个攻击者共同移动系统全局语义中心。

这些攻击在 SentenceBERT 空间中可能没有沿随机噪声模拟的方式明显远离正常区域，所以仍可能漏检。

此外，公式中的 \(\boldsymbol\epsilon/\|\boldsymbol\epsilon\|\) 从归一化高斯噪声获得方向，从数学上近似在高维单位球面上随机取方向。它的“semantic”主要来自 corruption 发生在语义嵌入空间，并按 \(\|\mathbf x_i\|\) 缩放；方向本身并不是由真实攻击语义指导的。因此将其称为完全 realistic 或 semantics-aware 需要克制。

论文的实验证据支持“有一定泛化”，而不是理论保证：

- PI 监督训练、MA 未见攻击测试时，BlindGuard 优于 G-Safeguard；
- 在多种 LLM 与拓扑上保持较稳定结果；
- \(\alpha\) 在 0.3–0.8 范围表现较稳定；
- failure analysis 也承认 on-topic mimicry 会造成 false negative，正常推理风格差异会造成 false positive。

准确结论：

> 随机 corruption 通过覆盖正常区域周围的多个方向，降低对具体攻击签名的过拟合，所以可能提升跨攻击泛化；但它只擅长模拟 off-manifold 语义偏离，不能保证识别语义自然、工具参数级或协同操纵型攻击。

#### 3. BlindGuard 是否实时检测？

它是 runtime、round-level online detection，但不是 token-level real-time prevention。

实际时序：

```text
第 t 轮 agent 已经生成 responses
            ↓
SentenceBERT 编码当前回复
            ↓
hierarchical encoder 生成 z_i
            ↓
计算 anomaly scores
            ↓
Top-K/阈值选出可疑节点
            ↓
剪边
            ↓
第 t+1 轮只使用保留的消息
```

因此它可以在每轮对话之间及时阻止下一轮传播，但必须先观察到一轮完整回复。它不是：

- 在每个 token 生成时持续检测；
- 在 agent 采取工具动作前必然拦截；
- 在攻击进入系统前进行预防；
- 对已经发生的删除文件、数据外传或 memory 写入执行回滚。

最准确的叫法是：

> per-round runtime containment，按轮次运行时遏制。

#### 4. 是否边训练边优化图？

论文默认不是。必须区分 offline training 与 online deployment。

##### 离线训练阶段

```text
正常 MAS 图
→ response embeddings
→ 随机 corruption 生成伪异常
→ 对比损失
→ 更新 encoder 参数 θ
→ 保存训练好的检测器
```

训练阶段优化的是 \(g_\theta\) 的模型参数，使表示空间更适合异常检测。这里不会为了保护一个正在运行的真实 MAS 而实时剪它的边。

##### 在线部署阶段

```text
加载并冻结训练好的 θ
→ 当前 MAS 生成一轮回复
→ 检测异常节点
→ 按规则剪边
→ 下一轮继续运行
```

部署时通常不计算对比损失、不反向传播，也不继续更新 \(\theta\)。剪边也不是通过梯度“学习出最佳邻接矩阵”，而是检测后执行的规则性拓扑干预：高风险节点被选中，就移除相关边。

所以：

```text
不是：边训练检测器，边修改线上图

而是：先离线训练检测器，
      再在线边运行、边检测、边剪图
```

#### 5. 为什么论文不默认在线继续训练？

如果把运行时新数据直接作为正常样本继续训练，会出现安全风险：

```text
攻击者产生恶意回复
→ 系统误以为是新正常数据
→ 在线更新检测器
→ 检测边界逐渐向攻击者移动
→ model poisoning / concept drift hijacking
```

若未来要设计在线自适应版，至少需要：

- 独立验证哪些新数据可信；
- replay buffer 保存历史干净基线；
- 慢速、受约束的参数更新；
- drift detector 区分正常变化与攻击；
- 可回滚 checkpoint；
- 更新前后安全验证。

#### 6. “优化图”也有两种含义

##### 论文实际做的拓扑修复

```text
异常分 → Top-K/阈值 → 剪边
```

这是 rule-based graph intervention，更准确叫 pruning/remediation。

##### 真正的可学习图优化

```text
联合学习节点风险、边信任权重和新拓扑
→ 用安全性 + 任务效用的联合目标更新图
```

BlindGuard 没有完成这一层。它没有学习连续边权、最优替代路径或剪边后的连接恢复。

#### 最终总结

> BlindGuard 的随机噪声是在语义嵌入空间围绕正常样本制造多方向伪异常，能够减少对具体攻击模板的过拟合，因此对造成明显语义偏离的未知攻击具有一定泛化，但不是对真实攻击的完整模拟。它是在每轮回复结束后、下一轮传播前执行的 runtime 检测，而不是 token 级或动作前预防。论文也不是边训练边修图：检测器先在干净数据上离线训练，部署时冻结参数，再按轮检测并规则性剪边；它实现的是在线检测与拓扑干预，不是在线学习或联合图优化。

### 2026-08-10｜第四章实验完整通俗解读：BlindGuard 到底有没有 G-Safeguard 好？

**Q：** 通俗解释第四章的实验设置、主结果、泛化、规模与消融，并判断 BlindGuard 是否优于 G-Safeguard。

#### 0. 最终答案先行

> 在攻击类型已知、能够为 G-Safeguard 提供真实攻击标签并分别训练的主实验里，BlindGuard 没有 G-Safeguard 好，G-Safeguard 是明显更强的监督上界；BlindGuard 的成绩是“最强或接近最强的无监督方法，用更少训练信息接近监督方法”。当测试攻击是 G-Safeguard 训练时没见过的新类型时，BlindGuard 才显示出核心优势，并在论文的 PI→MA 未见攻击实验中超过 G-Safeguard。

因此谁更好取决于问题：

```text
已知攻击 + 有足够攻击标签 + 追求最高检测性能
→ G-Safeguard 更好

没有攻击标签 / 攻击类型未来会变化
→ BlindGuard 更实用，未知攻击泛化更好
```

---

#### 1. 第四章想回答哪四个问题？

- RQ1：BlindGuard 面对不同攻击时，是否优于其他防御？
- RQ2：换 LLM、换拓扑、遇到未见攻击后是否仍有效？
- RQ3：agent 数量增加到 20/50 后是否仍有效？
- RQ4：neighbor-level 与 global-level 组件是否真的有用？

---

#### 2. 实验设置

##### 攻击与任务

| 攻击类型 | 数据集/任务 | 直观含义 |
|---|---|---|
| PI | CSQA、MMLU、GSM8K | 修改提示，使 agent 输出错误答案 |
| TA | InjecAgent | 工具返回或插件中隐藏恶意指令 |
| MA | PoisonRAG、CSQA | 污染 memory/检索知识，诱导错误回复 |

##### 拓扑

chain、tree、star、random，用来测试不同消息传播路线。

##### 主表 backbone

GPT-4o-mini。RQ2 再增加 DeepSeek-V3 与 Qwen3-30B-A3B。

##### 攻击者数量与防御预算

每个主实验恰好有 3 个 compromised agents，所有防御选异常分最高的 Top-3 进行隔离。

这保证比较方便，但也是较强先验：现实中通常不知道真实攻击者数量。

##### 比较方法

- No Defense：不防御；
- G-Safeguard：使用真实攻击标签监督训练，作者称为 upper bound；
- DOMINANT：重构式无监督 GAD；
- PREM：ego-neighbor 对比式 GAD；
- TAM：局部 affinity/homophily 异常检测；
- BlindGuard：corruption + self/neighbor/global + 对比学习。

---

#### 3. 两个指标怎样读？

##### AUC：检测器会不会把攻击者排在前面

```text
AUC = 100%：完美区分正常与恶意
AUC = 50%：接近随机猜
AUC 越高越好
```

AUC 衡量检测排序质量，基本不依赖具体 Top-K 阈值。

##### ASR@3：经过三轮后攻击传播得多严重

```text
ASR@3 越低越好
```

它是系统级后果，受到以下因素共同影响：

- 检测器是否找对攻击者；
- Top-3 是否包含关键传播节点；
- 剪边是否及时；
- 拓扑是否容易传播；
- backbone 是否容易被恶意消息影响。

因此高 AUC 通常有利于低 ASR，但两者不必完全同步。

---

#### 4. RQ1 主表：在已知攻击上谁更好？

主表共有：

\[
4\text{ 种拓扑}\times6\text{ 个任务}=24\text{ 个设置}.
\]

##### 检测 AUC

G-Safeguard 在 24/24 个设置中都高于 BlindGuard。

按主表 24 格做简单等权平均（这是辅助理解的重新汇总，不是论文原报 aggregate）：

```text
G-Safeguard 平均 AUC ≈ 98.59%
BlindGuard  平均 AUC ≈ 79.41%
```

这不是小差距。G-Safeguard 因为训练时看过该攻击类型的真实恶意节点，很多 AUC 接近 100%。

##### 最终 ASR@3

24 个设置中：

```text
G-Safeguard ASR 更低：21 个
BlindGuard  ASR 更低： 2 个
两者持平：             1 个
```

简单平均：

```text
No Defense  平均 ASR@3 ≈ 30.49%
BlindGuard  平均 ASR@3 ≈ 14.26%
G-Safeguard 平均 ASR@3 ≈  9.84%
```

因此：

- BlindGuard 相比无防御非常有效，平均 ASR 大约减半；
- 但 G-Safeguard 在已知攻击条件下防得更彻底。

##### BlindGuard 仅有的主表 ASR 优势

```text
Chain + MA(CSQA)：
G-Safeguard 7.67，BlindGuard 7.00

Random + PoisonRAG：
G-Safeguard 7.00，BlindGuard 6.67

Chain + PI(MMLU)：
两者都是 19.33
```

这些差距很小，不能推翻整体结论。

##### BlindGuard 与其他无监督 GAD 比呢？

它在大多数主表设置中获得最高无监督 AUC，明显比 DOMINANT、PREM 和 TAM 稳定。少数例外包括某些 TA 与 GSM8K 场景，PREM/DOMINANT 可能更好。

所以作者真正成立的 claim 是：

> BlindGuard 是整体最强的无监督方法，并在不使用真实攻击标签的情况下取得接近监督上界的防御结果。

“接近”主要适合描述最终 ASR/任务效用，若看 AUC，约 79 与 99 的差距仍明显。

---

#### 5. 分攻击类型观察

##### PI：BlindGuard 有效，但 G-Safeguard 通常更强

以 CSQA 为例：

```text
Chain：GS 19.33 < BG 23.67
Tree： GS 18.67 < BG 24.00
Star： GS 19.33 < BG 22.00
Random：GS 19.00 < BG 30.00
```

BlindGuard 都降低了无防御 ASR，但 random 下仍有较大残余传播。

##### TA：BlindGuard 能防，但短板明显

```text
Chain： GS 10.24 < BG 16.38
Tree：  GS  4.76 < BG 12.50
Star：  GS  6.87 < BG 12.59
Random：GS  5.14 < BG 17.69
```

BlindGuard 比无防御的 39–48% 好很多，但距离 G-Safeguard 较远。原因与前面分析一致：工具危险可能存在于 Observation、调用参数和外部动作中，而 BlindGuard 主要观察 response 句向量。

##### MA：BlindGuard 相对表现最好

它在 MA 上经常接近 G-Safeguard，并有两个主表设置的 ASR 略优。合理原因是 memory poisoning 经常会持续改变 agent 的语言和结论，使其相对正常群体产生更稳定的语义偏离，比较符合 BlindGuard 的检测假设。

---

#### 6. CSQA 每轮准确率图说明什么？

图中横轴为轮数，纵轴为 MAS 回答准确率。

在 star：

```text
No Defense：约 0.80 → 0.48
BlindGuard：约 0.78 → 0.73
G-Safeguard：约 0.79 → 0.80
```

在 tree：

```text
No Defense：约 0.80 → 0.63
BlindGuard：约 0.81 → 0.75
G-Safeguard：约 0.80 → 0.82
```

直观结论：

- 不防御时，对话轮数越多，污染传播越严重，准确率持续下降；
- BlindGuard 阻止了大部分下降，是最稳定的无监督曲线；
- G-Safeguard 仍然最高，几乎保持初始准确率。

这张图再次支持“BG 有效但没有超过 GS”。

---

#### 7. RQ2：换 LLM 和拓扑后是否泛化？

作者换用 DeepSeek-V3 与 Qwen3-30B-A3B，在 CSQA(PI) 和 PoisonRAG 上测试四种拓扑。

##### AUC 图

总体模式很稳定：

```text
G-Safeguard：约 0.94–1.00，最高
BlindGuard：约 0.70–0.89，通常为无监督最高
其他无监督方法：约 0.43–0.69
```

##### ASR 图

- BlindGuard 在几乎所有柱组都明显低于 No Defense；
- 在无监督方法中通常最好或接近最好；
- G-Safeguard 在绝大多数设置仍最低；
- 个别 PoisonRAG/拓扑上 BlindGuard 可略接近或略优于 G-Safeguard，但不是总体趋势。

所以“跨 backbone robust”的准确含义是：

> 换模型后 BlindGuard 仍然有效且维持无监督领先，不是换模型后全面超过 G-Safeguard。

而且该实验只在 CSQA(PI) 与 PoisonRAG 上测试，不包含所有六个任务，所以“universal”仍是有限证据。

---

#### 8. 真正让 BlindGuard 反超的实验：未见攻击

这是全篇最关键的比较。

实验设计：

```text
G-Safeguard：只用 PI 攻击监督训练
测试：突然换成没见过的 MA

BlindGuard：只学习正常 CSQA 行为
测试：同样面对 MA
```

结果：

| 拓扑 | GS ASR | BG ASR | GS AUC | BG AUC |
|---|---:|---:|---:|---:|
| Chain | 19.00 | **9.00** | 59.56 | **73.33** |
| Tree | 16.70 | **8.00** | 60.44 | **78.67** |
| Star | 10.67 | **7.33** | 64.00 | **75.56** |
| Random | 13.33 | 13.33 | 60.44 | **78.22** |

这里 BlindGuard：

- AUC 在 4/4 拓扑更高；
- ASR 在 3/4 更低；
- random 持平。

这说明：

```text
G-Safeguard 学到了“PI 攻击者长什么样”
→ 换成 MA，原分类边界失效

BlindGuard 学到了“正常 CSQA 协作长什么样”
→ MA 虽然没见过，只要偏离正常模式仍可检测
```

因此 BlindGuard 不是在普通主表击败 G-Safeguard，而是在“攻击类型发生变化”时击败它。

但这个实验仍是 PI→MA、同一 CSQA 任务的一次迁移，不能代表任意开放世界攻击。

---

#### 9. RQ3：20/50-agent 可扩展性

PoisonRAG 结果：

##### 20 agents

```text
No Defense：R1 15.89 → R2 23.22 → R3 29.51
BlindGuard：R1  3.51 → R2  4.54 → R3  5.57
```

##### 50 agents

```text
No Defense：R1 5.67 → R2 16.31 → R3 20.92
BlindGuard：R1 1.81 → R2  2.66 → R3  3.76
```

通俗结论：

- 图变大后代码仍可工作；
- 没有防御时污染逐轮增长；
- BlindGuard 把增长压得很低。

但这张表不能说明 BlindGuard 比 G-Safeguard 更 scalable，因为没有列出 G-Safeguard 或其他 baseline。

还要注意：所有测试默认恰好 3 个攻击者。如果 20/50 agents 仍固定 3 个，那么攻击比例从 15% 降到 6%，正常全局平均会更稳定，检测问题可能反而更容易。因此它证明“可以扩展并有效”，但没有完全证明固定攻击比例下的 scaling robustness。

---

#### 10. RQ4：消融实验说明什么？

图例：

- BlindGuard：完整模型；
- w/o NL：去掉 neighbor-level；
- w/o GL：去掉 global-level；
- w/o (NL & GL)：两者都去掉，只剩 self。

##### AUC 图（越高越好）

四种拓扑中，完整 BlindGuard 基本都最高。去掉 NL 或 GL 会下降，同时去掉二者下降最大；chain 和 star 尤其明显。

##### ASR 图（越低越好）

完整模型总体最低：

- random 约从完整 0.235，恶化到只剩 self 的约 0.28；
- chain 约从 0.25 恶化到约 0.31；
- star/tree 的差距较小，但完整模型仍总体占优。

直觉解释：

```text
NL：发现“这个 agent 与直接协作者不一致”

GL：发现“几个攻击者局部互相支持，
    但整个小团体偏离全局目标”
```

所以两者互补。

批判性看，这个 RQ4 只在 PoisonRAG 上重点消融 NL/GL，没有在主章节完整拆除 corruption、对比损失、不同 global summarization 等组件。因此它证明了分层上下文有用，但没有完全量化所有创新组件的贡献。

---

#### 11. 为什么 AUC 明显较差，ASR 有时却接近甚至略好？

因为 AUC 衡量所有节点的整体排序，而 ASR 只关心最终传播后果。

例如 random + PoisonRAG：

```text
G-Safeguard AUC 98.67，ASR 7.00
BlindGuard  AUC 82.67，ASR 6.67
```

可能出现：

- BlindGuard 的全体排序不如 GS；
- 但 Top-3 恰好剪中了最关键传播节点；
- random topology 下关键边被切断；
- 最终 ASR 略低。

因此不能只看某一个 ASR 数字就说检测器整体更强，应同时看 AUC、ASR 与 ACC。

---

#### 12. 对作者结论的准确评价

##### 得到充分支持

1. BlindGuard 明显优于传统无监督 GAD 的整体稳定性；
2. 不使用真实攻击标签也能显著降低 PI、TA、MA 的 ASR；
3. self/neighbor/global 组合确实有用；
4. 换拓扑、换 LLM、扩大 agent 数后仍有效；
5. 对未见 MA 的泛化优于只在 PI 上训练的 G-Safeguard。

##### 表述偏强或证据有限

1. 主表并没有超过 G-Safeguard；
2. “AUC 多数 >80%”不等于接近 G-Safeguard 的近 100%；
3. universal 只在有限攻击、任务和 backbone 中验证；
4. 主结果使用已知攻击者数量的 Top-3；
5. 规模实验没有与 GS 对比，且攻击比例可能下降；
6. 未见攻击只做 PI→MA，一次迁移不足以代表开放世界；
7. 公开实现按不同任务/攻击场景训练正常数据 checkpoint，不是一个 checkpoint 覆盖全部场景。

---

#### 13. 最终回答：到底有没有 G-Safeguard 好？

不能只回答“有”或“没有”，必须带条件：

| 使用场景 | 更好的方法 | 原因 |
|---|---|---|
| 已知攻击、有准确恶意标签 | G-Safeguard | 主表 AUC 24/24 更高，ASR 21/24 更低 |
| 追求最高同分布检测精度 | G-Safeguard | 真实攻击监督提供了强先验 |
| 没有任何攻击标签 | BlindGuard | G-Safeguard 无法按原范式训练 |
| 攻击类型不断变化/真正未见 | BlindGuard 更有优势 | 学正常边界，不绑定某个攻击签名 |
| 工具攻击 | 当前实验中 G-Safeguard 明显更好 | BlindGuard 的 response 句向量遗漏工具层细节 |
| 完整 self-healing | 两者都不够 | 都主要停在 detect + isolate |

最准确的一句话：

> BlindGuard 不是一个在绝对性能上全面击败 G-Safeguard 的方法，而是用“牺牲一部分已知攻击检测精度”换取“不需要真实攻击标签和更好的未知攻击泛化”。G-Safeguard 是信息充分时的性能上界，BlindGuard 是信息不足、攻击不断变化时更实际的方案。

### 2026-08-10｜MA 是什么？

在 BlindGuard/G-Safeguard 的实验表中，\(\mathrm{MA}\) 表示 **Memory Attack（记忆攻击/记忆投毒）**，不是 multi-agent。\(\mathrm{MAS}\) 才表示 **Multi-Agent System（多智能体系统）**。

其基本攻击链是：

```text
攻击者向 agent memory / 外部知识库写入错误或恶意内容
→ agent 以后执行任务时检索到被污染的记忆
→ 将其当作可信历史或知识生成错误回复
→ 回复再经 agent-to-agent communication 传播
→ 其他正常 agent 也被误导
```

例子：

```text
正常 memory：项目截止日期是8月20日。
投毒 memory：项目截止日期已改为9月20日，无需再次确认。
```

以后 agent 被问到截止日期时，即使用户当前 prompt 完全正常，也可能从 memory 中检索出“9月20日”，再把错误日期告诉其他 agent。

与另外两种攻击的区别：

| 缩写 | 攻击面 | 恶意内容从哪里进入 |
|---|---|---|
| PI | Prompt Injection | 当前 system/user prompt |
| TA | Tool Attack | 工具、插件或 Observation |
| MA | Memory Attack | 长期记忆、历史记录、RAG/知识库 |

MA 往往比一次性 PI 更持久，因为污染内容被存储后可能跨轮次、跨任务反复被检索。BlindGuard 通常不直接检查 memory 内部内容，而是从 agent 最终 response 是否偏离 self/neighbor/global 正常语义模式来间接发现 MA；因此如果投毒后的回复持续偏离群体，较容易检测，但若错误记忆生成的回答非常自然且与群体一致，仍可能漏检。

### 2026-08-10｜实验与训练超参数：为何这样设计，能否直接复用到自愈系统？

**Q：** BlindGuard 的实验/模型超参数如何设置？为什么这么设计？以后构建 self-healing MAS 能否直接使用相同设置？

#### 1. 先区分三类“参数”

很多设置都被口头称为超参数，但实际含义不同：

1. **优化超参数：**学习率、weight decay、epoch、batch size、hidden dimension；
2. **检测/方法超参数：**corruption 强度 \(\alpha\)、temperature \(\tau\)、corruption 节点比例、Top-K/阈值；
3. **实验/威胁模型设置：**攻击者数量、agent 数、通信轮数、拓扑、backbone 和测试样本数。

对新系统的可迁移性不同：优化超参数可作初始化参考；检测参数必须重新校准；威胁模型设置更不能照搬。

---

#### 2. 论文报告的核心训练超参数

| 设置 | 论文值 | 作用与设计理由 |
|---|---:|---|
| Optimizer | Adam | 对小型神经网络和带噪梯度训练稳定，减少繁琐手工调步长 |
| Initial LR | 0.001 | 图学习/MLP 常见起点，收敛速度与稳定性的折中 |
| Weight decay | \(\{5\times10^{-5},10^{-4},2\times10^{-4}\}\) | L2 正则化，避免只在有限 clean graph 上记忆训练样本 |
| LR scheduler | cosine annealing | 前期较快学习，后期降低学习率细调表示空间 |
| \(T_{\max}\) | 10 | 余弦学习率变化的调度周期 |
| \(\eta_{\min}\) | \(10^{-5}\) | 学习率最低值，避免后期完全停止更新 |
| Hidden dimension | 论文写 512 | 表示容量与计算/存储开销的折中 |
| SentenceBERT | frozen | 保留预训练语义几何、降低训练成本，避免小数据破坏文本编码器 |
| Hardware | 4×NVIDIA L40 | 实验训练资源，不是算法必须配置 |

公开实现与论文描述不完全相同：PI 代码常见默认 hidden dimension 1024、latent dimension 512、dropout 0.2、2 layers、8 heads；官方运行命令又按数据集使用不同 epochs 和 batch size，例如 CSQA 20 epochs、MMLU/GSM8K 100、MA 10、TA 50，BlindGuard 命令常用 batch size 1。这说明“512/某个 epoch”不是理论固定值，而是任务特定实现选择。复现实验时必须以对应 checkpoint、commit 和命令为准，而不能只读正文的一行超参数。

---

#### 3. corruption 强度 \(\alpha=0.8\)

\[
\widetilde{\mathbf x}_i
=\mathbf x_i+
\alpha\|\mathbf x_i\|_2
\frac{\boldsymbol\epsilon_i}{\|\boldsymbol\epsilon_i\|_2}.
\]

\(\alpha\) 控制伪异常离正常向量多远：

```text
α 太小：伪异常几乎还在正常区域，训练分离信号太弱

α 适中：在正常区域周围形成可学习 margin

α 太大：伪异常被推到极远、很不真实的位置，任务变得过于简单，
        模型学不到细微异常
```

作者在 random topology 上对两个任务测试：

| \(\alpha\) | 0.03 | 0.3 | 0.5 | 0.8 | 10 |
|---|---:|---:|---:|---:|---:|
| PI-CSQA AUC | 52.4 | 72.9 | 73.8 | **75.1** | 62.7 |
| MA-PoisonRAG AUC | 61.3 | 75.6 | 80.0 | **82.7** | 68.9 |

所以固定 \(\alpha=0.8\) 是经验选择：在这两个数据集与该表示模型上最好，同时 0.3–0.8 的 practical 区间相对稳定。

但这不能证明 0.8 对新领域仍最好，因为 \(\alpha\) 的实际含义依赖：

- SentenceBERT 的表示几何和维度；
- 文本领域与语言；
- 是否加入 tool/memory/temporal features；
- 正常行为本身有多 heterogeneous；
- 希望检测的攻击有多 subtle。

---

#### 4. corruption 数量：训练时 3/8 节点

公开 PI 实现会构造类似：

```text
[1,1,1,0,0,0,0,0]
```

再随机打乱，即每张 8-node graph 中恰好将 3 个节点 corruption。测试 threat model 同样恰好有 3 个真实攻击者，修复又选择 Top-3。

这形成高度配套的实验：

```text
训练伪异常数 = 3
测试真实攻击者数 = 3
修复预算 K       = 3
```

好处：控制变量清楚，各方法公平，检测器不会通过“把所有人都判异常”获得低 ASR。

局限：现实攻击者数量未知；模型可能适应 3/8 的异常比例；Top-3 可能漏掉第 4 个攻击者，也会在零攻击时强制误剪三个正常节点。

---

#### 5. 为什么主实验用 Top-K=3？

不同异常检测器的分数尺度不一致：

```text
方法 A 正常分数范围：0.0–1.0
方法 B 正常分数范围：-0.8–-0.2
方法 C 所有分数都偏高
```

若统一用 0.5 阈值，会对某些方法天然有利。固定 Top-3 保证每个方法拥有相同隔离预算，比较的是“谁把真正攻击者排得更靠前”。

这是良好的 benchmark 设计，却不是现实部署的最佳策略。实际系统不知道攻击者数量，更应使用按 clean validation 校准的阈值、置信区间或风险分级动作。

---

#### 6. 为什么用三轮通信？

ASR@1、ASR@2、ASR@3 用于观察传播：

```text
R1：攻击刚进入通信图
R2：邻居开始受影响
R3：级联传播更加明显
```

三轮是实验成本和可观察传播之间的折中，也沿用了 G-Safeguard 设置，便于直接比较。它不是安全系统的理论最优 horizon。长任务、软件开发或持续运维 MAS 可能需要几十轮甚至无限期监控。

---

#### 7. 为什么用四种拓扑与多种 LLM？

##### 四种拓扑

- chain：顺序传播；
- tree：层级分支传播；
- star：中心节点是传播枢纽；
- random：不规则多路径。

目的是防止模型只适应一种邻接矩阵。

##### 多 backbone

主实验 GPT-4o-mini，额外 DeepSeek-V3、Qwen3-30B-A3B。目的是检查 detector 是否只学习某个 LLM 的语言风格。

但对自愈系统，应测试真实将部署的模型组合，包括 heterogeneous MAS，而不应认为这三种 backbone 已覆盖目标环境。

---

#### 8. 哪些 BlindGuard 设置可以作为自愈系统起点？

可以复用为 baseline/start point：

1. frozen SentenceBERT + small encoder，先建立低成本观测基线；
2. Adam + lr \(10^{-3}\)，作为第一组优化参数；
3. weight decay \(10^{-5}\)–\(10^{-4}\) 量级；
4. cosine scheduler；
5. \(\alpha\) 从 0.3、0.5、0.8 开始做敏感性实验；
6. train only on clean data + unseen attack test 的实验协议；
7. chain/tree/star/random 和多 backbone 的鲁棒性矩阵；
8. 同时报告 AUC、ASR、clean utility 与 latency。

这些是合理的工程起点，但不能直接宣称为 self-healing 系统的最佳设置。

---

#### 9. 自愈系统中必须重新设计的参数

##### K / detection threshold

不能固定 Top-3。应根据 clean validation data 控制 false positive rate，例如选择使正常场景误隔离率低于 1% 或 5% 的阈值；也可按风险分级：

```text
低风险：降低消息权重
中风险：限流/沙箱
高风险：隔离并触发恢复
```

##### corruption rate

不要始终 corruption 3/8。应测试不同异常比例，例如 10%、25%、40%、50%，防止模型记住固定攻击者数量。

##### corruption mechanism

如果 self-healing system 同时观察文本、tool、memory 和时间状态，不能给所有模态简单加同一种高斯噪声：

```text
文本表示：角度/语义扰动
tool call：参数替换、权限越界、调用序列扰动
memory：插入、删除、版本冲突、provenance 破坏
拓扑：边增加、删除、串通子图
时间序列：慢速 drift、burst attack
```

##### representation dimension

应根据数据量、延迟和 agent 数重新选择，例如 128/256/512，而不是默认越大越好。

##### communication horizon

自愈不只看 R1–R3，还要评估 detection delay、recovery time、恢复后持续安全时间和是否能安全 rejoin。

##### online update

不能把线上新回复直接当 clean data 继续训练，否则攻击者可能污染检测边界。在线适应需要 trusted validation、replay buffer、受限更新、checkpoint rollback 和独立验证。

---

#### 10. 推荐的自愈系统初始搜索空间

这是一套起步网格，不是最终答案：

| 参数 | 建议起始候选 |
|---|---|
| learning rate | \(10^{-4},3\times10^{-4},10^{-3}\) |
| weight decay | \(10^{-5},10^{-4},2\times10^{-4},10^{-3}\) |
| latent dimension | 128、256、512 |
| \(\alpha\) | 0.2、0.4、0.6、0.8、1.0 |
| corruption fraction | 10%、25%、40%、50% |
| clean target FPR | 0.5%、1%、5% |
| random seeds | 至少 3，最好 5 |
| rounds/horizon | 3、5、10，以及持续运行设置 |

选择参数不能只优化攻击 AUC，而应联合考虑：

\[
\text{safety gain}
-\lambda_1\text{clean utility loss}
-\lambda_2\text{recovery cost}
-\lambda_3\text{latency}
-\lambda_4\text{false intervention}.
\]

这里的 \(\lambda\) 表示你对不同代价的权重。直觉上，自愈系统不是“检测越激进越好”，而是要在安全、正常任务、恢复成本和速度之间取得可解释折中。

---

#### 11. 推荐的调参/评测流程

1. 先定义 threat model：攻击面、攻击比例、攻击者知识和可执行动作；
2. 将 clean data 按任务/时间拆成 train、validation、test，防止泄漏；
3. 在 clean train 上训练正常行为表示；
4. 用 clean validation 校准阈值和目标 FPR；
5. 在不看最终未知攻击测试集的情况下选择 \(\alpha\)、dimension、lr；
6. 锁定所有参数后测试已知、未见、串通和 adaptive attacks；
7. 对攻击比例、拓扑、LLM、轮数与系统规模做 sensitivity analysis；
8. 至少 3–5 个随机种子，报告 mean±std；
9. 对 self-healing 额外报告检测延迟、隔离正确率、恢复成功率、恢复时间、rollback 成本、验证通过率和 rejoin 后复发率。

#### 最终结论

> BlindGuard 的 \(\alpha=0.8\)、Adam/0.001、weight decay、512 维和 Top-3 等设置，是针对其数据、8-node/3-attacker threat model 与计算预算做出的经验选择。你以后可以把优化器、学习率量级、corruption 范围和多拓扑评测作为 baseline，但不能直接照搬 Top-3、3/8 corruption、三轮 horizon 或 \(alpha=0.8\)。对 self-healing MAS，超参数本身必须服从攻击比例、误报代价、恢复动作、工具/memory 状态与长期运行需求，采用 clean-data calibration、敏感性分析和多目标安全—效用评估。简言之：架构思想可以复用，数值参数必须具体问题具体分析。

---

## 2026-08-10｜BlindGuard 为什么使用 MLP？它到底负责什么？

### 问题

论文在层级编码器中写道：

\[
z_i=g_\theta(h_i^s\parallel h_i^n\parallel h_i^g),
\]

并称 \(g_\theta\) 为 MLP，但几乎没有解释 MLP 的结构、为什么需要它，以及它和 SentenceBERT、GNN、攻击分类器之间有什么区别。

### 1. 先说结论

BlindGuard 中的 MLP 不是文本编码器，也不是直接输出“攻击/正常”概率的分类器。它是**三种上下文表示的可学习融合器**：

```text
智能体回复 Ri
   ↓ frozen SentenceBERT
节点特征 xi
   ↓ 分别提取
self hi^s + neighbor hi^n + global hi^g
   ↓ concatenate
长向量 ui
   ↓ MLP / projection
统一表示 zi
   ↓ contrastive learning + similarity scoring
异常分数 si
```

一句话理解：

> 前三个表示负责收集证据，MLP 负责学习怎样组合这些证据；最终相似度评分才负责判断谁像异常点。

### 2. 公式逐符号解释

定义拼接后的输入：

\[
u_i=h_i^s\parallel h_i^n\parallel h_i^g.
\]

- \(h_i^s\)：智能体 \(i\) 自己回复的表示；
- \(h_i^n\)：其邻居回复的聚合表示；
- \(h_i^g\)：整个 MAS 的平均表示；
- \(\parallel\)：concatenate，只是把三个向量首尾相接；
- \(u_i\)：三种信息拼起来的长向量；
- \(g_\theta\)：带可学习参数 \(\theta\) 的 MLP；
- \(z_i\)：融合后的智能体表示，用于后续对比学习和异常评分。

如果每个 \(h\) 都是 \(D\) 维，那么：

\[
h_i^s,h_i^n,h_i^g\in\mathbb R^D,
\qquad
u_i\in\mathbb R^{3D}.
\]

例如 SentenceBERT 输出 384 维时，三个向量拼接后是 \(3\times384=1152\) 维。融合器可以再把 1152 维投影为较紧凑的潜在表示，例如 512 维：

\[
z_i\in\mathbb R^{512}.
\]

所以 MLP 确实具有“改变/压缩维度”的作用，但它的核心不只是压缩，而是**学习哪些维度和哪些上下文关系值得保留**。

### 3. MLP 到底是什么？

一个典型的两层 MLP 可以写成：

\[
a_i=\operatorname{ReLU}(W_1u_i+b_1),
\]

\[
z_i=W_2a_i+b_2.
\]

- \(W_1,W_2\)：可训练的权重矩阵，学习怎样重新组合输入；
- \(b_1,b_2\)：偏置；
- ReLU：非线性激活函数；
- \(a_i\)：中间隐藏表示；
- \(z_i\)：最终融合表示。

MLP 可以直观理解为一个“可学习调音台”：它接收 self、neighbor、global 三路信号，学习每路信号的权重，以及它们组合后代表什么模式。

### 4. 为什么不能拼接后直接使用？

拼接只完成“把信息放在一起”，并没有真正比较或融合：

\[
[h_i^s;h_i^n;h_i^g]
\]

仍然只是三个向量并排放置。它不会自动知道：

- self 与 neighbor 的不一致是否重要；
- self 与 global 的偏离是否更危险；
- 邻居被共同污染时，应不应该更信任 global；
- 哪些 SentenceBERT 维度只是噪声；
- 三种视角应分别占多大权重。

线性层已经能够学习类似下面的比较：

\[
W_s h_i^s+W_n h_i^n+W_g h_i^g.
\]

如果某些权重呈相反方向，它就可以近似形成 \(h_i^s-h_i^g\) 或 \(h_i^s-h_i^n\)，即学习“局部与整体是否一致”。加入非线性后，还可以表达更复杂的条件关系。

### 5. 一个直观例子

假设一个数学任务的正确答案是 36：

```text
Agent i（self）：回答 27
其大多数邻居：回答 36
系统整体：回答 36
```

只看 Agent i 的回复，“27”未必能说明它是恶意的，也可能只是普通推理错误。但同时观察到：

```text
self 与 neighbor 不一致
self 与 global 也不一致
```

这种联合模式就更可疑。融合器要学习的正是这种多视角关系。

再考虑两个恶意智能体互相呼应，都回答 27：

```text
self 与 neighbor 一致
self 与 global 不一致
```

这时只看局部邻居可能误以为它正常，全局表示则提供纠偏证据。MLP 可以学习在不同组合模式下重新分配三种证据的作用。

注意，模型处理的是 SentenceBERT 语义向量，并不是直接计算数字 27 与 36 的差；上例只是帮助理解“多层上下文不一致”这一机制。

### 6. 为什么不直接把三个向量平均？

若计算：

\[
\frac{h_i^s+h_i^n+h_i^g}{3},
\]

就无法再区分哪部分来自自己、邻居或全局。异常的 self 表示还可能被两个正常平均表示冲淡。拼接保留三种来源的身份，MLP 再学习如何融合，比简单平均更有表达能力。

### 7. 为什么不用更复杂的 GNN？

BlindGuard 已通过归一化邻接矩阵显式构造了邻居表示，并通过全图平均构造了全局表示。图结构信息已经在进入 MLP 前被汇总，因此后面用小型 MLP 有几个现实理由：

1. 参数少、训练和运行成本低；
2. 不需要微调 SentenceBERT 或 backbone LLM；
3. 不需要再堆多层消息传播，减少过度平滑风险；
4. 每个节点都可用同一个融合器，适用于不同节点数和拓扑。

但代价是：它对图结构的建模比深层、边感知 GNN 更简单，主要依赖预先设计的 self/neighbor/global 聚合。

### 8. MLP 是攻击分类器吗？

不是。监督分类器通常直接输出：

\[
p(y_i=1\mid v_i),
\]

即节点为恶意的概率。BlindGuard 的融合器输出的是向量 \(z_i\)，没有直接说“攻击概率是多少”。随后对比学习把正常样本拉近、伪异常推远；推理时再根据 \(z_i\) 与其他节点表示的相似程度计算异常分数。

因此链条是：

```text
MLP：产生便于比较的表示
contrastive loss：塑造表示空间
similarity score：产生异常程度
Top-K/阈值：决定干预谁
```

### 9. 到底训练了谁？

- backbone LLM：不训练；
- SentenceBERT：冻结，不训练；
- 层级融合器中的线性层/MLP：训练；
- 对比学习投影层：训练。

训练信号不是人工攻击标签，而是正常样本与人工 corruption 样本构成的对比关系。因此它仍被称为无监督攻击检测：没有使用真实攻击类型和真实恶意节点标签。

### 10. 官方代码与论文描述的差别

正文把 \(g_\theta\) 概括为 MLP，但官方实现的完整三视角模式更具体地执行：

```text
x_nei   = normalized_adj × x
x_graph = mean(x)
u       = concat(x, x_nei, x_graph)
z       = Linear(3D, latent_dim)(u)
```

对比损失中又执行：

```text
projection = Linear(ReLU(z))
```

所以从代码层面更准确的描述是：

> 一个线性三视角融合层，加一个用于对比训练的 ReLU + 线性投影头。

如果把两部分整体看待，可以宽松地称为两层 MLP；但层级编码器本身不是正文可能让人联想到的复杂深层 MLP。推理异常分数使用的是融合后的 \(z\)，而对比投影头主要服务于训练损失。

### 11. 对论文的批判性评价

这是 BlindGuard 方法描述中的一个不足：正文没有清楚报告 MLP 的层数、宽度、激活函数、dropout、归一化，以及训练投影头与推理表示之间的关系。仅写一个 \(g_\theta\) 会让读者无法从论文正文准确复现。

理想实验还应比较：

```text
raw concatenation
simple average
single linear projection
two-layer MLP
GNN fusion
```

从而回答性能究竟来自层级上下文本身、可学习融合、非线性 MLP，还是对比学习目标。论文现有的表示消融能说明 self/neighbor/global 有价值，但不能充分证明某一种 MLP 结构是必要或最优的。

### 最终记忆句

> BlindGuard 的 MLP 不是负责“看文本”，也不是直接负责“判攻击”；它负责把智能体自身、邻居和全局三种证据融合成一个适合对比学习与异常比较的表示。拼接只是收集材料，MLP 才是学习怎样配材料。不过官方实现实际上相当简洁：线性融合层加对比投影头，论文对此说明不足。

---

## 2026-08-10｜BlindGuard 本质上训练的是一个什么东西？

### 最短答案

> BlindGuard 本质上训练的是一个“正常行为表示编码器”：它学习一套权重，把每个智能体的 self、neighbor、global 信息转换到一个新的向量空间，使正常智能体彼此接近，人工 corruption 出来的伪异常与正常智能体分开。

它不是在训练 backbone LLM，不是在重新训练 SentenceBERT，也不是在训练一个见过真实攻击标签的二分类器。

### 1. 从“程序里哪些数字被更新”来看

BlindGuard 中：

| 部分 | 是否训练 | 作用 |
|---|---:|---|
| backbone LLM | 否 | 产生 MAS 回复 |
| SentenceBERT | 否，冻结 | 把文本变成初始向量 \(x_i\) |
| 邻居加权聚合 | 否 | 根据图结构计算 \(h_i^n\) |
| 全局平均 | 否 | 计算 \(h_i^g\) |
| 融合层/MLP | 是 | 把三种上下文融合为 \(z_i\) |
| contrastive projection head | 是 | 帮助对比损失塑造表示空间 |
| corruption noise | 否 | 人工生成训练时的伪异常 |

真正被梯度下降反复修改的是融合层和投影头里的权重矩阵 \(W\) 与偏置 \(b\)。

### 2. 从“它学到了什么知识”来看

它学到的不是：

```text
出现 "ignore previous instructions" 就是攻击
调用某个工具就是攻击
某一种 memory 内容就是投毒
```

它主要学习的是：

```text
在正常 MAS 中，
一个智能体自己的语义、邻居语义和系统整体语义，
通常应该呈现怎样的一致性关系。
```

因此它学到的是一种**正常行为的几何结构/比较尺度**。

可以把原始 SentenceBERT 空间想成一间杂乱仓库。训练后的编码器相当于学会了一种整理规则：

```text
正常且关系相似的智能体 → 摆得比较近
corruption 产生的异常模式 → 摆得比较远
```

推理时，新智能体如果被映射到远离大多数节点的位置，就获得较高异常分数。

### 3. 一轮训练到底发生什么？

```text
正常 MAS 图
   ├─ 原始正常节点表示
   └─ 给部分节点加入定向噪声，制造伪异常
                 ↓
       使用同一个融合编码器
                 ↓
      得到正常与伪异常的向量
                 ↓
            对比损失
                 ↓
 修改融合层/投影头的 W 和 b
```

对比损失会向模型表达：

```text
这些正常表示应该更相似；
这些被 corruption 的表示应该与正常表示更不相似。
```

经过许多轮更新，网络逐渐找到一种适合区分“正常一致模式”和“偏离模式”的映射方式。

### 4. 用一个简化公式表示

训练目标可以概括为：

\[
\theta^*=\arg\min_\theta
\mathcal L_{contrastive}.
\]

- \(\theta\)：融合层和投影头中所有可训练的 \(W,b\)；
- \(\mathcal L_{contrastive}\)：对比损失，衡量当前表示空间排得好不好；
- \(\arg\min\)：不是求最小损失的数值，而是寻找“让损失最小的那组参数”；
- \(\theta^*\)：训练结束后保存下来的最好权重。

所以训练产物就是一个 checkpoint，里面主要保存学好的参数 \(\theta^*\)。这些参数定义了从层级上下文到异常检测表示的映射规则。

### 5. 它为什么能检测没见过的攻击？

因为它没有试图记忆每种攻击长什么样，而是学习正常交互通常长什么样。未知攻击只要破坏了这种正常的 self—neighbor—global 关系，就可能在表示空间中成为离群点。

但这里必须加限制：

> BlindGuard 学到的不是完整的“正常世界真理”，而是训练数据、拓扑、任务、SentenceBERT 表示与 corruption 机制共同塑造出的正常性近似。

如果未知攻击在语义和上下文关系上都很像正常行为，或者大多数节点同时被攻陷并形成新的多数模式，它仍可能检测失败。

### 6. 与 G-Safeguard 的本质区别

```text
G-Safeguard：学习“哪些特征对应攻击标签”
BlindGuard：学习“正常节点在表示空间中应该怎样排列”
```

G-Safeguard 的最终产物偏向一个监督攻击分类器；BlindGuard 的最终产物偏向一个正常行为表示编码器和相似度度量空间。

### 最终记忆句

> BlindGuard 真正训练的是 MLP/投影层中的权重，也就是一把“正常性尺子”。SentenceBERT 提供原材料，图聚合收集 self、neighbor、global 三种证据，对比学习负责教这把尺子怎样衡量；上线以后，再用这把尺子找出与群体正常模式不相似的智能体。

---

## 2026-08-10｜说白了是不是就在训练 MLP？官方 network 架构精确展开

### 直接结论

是。对 BlindGuard/SCL 的实际有效路径来说，**训练的就是一个很小的 MLP，更准确地说是一个线性融合层加一个对比学习投影层**。

论文容易让人误以为它训练了一个复杂 GNN，但根据官方代码，训练和推理调用的是 `GATSCL.encode()`；这条路径手工计算邻居与全局聚合，然后进入全连接层，并没有调用类中定义的 GAT。

### 1. 完整训练架构

以完整的 self + neighbor + global 模式（`rep_type=0`）为例：

```text
每个节点的文本回复
        ↓
冻结的 all-MiniLM-L6-v2
        ↓
x：384维
        ↓ 加定向噪声（仅训练时，噪声本身不训练）
 ┌──────┼────────────────┐
 │      │                │
self  neighbor          global
x     Âx               mean(x)
384    384                384
 └──────┼────────────────┘
        ↓ concatenate
u：[x || x_neighbor || x_global]
        1152维
        ↓
fc = Linear(1152, 512)
        ↓
z：512维
        ↓
ReLU
        ↓
fc1 = Linear(512, 512)
        ↓
L2 normalize
        ↓
两两 cosine similarity / temperature 0.3
        ↓
contrastive loss
        ↓ backpropagation
更新 fc 和 fc1 的 W、b
```

用公式表示：

\[
u_i=x_i\parallel(\hat A X)_i\parallel\operatorname{mean}(X)
\in\mathbb R^{1152},
\]

\[
z_i=W_0u_i+b_0\in\mathbb R^{512},
\]

\[
q_i=W_1\operatorname{ReLU}(z_i)+b_1
\in\mathbb R^{512},
\]

\[
\bar q_i=\frac{q_i}{\lVert q_i\rVert_2}.
\]

训练损失根据不同节点的 \(\bar q_i\) 之间的相似度计算，再通过反向传播同时更新 \(W_0,b_0,W_1,b_1\)。

### 2. 它是不是 MLP？

严格区分如下：

- `Linear(1152→512)` 单独看只是一个线性层，不是典型的多层 MLP；
- 把 `fc → ReLU → fc1` 整体看，就是一个两层 MLP；
- 第二层 `fc1` 是 contrastive projection head；
- 推理异常评分使用 `fc` 输出的 \(z\)，不再经过 `ReLU + fc1`；
- 但训练时损失经过 `fc1` 后仍会反向传播到 `fc`，因此两个层都会被训练。

因此最准确的表述是：

> 训练阶段使用两层 MLP 形式的 encoder + projection head；部署评分主要保留第一层输出作为节点表示。

### 3. 到底有哪些可训练参数？

完整模式下：

#### 第一层 `fc`

\[
W_0\in\mathbb R^{512\times1152},
\qquad b_0\in\mathbb R^{512}.
\]

参数量：

\[
1152\times512+512=590,336.
\]

#### 第二层 `fc1`

\[
W_1\in\mathbb R^{512\times512},
\qquad b_1\in\mathbb R^{512}.
\]

参数量：

\[
512\times512+512=262,656.
\]

#### 实际有效训练参数总数

\[
590,336+262,656=852,992,
\]

即大约 85.3 万个参数，远小于 LLM。

### 4. 图在哪里？为什么它仍被叫作 graph 方法？

图没有作为神经网络层被训练，而是在 MLP 前参与特征构造：

\[
x_i^n=(\hat A X)_i.
\]

邻接矩阵 \(\hat A\) 决定节点 \(i\) 聚合哪些邻居。因此：

```text
图结构：决定信息从哪里取
MLP：决定取来的三种信息怎样融合
对比损失：决定融合空间应该怎样排列
```

所以它是 graph-aware 的方法，但官方 BlindGuard 主路径并不是“多层 GNN 消息传播后分类”。

### 5. 代码里不是还有 GAT 吗？

`GATSCL` 类确实定义了：

```python
self.gat = GATConv(...)
```

但 BlindGuard 训练代码调用：

```python
node_emb = model.encode(x, edge_index)
loss = model.neg_all(node_emb, anamaly_idx)
```

评估代码也调用 `encode()`。而 `encode()` 内部只执行：

```text
邻接矩阵聚合
全局平均
concatenate
self.fc
```

它没有调用 `self.gat`。虽然优化器接收了整个 `model.parameters()`，但一个参数只有参与当前前向计算、得到梯度，才会真正更新。未进入计算图的 GAT 参数不会因为被放进 optimizer 就自动训练。

官方 `forward()` 虽然调用 GAT，但当前 BlindGuard/SCL 训练路径没有调用这个 `forward()`；而且该 `forward()` 还引用了已被注释掉的 `self.fc2`。这进一步说明公开实现中真正工作的主路径是 `encode()`，不是 GAT forward 路径。

### 6. 哪些超参数真正影响这条 MLP 路径？

- `latent_dim=512`：直接决定 `fc` 和 `fc1` 的输出宽度，确实生效；
- `rep_type`：决定输入是三视角、两视角还是仅 self，确实生效；
- learning rate、weight decay、epochs：影响 MLP 训练，确实生效；
- `hidden_dim=1024`、`num_heads=8`：主要用于代码中未被调用的 GAT，对当前 `encode()` 路径不起实质作用；
- `num_layers=2`：没有被传入或用于构造 BlindGuard 的有效 MLP 路径；
- 训练脚本中的 `dropout`：构造 `GATSCL` 时没有传入，使用默认值 0。

这说明论文/代码的参数命名带有复用其他 GNN baseline 代码的痕迹，不能仅看 checkpoint 文件名就认为 BlindGuard 真使用了 2 层 GNN、8 个 attention heads 和 1024 hidden dimension。

### 7. 推理时的 network

推理时没有 corruption，也不需要投影头：

```text
384维节点表示
   ↓ self / neighbor / global
1152维拼接
   ↓ Linear(1152→512)
512维 z
   ↓ L2 normalize + 节点两两相似度
异常分数
   ↓ Top-K
隔离可疑节点
```

### 最终结论

> 对，BlindGuard 本质上就是利用正常数据和人工 corruption，通过对比损失训练一个小型 MLP。图结构主要用于在 MLP 前构造 neighbor 特征。官方有效训练路径是 `Linear(1152→512) → ReLU → Linear(512→512)`；推理时使用第一层得到的 512 维表示做相似度异常检测。代码虽然定义了 GAT，但当前训练/推理主路径没有使用它。
