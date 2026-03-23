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
  consultation.py       VirtualPatient class
  intent_recognition.py IntentRecognizer class
  evaluation.py         ClinicalEvaluator class
  requirements.txt

SPBench/          ← benchmark construction and evaluation scripts
  create_conversation.py              generate dialogues with VirtualPatient
  create_conversation_with_intent.py  same + intent annotation per turn
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
    question="How is your sleep lately?",
    history=[{"question": "Where does it hurt?", "answer": "My head hurts."}],
)
print(intent)   # e.g. "General Condition"
```

**32 intent categories:**

> Personal Information · Chief Complaint · Onset Time · Triggering Factors ·
> Symptom Location · Symptom Characteristics · Duration and Frequency ·
> Aggravating / Relieving Factors · Associated Symptoms · Disease Progression ·
> Prior Diagnosis and Treatment · General Condition · Bowel and Bladder Function ·
> Weight Change · Chronic Disease History · Infectious Disease History ·
> Surgical and Trauma History · Transfusion History · Allergy History ·
> Vaccination History · Medication History · Travel History · Lifestyle Habits ·
> Occupational History · Sexual History · Marital and Reproductive History ·
> Family History · Menstrual History · Patient Understanding ·
> Patient Concerns · Patient Expectations · Small Talk

### ClinicalEvaluator — `EasyMED/evaluation.py`

```python
from EasyMED.evaluation import ClinicalEvaluator
import json

evaluator = ClinicalEvaluator()

with open("case_template.json", encoding="utf-8") as f:
    template = json.load(f)

session_data = {
    "sessionId": "student01_case01_1711900000",
    "userId":    "student01",
    "caseId":    "01",
    "history": [
        {
            "question": "Where does it hurt?",
            "answer":   "My lower right abdomen.",
            "intentClassification": "Symptom Location"
        },
        ...
    ],
    "performedExams": [
        {
            "itemName": "Abdominal palpation",
            "result":   "Tenderness at McBurney's point, rebound tenderness positive",
            "examType": "physical_exam"
        },
    ],
    "userSubmissions": [
        {"data": {
            "mainDiagnoses": [{"diagnosisName": "Acute appendicitis"}],
            "differentialDiagnoses": [
                {"disease": "Right-sided salpingitis", "status": "exclude"}
            ],
        }}
    ],
    "userTreatments": [
        {"data": {"treatmentPlan": "1. Emergency appendectomy\n2. Anti-infective therapy"}},
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
  "caseTitle":       "Acute Appendicitis",
  "caseDescription": "28-year-old male presenting with right lower quadrant pain.",
  "patientProfile": {
    "name":                      "John Smith",
    "age_value":                 28,
    "age_unit":                  "years old",
    "gender":                    "Male",
    "occupation":                "Teacher",
    "chief_complaint":           "Right lower abdominal pain for 6 hours",
    "present_illness_history":   "...",
    "past_medical_history":      "None",
    "personal_history":          "Non-smoker, non-drinker",
    "family_history":            "No family history of similar condition",
    "other_medical_history":     "None",
    "surgery_injury_history":    "None",
    "transfusion_history":       "None",
    "infection_history":         "None",
    "allergy_history":           "None",
    "menstrual_history":         "N/A",
    "reproductive_history":      "N/A"
  },
  "mustConsultionItems":    ["Chief Complaint", "Onset Time", "Triggering Factors", "Associated Symptoms"],
  "optionalConsultionItems":["General Condition", "Family History"],
  "mustPhysicalExams":      ["Temperature", "Blood Pressure", "Abdominal palpation"],
  "optionalPhysicalExams":  ["Rectal examination"],
  "mustAuxiliaryLabs":      ["CBC", "Abdominal ultrasound"],
  "optionalAuxiliaryLabs":  ["Abdominal CT"],
  "physicalExams":          {
    "Temperature": "38.2°C",
    "Abdominal palpation": "McBurney's point tenderness (+), rebound tenderness (+)"
  },
  "auxiliaryLabs":          {
    "CBC": "WBC 12.3×10⁹/L",
    "Abdominal ultrasound": "Swollen appendix, diameter 8 mm"
  },
  "diagnoses": {
    "mainDiagnosis": {"disease": "Acute appendicitis"},
    "differentialDiagnoses": [
      {"disease": "Right-sided salpingitis"},
      {"disease": "Right ureteral stone"}
    ]
  },
  "treatments": "1. Emergency appendectomy\n2. Pre-operative anti-infective therapy (ceftriaxone 2 g IV)\n3. Fluid resuscitation"
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
