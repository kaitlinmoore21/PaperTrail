// 1. THE CONNECTION HUB:
// 'DEV_IP' is the specific IP address of your computer on your local Wi-Fi.
// This is crucial for mobile apps: your phone needs to know exactly which 
// computer in the building is running the Python backend.
export const DEV_IP = "10.18.225.232"; 

// 'API_BASE' combines the IP with the port (8000) to create the full address.
// Other files will import this to know where to send their "requests."
export const API_BASE = `http://${DEV_IP}:8000`;

// 2. THE BRANDING VAULT:
// This object stores your "Source of Truth" for the app's look and feel.
// We use HSE (Health Service Executive) official colors to give the app 
// a professional, medical authority.
export const HSE_THEME = {
  primary: '#005b94',    // The main blue used for headers and primary buttons
  secondary: '#00a38d',  // The green used for "Success" or "Upload" buttons
  background: '#f8f9fa', // A light grey-white to reduce eye strain
  white: '#ffffff',      // Standard clean white for cards and backgrounds
  accent: '#ffc107',     // A yellow/gold for warnings or highlights
};
