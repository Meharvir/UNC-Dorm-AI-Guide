import { useState, useEffect } from "react";
import "./App.css";

// Backend URL
const API_URL = "http://127.0.0.1:8002/query";

async function sendMessageToBackend(message, expand = false) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, expand }),
  });

  if (!res.ok) {
    const text = await res.text();
    console.error("Backend error:", res.status, text);
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json();
}

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! I'm the UNC Dorm Guide. Tell me what you're looking for in a dorm.", id: 0 },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [showSessions, setShowSessions] = useState(false);
  const [expandedMessages, setExpandedMessages] = useState(new Set());

  const quickFilters = [
    "Quiet dorm close to classes",
    "Very social dorm with lots of people",
    "Suite-style dorm near the gym",
    "Dorm close to Franklin Street",
    "Dorm with good dining",
    "Close to medical school",
  ];

  // Load sessions from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("dormSessions");
    if (saved) setSessions(JSON.parse(saved));
  }, []);

  // Persist sessions
  useEffect(() => {
    localStorage.setItem("dormSessions", JSON.stringify(sessions));
  }, [sessions]);

  // Save messages in current session
  useEffect(() => {
    if (!currentSessionId) return;
    setSessions(prev =>
      prev.map(s => (s.id === currentSessionId ? { ...s, messages } : s))
    );
  }, [messages, currentSessionId]);

  // Send message
  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const newMessages = [
      ...messages,
      { sender: "user", text: trimmed, id: messages.length },
    ];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const data = await sendMessageToBackend(trimmed, false);
      const botText = data.response || "Sorry, I couldn't generate a response.";
      setMessages([
        ...newMessages,
        { sender: "bot", text: botText, id: newMessages.length, fullText: botText },
      ]);
    } catch (err) {
      console.error(err);
      setMessages([
        ...newMessages,
        {
          sender: "bot",
          text: "Oops — I couldn't reach the server. Try again in a moment.",
          id: newMessages.length,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Expand message to show full content
  const handleExpandMessage = async (messageId) => {
    if (expandedMessages.has(messageId)) {
      // Collapse
      setExpandedMessages(prev => {
        const newSet = new Set(prev);
        newSet.delete(messageId);
        return newSet;
      });
      return;
    }

    // Find the user's original question
    const messageIndex = messages.findIndex(m => m.id === messageId);
    const userMessage = messageIndex > 0 ? messages[messageIndex - 1] : null;
    
    if (!userMessage || userMessage.sender !== "user") return;

    // Request expanded version
    setIsLoading(true);
    try {
      const data = await sendMessageToBackend(userMessage.text, true);
      const expandedText = data.response || messages.find(m => m.id === messageId).text;
      
      setMessages(prev =>
        prev.map(m =>
          m.id === messageId ? { ...m, fullText: expandedText } : m
        )
      );
      
      setExpandedMessages(prev => new Set(prev).add(messageId));
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Quick filter input
  const handleQuickFilterClick = (text) => setInput(text);

  // Start a new chat session
  const startNewSession = () => {
    const newSession = {
      id: Date.now(),
      title: `Chat ${new Date().toLocaleString()}`,
      messages: [
        {
          sender: "bot",
          text: "Hi! I'm the UNC Dorm Guide. Tell me what you're looking for in a dorm.",
          id: 0,
        },
      ],
      createdAt: new Date().toISOString(),
    };
    setSessions([newSession, ...sessions]);
    setCurrentSessionId(newSession.id);
    setMessages(newSession.messages);
    setExpandedMessages(new Set());
  };

  // Load a saved session
  const loadSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSessionId(sessionId);
      setMessages(session.messages);
      setSearchQuery("");
      setExpandedMessages(new Set());
    }
  };

  // Delete a session
  const deleteSession = (sessionId) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
      setMessages([
        { sender: "bot", text: "Hi! I'm the UNC Dorm Guide. Tell me what you're looking for in a dorm.", id: 0 },
      ]);
      setExpandedMessages(new Set());
    }
  };

  // Filtered messages for search
  const filteredMessages = messages.filter(m =>
    m.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Check if message is truncated
  const isTruncated = (text) => {
    return text.includes('...') || text.includes('Want a breakdown of each? 👇');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-top">
          <h1>UNC Dorm Guide</h1>
          <div className="header-buttons">
            <button
              className="sessions-toggle"
              onClick={() => setShowSessions(!showSessions)}
              title="View saved chats"
            >
              💬
            </button>
            <button className="new-chat-btn" onClick={startNewSession}>
              + New Chat
            </button>
          </div>
        </div>
        <p>Find your ideal UNC first-year dorm through conversation.</p>

        {showSessions && (
          <div className="sessions-panel">
            <h3>Saved Chats</h3>
            {sessions.length === 0 ? (
              <p className="no-sessions">No saved chats yet</p>
            ) : (
              <div className="sessions-list">
                {sessions.map(s => (
                  <div key={s.id} className="session-item">
                    <button
                      className={`session-title ${currentSessionId === s.id ? "active" : ""}`}
                      onClick={() => loadSession(s.id)}
                    >
                      {s.title}
                    </button>
                    <button
                      className="session-delete"
                      onClick={() => deleteSession(s.id)}
                      title="Delete chat"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="quick-filters">
          {quickFilters.map(q => (
            <button
              key={q}
              type="button"
              className="quick-filter-chip"
              onClick={() => handleQuickFilterClick(q)}
            >
              {q}
            </button>
          ))}
        </div>
      </header>

      <div className="main-layout">
        <main className="chat-container">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="messages">
            {filteredMessages.map((m, idx) => (
              <div
                key={idx}
                className={`message-row ${m.sender === "user" ? "user-row" : "bot-row"}`}
              >
                <div className="message-content">
                  <div className={`bubble ${m.sender}`}>
                    {expandedMessages.has(m.id) && m.fullText ? m.fullText : m.text}
                  </div>
                  {m.sender === "bot" && isTruncated(m.text) && (
                    <button
                      className="expand-btn"
                      onClick={() => handleExpandMessage(m.id)}
                      disabled={isLoading}
                    >
                      {expandedMessages.has(m.id) ? "Show less" : "Show more"}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message-row bot-row">
                <div className="bubble bot typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
          </div>

          <form className="input-row" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Describe your ideal dorm..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              Send
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}

export default App;