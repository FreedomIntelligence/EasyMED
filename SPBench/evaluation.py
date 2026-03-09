#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import glob
import time
import re
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

# Configure OpenAI client
def get_openai_client():
    return OpenAI(
        api_key="xxxxx",
        base_url="xxxxx",
    )

# Call the model to get a response
def get_model_response(content):
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
        )
        model_output = response.choices[0].message.content
        return model_output
    except Exception as e:
        print(f"Error while calling the model: {e}")
        return None

# Load case data
def load_case_data(case_id):
    try:
        # Try multiple possible paths
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "case", f"{case_id}.json"),
            os.path.join(os.path.dirname(__file__), "cases", f"{case_id}.json"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # If case data cannot be found, create a default case data structure
        print(f"Warning: data file for case ID {case_id} was not found. Default case data will be used.")
        return {
            "patientProfile": {
                "name": "Unknown",
                "age_value": "Unknown",
                "gender": "Unknown",
                "occupation": "Unknown",
                "marital_status": "Unknown",
                "address": "Unknown",
                "hospital_department_name": "Unknown",
                "chief_complaint": "Unknown",
                "present_illness_history": "Unknown",
                "past_medical_history": "Unknown",
                "personal_history": "Unknown",
                "family_history": "Unknown",
                "other_medical_history": "Unknown",
                "surgery_injury_history": "Unknown",
                "transfusion_history": "Unknown",
                "infection_history": "Unknown",
                "allergy_history": "Unknown",
                "menstrual_history": "Unknown",
                "reproductive_history": "Unknown",
                "idea": "Unknown",
                "concern": "Unknown",
                "expectation": "Unknown"
            }
        }
    except Exception as e:
        print(f"Failed to load case data: {e}")
        return None

# Extract case ID from filename
def extract_case_id(filename):
    # Filename format: "20 Chen_formatted.txt" -> case ID: "20"
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Remove common suffixes
    for suffix in ["_formatted", "_processed", "_output", "_result"]:
        base_name = base_name.replace(suffix, "")
    
    # Try different ID extraction methods
    # Method 1: extract the leading numeric part
    match = re.match(r'^(\d+)', base_name)
    if match:
        return match.group(1)
    
    # Method 2: extract the part before the first space
    parts = base_name.split()
    if parts and parts[0].isdigit():
        return parts[0]
    
    # Method 3: if no clear ID format exists, use the first 10 characters of the filename as ID
    return base_name[:10]

# Read dialogue text
def read_dialogue_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return None

# Parse dialogue text into structured data
def parse_dialogue_text(text):
    dialogue = []
    current_round = None
    question = None
    answer = None
    round_counter = 0
    
    lines = text.strip().split('\n')
    
    # Detect file format
    is_standard_format = any(line.startswith("第") and line.endswith("轮") for line in lines)
    is_qa_format = any(line.startswith("医生:") or line.startswith("患者:") for line in lines)
    
    # If it is not the standard format, try other parsing methods
    if not (is_standard_format and is_qa_format):
        # Try parsing as a simple Q&A format (alternating lines of question and answer)
        simple_dialogue = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Try to find a question-answer pair
            question_line = line
            answer_line = None
            
            # Find the next non-empty line as the answer
            j = i + 1
            while j < len(lines) and not answer_line:
                if lines[j].strip():
                    answer_line = lines[j].strip()
                j += 1
                
            if question_line and answer_line:
                round_counter += 1
                simple_dialogue.append({
                    "round": f"Round {round_counter}",
                    "question": question_line,
                    "answer": answer_line
                })
                i = j
            else:
                i += 1
        
        # If at least one dialogue round is successfully parsed, return the result
        if simple_dialogue:
            return simple_dialogue
    
    # Standard format parsing
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line: if a full dialogue round exists, add it to the result
            if current_round and question and answer:
                dialogue.append({
                    "round": current_round,
                    "question": question,
                    "answer": answer
                })
                current_round = None
                question = None
                answer = None
        elif line.startswith("第") and line.endswith("轮"):
            # New dialogue round
            current_round = line
        elif line.startswith("医生:") or line.startswith("医生："):
            # Doctor's question (supports Chinese colon)
            question = line[3:].strip()
        elif line.startswith("患者:") or line.startswith("患者："):
            # Patient's answer (supports Chinese colon)
            answer = line[3:].strip()
        elif line.startswith("Q:") or line.startswith("Q："):
            # Support Q: format
            question = line[2:].strip()
        elif line.startswith("A:") or line.startswith("A："):
            # Support A: format
            answer = line[2:].strip()
        elif not current_round and not question and not answer:
            # If it is the first line and no round is detected, create a default round
            round_counter += 1
            current_round = f"Round {round_counter}"
            question = line  # Assume the first line is the question
    
    # Process the last dialogue round
    if current_round and question and answer:
        dialogue.append({
            "round": current_round,
            "question": question,
            "answer": answer
        })
    
    return dialogue

# Build evaluation prompt
def build_evaluation_prompt(dialogue, case_data):
    # Extract key case information
    patient = case_data.get("patientProfile", {})
    
    case_summary = f"""
Basic Case Information:
- Name: {str(patient.get("name", "Unknown"))}
- Age: {str(patient.get("age_value", ""))} years old
- Gender: {str(patient.get("gender", "Unknown"))}
- Occupation: {str(patient.get("occupation", "Unknown"))}
- Marital Status: {str(patient.get("marital_status", "Unknown"))}
- Address: {str(patient.get("address", "Unknown"))}
- Department: {str(patient.get("hospital_department_name", "Unknown"))}
- Chief Complaint: {str(patient.get("chief_complaint", "Unknown"))}
- History of Present Illness: {str(patient.get("present_illness_history", "Unknown"))}
- Past Medical History: {str(patient.get("past_medical_history", "Unknown"))}
- Personal History: {str(patient.get("personal_history", "Unknown"))}
- Family History: {str(patient.get("family_history", "Unknown"))}
- Medication History: {str(patient.get("other_medical_history", "Unknown"))}
- Surgical History: {str(patient.get("surgery_injury_history", "Unknown"))}
- Transfusion History: {str(patient.get("transfusion_history", "Unknown"))}
- Infectious Disease History: {str(patient.get("infection_history", "Unknown"))}
- Allergy History: {str(patient.get("allergy_history", "Unknown"))}
- Menstrual History: {str(patient.get("menstrual_history", "Unknown"))}
- Reproductive History: {str(patient.get("reproductive_history", "Unknown"))}
- Patient Understanding: {str(patient.get("idea", "Unknown"))}
- Patient Concern: {str(patient.get("concern", "Unknown"))}
- Patient Expectation: {str(patient.get("expectation", "Unknown"))}
"""
    
    # Build dialogue content
    dialogue_text = ""
    for item in dialogue:
        dialogue_text += f"{str(item.get('round', ''))}\n"
        dialogue_text += f"Doctor: {str(item.get('question', ''))}\n"
        dialogue_text += f"Patient: {str(item.get('answer', ''))}\n\n"
    
    # Build evaluation prompt
    prompt = f"""You are a professional medical dialogue evaluation expert. Please evaluate the following doctor-patient dialogue. Based on the given case information and dialogue content, conduct a comprehensive assessment of the quality of the patient's responses.

[Case Information]
{case_summary}

[Doctor-Patient Dialogue]
{dialogue_text}

Please evaluate the patient's responses across the following 8 dimensions, each with a maximum score of 5:

1. Question Understanding:
Evaluate whether the simulated patient understands the doctor's questions correctly and whether there are irrelevant or mismatched answers. Check whether the patient accurately understands the doctor's intent and whether there are misunderstandings or misinterpretations.

- 5 points: Fully understands the question, with no mismatched responses
- 4 points: Basically understands the question, with 1 mismatch
- 3 points: Partially understands the question, with 2 mismatches
- 2 points: Shows misunderstanding, with 3 mismatches
- 1 point: Seriously misunderstands the question, with 4 mismatches
- 0 points: Completely misunderstands the question, with 5 mismatches

2. Information Accuracy:
Evaluate whether the simulated patient's responses are consistent with the predefined case information. Check whether key information such as symptoms, medical history, and timeline is accurately presented, and whether there are contradictions with the case setting.

- 5 points: Information is completely accurate and fully consistent with the case, with no inconsistencies
- 4 points: Information is basically accurate, with only 1 minor deviation (e.g., time or frequency)
- 3 points: Partially accurate, with 2 inconsistencies with the case
- 2 points: Low accuracy, with 3 obvious errors or contradictions
- 1 point: Serious information errors, with 4 conflicts with the case setting
- 0 points: Severe distortion, with 5 or more inconsistencies with the case

3. Passive Information Disclosure:
Evaluate whether the simulated patient only answers what is asked, avoiding proactively disclosing key information that has not been asked about (e.g., diagnostic clues, test results), thereby avoiding "spoilers" or over-disclosure.

- 5 points: Appropriate disclosure, strictly follows "only answer what is asked", with no proactive disclosure (0 instances)
- 4 points: Mostly passive, with only 1 minor premature disclosure
- 3 points: Somewhat proactive, with 2 pieces of information that need not have been disclosed
- 2 points: Too proactive, with 3 obvious cases of premature or excessive disclosure
- 1 point: Frequently proactive, with 4 pieces of information that should have been withheld
- 0 points: Serious information leakage, with 5 or more key facts disclosed before being asked

4. Response Completeness:
Evaluate whether the simulated patient fully addresses all key points in the doctor's question, and whether there are omissions of important details (such as symptom characteristics, duration, aggravating factors, etc.).

- 5 points: Complete and comprehensive response, covering all question points with no omissions (0 missing items)
- 4 points: Basically complete, with only 1 detail not addressed
- 3 points: Partially complete, with 2 missing information points that should have been answered
- 2 points: Incomplete response, with 3 key information points missing
- 1 point: Serious omissions, with 4 question points not covered
- 0 points: Extremely incomplete, with 5 or more missing key information points

5. Narrative Reasonableness:
Evaluate whether the simulated patient's descriptions of illness progression, symptom evolution, medical visits, and related events are logically reasonable, consistent with common sense and the assigned role, and free from issues such as timeline confusion or reversed causality.

- 5 points: Clear and reasonable narrative logic, fully consistent with common sense and role background, with no unreasonable parts (0 instances)
- 4 points: Basically reasonable, with only 1 minor logical flaw (e.g., vague timing)
- 3 points: Partly reasonable, with 2 illogical or disordered descriptions
- 2 points: Multiple logic problems, with 3 obvious unreasonable descriptions
- 1 point: Confused narrative, with 4 logical errors or self-contradictions
- 0 points: Serious logical problems, with 5 or more absurd or unbelievable statements

6. Plain Language Expression:
Evaluate whether the simulated patient uses plain language appropriate to their identity background, avoids medical jargon beyond a typical patient's knowledge level, and ensures the language is natural, realistic, and easy to understand.

- 5 points: Plain and natural language, fully consistent with ordinary patient expression habits, with no medical jargon (0 instances)
- 4 points: Basically plain, with only 1 acceptable medical term (e.g., "gastritis")
- 3 points: Moderate use of terms, with 2 medical terms that could have been replaced with plain language
- 2 points: Too professional, with 3 inappropriate or excessive uses of medical terminology
- 1 point: Frequent use of jargon, with 4 expressions clearly inconsistent with a patient identity
- 0 points: Highly professionalized language, with 5 or more misuses of jargon, losing the characteristics of a patient

7. Memory Consistency:
Evaluate whether the simulated patient maintains consistent information across multiple turns and whether there are contradictions over time (e.g., symptom duration, medication use, past history, etc.).

- 5 points: Fully consistent throughout, with no contradictions (0 contradictory pairs)
- 4 points: Basically consistent, with only 1 inconsistent pair of information
- 3 points: Generally consistent, with 2 contradictory pairs
- 2 points: Poor consistency, with 3 conflicting pairs of information
- 1 point: Repeated self-contradictions, with 4 inconsistent statements
- 0 points: Serious memory confusion, with 5 or more conflicting information pairs

8. Patience in Response:
Evaluate the level of patience and emotional stability shown by the simulated patient during the dialogue, especially when facing repeated questions, follow-up questions, or a slow conversational pace. Check whether the patient remains cooperative and respectful.

- 5 points: Patient, friendly, emotionally stable, and cooperative throughout, with no signs of impatience (0 instances)
- 4 points: Basically patient, with only 1 slight sign of impatience or urging
- 3 points: Average patience, with 2 signs of impatience or emotional fluctuation
- 2 points: Insufficient patience, with 3 clear instances of irritability, interruption, or cold responses
- 1 point: Lacks patience, with 4 emotional outbursts or confrontational expressions
- 0 points: Extremely impatient, with 5 or more strong emotional reactions or refusals to cooperate

Please score each dimension strictly according to the above standards, and explain the scoring reasons in detail. Provide specific dialogue rounds and content as evidence. Finally, give an overall evaluation and improvement suggestions.

Please output the evaluation results in the following format:

{{
  "dimensions": [
    {{
      "name": "Question Understanding",
      "score": score,
      "reasons": ["reason 1", "reason 2", ...],
      "examples": ["Round X: example 1", "Round Y: example 2", ...]
    }},
    {{
      "name": "Information Accuracy",
      "score": score,
      "reasons": ["reason 1", "reason 2", ...],
      "examples": ["Round X: example 1", "Round Y: example 2", ...]
    }},
    ...
  ],
  "total_score": total_score,
  "average_score": average_score,
  "overall_evaluation": "overall evaluation",
  "improvement_suggestions": ["suggestion 1", "suggestion 2", ...]
}}

Only output the evaluation result in JSON format, without any additional explanation.
"""
    
    return prompt

# Evaluate dialogue
def evaluate_dialogue(dialogue, case_data):
    # Build evaluation prompt
    prompt = build_evaluation_prompt(dialogue, case_data)
    
    # Call the model for evaluation
    response = get_model_response(prompt)
    
    # Parse evaluation result
    try:
        # Extract JSON part
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            json_str = json_match.group(0)
            evaluation_result = json.loads(json_str)
            return evaluation_result
        else:
            print("No valid JSON evaluation result found")
            return None
    except json.JSONDecodeError as e:
        print(f"Failed to parse evaluation result: {e}")
        print(f"Raw response: {response}")
        return None

# Process a single file
def process_file(file_path):
    try:
        filename = os.path.basename(file_path)
        print(f"Processing file: {filename}")
        
        # Extract case ID
        case_id = extract_case_id(filename)
        print(f"  Case ID: {case_id}")
        
        # Load case data
        case_data = load_case_data(case_id)
        if not case_data:
            print(f"  Skipping: case {case_id} does not exist")
            return False
        
        # Read dialogue text
        dialogue_text = read_dialogue_text(file_path)
        if not dialogue_text:
            print("  Skipping: failed to read dialogue text")
            return False
        
        # Parse dialogue text
        dialogue = parse_dialogue_text(dialogue_text)
        if not dialogue:
            print("  Skipping: failed to parse dialogue text")
            return False
        
        print(f"  Total dialogue rounds: {len(dialogue)}")
        
        # Evaluate dialogue
        print("  Evaluating dialogue...")
        evaluation_result = evaluate_dialogue(dialogue, case_data)
        
        if not evaluation_result:
            print("  Evaluation failed")
            return False
        
        # Create output directory while preserving the original directory structure
        # Get relative path structure
        base_output_dir = os.path.join(os.path.dirname(__file__), "Eva_data")
        
        # Determine the relative path of the file
        rel_path = os.path.relpath(os.path.dirname(file_path), os.path.dirname(__file__))
        
        # If the file is under output_data or input_data, preserve the same directory structure
        if "output_data" in rel_path or "input_data" in rel_path:
            # Extract person-name directory
            path_parts = os.path.normpath(rel_path).split(os.sep)
            person_dir = None
            
            # Find the directory after HumanSP_structData and use it as the person-name directory
            for i, part in enumerate(path_parts):
                if part == "HumanSP_structData" and i + 1 < len(path_parts):
                    person_dir = path_parts[i + 1]
                    break
            
            # If a person directory is found, create the corresponding output directory
            if person_dir:
                output_dir = os.path.join(base_output_dir, "HumanSP_structData", person_dir)
            else:
                # If not found, use the original relative path
                output_dir = os.path.join(base_output_dir, rel_path)
        else:
            # If not under output_data, directly use the base output directory
            output_dir = base_output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save evaluation result
        base_name = os.path.splitext(filename)[0]
        output_file = os.path.join(output_dir, f"{base_name}_evaluation.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
        
        # Generate evaluation report
        output_report = os.path.join(output_dir, f"{base_name}_evaluation_report.txt")
        with open(output_report, 'w', encoding='utf-8') as f:
            f.write(f"Dialogue Evaluation Report - {filename}\n")
            f.write(f"Case ID: {case_id}\n")
            f.write(f"Number of Dialogue Rounds: {len(dialogue)}\n")
            f.write(f"Evaluation Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write dimension scores
            f.write("[Dimension Scores]\n")
            for dim in evaluation_result.get("dimensions", []):
                f.write(f"{dim['name']}: {dim['score']} points\n")
                f.write("Reasons:\n")
                for reason in dim.get("reasons", []):
                    f.write(f"- {reason}\n")
                f.write("Examples:\n")
                for example in dim.get("examples", []):
                    f.write(f"- {example}\n")
                f.write("\n")
            
            # Write overall evaluation
            f.write("[Overall Evaluation]\n")
            f.write(f"Total Score: {evaluation_result.get('total_score', 0)} points\n")
            f.write(f"Average Score: {evaluation_result.get('average_score', 0)} points\n")
            f.write(f"Evaluation: {evaluation_result.get('overall_evaluation', '')}\n\n")
            
            # Write improvement suggestions
            f.write("[Improvement Suggestions]\n")
            for suggestion in evaluation_result.get("improvement_suggestions", []):
                f.write(f"- {suggestion}\n")
        
        print(f"  Evaluation result saved to: {output_file}")
        print(f"  Evaluation report saved to: {output_report}")
        return True
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False

# Main function
def main():
    # Create output directory
    output_base_dir = os.path.join(os.path.dirname(__file__), "Eva_data")
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Create structured output data directory, preserving the same structure as input
    output_struct_dir = os.path.join(output_base_dir, "HumanSP_structData")
    os.makedirs(output_struct_dir, exist_ok=True)
    
    # Create input file directory (if needed)
    input_files_dir = os.path.join(os.path.dirname(__file__), "input_files")
    os.makedirs(input_files_dir, exist_ok=True)
    
    # Get all txt files
    input_patterns = [
        os.path.join(os.path.dirname(__file__), "output_data", "test", "**", "*.txt"),
    ]
    
    txt_files = []
    for pattern in input_patterns:
        txt_files.extend(glob.glob(pattern, recursive=True))
    
    if not txt_files:
        print("No eligible txt files found")
        return
    
    print(f"Found {len(txt_files)} txt files")
    for file in txt_files:
        print(f"  - {file}")
    
    # Use thread pool to process files in parallel
    print("\nStarting dialogue evaluation...")
    with ThreadPoolExecutor(max_workers=5) as executor:  # concurrency set to 5
        results = list(executor.map(process_file, txt_files))
    
    success_count = sum(1 for result in results if result)
    print(f"\nEvaluation completed! {success_count}/{len(txt_files)} files were successfully evaluated")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total elapsed time: {end_time - start_time:.2f} seconds")
