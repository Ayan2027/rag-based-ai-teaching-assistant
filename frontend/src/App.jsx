import { useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error.message ||
            "Unable to connect to the backend.",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const useSuggestion = (text) => {
    setQuestion(text);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 text-gray-900">

      {/* ================= SIDEBAR ================= */}

      <aside className="hidden w-72 flex-col bg-gray-950 text-white md:flex">

        {/* Logo */}
        <div className="flex items-center gap-3 border-b border-gray-800 p-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-lg font-bold text-gray-950">
            R
          </div>

          <div>
            <h1 className="text-sm font-semibold">
              RAG Assistant
            </h1>

            <p className="text-xs text-gray-400">
              AI Teaching Assistant
            </p>
          </div>
        </div>

        {/* New conversation */}
        <div className="p-4">
          <button
            onClick={clearChat}
            className="flex w-full items-center gap-3 rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-sm font-medium transition hover:bg-gray-800"
          >
            <span className="text-lg">+</span>
            New Conversation
          </button>
        </div>

        {/* Knowledge base */}
        <div className="px-4">
          <div className="rounded-xl border border-gray-800 bg-gray-900 p-4">

            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Knowledge Base
            </h3>

            <div className="space-y-3 text-sm text-gray-300">
              <div className="flex items-center gap-2">
                <span>📄</span>
                Course Documents
              </div>

              <div className="flex items-center gap-2">
                <span>🎥</span>
                Course Videos
              </div>

              <div className="flex items-center gap-2">
                <span>🧠</span>
                AI-powered Retrieval
              </div>
            </div>

          </div>
        </div>

        {/* Footer */}
        <div className="mt-auto flex items-center gap-2 border-t border-gray-800 px-5 py-4 text-xs text-gray-400">
          <span className="h-2 w-2 rounded-full bg-green-500"></span>
          Local AI System
        </div>
      </aside>

      {/* ================= MAIN ================= */}

      <main className="flex min-w-0 flex-1 flex-col">

        {/* Header */}
        <header className="flex min-h-20 items-center justify-between border-b border-gray-200 bg-white px-5 md:px-8">

          <div>
            <h2 className="text-lg font-semibold">
              AI Teaching Assistant
            </h2>

            <p className="mt-1 text-xs text-gray-500 md:text-sm">
              Ask questions about your course materials,
              projects and videos.
            </p>
          </div>

          {/* Backend status */}
          <div className="hidden items-center gap-2 rounded-full border border-gray-200 px-3 py-2 text-xs text-gray-600 sm:flex">
            <span className="h-2 w-2 rounded-full bg-green-500"></span>
            Backend Online
          </div>

        </header>

        {/* ================= CHAT AREA ================= */}

        <section className="flex-1 overflow-y-auto px-4 py-6 md:px-8">

          {messages.length === 0 ? (

            /* ================= WELCOME ================= */

            <div className="mx-auto mt-12 max-w-3xl text-center md:mt-20">

              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-950 text-2xl text-white shadow-lg">
                ✦
              </div>

              <h2 className="mt-6 text-2xl font-bold tracking-tight md:text-3xl">
                How can I help you?
              </h2>

              <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-gray-500">
                Ask questions about your course documents,
                projects or lecture videos.
              </p>

              {/* Suggestions */}
              <div className="mt-8 grid gap-3 sm:grid-cols-2">

                <Suggestion
                  text="What is BookMyCut?"
                  onClick={useSuggestion}
                />

                <Suggestion
                  text="What is Core Web Vitals?"
                  onClick={useSuggestion}
                />

                <Suggestion
                  text="What did I work on at NinePay?"
                  onClick={useSuggestion}
                />

                <Suggestion
                  text="How do you embed a video in HTML?"
                  onClick={useSuggestion}
                />

              </div>
            </div>

          ) : (

            /* ================= MESSAGES ================= */

            <div className="mx-auto max-w-4xl space-y-6">

              {messages.map((message, index) => (

                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >

                  {/* Avatar */}
                  {message.role === "assistant" && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gray-950 text-xs font-bold text-white">
                      AI
                    </div>
                  )}

                  {/* Message */}
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-7 md:max-w-[75%] ${
                      message.role === "user"
                        ? "rounded-tr-md bg-gray-950 text-white"
                        : message.isError
                        ? "rounded-tl-md border border-red-200 bg-red-50 text-red-700"
                        : "rounded-tl-md border border-gray-200 bg-white text-gray-800 shadow-sm"
                    }`}
                  >

                    <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide opacity-50">
                      {message.role === "user"
                        ? "You"
                        : "Teaching Assistant"}
                    </div>

                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>

                  </div>

                  {message.role === "user" && (
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gray-200 text-xs font-bold text-gray-700">
                      You
                    </div>
                  )}

                </div>

              ))}

              {/* Loading */}
              {loading && (
                <div className="flex gap-3">

                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gray-950 text-xs font-bold text-white">
                    AI
                  </div>

                  <div className="rounded-2xl rounded-tl-md border border-gray-200 bg-white px-5 py-4 shadow-sm">

                    <div className="flex gap-1.5">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400"></span>
                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                        style={{ animationDelay: "150ms" }}
                      ></span>
                      <span
                        className="h-2 w-2 animate-bounce rounded-full bg-gray-400"
                        style={{ animationDelay: "300ms" }}
                      ></span>
                    </div>

                  </div>

                </div>
              )}

            </div>
          )}

        </section>

        {/* ================= INPUT ================= */}

        <div className="border-t border-gray-200 bg-white px-4 py-4 md:px-8">

          <div className="mx-auto max-w-4xl">

            <div className="flex items-end gap-2 rounded-2xl border border-gray-300 bg-gray-50 p-2 shadow-sm focus-within:border-gray-500 focus-within:ring-2 focus-within:ring-gray-100">

              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                rows={1}
                placeholder="Ask something about your course..."
                className="max-h-32 min-h-10 flex-1 resize-none bg-transparent px-3 py-2.5 text-sm text-gray-900 outline-none placeholder:text-gray-400 disabled:cursor-not-allowed"
              />

              <button
                onClick={askQuestion}
                disabled={!question.trim() || loading}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-950 text-lg text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-30"
              >
                ↑
              </button>

            </div>

            <p className="mt-2 text-center text-[10px] text-gray-400">
              Enter to send · Shift + Enter for a new line
            </p>

          </div>

        </div>

      </main>
    </div>
  );
}


/* ================= SUGGESTION COMPONENT ================= */

function Suggestion({ text, onClick }) {
  return (
    <button
      onClick={() => onClick(text)}
      className="rounded-xl border border-gray-200 bg-white p-4 text-left text-sm text-gray-700 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-md"
    >
      {text}
    </button>
  );
}

export default App;