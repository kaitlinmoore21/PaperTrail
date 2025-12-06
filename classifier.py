import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def classify_document(text: str) -> str:
    """
    Sends extracted text to an Ollama LLaMA3 model to classify document type.
    """

    prompt = f"""
You are a document classification AI.

Classify the following document into ONE category:

- invoice
- email
- prescription
- receipt
- bank_statement
- id_document
- academic
- form
- other

Return only the category name, nothing else.

Document text:
{text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        return "other"

    result = response.json().get("response", "").strip().lower()

    # Ensure result is a valid category
    valid_categories = {
        "invoice", "email", "prescription", "receipt",
        "bank_statement", "id_document", "academic",
        "form", "other"
    }

    if result not in valid_categories:
        return "other"

    return result
