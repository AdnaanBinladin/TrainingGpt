"use client";

import { useState } from "react";

import { sendMessage } from "../services/api";

export default function ChatSection({ team }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  async function handleSend(event) {
    event.preventDefault();

    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return;
    }

    setMessages((current) => [...current, { role: "user", text: trimmedQuery }]);
    setQuery("");
    setError("");
    setIsSending(true);

    try {
      const data = await sendMessage(trimmedQuery, team);
      setMessages((current) => [
        ...current,
        { role: "bot", text: data.answer || data.response || "No response returned" },
      ]);
    } catch (error) {
      setError(error.message || "Request failed");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <section className="box">
      <h2>Chat Section</h2>
      <p className="status">Team: {team}</p>

      <div className="chat-list">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
            {message.text}
          </div>
        ))}
      </div>

      <form className="chat-form" onSubmit={handleSend}>
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask a question"
        />
        <button type="submit" disabled={isSending}>
          {isSending ? "Sending..." : "Send"}
        </button>
      </form>

      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
