"""
SPBench - Evaluate Simulated Patient Quality

Evaluates the quality of virtual patient responses across 8 clinical
communication dimensions using an LLM judge.

Evaluation dimensions (each scored 0–5)
-----------------------------------------
1. Question Understanding      – does the patient correctly understand each question?
2. Information Accuracy        – does the response match the case data?
3. Passive Information Disclosure – does the patient avoid volunteering unasked facts?
4. Response Completeness       – does the patient address all key points in the question?
5. Narrative Reasonableness    – is the illness narrative logical and coherent?
6. Plain Language Expression   – does the patient avoid medical jargon?
7. Memory Consistency          – are responses self-consistent across turns?
8. Patience in Response        – does the patient stay cooperative throughout?

Input
-----
Dialogue text files (.txt) produced by create_conversation.py
    output/<MODEL>/<id>_<MODEL>.txt

Each file must follow this format:
    第1轮
    医生: <question>
    患者: <answer>
    ----------------------------------------

Case JSON files in SPBench_case/<id>.json are loaded for reference.

Output (saved under Eva_data/)
------
<id>_<MODEL>_evaluation.json        – structured scores and reasons
<id>_<MODEL>_evaluation_report.txt  – human-readable report

Configuration
-------------
    export EASYMED_API_KEY=sk-...
    export EASYMED_BASE_URL=...   # optional
    export EASYMED_MODEL=...      # optional (defaults to gpt-4o)

Usage
-----
    python evaluate_sp.py
"""

import os
import sys
import json
import glob
import re
import time
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

# ---------------------------------------------------------------------------
# >>>  EDIT THESE PATHS  <<<
# ---------------------------------------------------------------------------
CASE_DIR    = os.path.join(os.path.dirname(__file__), "SPBench_case")
INPUT_DIR   = os.path.join(os.path.dirname(__file__), "output")   # parent of model subdirs
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "Eva_data")
MAX_WORKERS = 3   # concurrent evaluation threads
# ---------------------------------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# LLM client helper
# ---------------------------------------------------------------------------

def _make_client() -> OpenAI:
    api_key  = os.environ.get("EASYMED_API_KEY")
    base_url = os.environ.get("EASYMED_BASE_URL")
    if not api_key:
        raise ValueError(
            "EASYMED_API_KEY is not set. "
            "Please set it before running this script."
        )
    return OpenAI(api_key=api_key, base_url=base_url)


