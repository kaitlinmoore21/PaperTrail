import requests # Imports the tool to send data to other programs (Ollama)
import json # Imports the tool to handle data formatted like a list or dictionary
import re # Imports a tool for searching through text (not used here, but good for cleanup)

# This function talks to the AI model (Ollama) running on your computer
def ollama_prompt(prompt: str, model: str = "llama3.2"):
    """
    Sends a prompt to the Ollama API with high limits to prevent cutting off data.
    """
    url = "http://localhost:11434/api/generate" # The digital "address" where Ollama is listening
    payload = {
        "model": model, # Tells Ollama which AI "brain" to use (llama3.2)
        "prompt": prompt, # The actual question or instruction we are sending
        "stream": False, # Tells the AI to send the whole answer at once, not one word at a time
        "options": {
            "num_predict": 4096,  # Allows the AI to write a very long answer if needed
            "temperature": 0.1,   # Makes the AI very focused and less "creative" (better for data)
            "repeat_penalty": 1.1 # Stops the AI from getting stuck repeating the same words
        }
    }

    try:
        response = requests.post(url, json=payload) # Sends the request to Ollama
        response.raise_for_status() # Checks if the server crashed or failed
        return response.json().get("response", "").strip() # Returns the text answer from the AI
    except Exception as e:
        return f"ERROR: {e}" # If something breaks, it tells you what happened

# This function organizes the document by type and extracts the details
def ai_extract_and_classify(text: str):
    """
    Classifies the document and dynamically extracts ALL critical information.
    """
    # CLASSIFY (What kind of paper is this?) 
    classify_prompt = (
        f"Classify this text into ONLY ONE word: invoice, receipt, prescription, "
        f"statement, document, id_card, or other. Respond with JUST the word. TEXT: {text}"
    )
    raw_type = ollama_prompt(classify_prompt).lower().strip() # Asks the AI for one category word
    
    # List of categories the app understands
    valid_categories = ["invoice", "receipt", "prescription", "statement", "document", "id_card", "other"]
    doc_type = "other" # Sets a default answer in case the AI gets confused
    for cat in valid_categories:
        if cat in raw_type: # Checks if the AI's answer matches one of our valid categories
            doc_type = cat # Updates the document type to the correct category
            break
    
    # DYNAMIC EXTRACTION (Find the details) 
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

    raw_response = ollama_prompt(extract_prompt) # Sends the text to the AI to find facts

    try:
        # Find the JSON brackets (the AI sometimes adds extra talking text we need to ignore)
        start_idx = raw_response.find('{') # Finds where the data list starts
        end_idx = raw_response.rfind('}') + 1 # Finds where the data list ends
        if start_idx == -1: # If the AI didn't provide a list
            raise ValueError("No JSON found")
            
        clean_json_str = raw_response[start_idx:end_idx] # Pulls out just the data list
        
        # Parse into a dictionary (converts the text into a format Python can use)
        fields = json.loads(clean_json_str) 
        
    except Exception:
        # Fallback if the AI messes up the format or doesn't find any data
        fields = {"summary": "Extraction failed", "raw_content": raw_response[:500]}

    # Combines the category (doc_type) and all the facts (fields) into one final result
    return {
        "doc_type": doc_type,
        **fields
    }
