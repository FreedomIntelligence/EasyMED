"""
EasyMED - Clinical Skills Evaluation Module

Evaluates a medical student's consultation performance against an expert
case template.  The evaluator uses an LLM to analyse six dimensions:

    1. History-Taking         – completeness and accuracy of the consultation
    2. Physical Examination   – appropriate selection of physical exam items
    3. Auxiliary Examination  – appropriate use of laboratory / imaging studies
    4. Diagnostic Reasoning   – correctness of diagnosis and differential diagnosis
    5. Treatment Planning     – appropriateness of the proposed treatment plan
    6. Overall Performance    – assessment and improvement suggestions

Usage:
    from evaluation import ClinicalEvaluator

    evaluator = ClinicalEvaluator()   # reads config from env vars

    result = evaluator.evaluate(session_data, case_template)
    for section, text in result.items():
        print(f"=== {section} ===")
        print(text)

Session data format
-------------------
session_data = {
    "sessionId": "...",
    "userId":    "...",
    "caseId":    "...",
    "history": [
        {"question": "...", "answer": "...", "intentClassification": "..."},
        ...
    ],
    "performedExams": [
        {"itemName": "...", "result": "...", "examType": "physical_exam|auxiliary_exam"},
        ...
    ],
    "userSubmissions": [
        {
            "data": {
                "mainDiagnoses": [{"diagnosisName": "..."}],
                "differentialDiagnoses": [{"disease": "...", "status": "support|exclude"}],
            }
        },
        ...
    ],
    "userTreatments": [
        {"data": {"treatmentPlan": "..."}},
        ...
    ],
}

Case template format
--------------------
case_template = {
    "caseId":    "...",
    "caseTitle": "...",
    "patientProfile": {
        "name": "...", "age_value": 30, "age_unit": "years",
        "gender": "Male", "chief_complaint": "...",
        "present_illness_history": "...",
        ...
    },
    "mustConsultionItems":    ["Chief Complaint", "Onset Time", ...],
    "optionalConsultionItems":["Lifestyle Habits", ...],
    "mustPhysicalExams":      ["Temperature", "Blood Pressure", ...],
    "optionalPhysicalExams":  [...],
    "mustAuxiliaryLabs":      ["CBC", "Chest CT", ...],
    "optionalAuxiliaryLabs":  [...],
    "physicalExams":          {"Temperature": "36.5°C", ...},
    "auxiliaryLabs":          {"CBC": "...", ...},
    "diagnoses": {
        "mainDiagnosis": {"disease": "..."},
        "differentialDiagnoses": [{"disease": "..."}, ...]
    },
    "treatments": "1. Oxygen therapy\n2. Anti-infective treatment\n...",
}
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from openai import OpenAI


class ClinicalEvaluator:
    """
    Evaluates a medical student's clinical consultation against an expert case template.

    Returns a dict with keys:
        "consultation", "physical", "auxiliary", "diagnosis", "treatment", "overall"
    each containing a plain-text evaluation paragraph.

    API configuration (same env vars as VirtualPatient):
        EASYMED_API_KEY   – required
        EASYMED_BASE_URL  – optional
        EASYMED_MODEL     – optional, defaults to "gpt-4o"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key  = api_key  or os.environ.get("EASYMED_API_KEY")
        self.base_url = base_url or os.environ.get("EASYMED_BASE_URL")
        self.model    = model    or os.environ.get("EASYMED_MODEL", "gpt-4o")

        if not self.api_key:
            raise ValueError(
                "API key is required. "
                "Set the EASYMED_API_KEY environment variable or pass api_key=."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def evaluate(
        self,
        session_data: Dict,
        case_template: Dict,
    ) -> Dict[str, str]:
        """
        Evaluate the student's performance for a single session.

        Args:
            session_data:   Dict describing what the student did.
            case_template:  Dict containing the expert standard answer.

        Returns:
            Dict with keys "consultation", "physical", "auxiliary",
            "diagnosis", "treatment", "overall", each mapping to a
            plain-text evaluation string.
        """
        session_summary = self._build_session_summary(session_data, case_template)
        expert_answer   = self._build_expert_answer(case_template)
        prompt          = self._build_evaluation_prompt(session_summary, expert_answer)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            raw_text = response.choices[0].message.content.strip()
            return self._parse_evaluation(raw_text)

        except Exception as exc:
            print(f"[ClinicalEvaluator] LLM call failed: {exc}")
            return self._default_evaluation()

    # ------------------------------------------------------------------
    # Session summary builder
    # ------------------------------------------------------------------

    def _build_session_summary(self, session: Dict, template: Dict) -> str:
        parts: List[str] = []
        patient = template.get("patientProfile", {})

        parts.append(
            f"[Case Information]\n"
            f"Patient: {patient.get('name', 'Unknown')}, "
            f"{patient.get('age_value', '')} {patient.get('age_unit', 'years old')}, "
            f"{patient.get('gender', 'Unknown')}\n"
            f"Chief Complaint: {patient.get('chief_complaint', '')}\n"
            f"History of Present Illness: {patient.get('present_illness_history', '')}\n"
        )

        # History-taking
        lines: List[str] = []
        for item in session.get("history", []):
            if item.get("question") and item.get("answer"):
                q_line = f"Doctor: {item['question']}"
                if item.get("intentClassification"):
                    q_line += f" (Intent: {item['intentClassification']})"
                lines.append(q_line)
                lines.append(f"Patient: {item['answer']}")

        if lines:
            parts.append("[Consultation Process]")
            parts.extend(lines[:40])
            if len(lines) > 40:
                parts.append("... (truncated)")

        # Physical / auxiliary exams
        physical: List[str] = []
        auxiliary: List[str] = []
        for exam in session.get("performedExams", []):
            if not exam.get("itemName"):
                continue
            line = f"{exam['itemName']}: {exam.get('result', '')}"
            if exam.get("examType") == "physical_exam":
                physical.append(line)
            else:
                auxiliary.append(line)

        if physical:
            parts.append("\n[Physical Examination Performed]")
            parts.extend(physical)

        if auxiliary:
            parts.append("\n[Auxiliary Examinations Performed]")
            parts.extend(auxiliary)

        # Diagnosis
        submissions = session.get("userSubmissions", [])
        if submissions:
            sub_data = submissions[-1].get("data", {})
            parts.append("[Student Diagnosis]")

            main_dx = sub_data.get("mainDiagnoses", [])
            if main_dx:
                parts.append("Primary Diagnosis:")
                for dx in main_dx:
                    parts.append(f"  - {dx.get('diagnosisName', '')}")

            diff_dx = sub_data.get("differentialDiagnoses", [])
            if diff_dx:
                parts.append("Differential Diagnosis:")
                for dx in diff_dx:
                    status = "Support" if dx.get("status") == "support" else "Exclude"
                    parts.append(f"  - {dx.get('disease', '')} ({status})")

        # Treatment
        treatments = session.get("userTreatments", [])
        if treatments:
            plan = treatments[-1].get("data", {}).get("treatmentPlan", "")
            if plan:
                parts.append("\n[Treatment Plan Submitted]")
                parts.append(f"Treatment Plan: {plan}")

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Expert answer builder
    # ------------------------------------------------------------------

    def _build_expert_answer(self, template: Dict) -> str:
        lines: List[str] = []

        lines.append("[Standard Consultation Key Points]")
        must_consult = template.get("mustConsultionItems", [])
        lines.append("Required inquiry items: " + ", ".join(must_consult))
        opt_consult  = template.get("optionalConsultionItems", [])
        if opt_consult:
            lines.append("Optional inquiry items: " + ", ".join(opt_consult))

        lines.append("\n[Standard Physical Examination]")
        must_phys = template.get("mustPhysicalExams", [])
        lines.append("Required examination items: " + ", ".join(must_phys))
        opt_phys  = [i for i in template.get("optionalPhysicalExams", []) if i.strip()]
        if opt_phys:
            lines.append("Optional examination items: " + ", ".join(opt_phys))
        phys_results = template.get("physicalExams", {})
        if phys_results:
            lines.append("Standard examination findings:")
            for k, v in phys_results.items():
                lines.append(f"  - {k}: {v}")

        lines.append("\n[Standard Auxiliary Examinations]")
        must_aux = template.get("mustAuxiliaryLabs", [])
        lines.append("Required examination items: " + ", ".join(must_aux))
        opt_aux  = [i for i in template.get("optionalAuxiliaryLabs", []) if i.strip()]
        if opt_aux:
            lines.append("Optional examination items: " + ", ".join(opt_aux))
        aux_results = template.get("auxiliaryLabs", {})
        if aux_results:
            lines.append("Standard examination findings:")
            for k, v in aux_results.items():
                lines.append(f"  - {k}: {v}")

        lines.append("\n[Standard Diagnosis]")
        dx = template.get("diagnoses", {})
        main_dx = dx.get("mainDiagnosis", {})
        if isinstance(main_dx, list):
            lines.append("Primary diagnosis: " + ", ".join(d.get("disease", "") for d in main_dx))
        else:
            lines.append(f"Primary diagnosis: {main_dx.get('disease', '')}")

        diff_dxs = dx.get("differentialDiagnoses", [])
        if diff_dxs:
            lines.append("Differential diagnoses:")
            for d in diff_dxs:
                lines.append(f"  - {d.get('disease', '')}")

        lines.append("\n[Standard Treatment Plan]")
        lines.append(template.get("treatments", ""))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Prompt / parse helpers
    # ------------------------------------------------------------------

    def _build_evaluation_prompt(self, session_summary: str, expert_answer: str) -> str:
        return f"""
You are a senior clinical medical education expert. Please evaluate a medical student's clinical skills practice session.

[Important Evaluation Principles]
1. Evaluate strictly against the expert standard answer — do not add requirements beyond it.
2. Only compare the student's performance to the standard answer; do not apply your own judgment.
3. Items listed in the standard answer are required; items NOT listed must not be used as grounds for deduction.
4. Focus on whether the student completed all requirements in the standard answer.
5. Do not evaluate content that is not in the standard answer.
6. Do not use phrases such as "does not meet the standard answer."
7. Present your findings clearly and without repetition.

[Student Performance Record]
{session_summary}

[Expert Standard Answer]
{expert_answer}

Please evaluate the student's performance strictly against the standard answer, focusing on the following six areas:

1. **History-Taking**:
   - Compare against the required consultation key points — did the student cover all required inquiry items?
   - Identify any missed intent categories and explain their relevance to the diagnosis.
   - Note any inquiry items outside the standard answer and assess whether they are appropriate.
   - Focus on the completeness and accuracy of the consultation.

2. **Physical Examination**:
   - Compare against the required physical exam items — did the student complete all required items?
   - Completed items: list required and optional items the student performed.
   - Missed items: list required items the student omitted, and explain their relevance to the diagnosis. If none, state so.
   - Extra items: list any items the student performed that are outside the standard answer, and assess whether they are clinically appropriate.

3. **Auxiliary Examinations**:
   - Compare against the required auxiliary examination items — did the student complete all required items?
   - Completed items: list required and optional items the student ordered.
   - Missed items: list required items the student missed, and explain their relevance to the diagnosis. If none, state so.
   - Extra items: list any tests outside the standard answer, and assess clinical appropriateness.

4. **Diagnostic Reasoning**:
   - Compare against the standard diagnosis — does the student's diagnosis match the expert answer?
   - Compare the differential diagnosis against the standard answer.
   - Assess whether the student's supporting evidence is sufficient and accurate.
   - Note any diagnoses outside the standard answer and suggest improvements.

5. **Treatment Planning**:
   - List both the student's treatment plan and the standard treatment plan separately.
   - Note: items in parentheses in the standard answer are examples — the student may use alternative specific measures.
   - Compare against the standard plan and clearly identify discrepancies and missing items; provide improvement suggestions.
   - Evaluate any treatments outside the standard answer for clinical rationale.

6. **Overall Performance**:
   - Provide a comprehensive assessment based on the standard answer.
   - Summarize how well the student met the required standards.
   - Provide targeted improvement suggestions.

[Important Reminders]
- Strictly follow the above six section headings and sub-points in your output.
- Keep each section to approximately 200–300 words.

Please format your evaluation as follows:

## Consultation Evaluation
[Specific evaluation based on the standard consultation key points]

## Physical Examination Evaluation
[Specific evaluation based on the standard physical exam items]

## Auxiliary Examination Evaluation
[Specific evaluation based on the standard auxiliary examination items]

## Diagnosis Evaluation
[Specific evaluation based on the standard diagnosis]

## Treatment Evaluation
[Specific evaluation based on the standard treatment plan]

## Overall Evaluation
[Comprehensive evaluation based on the standard answer]

Note: Follow the above format strictly. Do not include any other content.
"""

    def _parse_evaluation(self, text: str) -> Dict[str, str]:
        sections = {
            "consultation": "",
            "physical":     "",
            "auxiliary":    "",
            "diagnosis":    "",
            "treatment":    "",
            "overall":      "",
        }
        mapping = {
            "Consultation Evaluation":          "consultation",
            "Physical Examination Evaluation":  "physical",
            "Auxiliary Examination Evaluation": "auxiliary",
            "Diagnosis Evaluation":             "diagnosis",
            "Treatment Evaluation":             "treatment",
            "Overall Evaluation":               "overall",
        }

        current = None
        for line in text.split("\n"):
            line = line.strip()
            matched = False
            for label, key in mapping.items():
                if label in line:
                    current = key
                    matched = True
                    break
            if not matched and current and line and not line.startswith("#"):
                sections[current] += line + "\n"

        return {k: v.strip() for k, v in sections.items()}

    def _default_evaluation(self) -> Dict[str, str]:
        return {
            "consultation": "The consultation process was largely completed. Consider further improving history-taking skills.",
            "physical":     "Physical examination items were generally appropriate. Ensure comprehensive coverage.",
            "auxiliary":    "Auxiliary examination choices were generally appropriate. Ensure targeted selection.",
            "diagnosis":    "The diagnostic reasoning was mostly correct. Consider strengthening evidence collection.",
            "treatment":    "The treatment plan needs further refinement.",
            "overall":      "Overall performance was average. There is room for further improvement.",
        }


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    session_file  = "sample_session.json"
    template_file = "sample_template.json"

    for f in (session_file, template_file):
        if not os.path.exists(f):
            print(f"Demo file '{f}' not found. Please provide sample JSON files.")
            exit(1)

    with open(session_file,  encoding="utf-8") as f:
        session = json.load(f)
    with open(template_file, encoding="utf-8") as f:
        template = json.load(f)

    evaluator = ClinicalEvaluator()
    result    = evaluator.evaluate(session, template)

    print("=== EasyMED Clinical Evaluation ===\n")
    labels = {
        "consultation": "History-Taking",
        "physical":     "Physical Examination",
        "auxiliary":    "Auxiliary Examinations",
        "diagnosis":    "Diagnostic Reasoning",
        "treatment":    "Treatment Planning",
        "overall":      "Overall Performance",
    }
    for key, label in labels.items():
        print(f"### {label}")
        print(result[key])
        print()
