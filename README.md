# EasyMED  
### A Multi-Agent Virtual Standardized Patient Framework for Medical Education

<p align="center">

<img src="docs/easymed_architecture.png" width="750">

</p>

<p align="center">

<a href="https://arxiv.org/abs/XXXX.XXXXX">
<img src="https://img.shields.io/badge/Paper-arXiv-red">
</a>

<img src="https://img.shields.io/badge/License-MIT-blue">

<img src="https://img.shields.io/badge/Python-3.10+-green">

</p>

---


# Overview

Standardized Patients (SPs) play a critical role in medical education by enabling students to practice clinical communication and diagnostic reasoning. However, human SP programs are expensive, labor-intensive, and difficult to scale.

EasyMED addresses these limitations by introducing an **LLM-based virtual standardized patient system** that supports:

- stable multi-turn clinical dialogue
- inquiry-conditioned information disclosure
- structured feedback for clinical training

Unlike traditional end-to-end LLM simulations, EasyMED decomposes the workflow into multiple agents that explicitly model the clinical interaction process.

---

# Key Features

### Multi-Agent Architecture

EasyMED consists of three coordinated agents:

| Agent | Function |
|------|---------|
| **Auxiliary Agent** | Recognizes the clinical intent of the student's question |
| **Patient Agent** | Generates case-grounded patient responses |
| **Evaluation Agent** | Analyzes the full interaction and produces feedback |

This factorized architecture improves interaction stability and allows precise control over patient behavior.

---

### SPBench Benchmark

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

This process enables inquiry-conditioned information disclosure.

## Phase 2 — Evaluation

After the dialogue ends:

1. The **Evaluation Agent** reviews the full interaction history.
2. It compares the student's inquiries against expert clinical checklists.
3. Structured feedback is generated to support learning.

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

### Requirements

- Python 3.10+
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

Example interaction:

```
Doctor: When did the pain start?

Patient: It started about three days ago, doctor.
At first it was mild but it has been getting worse.
```

After the session ends, the Evaluation Agent will generate structured feedback.

---

# Dataset

## SPBench

SPBench contains:

- 58 patient cases
- 3,208 doctor–patient dialogue pairs
- 14 medical specialties

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

EasyMED achieves performance closest to human standardized patients.

In a **four-week controlled study with medical students**, EasyMED demonstrates:

- learning outcomes comparable to human SP training
- stronger improvements for novice learners
- significantly lower training cost

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

We thank the clinical experts, 
