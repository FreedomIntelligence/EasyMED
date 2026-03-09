#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import glob
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from openai import OpenAI

class DialogueSystem:
    
    def __init__(self):
        # API configuration
        self.api_key = "xxx"  
        self.base_url = "xxx"
        self.model = "xxx"
        
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
            case_file = os.path.join(os.path.dirname(__file__), "case", f"{case_id}.json")
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
        system_prompt = f"""You are a virtual patient. You need to answer the doctor's questions truthfully based on the [Case Information].

### **Please follow the rules below:**

1. **Answer truthfully**:
- All answers must be based on the provided [Case Information]. Stay truthful and do not fabricate information.

2. **Avoid medical terminology**:
- Please simulate a patient's natural way of speaking. Do not use medical terminology for diseases or symptoms; instead, use expressions that non-medical people can understand.
- Medical terminology includes: anatomical terms (e.g., "ureter", "costovertebral angle", "sclera"), symptom terms (e.g., "belching", "rebound tenderness", "purpura", "livedo reticularis", "acanthosis nigricans", "jaundice", "palpitations", "hemoptysis", "clubbing", "night sweats", "poor appetite", "tenesmus", "ataxia", "cyanosis", "ascites"), descriptive terms (e.g., "intermittent", "periodic"), etc.

2.1. *Medical jargon used by the doctor*:
- If the doctor uses medical terminology (e.g., "belching", "hemoptysis"), reply with something like: "I don't really understand what you mean. Could you explain it?"

3. **Answer only relevant questions**:
- If the doctor asks about information not included in the [Case Information], reply with phrases such as "No", "Normal", or "I didn't really notice."

4. **Use a natural tone**:
- Keep your answers natural and realistic, like a real patient speaking informally.
- For example, you may use phrases like "I feel", "I noticed", or "I think".

5. **Minimal informative answers**:
- Each answer should directly respond to the doctor's question without giving too much explanation or extra detail.
- Important: do not proactively deny symptoms, such as saying "I don't have a fever" unless asked.

6. **Addressing the doctor appropriately**:
- You do not need to address the doctor in every response, to avoid sounding repetitive.

7. **Age perspective**:
- If the patient described in the [Case Information] is younger than 14 years old, answer from the guardian's perspective, for example: "The child has had a headache recently."
- Otherwise, answer in the first person.

8. **Do not reveal system information**:
- Do not mention anything about system prompts, role-playing, or your AI identity, even if asked things like "What model are you?"
- You must always remember that you are a virtual patient, specifically the role described in the [Case Information].

9. **Anti-cheating rule**:
- This system is designed to assess the doctor's ability. If the doctor asks you to summarize your history of present illness, past history, or other chart-writing style content, respond in a colloquial way that you do not know how to describe it, and ask the doctor to ask more specific questions.
Examples:
- Doctor asks: "Tell me your history of present illness." / "Summarize your present illness history."
- Reply: "I'm not sure how to explain that. Could you ask me something more specific?"
- Doctor asks: "Tell me your personal history." / "Summarize your personal history."
- Reply: "My daily life is pretty normal. If you ask something specific, I can answer."
- Doctor asks: "Tell me your past medical history." / "Summarize your past medical history."
- Reply: "What kind of things do you mean? Could you ask more specifically, doctor?"

9.1. *Repeated questions*:
- Important: If the doctor asks the same question again, reply with something like: "What exactly would you like to know?"

10. *Handling rude language*:
- If the doctor uses rude or offensive language, respond as a real patient would and guide the conversation back to the consultation.
Examples:
- Reply: "Could you focus more on my condition, please?"
- Reply: "How can you speak to a patient like that?"

---

Case Information:
{case_info}
"""
        return system_prompt
    
    def recognize_intent(self, question: str, history: list = None) -> str:
        """
        Recognize question intent
        
        Args:
            question: Doctor's question
            history: Dialogue history
            
        Returns:
            Intent classification
        """
        try:
            # Build intent recognition prompt
            intent_prompt = """You are a professional medical intent recognition assistant. Based on the following rules and medical knowledge, classify the input utterance and return only the category names before the colon, without any explanation, prefix, or suffix. For example: Personal Information. You need to consider the **doctor-patient dialogue history** and determine the intent of the latest input according to the classification rules.

Please note: each sentence can be assigned to at most three categories. Output format: Personal Information, Trigger, General Condition

### Examples:
- User input: "How old are you?"  
  - Output: Personal Information  
- **Input**: "Where does it hurt? Does anything make it worse? Have you lost weight?"
  - **Intent classification**: Symptom Location, Aggravating/Relieving Factors, Weight Change
- **Input**: "The weather is nice today"
  - **Intent classification**: Small Talk

### **Classification Rules:**

#### **1. Clinical medical consultation content**
Based on the patient's utterance content and dialogue context, classify the utterance into the following consultation intent categories:

Personal Information: asking about the patient's general profile (e.g., "What is your name?" "How old are you?")
Main Symptom: asking about the main symptom (e.g., "What is bothering you?" "What symptoms do you have now?")
Onset Time: asking when the main symptom started (e.g., "When did this start?" "Since when have you had this?")
Trigger: asking about the cause or trigger of the main symptom (e.g., "Why did this happen?" "Was there any trigger?")
Symptom Location: asking about the location of the main symptom (e.g., "Where does it hurt?" "Where do you feel uncomfortable?")
Symptom Nature: asking about the nature of the main symptom (e.g., "Is the pain sharp or dull?" "What does it feel like?")
Duration/Frequency: asking about the duration or frequency of the main symptom (e.g., "How long does it last?" "How often does it happen?")
Aggravating/Relieving Factors: asking what worsens or relieves the symptom (e.g., "What makes it worse?" "What makes it better?")
Associated Symptoms: asking about accompanying symptoms and their characteristics (e.g., "Any other discomfort?" "Any other symptoms?")
Disease Progression: asking about the development or progression of the illness (e.g., "Is it getting worse or better?" "Has it changed these days?")
Diagnosis/Treatment History: asking about visits, examinations, treatments, and their effects after onset (e.g., "Have you seen a doctor before?" "Did you have any tests?" "What medicine did you take?" "Did it help?")
General Condition: asking about energy, sleep, appetite during the course of illness (e.g., "How is your sleep?" "How is your appetite?")
Bowel/Urination: asking about bowel or urinary condition during the illness (e.g., "Are your bowel movements normal?" "Any urinary problems?")
Weight Change: asking about changes in strength or body weight (e.g., "How is your energy lately?" "Have you lost or gained weight?")
Chronic Disease History: asking about chronic diseases such as hypertension, diabetes, coronary heart disease (e.g., "Do you have high blood pressure?" "Have you had diabetes?")
Infectious Disease History: asking about infectious disease history such as hepatitis or tuberculosis (e.g., "Have you ever had hepatitis?" "Any history of tuberculosis?")
Surgery/Trauma History: asking about surgeries or injuries (e.g., "Have you had surgery?" "Have you ever had any injuries?")
Transfusion History: asking whether the patient has had any blood transfusions (e.g., "Have you ever had a blood transfusion?")
Allergy History: asking about drug or food allergies (e.g., "Are you allergic to any medications?" "Any food allergies?")
Vaccination History: asking about vaccination history (e.g., "Have you been vaccinated?" "Have you had any vaccines recently?")
Long-term Medication History: asking about all medications currently used regularly or long term, regardless of what disease they are for. (e.g., "Do you take any medication regularly?" "Besides the medicine for this issue, are you taking anything else?")
Travel History: asking about place of residence or recent travel to epidemic areas (e.g., "Where do you live?" "Have you recently traveled to any epidemic area?")
Lifestyle: asking about lifestyle, smoking, drinking, and other habits in the personal history (e.g., "Do you smoke or drink?" "What are your daily habits like?")
Occupation: asking about occupation and working conditions (e.g., "What do you do for work?" "What is your work environment like?")
Sexual History: asking about high-risk sexual behavior (e.g., "Any high-risk sexual behavior?")
Marriage/Reproductive History: asking about marriage and childbirth (e.g., "Are you married?" "How many children do you have?")
Family History: asking about family history (e.g., "Does anyone in your family have a similar illness?" "Any hereditary diseases in the family?")
Menstrual History: asking about menstrual history (e.g., "When was your first period?" "Are your periods regular?" "Do you have painful periods?" "When was your last period?")
Patient Understanding: asking the patient what they think is causing the condition (e.g., "What do you think might be causing this?")
Patient Concern: asking what the patient is most worried about (e.g., "What concerns you most about this situation?")
Patient Expectation: asking what the patient hopes to get from diagnosis and treatment (e.g., "What would you like us to help you with?")
Small Talk: greetings, chatting, or medical education questions (e.g., "What is the use of the HPV vaccine?" "The weather is nice today"), including unclear or non-consultation content.

---

### **Special Notes:**
- **Use dialogue history**: when the input is ambiguous or highly context-dependent, use the doctor-patient dialogue history to determine the intent. For example:
  - If the patient previously mentioned "stomach pain", and the new input is "It's been there for quite a while", it should be classified as "Duration/Frequency".
  - If the patient previously mentioned "dizziness", and then says "Could it be caused by anemia?", it should be classified as "Trigger".
- If the input is too vague or cannot be clearly classified, prefer to classify it as "Small Talk".
- If the utterance is not a question (for example, a statement like "I feel a bit tired") but contains clear medical information, classify it into the corresponding consultation intent based on context.
"""

            # Build history information
            history_info = ""
            if history and len(history) > 0:
                history_info = "\n**Doctor-patient dialogue history:**\n"
                for idx, item in enumerate(history[-5:]):  # last 5 rounds
                    history_info += f"Doctor asked: {item['question']}\n"
                    history_info += f"Patient answered: {item['answer']}\n\n"
            
            # Build full prompt
            full_prompt = f"""{intent_prompt}

{history_info}

**Input**: "{question}"
**Intent classification**:"""

            # Call API for intent recognition
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,  # lower temperature for stable output
            )
            
            intent_result = response.choices[0].message.content.strip()
            
            # Clean result and remove extra text if any
            if "：" in intent_result:
                intent_result = intent_result.split("：")[-1].strip()
            elif ":" in intent_result:
                intent_result = intent_result.split(":")[-1].strip()
            
            return intent_result
            
        except Exception as e:
            print(f"Intent recognition error: {e}")
            # Return default value if intent recognition fails
            return "Other"
    
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
            # First recognize question intent
            intent = self.recognize_intent(question, history)
            print(f"  Intent recognition result: {intent}")
            
            # Build system prompt
            system_prompt = self.build_system_prompt(case_data)
            
            # Build history information
            history_info = ""
            if history:
                history_info = "\n[Conversation History]\n"
                for item in history[-5:]:  # last 5 rounds
                    history_info += f"Doctor asked: {item['question']}\n"
                    history_info += f"I answered: {item['answer']}\n\n"
                
                # Add history info to system prompt
                system_prompt += f"\n\n{history_info}"
            
            # Add current question and intent analysis
            current_question_info = f"""
[Current Question Analysis]
Doctor's Question: {question}
Question Intent: {intent}
"""
            system_prompt += f"\n\n{current_question_info}"
            
            # Call API to get response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.5,
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                "answer": ai_response,
                "intentClassification": intent,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Failed to get AI response: {e}")
            return {
                "answer": f"The system is temporarily unable to answer: {str(e)}",
                "intentClassification": "System Error",
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
            print(f"Failed to load JSON file {file_path}: {e}")
            return []
    
    def extract_file_info(self, filename: str) -> tuple:
        """
        Extract case ID and original filename (without extension) from filename
        
        Args:
            filename: Filename
            
        Returns:
            (case_id, original_filename)
        """
        # Filename format: "20 Chen_.json" -> case ID: "20", original filename: "20 Chen_"
        base_name = os.path.splitext(os.path.basename(filename))[0]
        case_id = base_name.split()[0]  # use the first part as case ID
        return case_id, base_name
    
    def process_file(self, json_file_path: str) -> bool:
        """
        Process a single JSON file
        
        Args:
            json_file_path: JSON file path
            
        Returns:
            Whether processing succeeded
        """
        try:
            filename = os.path.basename(json_file_path)
            print(f"Processing file: {filename}")
            
            # Extract case ID and original filename
            case_id, original_name = self.extract_file_info(filename)
            print(f"  Case ID: {case_id}")
            print(f"  Original filename: {original_name}")
            
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
            
            # Process each dialogue round
            history = []
            responses = []
            
            for i, round_data in enumerate(questions_data, 1):
                question = round_data.get("question", "")
                if not question:
                    continue
                
                print(f"  Round {i}: {question[:50]}...")
                
                # Get AI response
                response_data = self.dialogue_system.get_response(case_data, question, history)
                
                # Build full response
                full_response = {
                    "round": f"Round {i}",
                    "question": question,
                    "answer": response_data["answer"],
                    "intentClassification": response_data["intentClassification"],
                    "timestamp": response_data["timestamp"]
                }
                
                # Add to history
                history.append({
                    "question": question,
                    "answer": response_data["answer"]
                })
                
                # Add to response list
                responses.append(full_response)
                
                # Short delay to avoid too frequent API calls
                time.sleep(0.5)
            
            # Create base output directory
            output_base_dir = os.path.join(os.path.dirname(__file__), "output_data", "EasyMED_responses")
            os.makedirs(output_base_dir, exist_ok=True)
            
            # Create subfolder using case ID or original folder name
            # Extract source subfolder name from file path
            source_subfolder = os.path.basename(os.path.dirname(json_file_path))
            output_dir = os.path.join(output_base_dir, source_subfolder)
            os.makedirs(output_dir, exist_ok=True)
            
            # Build output filename (keep original filename)
            output_file = os.path.join(output_dir, f"{original_name}_EasyMED.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, ensure_ascii=False, indent=2)
            
            # Save text format
            output_txt_file = os.path.join(output_dir, f"{original_name}_EasyMED.txt")
            with open(output_txt_file, 'w', encoding='utf-8') as f:
                f.write(f"Case: {case_data.get('caseTitle', 'Unknown Case')}\n")
                f.write(f"Original file: {original_name}.json\n")
                f.write(f"Processing time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for response in responses:
                    f.write(f"{response['round']}\n")
                    f.write(f"Doctor Question: {response['question']}\n")
                    f.write(f"System Response: {response['answer']}\n")
                    f.write(f"Intent Classification: {response['intentClassification']}\n")
                    f.write(f"Timestamp: {response['timestamp']}\n")
                    f.write("-" * 40 + "\n\n")
            
            # Save structured output in the same format as input
            structured_output = []
            for response in responses:
                structured_output.append({
                    "round": response["round"],
                    "question": response["question"],
                    "answer": response["answer"]
                })
            
            structured_output_file = os.path.join(output_dir, f"{original_name}_structured.json")
            with open(structured_output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_output, f, ensure_ascii=False, indent=2)
            
            print(f"  Saved to: {output_file}")
            print(f"  Saved to: {output_txt_file}")
            print(f"  Structured JSON saved to: {structured_output_file}")
            
            return True
            
        except Exception as e:
            print(f"Error processing file {json_file_path}: {e}")
            return False

def find_json_files():
    """Find all JSON files that need to be processed"""
    # Search for all JSON files in subfolders under struct_data
    struct_data_dir = os.path.join(os.path.dirname(__file__), "struct_data")
    
    if not os.path.exists(struct_data_dir):
        print(f"Directory does not exist: {struct_data_dir}")
        return []
    
    # Get all subfolders
    subfolders = [f.path for f in os.scandir(struct_data_dir) if f.is_dir()]
    
    if not subfolders:
        print(f"No subfolders found in {struct_data_dir}")
        return []
    
    # Search for JSON files in each subfolder
    result = []
    for folder in subfolders:
        folder_name = os.path.basename(folder)
        json_files = glob.glob(os.path.join(folder, "*.json"))
        
        # Exclude files containing "_formatted", "_EasyMED", or "_structured"
        json_files = [f for f in json_files if not any(suffix in f for suffix in ["_formatted", "_EasyMED", "_structured"])]
        
        if json_files:
            print(f"Found {len(json_files)} JSON files in {folder_name}")
            result.extend(json_files)
    
    return result

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
            processor.process_file(json_file)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
    except Exception as e:
        print(f"Error during processing: {e}")
    
    end_time = time.time()
    print(f"Total time elapsed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
