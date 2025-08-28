// src/components/Loader.js
'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const loadingSteps = [
  "Connecting to profile...",
  "Analyzing numerical patterns...",
  "Scanning bio for keywords...",
  "Consulting AI Analyst...",
  "Finalizing report...",
];

export default function Loader() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % loadingSteps.length);
    }, 1500); // Change text every 1.5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div 
        className="mt-6 flex flex-col items-center justify-center space-y-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
    >
      <div className="w-12 h-12 border-4 border-dashed rounded-full animate-spin border-[#457b9d]"></div>
      <AnimatePresence mode="wait">
        <motion.p
          key={index}
          className="text-[#457b9d] dark:text-[#a8dadc] font-semibold"
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 10, opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {loadingSteps[index]}
        </motion.p>
      </AnimatePresence>
    </motion.div>
  );
}