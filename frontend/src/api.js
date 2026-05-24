import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://mukulgupta3264.pythonanywhere.com/api/',
});

export default api;
