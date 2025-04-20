import axios from "axios";

const BASE = "http://localhost:8000";

export async function getState() {
  const { data } = await axios.get(`${BASE}/state`);
  return data;
}

export async function sendCommand(action: string) {
  await axios.post(`${BASE}/command/${action}`);
}