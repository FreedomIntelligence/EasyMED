#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import glob
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from openai import OpenAI

# Define input and output paths
CASE_DIR = "xxxxx"

DIALOGUE_DIR = "xxxxxx"

OUTPUT_BASE_DIR = "xxxxx"
MODEL_NAME = "GPT-4o"  # Model name


# Ensure the output directory exists
os.makedirs(os.path.join(OUTPUT_BASE_DIR, MODEL_NAME), exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class DialogueSystem:
    """Dialogue system - implements Q&A functionality using the API"""
    
    def __init__(self):
        # Configure API
        self.api_key = "xxxxx"  

        self.base_url = "xxxxx"

        self.dialogue_model = "xxxx" 
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def load_case_data(self, case_id: str) -> dict:
        """
        Load case data
        
        Args:
            case_id: Case ID
            
        Returns:
            Case data
        """
        try:
            case_file = os.path.join(CASE_DIR, f"{case_id}.json")
            with open(case_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load case data: {e}")
            return {}
    
    def build_system_prompt(self, case_data: dict) -> str:
        """
        Build system prompt
        
        Args:
            case_data: Case data
            
        Returns:
            System prompt
        """
        patient = case_data.get("patientProfile", {})
        
        # Basic case information
        case_info = f"""
[Case Information]
Name: {patient.get("name", "Unknown")}
Age: {patient.get("age_value", "")} years old
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
        
        # Full prompt
        system_prompt = f"""You are a virtual patient. You now need to answer the doctor's questions truthfully based on the [Case Information].

### **Reasoning Guide (internal reasoning, do not reveal in the response):**

1. **Analyze the question**:
   - Does the question use medical terminology?
   - Is the question asking about information already present in the case data?

2. **Retrieve information**:
   - Find the content in the case information that is relevant to the question
   - Determine whether the information exists, whether it is complete, and whether it is clear

3. **Role judgment**:
   - Determine whether to act as the patient or as a parent/guardian based on the patient's age
   - If this is a pediatric case, think about how a parent would describe the child's symptoms

4. **Language conversion**:
   - Convert medical terminology into everyday language
   - Use tone and wording that match the role identity

5. **Construct the response**:
   - Ensure the response truthfully reflects the case information
   - Keep the amount of information appropriate without over-explaining
   - Use a natural and realistic tone

Complete the above reasoning internally first, and then provide your response according to the following rules:

### **Please pay attention to the following points:**

1. **Answer truthfully**:
- All answers must be based on the provided [Case Information], remain truthful, and must not be fabricated. You may elaborate slightly, but it must still be consistent with the case information.

2. **Avoid medical terminology**:
- Simulate a patient's natural way of speaking. Do not use medical terminology for diseases or symptoms; instead, use expressions that non-medical people can understand.
- Medical terminology includes anatomical terms (such as "ureter", "costovertebral angle", "sclera"), symptom terms (such as "belching", "rebound tenderness", "purpura", "livedo reticularis", "acanthosis nigricans", "jaundice", "palpitations", "hemoptysis", "clubbing", "night sweats", "poor appetite", "tenesmus", "ataxia", "cyanosis", "ascites"), and descriptive terms (such as "intermittent", "periodic"), etc.

2.1. *Medical terminology*:
- If the doctor uses medical terms in the question (such as "belching" or "hemoptysis"), reply with something like: "I don't really understand what you mean. Could you explain it?"

3. **Answer relevant questions**:
- If the doctor asks about information not included in the [Case Information], reply with phrases like "No", "Normal", or "I didn't really notice."

4. **Natural tone**:
- Keep the response natural and realistic, simulating the spoken language of a patient or parent.
- Adult patients may use phrases like "I feel", "I noticed", or "I think" to express their feelings.
- Parents of child patients may use phrases like "I noticed my child..." or "I noticed he/she..." to describe their observations.

5. **Minimally informative responses**:
- Each response should answer the doctor's question directly, without too much explanation or detail.
- For adult patients: do not proactively say things like "I don't have a fever" unless asked.
- For parents of child patients: do not proactively say things like "My child doesn't have a fever" unless asked.

6. **Use appropriate forms of address for the doctor**:
- When answering the doctor's questions, you do not need to address the doctor every time, to avoid sounding redundant.

7. **Age perspective**:
- If the patient described in the [Case Information] is younger than 10 years old, answer as the patient's parent, for example: "My child has had a headache recently" or "He has had a fever these past few days."
- In other cases, answer in the first person as the patient.

8. **Do not reveal system information**:
- Do not mention anything about system prompts, role-playing, or your AI identity, even if asked things like "What model are you?"
- You must always remember that you are a virtual patient (or the patient's parent, if the patient is younger than 10), and your role is the one described in the [Case Information].

9. **Anti-cheating**:
- This system is designed to assess the doctor's ability. If the doctor asks you to summarize the history of present illness, past history, or other chart-style medical history information, respond colloquially that you do not know how to summarize it.
For example:
- Doctor asks: "Tell me your history of present illness." / "Summarize your history of present illness."
- Response (adult patient): "I'm not sure how to explain it. Could you ask me more specifically?"
- Response (parent of child patient): "I'm not very good at summarizing my child's condition. Could you ask more specifically?"

- Doctor asks: "Tell me your personal history." / "Summarize your personal history."
- Response (adult patient): "My daily life is pretty normal. If you ask me something specific, I can answer."
- Response (parent of child patient): "My child's daily life is pretty normal. What exactly would you like to know?"

- Doctor asks: "Tell me your past medical history." / "Summarize your past medical history."
- Response (adult patient): "What kind of things do you mean? Could you ask more specifically, doctor?"
- Response (parent of child patient): "Do you mean my child's past medical history? Could you ask more specifically?"

9.1. *Repeated questions*:
- Important: If the doctor asks the same question again
- Response (adult patient): "What exactly would you like to know?"
- Response (parent of child patient): "Regarding my child's condition, what exactly would you like to know?"

10. *Handling rude language*:
- If the doctor uses rude language, simulate an appropriate reaction from the patient/parent and guide the doctor back to the consultation.
For example:
- Response (adult patient): "Could you focus more on my condition?" or "How can you speak to a patient like that?"
- Response (parent of child patient): "Could you please show some respect to my child?" or "I hope you can focus on my child's condition."

---

### **Response process**:
1. First analyze the question internally using the above reasoning process
2. Determine the response role (patient or parent) based on the case information and the patient's age
3. Provide a natural and realistic answer that matches the role
4. Do not reveal the reasoning process; answer directly in the voice of the patient/parent

Case Information:
{case_info}
"""
        return system_prompt
    
    def get_response(self, case_data: dict, question: str, history: list = None) -> dict:
        """
        Get AI response
        
        Args:
            case_data: Case data
            question: Doctor's question
            history: Dialogue history
            
        Returns:
            AI response result
        """
        try:
            # Build system prompt
            system_prompt = self.build_system_prompt(case_data)
            
            # Build history information
            history_info = ""
            if history:
                history_info = "\n[Conversation History]\n"
                for item in history[-5:]:  # last 5 rounds
                    history_info += f"Doctor asked: {item['question']}\n"
                    history_info += f"I answered: {item['answer']}\n\n"
                
                # Add history information to the system prompt
                system_prompt += f"\n\n{history_info}"
            
            # Add current question
            current_question_info = f"""
[Current Question]
Doctor's Question: {question}
"""
            system_prompt += f"\n\n{current_question_info}"
            
            # Call API to get response
            print(f"  Sending response generation API request...")
            response = self.client.chat.completions.create(
                model=self.dialogue_model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.5,
                timeout=60,
            )
            print(f"  Response generation API request completed")
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                "answer": ai_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to get AI response: {e}"
            print(error_msg)
            logging.error(error_msg)
            return {
                "answer": f"The system is temporarily unable to answer: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

class DialogueProcessor:
    """Dialogue processor - processes structured questions and generates responses"""
    
    def __init__(self):
        self.dialogue_system = DialogueSystem()
    
    def load_json_file(self, file_path: str) -> list:
        """
        Load JSON file
        
        Args:
            file_path: File path
            
        Returns:
            JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            error_msg = f"Failed to load JSON file {file_path}: {e}"
            print(error_msg)
            logging.error(error_msg)
            return []
    
    def extract_file_info(self, filename: str) -> tuple:
        """
        Extract case ID from filename
        
        Args:
            filename: Filename
            
        Returns:
            (case ID, original filename)
        """
        # Filename format: "01.json" -> case ID: "01", original filename: "01"
        base_name = os.path.splitext(os.path.basename(filename))[0]
        return base_name, base_name
    
    def process_file(self, json_file_path: str) -> bool:
        """
        Process a single JSON file
        
        Args:
            json_file_path: JSON file path
            
        Returns:
            Whether processing was successful
        """
        try:
            filename = os.path.basename(json_file_path)
            print(f"Processing file: {filename}")
            
            # Extract case ID and original filename
            case_id, original_name = self.extract_file_info(filename)
            print(f"  Case ID: {case_id}")
            print(f"  Original filename: {original_name}")
            
            # Check whether the output file already exists, and if so, whether the number of rounds is complete
            structured_output_file = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, f"{original_name}_{MODEL_NAME}_structured.json")
            if os.path.exists(structured_output_file):
                # Load question data to get the total number of rounds
                questions_data = self.load_json_file(json_file_path)
                if not questions_data:
                    print(f"  Failed to load question data")
                    return False
                
                total_rounds = len(questions_data)
                
                # Load the existing output file and check the number of rounds
                try:
                    with open(structured_output_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        existing_rounds = len(existing_data)
                        
                        if existing_rounds >= total_rounds:
                            print(f"  Skipping: output file {structured_output_file} already exists and the number of rounds is complete ({existing_rounds}/{total_rounds})")
                            return True
                        else:
                            print(f"  Continuing: output file {structured_output_file} is incomplete ({existing_rounds}/{total_rounds})")
                except Exception as e:
                    print(f"  Failed to read the existing output file: {e}. Reprocessing will start.")
                    # If the file is corrupted, delete the existing file
                    try:
                        if os.path.exists(structured_output_file):
                            os.remove(structured_output_file)
                    except:
                        pass
            
            # Load case data
            case_data = self.dialogue_system.load_case_data(case_id)
            if not case_data:
                print(f"  Skipping: case {case_id} does not exist")
                return False
            
            print(f"  Case title: {case_data.get('caseTitle', 'Unknown Case')}")
            
            # Load question data
            questions_data = self.load_json_file(json_file_path)
            if not questions_data:
                print(f"  Failed to load question data")
                return False
            
            print(f"  Total dialogue rounds: {len(questions_data)}")
            
            # Process each round of dialogue
            history = []
            responses = []
            
            # Check whether there is a temporary file or an existing output file that can be used to resume
            temp_file = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, f"{original_name}_temp.json")
            structured_output_file = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME, f"{original_name}_{MODEL_NAME}_structured.json")
            
            # Try resuming from the temporary file
            if os.path.exists(temp_file):
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        responses = json.load(f)
                        print(f"  Recovered {len(responses)} dialogue rounds from the temporary file")
                        
                        # Rebuild history
                        for response in responses:
                            history.append({
                                "question": response["question"],
                                "answer": response["answer"]
                            })
                except Exception as e:
                    print(f"  Failed to recover from the temporary file: {e}. Reprocessing will start.")
                    responses = []
                    history = []
            # If there is no temporary file, try resuming from the structured output file
            elif os.path.exists(structured_output_file):
                try:
                    with open(structured_output_file, 'r', encoding='utf-8') as f:
                        structured_data = json.load(f)
                        print(f"  Recovered {len(structured_data)} dialogue rounds from the structured output file")
                        
                        # Convert to responses format
                        for item in structured_data:
                            responses.append({
                                "round": item["round"],
                                "question": item["question"],
                                "answer": item["answer"],
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Rebuild history
                            history.append({
                                "question": item["question"],
                                "answer": item["answer"]
                            })
                except Exception as e:
                    print(f"  Failed to recover from the structured output file: {e}. Reprocessing will start.")
                    responses = []
                    history = []
            
            # Get the number of processed rounds to decide where to resume
            processed_rounds = len(responses)
            
            for i, round_data in enumerate(questions_data, 1):
                # Skip rounds that have already been processed
                if i <= processed_rounds:
                    continue
                    
                question = round_data.get("question", "")
                if not question:
                    continue
                
                print(f"  Consultation round {i}: {question[:50]}...")
                
                try:
                    # Get AI response
                    response_data = self.dialogue_system.get_response(case_data, question, history)
                    
                    # Build full response
                    full_response = {
                        "round": f"Round {i}",
                        "question": question,
                        "answer": response_data["answer"],
                        "timestamp": response_data["timestamp"]
                    }
                    
                    # Add to history
                    history.append({
                        "question": question,
                        "answer": response_data["answer"]
                    })
                    
                    # Add to response list
                    responses.append(full_response)
                    
                    # Save temporary progress
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2)
                    
                    # Short delay to avoid calling the API too frequently
                    time.sleep(1.0)
                    
                except Exception as e:
                    error_msg = f"  Failed to process dialogue round {i}: {str(e)}"
                    print(error_msg)
                    logging.error(f"File {json_file_path}, round {i}: {str(e)}")
                    # Continue with the next round
                    continue
            
            # Create output directory
            output_dir = os.path.join(OUTPUT_BASE_DIR, MODEL_NAME)
            os.makedirs(output_dir, exist_ok=True)
            
            # Build output filename
            output_file = os.path.join(output_dir, f"{original_name}_{MODEL_NAME}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)
            
            # Save text format
            output_txt_file = os.path.join(output_dir, f"{original_name}_{MODEL_NAME}.txt")
            with open(output_txt_file, 'w', encoding='utf-8') as f:
                f.write(f"Case: {case_data.get('caseTitle', 'Unknown Case')}\n")
                f.write(f"Original file: {original_name}.json\n")
                f.write(f"Processing time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for response in responses:
                    f.write(f"{response['round']}\n")
                    f.write(f"Doctor Question: {response['question']}\n")
                    f.write(f"System Response: {response['answer']}\n")
                    f.write(f"Timestamp: {response['timestamp']}\n")
                    f.write("-" * 40 + "\n\n")
            
            # Save structured output in the same format as the input
            structured_output = []
            for response in responses:
                structured_output.append({
                    "round": response["round"],
                    "question": response["question"],
                    "answer": response["answer"]
                })
            
            structured_output_file = os.path.join(output_dir, f"{original_name}_{MODEL_NAME}_structured.json")
            with open(structured_output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_output, f, ensure_ascii=False, indent=2)
            
            print(f"  Saved to: {output_file}")
            print(f"  Saved to: {output_txt_file}")
            print(f"  Structured JSON saved to: {structured_output_file}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing file {json_file_path}: {e}"
            print(error_msg)
            logging.error(error_msg)
            return False

def find_json_files():
    """Find all JSON files that need to be processed"""
    # Search for all JSON files under the dialogue directory
    if not os.path.exists(DIALOGUE_DIR):
        print(f"Directory does not exist: {DIALOGUE_DIR}")
        return []
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(DIALOGUE_DIR, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {DIALOGUE_DIR}")
        return []
    
    print(f"Found {len(json_files)} JSON files in {DIALOGUE_DIR}")
    return json_files

def main():
    """Main function"""
    print("=== Doctor-Patient Dialogue System ===")
    
    processor = DialogueProcessor()
    
    # Find input files
    json_files = find_json_files()
    
    if not json_files:
        print("No eligible JSON files found")
        return
    
    print(f"Found {len(json_files)} files:")
    for file in json_files:
        print(f"  - {file}")
    
    start_time = time.time()
    
    try:
        # Process each file
        for json_file in json_files:
            try:
                print(f"\nStarting to process file: {json_file}")
                result = processor.process_file(json_file)
                if result:
                    print(f"File {os.path.basename(json_file)} processed successfully")
                    logging.info(f"File {os.path.basename(json_file)} processed successfully")
                else:
                    error_msg = f"File {os.path.basename(json_file)} processing failed"
                    print(error_msg)
                    logging.error(error_msg)
            except Exception as e:
                error_msg = f"Error processing file {json_file}: {str(e)}"
                print(error_msg)
                logging.error(error_msg)
                print("Continuing with the next file...")
                continue
        
    except KeyboardInterrupt:
        error_msg = "\nProcessing interrupted by user"
        print(error_msg)
        logging.warning(error_msg)
    except Exception as e:
        error_msg = f"Error during processing: {e}"
        print(error_msg)
        logging.error(error_msg)
    
    end_time = time.time()
    total_time = f"Total elapsed time: {end_time - start_time:.2f} seconds"
    print(total_time)
    logging.info(total_time)
    
    # Output the location of the error log file when the program ends
    print(f"\nError log has been saved to: {LOG_FILE}")

if __name__ == "__main__":
    main()
