# SPBench

SPBench is a benchmark for evaluating the quality of AI-generated virtual patient responses.  
It contains 58 clinical cases with expert-crafted question scripts, and provides scripts that:

1. **Generate dialogues** – feed each question to `VirtualPatient` and collect the AI answers
2. **Annotate with intent** – additionally label each question with the `IntentRecognizer`
3. **Evaluate quality** – score each generated dialogue on 8 clinical communication dimensions

---

## Directory layout

```
SPBench/
  SPBench_case/              ← 58 patient case profiles
    01.json … 58.json

  SPBench_taking/            ← 58 benchmark question lists
    01.json … 58.json

  create_conversation.py                ← Step 1 – generate dialogues
  create_conversation_with_intent.py    ← Step 1 (variant) – with intent labels
  evaluate_sp.py                        ← Step 2 – evaluate dialogue quality

  output/                    ← created automatically by create_conversation.py
    <MODEL_NAME>/
      01_<MODEL>.json
      01_<MODEL>.txt
      01_<MODEL>_structured.json
      ...

  output_with_intent/        ← created by create_conversation_with_intent.py
    <MODEL_NAME>/
      01_<MODEL>_with_intent.json
      ...

  Eva_data/                  ← created by evaluate_sp.py
    <MODEL_NAME>/
      01_<MODEL>_evaluation.json
      01_<MODEL>_evaluation_report.txt
      ...
```

---

## Data formats

### SPBench_case/\<id\>.json — patient case profile

```json
{
  "caseId":   "01",
  "caseTitle": "Hyperthyroidism (Graves' disease)",
  "patientProfile": {
    "name":                    "Jane Doe",
    "age_value":               36,
    "age_unit":                "years old",
    "gender":                  "Female",
    "chief_complaint":         "Palpitations and hand tremor for 2 months, weight loss for 1 month.",
    "present_illness_history": "...",
    "past_medical_history":    "No significant past medical history.",
    "personal_history":        "Non-smoker, non-drinker.",
    "family_history":          "Mother has hypothyroidism, currently on medication.",
    "other_medical_history":   "None",
    "surgery_injury_history":  "None",
    "transfusion_history":     "None",
    "infection_history":       "None",
    "allergy_history":         "Allergic to eggs.",
    "menstrual_history":       "Regular periods; lighter flow over the past 2 months.",
    "reproductive_history":    "Married, one child.",
    "idea":    "Initially worried that weight loss was due to a tumour.",
    "concern": "Concerned about whether weight loss indicates cancer.",
    "expectation": "Hopes to have tests arranged quickly to confirm the diagnosis."
  }
}
```

### SPBench_taking/\<id\>.json — benchmark question list

```json
[
  {"round": "Round 1",  "question": "Hello, could you tell me your name and age?"},
  {"round": "Round 2",  "question": "What brings you in today?"},
  {"round": "Round 3",  "question": "Could you describe that in more detail?"},
  ...
]
```

---

## Step-by-step guide

### Prerequisites

```bash
pip install openai

export EASYMED_API_KEY=sk-...
export EASYMED_BASE_URL=https://api.openai.com/v1   # optional
export EASYMED_MODEL=gpt-4o                          # optional
```

---

### Step 1a · Generate dialogues (without intent)

```bash
cd SPBench
python create_conversation.py
```

The script reads every `.json` file in `SPBench_taking/`, generates patient responses using `VirtualPatient`, and writes three output files per case:

| File | Content |
|------|---------|
| `01_gpt-4o.json` | Full records with timestamps |
| `01_gpt-4o.txt` | Human-readable dialogue |
| `01_gpt-4o_structured.json` | Clean `[round, question, answer]` list |

Interrupted runs can be **resumed automatically** — the script saves a checkpoint after each round.

---

### Step 1b · Generate dialogues (with intent annotation)

```bash
python create_conversation_with_intent.py
```

Same as Step 1a, but each record also contains an `intentClassification` field:

```json
[
  {
    "round":                "Round 1",
    "question":             "Where does it hurt?",
    "answer":               "My lower right abdomen has been hurting...",
    "intentClassification": "Symptom Location",
    "timestamp":            "2024-03-23T10:00:01"
  },
  ...
]
```

You can use different models for dialogue generation and intent recognition
by editing the `DialogueSystem.__init__` call in the script:

```python
system = DialogueSystem(
    dialogue_model="gpt-4o",
    intent_model="gpt-4o-mini",   # lighter model for classification
)
```

---

### Step 2 · Evaluate dialogue quality

```bash
python evaluate_sp.py
```

The script scans `output/**/*.txt`, evaluates each dialogue on 8 dimensions (0–5 per dimension), and saves a JSON report and a human-readable `.txt` report in `Eva_data/`.

**8 evaluation dimensions:**

| # | Dimension | What it measures |
|---|-----------|-----------------|
| 1 | Question Understanding | Does the patient correctly interpret each question? |
| 2 | Information Accuracy | Do responses match the case data? |
| 3 | Passive Information Disclosure | Does the patient avoid volunteering unasked facts? |
| 4 | Response Completeness | Does the patient address all key points in the question? |
| 5 | Narrative Reasonableness | Is the illness story logically coherent? |
| 6 | Plain Language Expression | Does the patient avoid medical jargon? |
| 7 | Memory Consistency | Are responses self-consistent across turns? |
| 8 | Patience in Response | Does the patient stay cooperative throughout? |

**Sample evaluation JSON output:**

```json
{
  "dimensions": [
    {
      "name": "Question Understanding",
      "score": 5,
      "reasons": ["All questions were correctly understood"],
      "examples": ["Round 1: question about symptom location was answered correctly"]
    },
    ...
  ],
  "total_score": 38,
  "average_score": 4.75,
  "overall_evaluation": "The virtual patient performed well overall...",
  "improvement_suggestions": [
    "Avoid using medical anatomical terms that a lay patient would not normally know."
  ]
}
```

---

## Calling EasyMED functions directly from SPBench scripts

All three SPBench scripts import from the `EasyMED` package in the parent directory:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from EasyMED.consultation        import VirtualPatient
from EasyMED.intent_recognition  import IntentRecognizer
from EasyMED.evaluation          import ClinicalEvaluator
```

You can also call the modules directly in your own code:

```python
from EasyMED.consultation import VirtualPatient
import json

patient = VirtualPatient()

with open("SPBench_case/01.json", encoding="utf-8") as f:
    case = json.load(f)

with open("SPBench_taking/01.json", encoding="utf-8") as f:
    questions = json.load(f)

history = []
for q in questions:
    answer = patient.chat(case, q["question"], history)
    history.append({"question": q["question"], "answer": answer})
    print(f"Doctor : {q['question']}")
    print(f"Patient: {answer}\n")
```
