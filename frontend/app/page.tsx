"use client";
import { useState } from "react";

import { askQuestion, type Source } from "./lib/api";

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
};

const EXAMPLE_QUESTIONS = [
  "What are the false start rules?",
  "How is a relay exchange zone defined?",
  "What counts as a legal wind reading?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      const response = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.answer, sources: response.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    void send(question);
  };

  return (
    <main className="min-h-screen bg-zinc-50 p-6 text-zinc-900">
      <section className="mx-auto flex max-w-3xl flex-col gap-6">
        <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-semibold">Track Atlas</h1>
          <p className="mt-2 text-zinc-600">
            Ask about track &amp; field rules and get answers grounded in the knowledge base.
          </p>
        </div>

        <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <div className="min-h-[300px] space-y-3">
            {messages.length === 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-zinc-500">Try one of these questions:</p>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_QUESTIONS.map((question) => (
                    <button
                      key={question}
                      type="button"
                      disabled={loading}
                      onClick={() => void send(question)}
                      className="rounded-full border border-zinc-300 px-3 py-1 text-sm text-zinc-700 hover:border-zinc-500 disabled:opacity-50"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={
                    message.role === "user"
                      ? "ml-auto max-w-[85%] rounded-lg bg-zinc-900 p-3 text-sm text-white"
                      : "max-w-[85%] rounded-lg bg-zinc-100 p-3 text-sm"
                  }
                >
                  <p className="whitespace-pre-wrap">{message.text}</p>
                  {message.sources && message.sources.length > 0 && (
                    <details className="mt-3 text-xs text-zinc-600">
                      <summary className="cursor-pointer">
                        {message.sources.length} source
                        {message.sources.length === 1 ? "" : "s"}
                      </summary>
                      <ul className="mt-2 space-y-2">
                        {message.sources.map((source, sourceIndex) => (
                          <li key={sourceIndex} className="rounded border border-zinc-200 bg-white p-2">
                            <p className="font-medium">
                              [{sourceIndex + 1}] {source.file_name}
                              {source.chunk_id !== null && ` · chunk ${source.chunk_id}`}
                              {source.score !== null && ` · ${source.score.toFixed(2)}`}
                            </p>
                            <p className="mt-1 text-zinc-500">{source.excerpt}</p>
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
              ))
            )}
          </div>

          {loading && <p className="mt-4 text-sm text-zinc-500">Searching the knowledge base...</p>}

          {error && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSend} className="mt-4 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a track & field question..."
              className="flex-1 rounded-lg border border-zinc-300 px-3 py-2 outline-none focus:border-zinc-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-zinc-900 px-4 py-2 text-white disabled:opacity-50"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
