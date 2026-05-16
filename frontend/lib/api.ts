export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export type AnalysisSummary = {
  id: string;
  original_filename: string;
  media_type: string;
  patient_code: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type AnalysisDetail = AnalysisSummary & {
  result_json: Record<string, unknown> | null;
  report_json: Record<string, unknown> | null;
  error_message: string | null;
};

export function apiHeaders(): HeadersInit {
  return API_KEY ? { "X-API-Key": API_KEY } : {};
}

