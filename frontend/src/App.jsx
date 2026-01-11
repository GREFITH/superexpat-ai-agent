// frontend/src/App.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Calendar, MapPin, ExternalLink, DollarSign, Briefcase, MessageSquare, Clock, Sparkles } from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (queryText) => {
    const finalQuery = queryText || input;
    if (!finalQuery.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: finalQuery,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: finalQuery,
          page: 1,
          page_size: 20
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        timestamp: new Date().toISOString(),
        data: data
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error:', err);
      
      const errorMessage = {
        role: 'assistant',
        timestamp: new Date().toISOString(),
        error: true,
        content: `Connection error: ${err.message}. Please make sure the backend is running.`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const EventCard = ({ event }) => {
    const displayDate = event.start_date 
      ? formatDate(event.start_date)
      : "Date To Be Announced";

    const isDateUnknown = !event.start_date;
    const [imageError, setImageError] = useState(false);

    return (
      <div className="event-card">
        <div className="event-poster">
          {event.poster && !imageError ? (
            <img 
              src={event.poster} 
              alt={event.title}
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="no-image-placeholder">
              {event.type === 'job' ? <Briefcase size={48} /> : <Calendar size={48} />}
            </div>
          )}
        </div>
        
        <div className="event-content">
          <span className="event-type-badge">
            {event.type === 'job' ? '💼 Job' : '🎉 Event'}
          </span>
          
          <h4 className="event-title">{event.title}</h4>
          
          <div className="event-details">
            <div className="event-detail">
              <Calendar size={16} />
              <span className={isDateUnknown ? 'date-tba' : ''}>
                {displayDate}
              </span>
            </div>
            
            {event.start_time && !isDateUnknown && (
              <div className="event-detail">
                <Clock size={16} />
                <span>{event.start_time}</span>
              </div>
            )}
            
            {event.venue && (
              <div className="event-detail">
                <MapPin size={16} />
                <span>{event.venue}</span>
              </div>
            )}
            
            {event.company && (
              <div className="event-detail">
                <Briefcase size={16} />
                <span>{event.company}</span>
              </div>
            )}
            
            {event.address && !event.venue && (
              <div className="event-detail">
                <MapPin size={16} />
                <span className="event-address">{event.address}</span>
              </div>
            )}
            
            {event.price && (
              <div className="event-detail">
                <DollarSign size={16} />
                <span>{event.price}</span>
              </div>
            )}
          </div>

          <div className="event-footer">
            {event.url && (
              <a 
                href={event.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="event-link"
              >
                View Details <ExternalLink size={14} />
              </a>
            )}
          </div>
        </div>
      </div>
    );
  };

  const AssistantMessage = ({ message }) => {
    if (message.error) {
      return (
        <div className="message assistant">
          <div className="message-content">
            <div className="message-header">
              <span className="message-role">AI Assistant</span>
              <span className="message-time">{formatTimestamp(message.timestamp)}</span>
            </div>
            <p className="message-text error-text">{message.content}</p>
          </div>
        </div>
      );
    }

    if (!message.data) {
      return null;
    }

    const { total_results, results, ai_summary } = message.data;

    return (
      <div className="message assistant">
        <div className="message-content assistant-response">
          <div className="message-header">
            <span className="message-role">AI Assistant</span>
            <span className="message-time">{formatTimestamp(message.timestamp)}</span>
          </div>

          {/* AI Summary Section */}
          {ai_summary && (
            <div className="ai-summary-box">
              <div className="ai-summary-header">
                <Sparkles size={16} />
                <span>AI Summary</span>
              </div>
              <p className="ai-summary-text">{ai_summary}</p>
            </div>
          )}

        {!ai_summary && (
  <div className="response-summary">
    <p>
      I found <strong>{total_results}</strong> result{total_results !== 1 ? 's' : ''} for you
    </p>
  </div>
)}

          {results && results.length > 0 ? (
            <div className="events-grid">
              {results.map((event, idx) => (
                <EventCard key={event.id || idx} event={event} />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <MessageSquare size={32} opacity={0.3} />
              <p>No results found. Try a different search.</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <div className="container">
        <div className="card">
          {/* Header */}
          <div className="header">
            <h1>SuperExpat AI Agent System</h1>
            <p className="subtitle">Find Events & Jobs Worldwide with AI-Powered Search</p>
          </div>

          {/* Chat Content */}
          <div className="content">
            <div className="chat-container">
              <div className="messages">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <MessageSquare size={48} />
                    <h3>Welcome to SuperExpat AI Assistant</h3>
                    <p>Find events, jobs, and opportunities anywhere in the world powered by AI!</p>
                    <div className="sample-queries">
                      <button onClick={() => handleSendMessage('events in London')}>
                        Events in London
                      </button>
                      <button onClick={() => handleSendMessage('jobs in Berlin')}>
                        Jobs in Berlin
                      </button>
                      <button onClick={() => handleSendMessage('concerts in New York')}>
                        Concerts in New York
                      </button>
                      <button onClick={() => handleSendMessage('festivals in Paris')}>
                        Festivals in Paris
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((msg, idx) => (
                      msg.role === 'user' ? (
                        <div key={idx} className="message user">
                          <div className="message-content">
                            <div className="message-header">
                              <span className="message-role">You</span>
                              <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
                            </div>
                            <p className="message-text">{msg.content}</p>
                          </div>
                        </div>
                      ) : (
                        <AssistantMessage key={idx} message={msg} />
                      )
                    ))}
                    {loading && (
                      <div className="message assistant">
                        <div className="message-content">
                          <div className="typing-indicator">
                            <Loader2 className="spin" size={20} />
                            <span>Searching with AI...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input */}
              <div className="input-container">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Try: 'events in London' or 'jobs in Berlin'"
                  disabled={loading}
                  className="input-field"
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={loading || !input.trim()}
                  className="send-button"
                >
                  {loading ? <Loader2 className="spin" size={20} /> : <Send size={20} />}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="footer">
          <p>SuperExpat AI Agent - Powered by FastAPI + React + Gemini AI + SerpAPI</p>
        </div>
      </div>
    </div>
  );
}

export default App;