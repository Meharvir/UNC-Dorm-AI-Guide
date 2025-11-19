import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/query";

async function sendMessageToBackend(message) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error("Backend error");
  }

  return res.json();
}

function App() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hi! I’m the UNC Dorm Guide. Tell me what you’re looking for in a dorm.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const newMessages = [
      ...messages,
      { sender: "user", text: trimmed },
    ];

    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendMessageToBackend(trimmed);
      const botText = data.response || "Sorry, I couldn't generate a response.";
      setMessages([
        ...newMessages,
        { sender: "bot", text: botText },
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          sender: "bot",
          text: "Oops — I couldn’t reach the server. Try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>UNC Dorm Guide</h1>
        <p>Find your ideal UNC first-year dorm through conversation.</p>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`message-row ${
                m.sender === "user" ? "user-row" : "bot-row"
              }`}
            >
              <div className={`bubble ${m.sender}`}>
                {m.text}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-row bot-row">
              <div className="bubble bot">Thinking…</div>
            </div>
          )}
        </div>

        <form className="input-row" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Describe your ideal dorm..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;
