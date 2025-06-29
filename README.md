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

为了全面评估 EasyMED 系统的价值，我们设计并实施了一项单一、综合性的研究。本研究旨在通过一次严谨的对照实验，同时回答关于**系统有效性（Efficacy）**、**模拟逼真度（Realism）**和**评估可靠性（Reliability）**的多个核心问题。

> **核心研究问题：** 与传统的人类标准化病人相比，由LLM驱动的EasyMED能否成为一种更有效、更可靠、且广受欢迎的临床技能训练方案？

### **实验设计与流程 (Experimental Design & Procedure)**

我们采用严格的实验设计来确保研究结论的科学性。

* **参与者与分组 (Participants & Design):**
    * 我们招募了 **20名** 已完成理论学习但尚未通过临床技能考试的医学生。
    * 所有参与者先进行一次**基线前测 (Pre-test)** 以评估初始水平。
    * 随后，我们根据前测成绩采用**配对设计 (Matched-Pairs Design)**，将他们分配到两个能力均衡的小组：
        * **A组 (实验组, n=10):** 使用 EasyMED 系统进行为期四周的自主训练。
        * **B组 (对照组, n=10):** 与经验丰富的真人标准化病人（SP）进行同时长、同内容的一对一模拟训练。

* **干预与数据收集 (Intervention & Data Collection):**
    * 在为期 **4周** 的训练周期中，我们全面记录了所有交互数据，包括A组的系统日志和B组的现场录音/录像。
    * 训练结束后，所有参与者参加一场由外部专家考官进行的、**盲法评分**的**最终后测 (Post-test)**，以评估技能提升情况。
    * 同时，我们通过问卷收集了所有参与者对训练体验的主观反馈。

### **多维度数据分析 (Multi-Faceted Data Analysis)**

在实验结束后，我们利用收集到的丰富数据，从以下三个关键维度进行了深入分析：

#### **1. 教学有效性分析 (Efficacy Analysis)**

* **目标：** 检验 EasyMED 在提升医学生临床技能方面的实际效果。
* **方法：**
    * **主要指标：** 对比实验组与对照组在最终后测中的**技能增益分数 (Gain Score = Post-test - Pre-test)**。
    * **统计检验：** 使用独立样本t检验，分析两组间的差异是否具有统计学意义。
    * **主观反馈：** 分析前后测问卷中，学生对自身能力信心的变化。

#### **2. 模拟逼真度与一致性分析 (Realism & Consistency Analysis)**

* **目标：** 评估 EasyMED (VSP) 在模拟对话时，与真人SP的相似程度。
* **方法：**
    * 我们从实验过程中抽取A组（与VSP交互）和B组（与真人SP交互）的对话记录。
    * **语义一致性：** 使用 Sentence-BERT 等模型计算 VSP 与真人SP 在相同上下文中的回复内容的语义相似度。
    * **交互模式：** 对比两组对话的平均**交互轮次**和**回复长度**，分析其在交互节奏和信息密度上的异同。

#### **3. 内部评估可靠性分析 (Reliability Analysis of Internal Assessment)**

* **目标：** 验证 EasyMED 内置的 CR-PTE 自动评估框架是否准确、可靠。
* **方法：**
    * 我们将实验组学生的训练表现同时交由 **EasyMED系统** 和 **外部人类专家** 进行评分。
    * **相关性分析：** 计算系统自动评分与专家评分之间的**皮尔逊相关系数 (Pearson correlation coefficient)**。
    * **一致性检验：** 分析两者在“病史采集完整性”、“诊断准确性”等细分维度上评分的一致性。

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
