import axios from "axios";
const BASE = "http://localhost:8000";

export const analyzeStock = (ticker, period) =>
  axios.post(`${BASE}/analyze`, { ticker, period }).then(r => r.data);