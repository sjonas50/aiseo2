import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, Send } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, isLoading = false }) => {
  const [query, setQuery] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const placeholders = [
    "What are the best ETFs for retirement?",
    "How to find a financial advisor?",
    "Compare top investment platforms",
    "Best AI tools for content creation",
    "How to optimize for AI search engines?",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % placeholders.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query);
    }
  };

  return (
    <motion.div
      className="w-full max-w-4xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative bg-card rounded-2xl border border-border overflow-hidden group hover:border-accent/50 transition-all duration-300">
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-primary opacity-5 animate-gradient" />
          
          <div className="relative flex items-center p-4 sm:p-6">
            {/* Search Icon */}
            <Search className="w-6 h-6 text-gray-400 mr-4" />
            
            {/* Input Field */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-transparent text-white text-lg placeholder-gray-500 outline-none"
                disabled={isLoading}
              />
              
              {/* Animated Placeholder */}
              {!query && (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={placeholderIndex}
                    className="absolute inset-0 pointer-events-none flex items-center"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }}
                  >
                    <span className="text-gray-500 text-lg">
                      {placeholders[placeholderIndex]}
                    </span>
                  </motion.div>
                </AnimatePresence>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              className={`ml-4 p-3 rounded-xl bg-accent text-white transition-all duration-200 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600 hover:scale-105'
              }`}
              disabled={isLoading || !query.trim()}
              whileHover={!isLoading ? { scale: 1.05 } : {}}
              whileTap={!isLoading ? { scale: 0.95 } : {}}
            >
              {isLoading ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Sparkles className="w-5 h-5" />
                </motion.div>
              ) : (
                <Send className="w-5 h-5" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Quick Actions */}
        <motion.div
          className="mt-4 flex flex-wrap gap-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <span className="text-sm text-gray-400">Try:</span>
          {placeholders.slice(0, 3).map((placeholder, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setQuery(placeholder)}
              className="text-sm px-3 py-1 bg-card rounded-lg text-gray-300 hover:text-white hover:bg-gray-800 transition-all duration-200"
            >
              {placeholder.length > 30 ? placeholder.substring(0, 30) + '...' : placeholder}
            </button>
          ))}
        </motion.div>
      </form>
    </motion.div>
  );
};

export default QueryInput;