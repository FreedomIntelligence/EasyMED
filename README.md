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

为了最有效地比较两种训练方法的优劣，我们采用了一种严谨的 **双周期交叉设计 (Two-Period Crossover Design)**。这种设计让每位参与者都能体验到 EasyMED 和真人SP两种模式，从而充当其自身的对照，使比较结果更为可靠。

* **参与者与基线评估 (Participants & Baseline):**
    * 我们招募了 **20名** 已完成理论学习但尚未通过临床技能考试的医学生。
    * 在实验开始前，所有参与者都参加了一次**基线前测 (Baseline Pre-test)**，以评估其初始临床技能水平。
    * 随后，我们根据前测成绩，将他们随机分配到两个小组：A组 (n=10) 和 B组 (n=10)。

* **双周期交叉流程 (Two-Period Crossover Procedure):**
    整个实验为期四周，分为两个周期，每个周期结束后都进行一次全面的技能测试 。

| 时期 | 周期时长 | A组 (n=10) 的训练方式 | B组 (n=10) 的训练方式 |
| :--- | :--- | :--- | :--- |
| **周期一** | **前两周** | 🤖 **使用 EasyMED 系统** | 🧑‍⚕️ **与真人SP练习** |
| *中期测试* | *第二周结束时* | \- | *所有20名参与者参加第一次能力测试* |
| **周期二** | **后两周** | 🧑‍⚕️ **与真人SP练习** (交叉) | 🤖 **使用 EasyMED 系统** (交叉) |
| *最终测试* | *第四周结束时* | \- | *所有20名参与者参加第二次能力测试* |

* **盲法评估 (Blinded Assessment):**
    * 在中期和最终的所有技能测试中，负责评分的外部专家考官均**不知晓学生在此期间接受了何种训练方式**。这确保了评估结果的绝对客观与公正。

---
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


## 🤝 如何贡献 (Contributing)

我们热烈欢迎并感谢任何形式的贡献！无论您是开发者、研究人员还是临床专家，如果您对改进本项目有任何想法、建议或想要修复错误，请随时：
* **Fork** 本仓库
* 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
* 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
* 推送到分支 (`git push origin feature/AmazingFeature`)
* **提交一个 Pull Request**

---

---

## 📜 许可证 (License)

本项目采用 [MIT License](LICENSE.txt) 授权。
