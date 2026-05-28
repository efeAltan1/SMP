import axios from 'axios'

// In dev, Vite proxies /api → http://127.0.0.1:5000/api (see vite.config.js)
// In production, set VITE_API_URL to the deployed backend URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

export default api
