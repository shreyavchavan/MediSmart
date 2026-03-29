import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function Home() {
    const navigate = useNavigate();

    return (
        <div className="App">
            <div className="container">
                <header className="header">
                    <h1 className="title">
                        <span className="icon">🏥</span>
                        Medical AI Assistant
                    </h1>
                    <p className="subtitle">
                        Your personal AI-powered medical companion
                    </p>
                </header>

                <div className="main-content selection-container">
                    <div className="selection-card" onClick={() => navigate('/extractor')}>
                        <div className="card-icon">💊</div>
                        <h2>Medicine Information</h2>
                        <p>Upload medicine images to extract detailed information about usage, dosage, and side effects.</p>
                        <button className="select-btn">Open Extractor</button>
                    </div>

                    <div className="selection-card" onClick={() => navigate('/chat')}>
                        <div className="card-icon">💬</div>
                        <h2>Medical Chatbot</h2>
                        <p>Chat with our AI assistant for general medical queries and health information.</p>
                        <button className="select-btn">Start Chat</button>
                    </div>

                    <div className="selection-card" onClick={() => navigate('/interactions')}>
                        <div className="card-icon">🤝</div>
                        <h2>Interaction Checker</h2>
                        <p>Check if taking multiple medicines together is safe and avoid harmful reactions.</p>
                        <button className="select-btn">Open Checker</button>
                    </div>
                </div>

                <footer className="footer">
                    <p>⚠️ This information is for educational purposes only. Always consult with a healthcare professional before taking any medication.</p>
                </footer>
            </div>
        </div>
    );
}

export default Home;
