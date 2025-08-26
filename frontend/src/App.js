// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {

  const [username, setUsername] = useState('');
  const [platform, setPlatform] = useState('instagram'); 
  const [modelChoice, setModelChoice] = useState('xgboost'); 
  
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {

      const response = await axios.post('http://127.0.0.1:5000/predict', {
        username: username,
        platform: platform,
        model_choice: modelChoice,
      });
      setResult(response.data);
    } catch (err) {

      if (err.response && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Could not connect to the server. Is it running?');
      }
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Fake Account Detector</h1>
        <p>Enter a username and select a platform to analyze its authenticity.</p>
        
        <form onSubmit={handleSubmit}>
          {/* Platform Selection */}
          <div className="input-group">
            <label>Platform</label>
            <div className="radio-group">
              <label>
                <input type="radio" value="instagram" checked={platform === 'instagram'} onChange={(e) => setPlatform(e.target.value)} />
                Instagram
              </label>
              <label>
                <input type="radio" value="x" checked={platform === 'x'} onChange={(e) => setPlatform(e.target.value)} />
                Twitter / X
              </label>
            </div>
          </div>
          
          {/* Username Input */}
          <div className="input-group">
            <label htmlFor="username-input">Username</label>
            <input
              id="username-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username to analyze..."
              required
            />
          </div>

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze Profile'}
          </button>
        </form>

        {/* --- Result and Error Display --- */}
        {isLoading && <div className="loader"></div>}

        {error && (
          <div className="result-container error">
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <h3>Prediction: <span className={result.prediction === 'Fake' ? 'fake' : 'real'}>{result.prediction}</span></h3>
            <p>Confidence: {result.confidence_percent}%</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
