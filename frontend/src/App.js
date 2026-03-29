import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Extractor from './components/Extractor';
import Chatbot from './components/Chatbot';
import InteractionChecker from './components/InteractionChecker';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/extractor" element={<Extractor />} />
        <Route path="/chat" element={<Chatbot />} />
        <Route path="/interactions" element={<InteractionChecker />} />
      </Routes>
    </Router>
  );
}

export default App;
