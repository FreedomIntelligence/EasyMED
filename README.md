# 🏥 EasyMED: AI-Powered Clinical Skills Training Platform

![EasyMED Project Banner](https://placehold.co/1200x250/3367d6/ffffff?text=EasyMED%3A+The+Future+of+Clinical+Education)

<p align="center">
  <em>An advanced AI tutor designed to revolutionize medical education by simulating realistic, standardized patient interactions.</em>
</p>

<p align="center">
  <a href="#-overview">Overview</a> •
  <a href="#-features">Features</a> •
  <a href="#-research--experiments">Research & Experiments</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-contributing">Contributing</a> •
  <a href="#-citation">Citation</a>
</p>

---

## 🎯 Overview

**EasyMED** is a Virtual Standardized Patient (VSP) system powered by Large Language Models (LLMs). It is designed to address the core challenges of traditional medical training using human Standardized Patients (SPs), namely **high costs, poor scalability, and a lack of consistency**.

Our platform provides medical students with a safe and repeatable environment to practice a full range of core clinical skills by interacting with highly realistic AI patients. This includes **clinical consultation, physical examination, ordering ancillary tests, making a diagnosis, and formulating a treatment plan**.

More than just a simulator, EasyMED is an intelligent tutor. Its built-in **Clinical Reasoning Path Tracing and Evaluation (CR-PTE)** framework automatically assesses student performance, providing instant, objective, and data-driven feedback to help them efficiently improve their clinical reasoning skills.

---

## ✨ Features

- 💬 **Natural Language Consultation:** Engage in fluid, medically logical conversations with AI patients.
- 🩺 **Multi-Scenario Clinical Simulation:** Covers the five core stages of a clinical encounter, from consultation to treatment.
- 🔬 **Dynamic Lab & Imaging Generation:** Order tests like a complete blood count (CBC) or X-rays, and the system will generate dynamic reports that match the case's pathophysiology.
- 🤖 **Intelligent Assessment & Feedback:** The built-in CR-PTE framework automatically analyzes and scores a student's clinical reasoning path.
- 📈 **Data-Driven Educational Analytics:** Logs and analyzes learning behaviors to provide educators with insights for curriculum optimization.

---

## 🧪 Research & Experiments

To comprehensively evaluate the value of EasyMED, we designed and implemented a single, integrated study. This rigorous controlled experiment aims to simultaneously answer key questions regarding the system's **Efficacy**, **Realism**, and **Reliability**.

> **Core Research Question:** Compared to traditional human SPs, can the LLM-driven EasyMED serve as a more effective, reliable, and well-received alternative for clinical skills training?

### **Experimental Design & Procedure**

To most effectively compare the two training methods, we employed a rigorous **Two-Period Crossover Design**. This design allows each participant to experience both the EasyMED and human SP modalities, thereby serving as their own control and making the results more reliable.

* **Participants & Baseline:**
    * We recruited **20 medical students** who had completed their theoretical coursework but had not yet passed the national clinical skills examination.
    * Prior to the experiment, all participants took a **Baseline Pre-test** to assess their initial skill level.
    * Based on the pre-test scores, participants were randomly assigned to two balanced groups using a matched-pairs methodology: Group A (n=10) and Group B (n=10).

* **Two-Period Crossover Procedure:**
    The entire experiment lasted four weeks and was divided into two periods. A comprehensive skills assessment was conducted after each period.

| Period | Duration | Group A (n=10) Training Method | Group B (n=10) Training Method |
| :--- | :--- | :--- | :--- |
| **Period 1** | First 2 Weeks | 🤖 **Trains with the EasyMED System** | 🧑‍⚕️ **Trains with a Human SP** |
| *Mid-Experiment Test* | End of Week 2 | \- | *All 20 participants take the first clinical skills assessment* |
| **Period 2** | Last 2 Weeks | 🧑‍⚕️ **Trains with a Human SP** (Crossover) | 🤖 **Trains with the EasyMED System** (Crossover) |
| *Final Test* | End of Week 4 | \- | *All 20 participants take the final clinical skills assessment* |

* **Blinded Assessment:**
    * All mid-experiment and final skills assessments were scored by external expert examiners who were **blinded to the training modality each student received** during the respective period. This ensures the absolute objectivity and fairness of the evaluation.

### **Multi-Faceted Data Analysis**

After the experiment, we conducted an in-depth analysis of the rich data we collected across three key dimensions:

#### **1. Efficacy Analysis**

* **Objective:** To determine the actual effectiveness of EasyMED in improving the clinical skills of medical students.
* **Methods:**
    * **Primary Metric:** Compared the **Gain Score (Post-test - Pre-test)** on clinical skills assessments between the two groups.
    * **Statistical Test:** Used an independent samples t-test to analyze if the difference between groups was statistically significant.
    * **Subjective Feedback:** Analyzed changes in students' self-reported confidence from pre- and post-experiment questionnaires.

#### **2. Realism & Consistency Analysis**

* **Objective:** To assess how closely the EasyMED VSP's conversational behavior resembles that of a human SP.
* **Methods:**
    * Dialogue logs from both Group A (interacting with VSP) and Group B (interacting with human SP) were extracted.
    * **Semantic Consistency:** Used models like Sentence-BERT to calculate the cosine similarity between VSP and human SP responses in the same context.
    * **Interaction Patterns:** Compared the average **Interaction Turns** and **Response Length** to analyze similarities in conversational rhythm and information density.

#### **3. Reliability Analysis of Internal Assessment**

* **Objective:** To validate the accuracy and reliability of the built-in CR-PTE automated assessment framework.
* **Methods:**
    * Students' performance data was scored by both the **EasyMED system** and by **external human experts**.
    * **Correlation Analysis:** Calculated the **Pearson correlation coefficient** between the system's automated scores and the experts' scores.
    * **Consistency Check:** Analyzed the scoring agreement on sub-dimensions such as "history-taking completeness" and "diagnostic accuracy."

---


## 🤝 Contributing

We warmly welcome and appreciate all forms of contributions! Whether you are a developer, a researcher, or a clinical expert, if you have ideas for improving this project or want to fix a bug, please feel free to:
1.  **Fork** this repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a **Pull Request**.

---


## 📜 License

This project is licensed under the [MIT License](LICENSE.txt).
