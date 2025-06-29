# 🏥 EasyMED: AI-Powered Clinical Skills Training Platform

![EasyMED Project Banner](https://placehold.co/1200x250/3367d6/ffffff?text=EasyMED%3A+The+Future+of+Clinical+Education)

<p align="center">
  <em>An advanced AI tutor designed to revolutionize medical education by simulating realistic, standardized patient interactions.</em>
</p>

<p align="center">
  <a href="#-项目简介">项目简介</a> •
  <a href="#-核心功能">核心功能</a> •
  <a href="#-研究与实验">研究与实验</a> •
  <a href="#-技术实现">技术实现</a> •
  <a href="#-如何贡献">如何贡献</a> •
  <a href="#-如何引用">如何引用</a>
</p>

---

## 🎯 项目简介 (Project Overview)

**EasyMED** 是一个基于大型语言模型 (LLM) 的虚拟病人（Virtual Standardized Patient, VSP）系统。它旨在解决传统医学教育中真人标准化病人 (SP) 培训**成本高、规模小、一致性差**的核心痛点。

通过本平台，医学生可以在一个安全、可重复的环境中，与高度逼真的AI病人进行互动，全面练习**临床问诊、体格检查、开具辅助检查、做出诊断、制定治疗方案**等一系列核心临床技能。

我们的系统不仅是一个模拟器，更是一个智能导师。其内置的 **Clinical Reasoning Path Tracing and Evaluation (CR-PTE)** 框架能够自动评估学生的表现，提供即时、客观、数据驱动的反馈，帮助他们高效提升临床思维能力。

---

## ✨ 核心功能 (Core Features)

- 💬 **自然语言对话问诊:** 与AI病人进行流畅、符合医学逻辑的自然语言交流。
- 🩺 **多场景临床模拟:** 完整覆盖从接诊到治疗的五个核心环节。
- 🔬 **动态检查报告生成:** 可开具血常规、X光等检查，系统会生成与病例匹配的动态报告。
- 🤖 **智能化评估反馈:** 内置CR-PTE框架，对学生的临床推理路径进行自动分析与评分。
- 📈 **数据驱动的教学洞察:** 记录并分析学习行为，为教育者提供教学优化的数据支持。

---

## 🧪 研究与实验 (Research & Experiments)

我们设计了一系列严谨的实验来验证 EasyMED 的有效性、可靠性与实用价值。

> **核心研究问题：** 与传统的人类标准化病人相比，由LLM驱动的EasyMED能否成为一种更有效、更可靠、更具扩展性的临床技能训练方案？

#### **阶段一：VSP 代理的验证性评估 (Phase 1: Validation of the VSP Agent)**

在进行大规模人体试验前，我们首先需要确保我们的AI病人本身是可靠且逼真的。

* **目标：** 评估 EasyMED (VSP) 在模拟对话时，与真人SP的**一致性**和**可靠性**。
* **方法：** 我们收集了10组由医学生分别与 **VSP** 和**真人SP** 在同一病例下进行的问诊对话记录。
* **评估指标：**
    * **✅ 语义一致性 (Semantic Consistency):** 使用 Sentence-BERT 模型计算 VSP 与 SP 在相同上下文中的回复向量的余弦相似度，评估其在关键医学信息和情感表达上的一致性。
    * **🔄 交互轮次 (Interaction Turns):** 对比两种模式下对话的平均交互轮次，评估交互的完整性与节奏。
    * **📄 回复长度 (Response Length):** 分析每轮回复的文本长度分布，评估对话的自然度和信息密度。
* **初步结论：** 结果显示，EasyMED在以上所有维度上均表现出与人类SP高度的一致性，证明了其作为模拟工具的有效性。

#### **阶段二：主要功效研究 (Phase 2: Main Efficacy Study)**

验证了AI的可靠性后，我们开展了一项为期四周的严格对照研究，以评估其教学效果。

* **目标：** 直接比较使用 EasyMED 进行训练与使用传统真人SP进行训练，对医学生临床技能提升的影响。
* **实验设计：**
    * **参与者：** 招募 **20名** 已完成理论学习但尚未通过临床技能考试的医学生。
    * **分组：** 所有参与者先进行一次**基线前测 (Pre-test)**，然后根据成绩采用**配对设计 (Matched-Pairs Design)**，将他们分配到两个能力均衡的小组：
        * **A组 (实验组, n=10):** 使用 EasyMED 系统进行自主训练。
        * **B组 (对照组, n=10):** 与经验丰富的真人SP进行一对一模拟训练。
* **实验流程：**
    * **训练周期：** 持续 **4周**，两组每周完成同等数量和难度的病例学习任务。
    * **最终测试：** 训练结束后，所有参与者参加一场标准化的**最终后测 (Post-test)**。
    * **盲法评估：** 所有考试的评分工作均由**不知晓学生分组情况**的外部专家考官完成，以确保评估的客观公正。
* **结果衡量 (Outcome Measures):**
    * **客观指标：** 对比两组在最终后测中的**技能增益分数 (Gain Score = Post-test - Pre-test)**，并使用独立样本t检验分析其差异的统计显著性。
    * **主观指标：** 通过实验前后的问卷调查，收集学生在学习体验、技能信心、系统易用性等方面的反馈。

---

## 🛠️ 技术实现 (How It Works)

本项目的核心技术栈（待补充）:
* **大语言模型 (LLM):** `Qwen2.5-Max` (用于意图识别)
* **后端:** `Python`, `FastAPI`
* **前端:** `Vue.js`, `TypeScript`
* **数据库:** `PostgreSQL`

---

## 🤝 如何贡献 (Contributing)

我们热烈欢迎并感谢任何形式的贡献！无论您是开发者、研究人员还是临床专家，如果您对改进本项目有任何想法、建议或想要修复错误，请随时：
* **Fork** 本仓库
* 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
* 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
* 推送到分支 (`git push origin feature/AmazingFeature`)
* **提交一个 Pull Request**

---

## 🎓 如何引用 (Citation)

如果您在您的研究中使用了 EasyMED 或本文档，请引用我们的论文（待发表）：

```bibtex
@article{zhang2025easymed,
  title={Human or LLM as Standardized Patients? A Comparative Study for Medical Education},
  author={Zhang, Bingquan and Wang, Yuchi and Hu, Yan and Xie, Qianqian and Wang, Benyou},
  journal={Preprint},
  year={2025}
}
```

---

## 📜 许可证 (License)

本项目采用 [MIT License](LICENSE.txt) 授权。
