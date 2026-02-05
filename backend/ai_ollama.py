import subprocess
import json

def ollama_prompt(prompt: str, model: str = "llama3.2"):
    """
    Sends a prompt to a local Ollama model and returns raw text output.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.decode().strip()}"

        return result.stdout.decode().strip()

    except Exception as e:
        return f"ERROR: {e}"


def ai_extract_and_classify(text: str):
    """
    1) Classifies the document into:
       [invoice, receipt, medical_prescription, bank_statement, document, id_card, other]

    2) Extracts structured JSON fields from the text.

    Returns a dictionary:
    {
        "doc_type": "...",
        ... extracted fields ...
    }
    """

    # -------------------------------
    # 1. CLASSIFY
    # -------------------------------
    classify_prompt = f"""
    You are a document classifier.

    Classify this text into ONE category:
    invoice, receipt, medical_prescription, bank_statement, document, id_card

    If unknown, respond: other.

    TEXT:
    {text}

    Respond ONLY with the category word.
    """

    doc_type = ollama_prompt(classify_prompt).strip().lower()

    # Safety fallback
    allowed = [
        "invoice", "receipt", "medical_prescription",
        "bank_statement", "document", "id_card", "other"
    ]
    if doc_type not in allowed:
        doc_type = "other"

    # -------------------------------
    # 2. STRUCTURED JSON EXTRACTION
    # -------------------------------
    extract_prompt = f"""
    Extract all meaningful structured fields from the document.
    Respond ONLY with valid JSON.

    TEXT:
    {text}
    """

    raw_json = ollama_prompt(extract_prompt)

    try:
        fields = json.loads(raw_json)
    except:
        fields = {"raw_extraction": raw_json}

    # Return combined result
    return {
        "doc_type": doc_type,
        **fields
    }
