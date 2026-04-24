import requests # Imports the tool used to send data over the internet to the AI (Ollama)

OLLAMA_URL = "http://localhost:11434/api/generate" # The digital "doorbell" address for the AI model on your computer

# This function takes a block of text and decides what kind of document it is
def classify_document(text: str) -> str:
    """
    Sends extracted text to an Ollama LLaMA3 model to classify document type.
    """

    # This is the instruction manual we send to the AI so it knows its job
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

    # This part actually sends the "package" of info to the AI
    response = requests.post(
        OLLAMA_URL, # The address we defined at the top
        json={
            "model": "llama3", # Tells the computer to use the LLaMA3 "brain"
            "prompt": prompt, # Sends the instructions and the document text
            "stream": False # Tells the AI to wait until it's finished before answering
        }
    )

    # If the AI doesn't answer or the computer has an error (status is not 200)
    if response.status_code != 200:
        return "other" # Just label it as "other" and move on

    # Takes the AI's answer, cleans off any extra spaces, and makes it lowercase
    result = response.json().get("response", "").strip().lower()

    # This is our "Approved List" of labels the app is allowed to use
    valid_categories = {
        "invoice", "email", "prescription", "receipt",
        "bank_statement", "id_document", "academic",
        "form", "other"
    }

    # If the AI gets creative and makes up a new category not in our list
    if result not in valid_categories:
        return "other" # Force it back to "other" to keep the app from breaking

    return result # Give back the final, clean category name (e.g., "receipt")