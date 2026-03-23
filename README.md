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

## Repository layout

```
EasyMED/          ← core Python modules
  consultation.py      VirtualPatient class
  intent_recognition.py IntentRecognizer class
  evaluation.py        ClinicalEvaluator class
  requirements.txt

SPBench/          ← benchmark construction and evaluation scripts
  create_conversation.py              generate dialogues with VirtualPatient
  create_conversation_with_intent.py  same + intent annotation
  evaluate_sp.py                      evaluate generated dialogue quality (8 dimensions)
  SPBench_case/    ← patient case JSON files  (01.json … 58.json)
  SPBench_taking/  ← benchmark question lists (01.json … 58.json)

.env.example      ← copy to .env and fill in your API key
```

---

## Quick start

### 1 · Install dependencies

```bash
pip install openai
```

### 2 · Set your API key

```bash
# Copy and edit the example file
cp .env.example .env

# Or export directly in your shell
export EASYMED_API_KEY=sk-...
export EASYMED_BASE_URL=https://api.openai.com/v1   # optional
export EASYMED_MODEL=gpt-4o                         # optional
```

EasyMED works with **any OpenAI-compatible API** (OpenAI, Azure OpenAI, local vLLM, etc.).

---

## EasyMED modules

### VirtualPatient — `EasyMED/consultation.py`

```python
from EasyMED.consultation import VirtualPatient
import json

patient = VirtualPatient()        # reads EASYMED_* env vars

with open("SPBench/SPBench_case/01.json", encoding="utf-8") as f:
    case_data = json.load(f)

history = []
while True:
    question = input("Doctor: ")
    answer   = patient.chat(case_data, question, history)
    print(f"Patient: {answer}\n")
    history.append({"question": question, "answer": answer})
```

### IntentRecognizer — `EasyMED/intent_recognition.py`

```python
from EasyMED.intent_recognition import IntentRecognizer

recognizer = IntentRecognizer()

intent = recognizer.recognize(
    question="您最近睡眠怎么样？",
    history=[{"question": "哪里不舒服？", "answer": "头疼"}],
)
print(intent)   # → "一般情况"
```

**32 intent categories** (abridged):

> 个人信息 · 主要症状 · 发作时间 · 诱因 · 症况部位 · 症状性质 ·
> 持续时间频率 · 加重缓解情况 · 伴随症状 · 病情演变 · 诊疗经过 ·
> 一般情况 · 大小便情况 · 体重变化 · 慢性病史 · 传染病史 ·
> 手术外伤史 · 输血史 · 过敏史 · 预防接种史 · 长期用药史 ·
> 旅行史 · 生活习惯 · 职业情况 · 冶游史 · 婚育史 · 家族史 ·
> 月经史 · 患者理解 · 患者担忧 · 患者期望 · 闲聊

### ClinicalEvaluator — `EasyMED/evaluation.py`

```python
from EasyMED.evaluation import ClinicalEvaluator
import json

evaluator = ClinicalEvaluator()

with open("case_template.json", encoding="utf-8") as f:
    template = json.load(f)

session_data = {
    "sessionId": "student_01_case01_1711900000",
    "userId":    "student_01",
    "caseId":    "01",
    "history": [
        {"question": "您哪里不舒服？", "answer": "肚子疼", "intentClassification": "主要症状"},
        ...
    ],
    "performedExams": [
        {"itemName": "腹部触诊", "result": "右下腹压痛", "examType": "physical_exam"},
    ],
    "userSubmissions": [
        {"data": {
            "mainDiagnoses": [{"diagnosisName": "急性阑尾炎"}],
            "differentialDiagnoses": [{"disease": "右侧输卵管炎", "status": "exclude"}],
        }}
    ],
    "userTreatments": [
        {"data": {"treatmentPlan": "1. 急诊手术\n2. 抗感染治疗"}},
    ],
}

result = evaluator.evaluate(session_data, template)
for section, text in result.items():
    print(f"=== {section} ===")
    print(text)
```

---

## SPBench

See **[SPBench/README.md](SPBench/README.md)** for the complete guide on:

- SPBench case data format
- Generating dialogues with `create_conversation.py`
- Adding intent labels with `create_conversation_with_intent.py`
- Evaluating dialogue quality with `evaluate_sp.py`

---

## Case data format

Each case file (`SPBench_case/<id>.json`) follows this structure:

```json
{
  "caseId":          "01",
  "caseTitle":       "急性阑尾炎",
  "caseDescription": "...",
  "patientProfile": {
    "name":                      "张三",
    "age_value":                 28,
    "age_unit":                  "岁",
    "gender":                    "男",
    "occupation":                "教师",
    "chief_complaint":           "右下腹疼痛6小时",
    "present_illness_history":   "...",
    "past_medical_history":      "无",
    "personal_history":          "无特殊",
    "family_history":            "无",
    "other_medical_history":     "无",
    "surgery_injury_history":    "无",
    "transfusion_history":       "无",
    "infection_history":         "无",
    "allergy_history":           "无",
    "menstrual_history":         "不适用",
    "reproductive_history":      "不适用"
  },
  "mustConsultionItems":    ["主要症状", "发作时间", "诱因", "伴随症状"],
  "optionalConsultionItems":["一般情况", "家族史"],
  "mustPhysicalExams":      ["体温", "血压", "腹部触诊"],
  "optionalPhysicalExams":  ["直肠指检"],
  "mustAuxiliaryLabs":      ["血常规", "腹部B超"],
  "optionalAuxiliaryLabs":  ["腹部CT"],
  "physicalExams":          {"体温": "38.2°C", "腹部触诊": "右下腹麦氏点压痛(+)，反跳痛(+)"},
  "auxiliaryLabs":          {"血常规": "WBC 12.3×10⁹/L", "腹部B超": "阑尾肿胀，直径8mm"},
  "diagnoses": {
    "mainDiagnosis": {"disease": "急性阑尾炎"},
    "differentialDiagnoses": [
      {"disease": "右侧输卵管炎"},
      {"disease": "右侧输尿管结石"}
    ]
  },
  "treatments": "1. 急诊阑尾切除术\n2. 术前抗感染治疗（头孢曲松 2g iv）\n3. 补液支持"
}
```

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EASYMED_API_KEY` | ✅ | — | OpenAI-compatible API key |
| `EASYMED_BASE_URL` | ❌ | OpenAI default | Custom API endpoint |
| `EASYMED_MODEL` | ❌ | `gpt-4o` | Model name |

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
