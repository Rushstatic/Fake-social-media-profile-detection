// src/App.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import {
  FaInstagram, FaUserCircle, FaHome, FaCompass, FaBox, FaBell, FaCog, FaPlus, FaFilePdf, FaHistory, FaChevronDown, FaChevronUp
} from 'react-icons/fa';
import { BsTwitterX } from 'react-icons/bs';
import CountUp from 'react-countup';

import "./App.css";


// =================================================================================
//  NEW, MINIMALIST COMPONENTS
// =================================================================================

// Replace your entire existing Sidebar component with this new one
const Sidebar = ({ history }) => {

  const [isHistoryVisible, setIsHistoryVisible] = useState(true);

  return (

    <nav className="sidebar">
      <div className="sidebar-top">
        <a href="/" className="sidebar-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
            <path d="M2 7L12 12L22 7" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
            <path d="M12 12V22" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
          </svg>
        </a>
        <button className="sidebar-button"><FaPlus /></button>
        <div className="sidebar-links">
          <a href="/" className="sidebar-link active"><FaHome /><span>Home</span></a>

          {/* START: This is the new expandable history section */}
          <div className="history-section">
            <button className="sidebar-link history-header" onClick={() => setIsHistoryVisible(!isHistoryVisible)}>
              <FaHistory />
              <span>Recent</span>
              {isHistoryVisible ? <FaChevronUp className="chevron-icon" /> : <FaChevronDown className="chevron-icon" />}
            </button>
            {isHistoryVisible && (
              <div className="history-list">
                {Array.isArray(history) && history.length > 0 ? (
                  history.map((item, index) => (
                    <div key={index} className="history-item">
                      <span className={`history-dot ${item.prediction === 'Fake' ? 'fake' : 'real'}`}></span>
                      <span className="history-username">{item.username}</span>
                    </div>
                  ))
                ) : (
                  <span className="history-empty">No searches yet.</span>
                )}
              </div>
            )}
          </div>
          {/* END: New expandable history section */}

          <a href="/" className="sidebar-link"><FaBox /><span>Spaces</span></a>
        </div>
      </div>
      <div className="sidebar-bottom">
        <a href="/" className="sidebar-link"><FaBell /><span>Notifications</span></a>
        <a href="/" className="sidebar-link"><FaCog /><span>Settings</span></a>
        <a href="/" className="sidebar-link"><FaUserCircle /><span>Account</span></a>
      </div>
    </nav>
  );
};

// Make sure the main App component is still passing the history prop correctly
// No changes are needed in the App component itself, just in the Sidebar

const AnalysisForm = ({ onSubmit, isLoading }) => {
  const [username, setUsername] = useState("");
  const [platform, setPlatform] = useState("instagram");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      onSubmit({ username, platform });
    }
  };

  return (
    <div className="analysis-form-container">
      <h1 className="main-logo">fakebuster</h1>
      <form onSubmit={handleSubmit} className="analysis-form">
        <div className={`input-wrapper ${username ? 'has-content' : ''}`}>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Analyze a social media profile..."
            required
          />
          <button type="submit" disabled={isLoading || !username.trim()} className="analyze-button">
            {isLoading ? "..." : "Analyze"}
          </button>
        </div>
        <div className="platform-switcher">
          <span className="switcher-label">Platform:</span>
          <button
            type="button"
            className={`platform-chip ${platform === 'instagram' ? 'active' : ''}`}
            onClick={() => setPlatform('instagram')}
          >
            <FaInstagram /> Instagram
          </button>
          <button
            type="button"
            className={`platform-chip ${platform === 'x' ? 'active' : ''}`}
            onClick={() => setPlatform('x')}
          >
            <BsTwitterX /> X
          </button>
        </div>
      </form>
    </div>
  );
};

/**
 * A clean, simple component to display a single result.
 * NOW INCLUDES THE onDownload PROP AND BUTTON.
 */
const AnalysisResult = ({ result, onDownload }) => {
  const isFake = result.prediction === "Fake";
  return (
    <div className={`analysis-result ${isFake ? 'fake' : 'real'}`}>
      <div className="result-header">
        <div className="result-title">
          <h4>@{result.username}</h4>
          <span className={`prediction-pill ${isFake ? 'fake' : 'real'}`}>{result.prediction}</span>
          <span className="prediction-percent">{result.confidence_percent}%</span>
        </div>
        <button className="download-button" onClick={() => onDownload(result)}>
          <FaFilePdf />
        </button>
      </div>
      <div className="result-body">
        <ReactMarkdown>{result.ai_analysis}</ReactMarkdown>
      </div>
    </div>
  );
};




// =================================================================================
//  MAIN APP COMPONENT
// =================================================================================
// Replace your entire existing App function with this one

function App() {

  const LoadingIndicator = () => (
    <div className="loading-indicator">
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
    </div>
  );
  // FIX 1: Changed state to handle a single result object, not an array
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });

  const fetchHistory = async () => {
    try {
      const response = await axios.get("https://fakebuster-backend.onrender.com/recent-searches");
      setHistory(response.data);
      localStorage.setItem('searchHistory', JSON.stringify(response.data));
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleAnalyzeSubmit = async ({ username, platform }) => {
    setIsLoading(true);
    setError(null);
    // FIX 1: Using the correct 'setResult' function
    setResult(null);
    try {
      const response = await axios.post("https://fakebuster-backend.onrender.com/predict", { username, platform });
      const newResult = { ...response.data, id: Date.now() };
      // FIX 1: Using the correct 'setResult' function
      setResult(newResult);
      fetchHistory();
    } catch (err) {
      const errorMessage = err.response?.data?.error || "Could not connect to the analysis server.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadReport = async (profileData) => {
    try {
      const response = await axios.post("https://fakebuster-backend.onrender.com/generate-report", profileData, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `FakeBuster_Report_${profileData.username}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch {
      alert("Failed to generate PDF report.");
    }
  };

  return (
    <div className="app-layout">
      <Sidebar history={history} />
      <main className="main-content">
        <div className="content-wrapper">
          <AnalysisForm onSubmit={handleAnalyzeSubmit} isLoading={isLoading} />

          {error && <div className="error-message">{error}</div>}

          {isLoading && <LoadingIndicator />}

          <div className="results-feed">
            {/* FIX 2: Conditionally render the single result, do not use .map() */}
            {result && (
              <AnalysisResult
                key={result.id}
                result={result}
                onDownload={handleDownloadReport}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
