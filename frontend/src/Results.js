// src/components/Results.js
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
} from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip);

export default function Results({ result }) {
  const [showDetails, setShowDetails] = useState(false);

  // Prepare data for the Radar Chart
  const chartData = {
    labels: ['Follower Ratio', 'Bio Length', 'Post Count', 'Verified', 'Has Link in Bio'],
    datasets: [
      {
        label: 'Account Authenticity Score',
        data: [
          Math.min(10, (result.followers_to_following_ratio || 0) * 2),
          Math.min(10, (result.bio_length || 0) / 10),
          Math.min(10, (result.posts_count || 0) / 5),
          result.is_verified ? 10 : 1,
          result.external_url ? 8 : 2,
        ],
        backgroundColor: 'rgba(69, 123, 157, 0.2)',
        borderColor: 'rgba(69, 123, 157, 1)',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
        pointLabels: { font: { size: 14 } },
        suggestedMin: 0,
        suggestedMax: 10,
        ticks: { display: false },
      },
    },
    plugins: {
        legend: { display: false }
    }
  };

  return (
    <motion.div className="mt-6 text-left" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <div className="flex justify-center mb-6">
        <label className="inline-flex items-center cursor-pointer">
          <span className="mr-3 font-semibold">Raw Data</span>
          <input type="checkbox" checked={showDetails} onChange={() => setShowDetails(!showDetails)} className="sr-only peer" />
          <div className="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          <span className="ml-3 font-semibold">AI Analysis</span>
        </label>
      </div>

      {!showDetails ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="text-xl font-bold mb-4 text-center">Profile Raw Data</h3>
            <ul className="list-disc list-inside">
                <li>Followers: {result.followers_count}</li>
                <li>Following: {result.following_count}</li>
                <li>Posts: {result.posts_count}</li>
                <li>Bio Length: {result.bio_length}</li>
            </ul>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h3 className="text-2xl font-bold mb-4 text-center">Prediction: 
              <span className={result.prediction === 'Fake' ? 'text-[#e63946]' : 'text-[#2a9d8f]'}> {result.prediction}</span>
          </h3>
          <p className="text-center mb-6 text-lg text-[#457b9d] dark:text-[#a8dadc]">Confidence: {result.confidence_percent}%</p>
          
          <div className="w-full max-w-sm mx-auto mb-6">
             <Radar data={chartData} options={chartOptions} />
          </div>

          {result.ai_analysis && (
            <div className="p-4 border-t border-[#a8dadc] dark:border-[#457b9d]">
              <h4 className="font-bold text-xl mb-2 text-center text-[#457b9d] dark:text-[#a8dadc]">AI Analyst Report</h4>
              <div className="prose dark:prose-invert max-w-none">
                <ReactMarkdown>{result.ai_analysis}</ReactMarkdown>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}