"""
EasyMED - Medical Intent Recognition Module

Classifies a doctor's question during a consultation into one or more
standardized medical inquiry intent categories (32 categories).

Intent categories cover the full spectrum of clinical history-taking:
chief complaint, onset time, symptom characteristics, past medical history,
family history, social history, ICE (ideas/concerns/expectations), and more.

Usage:
    from intent_recognition import IntentRecognizer

    recognizer = IntentRecognizer()   # reads config from env vars

    intent = recognizer.recognize(
        question="Do you have any fever?",
        history=[
            {"question": "Where does it hurt?", "answer": "My stomach hurts."},
        ],
    )
    print(intent)  # e.g. "Associated Symptoms"
"""

import os
from openai import OpenAI
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Intent category reference  (32 categories)
# ---------------------------------------------------------------------------

INTENT_CATEGORIES = [
    "Personal Information",
    "Chief Complaint",
    "Onset Time",
    "Triggering Factors",
    "Symptom Location",
    "Symptom Characteristics",
    "Duration and Frequency",
    "Aggravating / Relieving Factors",
    "Associated Symptoms",
    "Disease Progression",
    "Prior Diagnosis and Treatment",
    "General Condition",
    "Bowel and Bladder Function",
    "Weight Change",
    "Chronic Disease History",
    "Infectious Disease History",
    "Surgical and Trauma History",
    "Transfusion History",
    "Allergy History",
    "Vaccination History",
    "Medication History",
    "Travel History",
    "Lifestyle Habits",
    "Occupational History",
    "Sexual History",
    "Marital and Reproductive History",
    "Family History",
    "Menstrual History",
    "Patient Understanding",
    "Patient Concerns",
    "Patient Expectations",
    "Small Talk",
]


