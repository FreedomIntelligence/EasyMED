"""
SPBench - Create Conversation

Generates virtual patient responses for each question in a benchmark
dialogue script, using the EasyMED VirtualPatient module.

Input
-----
SPBench_case/<id>.json     – patient case profile (patientProfile, etc.)
SPBench_taking/<id>.json   – ordered list of doctor questions
    [{"round": "第1轮", "question": "..."}, ...]

Output (saved under output/<MODEL_NAME>/<id>/)
------
<id>_<MODEL>.json              – full response records
<id>_<MODEL>.txt               – human-readable dialogue
<id>_<MODEL>_structured.json   – clean [round, question, answer] list

Configuration
-------------
Set environment variables before running:

    export EASYMED_API_KEY=sk-...
    export EASYMED_BASE_URL=https://api.openai.com/v1   # optional
    export EASYMED_MODEL=gpt-4o                         # optional

Then edit the path constants below (CASE_DIR, DIALOGUE_DIR, OUTPUT_BASE_DIR)
to point to your local directories.

Usage
-----
    python create_conversation.py
"""

import os
import sys
import json
import glob
import time
import logging
from datetime import datetime

# Allow importing EasyMED from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from EasyMED.consultation import VirtualPatient

# ---------------------------------------------------------------------------
# >>>  EDIT THESE PATHS  <<<
# ---------------------------------------------------------------------------
CASE_DIR      = os.path.join(os.path.dirname(__file__), "SPBench_case")
DIALOGUE_DIR  = os.path.join(os.path.dirname(__file__), "SPBench_taking")
OUTPUT_BASE_DIR = os.path.join(os.path.dirname(__file__), "output")
MODEL_NAME    = os.environ.get("EASYMED_MODEL", "gpt-4o")
# ---------------------------------------------------------------------------

os.makedirs(os.path.join(OUTPUT_BASE_DIR, MODEL_NAME), exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class DialogueProcessor:
    """
    Drives the per-case dialogue generation loop.
    Supports resuming interrupted runs via a temporary checkpoint file.
    """

    def __init__(self):
        self.patient = VirtualPatient()

    # ------------------------------------------------------------------

    def _load_json(self, path: str):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logging.error("Failed to load %s: %s", path, exc)
            return None

    def _case_id_from_filename(self, filename: str) -> str:
        return os.path.splitext(os.path.basename(filename))[0]

    # ------------------------------------------------------------------

    def process_file(self, dialogue_json_path: str) -> bool:
        """
        Process one dialogue script file for a given case.

        Args:
            dialogue_json_path: Path to the SPBench_taking/<id>.json file.

        Returns:
            True on success, False on failure.
        """
        filename  = os.path.basename(dialogue_json_path)
        case_id   = self._case_id_from_filename(filename)
        print(f"\n[Processing] {filename}  (case_id={case_id})")

        out_dir = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME)
        os.makedirs(out_dir, exist_ok=True)

        structured_out = os.path.join(out_dir, f"{case_id}_{MODEL_NAME}_structured.json")
        temp_file      = os.path.join(out_dir, f"{case_id}_temp.json")

        # Load question list
        questions = self._load_json(dialogue_json_path)
        if not questions:
            print(f"  [Skip] Failed to load questions from {filename}")
            return False

        total_rounds = len(questions)

        # Check if already fully completed
        if os.path.exists(structured_out):
            try:
                existing = self._load_json(structured_out)
                if existing and len(existing) >= total_rounds:
                    print(f"  [Skip] Already complete ({len(existing)}/{total_rounds} rounds)")
                    return True
            except Exception:
                pass

        # Load case profile
        case_file = os.path.join(CASE_DIR, f"{case_id}.json")
        case_data = self._load_json(case_file)
        if not case_data:
            print(f"  [Skip] Case file not found: {case_file}")
            return False

        print(f"  Case: {case_data.get('caseTitle', 'Unknown')}")
        print(f"  Total rounds: {total_rounds}")

        # Resume from checkpoint if available
        responses: list = []
        history:   list = []

        if os.path.exists(temp_file):
            saved = self._load_json(temp_file)
            if saved:
                responses = saved
                history   = [{"question": r["question"], "answer": r["answer"]} for r in saved]
                print(f"  Resumed from checkpoint: {len(responses)}/{total_rounds} rounds done")

        processed = len(responses)

        # Generate responses
        for i, round_data in enumerate(questions, start=1):
            if i <= processed:
                continue

            question = round_data.get("question", "").strip()
            if not question:
                continue

            print(f"  Round {i}/{total_rounds}: {question[:60]}...")

            try:
                answer = self.patient.chat(case_data, question, history)

                record = {
                    "round":     f"第{i}轮",
                    "question":  question,
                    "answer":    answer,
                    "timestamp": datetime.now().isoformat(),
                }
                responses.append(record)
                history.append({"question": question, "answer": answer})

                # Save checkpoint
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(responses, f, ensure_ascii=False, indent=2)

                time.sleep(0.5)

            except Exception as exc:
                msg = f"Round {i} failed: {exc}"
                print(f"  [Error] {msg}")
                logging.error("File %s, %s", filename, msg)

        if not responses:
            print("  [Error] No responses generated")
            return False

        # Save full JSON
        full_out = os.path.join(out_dir, f"{case_id}_{MODEL_NAME}.json")
        with open(full_out, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)

        # Save human-readable TXT
        txt_out = os.path.join(out_dir, f"{case_id}_{MODEL_NAME}.txt")
        with open(txt_out, "w", encoding="utf-8") as f:
            f.write(f"病例：{case_data.get('caseTitle', 'Unknown')}\n")
            f.write(f"文件：{case_id}.json\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            for r in responses:
                f.write(f"{r['round']}\n")
                f.write(f"医生: {r['question']}\n")
                f.write(f"患者: {r['answer']}\n")
                f.write("-" * 40 + "\n\n")

        # Save structured JSON (clean, without timestamps)
        structured = [
            {"round": r["round"], "question": r["question"], "answer": r["answer"]}
            for r in responses
        ]
        with open(structured_out, "w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)

        # Remove checkpoint
        if os.path.exists(temp_file):
            os.remove(temp_file)

        print(f"  Saved → {full_out}")
        print(f"  Saved → {txt_out}")
        print(f"  Saved → {structured_out}")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== SPBench — Create Conversation ===")
    print(f"Model : {MODEL_NAME}")
    print(f"Cases : {CASE_DIR}")
    print(f"Dialogues : {DIALOGUE_DIR}")
    print(f"Output    : {OUTPUT_BASE_DIR}\n")

    if not os.path.exists(DIALOGUE_DIR):
        print(f"[Error] Dialogue directory not found: {DIALOGUE_DIR}")
        return

    json_files = sorted(glob.glob(os.path.join(DIALOGUE_DIR, "*.json")))
    if not json_files:
        print(f"[Error] No JSON files found in {DIALOGUE_DIR}")
        return

    print(f"Found {len(json_files)} dialogue files")

    processor  = DialogueProcessor()
    success, failed = 0, 0
    t0 = time.time()

    for path in json_files:
        try:
            ok = processor.process_file(path)
            if ok:
                success += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as exc:
            logging.error("Unhandled error for %s: %s", path, exc)
            print(f"[Error] {path}: {exc}")
            failed += 1

    elapsed = time.time() - t0
    print(f"\n=== Done: {success} success, {failed} failed, {elapsed:.1f}s ===")
    print(f"Error log: {LOG_FILE}")


if __name__ == "__main__":
    main()