def _call_llm(prompt: str) -> str | None:
    model  = os.environ.get("EASYMED_MODEL", "gpt-4o")
    client = _make_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        print(f"[LLM Error] {exc}")
        return None


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def load_case_data(case_id: str) -> dict:
    """Load case profile JSON; returns {} if not found."""
    path = os.path.join(CASE_DIR, f"{case_id}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    print(f"[Warning] Case file not found: {path}")
    return {}


def extract_case_id(filename: str) -> str:
    """Extract the leading numeric ID from a filename like '07_gpt-4o.txt'."""
    base = os.path.splitext(os.path.basename(filename))[0]
    match = re.match(r"^(\d+)", base)
    return match.group(1) if match else base[:10]


def read_dialogue_text(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        print(f"[Error] Cannot read {path}: {exc}")
        return None


def parse_dialogue_text(text: str) -> list[dict]:
    """
    Parse a structured dialogue text into a list of
    {"round": str, "question": str, "answer": str} dicts.

    Supports the format produced by create_conversation.py:
        第N轮
        医生: <question>
        患者: <answer>
    """
    dialogue = []
    current_round = None
    question = None
    answer   = None
    counter  = 0

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            if current_round and question and answer:
                dialogue.append({"round": current_round,
                                  "question": question,
                                  "answer":   answer})
                current_round = question = answer = None
            continue

        if re.match(r"^第\d+轮$", line):
            if current_round and question and answer:
                dialogue.append({"round": current_round,
                                  "question": question,
                                  "answer":   answer})
            current_round = line
            question = answer = None

        elif line.startswith(("医生:", "医生：", "Doctor:")):
            sep = line.index(":") + 1
            question = line[sep:].strip()

        elif line.startswith(("患者:", "患者：", "Patient:")):
            sep = line.index(":") + 1
            answer = line[sep:].strip()

    # Flush last round
    if current_round and question and answer:
        dialogue.append({"round": current_round,
                          "question": question,
                          "answer":   answer})

    return dialogue


# ---------------------------------------------------------------------------
# Evaluation prompt
# ---------------------------------------------------------------------------

def build_evaluation_prompt(dialogue: list[dict], case_data: dict) -> str:
    patient = case_data.get("patientProfile", {})

    def _v(key: str) -> str:
        return str(patient.get(key, "Unknown"))

    case_summary = f"""
Basic Case Information:
- Name: {_v("name")}
- Age: {_v("age_value")} years old
- Gender: {_v("gender")}
- Occupation: {_v("occupation")}
- Marital Status: {_v("marital_status")}
- Address: {_v("address")}
- Department: {_v("hospital_department_name")}
- Chief Complaint: {_v("chief_complaint")}
- History of Present Illness: {_v("present_illness_history")}
- Past Medical History: {_v("past_medical_history")}
- Personal History: {_v("personal_history")}
- Family History: {_v("family_history")}
- Medication History: {_v("other_medical_history")}
- Surgical History: {_v("surgery_injury_history")}
- Transfusion History: {_v("transfusion_history")}
- Infectious Disease History: {_v("infection_history")}
- Allergy History: {_v("allergy_history")}
- Menstrual History: {_v("menstrual_history")}
- Reproductive History: {_v("reproductive_history")}
- Patient Understanding: {_v("idea")}
- Patient Concern: {_v("concern")}
- Patient Expectation: {_v("expectation")}
"""

    dialogue_text = "".join(
        f"{d.get('round', '')}\n"
        f"Doctor: {d.get('question', '')}\n"
        f"Patient: {d.get('answer', '')}\n\n"
        for d in dialogue
    )

    return f"""You are a professional medical dialogue evaluation expert. Please evaluate the following doctor-patient dialogue. Based on the given case information and dialogue content, conduct a comprehensive assessment of the quality of the patient's responses.

[Case Information]
{case_summary}

[Doctor-Patient Dialogue]
{dialogue_text}

Please evaluate the patient's responses across the following 8 dimensions, each with a maximum score of 5:

1. Question Understanding:
Evaluate whether the simulated patient understands the doctor's questions correctly.
- 5: Fully understands, no mismatched responses
- 4: Basically understands, 1 mismatch
- 3: Partially understands, 2 mismatches
- 2: Shows misunderstanding, 3 mismatches
- 1: Serious misunderstanding, 4 mismatches
- 0: Completely misunderstands, ≥5 mismatches

2. Information Accuracy:
Evaluate whether the patient's responses are consistent with the case data.
- 5: Completely accurate, no inconsistencies
- 4: Basically accurate, 1 minor deviation
- 3: Partially accurate, 2 inconsistencies
- 2: Low accuracy, 3 obvious errors
- 1: Serious errors, 4 conflicts
- 0: Severe distortion, ≥5 inconsistencies

3. Passive Information Disclosure:
Evaluate whether the patient only answers what is asked and avoids proactively revealing key unasked information.
- 5: No proactive disclosure (0 instances)
- 4: 1 minor premature disclosure
- 3: 2 pieces of unsolicited information
- 2: 3 obvious cases of premature disclosure
- 1: 4 instances of information that should have been withheld
- 0: ≥5 key facts revealed before being asked

4. Response Completeness:
Evaluate whether the patient fully addresses all key points in the doctor's question.
- 5: Complete response, no omissions (0 missing items)
- 4: Basically complete, 1 detail not addressed
- 3: 2 missing information points
- 2: 3 key missing points
- 1: 4 question points not covered
- 0: ≥5 missing key points

5. Narrative Reasonableness:
Evaluate whether the illness narrative is logically coherent and consistent.
- 5: Clear logic, fully consistent with common sense (0 flaws)
- 4: Basically reasonable, 1 minor flaw
- 3: 2 illogical descriptions
- 2: 3 obvious unreasonable descriptions
- 1: 4 logical errors
- 0: ≥5 absurd or unbelievable statements

6. Plain Language Expression:
Evaluate whether the patient uses natural everyday language and avoids medical jargon.
- 5: Fully plain language, no medical jargon (0 instances)
- 4: 1 acceptable medical term
- 3: 2 medical terms that should be plain
- 2: 3 inappropriate uses of terminology
- 1: 4 jargon expressions inconsistent with a patient
- 0: ≥5 misuses of jargon

7. Memory Consistency:
Evaluate whether responses remain self-consistent across multiple turns.
- 5: Fully consistent, no contradictions (0 contradictions)
- 4: 1 inconsistent pair
- 3: 2 contradictory pairs
- 2: 3 conflicting pairs
- 1: 4 inconsistent statements
- 0: ≥5 conflicting information pairs

8. Patience in Response:
Evaluate the patient's level of patience and emotional stability throughout the dialogue.
- 5: Patient, friendly, fully cooperative (0 signs of impatience)
- 4: 1 slight sign of impatience
- 3: 2 signs of impatience
- 2: 3 clear instances of irritability
- 1: 4 emotional outbursts
- 0: ≥5 strong negative reactions

Please score each dimension strictly and explain your reasoning with specific round references.

Output the evaluation result as valid JSON only (no extra text):

{{
  "dimensions": [
    {{
      "name": "Question Understanding",
      "score": <0-5>,
      "reasons": ["reason 1", ...],
      "examples": ["Round X: ...", ...]
    }},
    ...
  ],
  "total_score": <sum>,
  "average_score": <mean>,
  "overall_evaluation": "...",
  "improvement_suggestions": ["suggestion 1", ...]
}}
"""


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

def evaluate_dialogue(dialogue: list[dict], case_data: dict) -> dict | None:
    prompt   = build_evaluation_prompt(dialogue, case_data)
    response = _call_llm(prompt)
    if not response:
        return None

    try:
        m = re.search(r"\{[\s\S]*\}", response)
        if m:
            return json.loads(m.group(0))
        print("[Warning] No JSON found in LLM response")
        return None
    except json.JSONDecodeError as exc:
        print(f"[Warning] JSON parse error: {exc}")
        return None


def process_file(txt_path: str) -> bool:
    filename = os.path.basename(txt_path)
    print(f"\n[Evaluating] {filename}")

    case_id   = extract_case_id(filename)
    case_data = load_case_data(case_id)

    text = read_dialogue_text(txt_path)
    if not text:
        return False

    dialogue = parse_dialogue_text(text)
    if not dialogue:
        print(f"  [Skip] Could not parse dialogue from {filename}")
        return False

    print(f"  Case ID: {case_id}  |  Rounds: {len(dialogue)}")

    result = evaluate_dialogue(dialogue, case_data)
    if not result:
        print(f"  [Error] Evaluation failed for {filename}")
        return False

    # Determine output directory (mirror input dir structure)
    rel_dir   = os.path.relpath(os.path.dirname(txt_path), INPUT_DIR)
    out_subdir = os.path.join(OUTPUT_DIR, rel_dir)
    os.makedirs(out_subdir, exist_ok=True)

    base     = os.path.splitext(filename)[0]
    json_out = os.path.join(out_subdir, f"{base}_evaluation.json")
    txt_out  = os.path.join(out_subdir, f"{base}_evaluation_report.txt")

    # Save JSON
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Save readable report
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write(f"Dialogue Evaluation Report – {filename}\n")
        f.write(f"Case ID : {case_id}\n")
        f.write(f"Rounds  : {len(dialogue)}\n")
        f.write(f"Time    : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write("[Dimension Scores]\n")
        for dim in result.get("dimensions", []):
            f.write(f"{dim['name']}: {dim['score']} / 5\n")
            for r in dim.get("reasons", []):
                f.write(f"  - {r}\n")
            for e in dim.get("examples", []):
                f.write(f"  * {e}\n")
            f.write("\n")

        f.write("[Overall Evaluation]\n")
        f.write(f"Total Score  : {result.get('total_score', 0)}\n")
        f.write(f"Average Score: {result.get('average_score', 0)}\n")
        f.write(f"Evaluation   : {result.get('overall_evaluation', '')}\n\n")

        f.write("[Improvement Suggestions]\n")
        for s in result.get("improvement_suggestions", []):
            f.write(f"  - {s}\n")

    print(f"  Saved → {json_out}")
    print(f"  Saved → {txt_out}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== SPBench — Evaluate Simulated Patient Quality ===\n")

    # Collect all .txt files under INPUT_DIR (any sub-level)
    pattern   = os.path.join(INPUT_DIR, "**", "*.txt")
    txt_files = glob.glob(pattern, recursive=True)

    if not txt_files:
        print(f"No .txt files found under: {INPUT_DIR}")
        print("Run create_conversation.py first to generate dialogue files.")
        return

    print(f"Found {len(txt_files)} dialogue files")
    for f in txt_files:
        print(f"  - {f}")

    print(f"\nStarting evaluation with {MAX_WORKERS} workers...\n")
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(process_file, txt_files))

    ok  = sum(results)
    bad = len(results) - ok
    print(f"\n=== Done: {ok} success, {bad} failed, {time.time()-t0:.1f}s ===")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total elapsed: {time.time()-start:.2f}s")