class IntentRecognizer:
    """
    Classifies doctor questions into standardized medical inquiry intent categories.

    Each question is assigned 1–3 intent labels from the 32-category taxonomy.
    Output is a comma-separated string, e.g. "Symptom Location, Aggravating / Relieving Factors".

    API configuration (same env vars as VirtualPatient):
        EASYMED_API_KEY   – required
        EASYMED_BASE_URL  – optional
        EASYMED_MODEL     – optional, defaults to "gpt-4o"
    """

    _SYSTEM_PROMPT = """You are a professional medical intent recognition assistant. Based on the rules below and your medical knowledge, classify the input question into one or more intent categories and return only the category name(s). No explanation, no prefix, no suffix. Example output: Personal Information

Important: Assign at most 3 categories per question. Output format: Category1, Category2, Category3

### Examples:
- Input: "How old are you?"
  Output: Personal Information
- Input: "Where does it hurt? Does anything make it worse? Have you noticed any weight change?"
  Output: Symptom Location, Aggravating / Relieving Factors, Weight Change
- Input: "Nice weather today, isn't it?"
  Output: Small Talk

---

### Classification rules:

Classify the doctor's question into one of the following 32 intent categories based on the content and conversation context:

Personal Information: Asking about the patient's general demographics (e.g., "What is your name?" / "How old are you?")
Chief Complaint: Asking about the main symptom (e.g., "What brings you in today?" / "What is bothering you?")
Onset Time: Asking when the main symptom started (e.g., "When did this start?" / "How long have you had this?")
Triggering Factors: Asking about the cause or precipitant (e.g., "What do you think triggered this?" / "Did anything cause it?")
Symptom Location: Asking about where the symptom is (e.g., "Where does it hurt?" / "Where exactly do you feel uncomfortable?")
Symptom Characteristics: Asking about the nature of the symptom (e.g., "Is it a sharp pain or a dull ache?" / "What does it feel like?")
Duration and Frequency: Asking how long the symptom lasts or how often it occurs (e.g., "How long does it last?" / "How often does it happen?")
Aggravating / Relieving Factors: Asking what makes it better or worse (e.g., "Does anything make it worse?" / "What gives you relief?")
Associated Symptoms: Asking about accompanying symptoms (e.g., "Do you have any other symptoms?" / "Anything else bothering you?")
Disease Progression: Asking how the condition has changed over time (e.g., "Is it getting better or worse?" / "Has it changed at all?")
Prior Diagnosis and Treatment: Asking about prior medical visits, tests, or treatments (e.g., "Have you seen another doctor?" / "Have you taken any medications for this?" / "What were the results?")
General Condition: Asking about general well-being during the illness (e.g., "How is your sleep?" / "How is your appetite?")
Bowel and Bladder Function: Asking about bowel or urinary changes (e.g., "Are your bowel movements normal?" / "Any changes in urination?")
Weight Change: Asking about changes in weight or energy (e.g., "Have you lost or gained any weight recently?" / "How is your energy level?")
Chronic Disease History: Asking about chronic illnesses (e.g., "Do you have high blood pressure?" / "Any history of diabetes?")
Infectious Disease History: Asking about infectious diseases (e.g., "Any history of hepatitis?" / "Have you ever had tuberculosis?")
Surgical and Trauma History: Asking about past surgeries or injuries (e.g., "Have you had any surgeries?" / "Any significant injuries?")
Transfusion History: Asking about blood transfusions (e.g., "Have you ever received a blood transfusion?")
Allergy History: Asking about drug or food allergies (e.g., "Are you allergic to any medications?" / "Any food allergies?")
Vaccination History: Asking about vaccinations (e.g., "Are you up to date on your vaccinations?" / "Have you received any recent vaccines?")
Medication History: Asking about current regular or long-term medications, regardless of condition (e.g., "Are you taking any medications regularly?" / "Any other drugs besides what you mentioned?")
Travel History: Asking about residence or recent travel to endemic areas (e.g., "Where do you live?" / "Have you traveled to any disease-endemic areas recently?")
Lifestyle Habits: Asking about personal habits such as smoking or alcohol (e.g., "Do you smoke or drink?" / "How are your lifestyle habits?")
Occupational History: Asking about occupation or working conditions (e.g., "What do you do for work?" / "What is your work environment like?")
Sexual History: Asking about high-risk sexual behavior (e.g., "Any history of high-risk sexual activity?")
Marital and Reproductive History: Asking about marriage and children (e.g., "Are you married?" / "How many children do you have?")
Family History: Asking about family medical history (e.g., "Does anyone in your family have a similar condition?" / "Any hereditary diseases in your family?")
Menstrual History: Asking about menstrual cycle (e.g., "When was your first period?" / "Are your periods regular?" / "Any pain during periods?" / "When was your last period?")
Patient Understanding: Asking what the patient thinks is causing the problem (e.g., "What do you think might be causing this?")
Patient Concerns: Asking what the patient is most worried about (e.g., "What concerns you most about this?")
Patient Expectations: Asking what the patient hopes to get from the visit (e.g., "What would you like us to help you with today?")
Small Talk: Greetings, small talk, health education questions, or anything unclear or unrelated to clinical history-taking (e.g., "Nice weather today" / "What is the HPV vaccine for?")

---

### Special notes:
- **Use conversation history**: When the input is ambiguous or context-dependent, use the conversation history to determine intent. Examples:
  - If the patient previously mentioned "stomach pain" and then says "it's been going on for a while," classify as "Duration and Frequency."
  - If the patient mentioned "dizziness" and then asks "could it be from anaemia?", classify as "Triggering Factors."
- If the input is too vague to classify, default to "Small Talk."
- If the input is a statement rather than a question but contains clear medical information, classify by context.

---

### More examples:
- Input: "Have you noticed any other unusual changes?"
  Intent: Associated Symptoms
- Input: "What medications are you currently taking regularly?"
  Intent: Medication History
- Input: "Nice weather today!"
  Intent: Small Talk"""

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

    def recognize(
        self,
        question: str,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Classify the doctor's question into intent category/categories.

        Args:
            question: The doctor's question text.
            history:  Previous turns as [{"question": str, "answer": str}, ...].
                      Up to the last 5 turns are used for context.

        Returns:
            A comma-separated string of intent labels,
            e.g. "Symptom Location, Aggravating / Relieving Factors".
            Returns "Other" on failure.
        """
        history_block = ""
        if history:
            history_block = "\n**Conversation History:**\n"
            for item in (history or [])[-5:]:
                history_block += f"Doctor: {item['question']}\n"
                history_block += f"Patient: {item['answer']}\n\n"

        full_prompt = (
            f"{self._SYSTEM_PROMPT}\n\n"
            f"{history_block}\n"
            f'**Input**: "{question}"\n'
            f"**Intent**:"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1,
            )
            result = response.choices[0].message.content.strip()

            # Strip any accidental colon-prefix the model might produce
            if ":" in result:
                result = result.split(":")[-1].strip()

            return result

        except Exception as exc:
            print(f"[IntentRecognizer] Error: {exc}")
            return "Other"


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    recognizer = IntentRecognizer()
    test_cases = [
        ("Where does it hurt?", []),
        ("How long has this been going on?",
         [{"question": "Where does it hurt?", "answer": "My stomach hurts."}]),
        ("Do you have any nausea or vomiting?", []),
        ("Does anyone in your family have a similar condition?", []),
        ("Nice weather today!", []),
    ]

    print("=== Intent Recognition Demo ===\n")
    for q, h in test_cases:
        intent = recognizer.recognize(q, h)
        print(f"Q: {q}")
        print(f"Intent: {intent}\n")
