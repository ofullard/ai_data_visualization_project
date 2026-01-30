import { useMemo, useState } from "react";
import "./App.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: string;
};

const seedMessages: Message[] = [
  {
    id: "m1",
    role: "assistant",
    text: "Hi! Ask me about your data or type a question to generate insights.",
    timestamp: new Date().toLocaleTimeString()
  }
];

const samplePrompts = [
  "Summarize today’s chat traffic.",
  "What are the top 3 themes?",
  "Generate a quick data insight."
];

function createAssistantReply(input: string): string {
  return `Here is a quick AI insight based on your prompt: "${input}". Try the Streamlit app for live analytics.`;
}

function App() {
  const [messages, setMessages] = useState<Message[]>(seedMessages);
  const [draft, setDraft] = useState("");

  const handleSend = () => {
    if (!draft.trim()) return;
    const time = new Date().toLocaleTimeString();
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: draft.trim(),
      timestamp: time
    };
    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      text: createAssistantReply(draft.trim()),
      timestamp: time
    };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setDraft("");
  };

  const chartData = useMemo(() => {
    const lastMessages = messages.slice(-6);
    return lastMessages.map((message, index) => ({
      label: `${index + 1}`,
      value: Math.min(message.text.length, 60),
      role: message.role
    }));
  }, [messages]);

  return (
    <div className="app">
      <header className="header">
        <div>
          <p className="eyebrow">AI Chat + Data Visualization</p>
          <h1>Messaging Studio</h1>
          <p className="subtitle">
            React front-end for chat flow and quick insights.
          </p>
        </div>
        <div className="prompt-group">
          {samplePrompts.map((prompt) => (
            <button
              key={prompt}
              className="prompt"
              onClick={() => setDraft(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </header>

      <main className="layout">
        <section className="panel chat-panel">
          <h2>Chat</h2>
          <div className="chat-window">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                <div className="message-meta">
                  <span className="role">{message.role}</span>
                  <span className="time">{message.timestamp}</span>
                </div>
                <p>{message.text}</p>
              </div>
            ))}
          </div>
          <div className="composer">
            <textarea
              placeholder="Type a message..."
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              rows={3}
            />
            <button className="send" onClick={handleSend}>
              Send
            </button>
          </div>
        </section>

        <section className="panel viz-panel">
          <h2>Message Length Insights</h2>
          <p className="muted">
            Each bar represents the character count of the most recent messages.
          </p>
          <div className="chart">
            {chartData.map((item) => (
              <div key={item.label} className="chart-row">
                <span className="chart-label">{item.label}</span>
                <div className="chart-bar">
                  <div
                    className={`chart-fill ${item.role}`}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
                <span className="chart-value">{item.value}</span>
              </div>
            ))}
          </div>
          <div className="footer-note">
            Use the Streamlit app for live analytics dashboards.
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
