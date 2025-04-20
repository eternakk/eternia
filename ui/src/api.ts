import axios from "axios";
const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { Authorization: `Bearer ${TOKEN}` },
});
export const getState = () => api.get("/state").then(r => r.data);
export const sendCommand = (a: string) => api.post(`/command/${a}`);
export const getCheckpoints = () => api.get<string[]>("/checkpoints").then(r => r.data);
export const rollbackTo = (file?: string) =>
  api.post("/command/rollback", null, { params: { file } });