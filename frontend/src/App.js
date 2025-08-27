// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

import './App.css';
import InstagramLogo from './instagram-logo.svg';
import XLogo from './x-logo.svg';
import Logo from './logo.svg';

function App() {
  const [username, setUsername] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('dark-mode', isDarkMode);
  }, [isDarkMode]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', {
        username: username,
        platform: platform,
        model_choice: 'xgboost',
      });
      setResult(response.data);
    } catch (err) {
      if (err.response && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Could not connect to the server. Is it running?');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <motion.button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="mode-toggle"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </motion.button>
      </div>

      <motion.div
        className="card"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="title-container">
          <img src={Logo} alt="Fake Buster Logo" className="logo-main" />
          <h1>Fake Buster</h1>
        </div>
        <p className="subtitle">Analyze any public Instagram or X profile.</p>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Platform</label>
            <div className="radio-group">
              <label className={platform === 'instagram' ? 'selected' : ''}>
                <input type="radio" name="platform" value="instagram" checked={platform === 'instagram'} onChange={(e) => setPlatform(e.target.value)} />
                Instagram
              </label>
              <label className={platform === 'x' ? 'selected' : ''}>
                <input type="radio" name="platform" value="x" checked={platform === 'x'} onChange={(e) => setPlatform(e.target.value)} />
                Twitter / X
              </label>
            </div>
          </div>

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

          <motion.button type="submit" disabled={isLoading} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            {isLoading ? 'Analyzing...' : 'Analyze Profile'}
          </motion.button>
        </form>

        <AnimatePresence>
          {isLoading && (
            <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}>
              <div className="loader"></div>
            </motion.div>
          )}

          {error && (
            <motion.div className="result-container error" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <p>{error}</p>
            </motion.div>
          )}

          {result && (
            <motion.div className="result-container" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <h3>Prediction: <span className={result.prediction === 'Fake' ? 'fake' : 'real'}>{result.prediction}</span></h3>
              <p>Confidence: {result.confidence_percent}%</p>
                  <div className="download-button-container">
      <button 
        onClick={async () => {
          try {
            const response = await axios.post('http://127.0.0.1:5000/generate-report', result, {
              responseType: 'blob', // Important: tells axios to expect a file
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `FakeBuster_Report_${result.username}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
          } catch (error) {
            console.error("Could not download the report.", error);
            setError("Failed to generate PDF report.");
          }
        }}
        className="download-button"
      >
        Download Report 📄
      </button>
    </div>
              {result.ai_analysis && (
                <div className="ai-analysis">
                  <h4>AI Analyst Report</h4>
                  <div className="ai-analysis-grid">
                    <div className="analysis-summary">
                      <h5>Summary</h5>
                      <ReactMarkdown>{result.ai_analysis.split('Points of Caution')[0]}</ReactMarkdown>
                    </div>
                    <div className="analysis-caution">
                      <h5>Points of Caution</h5>
                      <ReactMarkdown>{result.ai_analysis.includes('Points of Caution') ? result.ai_analysis.split('Points of Caution')[1] : 'None'}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <div className="footer">
        <p>Made with ❤️ by rushstatic</p>
        <div className="logo-container">
          <AnimatePresence>
            {platform === 'instagram' && (<motion.img src={InstagramLogo} alt="Instagram" className="logo" initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.5 }} transition={{ duration: 0.3 }} />)}
            {platform === 'x' && (<motion.img src={XLogo} alt="Twitter/X" className="logo" initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.5 }} transition={{ duration: 0.3 }} />)}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App;