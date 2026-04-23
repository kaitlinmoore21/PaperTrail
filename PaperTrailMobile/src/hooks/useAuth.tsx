import axios from 'axios';
import { API_BASE } from '../config';

type AuthParams = {
  email: string;
  password: string;
};

// We use axios directly here to ensure the response structure is predictable
export const signupUser = async ({ email, password }: AuthParams) => {
  return await axios.post(`${API_BASE}/signup/`, { email, password });
};

export const loginUser = async ({ email, password }: AuthParams) => {
  // Returns the full axios response including .data (where the token is) and .status
  return await axios.post(`${API_BASE}/login/`, { email, password });
};