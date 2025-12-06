const BASE_URL = "http://192.168.1.20:8000"; // ← CHANGE THIS TO YOUR LAPTOP IP

// List all documents
export async function listDocuments() {
  const res = await fetch(`${BASE_URL}/documents/`);
  return res.json();
}

// Get details for one document
export async function getDocument(id: number) {
  const res = await fetch(`${BASE_URL}/documents/${id}`);
  return res.json();
}

// Unlock a document
export async function unlockDocument(id: number, password: string) {
  const res = await fetch(`${BASE_URL}/documents/${id}/unlock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });

  return res.json();
}

// Upload new document
export async function uploadDocument(fileUri: string, filename: string) {
  let formData = new FormData();
  formData.append("file", {
    uri: fileUri,
    name: filename,
    type: "application/pdf"
  } as any);

  const res = await fetch(`${BASE_URL}/upload/`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}

// Decrypted PDF download
export async function downloadDecrypted(id: number) {
  return `${BASE_URL}/documents/${id}/download-decrypted`;
}

// Encrypted PDF download
export async function downloadEncrypted(id: number) {
  return `${BASE_URL}/documents/${id}/download`;
}
