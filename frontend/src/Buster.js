// src/components/Buster.js
'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import Loader from './Loader';
import Results from './Results';

const ProjectLogo = '/logo.svg';

export default function Buster() {
  const [username, setUsername] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
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
      
      const scrapedData = response.data.scraped_data || {};
      const resultData = {
        ...response.data,
        followers_count: scrapedData.followers_count || 0,
        following_count: scrapedData.following_count || 0,
        posts_count: scrapedData.media_count || 0,
        bio_length: scrapedData.bio?.length || 0,
        is_verified: scrapedData.is_verified || false,
        external_url: !!scrapedData.bio_links,
        followers_to_following_ratio: (scrapedData.followers_count || 0) / ((scrapedData.following_count || 0) + 1),
      };
      setResult(resultData);
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
    <div className="w-full max-w-2xl mx-auto font-sans">
      <div className="flex justify-end mb-4">
        <motion.button 
          onClick={() => setIsDarkMode(!isDarkMode)} 
          className="w-12 h-12 rounded-full flex items-center justify-center bg-white dark:bg-[#2c4060] border border-[#a8dadc] dark:border-[#457b9d] text-2xl"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </motion.button>
      </div>

      <div className="bg-white dark:bg-[#2c4060] p-8 md:p-12 rounded-2xl shadow-lg text-center">
        <div className="flex items-center justify-center gap-4 mb-2">
            <img src={ProjectLogo} alt="Fake Buster Logo" className="w-12 h-12"/>
            <h2 className="text-4xl md:text-5xl font-bold text-[#1d3557] dark:text-[#f1faee]">Fake Buster</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6 mt-8">
          <div>
            <div className="grid grid-cols-2 gap-4">
              <button type="button" onClick={() => setPlatform('instagram')} className={`p-4 rounded-lg font-bold transition-all duration-200 ${platform === 'instagram' ? 'bg-[#457b9d] text-white' : 'bg-[#f1faee] dark:bg-[#1d3557] text-[#1d3557] dark:text-[#f1faee]'}`}>Instagram</button>
              <button type="button" onClick={() => setPlatform('x')} className={`p-4 rounded-lg font-bold transition-all duration-200 ${platform === 'x' ? 'bg-[#457b9d] text-white' : 'bg-[#f1faee] dark:bg-[#1d3557] text-[#1d3557] dark:text-[#f1faee]'}`}>Twitter / X</button>
            </div>
          </div>
          
          <div>
              <input
                id="username-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username to analyze..."
                required
                className="w-full p-4 rounded-lg bg-[#f1faee] dark:bg-[#1d3557] text-[#1d3557] dark:text-[#f1faee] border-2 border-transparent focus:border-[#457b9d] focus:outline-none"
              />
          </div>

          <motion.button 
            type="submit" 
            disabled={isLoading}
            className="w-full p-4 text-lg font-bold text-white bg-[#457b9d] rounded-lg transition-all duration-200 hover:bg-[#3a6883] disabled:bg-gray-400"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? 'Analyzing...' : 'Analyze Profile'}
          </motion.button>
        </form>

        <AnimatePresence mode="wait">
          {isLoading && <Loader key="loader" />}
          {error && (
            <motion.div key="error" className="mt-6 p-4 rounded-lg bg-[#fff0f0] text-[#e63946]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <p className="font-bold">{error}</p>
            </motion.div>
          )}
          {result && <Results key="result" result={result} />}
        </AnimatePresence>
      </div> 
    </div>
  );
}