# Trustworthy-ML foundations

Transferable classics for robustness, uncertainty, verification, privacy, fairness, and Byzantine fault tolerance. They are not MAS-primary evidence. They supply language for detectors, thresholds, and recovery.

## Madry AT

**Towards Deep Learning Models Resistant to Adversarial Attacks.** ICLR 2018. [arXiv](https://arxiv.org/abs/1706.06083)

- **Problem:** Patching named attacks does not define robustness. The attacker needs an allowed set, and the model should resist the worst perturbation in that set.
- **Method:** Saddle-point training: inner max over an Lp ball via multi-step PGD, outer min over parameters. Capacity is shown to matter for robust boundaries.
- **Result:** MNIST remains above 89% under the paper's strongest test attacks; CIFAR-10 is about 46% under strong white-box iteration, higher under black-box transfer. PGD training beats natural and FGSM training.
- **Takeaway:** Write the threat model as an allowed attack set (k agents, which edges, how many messages), then optimize worst-case loss. Semantic LLM attacks are not Lp balls; a wrong set S makes the guarantee meaningless.

## Group DRO

**Distributionally Robust Neural Networks for Group Shifts.** ICLR 2020. [arXiv](https://arxiv.org/abs/1911.08731)

- **Problem:** High average accuracy can hide collapse on a small, dangerous group.
- **Method:** Minimize the worst-group loss. Groups are known at training (for example label times spurious attribute). Strong L2, early stopping, or group-size correction is required or overparameterized nets fit every training group to zero and DRO stops discriminating.
- **Result:** Worst-group test accuracy rises 10-40 points. Waterbirds worst-group moves from 21.3% ERM to 84.6% DRO under strong regularization; similar jumps with early stopping on Waterbirds and CelebA, with only 1-3 points of average-accuracy cost.
- **Takeaway:** Report worst-attack, worst-topology, and worst-role, not only mean F1/ASR. Unknown attack groups may not exist at train time.

## Guo Calibration

**On Calibration of Modern Neural Networks.** ICML 2017. [PMLR](https://proceedings.mlr.press/v70/guo17a.html)

- **Problem:** Accuracy is not reliability. A detector that says "attack probability 0.9" is calibrated only if about 90% of such cases are attacks.
- **Method:** Reliability diagrams, ECE, MCE, NLL. Learn a scalar temperature T on a held-out set; replace logits z with z/T before softmax. Argmax class is unchanged.
- **Result:** Modern nets are often more overconfident than older ones. Temperature scaling beats more complex calibrators on vision and is competitive on NLP, and is cheap.
- **Takeaway:** GNN anomaly scores are not isolation probabilities until they are calibrated. Calibration drifts when the deployment distribution moves.

## Deep Ensembles

**Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles.** NeurIPS 2017. [NeurIPS](https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html)

- **Problem:** One network is a bad estimator of its own ignorance.
- **Method:** Train M independently initialized probabilistic nets with a proper scoring rule; optionally add light adversarial training. At inference, average predictive distributions; disagreement/entropy is epistemic uncertainty.
- **Result:** Uncertainty quality matches or beats then-current approximate Bayes. Better OOD behavior than MC-dropout. M=5 already helps, including ImageNet-scale experiments.
- **Takeaway:** Multi-agent diversity is an ensemble only if models, tools, or evidence actually differ. Identical prompted clones fail together under one injection.

## Energy OOD

**Energy-based Out-of-distribution Detection.** NeurIPS 2020. [NeurIPS](https://proceedings.neurips.cc/paper/2020/hash/f5496252609c43eb8a3d147ab9b9c006-Abstract.html)

- **Problem:** Softmax compares known classes. An unknown input can still have a high max probability.
- **Method:** Energy score E(x) = -T log sum_j exp(f_j(x)/T). In-distribution samples tend to have low energy. Optional fine-tuning with auxiliary outliers and energy margins. Metrics: FPR95, AUROC, AUPR.
- **Result:** On CIFAR-10 WideResNet, energy cuts FPR95 by about 18 points versus softmax; energy fine-tuning beats outlier exposure by about 5 points (CIFAR-10) and 11 points (CIFAR-100).
- **Takeaway:** Unknown-attack detection can be "does this interaction look in-distribution?" rather than "which known attack is it?" Camouflaged attacks and novel benign tasks both fool a naive OOD score.

## Conformal Risk Control

**Conformal Risk Control.** ICLR 2024. [ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html)

- **Problem:** Conformal prediction controls miscoverage. Operators often care about a different bounded, monotone loss (false-clear cost, false-quarantine cost).
- **Method:** Hold out n calibration points. Pick threshold hat-lambda so empirical risk plus a B/(n+1) correction stays under budget alpha. Under exchangeability, boundedness, and monotonicity, expected risk is at most alpha, with an O(1/n) gap.
- **Result:** Realized risk hugs the target: tumor segmentation 0.0987 vs 0.1; COCO 0.0996 vs 0.1; ImageNet hierarchical 0.0499 vs 0.05; Natural Questions 0.2996 vs 0.3.
- **Takeaway:** Turns a detector score into a risk-budgeted decision rule. Exchangeability fails under adaptive attacks and strong drift; those need extra work.

## Feature Squeezing

**Feature Squeezing: Detecting Adversarial Examples in Deep Neural Networks.** NDSS 2018. [UVA](https://www.cs.virginia.edu/~evans/pubs/ndss2018/)

- **Problem:** Tiny adversarial features may not survive a squeezing transform. If the model's prediction changes a lot under squeezing, the input is suspect.
- **Method:** Reduce bit depth and apply spatial smoothing. L1 distance between original and squeezed softmax vectors is the score; a joint detector takes the max over squeezers. Thresholds are set on clean data (~5% FPR).
- **Result:** Joint detector catches about 98% of 11 static attacks on MNIST and about 85% on CIFAR-10 / ImageNet, without changing the classifier.
- **Takeaway:** Consistency under sanitization (paraphrase, strip hidden instructions, normalize tool args) is a detection idea. Adaptive attackers who know the squeezer are out of scope of the original guarantee.

## Reluplex

**Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks.** CAV 2017. [PDF](https://theory.stanford.edu/~barrett/pubs/KBD+17.pdf)

- **Problem:** Many test samples with no failure is not a proof. Safety-critical nets need SAT (counterexample) or UNSAT (no violation in the region).
- **Method:** Simplex extended to non-convex ReLU, with bound propagation and on-demand splits. Exact on the full net, not an approximation.
- **Result:** Verifies 45 ACAS Xu networks (8 layers, 300 ReLUs): some properties proved, some real counterexamples found. Roughly an order of magnitude larger than prior exact methods; hard properties still time out.
- **Takeaway:** Do not verify the LLM. Verify small routers, permission controllers, and tool policies.

## DeepPoly

**An Abstract Domain for Certifying Neural Networks.** POPL 2019. [ETH](https://files.sri.inf.ethz.ch/popl19-paper264.pdf)

- **Problem:** Exact enumeration does not scale. If a sound over-approximation of reachable outputs never hits a bad set, the true net is safe.
- **Method:** Abstract domain mixing floating-point polyhedra and intervals; transformers for affine, ReLU, maxpool; refinement by splitting when bounds are loose.
- **Result:** Tighter than AI2 and Fast-Lin on the paper's suite, at larger scale. First abstract-refinement proofs of robustness to non-trivial rotations on given images.
- **Takeaway:** Bound worst-case influence on a collaboration graph. Loose abstracts yield "unknown," not "unsafe." Natural language still lacks a good sound abstraction.

## IBP

**Scalable Verified Training for Provably Robust Image Classification.** ICCV 2019. [CVF](https://openaccess.thecvf.com/content_ICCV_2019/html/Gowal_Scalable_Verified_Training_for_Provably_Robust_Image_Classification_ICCV_2019_paper.html)

- **Problem:** Interval bounds on ordinary nets are too loose to prove much. Training against those bounds can make the net easier to certify.
- **Method:** Interval bound propagation; verified loss from worst-case logit bounds; curriculum on perturbation radius and mix with standard loss.
- **Result:** MNIST verified error 3.67% to 2.23% (eps=0.1) and 19.32% to 8.05% (eps=0.3); CIFAR-10 8/255 from 78.22% to 67.96%. Tiny-ImageNet gets non-vacuous bounds with still-high verified error (~94%).
- **Takeaway:** Train the small control layer (router, aggregator) to be certifiable; do not expect this of the LLM.

## Shielding

**Safe Reinforcement Learning via Shielding.** AAAI 2018. [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/11797)

- **Problem:** Learners violate hard safety rules during exploration. The environment should block those actions with minimum interference.
- **Method:** Temporal-logic / automaton specs, a finite environment abstraction, product game, winning region. The shield forwards safe actions and replaces unsafe ones. Proofs of safety and low interference, plus learning-convergence discussion.
- **Result:** Grid-world, driving, tank, Pacman: unshielded runs violate; shielded runs do not. Some learners also train faster. Small-grid synthesis under 2 seconds.
- **Takeaway:** Runtime shield on tool actions (allow, rewrite, deny) without retraining the backbone. Specs and abstractions are human-provided; a wrong abstract voids the guarantee.

## DP-SGD

**Deep Learning with Differential Privacy.** CCS 2016. [Google](https://research.google/pubs/archive/45428.pdf)

- **Problem:** Trained parameters can leak training points. Bound each example's influence and add noise.
- **Method:** Per-example gradients, clip L2 to C, add Gaussian noise, update. Moments accountant tracks (epsilon, delta).
- **Result:** Tighter privacy accounting than strong composition (example: epsilon 1.26 versus 9.34 at 100 epochs). (8, 1e-5)-DP: MNIST 97%, CIFAR-10 ~73%.
- **Takeaway:** If a trust or memory model is trained on multi-tenant traces, DP-SGD is the privacy layer. It does not stop inference-time injection.

## Fair Representations

**Learning Adversarially Fair and Transferable Representations.** ICML 2018. [PMLR](https://proceedings.mlr.press/v80/madras18a.html)

- **Problem:** Fairness only on the current head does not transfer. Sensitive attributes should be hard to recover from the representation.
- **Method:** Encoder, task head, decoder, and an adversary that predicts sensitive attribute A from Z. Min-max training with objectives matched to demographic parity, equalized odds, or equal opportunity. Freeze the encoder and test new tasks.
- **Result:** Matching the adversary to the fairness definition improves the accuracy-fairness curve on Adult. On Heritage Health transfer tasks, equalized-odds unfairness drops about 20% versus non-transfer baselines.
- **Takeaway:** Trust detectors can confuse role, language, or position with malice. Report false-quarantine by role. Fairness definitions conflict; stripping group signal can also strip security-relevant context.

## PBFT

**Practical Byzantine Fault Tolerance.** OSDI 1999. [USENIX](https://www.usenix.org/conference/osdi-99/practical-byzantine-fault-tolerance)

- **Problem:** Up to f replicas may behave arbitrarily. The service should still agree on operation order if there are at least 3f+1 replicas.
- **Method:** Primary orders requests; backups follow pre-prepare, prepare, commit. Intersecting quorums prevent conflicting commits. View change on a bad primary; checkpoints and state transfer recover lagging replicas. MACs, batching, read-only optimizations.
- **Result:** Byzantine-fault-tolerant NFS (BFS) is about 3% slower than unreplicated NFS on Andrew, an order of magnitude faster than prior practical BFT.
- **Takeaway:** Global correctness does not require identifying every faulty node. MAS can borrow quorum, view change, and checkpoints, but must upgrade byte equality to semantic / evidence agreement. LLMs are not deterministic state machines; correlated failures are likely.

## Cross-paper conclusions

1. A detector score is not trust. Calibrate, estimate uncertainty / OOD, then make a risk-budgeted decision, then intervene and recover.
2. Average performance is not reliability. Name the attacker set and the worst group.
3. Redundancy works only if errors are not highly correlated.
4. Verify small controllers, not the full LLM.
5. Healing needs a recovery semantics (view change, checkpoint, shield), not only permanent edge cuts.
