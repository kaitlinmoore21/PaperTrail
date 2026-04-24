import axios from 'axios'; // Imports the tool used to send data over the internet
import { API_BASE } from '../config'; // Gets the home address of your server (e.g., http://localhost:8000)

// Defines the "Guest List" - exactly what info we need from a user
type AuthParams = {
  email: string; // Every user must provide a text-based email
  password: string; // Every user must provide a text-based password
  employee_number: string; // Every user must provide their unique ID number
};

// This function handles the "Create Account" process
export const signupUser = async ({ email, password, employee_number }: AuthParams) => {
  // It sends the email, password, and ID to the server's /signup/ folder and waits for a reply
  return await axios.post(`${API_BASE}/signup/`, { email, password, employee_number });
};

// This function handles the "Sign In" process
export const loginUser = async ({ email, password, employee_number }: AuthParams) => {
  // It sends the credentials to the server's /login/ folder to see if they match the records
  return await axios.post(`${API_BASE}/login/`, { email, password, employee_number });
};