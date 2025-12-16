const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

export async function generateFull(prompt: string): Promise<any> {
  const res = await fetch(`${BASE}/infra/generate-full`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`generateFull failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function runPlan(iac: any): Promise<any> {
  const res = await fetch(`${BASE}/terraform/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ iac }),
  });
  if (!res.ok) throw new Error("terraform plan failed");
  return res.json();
}
