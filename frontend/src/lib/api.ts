import axios from "axios";
import {
  ClusterEvalData,
  RecommendationEvalData,
  NLPEvalData
} from "@/types";

/* ================================
   API ENDPOINTS
================================ */

const RASA_URL =
  process.env.NEXT_PUBLIC_RASA_URL ||
  "http://localhost:5005/webhooks/rest/webhook";

const FASTAPI_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

/* ================================
   FASTAPI CLIENT
================================ */

const api = axios.create({
  baseURL: FASTAPI_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000
});

/* ================================
   CHAT → RASA
================================ */

export async function sendChatMessage(message: string) {

  console.log("==================================================");
  console.log(`[FRONTEND -> API] Mengirim pesan ke Rasa (${RASA_URL}):`, message);

  const { data } = await axios.post(
    RASA_URL,
    {
      sender: "user",
      message: message
    }
  );

  console.log(`[FRONTEND -> API] Eksekusi Rasa selesai, respons dari webhook:`, data);
  console.log("==================================================");

  return data;
}

/* ================================
   FEATURE SUMMARY
================================ */

export async function getFeatureSummary() {
  const { data } = await api.get("/features");
  return data;
}

/* ================================
   CLUSTERING EVALUATION
================================ */

export async function getClusteringEval(): Promise<ClusterEvalData> {

  const { data } = await api.get("/evaluasi/clustering");

  return data;
}

/* ================================
   RECOMMENDATION EVALUATION
================================ */

export async function getRecommendationEval(): Promise<RecommendationEvalData> {

  const { data } = await api.get("/evaluasi/rekomendasi");

  return data;
}

/* ================================
   NLP EVALUATION
================================ */

export async function getNLPEval(): Promise<NLPEvalData> {

  const { data } = await api.get("/evaluasi/nlp");

  return data;
}

export default api;