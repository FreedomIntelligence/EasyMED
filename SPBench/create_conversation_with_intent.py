"""
SPBench - Create Conversation with Intent Annotation

Same as create_conversation.py, but each doctor question is also passed
through the IntentRecognizer before the patient responds.  The intent
label is stored in the output JSON alongside the question/answer.

Output format (structured JSON)
--------------------------------
[
  {
    "round":                "第1轮",
    "question":             "您哪里不舒服？",
    "answer":               "我肚子疼...",
    "intentClassification": "主要症状"
  },
  ...
]

Configuration
-------------
Same environment variables as create_conversation.py:

    export EASYMED_API_KEY=sk-...
    export EASYMED_BASE_URL=...   # optional
    export EASYMED_MODEL=...      # optional

You can use different models for dialogue generation vs intent recognition
by passing them explicitly:

    system = DialogueSystem(
        dialogue_model="gpt-4o",
        intent_model="gpt-4o-mini",
    )

Usage
-----
    python create_conversation_with_intent.py
"""

import os
import sys
import json
import glob
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from EasyMED.consultation      import VirtualPatient
from EasyMED.intent_recognition import IntentRecognizer

# ---------------------------------------------------------------------------
# >>>  EDIT THESE PATHS  <<<
# ---------------------------------------------------------------------------
CASE_DIR        = os.path.join(os.path.dirname(__file__), "SPBench_case")
DIALOGUE_DIR    = os.path.join(os.path.dirname(__file__), "SPBench_taking")
OUTPUT_BASE_DIR = os.path.join(os.path.dirname(__file__), "output_with_intent")
MODEL_NAME      = os.environ.get("EASYMED_MODEL", "gpt-4o")
# ---------------------------------------------------------------------------

os.makedirs(os.path.join(OUTPUT_BASE_DIR, MODEL_NAME), exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DialogueSystem:
    """
    Wraps VirtualPatient + IntentRecognizer.

    You can optionally use a lighter/faster model for intent recognition
    while using a more capable model for generating patient responses.
    """

    def __init__(
        self,
        dialogue_model: str | None = None,
        intent_model:   str | None = None,
    ):
        api_key  = os.environ.get("EASYMED_API_KEY")
        base_url = os.environ.get("EASYMED_BASE_URL")
        default  = os.environ.get("EASYMED_MODEL", "gpt-4o")

        self.patient    = VirtualPatient(
            api_key=api_key,
            base_url=base_url,
            model=dialogue_model or default,
        )
        self.recognizer = IntentRecognizer(
            api_key=api_key,
            base_url=base_url,
            model=intent_model or default,
        )

    def get_response(
        self,
        case_data: dict,
        question:  str,
        history:   list,
    ) -> dict:
        """
        Recognise intent, then generate patient answer.

        Returns:
            {"answer": str, "intentClassification": str, "timestamp": str}
        """
        intent = self.recognizer.recognize(question, history)
        answer = self.patient.chat(case_data, question, history)
        return {
            "answer":               answer,
            "intentClassification": intent,
            "timestamp":            datetime.now().isoformat(),
        }


class DialogueProcessor:
    def __init__(self):
        self.system = DialogueSystem()

    def _load_json(self, path: str):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logging.error("Failed to load %s: %s", path, exc)
            return None

    def _case_id(self, filename: str) -> str:
        return os.path.splitext(os.path.basename(filename))[0]

    def process_file(self, dialogue_json_path: str) -> bool:
        filename = os.path.basename(dialogue_json_path)
        case_id  = self._case_id(filename)
        print(f"\n[Processing] {filename}  (case_id={case_id})")

        out_dir = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME)
        os.makedirs(out_dir, exist_ok=True)

        questions = self._load_json(dialogue_json_path)
        if not questions:
            print("  [Skip] Failed to load questions")
            return False

        case_file = os.path.join(CASE_DIR, f"{case_id}.json")
        case_data = self._load_json(case_file)
        if not case_data:
            print(f"  [Skip] Case file not found: {case_file}")
            return False

        print(f"  Case  : {case_data.get('caseTitle', 'Unknown')}")
        print(f"  Rounds: {len(questions)}")

        history:   list = []
        responses: list = []

        for i, round_data in enumerate(questions, start=1):
            question = round_data.get("question", "").strip()
            if not question:
                continue

            print(f"  Round {i}: {question[:55]}...")

            try:
                resp = self.system.get_response(case_data, question, history)
                print(f"    Intent: {resp['intentClassification']}")

                record = {
                    "round":                f"第{i}轮",
                    "question":             question,
                    "answer":               resp["answer"],
                    "intentClassification": resp["intentClassification"],
                    "timestamp":            resp["timestamp"],
                }
                responses.append(record)
                history.append({"question": question, "answer": resp["answer"]})
                time.sleep(0.5)

            except Exception as exc:
                msg = f"Round {i} failed: {exc}"
                print(f"  [Error] {msg}")
                logging.error("File %s, %s", filename, msg)

        if not responses:
            print("  [Error] No responses generated")
            return False

        # Save full JSON
        out_file = os.path.join(out_dir, f"{case_id}_{MODEL_NAME}_with_intent.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        print(f"  Saved → {out_file}")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== SPBench — Create Conversation with Intent ===")
    print(f"Model : {MODEL_NAME}")
    print(f"Output: {OUTPUT_BASE_DIR}\n")

    if not os.path.exists(DIALOGUE_DIR):
        print(f"[Error] Dialogue directory not found: {DIALOGUE_DIR}")
        return

    json_files = sorted(glob.glob(os.path.join(DIALOGUE_DIR, "*.json")))
    if not json_files:
        print(f"[Error] No JSON files found in {DIALOGUE_DIR}")
        return

    print(f"Found {len(json_files)} dialogue files")
    processor = DialogueProcessor()
    success, failed = 0, 0
    t0 = time.time()

    for path in json_files:
        try:
            ok = processor.process_file(path)
            success += ok
            failed  += not ok
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as exc:
            logging.error("Unhandled error %s: %s", path, exc)
            failed += 1

    elapsed = time.time() - t0
    print(f"\n=== Done: {success} success, {failed} failed, {elapsed:.1f}s ===")
    print(f"Error log: {LOG_FILE}")


if __name__ == "__main__":
    main()
