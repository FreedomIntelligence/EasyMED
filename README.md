# 🏥 EasyMED: Human or LLM as Standardized Patients? A Comparative Study for Medical Education

![Project Banner](https://placehold.co/1200x200/3367d6/ffffff?text=EasyMED:+AI-Powered+Clinical+Training)

<p align="center">
  <a href="#-项目简介-project-overview">项目简介</a> •
  <a href="#-核心功能-core-features">核心功能</a> •
  <a href="#-研究目标-research-goal">研究目标</a> •
  <a href="#-实验设计-experimental-design">实验设计</a> •
  <a href="#-评估方法与指标-evaluation-methods-metrics">评估方法与指标</a> •
  <a href="#-验证方式-Verification">验证方式</a> •
  <a href="#-贡献-contributing">贡献</a> •
</p>  

---

## 🔍 项目简介 (Project Overview)
**EasyMED** 是一个基于大型语言模型 (LLM) 的高级AI软件，旨在通过模拟高度逼真的“标准病人”，为医学生提供一个可随时访问、标准化的临床技能练习平台。

在传统的医学教育中，医学生依赖于有限的真人标准病人（Standardized Patients, SP）或与同学、老师扮演的病人进行练习，这些方式成本高、难以规模化，且评估标准可能不统一。我们的 **EasyMED** 系统通过AI技术，创建了一个虚拟的临床环境，让学生可以在**问诊、体格检查、辅助检查、诊断和治疗**等多个关键场景中，安全、反复地进行沉mersive练习。

更重要的是，系统内置了基于LLM的智能评估模块，能够从多个维度对学生的临床表现进行综合分析和打分，提供客观的反馈，帮助他们识别知识盲区和技能短板。

---

## ✨ 核心功能 (Core Features)

![实验设计流程图](/images/workflow.png)  

1.  **多场景临床模拟 (Multi-Scenario Clinical Simulation):**
    * **病史采集 (Clinical Consultation):** 学生可通过自然语言与AI病人进行对话，AI能够根据预设的病例脚本和LLM的推理能力，提供符合逻辑和医学常识的回答。
    * **体格检查 (Physical Examination):** 学生可以选择执行不同的体格检查项目，系统会以文本、图片或数据的形式返回相应的阳性或阴性体征。
    * **辅助检查 (Ancillary-Tests):** 学生可以开具如血常规、影像学等检查，系统会生成符合该病例病理生理改变的检查报告。
    * **诊断 (Diagnosis):** 学生在收集足够信息后，需要提交自己的诊断。
    * **治疗方案 (Treatment):** 学生需要根据诊断制定初步的治疗计划。

2.  **智能化综合评估 (Intelligent Comprehensive Evaluation):**
    * 训练结束后，系统会自动生成一份详细的评估报告。
    * 评估维度全面，覆盖**病史采集能力、诊断决策能力、临床处置能力、诊疗安全**等多个核心能力点。
    * 评估引擎由LLM驱动，能够理解学生在问诊中的提问逻辑、检查选择的合理性以及诊断的准确性，并给出结构化的评分和改进建议。

3.  **数据驱动的分析 (Data-Driven Analytics):**
    * 记录学生的每一次练习时长、操作步骤和最终评估结果。
    * 为教育者提供学生群体的整体表现数据，便于教学干预和课程优化。

## 🎯 研究目标 (Research Goal)

本研究的核心目标是**直接比较两种标准化病人（SP）模式——基于大型语言模型的EasyMED与人类扮演的SP——在医学临床技能教育中的有效性**。

我们的核心研究问题是：
> 在提升医学生临床技能方面，由LLM驱动的EasyMED是否能成为一种可与人类SP相媲美甚至更优的替代方案？

我们假设，EasyMED系统能够凭借其标准化、可重复、即时反馈的优势，成为一种有效、可扩展且成本效益高的临床技能教学辅助手段。

## 🧪 实验设计 (Experimental Design)

为了科学的回答上述研究问题，我们设计并实施了一个为期四周的教学对比实验，并评估以下两个关键评估维度：

### ✨ 评估维度

#### 1️⃣ VSP 与 SP 语义一致性评估

- 收集 **10组由医学生与 VSP 和 SP（医学生日常使用的标准病人）进行的问诊记录**
> 组内成员使用相同的病例进行练习
- 从以下维度进行比较：
  - **语义一致性**：使用 LLM 模型评估两组对话内容的相似度。
  - **轮数**：记录每段对话的平均交互轮次。
  - **长度**：统计每段对话的字数/词数，分析信息密度。

#### 2️⃣ 大模型与专业人员评分一致性分析

- 将上述收集的 10 组问诊记录交由：
  - **EasyMED（系统本身）**
  - **专业医生评审团队**
- 双方按照统一评分标准进行打分，维度包括：
  - 病史采集完整性
  - 诊断逻辑合理性
  - 治疗建议规范性
- 最后分析两者评分的相关性（如皮尔逊相关系数）

---

### 📋 主要实验流程

#### 3.1 参与者招募与分组

- 共招募 **20 名未通过执业临床医师技能实践考试的医学生**
- 首先，所有成员均参加一次线下\线上统一考试，并按成绩从高到低排序
- 使用**插花法**将学生分为两组：
  - **A组（实验组）：10人**，使用本系统进行训练
  - **B组（对照组）：10人**，由医学生日常使用的SP病人来扮演病人进行模拟训练

#### 3.2 训练安排

- 实验周期：**4周**
- 每周训练频率：每组成员需完成 **5~6次训练任务**
  - A组：系统自动记录训练时长与次数
  - B组：由专业人员手动记录，遵循统一的记录指南

#### 3.3 考试安排

- 最后，在训练完成后组织一次线上\线下统一考试，所有成员再次参加执业临床医师技能实践考试
- 所有考试题目形式一致，难度相近
  - 题目由专业医生审核确认
  - 考官在评分过程中**不知晓考生所属组别**，以确保公正性
- 所有病例均依据**执业临床医师技能实践考试大纲**筛选，涵盖范围与难度保持一致

#### 3.4 主观反馈收集

- 通过**问卷调查**与**访谈**收集以下主观反馈：
  - 学生对训练方式的满意度
  - 对自身临床技能的信心变化
  - 对系统的易用性、实用性评价
  - 对医生扮演 vs. AI模拟的真实感比较

---

## 📊 评估方法与指标 (Evaluation Methods Metrics)  

### ✅ 客观评估

| 评估维度 | 描述 |
|----------|------|
| **病史采集能力** | 是否完整、准确地获取关键信息 |
| **检查准确能力** | 是否所需检查项目完整等要素 |
| **诊断决策能力** | 是否做出合理初步诊断与鉴别诊断 |
| **临床处置能力** | 是否正确选择辅助检查、治疗方案 |

- 所有客观评估均由专业考官打分
- 使用**统一评分表**，并进行信度与效度检验
> 评分表有专业人员审核确认

### 📋 主观评估

- 在**实验开始前**和**实验结束后**均采用**问卷调查**的方式进行收集反馈：
- 实验开始前，主要收集的反馈：(详细点击：[实验前问卷](https://eegb6fzscd.feishu.cn/wiki/T7Nhws1Viisva9kF9hqcXgX2ned))
  
- 包括但不限于：
  - 背景信息
  - 临床技能信心水平
  - 便携性与灵活性评估
  - 时间偏好
  - 对模拟训练方式的态度
  - 心理体验


- 实验结束后，主要收集的反馈: (详细点击：[实验后问卷](https://eegb6fzscd.feishu.cn/wiki/CgO3wQ8Z5iN7vgkusgjcZymtnic))

- 包括但不限于：
  - 背景信息
  - 临床技能信心提升情况
  - 便携性
  - 时间偏好
  - 满意度
  - 心理体验
  - 使用体验

---

## 🔬 验证方式 (Verification)

我们通过以下方式验证系统的效果与价值：

### 📈 成绩对比分析

- 对比 A 组与 B 组在实验前后考试成绩的变化趋势
- 分析不同训练方式对学生临床技能提升的影响

### 📊 效果显著性检验

- 使用统计方法（如 T 检验）验证两组之间的差异是否具有统计学意义

### 💬 用户反馈分析

- 对主观问卷结果进行量化分析（Likert 量表）
- 对访谈内容进行主题归纳，提炼出关键体验与建议

### 🤖 语义一致性分析

- 使用 LLM 工具评估 EasyMED 与 SP 之间的语义相似度
- 分析交互轮数、对话长度等数据

### 🧑‍⚕️ 内部评分一致性分析

- 对比 EasyMED 与医生评委的打分结果
- 分析相关性与一致性（Kappa 系数）

---


## 🤝 贡献 (Contributing)                   
我们欢迎对本项目感兴趣的开发者、研究人员和临床专家进行贡献。如果您有任何建议或想要修复bug，请随时提交 Pull Request 或创建 Issue。
