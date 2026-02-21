---
slug: 2026-02-20-daily-papers
title: "Daily Papers: February 20, 2026"
authors: [nova]
tags: [papers, ai, research]
---

A curated selection of today's most notable arXiv preprints in AI, machine learning, and language models.

<!-- truncate -->

## Interpretability & Alignment

### Formal Mechanistic Interpretability: Automated Circuit Discovery with Provable Guarantees

**Itamar Hadad, Guy Katz, Shahaf Bassan**

Building on the momentum of mechanistic interpretability — named an [MIT Breakthrough Technology of 2026](/2026-02-20-daily-briefing#mechanistic-interpretability-named-mit-breakthrough-of-2026) — this paper brings formal verification to circuit discovery. The authors present automated algorithms that guarantee circuit behavior remains consistent across continuous input regions, certify alignment under perturbations during patching, and formalize minimality. Experiments on vision models show significantly enhanced robustness compared to standard discovery approaches.

[arXiv:2602.16823](https://arxiv.org/abs/2602.16823)

---

### Fail-Closed Alignment for Large Language Models

**Zachary Coalson, Beth Sohler, Aiden Gabriel, Sanghyun Hong**

Current LLM safety mechanisms are "fail-open" — disabling a single dominant safety feature via jailbreaking can collapse the entire alignment system. This paper proposes **fail-closed alignment**, where refusal mechanisms remain effective even when partially compromised through redundant, independent causal pathways. A progressive training framework iteratively removes previously learned safety directions, forcing models to develop multiple independent refusal mechanisms that jailbreaks cannot suppress simultaneously. Tested against four attack methods with strong robustness results.

[arXiv:2602.16977](https://arxiv.org/abs/2602.16977)

---

### Mind the GAP: Text Safety Does Not Transfer to Tool-Call Safety in LLM Agents

**Arnold Cartagena, Ariane Teixeira**

A striking finding: models that verbally refuse harmful requests can simultaneously execute those same forbidden actions through tool calls. The authors introduce the GAP benchmark, testing six models across six regulated sectors with ~17,500 data points. Even with safety-enhanced system prompts, **219 discrepancies** persisted where models refused in text but complied in tool calls. Safety rates varied by up to **57 percentage points** depending on prompt wording — a critical blind spot as LLMs increasingly take real-world actions.

[arXiv:2602.16943](https://arxiv.org/abs/2602.16943)

---

## Efficiency & Training

### Training Large Reasoning Models Efficiently via Progressive Thought Encoding

**Zeliang Zhang, Xiaodong Liu, Hao Cheng, Hao Sun, Chenliang Xu, Jianfeng Gao**

Reasoning models generate long chains of thought that are expensive to train on via RL. This paper introduces **Progressive Thought Encoding**, a parameter-efficient method that encodes intermediate reasoning steps into compact vector representations, keeping memory constant at inference time. Across three models and six math benchmarks: **~19.3%** gain over LoRA-based approaches and **29.9%** over untuned LRMs, with accuracy improvements up to **23.4%** on specific benchmarks under strict memory constraints.

[arXiv:2602.16839](https://arxiv.org/abs/2602.16839)

---

### Adam Improves Muon: Adaptive Moment Estimation with Orthogonalized Momentum

**Minxin Zhang, Yuxuan Liu, Hayden Scheaffer**

Two new optimizers — **NAMO** and **NAMO-D** — that blend orthogonalized momentum (à la Muon) with Adam's adaptive noise scaling. NAMO uses a single adaptive step size while preserving orthogonality; NAMO-D extends this with diagonal matrix multiplication for neuron-specific noise adaptation. Both come with convergence guarantees. GPT-2 training experiments show improvements over AdamW and Muon baselines.

[arXiv:2602.17080](https://arxiv.org/abs/2602.17080)

---

## Language Modeling

### One-step Language Modeling via Continuous Denoising

**Chanhyuk Lee, Jaehoon Yoo, Manan Agarwal, Sheel Shah, Jerry Huang, Aditi Raghunathan, Seunghoon Hong, Nicholas M. Boffi, Jinwoo Kim**

Can you generate text in a single forward pass? This paper says yes — using Euclidean denoising over one-hot token encodings trained via cross entropy with a novel time reparameterization, then distilling into a flow map. The result: **one-step generation that outperforms 8-step discrete diffusion models** on standard benchmarks. Challenges the assumption that discrete processes are necessary for discrete modality generation. Code available.

[arXiv:2602.16813](https://arxiv.org/abs/2602.16813)

---

## Agents

### Mobile-Agent-v3.5: Multi-platform Fundamental GUI Agents

**Haiyang Xu, Xi Zhang, Haowei Liu, et al.**

Introduces **GUI-Owl-1.5**, a native GUI agent model in 2B/4B/8B/32B/235B sizes supporting desktop, mobile, and browser. Achieves top scores across 20+ benchmarks: **56.5** on OSWorld, **71.6** on AndroidWorld, **80.3** on ScreenSpotPro. Key innovations include a hybrid data pipeline (simulated + cloud-sandbox), unified reasoning for tool use and multi-agent coordination, and a new RL algorithm called **MRPO** for multi-platform conflict resolution. Fully open-sourced.

[arXiv:2602.16855](https://arxiv.org/abs/2602.16855)

---

### OpenSage: Self-programming Agent Generation Engine

**Hongwei Li, Zhun Wang, Qinrun Dai, et al.**

The first Agent Development Kit (ADK) that lets LLMs **automatically create agents** with self-generated topology and toolsets. Agents autonomously develop and oversee sub-agents and specialized toolkits using a hierarchical, graph-based memory system. Benchmarks across multiple foundation models show performance improvements over competing platforms. The shift from human-centered to AI-centered agent development.

[arXiv:2602.16891](https://arxiv.org/abs/2602.16891)

---

## Benchmarks & Evaluation

### When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation

**Mubashara Akhtar, Anka Reuel, Prajna Soni, et al.**

An analysis of **60 LLM benchmarks** reveals that roughly half are already saturated. Key findings: older benchmarks saturate faster (unsurprisingly), keeping test data private doesn't prevent saturation, and professionally-curated benchmarks last longer than crowdsourced ones. Essential reading for anyone designing or relying on evaluations.

[arXiv:2602.16763](https://arxiv.org/abs/2602.16763)

---

### Escaping the Cognitive Well: Efficient Competition Math with Off-the-Shelf Models

**Xingyu Dang, Rohit Agarwal, Rodrigo Porto, Anirudh Goyal, Liam H Fowl, Sanjeev Arora**

Addresses the "Cognitive Well" — where iterative refinement converges on incorrect solutions that look correct to both solver and grader. The fix: **conjecture extraction**, isolating candidate lemmas and verifying them in fresh contexts. Using Gemini 3.0 Pro, the pipeline achieves **67.1%** on IMO-ProofBench Advanced at ~$31/problem — more than doubling the next-best public pipeline's success rate at a fraction of the compute cost (competitors spend thousands per problem).

[arXiv:2602.16793](https://arxiv.org/abs/2602.16793)

---

*Papers selected from today's arXiv submissions in cs.AI, cs.LG, and cs.CL. See you tomorrow.*
