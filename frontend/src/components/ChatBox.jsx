import React, { useState } from "react";
import axios from "axios";

export default function ChatBox({ filename, onCitationClick, setCitationPage, setHighlights }) {
  const [messages, setMessages] = useState([]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !filename) return;
    setLoading(true);
    setMessages((msgs) => [...msgs, { user: true, text: input }]);
    try {
      const res = await axios.post("/chat", { query: input, filename });
      if (typeof res.data.answer === "string") {
        setMessages((msgs) => [
          ...msgs,
          { user: false, text: res.data.answer, citations: res.data.citations || [] },
        ]);
      } else {
        console.error('Unexpected /chat response:', res.data);
        setMessages((msgs) => [
          ...msgs,
          { user: false, text: "Error: Unexpected response from server.", citations: [] },
        ]);
      }
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { user: false, text: "Error: " + (err.response?.data?.detail || err.message) },
      ]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto p-4 space-y-2">
        {messages.map((msg, i) => (
          <div key={i} className={msg.user ? "text-right" : "text-left"}>
            <div className={msg.user ? "bg-blue-100 inline-block px-2 py-1 rounded" : "bg-gray-200 inline-block px-2 py-1 rounded"}>
              {msg.text}
              {msg.citations && msg.citations.length > 0 && (
                <div className="flex flex-row gap-2 mt-2">
                  {msg.citations.map((c, j) => (
                    <span
                      key={j}
                      className="w-6 h-6 flex items-center justify-center rounded-full bg-blue-500 text-white text-xs font-bold cursor-pointer shadow hover:bg-blue-700 transition"
                      title={c.text || `Page ${c.page_numbers?.[0]}`}
                      onClick={() => {
                        if (onCitationClick) onCitationClick(c);
                        if (setCitationPage) setCitationPage(c.page);
                        if (setHighlights) setHighlights([c]);
                      }}
                    >
                      {j + 1}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-400">Loading...</div>}
      </div>
      <form className="p-2 border-t flex" onSubmit={sendMessage}>
        <input
          className="flex-1 border rounded px-2 py-1 mr-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={filename ? "Ask a question..." : "Upload a document first"}
          disabled={!filename || loading}
        />
        <button type="submit" className="bg-green-600 text-white px-4 py-1 rounded" disabled={!filename || loading}>
          Send
        </button>
      </form>
    </div>
  );
}
