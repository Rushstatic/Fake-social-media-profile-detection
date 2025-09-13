// src/App.js

import React, { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

import "./App.css";
import InstagramLogo from "./instagram-logo.svg";
import XLogo from "./x-logo.svg";
import Logo from "./logo.svg";
import Orb from "./LetterGlitch";
import ParticlesBackground from './components/ParticlesBackground';

function App() {
  const [username, setUsername] = useState("");
  const [platform, setPlatform] = useState("instagram");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const container = document.documentElement;
    container.classList.add("theme-transition");
    container.classList.toggle("dark-mode", isDarkMode);

    const timeout = setTimeout(() => {
      container.classList.remove("theme-transition");
    }, 600);

    return () => clearTimeout(timeout);
  }, [isDarkMode]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/predict", {
        username,
        platform,
      });
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Could not connect to the server. Is it running?"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const downloadReport = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/generate-report",
        result,
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `FakeBuster_Report_${result.username}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch {
      setError("Failed to generate PDF report.");
    }
  };

return (
  <main className="app-container">
  <ParticlesBackground />
    <div className="orb-layer">
      <Orb hoverIntensity={0.5} rotateOnHover={true} hue={0} />
    </div>

    <section className="app-content">
      <div className="container">
        <header className="header">
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="mode-toggle"
            title="Toggle Theme"
          >
            {isDarkMode ? "☀️" : "🌙"}
          </button>
        </header>

        <div className="card fade-in">
          <div className="title-container">
            <img src={Logo} alt="Fake Buster Logo" className="logo-main" />
            <h1 className="hero-title">Fake Buster</h1>
          </div>
          <p className="subtitle">Analyze any public Instagram or X profile.</p>

          <form onSubmit={handleSubmit} className="form-section">
            <div className="input-group">
              <label>Platform</label>
              <div className="radio-group">
                <label className={platform === "instagram" ? "selected" : ""}>
                  <input
                    type="radio"
                    name="platform"
                    value="instagram"
                    checked={platform === "instagram"}
                    onChange={(e) => setPlatform(e.target.value)}
                  />
                  Instagram
                </label>
                <label className={platform === "x" ? "selected" : ""}>
                  <input
                    type="radio"
                    name="platform"
                    value="x"
                    checked={platform === "x"}
                    onChange={(e) => setPlatform(e.target.value)}
                  />
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

            <button type="submit" disabled={isLoading} className="cta-button">
              {isLoading ? "Analyzing..." : "Analyze Profile"}
            </button>
          </form>

          {isLoading && <div className="loader"></div>}

          {error && (
            <div className="result-block error">
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="result-block">
              <h3>
                Prediction:{" "}
                <span className={result.prediction === "Fake" ? "fake" : "real"}>
                  {result.prediction}
                </span>
              </h3>
              <p>Confidence: {result.confidence_percent}%</p>
              <div className="download-button-container">
                <button onClick={downloadReport} className="download-button">
                  Download Report 📄
                </button>
              </div>
              {result.ai_analysis && (
                <div className="ai-analysis">
                  <h4>AI Analyst Report</h4>
                  <ReactMarkdown>{result.ai_analysis}</ReactMarkdown>
                </div>
              )}
            </div>
          )}
        </div>

        <footer className="footer">
          <p>Made with ❤️ by rushstatic</p>
          <div className="logo-container">
            {platform === "instagram" && (
              <img src={InstagramLogo} alt="Instagram" className="logo" />
            )}
            {platform === "x" && (
              <img src={XLogo} alt="Twitter/X" className="logo" />
            )}
          </div>
        </footer>
      </div>
    </section>
  </main>
);

}

export default App;
