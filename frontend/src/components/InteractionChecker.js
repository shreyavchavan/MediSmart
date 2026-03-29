import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

function InteractionChecker() {
    const navigate = useNavigate();
    const [medicines, setMedicines] = useState(['', '']);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleAddMedicine = () => {
        setMedicines([...medicines, '']);
    };

    const handleRemoveMedicine = (index) => {
        if (medicines.length > 2) {
            const newMedicines = medicines.filter((_, i) => i !== index);
            setMedicines(newMedicines);
        }
    };

    const handleMedicineChange = (index, value) => {
        const newMedicines = [...medicines];
        newMedicines[index] = value;
        setMedicines(newMedicines);
    };

    const checkInteractions = async () => {
        const filteredMedicines = medicines.filter(m => m.trim() !== '');
        if (filteredMedicines.length < 2) {
            setError('Please enter at least two medicine names.');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('http://localhost:8000/api/check-interactions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ medicines: filteredMedicines }),
            });

            if (!response.ok) {
                throw new Error('Failed to check interactions. Please try again.');
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity.toLowerCase()) {
            case 'dangerous': return '#ff4d4d';
            case 'caution': return '#ffa500';
            case 'safe': return '#4caf50';
            default: return '#666';
        }
    };

    return (
        <div className="App">
            <div className="container">
                <header className="header">
                    <button className="back-btn" onClick={() => navigate('/')}>← Home</button>
                    <h1 className="title">
                        <span className="icon">🤝</span>
                        Interaction Checker
                    </h1>
                    <p className="subtitle">
                        Check if taking multiple medicines together is safe
                    </p>
                </header>

                <div className="main-content">
                    <div className="interaction-form-card">
                        <h3>Enter Medicines</h3>
                        {medicines.map((medicine, index) => (
                            <div key={index} className="medicine-input-group">
                                <input
                                    type="text"
                                    placeholder={`Medicine ${index + 1}`}
                                    value={medicine}
                                    onChange={(e) => handleMedicineChange(index, e.target.value)}
                                    className="medicine-input"
                                />
                                {medicines.length > 2 && (
                                    <button 
                                        className="remove-btn" 
                                        onClick={() => handleRemoveMedicine(index)}
                                        title="Remove"
                                    >
                                        ✕
                                    </button>
                                )}
                            </div>
                        ))}
                        
                        <div className="form-actions">
                            <button className="add-btn" onClick={handleAddMedicine}>
                                + Add Another
                            </button>
                            <button 
                                className="check-btn" 
                                onClick={checkInteractions}
                                disabled={loading}
                            >
                                {loading ? 'Checking...' : 'Check Interactions'}
                            </button>
                        </div>

                        {error && <div className="error-message">{error}</div>}
                    </div>

                    {result && (
                        <div className="results-container">
                            <div className={`overall-status-card ${result.overall_status.toLowerCase()}`}>
                                <h2>Overall Status: {result.overall_status}</h2>
                            </div>

                            <div className="interactions-list">
                                {result.interactions.map((interaction, index) => (
                                    <div key={index} className="interaction-detail-card">
                                        <div 
                                            className="severity-tag" 
                                            style={{ backgroundColor: getSeverityColor(interaction.severity) }}
                                        >
                                            {interaction.severity}
                                        </div>
                                        <p className="explanation"><strong>Explanation:</strong> {interaction.explanation}</p>
                                        
                                        {interaction.harmful_effects && interaction.harmful_effects.length > 0 && (
                                            <div className="harmful-effects">
                                                <strong>Harmful Effects:</strong>
                                                <ul>
                                                    {interaction.harmful_effects.map((effect, i) => (
                                                        <li key={i}>{effect}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        
                                        <div className="advice-box">
                                            <strong>Advice:</strong> {interaction.advice}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="disclaimer-info">
                                <p>{result.disclaimer}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default InteractionChecker;
