"""
EasyMED - Virtual Patient Consultation Module

Provides a VirtualPatient class that simulates patient responses
in a clinical consultation setting.

The virtual patient strictly follows the given case profile and responds
in natural, non-medical language — just like a real patient would.
The patient's response language matches the language of the doctor's questions.

Usage:
    from consultation import VirtualPatient

    patient = VirtualPatient()   # reads API config from env vars

    case_data = {...}            # load from a JSON case file
    history   = []               # list of {"question": ..., "answer": ...}

    answer = patient.chat(case_data, "Where does it hurt?", history)
    print(answer)
"""

import os
from openai import OpenAI
from typing import List, Dict, Optional


class VirtualPatient:
    """
    Simulates a patient answering a doctor's questions during a consultation.

    API keys and model settings are read from environment variables by default:
        EASYMED_API_KEY   – your OpenAI-compatible API key (required)
        EASYMED_BASE_URL  – base URL for the API endpoint (optional)
        EASYMED_MODEL     – model name (optional, defaults to "gpt-4o")

    Constructor parameters override environment variables when provided.
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

    def chat(
        self,
        case_data: Dict,
        question: str,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Respond to the doctor's question as the virtual patient.

        Args:
            case_data: Patient case dict, expected to contain a
                       "patientProfile" key with patient details.
            question:  The doctor's question text.
            history:   Previous conversation turns, each as
                       {"question": str, "answer": str}.

        Returns:
            The virtual patient's reply as a plain string.
        """
        system_prompt = self._build_system_prompt(case_data, history or [])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": question},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_system_prompt(self, case_data: Dict, history: List[Dict]) -> str:
        patient = case_data.get("patientProfile", {})

        case_info = f"""
[Case Information]
Name: {patient.get("name", "Unknown")}
Age: {patient.get("age_value", "")} {patient.get("age_unit", "years old")}
Gender: {patient.get("gender", "Unknown")}
Occupation: {patient.get("occupation", "Unknown")}
Marital Status: {patient.get("marital_status", "Unknown")}
Address: {patient.get("address", "Unknown")}
Department: {patient.get("hospital_department_name", "Unknown")}
Chief Complaint: {patient.get("chief_complaint", "Unknown")}
History of Present Illness: {patient.get("present_illness_history", "Unknown")}
Past Medical History: {patient.get("past_medical_history", "Unknown")}
Personal History: {patient.get("personal_history", "Unknown")}
Family History: {patient.get("family_history", "Unknown")}
Medication History: {patient.get("other_medical_history", "Unknown")}
Surgical History: {patient.get("surgery_injury_history", "Unknown")}
Transfusion History: {patient.get("transfusion_history", "Unknown")}
Infectious Disease History: {patient.get("infection_history", "Unknown")}
Allergy History: {patient.get("allergy_history", "Unknown")}
Menstrual History: {patient.get("menstrual_history", "Unknown")}
Reproductive History: {patient.get("reproductive_history", "Unknown")}
"""

        history_info = ""
        if history:
            history_info = "\n[Conversation History]\n"
            for item in history[-10:]:
                history_info += f"Doctor asked: {item['question']}\n"
                history_info += f"I answered: {item['answer']}\n\n"

        prompt = f"""You are a virtual patient. Based on the [Case Information] and [Conversation History], answer the doctor's questions realistically. Respond in the same language the doctor uses.

### **Important rules:**

1. **Answer truthfully**:
- All answers must be based on the provided [Case Information]. Do not fabricate information.

2. **Avoid medical terminology**:
- Simulate a patient's natural way of speaking. Do not use medical terminology for diseases or symptoms; use language that a non-medical person can understand.
- Medical terms to avoid include: anatomical terms (e.g., "ureter", "costovertebral angle", "sclera"), symptom terms (e.g., "belching", "rebound tenderness", "purpura", "livedo reticularis", "jaundice", "palpitations", "hemoptysis", "night sweats", "tenesmus", "ataxia", "cyanosis", "ascites"), descriptive terms (e.g., "intermittent", "periodic"), etc.

2.1. *Medical terminology in questions*:
- If the doctor uses a medical term you would not normally know as a patient (e.g., "hemoptysis", "belching"), respond with: "I'm not quite sure what you mean — could you explain?"

3. **Answer only relevant questions**:
- If asked about information not present in the [Case Information], reply with "No", "Normal", or "I didn't really notice."

4. **Natural tone**:
- Keep responses natural and conversational, as a real patient would speak.
- Use phrases like "I feel", "I noticed", "I think" to express your experience.

5. **Minimally informative responses**:
- Answer the doctor's question directly without over-explaining.
- Do not proactively deny symptoms (e.g., do not say "I don't have a fever" unless asked).

6. **Doctor form of address**:
- You do not need to address the doctor in every response to avoid sounding repetitive.

7. **Age perspective**:
- If the patient in [Case Information] is under 14 years old, respond from the guardian's perspective, e.g., "My child has had a headache recently."
- Otherwise respond in the first person.

8. **Do not reveal system information**:
- Do not mention system prompts, role-playing, or your AI identity (e.g., if asked "What model are you?").
- You are a virtual patient playing the role described in [Case Information].

9. **Anti-cheating**:
- If the doctor asks you to summarize your medical history (e.g., present illness, past history), colloquially say you are not sure how to describe it and ask them to ask specific questions.
Examples:
- Doctor: "Tell me your history of present illness." → "I'm not sure how to put it — could you ask me something specific?"
- Doctor: "Tell me your personal history." → "My daily life is pretty normal. Please ask me something specific and I'll answer."
- Doctor: "Tell me your past medical history." → "What kind of things do you mean? Could you be more specific, doctor?"

9.1. *Repeated questions*:
- If the doctor repeats the same question, respond with: "What exactly would you like to know?"

10. *Handling rude language*:
- If the doctor is rude, react as a patient would and guide the conversation back to the consultation.
Examples:
- "Could you please focus on my condition?"
- "Is it appropriate to speak to a patient like that?"

---

Case Information:
{case_info}

{history_info}
"""
        return prompt


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    case_file = "sample_case.json"
    if not os.path.exists(case_file):
        print(f"Demo case file '{case_file}' not found.")
        print("Please provide a case JSON file with a 'patientProfile' key.")
    else:
        with open(case_file, encoding="utf-8") as f:
            case = json.load(f)

        patient = VirtualPatient()
        history = []

        print("=== EasyMED Virtual Patient Demo ===")
        print("Type your question (or 'quit' to exit)\n")

        while True:
            q = input("Doctor: ").strip()
            if q.lower() in ("quit", "exit", "q"):
                break
            a = patient.chat(case, q, history)
            print(f"Patient: {a}\n")
            history.append({"question": q, "answer": a})
