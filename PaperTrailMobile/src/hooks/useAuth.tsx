import api from '../api';

export const signupUser = async (email, password) => {
  // Add the trailing slash to match the new backend route
  return await api.post('/signup/', { email, password });
};

// Do the same for login if you have it there
export const loginUser = async (email, password) => {
  return await api.post('/login/', { email, password });
};