import type { GeoJSONCollection, Tip } from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function fetchSources(): Promise<GeoJSONCollection> {
  const res = await fetch(`${API_BASE}/sources`);
  if (!res.ok) throw new Error("Failed to load water sources");
  return res.json();
}

export async function fetchTips(): Promise<Tip[]> {
  const res = await fetch(`${API_BASE}/tips`);
  if (!res.ok) throw new Error("Failed to load tips");
  const data = await res.json();
  return data.tips;
}

export async function submitReport(
  sourceId: string,
  causeCategory: string
): Promise<{ message: string; repair_case_id: number }> {
  const res = await fetch(`${API_BASE}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_id: sourceId, cause_category: causeCategory }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Report failed");
  }
  return res.json();
}
