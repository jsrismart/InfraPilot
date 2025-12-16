const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8001/api/v1";

export interface GenerateResponse {
  iac: Record<string, string>;
  plan?: Record<string, any>;
  security?: Record<string, any>;
  finops?: Record<string, any>;
}

export async function generateFull(prompt: string, fast: boolean = false): Promise<GenerateResponse> {
  if (!prompt.trim()) {
    throw new Error("Prompt cannot be empty");
  }

  if (prompt.length > 5000) {
    throw new Error("Prompt exceeds maximum length of 5000 characters");
  }

  try {
    const url = new URL(`${BASE}/infra/generate-iac`);
    if (fast) {
      url.searchParams.append("fast", "true");
    }

    const res = await fetch(url.toString(), {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      },
      body: JSON.stringify({ prompt }),
      cache: "no-store"
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${res.status}: Pipeline failed`);
    }

    return res.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Unknown error occurred");
  }
}
