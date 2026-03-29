import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import '../App.css';

const API_BASE_URL = 'http://localhost:8000';

function Chatbot() {
    const [messages, setMessages] = useState([
        { role: 'model', content: "Hello! I'm your medical AI assistant. How can I help you today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const navigate = useNavigate();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            // Prepare history excluding the last user message we just added (backend handles prompt)
            // actually backend expects history including latest? No, typically history is past context.
            // Let's send past history + current message param.
            // The backend implementation takes "history" list.

            const history = messages.map(m => ({ role: m.role, content: m.content }));

            const response = await axios.post(`${API_BASE_URL}/api/chat`, {
                message: input,
                history: history
            });

            const botMessage = { role: 'model', content: response.data.response };
            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { role: 'model', content: "Sorry, I encountered an error. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <div className="container">
                <button className="back-btn" onClick={() => navigate('/')}>← Back</button>

                <header className="header compact">
                    <h1 className="title small">
                        <span className="icon">💬</span>
                        Medical Chatbot
                    </h1>
                </header>

                <div className="main-content chat-container">
                    <div className="messages-area">
                        {messages.map((msg, index) => (
                            <div key={index} className={`message ${msg.role}`}>
                                <div className="message-content">
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="message model">
                                <div className="message-content typing">
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form className="chat-input-form" onSubmit={sendMessage}>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask a medical question..."
                            disabled={loading}
                        />
                        <button type="submit" disabled={loading || !input.trim()}>
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Chatbot;
