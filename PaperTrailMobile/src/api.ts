import axios from 'axios'; // Imports the Axios library, a popular tool for making web requests
import { API_BASE } from './config'; // Imports your server's address (e.g., http://127.0.0.1:8000)

// This creates a "Pre-configured Messenger"
const api = axios.create({
  // 1. The Base URL: Now you can just use api.get('/documents') 
  // instead of the full 'http://127.0.0.1:8000/documents'
  baseURL: API_BASE,

  // 2. Default Headers: Tells the server that we are sending 
  // and expecting "JSON" (the language of data)
  headers: { 'Content-Type': 'application/json' }
});

// This makes the 'api' tool available to every other file in your project
export default api;