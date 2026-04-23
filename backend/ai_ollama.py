import requests
import json
import re

def ollama_prompt(prompt: str, model: str = "llama3.2"):
    """
    Sends a prompt to the Ollama API with high limits to prevent cutting off data.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 4096,  # Allows for very large data extraction
            "temperature": 0.1,   # Keeps the AI focused on the format
            "repeat_penalty": 1.1
        }
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"

def ai_extract_and_classify(text: str):
    """
    Classifies the document and dynamically extracts ALL critical information.
    """
    # 1. CLASSIFY
    classify_prompt = (
        f"Classify this text into ONLY ONE word: invoice, receipt, prescription, "
        f"statement, document, id_card, or other. Respond with JUST the word. TEXT: {text}"
    )
    raw_type = ollama_prompt(classify_prompt).lower().strip()
    
    valid_categories = ["invoice", "receipt", "prescription", "statement", "document", "id_card", "other"]
    doc_type = "other" 
    for cat in valid_categories:
        if cat in raw_type:
            doc_type = cat
            break
    
    # 2. DYNAMIC STRUCTURED EXTRACTION
    # Note: We removed the fixed keys so it finds what's actually there!
    extract_prompt = f"""
    Act as an expert data extractor. Identify and extract EVERY important detail from the text below.
    
    Guidelines:
    - Do not use a fixed template. Extract License Numbers, Dates, Amounts, Addresses, or Instructions.
    - Use clear, descriptive keys in snake_case (e.g., "license_class", "issuing_authority").
    - Include a "summary" key describing the document in one sentence.
    - Respond ONLY with a raw JSON object. No markdown, no conversational text.

    TEXT TO ANALYZE:
    {text}
    """

    raw_response = ollama_prompt(extract_prompt)

    try:
        # Find the JSON brackets
        start_idx = raw_response.find('{')
        end_idx = raw_response.rfind('}') + 1
        if start_idx == -1:
            raise ValueError("No JSON found")
            
        clean_json_str = raw_response[start_idx:end_idx]
        
        # Parse into a dictionary (this is what kills the backslashes!)
        fields = json.loads(clean_json_str)
        
    except Exception:
        # Fallback if the AI messes up the format
        fields = {"summary": "Extraction failed", "raw_content": raw_response[:500]}

    return {
        "doc_type": doc_type,
        **fields
    }