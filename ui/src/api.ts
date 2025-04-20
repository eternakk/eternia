import axios from "axios";
const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { Authorization: `Bearer ${TOKEN}` },
});
export const getState = () => api.get("/state").then(r => r.data);
export const sendCommand = (a: string) => api.post(`/command/${a}`);