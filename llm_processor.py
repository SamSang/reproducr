import argparse
import requests
import yaml
from sqlalchemy import text, exists
from database import create_connection, DataAvailableCoded, DataAvailableStatement

from tqdm import tqdm

class DatabaseConnector:
    """
    Handles database connections and queries using SQLAlchemy from database.py.
    """
    def __init__(self):
        # 1. Connect to a database
        self.session = create_connection()

    def get_records(self, model_name):
        """
        2. Read value from a database table
        """
        # using native sqlalchemy
        result = self.session.query(DataAvailableStatement).filter(
            ~exists().where(
                DataAvailableCoded.original_value
                == DataAvailableStatement.statement,
                DataAvailableCoded.model_name == model_name
            )
        )
        # return as list of dicts for easy access
        return [{"statement": row.statement} for row in result]

    def save_processed_record(self, original_value: str, llm_response: str, model_name: str):
        """
        5. Load that response and the read value to another database table.
        Using the SQLAlchemy table definition LLMResult.
        """
        new_record = DataAvailableCoded(
            original_value=original_value,
            raw_response=llm_response,
            model_name=model_name,
        )
        self.session.add(new_record)
        self.session.commit()
        
    def close(self):
        self.session.close()


class LLMClient:
    """
    Handles communication with the LLM API using Ollama / Copilot configurations.
    """
    def __init__(self, model_name: str, endpoint: str):
        self.model_name = model_name
        self.endpoint = endpoint

    def generate(self, system_prompt: str, user_prompt: str, user_input: str) -> str:
        """
        3. Make an api call to an llm using the model-specific prompts and data value.
        """
        # print(f"Calling Endpoint ({self.model_name}) with input string: {user_input[:30]}...")
        
        # Inject the user input dynamically into the formatted prompt
        formatted_user_prompt = user_prompt.format(user_input=user_input)
        
        # Combine them depending on the API structure. For Ollama base generations, 
        # both often fit linearly into `prompt`. Some endpoints (like OpenAI style) prefer roles.
        full_prompt = f"{system_prompt}\n\n{formatted_user_prompt}"

        # print(full_prompt)
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }


        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"LLM API Call failed: {e}")
            raise


def clean_and_validate_response(raw_response: str) -> str:
    """
    4. Clean and validate the response from the llm
    """
    cleaned = raw_response.strip()
    if cleaned.startswith("```json") and cleaned.endswith("```"):
        cleaned = cleaned[7:-3].strip()
    
    if not cleaned:
        raise ValueError("Response from LLM was empty.")
        
    return cleaned

def load_prompts(yaml_path: str, model_name: str):
    """
    Load model-specific prompts from a YAML registry file.
    Falls back to 'default' if the specific model isn't listed.
    """
    try:
        with open(yaml_path, 'r') as file:
            registry = yaml.safe_load(file)
            
        model_prompts = registry.get(model_name)
        if not model_prompts:
            print(f"Warning: No explicit prompts found for '{model_name}'. Falling back to 'default'.")
            model_prompts = registry.get('default')
            
        return model_prompts['system_prompt'], model_prompts['user_prompt']
    
    except Exception as e:
        print(f"Failed to load prompt registry: {e}")
        raise


def run_pipeline(model_name: str, endpoint: str, prompts_file: str):
    db = DatabaseConnector()
    llm = LLMClient(model_name=model_name, endpoint=endpoint)
    
    # Load specific prompts based on the model provided
    system_prompt, user_prompt = load_prompts(prompts_file, model_name)

    try:
        records = db.get_records(model_name=model_name)
        print(f"Found {len(records)} records to process.")

        for row in tqdm(records):
            statement = row['statement']

            try:
                # 3. API Call using the loaded model prompts
                raw_response = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt, user_input=statement)
                
                # 4. Clean & Validate
                validated_response = clean_and_validate_response(raw_response)
                
                # 5. Load Original Value and Validated Response to Output Table
                # print(statement, validated_response)
                db.save_processed_record(statement, validated_response, model_name)
                
            except Exception as e:
                print(f"Failed to process statement '{statement}': {e}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Data Processing Pipeline")
    
    parser.add_argument("--model", type=str, help="LLM model name to use (e.g. llama or copilot)")
    parser.add_argument("--endpoint", type=str, default="http://localhost:11434/api/generate", help="API endpoint")
    parser.add_argument("--prompts-file", type=str, default="prompts.yaml", help="Path to YAML prompt registry")
    
    args = parser.parse_args()
    
    run_pipeline(args.model, args.endpoint, args.prompts_file)

