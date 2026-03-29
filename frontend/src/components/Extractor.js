import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function Extractor() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [medicineData, setMedicineData] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setMedicineData(null);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(
        `${API_BASE_URL}/api/analyze-medicine`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setMedicineData(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Error processing image. Please try again.'
      );
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!medicineData) return;

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/generate-pdf`,
        medicineData,
        {
          responseType: 'blob',
        }
      );

      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `medicine_report_${new Date().getTime()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Error generating PDF. Please try again.');
      console.error('PDF generation error:', err);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setMedicineData(null);
    setError(null);
  };

  return (
    <div className="App">
      <div className="container">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        <header className="header">
          <h1 className="title">
            <span className="icon">💊</span>
            Medicine Information Extractor
          </h1>
          <p className="subtitle">
            Upload an image of a medicine strip, bottle, or package to get detailed information
          </p>
        </header>

        <div className="main-content">
          {!medicineData ? (
            <div className="upload-section">
              <div className="upload-card">
                <div className="upload-area">
                  {preview ? (
                    <div className="preview-container">
                      <img src={preview} alt="Preview" className="preview-image" />
                      <button className="change-image-btn" onClick={() => {
                        setSelectedFile(null);
                        setPreview(null);
                        document.getElementById('file-input').value = '';
                      }}>
                        Change Image
                      </button>
                    </div>
                  ) : (
                    <label htmlFor="file-input" className="upload-label">
                      <div className="upload-icon">📷</div>
                      <p className="upload-text">
                        Click to upload or drag and drop
                      </p>
                      <p className="upload-hint">
                        PNG, JPG, JPEG up to 10MB
                      </p>
                      <input
                        id="file-input"
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="file-input"
                      />
                    </label>
                  )}
                </div>

                {error && (
                  <div className="error-message">
                    ⚠️ {error}
                  </div>
                )}

                <button
                  className="analyze-btn"
                  onClick={handleUpload}
                  disabled={!selectedFile || loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Analyzing...
                    </>
                  ) : (
                    '🔍 Analyze Medicine'
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="results-section">
              <div className="results-header">
                <h2>Medicine Information</h2>
                <div className="action-buttons">
                  <button className="download-btn" onClick={handleDownloadPDF}>
                    📥 Download PDF Report
                  </button>
                  <button className="reset-btn" onClick={handleReset}>
                    🔄 Analyze Another
                  </button>
                </div>
              </div>

              <div className="medicine-info">
                <div className="info-card highlight">
                  <h3>Medicine Name</h3>
                  <p className="medicine-name">
                    {medicineData.medicine_info.medicine_name}
                  </p>
                </div>

                <div className="info-grid">
                  <div className="info-card">
                    <h3>📋 Active Ingredients</h3>
                    <ul>
                      {medicineData.medicine_info.active_ingredients.map((ing, idx) => (
                        <li key={idx}>{ing}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="info-card">
                    <h3>🏥 Medical Uses</h3>
                    <ul>
                      {medicineData.medicine_info.uses.map((use, idx) => (
                        <li key={idx}>{use}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="info-card">
                    <h3>⚠️ Side Effects</h3>
                    <ul>
                      {medicineData.medicine_info.side_effects.map((effect, idx) => (
                        <li key={idx}>{effect}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="info-card">
                    <h3>👥 Age Recommendation</h3>
                    <p>{medicineData.medicine_info.age_recommendation}</p>
                  </div>

                  <div className="info-card">
                    <h3>💉 Dosage</h3>
                    <p>{medicineData.medicine_info.dosage}</p>
                  </div>

                  {medicineData.medicine_info.warnings &&
                    medicineData.medicine_info.warnings.length > 0 && (
                      <div className="info-card warning">
                        <h3>🚨 Warnings & Precautions</h3>
                        <ul>
                          {medicineData.medicine_info.warnings.map((warning, idx) => (
                            <li key={idx}>{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {medicineData.medicine_info.storage && (
                    <div className="info-card">
                      <h3>📦 Storage Instructions</h3>
                      <p>{medicineData.medicine_info.storage}</p>
                    </div>
                  )}

                  {medicineData.medicine_info.manufacturer && (
                    <div className="info-card">
                      <h3>🏭 Manufacturer</h3>
                      <p>{medicineData.medicine_info.manufacturer}</p>
                    </div>
                  )}

                  {(medicineData.medicine_info.batch_number || medicineData.medicine_info.expiry_date) && (
                    <div className="info-card">
                      <h3>📅 Batch & Expiry</h3>
                      {medicineData.medicine_info.batch_number && (
                        <p><strong>Batch:</strong> {medicineData.medicine_info.batch_number}</p>
                      )}
                      {medicineData.medicine_info.expiry_date && (
                        <p><strong>Expiry:</strong> {medicineData.medicine_info.expiry_date}</p>
                      )}
                    </div>
                  )}
                </div>

                {preview && (
                  <div className="preview-section">
                    <h3>Uploaded Image</h3>
                    <img src={preview} alt="Medicine" className="result-image" />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>⚠️ This information is for educational purposes only. Always consult with a healthcare professional before taking any medication.</p>
        </footer>
      </div>
    </div>
  );
}

export default Extractor;

