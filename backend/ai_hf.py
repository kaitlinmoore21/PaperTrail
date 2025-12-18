# backend/ai_hf.py
import os, httpx, json

HF_TOKEN = os.getenv("HF_API_TOKEN")  # set in env
HF_URL = "https://api-inference.huggingface.co/models/"

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

def summarize_text(text, model="sshleifer/distilbart-cnn-12-6"):
    # short-circuit empty
    if not text: return ""
    payload = {"inputs": text, "parameters": {"max_length": 150, "min_length": 30}}
    with httpx.Client(timeout=60.0) as client:
        r = client.post(HF_URL + model, headers=headers, json=payload)
    if r.status_code == 200:
        out = r.json()
        if isinstance(out, list): return out[0].get("summary_text","")
    return ""

def ner_entities(text, model="dbmdz/bert-large-cased-finetuned-conll03-english"):
    if not text: return []
    payload = {"inputs": text}
    with httpx.Client(timeout=60.0) as client:
        r = client.post(HF_URL + model, headers=headers, json=payload)
    if r.status_code == 200:
        return r.json()
    return []

def extract_structured(text):
    # 1) summary
    summary = summarize_text(text[:4000])  # keep payload size reasonable
    # 2) NER
    ents = ner_entities(text[:4000])
    # heuristics for invoice fields (example)
    import re
    total_m = re.search(r'(\£|\$|€)\s?[\d,]+(?:\.\d{2})?', text)
    date_m = re.search(r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b', text)
    invoice_m = re.search(r'(invoice\s*(no|number)[:\s]*\#?\s*([A-Za-z0-9\-]+))', text, re.IGNORECASE)
    struct = {
        "summary": summary,
        "entities": ents,
        "total": total_m.group(0) if total_m else None,
        "date": date_m.group(0) if date_m else None,
        "invoice_number": invoice_m.group(3) if invoice_m else None
    }
    return struct
