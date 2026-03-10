# EasyMED

<p align="center">
<b>EasyMED: A Multi-Agent Virtual Standardized Patient Framework for Medical Education</b>
</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue">
<img src="https://img.shields.io/badge/License-MIT-green">
<img src="https://img.shields.io/badge/Status-Research-orange">

</p>

EasyMED is a **multi-agent virtual standardized patient (VSP) framework** designed to support clinical skills training in medical education.  
The system separates **clinical intent recognition, patient simulation, and educational evaluation** into coordinated agents, enabling stable multi-turn dialogue, controlled information disclosure, and structured learning feedback.

This repository contains the implementation used in the paper:

> **Human or LLM as Standardized Patients? A Comparative Study in Medical Education**

---

# Overview

Standardized Patients (SPs) are widely used in medical education to train students in **clinical communication, history taking, and diagnostic reasoning**. However, traditional SP programs rely on human actors and are therefore **costly, labor-intensive, and difficult to scale**.

EasyMED addresses these challenges by introducing a **large-language-model-based virtual standardized patient system** that enables scalable and realistic doctor–patient interactions.

Compared with traditional monolithic LLM simulations, EasyMED decomposes the interaction pipeline into specialized agents that explicitly model different components of the clinical consultation process.

The framework supports:

- stable multi-turn clinical dialogue
- case-grounded patient simulation
- controlled information disclosure
- automated evaluation of clinical inquiry performance

---

# Key Features

## Multi-Agent Architecture

EasyMED consists of three coordinated agents:

| Agent | Function |
|------|---------|
| **Auxiliary Agent** | Recognizes the clinical intent of the student's question |
| **Patient Agent** | Generates case-grounded patient responses |
| **Evaluation Agent** | Analyzes the full interaction and produces structured feedback |

This factorized architecture improves interaction stability and enables precise control over patient behavior.

---

## SPBench Benchmark

We also introduce **SPBench**, a benchmark dataset designed for evaluating virtual standardized patients.

SPBench evaluates systems along **eight clinically motivated criteria**:

- Query Comprehension (QC)
- Case Consistency (CC)
- Controlled Disclosure (CD)
- Response Completeness (RC)
- Logical Coherence (LC)
- Language Naturalness (LN)
- Conversational Consistency (CS)
- Patient Demeanor (PD)

---

# System Workflow

EasyMED operates in two phases.

## Phase 1 — Consultation

1. The student asks a clinical question.
2. The **Auxiliary Agent** identifies the clinical intent.
3. The **Patient Agent** retrieves relevant case information.
4. The **Patient Agent** generates a natural patient response.

This design ensures that patient responses remain consistent with the underlying case while revealing information only when appropriate.

---

## Phase 2 — Evaluation

After the dialogue ends:

1. The **Evaluation Agent** reviews the full interaction history.
2. It compares the student's inquiries against expert clinical checklists.
3. Structured feedback is generated to support learning.

This evaluation helps students identify **missing clinical inquiries and reasoning gaps**.

---

# Repository Structure

```
EasyMED/
│
├── agents/
│   ├── auxiliary_agent.py
│   ├── patient_agent.py
│   └── evaluation_agent.py
│
├── prompts/
│   ├── patient_prompt.txt
│   ├── intent_prompt.txt
│   └── evaluation_prompt.txt
│
├── datasets/
│   └── spbench/
│
├── scripts/
│   └── run_dialogue.py
│
├── outputs/
│
└── README.md
```

---

# Installation

## Requirements

- Python **3.10+**
- OpenAI / Gemini API
- CUDA GPU (optional)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Quick Start

Run a simulated clinical consultation:

```bash
python scripts/run_dialogue.py \
    --case_id 001 \
    --model gemini-2.5-pro
```

The script will:

1. Load a patient case
2. Simulate doctor–patient interaction
3. Save dialogue and evaluation results

---

# Example Dialogue

```
Doctor: When did the pain start?

Patient: It started about three days ago, doctor.
At first it was mild, but it has gradually become worse.

Doctor: Does anything make the pain worse?

Patient: Yes, it tends to hurt more when I sit or lie down.
```

After the consultation, the system automatically produces **structured feedback** on the student’s clinical inquiry performance.

---

# Dataset

## SPBench

SPBench contains:

- **58 clinical cases**
- **3,208 doctor–patient dialogue pairs**
- **14 medical specialties**

Each case includes:

```
patient_profile.json
dialogue_history.json
clinical_checklist.json
```

The dataset is designed for **interaction-level evaluation of virtual standardized patients**.

---

# Experimental Results

On SPBench evaluation:

| System | Overall Score |
|------|------|
| Human SP | 97.33 |
| EasyMED | 96.98 |
| EvoPatient | 93.33 |

EasyMED achieves performance **closest to human standardized patients**.

In a **four-week controlled study with medical students**, EasyMED demonstrates:

- learning outcomes comparable to human SP training
- stronger improvements for novice learners
- significantly reduced training cost

---

# Citation

If you use EasyMED in your research, please cite:

```bibtex
@article{zhang2026easymed,
  title={Human or LLM as Standardized Patients? A Comparative Study in Medical Education},
  author={Zhang, Bingquan and Liu, Xiaoxiao and Wang, Yuchi and Zhou, Lei and Xie, Qianqian and Wang, Benyou},
  year={2026},
  archivePrefix={arXiv},
  primaryClass={cs.CL}
}
```

---

# License

This project is released under the **MIT License**.

---

# Acknowledgements

We thank the clinical experts, standardized patient instructors, and medical students who contributed to the dataset construction and evaluation.

---

# Contact

For questions or collaborations, please open an issue on GitHub.
