"use client";

import React, { useState, useRef, useEffect } from 'react';

type Source = {
  chunk: string;
  source: string;
};

export default function Home() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [hasAsked, setHasAsked] = useState(false);
  const [error, setError] = useState('');
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [answer, sources, isStreaming, error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isStreaming) return;

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setAnswer('');
    setSources([]);
    setError('');
    setIsStreaming(true);
    setHasAsked(true);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const streamUrl = `${apiUrl}/ask/stream?q=${encodeURIComponent(question)}`;

    const eventSource = new EventSource(streamUrl);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Invalid JSON:", event.data);
        return;
      }

      if (data.type === 'sources') {
        setSources(data.sources);
      } else if (data.type === 'token') {
        setAnswer((prev) => prev + data.text);
      } else if (data.type === 'done') {
        eventSource.close();
        setIsStreaming(false);
      }
    };

    eventSource.onerror = (err: Event) => {
      console.error('SSE Error:', err);
      setError("Something went wrong. Try again.");
      eventSource.close();
      setIsStreaming(false);
    };
  };

  return (
    <main className="container">
      <h1>Knowledge Assistant</h1>
      
      <div className="chat-box" ref={scrollRef}>
        {!hasAsked ? (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem', color: '#60a5fa' }}>
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 16v-4"></path>
              <path d="M12 8h.01"></path>
            </svg>
            <h2>Ask any question</h2>
            <p>I will search the knowledge base and construct an answer.</p>
          </div>
        ) : (
          <div className="answer-section">
            {error && <div className="error">{error}</div>}
            
            {isStreaming && !answer && !error && (
              <div className="loading">Generating answer...</div>
            )}
            
            <div className="answer-text">
              {answer}
              {isStreaming && <span className="cursor"></span>}
            </div>

            {sources.length > 0 && (
              <div className="sources-container">
                <div className="sources-title">Retrieved Sources</div>
                {sources.map((src: Source, i: number) => (
                  <div key={i} className="source-item">
                    <span className="source-name">{src.source}</span>
                    <span className="source-chunk">"{src.chunk}"</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <input
          ref={inputRef}
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What do you want to know?"
          className="input-field"
          disabled={isStreaming}
        />
        <button type="submit" className="submit-btn" disabled={isStreaming || !question.trim()}>
          {isStreaming ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </main>
  );
}
