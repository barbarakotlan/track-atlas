export type Source = {
  file_name: string;
  chunk_id: number | null;
  score: number | null;
  excerpt: string;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function askQuestion(question: string): Promise<AskResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch {
    throw new Error(`Could not reach the Track Atlas API at ${API_URL}.`);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `The API returned ${response.status}.`);
  }

  return response.json();
}
