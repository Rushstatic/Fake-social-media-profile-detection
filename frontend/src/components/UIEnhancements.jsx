import React, { useState, useEffect } from "react";
import Orb from "../LetterGlitch";
import "./UIEnhancements.css";

/**
 * 1. ConfidenceMeter
 */
export const ConfidenceMeter = ({ confidence }) => {
  const getLevel = () => {
    if (confidence >= 75) return "high";
    if (confidence >= 50) return "medium";
    return "low";
  };

  return (
    <div className="confidence-meter-container">
      <div className="confidence-label">Confidence</div>
      <div className="confidence-meter">
        <div
          className={`confidence-fill ${getLevel()}`}
          style={{ width: `${confidence}%` }}
        />
      </div>
      <div className="confidence-percentage">{confidence}%</div>
    </div>
  );
};

/**
 * 2. GlitchText
 */
export const GlitchText = ({ text, className = "" }) => (
  <span className={`glitch-text ${className}`} data-text={text}>
    {text}
  </span>
);

/**
 * 3. OrbGlow
 */
export const OrbGlow = ({ prediction }) => (
  <div className={`orb-glow-layer ${prediction === "Fake" ? "fake" : "real"}`}>
    <Orb hoverIntensity={0.5} rotateOnHover={true} hue={0} />
  </div>
);

/**
 * 4. Toast
 */
export const Toast = ({ message, type = "info", onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`toast toast-${type}`} onClick={onClose}>
      {message}
    </div>
  );
};

/**
 * 5. RippleButton
 */
export const RippleButton = ({ children, onClick, className = "" }) => {
  const handleClick = (e) => {
    const btn = e.currentTarget;
    const circle = document.createElement("span");
    const diameter = Math.max(btn.clientWidth, btn.clientHeight);
    const radius = diameter / 2;
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - btn.offsetLeft - radius}px`;
    circle.style.top = `${e.clientY - btn.offsetTop - radius}px`;
    circle.classList.add("ripple");
    const ripple = btn.getElementsByClassName("ripple")[0];
    if (ripple) ripple.remove();
    btn.appendChild(circle);
    onClick && onClick(e);
  };

  return (
    <button className={`ripple-button ${className}`} onClick={handleClick}>
      {children}
    </button>
  );
};

/**
 * 6. ProfilePreview
 *   profile = { avatar, username, bio, followers, following }
 */
export const ProfilePreview = ({ profile }) => (
  <div className="profile-preview">
    <img src={profile.avatar} alt={`${profile.username} avatar`} />
    <h4>{profile.username}</h4>
    <p>{profile.bio}</p>
    <div className="stats">
      <span>{profile.followers} followers</span>
      <span>{profile.following} following</span>
    </div>
  </div>
);

/**
 * 7. ThemeToggle
 */
export const ThemeToggle = ({ isDarkMode, toggleTheme }) => (
  <button className="theme-toggle" onClick={toggleTheme}>
    {isDarkMode ? "☀️" : "🌙"}
  </button>
);

/**
 * 8. AIAnalysisTimeline
 */
export const AIAnalysisTimeline = ({ items }) => (
  <ul className="timeline">
    {items.map((item, i) => (
      <li key={i}>{item}</li>
    ))}
  </ul>
);

/**
 * 9. GradientTitle
 */
export const GradientTitle = ({ children }) => (
  <h1 className="gradient-title">{children}</h1>
);

/**
 * 10. SoundToggle
 */
export const SoundToggle = ({ src }) => {
  const [audio] = useState(new Audio(src));
  const [playing, setPlaying] = useState(false);

  const toggle = () => {
    if (playing) {
      audio.pause();
    } else {
      audio.loop = true;
      audio.volume = 0.1;
      audio.play();
    }
    setPlaying(!playing);
  };

  return (
    <button className="sound-toggle" onClick={toggle}>
      {playing ? "🔊" : "🔇"}
    </button>
  );
};
